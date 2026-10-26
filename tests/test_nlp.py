import json
import logging
import time
from contextlib import contextmanager

import pandas as pd
import pytest
from pydantic import BaseModel

from aiasn.model_adapters.llm_client import LLMClient
from aiasn.model_adapters.nlp.base import found, speaker_id, transcript
from aiasn.model_adapters.nlp.captions import Caption, CaptionExtractor, Captions
from aiasn.model_adapters.nlp.ideas import Idea, IdeaExtractor, Ideas
from aiasn.model_adapters.nlp.mentions import Mention, MentionExtractor, Mentions
from aiasn.model_adapters.nlp.references import Reference, ReferenceExtractor, References
from aiasn.model_adapters.nlp.roles import Piece, RoleExtractor, SpeakerRole
from aiasn.model_adapters.nlp import tone
from aiasn.model_adapters.nlp.tone import (LlmToneClassifier, Tones, TurnTone, ZeroShotToneClassifier,
                                           make_tone_classifier)
from aiasn.model_adapters.nlp.topics import Topic, TopicExtractor, Topics
from aiasn.pipelines.captions import CaptionsPipeline
from aiasn.pipelines.context import RunContext
from aiasn.pipelines.nlp import NlpPipeline
from aiasn.settings import NlpSettings, Settings, ToneSettings
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
REFERENCES = References(references=[
    Reference(turn=3, name="Ada Lovelace", literal="Ada Lovelace", gender="F"),
    Reference(turn=1, name="Hedy Lamarr", literal="Heidi Lamar", gender="F"),
    Reference(turn=8, name="Alan Turing", literal="Turing", gender="M"),
])
PIECE = Piece(format="interview", roles=[
    SpeakerRole(speaker="Speaker_0", role="interviewer"), SpeakerRole(speaker="Speaker_1", role="expert "),
    SpeakerRole(speaker="Speaker_1", role="testimony"), SpeakerRole(speaker="Speaker_5", role="host"),
])
IDEAS = Ideas(ideas=[
    Idea(idea="Ada Lovelace inspired her career", speakers=["Speaker_1"]),
    Idea(idea="Science needs more women", speakers=["Speaker_0", "Speaker_1", "Speaker_1", "Speaker_9"]),
    Idea(idea="Nobody said this", speakers=["Speaker_9"]),
])
TONES = Tones(turns=[
    TurnTone(turn=0, tone="technical_assertive", evidence="investigadora del CSIC"),
    TurnTone(turn=1, tone=None, evidence=None),
    TurnTone(turn=3, tone="collaborative", evidence="Ada Lovelace, que fue mi referente"),
    TurnTone(turn=3, tone="dissent", evidence="Empecé"),
    TurnTone(turn=12, tone="dissent", evidence="no"),
])
ANSWERS = {Mentions: MENTIONS, Topics: TOPICS, References: REFERENCES, Piece: PIECE, Ideas: IDEAS, Tones: TONES}


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


def test_references_take_the_speaker_who_mentions_them():
    r = ReferenceExtractor(FakeLLM({References: REFERENCES}), NlpSettings()).extract(TURNS)
    assert list(r.columns) == ["turn", "speaker", "name", "literal", "gender", "found"]
    assert r.name.tolist() == ["Ada Lovelace", "Hedy Lamarr"] and r.speaker.tolist() == [1, 1]   # turn 8 does not exist
    assert r.found.tolist() == [True, False]   # "Heidi Lamar" is not in turn 1


def test_roles_one_per_known_speaker():
    llm = FakeLLM({Piece: PIECE})
    r = RoleExtractor(llm, NlpSettings(roles_guide=["host", "expert"])).extract(TURNS)
    assert list(r.columns) == ["speaker", "role"]
    assert r.speaker.tolist() == [0, 1] and r.role.tolist() == ["interviewer", "expert"]   # first role wins; Speaker_5 unknown
    assert "host, expert" in llm.calls[0][0]


