import subprocess

from aiasn.pipelines.base_pipeline import Pipeline
from aiasn.pipelines.context import RunContext


def ffmpeg(*args: str) -> None:
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", *args], check=True)


class VideoPipeline(Pipeline):
    name = "video"

    def run(self, ctx: RunContext) -> None:
        cfg = ctx.settings.video
        source = ctx.lake.landing_file(ctx.video_id)
        work = ctx.tmp_dir / self.name
        frames_dir = work / "frames"
        frames_dir.mkdir(parents=True, exist_ok=True)

        # Same as the TalkNet demo: 25 fps video first, then audio and frames from it
        video, audio = work / "video.avi", work / "audio.wav"
        ffmpeg("-i", str(source), "-qscale:v", "2", "-async", "1", "-r", str(cfg.fps), str(video))
        ffmpeg("-i", str(video), "-ac", "1", "-vn", "-ar", str(cfg.audio_sample_rate), str(audio))
        ffmpeg("-i", str(video), "-qscale:v", "2", "-f", "image2", str(frames_dir / "%06d.jpg"))
