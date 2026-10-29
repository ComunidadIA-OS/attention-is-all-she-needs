'''Model used to estimate perceived gender from face and body (MiVOLO v2).

MiVOLO also predicts an age; it is never read, kept nor stored (data minimisation: GDPR, EU AI Act).
'''

import numpy as np
import pandas as pd
import torch
from transformers import AutoConfig, AutoImageProcessor, AutoModelForImageClassification

from aiasn.settings import GenderEstimatorSettings

COLUMNS = ["gender", "gender_prob"]


class GenderEstimator:
    def __init__(self, cfg: GenderEstimatorSettings, device: str = "auto"):
        self.device = torch.device(("cuda" if torch.cuda.is_available() else "cpu") if device == "auto" else device)
        hub = dict(revision=cfg.revision, trust_remote_code=True)   # the model code lives in its Hub repo
        self.config = AutoConfig.from_pretrained(cfg.model, **hub)
        dtype = torch.float16 if self.device.type == "cuda" else torch.float32
        self.model = AutoModelForImageClassification.from_pretrained(cfg.model, dtype=dtype, **hub).to(self.device).eval()
        self.processor = AutoImageProcessor.from_pretrained(cfg.model, **hub)

    def estimate(self, image: np.ndarray, people: pd.DataFrame) -> pd.DataFrame:
        """For each person (box x1, y1, x2, y2 and face box face_x1..., NaN if unseen): gender (F/M) and its probability."""
        if people.empty:
            return pd.DataFrame(columns=COLUMNS, index=people.index).astype({"gender_prob": float})
        faces = [_crop(image, b) for b in people[["face_x1", "face_y1", "face_x2", "face_y2"]].to_numpy()]
        bodies = [_crop(image, b) for b in people[["x1", "y1", "x2", "y2"]].to_numpy()]
        with torch.no_grad():
            out = self.model(faces_input=self._pixels(faces), body_input=self._pixels(bodies))
        labels = [self.config.gender_id2label[int(i)] for i in out.gender_class_idx[:, 0]]
        return pd.DataFrame({"gender": ["F" if label == "female" else "M" for label in labels],
                             "gender_prob": out.gender_probs[:, 0].float().cpu().numpy()}, index=people.index)

    def _pixels(self, crops: list[np.ndarray | None]) -> torch.Tensor:
        return self.processor(images=crops)["pixel_values"].to(self.device, self.model.dtype)


def _crop(image: np.ndarray, box: np.ndarray) -> np.ndarray | None:
    """Image inside the box, or None if the box is missing or empty (MiVOLO then relies on the other input)."""
    if np.isnan(box).any():
        return None
    x1, y1, x2, y2 = [max(int(v), 0) for v in box]
    crop = image[y1:y2, x1:x2]
    return crop if crop.size else None
