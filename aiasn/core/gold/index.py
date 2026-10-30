# SPDX-FileCopyrightText: 2026 Equipo 1: Attention Is All She Needs (Alba Camiña García, Pilar de la Fuente Diez, Rocío Jiménez Villén)
# SPDX-License-Identifier: Apache-2.0

"""Índice Global de Representación (0-100): weighted mean of four signals of the spec 21 §4, from the KPIs of gold.

Provisional: the spec does not close the authority signal yet. Until it does, authority is women's share of speech from
authority against men's, and the share of women among the cited references. A signal without data is left out and
the weights of the rest are scaled up.
"""

import pandas as pd

from aiasn.core.transform import Transform

WEIGHTS = {"pantalla": 0.30, "voz": 0.20, "espacio": 0.25, "autoridad": 0.25}   # spec 21 §4
FLOOR = 40.0   # % of women at which screen and voice score 100 (LO 2/2024)
INDEX = ["indice", "pantalla", "voz", "espacio", "autoridad", "provisional"]


def _share(kpis: pd.DataFrame, kpi: str, categoria: str | None, genero: str) -> float | None:
    """valor / base of one KPI row; None if there is no such row or its base is 0."""
    r = kpis[(kpis.kpi == kpi) & (kpis.genero == genero)
             & ((kpis.categoria == categoria) if categoria else kpis.categoria.isna())]
    return float(r.valor.iloc[0] / r.base.iloc[0]) if len(r) and r.base.iloc[0] else None


def _parity(women: float | None, men: float | None) -> float | None:
    """100 when women reach men's value (or there are no men), less in proportion below it."""
    if women is None and men is None:
        return None
    if not men:
        return 100.0
    return min(1.0, (women or 0.0) / men) * 100


def _mean(scores: list[float | None]) -> float | None:
    known = [s for s in scores if s is not None]
    return sum(known) / len(known) if known else None


def representation_index(kpis: pd.DataFrame) -> dict:
    """The index and each of its four signals, 0-100 (None without data)."""
    shares = {g: {"voz": _share(kpis, "parity", "voz_s", g), "pantalla": _share(kpis, "parity", "pantalla_s", g)}
              for g in ("mujer", "hombre")}
    def floor(share: float | None) -> float | None:   # share 0-1 → 100 at the 40 % floor, linear below it
        return None if share is None else min(100.0, share * 100 / FLOOR * 100)
    refs = kpis[kpis.kpi == "references"].set_index("genero").valor
    cited = float(refs.sum()) if len(refs) else 0.0
    scores = {
        "pantalla": floor(shares["mujer"]["pantalla"]),
        "voz": floor(shares["mujer"]["voz"]),
        "espacio": _mean([_parity(_share(kpis, "parity", c, "mujer"), _share(kpis, "parity", c, "hombre"))
                          for c in ("centralidad", "area")]),
        "autoridad": _mean([_parity(_share(kpis, "authority", None, "mujer"), _share(kpis, "authority", None, "hombre")),
                            min(100.0, float(refs.get("mujer", 0.0)) / cited / 0.5 * 100) if cited else None]),
    }
    known = {k: s for k, s in scores.items() if s is not None}
    total = sum(WEIGHTS[k] * s for k, s in known.items()) / sum(WEIGHTS[k] for k in known) if known else None
    return {"indice": total, **scores, "provisional": True}


class IndexGold(Transform):
    name, layer = "index", "gold"
    inputs = ["gold/kpis"]
    outputs = ["index"]

    def run(self, tables: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
        row = representation_index(tables["gold/kpis"])
        return {"index": pd.DataFrame([row], columns=INDEX).astype({k: float for k in INDEX[:-1]})}
