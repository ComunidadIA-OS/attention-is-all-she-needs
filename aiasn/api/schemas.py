# SPDX-FileCopyrightText: 2026 Equipo 1: Attention Is All She Needs (Alba Camiña García, Pilar de la Fuente Diez, Rocío Jiménez Villén)
# SPDX-License-Identifier: Apache-2.0

"""The result of a video as the front shows it, one key per section, read from gold. Only reshaping: every figure is
already computed in silver and gold (ADR-0001)."""

import pandas as pd

from aiasn.core.silver.identity import participant_of
from aiasn.storage.lake import Lake


def status(manifest: dict) -> dict:
    return {"estado": manifest["status"], "pasos": {k: v.get("status") for k, v in manifest["steps"].items()},
            "error": manifest["error"]}


def result(lake: Lake, video_id: str) -> dict:
    gold = {t: lake.read("gold", t, video_id) for t in ("summary", "kpis", "graph_nodes", "graph_edges", "quadrants")}
    people = lake.read("silver", "people", video_id)
    kpis, nodes = gold["kpis"], gold["graph_nodes"]
    participants = nodes[nodes.tipo == "participante"]
    return {
        "veredicto": _verdict(gold["summary"].iloc[0]) | {"indice_global": _index(lake, video_id)},
        "metricas": {
            # shares of the time of determined gender; sin_determinar_pct: the part of all the time left out
            "voz_pct": _determined(_by_gender(kpis, "parity", "voz_s", pct=True)),
            "pantalla_pct": _determined(_by_gender(kpis, "parity", "pantalla_s", pct=True)),
            "sin_determinar_pct": {"voz": _by_gender(kpis, "parity", "voz_s", pct=True).get("no_determinado"),
                                   "pantalla": _by_gender(kpis, "parity", "pantalla_s", pct=True).get("no_determinado")},
            # RVP (spec 21 §1.3): share of voice over share of screen; voz_activa_en_pantalla: screen time speaking
            "ratio_voz_pantalla": _rvp(_by_gender(kpis, "parity", "voz_s", pct=True),
                                       _by_gender(kpis, "parity", "pantalla_s", pct=True)),
            "voz_activa_en_pantalla": _determined(_by_gender(kpis, "parity", "voz_activa_en_pantalla")),
            "referentes": _by_gender(kpis, "references", value=True),
        },
        "personas": _people(participants, people),
        "temas": _topics(kpis, nodes),
        "poder": {
            "centralidad_media": _determined(_by_gender(kpis, "parity", "centralidad")),
            "area_media": _determined(_by_gender(kpis, "parity", "area")),   # mean share of the frame on screen
            "personas_distintas": participants.genero.value_counts().to_dict(),
            "veces_citado_como_referente": _by_gender(kpis, "references", value=True),
            "referentes": _references(lake.read("silver", "nlp_references", video_id), participants),
        },
        "roles": _records(participants.dropna(subset=["role_es"]).groupby(["role_es", "genero"], as_index=False)
                          .speech_time_s.sum().rename(columns={"role_es": "rol", "speech_time_s": "voz_s"})),
        "clima": _tone(kpis),
        "autoridad": {   # shares within each gender, from the KPIs of gold
            "voz_con_autoridad_pct": _by_gender(kpis, "authority", pct=True),
            "presentacion_con_cargo_pct": _by_gender(kpis, "naming", pct=True),
            "ideas": _ideas(kpis),
        },
        "constelacion": {"nodos": _records(nodes.rename(columns={"node_id": "id"})),
                         "aristas": _records(gold["graph_edges"])},
        "kpis": _records(kpis),   # every KPI, long format (valor / base), for what the sections above do not show
        **_segments(gold["quadrants"], lake.read("silver", "speaker_person", video_id)),
    }


