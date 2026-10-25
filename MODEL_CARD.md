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
| **Visión (Detección / Atributos)** | `miVOLO` | MediaTek Research | Apache-2.0 / MIT | Estimación visual de género y edad sobre recortes faciales/corporales. |
| **Visión (Reidentificación)** | Embeddings Re-ID / Tracking | Basado en baseline UPC | Abierta | Mapeo de identidad temporal entre fotogramas (*tracking* multiescena). |
| **Texto (OCR)** | `EasyOCR` | JaidedAI | Apache-2.0 | Extracción de nombres, cargos y títulos de rótulos televisivos. |
| **Texto (Embeddings)** | `bge-m3` | BAAI / OVHcloud | MIT | Representación vectorial densa para análisis semántico y constelación. |

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
* **Supervisión Humana:** Los casos dudosos o con solape de múltiples hablantes se derivan a revisión humana mediante pantalla interactiva con validación expresa (**«Asumo / No asumo»**).

---

## 4. Limitaciones Conocidas y Sesgos

1. **Condiciones acústicas adversas:** En fragmentos con ruido de fondo extremo, solape de múltiples personas hablando simultáneamente o música de cabecera, la diarización puede fragmentar turnos o inducir bucles de repetición en ASR.
2. **Dependencia del plano de cámara:** Si las personas en pantalla no aparecen de frente o el tiro de cámara es muy lejano, la resolución de imagen puede ser insuficiente para la clasificación facial, derivando a `no_determinado`.
3. **Perspectiva de género no biológica:** Conforme al Art. 50 del RIA, las variables reportadas son estimaciones de **presentación de género percibida a partir de evidencias audiovisuales**, sin atribuir sexo biológico ni orientación identitaria privada.
