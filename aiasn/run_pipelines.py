"""Usage: python -m aiasn.run_pipelines path/to/video.mp4"""

import logging
import shutil
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from aiasn.pipelines.audio import AudioPipeline
from aiasn.pipelines.base_pipeline import Pipeline
from aiasn.pipelines.context import RunContext
from aiasn.pipelines.video import VideoPipeline
from aiasn.settings import Settings
from aiasn.storage.lake import Lake
from aiasn.storage.manifest import Manifest


def process_video(video_id: str, settings: Settings, pipelines: list[Pipeline]) -> None:
    """Runs the pipelines in parallel threads: audio mostly waits for the remote API while video uses the GPU."""
    lake = Lake(settings.lake_dir)
    tmp_dir = settings.tmp_dir / video_id
    ctx = RunContext(video_id, settings, lake, Manifest(settings.lake_dir, video_id), tmp_dir)
    with ThreadPoolExecutor(len(pipelines)) as pool:
        for run in [pool.submit(p, ctx) for p in pipelines]:
            run.result()   # re-raises the first failure, once all have finished


def upload_to_landing(video: Path, lake: Lake) -> str:
    """What the API will do."""
    video_id = video.stem
    landing = lake.landing_dir(video_id)
    landing.mkdir(parents=True, exist_ok=True)
    shutil.copy2(video, landing / video.name)
    return video_id


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s", datefmt="%H:%M:%S")
    settings = Settings()
    pipelines = [AudioPipeline(settings.audio), VideoPipeline(settings.video)]   # loads the models once
    video_id = upload_to_landing(Path(sys.argv[1]), Lake(settings.lake_dir))
    process_video(video_id, settings, pipelines)
