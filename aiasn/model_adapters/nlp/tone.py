'''Task 8: discursive register of each turn (technical/assertive, collaborative, dissent), from the text only (ADR-009)'''

from typing import Literal

import pandas as pd
from pydantic import BaseModel, Field

from aiasn.model_adapters.nlp.base import NlpTask, found, transcript

Tone = Literal["technical_assertive", "collaborative", "dissent"]


class TurnTone(BaseModel):
    turn: int = Field(description="Number of the turn, as in [n]")
    tone: Tone | None = Field(description="Register of the turn; null if none applies (greetings, thanks, procedural questions)")
    evidence: str | None = Field(description="Short literal fragment of the turn that shows it; null if tone is null")


class Tones(BaseModel):
    turns: list[TurnTone]


PROMPT = """You analyse the automatic transcript of a video (it may be in Spanish, Catalan or English and contain errors).
Each line is a turn: [turn number] speaker: what they say.
Classify the discursive register of EVERY turn, judging only the text (never the person, their emotions or intentions):
- technical_assertive: states facts, provides data or takes a clear position.
- collaborative: supports, nuances or builds on what others said.
- dissent: openly rebuts or questions what others said.
- null: none applies (greetings, thanks, procedural questions).
For each turn give the tone and a short literal fragment of the turn as evidence."""


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
