import subprocess

import cv2

import pytest
from ultralytics.utils import ASSETS

from aiasn.pipelines.video import VideoPipeline
from aiasn.settings import VideoSettings

ZIDANE, BUS = ASSETS / "zidane.jpg", ASSETS / "bus.jpg"   # sample images shipped with Ultralytics: 2 and 4 people


@pytest.fixture(scope="session")
def video_pipeline() -> VideoPipeline:
    """Loaded once: the models take seconds to load."""
    return VideoPipeline(VideoSettings())


@pytest.fixture(scope="session")
def clip_with_cut(tmp_path_factory):
    """6 s clip at 30 fps with 44.1 kHz audio: 2 s each of ZIDANE, BUS and ZIDANE again, with hard cuts."""
    path = tmp_path_factory.mktemp("clips") / "clip.mp4"
    fit = "scale=640:360:force_original_aspect_ratio=decrease,pad=640:360:(ow-iw)/2:(oh-ih)/2,setsar=1,fps=30"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error",
                    "-loop", "1", "-t", "2", "-i", str(ZIDANE), "-loop", "1", "-t", "2", "-i", str(BUS),
                    "-loop", "1", "-t", "2", "-i", str(ZIDANE), "-f", "lavfi", "-i", "sine=duration=6:sample_rate=44100",
                    "-filter_complex", f"[0]{fit}[a];[1]{fit}[b];[2]{fit}[c];[a][b][c]concat=n=3:v=1[v]",
                    "-map", "[v]", "-map", "3", "-shortest", "-pix_fmt", "yuv420p", str(path)], check=True)
    return path


@pytest.fixture(scope="session")
def talking_clip(video_pipeline, tmp_path_factory):
    """TalkNet's demo clip (one person talking among several), as 25 fps frames, 16 kHz audio and faces per frame."""
    source = video_pipeline.cfg.active_speaker_detector.repo_dir / "demo" / "001.avi"
    if not source.is_file():
        pytest.skip("TalkNet demo clip not available")
    _, audio, frames = video_pipeline._extract(source, tmp_path_factory.mktemp("talking"))
    return frames, audio, [video_pipeline.face_detector.detect(cv2.imread(str(f))) for f in frames]
