# SPDX-FileCopyrightText: 2026 Equipo 1: Attention Is All She Needs (Alba Camiña García, Pilar de la Fuente Diez, Rocío Jiménez Villén)
# SPDX-License-Identifier: Apache-2.0

from pathlib import Path

import pytest

from aiasn.pipelines.base_pipeline import Pipeline
from aiasn.pipelines.context import RunContext
from aiasn.pipelines.runner import process_video
from aiasn.settings import Settings
from aiasn.storage.lake import Lake
from aiasn.storage.manifest import Manifest


def settings_in(tmp_path) -> Settings:
    return Settings(lake_uri=str(tmp_path / "lake"), tmp_dir=tmp_path / "tmp")


def stored(settings: Settings, video_id: str = "vid1") -> dict:
    return Manifest(Lake.from_settings(settings), video_id).read()


class Counting(Pipeline):
    """Counts its runs; fails while `fails` is set."""
    name, runs, fails = "counting", 0, False

    def run(self, ctx):
        type(self).runs += 1
        if self.fails:
            raise RuntimeError("boom")


class OkPipeline(Counting):
    name = "ok"


class FailingPipeline(Counting):
    name, fails = "failing", True


class AfterOkPipeline(OkPipeline):
    name = "after_ok"


class AfterFailingPipeline(OkPipeline):
    name = "after_failing"


class ThenPipeline(OkPipeline):
    name = "then"


@pytest.fixture(autouse=True)
def reset_counts():
    for cls in (Counting, OkPipeline, FailingPipeline, AfterOkPipeline, AfterFailingPipeline, ThenPipeline):
        cls.runs = 0
        cls.fails = cls is FailingPipeline


def test_pipeline_records_success(tmp_path):
    ctx = RunContext.for_video(settings_in(tmp_path), "vid1")
    OkPipeline()(ctx)
    step = ctx.manifest.read()["steps"]["ok"]
    assert step["status"] == "ok" and step["seconds"] >= 0


def test_pipeline_records_failure_and_reraises(tmp_path):
    ctx = RunContext.for_video(settings_in(tmp_path), "vid1")
    with pytest.raises(RuntimeError):
        FailingPipeline()(ctx)
    step = ctx.manifest.read()["steps"]["failing"]
    assert step["status"] == "error" and "boom" in step["error"]


def test_manifest_is_kept_across_runs(tmp_path):
    settings = settings_in(tmp_path)
    OkPipeline()(RunContext.for_video(settings, "vid1"))
    assert Manifest(Lake.from_settings(settings), "vid1").step_done("ok")   # a new manifest object reads it back


def test_finished_steps_are_skipped_unless_forced(tmp_path):
    settings = settings_in(tmp_path)
    OkPipeline()(RunContext.for_video(settings, "vid1"))
    OkPipeline()(RunContext.for_video(settings, "vid1"))
    assert OkPipeline.runs == 1
    OkPipeline()(RunContext.for_video(settings, "vid1", force=True))
    assert OkPipeline.runs == 2


def test_process_video_runs_chains_in_parallel_and_reraises(tmp_path):
    settings = settings_in(tmp_path)
    with pytest.raises(RuntimeError, match="boom"):
        process_video("vid1", settings, [[FailingPipeline(), AfterFailingPipeline()], [OkPipeline(), AfterOkPipeline()]],
                      then=[ThenPipeline()])
    manifest = stored(settings)
    steps = manifest["steps"]
    assert steps["failing"]["status"] == "error"
    assert "after_failing" not in steps                                   # a failure stops the rest of its chain...
    assert steps["ok"]["status"] == steps["after_ok"]["status"] == "ok"   # ...but not the other chains
    assert "then" not in steps                                            # and what comes after does not run
    assert manifest["status"] == "error" and "boom" in manifest["error"]


def test_process_video_runs_then_after_the_chains(tmp_path):
    settings = settings_in(tmp_path)
    process_video("vid1", settings, [[OkPipeline()], [AfterOkPipeline()]], then=[ThenPipeline()])
    manifest = stored(settings)
    steps = manifest["steps"]
    assert steps["then"]["status"] == "ok"
    assert steps["then"]["started_at"] >= max(steps["ok"]["started_at"], steps["after_ok"]["started_at"])
    assert manifest["status"] == "ok" and manifest["error"] is None


