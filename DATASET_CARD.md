<!--
SPDX-FileCopyrightText: 2026 Equipo 1: Attention Is All She Needs (Alba Camiña García, Pilar de la Fuente Diez, Rocío Jiménez Villén)
SPDX-License-Identifier: Apache-2.0
-->

# Ficha de Conjuntos de Datos (Dataset Card)

## Proyecto: «Attention Is All She Needs» (AIASN)
**Reto «Mujeres por la IA Abierta» — Equipo 1**

Esta ficha de datos documenta los corpus y fuentes audiovisuales utilizados para la experimentación, validación y prueba del prototipo AIASN, sus licencias de origen, régimen de uso y consideraciones éticas.

---

## 1. Corpus de Validación y Prueba

| Dataset / Fuente | Proveedor / Origen | Idioma | Duración / Muestra | Propósito en AIASN |
| :--- | :--- | :---: | :---: | :--- |
| **`Àgora`** | Televisió de Catalunya (TV3) / UPC (Adrián Fonollosa) | Catalán | 37 horas (*Ground Truth* manual con 14 % habla femenina) | Validación empírica objetiva de la diarización y transcripción frente a anotaciones humanas periciales. |
| **`Canal 3/24`** | Televisió de Catalunya (TV3) / UPC | Catalán | 87 horas (noticiario continuo) | Evaluación de robustez en formatos informativos. |
| **Vídeos Divulgación CSIC / ICMAT** | Consejo Superior de Investigaciones Científicas | Español | Clips de conferencias y entrevistas científicas | Validación de visión por computador, tracking facial y OCR en entorno académico público. |
| **Podcast *«Quanta, quanta IA!»*** | IDEAI-UPC / donesCOEINF (Karina Gibert) | Catalán | Píldoras de podcast divulgativo | Prueba de reidentificación (Re-ID) multiescena y asignación de roles de moderación y experta. |

---

## 2. Régimen Legal y Amparo en Minería de Textos y Datos (TDM)

1. **Uso de Datos en Fase de Hackathon:** El procesado de estos fragmentos audiovisuales se realiza estrictamente en el marco de la investigación científica, formativa y sin fines de lucro del reto.
2. **Amparo en el Art. 67 del Real Decreto-ley 24/2021:**
   * La extracción de metadatos, transcripciones estadísticas y tiempos de pantalla constituye **minería de textos y datos (TDM)** legítima sobre contenidos a los que se tiene acceso lícito.
   * El repositorio **no redistribuye los archivos de vídeo o audio originales en bruto** (`*.mp4`, `*.wav` excluidos en `.gitignore`), sino exclusivamente el código de análisis y las tablas de resultados derivados reproducibles.
3. **Privacidad y Datos Personales (RGPD):**
   * Los vectores faciales se calculan solo en memoria y se descartan antes de escribir en el lake; no se construyen ni comercializan perfiles biométricos de las personas intervinientes.
   * El pipeline escribe ficheros temporales (fotogramas, audio y vídeo remuestreado) en `tmp/` y conserva el vídeo original en `landing/`; **en el prototipo no se borran automáticamente** (limpieza prevista, véase `ETHICS_CHECKLIST.md`, 3.5). Ambas rutas están fuera del repositorio (`data/` y `tmp/` en `.gitignore`).
   * Se guarda una estimación de edad por detección que no interviene en ninguna métrica; está prevista su eliminación (minimización de datos).
4. **Limitación técnica del MVP:** los vídeos de prueba deben ser cortos (se recomiendan clips de 2–3 min) por el tiempo de procesado; el análisis de vídeos largos queda como línea de trabajo futura.
