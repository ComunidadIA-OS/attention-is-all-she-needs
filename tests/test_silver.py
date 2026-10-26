# SPDX-FileCopyrightText: 2026 Equipo 1: Attention Is All She Needs (Alba Camiña García, Pilar de la Fuente Diez, Rocío Jiménez Villén)
# SPDX-License-Identifier: Apache-2.0

import json
import logging
from contextlib import contextmanager

import numpy as np
import pandas as pd
import pytest

from aiasn.core.silver.audio import AudioSilver
from aiasn.core.silver.gender import decide_gender, female_prob, fuse_gender
from aiasn.core.silver.identity import IdentitySilver
from aiasn.core.silver.video import VideoSilver
from aiasn.core.transform import Transform
from aiasn.pipelines.silver import SilverPipeline
from aiasn.pipelines.context import RunContext
from aiasn.pipelines.transform_pipeline import TransformPipeline
from aiasn.settings import Settings
from aiasn.storage.lake import Lake
from aiasn.storage.manifest import Manifest


def make_ctx(tmp_path, **settings) -> RunContext:
    s = Settings(lake_dir=tmp_path / "lake", tmp_dir=tmp_path / "tmp", **settings)
    return RunContext("vid1", s, Lake(s.lake_dir), Manifest(s.lake_dir, "vid1"), s.tmp_dir / "vid1")


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


# Gender vote

def test_female_prob_from_model_labels():
    p = female_prob(pd.Series(["F", "M", None, "F"]), pd.Series([0.9, 0.7, 0.8, np.nan]))
    assert p.tolist()[:2] == [0.9, pytest.approx(0.3)]
    assert p.isna().tolist() == [False, False, True, True]


@pytest.mark.parametrize("female, expected", [
    ([0.9, 0.85], "mujer"), ([0.1, 0.15], "hombre"), ([0.9, 0.1], "no_determinado"), ([0.79], "no_determinado"),
    ([0.8], "mujer"), ([0.2], "hombre"),
])
def test_decide_gender_abstains_below_the_threshold(female, expected):
    assert decide_gender(pd.Series(female), 0.8)[0] == expected


def test_decide_gender_weights_and_missing_values():
    gender, p = decide_gender(pd.Series([0.9, 0.1, np.nan]), 0.8, weights=pd.Series([9.0, 1.0, 100.0]))
    assert gender == "mujer" and p == pytest.approx(0.82)   # the long turn counts more; the unlabelled one not at all
    gender, p = decide_gender(pd.Series([np.nan]), 0.8)
    assert gender == "no_determinado" and np.isnan(p)
    assert decide_gender(pd.Series([0.9, 0.7]), 0.8, weights=pd.Series([0.0, 0.0]))[1] == pytest.approx(0.8)


# Transform pipeline

class Doubler(Transform):
    name, layer, inputs, outputs = "double", "silver", ["bronze/numbers"], ["doubled", "count"]

    def run(self, tables):
        n = tables["bronze/numbers"]
        return {"doubled": n.assign(x=n.x * 2), "count": pd.DataFrame({"n": [len(n)]})}


class Silver(TransformPipeline):
    name = "silver"


def test_transform_pipeline_reads_and_writes_the_lake(tmp_path):
    ctx = make_ctx(tmp_path)
    ctx.lake.write("bronze", "numbers", "vid1", pd.DataFrame({"x": [1, 2, 3]}))
    with captured_log() as lines:
        Silver([Doubler(ctx.settings)])(ctx)
    assert ctx.lake.read("silver", "doubled", "vid1").x.tolist() == [2, 4, 6]
    assert ctx.lake.read("silver", "count", "vid1").n.tolist() == [3]
    assert json.loads(ctx.manifest.path.read_text())["steps"]["silver"]["status"] == "ok"
    assert "3 doubled, 1 count" in lines[0]


def test_transform_pipeline_fails_without_its_inputs(tmp_path):
    ctx = make_ctx(tmp_path)
    with pytest.raises(FileNotFoundError):
        Silver([Doubler(ctx.settings)])(ctx)
    assert json.loads(ctx.manifest.path.read_text())["steps"]["silver"]["status"] == "error"


# Video

def detections(person: int, frames, gender: str, prob: float, speaking=None, box=(160, 90, 480, 270)) -> pd.DataFrame:
    """bronze video_detections of one person (fps 25, stride 4: each detection stands for 0.16 s), on a 640x360 frame."""
    n = len(frames)
    return pd.DataFrame({"frame": frames, "person_id": pd.array([person] * n, dtype="Int64"),
                         "x1": box[0], "y1": box[1], "x2": box[2], "y2": box[3], "frame_width": 640, "frame_height": 360,
                         "gender": gender, "gender_prob": prob, "age": 30.0,
                         "speaking_score": speaking if speaking is not None else [np.nan] * n})


