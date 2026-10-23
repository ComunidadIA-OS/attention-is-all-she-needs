# 0009. Exclusión de inferencia biométrica de emociones (AI Act) y postergación de sentiment analysis al roadmap

* **Fecha:** 2026-10-22
* **Estado:** Aceptada
* **Decisores:** Equipo AIASN (Pilar de la Fuente Diez, Rocío Jiménez Villén, Alba Camiña García)
* **Directriz de referencia:** Reglamento Europeo de IA (*EU AI Act*, UE 2024/1689), Arts. 5.1.f, 3.39 y 50, y Directrices de la Comisión Europea sobre Prácticas de IA Prohibidas (C(2025) 884)

---

## Contexto y Problema

Se evaluó la posibilidad de incluir análisis de microexpresiones faciales o tono vocal para inferir el «estado emocional» de las ponentes (ej. «seguridad», «sumisión» o «asertividad»), así como análisis de sentimiento textual (*sentiment analysis*) sobre las citas a referentes femeninos. Esto planteaba riesgos regulatorios severos bajo el recién aprobado *EU AI Act* y dudas metodológicas refutadas por la neurociencia (Lisa Feldman Barrett, 2019).

## Opciones Consideradas

1. **Inferencia de Emociones por Rasgos Faciales o Gestos:**
   * El Art. 3.39 del RIA define el reconocimiento de emociones como la inferencia de estados o intenciones a partir de **datos biométricos** (cara, voz, gestos o postura corporal).
   * El Art. 5.1.f prohíbe taxativamente su uso en entornos laborales y educativos, y lo califica como sistema de **Alto Riesgo** (Anexo III) en el resto de ámbitos públicos.
   * *Decisión:* **Exclusión total del MVP.** La postura o el encuadre solo se analizan como composición geométrica (`area` y `centrality`), sin inferir jamás estados psicológicos internos.
2. **Análisis de Sentimiento Textual (*Entity Sentiment*):**
   * Las directrices de la Comisión Europea (febrero 2025) aclaran que el análisis de texto escrito **no utiliza datos biométricos** y, por tanto, queda fuera de la prohibición del RIA.
   * Sin embargo, genera altas tasas de falsos positivos en debates parlamentarios o científicos y no constituye un KPI exigido por los evaluadores del reto.
   * *Decisión:* **Postergación consciente al roadmap futuro (Fase 2).** Se prioriza la extracción de autoridad y menciones (*named entity recognition*) con `GLiNER` sin añadir latencia de sentiment.

## Decisión Adoptada

Se excluye radicalmente la inferencia biométrica de emociones por imperativo ético-legal y se deriva el sentiment analysis textual al backlog de fases futuras.

## Consecuencias

* **Positivas:**
  * Cumplimiento preventivo total del *EU AI Act* (auditoría ética inexpugnable).
  * Enfoque sobrio y científico: se miden hechos observables (segundos de habla, presencia en encuadre, rótulos de autoría), no conjeturas subjetivas sobre el estado anímico.
  * Reducción de latencia en inferencia.
* **Compromisos asumidos:**
  * El sistema no califica el «tono» del debate, sino la distribución objetiva del tiempo y la autoridad de los turnos de palabra.

