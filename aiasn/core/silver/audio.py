# SPDX-FileCopyrightText: 2026 Equipo 1: Attention Is All She Needs (Alba Camiña García, Pilar de la Fuente Diez, Rocío Jiménez Villén)
# SPDX-License-Identifier: Apache-2.0

"""Silver tables of the audio pipeline: one row per speaker, and the turns with the contract columns (ADR-0001)."""

import pandas as pd

from aiasn.core.silver.gender import UNDETERMINED, decide_gender, female_prob
from aiasn.core.transform import Transform

SPEAKERS = ["speaker_id", "genero", "prob_mujer", "speech_time_s", "n_turns"]
TURNS = ["turn", "tiempo_i", "tiempo_f", "speaker_id", "transcripcion", "genero_inferido"]


class AudioSilver(Transform):
    name, layer = "audio", "silver"
    inputs, outputs = ["bronze/audio_turns"], ["audio_speakers", "audio_turns"]

    def run(self, tables: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
        t = tables["bronze/audio_turns"]
        seconds, female = (t.end - t.start).clip(lower=0), female_prob(t.gender, t.gender_prob)
        rows = []
        for speaker, turns in t.groupby("speaker").groups.items():
            # Longer turns weigh more in the vote: more voice to judge by
            gender, p = decide_gender(female[turns], self.settings.silver.gender_threshold, weights=seconds[turns])
            rows.append([speaker, gender, p, seconds[turns].sum(), len(turns)])
        speakers = pd.DataFrame(rows, columns=SPEAKERS).astype({"speaker_id": "Int64", "n_turns": int})

        # Each turn takes the gender of its speaker; turns without speaker (no diarization) stay undetermined
        gender_of = speakers.set_index("speaker_id").genero
        contract = pd.DataFrame({"turn": t["turn"] if "turn" in t else range(len(t)),
                                 "tiempo_i": t.start, "tiempo_f": t.end, "speaker_id": t.speaker, "transcripcion": t.text,
                                 "genero_inferido": t.speaker.map(gender_of).astype(object).fillna(UNDETERMINED)})
        return {"audio_speakers": speakers, "audio_turns": contract[TURNS]}
