# SPDX-FileCopyrightText: 2026 Equipo 1: Attention Is All She Needs (Alba Camiña García, Pilar de la Fuente Diez, Rocío Jiménez Villén)
# SPDX-License-Identifier: Apache-2.0

"""Who is who in a video: the voice of each speaker linked to the person speaking on screen at the same time."""

import numpy as np
import pandas as pd

from aiasn.core.silver.gender import fuse_gender
from aiasn.core.transform import Transform

LINKS = ["speaker_id", "person_id", "overlap_s", "share"]
PEOPLE = ["participant_id", "person_id", "speaker_id", "genero", "genero_fuente", "screen_time_s", "speaking_time_s",
          "speech_time_s", "area", "centrality"]


def participant_of(links: pd.DataFrame) -> dict[int, str]:
    """Participant of each speaker (silver speaker_person): their person if the voice is on screen (`p<person_id>`),
    otherwise the voice itself (`v<speaker_id>`). The same ids as in the people table."""
    return {int(s): f"p{int(p)}" if pd.notna(p) else f"v{int(s)}" for s, p in zip(links.speaker_id, links.person_id)}


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
    inputs = ["silver/audio_turns", "silver/audio_speakers", "silver/video_presence", "silver/video_people"]
    outputs = ["speaker_person", "people"]

    def run(self, tables: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
        speakers = tables["silver/audio_speakers"]
        links = self._links(tables["silver/audio_turns"], speakers, tables["silver/video_presence"])
        return {"speaker_person": links, "people": self._people(links, speakers, tables["silver/video_people"])}

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

    @staticmethod
    def _people(links: pd.DataFrame, speakers: pd.DataFrame, video_people: pd.DataFrame) -> pd.DataFrame:
        """One row per participant: each person on screen (`p<person_id>`), with their main speaker if they talk, and
        each voice off screen (`v<speaker_id>`). Gender from face and voice together (`fuse_gender`)."""
        linked = links.dropna(subset=["person_id"]).merge(speakers[["speaker_id", "genero", "speech_time_s"]],
                                                          on="speaker_id")
        main = linked.sort_values("overlap_s", ascending=False).drop_duplicates("person_id").set_index("person_id")
        on_screen = video_people.assign(
            participant_id="p" + video_people.person_id.astype(str),
            speaker_id=video_people.person_id.map(main.speaker_id).astype("Int64"),
            genero_audio=video_people.person_id.map(main.genero),
            speech_time_s=video_people.person_id.map(linked.groupby("person_id").speech_time_s.sum()).fillna(0.0))
        voices = speakers[~speakers.speaker_id.isin(linked.speaker_id)]
        off_screen = pd.DataFrame({
            "participant_id": "v" + voices.speaker_id.astype(str), "person_id": pd.array([pd.NA] * len(voices), "Int64"),
            "speaker_id": voices.speaker_id, "genero_audio": voices.genero, "speech_time_s": voices.speech_time_s,
            "screen_time_s": 0.0, "speaking_time_s": 0.0, "area": np.nan, "centrality": np.nan})
        people = pd.concat([on_screen.rename(columns={"genero": "genero_video"}), off_screen], ignore_index=True)
        fused = [fuse_gender(v if isinstance(v, str) else None, a if isinstance(a, str) else None)
                 for v, a in zip(people.genero_video, people.genero_audio)]
        people["genero"] = [g for g, _ in fused]
        people["genero_fuente"] = [source for _, source in fused]
        return people[PEOPLE].astype({"person_id": "Int64", "speaker_id": "Int64"})
