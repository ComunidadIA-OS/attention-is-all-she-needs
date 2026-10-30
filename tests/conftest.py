import importlib.util
import subprocess

import pytest

# Model tests need the model libraries; the CI only installs the light ones, so they are not collected there
collect_ignore = [] if all(importlib.util.find_spec(m) for m in ("cv2", "torch")) else [
    "test_model_adapters.py", "test_pipelines.py"]

CAPTION, LOGO = "ENTREVISTA", "LOGO"
# Shape of an OVHcloud transcription with diarization (verbose_json), for turns within `clip_with_cut`
ASR_RESPONSE = {
    "language": "es",
    "segments": [{"id": 1, "start": 0.0, "end": 5.5, "text": " Hola. Bienvenidas al programa."}],
    "diarization": [{"speaker": 0, "text": "Hola.", "start": 0.0, "end": 0.3},
                    {"speaker": 0, "text": "Bienvenidas", "start": 0.5, "end": 3.0},
                    {"speaker": 1, "text": " al programa. ", "start": 3.0, "end": 5.5}],
}


@pytest.fixture(scope="session")
def video_pipeline():
    """Loaded once: the models take seconds to load."""
    from aiasn.pipelines.video import VideoPipeline
    from aiasn.settings import VideoSettings
    return VideoPipeline(VideoSettings())


@pytest.fixture(scope="session")
def voice_gender_classifier():
    from aiasn.model_adapters.voice_gender_classifier import VoiceGenderClassifier
    from aiasn.settings import VoiceGenderClassifierSettings
    return VoiceGenderClassifier(VoiceGenderClassifierSettings())


@pytest.fixture(scope="session")
def audio_pipeline():
    from aiasn.pipelines.audio import AudioPipeline
    from aiasn.settings import AudioSettings
    return AudioPipeline(AudioSettings())


@pytest.fixture(scope="session")
def clip_with_cut(tmp_path_factory):
    """6 s clip at 30 fps with 44.1 kHz audio: 2 s each of ZIDANE, BUS and ZIDANE again, with hard cuts.

    A CAPTION is shown at the bottom centre and a LOGO in the top-left corner all along.
    """
    import cv2
    from media import BUS, ZIDANE, text_image

    folder = tmp_path_factory.mktemp("clips")
    path, caption, logo = folder / "clip.mp4", folder / "caption.png", folder / "logo.png"
    cv2.imwrite(str(caption), text_image(CAPTION, 1.0))
    cv2.imwrite(str(logo), text_image(LOGO, 0.6))
    fit = "scale=640:360:force_original_aspect_ratio=decrease,pad=640:360:(ow-iw)/2:(oh-ih)/2,setsar=1,fps=30"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error",
                    "-loop", "1", "-t", "2", "-i", str(ZIDANE), "-loop", "1", "-t", "2", "-i", str(BUS),
                    "-loop", "1", "-t", "2", "-i", str(ZIDANE), "-f", "lavfi", "-i", "sine=duration=6:sample_rate=44100",
                    "-i", str(caption), "-i", str(logo),
                    "-filter_complex", f"[0]{fit}[a];[1]{fit}[b];[2]{fit}[c];[a][b][c]concat=n=3:v=1[v0];"
                                       "[v0][4]overlay=(W-w)/2:H-h-10[v1];[v1][5]overlay=8:8[v]",
                    "-map", "[v]", "-map", "3", "-shortest", "-pix_fmt", "yuv420p", str(path)], check=True)
    return path


@pytest.fixture(scope="session")
def talking_clip(video_pipeline, tmp_path_factory):
    """TalkNet's demo clip (one person talking among several), as 25 fps frames, 16 kHz audio and faces per frame."""
    import cv2

    source = video_pipeline.cfg.active_speaker_detector.repo_dir / "demo" / "001.avi"
    if not source.is_file():
        pytest.skip("TalkNet demo clip not available")
    _, audio, frames = video_pipeline._extract(source, tmp_path_factory.mktemp("talking"))
    return frames, audio, [video_pipeline.face_detector.detect(cv2.imread(str(f))) for f in frames]
