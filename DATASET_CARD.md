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
| **Vídeos Divulgación CSIC / ICMAT** | Consejo Superior de Investigaciones Científicas | Español | Clips de conferencias y entrevistas científicas | Calibración interna de visión por computador, tracking facial y OCR (descargados de YouTube; **licencia no comprobada**; ver 1.1). |
| **Podcast *«Quanta, quanta IA!»*** | IDEAI-UPC / donesCOEINF (Karina Gibert) | Catalán | Píldoras de podcast divulgativo | Calibración interna de reidentificación (Re-ID) multiescena y roles de moderación y experta. **Sin permiso expreso** de la organización (ver 1.1). |

---

### 1.1. Vídeos de prueba y de calibración (estado a 28/10/2026)

| Vídeo | Uso | Origen y licencia | ¿Se puede compartir el fichero? | Estado |
| :--- | :--- | :--- | :--- | :--- |
| `clip_1_wikimania.mp4` (3:38) | **Demostración** y prueba pública reproducible | Panel con dos mujeres y dos hombres: [*Wikipedia Five Pillars Panel*](https://commons.wikimedia.org/wiki/File:Wikimania_2015_-_Wikipedia_Five_Pillars_Panel.webm), Wikimedia México (Wikimania 2015), Wikimedia Commons, **CC BY-SA 3.0** | Sí, con atribución, indicando que está recortado, y con la misma licencia | Licencia y enlace comprobados el 28/10/2026. **Pendiente:** tramo exacto, huella SHA-256 y ejecución con resultados |
| `clip_2_wikimania.mp4` (5:12) | **Demostración** | El mismo panel, otro tramo (misma fuente y licencia) | Igual | **Pendiente:** tramo exacto, huella SHA-256 y ejecución |
| `clip_mesa_redonda.mp4` (5:11) | **Demostración** | Videollamada con dos mujeres y dos hombres: [mesa redonda FLISoL Tenerife 2021](https://archive.org/details/flisoltenerife20211mesa-redonda), FLISoL Tenerife, Internet Archive, **CC BY-SA 4.0** | Sí, con atribución, indicando que está recortado, y con la misma licencia | Licencia y enlace comprobados el 28/10/2026. **Pendiente:** tramo exacto, huella SHA-256 y ejecución. Al ser una videollamada en cuadrícula, puede dar métricas poco útiles; alternativa verificada: Wikimania 2025 (CC BY-SA 4.0) |
| `csic_javier_oroz.mp4` (1:24) | **Demostración** | [*CSIC Cicerón. Biología Estructural para acelerar el diagnóstico de ELA. Javier Oroz*](https://www.youtube.com/watch?v=V6I84IL-L0o), CSIC Comunicación (YouTube, publicado el 07/07/2025). Según el equipo, solo habla él y las investigadoras salen sin voz | **CC BY** (Creative Commons de YouTube: «reutilización permitida»). El equipo indica la versión 4.0, **no verificada en la página** | Sí, con atribución. Se usa completo y sin cambios | Duración y licencia comprobadas el 29/10/2026. **Pendiente:** huella SHA-256 y ejecución |
| Vídeos de divulgación científica descargados de YouTube por el equipo | **Calibración interna** del modelo | YouTube; licencia **no comprobada**; fuente original por localizar | **No**: sin redistribuir y fuera de la demostración y de las capturas públicas | Solo uso interno |
| *«Quanta, quanta IA!»* | **Calibración interna** | betevé / IDEAI-UPC (YouTube); **sin permiso expreso** | **No** | Solo análisis en local; el amparo de minería de datos está pendiente de validar |

Los `.mp4` **no están en Git**: se descargan de los enlaces originales (por ejemplo, con `ffmpeg -ss … -to … -i <URL> -c copy` sobre las URL de Wikimedia Commons e Internet Archive). Según el equipo, **no aparecen menores** en estos cuatro vídeos (no verificado de forma independiente), y las personas intervienen en público y en actos grabados para difundirse. Al mostrarlos hay que citar la autoría y la licencia y, en los clips, indicar que están recortados. Al ejecutarlos se registrarán la huella SHA-256 de cada fichero, la versión del código (*commit*) y los resultados con fecha. *Ficha en elaboración a 29/10/2026: el conjunto de la demo puede cambiar.*

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
