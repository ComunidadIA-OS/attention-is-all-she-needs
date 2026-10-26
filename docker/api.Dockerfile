# SPDX-FileCopyrightText: 2026 Equipo 1: Attention Is All She Needs (Alba Camiña García, Pilar de la Fuente Diez, Rocío Jiménez Villén)
# SPDX-License-Identifier: Apache-2.0

# The API: light, no models. It starts a worker container per video through the Docker socket.
FROM python:3.13-slim
COPY --from=ghcr.io/astral-sh/uv:0.10.11 /uv /bin/uv
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy PATH=/app/.venv/bin:$PATH
WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --extra api --no-install-project
COPY README.md ./
COPY aiasn aiasn
RUN uv sync --frozen --no-dev --extra api
EXPOSE 8000
CMD ["uvicorn", "aiasn.api.app:create_app", "--factory", "--host", "0.0.0.0", "--port", "8000"]
