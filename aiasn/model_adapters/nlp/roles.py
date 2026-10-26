'''Task 4: role of each speaker in the piece (host, expert, voice-over narrator...)'''

import pandas as pd
from pydantic import BaseModel, Field

from aiasn.model_adapters.nlp.base import NlpTask, speaker_id, transcript


class SpeakerRole(BaseModel):
    speaker: str = Field(description="Hablante tal como aparece (Speaker_0, Speaker_1...)")
    role: str = Field(description="Rol de este hablante en la pieza, en inglés: uno de la guía si encaja, o uno nuevo")


class Piece(BaseModel):
    format: str = Field(description="Formato de la pieza: entrevista, reportaje con voz en off, narración, anuncio, debate...")
    roles: list[SpeakerRole]


PROMPT = """Analizas la transcripción automática de un vídeo (puede estar en español, catalán o inglés y tener errores).
Cada línea es un turno: [número de turno] hablante: lo que dice.
1. Indica el formato de la pieza (entrevista, reportaje con voz en off, narración, anuncio, debate...).
2. Para cada hablante, indica su rol en la pieza. Usa como guía estos roles y, si uno encaja, escríbelo exactamente igual:
{guide}. Si ninguno encaja, crea uno nuevo corto en inglés."""


class RoleExtractor(NlpTask):
    table = "nlp_roles"
    columns = ["speaker", "role"]

    def _extract(self, turns: pd.DataFrame) -> pd.DataFrame:
        """One row per speaker with the role the model gives them. The format only guides the model: it is not kept."""
        answer = self.llm.complete(PROMPT.format(guide=", ".join(self.cfg.roles_guide)), transcript(turns), Piece)
        speakers = set(turns.speaker.dropna())
        rows = [[s, r.role.strip()] for r in answer.roles if (s := speaker_id(r.speaker, speakers)) is not None]
        roles = pd.DataFrame(rows, columns=self.columns).drop_duplicates("speaker")
        return roles.astype({"speaker": "Int64"})
