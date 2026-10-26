# SPDX-FileCopyrightText: 2026 Equipo 1: Attention Is All She Needs (Alba Camiña García, Pilar de la Fuente Diez, Rocío Jiménez Villén)
# SPDX-License-Identifier: Apache-2.0

'''Names and titles of the people captioned on screen, from the texts read by the OCR'''

import pandas as pd
from pydantic import BaseModel, Field

from aiasn.model_adapters.llm_client import LLMClient
from aiasn.core.text import normalize
from aiasn.model_adapters.nlp.base import found

COLUMNS = ["frame", "shot", "text", "name", "title", "found"]


class Caption(BaseModel):
    block: int = Field(description="Número del bloque, como en [n]")
    name: str = Field(description="Nombre de la persona tal como aparece, corrigiendo solo errores evidentes del OCR")
    title: str | None = Field(description="Cargo, profesión o institución que acompaña al nombre; null si no hay")


class Captions(BaseModel):
    captions: list[Caption]


PROMPT = """Recibes los textos que un OCR ha leído en fotogramas de un vídeo (puede haber errores de lectura).
Cada línea es un bloque: [número de bloque] los textos de un fotograma, de arriba abajo, separados por " | ".
Indica qué bloques son el rótulo de una persona: su nombre y, si aparece, su cargo, profesión o institución.
Ignora titulares, nombres de programas o secciones, logotipos, marcas y cualquier otro texto que no presente a una persona.
Para cada rótulo devuelve: block, name (tal como aparece, corrigiendo solo errores evidentes del OCR como "_" en vez de
un espacio) y title (null si no hay)."""


class CaptionExtractor:
    def __init__(self, llm: LLMClient):
        self.llm = llm

    def extract(self, texts: pd.DataFrame) -> pd.DataFrame:
        """One row per frame showing a person's caption, from bronze video_texts.

        The texts of each frame are read together, top to bottom, since the OCR splits name and title in several
        boxes; the model only sees each distinct block once.
        """
        if texts.empty:
            return pd.DataFrame(columns=COLUMNS)
        frames = (texts.sort_values(["frame", "y1", "x1"]).groupby("frame")
                  .agg(shot=("shot", "first"), text=("text", " | ".join)).reset_index())
        frames["key"] = frames.text.map(normalize)
        blocks = frames.drop_duplicates("key").reset_index(drop=True)
        user = "\n".join(f"[{i}] {text}" for i, text in enumerate(blocks.text))
        answer = self.llm.complete(PROMPT, user, Captions)
        by_key = {blocks.key[c.block]: c for c in answer.captions if 0 <= c.block < len(blocks)}
        rows = [[f.frame, f.shot, f.text, c.name, c.title, found(c.name, f.text)]
                for f in frames.itertuples() if (c := by_key.get(f.key))]
        return pd.DataFrame(rows, columns=COLUMNS).astype({"frame": int, "found": bool})