def test_ideas_one_row_per_contributing_speaker():
    llm = FakeLLM({Ideas: IDEAS})
    i = IdeaExtractor(llm, NlpSettings(max_ideas=5)).extract(TURNS)
    assert list(i.columns) == ["idea_id", "idea", "speaker"]
    # Duplicated and unknown speakers dropped; the idea left without speakers too
    assert i.idea_id.tolist() == [0, 1, 1] and i.speaker.tolist() == [1, 0, 1]
    assert "no más de 5" in llm.calls[0][0]


def test_tone_one_row_per_turn():
    t = LlmToneClassifier(FakeLLM({Tones: TONES}), NlpSettings()).extract(TURNS)
    assert list(t.columns) == ["turn", "speaker", "tone", "score", "evidence", "found"]
    assert t.score.isna().all()   # the LLM gives no score
    assert t.turn.tolist() == [0, 1, 3] and t.speaker.tolist() == [0, 1, 1]   # first answer per turn; turn 12 unknown
    assert t.tone.isna().tolist() == [False, True, False]
    assert t.tone.dropna().tolist() == ["technical_assertive", "collaborative"]
    assert t.found.tolist() == [True, False, True]


def test_tasks_skip_the_model_without_turns():
    llm = FakeLLM({})
    assert MentionExtractor(llm, NlpSettings()).extract(TURNS.iloc[:0]).empty
    assert not llm.calls


TABLES = ["nlp_mentions", "nlp_topics", "nlp_references", "nlp_roles", "nlp_ideas", "nlp_tone"]


def make_ctx(tmp_path) -> RunContext:
    settings = Settings(lake_dir=tmp_path / "lake", tmp_dir=tmp_path / "tmp")
    ctx = RunContext("vid1", settings, Lake(settings.lake_dir), Manifest(settings.lake_dir, "vid1"), settings.tmp_dir / "vid1")
    ctx.lake.write("bronze", "audio_turns", "vid1", TURNS)
    return ctx


@contextmanager
def captured_log():
    lines = []
    handler = logging.Handler()
    handler.emit = lambda record: lines.append(record.getMessage())
    logger = logging.getLogger("aiasn")
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    try:
        yield lines
    finally:
        logger.removeHandler(handler)


def test_nlp_pipeline_writes_bronze_tables(tmp_path):
    ctx = make_ctx(tmp_path)
    with captured_log() as lines:
        NlpPipeline(ctx.settings.nlp, llm=FakeLLM(ANSWERS))(ctx)

    assert json.loads(ctx.manifest.path.read_text())["steps"]["nlp"]["status"] == "ok"
    assert len(ctx.lake.read("bronze", "nlp_mentions", "vid1")) == 3
    assert len(ctx.lake.read("bronze", "nlp_topics", "vid1")) == 2
    assert len(ctx.lake.read("bronze", "nlp_references", "vid1")) == 2
    assert len(ctx.lake.read("bronze", "nlp_roles", "vid1")) == 2
    assert len(ctx.lake.read("bronze", "nlp_ideas", "vid1")) == 3
    assert len(ctx.lake.read("bronze", "nlp_tone", "vid1")) == 3
    steps = [line.split()[1] for line in lines]
    assert steps[0] == "load" and steps[-1] == "total"   # tasks in any order: they run in parallel
    assert sorted(steps[1:-1]) == sorted(t.removeprefix("nlp_") for t in TABLES)
    assert any(line.split()[1] == "mentions" and "3 rows, 1 not found" in line for line in lines)


class SlowLLM(FakeLLM):
    def complete(self, system, user, schema):
        time.sleep(0.3)
        return super().complete(system, user, schema)


def test_nlp_tasks_run_in_parallel(tmp_path):
    ctx = make_ctx(tmp_path)
    start = time.perf_counter()
    NlpPipeline(ctx.settings.nlp, llm=SlowLLM(ANSWERS))(ctx)
    assert time.perf_counter() - start < 1.0   # one after the other it would take 6 × 0.3 s


