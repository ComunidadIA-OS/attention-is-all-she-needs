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

Se adopta la **Opción B**. El audio diarizado actúa como columna vertebral de sincronización temporal y el vídeo se analiza selectivamente aplicando la constante `STRIDE`.

## Consecuencias

* **Positivas:**
  * Ahorro superior al 95 % de tiempo de GPU y consumo eléctrico.
  * Coste computacional inferior a 0,30 € por hora de vídeo analizada.
  * Procesado de 1 hora de vídeo en ~4–6 minutos sobre una única tarjeta NVIDIA V100.
* **Compromisos asumidos:**
  * Margen de resolución temporal de $\pm 0.5$ a $1.0$ segundos en la entrada/salida de plano, lo cual resulta estadísticamente inocuo para métricas agregadas de presencia y protagonismo.
