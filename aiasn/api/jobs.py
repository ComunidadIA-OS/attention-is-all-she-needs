# SPDX-FileCopyrightText: 2026 Equipo 1: Attention Is All She Needs (Alba Camiña García, Pilar de la Fuente Diez, Rocío Jiménez Villén)
# SPDX-License-Identifier: Apache-2.0

"""How the API starts the worker for a video. One video at a time: the GPU holds one."""

import logging
import os
import subprocess
import sys
from typing import Protocol

from aiasn.settings import ApiSettings, WorkerContainerSettings

log = logging.getLogger("aiasn")
LABEL = "aiasn.worker"


class Launcher(Protocol):
    def launch(self, video_id: str) -> None: ...

    def busy(self) -> bool:
        """A video is being processed."""


class ProcessLauncher:
    """The worker as a child process of the API, in the same environment (no Docker)."""

    def __init__(self):
        self._process: subprocess.Popen | None = None

    def launch(self, video_id: str) -> None:
        self._process = subprocess.Popen([sys.executable, "-m", "aiasn.run_pipelines", "--video-id", video_id])

    def busy(self) -> bool:
        return self._process is not None and self._process.poll() is None


class DockerLauncher:
    """The worker as a container started through the Docker socket, removed on the next launch (its logs stay until
    then: `docker logs aiasn-worker-<video_id>`)."""

    def __init__(self, cfg: WorkerContainerSettings, client=None):
        import docker
        self.cfg, self.client = cfg, client or docker.from_env()

    def launch(self, video_id: str) -> None:
        from docker.types import DeviceRequest
        for old in self.client.containers.list(all=True, filters={"label": LABEL, "status": "exited"}):
            old.remove()
        self.client.containers.run(
            self.cfg.image, ["python", "-m", "aiasn.run_pipelines", "--video-id", video_id],
            name=f"aiasn-worker-{video_id}", labels={LABEL: video_id}, detach=True,
            environment=worker_env(self.cfg.env, os.environ), network=self.cfg.network,
            volumes={src: {"bind": dst, "mode": "rw"} for src, dst in self.cfg.volumes.items()},
            device_requests=[DeviceRequest(count=-1, capabilities=[["gpu"]])] if self.cfg.gpu else None)

    def busy(self) -> bool:
        return bool(self.client.containers.list(filters={"label": LABEL, "status": "running"}))


def worker_env(names: list[str], environ: dict[str, str]) -> dict[str, str]:
    """The variables of `environ` named in `names`, exactly or by prefix (ending in _), case-insensitive."""
    wanted = [n.upper() for n in names]
    return {k: v for k, v in environ.items()
            if any(k.upper() == n or (n.endswith("_") and k.upper().startswith(n)) for n in wanted)}


def make_launcher(cfg: ApiSettings) -> Launcher:
    if cfg.launcher != "process":
        try:
            launcher = DockerLauncher(cfg.worker)
            launcher.client.images.get(cfg.worker.image)
            log.info("Worker: container %s", cfg.worker.image)
            return launcher
        except Exception as e:
            if cfg.launcher == "docker":
                raise
            log.info("Worker: child process (Docker or the image %s not available: %r)", cfg.worker.image, e)
    return ProcessLauncher()
