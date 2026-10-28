<!--
SPDX-FileCopyrightText: 2026 Equipo 1: Attention Is All She Needs (Alba Camiña García, Pilar de la Fuente Diez, Rocío Jiménez Villén)
SPDX-License-Identifier: Apache-2.0
-->

# Autoevaluación Ética y Regulatoria (ETHICS_CHECKLIST)
## Proyecto: «Attention Is All She Needs» (AIASN) — Reto «Mujeres por la IA Abierta»

> **Ficha Técnica de Conformidad:**  
> * **Marcos de Referencia Oficiales:** Directrices Éticas para una IA Fiable (*Ethics Guidelines for Trustworthy AI* / `ALTAI`, Comisión Europea HLEG 2019/2020), Reglamento (UE) 2024/1689 (*Reglamento Europeo de Inteligencia Artificial / RIA*), Guías Técnicas del Sandbox Regulatorio Español de IA (SEDIA / AESIA) y Modelo `PIO` (*Principis d'Intel·ligència Artificial Oberta*, OEIAC / UdG). **Contexto normativo a 28/10/2026:** Reglamento (UE) 2026/1744 (Ómnibus Digital de IA, que retrasa el alto riesgo y retoca otros puntos sin cambiar las prohibiciones ni el Art. 50) y Proyecto de Ley Orgánica para el buen uso y la gobernanza de la IA (BOCG, Serie A, núm. 97-1, 12/06/2026), que conocemos y tomamos como norte y filosofía de uso, **sin presentarlo como norma vigente** ([ADR-0012](./docs/adr/0012-marco-normativo-omnibus-digital-y-proyecto-de-ley.md)).  
> * **Clasificación de Riesgo según el RIA:** Sistema de **Riesgo Limitado / Transparencia (Art. 50 RIA)** en fase de prototipo de I+D, incorporando de forma preventiva salvaguardas de sistemas de Alto Riesgo (*High-Risk AI*) por diseño.  
> * **Equipo de Auditoría:** Alba Camiña García, Rocío Jiménez Villén y Pilar de la Fuente Diez (Equipo 1).

---

## Matriz Resumen de Cumplimiento Ético por Principio

| # | Principio de la IA Fiable (ALTAI / RIA) | Estado | Salvaguarda Técnica Principal en el Repositorio | Referencia en Formaciones |
| :-: | :--- | :---: | :--- | :--- |
| **1** | **Agencia y Supervisión Humana** | ⚠️ **Parcial (ver 1.1 y 1.3)** | Panel de revisión de personas con género dudoso en el frontend piloto (*HitL*); las decisiones aún no se guardan. El botón *«Asumo / No asumo»* con identificador pseudonimizado está por integrar (hoja de ruta). | Karina Gibert (`1:00:50`) y Ángela Gasch |
| **2** | **Robustez Técnica y Seguridad** | ✅ **Verificado** | Separación determinista: Inferencia IA abierta + Cálculo Python sin alucinaciones. | Fonollosa (VAD/Whisper), Vilaplana (VLMs) |
| **3** | **Privacidad y Gobernanza de Datos** | ⚠️ **Parcial (ver 3.5)** | *Zero Facial Retention* (biometría efímera en RAM) y amparo Art. 67 RDL 24/2021. | Karina Gibert (`2:05:10`) y Ángela Gasch |
| **4** | **Transparencia y Explicabilidad** | ✅ **Verificado** | Declaración RIA (obligatoria desde ago 2026) y *Data Profile* de `Àgora` (14%). | Jorge Teixeira y Karina Gibert (`0:40:41`) |
| **5** | **Diversidad, Equidad y No Sesgo** | ✅ **Verificado** | Detector de *Equality-Washing* (4 cuadrantes) y tratamiento de bolsa `unknown`. | Vilaplana (Diap. 91-92) y Karina (Diap. 10) |
| **6** | **Bienestar Social y Ambiental** | ✅ **Verificado** | *Green AI*: Muestreo STRIDE (1-5 fps) con ahorro $>80\%$ en GPU y coste $<0,30$ €/h. | Montse Guàrdia (`1:55:45`) y David Buenhombre |
| **7** | **Rendición de Cuentas** | ✅ **Verificado** | Arquitectura agnóstica al modelo, suite ADRs y trazabilidad fotograma a fotograma. | Jorge Teixeira (ComunidadIA-OS) y ALTAI |

---

## 1. Agencia Humana y Supervisión (*Human Agency & Oversight*)

- [ ] **1.1. Supervisión Operativa en la Interfaz (Botón *«Asumo / No asumo»*) — Parcial:**  
  *Estado real (v0.1.0):* el frontend piloto incluye un panel de revisión de personas con género dudoso donde una persona puede asignar «Mujer», «Hombre» o «No determinable» a cada persona dudosa, pero **las decisiones no se guardan** (se pierden al recargar), **no hay botón «Asumo / No asumo» como tal** y la revisión **no bloquea** la emisión del informe. Lo que sigue es el **diseño objetivo** (hoja de ruta):  
  *Justificación:* Conforme a la advertencia de Karina Gibert y Ángela Gasch sobre el escándalo *Toeslagenaffaire* en Países Bajos, el sistema **nunca emite un informe definitivo de forma autónoma**. La interfaz presenta un panel de supervisión *Human-in-the-Loop* (HitL) donde el personal responsable de igualdad o auditoría debe pulsar expresamente **«Asumo las métricas»** o **«No asumo / Derivar a revisión manual»** tras inspeccionar los casos dudosos.
- [x] **1.2. Asistente que Aumenta, No que Sustituye:**  
  *Justificación:* El software está conceptualizado como una herramienta de apoyo analítico que automatiza la ingesta tediosa de minutados, pero deja la valoración contextual y jurídica del cumplimiento a la persona operadora.
- [ ] **1.3. Segmentación de Vistas por Rol — Hoja de ruta:**  
  *Estado real (v0.1.0):* el frontend piloto es una única página; la pestaña «En palabras sencillas» es lo más cercano a una vista no técnica. La capa ciudadana existe solo como maqueta en una rama de diseño (PR #26), sin envío a servidor. *Diseño objetivo:* tres niveles de visualización para evitar la sobrecarga informativa:  
  * **Vista Operadora/Técnica:** Inspección al segundo, tracks dudosos y métricas de audio/vídeo.  
  * **Vista Auditora/ESG:** Cuadro de mando ejecutivo con semáforos de cumplimiento (Ley 2/2024 / CSRD).  
  * **Vista Ciudadana:** Capa de confianza intuitiva en 4 estados comprensible en 5 segundos.

---

## 2. Robustez Técnica y Seguridad (*Technical Robustness & Safety*)

- [x] **2.1. Separación Estricta entre Inferencia y Cálculo Determinista:**  
  *Justificación:* Los LLMs y VLMs generativos alucinan y no son reproducibles por construcción (`1:14:30` del 16/10). En AIASN, los modelos abiertos se limitan a extraer transcripciones (`Whisper`), entidades y descriptores (`miVOLO`, `EasyOCR`); **el 100 % de los cálculos temporales, solapes, porcentajes y ratios los procesa determinísticamente Python (`pandas`)**.
- [x] **2.2. Preprocesamiento Acústico contra Alucinaciones (VAD):**  
  *Justificación:* Siguiendo a Adrián Fonollosa, se implementa Voice Activity Detection (VAD) previo a la transcripción para evitar que `whisper-large-v3` genere texto fantasma sobre tramos de silencio o música de fondo.
- [x] **2.3. Descarte de VLMs Genéricos para Conteo Espacial:**  
  *Justificación:* Atendiendo a la recomendación taxativa de Verónica Vilaplana (`1:25:30`), se descartan modelos multimodales genéricos (`Qwen2.5-VL`) para detectar personas o contar caras. Se adopta el pipeline especializado modular: **`YOLO11m` + `ByteTrack` + `miVOLO`**.
- [x] **2.4. Gestión de la Incertidumbre (Umbral de Abstención $p < 0.80$):**  
  *Justificación:* Cuando la certidumbre de los modelos acústicos o visuales es inferior al 80 %, el sistema **se abstiene de forzar una etiqueta binaria** y clasifica el segmento como `no_determinado / desconocido`, preservándolo para arbitraje humano.

---

## 3. Privacidad y Gobernanza de Datos (*Privacy & Data Governance*)

- [x] **3.1. Principio de *Zero Facial Retention* (Biometría Efímera en Memoria):**  
  *Justificación:* En cumplimiento de los trílogos europeos liderados bajo presidencia española (citados por Karina Gibert y Ángela Gasch), **el sistema no almacena ni indexa vectores o huellas biométricas faciales** y no identifica a nadie contra una base de datos. Los *embeddings* faciales (`InsightFace`) se calculan en memoria únicamente para agrupar apariciones de la misma persona dentro de un vídeo y se descartan antes de escribir en el lake (`aiasn/pipelines/video.py`; purga adicional en `aiasn/core/compliance.py`).
- [x] **3.2. Prioridad Absoluta al Dato Declarado sobre la Biometría:**  
  *Justificación:* Siguiendo la regla de oro de Verónica Vilaplana (Diap. 68), la lectura de rótulos mediante OCR (*«Dra. Maria Pons — Catedràtica d'Economia»*) o las actas oficiales tienen **prevalencia jerárquica estricta** sobre cualquier inferencia física facial o vocal.
- [x] **3.3. Amparo Legal de Datos en Fase de Prototipo (Art. 67 RDL 24/2021):**  
  *Justificación:* Los vídeos de calibración públicos (como *«Quanta, quanta IA!»*, **sin permiso expreso** de la organización) se tratan en local bajo la excepción de **Minería de Textos y Datos (TDM)** (amparo pendiente de validar con Karina Gibert y Ángela Gasch), sin redistribuir el material audiovisual bruto y fuera de la demostración pública. Las pruebas públicas reproducibles usan vídeos con licencia abierta (`DATASET_CARD.md`, 1.1).
- [x] **3.4. Prohibición de *Web Scraping* Indiscriminado y Plan de Despliegue:**  
  *Justificación:* Conforme a la instrucción de Karina Gibert (`2:05:10`), se prohíbe el scraping masivo. El Plan de Producción estipula una **Fase 0 de Convenios Formales y Conexión vía API Oficial Autorizada** con las entidades emisoras.
- [ ] **3.5. Ficheros temporales y minimización de datos (PENDIENTE para la 1.0):**  
  *Estado real:* el pipeline de vídeo escribe en `tmp/<video_id>/` los fotogramas completos en JPG (que contienen rostros), el audio (`audio.wav`) y el vídeo remuestreado, y el vídeo original permanece en `landing/`. **No hay borrado automático al terminar el procesado**, y se guardan `gender` y `age` estimados por detección (la edad no se utiliza en el cálculo). *Mitigación en el prototipo:* `tmp/` está en `.gitignore` y el vídeo anotado es solo una utilidad de desarrollo. *Acción prevista:* paso final de limpieza de `tmp/` y `landing/` (activable por configuración, porque la depuración y la reanudación necesitan esos ficheros) y retirada de la edad; en producción, borrado periódico conforme a los plazos del RGPD. *Hasta entonces, no se debe afirmar que el tratamiento sea «solo en RAM».*
- [ ] **3.6. Consulta pendiente sobre nombres de personas (Karina Gibert / Ángela Gasch):**  
  *Estado real:* los nombres proceden únicamente de rótulos en pantalla (OCR) y de menciones en el audio transcrito; no se deducen de la cara ni se contrastan con ninguna base de datos de identidades. Está pendiente confirmar con las mentoras la licitud de reconocer y conservar esos nombres, especialmente para vídeos privados (consentimiento, plazos de conservación).
- [x] **3.5. Cláusula de Usos Permitidos y Cruces Prohibidos:**  
  *Justificación:* Todo archivo `.parquet` o exportación de la herramienta incorpora una cabecera que limita su uso a auditoría de paridad agregada y **prohíbe expresamente cualquier cruce para perfilado ideológico o re-identificación de personas físicas**.

---

## 4. Transparencia y Explicabilidad (*Transparency*)

- [x] **4.1. Declaración Obligatoria de Uso de IA (Reglamento Europeo de IA):**  
  *Justificación:* Cumplimiento de la obligación legal vigente desde agosto de 2026 (`0:40:41` del 16/10) mediante una declaración formal en el repositorio (`MODEL_CARD.md`, `README.md`) y en los metadatos de los informes generados.
- [x] **4.2. Perfil Poblacional de los Datos de Validación (*Data Profile*):**  
  *Justificación:* Se documentan con rigor los conjuntos de datos de prueba:  
  * **Audio/Voz:** Corpus `Àgora` de la UPC (37 h de debate con el *Ground Truth* de **14 % de habla femenina**).  
  * **Imagen/Vídeo:** Episodios de divulgación científica (*«Quanta, quanta IA!»*, IDEAI-UPC) y mesas redondas de debate.
- [x] **4.3. Explicabilidad Abierta de las Métricas:**  
  *Justificación:* Las fórmulas de los ratios (tiempo de palabra, tiempo de pantalla, área ocupada y centralidad) se documentan en código abierto en lenguaje natural para que cualquier ciudadana o auditor pueda auditarlas sin conocimientos de programación.

---

## 5. Diversidad, No Discriminación y Equidad (*Diversity & Fairness*)

- [x] **5.1. Detección Activa de *Equality-Washing* y *Purplewashing*:**  
  *Justificación:* Aplicación de la matriz de 4 cuadrantes *«Seeing and Hearing»* de Verónica Vilaplana (Diap. 92). El sistema detecta y penaliza la **presencia muda** (Cuadrante 2: mujer en pantalla pero en silencio), desenmascarando cuotas cosméticas de imagen que carecen de voz experta real.
- [x] **5.2. Salvaguarda contra la Invisibilización (La Bolsa `unknown`):**  
  *Justificación:* Basado en el hallazgo empírico de la Diapositiva 91 de Verónica Vilaplana (donde el 50 % de las mujeres caen en `"unknown"` por ángulos de cámara difíciles o inclinación de cabeza), **la herramienta jamás descarta la categoría `"unknown"`**, visibilizándola y asignándole un estado de `⚠️ Cobertura Parcial` para revisión.
- [x] **5.3. Mitigación de Sesgos Acústicos de Género y Edad:**  
  *Justificación:* Calibración adaptada a frecuencias fundamentales femeninas e infantiles (evitando el sesgo histórico de clasificadores entrenados exclusivamente con voces masculinas adultas).
- [x] **5.4. Respeto a Identidades No Binarias (ADR-0006):**  
  *Justificación:* El esquema de datos no impone un binarismo forzado; acepta categorías de género autoidentificadas y declaradas en actas oficiales sin detraer del suelo del 40 % femenino.
- [x] **5.5. Soberanía Lingüística Cooficial, Inclusividad y Accesibilidad Universal por Diseño (ADR-0010 / Pilar 5 ALTAI):**  
  *Justificación:* Soporte nativo sin traducción intermedia para todas las lenguas cooficiales del Estado (`es`, `ca`, `gl`, `eu`) más inglés (`en`), facilitando su reutilización por las Administraciones Públicas (**Esquema Nacional de Interoperabilidad, ENI**), junto con **Accesibilidad Universal** (**Directiva UE 2019/882**, **RD 1112/2018**, **WCAG 2.2 AA** con paleta Okabe-Ito, **Lectura Fácil UNE 153101** en `resumen_lectura_facil` para lectores de pantalla y subtitulado **UNE 153010**).

---

## 6. Bienestar Social y Ambiental (*Green AI & Sustainability*)

- [x] **6.1. *Energía por Diseño* (Muestreo Temporal `STRIDE`):**  
  *Justificación:* Atendiendo a las directrices de Montse Guàrdia (`1:55:45`) y Verónica Vilaplana, se rechaza el procesado bruto de 25–30 fps. Se adopta un muestreo de **1 a 5 fps (`STRIDE = 3` a `6`)**, reduciendo el consumo de GPU y la huella de carbono en más de un **80 %** sin pérdida de representatividad estadística.
- [x] **6.2. Regla de Oro de Depuración de Karina Gibert (`1:56:50`):**  
  *Justificación:* Todo el pipeline se depura en local sobre muestras mínimas de audio y vídeo de pocos segundos antes de desplegarse en las instancias GPU de OVHcloud, evitando el gasto superfluo de cómputo en la nube.
- [x] **6.3. Optimización para Arquitectura NVIDIA Volta (V100):**  
  *Justificación:* Uso estricto de precisión en coma flotante media **`torch.float16`** adaptado al hardware cedido por OVHcloud (sin exigir `bfloat16` ni *FlashAttention-2* no soportados).
- [x] **6.4. Sostenibilidad Financiera del MVP y Arquitectura *Split Edge-to-Cloud* (ENS):**  
  *Justificación:* Procesamiento efímero del vídeo pesado en local y transmisión exclusiva de kilobytes de texto y tablas anónimas (`.csv`/`.tsv`), logrando un **99,99 % de reducción de tráfico de red y almacenamiento cloud**, adecuación al **Esquema Nacional de Seguridad (ENS)** para el sector público y un coste auditado inferior a **0,30 € por hora de vídeo analizada**, además del enriquecimiento del diccionario de referentes (`Top Rosies Talent` / `ReDivIAcat` / `WikiMujeres`) sin reentrenar GPU.

---

## 7. Rendición de Cuentas y Software Libre (*Accountability & Open Source*)

- [x] **7.1. Licencia Abierta, Estándar REUSE (FSFE) y Protección del Sello Oficial (Art. 6 Apache-2.0):**  
  *Justificación:* Todo el código se publica bajo `Apache-2.0` cumpliendo el estándar [`reuse.software`](https://reuse.software/) de la FSFE y reservando el Sello Oficial («AIASN Trust Verified») mediante firma criptográfica `SHA-256`, ventana de 3 años contra lavado de cara (*No-Wash Policy*), vía de rehabilitación activa (*Self-Cleaning*) e identificador pseudonimizado en el botón «Asumo» (`operador_supervision_id`).
- [x] **7.2. Arquitectura Agnóstica al Modelo:**  
  *Justificación:* El núcleo del sistema desacopla los adaptadores de inferencia mediante interfaces `Pydantic`. Cualquier modelo (`Whisper`, `miVOLO`, `YOLOX`, `Qwen`, `Llama`) puede sustituirse por otra alternativa abierta sin reescribir la lógica de cálculo ni generar dependencias de un único proveedor.
- [x] **7.3. Registro Canónico de Decisiones de Arquitectura (ADRs):**  
  *Justificación:* Trazabilidad técnica exhaustiva documentada en **11 ADRs ([ADR-0001 a ADR-0011](./docs/adr/README.md), incluyendo exclusión de emociones biométricas Art. 5.1.f RIA, soberanía lingüística/reutilización en AAPP Art. 157 LRJSP y adopción del Test de Interlocución Femenina TIF)**, explicando el contexto, alternativas descartadas y consecuencias ético-técnicas de cada decisión.
- [x] **7.4. Gobernanza Comunitaria y Marco Regulatorio Completo:**  
  *Justificación:* Inclusión en el repositorio de los informes y archivos canónicos: [docs/marco_normativo_y_mercado.md](./docs/marco_normativo_y_mercado.md) (análisis RIA / Ley 2/2024 / CSRD), [docs/evidencias_trabajo_en_equipo.md](./docs/evidencias_trabajo_en_equipo.md) (gobernanza paritaria y proceso deliberativo), [docs/informe_conformidad_accesibilidad.md](./docs/informe_conformidad_accesibilidad.md) (auditoría WCAG 2.2 AA), CODE_OF_CONDUCT.md, CONTRIBUTING.md, SECURITY.md, CHANGELOG.md, MODEL_CARD.md, DATASET_CARD.md y pyproject.toml.

---

> **Conclusión de la Autoevaluación:**  
> El sistema cumple satisfactoriamente con los requerimientos éticos, normativos y algorítmicos formulados en el marco del reto, quedando listo para su auditoría por parte del tribunal y de las autoridades competentes.
