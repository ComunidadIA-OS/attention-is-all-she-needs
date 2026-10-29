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

> **Para evaluar:** comandos, vídeos de la demo y dónde mirar en [Cómo probarlo](#-cómo-probarlo).

---

## 💡 El Giro Epistémico: «Attention Is All She Needs»

El nombre del proyecto rinde homenaje y resignifica el artículo fundacional de la arquitectura Transformer:
> **Vaswani, A. et al. (2017). *Attention Is All You Need*. NeurIPS.**

En las redes neuronales, el mecanismo de **autoatención (*self-attention*)** calcula matemáticamente qué elementos de una secuencia merecen peso y cuáles constituyen ruido contextual.
En la esfera pública y mediática, históricamente los «pesos de atención» se han concedido de forma casi exclusiva a los hombres (reflejado en el escaso **14 % de habla femenina** registrado en el corpus de debate `Àgora` de la UPC), relegando a las mujeres a los márgenes (*aniquilación simbólica*) o a la presencia física muda (*equality-washing*).

**AIASN** proclama que lo que las mujeres necesitan no es condescendencia ni cuotas cosméticas de imagen, sino que el foco de la atención algorítmica, mediática y social se pose con rigor objetivo sobre su **voz efectiva, rol experto y liderazgo real**.

→ Misión social, principios de arquitectura y círculo virtuoso: [fundamentos](./docs/fundamentos_y_principios.md).

---

## 🚀 Cómo probarlo

**Probado en** Ubuntu 24.04 (x86_64): AMD Ryzen 7 7840HS (16 hilos), 30 GB de RAM y GPU NVIDIA RTX 4060 Laptop (8 GB), con Docker 29 y Python 3.13. También en CPU, sin GPU, con 2 núcleos y 6 GB de RAM. En Windows, macOS (Apple Silicon) y Linux ARM las dependencias se resuelven, pero el procesado no se ha probado.

> ⚠️ **Sin GPU funciona, pero es lento.** Un vídeo de 84 s tardó **12 min** con 16 hilos y **45 min** con 2 núcleos y 6 GB de RAM (con GPU, 2 min); casi todo es la detección de personas y el OCR. Con la GPU de arriba, los vídeos de la demo tardan entre 2 y 9 min. La primera vez se suman unos minutos para descargar los modelos (~1,6 GB).

### Requisitos

* **Python 3.11+** con [uv](https://docs.astral.sh/uv/) (recomendado) o pip.
* **ffmpeg**, solo sin Docker (la imagen ya lo trae). Hay versión para Linux, macOS y Windows:
  ```bash
  sudo apt install ffmpeg     # Ubuntu / Debian
  brew install ffmpeg         # macOS
  winget install ffmpeg       # Windows
  ```
* **Token de OVHcloud AI Endpoints**, para la transcripción y el LLM: `cp .env.example .env` y rellena `OVH_AI_ENDPOINTS_ACCESS_TOKEN`. Sin él, el *worker* lo avisa al arrancar y falla al transcribir.
* **Con Docker y GPU**, el **NVIDIA Container Toolkit**. Si no está, el *worker* se lanza en CPU y la API lo avisa en su log. [Guía oficial](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html); en Ubuntu/Debian:
  ```bash
  curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg
  curl -s -L https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list \
  | sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' \
  | sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list
  sudo apt-get update && sudo apt-get install -y nvidia-container-toolkit
  sudo nvidia-ctk runtime configure --runtime=docker && sudo systemctl restart docker
  docker run --rm --gpus all ubuntu nvidia-smi   # debe mostrar tu GPU
  ```

### 1. Tests (1 minuto, sin GPU ni token)

```bash
git clone https://github.com/ComunidadIA-OS/attention-is-all-she-needs.git
cd attention-is-all-she-needs

python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\Activate.ps1
pip install -e ".[dev,api]"
python -m pytest tests/ -v
```

Entre otros, validan:
* `tests/test_contracts.py`: contratos de audio, solape temporal, matriz de 4 cuadrantes *Seeing and Hearing* (Verónica Vilaplana), regla anti-*equality-washing* (Kanter 1977 / Tuchman 1978) y abstención ética ($p < 0{,}80 \rightarrow \text{no\_determinado}$).
* `tests/test_compliance_adapters.py`: no retención de vectores biométricos faciales (`COLUMNAS_BIOMETRICAS_PROHIBIDAS`), denegación de Sello Oficial ante sanciones LISOS o *cherry-picking* (Art. 6 Apache-2.0), rehabilitación corporativa (*Self-Cleaning*, ventana de 3 años) y firma `SHA-256` con ID de supervisión pseudonimizado (`operador_supervision_id`).

### 2. Demo con Docker

```bash
docker compose --profile jobs build   # imágenes de la API, el front y el worker (este ocupa ~12,5 GB: 10–20 min la primera vez)
docker compose up -d                  # almacén S3, API en http://localhost:8000 y front en http://localhost:8080
```

**Sin GPU NVIDIA**, o para ocupar menos disco, construye el *worker* sin CUDA: pon `WORKER_DEVICE=cpu` en `.env` antes del `build` (o `WORKER_DEVICE=cpu docker compose --profile jobs build worker`). No hay que cambiar nada más:

| *Worker* | Imagen | Vídeo de 84 s (`csic_javier_oroz.mp4`) |
|---|---|---|
| `gpu` (por defecto) | ~12,5 GB | 108 s con una RTX 4060 Laptop |
| `cpu` | ~4,4 GB | 708 s (~12 min) con 16 hilos, sin GPU |

Los modelos (~1,6 GB, en el volumen `aiasn-models`) y las versiones de las librerías (`uv.lock`) son los mismos; solo cambia el PyTorch y el ONNX Runtime sin CUDA. En la prueba, los KPIs por género salieron iguales; cambió algún *track* corto sin género determinado y el número de ideas, que varía entre ejecuciones porque el LLM no es determinista. Con la imagen `cpu` en un equipo con GPU, la GPU no se usa.

* El *worker* no queda corriendo: la API arranca un contenedor `aiasn-worker-<video_id>` por vídeo, y lo borra al lanzar el siguiente. Su log: `docker logs aiasn-worker-<video_id>`.
* La API usa el socket de Docker, lo que le da control sobre Docker en esa máquina: no la expongas fuera de tu equipo.
* ¿El puerto 8000 o el 8080 está ocupado? Cámbialos con `API_PORT` y `FRONT_PORT` en `.env`.

### 3. Analizar un vídeo

Los vídeos de la demo, con su licencia y autoría, y la medición de su ejecución (tiempos, tokens y SHA-256), están en [`DATASET_CARD.md`](./DATASET_CARD.md) (1.1 y 1.2).

* **Desde el front** (<http://localhost:8080>): «Elegir vídeo» → «Analizar». Al finalizar el procesado, el panel muestra la matriz de 4 cuadrantes, las métricas de voz y presencia, y el bloque de supervisión humana (*Human-in-the-Loop*, Art. 14 RIA) con botones interactivos **«Asumo / No asumo»** para arbitrar las personas con género dudoso (decisión persistida en la API vía `POST /videos/{id}/supervision`).
* **Desde la API**:
  ```bash
  curl -F file=@video.mp4 http://localhost:8000/videos   # → {"video_id": "video-3f9a"}
  curl http://localhost:8000/videos/video-3f9a           # estado; con "ok", también el resultado
  ```
  Documentación interactiva en <http://localhost:8000/docs>.
* **Si falla** (por ejemplo, si OVHcloud corta la conexión): sin Docker, `uv run python -m aiasn.run_pipelines --video-id <video_id>` sigue desde el paso que falló; con Docker, vuelve a subir el vídeo.

Ejecución sin Docker, trazas del LLM con Langfuse y vídeo anotado: [guía de ejecución avanzada](./docs/guia_ejecucion_avanzada.md).

---

## 🧭 Estado actual y hoja de ruta (a 29/10/2026)

AIASN es un **prototipo** del reto. Esta sección dice con claridad qué hay, qué está en revisión y qué **se pretende hacer y falta**, para que nadie lo confunda con una funcionalidad ya disponible.

**Hecho en v0.1.0 (rama `dev`):** pipelines de audio, vídeo y NLP con extracción abierta; cálculo determinista de métricas (4 cuadrantes, ratio voz/pantalla, TIF en tres estados, alertas); arquitectura *medallion* (bronze, silver, gold) con trazabilidad por vídeo; API FastAPI con procesado de un vídeo cada vez; frontend piloto (HTML/JS) con panel de revisión de personas con género dudoso y botones «Asumo / No asumo» cuyas decisiones se guardan en la API; contenedores con Docker Compose; borrado del vídeo y de sus temporales al terminar; tiempos, tokens del LLM y huellas SHA-256 de los 6 vídeos de la demo medidos en una RTX 4060 Laptop (`DATASET_CARD.md`, 1.2); validación empírica exploratoria de audio sobre el corpus `Àgora` confirmando el 14,61 % de Ground Truth ([`docs/evaluacion_experimental_agora.md`](./docs/evaluacion_experimental_agora.md)); plan de producción en OVHcloud (`ARCHITECTURE.md`); observabilidad opcional de las llamadas al LLM con Langfuse (desactivada por defecto); documentación de gobernanza (ADR, fichas, checklist ético).

**Pendiente principal** (el detalle y el resto de áreas están en la [hoja de ruta](./docs/hoja_de_ruta.md)):

* **Seguridad del despliegue:** HTTPS, autenticación y control de acceso. **Hoy la API y el front no deben exponerse a Internet.**
* **Supervisión humana:** que la revisión recalcule las métricas y condicione el informe, identificar a cada operadora con un pseudónimo propio, vistas por rol e integrar `emitir_sello_auditoria` en la API.
* **Validación:** evaluación completa de extremo a extremo con el pipeline unificado y métricas formales WER/DER en todo el corpus (la calibración exploratoria de componentes de audio y el cálculo exacto del 14,61 % de habla femenina ya se han completado: [informe](./docs/evaluacion_experimental_agora.md)), y medición empírica del ahorro de cómputo frente al análisis continuo a 30 fps.
* **Vistas por rol y capa ciudadana**, y el **frontend alternativo** de la rama `feat/frontend-dashboard` (no integrado).
* **Licencias:** sustituir Ultralytics YOLO (AGPL-3.0) por un adaptador permisivo (YOLOX).
* **Marco legal para terceros:** revisión jurídica del contrato de servicios y de la plantilla del Art. 50.3.

### Alcance de esta entrega

| | |
| :--- | :--- |
| **Dentro del alcance (entrega y demostración del reto)** | Análisis de **vídeos cortos** (probados hasta 5 min 12 s de audio), subidos de uno en uno · métricas **agregadas** de presencia y voz de mujeres y hombres · género **atribuido o percibido** con abstención por debajo de 0,80 y revisión humana de los casos dudosos · ejecución en local o con Docker Compose en una **red controlada** · datos de prueba públicos con licencia abierta |
| **Fuera del alcance (hoja de ruta o decisión futura)** | Servicio multiusuario o expuesto a Internet · producción con terceros y contrato de servicios (solo borrador) · evaluación, selección o vigilancia de personas · identificación biométrica · análisis masivo de canales o *scraping* · vídeos largos · certificación pública con el Sello · tratamiento de **menores** o de categorías especiales de datos · garantías de disponibilidad, tiempos de respuesta o exactitud |
| **Límites declarados** | Prototipo: los resultados son orientativos y exigen revisión humana · los tiempos y tokens están medidos en una sola máquina (RTX 4060 Laptop); el ahorro de cómputo frente a analizarlo todo y el coste de producción son estimaciones · la clasificación normativa del sistema está en revisión ([ADR-0012](./docs/adr/0012-marco-normativo-omnibus-digital-y-proyecto-de-ley.md)) · los vídeos de calibración interna no se redistribuyen ([`DATASET_CARD.md`](./DATASET_CARD.md), 1.1) |

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
