<!--
SPDX-FileCopyrightText: 2026 Equipo 1: Attention Is All She Needs (Alba Camiña García, Pilar de la Fuente Diez, Rocío Jiménez Villén)
SPDX-License-Identifier: Apache-2.0
-->

# Evaluación Experimental sobre el Corpus Àgora (UPC)
## Validación Empírica de Componentes de Audio, Diarización y Clasificación de Voz

> **Proyecto:** Attention Is All She Needs (AIASN) — Reto «Mujeres por la IA Abierta»  
> **Fecha de ejecución:** 29 de octubre de 2026  
> **Autora de la evaluación:** Alba Camiña García (con componentes de backend y clasificador de voz de Rocío Jiménez Villén)  
> **Marco metodológico:** [ADR-0007 (Estrategia dual de datasets)](./adr/0007-estrategia-dual-datasets-agora-quanta.md), [TESTING.md](../TESTING.md) (§2.1) y directrices de tutoría del Dr. José Adrián Rodríguez Fonollosa (TALP-UPC).

---

## 1. Contexto y Objetivos

Durante la sesión formativa oficial del 15 de octubre de 2026, el **Dr. José Adrián Rodríguez Fonollosa** (catedrático de la UPC e investigador de TALP) puso a disposición de los equipos el corpus de debate televisivo **`Àgora`** (emitido por TV3 / Televisió de Catalunya), destacando un hallazgo sociológico y computacional clave:
* El corpus dispone de anotación manual pericial transectorial realizada en 2008–2009 mediante la herramienta *Transcriber*.
* Dicha anotación establece un **Ground Truth histórico de habla femenina de aproximadamente el 14 %** (con el 86 % restante copado por intervenciones masculinas).

El objetivo de esta campaña experimental es someter a prueba objetiva los componentes de audio de AIASN sobre este corpus de referencia para:
1. **Calcular de forma exacta y exhaustiva el *Ground Truth*** del corpus completo sobre sus ficheros de anotación original XML (`agora_trs.gz`).
2. **Evaluar el clasificador acústico de género por voz** del proyecto ([`VoiceGenderClassifier`](../aiasn/model_adapters/voice_gender_classifier.py), modelo Wav2Vec2 `prithivMLmods/Common-Voice-Gender-Detection`) sobre los turnos de habla anotados a mano (**Prueba 1**).
3. **Evaluar la integración de `whisper-large-v3` diarizado** en los AI Endpoints de OVHcloud junto con el clasificador acústico sobre fragmentos de audio reales de los debates (**Prueba 2**).
4. **Verificar los costes reales de inferencia y la viabilidad de cómputo (*Green AI*)** en la nube europea.

---

## 2. Metodología y Corpus

* **Corpus de audio:** `agora.gz` (70 ficheros de audio en formato WAV, 16 kHz mono, 16 bit PCM, total de 36,9 horas de grabación).
* **Corpus de anotación:** `agora_trs.gz` (57 ficheros XML de Transcriber con marcas temporales de cambio de turno, identificación de hablantes y atributo de género `male` / `female`).
* **Regla de agregación de referencia:** Se computa el tiempo neto de habla de intervenciones individuales de un único hablante. Las secciones de solapamiento multiparlante o música/ruido de fondo sin etiqueta de género unívoca se excluyen del denominador de género binario, contabilizándose en la métrica global de cobertura acústica.

### Cálculo del *Ground Truth* Global del Corpus (57 debates analizados)

El análisis matemático automatizado de los 57 ficheros XML de anotación arroja las siguientes magnitudes consolidadas:

| Parámetro de Referencia | Valor Medido | Proporción |
| :--- | :---: | :---: |
| **Tiempo total de habla femenina anotada** | **5,04 horas** (18.145,2 s) | **14,61 %** |
| **Tiempo total de habla masculina anotada** | **29,47 horas** (106.108,8 s) | **85,39 %** |
| **Tiempo de habla con solape multiparlante** | 1,11 horas (4.004,1 s) | — |
| **Tiempo total de habla individual neta** | 34,51 horas (124.254,0 s) | 100,0 % |

