'''Video pipeline results drawn on the video, to check them by eye (debug only: written to tmp, never to the lake)'''

import subprocess
import unicodedata
from pathlib import Path

import cv2
import pandas as pd
from tqdm import tqdm

from aiasn.pipelines.context import RunContext

COLOR = {"F": (161, 86, 99), "M": (176, 143, 46)}   # BGR
SPEAKING, TEXT, WHITE = (0, 255, 0), (0, 255, 255), (255, 255, 255)
FONT = cv2.FONT_HERSHEY_SIMPLEX


def annotate(ctx: RunContext) -> Path:
    """Each person as `P<id> | gender | age`, in green while speaking, and the texts read by the OCR.

    Gender and age are the most common and median values of each person. Returns the annotated mp4.
    """
    cfg, work = ctx.settings.video, ctx.tmp_dir / "video"
    detections = ctx.lake.read("bronze", "video_detections", ctx.video_id)
    texts = ctx.lake.read("bronze", "video_texts", ctx.video_id)
    person = detections.groupby("person_id").agg(gender=("gender", lambda g: g.mode()[0]), age=("age", "median"))

    frames = sorted((work / "frames").glob("*.jpg"))
    raw, out = work / "annotated.avi", work / "annotated.mp4"
    writer = cv2.VideoWriter(str(raw), cv2.VideoWriter_fourcc(*"XVID"), cfg.fps, cv2.imread(str(frames[0])).shape[1::-1])
    people_at, texts_at = detections.groupby("frame"), texts.groupby("frame")
    people, words = pd.DataFrame(), pd.DataFrame()
    for f, path in enumerate(tqdm(frames, desc="annotate", unit="frame", leave=False)):
        image = cv2.imread(str(path))
        if f % cfg.stride == cfg.stride - 1:   # analysed frame: its detections last until the next one
            people = people_at.get_group(f) if f in people_at.groups else pd.DataFrame()
        if f in texts_at.groups:
            words = texts_at.get_group(f)
        for r in people.itertuples():
            p = person.loc[r.person_id]
            color = SPEAKING if r.speaking_score > 0 else COLOR[p.gender]
            cv2.rectangle(image, (int(r.x1), int(r.y1)), (int(r.x2), int(r.y2)), color, 2)
            cv2.putText(image, f"P{r.person_id} | {p.gender} | {p.age:.0f}", (int(r.x1) + 5, int(r.y1) + 20), FONT, 0.6, WHITE, 2)
        for t in words.itertuples():
            cv2.rectangle(image, (int(t.x1), int(t.y1)), (int(t.x2), int(t.y2)), TEXT, 1)
            cv2.putText(image, _ascii(t.text), (int(t.x1), max(int(t.y1) - 5, 12)), FONT, 0.5, TEXT, 1)
        writer.write(image)
    writer.release()
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(raw), "-i", str(work / "audio.wav"),
                    "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac", str(out)], check=True)
    raw.unlink()
    return out


def _ascii(text: str) -> str:
    """OpenCV cannot draw accents or ñ."""
    return unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
