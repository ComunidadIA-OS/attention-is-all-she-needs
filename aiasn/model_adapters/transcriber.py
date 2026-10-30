'''Model used to transcribe speech and tell speakers apart (Whisper with diarization on OVHcloud AI Endpoints)'''

import time
from pathlib import Path

import pandas as pd
import requests

from aiasn.settings import TranscriberSettings

COLUMNS = ["turn", "start", "end", "speaker", "text"]


class Transcriber:
    def __init__(self, cfg: TranscriberSettings):
        self.cfg = cfg
        self.token = "".join(cfg.token.get_secret_value().split())   # pasted tokens often carry line breaks

    def transcribe(self, audio: Path) -> pd.DataFrame:
        """One row per speech turn: turn (0, 1, ...), start and end (s), speaker (0, 1, ...; NA without diarization) and text."""
        if not self.token:
            raise RuntimeError("Missing OVHcloud token: set OVH_AI_ENDPOINTS_ACCESS_TOKEN in the environment or .env")
        data = {"model": self.cfg.model, "response_format": "verbose_json", "diarize": "true"}
        if self.cfg.language:
            data["language"] = self.cfg.language
        for attempt in range(self.cfg.retries + 1):
            try:
                with open(audio, "rb") as f:
                    r = requests.post(f"{self.cfg.base_url}/audio/transcriptions",
                                      headers={"Authorization": f"Bearer {self.token}"},
                                      files={"file": (audio.name, f)}, data=data, timeout=self.cfg.timeout)
                break
            except requests.ConnectionError:   # the endpoint sometimes drops the connection: try again
                if attempt == self.cfg.retries:
                    raise
                time.sleep(5)
        if not r.ok:
            raise RuntimeError(f"Transcription failed ({r.status_code}): {r.text[:500]}")
        return self.parse(r.json())

    @staticmethod
    def parse(response: dict) -> pd.DataFrame:
        """Turns of an API response: `diarization` when present, else `segments` (without speaker)."""
        turns = response.get("diarization") or response.get("segments") or []
        rows = [[i, float(t.get("start", 0)), float(t.get("end", 0)), t.get("speaker"), t.get("text", "").strip()]
                for i, t in enumerate(turns)]
        return pd.DataFrame(rows, columns=COLUMNS).astype({"turn": int, "start": float, "end": float,
                                                           "speaker": "Int64", "text": str})
