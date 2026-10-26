# SPDX-FileCopyrightText: 2026 Equipo 1: Attention Is All She Needs (Alba Camiña García, Pilar de la Fuente Diez, Rocío Jiménez Villén)
# SPDX-License-Identifier: Apache-2.0

import json

import pandas as pd
import pytest

from aiasn.core.gold.fusion import FusionGold, fusion_inputs
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
                                   "name_source": ["rotulo", "mencion", "ninguna"]}),
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
    GoldPipeline(settings)(ctx)
    assert len(ctx.lake.read("gold", "quadrants", "vid1")) > 0 and len(ctx.lake.read("gold", "summary", "vid1")) == 1
    assert json.loads(ctx.manifest.path.read_text())["steps"]["gold"]["status"] == "ok"
