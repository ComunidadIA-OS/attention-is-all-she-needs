'''Task 4: role of each speaker in the piece (host, expert, voice-over narrator...)'''

import pandas as pd
from pydantic import BaseModel, Field

from aiasn.model_adapters.nlp.base import NlpTask, speaker_id, transcript


class SpeakerRole(BaseModel):
    speaker: str = Field(description="Speaker as it appears (Speaker_0, Speaker_1...)")
    role: str = Field(description="Role of this speaker in the piece, in English: one of the guide if it fits, or a new one")


class Piece(BaseModel):
    format: str = Field(description="Format of the piece: interview, report with voice-over, narration, advert, debate...")
    roles: list[SpeakerRole]


PROMPT = """You analyse the automatic transcript of a video (it may be in Spanish, Catalan or English and contain errors).
Each line is a turn: [turn number] speaker: what they say.
1. Say the format of the piece (interview, report with voice-over, narration, advert, debate...).
2. For each speaker, say their role in the piece. Use these roles as a guide and, if one fits, write it exactly the same:
{guide}. If none fits, create a new short one in English."""


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
