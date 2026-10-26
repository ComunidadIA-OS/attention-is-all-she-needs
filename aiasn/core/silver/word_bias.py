# SPDX-FileCopyrightText: 2026 Equipo 1: Attention Is All She Needs (Alba Camiña García, Pilar de la Fuente Diez, Rocío Jiménez Villén)
# SPDX-License-Identifier: Apache-2.0

"""Gender bias in word2vec of the topics talked about and of the participants' titles (Bolukbasi et al. 2016).

A lookup in a fixed table of vectors, deterministic: no inference (ADR-0001).
"""

import logging
from collections.abc import Callable

import pandas as pd

from aiasn.core.transform import Transform
from aiasn.settings import Settings

TERM_BIAS = ["termino", "tipo", "sesgo"]   # sesgo > 0: towards "she", < 0: towards "he"; NA: not in the vocabulary
TOPIC, TITLE = "tema", "cargo"
log = logging.getLogger("aiasn")


class WordBiasSilver(Transform):
    name, layer = "word_bias", "silver"
    inputs = ["silver/nlp_topics", "silver/people"]
    outputs = ["term_bias"]

    def __init__(self, settings: Settings, score: Callable[[str], float | None] | None = None):
        super().__init__(settings)
        self._score = score   # loaded on first use: the model takes seconds and ~600 MB

    def run(self, tables: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
        """One row per distinct topic (English key) and caption title (`title_en`) of the video, with its bias."""
        terms = pd.concat([pd.DataFrame({"termino": tables["silver/nlp_topics"].topic.dropna().unique(), "tipo": TOPIC}),
                           pd.DataFrame({"termino": tables["silver/people"].title_en.dropna().unique(), "tipo": TITLE})],
                          ignore_index=True)
        score = self._scorer()
        bias = [score(t) for t in terms.termino] if score else [None] * len(terms)
        return {"term_bias": terms.assign(sesgo=pd.array(bias, dtype="Float64"))[TERM_BIAS]}

    def _scorer(self) -> Callable[[str], float | None] | None:
        if self._score is None:
            from aiasn.model_adapters.gender_direction import GenderDirection, download_word2vec   # numpy only
            cfg = self.settings.bias
            if not cfg.model_path.expanduser().is_file() and cfg.url:
                log.info("Downloading word2vec (1.6 GB) from %s", cfg.url)
                try:
                    download_word2vec(cfg)
                except OSError as e:
                    log.warning("word2vec download failed: %r", e)
            if not cfg.model_path.expanduser().is_file():
                log.warning("word2vec not found at %s: no gender bias of the terms", cfg.model_path)
                return None
            self._score = GenderDirection(self.settings.bias).score
        return self._score
