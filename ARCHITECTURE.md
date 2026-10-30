<!--
SPDX-FileCopyrightText: 2026 Equipo 1: Attention Is All She Needs (Alba Camiña García, Pilar de la Fuente Diez, Rocío Jiménez Villén)
SPDX-License-Identifier: Apache-2.0
-->

# Arquitectura de AIASN

Cada vídeo es procesado por cuatro pipelines de datos y los resultados se organizan en un Data Lake de tres capas siguiendo una arquitectura Medallion: bronze, silver y gold. Los resultados vuelven al front para completar el análisis de paridad.

**Contenido:** [Visión general](#visión-general) · [Orden de ejecución](#orden-de-ejecución) · [Audio](#pipeline-de-audio) · [Vídeo](#pipeline-de-vídeo) · [NLP](#pipeline-de-nlp) · [Rótulos](#pipeline-de-rótulos) · [Silver](#silver) · [Gold](#gold) · [API y front](#api-y-front) · [Producción](#producción-en-ovhcloud) · [Referencias](#referencias)

## Visión general

La demo local consiste en cuatro contenedores en un `docker compose`: el front, la API, el almacén S3 y el worker. El worker no está levantado siempre, sino que la API arranca un contenedor cuando se quiere iniciar el procesamiento de un vídeo, simulando un comportamiento serverless. Ningún procesamiento sucede en la API. Solo manda el vídeo al backend, lanza el worker y finalmente, lee los datos resultantes de gold. El worker es el único que escribe bronze, silver y gold. 

![Arquitectura de AIASN](img/arquitectura-aiasn.drawio.png)

Nota: Sin Docker, la API lanza el worker como proceso hijo y el lago es la carpeta local `data/`.

| Componente | Descripción |
|---|---|
| Front | nginx en `:8080` con `frontend-piloto/`; |
| API | FastAPI en `:8000`. Lanza los workers por `docker.sock`. |
| Worker | `python -m aiasn.run_pipelines --video-id ID`, un contenedor por vídeo, con GPU NVIDIA si la hay. Modelos locales en el volumen `aiasn-models` (`/models`). |
| Almacén S3 | SeaweedFS, bucket `s3://aiasn`, Parquet por `video_id=`. Carpetas `landing/` (vídeo subido), `bronze/` (salida de modelos, 10 tablas), `silver/` (personas y hechos, 13 tablas), `gold/` (KPIs y dictamen, 6 tablas), `runs/` (manifest con el estado de cada paso del pipeline) y `supervision/` (decisiones de la revisión humana, un fichero por decisión). |
| OVHcloud AI Endpoints [1] | Whisper large v3 [2] para speech to text; Llama 3.3 70B [3] como LLM y gpt-oss-120b [4] para los referentes. |
| Langfuse (opcional) | Perfil `langfuse` del compose: trazas de las llamadas al LLM, agrupadas por vídeo. Se activa con `LANGFUSE_ENABLED`. |


## Orden de ejecución

Dos pipelines corren a la vez en distintos hilos: audio y después NLP (que necesita la transcripción), y vídeo y después rótulos (que necesita los textos del OCR). Cuando acaban los dos, silver une lo que dicen, limpia y transforma y gold calcula los KPIs, el dictamen y los datos para generar la constelación en el frontend.

```mermaid
%%{init: {"flowchart": {"curve": "step", "nodeSpacing": 24, "rankSpacing": 40}}}%%
flowchart LR
    L["landing/<br/>vídeo.mp4"]
    subgraph C1["pipeline 1 · en paralelo"]
        A[Audio] --> AT[(audio_turns)] --> N[NLP] --> NT[("nlp_topics · mentions<br/>references · roles<br/>ideas · tone")]
    end
    subgraph C2["pipeline 2 · en paralelo"]
        V[Vídeo] --> VT[("video_detections<br/>video_texts")] --> R[Rótulos] --> RT[(video_captions)]
    end
    L --> A
    L --> V
    NT --> S["Silver<br/>6 transforms"]
    RT --> S
    S ----> G["Gold<br/>4 transforms"]
    classDef bronze fill:#f6e9dc,stroke:#9a5a22,color:#5a3410
    classDef silver fill:#e9edf1,stroke:#5f6b78,color:#2e353d
    classDef gold fill:#f7efd2,stroke:#8a6b0c,color:#4d3c06
    class AT,NT,VT,RT bronze
    class S silver
    class G gold
```


## Pipeline de audio

`lee landing/` → `escribe bronze/audio_turns`. Quién habla, cuándo, qué dice y con qué voz.

| Paso | Modelo | Qué hace |
|---|---|---|
| 1. `extract` | ffmpeg | Audio mono a 16 kHz, en `tmp/`. |
| 2. `asr` | Whisper large v3 de OVHcloud [2] | Transcripción con diarización: turnos con inicio, fin, hablante y texto. |
| 3. `gender` | prithivMLmods/Common-Voice-Gender-Detection, sobre wav2vec 2.0 [5] | Clasificador binario de Género de la voz por turno, con su probabilidad |

| Tabla | Una fila por | Columnas |
|---|---|---|
| `audio_turns` | turno de palabra | turn, start, end, speaker, text, gender, gender_prob |

## Pipeline de vídeo

`lee landing/` → `escribe bronze/video_detections y video_texts`. Quién sale, dónde, si habla y qué textos aparecen. Es el paso que usa la GPU.

| Paso | Modelo | Qué hace |
|---|---|---|
| 1. `extract` | ffmpeg | Fotogramas a 25 fps y audio a 16 kHz, en `tmp/`. |
| 2. `shots` | TransNetV2 [6] | Cortes de plano. |
| 3. `detect` | YOLO11m-pose [7] · InsightFace buffalo_l (SCRFD) [8] · MiVOLO v2 [9][10] | Personas y su seguimiento (1 de cada 4 fotogramas), caras, y género por cara y cuerpo. |
| 4. `RE-ID` | ArcFace (InsightFace) [11] | Reidentificación: Une las pistas de una misma persona entre planos: agrupa la cara media de cada pista por distancia coseno (< 0,6). Los vectores no se guardan.  |
| 5. `asd` | TalkNet [12] | Active Speaker Recognition: Reconoce quién está hablando en cada fotograma, cruzando cara y audio. |
| 6. `ocr` | EasyOCR (CRAFT) [13] | Textos en pantalla a 1 fps |

| Tabla | Una fila por | Columnas |
|---|---|---|
| `video_detections` | persona y fotograma analizado | frame, shot, track_id, person_id, x1, y1, x2, y2, head, face_x1…face_y2, gender, gender_prob, age, frame_width, frame_height, speaking_score |
| `video_texts` | texto leído | frame, shot, text, conf, x1, y1, x2, y2 |

## Pipeline de NLP

Lee `bronze/audio_turns` → `escribe 6 tablas nlp_*`. Seis tareas independientes sobre la transcripción, lanzadas a la vez (hasta 6 llamadas) a los LLM de OVHcloud por LiteLLM: Llama 3.3 70B [3] y, para los referentes, gpt-oss-120b [4], que distingue mejor a las figuras públicas citadas de quienes participan, de los institutos con nombre de persona y de las épocas. Para evitar alucinaciones, cada cita que devuelve el modelo se comprueba contra la transcripción (`found`) y lo que no aparece en el texto se descarta.

| Tarea | Qué extrae |
|---|---|
| `mentions` | Quién alude a quién en la conversación, y si dice su nombre y cargo. |
| `topics` | Temas de la conversación entera y qué hablantes tratan cada uno, guiado por una lista de temas incluidos en el prompt. |
| `references` | Personas históricas o conocidas públicamente citadas como referente, con su género. Por cada una, el modelo razona y responde sí o no a si es una persona concreta (no una época, un lugar o un instituto), si es conocida públicamente y si se cita como referente; solo quedan las que cumplen las tres y cuyo nombre parece de persona. |
| `roles` | Formato de la pieza y rol de cada hablante: presentador/a, entrevistado/a, experto/a, testimonio… |
| `ideas` | Ideas clave de la pieza y quién las aporta. |
| `tone` | Tono de cada turno: técnico/asertivo, colaborativo o disenso. Con el LLM o, si se elige desde la configuración, con clasificación zero-shot con mDeBERTa [14] en local. |

| Tabla | Una fila por | Columnas |
|---|---|---|
| `nlp_mentions` | mención a un participante | turn, speaker, literal, name, title, gender, referred_speaker, found |
| `nlp_topics` | tema y hablante que lo trata | speaker, topic, topic_es, evidence, found |
| `nlp_references` | referente citado | turn, speaker, name, literal, gender, found |
| `nlp_roles` | hablante | speaker, role, role_es |
| `nlp_ideas` | idea y hablante que la aporta | idea_id, idea, speaker |
| `nlp_tone` | turno | turn, speaker, tone, score, evidence, found |

## Pipeline de rótulos

Lee `bronze/video_texts` y escribe`bronze/video_captions`. El LLM lee los textos del OCR y responde, bloque a bloque, sí o no a si presenta a una persona concreta (por defecto, no: logotipos, títulos de evento o nombres de centros no lo son). De los rótulos de persona saca nombre, cargo, el cargo en inglés (lo necesitaremos para word2vec [15]) y si el cargo muestra autoridad experta o institucional.

| Tabla | Una fila por | Columnas |
|---|---|---|
| `video_captions` | rótulo de persona en un fotograma | frame, shot, text, name, title, title_en, title_authority, found |

## Silver

En esta fase se realizan seis transformaciones y se cruzan los resultados de video y transcripción para decidir quién es cada persona, de qué género (con abstención por debajo de una probabilidad de 0,80) y qué dijo.

```mermaid
%%{init: {"flowchart": {"curve": "step", "nodeSpacing": 24, "rankSpacing": 40}}}%%
flowchart LR
    %% left: bronze it reads · middle: transformations, in the order they run · right: silver they write
    %% the longer arrows (more dashes) keep bronze in the first column and silver in the last one
    VD[(video_detections)] --> video
    AT[(audio_turns)] --> audio
    CM[("video_captions<br/>nlp_mentions")] ----> names
    NL[("nlp_topics · roles<br/>references · ideas · tone")] -----> nlp

    video --> identity
    audio --> identity
    identity -- personas --> names
    identity -- voces --> nlp
    names -- nombres --> nlp
    names -- cargos --> word_bias
    nlp -- temas --> word_bias

    video -.....-> S1[("video_people · video_presence")]
    audio -.....-> S2[("audio_speakers · audio_turns")]
    identity -....-> S3[("speaker_person · people")]
    names -...-> S4[("person_names · people")]
    nlp -..-> S6[("nlp_topics · roles · references<br/>nlp_ideas · nlp_tone")]
    word_bias -.-> S5[(term_bias)]

    classDef bronze fill:#f6e9dc,stroke:#9a5a22,color:#5a3410
    classDef silver fill:#e9edf1,stroke:#5f6b78,color:#2e353d
    class VD,AT,CM,NL bronze
    class S1,S2,S3,S4,S5,S6 silver
```


| Transformación | Qué decide | Escribe |
|---|---|---|
| `video` | Género de cada persona por voto de los fotogramas con cara (sin cara visible en la mitad de ellos: no determinado); tiempo en pantalla y hablando, área y centralidad; tramos de presencia, con el estado de habla suavizado en 1 s. | `video_people`, `video_presence` |
| `audio` | Género de cada voz con todos sus turnos; turnos con su hablante. | `audio_speakers`, `audio_turns` |
| `identity` | Qué voz es qué cara. Primero por TalkNet [12]: las enlaza si hablan a la vez al menos 1 s y el 30 % de su voz. Si no, por copresencia: la única persona en pantalla durante al menos el 60 % de esa voz, y en pantalla sobre todo mientras habla, si los géneros no se contradicen. Crea los participantes y fusiona el género de cara y voz (si se contradicen, no determinado). | `speaker_person`, `people` |
| `names` | Nombre y cargo de cada participante, de sus rótulos y de cómo lo mencionan. | `person_names`, `people` |
| `nlp` | Pasa las tablas del LLM de hablante a participante. Autoridad por rol o por rótulo con cargo; quien habla en pantalla no puede ser narrador/a en off. | `nlp_topics`, `nlp_references`, `nlp_roles`, `nlp_ideas`, `nlp_tone` |
| `word_bias` | Sesgo de género en word2vec [15] de cada topic y cargo, con el método de Bolukbasi et al. (2016) [16]. | `term_bias` |

## Gold

Cuatro transformaciones. La fusión cruza voz y pantalla en el tiempo y de ahí salen los cuadrantes y el veredicto.

```mermaid
%%{init: {"flowchart": {"curve": "step", "nodeSpacing": 24, "rankSpacing": 40}}}%%
flowchart LR
    S[("silver/<br/>audio_turns · speaker_person<br/>video_people · video_presence<br/>people · person_names<br/>nlp_topics · roles · references<br/>nlp_ideas · nlp_tone<br/>term_bias")]
    S --> fusion --> Q[("quadrants<br/>summary")]
    S --> kpis --> K[(kpis)]
    Q ----> kpis
    K --> index --> I[(index)]
    S --> GT[graph] --> GR[("graph_nodes<br/>graph_edges")]
    classDef bronze fill:#f6e9dc,stroke:#9a5a22,color:#5a3410
    classDef silver fill:#e9edf1,stroke:#5f6b78,color:#2e353d
    classDef gold fill:#f7efd2,stroke:#8a6b0c,color:#4d3c06
    class S silver
    class Q,K,I,GR gold
```

**fusion: quadrants y summary**

- Cuadrante 1: voz activa en pantalla. Cuadrante 2: presencia muda. Cuadrante 3: voz en off.
- % de voz y de pantalla sobre el tiempo de género conocido; lo no determinado, aparte.
- Ratio voz/pantalla = % voz ÷ % pantalla.
- Equality-washing: pantalla ≥ 35 % y (ratio < 0,30 o voz < 20 %).
- Infrarrepresentación: pantalla < 40 % (la presencia equilibrada de la LO 2/2024 [17]) y ratio < 1.
- Salvaguarda de paridad (ADR-0006), Test de Interlocución Femenina (adaptación del test de Bechdel [18]) con tres estados y resumen en lectura fácil (pautas UNE 153101 EX [19]).

**kpis**

- `parity`: segundos de voz, pantalla y cada cuadrante; área y centralidad.
- `authority`: voz desde un rol o un rótulo de autoridad.
- `topics`: participantes por tema y género. `tone`: turnos por tono.
- `references`: referentes citados. `naming`: menciones con cargo.
- `ideas`: ideas aportadas, con otras personas y en exclusiva.
- `stereotype`: sesgo word2vec medio de temas y cargos.

**index**

- Índice global de representación (0–100): media ponderada de pantalla, voz, espacio y autoridad. Provisional hasta cerrar la señal de autoridad; no se muestra en el front.

**graph: graph_nodes y graph_edges**

- Nodos: cada participante (con género, rol, autoridad, tiempos, área y centralidad) y cada tema (con su sesgo y el número de personas que lo tratan).
- Aristas: `menciona` (A nombra a B), `turno` (B habla después de A), `comparte_plano` (salen a la vez, en segundos) y `habla_de` (persona → tema).

## API y front

| Endpoint | Descripción |
|---|---|
| `POST /videos` | Guarda el vídeo en `landing/`, deja el manifest en cola y lanza el worker. 409 si ya hay otro en marcha. |
| `GET /videos/{id}` | Estado y pasos del manifest y, cuando está "ok", el resultado por secciones y la última decisión de la revisión humana. Si el worker ha muerto, marca el vídeo como error. |
| `POST /videos/{id}/supervision` | Guarda una decisión de la revisión humana (género de cada persona dudosa, «Asumo» o «No asumo» con su motivo) como un fichero nuevo en `supervision/`, con fecha y huella SHA-256 de las métricas. No recalcula los KPIs. |
| `GET /videos` | Todos los vídeos del Data Lake con su estado, el más reciente primero. |
| `GET /health` | Comprueba que la API responde. |

**De dónde sale cada sección del resultado**

| Sección | Lo que muestra el front | Procedencia |
|---|---|---|
| `veredicto` | Alertas, TIF, salvaguarda, lectura fácil | `summary` (y `index`) |
| `metricas` | % de voz y pantalla, ratio, parte sin determinar, referentes | `kpis` |
| `personas` | Ficha de cada estrella | `graph_nodes`, `people` |
| `temas` | Segregación temática con su sesgo | `kpis`, `graph_nodes` |
| `poder`, `roles`, `autoridad` | Señales de rol protagonista, jerarquía de rol y autoridad | `kpis`, `graph_nodes`, `nlp_references` |
| `clima` | Tono por género | `kpis` |
| `constelacion` | El cielo: estrellas, temas y vínculos | `graph_nodes`, `graph_edges` |
| `segmentos`, `segmentos_dudosos` | Supervisión humana de los tramos sin género | `quadrants`, `speaker_person` |

## Producción en OVHcloud

Propuesta de despliegue en producción, aún no implementada. Utilizaríamos los servicios del ecosistema de OVHcloud: AI Training, AI Endpoints y S3 Object Storage.

![Arquitectura en producción](img/arquitectura-produccion.png)

| Componente | Sustituye en la demo | Especificación | Coste (sin IVA) [20] |
|---|---|---|---|
| VPS-1 [21] | Front y API del `docker compose` | 2 vCores, 4 GB RAM, 40 GB NVMe. HTTPS con Caddy y Let's Encrypt | 4,49 €/mes |
| AI Training [22] | Contenedor del worker | Un *job* por vídeo con 1× NVIDIA L4 (`l4-1-gpu`), imagen pública de PyTorch y el código del repositorio | 0,83 €/h, por minuto en estado `RUNNING` [23] |
| Object Storage [24] | SeaweedFS y volumen `aiasn-models` | Standard, ~2 GB: Data Lake y modelos | 0,0071 €/GB al mes |
| AI Endpoints [1] | Lo mismo que en la demo | Whisper, Llama 3.3 70B y gpt-oss-120b | ≈0,31 €/h de audio (medido en la demo) |
| Langfuse Cloud EU | Perfil `langfuse` del compose | Plan Hobby | 0 € |

- La API lanza cada *job* con la API de OVHcloud (`POST /cloud/project/{serviceName}/ai/job`) [25] y le pasa las credenciales de S3 y AI Endpoints como variables de entorno. El navegador no las ve.
- El *job* recibe los modelos del bucket, copiados a su disco local antes de arrancar [26]; lee el vídeo de `landing/` y escribe bronze, silver y gold en el bucket, como en la demo.
- La API sigue el estado del vídeo por el manifest, como en la demo.

**Coste estimado:** ≈0,07 € + 0,026 € por minuto de vídeo, más ≈5 €/mes fijos (VPS, dominio y bucket). Supone que la L4 va como la RTX 4060 medida en `DATASET_CARD.md` (1.2), más el arranque de cada *job*; no está medido en una L4.

| Volumen diario | Coste al mes |
|---|---|
| 5 vídeos de 5 min | ≈35 € |
| 10 vídeos de 10 min | ≈103 € |
| 2 vídeos de 60 min | ≈102 € |


# Referencias

1. OVHcloud AI Endpoints. <https://endpoints.ai.cloud.ovh.net>
2. Radford, A., Kim, J. W., Xu, T., Brockman, G., McLeavey, C. y Sutskever, I. (2023). *Robust Speech Recognition via Large-Scale Weak Supervision*. ICML 2023. [arXiv:2212.04356](https://arxiv.org/abs/2212.04356)
3. Grattafiori, A., Dubey, A., Jauhri, A. et al. (2024). *The Llama 3 Herd of Models*. [arXiv:2407.21783](https://arxiv.org/abs/2407.21783). Modelo: <https://huggingface.co/meta-llama/Llama-3.3-70B-Instruct>
4. OpenAI (2025). *gpt-oss-120b & gpt-oss-20b Model Card*. [arXiv:2508.10925](https://arxiv.org/abs/2508.10925). Modelo: <https://huggingface.co/openai/gpt-oss-120b>
5. Baevski, A., Zhou, H., Mohamed, A. y Auli, M. (2020). *wav2vec 2.0: A Framework for Self-Supervised Learning of Speech Representations*. NeurIPS 2020. [arXiv:2006.11477](https://arxiv.org/abs/2006.11477)
6. Souček, T. y Lokoč, J. (2020). *TransNet V2: An effective deep network architecture for fast shot transition detection*. [arXiv:2008.04838](https://arxiv.org/abs/2008.04838)
7. Jocher, G. y Qiu, J. (2024). *Ultralytics YOLO11* (AGPL-3.0). <https://github.com/ultralytics/ultralytics>
8. Guo, J., Deng, J., Lattas, A. y Zafeiriou, S. (2022). *Sample and Computation Redistribution for Efficient Face Detection* (SCRFD). ICLR 2022. [arXiv:2105.04714](https://arxiv.org/abs/2105.04714)
9. Kuprashevich, M. y Tolstykh, I. (2023). *MiVOLO: Multi-input Transformer for Age and Gender Estimation*. [arXiv:2307.04616](https://arxiv.org/abs/2307.04616)
10. Kuprashevich, M., Alekseenko, G. y Tolstykh, I. (2024). *Beyond Specialization: Assessing the Capabilities of MLLMs in Age and Gender Estimation* (MiVOLO v2). [arXiv:2403.02302](https://arxiv.org/abs/2403.02302)
11. Deng, J., Guo, J., Xue, N. y Zafeiriou, S. (2019). *ArcFace: Additive Angular Margin Loss for Deep Face Recognition*. CVPR 2019. [arXiv:1801.07698](https://arxiv.org/abs/1801.07698)
12. Tao, R., Pan, Z., Das, R. K., Qian, X., Shou, M. Z. y Li, H. (2021). *Is Someone Speaking? Exploring Long-term Temporal Features for Audio-visual Active Speaker Detection* (TalkNet). ACM MM 2021. [arXiv:2107.06592](https://arxiv.org/abs/2107.06592)
13. Baek, Y., Lee, B., Han, D., Yun, S. y Lee, H. (2019). *Character Region Awareness for Text Detection* (CRAFT). CVPR 2019. [arXiv:1904.01941](https://arxiv.org/abs/1904.01941)
14. He, P., Gao, J. y Chen, W. (2023). *DeBERTaV3: Improving DeBERTa using ELECTRA-Style Pre-Training with Gradient-Disentangled Embedding Sharing*. ICLR 2023. [arXiv:2111.09543](https://arxiv.org/abs/2111.09543)
15. Mikolov, T., Sutskever, I., Chen, K., Corrado, G. y Dean, J. (2013). *Distributed Representations of Words and Phrases and their Compositionality*. NeurIPS 2013. [arXiv:1310.4546](https://arxiv.org/abs/1310.4546)
16. Bolukbasi, T., Chang, K.-W., Zou, J., Saligrama, V. y Kalai, A. (2016). *Man is to Computer Programmer as Woman is to Homemaker? Debiasing Word Embeddings*. NeurIPS 2016. [arXiv:1607.06520](https://arxiv.org/abs/1607.06520)
17. Ley Orgánica 2/2024, de 1 de agosto, de representación paritaria y presencia equilibrada de mujeres y hombres. BOE núm. 186, de 2 de agosto de 2024.
18. Bechdel, A. (1985). «The Rule», *Dykes to Watch Out For*.
19. AENOR (2018). *UNE 153101:2018 EX. Lectura Fácil. Pautas y recomendaciones para la elaboración de documentos*.
20. OVHcloud. *Precios de Public Cloud*. <https://www.ovhcloud.com/es-es/public-cloud/prices/>
21. OVHcloud. *VPS*. <https://www.ovhcloud.com/es-es/vps/>
22. OVHcloud. *AI Training*. <https://www.ovhcloud.com/es-es/public-cloud/ai-training/>
23. OVHcloud. *AI Training - Getting started*. <https://docs.ovhcloud.com/en/guides/public-cloud/ai-machine-learning/ai-training-submit-job>
24. OVHcloud. *Object Storage*. <https://www.ovhcloud.com/es-es/public-cloud/object-storage/>
25. OVHcloud. *API de OVHcloud*. <https://eu.api.ovh.com/console/>
26. OVHcloud. *AI - Data*. <https://docs.ovhcloud.com/en/guides/public-cloud/ai-machine-learning/ai-data>
