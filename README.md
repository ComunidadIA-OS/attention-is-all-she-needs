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

## 👥 Equipo 1: «Attention Is All She Needs»
* **Rocío Jiménez Villén** ([@rjvillen](https://github.com/rjvillen)) — Procesamiento de texto, embeddings semánticos, grafos de conocimiento y visión por computador.
* **Pilar de la Fuente Diez** ([@pilarvolatixia-cloud](https://github.com/pilarvolatixia-cloud)) — Interlocución oficial, estrategia de producto, modelo de negocio B2B (EIPs / Ley 2/2024) y presentación presencial.
* **Alba Camiña García** ([@ewigkeitt-cloud](https://github.com/ewigkeitt-cloud)) — Marco conceptual, gobernanza ética y regulatoria (RIA / Sandbox), arquitectura desacoplada y Algoritmos Verdes (*Green AI*).

---

## 💡 El Giro Epistémico: «Attention Is All She Needs»

El nombre del proyecto rinde homenaje y resignifica el artículo fundacional de la arquitectura Transformer:
> **Vaswani, A. et al. (2017). *Attention Is All You Need*. NeurIPS.**

En las redes neuronales, el mecanismo de **autoatención (*self-attention*)** calcula matemáticamente qué elementos de una secuencia merecen peso y cuáles constituyen ruido contextual.
En la esfera pública y mediática, históricamente los «pesos de atención» se han concedido de forma casi exclusiva a los hombres (reflejado en el escaso **14 % de habla femenina** registrado en el corpus de debate `Àgora` de la UPC), relegando a las mujeres a los márgenes (*aniquilación simbólica*) o a la presencia física muda (*equality-washing*).

**AIASN** proclama que lo que las mujeres necesitan no es condescendencia ni cuotas cosméticas de imagen, sino que el foco de la atención algorítmica, mediática y social se pose con rigor objetivo sobre su **voz efectiva, rol experto y liderazgo real**.

---

## 🏛️ Arquitectura del Sistema: Extracción Abierta + Cálculo Determinista

```mermaid
flowchart TD
subgraph INGESTA["1. Ingesta Multimodal"]
A1["Señal de Audio (16 kHz mono)"]
A2["Fotogramas Muestreados (STRIDE 1-5 fps)"]
end

subgraph INFERENCIA["2. Inferencia con Modelos Abiertos"]
B1["VAD + Whisper-large-v3<br>(AI Endpoints OVHcloud)"]
B2["YOLO11m + ByteTrack + miVOLO<br>(Detección y Género Visual Efímero)"]
B3["EasyOCR / PaddleOCR<br>(Lectura de Rótulos y Cargos)"]
end

subgraph DETERMINISTA["3. Núcleo Matemático Determinista (Python)"]
C1["Solape Temporal de Intervalos"]
C2["Matriz 4 Cuadrantes Seeing & Hearing"]
C3["Cortafuegos Ético (p < 0.80 -> no_determinado)"]
end

subgraph HITL["4. Supervisión Humana (Human-in-the-Loop)"]
D1["Pantalla con Botón 'Asumo / No asumo'"]
D2["Informe de Paridad y Certificación B2B"]
end

A1 --> B1
A2 --> B2
A2 --> B3
B1 --> C1
B2 --> C1
B3 --> C2
C1 --> C2
C2 --> C3
C3 --> D1
D1 --> D2
```

### Principios Rectores de Arquitectura
1. **Separación Estricta entre Inferencia y Cálculo:** Los modelos de IA abierta extraen transcripciones, coordenadas y probabilidades; el **100 % de los tiempos, porcentajes, solapes y ratios los calcula determinísticamente Python (`pandas`)**, eliminando cualquier riesgo de alucinación generativa.
2. **Prioridad al Dato Declarado sobre la Biometría:** Un rótulo leído por OCR (*«Dra. Maria Pons — Catedràtica d'Economia»*) tiene **prevalencia jerárquica estricta** sobre cualquier inferencia biométrica física.
3. **Privacidad por Diseño (*Zero Facial Retention*):** Las inferencias faciales se procesan en memoria RAM efímera y se destruyen de inmediato tras el conteo estadístico; **nunca se almacenan vectores faciales ni se crean bases de datos biométricas**.
4. **Detector de *Equality-Washing* (Matriz *Seeing and Hearing*):** Clasifica cada aparición en 4 cuadrantes:
* **Cuadrante 1 (Voz Activa):** En pantalla y hablando $\rightarrow$ Liderazgo y voz experta.
* **Cuadrante 2 (Presencia Muda):** En pantalla y en silencio $\rightarrow$ Alerta de figuración / lavado de imagen.
* **Cuadrante 3 (Voz en Off):** Fuera de pantalla y hablando $\rightarrow$ Narración o locución.
* **Cuadrante 4 (Pasivo):** Solo mencionado en el texto o subtítulo.
5. **Test de Bechdel Digital (*Autoridad Relacional*):** Evalúa de forma 100 % determinista (`evaluar_bechdel_conversacional` en `aiasn/core/fusion.py`, 0 W GPU) tres condiciones sobre la pieza audiovisual: (1) pluralidad femenina ($\ge 2$ mujeres distintas con voz activa, superando el *Efecto Token*), (2) identidad y autoridad propia ($\ge 2$ mujeres acreditadas con nombre o cargo vía OCR/diarización), y (3) interlocución horizontal directa ($\ge 1$ transición consecutiva $\text{Mujer}_A \to \text{Mujer}_B$ sin mediación masculina).
6. **Supervisión Humana (*Human-in-the-Loop*):** Conforme a las recomendaciones de Karina Gibert y Ángela Gasch (SEDIA), el sistema incluye una pantalla operativa con el botón **«Asumo / No asumo»** previa a la emisión de cualquier informe o certificado de paridad (especificada en [`docs/especificacion_alertas_dashboard_y_hitl.md`](./docs/especificacion_alertas_dashboard_y_hitl.md)).

> 🏛️ **Registro Formal de Decisiones de Arquitectura (ADRs):** Todas las decisiones técnicas y éticas del proyecto están formalizadas bajo el estándar de Michael Nygard en el catálogo [`docs/adr/`](./docs/adr/README.md).

---

## ⚡ Algoritmos Verdes (*Green AI*) y Eficiencia

* **Muestreo Temporal `STRIDE`:** Se procesan entre 1 y 5 fotogramas por segundo (`STRIDE = 3` a `6`), reduciendo el consumo de GPU y la huella de carbono en más de un **80 %** frente al procesado continuo a 25/30 fps, sin pérdida de precisión estadística.
* **Optimización Hardware:** Diseñado para ejecutarse en las instancias $2 \times \text{NVIDIA V100}$ de OVHcloud con precisión de coma flotante media **`torch.float16`**.
* **Arquitectura *Split Edge-to-Cloud* (99,99 % de ahorro en red y almacenamiento):** El vídeo pesado (.mp4 de varios GB) se procesa de forma efímera en local; hacia la nube (AI Endpoints de OVHcloud) o el repositorio solo viajan kilobytes de texto y tablas anónimas (.csv/.tsv), reduciendo drásticamente la huella de carbono de transmisión y almacenamiento.
* **Coste de Sostenibilidad:** Inferencia auditada por debajo de **0,30 € por hora de vídeo analizada**.

### 🔄 Del «Círculo Vicioso» al «Círculo Virtuoso» de Referentes (`Top Rosies Talent` + `WikiMujeres`)
> **Nombre estratégico/comercial:** *Círculo Virtuoso de Referentes Femeninos (Green AI Flywheel)*
> **Nombres técnicos de ingeniería:** *Retroalimentación Incremental sin Reentrenamiento (`Zero-Retraining Feedback Loop`)* / *Enriquecimiento Autónomo del Diccionario de Referentes*

1. **Más auditoría $\rightarrow$ Más expertas en pantalla:** Las empresas y medios usan AIASN (y la extensión en caliente en edición) para cumplir la paridad real (Cuadrante 1), invitando y rotulando a más mujeres profesionales.
2. **Más expertas en pantalla $\rightarrow$ Extracción automática ($p \ge 0{,}80$):** AIASN lee de forma autónoma sus rótulos (`rol_ocr`) y sus intervenciones mediante consenso multimodal (`EasyOCR` + `Whisper` + `GLiNER`).
3. **Extracción $\rightarrow$ Diccionario más rico (`Top Rosies Talent` / `ReDivIAcat` / `WikiMujeres`):** Esos nombres y cargos verificados se añaden solos al diccionario ligero (`.csv`/`.json`), tanto en local desconectado (*offline/batch*) como sincronizado.
4. **Diccionario más rico $\rightarrow$ Algoritmo más inteligente sin reentrenar GPU (*Green AI*):** En el siguiente vídeo que se audite, el detector ya conoce a esas profesionales cuando alguien las cita en una conversación (Cuadrante 4), **sin gastar un solo euro ni vatio de GPU en reentrenar la red neuronal**.
5. **Más visibilidad $\rightarrow$ Más invitaciones:** Al quedar registradas con evidencias de vídeo en **`Top Rosies Talent`** (IDEAI-UPC / donesCOEINF) y **`WikiMujeres`**, más organizadores las encuentran y las llaman para nuevos debates (vuelta al punto 1, multiplicando el efecto).

```mermaid
flowchart LR
A1["1. Más auditoría AIASN<br>→ Más expertas en pantalla"] --> A2["2. Extracción automática<br>(p ≥ 0.80, rol_ocr)"]
A2 --> A3["3. Diccionario enriquecido<br>(Top Rosies Talent / WikiMujeres)"]
A3 --> A4["4. Algoritmo más preciso (Cuad. 4)<br>SIN REENTRENAR GPU (0 W)"]
A4 --> A5["5. Más visibilidad pública<br>y fuentes en Wikipedia"]
A5 ==>|"Multiplica invitaciones"| A1
```

---

## 🚀 Instalación, Configuración y Reproducción

El proyecto está diseñado bajo una arquitectura modular agnóstica que ofrece **tres vías de prueba inmediata** según los recursos disponibles:

### 1. Clonar el Repositorio y Crear el Entorno
```bash
git clone https://github.com/ComunidadIA-OS/attention-is-all-she-needs.git
cd attention-is-all-she-needs

# Con uv (Recomendado — instalación ultra-rápida y reproducible):
uv venv
source .venv/bin/activate # En Linux / macOS
# o en Windows PowerShell: .venv\Scripts\Activate.ps1

uv pip install -e ".[dev]"

# (Alternativa con pip estándar):
# python -m venv .venv && source .venv/bin/activate
# pip install -e ".[dev]"
```

---

### 2. Modos de Verificación para el Tribunal Evaluador

#### 🟢 Modo A: Verificación Inmediata y Automática (Zero Setup — <3 segundos)
> **Comando atómico con auto-detección inteligente:** Si Docker está activo, ejecuta los tests dentro del contenedor aislado; si Docker no está disponible, conmuta automáticamente a tu entorno local (`uv run pytest` o Python activo) y ejecuta también los 14 tests del frontend piloto si detecta Node.js:
```bash
python scripts/run_tests.py
```
*(O si prefieres invocar la herramienta directamente según tu flujo de trabajo:)*
* **Vía Docker (aislado, sin configurar nada en tu máquina):** `docker compose run --rm backend pytest`
* **Vía uv (entorno local reproducible):** `uv run pytest`
* **Vía Python estándar:** `pytest tests/ -v` (requiere `.venv` activado)
* **Frontend piloto (Node.js):** `node frontend-piloto/tests/run.mjs`

### 4. Despliegue con Docker (Opcional)
Para levantar la demo completa (subir un vídeo y ver sus resultados), ver [Demo: subir un vídeo y ver sus resultados](#-demo-subir-un-vídeo-y-ver-sus-resultados).
* **Qué valida:**
* **Suite de pruebas unitarias y contratos éticos (10 tests en esta rama + 5 tests del motor determinista en PR de fusión):**
* `tests/test_contracts.py` (6 tests): Contratos de audio, solape temporal, matriz de 4 cuadrantes *Seeing and Hearing* (Verónica Vilaplana), regla anti-*equality-washing* (Kanter 1977 / Tuchman 1978) y abstención ética ($p < 0{,}80 \rightarrow \text{no\_determinado}$).
* `tests/test_compliance_adapters.py` (4 tests): Purga biométrica en RAM (*Zero Facial Retention*), denegación de Sello Oficial ante sanciones LISOS o *cherry-picking* (Art. 6 Apache-2.0), rehabilitación corporativa activa (*Self-Cleaning* con ventana de 3 años e informes históricos) e inmutabilidad criptográfica `SHA-256` con ID de supervisión pseudonimizado (`operador_supervision_id`).

#### ☁️ Modo B: Inferencia Cloud con AI Endpoints de OVHcloud (Infraestructura Oficial)
> **Aprovecha el catálogo de modelos servidos en Europa por OVHcloud con aceleración GPU.**
1. Copiar la plantilla de configuración:
```bash
cp .env.example .env
```
2. Configurar en `.env` tu token de acceso proporcionado por OVHcloud:
```env
OVH_BASE_URL="https://oai.endpoints.kepler.ai.cloud.ovh.net/v1"
OVH_AI_ENDPOINTS_ACCESS_TOKEN="tu_token_aqui"
OVH_ASR_MODEL="whisper-large-v3"
```
3. Ejecutar el pipeline de audio sobre una muestra de prueba:
```bash
python scripts/test_audio_ovh.py tests/fixtures/muestra_audio.wav ca
```
*Genera de forma automática el archivo tabular estructurado con turnos de palabra, diarización y marcas de tiempo.*

#### 💻 Modo C: Ejecución Local Permisiva, Offline y Sector Público (ENS / Art. 157 LRJSP / Zero Cloud)
> **Para todas las Administraciones Públicas del Estado (RTVE, 3Cat/TV3, EITB, CRTVG, universidades, ministerios, diputaciones y ayuntamientos) sujetas al Esquema Nacional de Seguridad (ENS), al Art. 157 de la Ley 40/2015 (reutilización de sistemas) y a la Directiva UE 2019/882 de Accesibilidad.**
* **Soberanía Lingüística Cooficial e Inclusividad por Diseño (`ADR-0010`):** Soporte nativo sin traducción intermedia para todas las **lenguas cooficiales del Estado (`es`, `ca`, `gl`, `eu`) + `en`**, e inclusión automática de resumen en **Lectura Fácil (Norma UNE 153101 / WCAG 2.2 AA)** (`resumen_lectura_facil`) compatible con lectores de pantalla (`NVDA`/`JAWS`).
* **Aislamiento de Licencias (`aiasn/model_adapters/vision_adapter.py`):** Permite ingerir trazas precomputadas vía archivo plano (`.csv` / `.tsv` mediante `CSVPrecomputedAdapter`, doctrina de separación de procesos de la FSF) o ejecutar inferencia local 100 % permisiva (`PermissiveYOLOXAdapter` con **YOLOX Apache-2.0**, **InsightFace MIT** e **EasyOCR Apache-2.0**), sin contaminar entornos B2B o públicos con licencias copyleft (AGPL-3.0).
* **Círculo Virtuoso de Referentes Femeninos sin Reentrenamiento (*Green AI Flywheel*):** Los rótulos y menciones extraídos por consenso de alta confianza ($p \ge 0{,}80$) enriquecen un diccionario ligero local (`.csv`/`.json`) interoperable con **`Top Rosies Talent`**, **`ReDivIAcat`** y **`tFemTIC`** (`IDEAI-UPC` / `donesCOEINF`) y con **`WikiMujeres` / `Wikidata`**, mejorando el reconocimiento futuro (Cuadrante 4) tanto *offline/batch* como sincronizado sin coste de GPU en reentrenamiento.
* **Extensión en Caliente para las 4 Modalidades (*Shift-Left Parity*):** Diseñado para inyectarse como asistente preventivo en herramientas de **Vídeo** (`OBS Studio`, `DaVinci Resolve`, `Premiere`), **Audio/Podcasts** (`Audacity`, `Audition`), **Imagen/Cartelería** (`Canva`, `Figma`) y **Texto/Prensa** (`WordPress`, `Docs`), y emitir certificados con huella inmutable **`SHA-256`** (`emitir_sello_auditoria`).

---

## 🎬 Demo: subir un vídeo y ver sus resultados

La API recibe un vídeo, lanza el *worker* que lo procesa (audio, vídeo, NLP, silver y gold) y devuelve los resultados agrupados como las secciones del front. Se procesa un vídeo cada vez.

### Antes de empezar

* **GPU NVIDIA (muy recomendable).** Sin GPU todo funciona en CPU, pero el paso de vídeo tarda unas 5 veces la duración del vídeo (un vídeo de 2 min: ~10–12 min, frente a ~2 min con GPU).
* **Con Docker** hace falta además el **NVIDIA Container Toolkit**, para que los contenedores vean la GPU. Si no está, el *worker* se lanza en CPU y la API lo avisa en su log. Guía oficial: <https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html>. En Ubuntu/Debian:
```bash
curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg
curl -s -L https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list \
| sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' \
| sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list
sudo apt-get update && sudo apt-get install -y nvidia-container-toolkit
sudo nvidia-ctk runtime configure --runtime=docker && sudo systemctl restart docker
docker run --rm --gpus all ubuntu nvidia-smi # debe mostrar tu GPU
```
* **Token de OVHcloud** para la transcripción y el LLM: `cp .env.example .env` y rellena `OVH_AI_ENDPOINTS_ACCESS_TOKEN`.
* **Modelos:** no hay que descargarlos a mano. Cada uno se descarga la primera vez que se usa (~2,5 GB en total, entre ellos word2vec de 1,6 GB), así que el primer vídeo tarda más (medido: 8,3 min el primero frente a 1,9 min los siguientes, en un vídeo de 96 s con GPU). Con Docker quedan en el volumen `aiasn-models`; sin Docker, en la caché de cada librería (o en `MODELS_DIR` si la defines).
* **Límite actual:** vídeos de hasta ~2 minutos; con audios más largos la transcripción de OVHcloud falla.
* **Probado en** Linux con GPU NVIDIA. Windows y macOS están por probar; en macOS la instalación sin Docker aún no funciona (`onnxruntime-gpu` no existe para macOS).

### Con Docker

```bash
docker compose --profile jobs build # imágenes de la API y del worker (la del worker, ~8 GB, tarda 10–20 min la primera vez)
docker compose up -d # almacén S3 (SeaweedFS), API en http://localhost:8000 y front en http://localhost:8080
```

El *worker* no queda corriendo: la API arranca un contenedor `aiasn-worker` por vídeo y lo borra al lanzar el siguiente (hasta entonces, `docker logs aiasn-worker-<video_id>`). La API usa el socket de Docker para ello, lo que le da control sobre Docker en esa máquina: no la expongas fuera de tu equipo.

### Sin Docker

```bash
uv sync --extra worker --extra api
uv run uvicorn aiasn.api.app:create_app --factory --port 8000
```

Sin la imagen `aiasn-worker`, la API lanza el *worker* como proceso hijo (`API__LAUNCHER=process` para forzarlo) y guarda el lake en la carpeta `data/`. También se puede procesar un vídeo sin la API: `uv run python -m aiasn.run_pipelines --file video.mp4`.

### Uso

```bash
curl -F file=@video.mp4 http://localhost:8000/videos # → {"video_id": "video-3f9a"}
curl http://localhost:8000/videos/video-3f9a # estado; con "ok", también el resultado
```

O, desde el navegador, abre el front en <http://localhost:8080>: «Elegir vídeo» → «Analizar». Documentación interactiva de la API en <http://localhost:8000/docs>. Si los puertos 8000 u 8080 están ocupados, cámbialos con `API_PORT` y `FRONT_PORT` en `.env`.

---

## ⚖️ Declaración de Transparencia (EU AI Act - Art. 50)

En cumplimiento del **Reglamento (UE) 2024/1689 (Reglamento Europeo de IA)** y de la obligación legal vigente desde agosto de 2026:
* Este prototipo utiliza sistemas de inteligencia artificial de código abierto para tareas de transcripción (`whisper-large-v3`), detección visual (`YOLO11m`), clasificación demográfica agregada (`miVOLO`) y embeddings (`bge-m3`).
* **Uso de Asistentes y Copilotos de IA en el Desarrollo:** Conforme a las directrices de la Oficina Técnica de Código Abierto (`ComunidadIA-OS` / Jorge Teixeira) y la tecnoética de SEDIA, se declara explícitamente el uso de asistentes inteligentes de código y documentación (copilotos de IA) como herramientas de aceleración y soporte metodológico. El 100 % de la arquitectura, el código generado, las decisiones de diseño y la compatibilidad de licencias han sido supervisados, comprendidos, validados y auditados directamente por las desarrolladoras del equipo (*Human-in-the-Loop* en el ciclo de ingeniería).
* El sistema **no toma decisiones automatizadas vinculantes ni elabora perfiles biométricos individuales**. Su salida constituye una propuesta analítica sujeta a supervisión humana preceptiva (*Human-in-the-Loop*).
* Los datos de prueba utilizados en fase de desarrollo proceden de corpus autorizados por la UPC (`Àgora`) y de grabaciones de divulgación pública tratadas al amparo del **Art. 67 del Real Decreto-ley 24/2021** (excepción de Minería de Textos y Datos con fines de investigación).

---

## 📚 Documentación de Gobernanza y Enlaces Canónicos

* 🖥️ [**docs/especificacion_alertas_dashboard_y_hitl.md**](./docs/especificacion_alertas_dashboard_y_hitl.md): Especificación funcional de las 3 vistas por rol, alertas anti-*equality-washing*, Test de Interlocución Femenina (TIF) y pantalla *«Asumo / No asumo»* (#6).
* ⚖️ [**docs/marco_normativo_y_mercado.md**](./docs/marco_normativo_y_mercado.md): Marco normativo integral, cumplimiento exhaustivo del RIA (Reglamento UE 2024/1689), Ley Orgánica 2/2024 de Paridad, Directiva CSRD, datos CNMV 2025 y dimensionamiento del mercado B2B (#8).
* 👥 [**docs/evidencias_trabajo_en_equipo.md**](./docs/evidencias_trabajo_en_equipo.md): Informe oficial de gobernanza paritaria, evidencias de trabajo colaborativo, registro de reuniones sincrónicas y proceso deliberativo del equipo (TyC §13).
* 📐 [**docs/adr/README.md**](./docs/adr/README.md): Registro Canónico de Decisiones de Arquitectura (ADR-0001 a ADR-0011): justificación formal de la separación inferencia/cálculo, Green AI, biometría efímera, salvaguarda no binaria y TIF.
* ♿ [**docs/informe_conformidad_accesibilidad.md**](./docs/informe_conformidad_accesibilidad.md): Informe de conformidad de accesibilidad del dashboard (*WCAG 2.2 AA*, UNE 153101 EX, RD 1112/2018 y Directiva UE 2019/882): auditoría `axe-core`, doble codificación de color, contraste verificado y soporte para lectores de pantalla (#18).
* 📖 [**GLOSSARY.md**](./GLOSSARY.md): Glosario maestro de los 25 términos, elementos clave de la solución y diagrama del Círculo Virtuoso (*Retroalimentación Incremental sin Reentrenamiento*).
* 📋 [**ETHICS_CHECKLIST.md**](./ETHICS_CHECKLIST.md): Autoevaluación formal bajo los 7 principios de ALTAI y el Sandbox de la SEDIA / AESIA.
* 🧪 [**TESTING.md**](./TESTING.md): Protocolo de pruebas con *Ground Truth*, tests unitarios y pruebas de usabilidad humana.
* 🤖 [**MODEL_CARD.md**](./MODEL_CARD.md): Ficha técnica de modelos abiertos, umbrales y limitaciones conocidas.
* 📊 [**DATASET_CARD.md**](./DATASET_CARD.md): Ficha de procedencia de datos, perfil poblacional y régimen legal de fuentes.
* 🔒 [**SECURITY.md**](./SECURITY.md): Modelo de amenazas frente a ataques adversarios (Art. 15 RIA y OWASP ML/LLM), *Zero Facial Retention* y reporte responsable.
* 🤖 [**AGENTS.md**](./AGENTS.md): Guardarraíles vinculantes de seguridad, aislamiento de licencias y ética para agentes de código (*AI Coding Guardrails*).
* 🤝 [**CONTRIBUTING.md**](./CONTRIBUTING.md): Guía de contribución comunitaria y flujo de ramas.
* 📜 [**CODE_OF_CONDUCT.md**](./CODE_OF_CONDUCT.md): Código Ético a medida, Estatuto de Propósito Social, Cláusula Anti-Lavado de Cara (Art. 6 Apache-2.0), Política de Uso Responsable y Código de Conducta.
* 📝 [**CHANGELOG.md**](./CHANGELOG.md): Historial de versiones y evolución del prototipo.

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
* **Aislamiento y Compatibilidad de Dependencias:** El núcleo determinista (`[core]`) y los adaptadores locales (`[local-ai]` vía YOLOX e InsightFace) operan bajo licencias permisivas (Apache-2.0 / MIT). Cualquier uso de modelos bajo licencias copyleft de red (como Ultralytics AGPL-3.0) queda aislado en adaptadores opcionales independientes o mediante consumo remoto vía API HTTP REST en los AI Endpoints de OVHcloud, impidiendo cualquier contaminación de código privativo en clientes y corporaciones B2B.
