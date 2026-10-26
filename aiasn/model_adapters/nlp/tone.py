'''Task 8: discursive register of each turn (technical/assertive, collaborative, dissent), from the text only (ADR-009)'''

from typing import Literal

import pandas as pd
import torch
from pydantic import BaseModel, Field
from transformers import pipeline

from aiasn.model_adapters.llm_client import LLMClient
from aiasn.model_adapters.nlp.base import NlpTask, found, transcript
from aiasn.settings import NlpSettings

Tone = Literal["technical_assertive", "collaborative", "dissent"]


class TurnTone(BaseModel):
    turn: int = Field(description="Número del turno, como en [n]")
    tone: Tone | None = Field(description="Registro del turno; null si no aplica ninguno (saludos, agradecimientos, preguntas de trámite)")
    evidence: str | None = Field(description="Fragmento literal breve del turno que lo muestra; null si tone es null")


class Tones(BaseModel):
    turns: list[TurnTone]


PROMPT = """Analizas la transcripción automática de un vídeo (puede estar en español, catalán o inglés y tener errores).
Cada línea es un turno: [número de turno] hablante: lo que dice.
Clasifica el registro discursivo de CADA turno, juzgando solo el texto (nunca a la persona, sus emociones ni sus intenciones):
- technical_assertive: afirma hechos, aporta datos o marca una posición clara.
- collaborative: apoya, matiza o construye sobre lo que han dicho otras personas.
- dissent: rebate o cuestiona abiertamente lo que han dicho otras personas.
- null: no aplica ninguno (saludos, agradecimientos, preguntas de trámite).
Para cada turno da el tono y, como evidencia, un fragmento literal breve del turno."""


TABLE, COLUMNS = "nlp_tone", ["turn", "speaker", "tone", "score", "evidence", "found"]
DTYPES = {"turn": int, "speaker": "Int64", "score": "Float64", "found": "boolean"}

# Zero-shot: each tone as an NLI hypothesis about the last turn, in priority order. Almost every turn states
# something, so a stance towards what others said wins over stating facts.
HYPOTHESES = {
    "dissent": "está en desacuerdo con lo anterior",
    "collaborative": "está de acuerdo con lo anterior y lo amplía",
    "technical_assertive": "expone datos o hechos",
}
TEMPLATE = "Quien habla en el último turno {}."


class LlmToneClassifier(NlpTask):
    """The model reads the whole transcript; it quotes the evidence (checked in `found`) but gives no score."""
    table, columns = TABLE, COLUMNS

    def _extract(self, turns: pd.DataFrame) -> pd.DataFrame:
        """One row per turn classified by the model (tone NA when none applies); the speaker is the one of the turn."""
        answer = self.llm.complete(PROMPT, transcript(turns), Tones)
        by_turn = turns.set_index("turn")
        rows = [[t.turn, by_turn.speaker[t.turn], t.tone, None, t.evidence, found(t.evidence, by_turn.text[t.turn])]
                for t in answer.turns if t.turn in by_turn.index]
        return pd.DataFrame(rows, columns=self.columns).drop_duplicates("turn").astype(DTYPES)


class ZeroShotToneClassifier(NlpTask):
    """A local multilingual NLI model scores each tone as a hypothesis (deterministic, no remote calls).

    It reads each turn with, optionally, the previous one; it gives a score but no evidence.
    """
    table, columns = TABLE, COLUMNS

    def __init__(self, llm: LLMClient, cfg: NlpSettings):
        super().__init__(llm, cfg)
        device = 0 if cfg.device == "cuda" or (cfg.device == "auto" and torch.cuda.is_available()) else -1
        self.model = pipeline("zero-shot-classification", model=cfg.tone.zero_shot_model, device=device)

    def _extract(self, turns: pd.DataFrame) -> pd.DataFrame:
        """One row per turn: the first tone (in priority order) that reaches `min_score`, NA if none does.

        `score` is that tone's score, or the highest one when there is no tone.
        """
        texts = turns.text.tolist()
        premises = [f"Turno anterior: {texts[i - 1]}\nÚltimo turno: {text}" if i and self.cfg.tone.with_previous_turn
                    else f"Último turno: {text}" for i, text in enumerate(texts)]
        results = self.model(premises, candidate_labels=list(HYPOTHESES.values()), hypothesis_template=TEMPLATE,
                             multi_label=True)   # independent scores: a turn may fit none
        results = [results] if isinstance(results, dict) else results
        tone_of = {hypothesis: tone for tone, hypothesis in HYPOTHESES.items()}
        rows = []
        for t, r in zip(turns.itertuples(), results):
            scores = {tone_of[label]: score for label, score in zip(r["labels"], r["scores"])}
            chosen = next((tone for tone in HYPOTHESES if scores[tone] >= self.cfg.tone.min_score), None)
            rows.append([t.turn, t.speaker, chosen, scores[chosen] if chosen else max(scores.values()), None, None])
        return pd.DataFrame(rows, columns=self.columns).astype(DTYPES)


def make_tone_classifier(llm: LLMClient, cfg: NlpSettings) -> NlpTask:
    """The tone classifier chosen in the settings."""
    return {"llm": LlmToneClassifier, "zero_shot": ZeroShotToneClassifier}[cfg.tone.method](llm, cfg)
