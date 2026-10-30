# SPDX-FileCopyrightText: 2026 Equipo 1: Attention Is All She Needs (Alba Camiña García, Pilar de la Fuente Diez, Rocío Jiménez Villén)
# SPDX-License-Identifier: Apache-2.0

"""Modulo Core determinista de AIASN."""

from aiasn.core.fusion import (
    LENGUAS_COOFICIALES_SOPORTADAS,
    aplicar_umbral_etico,
    calcular_kpis_paridad,
    calcular_solape_temporal,
    clasificar_cuadrante,
    cruzar_intervalos_multimodales,
    generar_resumen_lectura_facil,
    verificar_salvaguarda_paridad_no_binaria,
)

__all__ = [
    "LENGUAS_COOFICIALES_SOPORTADAS",
    "aplicar_umbral_etico",
    "calcular_kpis_paridad",
    "calcular_solape_temporal",
    "clasificar_cuadrante",
    "cruzar_intervalos_multimodales",
    "generar_resumen_lectura_facil",
    "verificar_salvaguarda_paridad_no_binaria",
]
