<!--
SPDX-FileCopyrightText: 2026 Equipo 1: Attention Is All She Needs (Alba Camiña García, Pilar de la Fuente Diez, Rocío Jiménez Villén)
SPDX-License-Identifier: Apache-2.0
-->

# ADR-0011: Adopción del Test de Interlocución Femenina (TIF) como Adaptación Pericial del Test de Bechdel-Wallace en Entornos Audiovisuales Profesionales

* **Estado:** Aceptada
* **Fecha:** 2026-10-27
* **Autoras:** Alba Camiña García, Rocío Jiménez Villén, Pilar de la Fuente Diez (Equipo 1)
* **Referencia Legal y Metodológica:** Alison Bechdel (1985), Liz Wallace, UNESCO Global Media Monitoring Project (GMMP 2020), Ley Orgánica 2/2024 de Representación Paritaria, Directiva (UE) 2024/825 y principios de Gobernanza e Interlocución Válida (Adela Cortina y Carol Gilligan).

---

## 1. Contexto y Problema

El clásico **Test de Bechdel-Wallace (1985)** nació en el ámbito de la ficción cinematográfica para evidenciar la invisibilidad femenina evaluando tres reglas sencillas: (1) que aparezcan al menos dos mujeres, (2) que hablen entre sí, y (3) sobre algo que no sea un hombre.

Al trasladar este concepto al análisis de **contenidos informativos, debates, mesas redondas y retransmisiones corporativas**, surgían tres discrepancias operativas identificadas en los debates colegiados del equipo (Debate D-10 y Doc 26):
1. **Inaplicabilidad de la Regla 3 Clásica en Ámbitos Profesionales:** Evaluar si dos expertas hablan «de un hombre» en una mesa redonda sobre inteligencia artificial o economía desvirtúa el análisis técnico. Lo relevante en un panel es si existe **interlocución directa horizontal entre mujeres sin mediación masculina**.
2. **El Problema del Falso Negativo en Formatos Especiales:** En formatos unipersonales (un monólogo, un informativo con una sola presentadora o una entrevista individual a una científica), aplicar el test de 0 a 3 daba como resultado "0/3" (Suspenso), penalizando injustamente una pieza protagonizada enteramente por una mujer.
3. **El Riesgo de Redundancia con otras Alertas:** Medir que hay al menos 2 mujeres ya lo computan el Ratio Voz/Pantalla (RVP) y la Alerta de Infrarrepresentación. El valor diferencial del test radica en evaluar la **autoridad y la dinámica relacional inter-femenina**.

---

## 2. Opciones Consideradas

* **Opción A (Test de Bechdel Rígido Clásico 0 a 3):** Evaluar siempre los tres puntos clásicos con puntuación numérica entera (0, 1, 2 o 3) en cualquier tipo de vídeo. *(Descartada: penaliza piezas unipersonales femeninas y no discrimina formatos donde no hay hombres).*
* **Opción B (Adopción - Test de Interlocución Femenina con Árbol de Decisión en Tres Estados):** Rediseñar la metodología como una adaptación pericial específica para el audiovisual profesional (**Test de Interlocución Femenina — TIF**):
  1. **Condición Previa de Activación:** El test solo se activa para emitir veredicto cuando la pieza reúne condiciones de debate plural: presencia de al menos **dos mujeres ($M \ge 2$) y al menos un hombre ($H \ge 1$)**.
  2. **Tres Reglas Profesionales Deterministas:**
     * **R1 (Pluralidad Femenina / Superación del Efecto Token):** Al menos 2 mujeres intervienen con voz activa ($\%V > 0$).
     * **R2 (Acreditación y Autoridad Propia):** Al menos 2 mujeres son acreditadas con nombre propio o cargo profesional mediante OCR de rótulos o transcripción (`naming`).
     * **R3 (Interlocución Horizontal Directa):** Existe al menos una transición consecutiva de turno de palabra $\text{Mujer}_A \to \text{Mujer}_B$ sin mediación ni interrupción masculina intermedia.
  3. **Árbol de Decisión en 3 Estados:**
     * `evaluado_supera`: Cumple la condición previa y supera R1, R2 y R3.
     * `evaluado_no_supera`: Cumple la condición previa pero suspende alguna de las reglas (reportando qué regla falló: tokenismo, falta de cargo o mediación masculina).
     * `no_evaluable`: La pieza no reúne la condición previa (ej. menos de dos mujeres o formato femenino exclusivo), explicitando el motivo para no penalizar el cómputo global.

---

## 3. Decisión Adoptada

Se aprueba formalmente por unanimidad la **Opción B**, codificando el **Test de Interlocución Femenina (TIF)** en `aiasn/core/fusion.py`, exponiendo su veredicto en `aiasn/api/schemas.py` y visualizándolo en el panel frontend (`frontend-piloto/`) mediante un semáforo accesible de 3 estados (`✅ Superado`, `❌ No superado`, `⚪ No evaluable`).

---

## 4. Consecuencias y Compromisos (*Trade-offs*)

* **Positivas:**
  * Rigor científico: elimina falsos suspensos en vídeos unipersonales o monográficos de mujeres.
  * Perspectiva de género profunda: audita por primera vez en código abierto la **interlocución horizontal entre mujeres** y el reconocimiento formal de sus cargos en retransmisiones.
  * Cumplimiento con las bases: responde de un vistazo a la pregunta de las TyC §9.1.3 («en qué medida aparecen en roles protagonistas»).
* **Compromisos asumidos:**
  * Requiere sincronizar las marcas de tiempo de los turnos de diarización para calcular las transiciones consecutivas $\text{Mujer}_A \to \text{Mujer}_B$.

