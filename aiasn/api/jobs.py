# SPDX-FileCopyrightText: 2026 Equipo 1: Attention Is All She Needs (Alba Camiña García, Pilar de la Fuente Diez, Rocío Jiménez Villén)
# SPDX-License-Identifier: Apache-2.0

"""How the API starts the worker for a video. One video at a time: the GPU holds one."""

import subprocess
import sys
from typing import Protocol


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
