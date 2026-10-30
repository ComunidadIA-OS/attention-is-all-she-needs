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
| **Visión (Cortes de plano)** | `TransNetV2` | Souček y Lokoč | MIT | Detecta los cambios de plano. |
| **Visión (Género percibido)** | `MiVOLO v2` (`iitolstykh/mivolo_v2`) | iitolstykh (Hugging Face) | Apache-2.0 | Estimación visual de género sobre recortes faciales/corporales. El modelo también predice la edad, pero se descarta sin leerla ni guardarla. |
| **Visión (Caras y agrupación de apariciones)** | `InsightFace` (pack `buffalo_l`) | InsightFace | Código MIT; **pesos preentrenados solo para investigación no comercial** | Detección facial y *embeddings* para agrupar las apariciones de una misma persona dentro de un vídeo. Los *embeddings* no se guardan. |
| **Visión (Detección y seguimiento de personas)** | `YOLO11m-pose` + BoT-SORT | Ultralytics | **AGPL-3.0** | Detección y seguimiento de personas (`person_tracker.py`). Sustitución por un detector permisivo (p. ej. YOLOX) prevista en Fase 2, no implementada. |
| **Visión (Hablante activo)** | `TalkNet-ASD` | Tao Ruijie et al. | MIT | Identifica qué persona en pantalla está hablando. |
| **Texto (OCR)** | `EasyOCR` | JaidedAI | Apache-2.0 | Lee los textos en pantalla, una vez por segundo; el LLM decide después cuáles son rótulos de persona. |
| **Texto (Sesgo de palabras)** | `word2vec` (Google News, 300 dim.) | Google | Código Apache-2.0; los vectores preentrenados **no declaran licencia** (se descargan del original y no se redistribuyen) | Sesgo de género de cada tema y cargo, con el método de Bolukbasi et al. (2016). Solo se descargan y guardan las 500.000 palabras más frecuentes, las únicas que se leen (0,29 GB de 1,6 GB). |
| **Texto (NLP y rótulos)** | `Llama-3.3-70B-Instruct` (OVHcloud AI Endpoints) | Meta / OVHcloud | Llama 3.3 Community License (pesos abiertos, **no OSI**) | Roles, menciones, temas, ideas, tono y rótulos de persona; salida probabilística que revisa el HitL. |
| **Texto (NLP: referentes)** | `gpt-oss-120b` (OVHcloud AI Endpoints) | OpenAI / OVHcloud | Apache-2.0 | Personas conocidas citadas como referente. Distingue mejor que Llama a las figuras públicas de quienes participan, de los centros con nombre de persona y de las épocas. |
| **Texto (Tono, opcional)** | `mDeBERTa-v3-base-xnli` (zero-shot) | MoritzLaurer | MIT | Alternativa local para clasificar el tono (por defecto lo hace Llama). |

---

## 2. Separación entre Inferencia y Cálculo Determinista

Un pilar fundamental de la arquitectura de AIASN es que **los modelos de IA nunca calculan métricas finales**:
1. Los modelos actúan como **extractores y clasificadores de evidencias con marcas de tiempo**.
2. Todos los porcentajes de representación, duraciones agregadas, ratios de centralidad, índices de dominancia y alertas son calculados **al 100 % mediante algoritmos deterministas en Python** completamente auditables.
3. **Contra las alucinaciones del LLM:** cada cita que devuelve se comprueba contra la transcripción y se descarta si no aparece. Además, en los rótulos y en los referentes el modelo responde sí o no por cada elemento (si el texto presenta a una persona concreta; si es una persona real, conocida públicamente y citada como referente), y solo se quedan los que cumplen todo.

---

## 3. Salvaguarda Ética y Tratamiento de la Incertidumbre (*Human-in-the-Loop*)

