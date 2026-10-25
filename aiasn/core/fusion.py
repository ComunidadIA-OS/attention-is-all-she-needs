# SPDX-FileCopyrightText: 2026 Equipo 1: Attention Is All She Needs (Alba Camiña García, Pilar de la Fuente Diez, Rocío Jiménez Villén)
# SPDX-License-Identifier: Apache-2.0

"""Motor Determinista de Fusion Multimodal y Calculo de Paridad.

Proyecto: «Attention Is All She Needs» (AIASN)
Reto «Mujeres por la IA Abierta» (SEDIA / ComunidadIA-OS / IDEAI-UPC)

Principios Arquitectonicos:
1. ADR-001: Separacion estricta entre extraccion probabilistica y calculo determinista.
2. ADR-004: Zero Facial Retention (coordenadas y tiempos efimeros en RAM).
3. ADR-005: Cortafuegos etico de abstencion probabilistica (p < 0.80 -> no_determinado).
4. ADR-006: Salvaguarda matematica progresiva en 3 fases para identidades no binarias y mesas LGTBIQ+.
5. ADR-010: Soberania linguistica cooficial (Art. 3 CE / Art. 157 LRJSP) y Accesibilidad Universal
   por Diseno (Art. 49 CE, CDPD ONU, Ley 15/2022 Art. 23, WCAG 2.2 AA y Lectura Facil UNE 153101 EX).
6. Seeing and Hearing (Veronica Vilaplana, Diap. 92): Matriz de 4 cuadrantes.
7. Regla anti-equality-washing determinista basada en el Ratio Voz/Pantalla.
"""

from typing import Any, Dict, List, Optional, Sequence, Tuple
import pandas as pd

LENGUAS_COOFICIALES_SOPORTADAS: Sequence[str] = ("es", "ca", "gl", "eu", "en")


def calcular_solape_temporal(
    inicio_a: float, fin_a: float, inicio_b: float, fin_b: float
) -> float:
    """Calcula deterministamente los segundos exactos de solape entre dos intervalos."""
    inicio_solape = max(float(inicio_a), float(inicio_b))
    fin_solape = min(float(fin_a), float(fin_b))
    return max(0.0, fin_solape - inicio_solape)


def clasificar_cuadrante(en_pantalla: bool, hablando: bool) -> int:
    """Clasifica un evento en los 4 cuadrantes Seeing & Hearing (Vilaplana Diap. 92).

    1: En pantalla y hablando (Voz activa / Protagonismo real)
    2: En pantalla y en silencio (Presencia muda / Riesgo equality-washing)
    3: Fuera de pantalla y hablando (Voz en off)
    4: Ni en pantalla ni hablando (Sujeto pasivo / Mencionada)
    """
    if en_pantalla and hablando:
        return 1
    elif en_pantalla and not hablando:
        return 2
    elif not en_pantalla and hablando:
        return 3
    else:
        return 4


def aplicar_umbral_etico(genero: str, probabilidad: float, umbral: float = 0.80) -> str:
    """Aplica el cortafuegos etico: deriva a 'no_determinado' si p < umbral."""
    if probabilidad is None:
        return "no_determinado"
    try:
        prob = float(probabilidad)
    except (ValueError, TypeError):
        return "no_determinado"

    if prob < umbral:
        return "no_determinado"
    return str(genero).lower()


