# SPDX-FileCopyrightText: 2026 Equipo 1: Attention Is All She Needs (Alba Camiña García, Pilar de la Fuente Diez, Rocío Jiménez Villén)
# SPDX-License-Identifier: Apache-2.0

"""Silver tables of the video pipeline: one row per person, and the time spans each person is on screen."""

import numpy as np
import pandas as pd

from aiasn.core.silver.gender import decide_gender, female_prob
from aiasn.core.transform import Transform

PEOPLE = ["person_id", "genero", "prob_mujer", "age", "screen_time_s", "speaking_time_s", "area", "centrality"]
PRESENCE = ["person_id", "tiempo_i", "tiempo_f", "hablando"]


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
        d = tables["bronze/video_detections"]
        area, centrality = geometry(d)
        d = d.assign(female=female_prob(d.gender, d.gender_prob), area=area, centrality=centrality,
                     speaking=d.speaking_score > self.settings.silver.speaking_threshold)   # NaN (no face): not speaking
        return {"video_people": self._people(d), "video_presence": self._presence(d)}

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
        d = d.sort_values(["person_id", "frame"])
        continues = (d.person_id.eq(d.person_id.shift())
                     & ((d.frame - d.frame.shift()) / fps <= stride / fps + self.settings.silver.max_gap_s)
                     & d.speaking.eq(d.speaking.shift()))
        spans = d.groupby((~continues).cumsum()).agg(person_id=("person_id", "first"), first=("frame", "min"),
                                                       last=("frame", "max"), hablando=("speaking", "first"))
        presence = pd.DataFrame({"person_id": spans.person_id,
                                 "tiempo_i": ((spans["first"] - stride + 1) / fps).clip(lower=0),
                                 "tiempo_f": (spans["last"] + 1) / fps, "hablando": spans.hablando})
        return presence[PRESENCE].reset_index(drop=True).astype({"person_id": "Int64", "hablando": bool})