def test_a_retry_resumes_where_the_last_run_stopped(tmp_path):
    settings = settings_in(tmp_path)
    with pytest.raises(RuntimeError):
        process_video("vid1", settings, [[OkPipeline(), FailingPipeline()]])
    FailingPipeline.fails = False   # whatever made it fail is fixed
    process_video("vid1", settings, [[OkPipeline(), FailingPipeline()]])
    assert OkPipeline.runs == 1 and FailingPipeline.runs == 2   # the done step is not run again
    assert stored(settings)["status"] == "ok"


def test_steps_after_a_rerun_step_run_again(tmp_path):
    settings = settings_in(tmp_path)
    process_video("vid1", settings, [[OkPipeline(), AfterOkPipeline()]], then=[ThenPipeline()])
    # Only the first step's record is lost (or it is redone): everything after it is redone too
    manifest = Manifest(Lake.from_settings(settings), "vid1")
    del manifest.data["steps"]["ok"]
    manifest._save()
    process_video("vid1", settings, [[OkPipeline(), AfterOkPipeline()]], then=[ThenPipeline()])
    assert OkPipeline.runs == AfterOkPipeline.runs == ThenPipeline.runs == 2


def test_nothing_runs_again_when_everything_is_done(tmp_path):
    settings = settings_in(tmp_path)
    for _ in range(2):
        process_video("vid1", settings, [[OkPipeline()], [AfterOkPipeline()]], then=[ThenPipeline()])
    assert OkPipeline.runs == AfterOkPipeline.runs == ThenPipeline.runs == 1


# Media deleted after the run (data minimisation)

def private_settings(tmp_path, delete: bool = True) -> Settings:
    return Settings(lake_uri=str(tmp_path / "lake"), tmp_dir=tmp_path / "tmp", privacy={"delete_media_after_run": delete})


def staged_media(settings: Settings, tmp_path, video_id: str = "vid1") -> tuple[Path, Path]:
    """A video in landing and frames in tmp, as the pipelines leave them: (landing folder, tmp folder)."""
    source = tmp_path / "source.mp4"
    source.write_bytes(b"video")
    lake = Lake.from_settings(settings)
    lake.upload_to_landing(video_id, source)
    frames = settings.tmp_dir / video_id / "video" / "frames"
    frames.mkdir(parents=True)
    (frames / "000001.jpg").write_bytes(b"face")
    return Path(lake.landing_dir(video_id)), settings.tmp_dir / video_id


def test_delete_media_is_opt_in_and_set_by_the_environment(monkeypatch):
    assert Settings().privacy.delete_media_after_run is False
    monkeypatch.setenv("PRIVACY__DELETE_MEDIA_AFTER_RUN", "true")
    assert Settings().privacy.delete_media_after_run is True


def test_media_is_kept_by_default(tmp_path):
    settings = private_settings(tmp_path, delete=False)
    landing, tmp = staged_media(settings, tmp_path)
    process_video("vid1", settings, [[OkPipeline()]])
    assert landing.exists() and tmp.exists()


def test_media_is_deleted_after_a_successful_run(tmp_path):
    settings = private_settings(tmp_path)
    landing, tmp = staged_media(settings, tmp_path)
    process_video("vid1", settings, [[OkPipeline()]], then=[ThenPipeline()])
    assert not landing.exists() and not tmp.exists()
    assert stored(settings)["status"] == "ok"   # the manifest, like the tables, stays in the lake


def test_a_failed_run_deletes_tmp_but_keeps_the_video_to_retry(tmp_path):
    settings = private_settings(tmp_path)
    landing, tmp = staged_media(settings, tmp_path)
    with pytest.raises(RuntimeError, match="boom"):
        process_video("vid1", settings, [[FailingPipeline()]])
    assert not tmp.exists() and landing.exists()   # frames with faces go; the source stays for the retry
    FailingPipeline.fails = False
    process_video("vid1", settings, [[FailingPipeline()]])
    assert stored(settings)["status"] == "ok" and not landing.exists()


def test_a_failure_to_delete_does_not_fail_the_run(tmp_path, monkeypatch):
    settings = private_settings(tmp_path)
    staged_media(settings, tmp_path)

    def boom(self, video_id):
        raise OSError("store unreachable")

    monkeypatch.setattr(Lake, "delete_landing", boom)
    process_video("vid1", settings, [[OkPipeline()]])
    assert stored(settings)["status"] == "ok"