DETECTIONS = pd.concat([
    # Person 1: a woman, centred on a quarter of the frame, silent and then speaking
    detections(1, range(3, 40, 4), "F", 0.9, speaking=[-1.0] * 5 + [2.0] * 5),
    # Person 2: a man in a corner, no face for TalkNet; leaves the frame for 3.5 s
    detections(2, [3, 7, 11, 99, 103], "M", 0.95, box=(0, 0, 64, 36)),
    # Person 3: unsure gender; one detection missing (shorter than max_gap_s)
    detections(3, [3, 11], "F", 0.6),
], ignore_index=True)


def test_video_people():
    people = VideoSilver(Settings()).run({"bronze/video_detections": DETECTIONS})["video_people"].set_index("person_id")
    assert people.genero.tolist() == ["mujer", "hombre", "no_determinado"]
    assert people.prob_mujer.tolist() == pytest.approx([0.9, 0.05, 0.6])
    assert people.screen_time_s.tolist() == pytest.approx([1.6, 0.8, 0.32])
    assert people.speaking_time_s.tolist() == pytest.approx([0.8, 0, 0])
    assert people.area[1] == pytest.approx(0.25) and people.centrality[1] == pytest.approx(1.0)
    assert people.area[2] == pytest.approx(0.01) and people.centrality[2] < 0.2
    assert people.age.tolist() == [30, 30, 30]


def test_video_presence_splits_on_speaking_and_long_absences():
    presence = VideoSilver(Settings()).run({"bronze/video_detections": DETECTIONS})["video_presence"]
    assert list(presence.columns) == ["person_id", "tiempo_i", "tiempo_f", "hablando"]
    assert presence.person_id.tolist() == [1, 1, 2, 2, 3]
    assert presence.hablando.tolist() == [False, True, False, False, False]
    assert presence.tiempo_i.tolist() == pytest.approx([0.0, 0.8, 0.0, 3.84, 0.0])
    assert presence.tiempo_f.tolist() == pytest.approx([0.8, 1.6, 0.48, 4.16, 0.48])


def test_video_presence_max_gap_is_configurable():
    settings = Settings(silver={"max_gap_s": 5.0})
    presence = VideoSilver(settings).run({"bronze/video_detections": DETECTIONS})["video_presence"]
    assert presence.person_id.tolist() == [1, 1, 2, 3]   # person 2's absence no longer splits the span


def test_video_silver_without_detections():
    out = VideoSilver(Settings()).run({"bronze/video_detections": DETECTIONS.iloc[:0]})
    assert out["video_people"].empty and out["video_presence"].empty


# Audio

AUDIO_TURNS = pd.DataFrame({   # bronze audio_turns
    "turn": [0, 1, 2, 3, 4, 5],
    "start": [0.0, 4.0, 5.0, 15.0, 16.0, 20.0], "end": [4.0, 5.0, 15.0, 16.0, 20.0, 21.0],
    "speaker": pd.array([0, 0, 1, 1, 2, pd.NA], dtype="Int64"),
    "text": ["Hola a todas.", "Bienvenida.", "Gracias por invitarme.", "Sí.", "Yo creo que no.", "Aplausos."],
    # speaker 0: a woman; speaker 1: a long man's turn outweighs a short unsure one; speaker 2: unsure
    "gender": ["F", None, "M", "F", "F", "F"], "gender_prob": [0.95, np.nan, 0.9, 0.9, 0.6, 0.99],
})


def test_audio_speakers_vote_weighted_by_duration():
    speakers = AudioSilver(Settings()).run({"bronze/audio_turns": AUDIO_TURNS})["audio_speakers"]
    assert list(speakers.columns) == ["speaker_id", "genero", "prob_mujer", "speech_time_s", "n_turns"]
    assert speakers.speaker_id.tolist() == [0, 1, 2]   # the turn without speaker is not a speaker
    assert speakers.genero.tolist() == ["mujer", "hombre", "no_determinado"]
    assert speakers.prob_mujer.tolist() == pytest.approx([0.95, (10 * 0.1 + 1 * 0.9) / 11, 0.6])
    assert speakers.speech_time_s.tolist() == [5.0, 11.0, 4.0] and speakers.n_turns.tolist() == [2, 2, 1]


