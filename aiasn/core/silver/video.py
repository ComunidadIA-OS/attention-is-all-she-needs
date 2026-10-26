# SPDX-FileCopyrightText: 2026 Equipo 1: Attention Is All She Needs (Alba Camiña García, Pilar de la Fuente Diez, Rocío Jiménez Villén)
# SPDX-License-Identifier: Apache-2.0

"""Silver tables of the video pipeline: one row per person, and the time spans each person is on screen."""

import numpy as np
import pandas as pd

from aiasn.core.silver.gender import decide_gender, female_prob
from aiasn.core.transform import Transform

PEOPLE = ["person_id", "genero", "prob_mujer", "age", "screen_time_s", "speaking_time_s", "area", "centrality"]
PRESENCE = ["person_id", "tiempo_i", "tiempo_f", "hablando"]
FUSION_VIDEO = ["tiempo_i", "tiempo_f", "track_id", "person_id", "hablando", "genero_visual", "prob_genero",
                "rotulo_nombre", "rotulo_cargo", "area", "centrality"]


def geometry(d: pd.DataFrame) -> tuple[pd.Series, pd.Series]:
    """Share of the frame each box covers, and how central it is (1 at the centre, 0 at a corner).

    Same formulas as the fusion (`normalizar_tabla_video`), so both give the same numbers.
    """
    w, h = d.frame_width.astype(float), d.frame_height.astype(float)
    area = (d.x2 - d.x1).clip(lower=0) * (d.y2 - d.y1).clip(lower=0) / (w * h)
    cx, cy = (d.x1 + d.x2) / (2 * w), (d.y1 + d.y2) / (2 * h)
    centrality = (1 - np.hypot(cx - 0.5, cy - 0.5) / np.sqrt(0.5)).clip(0, 1)
    return area, centrality


class VideoSilver(Transform):
    name, layer = "video", "silver"
    inputs, outputs = ["bronze/video_detections"], ["video_people", "video_presence"]

    def run(self, tables: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
        d = tables["bronze/video_detections"].sort_values(["person_id", "frame"])
        area, centrality = geometry(d)
        d = d.assign(female=female_prob(d.gender, d.gender_prob), area=area, centrality=centrality,
                     speaking=self._speaking(d))
        return {"video_people": self._people(d), "video_presence": self._presence(d)}

    def _speaking(self, d: pd.DataFrame) -> pd.Series:
        """Whether each detection is speaking: TalkNet's score above the threshold (NaN, no face: not speaking),
        by majority over `speaking_window_s` around it, so that flickers shorter than half the window are ignored."""
        cfg, video = self.settings.silver, self.settings.video
        speaking = d.speaking_score > cfg.speaking_threshold
        n = max(1, round(cfg.speaking_window_s * video.fps / video.stride)) | 1   # odd number of detections
        if n == 1:
            return speaking
        votes = speaking.astype(float).groupby(d.person_id).transform(
            lambda s: s.rolling(n, center=True, min_periods=1).mean())
        return votes > 0.5

    def _people(self, d: pd.DataFrame) -> pd.DataFrame:
        """Gender by vote, median age, seconds on screen and speaking, mean area and centrality."""
        step = self.settings.video.stride / self.settings.video.fps   # seconds each detection stands for
        rows = []
        for person, g in d.groupby("person_id"):
            gender, p = decide_gender(g.female, self.settings.silver.gender_threshold)
            rows.append([person, gender, p, g.age.median(), len(g) * step, g.speaking.sum() * step,
                         g.area.mean(), g.centrality.mean()])
        return pd.DataFrame(rows, columns=PEOPLE).astype({"person_id": "Int64"})

    def _presence(self, d: pd.DataFrame) -> pd.DataFrame:
        """Spans of a person on screen without changing between speaking and silent. Absences up to `max_gap_s` do not
        split a span. Each detection covers the `stride` frames up to its own, as in the fusion."""
        fps, stride = self.settings.video.fps, self.settings.video.stride
        continues = (d.person_id.eq(d.person_id.shift())
                     & ((d.frame - d.frame.shift()) / fps <= stride / fps + self.settings.silver.max_gap_s)
                     & d.speaking.eq(d.speaking.shift()))
        spans = d.groupby((~continues).cumsum()).agg(person_id=("person_id", "first"), first=("frame", "min"),
                                                       last=("frame", "max"), hablando=("speaking", "first"))
        presence = pd.DataFrame({"person_id": spans.person_id,
                                 "tiempo_i": ((spans["first"] - stride + 1) / fps).clip(lower=0),
                                 "tiempo_f": (spans["last"] + 1) / fps, "hablando": spans.hablando})
        return presence[PRESENCE].reset_index(drop=True).astype({"person_id": "Int64", "hablando": bool})


def fusion_video(people: pd.DataFrame, presence: pd.DataFrame, names: pd.DataFrame | None = None) -> pd.DataFrame:
    """Video table in the contract of the fusion (`cruzar_intervalos_multimodales`): one row per stretch of a person
    on screen, with the gender, area and centrality of the person and, when known, the name and title of their caption.

    The fusion does not tell speaking from silent spans, so contiguous spans are one stretch (`hablando` if any is).
    `names` has `person_id`, `rotulo_nombre` and `rotulo_cargo`. `prob_genero` is the probability of the decided gender,
    so the fusion's own threshold keeps the same decision.
    """
    spans = presence.sort_values(["person_id", "tiempo_i"])
    new = ~(spans.person_id.eq(spans.person_id.shift()) & np.isclose(spans.tiempo_i, spans.tiempo_f.shift()))
    presence = (spans.groupby(new.cumsum()).agg(person_id=("person_id", "first"), tiempo_i=("tiempo_i", "min"),
                                                tiempo_f=("tiempo_f", "max"), hablando=("hablando", "any"))
                .reset_index(drop=True).astype({"person_id": "Int64"}))
    by_person = people.set_index("person_id")
    contract = presence.assign(
        track_id="person_" + presence.person_id.astype(str),
        genero_visual=presence.person_id.map(by_person.genero),
        prob_genero=presence.person_id.map(np.maximum(by_person.prob_mujer, 1 - by_person.prob_mujer)),
        area=presence.person_id.map(by_person.area), centrality=presence.person_id.map(by_person.centrality))
    if names is None:
        names = pd.DataFrame(columns=["person_id", "rotulo_nombre", "rotulo_cargo"])
    contract = contract.merge(names.astype({"person_id": "Int64"}), on="person_id", how="left")
    return contract[FUSION_VIDEO]
