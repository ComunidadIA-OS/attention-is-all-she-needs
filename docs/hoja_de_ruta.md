<!--
SPDX-FileCopyrightText: 2026 Equipo 1: Attention Is All She Needs (Alba Camiña García, Pilar de la Fuente Diez, Rocío Jiménez Villén)
SPDX-License-Identifier: Apache-2.0
-->

# Hoja de ruta completa

Detalle de lo pendiente a 29/10/2026. El resumen y el alcance de la entrega están en el [README](../README.md#-estado-actual-y-hoja-de-ruta-a-29102026).

[← Volver al README](../README.md)

---

**Pretendemos hacer y está pendiente (previsto para v1.0 y posteriores):**

| Área | Qué falta | Dónde se detalla |
| :--- | :--- | :--- |
| **Seguridad del despliegue** | **HTTPS (TLS)**, autenticación y control de acceso por roles, CORS restringido, cifrado en reposo, aislar el lanzador de contenedores (hoy la API monta `docker.sock`) y análisis de vulnerabilidades en dependencias. **Hoy la API y el front no deben exponerse a Internet.** | `docs/marco_normativo_y_mercado.md` (punto 11 del checklist), Anexo C del [borrador de contrato](./contrato_servicios_y_condiciones_de_uso_borrador.md) |
| **Privacidad y conservación** | Plazo de conservación de las tablas derivadas (el vídeo y sus temporales ya se borran al terminar) | `ETHICS_CHECKLIST.md` (3.5) |
| **Supervisión humana** | Que la revisión recalcule las métricas y condicione el informe, identificar a cada operadora con un pseudónimo propio, vistas por rol e integrar `emitir_sello_auditoria` en la API | `ETHICS_CHECKLIST.md` (1.1), [ADR-0005](./adr/0005-tratamiento-incertidumbre-abstencion-hitl.md) |
| **Atribución del género** | Decidir el género solo con evidencias textuales y dejar cara y voz en un modo de investigación (**propuesta, sin implementar**) | [ADR-0013](./adr/0013-atribucion-de-genero-por-evidencias-textuales.md) |
| **Vistas por rol y capa ciudadana** | Vistas operadora, auditora y ciudadana; valoraciones de la ciudadanía y QR real (hoy solo existe una maqueta en una rama de diseño) | `ETHICS_CHECKLIST.md` (1.3) |
| **Frontend alternativo** | Dashboard accesible con interfaz en castellano, catalán, galego, euskara e inglés, tres fases de material (preproducción, edición y publicado), réplica de las métricas de la especificación, arbitraje humano y pruebas propias, en la rama `feat/frontend-dashboard`. **No está integrado**: el frontend de esta entrega es `frontend-piloto/` y su interfaz solo existe en castellano | rama `feat/frontend-dashboard`, [ADR-0010](./adr/0010-soberania-linguistica-cooficial-accesibilidad-universal-aapp.md) |
| **Prevención en edición (*Shift-Left Parity*)** | Plugins y extensiones ligeras con disclaimers preventivos en herramientas de grabación y montaje (`OBS Studio`, `DaVinci Resolve`, `Adobe Premiere`, `Audacity`) que alertan en caliente al editor de los ratios de voz, pantalla y reconocimiento del protagonismo femenino antes de emitir | `CODE_OF_CONDUCT.md` (Art. 4.2), `GLOSSARY.md` (término 18) |
| **Dinámicas de debate e interrupciones (*manterrupting*)** | Medición objetiva de interrupciones asimétricas por género y solapes acústicos desde marcas de tiempo del ASR (sin biometría emocional, conforme al Art. 5 del RIA) | [ADR-0009](./adr/0009-exclusion-emociones-ai-act-postergacion-sentiment.md), `GLOSSARY.md` (término 11) |
| **Lenguaje inclusivo y no sexista** | Módulo desacoplado (`aiasn-nlp-inclusive`) para detección de masculinos genéricos y sugerencia de alternativas no sexistas en transcripciones (LO 3/2007, Art. 14.11), postergado en v0.1.0 por latencia y *Green AI* | `docs/marco_normativo_y_mercado.md`, [ADR-0010](./adr/0010-soberania-linguistica-cooficial-accesibilidad-universal-aapp.md) |
| **Escala** | Cola de procesado (hoy un vídeo cada vez; la API responde 409 si hay otro en marcha) | `aiasn/api/app.py` (responde 409 si ya hay un vídeo en proceso) |
| **Licencias** | Sustituir Ultralytics YOLO (AGPL-3.0) por un adaptador permisivo (YOLOX) y revisar la licencia de los pesos faciales (InsightFace: uso no comercial) | [Modo C](./modo_sector_publico.md) |
| **Validación** | Evaluación completa de extremo a extremo con el pipeline unificado y métricas formales WER/DER en todo el corpus (la calibración exploratoria de componentes de audio y el Ground Truth del 14,61 % ya se completaron: [informe](./evaluacion_experimental_agora.md)), y medición del ahorro de cómputo frente al análisis a 30 fps. **Ya medido:** tiempos, tokens del LLM y SHA-256 de los 6 vídeos de la demo en una RTX 4060 Laptop | `DATASET_CARD.md` (1.2 y 1.3), `TESTING.md` (2.1), [evaluación Àgora](./evaluacion_experimental_agora.md) |
| **Observabilidad** | Registro de accesos (las decisiones de revisión ya se guardan en `supervision/`; Langfuse, opcional, solo traza las llamadas al modelo de lenguaje) | `docker-compose.yml` (perfil `langfuse`) |
| **Marco legal para terceros** | Revisión jurídica del contrato de servicios y de la plantilla del Art. 50.3, contrato de encargo con OVHcloud, y revisión de las directrices finales de la Comisión sobre clasificación (previstas a finales de 2026) | [ADR-0012](./adr/0012-marco-normativo-omnibus-digital-y-proyecto-de-ley.md), [plantilla Art. 50.3](./plantilla_aviso_art50_y_encargo_tratamiento.md) |
| **Fichas** | Revisión final de `MODEL_CARD.md` y `DATASET_CARD.md`: criterio sobre los nombres de personas en la ficha de datos y versión de las licencias CC BY de YouTube | `DATASET_CARD.md` |


Seguimiento día a día en el [tablero del equipo](https://github.com/users/ewigkeitt-cloud/projects/1).