def verificar_salvaguarda_paridad_no_binaria(
    tiempo_mujeres: float,
    tiempo_hombres: float,
    tiempo_no_binario: float = 0.0,
    suelo_femenino_min: float = 0.40,
    techo_masculino_base: float = 0.60,
    mesa_monografica_diversidad: bool = False,
) -> Dict[str, float | bool | str]:
    """
    Aplica la salvaguarda matematica en 3 fases (ADR-006 / Karina Gibert, Art. 14 CE y LO 2/2024):
    - Fase 1 (NB <= 20 %): Se descuenta del margen masculino (60 % -> 40 %) protegiendo el
      suelo femenino del 40 % hasta que mujeres y hombres quedan igualados en el 40 %.
    - Fase 2 (NB > 20 %): Una vez igualados en el 40 %, el exceso (NB - 20 %) se reparte
      simetricamente al 50/50 entre ambos sexos binarios: (1.0 - cuota_nb) / 2.
    - Fase 3 (Mesas monograficas LGTBIQ+ / Diversidad o NB > 60 %): Cuando se trata de una
      mesa monografica de diversidad o de colectivos infrarrepresentados, aprueba siempre
      que no exista sobrerrepresentacion masculina (cuota_h <= techo_masculino_ajustado).
    """
    total_determinado = tiempo_mujeres + tiempo_hombres + tiempo_no_binario
    if total_determinado <= 0:
        return {
            "cuota_femenina": 0.0,
            "cuota_masculina": 0.0,
            "cuota_no_binaria": 0.0,
            "suelo_femenino_exigido": suelo_femenino_min,
            "techo_masculino_ajustado": techo_masculino_base,
            "regimen_aplicado": "SIN_DATOS_DETERMINADOS",
            "cumple_salvaguarda_paridad": False,
        }

    cuota_m = tiempo_mujeres / total_determinado
    cuota_h = tiempo_hombres / total_determinado
    cuota_nb = tiempo_no_binario / total_determinado
    margen_igualacion = round(techo_masculino_base - suelo_femenino_min, 4)  # 0.20

    if cuota_nb <= margen_igualacion:
        # Fase 1 (0% a 20%): Se absorbe del privilegio masculino (60% -> 40%) sin tocar el 40% femenino
        suelo_femenino_ajustado = suelo_femenino_min
        techo_masculino_ajustado = max(0.0, techo_masculino_base - cuota_nb)
        regimen = "FASE_1_ABSORCION_TECHO_MASCULINO"
    else:
        # Fase 2 (> 20%): Igualados en 40%, el descuento extra se reparte al 50/50 entre ambos sexos binarios
        exceso_nb = cuota_nb - margen_igualacion
        suelo_femenino_ajustado = max(0.0, suelo_femenino_min - (exceso_nb / 2.0))
        techo_masculino_ajustado = max(0.0, suelo_femenino_min - (exceso_nb / 2.0))
        regimen = "FASE_2_REPARTO_SIMETRICO_50_50"

    if mesa_monografica_diversidad or cuota_nb > 0.60:
        regimen = "FASE_3_MESA_MONOGRAFICA_DIVERSIDAD_LGTBIQ"
        cumple_techo_masculino = cuota_h <= (techo_masculino_ajustado + 1e-6)
        cumple_suelo_femenino = (cuota_m + cuota_nb) >= (
            1.0 - techo_masculino_ajustado - 1e-6
        )
    else:
        cumple_suelo_femenino = cuota_m >= (suelo_femenino_ajustado - 1e-6)
        cumple_techo_masculino = cuota_h <= (techo_masculino_ajustado + 1e-6)

    return {
        "cuota_femenina": round(cuota_m, 4),
        "cuota_masculina": round(cuota_h, 4),
        "cuota_no_binaria": round(cuota_nb, 4),
        "suelo_femenino_exigido": round(suelo_femenino_ajustado, 4),
        "techo_masculino_ajustado": round(techo_masculino_ajustado, 4),
        "regimen_aplicado": regimen,
        "cumple_salvaguarda_paridad": bool(
            cumple_suelo_femenino and cumple_techo_masculino
        ),
    }


def generar_resumen_lectura_facil(
    pct_voz_mujer: float,
    pct_pantalla_mujer: float,
    alerta_equality_washing: bool,
    cumple_salvaguarda: bool,
) -> str:
    """
    Genera un resumen textual estructurado en Lectura Facil (UNE 153101 EX / WCAG 2.2 AA, ADR-010)
    para garantizar accesibilidad cognitiva y compatibilidad con lectores de pantalla y lineas braille.
    """
    if alerta_equality_washing:
        estado_texto = (
            "ALERTA DE PRESENCIA FIGURATIVA: Las mujeres aparecen en pantalla pero tienen muy poca voz activa."
        )
    elif cumple_salvaguarda:
        estado_texto = (
            "CUMPLE PARIDAD: La participacion de las mujeres alcanza el umbral de equilibrio."
        )
    else:
        estado_texto = (
            "INFRARREPRESENTACION: La participacion de las mujeres esta por debajo del minimo del 40%."
        )

    return (
        f"Lectura Facil (UNE 153101): {estado_texto} "
        f"Tiempo de voz de mujeres: {pct_voz_mujer:.1f}%. "
        f"Tiempo en pantalla de mujeres: {pct_pantalla_mujer:.1f}%."
    )


