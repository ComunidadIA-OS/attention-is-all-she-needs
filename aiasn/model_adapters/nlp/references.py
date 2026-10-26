'''Task 3: well-known people each speaker cites as references (are women cited?)'''

from typing import Literal

import pandas as pd
from pydantic import BaseModel, Field

from aiasn.model_adapters.nlp.base import NlpTask, found, transcript


class Reference(BaseModel):
    turn: int = Field(description="Número del turno donde se menciona a la persona, como en [n]")
    name: str = Field(description="Nombre completo de la persona, corregido si la transcripción lo escribe mal")
    literal: str = Field(description="Cómo aparece EXACTAMENTE en la transcripción")
    gender: Literal["F", "M"] | None = Field(description="Género de la persona; null si no se sabe")


class References(BaseModel):
    references: list[Reference]


PROMPT = """Analizas la transcripción automática de un vídeo (puede estar en español, catalán o inglés y tener errores en los nombres).
Cada línea es un turno: [número de turno] hablante: lo que dice.
Extrae las personas famosas o históricas que se mencionan. No incluyas a quienes participan en la conversación,
ni a personas anónimas o genéricas ("una monja", "mi madre"...), NI PRONOMBRES.
Para cada mención: el turno donde está, name (nombre completo, corregido si está mal transcrito), literal (cómo aparece
exactamente en el texto) y gender (F o M). Si una persona se menciona en varios turnos, da un elemento por turno."""


class ReferenceExtractor(NlpTask):
    table = "nlp_references"
    columns = ["turn", "speaker", "name", "literal", "gender", "found"]

    def _extract(self, turns: pd.DataFrame) -> pd.DataFrame:
        """One row per mention of a well-known person; the speaker is the one who mentions them."""
        answer = self.llm.complete(PROMPT, transcript(turns), References)
        by_turn = turns.set_index("turn")
        rows = [[r.turn, by_turn.speaker[r.turn], r.name, r.literal, r.gender, found(r.literal, by_turn.text[r.turn])]
                for r in answer.references if r.turn in by_turn.index]
        return pd.DataFrame(rows, columns=self.columns).astype({"turn": int, "speaker": "Int64", "found": bool})
