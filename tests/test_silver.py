# SPDX-FileCopyrightText: 2026 Equipo 1: Attention Is All She Needs (Alba Camiña García, Pilar de la Fuente Diez, Rocío Jiménez Villén)
# SPDX-License-Identifier: Apache-2.0

import json
import logging
from contextlib import contextmanager

import numpy as np
import pandas as pd
import pytest

from aiasn.core.silver.gender import decide_gender, female_prob
from aiasn.core.silver.video import VideoSilver
from aiasn.core.transform import Transform
from aiasn.pipelines.context import RunContext
from aiasn.pipelines.transform_pipeline import TransformPipeline
from aiasn.settings import Settings
from aiasn.storage.lake import Lake
from aiasn.storage.manifest import Manifest


def make_ctx(tmp_path, **settings) -> RunContext:
    s = Settings(lake_dir=tmp_path / "lake", tmp_dir=tmp_path / "tmp", **settings)
    return RunContext("vid1", s, Lake(s.lake_dir), Manifest(s.lake_dir, "vid1"), s.tmp_dir / "vid1")


@contextmanager
def captured_log():
    lines = []
    handler = logging.Handler()
    handler.emit = lambda record: lines.append(record.getMessage())
    logger = logging.getLogger("aiasn")
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    try:
        yield lines
    finally:
        logger.removeHandler(handler)


# Gender vote

def test_female_prob_from_model_labels():
    p = female_prob(pd.Series(["F", "M", None, "F"]), pd.Series([0.9, 0.7, 0.8, np.nan]))
    assert p.tolist()[:2] == [0.9, pytest.approx(0.3)]
    assert p.isna().tolist() == [False, False, True, True]


@pytest.mark.parametrize("female, expected", [
    ([0.9, 0.85], "mujer"), ([0.1, 0.15], "hombre"), ([0.9, 0.1], "no_determinado"), ([0.79], "no_determinado"),
    ([0.8], "mujer"), ([0.2], "hombre"),
])
def test_decide_gender_abstains_below_the_threshold(female, expected):
    assert decide_gender(pd.Series(female), 0.8)[0] == expected


def test_decide_gender_weights_and_missing_values():
    gender, p = decide_gender(pd.Series([0.9, 0.1, np.nan]), 0.8, weights=pd.Series([9.0, 1.0, 100.0]))
    assert gender == "mujer" and p == pytest.approx(0.82)   # the long turn counts more; the unlabelled one not at all
    gender, p = decide_gender(pd.Series([np.nan]), 0.8)
    assert gender == "no_determinado" and np.isnan(p)


# Transform pipeline

class Doubler(Transform):
    name, layer, inputs, outputs = "double", "silver", ["bronze/numbers"], ["doubled", "count"]

    def run(self, tables):
        n = tables["bronze/numbers"]
        return {"doubled": n.assign(x=n.x * 2), "count": pd.DataFrame({"n": [len(n)]})}


class Silver(TransformPipeline):
    name = "silver"


def test_transform_pipeline_reads_and_writes_the_lake(tmp_path):
    ctx = make_ctx(tmp_path)
    ctx.lake.write("bronze", "numbers", "vid1", pd.DataFrame({"x": [1, 2, 3]}))
    with captured_log() as lines:
        Silver([Doubler(ctx.settings)])(ctx)
    assert ctx.lake.read("silver", "doubled", "vid1").x.tolist() == [2, 4, 6]
    assert ctx.lake.read("silver", "count", "vid1").n.tolist() == [3]
    assert json.loads(ctx.manifest.path.read_text())["steps"]["silver"]["status"] == "ok"
    assert "3 doubled, 1 count" in lines[0]


def test_transform_pipeline_fails_without_its_inputs(tmp_path):
    ctx = make_ctx(tmp_path)
    with pytest.raises(FileNotFoundError):
        Silver([Doubler(ctx.settings)])(ctx)
    assert json.loads(ctx.manifest.path.read_text())["steps"]["silver"]["status"] == "error"


# Video

def detections(person: int, frames, gender: str, prob: float, speaking=None, box=(160, 90, 480, 270)) -> pd.DataFrame:
    """bronze video_detections of one person (fps 25, stride 4: each detection stands for 0.16 s), on a 640x360 frame."""
    n = len(frames)
    return pd.DataFrame({"frame": frames, "person_id": pd.array([person] * n, dtype="Int64"),
                         "x1": box[0], "y1": box[1], "x2": box[2], "y2": box[3], "frame_width": 640, "frame_height": 360,
                         "gender": gender, "gender_prob": prob, "age": 30.0,
                         "speaking_score": speaking if speaking is not None else [np.nan] * n})


DETECTIONS = pd.concat([
    # Person 1: a woman, centred on a quarter of the frame, silent and then speaking
    detections(1, range(3, 40, 4), "F", 0.9, speaking=[-1.0] * 5 + [2.0] * 5),
    # Person 2: a man in a corner, no face for TalkNet; leaves the frame for 3.5 s
    detections(2, [3, 7, 11, 99, 103], "M", 0.95, box=(0, 0, 64, 36)),
    # Person 3: unsure gender; one detection missing (shorter than max_gap_s)
    detections(3, [3, 11], "F", 0.6),
], ignore_index=True)


def test_video_people():
    people = VideoSilver(Settings()).run({"bronze/video_detections": DETECTIONS})["video_people"].set_index("person_id")
    assert people.genero.tolist() == ["mujer", "hombre", "no_determinado"]
    assert people.prob_mujer.tolist() == pytest.approx([0.9, 0.05, 0.6])
    assert people.screen_time_s.tolist() == pytest.approx([1.6, 0.8, 0.32])
    assert people.speaking_time_s.tolist() == pytest.approx([0.8, 0, 0])
    assert people.area[1] == pytest.approx(0.25) and people.centrality[1] == pytest.approx(1.0)
    assert people.area[2] == pytest.approx(0.01) and people.centrality[2] < 0.2
    assert people.age.tolist() == [30, 30, 30]


def test_video_presence_splits_on_speaking_and_long_absences():
    presence = VideoSilver(Settings()).run({"bronze/video_detections": DETECTIONS})["video_presence"]
    assert list(presence.columns) == ["person_id", "tiempo_i", "tiempo_f", "hablando"]
    assert presence.person_id.tolist() == [1, 1, 2, 2, 3]
    assert presence.hablando.tolist() == [False, True, False, False, False]
    assert presence.tiempo_i.tolist() == pytest.approx([0.0, 0.8, 0.0, 3.84, 0.0])
    assert presence.tiempo_f.tolist() == pytest.approx([0.8, 1.6, 0.48, 4.16, 0.48])


def test_video_presence_max_gap_is_configurable():
    settings = Settings(silver={"max_gap_s": 5.0})
    presence = VideoSilver(settings).run({"bronze/video_detections": DETECTIONS})["video_presence"]
    assert presence.person_id.tolist() == [1, 1, 2, 3]   # person 2's absence no longer splits the span


def test_video_silver_without_detections():
    out = VideoSilver(Settings()).run({"bronze/video_detections": DETECTIONS.iloc[:0]})
    assert out["video_people"].empty and out["video_presence"].empty
