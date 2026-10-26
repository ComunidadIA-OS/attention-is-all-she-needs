# SPDX-FileCopyrightText: 2026 Equipo 1: Attention Is All She Needs (Alba Camiña García, Pilar de la Fuente Diez, Rocío Jiménez Villén)
# SPDX-License-Identifier: Apache-2.0
"""The local models the worker needs, and their download. The worker downloads the missing ones when it starts.

    python -m aiasn.models          download the missing models now (e.g. before going offline)
    python -m aiasn.models --list   only show which are present

To add or change a model, edit MODELS: where to find it in the settings, how to tell it is there and how to get it.
"""

import argparse
import logging
import urllib.request
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

from aiasn.settings import Settings

log = logging.getLogger(__name__)

W2V_URL = ("https://github.com/RaRe-Technologies/gensim-data/releases/download/"
           "word2vec-google-news-300/word2vec-google-news-300.gz")


@dataclass(frozen=True)
class Model:
    name: str
    present: Callable[[Settings], bool]
    fetch: Callable[[Settings], None]
    needed: Callable[[Settings], bool] = lambda settings: True


def _hf_present(repo: str, revision: str | None = None) -> bool:
    from huggingface_hub import snapshot_download
    try:
        snapshot_download(repo, revision=revision, local_files_only=True)
        return True
    except Exception:
        return False


def _hf_fetch(repo: str, revision: str | None = None) -> None:
    from huggingface_hub import snapshot_download
    snapshot_download(repo, revision=revision, ignore_patterns=["*.onnx", "*.h5", "*.msgpack", "*.ot", "onnx/*"])


def _yolo_fetch(settings: Settings) -> None:
    from ultralytics.utils.downloads import attempt_download_asset
    Path(settings.video.person_tracker.model).parent.mkdir(parents=True, exist_ok=True)
    attempt_download_asset(settings.video.person_tracker.model)


def _insightface_dir(settings: Settings) -> Path:
    cfg = settings.video.face_detector
    return cfg.root.expanduser() / "models" / cfg.model_pack


def _insightface_fetch(settings: Settings) -> None:
    from insightface.utils.storage import ensure_available
    cfg = settings.video.face_detector
    ensure_available("models", cfg.model_pack, root=str(cfg.root.expanduser()))


def _talknet_fetch(settings: Settings) -> None:
    from aiasn.model_adapters.active_speaker_detector import ActiveSpeakerDetector
    repo_dir = settings.video.active_speaker_detector.repo_dir
    repo_dir.parent.mkdir(parents=True, exist_ok=True)
    ActiveSpeakerDetector._ensure_repo(repo_dir)


def _easyocr_present(settings: Settings) -> bool:
    folder = settings.video.ocr.model_dir.expanduser()
    # detector + one recognizer; if the recognizer is for other languages, the OCR downloads it when it loads
    return (folder / "craft_mlt_25k.pth").is_file() and len(list(folder.glob("*.pth"))) > 1


def _easyocr_fetch(settings: Settings) -> None:
    import easyocr
    cfg = settings.video.ocr
    cfg.model_dir.expanduser().mkdir(parents=True, exist_ok=True)
    easyocr.Reader(cfg.languages, gpu=False, verbose=False, model_storage_directory=str(cfg.model_dir.expanduser()))


def _w2v_fetch(settings: Settings) -> None:
    target = settings.bias.model_path.expanduser()
    target.parent.mkdir(parents=True, exist_ok=True)
    partial = target.with_name(target.name + ".part")   # a cut download is not taken as the model
    urllib.request.urlretrieve(W2V_URL, partial)
    partial.rename(target)


MODELS = [
    Model("YOLO pose (person tracker)",
          lambda s: Path(s.video.person_tracker.model).is_file(), _yolo_fetch),
    Model("InsightFace (faces and re-identification)",
          lambda s: any(_insightface_dir(s).glob("*.onnx")), _insightface_fetch),
    Model("TalkNet (active speaker)",
          lambda s: (s.video.active_speaker_detector.repo_dir / "pretrain_TalkSet.model").is_file(), _talknet_fetch),
    Model("MiVOLO (gender on screen)",
          lambda s: _hf_present(s.video.gender_estimator.model, s.video.gender_estimator.revision),
          lambda s: _hf_fetch(s.video.gender_estimator.model, s.video.gender_estimator.revision)),
    Model("EasyOCR (captions)", _easyocr_present, _easyocr_fetch),
    Model("Voice gender",
          lambda s: _hf_present(s.audio.voice_gender_classifier.model),
          lambda s: _hf_fetch(s.audio.voice_gender_classifier.model)),
    Model("mDeBERTa (zero-shot tone)",
          lambda s: _hf_present(s.nlp.tone.zero_shot_model),
          lambda s: _hf_fetch(s.nlp.tone.zero_shot_model),
          needed=lambda s: s.nlp.tone.method == "zero_shot"),
    Model("word2vec Google News (gender bias)",
          lambda s: s.bias.model_path.expanduser().is_file(), _w2v_fetch),
]


def ensure_models(settings: Settings, models: list[Model] = MODELS) -> list[str]:
    """Downloads the needed models that are missing. Returns the names downloaded."""
    fetched = []
    for model in models:
        if model.needed(settings) and not model.present(settings):
            log.info("Downloading model: %s", model.name)
            model.fetch(settings)
            fetched.append(model.name)
    return fetched


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--list", action="store_true")
    args = parser.parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s", datefmt="%H:%M:%S")

    settings = Settings()
    if not args.list:
        ensure_models(settings)
    for model in MODELS:
        state = "not needed" if not model.needed(settings) else "ok" if model.present(settings) else "missing"
        print(f"{state:<11} {model.name}")


if __name__ == "__main__":
    main()
