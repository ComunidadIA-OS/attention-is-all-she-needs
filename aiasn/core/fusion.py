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
8. Test de Bechdel Digital / Conversacional determinista: Pluralidad femenina (>=2 mujeres),
   identidad/rotulo propio e interlocucion horizontal directa (Mujer_A -> Mujer_B).
"""

from typing import Any, Dict, List, Optional, Sequence, Tuple
import pandas as pd

LENGUAS_COOFICIALES_SOPORTADAS: Sequence[str] = ("es", "ca", "gl", "eu", "en")


# Equality-washing (spec 21 §3.1): a critical mass on screen (Kanter 1977) whose voice does not follow, by the ratio
# of shares or by a voice share as low as the media average (GMMP 2020: 19 %; Gender Gap Tracker: 21 %)
EW_PANTALLA_MIN, EW_RVP_MAX, EW_VOZ_MAX = 35.0, 0.30, 20.0
# Under-representation (spec 21 §3.2): below the legal floor on screen (LO 2/2024) and no more voice than presence
INFRA_PANTALLA_MAX, INFRA_RVP_MAX = 40.0, 1.0


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
    alerta_infrarrepresentacion: bool = False,
    pct_voz_no_determinado: float = 0.0,
) -> str:
    """
    Genera un resumen textual estructurado en Lectura Facil (UNE 153101 EX / WCAG 2.2 AA, ADR-010)
    para garantizar accesibilidad cognitiva y compatibilidad con lectores de pantalla y lineas braille.
    """
    if alerta_equality_washing:
        estado_texto = (
            "ALERTA DE PRESENCIA FIGURATIVA: Las mujeres aparecen en pantalla pero tienen muy poca voz activa."
        )
    elif alerta_infrarrepresentacion:
        estado_texto = (
            "INFRARREPRESENTACION: Las mujeres salen menos del 40% del tiempo en pantalla y no hablan mas de lo que salen."
        )
    elif cumple_salvaguarda:
        estado_texto = (
            "CUMPLE PARIDAD: La participacion de las mujeres alcanza el umbral de equilibrio."
        )
    else:
        estado_texto = (
            "PARIDAD NO ALCANZADA: El tiempo de voz de las mujeres no llega al reparto minimo del 40%."
        )
    cobertura = (
        f" En un {pct_voz_no_determinado:.0f}% del tiempo de voz no se pudo saber el genero."
        if pct_voz_no_determinado >= 0.5 else ""
    )

    return (
        f"Lectura Facil (UNE 153101): {estado_texto} "
        f"Tiempo de voz de mujeres: {pct_voz_mujer:.1f}%. "
        f"Tiempo en pantalla de mujeres: {pct_pantalla_mujer:.1f}%.{cobertura}"
    )


def evaluar_bechdel_conversacional(df_eventos: pd.DataFrame) -> Dict[str, Any]:
    """
    Test de Interlocucion Femenina (TIF), adaptacion AIASN del Test de Bechdel-Wallace (1985) a la no ficcion
    audiovisual (doc 26 §5). Mide el aislamiento relacional: mujeres presentes que solo hablan a traves de un hombre.

    Aplicabilidad, en orden (M: mujeres presentes con voz o pantalla; H: hombres presentes; V: personas con voz, de
    cualquier genero, porque que haya conversacion no depende del genero; no_determinado no cuenta en M ni en H):
    sin datos determinados, V < 2 o H = 0 -> no_evaluable; M = 0 o M = 1 -> no_supera; si no, evaluado.

    Reglas (solo si evaluado):
    1. Pluralidad femenina: al menos 2 mujeres distintas con voz activa (Cuadrantes 1 y 3).
    2. Identidad acreditada: al menos 2 mujeres con rotulo de nombre o cargo (OCR).
    3. Interlocucion horizontal: al menos una transicion directa de turno Mujer_A -> Mujer_B (A != B).
    Supera solo con 3/3.
    """
    vacio = {"mujeres_presentes": 0, "hombres_presentes": 0, "personas_con_voz": 0, "mujeres_distintas_hablando": 0,
             "mujeres_con_rotulo_identificado": 0, "transiciones_mujer_a_mujer": 0}
    if df_eventos.empty:
        return _resultado_tif("no_evaluable", "sin_datos", vacio)

    # Filtrar turnos con voz activa (Cuadrantes 1 y 3) ordenados cronologicamente
    if "cuadrante" in df_eventos.columns:
        df_voz = df_eventos[df_eventos["cuadrante"].isin([1, 3])].sort_values(by="tiempo_i")
    else:
        df_voz = df_eventos.sort_values(by="tiempo_i")

    def _id_participante(row: Any) -> str:
        for col in ("hablante_id", "rotulo_nombre", "track_id"):
            val = row.get(col)
            if pd.notna(val) and str(val).strip() not in ("", "None", "nan", "hablante_anonimo"):
                return str(val).strip()
        return f"anon_{row.get('tiempo_i', 0)}"

    df_voz_mujeres = df_voz[df_voz["genero"] == "mujer"]
    ids_mujeres_hablando = set()
    for _, row in df_voz_mujeres.iterrows():
        ids_mujeres_hablando.add(_id_participante(row))

    mujeres_distintas_hablando = len(ids_mujeres_hablando)

    # Identidad / rotulo acreditado (OCR nombre/cargo o identificador nominal)
    df_todas_mujeres = df_eventos[df_eventos["genero"] == "mujer"]
    ids_mujeres_rotuladas = set()
    for _, row in df_todas_mujeres.iterrows():
        nom = row.get("rotulo_nombre")
        car = row.get("rotulo_cargo")
        if (pd.notna(nom) and str(nom).strip() not in ("", "None", "nan")) or (
            pd.notna(car) and str(car).strip() not in ("", "None", "nan")
        ):
            # La persona en pantalla (track) primero: sus eventos C1 llevan hablante y los C2 no
            track = row.get("track_id")
            ids_mujeres_rotuladas.add(str(track) if pd.notna(track) and track else _id_participante(row))

    mujeres_con_rotulo = len(ids_mujeres_rotuladas)

    # Transiciones consecutivas de turno de voz activa Mujer_A -> Mujer_B (con A != B)
    transiciones_m_a_m = 0
    turnos_voz = df_voz.to_dict("records")
    for idx in range(len(turnos_voz) - 1):
        actual = turnos_voz[idx]
        siguiente = turnos_voz[idx + 1]
        if (
            str(actual.get("genero", "")).lower() == "mujer"
            and str(siguiente.get("genero", "")).lower() == "mujer"
        ):
            id_a = _id_participante(actual)
            id_b = _id_participante(siguiente)
            if id_a != id_b:
                transiciones_m_a_m += 1

    regla_1 = mujeres_distintas_hablando >= 2
    regla_2 = mujeres_con_rotulo >= 2
    regla_3 = transiciones_m_a_m >= 1
    puntuacion = int(regla_1) + int(regla_2) + int(regla_3)
    supera = bool(puntuacion == 3)

    # Quien es cada evento: su persona en pantalla, o su voz (enlazada a su persona si alguna vez habla en pantalla)
    pista_de_voz = {
        h: t for h, t in zip(df_eventos.get("hablante_id", pd.Series(dtype=float)), df_eventos.get("track_id", pd.Series(dtype=object)))
        if pd.notna(h) and pd.notna(t) and t
    }

    def _persona(row: Any) -> str:
        track, hablante = row.get("track_id"), row.get("hablante_id")
        if pd.notna(track) and track:
            return f"t:{track}"
        if pd.notna(hablante):
            return f"t:{pista_de_voz[hablante]}" if hablante in pista_de_voz else f"h:{hablante}"
        return _id_participante(row)

    personas = {g: {_persona(r) for r in df_eventos[df_eventos["genero"] == g].to_dict("records")}
                for g in ("mujer", "hombre", "no_binario")}
    conteos = {
        "mujeres_presentes": len(personas["mujer"]),
        "hombres_presentes": len(personas["hombre"]),
        "personas_con_voz": len({_persona(r) for r in df_voz.to_dict("records")}),
        "mujeres_distintas_hablando": mujeres_distintas_hablando,
        "mujeres_con_rotulo_identificado": mujeres_con_rotulo,
        "transiciones_mujer_a_mujer": transiciones_m_a_m,
    }
    m, h, v = conteos["mujeres_presentes"], conteos["hombres_presentes"], conteos["personas_con_voz"]
    if not any(personas.values()):
        return _resultado_tif("no_evaluable", "sin_datos", conteos)
    if v < 2:
        return _resultado_tif("no_evaluable", "sin_conversacion", conteos)
    if h == 0:
        return _resultado_tif("no_evaluable", "sin_hombres", conteos)
    if m == 0:
        return _resultado_tif("no_supera", "sin_mujeres", conteos)
    if m == 1:
        return _resultado_tif("no_supera", "una_mujer", conteos)

    regla_1 = mujeres_distintas_hablando >= 2
    regla_2 = mujeres_con_rotulo >= 2
    regla_3 = transiciones_m_a_m >= 1
    return _resultado_tif("evaluado", None, conteos, (regla_1, regla_2, regla_3))


evaluar_interlocucion_femenina = evaluar_bechdel_conversacional

MOTIVOS_TIF = {
    "sin_datos": "NO EVALUABLE: no hay tramos de genero determinado.",
    "sin_conversacion": "NO EVALUABLE: solo habla una persona; no hay conversacion.",
    "sin_hombres": "NO EVALUABLE: solo participan mujeres; el test mide la mediacion masculina.",
    "sin_mujeres": "NO SUPERA: no aparece ninguna mujer.",
    "una_mujer": "NO SUPERA: solo aparece una mujer; no puede dialogar con otra.",
}


def _resultado_tif(estado: str, motivo: Optional[str], conteos: Dict[str, int],
                   reglas: Optional[Tuple[bool, bool, bool]] = None) -> Dict[str, Any]:
    """Contrato de salida del TIF (doc 26 §5.5); las reglas y la puntuacion solo cuando se evalua."""
    if reglas is None:
        return {"estado": estado, "motivo": motivo, "aplica": False, **conteos,
                "regla_1_pluralidad_femenina": None, "regla_2_identidad_propia": None,
                "regla_3_dialogo_horizontal": None, "puntuacion_bechdel_0_3": None, "supera_bechdel_digital": False,
                "diagnostico_tif": motivo, "diagnostico_bechdel": MOTIVOS_TIF[motivo]}
    regla_1, regla_2, regla_3 = reglas
    puntuacion = int(regla_1) + int(regla_2) + int(regla_3)
    if puntuacion == 3:
        diagnostico, texto = "supera", (
            "SUPERA EL TEST DE INTERLOCUCION FEMENINA (3/3): pluralidad femenina acreditada e interlocucion "
            f"horizontal directa ({conteos['transiciones_mujer_a_mujer']} transicion(es) Mujer-Mujer sin intermediacion masculina).")
    elif not regla_1:
        diagnostico, texto = "mujer_sin_voz", (
            f"NO SUPERA ({puntuacion}/3): hay {conteos['mujeres_presentes']} mujeres presentes, pero solo "
            f"{conteos['mujeres_distintas_hablando']} con voz activa.")
    elif not regla_3:
        diagnostico, texto = "aislamiento_relacional", (
            f"NO SUPERA ({puntuacion}/3): aislamiento relacional; hablan >=2 mujeres pero todos sus turnos "
            "estan mediados por hombres.")
    else:
        diagnostico, texto = "parcial", (
            f"CUMPLIMIENTO PARCIAL ({puntuacion}/3): interlocucion directa detectada, pero falta rotulacion "
            "nominal o de cargo de al menos dos mujeres.")
    return {"estado": estado, "motivo": None, "aplica": True, **conteos,
            "regla_1_pluralidad_femenina": regla_1, "regla_2_identidad_propia": regla_2,
            "regla_3_dialogo_horizontal": regla_3, "puntuacion_bechdel_0_3": puntuacion,
            "supera_bechdel_digital": puntuacion == 3, "diagnostico_tif": diagnostico, "diagnostico_bechdel": texto}


def normalizar_tabla_audio(df_audio: pd.DataFrame, umbral_etico: float = 0.80) -> pd.DataFrame:
    """Normaliza transparentemente tanto el contrato CSV canonico como la tabla Parquet
    `bronze/audio_turns` de Rocio (`start`, `end`, `speaker`, `text`, `gender`, `gender_prob`).

    La tabla bronze se convierte con la capa silver (`aiasn.core.silver.audio`), la misma que usa el lake:
    el genero se decide por hablante (voto ponderado por duracion) con `umbral_etico`.
    """
    if df_audio.empty:
        return df_audio
    if "tiempo_i" not in df_audio.columns and "start" in df_audio.columns:
        # Import diferido: silver usa `aplicar_umbral_etico` de este modulo
        from aiasn.core.silver.audio import AudioSilver
        from aiasn.settings import Settings

        settings = Settings(silver={"gender_threshold": umbral_etico})
        return AudioSilver(settings).run({"bronze/audio_turns": df_audio})["audio_turns"]
    df = df_audio.copy()
    if "tiempo_i" not in df.columns and "start" in df.columns:
        df["tiempo_i"] = df["start"].astype(float)
    if "tiempo_f" not in df.columns and "end" in df.columns:
        df["tiempo_f"] = df["end"].astype(float)
    if "speaker_id" not in df.columns and "speaker" in df.columns:
        df["speaker_id"] = df["speaker"].apply(
            lambda x: f"spk_{int(x)}" if pd.notna(x) and str(x).strip() not in ("", "None", "<NA>") else "hablante_anonimo"
        )
    if "transcripcion" not in df.columns and "text" in df.columns:
        df["transcripcion"] = df["text"].fillna("").astype(str)
    if "genero_inferido" not in df.columns and "gender" in df.columns:
        mapa_gen = {"f": "mujer", "female": "mujer", "mujer": "mujer", "m": "hombre", "male": "hombre", "hombre": "hombre"}
        generos_norm = []
        for _, row in df.iterrows():
            raw_g = row.get("gender")
            prob_g = row.get("gender_prob", 1.0)
            if pd.isna(raw_g) or str(raw_g).strip() == "":
                generos_norm.append("no_determinado")
            else:
                g_mapped = mapa_gen.get(str(raw_g).strip().lower(), str(raw_g).strip().lower())
                if pd.notna(prob_g):
                    g_mapped = aplicar_umbral_etico(g_mapped, float(prob_g), umbral_etico)
                generos_norm.append(g_mapped)
        df["genero_inferido"] = generos_norm
    return df


def normalizar_tabla_video(
    df_video: pd.DataFrame, fps: float = 25.0, stride: int = 4
) -> pd.DataFrame:
    """Normaliza transparentemente tanto el contrato CSV canonico como la tabla Parquet
    `bronze/video_detections` de Rocio (`frame`, `shot`, `track_id`, `person_id`, `x1..y2`, `gender`, `gender_prob`).

    La tabla bronze se convierte con la capa silver (`aiasn.core.silver.video`), la misma que usa el lake: una fila
    por tramo continuo de cada persona en pantalla, con su genero por voto, area y centralidad. Si la tabla trae
    `rotulo_nombre` / `rotulo_cargo`, se conservan por persona.
    """
    if df_video.empty or "tiempo_i" in df_video.columns:
        return df_video

    # Import diferido: silver usa `aplicar_umbral_etico` de este modulo
    from aiasn.core.silver.video import VideoSilver, fusion_video
    from aiasn.settings import Settings

    df = df_video if "person_id" in df_video.columns else df_video.assign(person_id=df_video["track_id"])
    silver = VideoSilver(Settings(video={"fps": int(fps), "stride": int(stride)})).run({"bronze/video_detections": df})
    rotulos = ["rotulo_nombre", "rotulo_cargo"]
    names = df.groupby("person_id")[rotulos].first().reset_index() if set(rotulos) <= set(df.columns) else None
    return fusion_video(silver["video_people"], silver["video_presence"], names)


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

    # Normalizar transparentemente contratos CSV o tablas Parquet bronze (audio_turns / video_detections)
    df_audio_norm = normalizar_tabla_audio(df_audio, umbral_etico=umbral_etico)
    df_video_norm = normalizar_tabla_video(df_video)
    audio_records = df_audio_norm.to_dict("records") if not df_audio_norm.empty else []
    video_records = df_video_norm.to_dict("records") if not df_video_norm.empty else []

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
            if "track_id" in a:
                # Identidad resuelta en silver (voz <-> persona): el track de quien habla, o ninguno si no esta en pantalla
                track_hablante = next(((v, s) for v, s in tracks_solapados if v.get("track_id") == a["track_id"]), None)
            else:
                # Sin identidad: prioridad por coincidencia de genero o mayor solape
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

        if tracks_solapados and track_hablante is None:
            # Quien habla no esta en pantalla: Cuadrante 3; quienes se ven son Cuadrante 2 (bucle de abajo)
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
        elif tracks_solapados:
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

        if tracks_solapados:
            # Los demas tracks en pantalla durante este turno son Cuadrante 2 (Presencia muda)
            v_act = track_hablante[0] if track_hablante else {}
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

        # Share of the screen time spent speaking (C1 / screen, Vilaplana); not the RVP, which compares shares
        voz_activa_en_pantalla = (
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
            "voz_activa_en_pantalla": round(voz_activa_en_pantalla, 3),
            "area_media": round(area_media, 3),
            "centralidad_media": round(centrality_media, 3),
        }

    total_voz = sum(kpis_genero[g]["tiempo_voz_s"] for g in generos_validos)
    total_pantalla = sum(kpis_genero[g]["tiempo_pantalla_s"] for g in generos_validos)
    # Shares over the time of determined gender only (spec 21 §5.3, ADR-0005); the undetermined part is reported
    # apart, as how much of the piece could not be measured
    total_voz_det = total_voz - kpis_genero["no_determinado"]["tiempo_voz_s"]
    total_pantalla_det = total_pantalla - kpis_genero["no_determinado"]["tiempo_pantalla_s"]

    pct_voz_mujer = (
        (kpis_genero["mujer"]["tiempo_voz_s"] / total_voz_det * 100.0) if total_voz_det > 0 else 0.0
    )
    pct_pantalla_mujer = (
        (kpis_genero["mujer"]["tiempo_pantalla_s"] / total_pantalla_det * 100.0)
        if total_pantalla_det > 0
        else 0.0
    )
    # RVP (spec 21 §1.3): share of voice over share of screen of each gender; None without screen time
    for gen in ("mujer", "hombre", "no_binario"):
        g = kpis_genero[gen]
        pct_v = g["tiempo_voz_s"] / total_voz_det * 100.0 if total_voz_det > 0 else 0.0
        pct_p = g["tiempo_pantalla_s"] / total_pantalla_det * 100.0 if total_pantalla_det > 0 else 0.0
        g["ratio_voz_pantalla"] = round(pct_v / pct_p, 3) if pct_p > 0 else None
    kpis_genero["no_determinado"]["ratio_voz_pantalla"] = None
    rvp_mujer = kpis_genero["mujer"]["ratio_voz_pantalla"]

    pct_voz_no_determinado = (
        kpis_genero["no_determinado"]["tiempo_voz_s"] / total_voz * 100.0 if total_voz > 0 else 0.0
    )
    pct_pantalla_no_determinado = (
        kpis_genero["no_determinado"]["tiempo_pantalla_s"] / total_pantalla * 100.0 if total_pantalla > 0 else 0.0
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
    if pct_pantalla_mujer >= EW_PANTALLA_MIN and (
        (rvp_mujer is not None and rvp_mujer < EW_RVP_MAX) or pct_voz_mujer < EW_VOZ_MAX
    ):
        alerta_equality_washing = True
        motivo_alerta = (
            f"Presencia figurativa detectada: Mujeres representan {pct_pantalla_mujer:.1f}% de pantalla, "
            f"pero solo {pct_voz_mujer:.1f}% de voz activa (Ratio Voz/Pantalla: {rvp_mujer:.2f})."
        )

    # Without women on screen there is no RVP: that is under-representation too, if there is screen time at all
    alerta_infrarrepresentacion = bool(
        total_pantalla_det > 0
        and pct_pantalla_mujer < INFRA_PANTALLA_MAX
        and (rvp_mujer is None or rvp_mujer < INFRA_RVP_MAX)
    )
    motivo_infrarrepresentacion = (
        f"Las mujeres ocupan el {pct_pantalla_mujer:.1f}% del tiempo en pantalla, por debajo del 40%, "
        f"y su voz ({pct_voz_mujer:.1f}%) no compensa esa presencia."
        if alerta_infrarrepresentacion else ""
    )

    test_bechdel = evaluar_bechdel_conversacional(df_eventos)

    resumen_lectura_facil = generar_resumen_lectura_facil(
        pct_voz_mujer=pct_voz_mujer,
        pct_pantalla_mujer=pct_pantalla_mujer,
        alerta_equality_washing=alerta_equality_washing,
        cumple_salvaguarda=bool(salvaguarda_paridad["cumple_salvaguarda_paridad"]),
        alerta_infrarrepresentacion=alerta_infrarrepresentacion,
        pct_voz_no_determinado=pct_voz_no_determinado,
    )

    return {
        "duracion_total_analizada_s": round(duracion_total_s, 2),
        "total_voz_segundos": round(total_voz, 2),
        "total_pantalla_segundos": round(total_pantalla, 2),
        "total_voz_determinado_s": round(total_voz_det, 2),
        "total_pantalla_determinado_s": round(total_pantalla_det, 2),
        "pct_voz_mujer": round(pct_voz_mujer, 2),
        "pct_pantalla_mujer": round(pct_pantalla_mujer, 2),
        "pct_voz_no_determinado": round(pct_voz_no_determinado, 2),
        "pct_pantalla_no_determinado": round(pct_pantalla_no_determinado, 2),
        "alerta_equality_washing": alerta_equality_washing,
        "motivo_alerta": motivo_alerta,
        "alerta_infrarrepresentacion": alerta_infrarrepresentacion,
        "motivo_infrarrepresentacion": motivo_infrarrepresentacion,
        "salvaguarda_paridad": salvaguarda_paridad,
        "test_bechdel_digital": test_bechdel,
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
        fila["supera_bechdel_digital"] = kpis.get("test_bechdel_digital", {}).get("supera_bechdel_digital", False)
        fila["puntuacion_bechdel_0_3"] = kpis.get("test_bechdel_digital", {}).get("puntuacion_bechdel_0_3", 0)
        filas_kpis.append(fila)

    df_kpis = pd.DataFrame(filas_kpis)
    df_kpis.to_csv(ruta_kpis_csv, index=False)
