# SPDX-FileCopyrightText: 2026 Equipo 1: Attention Is All She Needs (Alba Camiña García, Pilar de la Fuente Diez, Rocío Jiménez Villén)
# SPDX-License-Identifier: Apache-2.0

"""Text comparison shared by the layers: model quotes, OCR captions and names."""

import re
import unicodedata


def normalize(text: str) -> str:
    """Lower case, without accents, punctuation or repeated spaces."""
    text = unicodedata.normalize("NFKD", text.lower()).encode("ascii", "ignore").decode()
    return " ".join(re.sub(r"[^\w\s]|_", " ", text).split())   # "_" is a word character, but OCR reads it for spaces
