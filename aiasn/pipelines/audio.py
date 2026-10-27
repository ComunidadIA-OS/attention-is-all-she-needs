import argparse
import logging
import subprocess
from pathlib import Path

import numpy as np
from scipy.io import wavfile

from aiasn.model_adapters.transcriber import Transcriber
from aiasn.model_adapters.voice_gender_classifier import VoiceGenderClassifier
from aiasn.pipelines.base_pipeline import Pipeline
from aiasn.pipelines.context import RunContext
from aiasn.settings import AudioSettings


class AudioPipeline(Pipeline):
    name = "audio"

    def __init__(self, cfg: AudioSettings):
        self.cfg = cfg
        self.transcriber = Transcriber(cfg.transcriber)
        self.gender_classifier = VoiceGenderClassifier(cfg.voice_gender_classifier, cfg.device)

    def run(self, ctx: RunContext) -> None:
        work = ctx.tmp_dir / self.name
        audio = self._extract(ctx.lake.fetch_landing(ctx.video_id, work / "source"), work)
        rate, samples = wavfile.read(audio)
        self._log_step("extract", f"{len(samples) / rate:.0f} s of audio")

        turns = self.transcriber.transcribe(audio)
        speech = turns.end - turns.start
        self._log_step("asr", f"{len(turns)} turns, {turns.speaker.nunique()} speakers, {speech.sum():.0f} s of speech")

        turns = turns.join(self.gender_classifier.classify(samples.astype(np.float32) / 32768, rate, turns))
        classified = turns.gender.notna()
        female = speech[turns.gender == "F"].sum() / max(speech[classified].sum(), 1e-9)
        self._log_step("gender", f"{classified.sum()} of {len(turns)} turns classified, {female:.0%} of their speech female")
        ctx.lake.write("bronze", "audio_turns", ctx.video_id, turns)

    def _extract(self, source: Path, work: Path) -> Path:
        """Mono 16-bit audio at `sample_rate`: what Whisper and the voice classifier expect, and light to upload."""
        work.mkdir(parents=True, exist_ok=True)
        audio = work / "audio.wav"
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(source), "-vn", "-ac", "1",
                        "-ar", str(self.cfg.sample_rate), "-c:a", "pcm_s16le", str(audio)], check=True)
        return audio


if __name__ == "__main__":
    # Usage: python -m aiasn.pipelines.audio VIDEO_ID   (the video must be in landing)
    from aiasn.settings import Settings

    parser = argparse.ArgumentParser()
    parser.add_argument("video_id")
    video_id = parser.parse_args().video_id
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s", datefmt="%H:%M:%S")

    settings = Settings()
    ctx = RunContext.for_video(settings, video_id, force=True)   # run by hand: redo it
    AudioPipeline(settings.audio)(ctx)
