import argparse
import logging
import subprocess
from pathlib import Path

import cv2
import numpy as np
import pandas as pd
from tqdm import tqdm

from aiasn.model_adapters.active_speaker_detector import ActiveSpeakerDetector
from aiasn.model_adapters.face_detector import FaceDetector
from aiasn.model_adapters.gender_estimator import GenderEstimator
from aiasn.model_adapters.ocr_model import OcrModel
from aiasn.model_adapters.person_tracker import PersonTracker
from aiasn.model_adapters.reidentificator import Reidentificator
from aiasn.model_adapters.shot_detector import ShotDetector
from aiasn.pipelines.base_pipeline import Pipeline
from aiasn.pipelines.context import RunContext
from aiasn.settings import VideoSettings


class VideoPipeline(Pipeline):
    name = "video"

    def __init__(self, cfg: VideoSettings):
        self.cfg = cfg
        self.shot_detector = ShotDetector(cfg.shot_detector, cfg.device)
        self.person_tracker = PersonTracker(cfg.person_tracker, cfg.device)
        self.face_detector = FaceDetector(cfg.face_detector, cfg.device)
        self.reidentificator = Reidentificator(cfg.reidentificator, cfg.device)
        self.speaker_detector = ActiveSpeakerDetector(cfg.active_speaker_detector, cfg.device)
        self.gender_estimator = GenderEstimator(cfg.gender_estimator, cfg.device)
        self.ocr = OcrModel(cfg.ocr, cfg.device)

    def run(self, ctx: RunContext) -> None:
        work = ctx.tmp_dir / self.name
        video, audio, frames = self._extract(ctx.lake.landing_file(ctx.video_id), work)
        self._log_step("extract", f"{len(frames)} frames ({len(frames) / self.cfg.fps:.0f} s)")

        cuts = self.shot_detector.detect_cuts(video)
        self._log_step("shots", f"{len(cuts) + 1} shots")

        detections, faces = self._detect(frames)
        detections.insert(1, "shot", np.searchsorted(cuts, detections["frame"], side="right"))
        # The tracker can keep a track_id across a cut: one new track per shot
        detections["track_id"] = detections.groupby(["shot", "track_id"]).ngroup() + 1
        self._log_step("detect", f"{len(detections)} people in {detections.frame.nunique()} frames, "
                                 f"{sum(map(len, faces))} faces in {len(faces)} frames")

        tracks = detections.track_id.nunique()
        detections.insert(3, "person_id", self._reidentify(detections))
        detections = detections.dropna(subset="person_id")
        self._log_step("reid", f"{tracks} tracks, {tracks - detections.track_id.nunique()} discarded, "
                               f"{detections.person_id.nunique()} people")

        speakers = self.speaker_detector.detect(frames, audio, faces, cuts)
        detections["speaking_score"] = self._speaking(detections, speakers)
        self._log_step("asd", f"{speakers.track.nunique()} face tracks, "
                              f"{(detections.speaking_score > 0).mean():.0%} of detections speaking")
        # Face embeddings are biometric data: never stored (ADR-004)
        ctx.lake.write("bronze", "video_detections", ctx.video_id, detections.drop(columns="embedding"))

        texts = self._read_texts(frames)
        texts.insert(1, "shot", np.searchsorted(cuts, texts["frame"], side="right"))
        ctx.lake.write("bronze", "video_texts", ctx.video_id, texts)
        self._log_step("ocr", f"{len(texts)} texts, {texts.text.nunique()} distinct")

    def _reidentify(self, detections: pd.DataFrame) -> pd.Series:
        """Person of each detection: tracks with the same face, in any shot, get the same id.

        Tracks that are too short or rarely show head or shoulders (hands, arms) get none and are discarded.
        Tracks without a face are one person each.
        """
        stats = detections.groupby("track_id").agg(n=("frame", "size"), head=("head", "mean"))
        seconds = stats.n * self.cfg.stride / self.cfg.fps
        keep = stats.index[(seconds >= self.cfg.min_track_seconds) & (stats["head"] >= self.cfg.min_head)]
        with_face = detections[detections.track_id.isin(keep)].dropna(subset="embedding")
        person = self.reidentificator.cluster({t: np.stack(g.embedding) for t, g in with_face.groupby("track_id")})
        next_id = max(person.values(), default=0) + 1
        for t in keep.difference(list(person)):
            person[t] = next_id
            next_id += 1
        return detections.track_id.map(person).astype("Int64")

    def _speaking(self, detections: pd.DataFrame, speakers: pd.DataFrame) -> pd.Series:
        """TalkNet score of each detection: the best of the tracked faces it owns in that frame (NaN if none)."""
        score = pd.Series(np.nan, index=detections.index)
        by_frame = speakers.groupby("frame")
        for f, people in detections.groupby("frame"):
            if f in by_frame.groups:
                faces = by_frame.get_group(f)
                owner = self._owner(people, faces)
                score.update(faces.score.loc[owner.index].groupby(owner).max())
        return score

    def _read_texts(self, frames: list[Path]) -> pd.DataFrame:
        """Text on screen in `ocr_fps` frames per second, except near the corners (logos, watermarks)."""
        step, c = max(1, round(self.cfg.fps / self.cfg.ocr_fps)), self.cfg.ocr_corner
        rows = []
        for f in range(0, len(frames), step):
            image = cv2.imread(str(frames[f]))
            texts = self.ocr.read(image)
            cx, cy = (texts.x1 + texts.x2) / 2 / image.shape[1], (texts.y1 + texts.y2) / 2 / image.shape[0]
            corner = ((cx < c) | (cx > 1 - c)) & ((cy < c) | (cy > 1 - c))
            rows.append(texts[~corner].assign(frame=f))
        return pd.concat(rows, ignore_index=True)[["frame", "text", "conf", "x1", "y1", "x2", "y2"]]

    def _detect(self, frames: list[Path]) -> tuple[pd.DataFrame, list[pd.DataFrame]]:
        """Faces in every frame (TalkNet needs them all) and people in 1 of every `stride` frames.

        Returns the people, with their face box and embedding, gender and age and the frame size, and the faces of each frame.
        """
        self.person_tracker.reset()
        rows, faces = [], []
        for f, path in enumerate(tqdm(frames, desc="detect", unit="frame", leave=False)):
            image = cv2.imread(str(path))
            faces.append(self.face_detector.detect(image))
            if f % self.cfg.stride != self.cfg.stride - 1:   # same sampling as the notebook
                continue
            people = self._assign_faces(self.person_tracker.track(image), faces[f])
            matched = people.face.dropna().astype(int)
            emb = self.reidentificator.embed(image, faces[f].loc[matched])
            people["embedding"] = pd.Series(list(emb), index=matched.index, dtype=object)
            people = people.join(self.gender_estimator.estimate(image, people))
            rows.append(people.assign(frame=f, frame_width=image.shape[1], frame_height=image.shape[0]))
        detections = pd.concat(rows, ignore_index=True)
        return detections[["frame", "track_id", "x1", "y1", "x2", "y2", "head",
                           "face_x1", "face_y1", "face_x2", "face_y2", "gender", "gender_prob", "age",
                           "frame_width", "frame_height", "embedding"]], faces

    @staticmethod
    def _assign_faces(people: pd.DataFrame, faces: pd.DataFrame) -> pd.DataFrame:
        """Each person gets the best-scored of the faces it owns (see `_owner`).

        `face` is the index of the assigned face in `faces`.
        """
        people = people.assign(face=np.nan, face_x1=np.nan, face_y1=np.nan, face_x2=np.nan, face_y2=np.nan)
        owner = VideoPipeline._owner(people, faces)
        for p, i in faces.score.loc[owner.index].groupby(owner).idxmax().items():
            people.loc[p, ["face", "face_x1", "face_y1", "face_x2", "face_y2"]] = [i, *faces.loc[i, ["x1", "y1", "x2", "y2"]]]
        return people

    @staticmethod
    def _owner(people: pd.DataFrame, faces: pd.DataFrame) -> pd.Series:
        """Person (index in `people`) of each face: the narrowest box containing its centre (as in the notebook).

        Faces outside every box are left out.
        """
        owner = {}
        for i, cx, cy in zip(faces.index, (faces.x1 + faces.x2) / 2, (faces.y1 + faces.y2) / 2):
            inside = people[(people.x1 <= cx) & (cx <= people.x2) & (people.y1 <= cy) & (cy <= people.y2)]
            if not inside.empty:
                owner[i] = (inside.x2 - inside.x1).idxmin()
        return pd.Series(owner, dtype=int)

    def _extract(self, source: Path, work: Path) -> tuple[Path, Path, list[Path]]:
        """Resampled video, mono audio and frames. Audio and frames come from the resampled video, as in the TalkNet demo."""
        video, audio, frames_dir = work / "video.avi", work / "audio.wav", work / "frames"
        frames_dir.mkdir(parents=True, exist_ok=True)
        self._ffmpeg("-i", str(source), "-qscale:v", "2", "-async", "1", "-r", str(self.cfg.fps), str(video))
        self._ffmpeg("-i", str(video), "-ac", "1", "-vn", "-ar", str(self.cfg.audio_sample_rate), str(audio))
        self._ffmpeg("-i", str(video), "-qscale:v", "2", "-f", "image2", str(frames_dir / "%06d.jpg"))
        return video, audio, sorted(frames_dir.glob("*.jpg"))

    @staticmethod
    def _ffmpeg(*args: str) -> None:
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", *args], check=True)


if __name__ == "__main__":
    # Usage: python -m aiasn.pipelines.video VIDEO_ID [--annotate]   (the video must be inside /data/landing/video_id={VIDEO_ID})
    from aiasn.pipelines.video_annotation import annotate
    from aiasn.settings import Settings
    from aiasn.storage.lake import Lake
    from aiasn.storage.manifest import Manifest

    parser = argparse.ArgumentParser()
    parser.add_argument("video_id")
    parser.add_argument("--annotate", action="store_true", help="also draw the results on the video, in tmp/")
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s", datefmt="%H:%M:%S")

    settings = Settings()
    ctx = RunContext(args.video_id, settings, Lake(settings.lake_dir), Manifest(settings.lake_dir, args.video_id),
                     settings.tmp_dir / args.video_id)
    VideoPipeline(settings.video)(ctx)
    if args.annotate:
        logging.getLogger("aiasn").info("annotated video: %s", annotate(ctx))
