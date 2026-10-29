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

### 1.1. Vídeos de prueba y de calibración (estado a 29/10/2026)

| Vídeo | Uso | Origen y licencia | ¿Se puede compartir el fichero? | Estado | SHA-256 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `clip_1_wikimania.mp4` (3:38) | **Demostración** y prueba pública reproducible | Panel presencial en plano general fijo: [*Wikipedia Five Pillars Panel*](https://commons.wikimedia.org/wiki/File:Wikimania_2015_-_Wikipedia_Five_Pillars_Panel.webm), Wikimedia México (Wikimania 2015), Wikimedia Commons, **CC BY-SA 3.0**. Composición paritaria: dos ponentes mujeres y dos ponentes hombres (2M / 2H). Tramo inicial de apertura | Sí, con atribución («Wikimedia México»), indicando que está recortado, y con la misma licencia (CC BY-SA 3.0) | Licencia y enlace comprobados el 28/10/2026. Ejecutado el 29/10/2026 (ver 1.2). **Pendiente:** confirmación del tramo exacto por Rocío | `1bc959e4da17d302ce13ef6e9013c77ada060fceb022f15992e5ece2b37da0e6` |
| `clip_2_wikimania.mp4` (5:12) | **Demostración** y contraste paritario | El mismo panel presencial en plano general fijo ([*Wikipedia Five Pillars Panel*](https://commons.wikimedia.org/wiki/File:Wikimania_2015_-_Wikipedia_Five_Pillars_Panel.webm), Wikimedia México, **CC BY-SA 3.0**; composición paritaria 2M / 2H). Tramo recomendado en catálogo: `10:00–15:12` (5 min 12 s; intervención masculina con presencia femenina visible continua para contrastar el Ratio Voz/Pantalla y la regla anti-*equality-washing*) | Sí, con atribución («Wikimedia México»), indicando que está recortado, y con la misma licencia (CC BY-SA 3.0) | Enlace y licencia comprobados. Ejecutado el 29/10/2026 (ver 1.2). **Pendiente:** confirmación del tramo exacto por Rocío | `3c556965eb4bfe94f8cad5c46efcdba3bd8a5655008fec106f4459e05fcdbc92` |
| `clip_mesa_redonda.mp4` (5:11) | **Demostración** (formato videollamada) | Videollamada virtual en cuadrícula 2×2: [mesa redonda FLISoL Tenerife 2021: *Cultura libre y tecnología para la sociedad*](https://archive.org/details/flisoltenerife20211mesa-redonda), FLISoL Tenerife, Internet Archive, **CC BY-SA 4.0**. Composición paritaria: dos ponentes mujeres y dos ponentes hombres (2M / 2H). Tramo recomendado en catálogo: `09:00–14:11` (5 min 11 s; toma la palabra una ponente femenina mientras todos siguen en cuadro) | Sí, con atribución («FLISoL Tenerife 2021»), indicando que está recortado, y con la misma licencia (CC BY-SA 4.0) | Licencia y enlace comprobados el 28/10/2026. Ejecutado el 29/10/2026 (ver 1.2). **Pendiente:** confirmación del tramo exacto por Rocío. *(Alternativa verificada en estudio Full HD: Wikimania 2025, CC BY-SA 4.0)* | `71b1fa48023d223fc5e270ab65ac1181d73759cead0e08889b6bc9137565f7bf` |
| `csic_javier_oroz.mp4` (1:24) | **Demostración** (caso asimetría) / En revisión | [*CSIC Cicerón. Biología Estructural para acelerar el diagnóstico de ELA. Javier Oroz*](https://www.youtube.com/watch?v=V6I84IL-L0o), CSIC Comunicación (YouTube, publicado el 07/07/2025). Muestra investigadoras sin voz activa mientras habla el ponente. **CC BY** (Creative Commons de YouTube: «reutilización permitida»). El equipo indica la versión 4.0, **no verificada en la página** | Sí, con atribución. Se usa completo y sin cambios | Duración y licencia comprobadas el 29/10/2026. Ejecutado el 29/10/2026 (ver 1.2). **Pendiente:** decisión del equipo de si se mantiene en el set final frente al Plan A (100 % CC BY-SA) | `5c4a1cda5cc45685cc3c4b69195a2313a8a8583514408c8b94f736ad8d077583` |
| `margarita_salas.mp4` (5:00) | **Demostración** (referentes y rótulos) | Conferencia inaugural del ciclo «Mujer y Ciencia»: [*Dra. Margarita Salas, «Mujer y Ciencia: mi propia experiencia»*](https://www.youtube.com/watch?v=2nlMCQlT58g), Vall d'Hebron Barcelona Hospital Campus (YouTube, publicado el 12/03/2012). Mesa de dos mujeres y un hombre (2M / 1H), presentados con rótulo; cita a Severo Ochoa como referente. Tramo `00:00–05:00`. **CC BY 4.0** (Creative Commons de YouTube: «reutilización permitida»; la ayuda de YouTube enlaza a la versión 4.0) | Sí, con atribución («Vall d'Hebron Barcelona Hospital Campus») e indicando que está recortado | Licencia comprobada el 29/10/2026 en la página, la descripción y la tarjeta final. Sin menores (comprobado a ojo: las edades bajas que estimaba el modelo eran cabezas del público de espaldas). Ejecutado el 29/10/2026 (ver 1.2) | `bd2e98c5e5fe5063d03df96e65221e00669677eb1c0bd057d83ef4cd054775a4` |
| `cultura_igualdad.mp4` (4:56) | **Demostración** (rótulos con nombre y cargo) | Clausura de las jornadas «Culturas en Igualdad»: [*Diálogo entre Ernest Urtasun y Nerea Pérez de las Heras*](https://www.youtube.com/watch?v=IW9_5ngb4Nc), Ministerio de Cultura (YouTube, publicado el 26/03/2026). Diálogo en escenario entre el ministro de Cultura y una periodista (1M / 1H), con rótulos de nombre y cargo. Tramo `00:04–05:00` (sin el cartel inicial, cuyos personajes dibujados se detectaban como personas). **CC BY 4.0** (Creative Commons de YouTube: «reutilización permitida»; la ayuda de YouTube enlaza a la versión 4.0) | Sí, con atribución («Ministerio de Cultura») e indicando que está recortado | Licencia comprobada el 29/10/2026 en la página, la descripción y la tarjeta final. Sin menores (comprobado a ojo: la edad baja que estimaba el modelo era un personaje del cartel). Ejecutado el 29/10/2026 (ver 1.2) | `2e8c54f97ffe93ad9843eb17ca6f9c0f7ba68b6b2b8530c903b1b8826bc5d2f7` |
| Vídeos de divulgación científica descargados de YouTube por el equipo | **Calibración interna** del modelo | YouTube; licencia **no comprobada**; fuente original por localizar | **No**: sin redistribuir y fuera de la demostración y de las capturas públicas | Solo uso interno | — |
| *«Quanta, quanta IA!»* | **Calibración interna** | betevé / IDEAI-UPC (YouTube); **sin permiso expreso** | **No** | Solo análisis en local; el amparo de minería de datos está pendiente de validar | — |

Los `.mp4` **no están en Git**: se descargan de los enlaces originales mediante recorte directo sin recodificación (`ffmpeg`). Según el equipo, **no aparecen menores** en estos seis vídeos (no verificado de forma independiente), y las personas intervienen en público y en actos grabados para difundirse. Al mostrarlos hay que citar la autoría y la licencia y, en los clips, indicar que están recortados. La huella SHA-256 de cada fichero está en la tabla y la medición de su ejecución, en 1.2. *Ficha en elaboración a 29/10/2026: el conjunto de la demo puede cambiar.*

#### Órdenes reproducibles de descarga y recorte directo (`ffmpeg`):
```bash
# Clip 2 (Wikimania 2015, HD 720p, CC BY-SA 3.0):
ffmpeg -ss 00:10:00 -i "https://upload.wikimedia.org/wikipedia/commons/transcoded/4/4e/Wikimania_2015_-_Wikipedia_Five_Pillars_Panel.webm/Wikimania_2015_-_Wikipedia_Five_Pillars_Panel.webm.720p.vp9.webm" -t 00:05:12 -c copy clip_2_wikimania.webm

# Clip 3 (FLISoL Tenerife 2021, CC BY-SA 4.0):
ffmpeg -ss 00:09:00 -i "https://archive.org/download/flisoltenerife20211mesa-redonda/MesaRedonda.mp4" -t 00:05:11 -c copy clip_mesa_redonda.mp4

# Margarita Salas (YouTube, CC BY): los 5 primeros minutos
yt-dlp -f "bv*[height<=480]+ba/b[height<=480]" --download-sections "*0-300" --force-keyframes-at-cuts --merge-output-format mp4 -o margarita_salas.mp4 "https://www.youtube.com/watch?v=2nlMCQlT58g"

# Cultura en igualdad (YouTube, CC BY): los 5 primeros minutos, sin los 4 s del cartel inicial
yt-dlp -f "bv*[height<=480]+ba/b[height<=480]" --download-sections "*0-300" --force-keyframes-at-cuts --merge-output-format mp4 -o cultura_5min.mp4 "https://www.youtube.com/watch?v=IW9_5ngb4Nc"
ffmpeg -ss 4 -i cultura_5min.mp4 -c:v libx264 -crf 20 -c:a aac cultura_igualdad.mp4
```

### 1.2. Medición de la ejecución (29/10/2026)

Los seis vídeos de la demo, uno tras otro, con el código del *commit* `8f8eec9`, en Ubuntu 24.04 con un Ryzen 7 7840HS, 30 GB de RAM y una RTX 4060 Laptop (8 GB), con Docker y los modelos ya descargados. Audio y vídeo van en paralelo, así que el total no es la suma de los pasos. Tiempos en segundos.

Cómo se obtiene cada dato (scripts en `scripts/`):
* `measure_demo.sh` lanza el *worker* con cada vídeo y guarda un log por vídeo. Calcula el SHA-256 de cada fichero (`sha256sum`) y mide el **total** como el tiempo real del contenedor (`docker run`, incluidos el arranque y la carga de modelos).
* `measure_run.py` ejecuta el *worker* y cuenta los **tokens del LLM**: el `usage` que devuelve OVHcloud AI Endpoints en cada respuesta, leído con un *callback* de LiteLLM.
* `measure_table.py` genera las dos tablas a partir de los logs. La **duración del audio** y el **tiempo de cada paso** son los que el propio *worker* escribe en su log, una línea por paso.

| Fichero | Audio | Total | Audio (transcripción) | Vídeo: detección · hablante · OCR | NLP | Rótulos | Silver + gold |
|---|---|---|---|---|---|---|---|
| `clip_1_wikimania.mp4` | 3,6 min | 348 | 22 | 310: 204 · 61 · 32 | 49 | 13 | 5 |
| `clip_2_wikimania.mp4` | 5,2 min | 455 | 26 | 424: 283 · 81 · 43 | 59 | 7 | 5 |
| `clip_mesa_redonda.mp4` | 5,2 min | 523 | 26 | 453: 290 · 84 · 67 | 214 | 51 | 0,4 |
| `csic_javier_oroz.mp4` | 1,4 min | 108 | 7 | 75: 50 · 7 · 13 | 16 | 10 | 5 |
| `margarita_salas.mp4` | 5,0 min | 377 | 22 | 322: 246 · 43 · 20 | 64 | 30 | 5 |
| `cultura_igualdad.mp4` | 4,9 min | 374 | 30 | 237: 189 · 25 · 14 | 76 | 113 | 5 |

Tokens del LLM (OVHcloud AI Endpoints):

| Fichero | Llama 3.3 70B: llamadas · entrada · salida | gpt-oss-120b (referentes): llamadas · entrada · salida |
|---|---|---|
| `clip_1_wikimania.mp4` | 11 · 9.134 · 3.156 | 1 · 1.239 · 281 |
| `clip_2_wikimania.mp4` | 6 · 7.602 · 2.659 | 1 · 1.445 · 116 |
| `clip_mesa_redonda.mp4` | 14 · 14.081 · 5.397 | 1 · 1.831 · 246 |
| `csic_javier_oroz.mp4` | 10 · 5.514 · 1.912 | 1 · 665 · 175 |
| `margarita_salas.mp4` | 13 · 12.494 · 5.145 | 1 · 1.638 · 1.124 |
| `cultura_igualdad.mp4` | 36 · 26.012 · 9.143 | 1 · 1.757 · 936 |

La transcripción (Whisper large v3) se cobra por duración del audio. Los rótulos son la tarea que más llamadas hace: una por cada 4 bloques de texto leídos por el OCR.

## 2. Régimen Legal y Amparo en Minería de Textos y Datos (TDM)

1. **Uso de Datos en Fase de Hackathon:** El procesado de estos fragmentos audiovisuales se realiza estrictamente en el marco de la investigación científica, formativa y sin fines de lucro del reto.
2. **Amparo en el Art. 67 del Real Decreto-ley 24/2021:**
   * La extracción de metadatos, transcripciones estadísticas y tiempos de pantalla constituye **minería de textos y datos (TDM)** legítima sobre contenidos a los que se tiene acceso lícito.
   * El repositorio **no redistribuye los archivos de vídeo o audio originales en bruto** (`*.mp4`, `*.wav` excluidos en `.gitignore`), sino exclusivamente el código de análisis y las tablas de resultados derivados reproducibles.
3. **Privacidad y Datos Personales (RGPD):**
   * Los vectores faciales se calculan solo en memoria y se descartan antes de escribir en el lake; no se construyen ni comercializan perfiles biométricos de las personas intervinientes.
   * Mientras procesa un vídeo, el pipeline escribe ficheros temporales (fotogramas, audio y vídeo remuestreado) en `tmp/`, y el vídeo subido está en `landing/`. Con Docker Compose, al terminar se borran los temporales y, si todos los pasos han ido bien, el vídeo de `landing/` (`PRIVACY__DELETE_MEDIA_AFTER_RUN`; sin Docker está desactivado por defecto, para depurar). Se conservan las tablas del lake. Ambas rutas están fuera del repositorio (`data/` y `tmp/` en `.gitignore`). Véase `ETHICS_CHECKLIST.md`, 3.5.
   * La edad no se guarda: MiVOLO la predice, pero se descarta sin leerla (minimización de datos).
4. **Tiempo de procesado:** con GPU, los vídeos de la demo (1,4–5,2 min de audio) tardan entre 2 y 9 min (ver 1.2). Sin GPU el procesado es mucho más lento (un vídeo de 84 s tardó 45 min con 2 núcleos), así que en CPU conviene usar vídeos cortos.
