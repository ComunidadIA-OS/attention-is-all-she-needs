import subprocess
from pathlib import Path

import pandas as pd

from aiasn.model_adapters.shot_detector import ShotDetector
from aiasn.pipelines.base_pipeline import Pipeline
from aiasn.pipelines.context import RunContext
from aiasn.settings import VideoSettings


class VideoPipeline(Pipeline):
    name = "video"

    def __init__(self, cfg: VideoSettings):
        self.cfg = cfg
        self.shot_detector = ShotDetector(cfg.shot_detector, cfg.device)

    def run(self, ctx: RunContext) -> None:
        work = ctx.tmp_dir / self.name
        video, audio, frames = self._extract(ctx.lake.landing_file(ctx.video_id), work)

        cuts = self.shot_detector.detect_cuts(video)
        ctx.lake.write("bronze", "video_shots", ctx.video_id, self._shots_table(cuts, len(frames)))

    def _extract(self, source: Path, work: Path) -> tuple[Path, Path, list[Path]]:
        """Resampled video, mono audio and frames. Audio and frames come from the resampled video, as in the TalkNet demo."""
        video, audio, frames_dir = work / "video.avi", work / "audio.wav", work / "frames"
        frames_dir.mkdir(parents=True, exist_ok=True)
        self._ffmpeg("-i", str(source), "-qscale:v", "2", "-async", "1", "-r", str(self.cfg.fps), str(video))
        self._ffmpeg("-i", str(video), "-ac", "1", "-vn", "-ar", str(self.cfg.audio_sample_rate), str(audio))
        self._ffmpeg("-i", str(video), "-qscale:v", "2", "-f", "image2", str(frames_dir / "%06d.jpg"))
        return video, audio, sorted(frames_dir.glob("*.jpg"))

    @staticmethod
    def _shots_table(cuts: list[int], n_frames: int) -> pd.DataFrame:
        """One row per shot; end_frame is exclusive."""
        bounds = [0, *cuts, n_frames]
        return pd.DataFrame({"shot": range(len(bounds) - 1), "start_frame": bounds[:-1], "end_frame": bounds[1:]})

    @staticmethod
    def _ffmpeg(*args: str) -> None:
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", *args], check=True)