def cruzar_intervalos_multimodales(
    df_audio: pd.DataFrame,
    df_video: pd.DataFrame,
    min_solape_s: float = 0.5,
    umbral_etico: float = 0.80,
) -> pd.DataFrame:
    """Cruza deterministamente intervalos de audio y detecciones de video.

    Asigna cada evento a su cuadrante y calcula duraciones exactas.
    """
    registros_eventos: List[Dict[str, Any]] = []

    # Normalizar columnas de audio
    audio_records = df_audio.to_dict("records") if not df_audio.empty else []
    video_records = df_video.to_dict("records") if not df_video.empty else []

    # 1. Analizar cada intervencion de audio
    for a in audio_records:
        a_ini = float(a["tiempo_i"])
        a_fin = float(a["tiempo_f"])
        a_dur = max(0.0, a_fin - a_ini)
        a_genero = str(a.get("genero_inferido", "no_determinado")).lower()
        a_speaker = a.get("speaker_id", "hablante_anonimo")
        a_texto = a.get("transcripcion", "")

        # Buscar tracks de video que solapen con este turno de audio
        tracks_solapados: List[Tuple[Dict[str, Any], float]] = []
        for v in video_records:
            v_ini = float(v["tiempo_i"])
            v_fin = float(v["tiempo_f"])
            solape = calcular_solape_temporal(a_ini, a_fin, v_ini, v_fin)
            if solape >= min_solape_s:
                tracks_solapados.append((v, solape))

        if not tracks_solapados:
            # Cuadrante 3: Voz fuera de plano (Voz en off)
            registros_eventos.append(
                {
                    "tiempo_i": a_ini,
                    "tiempo_f": a_fin,
                    "duracion_s": round(a_dur, 2),
                    "cuadrante": 3,
                    "tipo_cuadrante": "Voz en off",
                    "genero": a_genero,
                    "hablante_id": a_speaker,
                    "track_id": None,
                    "rotulo_nombre": None,
                    "rotulo_cargo": None,
                    "area": None,
                    "centrality": None,
                    "transcripcion": a_texto,
                }
            )
        else:
            # Determinar cual de los tracks solapados es el hablante activo
            # Prioridad: coincidencia de genero y rotulo o mayor solape
            track_hablante = None
            for v, solape in tracks_solapados:
                v_gen = aplicar_umbral_etico(
                    v.get("genero_visual", "unknown"),
                    v.get("prob_genero", 1.0),
                    umbral_etico,
                )
                if v_gen == a_genero or a_genero == "no_determinado":
                    track_hablante = (v, solape)
                    break

            if track_hablante is None:
                track_hablante = tracks_solapados[0]

            # Registrar Cuadrante 1 para el hablante activo
            v_act, solape_act = track_hablante
            v_gen_act = aplicar_umbral_etico(
                v_act.get("genero_visual", "unknown"),
                v_act.get("prob_genero", 1.0),
                umbral_etico,
            )
            genero_final_c1 = v_gen_act if v_gen_act != "no_determinado" else a_genero

            registros_eventos.append(
                {
                    "tiempo_i": max(a_ini, float(v_act["tiempo_i"])),
                    "tiempo_f": min(a_fin, float(v_act["tiempo_f"])),
                    "duracion_s": round(solape_act, 2),
                    "cuadrante": 1,
                    "tipo_cuadrante": "Voz activa en pantalla",
                    "genero": genero_final_c1,
                    "hablante_id": a_speaker,
                    "track_id": v_act.get("track_id"),
                    "rotulo_nombre": v_act.get("rotulo_nombre"),
                    "rotulo_cargo": v_act.get("rotulo_cargo"),
                    "area": v_act.get("area"),
                    "centrality": v_act.get("centrality"),
                    "transcripcion": a_texto,
                }
            )

            # Si el turno de audio fue mas largo que la presencia en pantalla, el resto es Cuadrante 3
            if a_dur - solape_act >= min_solape_s:
                registros_eventos.append(
                    {
                        "tiempo_i": a_ini,
                        "tiempo_f": a_fin,
                        "duracion_s": round(a_dur - solape_act, 2),
                        "cuadrante": 3,
                        "tipo_cuadrante": "Voz en off parcial",
                        "genero": a_genero,
                        "hablante_id": a_speaker,
                        "track_id": None,
                        "rotulo_nombre": None,
                        "rotulo_cargo": None,
                        "area": None,
                        "centrality": None,
                        "transcripcion": a_texto,
                    }
                )

            # Los demas tracks en pantalla durante este turno son Cuadrante 2 (Presencia muda)
            for v_sil, solape_sil in tracks_solapados:
                if v_sil.get("track_id") != v_act.get("track_id"):
                    v_sil_gen = aplicar_umbral_etico(
                        v_sil.get("genero_visual", "unknown"),
                        v_sil.get("prob_genero", 1.0),
                        umbral_etico,
                    )
                    registros_eventos.append(
                        {
                            "tiempo_i": max(a_ini, float(v_sil["tiempo_i"])),
                            "tiempo_f": min(a_fin, float(v_sil["tiempo_f"])),
                            "duracion_s": round(solape_sil, 2),
                            "cuadrante": 2,
                            "tipo_cuadrante": "Presencia muda en pantalla",
                            "genero": v_sil_gen,
                            "hablante_id": None,
                            "track_id": v_sil.get("track_id"),
                            "rotulo_nombre": v_sil.get("rotulo_nombre"),
                            "rotulo_cargo": v_sil.get("rotulo_cargo"),
                            "area": v_sil.get("area"),
                            "centrality": v_sil.get("centrality"),
                            "transcripcion": None,
                        }
                    )

    # 2. Analizar tracks de video que no coincidieron con ningun audio (Presencia en silencio)
    for v in video_records:
        v_ini = float(v["tiempo_i"])
        v_fin = float(v["tiempo_f"])
        v_dur = max(0.0, v_fin - v_ini)
        solape_con_audio = sum(
            calcular_solape_temporal(v_ini, v_fin, float(a["tiempo_i"]), float(a["tiempo_f"]))
            for a in audio_records
        )
        silencio_puro = max(0.0, v_dur - solape_con_audio)
        if silencio_puro >= min_solape_s:
            v_gen = aplicar_umbral_etico(
                v.get("genero_visual", "unknown"),
                v.get("prob_genero", 1.0),
                umbral_etico,
            )
            registros_eventos.append(
                {
                    "tiempo_i": v_ini,
                    "tiempo_f": v_fin,
                    "duracion_s": round(silencio_puro, 2),
                    "cuadrante": 2,
                    "tipo_cuadrante": "Presencia muda en silencio",
                    "genero": v_gen,
                    "hablante_id": None,
                    "track_id": v.get("track_id"),
                    "rotulo_nombre": v.get("rotulo_nombre"),
                    "rotulo_cargo": v.get("rotulo_cargo"),
                    "area": v.get("area"),
                    "centrality": v.get("centrality"),
                    "transcripcion": None,
                }
            )

    df_resultado = pd.DataFrame(registros_eventos)
    if not df_resultado.empty:
        df_resultado = df_resultado.sort_values(by=["tiempo_i", "cuadrante"]).reset_index(drop=True)
    return df_resultado


