'''Model used to detect and track people across frames'''

import tempfile
from pathlib import Path

import numpy as np
import pandas as pd
import ultralytics
from ultralytics import YOLO

from aiasn.settings import PersonTrackerSettings

HEAD_KEYPOINTS = 7   # COCO: nose, eyes, ears, shoulders


class PersonTracker:
    def __init__(self, cfg: PersonTrackerSettings, device: str = "auto"):
        self.cfg = cfg
        self.device = None if device == "auto" else device
        self.model = YOLO(cfg.model)
        self.tracker_yaml = self._botsort_with_reid()

    def reset(self) -> None:
        """Forget the tracks of the previous video."""
        if self.model.predictor is not None:
            for tracker in getattr(self.model.predictor, "trackers", []):
                tracker.reset()

    def track(self, image: np.ndarray) -> pd.DataFrame:
        """One row per person: track_id, box (x1, y1, x2, y2) and whether head or shoulders are visible."""
        r = self.model.track(image, persist=True, tracker=self.tracker_yaml, device=self.device, verbose=False)[0]
        if r.boxes.id is None:
            return pd.DataFrame(columns=["track_id", "x1", "y1", "x2", "y2", "head"])
        boxes = r.boxes.xyxy.cpu().numpy()
        head = (r.keypoints.conf[:, :HEAD_KEYPOINTS] > self.cfg.keypoint_conf).any(dim=1).cpu().numpy()
        return pd.DataFrame({"track_id": r.boxes.id.int().cpu().numpy(),
                             "x1": boxes[:, 0], "y1": boxes[:, 1], "x2": boxes[:, 2], "y2": boxes[:, 3],
                             "head": head})

    @staticmethod
    def _botsort_with_reid() -> str:
        """Copy of Ultralytics' BoT-SORT config with ReID enabled (uses the detector's own features)."""
        default = Path(ultralytics.__file__).parent / "cfg" / "trackers" / "botsort.yaml"
        yaml = tempfile.NamedTemporaryFile("w", suffix=".yaml", delete=False)
        yaml.write(default.read_text().replace("with_reid: False", "with_reid: True"))
        yaml.close()
        return yaml.name