def test_a_failing_task_does_not_stop_the_others(tmp_path):
    ctx = make_ctx(tmp_path)
    answers = {schema: answer for schema, answer in ANSWERS.items() if schema is not Ideas}
    with pytest.raises(KeyError):
        NlpPipeline(ctx.settings.nlp, llm=FakeLLM(answers))(ctx)
    assert json.loads(ctx.manifest.path.read_text())["steps"]["nlp"]["status"] == "error"
    for table in TABLES:
        assert (ctx.lake.table_dir("bronze", table, "vid1") / "part-0.parquet").exists() == (table != "nlp_ideas")


def test_nlp_pipeline_needs_the_transcript(tmp_path):
    settings = Settings(lake_dir=tmp_path / "lake", tmp_dir=tmp_path / "tmp")
    ctx = RunContext("vid1", settings, Lake(settings.lake_dir), Manifest(settings.lake_dir, "vid1"), settings.tmp_dir / "vid1")
    with pytest.raises(FileNotFoundError):
        NlpPipeline(settings.nlp, llm=FakeLLM({}))(ctx)


class FakeZeroShot:
    """Stands in for the NLI pipeline: scores given per premise, highest first, as the real one returns them."""

    def __init__(self, scores: list[dict[str, float]]):
        self.scores, self.calls = scores, []

    def __call__(self, premises, candidate_labels, hypothesis_template, multi_label):
        self.calls.append(premises)
        results = []
        for score in self.scores[:len(premises)]:
            ranked = sorted(score.items(), key=lambda kv: -kv[1])
            results.append({"labels": [tone.HYPOTHESES[t] for t, _ in ranked], "scores": [v for _, v in ranked]})
        return results[0] if len(results) == 1 else results


def zero_shot(monkeypatch, scores, **tone_settings) -> tuple[ZeroShotToneClassifier, FakeZeroShot]:
    fake = FakeZeroShot(scores)
    monkeypatch.setattr(tone, "_load_pipeline", lambda *args, **kw: fake)
    cfg = NlpSettings(tone=ToneSettings(method="zero_shot", **tone_settings))
    return make_tone_classifier(FakeLLM({}), cfg), fake


def test_zero_shot_tone_prefers_a_stance_over_stating_facts(monkeypatch):
    scores = [{"technical_assertive": 0.95, "collaborative": 0.2, "dissent": 0.1},
              {"technical_assertive": 0.3, "collaborative": 0.4, "dissent": 0.1},    # none reaches min_score
              {"technical_assertive": 0.99, "collaborative": 0.2, "dissent": 0.92},  # dissent first, though lower
              {"technical_assertive": 0.99, "collaborative": 0.95, "dissent": 0.1}]
    classifier, fake = zero_shot(monkeypatch, scores, min_score=0.9)
    assert isinstance(classifier, ZeroShotToneClassifier)
    t = classifier.extract(TURNS)
    assert list(t.columns) == ["turn", "speaker", "tone", "score", "evidence", "found"]
    assert t.tone.isna().tolist() == [False, True, False, False]
    assert t.tone.dropna().tolist() == ["technical_assertive", "dissent", "collaborative"]
    assert t.score.tolist() == [0.95, 0.4, 0.92, 0.95] and t.speaker.tolist() == [0, 1, 0, 1]
    assert t.evidence.isna().all() and t.found.isna().all()   # no quote to check
    premises = fake.calls[0]
    assert premises[0] == "Último turno: " + TURNS.text[0]
    assert premises[1] == f"Turno anterior: {TURNS.text[0]}\nÚltimo turno: {TURNS.text[1]}"


