# SPDX-FileCopyrightText: 2026 Equipo 1: Attention Is All She Needs (Alba Camiña García, Pilar de la Fuente Diez, Rocío Jiménez Villén)
# SPDX-License-Identifier: Apache-2.0

# The worker: processes one video and exits. PyTorch and ONNX Runtime bring their own CUDA libraries, so a plain
# Python image works with the GPU (the host's driver comes through the NVIDIA Container Toolkit) and without it.
# DEVICE=cpu builds it without those libraries, for machines with no NVIDIA GPU: the same locked versions, much smaller.
FROM python:3.13-slim AS build
ARG DEVICE=gpu
COPY --from=ghcr.io/astral-sh/uv:0.10.11 /uv /bin/uv
RUN apt-get update && apt-get install -y --no-install-recommends build-essential git && rm -rf /var/lib/apt/lists/*
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy
WORKDIR /app
COPY pyproject.toml uv.lock ./
# cpu: everything in uv.lock except the CUDA packages, then PyTorch from its CPU index and onnxruntime for onnxruntime-gpu
# (--no-config there: the overrides of pyproject.toml would drop onnxruntime on x86_64)
RUN if [ "$DEVICE" = cpu ]; then \
        uv export --frozen --no-dev --extra worker --no-emit-project --no-hashes -o all.txt \
        && grep -v -E '^(torch|torchvision|triton|cuda-[a-z-]+|onnxruntime-gpu|nvidia-[a-z0-9-]+)==' all.txt > cpu.txt \
        && grep -E '^nvidia-ml-py==' all.txt >> cpu.txt \
        && uv venv && uv pip install --no-deps -r cpu.txt \
        && uv pip install --no-deps --index-url https://download.pytorch.org/whl/cpu \
            $(grep -o -E '^(torch|torchvision)==[^ ]+' all.txt | sed 's/$/+cpu/') \
        && uv pip install --no-config --no-deps $(grep -o -E '^onnxruntime-gpu==[^ ]+' all.txt | sed 's/-gpu//') \
        && rm all.txt cpu.txt; \
    else \
        uv sync --frozen --no-dev --extra worker --no-install-project; \
    fi

FROM python:3.13-slim
# git: TalkNet is cloned the first time; libgl/libglib: OpenCV; gcc: Triton (PyTorch on the GPU) compiles its kernels
RUN apt-get update && apt-get install -y --no-install-recommends ffmpeg gcc git libc6-dev libgl1 libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*
# The dependencies (~7 GB with CUDA, ~1.5 GB without) and the code in separate layers: a code change rebuilds only the small one. The project
# runs from /app (PYTHONPATH), not installed in the venv, so the venv layer does not change with the code.
COPY --from=build /app/.venv /app/.venv
WORKDIR /app
COPY aiasn aiasn
# Models live in the models volume, downloaded the first time they are needed
ENV PATH=/app/.venv/bin:$PATH PYTHONPATH=/app MODELS_DIR=/models HF_HOME=/models/huggingface
# The API runs it with --video-id; by hand: docker run aiasn-worker python -m aiasn.run_pipelines --help
CMD ["python", "-m", "aiasn.run_pipelines", "--help"]
