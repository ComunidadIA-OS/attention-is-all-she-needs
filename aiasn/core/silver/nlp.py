# SPDX-FileCopyrightText: 2026 Equipo 1: Attention Is All She Needs (Alba Camiña García, Pilar de la Fuente Diez, Rocío Jiménez Villén)
# SPDX-License-Identifier: Apache-2.0

"""The NLP tables by participant instead of speaker, without the quotes that are not in the transcript."""

import pandas as pd

from aiasn.core.silver.gender import from_model
from aiasn.core.silver.identity import participant_of
from aiasn.core.silver.names import same_name
from aiasn.core.transform import Transform

# English keys (stable, word2vec) and their Spanish labels (`_es`, for the UI)
TABLES = {
    "nlp_topics": ["participant_id", "turn", "topic", "topic_es", "evidence"],
    "nlp_references": ["participant_id", "turn", "name", "genero"],   # genero: of the person cited
    "nlp_roles": ["participant_id", "role", "role_es", "authority", "authority_source"],   # source: rol, rotulo, ambos
    "nlp_ideas": ["idea_id", "idea", "participant_id"],
    "nlp_tone": ["participant_id", "turn", "tone", "tone_es", "score"],   # per turn; only aggregated in gold (ADR-0009)
}
TONE_ES = {"technical_assertive": "técnico/asertivo", "collaborative": "colaborativo", "dissent": "disenso"}


def spanish(keys: pd.Series, guide: dict[str, str], model: pd.Series | None) -> list:
    """Spanish label of each key: the guide's when the key is in it (always the same), otherwise the model's."""
    model = model if model is not None else pd.Series([None] * len(keys), index=keys.index)
    by_key = {k.lower(): v for k, v in guide.items()}
    return [by_key.get(k, m.strip() if isinstance(m, str) else None) for k, m in zip(keys, model)]


class NlpSilver(Transform):
    name, layer = "nlp", "silver"
    inputs = [f"bronze/{t}" for t in TABLES] + ["silver/speaker_person", "silver/person_names", "silver/people"]
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
        nlp_cfg = self.settings.nlp
        topics = topics.assign(topic=topics.topic.str.strip().str.lower())
        roles = roles.assign(
            role_es=spanish(roles.role.str.strip().str.lower(), nlp_cfg.roles_guide, roles.get("role_es")))
        tone = bronze["nlp_tone"]
        out = {
            "nlp_topics": topics.assign(topic_es=spanish(topics.topic, nlp_cfg.topics_guide, topics.get("topic_es"))),
            "nlp_references": self._not_participants(references, tables["silver/person_names"]).assign(
                genero=lambda r: r.gender.map(from_model)),
            "nlp_roles": self._authority(roles, tables["silver/people"]),
            "nlp_ideas": bronze["nlp_ideas"], "nlp_tone": tone.assign(tone_es=tone.tone.map(TONE_ES)),
        }
        return {t: out[t][columns].reset_index(drop=True) for t, columns in TABLES.items()}

    def _authority(self, roles: pd.DataFrame, people: pd.DataFrame) -> pd.DataFrame:
        """Whether each participant speaks from authority: their role is one of `authority_roles`, or the title of
        their caption shows expert or institutional authority (the declared data prevails over the model's role)."""
        cfg = self.settings.silver
        by_role = roles.role.str.lower().isin({r.lower() for r in cfg.authority_roles})
        captioned = people.set_index("participant_id").title_authority.astype("boolean").fillna(False)
        by_title = roles.participant_id.map(captioned).astype("boolean").fillna(False) & cfg.caption_grants_authority
        source = [("ambos" if r and t else "rol" if r else "rotulo" if t else None) for r, t in zip(by_role, by_title)]
        return roles.assign(authority=(by_role | by_title).astype(bool), authority_source=source)

    def _not_participants(self, references: pd.DataFrame, names: pd.DataFrame) -> pd.DataFrame:
        """References that are not someone taking part: the model sometimes cites the guest as a celebrity."""
        known = names.name.dropna().unique()
        threshold = self.settings.silver.name_similarity
        participant = [any(same_name(r, k, threshold) or same_name(k, r, threshold) for k in known)
                       for r in references.name]
        return references[~pd.Series(participant, index=references.index, dtype=bool)]
