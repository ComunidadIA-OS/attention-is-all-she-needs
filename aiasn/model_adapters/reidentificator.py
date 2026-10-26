'''Model used to re-identify people across shots from their faces (ArcFace)'''

import glob
import os

import numpy as np
import pandas as pd
from insightface.model_zoo import get_model
from insightface.utils import ensure_available, face_align
from scipy.cluster.hierarchy import fcluster, linkage

from aiasn.settings import ReidentificatorSettings


class Reidentificator:
    def __init__(self, cfg: ReidentificatorSettings, device: str = "auto"):
        self.cfg = cfg
        providers = ["CPUExecutionProvider"] if device == "cpu" else ["CUDAExecutionProvider", "CPUExecutionProvider"]
        model_dir = ensure_available("models", cfg.model_pack, root=str(cfg.root.expanduser()))
        models = (get_model(f, providers=providers) for f in sorted(glob.glob(os.path.join(model_dir, "*.onnx"))))
        self.model = next(m for m in models if m is not None and m.taskname == "recognition")
        self.model.prepare(ctx_id=-1 if device == "cpu" else 0)

    def embed(self, image: np.ndarray, faces: pd.DataFrame) -> np.ndarray:
        """Unit-norm embedding of each face (rows of FaceDetector.detect), aligned with its landmarks."""
        if faces.empty:
            return np.empty((0, self.model.output_shape[1]), dtype=np.float32)
        crops = [face_align.norm_crop(image, landmark=k, image_size=self.model.input_size[0]) for k in faces.kps]
        emb = self.model.get_feat(crops)
        return emb / np.linalg.norm(emb, axis=1, keepdims=True)

    def cluster(self, embeddings: dict[int, np.ndarray]) -> dict[int, int]:
        """Person (1, 2, ...) of each track, given the embeddings of its faces: average-linkage on the track means."""
        tracks = list(embeddings)
        if len(tracks) < 2:
            return {t: 1 for t in tracks}
        means = np.stack([embeddings[t].mean(axis=0) for t in tracks])
        means /= np.linalg.norm(means, axis=1, keepdims=True)
        groups = fcluster(linkage(means, method="average", metric="cosine"), t=self.cfg.max_distance, criterion="distance")
        return dict(zip(tracks, groups.tolist()))
