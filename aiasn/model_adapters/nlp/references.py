'''Task 3: well-known people each speaker cites as references (are women cited?)'''

from typing import Literal

import pandas as pd
from pydantic import BaseModel, Field

from aiasn.model_adapters.nlp.base import NlpTask, found, transcript


class Reference(BaseModel):
    turn: int = Field(description="Number of the turn where the person is mentioned, as in [n]")
    name: str = Field(description="Full name of the person, corrected if the transcript misspells it")
    literal: str = Field(description="How the person appears EXACTLY in the transcript")
    gender: Literal["F", "M"] | None = Field(description="Gender of the person; null if unknown")


class References(BaseModel):
    references: list[Reference]


PROMPT = """You analyse the automatic transcript of a video (it may be in Spanish, Catalan or English and contain errors in the names).
Each line is a turn: [turn number] speaker: what they say.
Extract the famous or historical people mentioned. Do not include those taking part in the conversation, nor anonymous
or generic people ("a nun", "my mother"...).
For each mention: the turn where it is, name (corrected if misspelt), literal (how it appears exactly in the text)
and gender (F or M). A person mentioned in several turns gives one item per turn."""


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
