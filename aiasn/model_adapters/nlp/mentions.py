'''Task 1: how the people taking part in the conversation are named (name, title or position, grammatical gender)'''

from typing import Literal

import pandas as pd
from pydantic import BaseModel, Field

from aiasn.model_adapters.nlp.base import NlpTask, found, speaker_id, transcript


class Mention(BaseModel):
    turn: int = Field(description="Number of the turn where the mention is, as in [n]")
    literal: str = Field(description="COMPLETE literal fragment of the transcript that mentions the person")
    name: str | None = Field(description="Proper name of the person; null if not said")
    title: str | None = Field(description="Title, position or profession; null if not said")
    gender: Literal["F", "M"] | None = Field(description="Grammatical gender used for the person; null if unknown or non-binary")
    referred_speaker: str | None = Field(description="Speaker_k of the person mentioned; null if it is none of the speakers")


class Mentions(BaseModel):
    mentions: list[Mention]


PROMPT = """You analyse the automatic transcript of a video (it may be in Spanish, Catalan or English and contain speech recognition errors).
Each line is a turn: [turn number] speaker: what they say.
Extract ALL mentions of people who take part in the conversation: when they are introduced, addressed or talked about.
Do not include people who are only cited and do not take part (historical figures, celebrities), NOR PRONOUNS.

For each mention return:
- turn: the number of the turn where it is.
- literal: the complete, exact fragment of the transcript.
- name: the proper name as it appears; null if not said.
- title: title, position or profession (doctor, professor at the UPC, hospital director...); null if not said.
  Relationships are NOT titles: "my colleague", "my friend", "the wife of..." -> null.
- gender: "F" or "M" according to how the person is referred to (articles, pronouns, agreement); null if unknown.
- referred_speaker: the speaker (Speaker_k) who is the person mentioned, judging by the conversation; null if you cannot tell.

Examples:
Text: "[3] Speaker_0: Hoy nos acompaña la doctora Marta Ruiz, investigadora del CSIC." (and Speaker_1 then answers as Marta)
-> {"turn": 3, "literal": "la doctora Marta Ruiz, investigadora del CSIC", "name": "Marta Ruiz", "title": "doctora, investigadora del CSIC", "gender": "F", "referred_speaker": "Speaker_1"}
Text: "[7] Speaker_1: Gracias, Luis, por estar aquí." (Luis is Speaker_0)
-> {"turn": 7, "literal": "Gracias, Luis", "name": "Luis", "title": null, "gender": "M", "referred_speaker": "Speaker_0"}
Text: "[9] Speaker_0: Mi compañera nos lo explica ahora." (and Speaker_2 explains it)
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
