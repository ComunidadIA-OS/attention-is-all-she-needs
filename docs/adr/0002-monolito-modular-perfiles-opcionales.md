# 0002. Monolito modular desacoplado (`[core]`, `[local-ai]`, `[gpu]`) con adaptadores agnósticos frente a microservicios y modelos multimodales monolíticos

* **Fecha:** 2026-10-17 (revisada y ampliada el 2026-10-25)
* **Estado:** Aceptada
* **Decisores:** Equipo AIASN (Pilar de la Fuente Diez, Rocío Jiménez Villén, Alba Camiña García)
* **Directrices de referencia:** Bases Oficiales del Reto (Art. 10 — *«Independencia de modelos y libertad tecnológica»*), Jorge Teixeira (Oficina Técnica ComunidadIA-OS / mentor de código abierto) y Montse Guàrdia (`1:24:50` — sostenibilidad y prevención de costes ocultos en MVP).

---

## 1. Contexto y Problema

El software de auditoría audiovisual debe dar respuesta simultánea a tres requerimientos técnicos y operativos de partida:
1. **Diversidad de entornos de ejecución:** Debe poder ejecutarse con mínima fricción tanto en portátiles ligeros de analistas, periodistas y activistas (entornos sin GPU dedicada que consumen APIs o ejecutan inferencia CPU ligera) como en estaciones de cómputo con $2 \times \text{NVIDIA V100}$ en los AI Notebooks de OVHcloud.
2. **Exigencia de neutralidad tecnológica (Artículo 10 de las Bases):** El reglamento del reto y las orientaciones de la oficina técnica (Jorge Teixeira) estipulan taxativamente que la solución debe ser *«agnóstica al modelo de IA, modular y libre de ataduras o dependencias cautivas de proveedor (*vendor/model lock-in*)»*.
3. **Eficiencia computacional y Algoritmos Verdes:** Procesar vídeo de larga duración (debates de 1 a 2 horas) no puede comprometer costes desorbitados ni una huella de carbono inasumible.

Desplegar una arquitectura monolítica cerrada o una infraestructura hiperdistribuida de microservicios pondría en riesgo la viabilidad del proyecto, el rendimiento en tiempo de ejecución y la facilidad de mantenimiento.

---

## 2. Opciones Analizadas y Debatidas

Durante las sesiones de diseño de la arquitectura (debates de equipo D-03 y deliberaciones sincrónicas), se evaluaron tres alternativas arquitectónicas:

### Opción A: Arquitectura de Microservicios Distribuidos (Docker Compose / Kubernetes)
* **Propuesta inicial (Rocío):** Desplegar 4 contenedores independientes (frontend, worker de inferencia Celery, API FastAPI y almacenamiento de objetos MinIO) orquestados mediante `docker-compose.yml`.
* **Ventajas aparentes:** Aislamiento de entornos y escalado horizontal independiente de cada servicio.
* **Motivos de descarte para el MVP:**
  1. *Incompatibilidad en entornos de evaluación:* En los AI Notebooks de OVHcloud ($2 \times \text{V100}$ en JupyterLab), el entorno corre dentro de un contenedor sin privilegios de root ni daemon de Docker accesible, lo que impediría la ejecución directa del prototipo por parte del jurado.
  2. *Sobrecarga operativa y huella en reposo:* Levantar cuatro runtimes de Python y servicios auxiliares consume entre 2 y 4 GB de RAM solo en reposo (*idle*), introduciendo latencias de red inter-proceso (IPC/HTTP) innecesarias para procesar archivos locales.
  3. *Costes ocultos de mantenimiento:* Como advirtió Montse Guàrdia en su sesión de Innovación, la sobreingeniería de infraestructura en fases tempranas resta foco al valor central del producto. Se preserva como esquema de despliegue industrial B2B futuro, pero se descarta como núcleo del reto.

### Opción B: Modelo Multimodal Monolítico End-to-End (ej. CLIP, Video-LLaVA, VLM unificado)
* **Planteamiento evaluado:** Emplear un único modelo multimodal de visión y lenguaje que reciba el vídeo de extremo a extremo y genere directamente las descripciones y clasificaciones de presencia y rol.
* **Ventajas aparentes:** Ahorro conceptual de pipelines independientes de audio y visión.
* **Motivos de descarte categórico:**
  1. *Falta de resolución temporal y diarización acústica:* Los modelos de visión-lenguaje como CLIP son estáticos o ciegos al tiempo (*time-blind*). No disponen de precisión a nivel de milisegundo para segmentar la diarización de turnos de habla ni registrar la micro-dinámica conversacional (quién cede la palabra a quién).
  2. *Sesgos severos de género inauditables (caja negra):* Investigaciones fundamentales de referencia (Birhane et al., 2021; Radford et al., 2021) han demostrado que modelos multimodales como CLIP contienen sesgos sistemáticos de cosificación, sexualización y estereotipación tradicional hacia las mujeres, aprendidos de datos web masivos no filtrados. Al proyectar texto e imagen en un espacio latente conjunto opaco, resulta matemáticamente inviable aplicar calibración activa (*debiasing by design*) determinista o auditar los sesgos intermedios.
  3. *Riesgo regulatorio ante el Reglamento Europeo de IA (RIA - Art. 5.1.f):* Un modelo multimodal que interprete conjuntamente expresiones y rostros de forma opaca roza la prohibición de clasificación biométrica y análisis de emociones no consentido.
  4. *Incompatibilidad con Algoritmos Verdes (Green AI):* Alimentar un modelo multimodal continuo con 108.000 fotogramas por hora a 30 fps requeriría mantener la GPU a 300 W de forma ininterrumpida. Frente a esto, desacoplar el pipeline permite aplicar un **muestreo STRIDE guiado por audio (ADR-0003)**, donde la visión se ejecuta únicamente en el ~5% de los fotogramas clave, reduciendo el consumo energético en $>95\%$.
  5. *Atadura tecnológica (Violación del Art. 10 de las Bases):* Si el sistema depende de un modelo multimodal monolítico o de una API comercial cerrada, se viola la exigencia de que el software sea agnóstico al modelo.

