# Registro de Cambios (Changelog)

Todas las modificaciones notables de este proyecto se documentan en este archivo.
El formato se basa en [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/) y este proyecto se adhiere a [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Sin Publicar] - 2026-10-21

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
