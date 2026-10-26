# SPDX-FileCopyrightText: 2026 Equipo 1: Attention Is All She Needs (Alba Camiña García, Pilar de la Fuente Diez, Rocío Jiménez Villén)
# SPDX-License-Identifier: Apache-2.0

from pathlib import Path

from aiasn.models import MODELS, Model, ensure_models
from aiasn.settings import Settings


def _model(name, present, fetched, needed=True):
    return Model(name, lambda s: present, lambda s: fetched.append(name), lambda s: needed)


def test_only_missing_needed_models_are_downloaded():
    fetched = []
    models = [_model("here", True, fetched), _model("missing", False, fetched),
              _model("not needed", False, fetched, needed=False)]
    assert ensure_models(Settings(), models) == ["missing"] == fetched


def test_models_dir_holds_every_local_model(tmp_path):
    s = Settings(models_dir=tmp_path)
    paths = [s.video.person_tracker.model, s.video.face_detector.root, s.video.reidentificator.root,
             s.video.active_speaker_detector.repo_dir, s.video.ocr.model_dir, s.bias.model_path]
    assert all(Path(p).parent == tmp_path for p in paths)
    assert Path(s.video.person_tracker.model).name == "yolo11m-pose.pt"
    assert Settings().video.active_speaker_detector.repo_dir == Path("models/TalkNet-ASD")   # unset: defaults kept


def test_zero_shot_model_only_for_zero_shot_tone():
    mdeberta = next(m for m in MODELS if "zero-shot" in m.name)
    assert not mdeberta.needed(Settings())
    assert mdeberta.needed(Settings(nlp={"tone": {"method": "zero_shot"}}))


def test_missing_files_are_detected(tmp_path):
    s = Settings(models_dir=tmp_path)
    local = [m for m in MODELS if m.name.split()[0] in ("YOLO", "InsightFace", "TalkNet", "EasyOCR", "word2vec")]
    assert len(local) == 5 and not any(m.present(s) for m in local)
