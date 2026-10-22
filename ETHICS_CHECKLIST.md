# Autoevaluación Ética y Regulatoria (ETHICS_CHECKLIST)
## Proyecto: «Attention Is All She Needs» (AIASN) — Reto «Mujeres por la IA Abierta»

> **Ficha Técnica de Conformidad:**  
> * **Marcos de Referencia Oficiales:** Directrices Éticas para una IA Fiable (*Ethics Guidelines for Trustworthy AI* / `ALTAI`, Comisión Europea HLEG 2019/2020), Reglamento (UE) 2024/1689 (*Reglamento Europeo de Inteligencia Artificial / RIA*), Guías Técnicas del Sandbox Regulatorio Español de IA (SEDIA / AESIA) y Modelo `PIO` (*Principis d'Intel·ligència Artificial Oberta*, OEIAC / UdG).  
> * **Clasificación de Riesgo según el RIA:** Sistema de **Riesgo Limitado / Transparencia (Art. 50 RIA)** en fase de prototipo de I+D, incorporando de forma preventiva salvaguardas de sistemas de Alto Riesgo (*High-Risk AI*) por diseño.  
> * **Equipo de Auditoría:** Alba Camiña García, Rocío Jiménez Villén y Pilar de la Fuente Diez (Equipo 1).

---

## Matriz Resumen de Cumplimiento Ético por Principio

| # | Principio de la IA Fiable (ALTAI / RIA) | Estado | Salvaguarda Técnica Principal en el Repositorio | Referencia en Formaciones |
| :-: | :--- | :---: | :--- | :--- |
| **1** | **Agencia y Supervisión Humana** | ✅ **Verificado** | Pantalla de revisión con botón operativo *«Asumo / No asumo»* (*HitL*). | Karina Gibert (`1:00:50`) y Ángela Gasch |
| **2** | **Robustez Técnica y Seguridad** | ✅ **Verificado** | Separación determinista: Inferencia IA abierta + Cálculo Python sin alucinaciones. | Fonollosa (VAD/Whisper), Vilaplana (VLMs) |
| **3** | **Privacidad y Gobernanza de Datos** | ✅ **Verificado** | *Zero Facial Retention* (biometría efímera en RAM) y amparo Art. 67 RDL 24/2021. | Karina Gibert (`2:05:10`) y Ángela Gasch |
| **4** | **Transparencia y Explicabilidad** | ✅ **Verificado** | Declaración RIA (obligatoria desde ago 2026) y *Data Profile* de `Àgora` (14%). | Jorge Teixeira y Karina Gibert (`0:40:41`) |
| **5** | **Diversidad, Equidad y No Sesgo** | ✅ **Verificado** | Detector de *Equality-Washing* (4 cuadrantes) y tratamiento de bolsa `unknown`. | Vilaplana (Diap. 91-92) y Karina (Diap. 10) |
| **6** | **Bienestar Social y Ambiental** | ✅ **Verificado** | *Green AI*: Muestreo STRIDE (1-5 fps) con ahorro $>80\%$ en GPU y coste $<0,30$ €/h. | Montse Guàrdia (`1:55:45`) y David Buenhombre |
| **7** | **Rendición de Cuentas** | ✅ **Verificado** | Arquitectura agnóstica al modelo, suite ADRs y trazabilidad fotograma a fotograma. | Jorge Teixeira (ComunidadIA-OS) y ALTAI |

---

## 1. Agencia Humana y Supervisión (*Human Agency & Oversight*)

- [x] **1.1. Supervisión Operativa en la Interfaz (Botón *«Asumo / No asumo»*):**  
  *Justificación:* Conforme a la advertencia de Karina Gibert y Ángela Gasch sobre el escándalo *Toeslagenaffaire* en Países Bajos, el sistema **nunca emite un informe definitivo de forma autónoma**. La interfaz presenta un panel de supervisión *Human-in-the-Loop* (HitL) donde el personal responsable de igualdad o auditoría debe pulsar expresamente **«Asumo las métricas»** o **«No asumo / Derivar a revisión manual»** tras inspeccionar los casos dudosos.
- [x] **1.2. Asistente que Aumenta, No que Sustituye:**  
  *Justificación:* El software está conceptualizado como una herramienta de apoyo analítico que automatiza la ingesta tediosa de minutados, pero deja la valoración contextual y jurídica del cumplimiento a la persona operadora.
- [x] **1.3. Segmentación de Vistas por Rol:**  
  *Justificación:* Se diseñan tres niveles de visualización para evitar la sobrecarga informativa:  
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
  *Justificación:* En cumplimiento de los trílogos europeos liderados bajo presidencia española (citados por Karina Gibert y Ángela Gasch), **el sistema no almacena ni indexa vectores o huellas biométricas faciales**. La detección facial (`InsightFace` / `miVOLO`) se ejecuta en memoria volátil (RAM) únicamente para clasificar atributos estadísticos agregados y se destruye en caliente.
- [x] **3.2. Prioridad Absoluta al Dato Declarado sobre la Biometría:**  
  *Justificación:* Siguiendo la regla de oro de Verónica Vilaplana (Diap. 68), la lectura de rótulos mediante OCR (*«Dra. Maria Pons — Catedràtica d'Economia»*) o las actas oficiales tienen **prevalencia jerárquica estricta** sobre cualquier inferencia física facial o vocal.
- [x] **3.3. Amparo Legal de Datos en Fase de Prototipo (Art. 67 RDL 24/2021):**  
  *Justificación:* Los vídeos de prueba públicos (como *«Quanta, quanta IA!»*) se tratan bajo la excepción de **Minería de Textos y Datos (TDM) con fines de investigación e innovación** sin redistribución comercial del material audiovisual bruto.
- [x] **3.4. Prohibición de *Web Scraping* Indiscriminado y Plan de Despliegue:**  
  *Justificación:* Conforme a la instrucción de Karina Gibert (`2:05:10`), se prohíbe el scraping masivo. El Plan de Producción estipula una **Fase 0 de Convenios Formales y Conexión vía API Oficial Autorizada** con las entidades emisoras.
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
- [x] **5.4. Respeto a Identidades No Binarias:**  
  *Justificación:* El esquema de datos no impone un binarismo forzado; acepta categorías de género autoidentificadas y declaradas en actas oficiales.

---

## 6. Bienestar Social y Ambiental (*Green AI & Sustainability*)

- [x] **6.1. *Energía por Diseño* (Muestreo Temporal `STRIDE`):**  
  *Justificación:* Atendiendo a las directrices de Montse Guàrdia (`1:55:45`) y Verónica Vilaplana, se rechaza el procesado bruto de 25–30 fps. Se adopta un muestreo de **1 a 5 fps (`STRIDE = 3` a `6`)**, reduciendo el consumo de GPU y la huella de carbono en más de un **80 %** sin pérdida de representatividad estadística.
- [x] **6.2. Regla de Oro de Depuración de Karina Gibert (`1:56:50`):**  
  *Justificación:* Todo el pipeline se depura en local sobre muestras mínimas de audio y vídeo de pocos segundos antes de desplegarse en las instancias GPU de OVHcloud, evitando el gasto superfluo de cómputo en la nube.
- [x] **6.3. Optimización para Arquitectura NVIDIA Volta (V100):**  
  *Justificación:* Uso estricto de precisión en coma flotante media **`torch.float16`** adaptado al hardware cedido por OVHcloud (sin exigir `bfloat16` ni *FlashAttention-2* no soportados).
- [x] **6.4. Sostenibilidad Financiera del MVP:**  
  *Justificación:* Coste de mantenimiento e inferencia auditado por debajo de **0,30 € por hora de vídeo analizada**, garantizando la viabilidad de adopción para pymes y medios modestos.

---

## 7. Rendición de Cuentas y Software Libre (*Accountability & Open Source*)

- [x] **7.1. Licencia Abierta y Estándar *Open Source AI* (OSI):**  
  *Justificación:* Todo el código se publica bajo licencias abiertas estándar compatibles (`Apache 2.0` / `MIT`), cumpliendo el Art. 10 de las bases y las pautas de Jorge Teixeira (Oficina Técnica de ComunidadIA-OS).
- [x] **7.2. Arquitectura Agnóstica al Modelo:**  
  *Justificación:* El núcleo del sistema desacopla los adaptadores de inferencia mediante interfaces `Pydantic`. Cualquier modelo (`Whisper`, `miVOLO`, `Qwen`, `Llama`) puede sustituirse por otra alternativa abierta sin reescribir la lógica de cálculo ni generar dependencias de un único proveedor.
- [x] **7.3. Registro Canónico de Decisiones de Arquitectura (ADRs):**  
  *Justificación:* Trazabilidad técnica exhaustiva documentada en 8 ADRs (`ADR-001` a `ADR-008`), explicando el contexto, alternativas descartadas y consecuencias ético-técnicas de cada decisión.
- [x] **7.4. Gobernanza Comunitaria Completa:**  
  *Justificación:* Inclusión en el repositorio de los 7 archivos canónicos: `CODE_OF_CONDUCT.md`, `CONTRIBUTING.md`, `SECURITY.md`, `CHANGELOG.md`, `MODEL_CARD.md`, `DATASET_CARD.md` y `pyproject.toml`.

---

> **Conclusión de la Autoevaluación:**  
> El sistema cumple satisfactoriamente con los requerimientos éticos, normativos y algorítmicos formulados en el marco del reto, quedando listo para su auditoría por parte del tribunal y de las autoridades competentes.

