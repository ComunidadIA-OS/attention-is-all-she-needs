# SPDX-FileCopyrightText: 2026 Equipo 1: Attention Is All She Needs (Alba Camiña García, Pilar de la Fuente Diez, Rocío Jiménez Villén)
# SPDX-License-Identifier: Apache-2.0

"""KPIs of a video, by gender, for the front.

Every KPI is a function decorated with `@kpi(name)`: adding one is writing it here, removing one is deleting it.
Each returns rows of gold/kpis: `valor` is an amount (seconds, counts) and `base` the total it is a share of, so a
video's figure is valor / base and several videos are aggregated as sum(valor) / sum(base).
"""

from collections.abc import Callable

import pandas as pd

from aiasn.core.fusion import calcular_kpis_paridad
from aiasn.core.transform import Transform
from aiasn.settings import Settings

UNDETERMINED = "no_determinado"
COLUMNS = ["kpi", "genero", "categoria", "categoria_es", "valor", "base"]   # categoria_es: Spanish label, for the UI
Tables = dict[str, pd.DataFrame]
KPIS: dict[str, Callable[[Tables, Settings], pd.DataFrame]] = {}


def kpi(name: str):
    """Registers the function as the KPI `name` (its rows in gold/kpis)."""
    def register(fn: Callable[[Tables, Settings], pd.DataFrame]):
        KPIS[name] = fn
        return fn
    return register


def rows(name: str, records: list[tuple], labels: dict[str, str] | None = None) -> pd.DataFrame:
    """gold/kpis rows of a KPI from (genero, categoria, valor, base) tuples; `labels`: Spanish of each categoria."""
    df = pd.DataFrame([(name, g, c, v, b) for g, c, v, b in records],
                      columns=["kpi", "genero", "categoria", "valor", "base"])
    return df.assign(categoria_es=df.categoria.map(labels or {}))[COLUMNS]


def with_gender(df: pd.DataFrame, people: pd.DataFrame, column: str = "participant_id") -> pd.DataFrame:
    """`df` with the gender of the participant in `column`, from silver people."""
    return df.assign(genero=df[column].map(people.set_index("participant_id").genero))


@kpi("parity")
def parity(tables: Tables, settings: Settings) -> pd.DataFrame:
    """Seconds of voice, screen and each quadrant by gender, from the fusion (calcular_kpis_paridad).

    Voice and screen are shares of the time of determined gender (spec 21 §5.3, ADR-0005); for no_determinado, of all
    the time: how much could not be measured. `voz_activa_en_pantalla` is the screen time spent speaking (C1 over
    screen); `area` and `centralidad` are weighted by screen time.
    """
    events = tables["gold/quadrants"]
    if events.empty:
        return rows("parity", [])
    k = calcular_kpis_paridad(events)
    by_gender = k["por_genero"]
    quadrant_total = {q: sum(g[q] for g in by_gender.values())
                      for q in ("c1_voz_activa_s", "c2_presencia_muda_s", "c3_voz_off_s")}
    records = []
    for gender, g in by_gender.items():
        screen, det = g["tiempo_pantalla_s"], gender != UNDETERMINED
        records += [(gender, "voz_s", g["tiempo_voz_s"], k["total_voz_determinado_s" if det else "total_voz_segundos"]),
                    (gender, "pantalla_s", screen,
                     k["total_pantalla_determinado_s" if det else "total_pantalla_segundos"]),
                    *[(gender, q.removesuffix("_s"), g[q], quadrant_total[q]) for q in quadrant_total],
                    (gender, "voz_activa_en_pantalla", g["c1_voz_activa_s"], screen),
                    (gender, "area", g["area_media"] * screen, screen),
                    (gender, "centralidad", g["centralidad_media"] * screen, screen)]
    return rows("parity", records)


@kpi("authority")
def authority(tables: Tables, settings: Settings) -> pd.DataFrame:
    """Seconds of speech in a role of authority (silver nlp_roles), over all the speech of each gender."""
    people = tables["silver/people"]
    roles = tables["silver/nlp_roles"].groupby("participant_id").authority.any()
    speaking = people[people.speech_time_s > 0]
    with_authority = speaking.participant_id.map(roles).fillna(False).astype(bool)
    seconds = speaking.speech_time_s.where(with_authority, 0.0).groupby(speaking.genero).sum()
    totals = speaking.groupby("genero").speech_time_s.sum()
    return rows("authority", [(gender, None, seconds[gender], total) for gender, total in totals.items()])


