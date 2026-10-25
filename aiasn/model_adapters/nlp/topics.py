'''Task 2: topics each speaker talks about'''

import pandas as pd
from pydantic import BaseModel, Field

from aiasn.model_adapters.nlp.base import NlpTask, found, transcript


class Topic(BaseModel):
    turn: int = Field(description="Number of the turn where the topic is talked about, as in [n]")
    topic: str = Field(description="Short name of the topic, in English: one of the guide if it fits, or a new one")
    evidence: str = Field(description="Short literal fragment of that turn that shows the topic")


class Topics(BaseModel):
    topics: list[Topic]


PROMPT = """You analyse the automatic transcript of a video (it may be in Spanish, Catalan or English and contain errors).
Each line is a turn: [turn number] speaker: what they say.
List the topics each speaker talks about. For each topic, give the turn where it is talked about and a short literal
fragment of that turn as evidence. A speaker talking about the same topic in several turns gives one item per turn.
Use this list of topics as a guide and, if one fits, write it exactly the same: {guide}.
If something is not in the list, create a new topic with a short name in English."""


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
