'''Model used to transcribe speech and tell speakers apart (Whisper with diarization on OVHcloud AI Endpoints)'''

from pathlib import Path

import pandas as pd
import requests

from aiasn.settings import TranscriberSettings

COLUMNS = ["start", "end", "speaker", "text"]


class Transcriber:
    def __init__(self, cfg: TranscriberSettings):
        self.cfg = cfg
        self.token = "".join(cfg.token.get_secret_value().split())   # pasted tokens often carry line breaks

    def transcribe(self, audio: Path) -> pd.DataFrame:
        """One row per speech turn: start and end (s), speaker (0, 1, ...; NA without diarization) and text."""
        if not self.token:
            raise RuntimeError("Missing OVHcloud token: set OVH_AI_ENDPOINTS_ACCESS_TOKEN in the environment or .env")
        data = {"model": self.cfg.model, "response_format": "verbose_json", "diarize": "true"}
        if self.cfg.language:
            data["language"] = self.cfg.language
        with open(audio, "rb") as f:
            r = requests.post(f"{self.cfg.base_url}/audio/transcriptions", headers={"Authorization": f"Bearer {self.token}"},
                              files={"file": (audio.name, f)}, data=data, timeout=self.cfg.timeout)
        if not r.ok:
            raise RuntimeError(f"Transcription failed ({r.status_code}): {r.text[:500]}")
        return self.parse(r.json())

    @staticmethod
    def parse(response: dict) -> pd.DataFrame:
        """Turns of an API response: `diarization` when present, else `segments` (without speaker)."""
        turns = response.get("diarization") or response.get("segments") or []
        rows = [[float(t.get("start", 0)), float(t.get("end", 0)), t.get("speaker"), t.get("text", "").strip()] for t in turns]
        return pd.DataFrame(rows, columns=COLUMNS).astype({"start": float, "end": float, "speaker": "Int64", "text": str})
