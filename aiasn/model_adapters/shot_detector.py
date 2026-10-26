'''Model used to detect shot cuts in video'''

from pathlib import Path

import torch
from transnetv2_pytorch import TransNetV2

from aiasn.settings import ShotDetectorSettings


class ShotDetector:
    def __init__(self, cfg: ShotDetectorSettings, device: str = "auto"):
        self.cfg = cfg
        self.model = TransNetV2(device=device).eval()   # loads the bundled weights

    def detect_cuts(self, video_path: Path) -> list[int]:
        """Frame indices (in video_path's own frame rate) where a new shot starts; frame 0 is not included."""
        with torch.no_grad():
            scenes = self.model.detect_scenes(str(video_path), threshold=self.cfg.threshold)
        return [int(s["start_frame"]) for s in scenes[1:]]
