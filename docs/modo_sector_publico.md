<!--
SPDX-FileCopyrightText: 2026 Equipo 1: Attention Is All She Needs (Alba Camiña García, Pilar de la Fuente Diez, Rocío Jiménez Villén)
SPDX-License-Identifier: Apache-2.0
-->

# Modo C: ejecución local permisiva, offline y sector público

Modo de uso previsto para administraciones públicas. Sale del README para mantenerlo breve.

[← Volver al README](../README.md)

---

## 💻 Modo C: Ejecución Local Permisiva, Offline y Sector Público (ENS / Zero Cloud)
> **Para todas las Administraciones Públicas del Estado (RTVE, 3Cat/TV3, EITB, CRTVG, universidades, ministerios, diputaciones y ayuntamientos) sujetas al Esquema Nacional de Seguridad (ENS) y a la Directiva UE 2019/882 de Accesibilidad.**
* **Soberanía Lingüística Cooficial e Inclusividad por Diseño (`ADR-0010`):** Soporte nativo sin traducción intermedia para todas las **lenguas cooficiales del Estado (`es`, `ca`, `gl`, `eu`) + `en`**, e inclusión automática de resumen en **Lectura Fácil (Norma UNE 153101 / WCAG 2.2 AA)** (`resumen_lectura_facil`) compatible con lectores de pantalla (`NVDA`/`JAWS`).
* **Aislamiento de Licencias (estado real):** El pipeline de vídeo actual usa **Ultralytics YOLO (AGPL-3.0)** para detectar personas (`aiasn/model_adapters/person_tracker.py`), **InsightFace** para caras (`face_detector.py`) y **EasyOCR (Apache-2.0)** para rótulos, todos tras los adaptadores de `aiasn/model_adapters/`. En `aiasn/core/compliance.py` existen `CSVPrecomputedAdapter` (ingesta de trazas `.csv` / `.tsv`, separación de procesos) y un esqueleto `PermissiveYOLOXAdapter` (**hoja de ruta: aún no implementa inferencia sobre vídeo**). La sustitución por YOLOX (Apache-2.0) para despliegues B2B es **trabajo de Fase 2**, no está implementada. Nota: el código de InsightFace es MIT, pero sus **pesos preentrenados (p. ej. `buffalo_l`) son solo para investigación no comercial**; un uso comercial exigiría licencia o un modelo alternativo.
* **Círculo Virtuoso de Referentes Femeninos sin Reentrenamiento (*Green AI Flywheel*):** Los rótulos y menciones extraídos por consenso de alta confianza ($p \ge 0{,}80$) enriquecen un diccionario ligero local (`.csv`/`.json`) interoperable con **`Top Rosies Talent`**, **`ReDivIAcat`** y **`tFemTIC`** (`IDEAI-UPC` / `donesCOEINF`) y con **`WikiMujeres` / `Wikidata`**, mejorando el reconocimiento futuro (Cuadrante 4) tanto *offline/batch* como sincronizado sin coste de GPU en reentrenamiento.
* **Extensión en Caliente para las 4 Modalidades (*Shift-Left Parity*):** Diseñado para inyectarse como asistente preventivo en herramientas de **Vídeo** (`OBS Studio`, `DaVinci Resolve`, `Premiere`), **Audio/Podcasts** (`Audacity`, `Audition`), **Imagen/Cartelería** (`Canva`, `Figma`) y **Texto/Prensa** (`WordPress`, `Docs`), y emitir certificados con huella inmutable **`SHA-256`** (`emitir_sello_auditoria`).
