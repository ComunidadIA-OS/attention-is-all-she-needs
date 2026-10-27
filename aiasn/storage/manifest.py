"""Status of each step for one video, stored in runs/video_id=.../manifest.json of the lake."""

import json
import threading
import time
from datetime import datetime, timezone

from aiasn.storage.lake import Lake

# Status of the whole video, besides each step's
QUEUED, RUNNING, OK, ERROR = "en_cola", "procesando", "ok", "error"


class Manifest:
    def __init__(self, lake: Lake, video_id: str):
        self.lake = lake
        self.path = f"{lake.root}/runs/video_id={video_id}/manifest.json"   # as in load()
        self._lock = threading.Lock()   # audio and video write from different threads
        self._started: dict[str, float] = {}
        # Kept across runs: a retry resumes where the last one stopped
        if lake.fs.exists(self.path):
            self.data = self.read()
        else:
            self.data = {"video_id": video_id, "status": None, "error": None, "steps": {}}
            self._save()

    @staticmethod
    def load(lake: Lake, video_id: str) -> dict | None:
        """The manifest of `video_id` as stored, None if the video is unknown; unlike Manifest(), creates nothing."""
        path = f"{lake.root}/runs/video_id={video_id}/manifest.json"
        if not lake.fs.exists(path):
            return None
        with lake.fs.open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def read(self) -> dict:
        """The manifest as stored."""
        with self.lake.fs.open(self.path, "r", encoding="utf-8") as f:
            return json.load(f)

    def set_status(self, status: str, error: Exception | None = None) -> None:
        """Status of the whole video: QUEUED, RUNNING, OK or ERROR (with the error)."""
        with self._lock:
            self.data |= {"status": status, "error": repr(error) if error else None}
            self._save()

    def step_done(self, step: str) -> bool:
        return self.data["steps"].get(step, {}).get("status") == "ok"

    def start(self, step: str) -> None:
        self._started[step] = time.perf_counter()
        self._update(step, status="running", started_at=datetime.now(timezone.utc).isoformat())

    def done(self, step: str) -> None:
        self._update(step, status="ok", seconds=self._elapsed(step))

    def fail(self, step: str, error: Exception) -> None:
        self._update(step, status="error", seconds=self._elapsed(step), error=repr(error))

    def _elapsed(self, step: str) -> float:
        return round(time.perf_counter() - self._started[step], 2)

    def _update(self, step: str, **fields) -> None:
        with self._lock:
            self.data["steps"].setdefault(step, {}).update(fields)
            self._save()

    def _save(self) -> None:
        self.lake.fs.makedirs(self.path.rsplit("/", 1)[0], exist_ok=True)
        with self.lake.fs.open(self.path, "w", encoding="utf-8") as f:
            f.write(json.dumps(self.data, indent=2, ensure_ascii=False))