def calcular_kpis_paridad(
    df_eventos: pd.DataFrame,
    duracion_total_s: Optional[float] = None,
    mesa_monografica_diversidad: bool = False,
) -> Dict[str, Any]:
    """Calcula deterministamente los KPIs agregados por genero y activa alertas anti-equality-washing."""
    if df_eventos.empty:
        return {"error": "DataFrame de eventos vacio"}

    if duracion_total_s is None:
        duracion_total_s = float(df_eventos["tiempo_f"].max())

    generos_validos = ["mujer", "hombre", "no_binario", "no_determinado"]
    kpis_genero: Dict[str, Dict[str, float]] = {}

    for gen in generos_validos:
        df_g = df_eventos[df_eventos["genero"] == gen]

        c1_s = float(df_g[df_g["cuadrante"] == 1]["duracion_s"].sum())
        c2_s = float(df_g[df_g["cuadrante"] == 2]["duracion_s"].sum())
        c3_s = float(df_g[df_g["cuadrante"] == 3]["duracion_s"].sum())

        tiempo_voz_total = c1_s + c3_s
        tiempo_pantalla_total = c1_s + c2_s

        ratio_vp = (
            c1_s / max(0.01, tiempo_pantalla_total) if tiempo_pantalla_total > 0 else 0.0
        )

        area_media = float(df_g["area"].dropna().mean()) if not df_g["area"].dropna().empty else 0.0
        centrality_media = (
            float(df_g["centrality"].dropna().mean())
            if not df_g["centrality"].dropna().empty
            else 0.0
        )

        kpis_genero[gen] = {
            "tiempo_voz_s": round(tiempo_voz_total, 2),
            "tiempo_pantalla_s": round(tiempo_pantalla_total, 2),
            "c1_voz_activa_s": round(c1_s, 2),
            "c2_presencia_muda_s": round(c2_s, 2),
            "c3_voz_off_s": round(c3_s, 2),
            "ratio_voz_pantalla": round(ratio_vp, 3),
            "area_media": round(area_media, 3),
            "centralidad_media": round(centrality_media, 3),
        }

    total_voz = sum(kpis_genero[g]["tiempo_voz_s"] for g in generos_validos)
    total_pantalla = sum(kpis_genero[g]["tiempo_pantalla_s"] for g in generos_validos)

    pct_voz_mujer = (
        (kpis_genero["mujer"]["tiempo_voz_s"] / total_voz * 100.0) if total_voz > 0 else 0.0
    )
    pct_pantalla_mujer = (
        (kpis_genero["mujer"]["tiempo_pantalla_s"] / total_pantalla * 100.0)
        if total_pantalla > 0
        else 0.0
    )

    # Salvaguarda matematica progresiva en 3 fases (ADR-006)
    salvaguarda_paridad = verificar_salvaguarda_paridad_no_binaria(
        tiempo_mujeres=kpis_genero["mujer"]["tiempo_voz_s"],
        tiempo_hombres=kpis_genero["hombre"]["tiempo_voz_s"],
        tiempo_no_binario=kpis_genero["no_binario"]["tiempo_voz_s"],
        mesa_monografica_diversidad=mesa_monografica_diversidad,
    )

    # Regla dura Anti-Equality-Washing:
    # Alta presencia en pantalla pero deficit severo de voz activa
    alerta_equality_washing = False
    motivo_alerta = ""
    if pct_pantalla_mujer >= 35.0 and (
        kpis_genero["mujer"]["ratio_voz_pantalla"] < 0.40 or pct_voz_mujer < 25.0
    ):
        alerta_equality_washing = True
        motivo_alerta = (
            f"Presencia figurativa detectada: Mujeres representan {pct_pantalla_mujer:.1f}% de pantalla, "
            f"pero solo {pct_voz_mujer:.1f}% de voz activa (Ratio Voz/Pantalla: {kpis_genero['mujer']['ratio_voz_pantalla']:.2f})."
        )

    resumen_lectura_facil = generar_resumen_lectura_facil(
        pct_voz_mujer=pct_voz_mujer,
        pct_pantalla_mujer=pct_pantalla_mujer,
        alerta_equality_washing=alerta_equality_washing,
        cumple_salvaguarda=bool(salvaguarda_paridad["cumple_salvaguarda_paridad"]),
    )

    return {
        "duracion_total_analizada_s": round(duracion_total_s, 2),
        "total_voz_segundos": round(total_voz, 2),
        "total_pantalla_segundos": round(total_pantalla, 2),
        "pct_voz_mujer": round(pct_voz_mujer, 2),
        "pct_pantalla_mujer": round(pct_pantalla_mujer, 2),
        "alerta_equality_washing": alerta_equality_washing,
        "motivo_alerta": motivo_alerta,
        "salvaguarda_paridad": salvaguarda_paridad,
        "resumen_lectura_facil": resumen_lectura_facil,
        "idiomas_soportados": list(LENGUAS_COOFICIALES_SOPORTADAS),
        "por_genero": kpis_genero,
    }


def exportar_reportes_fusion(
    df_eventos: pd.DataFrame,
    kpis: Dict[str, Any],
    ruta_segmentos_csv: str,
    ruta_kpis_csv: str,
) -> None:
    """Exporta los dos archivos tabulares listos para consumo en la UI de Pilar (Lovable/Streamlit)."""
    df_eventos.to_csv(ruta_segmentos_csv, index=False)

    # Convertir KPIs agregados a formato tabular plano para el dashboard
    filas_kpis = []
    for gen, datos in kpis.get("por_genero", {}).items():
        fila = {"genero": gen, **datos}
        fila["alerta_equality_washing"] = kpis.get("alerta_equality_washing", False)
        fila["motivo_alerta"] = kpis.get("motivo_alerta", "")
        filas_kpis.append(fila)

    df_kpis = pd.DataFrame(filas_kpis)
    df_kpis.to_csv(ruta_kpis_csv, index=False)
