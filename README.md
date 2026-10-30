<!--
SPDX-FileCopyrightText: 2026 Equipo 1: Attention Is All She Needs (Alba Camiña García, Pilar de la Fuente Diez, Rocío Jiménez Villén)
SPDX-License-Identifier: Apache-2.0
-->

# Attention Is All She Needs (AIASN)

> **Auditoría de paridad, protagonismo y perspectiva de género en medios audiovisuales mediante Inteligencia Artificial Abierta.**
> Proyecto desarrollado para el **Reto «Mujeres por la IA Abierta»** convocado por la **Secretaría de Estado de Digitalización e Inteligencia Artificial (SEDIA)**, la **Comunidad IA de Código Abierto (`ComunidadIA-OS`)**, el **IDEAI-UPC**, **donesCOEINF** y **OVHcloud**.

[![License: Apache-2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](./LICENSE)
[![REUSE status](https://api.reuse.software/badge/github.com/ComunidadIA-OS/attention-is-all-she-needs)](https://api.reuse.software/info/github.com/ComunidadIA-OS/attention-is-all-she-needs)
[![Python: 3.11+](https://img.shields.io/badge/Python-3.11%2B-blue.svg)](./pyproject.toml)
[![Open Source AI](https://img.shields.io/badge/Open%20Source%20AI-Compliant-brightgreen.svg)](https://opensource.org/ai)
[![EU AI Act](https://img.shields.io/badge/EU%20AI%20Act-Art.%2050%20Compliant-success.svg)](./ETHICS_CHECKLIST.md)

---
<img width="964" height="902" alt="image" src="https://github.com/user-attachments/assets/34be94c4-8475-474e-aa3c-83689edce1ed" />

## 💡 El Giro Epistémico: «Attention Is All She Needs»

El nombre del proyecto rinde homenaje y resignifica el artículo fundacional de la arquitectura Transformer:
> **Vaswani, A. et al. (2017). *Attention Is All You Need*. NeurIPS.**

En las redes neuronales, el mecanismo de **autoatención (*self-attention*)** calcula matemáticamente qué elementos de una secuencia merecen peso y cuáles constituyen ruido contextual.
En la esfera pública y mediática, históricamente los «pesos de atención» se han concedido de forma casi exclusiva a los hombres (reflejado en el escaso **14 % de habla femenina** registrado en el corpus de debate `Àgora` de la UPC), relegando a las mujeres a los márgenes (*aniquilación simbólica*) o a la presencia física muda (*equality-washing*).

**AIASN** proclama que lo que las mujeres necesitan no es condescendencia ni cuotas cosméticas de imagen, sino que el foco de la atención algorítmica, mediática y social se pose con rigor objetivo sobre su **voz efectiva, rol experto y liderazgo real**.

→ Misión social, principios de arquitectura y círculo virtuoso: [fundamentos](./docs/fundamentos_y_principios.md).

---

## 🚀 Set up

> [!NOTE] 
> Probado en Ubuntu 24.04 (x86_64): AMD Ryzen 7 7840HS (16 hilos), 30 GB de RAM y GPU NVIDIA RTX 4060, Docker 29 y Python 3.13. También en CPU, sin GPU, con 2 núcleos y 6 GB de RAM. En Windows, macOS (Apple Silicon) y Linux ARM las dependencias se resuelven, pero el procesado no se ha probado.

> [!WARNING]
> **También funciona Sin GPU, pero es lento.** Un vídeo de 84 s tardó **12 min** con 16 hilos y **45 min** con 2 núcleos y 6 GB de RAM; con GPU, 2 min. Con GPU, los vídeos de la demo tardan entre 2 y 9 min. La primera vez tarda un poco más porque se descargan los modelos (~1,6 GB).

### Quick Start

1. Clona el repositorio y pon tu token de OVHcloud AI Endpoints (se necesita para transcripción y LLMs) en `.env`:
   ```bash
   git clone https://github.com/ComunidadIA-OS/attention-is-all-she-needs.git
   cd attention-is-all-she-needs
   cp .env.example .env   # rellena OVH_AI_ENDPOINTS_ACCESS_TOKEN
   ```
2. Los vídeos originales de la demo, con su licencia y autoría, están en [`DATASET_CARD.md`](DATASET_CARD.md) (1.1). Los clips `.mp4` exactos se pueden descargar de [Google Drive](https://drive.google.com/drive/folders/1e5kBlNMkaiqmWc0NBrCf-ULc3tC7L035?usp=sharing).
3. Tests documentados en [`TESTING.md`](TESTING.md).
   ```bash
   uv sync --extra dev # crea o sincroniza el entorno virtual con las dependencias de .toml
   uv run pytest tests/
   ```

### Con Docker

Con GPU NVIDIA hace falta el **NVIDIA Container Toolkit** (consulta la [guía oficial](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html) para instalarlo). Sin él, el contenedor de *worker* se lanza en CPU. En Ubuntu/Debian:
```bash
curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg
curl -s -L https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list \
| sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' \
| sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list
sudo apt-get update && sudo apt-get install -y nvidia-container-toolkit
sudo nvidia-ctk runtime configure --runtime=docker && sudo systemctl restart docker
docker run --rm --gpus all ubuntu nvidia-smi   # debería mostrar tu GPU
```

> [!WARNING]
> **Sin GPU NVIDIA**, o para ocupar menos disco, pon `WORKER_DEVICE=cpu` en `.env` antes del `build`.

1. Construye las imágenes y arranca la demo:
   ```bash
   docker compose --profile jobs build   # 10–20 min la primera vez
   docker compose up -d                  # front en http://localhost:8080 y API en http://localhost:8000
   ```
   
   Por defecto, el frontend accesible en http://localhost:8080 y API en http://localhost:8000 (documentación interactiva de la API en <http://localhost:8000/docs>)
   
   > [!NOTE]
   > ¿El puerto 8000 o el 8080 está ocupado? Puedes cambiarlos con `API_PORT` y `FRONT_PORT` en `.env`.


3. **Configuración de observabilidad de LLMs con Langfuse (opcional).** Langfuse guarda cada llamada al LLM: prompt, respuesta, modelo, duración y tokens. En `.env` completa:
   ```env
   LANGFUSE_ENABLED=true
   LANGFUSE_PUBLIC_KEY=pk-lf-...          # inventadas: Langfuse crea el proyecto con estas claves al arrancar
   LANGFUSE_SECRET_KEY=sk-lf-...
   LANGFUSE_INIT_USER_EMAIL=admin@aiasn.local
   LANGFUSE_INIT_USER_PASSWORD=...        # tu usuario de la web de Langfuse
   ```
   Arranca con `docker compose --profile langfuse up -d` y abre <http://localhost:3000> -> proyecto AIASN piloto -> *Sessions*: una sesión por vídeo. Si las claves no coinciden, el *worker* lo avisa en un log y sigue sin trazabilidad.

### Sin Docker

Necesitas [uv](https://docs.astral.sh/uv/), que instala Python si hace falta, y **ffmpeg**:
```bash
sudo apt install ffmpeg     # Ubuntu / Debian
brew install ffmpeg         # macOS
winget install ffmpeg       # Windows
```

1. Instala y arranca la API y el front:
   ```bash
   uv sync --extra worker --extra api    # ~7 GB (PyTorch y CUDA)
   uv run uvicorn aiasn.api.app:create_app --factory --port 8000
   uv run python -m http.server 8080 --directory frontend-piloto   # front en http://localhost:8080/?api=http://localhost:8000
   ```
   La API lanza el *worker* como proceso y guarda el lake en `data/`. Si tienes construida la imagen `aiasn-worker`, la usa: fuérzalo con `API__LAUNCHER=process`.
2. O procesa un vídeo sin la API. Si falla, `--video-id <video_id>` sigue desde el paso que falló:
   ```bash
   uv run python -m aiasn.run_pipelines --file video.mp4
   ```
3. **Vídeo anotado**, para comprobar el resultado a ojo: una caja por persona con `P<id> | F/M`, una caja verde *speaking* en la cara de quien habla y, en amarillo, los textos del OCR. Usa los fotogramas que quedan en `tmp/<video_id>/video/frames` después de procesar el vídeo:
   ```bash
   uv run python scripts/annotate_video.py <video_id>   # → tmp/<video_id>/video/annotated.mp4
   ```

### 💻 Modo C: Ejecución Local Permisiva, Offline y Sector Público (ENS / Art. 157 LRJSP / Zero Cloud)
> **Para todas las Administraciones Públicas del Estado (RTVE, 3Cat/TV3, EITB, CRTVG, universidades, ministerios, diputaciones y ayuntamientos) sujetas al Esquema Nacional de Seguridad (ENS), al Art. 157 de la Ley 40/2015 (reutilización de sistemas) y a la Directiva UE 2019/882 de Accesibilidad.**
* **Soberanía Lingüística Cooficial e Inclusividad por Diseño (`ADR-0010`):** Soporte nativo sin traducción intermedia para todas las **lenguas cooficiales del Estado (`es`, `ca`, `gl`, `eu`) + `en`**, e inclusión automática de resumen en **Lectura Fácil (Norma UNE 153101 / WCAG 2.2 AA)** (`resumen_lectura_facil`) compatible con lectores de pantalla (`NVDA`/`JAWS`).
* **Aislamiento de Licencias (estado real):** El pipeline de vídeo actual usa **Ultralytics YOLO (AGPL-3.0)** para detectar personas (`aiasn/model_adapters/person_tracker.py`), **InsightFace** para caras (`face_detector.py`) y **EasyOCR (Apache-2.0)** para rótulos, todos tras los adaptadores de `aiasn/model_adapters/`. En `aiasn/core/compliance.py` existen `CSVPrecomputedAdapter` (ingesta de trazas `.csv` / `.tsv`, separación de procesos) y un esqueleto `PermissiveYOLOXAdapter` (**hoja de ruta: aún no implementa inferencia sobre vídeo**). La sustitución por YOLOX (Apache-2.0) para despliegues B2B es **trabajo de Fase 2**, no está implementada. Nota: el código de InsightFace es MIT, pero sus **pesos preentrenados (p. ej. `buffalo_l`) son solo para investigación no comercial**; un uso comercial exigiría licencia o un modelo alternativo.
* **Círculo Virtuoso de Referentes Femeninos sin Reentrenamiento (*Green AI Flywheel*):** Los rótulos y menciones extraídos por consenso de alta confianza ($p \ge 0{,}80$) enriquecen un diccionario ligero local (`.csv`/`.json`) interoperable con **`Top Rosies Talent`**, **`ReDivIAcat`** y **`tFemTIC`** (`IDEAI-UPC` / `donesCOEINF`) y con **`WikiMujeres` / `Wikidata`**, mejorando el reconocimiento futuro (Cuadrante 4) tanto *offline/batch* como sincronizado sin coste de GPU en reentrenamiento.
* **Extensión en Caliente para las 4 Modalidades (*Shift-Left Parity*):** Diseñado para inyectarse como asistente preventivo en herramientas de **Vídeo** (`OBS Studio`, `DaVinci Resolve`, `Premiere`), **Audio/Podcasts** (`Audacity`, `Audition`), **Imagen/Cartelería** (`Canva`, `Figma`) y **Texto/Prensa** (`WordPress`, `Docs`), y emitir certificados con huella inmutable **`SHA-256`** (`emitir_sello_auditoria`).

Seguimiento día a día en el [tablero del equipo](https://github.com/users/ewigkeitt-cloud/projects/1).

---

## ⚡ Algoritmos Verdes (*Green AI*) y Eficiencia

* **Muestreo Temporal `STRIDE`:** El vídeo se extrae a 25 fps y se buscan caras en todos los fotogramas, porque el detector de hablante activo (TalkNet) los necesita; las personas se detectan en 1 de cada 4 fotogramas y los rótulos a 1 fps. El ahorro frente a analizarlo todo está pendiente de medir.
* **Optimización Hardware:** Diseñado para ejecutarse en las instancias $2 \times \text{NVIDIA V100}$ de OVHcloud con precisión de coma flotante media **`torch.float16`**.
* **Arquitectura *Split Edge-to-Cloud* (ahorro pendiente de medir):** El vídeo pesado (.mp4) se procesa en local (con ficheros temporales en `tmp/`, véase `ETHICS_CHECKLIST.md`, punto 3.5). Hacia la nube (AI Endpoints de OVHcloud) viajan únicamente el **audio extraído** (transcripción) y **texto** (tareas de NLP con LLM), y al almacén solo llegan tablas de resultados, lo que reduce el almacenamiento y la transferencia frente a subir el vídeo.
* **Coste de Sostenibilidad:** en medición con los vídeos de la demo; por ahora solo es oficial el precio de Whisper en OVHcloud, **≈0,15 € por hora de audio**.

→ El círculo virtuoso de referentes está explicado en [fundamentos](./docs/fundamentos_y_principios.md) y en el [glosario](./GLOSSARY.md).

→ Uso previsto en el sector público (ENS, lenguas cooficiales, aislamiento de licencias): [Modo C](./docs/modo_sector_publico.md).

---

## ⚖️ Declaración de Transparencia (EU AI Act - Art. 50)

En cumplimiento del **Reglamento (UE) 2024/1689 (Reglamento Europeo de IA)** y de la obligación legal vigente desde agosto de 2026:
* Este prototipo utiliza modelos de inteligencia artificial abiertos: transcripción (`whisper-large-v3`), detección y seguimiento de personas (`YOLO11m-pose` y BoT-SORT), caras (`InsightFace`), hablante activo (`TalkNet-ASD`), lectura de rótulos (`EasyOCR`), género percibido por imagen (`MiVOLO v2`) y por voz (`Common-Voice-Gender-Detection`), sesgo de palabras (`word2vec`) y modelos de lenguaje alojados en OVHcloud (`Llama-3.3-70B-Instruct` y `gpt-oss-120b`). Lista completa, licencias y límites en [`MODEL_CARD.md`](./MODEL_CARD.md).
* **Uso de Asistentes y Copilotos de IA en el Desarrollo:** Conforme a las directrices de la Oficina Técnica de Código Abierto (`ComunidadIA-OS` / Jorge Teixeira) y la tecnoética de SEDIA, se declara explícitamente el uso de asistentes inteligentes de código y documentación (copilotos de IA) como herramientas de aceleración y soporte metodológico. El 100 % de la arquitectura, el código generado, las decisiones de diseño y la compatibilidad de licencias han sido supervisados, comprendidos, validados y auditados directamente por las desarrolladoras del equipo (*Human-in-the-Loop* en el ciclo de ingeniería).
* El sistema **no toma decisiones automatizadas vinculantes ni elabora perfiles biométricos individuales**. Su salida constituye una propuesta analítica sujeta a supervisión humana preceptiva (*Human-in-the-Loop*).
* Los datos de prueba utilizados en fase de desarrollo proceden de corpus autorizados por la UPC (`Àgora`, datos de voz), de vídeos con licencia abierta (CC BY-SA y CC BY; véase `DATASET_CARD.md`, 1.1) y, solo para calibración interna y sin redistribuirlos, de grabaciones públicas **sin permiso expreso** de sus titulares, analizadas en local al amparo de la excepción de Minería de Textos y Datos del **Art. 67 del Real Decreto-ley 24/2021** (amparo pendiente de validar).

---

## 👥 Equipo 1: «Attention Is All She Needs»
* **Rocío Jiménez Villén** ([@rjvillen](https://github.com/rjvillen)) — Arquitectura de backend (FastAPI, Docker y Medallion), orquestación de pipelines, procesamiento NLP, embeddings semánticos y convocatoria de reuniones de sincronización.
* **Pilar de la Fuente Diez** ([@pilarvolatixia-cloud](https://github.com/pilarvolatixia-cloud)) — Interlocución institucional oficial, modelo de negocio B2B (EIPs / Ley 2/2024 / CSRD), mitigación de riesgos de licencia (AGPL), prototipado de frontend y defensa presencial.
* **Alba Camiña García** ([@ewigkeitt-cloud](https://github.com/ewigkeitt-cloud)) — Giro epistémico de AIASN, motor determinista y TIF (`fusion.py`), gobernanza ética y regulatoria (RIA / Sandbox), gestión ágil del repositorio (GitHub Project, issues e hitos), arquitectura documental SSoT y diseño de innovación (Constelación, Capa Ciudadana y Shift-Left).

---

## 📚 Documentación

* 📚 [**Índice completo de documentación**](./docs/indice_de_documentacion.md) · 📖 [**Bibliografía del proyecto**](./docs/bibliografia.md)
* 🖥️ [**Especificación del dashboard y supervisión humana**](./docs/especificacion_alertas_dashboard_y_hitl.md): alertas, TIF, vistas por rol y pantalla «Asumo / No asumo».
* ⚖️ [**Marco normativo y mercado**](./docs/marco_normativo_y_mercado.md) · 🏛️ [**Encuadramiento legal y delimitación de riesgo**](./docs/clasificacion_legal_y_marco_normativo.md)
* 🏗️ [**Arquitectura técnica y pipelines**](./ARCHITECTURE.md) · 📐 [**Decisiones de arquitectura (ADR)**](./docs/adr/README.md)
* 👥 [**Evidencias de trabajo en equipo**](./docs/evidencias_trabajo_en_equipo.md)
* 🔬 [**Evaluación experimental sobre Àgora (UPC)**](./docs/evaluacion_experimental_agora.md): validación de componentes de audio, diarización y Ground Truth del 14,61 %.
* 📖 [**GLOSSARY.md**](./GLOSSARY.md) · 📋 [**ETHICS_CHECKLIST.md**](./ETHICS_CHECKLIST.md) · 🧪 [**TESTING.md**](./TESTING.md) · 🤖 [**MODEL_CARD.md**](./MODEL_CARD.md) · 📊 [**DATASET_CARD.md**](./DATASET_CARD.md)

---

## 📄 Licencia y Conformidad REUSE

Este proyecto está licenciado bajo los términos de la **Licencia Apache 2.0**, cumpliendo estrictamente las directrices formativas de la Oficina Técnica de `ComunidadIA-OS` (Jorge Teixeira) y el estándar [REUSE Software](https://reuse.software/) de la *Free Software Foundation Europe* (FSFE):

* **Identificador SPDX:** `SPDX-License-Identifier: Apache-2.0`
* **Directorio de Licencias:** El texto íntegro y canónico se aloja en [`LICENSES/Apache-2.0.txt`](./LICENSES/Apache-2.0.txt) y en el archivo raíz [`LICENSE`](./LICENSE).
* **Aviso Formal de Copyright:**
```text
SPDX-FileCopyrightText: 2026 Equipo 1: Attention Is All She Needs
(Alba Camiña García, Pilar de la Fuente Diez, Rocío Jiménez Villén)
SPDX-License-Identifier: Apache-2.0
```
* **Aislamiento y Compatibilidad de Dependencias:** El núcleo determinista de métricas (`aiasn/core/`) es código propio bajo Apache-2.0. La detección de personas del prototipo depende de **Ultralytics YOLO (AGPL-3.0)**, aislada en el adaptador `person_tracker.py`; para clientes B2B cerrados se prevé sustituirla por YOLOX (Apache-2.0) y revisar la licencia de los pesos faciales (InsightFace: código MIT, pesos de uso no comercial). Esta sustitución es **hoja de ruta**, no funcionalidad actual. El consumo remoto por API en los AI Endpoints de OVHcloud no introduce dependencias copyleft en el cliente.
