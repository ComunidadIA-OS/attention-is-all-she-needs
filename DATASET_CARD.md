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
| **A1.** Wikimania 2015, *Wikipedia Five Pillars Panel* (fragmento `10:00–15:00`) | Prueba pública reproducible | Wikimedia Commons, **CC BY-SA 3.0** (Wikimedia México) | Sí, con atribución y la misma licencia | Enlace y licencia comprobados el 28/10/2026; **análisis pendiente de ejecutar** |
| **A2.** FLISoL Tenerife 2021, mesa redonda (fragmento `09:00–14:00`) | Prueba pública reproducible | Internet Archive, **CC BY-SA 4.0** | Sí, con atribución y la misma licencia | Enlace y licencia comprobados el 28/10/2026; **análisis pendiente de ejecutar** |
| `robot-social-csic-1526` y otros vídeos descargados de YouTube por el equipo | **Calibración interna** del modelo | YouTube; licencia **no comprobada**; fuente original por localizar. Según Rocío (28/10), entre ellos aparece al menos un niño | **No**: sin redistribuir y fuera de la demostración y de las capturas públicas | Solo uso interno |
| *«Quanta, quanta IA!»* | **Calibración interna** | betevé / IDEAI-UPC (YouTube); **sin permiso expreso** | **No** | Solo análisis en local; el amparo de minería de datos está pendiente de validar |

Reproducción de A1 y A2: fragmento con `ffmpeg -ss … -to … -i <URL> -c copy` sobre las URL oficiales de Wikimedia Commons e Internet Archive (los enlaces responden; las órdenes completas aún **no se han ejecutado de principio a fin**). Al ejecutarlos se registrarán la huella SHA-256 del fragmento, la versión del código (*commit*) y los resultados con fecha. Las citas de autoría son «Wikimedia México» (A1) y «FLISoL Tenerife 2021» (A2).

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
