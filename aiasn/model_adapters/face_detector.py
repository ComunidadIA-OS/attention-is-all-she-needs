'''Model used to detect faces in frames'''

import numpy as np
import pandas as pd
from insightface.app import FaceAnalysis

from aiasn.settings import FaceDetectorSettings

COLUMNS = ["x1", "y1", "x2", "y2", "score"]


class FaceDetector:
    def __init__(self, cfg: FaceDetectorSettings, device: str = "auto"):
        providers = ["CPUExecutionProvider"] if device == "cpu" else ["CUDAExecutionProvider", "CPUExecutionProvider"]
        self.model = FaceAnalysis(name=cfg.model_pack, allowed_modules=["detection"], providers=providers)
        self.model.prepare(ctx_id=-1 if device == "cpu" else 0, det_size=(cfg.det_size, cfg.det_size))

    def detect(self, image: np.ndarray) -> pd.DataFrame:
        """One row per face: box (x1, y1, x2, y2), detection score and the 5 landmarks (kps) used to align it."""
        faces = self.model.get(image)
        df = pd.DataFrame([[*f.bbox, f.det_score] for f in faces], columns=COLUMNS, dtype=float)
        df["kps"] = [f.kps for f in faces]
        return df
