"""Demostrador Ejecutable de Fusion Multimodal (Issue #4).

Proyecto: «Attention Is All She Needs» (AIASN)
Reto «Mujeres por la IA Abierta» (SEDIA / ComunidadIA-OS / IDEAI-UPC)

Ejecuta el cruce determinista sobre las fixtures reales de Agora y Video,
imprime el cuadro pericial de paridad y exporta los CSVs para la UI de Pilar.
"""

from pathlib import Path
import sys

# Asegurar inclusion de la raiz del proyecto en PYTHONPATH
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import pandas as pd
from aiasn.core.fusion import (
    calcular_kpis_paridad,
    cruzar_intervalos_multimodales,
    exportar_reportes_fusion,
)


def main():
    audio_path = BASE_DIR / "tests" / "fixtures" / "audio_sample_agora.csv"
    video_path = BASE_DIR / "tests" / "fixtures" / "video_sample_detections.csv"

    print("=" * 80)
    print("AIASN - DEMOSTRADOR DETERMINISTA DE FUSION MULTIMODAL (ISSUE #4)")
    print("=" * 80)
    print(f"Cargando evidencias de audio desde: {audio_path.name}")
    print(f"Cargando evidencias de video desde: {video_path.name}")

    df_audio = pd.read_csv(audio_path)
    df_video = pd.read_csv(video_path)

    # 1. Ejecutar cruce determinista
    df_eventos = cruzar_intervalos_multimodales(df_audio, df_video)

    # 2. Calcular KPIs agregados
    kpis = calcular_kpis_paridad(df_eventos)

    print("\n" + "-" * 80)
    print("TIMELINE DE SEGMENTOS CLASIFICADOS EN LOS 4 CUADRANTES (VILAPLANA DIAP. 92):")
    print("-" * 80)
    cols_mostrar = ["tiempo_i", "tiempo_f", "duracion_s", "cuadrante", "tipo_cuadrante", "genero", "rotulo_nombre"]
    print(df_eventos[cols_mostrar].to_string(index=False))

    print("\n" + "-" * 80)
    print("CUADRO DE AUDITORIA DE PARIDAD Y PERSPECTIVA DE GENERO (KPIS deterministas):")
    print("-" * 80)
    print(f"Duracion total analizada: {kpis['duracion_total_analizada_s']} s")
    print(f"Tiempo total de voz activa: {kpis['total_voz_segundos']} s")
    print(f"Tiempo total en pantalla:   {kpis['total_pantalla_segundos']} s")
    print(f"Porcentaje de voz femenina:     {kpis['pct_voz_mujer']:.1f} %")
    print(f"Porcentaje de pantalla femenina: {kpis['pct_pantalla_mujer']:.1f} %")

    print("\nDesglose por Genero:")
    for gen, datos in kpis["por_genero"].items():
        print(f"  [{gen.upper()}]: Voz={datos['tiempo_voz_s']}s | Pantalla={datos['tiempo_pantalla_s']}s | "
              f"C1={datos['c1_voz_activa_s']}s | C2={datos['c2_presencia_muda_s']}s | C3={datos['c3_voz_off_s']}s | "
              f"Ratio Voz/Pantalla={datos['ratio_voz_pantalla']}")

    print("\n" + "-" * 80)
    print("DICTAMEN ANTI-EQUALITY-WASHING:")
    print("-" * 80)
    if kpis["alerta_equality_washing"]:
        print("ALERTA ACTIVADA:")
        print(f"  {kpis['motivo_alerta']}")
    else:
        print("ESTADO: Paridad real y consistente (sin evidencia de presencia figurativa).")

    # 3. Exportar CSVs para el frontend de Pilar
    out_seg = BASE_DIR / "metricas_segmentos.csv"
    out_kpi = BASE_DIR / "metricas_agregadas.csv"
    exportar_reportes_fusion(df_eventos, kpis, str(out_seg), str(out_kpi))

    print("\nCSVs exportados con exito para la UI de Pilar:")
    print(f"  -> {out_seg.name}")
    print(f"  -> {out_kpi.name}")
    print("=" * 80)


if __name__ == "__main__":
    main()

