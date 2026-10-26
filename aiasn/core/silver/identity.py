# SPDX-FileCopyrightText: 2026 Equipo 1: Attention Is All She Needs (Alba Camiña García, Pilar de la Fuente Diez, Rocío Jiménez Villén)
# SPDX-License-Identifier: Apache-2.0

"""Who is who in a video: the voice of each speaker linked to the person speaking on screen at the same time."""

import numpy as np
import pandas as pd

from aiasn.core.transform import Transform

LINKS = ["speaker_id", "person_id", "overlap_s", "share"]


def speaking_overlap(turns: pd.DataFrame, presence: pd.DataFrame) -> pd.DataFrame:
    """Seconds each speaker talks while each person is speaking on screen, per (speaker_id, person_id) pair."""
    talking = presence.loc[presence.hablando, ["person_id", "tiempo_i", "tiempo_f"]]
    voiced = turns.dropna(subset=["speaker_id"])[["speaker_id", "tiempo_i", "tiempo_f"]]
    pairs = voiced.merge(talking, how="cross", suffixes=("_turn", "_span"))
    pairs["overlap_s"] = (np.minimum(pairs.tiempo_f_turn, pairs.tiempo_f_span)
                          - np.maximum(pairs.tiempo_i_turn, pairs.tiempo_i_span)).clip(lower=0)
    return pairs.groupby(["speaker_id", "person_id"], as_index=False).overlap_s.sum()


class IdentitySilver(Transform):
    name, layer = "identity", "silver"
    inputs = ["silver/audio_turns", "silver/audio_speakers", "silver/video_presence"]
    outputs = ["speaker_person"]

    def run(self, tables: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
        return {"speaker_person": self._links(tables["silver/audio_turns"], tables["silver/audio_speakers"],
                                              tables["silver/video_presence"])}

    def _links(self, turns: pd.DataFrame, speakers: pd.DataFrame, presence: pd.DataFrame) -> pd.DataFrame:
        """One row per speaker with the person they are, if any: the one speaking on screen for longest while they talk,
        when that reaches `min_link_s` and `min_link_share` of their speech. Otherwise the voice is off screen.

        Several speakers may link to the same person (diarization may split someone); `overlap_s` and `share` are kept
        for the best candidate even when it is not enough, for human review.
        """
        cfg = self.settings.silver
        best = (speaking_overlap(turns, presence).sort_values("overlap_s", ascending=False)
                .drop_duplicates("speaker_id"))
        links = speakers[["speaker_id", "speech_time_s"]].merge(best, on="speaker_id", how="left")
        links["overlap_s"] = links.overlap_s.fillna(0.0)
        links["share"] = (links.overlap_s / links.speech_time_s.where(links.speech_time_s > 0)).fillna(0.0)
        enough = (links.overlap_s >= cfg.min_link_s) & (links.share >= cfg.min_link_share)
        links["person_id"] = links.person_id.astype("Int64").where(enough)
        return links[LINKS].astype({"speaker_id": "Int64"})
