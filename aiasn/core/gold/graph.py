# SPDX-FileCopyrightText: 2026 Equipo 1: Attention Is All She Needs (Alba Camiña García, Pilar de la Fuente Diez, Rocío Jiménez Villén)
# SPDX-License-Identifier: Apache-2.0

"""The graph of a video for the front: the participants and the topics they talk about, and how they relate."""

from collections import Counter

import numpy as np
import pandas as pd

from aiasn.core.silver.identity import participant_of
from aiasn.core.transform import Transform

PARTICIPANT, TOPIC = "participante", "tema"
# sesgo: word2vec gender bias of the topic, or of the participant's caption title (> 0: towards "she")
NODES = ["node_id", "tipo", "label", "clave", "size", "sesgo", "genero", "genero_fuente", "role", "role_es",
         "authority", "authority_source", "title", "screen_time_s", "speech_time_s", "area", "centrality"]
EDGES = ["source", "target", "tipo", "peso", "peso_extra"]   # peso_extra: mentions with a title (menciona only)


def topic_node(topic: str) -> str:
    return f"tema:{topic}"


class GraphGold(Transform):
    name, layer = "graph", "gold"
    inputs = ["silver/people", "silver/nlp_roles", "silver/nlp_topics", "silver/person_names", "silver/audio_turns",
              "silver/speaker_person", "silver/video_presence", "silver/term_bias"]
    outputs = ["graph_nodes", "graph_edges"]

    def run(self, tables: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
        bias = tables["silver/term_bias"].dropna(subset=["sesgo"])
        score = {(t.tipo, t.termino): t.sesgo for t in bias.itertuples()}
        participants = self._participants(tables["silver/people"], tables["silver/nlp_roles"])
        participants["sesgo"] = [score.get(("cargo", t)) for t in tables["silver/people"].title_en]
        topics = self._topics(tables["silver/nlp_topics"])
        topics["sesgo"] = [score.get(("tema", t)) for t in topics.clave]
        nodes = pd.concat([participants, topics], ignore_index=True)
        edges = pd.concat([self._mentions(tables["silver/person_names"]),
                           self._turns(tables["silver/audio_turns"], tables["silver/speaker_person"]),
                           self._shared_screen(tables["silver/video_presence"]),
                           self._talks_about(tables["silver/nlp_topics"])], ignore_index=True)
        return {"graph_nodes": nodes[NODES].astype({"authority": "boolean", "sesgo": "Float64"}),   # NA: no role/score
                "graph_edges": edges[EDGES].astype({"peso": float, "peso_extra": float})}

    @staticmethod
    def _participants(people: pd.DataFrame, roles: pd.DataFrame) -> pd.DataFrame:
        """One node per participant, sized by their speech (their screen time if they never speak). Without age or
        tone: neither is shown per person (GDPR, ADR-0009)."""
        # A participant may have several speakers (diarization split): their first role, authority if any has it
        role = roles.groupby("participant_id").agg(role=("role", "first"), role_es=("role_es", "first"),
                                                   authority=("authority", "any"),
                                                   authority_source=("authority_source", "first"))
        unnamed = ["Persona " if p.startswith("p") else "Voz " for p in people.participant_id]
        label = people.name.where(people.name.notna(), [u + p[1:] for u, p in zip(unnamed, people.participant_id)])
        nodes = people.assign(node_id=people.participant_id, tipo=PARTICIPANT, label=label, clave=None,
                              size=people.speech_time_s.where(people.speech_time_s > 0, people.screen_time_s))
        return nodes.join(role, on="participant_id")

    @staticmethod
    def _topics(topics: pd.DataFrame) -> pd.DataFrame:
        """One small node per topic, sized by the participants who talk about it; labelled in Spanish."""
        t = topics.groupby("topic").agg(label=("topic_es", "first"), size=("topic", "size")).reset_index()
        return pd.DataFrame({"node_id": t.topic.map(topic_node), "tipo": TOPIC, "label": t.label, "clave": t.topic,
                             "size": t["size"].astype(float)})

    @staticmethod
    def _mentions(names: pd.DataFrame) -> pd.DataFrame:
        """A names B: how many times, and how many of them with a title. Introducing oneself is not an edge."""
        m = names[(names.source == "mencion") & names.said_by.notna() & names.participant_id.notna()]
        m = m[m.said_by != m.participant_id]
        g = (m.groupby(["said_by", "participant_id"])
             .agg(peso=("source", "size"), peso_extra=("title", lambda t: t.notna().sum())).reset_index())
        return g.rename(columns={"said_by": "source", "participant_id": "target"}).assign(tipo="menciona")

    @staticmethod
    def _turns(turns: pd.DataFrame, links: pd.DataFrame) -> pd.DataFrame:
        """B speaks right after A: how many times. Consecutive turns of the same participant are one."""
        of = participant_of(links)
        order = [of.get(int(s)) if pd.notna(s) else None for s in turns.sort_values("tiempo_i").speaker_id]
        passes = Counter((a, b) for a, b in zip(order, order[1:]) if a and b and a != b)
        return pd.DataFrame([(a, b, "turno", n, np.nan) for (a, b), n in passes.items()], columns=EDGES)

    @staticmethod
    def _shared_screen(presence: pd.DataFrame) -> pd.DataFrame:
        """A and B on screen at the same time: for how many seconds. Undirected (source < target)."""
        pairs = presence.merge(presence, how="cross", suffixes=("_a", "_b"))
        pairs = pairs[pairs.person_id_a < pairs.person_id_b]
        seconds = (np.minimum(pairs.tiempo_f_a, pairs.tiempo_f_b) - np.maximum(pairs.tiempo_i_a, pairs.tiempo_i_b))
        pairs = pairs.assign(peso=seconds.clip(lower=0))
        g = pairs[pairs.peso > 0].groupby(["person_id_a", "person_id_b"]).peso.sum().reset_index()
        return pd.DataFrame({"source": "p" + g.person_id_a.astype(int).astype(str),
                             "target": "p" + g.person_id_b.astype(int).astype(str), "tipo": "comparte_plano",
                             "peso": g.peso, "peso_extra": np.nan})

    @staticmethod
    def _talks_about(topics: pd.DataFrame) -> pd.DataFrame:
        """A participant talks about a topic. Topics shared by two participants join them."""
        g = (topics.dropna(subset=["participant_id"]).groupby(["participant_id", "topic"]).size()
             .reset_index(name="peso"))
        return pd.DataFrame({"source": g.participant_id, "target": g.topic.map(topic_node), "tipo": "habla_de",
                             "peso": g.peso, "peso_extra": np.nan})
