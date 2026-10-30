# SPDX-FileCopyrightText: 2026 Equipo 1: Attention Is All She Needs (Alba Camiña García, Pilar de la Fuente Diez, Rocío Jiménez Villén)
# SPDX-License-Identifier: Apache-2.0

"""Gender of a person or speaker from the per-detection or per-turn outputs of the models, with abstention (ADR-0005)."""

import numpy as np
import pandas as pd

from aiasn.core.fusion import aplicar_umbral_etico

WOMAN, MAN, UNDETERMINED = "mujer", "hombre", "no_determinado"


def female_prob(gender: pd.Series, prob: pd.Series) -> pd.Series:
    """Probability of a woman for each model output (gender F/M and the probability of that label); NaN without label."""
    return prob.where(gender == "F", 1 - prob).where(gender.isin(["F", "M"]))


def decide_gender(female: pd.Series, threshold: float, weights: pd.Series | None = None) -> tuple[str, float]:
    """Gender of everything in `female` (probabilities of a woman) together, and their weighted mean.

    `mujer` if the mean reaches `threshold`, `hombre` if it is at most 1 - `threshold`, otherwise `no_determinado`.
    """
    mask = female.notna()
    if not mask.any():
        return UNDETERMINED, np.nan
    weights = None if weights is None or not weights[mask].sum() else weights[mask]   # all zero: plain mean
    p = float(np.average(female[mask], weights=weights))
    label = WOMAN if p >= 0.5 else MAN
    return aplicar_umbral_etico(label, max(p, 1 - p), threshold), p


def fuse_gender(video: str | None, audio: str | None) -> tuple[str, str]:
    """Gender of a participant from their face and their voice, and where it comes from.

    A decided gender wins over an undetermined one; if face and voice contradict each other, the participant is left
    undetermined for human review (ADR-0005).
    """
    decided = {source: g for source, g in (("video", video), ("audio", audio)) if g in (WOMAN, MAN)}
    if not decided:
        return UNDETERMINED, "ninguna"
    if len(decided) == 1:
        return next(iter(decided.items()))[::-1]
    return (video, "ambos") if video == audio else (UNDETERMINED, "conflicto")


def from_model(label: str | None) -> str:
    """The gender label of a model (F/M) in the vocabulary of silver; anything else is undetermined."""
    return {"F": WOMAN, "M": MAN}.get(label, UNDETERMINED)
