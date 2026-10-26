import json
from pathlib import Path

import cv2
import numpy as np
import pandas as pd
import pytest
import requests
from scipy.io import wavfile

from conftest import ASR_RESPONSE, BUS, CAPTION, ZIDANE, text_image

from aiasn.model_adapters.transcriber import Transcriber
from aiasn.settings import TranscriberSettings

COLUMNS = ["track_id", "x1", "y1", "x2", "y2", "head"]


def test_shot_detector_finds_the_cuts(video_pipeline, clip_with_cut):
    cuts = video_pipeline.shot_detector.detect_cuts(clip_with_cut)
    assert len(cuts) == 2
    # cuts at 2 s and 4 s; indices are in the input video's own frames (30 fps)
    assert all(abs(c - s * 30) <= 2 for c, s in zip(cuts, [2, 4]))


def test_person_tracker_output(video_pipeline):
    tracker = video_pipeline.person_tracker
    image = cv2.imread(str(ZIDANE))
    h, w = image.shape[:2]
    tracker.reset()
    people = tracker.track(image)

    assert list(people.columns) == COLUMNS
    assert len(people) == 2
    assert people["head"].all()
    assert ((0 <= people.x1) & (people.x1 < people.x2) & (people.x2 <= w)).all()
    assert ((0 <= people.y1) & (people.y1 < people.y2) & (people.y2 <= h)).all()


def test_person_tracker_empty_image(video_pipeline):
    tracker = video_pipeline.person_tracker
    tracker.reset()
    people = tracker.track(cv2.imread(str(ZIDANE)) * 0)
    assert list(people.columns) == COLUMNS
    assert people.empty


def test_face_detector_output(video_pipeline):
    image = cv2.imread(str(ZIDANE))
    h, w = image.shape[:2]
    faces = video_pipeline.face_detector.detect(image)
    assert list(faces.columns) == ["x1", "y1", "x2", "y2", "score", "kps"]
    assert faces.kps[0].shape == (5, 2)
    assert len(faces) == 2
    assert ((0 <= faces.x1) & (faces.x1 < faces.x2) & (faces.x2 <= w)).all()
    assert video_pipeline.face_detector.detect(image * 0).empty


def test_person_tracker_reset_restarts_ids(video_pipeline):
    tracker = video_pipeline.person_tracker
    tracker.reset()
    tracker.track(cv2.imread(str(ZIDANE)))
    tracker.reset()
    assert tracker.track(cv2.imread(str(BUS))).track_id.min() == 1


def test_reidentificator_embeddings(video_pipeline):
    reid, image = video_pipeline.reidentificator, cv2.imread(str(ZIDANE))
    max_dist = reid.cfg.max_distance
    faces = video_pipeline.face_detector.detect(image)
    emb = reid.embed(image, faces)
    assert emb.shape == (2, 512)
    assert np.allclose(np.linalg.norm(emb, axis=1), 1)
    assert 1 - emb[0] @ emb[1] > max_dist   # two different people

    small = cv2.resize(image, None, fx=0.7, fy=0.7)
    emb_small = reid.embed(small, video_pipeline.face_detector.detect(small).sort_values("x1"))
    emb = emb[np.argsort(faces.x1.to_numpy())]
    assert (1 - (emb * emb_small).sum(axis=1) < max_dist).all()   # same people, rescaled

    assert reid.embed(image, faces.iloc[:0]).shape == (0, 512)


def test_reidentificator_cluster(video_pipeline):
    reid = video_pipeline.reidentificator
    a, b = np.eye(512)[0], np.eye(512)[1]
    person = reid.cluster({1: np.stack([a, a]), 2: np.stack([a + 0.1 * b]), 3: np.stack([b])})
    assert person[1] == person[2] != person[3]
    assert reid.cluster({7: np.stack([a])}) == {7: 1}
    assert reid.cluster({}) == {}


def test_active_speaker_detector_finds_the_speaker(video_pipeline, talking_clip):
    frames, audio, faces = talking_clip
    asd = video_pipeline.speaker_detector.detect(frames, audio, faces, cuts=[])
    assert list(asd.columns) == ["frame", "track", "x1", "y1", "x2", "y2", "score"]
    speaking = (asd.score > 0).groupby(asd.track).mean()
    assert (speaking > 0.8).sum() == 1   # one person talks most of the time
    assert (speaking < 0.1).sum() >= 3   # the others hardly ever


def test_active_speaker_detector_tracks_within_shots(video_pipeline, clip_with_cut, tmp_path):
    _, audio, frames = video_pipeline._extract(clip_with_cut, tmp_path)
    faces = [video_pipeline.face_detector.detect(cv2.imread(str(f))) for f in frames]
    cuts = [50, 100]   # 2 s and 4 s at 25 fps
    asd = video_pipeline.speaker_detector.detect(frames, audio, faces, cuts)
    shot = np.searchsorted(cuts, asd.frame, side="right")
    assert (pd.Series(shot).groupby(asd.track).nunique() == 1).all()
    assert asd.groupby("track").frame.apply(lambda f: (f.diff().dropna() == 1).all()).all()   # gaps interpolated
    assert asd.score.notna().all()
    zidane = asd[asd.frame < 50]
    assert zidane.track.nunique() == 2 and zidane.groupby("frame").size().max() == 2


def test_active_speaker_detector_no_faces(video_pipeline, clip_with_cut, tmp_path):
    _, audio, frames = video_pipeline._extract(clip_with_cut, tmp_path)
    no_faces = [video_pipeline.face_detector.detect(cv2.imread(str(frames[0])) * 0)] * len(frames)
    assert video_pipeline.speaker_detector.detect(frames, audio, no_faces, cuts=[]).empty


