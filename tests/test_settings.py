# SPDX-FileCopyrightText: 2026 Equipo 1: Attention Is All She Needs (Alba Camiña García, Pilar de la Fuente Diez, Rocío Jiménez Villén)
# SPDX-License-Identifier: Apache-2.0

from pathlib import Path

from aiasn.settings import Settings


def test_models_dir_holds_every_local_model(tmp_path):
    s = Settings(models_dir=tmp_path)
    paths = [s.video.person_tracker.model, s.video.face_detector.root, s.video.reidentificator.root,
             s.video.active_speaker_detector.repo_dir, s.video.ocr.model_dir, s.bias.model_path]
    assert all(Path(p).parent == tmp_path for p in paths)
    assert Path(s.video.person_tracker.model).name == "yolo11m-pose.pt"
    assert Settings().video.active_speaker_detector.repo_dir == Path("models/TalkNet-ASD")   # unset: defaults kept
