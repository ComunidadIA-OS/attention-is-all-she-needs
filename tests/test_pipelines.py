import json
import shutil
import wave

import pytest

from aiasn.pipelines.base_pipeline import Pipeline
from aiasn.pipelines.context import RunContext
from aiasn.settings import Settings
from aiasn.storage.lake import Lake
from aiasn.storage.manifest import Manifest


def make_ctx(tmp_path, video_id="vid1") -> RunContext:
    settings = Settings(lake_dir=tmp_path / "lake", tmp_dir=tmp_path / "tmp")
    return RunContext(video_id, settings, Lake(settings.lake_dir),
                      Manifest(settings.lake_dir, video_id), settings.tmp_dir / video_id)


def manifest_step(ctx, step):
    return json.loads(ctx.manifest.path.read_text())["steps"][step]


class OkPipeline(Pipeline):
    name = "ok"

    def run(self, ctx): pass


class FailingPipeline(Pipeline):
    name = "failing"

    def run(self, ctx):
        raise RuntimeError("boom")


def test_pipeline_records_success(tmp_path):
    ctx = make_ctx(tmp_path)
    OkPipeline()(ctx)
    step = manifest_step(ctx, "ok")
    assert step["status"] == "ok"
    assert step["seconds"] >= 0


def test_pipeline_records_failure_and_reraises(tmp_path):
    ctx = make_ctx(tmp_path)
    with pytest.raises(RuntimeError):
        FailingPipeline()(ctx)
    step = manifest_step(ctx, "failing")
    assert step["status"] == "error"
    assert "boom" in step["error"]


def test_video_pipeline_outputs(tmp_path, video_pipeline, clip_with_cut):
    ctx = make_ctx(tmp_path)
    cfg = ctx.settings.video
    landing = ctx.lake.landing_dir(ctx.video_id)
    landing.mkdir(parents=True)
    shutil.copy(clip_with_cut, landing)

    video_pipeline(ctx)
    assert manifest_step(ctx, "video")["status"] == "ok"

    # Ephemeral files: resampled frames and mono audio
    work = ctx.tmp_dir / "video"
    # ffmpeg may append a few duplicated frames when changing frame rate
    assert len(list((work / "frames").glob("*.jpg"))) == pytest.approx(6 * cfg.fps, abs=3)
    with wave.open(str(work / "audio.wav")) as wav:
        assert wav.getframerate() == cfg.audio_sample_rate
        assert wav.getnchannels() == 1

    # Bronze detections
    d = ctx.lake.read("bronze", "video_detections", ctx.video_id)
    assert list(d.columns) == ["frame", "shot", "track_id", "person_id", "x1", "y1", "x2", "y2", "head",
                               "face_x1", "face_y1", "face_x2", "face_y2", "frame_width", "frame_height"]
    assert (d.frame % cfg.stride == cfg.stride - 1).all()
    assert (d.frame_width == 640).all() and (d.frame_height == 360).all()
    assert set(d.shot) == {0, 1, 2}
    assert d[d.shot == 0].frame.max() < d[d.shot == 1].frame.min() <= d[d.shot == 1].frame.max() < d[d.shot == 2].frame.min()
    assert d.groupby("track_id").shot.nunique().max() == 1   # no track spans the cut
    zidane = d[d.shot == 0]
    assert zidane.groupby("frame").size().median() == 2
    assert zidane.face_x1.notna().all()   # both faces are visible
    inside = (zidane.x1 <= zidane.face_x1) & (zidane.face_x2 <= zidane.x2)
    assert inside.all()                   # each face lies within its person's box

    # Re-identification: the two people of the first shot are found again in the third one
    first, third = (d[d.shot == s].groupby("track_id").person_id.first() for s in (0, 2))
    assert first.notna().all() and first.nunique() == 2
    assert set(first) == set(third)
    assert d.person_id.notna().all()   # discarded tracks are dropped
    assert d.groupby("track_id").person_id.nunique().max() == 1
