# SPDX-FileCopyrightText: 2026 Equipo 1: Attention Is All She Needs (Alba Camiña García, Pilar de la Fuente Diez, Rocío Jiménez Villén)
# SPDX-License-Identifier: Apache-2.0

# The worker: processes one video and exits. PyTorch and ONNX Runtime bring their own CUDA libraries, so a plain
# Python image works with the GPU (the host's driver comes through the NVIDIA Container Toolkit) and without it.
FROM python:3.13-slim AS build
COPY --from=ghcr.io/astral-sh/uv:0.10.11 /uv /bin/uv
RUN apt-get update && apt-get install -y --no-install-recommends build-essential git && rm -rf /var/lib/apt/lists/*
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy
WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --extra worker --no-install-project
COPY README.md ./
COPY aiasn aiasn
RUN uv sync --frozen --no-dev --extra worker

FROM python:3.13-slim
# git: TalkNet is cloned the first time; libgl/libglib: OpenCV; gcc: Triton (PyTorch on the GPU) compiles its kernels
RUN apt-get update && apt-get install -y --no-install-recommends ffmpeg gcc git libc6-dev libgl1 libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*
COPY --from=build /app /app
WORKDIR /app
# Models live in the models volume, downloaded the first time they are needed
ENV PATH=/app/.venv/bin:$PATH MODELS_DIR=/models HF_HOME=/models/huggingface
# The API runs it with --video-id; by hand: docker run aiasn-worker python -m aiasn.run_pipelines --help
CMD ["python", "-m", "aiasn.run_pipelines", "--help"]
