'''Model used to detect faces in frames'''

import numpy as np
import pandas as pd
import torch
from insightface.app import FaceAnalysis

from aiasn.settings import FaceDetectorSettings

COLUMNS = ["x1", "y1", "x2", "y2", "score"]


def onnx_device(device: str) -> tuple[list[str], int]:
    """ONNX Runtime providers and InsightFace ctx_id for `device`; "auto" asks for CUDA only when there is a GPU, so
    no failed CUDA attempt is logged without one."""
    if device == "cpu" or (device == "auto" and not torch.cuda.is_available()):
        return ["CPUExecutionProvider"], -1
    return ["CUDAExecutionProvider", "CPUExecutionProvider"], 0


class FaceDetector:
    def __init__(self, cfg: FaceDetectorSettings, device: str = "auto"):
        providers, ctx_id = onnx_device(device)
        self.model = FaceAnalysis(name=cfg.model_pack, root=str(cfg.root.expanduser()), allowed_modules=["detection"],
                                  providers=providers)
        self.model.prepare(ctx_id=ctx_id, det_size=(cfg.det_size, cfg.det_size))

    def detect(self, image: np.ndarray) -> pd.DataFrame:
        """One row per face: box (x1, y1, x2, y2), detection score and the 5 landmarks (kps) used to align it."""
        faces = self.model.get(image)
        df = pd.DataFrame([[*f.bbox, f.det_score] for f in faces], columns=COLUMNS, dtype=float)
        df["kps"] = [f.kps for f in faces]
        return df
