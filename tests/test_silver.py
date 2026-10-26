# SPDX-FileCopyrightText: 2026 Equipo 1: Attention Is All She Needs (Alba Camiña García, Pilar de la Fuente Diez, Rocío Jiménez Villén)
# SPDX-License-Identifier: Apache-2.0

import json
import logging
from contextlib import contextmanager

import numpy as np
import pandas as pd
import pytest

from aiasn.core.silver.gender import decide_gender, female_prob
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