Conforme a las recomendaciones de la **Dra. Karina Gibert** y la **Dra. Verónica Vilaplana**:
* **Umbral de abstención algorítmica ($p < 0.80$):** Cuando la probabilidad asignada por el clasificador de género (acústico o visual) sea inferior a 0.80, el sistema no fuerza una predicción binaria ficticia; categoriza el evento como **`no_determinado`**.
* **Índice de Cobertura Transparente:** Todo informe reporta explícitamente el porcentaje de tiempo con clasificación fiable:
  $$\text{Cobertura} = \frac{T_{\text{total}} - T_{\text{no\_determinado}}}{T_{\text{total}}} \times 100$$
* **Supervisión Humana:** Los casos dudosos o con solape de múltiples hablantes se derivan a un panel de revisión humana en el frontend piloto. En v0.1.0 el panel de revisión de personas con género dudoso y los botones «Asumo / No asumo» guardan cada decisión en la API (`POST /videos/{id}/supervision`) con su fecha, estado, motivo y huella SHA-256 de las métricas, sin recalcularlas; el informe y su bloqueo están en la hoja de ruta.

---

## 4. Limitaciones Conocidas y Sesgos

1. **Condiciones acústicas adversas:** En fragmentos con ruido de fondo extremo, solape de múltiples personas hablando simultáneamente o música de cabecera, la diarización puede fragmentar turnos o inducir bucles de repetición en ASR.
2. **Dependencia del plano de cámara:** Si las personas en pantalla no aparecen de frente o el tiro de cámara es muy lejano, la resolución de imagen puede ser insuficiente para la clasificación facial, derivando a `no_determinado`.
3. **Perspectiva de género no biológica:** Conforme al Art. 50 del RIA, las variables reportadas son estimaciones de **presentación de género percibida a partir de evidencias audiovisuales**, sin atribuir sexo biológico ni orientación identitaria privada.
4. **Estado de la validación:** la comparación sistemática con anotaciones humanas (p. ej. tasa de habla femenina del corpus `Àgora`, DER) **está pendiente**; las cifras de ahorro de cómputo y coste por hora son estimaciones hasta completar el *benchmark*.
5. **Licencias de los pesos:** Ultralytics YOLO es AGPL-3.0 y los pesos de InsightFace son de uso no comercial; un despliegue comercial requiere sustituirlos o licenciarlos (hoja de ruta, Fase 2).
6. **Datos temporales y minimización:** los fotogramas, el audio y el vídeo remuestreado pasan por `tmp/`, y el vídeo original por `landing/`. Con Docker Compose se borran al terminar cada vídeo (`PRIVACY__DELETE_MEDIA_AFTER_RUN`); sin Docker se conservan por defecto, para depurar (véase `ETHICS_CHECKLIST.md`, 3.5). La edad no se guarda.
7. **Duración de los vídeos:** el procesado de vídeos largos es lento; en este MVP se han probado clips de hasta 5 min, y los vídeos largos quedan como línea de trabajo futura.
8. **Diarización de OVHcloud:** con algunos audios devuelve un error 500 y el vídeo no se puede procesar. Cuando junta a varias personas en un solo hablante, la probabilidad de género de esa voz baja de 0,80 y queda `no_determinado`; si eso ocurre con buena parte de la voz, las alertas se calculan sobre muy poco tiempo y pueden no ser representativas.
9. **Rótulos:** el OCR puede leer mal un nombre, y el LLM a veces toma por persona un título de evento o un tratamiento («Dr.», «Dra.») por cargo; los nombres que se muestran se apoyan en lo que se ve y se oye, y conviene revisarlos.
10. **Género decidido por la cara y la voz:** hoy el género de cada participante se decide con un modelo visual y uno de voz (`fuse_gender`), lo que sitúa al sistema, cuando se usan, en la categorización biométrica del Art. 3.40 RIA y en el aviso del Art. 50(3) a cargo de quien lo despliegue. El [ADR-0013](./docs/adr/0013-atribucion-de-genero-por-evidencias-textuales.md) propone (Propuesta, sin implementar) decidirlo solo con evidencias textuales (nombre, alusiones, autorreferencia, rótulos), dejando cara y voz en un modo de investigación.
