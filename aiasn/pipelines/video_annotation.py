'''Video pipeline results drawn on the video, to check them by eye (debug only: written to tmp, never to the lake)'''

import subprocess
import unicodedata
from pathlib import Path

import cv2
import pandas as pd
from tqdm import tqdm

from aiasn.pipelines.context import RunContext

COLOR = {"F": (161, 86, 99), "M": (176, 143, 46)}   # BGR
SPEAKING, TEXT, WHITE = (0, 200, 0), (0, 255, 255), (255, 255, 255)
FONT = cv2.FONT_HERSHEY_SIMPLEX


def annotate(ctx: RunContext) -> Path:
    """Each person's box labelled `P<id> | gender | age`, a green "speaking" box on the face of whoever speaks,
    and the texts read by the OCR.

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
    ocr_step = max(1, round(cfg.fps / cfg.ocr_fps))   # same sampling as the pipeline
    people, words = pd.DataFrame(), pd.DataFrame()
    for f, path in enumerate(tqdm(frames, desc="annotate", unit="frame", leave=False)):
        image = cv2.imread(str(path))
        # Results last until the next frame that was analysed, also when nothing was found there
        if f % cfg.stride == cfg.stride - 1:
            people = people_at.get_group(f) if f in people_at.groups else pd.DataFrame()
        if f % ocr_step == 0:
            words = texts_at.get_group(f) if f in texts_at.groups else pd.DataFrame()
        for r in people.itertuples():
            p = person.loc[r.person_id]
            x1, y1 = int(r.x1), int(r.y1)
            cv2.rectangle(image, (x1, y1), (int(r.x2), int(r.y2)), COLOR[p.gender], 3)
            _label(image, f"P{r.person_id} | {p.gender} | {p.age:.0f}", x1, y1, COLOR[p.gender])
            if r.speaking_score > 0:
                if pd.notna(r.face_x1):
                    fx1, fy1 = int(r.face_x1), int(r.face_y1)
                    cv2.rectangle(image, (fx1, fy1), (int(r.face_x2), int(r.face_y2)), SPEAKING, 2)
                    _label(image, "speaking", fx1, int(r.face_y2) + 22, SPEAKING)
                else:
                    _label(image, "speaking", x1, y1 + 24, SPEAKING)
        for t in words.itertuples():
            cv2.rectangle(image, (int(t.x1), int(t.y1)), (int(t.x2), int(t.y2)), TEXT, 1)
            cv2.putText(image, _ascii(t.text), (int(t.x1), max(int(t.y1) - 5, 12)), FONT, 0.5, TEXT, 1)
        writer.write(image)
    writer.release()
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(raw), "-i", str(work / "audio.wav"),
                    "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac", str(out)], check=True)
    raw.unlink()
    return out


def _label(image, text: str, x: int, y: int, color: tuple) -> None:
    """White text on a filled box of `color`, whose top-left corner is (x, y - box height)."""
    (w, h), base = cv2.getTextSize(text, FONT, 0.55, 1)
    y = max(y, h + base + 4)   # keep it inside the frame
    cv2.rectangle(image, (x, y - h - base - 4), (x + w + 8, y), color, -1)
    cv2.putText(image, text, (x + 4, y - base - 2), FONT, 0.55, WHITE, 1, cv2.LINE_AA)


def _ascii(text: str) -> str:
    """OpenCV cannot draw accents or ñ."""
    return unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()


if __name__ == "__main__":
    # Usage: python -m aiasn.pipelines.video_annotation VIDEO_ID   (after the video pipeline, while tmp/ still has its frames)
    import argparse

    from aiasn.settings import Settings

    parser = argparse.ArgumentParser()
    parser.add_argument("video_id")
    video_id = parser.parse_args().video_id
    settings = Settings()
    ctx = RunContext.for_video(settings, video_id, force=True)   # run by hand: redo it
    print(annotate(ctx))
