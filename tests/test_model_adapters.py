import cv2
import numpy as np

from conftest import BUS, ZIDANE

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
