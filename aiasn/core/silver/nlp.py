# SPDX-FileCopyrightText: 2026 Equipo 1: Attention Is All She Needs (Alba Camiña García, Pilar de la Fuente Diez, Rocío Jiménez Villén)
# SPDX-License-Identifier: Apache-2.0

"""The NLP tables by participant instead of speaker, without the quotes that are not in the transcript."""

import pandas as pd

from aiasn.core.silver.gender import from_model
from aiasn.core.silver.identity import participant_of
from aiasn.core.silver.names import same_name
from aiasn.core.transform import Transform

TABLES = {
    "nlp_topics": ["participant_id", "turn", "topic", "evidence"],
    "nlp_references": ["participant_id", "turn", "name", "genero"],   # genero: of the person cited
    "nlp_roles": ["participant_id", "role", "authority"],
    "nlp_ideas": ["idea_id", "idea", "participant_id"],
    "nlp_tone": ["participant_id", "turn", "tone", "score"],          # per turn; only aggregated in gold (ADR-0009)
}


class NlpSilver(Transform):
    name, layer = "nlp", "silver"
    inputs = [f"bronze/{t}" for t in TABLES] + ["silver/speaker_person", "silver/person_names"]
    outputs = list(TABLES)

    def run(self, tables: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
        of = participant_of(tables["silver/speaker_person"])
        bronze = {t: tables[f"bronze/{t}"] for t in TABLES}
        for t, df in bronze.items():
            participant = [of.get(int(s), f"v{int(s)}") if pd.notna(s) else None for s in df.speaker]
            bronze[t] = df.assign(participant_id=participant)
            if "found" in df:   # NA: nothing quoted to check (zero-shot tone)
                bronze[t] = bronze[t][bronze[t].found.astype("boolean").fillna(True)]
        topics, references, roles = bronze["nlp_topics"], bronze["nlp_references"], bronze["nlp_roles"]
        authority = {r.lower() for r in self.settings.silver.authority_roles}
        out = {
            "nlp_topics": topics.assign(topic=topics.topic.str.strip().str.lower()),
            "nlp_references": self._not_participants(references, tables["silver/person_names"]).assign(
                genero=lambda r: r.gender.map(from_model)),
            "nlp_roles": roles.assign(authority=roles.role.str.lower().isin(authority)),
            "nlp_ideas": bronze["nlp_ideas"], "nlp_tone": bronze["nlp_tone"],
        }
        return {t: out[t][columns].reset_index(drop=True) for t, columns in TABLES.items()}

    def _not_participants(self, references: pd.DataFrame, names: pd.DataFrame) -> pd.DataFrame:
        """References that are not someone taking part: the model sometimes cites the guest as a celebrity."""
        known = names.name.dropna().unique()
        threshold = self.settings.silver.name_similarity
        participant = [any(same_name(r, k, threshold) or same_name(k, r, threshold) for k in known)
                       for r in references.name]
        return references[~pd.Series(participant, index=references.index, dtype=bool)]
