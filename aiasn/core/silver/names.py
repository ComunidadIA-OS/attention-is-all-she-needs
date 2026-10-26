# SPDX-FileCopyrightText: 2026 Equipo 1: Attention Is All She Needs (Alba Camiña García, Pilar de la Fuente Diez, Rocío Jiménez Villén)
# SPDX-License-Identifier: Apache-2.0

"""Names and titles of the participants: from the captions on screen and from how they are mentioned in the talk."""

from difflib import SequenceMatcher

import numpy as np
import pandas as pd

from aiasn.core.silver.identity import participant_of
from aiasn.core.text import normalize
from aiasn.core.transform import Transform

# `said_by` and `turn`: who mentions the participant, and when (mentions only)
NAMES = ["participant_id", "name", "title", "source", "tiempo_i", "seconds", "said_by", "turn"]
CAPTION, MENTION, NONE = "rotulo", "mencion", "ninguna"


def same_name(mentioned: str, captioned: str, threshold: float) -> bool:
    """Whether a name said in the talk can be the one of a caption: every word of it looks like some word of the
    caption (the transcript and the OCR misspell names differently, and people are often called by part of it)."""
    words = normalize(captioned).split()
    return bool(mentioned) and all(any(SequenceMatcher(None, w, c).ratio() >= threshold for c in words)
                                   for w in normalize(mentioned).split())


class NamesSilver(Transform):
    name, layer = "names", "silver"
    inputs = ["bronze/video_captions", "bronze/nlp_mentions", "silver/audio_turns", "silver/video_presence",
              "silver/speaker_person", "silver/people"]
    outputs = ["person_names", "people"]

    def run(self, tables: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
        captions = self._from_captions(tables["bronze/video_captions"], tables["silver/video_presence"])
        mentions = self._from_mentions(tables["bronze/nlp_mentions"], tables["silver/audio_turns"],
                                       tables["silver/speaker_person"])
        evidence = pd.concat([captions, self._to_captioned(mentions, captions)], ignore_index=True)
        return {"person_names": evidence, "people": self._name_people(tables["silver/people"], evidence)}

    def _to_captioned(self, mentions: pd.DataFrame, captions: pd.DataFrame) -> pd.DataFrame:
        """A mention whose name is the one of a single captioned person goes to that person: the caption is declared
        data and prevails over who the model thought was being mentioned."""
        captioned = captions.dropna(subset=["participant_id"])
        threshold = self.settings.silver.name_similarity
        participant = []
        for name, current in zip(mentions.name, mentions.participant_id):
            matches = set(captioned.participant_id[[isinstance(name, str) and same_name(name, c, threshold)
                                                    for c in captioned.name]])
            participant.append(matches.pop() if len(matches) == 1 else current)
        return mentions.assign(participant_id=participant)

    def _caption_spans(self, captions: pd.DataFrame) -> pd.DataFrame:
        """Time on screen of each caption: frames read by the OCR in a row with the same name. The title is the most
        complete one shown, since captions often grow line by line."""
        fps = self.settings.video.fps
        step = max(1, round(fps / self.settings.video.ocr_fps))   # frames between OCR reads
        c = captions.assign(key=captions.name.map(normalize)).sort_values(["key", "frame"])
        new = (c.key != c.key.shift()) | (c.frame - c.frame.shift() > step)
        spans = c.groupby(new.cumsum()).agg(name=("name", lambda n: n.mode()[0]), first=("frame", "min"),
                                            last=("frame", "max"),
                                            title=("title", lambda t: max(t.dropna(), key=len, default=None)))
        return spans.assign(tiempo_i=spans["first"] / fps, tiempo_f=(spans["last"] + step) / fps)

    def _from_captions(self, captions: pd.DataFrame, presence: pd.DataFrame) -> pd.DataFrame:
        """A caption belongs to the person on screen while it is shown; if several are, to the one speaking most.
        Captions that cannot be told apart are kept without participant, for human review."""
        if captions.empty:
            return pd.DataFrame(columns=NAMES)
        spans = self._caption_spans(captions).reset_index(drop=True).reset_index(names="span")
        pairs = spans.merge(presence, how="cross", suffixes=("", "_p"))
        pairs["overlap"] = (np.minimum(pairs.tiempo_f, pairs.tiempo_f_p)
                            - np.maximum(pairs.tiempo_i, pairs.tiempo_i_p)).clip(lower=0)
        pairs["speaking"] = pairs.overlap.where(pairs.hablando, 0.0)
        per_person = pairs[pairs.overlap > 0].groupby(["span", "person_id"])[["overlap", "speaking"]].sum()
        owners = {}
        for span, people in per_person.groupby(level="span"):
            people = people.droplevel("span")
            if len(people) == 1:
                owners[span] = people.index[0]
            else:
                ranked = people.speaking.sort_values(ascending=False)
                if ranked.iloc[0] > ranked.iloc[1]:
                    owners[span] = ranked.index[0]
        participant = spans.span.map({span: f"p{int(person)}" for span, person in owners.items()})
        return pd.DataFrame({"participant_id": participant, "name": spans.name, "title": spans.title,
                             "source": CAPTION, "tiempo_i": spans.tiempo_i, "seconds": spans.tiempo_f - spans.tiempo_i,
                             "said_by": None, "turn": pd.array([pd.NA] * len(spans), dtype="Int64")})

    @staticmethod
    def _from_mentions(mentions: pd.DataFrame, turns: pd.DataFrame, links: pd.DataFrame) -> pd.DataFrame:
        """How a speaker is named by the others, as participants (`participant_of`): who is mentioned and who says it.
        Mentions whose quote is not in the transcript are left out."""
        m = mentions[mentions.found & (mentions.name.notna() | mentions.title.notna())]
        of = participant_of(links)
        return pd.DataFrame({"participant_id": [of.get(int(s), f"v{int(s)}") for s in m.referred_speaker],
                             "name": m.name.values, "title": m.title.values, "source": MENTION,
                             "tiempo_i": m.turn.map(turns.set_index("turn").tiempo_i).values, "seconds": np.nan,
                             "said_by": [of.get(int(s)) if pd.notna(s) else None for s in m.speaker],
                             "turn": pd.array(m.turn.values, dtype="Int64")})

    @staticmethod
    def _name_people(people: pd.DataFrame, evidence: pd.DataFrame) -> pd.DataFrame:
        """The name and title of each participant. A caption wins over a mention (the declared data prevails): the
        name shown longest, with its most complete title; otherwise the name and the title said most often."""
        names = {}
        for participant, ev in evidence.dropna(subset=["participant_id"]).groupby("participant_id"):
            captions = ev[ev.source == CAPTION]
            if not captions.empty:
                key = captions.name.map(normalize)
                best = captions.seconds.groupby(key).sum().idxmax()
                chosen = captions[key == best]
                title = max(chosen.title.dropna(), key=len, default=None)
                names[participant] = (chosen.name.mode()[0], title, CAPTION)
            else:
                named, titled = ev.name.dropna(), ev.title.dropna()
                names[participant] = (named.mode()[0] if len(named) else None,
                                      titled.mode()[0] if len(titled) else None, MENTION)
        people = people.drop(columns=["name", "title", "name_source"], errors="ignore")
        chosen = [names.get(p, (None, None, NONE)) for p in people.participant_id]
        return people.assign(name=[c[0] for c in chosen], title=[c[1] for c in chosen],
                             name_source=[c[2] for c in chosen])