> 📌 **Conclusión del Ground Truth:** El cálculo empírico exacto del equipo fija la presencia femenina en el corpus en el **14,61 %**, confirmando con precisión decimal la cifra del ~14 % señalada por Fonollosa.

---

## 3. Prueba 1: Precisión del Clasificador de Voz sobre Anotaciones Humanas

Se seleccionó una muestra diversa de **6 debates completos** (177 minutos de habla individual neta distribuidos en **438 turnos de palabra**), evaluando si el clasificador acústico Wav2Vec2 asigna correctamente el género a partir del audio cortado según las marcas de tiempo humanas.

* **Parámetros del clasificador:** `min_seconds = 0.5`, `max_seconds = 15.0` (análisis de los primeros 15 s de cada intervención), ejecutado en CPU.

### Resultados por debate

| Identificador del Debate | Habla Femenina Anotada (GT) | Habla Femenina Estimada | Desviación Absoluta |
| :--- | :---: | :---: | :---: |
| `2007_01_08_a` | 6,0 % | 5,0 % | −1,0 pp |
| `2007_01_15_a` | 26,3 % | 23,8 % | −2,5 pp |
| `2007_02_05_a` | 69,9 % | 66,0 % | −3,9 pp |
| `2007_02_12_a` | 13,9 % | 5,6 % | −8,3 pp |
| `2007_03_05_a` | 17,2 % | 0,0 % | −17,2 pp |
| `2007_04_23_a` | 0,0 % | 0,0 % | 0,0 pp |
| **Muestra Agregada (6 debates)** | **21,3 %** | **15,9 %** | **−5,4 pp** |

### Métricas de Clasificación

* **Exactitud global ponderada por tiempo de habla:** **94,5 %**.
* **Recall masculino:** **100,0 %**. El sistema **no clasificó ni un solo segundo de voz masculina como femenina** (0 segundos de falsos positivos femeninos).
* **Recall femenino:** **74,3 %**. Se clasificaron erróneamente 582 segundos de voz femenina como masculina en 51 intervenciones.

> 🔍 **Hallazgo pericial de ingeniería:** El error femenino no es aleatorio ni difuso: **se concentró de forma crítica en dos mujeres con timbres vocales específicos** (una contertulia en `2007_03_05_a` con 283 s clasificada al 0 % de acierto con confianza media de 1,00; y otra en `2007_02_12_a` con acierto del 38 % y confianza 0,98).  
> **Implicación ética directa:** El clasificador acústico puede errar con **alta confianza matemática ($p > 0,95$)**. Esto valida de manera empírica e irrefutable por qué AIASN **nunca debe basar el género exclusivamente en la señal de voz o cara** ([ADR-0013](./adr/0013-atribucion-de-genero-por-evidencias-textuales.md)) y por qué la pantalla de supervisión humana ([HitL, ADR-0005](./adr/0005-tratamiento-incertidumbre-abstencion-hitl.md)) es un imperativo de diseño.

---

## 4. Prueba 2: Pipeline de Audio Completo (Whisper Diarizado + Clasificador)

Se evaluó el comportamiento coordinado de la transcripción con diarización remota en **OVHcloud AI Endpoints** (`whisper-large-v3`, parámetro `"diarize": "true"`, forzando `language="ca"`) y el clasificador acústico sobre los primeros 10 minutos de dos debates representativos.

* **Metodología de emparejamiento:** Los segmentos emitidos por Whisper se emparejan con los hablantes del ground truth mediante el criterio de **máximo solape temporal acumulado**.

| Métrica / Dimensión | Debate `2007_02_12_a` (10 min) | Debate `2007_01_15_a` (10 min) |
| :--- | :---: | :---: |
| Habla individual anotada manualmente | 574 s | 554 s |
| Habla individual detectada por Whisper | 593 s | 579 s |
| Desviación temporal de detección | +3,3 % | +4,5 % |
| Turnos y hablantes detectados por Whisper | 18 turnos (5 hablantes) | 8 turnos (5 hablantes) |
| Hablantes reales en la anotación | 6 hablantes | 6 hablantes |
| **% femenino según Ground Truth manual** | **16,7 %** | **35,2 %** |
| **% femenino real de los hablantes de Whisper** | **16,8 %** | **33,8 %** |
| **% femenino estimado por el pipeline** | **0,0 %** | **33,8 %** |
| **Acierto del pipeline sobre el audio diarizado** | **83,2 %** | **100,0 %** |
| Tiempo de respuesta de Whisper en OVHcloud | 47 segundos | 59 segundos |

