<!--
SPDX-FileCopyrightText: 2026 Equipo 1: Attention Is All She Needs (Alba Camiña García, Pilar de la Fuente Diez, Rocío Jiménez Villén)
SPDX-License-Identifier: Apache-2.0
-->

# Registro de Cambios (Changelog)

Todas las modificaciones notables de este proyecto se documentan en este archivo.
El formato se basa en [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/) y este proyecto se adhiere a [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Sin Publicar] - 2026-10-25

### Añadido
* **Conformidad REUSE (FSFE), Aislamiento de Licencias B2B y Sello Ético Criptográfico (`#17`):**
  * Incorporación de [`LICENSES/Apache-2.0.txt`](./LICENSES/Apache-2.0.txt), plantilla [`.env.example`](./.env.example) y cabeceras `SPDX-FileCopyrightText` / `SPDX-License-Identifier: Apache-2.0` en todos los archivos del repositorio conforme al estándar [`reuse.software`](https://reuse.software/).
  * Separación estricta de perfiles en [`pyproject.toml`](./pyproject.toml): núcleo determinista `dependencies` 100 % permisivo (`pandas`, `pydantic`, `requests`), perfil B2B `[permissive-vision]` (`YOLOX` ONNX + `InsightFace` + `EasyOCR` sin AGPL) y perfil aislado `[notebooks-research]` para cuadernos experimentales.
  * Nuevo módulo [`aiasn/core/compliance.py`](./aiasn/core/compliance.py) con `CSVPrecomputedAdapter`, un esqueleto de `PermissiveYOLOXAdapter` (hoja de ruta), purga automática de vectores biométricos en RAM (*Zero Facial Retention*), modelo `ElegibilidadEticaEntidad` y función `emitir_sello_auditoria()` con huella inmutable `SHA-256` e identificador de supervisión pseudonimizado (`operador_supervision_id`).
  * Nuevo [`CODE_OF_CONDUCT.md`](./CODE_OF_CONDUCT.md) adaptado a medida con Estatuto de Propósito Social y Democratización de la Validación (Art. 1), Círculo Virtuoso de Referentes Femeninos (`Top Rosies Talent` / `ReDivIAcat` de IDEAI-UPC y `WikiMujeres`) por consenso automático ($p \ge 0{,}80$) sin reentrenamiento de GPU (Art. 1.3), Cláusula Anti-Lavado de Cara bajo el Art. 6 de Apache-2.0 con ventana de 3 años y vía de Rehabilitación Activa *Self-Cleaning* (Art. 3), y extensión en caliente para las 4 modalidades: Vídeo, Audio, Imagen y Texto (Art. 4.2).
  * Glosario maestro [`GLOSSARY.md`](./GLOSSARY.md) con los 25 elementos clave de la solución, modelo de amenazas frente a ataques adversarios en [`SECURITY.md`](./SECURITY.md) (Art. 15 RIA / OWASP ML/LLM) y guardarraíles para agentes de código en [`AGENTS.md`](./AGENTS.md).
  * Suite de pruebas [`tests/test_compliance_adapters.py`](./tests/test_compliance_adapters.py) verificando la purga biométrica, la denegación de sello ante sanciones o *cherry-picking*, la rehabilitación *Self-Cleaning* y la firma `SHA-256`.

---

## [0.1.1] - 2026-10-21

### Añadido
* **Gobernanza de Código Abierto:**
  * Inclusión del estándar de Código de Conducta ([`CODE_OF_CONDUCT.md`](./CODE_OF_CONDUCT.md)) basado en Contributor Covenant 2.1.
  * Guía de contribución comunitaria ([`CONTRIBUTING.md`](./CONTRIBUTING.md)) con normas de ramas, commits convencionales y coautoría paritaria.
  * Política de reporte responsable de seguridad y privacidad ([`SECURITY.md`](./SECURITY.md)).
  * Ficha de modelos abiertos ([`MODEL_CARD.md`](./MODEL_CARD.md)) y procedencia de datos ([`DATASET_CARD.md`](./DATASET_CARD.md)).
  * Configuración de empaquetado reproducible en [`pyproject.toml`](./pyproject.toml) con dependencias modulares (`core`, `audio`, `video`, `gpu`).

---

## [0.1.0] - 2026-10-21

### Añadido
* **Pipeline de Audio y Diarización (Rama `feat/audio-pipeline`):**
  * Script de inferencia y diarización [`scripts/test_audio_ovh.py`](./scripts/test_audio_ovh.py) integrado con AI Endpoints de OVHcloud (`whisper-large-v3`, `diarize=true`).
  * Validación empírica sobre audio real del corpus *Àgora* (TV3 / UPC) detectando 3 turnos de palabra diferenciados.
  * Función de exportación automática a formato tabular canónico (`tiempo_i`, `tiempo_f`, `transcripcion`, `genero_inferido`).
  * Hook preparado para el clasificador acústico `prithivMLmods/Common-Voice-Gender-Detection` con salvaguarda ética de abstención (`no_determinado`).
* **Pipeline de Visión, Re-ID y OCR (Rama `feat/video-pipeline-notebooks`):**
  * Cuadernos de experimentación de visión por computador con modelo `miVOLO` para inferencia visual de género.
  * Módulo de reidentificación de personas (Re-ID) para tracking temporal en vídeos multiescena (*podcast de Karina Gibert / CSIC*).
  * Extracción de rótulos con EasyOCR para asignación de cargos y nombres a personas en pantalla.
  * Cálculo de KPIs visuales: centralidad media, área media y porcentaje de tiempo en pantalla.
