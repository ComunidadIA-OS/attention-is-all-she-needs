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
    p = float(np.average(female[mask], weights=None if weights is None else weights[mask]))
    label = WOMAN if p >= 0.5 else MAN
    return aplicar_umbral_etico(label, max(p, 1 - p), threshold), p
