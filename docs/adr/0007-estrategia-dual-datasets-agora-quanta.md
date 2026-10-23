# 0007. Estrategia dual de datasets: calibración en laboratorio (`Àgora`) vs. inferencia en producción (*«Quanta, quanta IA!»*)

* **Fecha:** 2026-10-19
* **Estado:** Aceptada
* **Decisores:** Equipo AIASN (Alba Camiña García, Rocío Jiménez Villén, Pilar de la Fuente Diez)
* **Directriz de referencia:** Dr. José Adrián Rodríguez Fonollosa (TALP-UPC, Diapositiva 41), Dra. Verónica Vilaplana (TALP-UPC, Diapositiva 91) y ALTAI

---

## Contexto y Problema

Surgió el debate de si prescindir del dataset oficial de audio `Àgora` (37 horas de debates de TV3 cedidas por la UPC) y operar exclusivamente sobre el videopodcast multimodal *«Quanta, quanta IA!»* (IDEAI-UPC / *betevé* en YouTube). Sin embargo, procesar contenidos sin anotar a mano carece de verdad terreno (*Ground Truth*) para evaluar el error objetivo (WER, DER), y el Dr. Adrián Fonollosa fijó como criterio central de evaluación comprobar empíricamente si el pipeline recupera el **14 % de habla femenina** anotado por lingüistas en `Àgora`.

## Opciones Consideradas

1. **Opción A (Monocultivo de Dataset en YouTube):** Analizar únicamente *«Quanta, quanta IA!»* y confiar a ciegas en la probabilidad de los modelos. *(Descartada por carecer de Ground Truth formal e incumplir el criterio de éxito de Fonollosa).*
2. **Opción B (Descarga masiva de 37h de vídeo de TV3 de hace 15 años):** *(Descartada por coste computacional innecesario y riesgos legales de web scraping).*
3. **Opción C (Estrategia Dual en Dos Tiempos):**
   * **Tiempo 1 (Laboratorio / Calibración pericial):** Evaluar sobre la muestra oficial de `Àgora` para calibrar el umbral ético de fiabilidad ($p \ge 0.80$) y verificar la recuperación del 14 % de habla femenina.
   * **Tiempo 2 (Producción / Demo viva multimodal):** Aplicar el motor ya calibrado sobre clips de vídeo real de divulgación institucional (*«Quanta, quanta IA!»* o debates CSIC/RTVE), calculando los 4 cuadrantes audiovisuales y lectura de rótulos por OCR.

## Decisión Adoptada

Se adopta la **Opción C**.

## Consecuencias

* **Positivas:**
  * Rigor científico incontestable: se audita contra el Ground Truth académico de la UPC.
  * Eficiencia computacional (*Green AI*): los experimentos de vídeo en producción se acotan a clips de 2 a 5 minutos, reduciendo a cero el gasto innecesario de GPU.
* **Compromisos asumidos:**
  * El paquete debe mantener adaptadores para formatos de audio puro (`WAV` + `XML`) y vídeo contenedor (`MP4`).

