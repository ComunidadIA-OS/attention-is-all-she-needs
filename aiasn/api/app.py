# SPDX-FileCopyrightText: 2026 Equipo 1: Attention Is All She Needs (Alba Camiña García, Pilar de la Fuente Diez, Rocío Jiménez Villén)
# SPDX-License-Identifier: Apache-2.0

"""The API: upload a video, which starts the worker, and poll its status until the results come.

    uvicorn aiasn.api.app:create_app --factory --host 0.0.0.0 --port 8000
"""

import logging
import re
import secrets
import threading
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from aiasn.api import schemas
from aiasn.api.jobs import Launcher, make_launcher
from aiasn.settings import Settings
from aiasn.storage.lake import Lake
from aiasn.storage.manifest import ERROR, OK, QUEUED, Manifest

VIDEO_ID = re.compile(r"[A-Za-z0-9_-]+")


def new_video_id(filename: str) -> str:
    """The file name as a slug plus a random suffix: readable, and two uploads of one file do not collide."""
    slug = re.sub(r"[^a-z0-9]+", "-", Path(filename).stem.lower()).strip("-")[:40] or "video"
    return f"{slug}-{secrets.token_hex(2)}"


def create_app(settings: Settings | None = None, launcher: Launcher | None = None) -> FastAPI:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s", datefmt="%H:%M:%S")
    settings = settings or Settings()
    launcher = launcher or make_launcher(settings.api)
    lake = Lake.from_settings(settings)
    lock = threading.Lock()   # busy() and launch() as one step: two uploads at once start one worker

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        lake.fs.makedirs(lake.root, exist_ok=True)   # the bucket, in an S3 store
        yield

    app = FastAPI(title="AIASN", lifespan=lifespan)
    app.add_middleware(CORSMiddleware, allow_origins=settings.api.cors_origins, allow_methods=["*"],
                       allow_headers=["*"])

    @app.get("/health")
    def health() -> dict:
        return {"ok": True}

    @app.post("/videos", status_code=202)
    def upload(file: UploadFile) -> dict:
        if Path(file.filename or "").suffix.lower() not in settings.api.upload_formats:
            raise HTTPException(400, f"Not a video: use one of {', '.join(settings.api.upload_formats)}")
        if launcher.busy():   # before storing the upload
            raise HTTPException(409, "Another video is being processed")
        video_id = new_video_id(file.filename)
        lake.write_landing(video_id, f"{video_id}{Path(file.filename).suffix.lower()}", file.file)
        manifest = Manifest(lake, video_id)
        manifest.set_status(QUEUED)
        with lock:
            if launcher.busy():
                manifest.set_status(ERROR, RuntimeError("Another video started first"))
                raise HTTPException(409, "Another video is being processed")
            try:
                launcher.launch(video_id)
            except Exception as e:
                manifest.set_status(ERROR, e)
                raise HTTPException(500, f"The worker could not start: {e!r}")
        return {"video_id": video_id}

    @app.get("/videos")
    def videos() -> list[dict]:
        """Every video in the lake with its status, latest first: a video already analysed opens without processing
        it again."""
        found = [(video_id, Manifest.load(lake, video_id)) for video_id in Manifest.video_ids(lake)]
        started = lambda m: max((s.get("started_at") or "" for s in m["steps"].values()), default="")
        found.sort(key=lambda vm: started(vm[1]), reverse=True)
        return [{"video_id": video_id, "estado": m["status"], "inicio": started(m) or None} for video_id, m in found]

    @app.get("/videos/{video_id}")
    def video(video_id: str) -> dict:
        manifest = Manifest.load(lake, video_id) if VIDEO_ID.fullmatch(video_id) else None
        if manifest is None:
            raise HTTPException(404, "Unknown video")
        done = manifest["status"] == OK
        return {"video_id": video_id, "status": schemas.status(manifest),
                "resultado": schemas.result(lake, video_id) if done else None}

    return app
