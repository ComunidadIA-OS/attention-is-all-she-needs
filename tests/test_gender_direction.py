# SPDX-FileCopyrightText: 2026 Equipo 1: Attention Is All She Needs (Alba Camiña García, Pilar de la Fuente Diez, Rocío Jiménez Villén)
# SPDX-License-Identifier: Apache-2.0

import gzip
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from aiasn.model_adapters.gender_direction import PAIRS, GenderDirection, read_word2vec
from aiasn.core.silver.word_bias import WordBiasSilver
from aiasn.settings import BiasSettings, Settings


def write_word2vec(path: Path, vectors: dict[str, list[float]]) -> None:
    """A tiny binary word2vec file, gzipped like w2vNEWS."""
    dim = len(next(iter(vectors.values())))
    with gzip.open(path, "wb") as f:
        f.write(f"{len(vectors)} {dim}\n".encode())
        for word, v in vectors.items():
            f.write(word.encode() + b" " + np.array(v, np.float32).tobytes() + b"\n")


def tiny_model(tmp_path: Path) -> Path:
    """Axis 0 is gender (+ she, - he), axis 1 meaning; nurse leans to she, architect to he."""
    vectors = {}
    for i, (female, male) in enumerate(PAIRS):
        vectors[female], vectors[male] = [1.0, 1.0, i], [-1.0, 1.0, i]
    vectors |= {"nurse": [0.6, 1.0, 0.0], "architect": [-0.3, 1.0, 0.0], "computer_programmer": [-0.2, 1.0, 0.0],
                "table": [0.0, 1.0, 0.0]}
    path = tmp_path / "w2v.bin.gz"
    write_word2vec(path, vectors)
    return path


def test_read_word2vec_keeps_the_most_frequent_words(tmp_path):
    words, vectors = read_word2vec(tiny_model(tmp_path), limit=4)
    assert words == ["woman", "man", "girl", "boy"]
    assert vectors.shape == (4, 3) and np.allclose(np.linalg.norm(vectors, axis=1), 1)


def test_score_is_the_projection_on_the_gender_direction(tmp_path):
    d = GenderDirection(BiasSettings(model_path=tiny_model(tmp_path)))
    assert abs(d.g[0]) == pytest.approx(1.0, abs=1e-6) and d.g[0] > 0   # oriented towards "she"
    assert d.score("nurse") > 0 > d.score("architect")
    assert d.score("table") == pytest.approx(0.0, abs=1e-6)
    assert d.score("computer programmer") == d.score("computer_programmer")   # phrases are joined with "_"


def test_terms_not_in_the_vocabulary_have_no_score(tmp_path):
    d = GenderDirection(BiasSettings(model_path=tiny_model(tmp_path)))
    assert d.score("nurse architect") is None   # no averaging of its words
    assert d.score("") is None and d.score(None) is None and d.score("unicorn") is None


W2V = BiasSettings().model_path.expanduser()


@pytest.mark.skipif(not W2V.is_file(), reason="w2vNEWS not downloaded")
def test_real_model_matches_the_notebook():
    d = GenderDirection(BiasSettings())
    # Figure 1 of the paper, as computed in notebooks/word-embedding-bias.ipynb
    for word, expected in {"homemaker": 0.323, "nurse": 0.308, "architect": -0.177, "maestro": -0.244}.items():
        assert d.score(word) == pytest.approx(expected, abs=0.005)


def test_word_bias_downloads_a_missing_model(tmp_path):
    source = tiny_model(tmp_path)
    settings = Settings(bias={"model_path": tmp_path / "models" / source.name, "url": source.as_uri()})
    out = WordBiasSilver(settings).run({"silver/nlp_topics": pd.DataFrame({"topic": ["nurse"]}),
                                        "silver/people": pd.DataFrame({"title_en": [None]})})
    assert (tmp_path / "models" / source.name).is_file() and out["term_bias"].sesgo.iloc[0] > 0
