import cv2

from conftest import BUS, ZIDANE

COLUMNS = ["track_id", "x1", "y1", "x2", "y2", "head"]


def test_shot_detector_finds_the_cut(video_pipeline, clip_with_cut):
    cuts = video_pipeline.shot_detector.detect_cuts(clip_with_cut)
    assert len(cuts) == 1
    assert abs(cuts[0] - 2 * 30) <= 2   # cut at 2 s; indices are in the input video's own frames (30 fps)


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
    assert list(faces.columns) == ["x1", "y1", "x2", "y2", "score"]
    assert len(faces) == 2
    assert ((0 <= faces.x1) & (faces.x1 < faces.x2) & (faces.x2 <= w)).all()
    assert video_pipeline.face_detector.detect(image * 0).empty


def test_person_tracker_reset_restarts_ids(video_pipeline):
    tracker = video_pipeline.person_tracker
    tracker.reset()
    tracker.track(cv2.imread(str(ZIDANE)))
    tracker.reset()
    assert tracker.track(cv2.imread(str(BUS))).track_id.min() == 1
