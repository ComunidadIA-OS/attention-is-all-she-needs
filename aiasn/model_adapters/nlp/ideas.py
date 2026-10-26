'''Task 6.1: key ideas of the piece and the speakers who contribute them'''

import pandas as pd
from pydantic import BaseModel, Field

from aiasn.model_adapters.nlp.base import NlpTask, speaker_id, transcript


class Idea(BaseModel):
    idea: str = Field(description="Idea clave de la pieza, en una frase corta")
    speakers: list[str] = Field(description="Hablantes que aportan esta idea (Speaker_0...)")


class Ideas(BaseModel):
    ideas: list[Idea]


PROMPT = """Analizas la transcripción automática de un vídeo (puede estar en español, catalán o inglés y tener errores).
Cada línea es un turno: [número de turno] hablante: lo que dice.
Extrae las ideas clave de la pieza (no más de {max_ideas}) y, para cada una, los hablantes que la aportan."""


class IdeaExtractor(NlpTask):
    table = "nlp_ideas"
    columns = ["idea_id", "idea", "speaker"]

    def _extract(self, turns: pd.DataFrame) -> pd.DataFrame:
        """One row per idea and speaker who contributes it. Speakers that do not exist are dropped, and so are ideas left
        without any."""
        answer = self.llm.complete(PROMPT.format(max_ideas=self.cfg.max_ideas), transcript(turns), Ideas)
        speakers = set(turns.speaker.dropna())
        rows = [[i, idea.idea, s] for i, idea in enumerate(answer.ideas)
                for s in dict.fromkeys(speaker_id(label, speakers) for label in idea.speakers) if s is not None]
        return pd.DataFrame(rows, columns=self.columns).astype({"idea_id": int, "speaker": "Int64"})
