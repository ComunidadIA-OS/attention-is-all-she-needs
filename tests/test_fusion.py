# SPDX-FileCopyrightText: 2026 Equipo 1: Attention Is All She Needs (Alba Camiña García, Pilar de la Fuente Diez, Rocío Jiménez Villén)
# SPDX-License-Identifier: Apache-2.0

"""Pruebas de Integracion y Determinismo para el Motor de Fusion Multimodal.

Verifica:
1. Calculo matematico de solape temporal sin perdida de precision.
2. Clasificacion en los 4 cuadrantes audiovisuales (Seeing and Hearing - Veronica Vilaplana Diap. 92).
3. Cruce de extremo a extremo utilizando fixtures de datos reales (Agora + Video tracks).
4. Deteccion determinista de presencia muda y alerta de equality-washing.
5. Cortafuegos etico p < 0.80 hacia 'no_determinado' (ADR-005).
6. Salvaguarda matematica progresiva en 3 fases para identidades no binarias y mesas LGTBIQ+ (ADR-006).
7. Resumen accesible en Lectura Facil (UNE 153101 EX) y Soberania Linguistica cooficial (ADR-010).
"""

from pathlib import Path
import pandas as pd
import pytest

from aiasn.core.fusion import (
    LENGUAS_COOFICIALES_SOPORTADAS,
    aplicar_umbral_etico,
    calcular_kpis_paridad,
    calcular_solape_temporal,
    clasificar_cuadrante,
    cruzar_intervalos_multimodales,
    verificar_salvaguarda_paridad_no_binaria,
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
    """Verifica la asignacion canonica a los 4 cuadrantes de Veronica Vilaplana."""
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
    assert "salvaguarda_paridad" in kpis
    assert "test_bechdel_digital" in kpis
    assert "resumen_lectura_facil" in kpis
    assert "Lectura Facil (UNE 153101)" in kpis["resumen_lectura_facil"]
    assert set(["es", "ca", "gl", "eu"]).issubset(set(kpis["idiomas_soportados"]))
    assert set(["es", "ca", "gl", "eu"]).issubset(set(LENGUAS_COOFICIALES_SOPORTADAS))

    # Verificar que los segundos son positivos y coherentes
    assert kpis["por_genero"]["hombre"]["tiempo_voz_s"] > 0
    assert kpis["por_genero"]["mujer"]["tiempo_pantalla_s"] > 0
    assert 0.0 <= kpis["por_genero"]["mujer"]["ratio_voz_pantalla"] <= 1.5


def test_salvaguarda_matematica_paridad_no_binaria_adr0006():
    """
    Verifica las 3 fases de la salvaguarda matematica ante identidades no binarias (ADR-006):
    1. Fase 1 (NB <= 20 %): Descuenta del techo masculino (60% -> 40%) sin tocar el 40% femenino.
    2. Fase 2 (NB > 20 %): Igualados en 40%, reparte el exceso al 50/50 entre mujeres y hombres.
    3. Fase 3 (Mesas monograficas LGTBIQ+ / Diversidad): Aprueba mesas de colectivos infrarrepresentados.
    """
    # Fase 1 - Caso tramposo: 60% H + 10% NB + 30% M -> RECHAZADO porque resta a las mujeres
    trampa = verificar_salvaguarda_paridad_no_binaria(
        tiempo_mujeres=30.0, tiempo_hombres=60.0, tiempo_no_binario=10.0
    )
    assert trampa["regimen_aplicado"] == "FASE_1_ABSORCION_TECHO_MASCULINO"
    assert trampa["suelo_femenino_exigido"] == 0.40
    assert trampa["techo_masculino_ajustado"] == 0.50
    assert trampa["cumple_salvaguarda_paridad"] is False

    # Fase 1 - Caso legitimo: 50% H + 10% NB + 40% M -> CUMPLE
    legitimo_f1 = verificar_salvaguarda_paridad_no_binaria(
        tiempo_mujeres=40.0, tiempo_hombres=50.0, tiempo_no_binario=10.0
    )
    assert legitimo_f1["cumple_salvaguarda_paridad"] is True

    # Fase 2 (NB = 30% -> exceso 10% sobre el 20% se reparte 5% y 5%: umbral 35% M y 35% H)
    reparto_simetrico = verificar_salvaguarda_paridad_no_binaria(
        tiempo_mujeres=35.0, tiempo_hombres=35.0, tiempo_no_binario=30.0
    )
    assert reparto_simetrico["regimen_aplicado"] == "FASE_2_REPARTO_SIMETRICO_50_50"
    assert reparto_simetrico["suelo_femenino_exigido"] == 0.35
    assert reparto_simetrico["techo_masculino_ajustado"] == 0.35
    assert reparto_simetrico["cumple_salvaguarda_paridad"] is True

    # Fase 3 (Mesa monografica LGTBIQ+ con 75% NB + 25% Mujeres + 0% Hombres -> CUMPLE)
    mesa_lgtbiq = verificar_salvaguarda_paridad_no_binaria(
        tiempo_mujeres=25.0,
        tiempo_hombres=0.0,
        tiempo_no_binario=75.0,
        mesa_monografica_diversidad=True,
    )
    assert (
        mesa_lgtbiq["regimen_aplicado"]
        == "FASE_3_MESA_MONOGRAFICA_DIVERSIDAD_LGTBIQ"
    )
    assert mesa_lgtbiq["cumple_salvaguarda_paridad"] is True


def test_bechdel_conversacional_determinista():
    """
    Verifica el Test de Bechdel Digital / Conversacional:
    1. Falla ante Efecto Token (1 sola mujer hablando) o aislamiento relacional (turnos mediados por hombre).
    2. Supera (3/3) cuando participan >=2 mujeres acreditadas con rotulo propio y dialogan directamente (Mujer_A -> Mujer_B).
    """
    from aiasn.core.fusion import evaluar_bechdel_conversacional

    # Caso 1: Aislamiento relacional (2 mujeres pero mediadas por un hombre: M1 -> H1 -> M2)
    df_mediado = pd.DataFrame(
        [
            {
                "tiempo_i": 0.0,
                "tiempo_f": 10.0,
                "duracion_s": 10.0,
                "cuadrante": 1,
                "genero": "mujer",
                "hablante_id": "spk_m1",
                "rotulo_nombre": "Dra. Elena Valls",
                "rotulo_cargo": "Catedratica IA",
            },
            {
                "tiempo_i": 10.0,
                "tiempo_f": 25.0,
                "duracion_s": 15.0,
                "cuadrante": 1,
                "genero": "hombre",
                "hablante_id": "spk_h1",
                "rotulo_nombre": "Marc Puig",
                "rotulo_cargo": "Moderador",
            },
            {
                "tiempo_i": 25.0,
                "tiempo_f": 40.0,
                "duracion_s": 15.0,
                "cuadrante": 1,
                "genero": "mujer",
                "hablante_id": "spk_m2",
                "rotulo_nombre": "Dra. Clara Roig",
                "rotulo_cargo": "Investigadora",
            },
        ]
    )
    res_mediado = evaluar_bechdel_conversacional(df_mediado)
    assert res_mediado["regla_1_pluralidad_femenina"] is True
    assert res_mediado["regla_2_identidad_propia"] is True
    assert res_mediado["regla_3_dialogo_horizontal"] is False
    assert res_mediado["transiciones_mujer_a_mujer"] == 0
    assert res_mediado["puntuacion_bechdel_0_3"] == 2
    assert res_mediado["supera_bechdel_digital"] is False

    # Caso 2: Dialogo horizontal directo Mujer_A -> Mujer_B con identidad acreditada (3/3)
    df_directo = pd.DataFrame(
        [
            {
                "tiempo_i": 0.0,
                "tiempo_f": 15.0,
                "duracion_s": 15.0,
                "cuadrante": 1,
                "genero": "mujer",
                "hablante_id": "spk_m1",
                "rotulo_nombre": "Dra. Elena Valls",
                "rotulo_cargo": "Catedratica IA",
            },
            {
                "tiempo_i": 15.0,
                "tiempo_f": 32.0,
                "duracion_s": 17.0,
                "cuadrante": 1,
                "genero": "mujer",
                "hablante_id": "spk_m2",
                "rotulo_nombre": "Dra. Clara Roig",
                "rotulo_cargo": "Investigadora",
            },
        ]
    )
    res_directo = evaluar_bechdel_conversacional(df_directo)
    assert res_directo["regla_1_pluralidad_femenina"] is True
    assert res_directo["regla_2_identidad_propia"] is True
    assert res_directo["regla_3_dialogo_horizontal"] is True
    assert res_directo["transiciones_mujer_a_mujer"] == 1
    assert res_directo["puntuacion_bechdel_0_3"] == 3
    assert res_directo["supera_bechdel_digital"] is True


def test_compatibilidad_directa_tablas_bronze_rocio():
    """Verifica que cruzar_intervalos_multimodales acepte sin cambios los DataFrames
    Parquet de la capa bronze de Rocio (`audio_turns` y `video_detections`).
    """
    df_audio_bronze = pd.DataFrame(
        [
            {"start": 0.0, "end": 4.0, "speaker": 0, "text": "Bienvenidas al debate.", "gender": "F", "gender_prob": 0.94},
            {"start": 4.0, "end": 8.0, "speaker": 1, "text": "Gracias, analizamos los datos.", "gender": "F", "gender_prob": 0.91},
        ]
    )
    # Como en un bronze real: una deteccion cada 4 fotogramas (stride) mientras cada persona esta en pantalla
    elena = {
        "shot": 0, "track_id": 1, "person_id": 10,
        "x1": 100.0, "y1": 50.0, "x2": 300.0, "y2": 300.0, "head": 1.0,
        "face_x1": 140.0, "face_y1": 60.0, "face_x2": 220.0, "face_y2": 140.0,
        "gender": "F", "gender_prob": 0.95, "age": 38.0,
        "frame_width": 640, "frame_height": 360, "speaking_score": 1.2,
        "rotulo_nombre": "Dra. Elena Puig", "rotulo_cargo": "Investigadora",
    }
    marta = {
        "shot": 1, "track_id": 2, "person_id": 20,
        "x1": 120.0, "y1": 50.0, "x2": 320.0, "y2": 300.0, "head": 1.0,
        "face_x1": 160.0, "face_y1": 60.0, "face_x2": 240.0, "face_y2": 140.0,
        "gender": "F", "gender_prob": 0.92, "age": 44.0,
        "frame_width": 640, "frame_height": 360, "speaking_score": 0.9,
        "rotulo_nombre": "Dra. Marta Soler", "rotulo_cargo": "Catedratica",
    }
    df_video_bronze = pd.DataFrame(
        [{"frame": f, **elena} for f in range(3, 100, 4)] + [{"frame": f, **marta} for f in range(103, 200, 4)]
    )
    df_ev = cruzar_intervalos_multimodales(df_audio_bronze, df_video_bronze)
    kpis = calcular_kpis_paridad(df_ev, duracion_total_s=8.0)
    assert kpis["pct_voz_mujer"] == 100.0
    assert kpis["test_bechdel_digital"]["supera_bechdel_digital"] is True
    assert kpis["test_bechdel_digital"]["transiciones_mujer_a_mujer"] == 1
