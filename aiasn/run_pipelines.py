"""Usage: python -m aiasn.run_pipelines path/to/video.mp4"""

import logging
import shutil
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from aiasn.pipelines.audio import AudioPipeline
from aiasn.pipelines.base_pipeline import Pipeline
from aiasn.pipelines.context import RunContext
from aiasn.pipelines.nlp import NlpPipeline
from aiasn.pipelines.silver import SilverPipeline
from aiasn.pipelines.video import VideoPipeline
from aiasn.settings import Settings
from aiasn.storage.lake import Lake
from aiasn.storage.manifest import Manifest


def process_video(video_id: str, settings: Settings, chains: list[list[Pipeline]], then: list[Pipeline] = ()) -> None:
    """Runs each chain in its own thread, its pipelines one after the other (a failure stops the rest of its chain).
    Then, if every chain succeeded, the pipelines in `then` in order: they read what the chains wrote.

    Audio and NLP mostly wait for remote APIs while video uses the GPU.
    """
    lake = Lake(settings.lake_dir)
    tmp_dir = settings.tmp_dir / video_id
    ctx = RunContext(video_id, settings, lake, Manifest(settings.lake_dir, video_id), tmp_dir)
    with ThreadPoolExecutor(len(chains)) as pool:
        for run in [pool.submit(_run_chain, chain, ctx) for chain in chains]:
            run.result()   # re-raises the first failure, once all have finished
    _run_chain(then, ctx)


def _run_chain(chain: list[Pipeline], ctx: RunContext) -> None:
    for pipeline in chain:
        pipeline(ctx)


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
    # NLP reads the transcript, so it goes after audio; models are loaded once
    chains = [[AudioPipeline(settings.audio), NlpPipeline(settings.nlp)], [VideoPipeline(settings.video)]]
    video_id = upload_to_landing(Path(sys.argv[1]), Lake(settings.lake_dir))
    process_video(video_id, settings, chains, then=[SilverPipeline(settings)])
