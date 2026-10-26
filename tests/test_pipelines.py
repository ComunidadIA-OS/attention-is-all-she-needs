import json
from pathlib import Path
import logging
import shutil
import wave
from contextlib import contextmanager

import cv2
import pytest

from conftest import ASR_RESPONSE, CAPTION, LOGO

from aiasn.model_adapters.transcriber import Transcriber
from aiasn.pipelines.base_pipeline import Pipeline
from aiasn.pipelines.context import RunContext
from aiasn.pipelines.video_annotation import annotate
from aiasn.run_pipelines import process_video
from aiasn.settings import Settings
from aiasn.storage.lake import Lake
from aiasn.storage.manifest import Manifest


def make_ctx(tmp_path, video_id="vid1") -> RunContext:
    settings = Settings(lake_uri=str(tmp_path / "lake"), tmp_dir=tmp_path / "tmp")
    return RunContext.for_video(settings, video_id)


def manifest_step(ctx, step):
    return ctx.manifest.read()["steps"][step]


def to_landing(ctx, video):
    ctx.lake.upload_to_landing(ctx.video_id, video)


@contextmanager
def captured_log():
    """Messages logged by the pipelines while inside the block."""
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


@pytest.fixture(scope="module")
def video_run(tmp_path_factory, video_pipeline, clip_with_cut) -> tuple[RunContext, list[str]]:
    """The video pipeline run once on `clip_with_cut`, and the lines it logged."""
    ctx = make_ctx(tmp_path_factory.mktemp("run"))
    to_landing(ctx, clip_with_cut)
    with captured_log() as lines:
        video_pipeline(ctx)
    return ctx, lines


def test_video_pipeline_outputs(video_run):
    ctx, _ = video_run
    cfg = ctx.settings.video
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
                               "face_x1", "face_y1", "face_x2", "face_y2", "gender", "gender_prob", "age",
                               "frame_width", "frame_height", "speaking_score"]
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

    # Gender and age of every detection; both men in the ZIDANE shots
    assert d.gender.isin(["F", "M"]).all() and d.gender_prob.between(0.5, 1).all() and d.age.between(0, 100).all()
    assert (d[d.shot != 1].gender == "M").all()

    # Active speaker: every visible face in the ZIDANE shots is tracked by TalkNet and gets a score,
    # except in the frames ffmpeg appends at the end, which have no audio left
    assert d[(d.shot != 1) & (d.frame < 6 * cfg.fps - 5)].speaking_score.notna().all()


def test_video_pipeline_texts(video_run):
    ctx, _ = video_run
    cfg = ctx.settings.video
    t = ctx.lake.read("bronze", "video_texts", ctx.video_id)
    assert list(t.columns) == ["frame", "shot", "text", "conf", "x1", "y1", "x2", "y2"]
    assert (t.frame % cfg.fps == 0).all()                         # 1 frame per second...
    assert set(range(0, 6 * cfg.fps, cfg.fps)) <= set(t.frame)    # ...all with the caption
    assert (t.groupby("frame").text.apply(lambda s: CAPTION in s.str.upper().tolist())).all()
    assert not t.text.str.upper().str.contains(LOGO).any()       # corner logos are dropped
    assert set(t.shot) == {0, 1, 2}


def test_video_pipeline_logs_one_line_per_step(video_run):
    _, lines = video_run
    assert [line.split()[1] for line in lines] == ["extract", "shots", "detect", "reid", "asd", "ocr", "total"]
    assert all(line.startswith("video") for line in lines)
    assert "3 shots" in lines[1]


def test_annotate(video_run):
    ctx, _ = video_run
    out = annotate(ctx)
    assert out == ctx.tmp_dir / "video" / "annotated.mp4"
    frames = int(cv2.VideoCapture(str(out)).get(cv2.CAP_PROP_FRAME_COUNT))
    assert frames == len(list((ctx.tmp_dir / "video" / "frames").glob("*.jpg")))
    assert not (ctx.tmp_dir / "video" / "annotated.avi").exists()


def test_audio_pipeline_outputs(tmp_path, monkeypatch, audio_pipeline, clip_with_cut):
    ctx = make_ctx(tmp_path)
    to_landing(ctx, clip_with_cut)
    monkeypatch.setattr(audio_pipeline.transcriber, "transcribe", lambda audio: Transcriber.parse(ASR_RESPONSE))
    with captured_log() as lines:
        audio_pipeline(ctx)
    assert manifest_step(ctx, "audio")["status"] == "ok"

    # Ephemeral mono audio at 16 kHz
    with wave.open(str(ctx.tmp_dir / "audio" / "audio.wav")) as wav:
        assert wav.getframerate() == ctx.settings.audio.sample_rate and wav.getnchannels() == 1

    turns = ctx.lake.read("bronze", "audio_turns", ctx.video_id)
    assert list(turns.columns) == ["turn", "start", "end", "speaker", "text", "gender", "gender_prob"]
    assert len(turns) == 3 and turns.speaker.tolist() == [0, 0, 1]
    assert turns.gender.isna().tolist() == [True, False, False]   # the first turn is too short
    assert [line.split()[1] for line in lines] == ["extract", "asr", "gender", "total"]
    assert "3 turns, 2 speakers" in lines[1]


class AfterOkPipeline(OkPipeline):
    name = "after_ok"


class AfterFailingPipeline(OkPipeline):
    name = "after_failing"


class ThenPipeline(OkPipeline):
    name = "then"


def test_process_video_runs_chains_in_parallel_and_reraises(tmp_path):
    settings = Settings(lake_uri=str(tmp_path / "lake"), tmp_dir=tmp_path / "tmp")
    with pytest.raises(RuntimeError, match="boom"):
        process_video("vid1", settings, [[FailingPipeline(), AfterFailingPipeline()], [OkPipeline(), AfterOkPipeline()]],
                      then=[ThenPipeline()])
    steps = json.loads((Path(settings.lake_uri) / "runs" / "video_id=vid1" / "manifest.json").read_text())["steps"]
    assert steps["failing"]["status"] == "error"
    assert "after_failing" not in steps                        # a failure stops the rest of its chain...
    assert steps["ok"]["status"] == steps["after_ok"]["status"] == "ok"   # ...but not the other chains
    assert "then" not in steps                                 # and what comes after the chains does not run


def test_process_video_runs_then_after_the_chains(tmp_path):
    settings = Settings(lake_uri=str(tmp_path / "lake"), tmp_dir=tmp_path / "tmp")
    process_video("vid1", settings, [[OkPipeline()], [AfterOkPipeline()]], then=[ThenPipeline()])
    steps = json.loads((Path(settings.lake_uri) / "runs" / "video_id=vid1" / "manifest.json").read_text())["steps"]
    assert steps["then"]["status"] == "ok"
    assert steps["then"]["started_at"] >= max(steps["ok"]["started_at"], steps["after_ok"]["started_at"])
