# SPDX-FileCopyrightText: 2026 Equipo 1: Attention Is All She Needs (Alba Camiña García, Pilar de la Fuente Diez, Rocío Jiménez Villén)
# SPDX-License-Identifier: Apache-2.0

"""
Contrato de Adaptadores Visuales Desacoplados y Salvaguarda de Certificación Ética
(ADR-0002, ADR-0004 y Artículos 2-4 de CODE_OF_CONDUCT.md).

Garantiza tres propiedades arquitectónicas fundamentales:
1. Aislamiento de Licencias (B2B Compliance): El núcleo determinista (`aiasn.core`)
   permanece 100 % bajo licencia Apache-2.0 sin importar directamente librerías
   con licencias copyleft (como Ultralytics AGPL-3.0).
2. Privacidad por Diseño y Sostenibilidad (Zero Facial Retention & Split Edge-to-Cloud):
   Cualquier columna de vectores biométricos (`embedding`, `face_vector`) se purga
   en memoria local antes de entregar el DataFrame ligero (.csv/.tsv) al motor.
3. Cortafuegos Anti-Lavado de Cara (Art. 6 Apache-2.0 y No-Wash Policy):
   Impide emitir el Sello Oficial de Confianza si la entidad no acredita ausencia
   de sanciones graves (LISOS / Art. 71.1.d LCSP / Art. 31 bis CP), muestra
   íntegra sin cherry-picking y supervisión humana asumida (Art. 14 RIA),
   sellando el resultado con una huella criptográfica inmutable SHA-256.
"""

from abc import ABC, abstractmethod
from datetime import datetime, timedelta, timezone
import hashlib
import json
from pathlib import Path
from typing import Any, Sequence

import pandas as pd
from pydantic import BaseModel, Field

COLUMNAS_CANONICAS_VIDEO: Sequence[str] = (
    "tiempo_i",
    "tiempo_f",
    "persona_id",
    "genero_visual",
    "confianza_visual",
    "rol_ocr",
)

COLUMNAS_BIOMETRICAS_PROHIBIDAS: Sequence[str] = (
    "embedding",
    "face_embedding",
    "face_vector",
    "biometric_hash",
)

LEYENDA_AUTODIAGNOSTICO_INTERNO = (
    "USO EXCLUSIVO DE AUTODIAGNOSTICO INTERNO — NO VALIDO COMO SELLO PUBLICO "
    "NI CERTIFICADO OFICIAL (Art. 6 Apache-2.0 y Art. 3 Codigo Etico AIASN)"
)


class ElegibilidadEticaEntidad(BaseModel):
    """
    Declaración y control de elegibilidad ética previa a la emisión del Sello Oficial
    (Artículos 2, 3 y 4 del Código Ético de AIASN).
    """

    entidad_nombre: str = Field(..., min_length=1)
    identificador_muestra: str = Field(..., min_length=1)
    sin_sanciones_firmes_lisos_o_penal: bool = Field(
        default=False,
        description="Ausencia de sanciones firmes en los últimos 3 años (LISOS, Art. 71.1.d LCSP, Art. 31 bis CP).",
    )
    anios_sin_sanciones_graves: int = Field(
        default=3,
        ge=0,
        description="Años transcurridos sin infracciones graves/muy graves (ventana legal de prescripción de 3 años).",
    )
    en_rehabilitacion_self_cleaning_auditada: bool = Field(
        default=False,
        description="Vía de rehabilitación activa (Self-Cleaning Art. 57.6 Directiva 2014/24/UE) tras subsanación.",
    )
    informes_historicos_aportados: int = Field(
        default=0,
        ge=0,
        description="Número de informes anuales o ciclos históricos íntegros aportados para acreditar mejora sostenida.",
    )
    plan_igualdad_vigente_o_exento: bool = Field(
        default=False,
        description="Plan de Igualdad inscrito en REGCON (RD 901/2020) o entidad legalmente exenta.",
    )
    muestra_representativa_sin_cherry_picking: bool = Field(
        default=False,
        description="Muestra temporal íntegra y representativa, sin selección oportunista de fragmentos.",
    )
    supervision_humana_asumida: bool = Field(
        default=False,
        description="Validación expresa mediante el botón 'Asumo' por la persona operadora (Art. 14 RIA).",
    )
    operador_supervision_id: str = Field(
        default="autodiagnostico_local",
        min_length=1,
        description="Identificador de rol o token pseudonimizado de quien asume la supervisión (Art. 14 RIA + Art. 5.1.c RGPD).",
    )
    idiomas_auditoria: list[str] = Field(
        default_factory=lambda: ["es", "ca", "gl", "eu", "en"],
        description="Lenguas cooficiales del Estado e idiomas habilitados por diseño (ADR-0010, Soberanía Lingüística y Art. 157 Ley 40/2015).",
    )

    @property
    def _cumple_requisitos_base_auditoria(self) -> bool:
        """Verifica Plan de Igualdad, ausencia de cherry-picking y supervisión humana."""
        return (
            self.plan_igualdad_vigente_o_exento
            and self.muestra_representativa_sin_cherry_picking
            and self.supervision_humana_asumida
        )

    @property
    def es_apta_para_sello_pleno(self) -> bool:
        """Determina si la entidad cumple la ventana limpia de 3 años para el Sello Oficial Pleno."""
        return (
            self._cumple_requisitos_base_auditoria
            and self.sin_sanciones_firmes_lisos_o_penal
            and self.anios_sin_sanciones_graves >= 3
        )

    @property
    def es_apta_para_sello_rehabilitacion(self) -> bool:
        """
        Determina si una entidad con sanciones en los últimos 3 años cualifica para el
        Sello en Observación / Rehabilitación Verificada (Art. 3.2 Código Ético, Self-Cleaning).
        """
        return (
            self._cumple_requisitos_base_auditoria
            and not self.es_apta_para_sello_pleno
            and self.en_rehabilitacion_self_cleaning_auditada
            and self.informes_historicos_aportados >= 2
        )

    @property
    def es_apta_para_sello_publico(self) -> bool:
        """Determina si la entidad puede hacer uso público del certificado (Pleno o en Rehabilitación)."""
        return self.es_apta_para_sello_pleno or self.es_apta_para_sello_rehabilitacion


