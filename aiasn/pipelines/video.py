import subprocess
from pathlib import Path

import cv2
import numpy as np
import pandas as pd

from aiasn.model_adapters.face_detector import FaceDetector
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

    def run(self, ctx: RunContext) -> None:
        work = ctx.tmp_dir / self.name
        video, audio, frames = self._extract(ctx.lake.landing_file(ctx.video_id), work)

        cuts = self.shot_detector.detect_cuts(video)
        detections, faces = self._detect(frames)
        detections.insert(1, "shot", np.searchsorted(cuts, detections["frame"], side="right"))
        # The tracker can keep a track_id across a cut: one new track per shot
        detections["track_id"] = detections.groupby(["shot", "track_id"]).ngroup() + 1
        detections.insert(3, "person_id", self._reidentify(detections))
        detections = detections.dropna(subset="person_id")
        # Face embeddings are biometric data: never stored (ADR-004)
        ctx.lake.write("bronze", "video_detections", ctx.video_id, detections.drop(columns="embedding"))

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

    def _detect(self, frames: list[Path]) -> tuple[pd.DataFrame, list[pd.DataFrame]]:
        """Faces in every frame (TalkNet needs them all) and people in 1 of every `stride` frames.

        Returns the people, with their face box and embedding and the frame size, and the faces of each frame.
        """
        self.person_tracker.reset()
        rows, faces = [], []
        for f, path in enumerate(frames):
            image = cv2.imread(str(path))
            faces.append(self.face_detector.detect(image))
            if f % self.cfg.stride != self.cfg.stride - 1:   # same sampling as the notebook
                continue
            people = self._assign_faces(self.person_tracker.track(image), faces[f])
            matched = people.face.dropna().astype(int)
            emb = self.reidentificator.embed(image, faces[f].loc[matched])
            people["embedding"] = pd.Series(list(emb), index=matched.index, dtype=object)
            rows.append(people.assign(frame=f, frame_width=image.shape[1], frame_height=image.shape[0]))
        detections = pd.concat(rows, ignore_index=True)
        return detections[["frame", "track_id", "x1", "y1", "x2", "y2", "head",
                           "face_x1", "face_y1", "face_x2", "face_y2", "frame_width", "frame_height", "embedding"]], faces

    @staticmethod
    def _assign_faces(people: pd.DataFrame, faces: pd.DataFrame) -> pd.DataFrame:
        """Each face goes to the narrowest person box containing its centre (as in the notebook); best score wins.

        `face` is the index of the assigned face in `faces`.
        """
        people = people.assign(face=np.nan, face_x1=np.nan, face_y1=np.nan, face_x2=np.nan, face_y2=np.nan)
        best: dict[int, tuple] = {}
        for face in faces.itertuples():
            cx, cy = (face.x1 + face.x2) / 2, (face.y1 + face.y2) / 2
            inside = people[(people.x1 <= cx) & (cx <= people.x2) & (people.y1 <= cy) & (cy <= people.y2)]
            if inside.empty:
                continue
            p = (inside.x2 - inside.x1).idxmin()
            if p not in best or face.score > best[p].score:
                best[p] = face
        for p, face in best.items():
            people.loc[p, ["face", "face_x1", "face_y1", "face_x2", "face_y2"]] = [face.Index, face.x1, face.y1, face.x2, face.y2]
        return people

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
