# SPDX-FileCopyrightText: 2026 Equipo 1: Attention Is All She Needs (Alba Camiña García, Pilar de la Fuente Diez, Rocío Jiménez Villén)
# SPDX-License-Identifier: Apache-2.0
"""The worker (aiasn.run_pipelines) on one video, also counting the LLM tokens. Run by measure_demo.sh.

    python scripts/measure_run.py --video-id ID --force
    python scripts/measure_run.py --file video.mp4 --force

Where each measure comes from:
- Time of each step: the worker logs it itself, one line per step (`video  detect  203.9 s  ...`, time.perf_counter
  in aiasn/pipelines/base_pipeline.py). This script does not measure it.
- LLM tokens: the `usage` that OVHcloud AI Endpoints returns with each answer (prompt_tokens, completion_tokens),
  read by a LiteLLM success callback. Summed by model and response schema, printed at the end as one line
  `LLM_USAGE {json}`.
"""
import json
import sys
import threading
import time
from collections import defaultdict

import litellm

from aiasn.run_pipelines import main

lock = threading.Lock()
usage = defaultdict(lambda: {"calls": 0, "input": 0, "output": 0})


def count(kwargs, response, start, end):
    u = getattr(response, "usage", None)
    rf = kwargs.get("response_format")
    schema = rf.get("json_schema", {}).get("name", "?") if isinstance(rf, dict) else getattr(rf, "__name__", "?")
    with lock:
        row = usage[f"{kwargs.get('model')} | {schema}"]
        row["calls"] += 1
        row["input"] += getattr(u, "prompt_tokens", 0) or 0
        row["output"] += getattr(u, "completion_tokens", 0) or 0


litellm.success_callback = [count]
try:
    main(sys.argv[1:])
finally:
    time.sleep(3)   # LiteLLM runs the success callbacks in a background thread
    print("LLM_USAGE " + json.dumps(usage), flush=True)
