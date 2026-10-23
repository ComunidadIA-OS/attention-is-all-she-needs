"""Usage: python -m aiasn.run_pipelines path/to/video.mp4"""

import shutil
import sys
from pathlib import Path

from aiasn.pipelines.context import RunContext
from aiasn.pipelines.video import VideoPipeline
from aiasn.settings import Settings
from aiasn.storage.lake import Lake
from aiasn.storage.manifest import Manifest


def process_video(video_id: str, settings: Settings) -> None:
    lake = Lake(settings.lake_dir)
    tmp_dir = settings.tmp_dir / video_id
    ctx = RunContext(video_id, settings, lake, Manifest(settings.lake_dir, video_id), tmp_dir)
    VideoPipeline()(ctx)


def upload_to_landing(video: Path, lake: Lake) -> str:
    """What the API will do."""
    video_id = video.stem
    landing = lake.landing_dir(video_id)
    landing.mkdir(parents=True, exist_ok=True)
    shutil.copy2(video, landing / video.name)
    return video_id


if __name__ == "__main__":
    settings = Settings()
    video_id = upload_to_landing(Path(sys.argv[1]), Lake(settings.lake_dir))
    process_video(video_id, settings)
