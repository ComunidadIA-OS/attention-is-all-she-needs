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
