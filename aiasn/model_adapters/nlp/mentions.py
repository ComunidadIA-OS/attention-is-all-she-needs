'''Task 1: how the people taking part in the conversation are named (name, title or position, grammatical gender)'''

from typing import Literal

import pandas as pd
from pydantic import BaseModel, Field

from aiasn.model_adapters.nlp.base import NlpTask, found, speaker_id, transcript


class Mention(BaseModel):
    turn: int = Field(description="Número del turno donde está la alusión, como en [n]")
    literal: str = Field(description="Fragmento COMPLETO literal de la transcripción donde se alude a la persona")
    name: str | None = Field(description="Nombre propio de la persona; null si no se dice")
    title: str | None = Field(description="Título, cargo o profesión; null si no se dice")
    gender: Literal["F", "M"] | None = Field(description="Género gramatical con el que se alude a la persona; null si no se sabe o no es binario")
    referred_speaker: str | None = Field(description="Speaker_k de la persona aludida; null si no es ninguno de los hablantes")


class Mentions(BaseModel):
    mentions: list[Mention]


PROMPT = """Analizas la transcripción automática de un vídeo (puede estar en español, catalán o inglés y tener errores de reconocimiento de voz).
Cada línea es un turno: [número de turno] hablante: lo que dice.
Extrae TODAS las alusiones a personas que participan en la conversación: cuando se las presenta, cuando alguien se dirige a ellas o cuando se habla de ellas.
No incluyas a personas que solo se citan y no participan (personajes históricos, famosos) NI PRONOMBRES.

Para cada alusión devuelve:
- turn: el número del turno donde está.
- literal: el fragmento completo exacto de la transcripción.
- name: el nombre propio tal como aparece; null si no se dice.
- title: título, cargo o profesión (doctora, catedrática de la UPC, director del hospital...); null si no se dice.
  Las relaciones NO son cargos: "mi compañera", "mi amigo", "la mujer de..." -> null.
- gender: "F" o "M" según cómo se alude a la persona (artículos, pronombres, concordancia); null si no se sabe.
- referred_speaker: el hablante (Speaker_k) que es la persona aludida, según la conversación; null si no lo puedes saber.

Ejemplos:
Texto: "[3] Speaker_0: Hoy nos acompaña la doctora Marta Ruiz, investigadora del CSIC." (y después Speaker_1 responde como Marta)
-> {"turn": 3, "literal": "la doctora Marta Ruiz, investigadora del CSIC", "name": "Marta Ruiz", "title": "doctora, investigadora del CSIC", "gender": "F", "referred_speaker": "Speaker_1"}
Texto: "[7] Speaker_1: Gracias, Luis, por estar aquí." (Luis es Speaker_0)
-> {"turn": 7, "literal": "Gracias, Luis", "name": "Luis", "title": null, "gender": "M", "referred_speaker": "Speaker_0"}
Texto: "[9] Speaker_0: Mi compañera nos lo explica ahora." (y Speaker_2 lo explica)
-> {"turn": 9, "literal": "Mi compañera", "name": null, "title": null, "gender": "F", "referred_speaker": "Speaker_2"}"""


class MentionExtractor(NlpTask):
    table = "nlp_mentions"
    columns = ["turn", "speaker", "literal", "name", "title", "gender", "referred_speaker", "found"]

    def _extract(self, turns: pd.DataFrame) -> pd.DataFrame:
        """One row per mention of a speaker: who says it (`speaker`) and who is mentioned (`referred_speaker`).

        Mentions the model cannot match to a speaker are dropped: that person does not take part in the conversation.
        """
        answer = self.llm.complete(PROMPT, transcript(turns), Mentions)
        by_turn, speakers = turns.set_index("turn"), set(turns.speaker.dropna())
        rows = []
        for m in answer.mentions:
            referred = speaker_id(m.referred_speaker, speakers)
            if referred is None or m.turn not in by_turn.index:
                continue
            t = by_turn.loc[m.turn]
            rows.append([m.turn, t.speaker, m.literal, m.name, m.title, m.gender, referred, found(m.literal, t.text)])
        return pd.DataFrame(rows, columns=self.columns).astype({"turn": int, "speaker": "Int64", "referred_speaker": "Int64",
                                                                "found": bool})
