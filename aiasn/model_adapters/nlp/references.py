'''Task 3: well-known people each speaker cites as references (are women cited?)'''

from typing import Literal

import pandas as pd
from pydantic import BaseModel, Field

from aiasn.model_adapters.nlp.base import NlpTask, found, transcript


class Reference(BaseModel):
    # First, so that the model reasons before it commits to a name; not kept in the lake
    reasoning: str = Field(description="Antes de nada: quién es esta persona y por qué es un referente citado en la "
                                       "conversación (una o dos frases)")
    # The conclusion of that reasoning: once a model starts an item it completes it, even when its reasoning says no
    is_reference: bool = Field(description="Si, según tu razonamiento, es de verdad un referente citado")
    turn: int = Field(description="Número del turno donde se menciona a la persona, como en [n]")
    name: str = Field(description="Nombre completo de la persona, corregido si la transcripción lo escribe mal")
    literal: str = Field(description="Cómo aparece EXACTAMENTE en la transcripción")
    gender: Literal["F", "M"] | None = Field(description="Género de la persona; null si no se sabe")


class References(BaseModel):
    references: list[Reference]


PROMPT = """Analizas la transcripción automática de un vídeo (puede estar en español, catalán o inglés y tener errores en los nombres).
Cada línea es un turno: [número de turno] hablante: lo que dice.
Extrae los referentes que se citan: personas reales y conocidas (figuras públicas, históricas o expertas) a las que
alguien menciona como autoridad, inspiración o ejemplo.
No son referentes:
- quienes participan en la conversación, ni las personas a las que se habla directamente (un nombre usado para
  llamar a alguien, como "Hey Pepe" u "Oye, Marta");
- robots, asistentes o máquinas, personajes de ficción, mascotas, marcas, productos u organizaciones;
- personas anónimas o genéricas ("una monja", "mi madre"...), ni pronombres.
Para cada candidato, razona primero en reasoning quién es y si es un referente citado, y di en is_reference si lo
es. Después da el turno donde está, name (nombre completo, corregido si está mal transcrito),
literal (cómo aparece exactamente en el texto) y gender (F o M). Si se menciona en varios turnos, da un elemento por
turno."""


class ReferenceExtractor(NlpTask):
    table = "nlp_references"
    columns = ["turn", "speaker", "name", "literal", "gender", "found"]

    def _extract(self, turns: pd.DataFrame) -> pd.DataFrame:
        """One row per mention of a well-known person; the speaker is the one who mentions them."""
        answer = self.llm.complete(PROMPT, transcript(turns), References)
        by_turn = turns.set_index("turn")
        rows = [[r.turn, by_turn.speaker[r.turn], r.name, r.literal, r.gender, found(r.literal, by_turn.text[r.turn])]
                for r in answer.references if r.is_reference and r.turn in by_turn.index]
        return pd.DataFrame(rows, columns=self.columns).astype({"turn": int, "speaker": "Int64", "found": bool})
