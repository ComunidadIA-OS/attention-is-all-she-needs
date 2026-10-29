#!/usr/bin/env bash
# SPDX-FileCopyrightText: 2026 Equipo 1: Attention Is All She Needs (Alba Camiña García, Pilar de la Fuente Diez, Rocío Jiménez Villén)
# SPDX-License-Identifier: Apache-2.0
#
# The demo videos through the worker image, one after the other, as measured for DATASET_CARD.md (1.2).
#   scripts/measure_demo.sh VIDEOS_DIR OUT_DIR
#   python scripts/measure_table.py OUT_DIR/*.log
# Needs `docker compose --profile jobs build` and `docker compose up -d` (the store), and .env with the OVHcloud token.
#
# Where each measure comes from (one log per video in OUT_DIR):
# - SHA-256 of each file: sha256sum, in OUT_DIR/sha256.txt.
# - Total time: wall time of `docker run` (container start and model loading included), measured here with
#   `date +%s` and appended to the log as `seconds=N`.
# - Time of each step and audio length: the worker's own log lines; LLM tokens: the LLM_USAGE line (see measure_run.py).
set -euo pipefail
videos=$(realpath "$1"); out=$(realpath "$2"); repo=$(realpath "$(dirname "$0")/..")
mkdir -p "$out"
(cd "$videos" && sha256sum ./*.mp4) > "$out/sha256.txt"

for video in "$videos"/*.mp4; do
  name=$(basename "$video" .mp4)
  start=$(date +%s)
  status=0
  docker run --rm --gpus all --network aiasn --env-file "$repo/.env" -e LANGFUSE_ENABLED=false \
    -e LAKE_URI=s3://aiasn -e STORAGE__ENDPOINT_URL=http://store:8333 \
    -e STORAGE__ACCESS_KEY="${S3_ACCESS_KEY:-aiasn}" -e STORAGE__SECRET_KEY="${S3_SECRET_KEY:-aiasn-secret}" \
    -e MODELS_DIR=/models -e HF_HOME=/models/huggingface \
    -v aiasn-models:/models -v "$repo/scripts:/scripts:ro" -v "$videos:/videos:ro" \
    aiasn-worker python /scripts/measure_run.py --file "/videos/$name.mp4" --force > "$out/$name.log" 2>&1 || status=$?
  echo "exit=$status seconds=$(( $(date +%s) - start ))" | tee -a "$out/$name.log"
done
