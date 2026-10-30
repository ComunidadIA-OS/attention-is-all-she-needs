# SPDX-FileCopyrightText: 2026 Equipo 1: Attention Is All She Needs (Alba Camiña García, Pilar de la Fuente Diez, Rocío Jiménez Villén)
# SPDX-License-Identifier: Apache-2.0
"""Times and LLM tokens of each video, as the Markdown tables of DATASET_CARD.md (1.2), from the logs of measure_demo.sh.

    python scripts/measure_table.py OUT_DIR/*.log

It only reads the logs; each column comes from:
- Audio: the line of the `audio extract` step ("218 s of audio").
- Total: the `seconds=N` line that measure_demo.sh appends (wall time of the container). Logs without it fall back to
  the time from the first step to the last, which leaves out the container start (~20 s less).
- Transcription, video (detection, speaker, OCR), NLP, captions, silver + gold: the seconds of each step's line,
  as the worker logs them (`total` of each pipeline; silver and gold added up).
- LLM calls and tokens: the `LLM_USAGE` line of measure_run.py, added up by model (gpt-oss-120b only does references).
"""
import json
import re
import sys
from collections import defaultdict
from datetime import datetime
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path

STEP = re.compile(r"(\d\d:\d\d:\d\d) (\w+) +(\w+) +([\d.]+) s(?:  (.*))?$")   # the worker logs one line per step
REFERENCES = "gpt-oss-120b"


def parse(log: Path) -> dict:
    text = log.read_text(errors="replace")
    steps, stamps, usage, audio = {}, [], {}, 0
    for line in re.split(r"[\r\n]+", text):
        if m := STEP.search(line):
            stamps.append(datetime.strptime(m[1], "%H:%M:%S"))
            steps[f"{m[2]}.{m[3]}"] = float(m[4])
            if (m[2], m[3]) == ("audio", "extract"):
                audio = int(m[5].split()[0])   # "218 s of audio"
        elif line.startswith("LLM_USAGE "):
            usage = json.loads(line.removeprefix("LLM_USAGE "))
    if m := re.search(r"seconds=(\d+)", text):   # wall time of the container, written by measure_demo.sh
        total = int(m[1])
    else:   # older logs: from the first step to the last, without the container start
        total = (stamps[-1] - stamps[0]).seconds
    llm = defaultdict(lambda: [0, 0, 0])
    for key, u in usage.items():   # "model | schema"
        model = REFERENCES if key.startswith(REFERENCES) else "llama"
        for i, field in enumerate(("calls", "input", "output")):
            llm[model][i] += u[field]
    return {"steps": steps, "audio": audio, "total": total, "llm": llm}


def num(x: float) -> str:
    """Rounded half up, in Spanish format: 9.134 and 0,4"""
    if x < 1:
        return f"{x:.1f}".replace(".", ",")
    return f"{Decimal(str(x)).quantize(Decimal(1), ROUND_HALF_UP):,}".replace(",", ".")


def main(logs: list[str]) -> None:
    times = ["| Fichero | Audio | Total | Audio (transcripción) | Vídeo: detección · hablante · OCR | NLP | Rótulos | Silver + gold |",
             "|---|---|---|---|---|---|---|---|"]
    tokens = ["| Fichero | Llama 3.3 70B: llamadas · entrada · salida | gpt-oss-120b (referentes): llamadas · entrada · salida |",
              "|---|---|---|"]
    for log in map(Path, logs):
        r = parse(log)
        s = r["steps"]
        audio = f"{r['audio'] / 60:.1f}".replace(".", ",")
        times.append(f"| `{log.stem}.mp4` | {audio} min | {r['total']} | {num(s['audio.total'])} | "
                     f"{num(s['video.total'])}: {num(s['video.detect'])} · {num(s['video.asd'])} · {num(s['video.ocr'])} | "
                     f"{num(s['nlp.total'])} | {num(s['captions.total'])} | {num(s['silver.total'] + s['gold.total'])} |")
        tokens.append(f"| `{log.stem}.mp4` | " + " | ".join(" · ".join(num(v) for v in r["llm"][m]) for m in ("llama", REFERENCES)) + " |")
    print("\n".join(times), "", "\n".join(tokens), sep="\n")


if __name__ == "__main__":
    main(sys.argv[1:])