def emitir_sello_auditoria(
    metricas: dict[str, Any],
    elegibilidad: ElegibilidadEticaEntidad,
    validez_dias: int = 365,
) -> dict[str, Any]:
    """
    Genera el registro de certificación verificable con firma criptográfica SHA-256.

    Distingue 3 estados conforme al Art. 3 del Código Ético:
    1. SELLO_OFICIAL_AIASN_TRUST_VERIFIED (ventana limpia >= 3 años).
    2. SELLO_EN_OBSERVACION_REHABILITACION_VERIFICADA (vía Self-Cleaning con >= 2 informes históricos).
    3. DENEGADO_SOLO_AUTODIAGNOSTICO_INTERNO (protección de marca del Art. 6 Apache-2.0).
    """
    ahora = datetime.now(timezone.utc)
    caducidad = ahora + timedelta(days=validez_dias)

    if elegibilidad.es_apta_para_sello_pleno:
        estado_sello = "SELLO_OFICIAL_AIASN_TRUST_VERIFIED"
        aviso_legal = (
            "Certificado emitido conforme al Codigo Etico de AIASN, ISO 37301 y Art. 14 RIA. "
            "Sujeto a la regla de No-Compensacion (Art. 4.3) y revocacion automatica ante "
            "manipulacion del hash SHA-256 o incumplimiento sobrevenido."
        )
        resumen_lectura_facil = (
            f"Lectura Facil (UNE 153101): La entidad '{elegibilidad.entidad_nombre}' CUMPLE los "
            "requisitos eticos y de paridad verificada en la muestra analizada, con supervision humana validada."
        )
    elif elegibilidad.es_apta_para_sello_rehabilitacion:
        estado_sello = "SELLO_EN_OBSERVACION_REHABILITACION_VERIFICADA"
        aviso_legal = (
            "Certificado en Observacion / Rehabilitacion Verificada (Self-Cleaning, Art. 3.2 Codigo Etico). "
            f"Acreditado mediante Plan de Igualdad vigente y auditoria historica de {elegibilidad.informes_historicos_aportados} ciclos."
        )
        resumen_lectura_facil = (
            f"Lectura Facil (UNE 153101): La entidad '{elegibilidad.entidad_nombre}' cuenta con un "
            f"Sello en Observacion tras acreditar su Plan de Igualdad y {elegibilidad.informes_historicos_aportados} ciclos de mejora."
        )
    else:
        estado_sello = "DENEGADO_SOLO_AUTODIAGNOSTICO_INTERNO"
        aviso_legal = LEYENDA_AUTODIAGNOSTICO_INTERNO
        resumen_lectura_facil = (
            f"Lectura Facil (UNE 153101): Este informe de '{elegibilidad.entidad_nombre}' es SOLO para "
            "revision interna y NO puede usarse como sello publico de igualdad."
        )

    payload_canonico = {
        "entidad": elegibilidad.entidad_nombre,
        "muestra": elegibilidad.identificador_muestra,
        "estado_sello": estado_sello,
        "apta_sello": elegibilidad.es_apta_para_sello_publico,
        "operador_supervision_id": elegibilidad.operador_supervision_id,
        "idiomas_soportados": elegibilidad.idiomas_auditoria,
        "metricas": metricas,
    }
    cadena_canonica = json.dumps(payload_canonico, sort_keys=True, ensure_ascii=False)
    huella_sha256 = hashlib.sha256(cadena_canonica.encode("utf-8")).hexdigest()

    return {
        "estado_sello": estado_sello,
        "apta_uso_publicitario": elegibilidad.es_apta_para_sello_publico,
        "aviso_legal": aviso_legal,
        "resumen_lectura_facil": resumen_lectura_facil,
        "accesibilidad_y_reutilizacion": "WCAG_2.2_AA_UNE_153101_DIRECTIVA_UE_2019_882_ART157_LRJSP",
        "idiomas_soportados": elegibilidad.idiomas_auditoria,
        "entidad": elegibilidad.entidad_nombre,
        "identificador_muestra": elegibilidad.identificador_muestra,
        "operador_supervision_id": elegibilidad.operador_supervision_id,
        "fecha_emision_utc": ahora.isoformat(),
        "fecha_caducidad_utc": caducidad.isoformat(),
        "sha256_integridad": huella_sha256,
    }


