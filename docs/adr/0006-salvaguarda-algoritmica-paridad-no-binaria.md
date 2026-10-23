# 0006. Salvaguarda algorítmica de paridad: minoración del techo masculino ante identidades no binarias

* **Fecha:** 2026-10-14
* **Estado:** Aceptada
* **Decisores:** Equipo AIASN (Alba Camiña García, Rocío Jiménez Villén, Pilar de la Fuente Diez)
* **Directriz de referencia:** Directriz inaugural de la Dra. Karina Gibert (`01_perspectiva_genero`, líneas 62–65)

---

## Contexto y Problema

En la sesión inaugural del reto, la Dra. Karina Gibert alertó sobre una distorsión institucional recurrente: computar la presencia de minorías de género o identidades no binarias **descontando su cuota exclusivamente del 40 % legalmente asignado a las mujeres**, mientras el bloque masculino retiene su 60 % hegemónico intacto. Las mujeres constituyen el 52 % de la sociedad y su presencia efectiva no puede verse mermada como donante unilateral de cuota ante la diversidad.

## Opciones Consideradas

1. **Opción A (Cuota Femenina Residual):** Tratar las identidades no binarias restando únicamente de la cuota mínima de mujeres. *(Descartada por sexista y lesiva para la paridad efectiva).*
2. **Opción B (Salvaguarda Algorítmica con Techo Masculino Decreciente):** El motor determinista de AIASN establece que la presencia masculina máxima admisible se reduce de forma proporcional ante cualquier presencia acreditada de identidades no binarias:
   $$\text{Presencia Masculina Máxima Aceptable} \le 100\% - \left(40\% + \text{Ratio No Binario}\right)$$
   Si la presencia masculina supera este techo mientras la femenina cae del 40 %, el sistema emite automáticamente una advertencia de asimetría de cuota.

## Decisión Adoptada

Se adopta la **Opción B**.

## Consecuencias

* **Positivas:**
  * Rigor político y sociológico acorde con las directrices de la presidencia del jurado (Dra. Karina Gibert).
  * Blindaje algorítmico contra la dilución de la representación femenina en paneles y eventos.
* **Compromisos asumidos:**
  * La fórmula matemática de paridad audita simultáneamente los tres ratios agregados.
