# 0003. Muestreo selectivo de fotogramas (`STRIDE` 1–5 fps) guiado por audio frente a 30 fps continuos

* **Fecha:** 2026-10-16
* **Estado:** Aceptada
* **Decisores:** Equipo AIASN (Alba Camiña García, Rocío Jiménez Villén, Pilar de la Fuente Diez)
* **Directriz de referencia:** Dra. Verónica Vilaplana (Diapositivas 85–91) y Criterio de *Algoritmos Verdes / Green AI* (Karina Gibert `1:56:50` y Montse Guàrdia `1:55:45`)

---

## Contexto y Problema

El vídeo estándar a 30 fps contiene 108.000 fotogramas por hora. Procesar cada fotograma con detectores convolucionales profundos y clasificadores de rostros colapsa las cuotas de computación, eleva la huella de carbono y vulnera el principio de sostenibilidad energética (*Green AI*). Verónica Vilaplana demostró empíricamente en su taller que la presencia de ponentes, la disposición escénica y los rótulos informativos no varían sustancialmente en fracciones de segundo.

## Opciones Consideradas

1. **Opción A (Procesado Exhaustivo a 25/30 fps continuos):** Inferencia fotograma a fotograma en GPU. *(Descartada por coste energético prohibitivo, lentitud y saturación innecesaria de hardware).*
2. **Opción B (Muestreo Selectivo `STRIDE` guiado por eventos de audio):** Muestrear entre 1 y 5 fotogramas por segundo (o guiado por los cambios de turno detectados por Whisper), calculando `screen_time_s`, `area` y `centrality` con `YOLO11m + ByteTrack` y lectura de rótulos con `EasyOCR`.

## Decisión Adoptada

Se adopta la **Opción B**, con un muestreo fijo (no guiado por los turnos de audio) que se configura en `VideoSettings` (`aiasn/settings.py`):

* El vídeo se remuestrea a 25 fps (lo exige TalkNet).
* **Personas** (YOLO11m-pose + BoT-SORT): 1 de cada 4 fotogramas (`stride = 4`, 6,25 fps).
* **Caras y hablante activo** (InsightFace + TalkNet): todos los fotogramas, porque TalkNet necesita la secuencia continua de la cara.
* **Rótulos** (EasyOCR): 1 fotograma por segundo (`ocr_fps = 1`).

Audio y vídeo se procesan en paralelo y se cruzan después por tiempo.

## Consecuencias

* **Positivas:**
  * La detección de personas, el paso más pesado, se hace sobre la cuarta parte de los fotogramas, y el OCR sobre 1 por segundo.
  * Medido el 29/10/2026 en una RTX 4060 Laptop (8 GB): los vídeos de la demo, de 1,4 a 5,2 min, tardan entre 2 y 9 min en total, y el paso de vídeo entre 75 y 453 s (`DATASET_CARD.md`, 1.2). Sin GPU, un vídeo de 84 s tardó 45 min con 2 núcleos.
  * No se ha medido el ahorro frente al procesado exhaustivo (Opción A) ni el consumo eléctrico.
* **Compromisos asumidos:**
  * Margen de resolución temporal de $\pm 0.5$ a $1.0$ segundos en la entrada/salida de plano, lo cual resulta estadísticamente inocuo para métricas agregadas de presencia y protagonismo.

