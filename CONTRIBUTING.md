# SPDX-FileCopyrightText: 2026 Equipo 1: Attention Is All She Needs (Alba Camiña García, Pilar de la Fuente Diez, Rocío Jiménez Villén)
# SPDX-License-Identifier: Apache-2.0

# Guía de Contribución al Proyecto

## Proyecto: «Attention Is All She Needs» (AIASN)
**Reto «Mujeres por la IA Abierta» — Equipo 1**

¡Gracias por tu interés en contribuir a **Attention Is All She Needs**! Este proyecto es de código abierto (licencia Apache 2.0) y sigue los principios de la *Open Source AI Definition* (OSI), promoviendo la transparencia algorítmica, la perspectiva de género y la reproducibilidad técnica.

---

## 1. Principios de Desarrollo del Equipo

1. **Separación estricta entre inferencia y cálculo:** Los modelos de IA extraen evidencias audiovisuales estructuradas; todos los tiempos, porcentajes y ratios son calculados de forma 100 % determinista mediante código auditable en Python.
2. **Trazabilidad y *Human-in-the-Loop* (HitL):** Toda métrica generada debe vincularse a su intervalo temporal (`tiempo_i` - `tiempo_f`) o fotograma. Ante incertidumbre ($p < 0.80$), el clasificador se abstiene (`no_determinado`).
3. **Eficiencia computacional (*Algoritmos Verdes*):** Priorizar el uso de AI Endpoints de OVHcloud y muestreo selectivo de fotogramas (`STRIDE`) frente al procesado masivo de vídeo bruto en GPU.

---

## 2. Flujo de Trabajo en Git (Git Flow Ágil)

Siguiendo las recomendaciones de **Jorge Teixeira** (*Comunidad IA-OS*) para evitar «commits monolíticos», trabajamos exclusivamente con ramas temáticas y Pull Requests:

### 2.1. Nomenclatura de Ramas
* `feat/<modulo>-<descripcion-corta>`: Nuevas funcionalidades (ej. `feat/audio-pipeline`, `feat/video-pipeline-notebooks`).
* `fix/<modulo>-<descripcion-corta>`: Corrección de errores.
* `docs/<descripcion-corta>`: Documentación, guías o gobernanza (ej. `docs/open-source-governance`).
* `test/<descripcion-corta>`: Pruebas unitarias o de integración.

### 2.2. Procedimiento para Enviar Cambios
1. Crea una rama a partir de `main`:
   ```bash
   git checkout main
   git pull origin main
   git checkout -b feat/mi-mejora
   ```
2. Realiza cambios atómicos y estructurados.
3. Haz push a tu rama remota:
   ```bash
   git push -u origin feat/mi-mejora
   ```
4. Abre una **Pull Request (PR)** en GitHub hacia la rama `main`.
5. La PR debe ser revisada y aprobada por al menos una integrante del equipo antes del *merge*.

---

## 3. Convención de Commits, Idioma y Coautoría Paritaria

### 3.1. Mensajes de Commit (*Conventional Commits*)
Los commits pueden redactarse indistintamente en **español o en inglés**, manteniendo siempre la disciplina del estándar *Conventional Commits*:
* `feat(...)`: Nueva característica.
* `fix(...)`: Corrección de fallo.
* `docs(...)`: Cambios en documentación.
* `test(...)`: Incorporación o mejora de pruebas unitarias.
* `refactor(...)`: Reestructuración sin cambio funcional.
* `chore(...)`: Tareas de mantenimiento o configuración.
* `build(...)`: Cambios que afectan al empaquetado o dependencias.
* `ci(...)`: Configuración de flujos de integración continua (GitHub Actions).

### 3.2. Criterio Lingüístico del Repositorio
* **Documentación institucional y de producto (`README.md`, guías, memoria, accesibilidad):** Redactada prioritariamente en **español**, con compatibilidad multilingüe y soporte de lenguas cooficiales (catalán, euskera, gallego) conforme a `ADR-010`.
* **Fichas estandarizadas de modelos y datos (`MODEL_CARD.md`, `DATASET_CARD.md`):** Se redactan en **inglés o formato bilingüe**, siguiendo los estándares internacionales de Hugging Face / Mitchell et al. para facilitar la reutilización comunitaria global (Open Source AI Definition de la OSI).

