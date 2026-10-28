<!--
SPDX-FileCopyrightText: 2026 Equipo 1: Attention Is All She Needs (Alba Camiña García, Pilar de la Fuente Diez, Rocío Jiménez Villén)
SPDX-License-Identifier: Apache-2.0
-->

# Ficha de Modelos (Model Card)

## Proyecto: «Attention Is All She Needs» (AIASN)
**Reto «Mujeres por la IA Abierta» — Equipo 1**

Esta ficha de modelos describe los componentes de Inteligencia Artificial de código abierto utilizados en el pipeline multimodal de AIASN, sus propósitos, licencias, limitaciones conocidas y salvaguardas éticas, conforme al **estándar de IA Abierta de la OSI** y las directrices del **Reglamento Europeo de IA (RIA / REIA, Art. 50)**.

---

## 1. Catálogo de Modelos del Pipeline

| Módulo | Modelo | Creador / Proveedor | Licencia | Propósito en AIASN |
| :--- | :--- | :--- | :---: | :--- |
| **Voz (ASR + Diarización)** | `whisper-large-v3` | OpenAI / OVHcloud Kepler API | MIT / Abierta | Transcripción de habla a texto y diarización de turnos en una llamada. |
| **Voz (Atributos Acústicos)** | `prithivMLmods/Common-Voice-Gender-Detection` | Prithiv Sakthivel (HF) | Apache-2.0 | Clasificador acústico de género percibido en turnos de voz. |
| **Visión (Género y edad percibidos)** | `MiVOLO v2` (`iitolstykh/mivolo_v2`) | iitolstykh (Hugging Face) | Apache-2.0 | Estimación visual de género y edad sobre recortes faciales/corporales. La edad se almacena pero no interviene en ninguna métrica (se prevé eliminarla). |
| **Visión (Caras y agrupación de apariciones)** | `InsightFace` (pack `buffalo_l`) | InsightFace | Código MIT; **pesos preentrenados solo para investigación no comercial** | Detección facial y *embeddings* para agrupar las apariciones de una misma persona dentro de un vídeo. Los *embeddings* no se guardan. |
| **Visión (Detección y seguimiento de personas)** | `YOLO11m-pose` + BoT-SORT | Ultralytics | **AGPL-3.0** | Detección y seguimiento de personas (`person_tracker.py`). Sustitución por un detector permisivo (p. ej. YOLOX) prevista en Fase 2, no implementada. |
| **Visión (Hablante activo)** | `TalkNet-ASD` | Tao Ruijie et al. | MIT | Identifica qué persona en pantalla está hablando. |
| **Texto (OCR)** | `EasyOCR` | JaidedAI | Apache-2.0 | Extracción de nombres, cargos y títulos de rótulos televisivos. |
| **Texto (Embeddings)** | `bge-m3` | BAAI / OVHcloud | MIT | Representación vectorial densa para análisis semántico y constelación. |
| **Texto (NLP: roles, menciones, ideas)** | `Llama-3.3-70B-Instruct` (OVHcloud AI Endpoints) | Meta / OVHcloud | Llama 3.3 Community License (pesos abiertos, **no OSI**) | Extracción de roles, menciones y temas; salida probabilística que revisa el HitL. |
| **Texto (Tono)** | `mDeBERTa-v3-base-xnli` (zero-shot) | MoritzLaurer | MIT | Clasificación de tono del discurso. |

---

## 2. Separación entre Inferencia y Cálculo Determinista

Un pilar fundamental de la arquitectura de AIASN es que **los modelos de IA nunca calculan métricas finales**:
1. Los modelos actúan como **extractores y clasificadores de evidencias con marcas de tiempo**.
2. Todos los porcentajes de representación, duraciones agregadas, ratios de centralidad, índices de dominancia y alertas son calculados **al 100 % mediante algoritmos deterministas en Python** completamente auditables.

---

## 3. Salvaguarda Ética y Tratamiento de la Incertidumbre (*Human-in-the-Loop*)

Conforme a las recomendaciones de la **Dra. Karina Gibert** y la **Dra. Verónica Vilaplana**:
* **Umbral de abstención algorítmica ($p < 0.80$):** Cuando la probabilidad asignada por el clasificador de género (acústico o visual) sea inferior a 0.80, el sistema no fuerza una predicción binaria ficticia; categoriza el evento como **`no_determinado`**.
* **Índice de Cobertura Transparente:** Todo informe reporta explícitamente el porcentaje de tiempo con clasificación fiable:
  $$\text{Cobertura} = \frac{T_{\text{total}} - T_{\text{no\_determinado}}}{T_{\text{total}}} \times 100$$
* **Supervisión Humana:** Los casos dudosos o con solape de múltiples hablantes se derivan a un panel de revisión humana en el frontend piloto. En v0.1.0 las decisiones del panel no se guardan; la validación expresa («Asumo / No asumo») y su registro están en la hoja de ruta.

---

## 4. Limitaciones Conocidas y Sesgos

1. **Condiciones acústicas adversas:** En fragmentos con ruido de fondo extremo, solape de múltiples personas hablando simultáneamente o música de cabecera, la diarización puede fragmentar turnos o inducir bucles de repetición en ASR.
2. **Dependencia del plano de cámara:** Si las personas en pantalla no aparecen de frente o el tiro de cámara es muy lejano, la resolución de imagen puede ser insuficiente para la clasificación facial, derivando a `no_determinado`.
3. **Perspectiva de género no biológica:** Conforme al Art. 50 del RIA, las variables reportadas son estimaciones de **presentación de género percibida a partir de evidencias audiovisuales**, sin atribuir sexo biológico ni orientación identitaria privada.
4. **Estado de la validación:** la comparación sistemática con anotaciones humanas (p. ej. tasa de habla femenina del corpus `Àgora`, DER) **está pendiente**; las cifras de ahorro de cómputo y coste por hora son estimaciones hasta completar el *benchmark*.
5. **Licencias de los pesos:** Ultralytics YOLO es AGPL-3.0 y los pesos de InsightFace son de uso no comercial; un despliegue comercial requiere sustituirlos o licenciarlos (hoja de ruta, Fase 2).
6. **Datos temporales y minimización:** los fotogramas, el audio y el vídeo remuestreado se escriben en `tmp/`, y el vídeo original queda en `landing/`; en el prototipo no se borran automáticamente (véase `ETHICS_CHECKLIST.md`, 3.5). La edad estimada se guarda sin usarse.
7. **Duración de los vídeos:** el procesado de vídeos largos es lento; en este MVP se recomiendan clips cortos (2–3 min) y se plantea como línea de trabajo futura.
