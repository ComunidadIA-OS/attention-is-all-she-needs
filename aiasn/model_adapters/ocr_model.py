'''Model used to read text on screen (captions, names, titles)'''

import easyocr
import numpy as np
import pandas as pd

from aiasn.settings import OcrSettings

COLUMNS = ["text", "conf", "x1", "y1", "x2", "y2"]


class OcrModel:
    def __init__(self, cfg: OcrSettings, device: str = "auto"):
        self.cfg = cfg
        self.reader = easyocr.Reader(cfg.languages, gpu=device != "cpu", verbose=False)   # falls back to CPU

    def read(self, image: np.ndarray) -> pd.DataFrame:
        """One row per text read with enough confidence: text, confidence and the box around it (x1, y1, x2, y2)."""
        rows = [[text, conf, *np.min(box, axis=0), *np.max(box, axis=0)]
                for box, text, conf in self.reader.readtext(image) if conf >= self.cfg.min_conf]
        return pd.DataFrame(rows, columns=COLUMNS).astype({c: float for c in COLUMNS[1:]})