def test_zero_shot_tone_without_previous_turn_and_with_one_turn(monkeypatch):
    classifier, fake = zero_shot(monkeypatch, [{"technical_assertive": 0.9, "collaborative": 0.1, "dissent": 0.1}],
                                 with_previous_turn=False)
    t = classifier.extract(TURNS.iloc[1:2])   # the pipeline returns a dict, not a list, for one premise
    assert t.tone.tolist() == ["technical_assertive"]
    assert fake.calls[0] == ["Último turno: " + TURNS.text[1]]


def test_tone_classifier_defaults_to_the_llm():
    assert isinstance(make_tone_classifier(FakeLLM({}), NlpSettings()), LlmToneClassifier)


def test_zero_shot_tone_with_the_real_model():
    """Clear-cut turns with the multilingual NLI model (downloaded the first time)."""
    pytest.importorskip("transformers")
    turns = pd.DataFrame({
        "turn": [0, 1, 2],
        "speaker": pd.array([0, 1, 0], dtype="Int64"),
        "text": ["Según los datos del INE, solo el 22 % de las personas que trabajan en IA en España son mujeres.",
                 "Exacto, y añadiría que en la universidad la proporción es todavía menor, como bien dices.",
                 "No estoy de acuerdo, eso que dices es falso: las cifras de este año lo contradicen."],
    })
    t = ZeroShotToneClassifier(FakeLLM({}), NlpSettings(tone=ToneSettings(method="zero_shot"))).extract(turns)
    assert t.tone.tolist() == ["technical_assertive", "collaborative", "dissent"]


# Captions

def ocr(frame: int, *lines: tuple[str, float]) -> list[dict]:
    """bronze video_texts rows of one frame: (text, y1) per box."""
    return [{"frame": frame, "shot": 0, "text": text, "conf": 0.9, "x1": 10.0, "y1": y, "x2": 200.0, "y2": y + 20}
            for text, y in lines]


TEXTS = pd.DataFrame(
    ocr(100, ("TOP SECRET ROSIES", 300.0))
    # The OCR splits name and title, reads them in any order and sometimes "_" for a space
    + ocr(125, ("Investigador del ICMAT", 213.0), ("David_Ríos Insua", 180.0))
    + ocr(150, ("David_Ríos Insua", 180.0), ("Investigador del ICMAT", 213.0))
    + ocr(175, ("David Ríos Insua", 174.0), ("Investigador del ICMAT", 213.0)))
CAPTIONS = Captions(captions=[Caption(block=1, name="David Ríos Insua", title="Investigador del ICMAT"),
                              Caption(block=9, name="Nadie", title=None)])


def test_captions_read_each_distinct_block_once():
    llm = FakeLLM({Captions: CAPTIONS})
    c = CaptionExtractor(llm).extract(TEXTS)
    assert llm.calls[0][1] == "[0] TOP SECRET ROSIES\n[1] David_Ríos Insua | Investigador del ICMAT"
    assert list(c.columns) == ["frame", "shot", "text", "name", "title", "found"]
    assert c.frame.tolist() == [125, 150, 175]   # every frame showing the caption; not the programme's name
    assert set(c.name) == {"David Ríos Insua"} and set(c.title) == {"Investigador del ICMAT"}
    assert c.found.all()                         # "David_Ríos" counts as "David Ríos"


def test_captions_without_texts_skip_the_model():
    llm = FakeLLM({})
    assert CaptionExtractor(llm).extract(TEXTS.iloc[:0]).empty and not llm.calls


def test_captions_pipeline(tmp_path):
    ctx = make_ctx(tmp_path)
    ctx.lake.write("bronze", "video_texts", "vid1", TEXTS)
    with captured_log() as lines:
        CaptionsPipeline(ctx.settings.nlp, llm=FakeLLM({Captions: CAPTIONS}))(ctx)
    assert len(ctx.lake.read("bronze", "video_captions", "vid1")) == 3
    assert "1 people captioned in 3 frames, 0 names not found" in lines[0]