def test_audio_turns_follow_the_contract_with_the_speaker_gender():
    turns = AudioSilver(Settings()).run({"bronze/audio_turns": AUDIO_TURNS})["audio_turns"]
    assert list(turns.columns) == ["turn", "tiempo_i", "tiempo_f", "speaker_id", "transcripcion", "genero_inferido"]
    assert turns.genero_inferido.tolist() == ["mujer", "mujer", "hombre", "hombre", "no_determinado", "no_determinado"]
    assert turns.tiempo_f.tolist() == AUDIO_TURNS.end.tolist() and turns.transcripcion[2] == "Gracias por invitarme."


def test_gender_threshold_is_configurable():
    speakers = AudioSilver(Settings(silver={"gender_threshold": 0.55})).run({"bronze/audio_turns": AUDIO_TURNS})
    assert speakers["audio_speakers"].genero.tolist() == ["mujer", "hombre", "mujer"]


# Silver pipeline

def test_silver_pipeline_writes_all_tables(tmp_path):
    ctx = make_ctx(tmp_path)
    ctx.lake.write("bronze", "video_detections", "vid1", DETECTIONS)
    ctx.lake.write("bronze", "audio_turns", "vid1", AUDIO_TURNS)
    with captured_log() as lines:
        SilverPipeline(ctx.settings)(ctx)
    for table, rows in {"video_people": 3, "video_presence": 5, "audio_speakers": 3, "audio_turns": 6,
                        "speaker_person": 3, "people": 6}.items():   # 3 on screen + 3 voices not linked
        assert len(ctx.lake.read("silver", table, "vid1")) == rows
    assert [line.split()[1] for line in lines] == ["video", "audio", "identity", "total"]
    assert "3 video_people, 5 video_presence" in lines[0]


def test_speaking_flickers_are_smoothed():
    # 3 s silent with a single "speaking" detection in the middle, then 3 s speaking with a single silent one
    scores = [-1.0] * 9 + [2.0] + [-1.0] * 9 + [2.0] * 9 + [-1.0] + [2.0] * 9
    flicker = detections(1, range(3, 3 + 4 * len(scores), 4), "F", 0.9, speaking=scores)
    smoothed = VideoSilver(Settings()).run({"bronze/video_detections": flicker})["video_presence"]
    assert smoothed.hablando.tolist() == [False, True]
    assert smoothed.tiempo_f[0] == pytest.approx(smoothed.tiempo_i[1])   # contiguous spans
    raw = VideoSilver(Settings(silver={"speaking_window_s": 0})).run({"bronze/video_detections": flicker})
    assert raw["video_presence"].hablando.tolist() == [False, True, False, True, False, True]


# Identity

def spans(*rows) -> pd.DataFrame:
    """silver video_presence from (person_id, tiempo_i, tiempo_f, hablando)."""
    return pd.DataFrame(rows, columns=["person_id", "tiempo_i", "tiempo_f", "hablando"]).astype({"person_id": "Int64"})


def turns(*rows) -> pd.DataFrame:
    """silver audio_turns from (speaker_id, tiempo_i, tiempo_f)."""
    t = pd.DataFrame(rows, columns=["speaker_id", "tiempo_i", "tiempo_f"]).astype({"speaker_id": "Int64"})
    return t.assign(turn=range(len(t)), transcripcion="", genero_inferido="no_determinado")


def speakers_of(t: pd.DataFrame) -> pd.DataFrame:
    """silver audio_speakers with the speech time of each speaker in `t`."""
    seconds = (t.tiempo_f - t.tiempo_i).groupby(t.speaker_id).sum()
    return pd.DataFrame({"speaker_id": seconds.index.astype("Int64"), "speech_time_s": seconds.values})


def video_people_of(presence: pd.DataFrame, genders: dict[int, str]) -> pd.DataFrame:
    """silver video_people of the people in `presence`, with the given gender."""
    ids = sorted(presence.person_id.unique())
    return pd.DataFrame({"person_id": pd.array(ids, dtype="Int64"), "genero": [genders.get(i, "mujer") for i in ids],
                         "screen_time_s": 10.0, "speaking_time_s": 5.0, "area": 0.3, "centrality": 0.8})


def identity(t, presence, speaker_genders=None, person_genders=None, **silver) -> dict[str, pd.DataFrame]:
    speakers = speakers_of(t)
    speakers["genero"] = [(speaker_genders or {}).get(s, "mujer") for s in speakers.speaker_id]
    tables = {"silver/audio_turns": t, "silver/audio_speakers": speakers, "silver/video_presence": presence,
              "silver/video_people": video_people_of(presence, person_genders or {})}
    return IdentitySilver(Settings(silver=silver)).run(tables)


def link(t, presence, **silver):
    return identity(t, presence, **silver)["speaker_person"].set_index("speaker_id")


