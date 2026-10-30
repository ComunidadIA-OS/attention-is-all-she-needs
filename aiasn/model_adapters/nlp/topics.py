'''Task 2: topics of the piece and the speakers who talk about each'''

import pandas as pd
from pydantic import BaseModel, Field

from aiasn.model_adapters.nlp.base import NlpTask, found, guide, speaker_id, transcript


class TopicSpeaker(BaseModel):
    speaker: str = Field(description="Hablante que habla de este tema, tal como aparece (Speaker_0, Speaker_1...)")
    evidence: str = Field(description="Fragmento literal breve de lo que dice este hablante que muestra el tema")


class Topic(BaseModel):
    topic: str = Field(description="Nombre corto del tema, en inglés: uno de la guía si encaja, o uno nuevo")
    topic_es: str = Field(description="El mismo tema en español (el de la guía si es uno de ella)")
    speakers: list[TopicSpeaker] = Field(description="Hablantes que hablan de este tema, cada uno una vez")


class Topics(BaseModel):
    topics: list[Topic]


PROMPT = """Analizas la transcripción automática de un vídeo (puede estar en español, catalán o inglés y tener errores).
Cada línea es un turno: [número de turno] hablante: lo que dice.
Lee la conversación entera y enumera los temas que se tratan en ella, consolidados: un tema por cada asunto que de
verdad se desarrolla, aunque lo traten varias personas o en varios turnos. No cuentes como temas los saludos, los
agradecimientos ni la presentación de quién es cada persona.
Para cada tema, indica qué hablantes hablan de él y, para cada uno, un fragmento literal breve de lo que dice que lo
muestre. Si dos hablantes comentan el mismo asunto, es el mismo tema: ponlos a los dos en él.
Usa como guía esta lista de temas, en inglés (y en español), y si uno encaja escríbelo exactamente igual: {guide}.
Si se habla de algo que no está en la lista, crea un tema nuevo con un nombre corto en inglés, de una palabra si es
posible.
Da cada tema en inglés (topic) y en español (topic_es)."""


class TopicExtractor(NlpTask):
    table = "nlp_topics"
    columns = ["speaker", "topic", "topic_es", "evidence", "found"]

    def _extract(self, turns: pd.DataFrame) -> pd.DataFrame:
        """One row per topic and speaker who talks about it, read from the whole transcript at once: the model sees
        when two people discuss the same thing, and a turn is not cut into topics of its own."""
        prompt = PROMPT.format(guide=guide(self.cfg.topics_guide))
        answer = self.llm.complete(prompt, transcript(turns), Topics)
        speakers = set(turns.speaker.dropna())
        said = turns.dropna(subset=["speaker"]).groupby("speaker").text.apply(" ".join)
        rows, seen = [], set()
        for t in answer.topics:
            topic = t.topic.strip()
            for s in t.speakers:
                speaker = speaker_id(s.speaker, speakers)
                if speaker is None or (speaker, topic.lower()) in seen:
                    continue
                seen.add((speaker, topic.lower()))
                rows.append([speaker, topic, t.topic_es.strip(), s.evidence, found(s.evidence, said[speaker])])
        return pd.DataFrame(rows, columns=self.columns).astype({"speaker": "Int64", "found": bool})
