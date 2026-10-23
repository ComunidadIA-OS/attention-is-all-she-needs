# 0001. Separación estricta entre extracción heurística por IA y cálculo estadístico determinista en Python

* **Fecha:** 2026-10-16
* **Estado:** Aceptada
* **Decisores:** Equipo AIASN (Alba Camiña García, Rocío Jiménez Villén, Pilar de la Fuente Diez)
* **Directriz de referencia:** Dra. Karina Gibert (`1:14:30`) y Robustez Técnica ALTAI / Modelo PIO

---

## Contexto y Problema

Los Modelos de Lenguaje Grandes (LLMs) y los clasificadores multimodales son sistemas probabilísticos que sufren alucinaciones numéricas, falta de consistencia en operaciones aritméticas y variabilidad no determinista entre llamadas idénticas (*«prompt instability»*, advertida expresamente por Karina Gibert). Delegar en un LLM el cómputo de métricas periciales (tiempo acumulado de habla, duración media de turnos, ratio voz/pantalla o porcentajes de paridad) invalidaría el rigor probatorio del informe ante auditorías de igualdad, inspecciones de trabajo o tribunales.

## Opciones Consideradas

1. **Opción A (Inferencia de Extremo a Extremo con LLM):** Pasar la transcripción completa a un LLM (ej. `gpt-oss-120b` o `Qwen-VL`) con un prompt solicitando directamente los porcentajes de paridad y el veredicto. *(Descartada por alucinación aritmética, falta de reproducibilidad y alto coste de tokens).*
2. **Opción B (Separación Estricta Inferencia vs. Cálculo Determinista):** Los modelos de IA abiertos actúan únicamente como extractores y clasificadores de evidencias atómicas estructuradas. Todo cálculo de tiempos, duraciones, medias, frecuencias y ratios agregados se implementa en Python puro determinista (`pandas`), auditable y testeable mediante pruebas unitarias (`pytest`).

## Decisión Adoptada

Se adopta la **Opción B**. Ningún porcentaje, suma de tiempos ni ratio de paridad es generado por un modelo de IA generativa. La IA clasifica evidencias; el código en Python calcula, agrega y emite los veredictos matemáticos.

## Consecuencias

* **Positivas:**
  * Reproducibilidad matemática del 100 % (mismo input genera exactamente el mismo output).
  * Auditabilidad legal plena ante inspecciones y litigios.
  * Verificación automatizada mediante suites de `pytest`.
  * Cumplimiento estricto del pilar de *Robustez Técnica y Seguridad* de ALTAI y el Modelo PIO.
* **Compromisos asumidos:**
  * Exige definir y mantener contratos tabulares estrictos (`tiempo_i`, `tiempo_f`, `genero_inferido`) entre los componentes.
  * Mayor rigor en la capa de parsing y validación previa a la ingestión en el motor determinista.
