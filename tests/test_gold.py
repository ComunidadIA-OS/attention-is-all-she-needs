# SPDX-FileCopyrightText: 2026 Equipo 1: Attention Is All She Needs (Alba Camiña García, Pilar de la Fuente Diez, Rocío Jiménez Villén)
# SPDX-License-Identifier: Apache-2.0

import json

import pandas as pd
import pytest

from aiasn.core.gold import kpis as kpis_module
from aiasn.core.gold.fusion import FusionGold, fusion_inputs
from aiasn.core.gold.graph import GraphGold
from aiasn.core.gold.kpis import KPIS, KpisGold, kpi
from aiasn.pipelines.context import RunContext
from aiasn.pipelines.gold import GoldPipeline
from aiasn.settings import Settings
from aiasn.storage.lake import Lake
from aiasn.storage.manifest import Manifest


def I(*values) -> pd.arrays.IntegerArray:
    return pd.array(values, dtype="Int64")


# Silver of a short piece: Marta (person 1, speaker 0) speaks on screen with her caption; Luis (person 2) is on
# screen in silence; a narrator (speaker 1) speaks off screen
SILVER = {
    "silver/audio_turns": pd.DataFrame({
        "turn": [0, 1, 2], "tiempo_i": [0.0, 10.0, 20.0], "tiempo_f": [10.0, 20.0, 30.0], "speaker_id": I(0, 1, 0),
        "transcripcion": ["Hola", "Narración", "Gracias"], "genero_inferido": ["mujer", "hombre", "mujer"]}),
    "silver/speaker_person": pd.DataFrame({"speaker_id": I(0, 1), "person_id": I(1, pd.NA),
                                           "overlap_s": [20.0, 0.0], "share": [1.0, 0.0]}),
    "silver/video_people": pd.DataFrame({"person_id": I(1, 2), "genero": ["mujer", "hombre"], "prob_mujer": [0.95, 0.05],
                                         "area": [0.3, 0.2], "centrality": [0.9, 0.5]}),
    "silver/video_presence": pd.DataFrame({"person_id": I(1, 1, 2), "tiempo_i": [0.0, 10.0, 0.0],
                                           "tiempo_f": [10.0, 30.0, 30.0], "hablando": [True, False, False]}),
    "silver/people": pd.DataFrame({"participant_id": ["p1", "p2", "v1"], "person_id": I(1, 2, pd.NA),
                                   "name": ["Marta Ruiz", "Luis", None], "title": ["Investigadora", None, None],
                                   "name_source": ["rotulo", "mencion", "ninguna"],
                                   "genero": ["mujer", "hombre", "hombre"], "speech_time_s": [20.0, 0.0, 10.0],
                                   "genero_fuente": ["ambos", "video", "audio"], "screen_time_s": [30.0, 30.0, 0.0],
                                   "area": [0.3, 0.2, None], "centrality": [0.9, 0.5, None],
                                   "title_en": ["researcher", None, None]}),
}


def test_fusion_inputs_carry_identity_and_caption_names():
    audio, video = fusion_inputs(SILVER)
    assert audio.track_id.fillna("").tolist() == ["person_1", "", "person_1"]   # the narrator is no one on screen
    assert video.track_id.tolist() == ["person_1", "person_2"]          # contiguous spans: one stretch each
    assert video.rotulo_nombre.tolist()[0] == "Marta Ruiz"
    assert pd.isna(video.rotulo_nombre.tolist()[1])                     # a name from a mention is not a caption


def test_fusion_gold_quadrants_and_summary():
    out = FusionGold(Settings()).run(SILVER)
    q = out["quadrants"]
    assert q.groupby("cuadrante").duracion_s.sum().to_dict() == {1: 20.0, 2: 40.0, 3: 10.0}
    assert q[q.cuadrante == 1].track_id.unique().tolist() == ["person_1"]   # Marta, not guessed by gender
    s = out["summary"].iloc[0]
    assert s.pct_voz_mujer == pytest.approx(66.67, abs=0.01)
    assert s.bechdel_mujeres_con_rotulo_identificado == 1 and "por_genero" not in out["summary"]
    assert {"alerta_equality_washing", "salvaguarda_cumple_salvaguarda_paridad", "resumen_lectura_facil"} <= set(s.index)


