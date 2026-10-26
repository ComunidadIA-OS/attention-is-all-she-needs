# SPDX-FileCopyrightText: 2026 Equipo 1: Attention Is All She Needs (Alba Camiña García, Pilar de la Fuente Diez, Rocío Jiménez Villén)
# SPDX-License-Identifier: Apache-2.0

"""The fusion of audio and video (aiasn.core.fusion) fed from silver: who speaks is already resolved there."""

import pandas as pd

from aiasn.core.fusion import calcular_kpis_paridad, cruzar_intervalos_multimodales
from aiasn.core.silver.names import CAPTION
from aiasn.core.silver.video import fusion_video
from aiasn.core.transform import Transform
from aiasn.settings import Settings

# Nested results of the parity KPIs flattened into the summary with these prefixes
NESTED = {"salvaguarda_paridad": "salvaguarda", "test_bechdel_digital": "bechdel"}


def fusion_inputs(tables: dict[str, pd.DataFrame]) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Audio and video tables in the contract of `cruzar_intervalos_multimodales`.

    The audio carries the `track_id` of the person each voice is (none for voices off screen), so the fusion does not
    guess who speaks; the video carries the names and titles of the captions.
    """
    turns, links, people = tables["silver/audio_turns"], tables["silver/speaker_person"], tables["silver/people"]
    track = {s: f"person_{int(p)}" if pd.notna(p) else None for s, p in zip(links.speaker_id, links.person_id)}
    audio = turns.assign(track_id=[track.get(s) if pd.notna(s) else None for s in turns.speaker_id])
    captioned = people[(people.name_source == CAPTION) & people.person_id.notna()]
    names = captioned[["person_id", "name", "title"]].rename(columns={"name": "rotulo_nombre", "title": "rotulo_cargo"})
    return audio, fusion_video(tables["silver/video_people"], tables["silver/video_presence"], names)


def parity(tables: dict[str, pd.DataFrame], settings: Settings) -> tuple[pd.DataFrame, dict]:
    """Events of the four quadrants and the parity KPIs of the fusion, with the same gender threshold as silver."""
    audio, video = fusion_inputs(tables)
    threshold = settings.silver.gender_threshold
    events = cruzar_intervalos_multimodales(audio, video, umbral_etico=threshold)
    return events, calcular_kpis_paridad(events) if not events.empty else {}


class FusionGold(Transform):
    name, layer = "fusion", "gold"
    inputs = ["silver/audio_turns", "silver/speaker_person", "silver/video_people", "silver/video_presence",
              "silver/people"]
    outputs = ["quadrants", "summary"]

    def run(self, tables: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
        events, kpis = parity(tables, self.settings)
        return {"quadrants": events, "summary": pd.DataFrame([self._summary(kpis)])}

    @staticmethod
    def _summary(kpis: dict) -> dict:
        """The verdicts of the video in one row: totals, alerts, Bechdel, non-binary safeguard and easy-read summary.
        The figures per gender go to gold/kpis."""
        row = {}
        for key, value in kpis.items():
            if key in NESTED:
                row |= {f"{NESTED[key]}_{k}": v for k, v in value.items()}
            elif not isinstance(value, (dict, list)):   # por_genero: gold/kpis; idiomas_soportados: fixed
                row[key] = value
        return row
