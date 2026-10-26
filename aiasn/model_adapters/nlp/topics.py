'''Task 2: topics each speaker talks about'''

import pandas as pd
from pydantic import BaseModel, Field

from aiasn.model_adapters.nlp.base import NlpTask, found, transcript


class Topic(BaseModel):
    turn: int = Field(description="Número del turno donde se habla del tema, como en [n]")
    topic: str = Field(description="Nombre corto del tema, en inglés: uno de la guía si encaja, o uno nuevo")
    evidence: str = Field(description="Fragmento literal breve de ese turno que muestra el tema")


class Topics(BaseModel):
    topics: list[Topic]


PROMPT = """Analizas la transcripción automática de un vídeo (puede estar en español, catalán o inglés y tener errores).
Cada línea es un turno: [número de turno] hablante: lo que dice.
Enumera los temas de los que habla cada hablante. Para cada tema, da el turno donde se habla de él y, como evidencia,
un fragmento literal breve de ese turno. Si un hablante trata el mismo tema en varios turnos, da un elemento por turno.
Usa como guía esta lista de temas y, si uno encaja, escríbelo exactamente igual: {guide}.
Si se habla de algo que no está en la lista, crea un tema nuevo con un nombre corto en inglés."""


class TopicExtractor(NlpTask):
    table = "nlp_topics"
    columns = ["turn", "speaker", "topic", "evidence", "found"]

    def _extract(self, turns: pd.DataFrame) -> pd.DataFrame:
        """One row per topic and turn; the speaker is the one of the turn."""
        prompt = PROMPT.format(guide=", ".join(self.cfg.topics_guide))
        answer = self.llm.complete(prompt, transcript(turns), Topics)
        by_turn = turns.set_index("turn")
        rows = [[t.turn, by_turn.speaker[t.turn], t.topic.strip(), t.evidence, found(t.evidence, by_turn.text[t.turn])]
                for t in answer.topics if t.turn in by_turn.index]
        return pd.DataFrame(rows, columns=self.columns).astype({"turn": int, "speaker": "Int64", "found": bool})
