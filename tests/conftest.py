import subprocess

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
    """4 s clip at 30 fps with 44.1 kHz audio: 2 s of ZIDANE, hard cut, 2 s of BUS."""
    path = tmp_path_factory.mktemp("clips") / "clip.mp4"
    fit = "scale=640:360:force_original_aspect_ratio=decrease,pad=640:360:(ow-iw)/2:(oh-ih)/2,setsar=1,fps=30"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error",
                    "-loop", "1", "-t", "2", "-i", str(ZIDANE), "-loop", "1", "-t", "2", "-i", str(BUS),
                    "-f", "lavfi", "-i", "sine=duration=4:sample_rate=44100",
                    "-filter_complex", f"[0]{fit}[a];[1]{fit}[b];[a][b]concat=n=2:v=1[v]",
                    "-map", "[v]", "-map", "2", "-shortest", "-pix_fmt", "yuv420p", str(path)], check=True)
    return path