### Hallazgos de la Prueba 2

1. **Alta fidelidad temporal de Whisper Diarizado:** La proporción femenina reconstruida a partir de los turnos de Whisper (16,8 % y 33,8 %) se sitúa a **menos de 1,4 puntos porcentuales** del ground truth humano (16,7 % y 35,2 %). Whisper delimita quién habla y durante cuánto tiempo con extraordinaria precisión.
2. **Replicación del sesgo acústico individual:** En el debate `01_15_a`, el acierto es del **100,0 %**. En el debate `02_12_a`, la contertulia cuyo timbre ya dio error en la Prueba 1 vuelve a ser clasificada como voz masculina, llevando la estimación a 0,0 %.
3. **Longitud de turnos y ventana de clasificación:** Whisper tiende a agrupar intervenciones en bloques largos (de 30 a 70 s de media). Como el clasificador analiza únicamente los primeros 15 s (`max_seconds=15`), turnos prolongados se deciden por su fragmento inicial.

---

## 5. Medición de Recursos y Eficiencia (*Green AI*)

La ejecución de la Prueba 2 sobre la infraestructura de OVHcloud proporcionó datos reales de coste y latencia:

* **Latencia de transcripción y diarización:** ≈ 5 a 6 segundos de tiempo de cómputo por cada minuto de audio analizado (un vídeo de 10 minutos se procesa en menos de 1 minuto).
* **Coste económico real:**
  $$\text{Coste por 20 minutos} \approx 0{,}049 \text{ \euro} \quad \longrightarrow \quad \approx 0{,}147 \text{ \euro / hora de audio}$$
  La cifra empírica coincide exactamente con el precio de tarifa oficial de OVHcloud AI Endpoints (**≈ 0,15 € / hora**).
* **Consumo de tokens LLM:** **0 tokens** consumidos en la fase de audio y cálculo estadístico determinista, validando el principio de diseño de [ADR-0001](./adr/0001-separacion-estricta-inferencia-calculo.md).

---

## 6. Trazabilidad y Reproducibilidad

Todo el material utilizado para la ejecución de estas pruebas se encuentra documentado y empaquetado para su verificación:

* **Paquete de datos y scripts de contraste:** Sincronizado en la carpeta compartida del equipo en Google Drive:  
  `Reto Mujeres por la IA Abierta/Prueba_Agora_componentes_audio/`
* **Ficheros de resultados generados:**
  * `resultado_prueba1_clasificador_voz.csv`: Registro de los 438 turnos clasificados con marcas de tiempo, predicción, confianza y ground truth (sin datos biométricos ni textos personales).
  * `resultado_prueba2_whisper_y_clasificador.csv`: Registro de turnos de Whisper emparejados.
  * `agora_referencia.csv`: Resumen cuantitativo de los 57 debates del corpus.
  * `comparar_audio_turns.py`: Script de contraste reproducible para comparar la salida del almacén Medallion (`bronze/audio_turns`) contra el Ground Truth.

---

## 7. Conclusiones para la Gobernanza de AIASN

1. **Confirmación del Ground Truth de Fonollosa:** Queda acreditado formalmente el **14,61 %** de presencia femenina en debates históricos de TV3, sirviendo como línea base canónica para contrastar la hipótesis de aniquilación simbólica.
2. **Justificación empírica de la supervisión humana (*HitL*):** Dado que los clasificadores acústicos pueden fallar con certidumbre aparente en timbres vocales singulares, el botón **«Asumo / No asumo»** del dashboard y el cortafuegos ético de incertidumbre no son adornos de interfaz, sino salvaguardas técnicas indispensables exigidas por el Art. 14 del Reglamento Europeo de IA.
3. **Validación del modelo económico de nube europea:** Un coste inferior a 0,15 € por hora de audio sitúa a AIASN como una solución tecnológicamente viable y económicamente sostenible para su despliegue continuo en medios públicos y corporaciones.
