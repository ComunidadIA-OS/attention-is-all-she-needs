# SPDX-FileCopyrightText: 2026 Equipo 1: Attention Is All She Needs (Alba Camiña García, Pilar de la Fuente Diez, Rocío Jiménez Villén)
# SPDX-License-Identifier: Apache-2.0

'''Gender direction of word2vec (w2vNEWS), as in Bolukbasi et al. 2016, "Man is to Computer Programmer as Woman is to
Homemaker?" and its code (github.com/tolga-b/debiaswe), to measure how gendered a term is'''

import gzip
import io
import urllib.request
from pathlib import Path

import numpy as np

from aiasn.settings import BiasSettings

# The 10 definitional pairs of the paper (Figure 5; data/definitional_pairs.json in debiaswe)
PAIRS = [("woman", "man"), ("girl", "boy"), ("she", "he"), ("mother", "father"), ("daughter", "son"), ("gal", "guy"),
         ("female", "male"), ("her", "his"), ("herself", "himself"), ("Mary", "John")]


def records(f, n: int, dim: int):
    """The next `n` (word, vector bytes) of an open binary word2vec file, after its header."""
    for _ in range(n):
        word = bytearray()
        while (c := f.read(1)) != b" ":
            if not c:
                raise EOFError("word2vec file cut short")
            if c != b"\n":   # some files end each vector with a newline
                word += c
        yield bytes(word), f.read(4 * dim)


def read_word2vec(path: Path, limit: int) -> tuple[list[str], np.ndarray]:
    """The first `limit` words of a binary word2vec file (sorted by frequency) and their unit vectors.

    Read with numpy instead of gensim, whose LGPL licence the core avoids (AGENTS.md).
    """
    raw = gzip.open(path, "rb") if path.suffix == ".gz" else open(path, "rb")
    with io.BufferedReader(raw) as f:
        total, dim = map(int, f.readline().split())
        n = min(limit, total)
        words, vectors = [], np.empty((n, dim), np.float32)
        for i, (word, vector) in enumerate(records(f, n, dim)):
            words.append(word.decode("utf-8", errors="replace"))
            vectors[i] = np.frombuffer(vector, np.float32)
    vectors /= np.linalg.norm(vectors, axis=1, keepdims=True)
    return words, vectors


def download_word2vec(cfg: BiasSettings) -> None:
    """Only the first `vocab_limit` words, the only ones read: the file is sorted by frequency, so the download stops
    there (w2vNEWS: ~0.5 GB of 1.6 GB, and that much less on disk)."""
    target = cfg.model_path.expanduser()
    target.parent.mkdir(parents=True, exist_ok=True)
    partial = target.with_name(target.name + ".part")   # a cut download is not taken as the model
    with urllib.request.urlopen(cfg.url) as response, io.BufferedReader(gzip.GzipFile(fileobj=response)) as f, \
            gzip.open(partial, "wb", compresslevel=6) as out:
        total, dim = map(int, f.readline().split())
        n = min(cfg.vocab_limit, total)
        out.write(f"{n} {dim}\n".encode())
        for word, vector in records(f, n, dim):
            out.write(word + b" " + vector)
    partial.rename(target)


def gender_direction(vector) -> np.ndarray:
    """g: first principal component of the definitional pairs centred on their means (doPCA in debiaswe), oriented so
    that g · (she - he) > 0."""
    rows = []
    for a, b in PAIRS:
        center = (vector(a) + vector(b)) / 2
        rows += [vector(a) - center, vector(b) - center]
    matrix = np.array(rows)
    g = np.linalg.svd(matrix - matrix.mean(axis=0), full_matrices=False)[2][0]   # what sklearn's PCA computes
    return g if g @ (vector("she") - vector("he")) > 0 else -g


class GenderDirection:
    def __init__(self, cfg: BiasSettings):
        words, self.vectors = read_word2vec(Path(cfg.model_path).expanduser(), cfg.vocab_limit)
        self.index = {w: i for i, w in enumerate(words)}
        self.g = gender_direction(lambda w: self.vectors[self.index[w]])

    def score(self, term: str | None) -> float | None:
        """Projection of the term on g (> 0: towards "she", < 0: towards "he"), looking it up as a single token with "_"
        between its words (as word2vec stores phrases). None if it is not among the most frequent words: no averaging
        of its words, which would add a bias of its own."""
        if not isinstance(term, str) or not term.strip():
            return None
        i = self.index.get("_".join(term.split()))
        return None if i is None else float(self.vectors[i] @ self.g)
