from dataclasses import dataclass
from pathlib import Path

from aiasn.settings import Settings
from aiasn.storage.lake import Lake
from aiasn.storage.manifest import Manifest


@dataclass
class RunContext:
    video_id: str
    settings: Settings
    lake: Lake
    manifest: Manifest
    tmp_dir: Path   # ephemeral files (frames, crops)

    @classmethod
    def for_video(cls, settings: Settings, video_id: str) -> "RunContext":
        """The context of one video: its lake and manifest from the settings, and its own tmp folder."""
        lake = Lake.from_settings(settings)
        return cls(video_id, settings, lake, Manifest(lake, video_id), settings.tmp_dir / video_id)
