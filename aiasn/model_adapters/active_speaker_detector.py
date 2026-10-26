'''Model used to detect who is speaking (TalkNet), adapted from demoTalkNet.py (https://github.com/TaoRuijie/TalkNet-ASD)'''

import logging
import subprocess
import sys
from pathlib import Path

import cv2
import gdown
import numpy as np
import pandas as pd
import python_speech_features
import torch
from scipy import signal
from scipy.io import wavfile

from aiasn.settings import ActiveSpeakerDetectorSettings

log = logging.getLogger("aiasn")

REPO = "https://github.com/TaoRuijie/TalkNet-ASD.git"
WEIGHTS_ID = "1AbN9fCf9IexMxEKXLQY2KYBlb-IhSEea"   # pretrain_TalkSet.model on Google Drive
FPS, MFCC_PER_SECOND = 25, 100                     # TalkNet works at 25 fps and 100 MFCC frames per second
# Face tracking and cropping as in the demo
MIN_TRACK, MAX_GAP, MIN_IOU, MIN_FACE_SIZE, CROP_SCALE = 10, 10, 0.5, 1, 0.40
DURATIONS = (1, 2, 3, 4, 5, 6)                     # seconds per chunk; scores are averaged over all of them


class ActiveSpeakerDetector:
    def __init__(self, cfg: ActiveSpeakerDetectorSettings, device: str = "auto"):
        self.cfg = cfg
        self.device = torch.device(("cuda" if torch.cuda.is_available() else "cpu") if device == "auto" else device)
        weights = self._ensure_repo(cfg.repo_dir)
        sys.path.insert(0, str(cfg.repo_dir))
        from loss import lossAV
        from model.talkNetModel import talkNetModel

        self.model = torch.nn.Module()
        self.model.model, self.model.lossAV = talkNetModel(), lossAV()
        state = torch.load(weights, map_location="cpu")
        self.model.load_state_dict({k: v for k, v in state.items() if k.startswith(("model.", "lossAV."))})
        self.model.to(self.device).eval()

    def detect(self, frames: list[Path], audio: Path, faces: list[pd.DataFrame], cuts: list[int]) -> pd.DataFrame:
        """One row per tracked face and frame: face track, smoothed box (x1, y1, x2, y2) and speaking score (> 0 = speaking).

        `faces` holds the faces of every frame (FaceDetector.detect) and `cuts` the frames where a shot starts.
        Frames must be at 25 fps and audio at 16 kHz.
        """
        rate, wav = wavfile.read(audio)
        mfcc = python_speech_features.mfcc(wav, rate, numcep=13, winlen=0.025, winstep=0.010)
        bounds = [0, *cuts, len(frames)]
        rows = []
        for a, b in zip(bounds[:-1], bounds[1:]):
            for track_frames, boxes in self._track_shot(faces[a:b], a):
                video, x, y, s = self._crop(frames, track_frames, boxes)
                score = self._score(mfcc[track_frames[0] * 4: (track_frames[-1] + 1) * 4], video)
                smooth = [score[max(i - 2, 0): i + 3].mean() for i in range(len(score))]   # ±2 frames, as the demo
                n = len(score)   # the last frames may have no audio left
                rows.append(pd.DataFrame({"frame": track_frames[:n], "track": len(rows), "x1": (x - s)[:n], "y1": (y - s)[:n],
                                          "x2": (x + s)[:n], "y2": (y + s)[:n], "score": smooth}))
        columns = ["frame", "track", "x1", "y1", "x2", "y2", "score"]
        return pd.concat(rows, ignore_index=True)[columns] if rows else pd.DataFrame(columns=columns, dtype=float)

    @staticmethod
    def _track_shot(faces: list[pd.DataFrame], start: int) -> list[tuple[np.ndarray, np.ndarray]]:
        """Face tracks of one shot: greedy IoU linking frame to frame, with gaps interpolated. Frames and boxes of each."""
        pending = [list(f[["x1", "y1", "x2", "y2"]].to_numpy()) for f in faces]
        tracks = []
        while True:
            track = []
            for f, frame_faces in enumerate(pending, start):
                if track and f - track[-1][0] > MAX_GAP:
                    break
                for k, box in enumerate(frame_faces):
                    if not track or _iou(box, track[-1][1]) > MIN_IOU:
                        track.append((f, frame_faces.pop(k)))
                        break
            if not track:
                return tracks
            if len(track) > MIN_TRACK:
                known, boxes = np.array([t[0] for t in track]), np.stack([t[1] for t in track])
                every = np.arange(known[0], known[-1] + 1)
                boxes = np.stack([np.interp(every, known, boxes[:, j]) for j in range(4)], axis=1)
                if max((boxes[:, 2] - boxes[:, 0]).mean(), (boxes[:, 3] - boxes[:, 1]).mean()) > MIN_FACE_SIZE:
                    tracks.append((every, boxes))

    @staticmethod
    def _crop(frames: list[Path], track_frames: np.ndarray, boxes: np.ndarray) -> tuple[np.ndarray, ...]:
        """Grey 112x112 face crops of a track, and the smoothed centre (x, y) and half size (s) of its box."""
        s = signal.medfilt(np.maximum(boxes[:, 3] - boxes[:, 1], boxes[:, 2] - boxes[:, 0]) / 2, kernel_size=13)
        x = signal.medfilt((boxes[:, 0] + boxes[:, 2]) / 2, kernel_size=13)
        y = signal.medfilt((boxes[:, 1] + boxes[:, 3]) / 2, kernel_size=13)
        crops = []
        for f, bs, mx, my in zip(track_frames, s, x, y):
            pad = int(bs * (1 + 2 * CROP_SCALE))
            image = np.pad(cv2.imread(str(frames[f]), cv2.IMREAD_GRAYSCALE), pad, constant_values=110)
            mx, my = mx + pad, my + pad
            face = image[int(my - bs):int(my + bs * (1 + 2 * CROP_SCALE)),
                         int(mx - bs * (1 + CROP_SCALE)):int(mx + bs * (1 + CROP_SCALE))]
            crops.append(cv2.resize(face, (224, 224))[56:168, 56:168])
        return np.array(crops), x, y, s

    def _score(self, audio: np.ndarray, video: np.ndarray) -> np.ndarray:
        """Speaking score of each frame of a face track, given its MFCC and face crops."""
        length = min((len(audio) - len(audio) % 4) / MFCC_PER_SECOND, len(video) / FPS)
        audio, video = audio[:round(length * MFCC_PER_SECOND)], video[:round(length * FPS)]
        net = self.model.model
        scores = []
        with torch.no_grad():
            for d in DURATIONS:
                chunks = []
                for i in range(int(np.ceil(length / d))):
                    a = torch.FloatTensor(audio[i * d * MFCC_PER_SECOND:(i + 1) * d * MFCC_PER_SECOND]).unsqueeze(0)
                    v = torch.FloatTensor(video[i * d * FPS:(i + 1) * d * FPS]).unsqueeze(0)
                    ea, ev = net.forward_audio_frontend(a.to(self.device)), net.forward_visual_frontend(v.to(self.device))
                    ea, ev = net.forward_cross_attention(ea, ev)
                    chunks.extend(self.model.lossAV(net.forward_audio_visual_backend(ea, ev)))
                scores.append(chunks)
        return np.mean(scores, axis=0)

    @staticmethod
    def _ensure_repo(repo_dir: Path) -> Path:
        """Clone TalkNet and download its weights if missing. Returns the weights file."""
        if not repo_dir.is_dir():
            log.info("Downloading TalkNet into %s", repo_dir)
            subprocess.run(["git", "clone", "-q", "--depth", "1", REPO, str(repo_dir)], check=True)
        weights = repo_dir / "pretrain_TalkSet.model"
        if not weights.is_file():
            gdown.download(id=WEIGHTS_ID, output=str(weights))
        return weights


def _iou(a: np.ndarray, b: np.ndarray) -> float:
    w, h = max(0, min(a[2], b[2]) - max(a[0], b[0])), max(0, min(a[3], b[3]) - max(a[1], b[1]))
    inter = w * h
    return inter / ((a[2] - a[0]) * (a[3] - a[1]) + (b[2] - b[0]) * (b[3] - b[1]) - inter)
