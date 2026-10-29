# SPDX-FileCopyrightText: 2026 Equipo 1: Attention Is All She Needs (Alba Camiña García, Pilar de la Fuente Diez, Rocío Jiménez Villén)
# SPDX-License-Identifier: Apache-2.0

"""Human review of a video (EU AI Act art. 14), in supervision/video_id=.../ of the lake: every decision is a new file,
never overwritten, so the history stays. It does not change the KPIs, computed in gold before the review."""

import hashlib
import json
from datetime import datetime, timezone

from aiasn.storage.lake import Lake

OPERATOR = "autodiagnostico_local"   # pseudonymous role, as in compliance.ElegibilidadEticaEntidad (no users in the demo)


def fingerprint(metrics: dict) -> str:
    """SHA-256 of the metrics the decision is about."""
    return hashlib.sha256(json.dumps(metrics, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()


def save(lake: Lake, video_id: str, decision: dict) -> dict:
    now = datetime.now(timezone.utc)
    record = decision | {"fecha": now.isoformat(), "operador_supervision_id": OPERATOR}
    folder = f"{lake.root}/supervision/video_id={video_id}"
    lake.fs.makedirs(folder, exist_ok=True)
    with lake.fs.open(f"{folder}/{now.strftime('%Y%m%dT%H%M%S%fZ')}.json", "w", encoding="utf-8") as f:
        json.dump(record, f, ensure_ascii=False)
    return record


def history(lake: Lake, video_id: str) -> list[dict]:
    """Every decision on `video_id`, oldest first."""
    folder = f"{lake.root}/supervision/video_id={video_id}"
    if not lake.fs.exists(folder):
        return []
    records = []
    for path in sorted(lake.fs.glob(f"{folder}/*.json")):
        with lake.fs.open(path, "r", encoding="utf-8") as f:
            records.append(json.load(f))
    return records