def test_fusion_gold_uses_the_silver_threshold():
    # Above Marta's face probability (0.95) the fusion abstains on her face, like silver; Luis is left undetermined
    q = FusionGold(Settings(silver={"gender_threshold": 0.99})).run(SILVER)["quadrants"]
    assert set(q[q.track_id == "person_2"].genero) == {"no_determinado"}
    assert set(q[q.cuadrante == 1].genero) == {"mujer"}   # her voice, decided in silver, still says who she is


def test_gold_pipeline_writes_the_lake(tmp_path):
    settings = Settings(lake_dir=tmp_path / "lake", tmp_dir=tmp_path / "tmp")
    ctx = RunContext("vid1", settings, Lake(settings.lake_dir), Manifest(settings.lake_dir, "vid1"),
                     settings.tmp_dir / "vid1")
    for ref, df in SILVER.items():
        ctx.lake.write(*ref.split("/"), "vid1", df)
    for ref, df in NLP_SILVER.items():
        ctx.lake.write(*ref.split("/"), "vid1", df)
    GoldPipeline(settings)(ctx)
    assert len(ctx.lake.read("gold", "quadrants", "vid1")) > 0 and len(ctx.lake.read("gold", "summary", "vid1")) == 1
    assert set(ctx.lake.read("gold", "kpis", "vid1").kpi) == set(KPIS)
    assert json.loads(ctx.manifest.path.read_text())["steps"]["gold"]["status"] == "ok"


# KPIs

PEOPLE = pd.DataFrame({"participant_id": ["p1", "p2", "v1"], "genero": ["mujer", "hombre", "hombre"],
                       "speech_time_s": [20.0, 0.0, 10.0], "title_en": ["researcher", None, None]})
NLP_SILVER = {
    "silver/person_names": pd.DataFrame({"participant_id": ["p1", "p1", "p2", "p1"], "name": ["Marta", "Marta", "Luis", "Marta Ruiz"],
                                         "title": ["doctora", None, "director", "Investigadora"],
                                         "source": ["mencion", "mencion", "mencion", "rotulo"],
                                         "said_by": ["v1", "v1", "p1", None]}),
    "silver/nlp_roles": pd.DataFrame({"participant_id": ["p1", "v1"], "role": ["testimony", "voice-over narrator"],
                                      "role_es": ["testimonio", "narrador/a en off"],
                                      "authority": [True, True], "authority_source": ["rotulo", "rol"]}),
    "silver/nlp_topics": pd.DataFrame({"participant_id": ["p1", "p1", "v1"], "turn": [0, 2, 1],
                                       "topic": ["technology", "care", "history"],
                                       "topic_es": ["tecnología", "cuidados", "historia"], "evidence": ["", "", ""]}),
    "silver/nlp_references": pd.DataFrame({"participant_id": ["p1", "v1", "v1"], "turn": [0, 1, 1],
                                           "name": ["Ada Lovelace", "Ada Lovelace", "Alan Turing"],
                                           "genero": ["mujer", "mujer", "hombre"]}),
    "silver/nlp_ideas": pd.DataFrame({"idea_id": [0, 0, 1, 2], "idea": ["a", "a", "b", "c"],
                                      "participant_id": ["p1", "v1", "p1", "v1"]}),
    "silver/term_bias": pd.DataFrame({"termino": ["technology", "care", "history", "researcher"],
                                      "tipo": ["tema", "tema", "tema", "cargo"],
                                      "sesgo": pd.array([-0.04, 0.16, pd.NA, 0.09], dtype="Float64")}),
    "silver/nlp_tone": pd.DataFrame({"participant_id": ["p1", "v1", "p1"], "turn": [0, 1, 2],
                                     "tone": ["technical_assertive", "dissent", None],
                                     "tone_es": ["técnico/asertivo", "disenso", None], "score": [None] * 3}),
}


def kpi_rows(name: str, labels: bool = False) -> pd.DataFrame:
    tables = SILVER | NLP_SILVER | {"silver/people": PEOPLE,
                                    "gold/quadrants": FusionGold(Settings()).run(SILVER)["quadrants"]}
    out = KPIS[name](tables, Settings())
    assert list(out.columns) == ["kpi", "genero", "categoria", "categoria_es", "valor", "base"] and (out.kpi == name).all()
    return out.set_index(["genero", "categoria"])[["valor", "base"] + (["categoria_es"] if labels else [])]