def test_each_speaker_links_to_the_person_speaking_meanwhile():
    t = turns((0, 0, 4), (1, 4, 10), (0, 10, 12), (2, 12, 20))
    presence = spans((1, 0, 4.2, True), (1, 4.2, 12, False), (2, 0, 4, False), (2, 4.5, 10, True),
                     (1, 10, 12, True), (3, 12, 12.5, True), (3, 12.5, 20, False))
    links = link(t, presence)
    assert list(links.reset_index().columns) == ["speaker_id", "person_id", "overlap_s", "share"]
    assert links.person_id[0] == 1 and links.person_id[1] == 2
    assert links.overlap_s[0] == pytest.approx(6.0) and links.share[0] == pytest.approx(1.0)
    # Speaker 2 overlaps person 3 speaking for only 0.5 s: a voice off screen, but the candidate is kept for review
    assert pd.isna(links.person_id[2]) and links.overlap_s[2] == pytest.approx(0.5)


def test_link_needs_a_share_of_the_speech():
    t = turns((0, 0, 20))
    presence = spans((1, 0, 3, True))   # 3 s of 20: 15 % < 30 %
    assert pd.isna(link(t, presence).person_id[0])
    assert link(t, presence, min_link_share=0.1).person_id[0] == 1


def test_a_person_may_have_several_speakers_and_silent_speakers_have_none():
    # Diarization split one voice in two speakers; speaker 2 talks while nobody speaks on screen
    t = turns((0, 0, 5), (1, 5, 10), (2, 10, 15))
    presence = spans((1, 0, 10, True), (1, 10, 15, False))
    links = link(t, presence)
    assert links.person_id[0] == links.person_id[1] == 1
    assert pd.isna(links.person_id[2]) and links.overlap_s[2] == 0 and links.share[2] == 0


def test_turns_without_speaker_are_ignored():
    t = turns((0, 0, 5), (None, 5, 10))
    links = link(t, spans((1, 0, 10, True)))
    assert links.index.tolist() == [0] and links.overlap_s[0] == pytest.approx(5.0)


@pytest.mark.parametrize("video, audio, expected", [
    ("mujer", "mujer", ("mujer", "ambos")), ("mujer", "hombre", ("no_determinado", "conflicto")),
    ("no_determinado", "hombre", ("hombre", "audio")), ("hombre", None, ("hombre", "video")),
    (None, "no_determinado", ("no_determinado", "ninguna")),
])
def test_fuse_gender(video, audio, expected):
    assert fuse_gender(video, audio) == expected


def test_people_one_row_per_participant():
    # Speakers 0-2 talk while people 1-3 speak on screen; speaker 3 is a voice off screen; person 4 never talks
    t = turns((0, 0, 5), (1, 5, 10), (2, 10, 15), (3, 15, 20), (0, 20, 22))
    presence = spans((1, 0, 5, True), (2, 5, 10, True), (3, 10, 15, True), (4, 0, 22, False), (1, 20, 22, False))
    people = identity(t, presence, speaker_genders={0: "mujer", 1: "mujer", 2: "hombre", 3: "hombre"},
                      person_genders={1: "mujer", 2: "hombre", 3: "no_determinado", 4: "mujer"})["people"]
    assert list(people.columns) == ["participant_id", "person_id", "speaker_id", "genero", "genero_fuente",
                                    "screen_time_s", "speaking_time_s", "speech_time_s", "area", "centrality"]
    p = people.set_index("participant_id")
    assert p.index.tolist() == ["p1", "p2", "p3", "p4", "v3"]
    assert p.speaker_id.tolist()[:3] == [0, 1, 2] and pd.isna(p.speaker_id["p4"]) and pd.isna(p.person_id["v3"])
    assert p.genero.tolist() == ["mujer", "no_determinado", "hombre", "mujer", "hombre"]
    assert p.genero_fuente.tolist() == ["ambos", "conflicto", "audio", "video", "audio"]
    assert p.speech_time_s.tolist() == [7.0, 5.0, 5.0, 0.0, 5.0]   # all the speech of their speaker
    assert p.screen_time_s["v3"] == 0 and np.isnan(p.area["v3"])


def test_people_adds_the_speech_of_every_speaker_of_a_person():
    t = turns((0, 0, 5), (1, 5, 8))   # diarization split one voice in two speakers
    people = identity(t, spans((1, 0, 8, True)))["people"]
    assert people.participant_id.tolist() == ["p1"] and people.speaker_id.tolist() == [0]   # main: longest overlap
    assert people.speech_time_s.tolist() == [8.0]
