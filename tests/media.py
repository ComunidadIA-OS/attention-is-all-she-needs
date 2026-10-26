# SPDX-FileCopyrightText: 2026 Equipo 1: Attention Is All She Needs (Alba Camiña García, Pilar de la Fuente Diez, Rocío Jiménez Villén)
# SPDX-License-Identifier: Apache-2.0
"""Sample images and drawing helpers for the model tests (need OpenCV and Ultralytics)."""

import cv2
import numpy as np
from ultralytics.utils import ASSETS

ZIDANE, BUS = ASSETS / "zidane.jpg", ASSETS / "bus.jpg"   # sample images shipped with Ultralytics: 2 and 4 people


def text_image(text: str, scale: float) -> np.ndarray:
    """Black text on a white box."""
    (w, h), base = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, scale, 2)
    image = np.full((h + base + 16, w + 16, 3), 255, np.uint8)
    cv2.putText(image, text, (8, h + 8), cv2.FONT_HERSHEY_SIMPLEX, scale, (0, 0, 0), 2)
    return image