### Opción C: Monolito Modular Desacoplado con Adaptadores Intercambiables (`model_adapters/`) y Perfiles Opcionales en `pyproject.toml`
* **Planteamiento:** Paquete único en Python (`aiasn`) estructurado en módulos funcionalmente independientes con fronteras estrictas de contrato de datos (`Pydantic`), coordinados por un motor determinista (`aiasn/core`) y comunicados con los modelos mediante el patrón de diseño *Adapter / Protocol* (`aiasn/model_adapters`).

---

## 3. Decisión Adoptada

Se adopta unánimemente la **Opción C**. 

1. **Arquitectura Agnóstica al Modelo mediante Adaptadores:**
   El código interactúa exclusivamente con interfaces abstractas (`AudioDiarizerAdapter`, `VisionDetectorAdapter`, `EmbeddingAdapter`, `LLMAdapter`). Cada componente puede reemplazarse en caliente sin modificar una sola línea del motor de fusión determinista (`fusion.py`) ni de las métricas:
   * **Audio:** `WhisperDiarizerOVH` (API Keppler) $\leftrightarrow$ `FasterWhisperLocal` (CPU/CUDA) $\leftrightarrow$ `PyannoteAudioAdapter`.
   * **Visión:** `YOLOInsightFaceAdapter` (baseline oficial) $\leftrightarrow$ `YOLOXAdapter` (Apache-2.0 puro de Megvii) $\leftrightarrow$ `MediaPipeAdapter`.
   * **Embeddings:** `BGEEmbeddingsOVH` $\leftrightarrow$ `QwenEmbeddingAdapter` $\leftrightarrow$ `SentenceTransformersLocal`.
   * **NLP / Roles:** `QwenOVHClient` $\leftrightarrow$ `Llama3OVHClient` $\leftrightarrow$ `OllamaLocalClient`.

2. **Perfiles de Instalación Graduales (`pyproject.toml`):**
   * `pip install -e ".[core]"`: Motor determinista + SQLite/Parquet + contratos Pydantic + conectores HTTP a AI Endpoints de OVHcloud (100% licencias permisivas MIT/Apache-2.0, arranque instantáneo en $< 3\text{ s}$, sin librerías CUDA pesadas).
   * `pip install -e ".[local-ai]"`: Perfil `[core]` + inferencia CPU ligera local (`faster-whisper`, ONNX, YOLOX de Megvii, InsightFace).
   * `pip install -e ".[gpu]"`: Perfil completo para instancias con GPU ($2 \times \text{V100}$) con PyTorch, Ultralytics (aislado con *lazy imports* por licencia AGPL-3.0), Pyannote y CUDA.

---

## 4. Consecuencias

### Positivas
* **Agnóstico al modelo y libre de ataduras (Art. 10 Bases):** Cumplimiento riguroso de la directriz de la oficina técnica (Jorge Teixeira). Si un modelo queda desfasado o cambia su política de licencias, se sustituye su adaptador sin reescribir el software.
* **Rendimiento óptimo y Algoritmos Verdes:** El motor determinista ejecuta todas las agregaciones y ratios matemáticos en milisegundos en memoria RAM, mientras que los módulos de inferencia solo se invocan bajo demanda con muestreo selectivo STRIDE.
* **Mantenibilidad y resiliencia:** Los fallos quedan contenidos en el módulo correspondiente. Si el servicio de visión se interrumpe, el pipeline de audio y transcripción sigue operando y deriva los datos de encuadre a supervisión humana (*HitL*).
* **Portabilidad y facilidad de corrección para el jurado:** El jurado y la organización pueden clonar el repositorio y ejecutar la suite de pruebas unitarias (`pytest`) o el dashboard sin necesidad de configurar Docker ni disponer de tarjetas gráficas dedicadas.
* **Blindaje de licencias B2B:** El núcleo (`[core]`) permanece 100% Apache-2.0 / MIT, garantizando que terceros puedan adoptar la herramienta sin riesgo de contaminación por licencias de red tipo copyleft (AGPL-3.0).

### Compromisos y Mitigaciones
* **Uso de Importaciones Diferidas (*Lazy Imports*):** Para evitar fallos de importación (`ModuleNotFoundError`) en el perfil ligero `[core]`, los módulos de visión pesada y frameworks GPU se importan dinámicamente solo en el momento en que se instancia el adaptador correspondiente.
* **Mantenimiento de Contratos Pydantic:** Exige conservar la estabilidad de las clases de intercambio de datos (`SegmentoHabla`, `DeteccionVisual`, `EventoTurno`) ante evoluciones en las respuestas de los modelos.
