# 0009. Exclusión de inferencia biométrica de emociones (AI Act) y rescate desacoplado del Índice de Clima Conversacional

* **Fecha:** 2026-10-23
* **Estado:** Aceptada
* **Decisores:** Equipo AIASN (Pilar de la Fuente Diez, Rocío Jiménez Villén, Alba Camiña García)
* **Referencia Legal:** Arts. 3.39, 5.1.f, 50 del Reglamento (UE) 2024/1689 (RIA) y Directrices C(2025) 884 de la Comisión Europea.
* **Referencia Metodológica:** Dimensiones 3 y 4 de `03_propuestas_y_diseno_proyecto.md` (*Ética Mínima* de Adela Cortina sobre la interlocución válida).

---

## Contexto y Problema

La inferencia de estados emocionales (ansiedad, agresividad, inseguridad) mediante rasgos biométricos (facciones faciales o señal acústica de voz) constituye una práctica prohibida en entornos laborales y educativos (Art. 5.1.f RIA) y de Alto Riesgo en el resto de aplicaciones (Anexo III punto 1.c). Además, presenta un grave sesgo de género al penalizar como «agresiva» o «emocional» la intervención firme de mujeres en debates técnicos.

Por otro lado, el equipo necesita auditar el clima y la asertividad del debate público (a quién se interrumpe, en qué registro léxico se debate y cómo se valida a las ponentes).

## Opciones Consideradas

1. **Opción A (Inferencia Emocional Multimodal):** Intentar predecir emociones desde la voz y la cara. *(Descartada radicalmente por ser práctica prohibida/alto riesgo según el RIA y reproducir sesgos sexistas).*
2. **Opción B (Exclusión Total de Todo Análisis Semántico o de Tono):** Limitar el sistema exclusivamente a milisegundos y cajas de vídeo. *(Descartada por empobrecer el potencial del stack de NLP y omitir las dimensiones de dinámica conversacional).*
3. **Opción C (Adopción — Rescate Desacoplado del Índice de Clima Conversacional sobre Texto Transcrito):** Excluir la biometría emocional de raíz y habilitar un módulo opcional en `aiasn/nlp/sentiment.py` que analiza exclusivamente las cadenas de texto transcritas (ASR), midiendo el registro discursivo agregado (Técnico/Asertivo, Colaborativo, Disenso) conforme a las directrices de la Comisión Europea (el texto no es dato biométrico).

## Decisión Adoptada

Se adopta la **Opción C**:
1. **Exclusión biométrica absoluta:** Prohibido deducir estados anímicos o psicológicos desde la voz, el rostro o la postura corporal.
2. **Giro epistémico hacia el espacio discursivo:** No se juzga ni etiqueta psicológicamente a la persona; se mide objetivamente el clima del espacio conversacional.
3. **Desacoplamiento modular (ADR-002):** El análisis de registro léxico sobre texto enriquece el dashboard de visualización sin condicionar la ejecución del motor determinista de solape temporal (Issue #4).

## Consecuencias

* **Positivas:**
  * Cumplimiento estricto y preventivo del Reglamento Europeo de IA (Art. 5 y Art. 50).
  * Recuperación de las dimensiones de interlocución válida y autoridad epistémica (Adela Cortina).
  * Enfoque sobrio y reproducible basado en evidencias textuales verificables, sin invadir la intimidad de las personas.
* **Compromisos asumidos:**
  * El módulo de registro discursivo debe usar importación diferida (*lazy import*) y operar exclusivamente sobre la columna `transcripcion`.

## Matriz de Veredicto Ético-Legal (RIA vs. Karina Gibert / ALTAI)

| Enfoque Técnico | Estado Legal (RIA / AI Act) | Estado Ético (Karina Gibert / ALTAI) | Veredicto Operativo AIASN |
| :--- | :--- | :--- | :--- |
| **Sentiment individual del Hablante** *(etiquetar si la ponente está «enfadada», «agresiva» o «negativa»)* | **Legal** (procesar texto transcrito no es dato biométrico según C(2025) 884). | **Inadmisible / Mala praxis**: genera indefensión, perfila a la persona y castiga la asertividad femenina. | **Descartado permanentemente.** |
| **Métricas Conversacionales Objetivas** *(interrupciones sufridas, tiempo de turno, solapamientos)* | **Legal** (sin biometría ni inferencia subjetiva interna). | **Excelente / Recomendado**: audita hechos empíricos de desigualdad conversacional (diapo Gibert sobre reuniones). | **Implementado en el Core (`[core]` / Issue #4).** |
| **Índice de Clima Conversacional (Adela Cortina)** *(asertividad técnica, descalificación o condescendencia en el texto)* | **Legal** (clasificación NLP de registros textuales con transparencia Art. 50). | **Plenamente Conforme**: audita el espacio deliberativo colectivo con supervisión humana (*HitL* y pantalla «Asumo/No asumo»). | **Rescatado para el Roadmap v1.0.0 (ADR-009).** |

> **Justificación canónica ante el tribunal:** *«Aunque el RIA permite procesar texto sin restricciones biométricas, en atención al marco ético de la Comisión Europea (ALTAI) y las directrices magistrales de la Dra. Karina Gibert ("pasar compliance legal no garantiza cumplir el código ético; se puede lanzar algo legal que genere indefensión o fomente desigualdades"), AIASN excluye conscientemente el sentiment individual para evitar sesgos sobre las personas, redirigiendo la inferencia hacia la objetividad de las interrupciones y el clima dialéctico colectivo con supervisión humana (Human-in-the-Loop).*»