def test_parity_seconds_and_shares():
    p = kpi_rows("parity")
    assert p.loc[("mujer", "voz_s")].tolist() == [20.0, 30.0]   # 20 of the 30 s of voice
    assert p.loc[("hombre", "c3_voz_off")].tolist() == [10.0, 10.0]
    ratio = p.loc[("mujer", "voz_activa_en_pantalla")]
    assert ratio.valor / ratio.base == pytest.approx(20 / 30)  # speaking 20 of her 30 s on screen
    assert p.loc[("mujer", "area")].valor / p.loc[("mujer", "area")].base == pytest.approx(0.3)


def test_authority_share_of_speech():
    a = kpi_rows("authority")
    assert a.loc[("mujer", None)].tolist() == [20.0, 20.0] and a.loc[("hombre", None)].tolist() == [10.0, 10.0]


def test_topics_by_gender_of_who_speaks():
    t = kpi_rows("topics", labels=True)
    assert t.loc[("mujer", "care")].tolist() == [1.0, 2.0, "cuidados"]
    assert t.loc[("hombre", "history")].tolist() == [1.0, 1.0, "historia"]


def test_references_count_each_person_cited_once():
    r = kpi_rows("references")
    assert r.loc[("mujer", None)].tolist() == [1.0, 2.0] and r.loc[("hombre", None)].tolist() == [1.0, 2.0]


def test_naming_counts_mentions_with_title():
    n = kpi_rows("naming")
    assert n.loc[("mujer", None)].tolist() == [1.0, 2.0]   # "doctora" once of her two mentions; the caption is not one
    assert n.loc[("hombre", None)].tolist() == [1.0, 1.0]


def test_ideas_with_and_only_by_each_gender():
    i = kpi_rows("ideas")
    assert i.loc[("mujer", "con")].tolist() == [2.0, 3.0] and i.loc[("mujer", "solo")].tolist() == [1.0, 3.0]
    assert i.loc[("hombre", "solo")].tolist() == [1.0, 3.0]


def test_tone_aggregated_by_gender():
    t = kpi_rows("tone", labels=True)
    assert t.loc[("mujer", "technical_assertive")].tolist() == [1.0, 1.0, "técnico/asertivo"]   # untoned turn left out
    assert t.loc[("hombre", "dissent")].tolist() == [1.0, 1.0, "disenso"]


def test_kpis_registry(monkeypatch):
    monkeypatch.setattr(kpis_module, "KPIS", dict(KPIS))

    @kpi("constant")
    def constant(tables, settings):
        return kpis_module.rows("constant", [("mujer", None, 1, 2)])

    assert kpis_module.KPIS["constant"] is constant and "constant" not in KPIS   # registered on the patched copy only
    tables = SILVER | NLP_SILVER | {"silver/people": PEOPLE,
                                    "gold/quadrants": FusionGold(Settings()).run(SILVER)["quadrants"]}
    out = KpisGold(Settings()).run(tables)["kpis"]
    assert set(out.kpi) == set(KPIS) | {"constant"} and out.valor.dtype == float


# Graph

GRAPH_PEOPLE = pd.DataFrame({
    "participant_id": ["p1", "p2", "v1"], "person_id": I(1, 2, pd.NA), "speaker_id": I(0, pd.NA, 1),
    "genero": ["mujer", "hombre", "hombre"], "genero_fuente": ["ambos", "video", "audio"],
    "screen_time_s": [30.0, 30.0, 0.0], "speaking_time_s": [10.0, 0.0, 0.0], "speech_time_s": [20.0, 0.0, 10.0],
    "area": [0.3, 0.2, None], "centrality": [0.9, 0.5, None],
    "name": ["Marta Ruiz", None, None], "title": ["Investigadora", None, None],
    "name_source": ["rotulo", "ninguna", "ninguna"], "title_authority": pd.array([True, pd.NA, pd.NA], "boolean"),
    "title_en": ["researcher", None, None]})


GRAPH_NAMES = pd.DataFrame({   # silver person_names
    "participant_id": ["p1", "p1", "p1", "p2"], "name": ["Marta Ruiz", "Marta", "Marta", "Luis"],
    "title": ["Investigadora", "doctora", None, None], "source": ["rotulo", "mencion", "mencion", "mencion"],
    "said_by": [None, "v1", "v1", "p2"], "turn": I(pd.NA, 1, 1, 2)})