def _segments(quadrants: pd.DataFrame, links: pd.DataFrame) -> dict:
    """The spans of the four quadrants with who is in each, and apart those of undetermined gender: what a person
    reviews (ADR-0005, art. 14 AI Act)."""
    by_speaker = participant_of(links)
    track = quadrants.track_id.astype("string").str.removeprefix("person_")
    who = ("p" + track).where(track.notna(), quadrants.hablante_id.map(lambda s: by_speaker.get(int(s)) if pd.notna(s) else None))
    seg = pd.DataFrame({"inicio": quadrants.tiempo_i, "fin": quadrants.tiempo_f, "segundos": quadrants.duracion_s,
                        "cuadrante": quadrants.cuadrante, "tipo": quadrants.tipo_cuadrante,
                        "genero": quadrants.genero, "persona": who, "texto": quadrants.transcripcion})
    seg = seg.sort_values(["inicio", "cuadrante"], kind="stable")
    return {"segmentos": _records(seg), "segmentos_dudosos": _records(seg[seg.genero == "no_determinado"])}


def _rvp(voice: dict, screen: dict) -> dict:
    return {g: round(voice[g] / screen[g], 2) if screen.get(g) else None for g in _determined(voice)}


def _index(lake: Lake, video_id: str) -> dict | None:
    """Índice Global de Representación (spec 21 §4) and its four signals, 0-100; None for a video from before it."""
    if not lake.exists("gold", "index", video_id):
        return None
    i = lake.read("gold", "index", video_id).iloc[0]
    return {"total": _clean(i.indice), "provisional": bool(i.provisional),
            "dimensiones": {k: _clean(i[k]) for k in ("pantalla", "voz", "espacio", "autoridad")}}


def _tif(s: pd.Series) -> dict:
    """Test de Interlocucion Femenina (doc 26 §5): its state, and the score and rules only when it is evaluated."""
    score = _clean(s.get("bechdel_puntuacion_bechdel_0_3"))
    rules = ("regla_1_pluralidad_femenina", "regla_2_identidad_propia", "regla_3_dialogo_horizontal")
    counts = ("mujeres_presentes", "hombres_presentes", "personas_con_voz", "mujeres_distintas_hablando",
              "mujeres_con_rotulo_identificado", "transiciones_mujer_a_mujer")
    return {
        "estado": s.get("bechdel_estado"), "motivo": _clean(s.get("bechdel_motivo")),
        "puntuacion_0_3": None if score is None else int(score),
        "supera": bool(s.get("bechdel_supera_bechdel_digital")),
        "diagnostico": _clean(s.get("bechdel_diagnostico_tif")), "texto": s.get("bechdel_diagnostico_bechdel"),
        "reglas": {r: None if _clean(s.get(f"bechdel_{r}")) is None else bool(s.get(f"bechdel_{r}")) for r in rules},
        **{c: int(s.get(f"bechdel_{c}") or 0) for c in counts},
    }


def _determined(shares: dict) -> dict:
    return {g: v for g, v in shares.items() if g != "no_determinado"}


SAFEGUARD = ("cuota_femenina", "cuota_masculina", "cuota_no_binaria", "suelo_femenino_exigido",
             "techo_masculino_ajustado", "regimen_aplicado")   # ADR-0006


def _verdict(s: pd.Series) -> dict:
    return {
        "resumen_lectura_facil": s.resumen_lectura_facil,
        "alerta_equality_washing": bool(s.alerta_equality_washing), "motivo_alerta": s.motivo_alerta,
        "alerta_infrarrepresentacion": bool(s.alerta_infrarrepresentacion),
        "motivo_infrarrepresentacion": s.motivo_infrarrepresentacion,
        "bechdel": _tif(s),
        "salvaguarda_paridad": {"cumple": bool(s.salvaguarda_cumple_salvaguarda_paridad),
                                **{k: _clean(s.get(f"salvaguarda_{k}")) for k in SAFEGUARD}},
        "valoracion_ciudadana": None,   # not measured yet
    }


