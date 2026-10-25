import json
import logging

import pandas as pd
import pytest
from pydantic import BaseModel

from aiasn.model_adapters.llm_client import LLMClient
from aiasn.model_adapters.nlp.base import found, speaker_id, transcript
from aiasn.model_adapters.nlp.mentions import Mention, MentionExtractor, Mentions
from aiasn.model_adapters.nlp.topics import Topic, TopicExtractor, Topics
from aiasn.pipelines.context import RunContext
from aiasn.pipelines.nlp import NlpPipeline
from aiasn.settings import NlpSettings, Settings
from aiasn.storage.lake import Lake
from aiasn.storage.manifest import Manifest

# bronze audio_turns of a short interview
TURNS = pd.DataFrame({
    "turn": [0, 1, 2, 3],
    "start": [0.0, 4.0, 7.0, 9.0], "end": [4.0, 7.0, 9.0, 15.0],
    "speaker": pd.array([0, 1, 0, 1], dtype="Int64"),
    "text": ["Hoy nos acompaña la doctora Marta Ruiz, investigadora del CSIC.",
             "Gracias, Luis, por invitarme.",
             "Marta, ¿cómo empezó todo?",
             "Empecé gracias a Ada Lovelace, que fue mi referente."],
    "gender": ["M", "F", "M", "F"], "gender_prob": [0.95, 0.9, 0.97, 0.92],
})


class FakeLLM(LLMClient):
    """Answers each schema with a fixed object and records the calls."""

    def __init__(self, answers: dict[type, BaseModel]):
        self.answers, self.calls = answers, []

    def complete(self, system, user, schema):
        self.calls.append((system, user, schema))
        return self.answers[schema]


MENTIONS = Mentions(mentions=[
    Mention(turn=0, literal="la doctora Marta Ruiz, investigadora del CSIC", name="Marta Ruiz",
            title="doctora, investigadora del CSIC", gender="F", referred_speaker="Speaker_1"),
    Mention(turn=1, literal="Gracias, Luis", name="Luis", title=None, gender="M", referred_speaker="Speaker_0"),
    Mention(turn=2, literal="querida Marta", name="Marta", title=None, gender="F", referred_speaker="Speaker_1"),
    Mention(turn=3, literal="Ada Lovelace", name="Ada Lovelace", title=None, gender="F", referred_speaker=None),
    Mention(turn=1, literal="Luis", name="Luis", title=None, gender="M", referred_speaker="Speaker_7"),
    Mention(turn=99, literal="Luis", name="Luis", title=None, gender="M", referred_speaker="Speaker_0"),
])
TOPICS = Topics(topics=[
    Topic(turn=3, topic="science and research", evidence="Empecé gracias a Ada Lovelace"),
    Topic(turn=0, topic="Diversity and equality ", evidence="mujeres en la ciencia"),
    Topic(turn=42, topic="history", evidence="Ada Lovelace"),
])
ANSWERS = {Mentions: MENTIONS, Topics: TOPICS}


def test_transcript_has_turns_and_speakers_but_no_gender():
    text = transcript(TURNS)
    assert text.splitlines()[1] == "[1] Speaker_1: Gracias, Luis, por invitarme."
    assert "F" not in text.split() and "gender" not in text


def test_found_ignores_case_accents_and_punctuation():
    assert found("como empezo todo", "Marta, ¿cómo empezó todo?")
    assert not found("querida Marta", "Marta, ¿cómo empezó todo?")
    assert not found("", "texto") and not found(None, "texto") and not found("¿?", "texto")


def test_speaker_id_accepts_only_known_speakers():
    assert speaker_id("Speaker_1", {0, 1}) == 1
    assert speaker_id("Speaker_7", {0, 1}) is None
    assert speaker_id(None, {0, 1}) is None and speaker_id("Luis", {0, 1}) is None


def test_mentions_keep_only_speakers_of_the_conversation():
    llm = FakeLLM({Mentions: MENTIONS})
    m = MentionExtractor(llm, NlpSettings()).extract(TURNS)
    assert list(m.columns) == ["turn", "speaker", "literal", "name", "title", "gender", "referred_speaker", "found"]
    # Dropped: no referred speaker (Ada Lovelace), unknown speaker, unknown turn
    assert m.turn.tolist() == [0, 1, 2]
    assert m.speaker.tolist() == [0, 1, 0]            # who says it, from the turn
    assert m.referred_speaker.tolist() == [1, 0, 1]
    assert m.found.tolist() == [True, True, False]    # "querida Marta" is not in the turn
    assert llm.calls[0][1] == transcript(TURNS)


def test_topics_take_the_speaker_of_their_turn():
    llm = FakeLLM({Topics: TOPICS})
    t = TopicExtractor(llm, NlpSettings(topics_guide=["care", "technology"])).extract(TURNS)
    assert list(t.columns) == ["turn", "speaker", "topic", "evidence", "found"]
    assert t.turn.tolist() == [3, 0] and t.speaker.tolist() == [1, 0]   # turn 42 does not exist
    assert t.topic.tolist() == ["science and research", "Diversity and equality"]
    assert t.found.tolist() == [True, False]
    assert "care, technology" in llm.calls[0][0]


def test_tasks_skip_the_model_without_turns():
    llm = FakeLLM({})
    assert MentionExtractor(llm, NlpSettings()).extract(TURNS.iloc[:0]).empty
    assert not llm.calls


def test_nlp_pipeline_writes_bronze_tables(tmp_path):
    settings = Settings(lake_dir=tmp_path / "lake", tmp_dir=tmp_path / "tmp")
    ctx = RunContext("vid1", settings, Lake(settings.lake_dir), Manifest(settings.lake_dir, "vid1"), settings.tmp_dir / "vid1")
    ctx.lake.write("bronze", "audio_turns", "vid1", TURNS)
    lines = []
    handler = logging.Handler()
    handler.emit = lambda record: lines.append(record.getMessage())
    logger = logging.getLogger("aiasn")
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    try:
        NlpPipeline(settings.nlp, llm=FakeLLM(ANSWERS))(ctx)
    finally:
        logger.removeHandler(handler)

    assert json.loads(ctx.manifest.path.read_text())["steps"]["nlp"]["status"] == "ok"
    assert len(ctx.lake.read("bronze", "nlp_mentions", "vid1")) == 3
    assert len(ctx.lake.read("bronze", "nlp_topics", "vid1")) == 2
    assert [line.split()[1] for line in lines] == ["load", "mentions", "topics", "total"]
    assert "3 rows, 1 not found" in lines[1]


def test_nlp_pipeline_needs_the_transcript(tmp_path):
    settings = Settings(lake_dir=tmp_path / "lake", tmp_dir=tmp_path / "tmp")
    ctx = RunContext("vid1", settings, Lake(settings.lake_dir), Manifest(settings.lake_dir, "vid1"), settings.tmp_dir / "vid1")
    with pytest.raises(FileNotFoundError):
        NlpPipeline(settings.nlp, llm=FakeLLM({}))(ctx)
