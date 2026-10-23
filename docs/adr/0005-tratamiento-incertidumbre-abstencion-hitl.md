# 0005. Tratamiento de la incertidumbre: abstención probabilística ($p < 0.80$) y supervisión humana *HitL*

* **Fecha:** 2026-10-16
* **Estado:** Aceptada
* **Decisores:** Equipo AIASN (Alba Camiña García, Rocío Jiménez Villén, Pilar de la Fuente Diez)
* **Directriz de referencia:** *Gender Shades* (Buolamwini & Gebru, 2018), Diapositiva 91 de Verónica Vilaplana y Dra. Karina Gibert (`1:00:50`)

---

## Contexto y Problema

Los clasificadores de visión y voz sufren de asimetría sistemática de error: en el benchmark de Verónica Vilaplana (Diapositiva 91), **el 50 % de las mujeres cayeron en la categoría `"unknown"`** debido a inclinaciones de cabeza o ángulos difíciles, mientras el 100 % de los hombres fueron reconocidos sin error. Forzar una etiqueta binaria ante la duda maquilla los datos y reproduce la discriminación algorítmica.

## Opciones Consideradas

1. **Opción A (Forzado Binario por Mayor Probabilidad):** Asignar género masculino si $p > 0.50$ y femenino si $p \le 0.50$. *(Descartada por sesgo algorítmico grave y ocultación de la incertidumbre técnica).*
2. **Opción B (Abstención Probabilística + Doble Anotador + Flujo HitL «Asumo / No asumo»):** Si la confianza estadística es inferior a 0.80 ($p < 0.80$), el sistema etiqueta como `"no_determinado"`, recurre a los rótulos OCR como segundo anotador prioritario y deriva los casos dudosos a la pantalla de supervisión humana (*Human-in-the-Loop*).

## Decisión Adoptada

Se adopta la **Opción B**. El modelo ejerce su derecho a la abstención estadística ante la incertidumbre.

## Consecuencias

* **Positivas:**
  * Transparencia pericial radical (no se ocultan errores ni casos ambiguos).
  * Cumplimiento directo del Artículo 14 del RIA (Supervisión Humana Obligatoria).
  * Eliminación del falso positivo en métricas de paridad.
* **Compromisos asumidos:**
  * La interfaz de usuario debe incluir un panel accesible para que un operador humano revise y arbitre los segmentos con estado `no_determinado`.