def graph() -> dict[str, pd.DataFrame]:
    tables = SILVER | NLP_SILVER | {"silver/people": GRAPH_PEOPLE, "silver/person_names": GRAPH_NAMES}
    return GraphGold(Settings()).run(tables)


def test_graph_nodes_participants_and_topics():
    nodes = graph()["graph_nodes"].set_index("node_id")
    assert nodes.index.tolist() == ["p1", "p2", "v1", "tema:care", "tema:history", "tema:technology"]
    assert nodes.tipo.tolist() == ["participante"] * 3 + ["tema"] * 3
    assert nodes.label.tolist() == ["Marta Ruiz", "Persona 2", "Voz 1", "cuidados", "historia", "tecnología"]
    assert nodes.loc[["p1", "p2", "v1"], "size"].tolist() == [20.0, 30.0, 10.0]   # speech, else screen time
    assert nodes.loc["tema:technology", "clave"] == "technology" and nodes.loc["tema:care", "size"] == 1
    assert nodes.loc["p1", "role_es"] == "testimonio" and nodes.loc["p1", "authority_source"] == "rotulo"
    assert nodes.authority.tolist()[:3] == [True, pd.NA, True]                     # p2 never speaks: no role
    assert "age" not in nodes and "tone" not in nodes


def test_graph_edges():
    edges = graph()["graph_edges"]
    assert list(edges.columns) == ["source", "target", "tipo", "peso", "peso_extra"]
    e = edges.set_index(["tipo", "source", "target"])
    # The narrator names Marta twice, once with a title; Luis naming himself is no edge
    assert e.loc[("menciona", "v1", "p1")].tolist() == [2.0, 1.0] and ("menciona", "p2", "p2") not in e.index
    # Marta, the narrator, Marta again
    assert e.loc[("turno", "p1", "v1"), "peso"] == 1 and e.loc[("turno", "v1", "p1"), "peso"] == 1
    # On screen together from 0 to 30 s (Marta's two spans and Luis's one)
    assert e.loc[("comparte_plano", "p1", "p2"), "peso"] == pytest.approx(30.0)
    # Marta talks about two topics in two turns; the narrator about one: no topic shared
    assert sorted(e.loc["habla_de"].index.tolist()) == [("p1", "tema:care"), ("p1", "tema:technology"),
                                                         ("v1", "tema:history")]
    assert set(edges.peso_extra.dropna().index) <= set(edges.index[edges.tipo == "menciona"])


def test_shared_topic_joins_two_participants():
    topics = NLP_SILVER["silver/nlp_topics"].assign(topic=["technology", "care", "technology"])
    tables = SILVER | NLP_SILVER | {"silver/people": GRAPH_PEOPLE, "silver/person_names": GRAPH_NAMES,
                                    "silver/nlp_topics": topics}
    e = GraphGold(Settings()).run(tables)["graph_edges"]
    assert set(e[(e.tipo == "habla_de") & (e.target == "tema:technology")].source) == {"p1", "v1"}


def test_stereotype_mean_bias_of_topics_and_titles():
    tables = SILVER | NLP_SILVER | {"silver/people": PEOPLE,
                                    "gold/quadrants": FusionGold(Settings()).run(SILVER)["quadrants"]}
    s = KPIS["stereotype"](tables, Settings()).set_index(["genero", "categoria"])
    # Marta talks about technology and care; the narrator about history, which has no score
    assert s.loc[("mujer", "temas"), "valor"] == pytest.approx(0.12) and s.loc[("mujer", "temas"), "base"] == 2
    assert ("hombre", "temas") not in s.index
    assert s.loc[("mujer", "cargos"), ["valor", "base"]].tolist() == pytest.approx([0.09, 1])


def test_graph_nodes_carry_the_bias():
    nodes = graph()["graph_nodes"].set_index("node_id")
    assert nodes.sesgo["tema:care"] == pytest.approx(0.16) and pd.isna(nodes.sesgo["tema:history"])
    assert nodes.sesgo["p1"] == pytest.approx(0.09) and pd.isna(nodes.sesgo["v1"])   # her title, researcher
