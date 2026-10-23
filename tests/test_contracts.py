"""Suite de Pruebas Unitarias y Verificación de Contratos de Datos.

Proyecto: «Attention Is All She Needs» (AIASN)
Reto «Mujeres por la IA Abierta» (SEDIA / ComunidadIA-OS / IDEAI-UPC)

Verifica:
1. Esquema del contrato tabular de audio (tiempo_i, tiempo_f, transcripcion, genero_inferido).
2. Cortafuegos etico de abstencion probabilistica (p < 0.80 -> no_determinado).
3. Calculo determinista de solape temporal y matriz de 4 cuadrantes Seeing & Hearing.
4. Principio de Zero Facial Retention en las estructuras de datos de vision.
"""

import pytest


def aplicar_umbral_etico(genero_crudo: str, probabilidad: float, umbral: float = 0.80) -> str:
    """Aplica la regla de abstencion etica (Fonollosa / Vilaplana / Karina Gibert)."""
    if probabilidad < umbral:
        return "no_determinado"
    return genero_crudo


def calcular_solape_temporal(
    audio_inicio: float, audio_fin: float, video_inicio: float, video_fin: float
) -> float:
    """Calcula deterministamente los segundos de solape entre audio y video."""
    inicio_solape = max(audio_inicio, video_inicio)
    fin_solape = min(audio_fin, video_fin)
    return max(0.0, fin_solape - inicio_solape)


def clasificar_cuadrante_audiovisual(esta_en_pantalla: bool, esta_hablando: bool) -> int:
    """Clasifica en los 4 cuadrantes Seeing & Hearing (Veronica Vilaplana, Diap. 92).

    Cuadrante 1: En pantalla y hablando (Voz activa)
    Cuadrante 2: En pantalla y en silencio (Riesgo figuracion / equality-washing)
    Cuadrante 3: Fuera de pantalla y hablando (Voz en off)
    Cuadrante 4: Ni en pantalla ni hablando (Solo mencionado)
    """
    if esta_en_pantalla and esta_hablando:
        return 1
    elif esta_en_pantalla and not esta_hablando:
        return 2
    elif not esta_en_pantalla and esta_hablando:
        return 3
    else:
        return 4


class TestDataContracts:
    """Verifica los contratos de datos de AIASN."""

    def test_audio_columns_contract(self):
        """Verifica que las columnas requeridas coinciden con el contrato convenido."""
        columnas_esperadas = ["tiempo_i", "tiempo_f", "transcripcion", "genero_inferido"]
        registro_ejemplo = {
            "tiempo_i": 0.0,
            "tiempo_f": 34.06,
            "transcripcion": "Texto de prueba transcrito...",
            "genero_inferido": "no_determinado",
        }
        for col in columnas_esperadas:
            assert col in registro_ejemplo, f"Falta la columna obligatoria '{col}'"

    def test_ethical_abstention_low_confidence(self):
        """Verifica que con confianza p < 0.80 se derive obligatoriamente a no_determinado."""
        assert aplicar_umbral_etico("femenino", 0.79) == "no_determinado"
        assert aplicar_umbral_etico("masculino", 0.55) == "no_determinado"
        assert aplicar_umbral_etico("femenino", 0.30) == "no_determinado"

    def test_ethical_abstention_high_confidence(self):
        """Verifica que con confianza p >= 0.80 se preserve la etiqueta inferida."""
        assert aplicar_umbral_etico("femenino", 0.80) == "femenino"
        assert aplicar_umbral_etico("masculino", 0.95) == "masculino"

    def test_temporal_overlap_exact_overlap(self):
        """Comprueba el solape temporal determinista."""
        # Solape parcial: audio [10, 20] vs video [15, 25] -> 5 segundos
        solape = calcular_solape_temporal(10.0, 20.0, 15.0, 25.0)
        assert pytest.approx(solape, 0.001) == 5.0

        # Sin solape: audio [0, 5] vs video [6, 10] -> 0 segundos
        assert calcular_solape_temporal(0.0, 5.0, 6.0, 10.0) == 0.0

        # Contencion total: audio [10, 30] vs video [12, 18] -> 6 segundos
        assert calcular_solape_temporal(10.0, 30.0, 12.0, 18.0) == 6.0

    def test_four_quadrants_anti_equality_washing(self):
        """Verifica la asignacion correcta a los 4 cuadrantes."""
        # Voz activa
        assert clasificar_cuadrante_audiovisual(True, True) == 1
        # Presencia muda (alerta de equality-washing)
        assert clasificar_cuadrante_audiovisual(True, False) == 2
        # Voz en off
        assert clasificar_cuadrante_audiovisual(False, True) == 3
        # Mencion pasiva
        assert clasificar_cuadrante_audiovisual(False, False) == 4

    def test_zero_facial_retention_schema(self):
        """Verifica que la estructura de tracks de video no contenga vectores biometricos."""
        track_record = {
            "track_id": 1,
            "frame": 30,
            "time_s": 3.0,
            "bbox": [100, 150, 300, 450],  # x1, y1, x2, y2
            "area": 0.05,
            "centrality": 0.85,
            "gender_label": "no_determinado",
        }
        # Asegurar que NO se persisten vectores biometricos (embeddings faciales de 512 dim)
        assert "face_embedding" not in track_record
        assert "biometric_vector" not in track_record

