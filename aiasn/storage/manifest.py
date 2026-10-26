"""Status of each step for one video, stored in runs/video_id=.../manifest.json of the lake."""

import json
import threading
import time
from datetime import datetime, timezone

from aiasn.storage.lake import Lake


class Manifest:
    def __init__(self, lake: Lake, video_id: str):
        self.lake = lake
        self.path = f"{lake.root}/runs/video_id={video_id}/manifest.json"
        self._lock = threading.Lock()   # audio and video write from different threads
        self._started: dict[str, float] = {}
        self.data = {"video_id": video_id, "steps": {}}
        self._save()

    def read(self) -> dict:
        """The manifest as stored."""
        with self.lake.fs.open(self.path, "r", encoding="utf-8") as f:
            return json.load(f)

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
