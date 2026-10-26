# SPDX-FileCopyrightText: 2026 Equipo 1: Attention Is All She Needs (Alba Camiña García, Pilar de la Fuente Diez, Rocío Jiménez Villén)
# SPDX-License-Identifier: Apache-2.0

"""Deterministic step of the silver and gold layers: reads some lake tables and computes new ones (ADR-0001)."""

from abc import ABC, abstractmethod

import pandas as pd

from aiasn.settings import Settings


class Transform(ABC):
    name: str            # step in the log
    layer: str           # where the outputs are written
    inputs: list[str]    # "layer/table" read from the lake
    outputs: list[str]   # tables written in `layer`

    def __init__(self, settings: Settings):
        self.settings = settings

    @abstractmethod
    def run(self, tables: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
        """The `outputs` of one video, from its `inputs` (keyed as "layer/table"). Pure: no I/O, no models."""
