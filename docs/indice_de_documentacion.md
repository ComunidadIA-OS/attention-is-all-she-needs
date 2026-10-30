<!--
SPDX-FileCopyrightText: 2026 Equipo 1: Attention Is All She Needs (Alba Camiña García, Pilar de la Fuente Diez, Rocío Jiménez Villén)
SPDX-License-Identifier: Apache-2.0
-->

# Índice de documentación
## Proyecto: «Attention Is All She Needs» (AIASN)

Índice completo de la documentación técnica, de gobernanza, ética, normativa, arquitectura y validación experimental del proyecto.

[← Volver al README](../README.md)

---

## 💡 Fundamentos y Misión Social

* 💡 [**docs/fundamentos_y_principios.md**](./fundamentos_y_principios.md): Misión social del proyecto, resignificación de Vaswani et al. (2017), aniquilación simbólica (*Tuchman 1978*), regla anti-*equality-washing*, principios de arquitectura y ciclo del Círculo Virtuoso.
* 📚 [**docs/bibliografia.md**](./bibliografia.md): Bibliografía unificada y referenciada en formato APA (7.ª ed.) estructurada por ejes temáticos: fuentes fundamentales de la investigación, representación de género y medios, NLP y sesgo textual, visión por computador y biometría, ética y filosofía moral, marco regulatorio y modelos abiertos.

---

## ⚖️ Gobernanza, Ética y Marco Normativo