def _by_gender(kpis: pd.DataFrame, kpi: str, categoria: str | None = None, pct: bool = False,
               value: bool = False) -> dict:
    """valor / base of each gender (x100 with `pct`), or the count valor with `value`; None where base is 0."""
    rows = kpis[(kpis.kpi == kpi) & ((kpis.categoria == categoria) if categoria else kpis.categoria.isna())]
    if value:
        return {r.genero: int(r.valor) for r in rows.itertuples()}   # counts
    return {r.genero: round(r.valor / r.base * (100 if pct else 1), 1 if pct else 3) if r.base else None
            for r in rows.itertuples()}


def _people(participants: pd.DataFrame, people: pd.DataFrame) -> list[dict]:
    names, titles_en = people.set_index("participant_id").name, people.set_index("participant_id").title_en
    out = pd.DataFrame({"id": participants.node_id, "nombre": participants.node_id.map(names),
                        "cargo": participants.title, "genero": participants.genero, "rol": participants.role_es,
                        "autoridad": participants.authority, "pantalla_s": participants.screen_time_s,
                        "voz_s": participants.speech_time_s,
                        # mean share of the frame and centrality (1 at the centre) while on screen
                        "area": participants.area, "centralidad": participants.centrality,
                        # word2vec gender bias of their caption title, scored in English (> 0: towards "she")
                        "cargo_en": participants.node_id.map(titles_en), "sesgo_cargo": participants.sesgo})
    return _records(out)


def _topics(kpis: pd.DataFrame, nodes: pd.DataFrame) -> list[dict]:
    t = kpis[kpis.kpi == "topics"]
    bias = nodes[nodes.tipo == "tema"].set_index("clave").sesgo
    return _records(pd.DataFrame({"tema": t.categoria_es, "clave": t.categoria, "genero": t.genero,
                                  "personas": t.valor.astype(int), "pct": (t.valor / t.base * 100).round(1),
                                  "sesgo": t.categoria.map(bias)}))


def _references(refs: pd.DataFrame, participants: pd.DataFrame) -> list[dict]:
    """Each well-known person cited as a reference, with their gender, how many times and by whom (as the graph names
    the participants), most cited first."""
    if refs.empty:
        return []
    label = participants.set_index("node_id").label
    out = []
    for name, g in refs.groupby("name", sort=False):
        by = list(dict.fromkeys(label.get(p, p) for p in g.participant_id.dropna()))
        out.append({"nombre": name, "genero": _clean(g.genero.iloc[0]), "veces": len(g), "citado_por": by})
    return sorted(out, key=lambda r: -r["veces"])


def _ideas(kpis: pd.DataFrame) -> dict:
    """The key ideas split into groups that add up to 100: those brought only by one gender, and those shared by
    several. An idea belongs to exactly one gender alone or is shared, so shared = total - those alone."""
    alone = kpis[(kpis.kpi == "ideas") & (kpis.categoria == "solo")]
    total = int(alone.base.iloc[0]) if len(alone) else 0
    pct = lambda n: round(float(n) / total * 100, 1) if total else None
    return {"total": total, "solo_pct": {r.genero: pct(r.valor) for r in alone.itertuples()},
            "compartidas_pct": pct(total - alone.valor.sum())}


def _tone(kpis: pd.DataFrame) -> dict:
    t = kpis[kpis.kpi == "tone"]
    return {g: {r.categoria_es: round(r.valor / r.base * 100, 1) for r in rows.itertuples()}
            for g, rows in t.groupby("genero")}


def _records(df: pd.DataFrame) -> list[dict]:
    return [{k: _clean(v) for k, v in row.items()} for row in df.to_dict("records")]


def _clean(v):
    """JSON-ready: NaN and NA as None, numpy numbers as Python ones, floats to 3 decimals."""
    if v is None or (not isinstance(v, (list, dict, str)) and pd.isna(v)):
        return None
    v = v.item() if hasattr(v, "item") else v
    return round(v, 3) if isinstance(v, float) else v