### 3.3. Autoría Individual y Coautoría Transversal de Equipo
El equipo sigue un esquema equilibrado de reconocimiento técnico:
* **Commits individuales de desarrollo (regla general):** Cada integrante firma y sube sus propios commits como **autora principal y directa** de sus módulos y tareas (por ejemplo, pipelines de audio/NLP de Rocío, frontend y UX de Pilar, o motor determinista y arquitectura de Alba). La persona que ejecuta el commit figura como autora indiscutible en la cabecera de Git, el historial de GitHub y el cómputo de líneas de código (`git blame`).
* **Commits transversales y decisiones colegiadas (excepción colaborativa):** En cambios que afecten a la gobernanza común (`CONTRIBUTING.md`, licencias, contratos de integración entre módulos o acuerdos de equipo), la autora del commit añade al final los trailers `Co-authored-by` de las compañeras para acreditar la colaboración paritaria ante el jurado del reto:

```git
feat(scope): short description in english or spanish

Optional body detailing architectural decisions.

Co-authored-by: Nombre Colega 1 <email1@ejemplo.com>
Co-authored-by: Nombre Colega 2 <email2@ejemplo.com>
```

---

## 4. Contrato de Datos para Fusión Multimodal

Para asegurar la interoperabilidad entre los módulos de audio, vídeo y texto, toda salida de datos debe respetar el esquema tabular canónico:

| Campo | Tipo | Descripción |
| :--- | :---: | :--- |
| `tiempo_i` | `float` | Segundo de inicio del evento o turno (redondeado a 2 decimales). |
| `tiempo_f` | `float` | Segundo de finalización del evento o turno. |
| `transcripcion` | `str` | Texto transcrito por Whisper o extraído por OCR de rótulo. |
| `genero_inferido` | `str` | `mujer`, `hombre` o `no_determinado` (en caso de duda o abstención). |

---

## 5. Reporte de Incidencias (*Issues*)

Si encuentras un error o deseas proponer una mejora:
1. Revisa los *Issues* existentes para evitar duplicados.
2. Abre un *New Issue* indicando:
   * Comportamiento observado vs. esperado.
   * Pasos reproducibles y archivo de entrada utilizado.
   * Entorno de ejecución (versión de Python, GPU o AI Endpoints).


### 5.1. Decisiones de Diseño por Consenso por Silencio (*Lazy Consensus*)

Las decisiones de arquitectura (`docs/adr/`) se adoptan por **consenso por silencio**, como en la Apache Software Foundation:

1. La persona que propone abre el ADR con estado **«Propuesta»** y lo anuncia al equipo con un resumen de sus consecuencias y un **plazo mínimo de 48 h**.
2. Cualquier integrante puede objetar o pedir más tiempo; una objeción detiene el plazo hasta resolverla.
3. Si no hay objeciones al vencer el plazo, el estado pasa a **«Aceptada (consenso por silencio, AAAA-MM-DD)»** en el ADR y en `docs/adr/README.md`.
4. Cualquier decisión aceptada así puede reabrirse en cualquier momento.
5. La licencia del repositorio y la entrega oficial requieren el acuerdo expreso de todo el equipo.

---

## 6. Política de Desarrollo Asistido por IA (Copilotos y LLMs)

Conforme a las pautas oficiales de la organización del reto (`ComunidadIA-OS` / SEDIA / Jorge Teixeira):
1. **Uso Autorizado y Transparente:** Se fomenta el uso de asistentes y copilotos de IA (Cursor, Copilot, ChatGPT, Claude Code, etc.) para acelerar la programación, el testeo y la documentación.
2. **Supervisión Humana Obligatoria (*Human-in-the-Loop*):** Las personas contribuidoras son plenamente responsables de cada línea de código incorporada. No se aceptan contribuciones ciegas; el equipo debe comprender, verificar y probar todo el código generado.
3. **Auditoría de Licencias:** Queda prohibido incorporar fragmentos de código sugeridos por asistentes que reproduzcan código con licencias incompatibles con Apache-2.0.