* 🏛️ [**docs/clasificacion_legal_y_marco_normativo.md**](./clasificacion_legal_y_marco_normativo.md): **Encuadramiento normativo y posición jurídica**, interpretación del RIA (sistema de riesgo limitado precomercial, Art. 50.3), normas habilitantes (RGPD Art. 6/89, LPI Art. 67, Ley 2/2024) y tabla de supuestos excluidos que no aplican a AIASN y por qué.
* 🖥️ [**docs/especificacion_alertas_dashboard_y_hitl.md**](./especificacion_alertas_dashboard_y_hitl.md): Especificación funcional (objetivo) de las 3 vistas por rol, alertas anti-*equality-washing*, Test de Interlocución Femenina (TIF) y pantalla *«Asumo / No asumo»* (#6); el estado de implementación está en el [`ETHICS_CHECKLIST.md`](../ETHICS_CHECKLIST.md).
* ⚖️ [**docs/marco_normativo_y_mercado.md**](./marco_normativo_y_mercado.md): Marco normativo integral, cumplimiento exhaustivo del RIA (Reglamento UE 2024/1689), Ley Orgánica 2/2024 de Paridad, Directiva CSRD, datos CNMV (ejercicio 2024), dimensionamiento del mercado B2B (#8) y actualización regulatoria tras el Ómnibus Digital de IA y el Proyecto de Ley Orgánica de gobernanza de la IA ([ADR-0012](./adr/0012-marco-normativo-omnibus-digital-y-proyecto-de-ley.md)).
* 📝 [**docs/plantilla_aviso_art50_y_encargo_tratamiento.md**](./plantilla_aviso_art50_y_encargo_tratamiento.md): Borrador de aviso del Art. 50.3 RIA y de contenido mínimo del encargo del tratamiento para organizaciones que usen AIASN (**pendiente de revisión jurídica**). Contrato de servicios y condiciones de uso (incluidas las del Sello): [borrador](./contrato_servicios_y_condiciones_de_uso_borrador.md), también **pendiente de revisión jurídica**. Decisión de diseño sobre atribución de género: [ADR-0013](./adr/0013-atribucion-de-genero-por-evidencias-textuales.md).
* 👥 [**docs/evidencias_trabajo_en_equipo.md**](./evidencias_trabajo_en_equipo.md): Informe oficial de gobernanza paritaria, evidencias de trabajo colaborativo, registro de reuniones sincrónicas y proceso deliberativo del equipo (TyC §13).
* 📐 [**docs/adr/README.md**](./adr/README.md): Registro Canónico de Decisiones de Arquitectura (ADR-0001 a ADR-0013): justificación formal de la separación inferencia/cálculo, Green AI, biometría efímera, salvaguarda no binaria y TIF.
* ♿ [**docs/informe_conformidad_accesibilidad.md**](./informe_conformidad_accesibilidad.md): Informe de conformidad de accesibilidad del dashboard (*WCAG 2.2 AA*, UNE 153101 EX, RD 1112/2018 y Directiva UE 2019/882): auditoría `axe-core`, doble codificación de color, contraste verificado y soporte para lectores de pantalla (#18).
* 🧭 [**docs/guia_uso_responsable_y_preguntas_orientativas.md**](./guia_uso_responsable_y_preguntas_orientativas.md): Guía de uso responsable para quien despliegue AIASN: preguntas orientativas por áreas éticas y estado real de cada respuesta (medida de apoyo a la alfabetización en IA, Art. 4 RIA).
* 📋 [**ETHICS_CHECKLIST.md**](../ETHICS_CHECKLIST.md): Autoevaluación formal bajo los 7 principios de ALTAI y el Sandbox de la SEDIA / AESIA.
* 📜 [**CODE_OF_CONDUCT.md**](../CODE_OF_CONDUCT.md): Código Ético a medida, Estatuto de Propósito Social, Cláusula Anti-Lavado de Cara (Art. 6 Apache-2.0), Política de Uso Responsable y Código de Conducta.

---

## 🔬 Validación Experimental, Datasets y Modelos

* 🔬 [**docs/evaluacion_experimental_agora.md**](./evaluacion_experimental_agora.md): **Evaluación experimental sobre el corpus `Àgora` de la UPC (29/10/2026)**: cálculo exacto del *Ground Truth* de habla femenina (**14,61 %**), prueba del clasificador acústico de voz (94,5 % de exactitud global en 177 min) y validación de `whisper-large-v3` diarizado en OVHcloud AI Endpoints (desviación temporal $\le 1{,}4$ pp; 0,15 €/h audio).
* 📊 [**DATASET_CARD.md**](../DATASET_CARD.md): Ficha de procedencia de datos, perfil poblacional, mediciones de cómputo en RTX 4060 Laptop y régimen legal de fuentes (amparo en el Art. 67 del RDL 24/2021).
* 🤖 [**MODEL_CARD.md**](../MODEL_CARD.md): Ficha técnica de modelos abiertos, umbrales de certidumbre ($p < 0{,}80$), licencias y limitaciones conocidas.
* 🧪 [**TESTING.md**](../TESTING.md): Protocolo de pruebas en tres niveles (*Ground Truth*, tests unitarios con `pytest` y pruebas de usabilidad humana).

---

## 🚀 Guías de Ejecución, Despliegue y Sector Público

* 🏗️ [**ARCHITECTURE.md**](../ARCHITECTURE.md): Arquitectura técnica completa, desacoplamiento inferencia/cálculo determinista, pipeline Medallion y plan de producción.
* ⚙️ [**docs/guia_ejecucion_avanzada.md**](./guia_ejecucion_avanzada.md): Ejecución sin Docker, observabilidad con Langfuse para llamadas al LLM, depuración y generación de vídeos anotados con marcas visuales.
* 🏛️ [**docs/modo_sector_publico.md**](./modo_sector_publico.md): Adaptación para Administraciones Públicas: soberanía lingüística (lenguas cooficiales), Esquema Nacional de Seguridad (ENS) y aislamiento estricto de licencias (*Modo C*).
* 🧭 [**docs/hoja_de_ruta.md**](./hoja_de_ruta.md): Planificación técnica y regulatoria detallada: transición desde el prototipo `v0.1.0` hacia `v1.0.0` y versiones posteriores.
* 🔒 [**SECURITY.md**](../SECURITY.md): Modelo de amenazas frente a ataques adversarios (Art. 15 RIA y OWASP ML/LLM), *Zero Facial Retention* y reporte responsable.

---

## 🤝 Gestión del Proyecto y Comunidad

* 📖 [**GLOSSARY.md**](../GLOSSARY.md): Glosario maestro de 33 términos canónicos de la solución y diagrama visual del Círculo Virtuoso.
* 📋 [**Tablero Kanban «Sprint v0.1.0 a v1.0.0 — AIASN»**](https://github.com/users/ewigkeitt-cloud/projects/1): Seguimiento diario del equipo en GitHub Projects.
* 🤖 [**AGENTS.md**](../AGENTS.md): Guardarraíles vinculantes de seguridad, aislamiento de licencias y ética para agentes de código (*AI Coding Guardrails*).
* 🤝 [**CONTRIBUTING.md**](../CONTRIBUTING.md): Guía de contribución comunitaria y protocolo paritario de Git (`Co-authored-by`).
* 📝 [**CHANGELOG.md**](../CHANGELOG.md): Historial de versiones y evolución ágil del prototipo.