def test_ocr_reads_text(video_pipeline):
    image = np.full((200, 600, 3), 90, np.uint8)
    caption = text_image(CAPTION, 1.0)
    image[80:80 + caption.shape[0], 100:100 + caption.shape[1]] = caption
    texts = video_pipeline.ocr.read(image)
    assert list(texts.columns) == ["text", "conf", "x1", "y1", "x2", "y2"]
    assert texts.text.tolist() == [CAPTION]
    t = texts.iloc[0]
    assert 90 <= t.x1 < t.x2 <= 100 + caption.shape[1] + 10 and 70 <= t.y1 < t.y2 <= 80 + caption.shape[0] + 10
    assert video_pipeline.ocr.read(image * 0).empty


def test_gender_estimator_output(video_pipeline):
    image = cv2.imread(str(ZIDANE))
    people = video_pipeline._assign_faces(video_pipeline.person_tracker.track(image),
                                          video_pipeline.face_detector.detect(image))
    est = video_pipeline.gender_estimator.estimate(image, people)
    assert list(est.columns) == ["gender", "gender_prob", "age"]
    assert est.index.equals(people.index)
    assert (est.gender == "M").all()
    assert est.gender_prob.between(0.5, 1).all() and est.age.between(20, 80).all()

    no_face = people.assign(face_x1=np.nan, face_y1=np.nan, face_x2=np.nan, face_y2=np.nan)
    assert video_pipeline.gender_estimator.estimate(image, no_face).gender.isin(["F", "M"]).all()   # body only
    assert video_pipeline.gender_estimator.estimate(image, people.iloc[:0]).empty


def test_transcriber_parses_diarized_turns():
    turns = Transcriber.parse(ASR_RESPONSE)
    assert list(turns.columns) == ["start", "end", "speaker", "text"]
    assert turns.speaker.tolist() == [0, 0, 1]
    assert turns.text.tolist() == ["Hola.", "Bienvenidas", "al programa."]
    assert turns.end.tolist() == [0.3, 3.0, 5.5]


def test_transcriber_without_diarization_falls_back_to_segments():
    turns = Transcriber.parse({"segments": ASR_RESPONSE["segments"]})
    assert len(turns) == 1 and turns.speaker.isna().all()
    assert Transcriber.parse({}).empty


class FakeResponse:
    def __init__(self, status=200, body=None):
        self.status_code, self.ok, self.body, self.text = status, status < 400, body, "quota exceeded"

    def json(self):
        return self.body


def test_transcriber_request(monkeypatch, tmp_path):
    calls = []
    monkeypatch.setattr(requests, "post", lambda url, **kw: calls.append((url, kw)) or FakeResponse(body=ASR_RESPONSE))
    audio = tmp_path / "audio.wav"
    audio.write_bytes(b"RIFF")

    turns = Transcriber(TranscriberSettings(token=" abc\n123 ")).transcribe(audio)
    url, kw = calls[0]
    assert url.endswith("/audio/transcriptions")
    assert kw["headers"]["Authorization"] == "Bearer abc123"   # whitespace removed from the token
    assert kw["data"]["diarize"] == "true" and "language" not in kw["data"]
    assert len(turns) == 3

    Transcriber(TranscriberSettings(token="abc", language="ca")).transcribe(audio)
    assert calls[1][1]["data"]["language"] == "ca"


def test_transcriber_errors(monkeypatch, tmp_path):
    audio = tmp_path / "audio.wav"
    audio.write_bytes(b"RIFF")
    with pytest.raises(RuntimeError, match="token"):
        Transcriber(TranscriberSettings(token="")).transcribe(audio)
    monkeypatch.setattr(requests, "post", lambda url, **kw: FakeResponse(status=429))
    with pytest.raises(RuntimeError, match="429"):
        Transcriber(TranscriberSettings(token="abc")).transcribe(audio)


def test_voice_gender_classifier_output(voice_gender_classifier):
    rate = 16_000
    audio = (0.3 * np.sin(2 * np.pi * 180 * np.arange(3 * rate) / rate)).astype(np.float32)
    turns = pd.DataFrame({"start": [0.0, 0.5], "end": [0.3, 2.5]}, index=[7, 9])
    out = voice_gender_classifier.classify(audio, rate, turns)
    assert list(out.columns) == ["gender", "gender_prob"]
    assert out.index.equals(turns.index)
    assert pd.isna(out.gender[7]) and np.isnan(out.gender_prob[7])   # too short
    assert out.gender[9] in ("F", "M") and 0.5 <= out.gender_prob[9] <= 1


def test_voice_gender_classifier_matches_notebook(voice_gender_classifier):
    """Same per-speaker labels as the audio notebook on the CSIC video (mean female probability, 0.80 threshold)."""
    notebooks = Path("notebooks")
    audio, response = notebooks / "audios" / "robot_social_CSIC.wav", notebooks / "robot_social_CSIC.json"
    expected = notebooks / "dataframes" / "robot_social_CSIC.csv"
    if not (audio.is_file() and response.is_file() and expected.is_file()):
        pytest.skip("CSIC audio, transcription or notebook output not available")
    rate, samples = wavfile.read(audio)
    turns = Transcriber.parse(json.loads(response.read_text()))
    out = turns.join(voice_gender_classifier.classify(samples.astype(np.float32) / 32768, rate, turns))
    female = out.gender_prob.where(out.gender == "F", 1 - out.gender_prob)
    mean = female.groupby(out.speaker).mean()
    label = mean.map(lambda p: "F" if p >= 0.8 else "M" if p <= 0.2 else "Unknown")
    nb = pd.read_csv(expected).groupby("speaker").genero_inferido.first()
    assert {f"Hablante_{s}": g for s, g in label.items()} == nb.to_dict()