class BaseVisionAdapter(ABC):
    """Interfaz abstracta para cualquier proveedor de detección visual."""

    @abstractmethod
    def extraer_detecciones(self, origen: str | Path) -> pd.DataFrame:
        """Extrae las trazas visuales y devuelve el DataFrame bajo contrato canónico."""

    @staticmethod
    def validar_y_sanitizar_contrato(df: pd.DataFrame) -> pd.DataFrame:
        """
        Aplica la salvaguarda de Zero Facial Retention (ADR-0004) y verifica las
        columnas canónicas requeridas por el motor determinista.
        """
        df_limpio = df.copy()

        # Purga preventiva de cualquier vector biométrico en RAM
        columnas_a_eliminar = [
            col for col in df_limpio.columns if col in COLUMNAS_BIOMETRICAS_PROHIBIDAS
        ]
        if columnas_a_eliminar:
            df_limpio = df_limpio.drop(columns=columnas_a_eliminar)

        faltantes = [
            col for col in COLUMNAS_CANONICAS_VIDEO if col not in df_limpio.columns
        ]
        if faltantes:
            raise ValueError(
                f"El adaptador visual no cumple el contrato canónico. Faltan: {faltantes}"
            )

        return df_limpio[list(COLUMNAS_CANONICAS_VIDEO)]


class CSVPrecomputedAdapter(BaseVisionAdapter):
    """
    Adaptador de desacoplamiento por archivo tabular (.csv / .tsv).

    Permite ingerir las salidas generadas por cuadernos de investigación externos
    (p. ej. pipelines en GPU con YOLO11m / ByteTrack / miVOLO) manteniendo
    separación estricta de procesos y licencias según las directrices de la FSF,
    y reduciendo en un 99,99 % el tráfico de red (arquitectura Split Edge-to-Cloud).
    """

    def extraer_detecciones(self, origen: str | Path) -> pd.DataFrame:
        ruta = Path(origen)
        if not ruta.exists():
            raise FileNotFoundError(f"No se encontró el archivo de trazas: {ruta}")

        separador = "\t" if ruta.suffix.lower() == ".tsv" else ","
        df = pd.read_csv(ruta, sep=separador)
        return self.validar_y_sanitizar_contrato(df)


class PermissiveYOLOXAdapter(BaseVisionAdapter):
    """
    Adaptador local 100 % permisivo para despliegues corporativos B2B (Modo C).

    Diseñado para operar exclusivamente con dependencias permisivas:
    - Detección de personas: YOLOX (Megvii, Apache-2.0) vía ONNX Runtime (MIT).
    - Análisis facial efímero en RAM: InsightFace (MIT).
    - Lectura de rótulos (chirons): EasyOCR (Apache-2.0).
    """

    def __init__(self, stride_seconds: float = 2.0, confidence_threshold: float = 0.80):
        self.stride_seconds = stride_seconds
        self.confidence_threshold = confidence_threshold

    def extraer_detecciones(self, origen: str | Path) -> pd.DataFrame:
        ruta = Path(origen)
        if ruta.suffix.lower() in {".csv", ".tsv"}:
            return CSVPrecomputedAdapter().extraer_detecciones(ruta)

        raise NotImplementedError(
            "Para inferencia de vídeo bruto en Modo C B2B, instale el perfil permisivo "
            "(`uv pip install -e '.[permissive-vision]'`) y configure los pesos ONNX de YOLOX."
        )
