'''Shared pieces of the NLP tasks: the transcript the model reads and the checks on what it answers'''

import re
from abc import ABC, abstractmethod

import pandas as pd

from aiasn.core.text import normalize
from aiasn.model_adapters.llm_client import LLMClient
from aiasn.settings import NlpSettings


class NlpTask(ABC):
    table: str           # bronze table it fills
    columns: list[str]

    def __init__(self, llm: LLMClient, cfg: NlpSettings):
        self.llm, self.cfg = llm, cfg

    def extract(self, turns: pd.DataFrame) -> pd.DataFrame:
        """Rows of `table` for the turns of one video (bronze audio_turns)."""
        if turns.empty:
            return pd.DataFrame(columns=self.columns)
        return self._extract(turns)[self.columns]

    @abstractmethod
    def _extract(self, turns: pd.DataFrame) -> pd.DataFrame: ...


def guide(labels: dict[str, str]) -> str:
    """A bilingual guide for a prompt: `english (español), ...`."""
    return ", ".join(f"{en} ({es})" for en, es in labels.items())


def speaker_label(speaker: int) -> str:
    return f"Speaker_{speaker}"


def speaker_id(label: str | None, speakers: set[int]) -> int | None:
    """Speaker of a `Speaker_k` label written by the model; None if it is not one of `speakers`."""
    match = re.fullmatch(r"\s*Speaker_(\d+)\s*", label or "")
    return int(match.group(1)) if match and int(match.group(1)) in speakers else None


def transcript(turns: pd.DataFrame) -> str:
    """One line per turn: `[turn] Speaker_k: text`. Without gender, so that it cannot sway the model."""
    return "\n".join(f"[{t.turn}] {speaker_label(t.speaker)}: {t.text}" for t in turns.itertuples())


def found(fragment: str | None, text: str) -> bool:
    """Whether a fragment quoted by the model is really in the text (ignoring case, accents and punctuation)."""
    fragment = normalize(fragment or "")
    return bool(fragment) and fragment in normalize(text)
