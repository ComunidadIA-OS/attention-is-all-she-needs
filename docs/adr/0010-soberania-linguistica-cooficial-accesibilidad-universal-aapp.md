<!--
SPDX-FileCopyrightText: 2026 Equipo 1: Attention Is All She Needs (Alba Camiña García, Pilar de la Fuente Diez, Rocío Jiménez Villén)
SPDX-License-Identifier: Apache-2.0
-->

# ADR-0010: Soberanía Lingüística Cooficial y Accesibilidad Universal por Diseño para Administraciones Públicas

* **Estado:** Aceptada
* **Fecha:** 2026-10-25
* **Autoras:** Alba Camiña García, Pilar de la Fuente Diez y Rocío Jiménez Villén (Equipo 1 — AIASN)
* **Issue relacionada:** [#18](https://github.com/ComunidadIA-OS/attention-is-all-she-needs/issues/18)

---

## 1. Contexto y Problema
El despliegue de una herramienta de auditoría de paridad y protagonismo con vocación de servicio público en España y Europa (conforme al Art. 157 de la Ley 40/2015 LRJSP sobre reutilización de sistemas entre Administraciones Públicas) exige garantizar dos derechos fundamentales desde el diseño (*by design*):
1. **Pluralismo y Soberanía Lingüística (Art. 3 CE):** Los corpus públicos del reto (`Àgora` y `Canal 3/24` de la UPC, RTVE, EITB, TVG, À Punt, IB3) combinan castellano, catalán/valenciano, gallego y euskera, además de inglés en congresos científicos.
2. **Accesibilidad Universal y Cognitiva (Art. 49 CE, CDPD ONU, Ley 15/2022 Art. 23, Directiva UE 2019/882 y RD 1112/2018):** Los cuadros de mando puramente visuales basados solo en colores (rojo/verde) o gráficas complejas excluyen a personas con discapacidad visual o cognitiva.

## 2. Decisión Adoptada
1. **Soporte nativo de las lenguas cooficiales (`es`, `ca`, `gl`, `eu`, `en`):**
   * En la transcripción (`whisper-large-v3` en OVHcloud AI Endpoints con detección automática de idioma o parámetro `language`),
   * En los embeddings semánticos multilingües (`bge-m3`),
   * Y en los metadatos de auditoría y elegibilidad (`LENGUAS_COOFICIALES_SOPORTADAS` en `aiasn/core/fusion.py` y `aiasn/core/compliance.py`).
2. **Accesibilidad Universal por Diseño (`WCAG 2.2 Nivel AA` y `UNE 153101 EX`):**
   * El motor determinista genera de serie en cada reporte el campo `resumen_lectura_facil` (`generar_resumen_lectura_facil`), estructurado conforme a la norma española **UNE 153101 EX de Lectura Fácil**, directamente interpretable por lectores de pantalla (`NVDA`, `JAWS`, `VoiceOver`) y líneas braille sin depender de la capa visual.
   * Todas las alertas del dashboard combinan **Icono + Etiqueta Textual + Patrón/Color** con contraste $\ge 4.5:1$.

## 3. Consecuencias
* **Positivas:** Cumplimiento estricto del Esquema Nacional de Interoperabilidad, elegibilidad inmediata para licitaciones públicas y transferencia tecnológica en el Directorio de Soluciones Libres de la Administración (CTT / SEDIA).
* **Coste computacional:** Nulo (**0 W adicionales de GPU**), ya que la generación del bloque de Lectura Fácil es 100 % determinista en el núcleo de Python.
