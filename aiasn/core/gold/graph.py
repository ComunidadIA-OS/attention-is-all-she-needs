# SPDX-FileCopyrightText: 2026 Equipo 1: Attention Is All She Needs (Alba Camiña García, Pilar de la Fuente Diez, Rocío Jiménez Villén)
# SPDX-License-Identifier: Apache-2.0

"""The graph of a video for the front: the participants and the topics they talk about, and how they relate."""

import pandas as pd

from aiasn.core.transform import Transform

PARTICIPANT, TOPIC = "participante", "tema"
NODES = ["node_id", "tipo", "label", "clave", "size", "genero", "genero_fuente", "role", "role_es", "authority",
         "authority_source", "title", "screen_time_s", "speech_time_s", "area", "centrality"]


def topic_node(topic: str) -> str:
    return f"tema:{topic}"


class GraphGold(Transform):
    name, layer = "graph", "gold"
    inputs = ["silver/people", "silver/nlp_roles", "silver/nlp_topics"]
    outputs = ["graph_nodes"]

    def run(self, tables: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
        nodes = pd.concat([self._participants(tables["silver/people"], tables["silver/nlp_roles"]),
                           self._topics(tables["silver/nlp_topics"])], ignore_index=True)
        return {"graph_nodes": nodes[NODES].astype({"authority": "boolean"})}   # NA: not speaking, no role

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
        """One small node per topic, sized by the turns it is talked about in; labelled in Spanish."""
        t = topics.groupby("topic").agg(label=("topic_es", "first"), size=("turn", "size")).reset_index()
        return pd.DataFrame({"node_id": t.topic.map(topic_node), "tipo": TOPIC, "label": t.label, "clave": t.topic,
                             "size": t["size"].astype(float)})
