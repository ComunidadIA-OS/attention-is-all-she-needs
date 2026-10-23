import json
import shutil
import subprocess
import wave

import pytest

from aiasn.pipelines.base_pipeline import Pipeline
from aiasn.pipelines.context import RunContext
from aiasn.pipelines.video import VideoPipeline
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


@pytest.mark.skipif(shutil.which("ffmpeg") is None, reason="ffmpeg not installed")
def test_video_pipeline_extracts_frames_and_audio(tmp_path):
    ctx = make_ctx(tmp_path)
    landing = ctx.lake.landing_dir(ctx.video_id)
    landing.mkdir(parents=True)
    # 2 s synthetic clip at 30 fps with 44.1 kHz audio, to check the conversion
    subprocess.run(["ffmpeg", "-loglevel", "error", "-f", "lavfi", "-i", "testsrc=duration=2:size=160x120:rate=30",
                    "-f", "lavfi", "-i", "sine=duration=2:sample_rate=44100", "-shortest", str(landing / "clip.mp4")],
                   check=True)

    VideoPipeline()(ctx)

    work = ctx.tmp_dir / "video"
    # ffmpeg may append a few duplicated frames when changing frame rate
    assert len(list((work / "frames").glob("*.jpg"))) == pytest.approx(2 * 25, abs=3)
    with wave.open(str(work / "audio.wav")) as wav:
        assert wav.getframerate() == 16_000
        assert wav.getnchannels() == 1
    assert manifest_step(ctx, "video")["status"] == "ok"