@kpi("topics")
def topics(tables: Tables, settings: Settings) -> pd.DataFrame:
    """Turns on each topic by the gender of who speaks, over all the topic turns of that gender."""
    t = with_gender(tables["silver/nlp_topics"], tables["silver/people"])
    counts = t.groupby(["genero", "topic"]).size()
    totals = t.groupby("genero").size()
    labels = dict(zip(t.topic, t.topic_es))
    return rows("topics", [(gender, topic, n, totals[gender]) for (gender, topic), n in counts.items()], labels)


@kpi("references")
def references(tables: Tables, settings: Settings) -> pd.DataFrame:
    """Distinct well-known people cited, by their gender, over all the people cited."""
    cited = tables["silver/nlp_references"].drop_duplicates("name")
    counts = cited.groupby("genero").size()
    return rows("references", [(gender, None, n, len(cited)) for gender, n in counts.items()])


@kpi("naming")
def naming(tables: Tables, settings: Settings) -> pd.DataFrame:
    """Mentions of the participants that give a title or position, over all their mentions, by the gender of who is
    mentioned (are women introduced with their title as often as men?)."""
    names = tables["silver/person_names"]
    m = with_gender(names[names.source == "mencion"], tables["silver/people"])
    titled = m.title.notna().groupby(m.genero).sum()
    totals = m.groupby("genero").size()
    return rows("naming", [(gender, None, titled[gender], total) for gender, total in totals.items()])


@kpi("ideas")
def ideas(tables: Tables, settings: Settings) -> pd.DataFrame:
    """Key ideas contributed with someone of each gender (`con`) and only by that gender (`solo`), over all ideas."""
    i = with_gender(tables["silver/nlp_ideas"], tables["silver/people"])
    genders = i.groupby("idea_id").genero.agg(set)
    records = []
    for gender in sorted(set().union(*genders)) if len(genders) else []:
        records += [(gender, "con", sum(gender in g for g in genders), len(genders)),
                    (gender, "solo", sum(g == {gender} for g in genders), len(genders))]
    return rows("ideas", records)


@kpi("tone")
def tone(tables: Tables, settings: Settings) -> pd.DataFrame:
    """Turns of each tone by gender, over the classified turns of that gender. Only aggregated, never per person
    (ADR-0009)."""
    t = with_gender(tables["silver/nlp_tone"].dropna(subset=["tone"]), tables["silver/people"])
    counts = t.groupby(["genero", "tone"]).size()
    totals = t.groupby("genero").size()
    labels = dict(zip(t.tone, t.tone_es))
    return rows("tone", [(gender, tone_, n, totals[gender]) for (gender, tone_), n in counts.items()], labels)


@kpi("stereotype")
def stereotype(tables: Tables, settings: Settings) -> pd.DataFrame:
    """Mean word2vec gender bias (> 0: towards "she") of the topics each gender talks about, per topic turn, and of
    their caption titles, per participant. Only terms in the vocabulary count."""
    people, bias = tables["silver/people"], tables["silver/term_bias"]
    score = {(t.tipo, t.termino): t.sesgo for t in bias.dropna(subset=["sesgo"]).itertuples()}
    topics = with_gender(tables["silver/nlp_topics"], people)
    topics = topics.assign(sesgo=[score.get(("tema", t)) for t in topics.topic]).dropna(subset=["sesgo"])
    titled = people.assign(sesgo=[score.get(("cargo", t)) for t in people.title_en]).dropna(subset=["sesgo"])
    records = []
    for categoria, df in (("temas", topics), ("cargos", titled)):
        by_gender = df.groupby("genero").sesgo
        totals, counts = by_gender.sum(), by_gender.size()
        records += [(gender, categoria, totals[gender], n) for gender, n in counts.items()]
    return rows("stereotype", records, {"temas": "temas", "cargos": "cargos"})


class KpisGold(Transform):
    name, layer = "kpis", "gold"
    inputs = ["gold/quadrants", "silver/people", "silver/person_names", "silver/nlp_roles", "silver/nlp_topics",
              "silver/nlp_references", "silver/nlp_ideas", "silver/nlp_tone", "silver/term_bias"]
    outputs = ["kpis"]

    def run(self, tables: Tables) -> dict[str, pd.DataFrame]:
        kpis = pd.concat([fn(tables, self.settings) for fn in KPIS.values()], ignore_index=True)
        return {"kpis": kpis.astype({"valor": float, "base": float})}
