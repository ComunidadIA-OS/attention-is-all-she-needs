# SPDX-FileCopyrightText: 2026 Equipo 1: Attention Is All She Needs (Alba Camiña García, Pilar de la Fuente Diez, Rocío Jiménez Villén)
# SPDX-License-Identifier: Apache-2.0

'''Names and titles of the people captioned on screen, from the texts read by the OCR'''

from concurrent.futures import ThreadPoolExecutor

import pandas as pd
from pydantic import BaseModel, Field

from aiasn.model_adapters.llm_client import LLMClient
from aiasn.core.text import normalize
from aiasn.model_adapters.nlp.base import found

COLUMNS = ["frame", "shot", "text", "name", "title", "title_en", "title_authority", "found"]


class Caption(BaseModel):
    block: int = Field(description="Número del bloque, como en [n]")
    is_person_caption: bool = Field(description="true solo si el bloque presenta a una persona concreta con su nombre "
                                                "y apellido; false en cualquier otro caso")
    name: str | None = Field(description="Nombre de la persona tal como aparece, corrigiendo solo errores evidentes "
                                         "del OCR; null si is_person_caption es false")
    title: str | None = Field(description="Cargo, profesión o institución que acompaña al nombre; null si no hay")
    title_en: str | None = Field(description="La profesión o cargo principal en inglés, en una o dos palabras en "
                                             "minúscula (researcher, professor, computer scientist...); null si no hay")
    title_authority: bool | None = Field(description="true si el cargo indica conocimiento experto o autoridad "
                                                     "profesional o institucional; false si no; null si no hay cargo")


class Captions(BaseModel):
    captions: list[Caption]


PROMPT = """Recibes los textos que un OCR ha leído en fotogramas de un vídeo (puede haber errores de lectura).
Cada línea es un bloque: [número de bloque] los textos de un fotograma, de arriba abajo, separados por " | ".
Responde a TODOS los bloques, uno por uno, diciendo si cada uno es el rótulo de una persona: su nombre y apellido y, si
aparece, su cargo, profesión o institución.
La mayoría de los bloques NO son rótulos: lo normal es responder false. No inventes ni adivines nombres; si dudas, false.
Son false: titulares, nombres de programas, eventos o secciones, logotipos, marcas, patrocinadores, carteles, fechas,
números, palabras sueltas o ilegibles, y centros, premios o calles que llevan el nombre de una persona. Ejemplos de
bloques que son false: "WIKIMANIA 15", "Ask | Google", "BRUKER", "CIB Margarita Salas", "EDICION ONLINE | TIC | MI",
"ITINERARIOS Cicerón | Biología Estructural para", "Oncinsidod".
Para cada bloque devuelve block e is_person_caption. Solo si es true, añade también: name (tal como aparece,
corrigiendo solo errores evidentes del OCR como "_" en vez de un espacio), title (null si no hay), title_en (la
profesión o cargo principal en inglés, en una o dos palabras en minúscula: "researcher", "professor",
"computer scientist"...; null si no hay cargo) y title_authority:
- true si el cargo indica conocimiento experto o autoridad profesional o institucional (catedrática, investigador,
  directora, médica, ingeniero, pedagoga, ministra, presidenta de una asociación...);
- false si no (estudiante, vecino, paciente, aficionada, familiar...);
- null si no hay cargo."""


class CaptionExtractor:
    def __init__(self, llm: LLMClient, blocks_per_call: int = 4, max_parallel: int = 6):
        self.llm, self.blocks_per_call, self.max_parallel = llm, blocks_per_call, max_parallel

    def extract(self, texts: pd.DataFrame) -> pd.DataFrame:
        """One row per frame showing a person's caption, from bronze video_texts.

        The texts of each frame are read together, top to bottom, since the OCR splits name and title in several
        boxes; the model only sees each distinct block once, in groups of `blocks_per_call` sent at the same time.
        """
        if texts.empty:
            return pd.DataFrame(columns=COLUMNS)
        frames = (texts.sort_values(["frame", "y1", "x1"]).groupby("frame")
                  .agg(shot=("shot", "first"), text=("text", " | ".join)).reset_index())
        frames["key"] = frames.text.map(normalize)
        blocks = frames.drop_duplicates("key").reset_index(drop=True)
        groups = [blocks.iloc[i:i + self.blocks_per_call] for i in range(0, len(blocks), self.blocks_per_call)]
        with ThreadPoolExecutor(min(self.max_parallel, len(groups))) as pool:
            answers = list(pool.map(self._read, groups))
        by_key = {key: c for answer in answers for key, c in answer.items()}
        rows = [[f.frame, f.shot, f.text, c.name, c.title, c.title_en, c.title_authority, found(c.name, f.text)]
                for f in frames.itertuples() if (c := by_key.get(f.key))]
        return pd.DataFrame(rows, columns=COLUMNS).astype({"frame": int, "title_authority": "boolean", "found": bool})

    def _read(self, group: pd.DataFrame) -> dict[str, Caption]:
        """The captions of one group of blocks, by block key."""
        user = "\n".join(f"[{i}] {text}" for i, text in enumerate(group.text))
        answer = self.llm.complete(PROMPT, user, Captions)
        return {group.key.iloc[c.block]: c for c in answer.captions
                if c.is_person_caption and c.name and 0 <= c.block < len(group)}
