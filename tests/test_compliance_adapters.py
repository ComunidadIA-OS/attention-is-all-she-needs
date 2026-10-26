# SPDX-FileCopyrightText: 2026 Equipo 1: Attention Is All She Needs (Alba Camiña García, Pilar de la Fuente Diez, Rocío Jiménez Villén)
# SPDX-License-Identifier: Apache-2.0

"""
Pruebas unitarias de Adaptadores Desacoplados, Cortafuegos Anti-Lavado de Cara
(Art. 6 Apache-2.0 y CODE_OF_CONDUCT.md) y Firma Criptográfica SHA-256 (#17).
"""

import pandas as pd

from aiasn.core.compliance import (
    BaseVisionAdapter,
    ElegibilidadEticaEntidad,
    LEYENDA_AUTODIAGNOSTICO_INTERNO,
    emitir_sello_auditoria,
)


def test_purga_biometrica_en_adaptador_visual():
    """Verifica que el adaptador purgue cualquier vector biométrico (Zero Facial Retention)."""
    df_crudo = pd.DataFrame(
        {
            "tiempo_i": [0.0],
            "tiempo_f": [2.0],
            "persona_id": [1],
            "genero_visual": ["M"],
            "confianza_visual": [0.95],
            "rol_ocr": ["Catedratica"],
            "embedding": [[0.12, -0.45, 0.88]],
            "face_vector": [[0.01, 0.02]],
        }
    )
    df_limpio = BaseVisionAdapter.validar_y_sanitizar_contrato(df_crudo)
    assert "embedding" not in df_limpio.columns
    assert "face_vector" not in df_limpio.columns
    assert list(df_limpio.columns) == [
        "tiempo_i",
        "tiempo_f",
        "persona_id",
        "genero_visual",
        "confianza_visual",
        "rol_ocr",
    ]


def test_denegacion_sello_ante_sanciones_o_cherry_picking():
    """
    Verifica que una entidad con sanciones LISOS/penales o muestra sesgada no pueda
    obtener el Sello Oficial (Cláusula Anti-Lavado de Cara y Art. 6 Apache-2.0).
    """
    elegibilidad_invalida = ElegibilidadEticaEntidad(
        entidad_nombre="Corporacion Con Sancion S.A.",
        identificador_muestra="video_aislado_8m",
        sin_sanciones_firmes_lisos_o_penal=False,
        plan_igualdad_vigente_o_exento=True,
        muestra_representativa_sin_cherry_picking=False,
        supervision_humana_asumida=True,
    )
    resultado = emitir_sello_auditoria(
        metricas={"indice_paridad": 52.0}, elegibilidad=elegibilidad_invalida
    )
    assert resultado["apta_uso_publicitario"] is False
    assert resultado["estado_sello"] == "DENEGADO_SOLO_AUTODIAGNOSTICO_INTERNO"
    assert LEYENDA_AUTODIAGNOSTICO_INTERNO in resultado["aviso_legal"]


def test_emision_sello_oficial_y_firma_sha256_inmutable():
    """
    Verifica la emisión del Sello Oficial cuando se cumplen los 4 requisitos éticos
    y que cualquier manipulación posterior de las métricas invalida el hash SHA-256.
    """
    elegibilidad_valida = ElegibilidadEticaEntidad(
        entidad_nombre="Entidad Cumplidora S.L.",
        identificador_muestra="ciclo_debates_2026_q3",
        sin_sanciones_firmes_lisos_o_penal=True,
        plan_igualdad_vigente_o_exento=True,
        muestra_representativa_sin_cherry_picking=True,
        supervision_humana_asumida=True,
    )
    sello_original = emitir_sello_auditoria(
        metricas={"indice_paridad": 48.5, "alerta_equality_washing": False},
        elegibilidad=elegibilidad_valida,
    )
    assert sello_original["apta_uso_publicitario"] is True
    assert sello_original["estado_sello"] == "SELLO_OFICIAL_AIASN_TRUST_VERIFIED"
    assert len(sello_original["sha256_integridad"]) == 64

    # Si alguien intenta alterar el índice de 48.5 a 50.0, el hash SHA-256 cambia por completo
    sello_manipulado = emitir_sello_auditoria(
        metricas={"indice_paridad": 50.0, "alerta_equality_washing": False},
        elegibilidad=elegibilidad_valida,
    )
    assert sello_original["sha256_integridad"] != sello_manipulado["sha256_integridad"]


def test_rehabilitacion_corporativa_self_cleaning_ventana_3_anios():
    """
    Verifica la vía de Rehabilitación Activa (Self-Cleaning, Art. 3.2 Código Ético):
    Una entidad con sanción en los últimos 3 años que ha subsanado el daño, registrado su
    Plan de Igualdad y aportado >= 2 informes históricos recibe el Sello en Observación.
    """
    elegibilidad_rehabilitacion = ElegibilidadEticaEntidad(
        entidad_nombre="Empresa En Transformacion S.A.",
        identificador_muestra="auditoria_historica_2024_2026",
        sin_sanciones_firmes_lisos_o_penal=False,
        anios_sin_sanciones_graves=1,
        en_rehabilitacion_self_cleaning_auditada=True,
        informes_historicos_aportados=3,
        plan_igualdad_vigente_o_exento=True,
        muestra_representativa_sin_cherry_picking=True,
        supervision_humana_asumida=True,
        operador_supervision_id="ROL-COMPLIANCE-IBC-04",
    )
    resultado = emitir_sello_auditoria(
        metricas={"indice_paridad": 46.0},
        elegibilidad=elegibilidad_rehabilitacion,
    )
    assert resultado["apta_uso_publicitario"] is True
    assert (
        resultado["estado_sello"]
        == "SELLO_EN_OBSERVACION_REHABILITACION_VERIFICADA"
    )
    assert resultado["operador_supervision_id"] == "ROL-COMPLIANCE-IBC-04"
    assert "3 ciclos" in resultado["aviso_legal"]
    assert "Lectura Facil (UNE 153101)" in resultado["resumen_lectura_facil"]
    assert set(["es", "ca", "gl", "eu"]).issubset(set(resultado["idiomas_soportados"]))

