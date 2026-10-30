'''Model used to classify the perceived gender of a voice (Common-Voice-Gender-Detection, wav2vec2)'''

import numpy as np
import pandas as pd
import torch
from transformers import Wav2Vec2FeatureExtractor, Wav2Vec2ForSequenceClassification

from aiasn.settings import VoiceGenderClassifierSettings

COLUMNS = ["gender", "gender_prob"]


class VoiceGenderClassifier:
    def __init__(self, cfg: VoiceGenderClassifierSettings, device: str = "auto"):
        self.cfg = cfg
        self.device = torch.device(("cuda" if torch.cuda.is_available() else "cpu") if device == "auto" else device)
        self.model = Wav2Vec2ForSequenceClassification.from_pretrained(cfg.model).to(self.device).eval()
        self.processor = Wav2Vec2FeatureExtractor.from_pretrained(cfg.model)

    def classify(self, audio: np.ndarray, rate: int, turns: pd.DataFrame) -> pd.DataFrame:
        """Gender (F/M) of the voice in each turn (start and end in s) and its probability, from its first `max_seconds`.

        `audio` is mono, as floats in [-1, 1]. Turns shorter than `min_seconds` get NA: too little voice to decide.
        """
        rows = []
        for t in turns.itertuples():
            if t.end - t.start < self.cfg.min_seconds:
                rows.append([None, np.nan])
                continue
            clip = audio[int(t.start * rate): int(min(t.end, t.start + self.cfg.max_seconds) * rate)]
            inputs = self.processor(clip, sampling_rate=rate, return_tensors="pt").to(self.device)
            with torch.no_grad():
                probs = self.model(**inputs).logits.softmax(-1)[0]
            label = self.model.config.id2label[int(probs.argmax())]
            rows.append(["F" if label == "female" else "M", float(probs.max())])
        return pd.DataFrame(rows, columns=COLUMNS, index=turns.index).astype({"gender_prob": float})
