import subprocess
from pathlib import Path

import cv2
import numpy as np
import pandas as pd

from aiasn.model_adapters.person_tracker import PersonTracker
from aiasn.model_adapters.shot_detector import ShotDetector
from aiasn.pipelines.base_pipeline import Pipeline
from aiasn.pipelines.context import RunContext
from aiasn.settings import VideoSettings


class VideoPipeline(Pipeline):
    name = "video"

    def __init__(self, cfg: VideoSettings):
        self.cfg = cfg
        self.shot_detector = ShotDetector(cfg.shot_detector, cfg.device)
        self.person_tracker = PersonTracker(cfg.person_tracker, cfg.device)

    def run(self, ctx: RunContext) -> None:
        work = ctx.tmp_dir / self.name
        video, audio, frames = self._extract(ctx.lake.landing_file(ctx.video_id), work)

        cuts = self.shot_detector.detect_cuts(video)
        detections = self._detect(frames)
        detections.insert(1, "shot", np.searchsorted(cuts, detections["frame"], side="right"))
        # The tracker can keep a track_id across a cut: one new track per shot
        detections["track_id"] = detections.groupby(["shot", "track_id"]).ngroup() + 1
        ctx.lake.write("bronze", "video_detections", ctx.video_id, detections)

    def _detect(self, frames: list[Path]) -> pd.DataFrame:
        """People in 1 of every `stride` frames, with the frame size to compute area and centrality later."""
        self.person_tracker.reset()
        rows = []
        for f, path in enumerate(frames):
            if f % self.cfg.stride != self.cfg.stride - 1:   # same sampling as the notebook
                continue
            image = cv2.imread(str(path))
            people = self.person_tracker.track(image)
            rows.append(people.assign(frame=f, frame_width=image.shape[1], frame_height=image.shape[0]))
        detections = pd.concat(rows, ignore_index=True)
        return detections[["frame", "track_id", "x1", "y1", "x2", "y2", "head", "frame_width", "frame_height"]]

    def _extract(self, source: Path, work: Path) -> tuple[Path, Path, list[Path]]:
        """Resampled video, mono audio and frames. Audio and frames come from the resampled video, as in the TalkNet demo."""
        video, audio, frames_dir = work / "video.avi", work / "audio.wav", work / "frames"
        frames_dir.mkdir(parents=True, exist_ok=True)
        self._ffmpeg("-i", str(source), "-qscale:v", "2", "-async", "1", "-r", str(self.cfg.fps), str(video))
        self._ffmpeg("-i", str(video), "-ac", "1", "-vn", "-ar", str(self.cfg.audio_sample_rate), str(audio))
        self._ffmpeg("-i", str(video), "-qscale:v", "2", "-f", "image2", str(frames_dir / "%06d.jpg"))
        return video, audio, sorted(frames_dir.glob("*.jpg"))

    @staticmethod
    def _ffmpeg(*args: str) -> None:
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", *args], check=True)
