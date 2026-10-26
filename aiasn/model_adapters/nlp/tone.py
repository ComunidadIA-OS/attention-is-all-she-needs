'''Task 8: discursive register of each turn (technical/assertive, collaborative, dissent), from the text only (ADR-009)'''

from typing import Literal

import pandas as pd
from pydantic import BaseModel, Field

from aiasn.model_adapters.nlp.base import NlpTask, found, transcript

Tone = Literal["technical_assertive", "collaborative", "dissent"]


class TurnTone(BaseModel):
    turn: int = Field(description="Número del turno, como en [n]")
    tone: Tone | None = Field(description="Registro del turno; null si no aplica ninguno (saludos, agradecimientos, preguntas de trámite)")
    evidence: str | None = Field(description="Fragmento literal breve del turno que lo muestra; null si tone es null")


class Tones(BaseModel):
    turns: list[TurnTone]


PROMPT = """Analizas la transcripción automática de un vídeo (puede estar en español, catalán o inglés y tener errores).
Cada línea es un turno: [número de turno] hablante: lo que dice.
Clasifica el registro discursivo de CADA turno, juzgando solo el texto (nunca a la persona, sus emociones ni sus intenciones):
- technical_assertive: afirma hechos, aporta datos o marca una posición clara.
- collaborative: apoya, matiza o construye sobre lo que han dicho otras personas.
- dissent: rebate o cuestiona abiertamente lo que han dicho otras personas.
- null: no aplica ninguno (saludos, agradecimientos, preguntas de trámite).
Para cada turno da el tono y, como evidencia, un fragmento literal breve del turno."""


class ToneClassifier(NlpTask):
    table = "nlp_tone"
    columns = ["turn", "speaker", "tone", "evidence", "found"]

    def _extract(self, turns: pd.DataFrame) -> pd.DataFrame:
        """One row per turn classified by the model (tone NA when none applies); the speaker is the one of the turn."""
        answer = self.llm.complete(PROMPT, transcript(turns), Tones)
        by_turn = turns.set_index("turn")
        rows = [[t.turn, by_turn.speaker[t.turn], t.tone, t.evidence, found(t.evidence, by_turn.text[t.turn])]
                for t in answer.turns if t.turn in by_turn.index]
        tones = pd.DataFrame(rows, columns=self.columns).drop_duplicates("turn")
        return tones.astype({"turn": int, "speaker": "Int64", "found": bool})
