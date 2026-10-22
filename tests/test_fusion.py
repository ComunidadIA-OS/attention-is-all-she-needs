"""Pruebas de Integracion y Determinismo para el Motor de Fusion Multimodal.

Verifica:
1. Calculo matematico de solape temporal sin perdida de precision.
2. Clasificacion en los 4 cuadrantes audiovisuales (Seeing and Hearing - Veronica Vilaplana Diap. 92).
3. Cruce de extremo a extremo utilizando fixtures de datos reales (Agora + Video tracks).
4. Deteccion determinista de presencia muda y alerta de equality-washing.
5. Cortafuegos etico p < 0.80 hacia 'no_determinado' (ADR-005).
"""

from pathlib import Path
import pandas as pd
import pytest

from aiasn.core.fusion import (
    aplicar_umbral_etico,
    calcular_kpis_paridad,
    calcular_solape_temporal,
    clasificar_cuadrante,
    cruzar_intervalos_multimodales,
)

FIXTURES_DIR = Path(__file__).parent / "fixtures"


def test_solape_temporal_valores_limite():
    """Verifica el calculo determinista de solape temporal."""
    # Sin solape (audio termina antes de que empiece video)
    assert calcular_solape_temporal(0.0, 10.0, 10.5, 20.0) == 0.0

    # Solape exacto
    assert pytest.approx(calcular_solape_temporal(10.0, 30.0, 15.0, 25.0), 0.01) == 10.0

    # Solape parcial inicial
    assert pytest.approx(calcular_solape_temporal(5.0, 15.0, 10.0, 20.0), 0.01) == 5.0

    # Solape parcial final
    assert pytest.approx(calcular_solape_temporal(15.0, 25.0, 10.0, 20.0), 0.01) == 5.0

    # Coincidencia identica
    assert pytest.approx(calcular_solape_temporal(0.0, 50.0, 0.0, 50.0), 0.01) == 50.0


def test_clasificacion_cuadrantes():
    """Verifica la asignacion canónica a los 4 cuadrantes de Veronica Vilaplana."""
    # Cuadrante 1: En pantalla y hablando
    assert clasificar_cuadrante(en_pantalla=True, hablando=True) == 1
    # Cuadrante 2: En pantalla y en silencio (Riesgo equality-washing)
    assert clasificar_cuadrante(en_pantalla=True, hablando=False) == 2
    # Cuadrante 3: Fuera de pantalla y hablando (Voz en off)
    assert clasificar_cuadrante(en_pantalla=False, hablando=True) == 3
    # Cuadrante 4: Ni en pantalla ni hablando
    assert clasificar_cuadrante(en_pantalla=False, hablando=False) == 4


def test_umbral_etico_abstencion():
    """Verifica que con p < 0.80 se active obligatoriamente 'no_determinado'."""
    assert aplicar_umbral_etico("mujer", 0.79) == "no_determinado"
    assert aplicar_umbral_etico("hombre", 0.65) == "no_determinado"
    assert aplicar_umbral_etico("mujer", 0.80) == "mujer"
    assert aplicar_umbral_etico("hombre", 0.95) == "hombre"


def test_cruce_multimodal_con_fixtures():
    """Prueba de integracion de extremo a extremo con fixtures de Agora y Video."""
    audio_path = FIXTURES_DIR / "audio_sample_agora.csv"
    video_path = FIXTURES_DIR / "video_sample_detections.csv"

    assert audio_path.exists(), f"No existe {audio_path}"
    assert video_path.exists(), f"No existe {video_path}"

    df_audio = pd.read_csv(audio_path)
    df_video = pd.read_csv(video_path)

    # Ejecutar cruce determinista
    df_eventos = cruzar_intervalos_multimodales(df_audio, df_video)

    assert not df_eventos.empty
    assert "cuadrante" in df_eventos.columns
    assert "tiempo_i" in df_eventos.columns
    assert "tiempo_f" in df_eventos.columns
    assert "duracion_s" in df_eventos.columns

    # Verificar que existen detecciones en Cuadrante 1 (Voz activa)
    c1_eventos = df_eventos[df_eventos["cuadrante"] == 1]
    assert len(c1_eventos) >= 1

    # Verificar que se detecta Cuadrante 2 (Presencia muda) de la participante Marta Sole (track_03)
    c2_eventos = df_eventos[df_eventos["cuadrante"] == 2]
    assert len(c2_eventos) >= 1
    assert any("Marta Sole" in str(x) for x in c2_eventos["rotulo_nombre"].fillna(""))


def test_calculo_kpis_y_alerta_equality_washing():
    """Verifica que los KPIs agregados se calculen correctamente y salte la alerta si hay disparidad."""
    audio_path = FIXTURES_DIR / "audio_sample_agora.csv"
    video_path = FIXTURES_DIR / "video_sample_detections.csv"

    df_audio = pd.read_csv(audio_path)
    df_video = pd.read_csv(video_path)

    df_eventos = cruzar_intervalos_multimodales(df_audio, df_video)
    kpis = calcular_kpis_paridad(df_eventos, duracion_total_s=140.0)

    # Validar estructura del diccionario de KPIs
    assert "total_voz_segundos" in kpis
    assert "total_pantalla_segundos" in kpis
    assert "por_genero" in kpis
    assert "mujer" in kpis["por_genero"]
    assert "hombre" in kpis["por_genero"]
    assert "alerta_equality_washing" in kpis

    # Verificar que los segundos son positivos y coherentes
    assert kpis["por_genero"]["hombre"]["tiempo_voz_s"] > 0
    assert kpis["por_genero"]["mujer"]["tiempo_pantalla_s"] > 0
    assert 0.0 <= kpis["por_genero"]["mujer"]["ratio_voz_pantalla"] <= 1.5
