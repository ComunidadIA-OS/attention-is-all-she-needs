# ADR-0012: Marco normativo vigente tras el Ómnibus Digital de IA y el Proyecto de Ley Orgánica de gobernanza de la IA como norte no vinculante

* **Estado:** **Propuesta** (pendiente de validación de Pilar y Rocío; consulta abierta a Ángela Gasch y Karina Gibert)
* **Fecha:** 2026-10-28
* **Decisores:** Alba Camiña García (propuesta), Pilar de la Fuente Diez y Rocío Jiménez Villén (validación)
* **Referencias principales:** Reglamento (UE) 2024/1689 (RIA); Reglamento (UE) 2026/1744 («Ómnibus Digital de IA»); Proyecto de Ley Orgánica para el buen uso y la gobernanza de la inteligencia artificial (Expediente 121/000096, BOCG, Congreso de los Diputados, XV Legislatura, Serie A, núm. 97-1, 12 de junio de 2026)

---

## 1. Contexto

Desde el 14 de octubre se han ido concretando dos novedades que afectan a cómo justificamos nuestras decisiones:

1. **El Ómnibus Digital de IA** modifica el calendario del RIA. Según las fuentes secundarias consultadas (artículos de despachos y de artificialintelligenceact.eu; el texto del DOUE no ha podido descargarse de forma automática y **está pendiente de contrastar a mano**), el Reglamento (UE) 2026/1744 se publicó el 24/07/2026 y entró en vigor el 27/07/2026. **Aplaza** las obligaciones de los sistemas de alto riesgo del Anexo III al **2 de diciembre de 2027** y las del Anexo I al **2 de agosto de 2028**. **No aplaza** las prácticas prohibidas (desde el 02/02/2025) ni las obligaciones de transparencia del **Art. 50**, aplicables desde el **02/08/2026**.
2. **El Proyecto de Ley Orgánica para el buen uso y la gobernanza de la IA** (Consejo de Ministros, 26/05/2026; publicado en el BOCG el 12/06/2026, plazo de enmiendas hasta el 30/06/2026) adapta el ordenamiento español al RIA. Según nos trasladaron las mentoras en las sesiones, **decayó con la disolución de las Cortes** y no llegó a aprobarse. Esa circunstancia **no está verificada por el equipo en una fuente oficial**; hasta confirmarla en congreso.es, se cita siempre como «proyecto de ley» y nunca como norma vigente.

**Contenido del proyecto relevante para nosotras** (leído directamente en el BOCG):

| Artículo | Contenido | Por qué nos importa |
|---|---|---|
| 1 | Objeto: gobernanza y supervisión, espacios controlados de pruebas, buen uso en el sector público estatal y régimen sancionador | Es una ley de adaptación del RIA, no añade obligaciones técnicas propias |
| 5 | La AESIA es autoridad de vigilancia por defecto; la **AEPD** lo es de las prácticas prohibidas del Art. 5.1.e y g del RIA y de la biometría del Anexo III.1.a y b | Confirma que la biometría y la categorización biométrica se vigilan desde protección de datos |
| 11 | La AESIA establece el espacio controlado de pruebas (sandbox) obligatorio | Marco en el que se inscribe la formación recibida (SEDIA/AESIA) |
| 12 | Sector público estatal: inventario de sistemas de IA, **delegado/a de IA** y evaluaciones de impacto sobre sesgo discriminatorio (Art. 23.1 de la Ley 15/2022) y sobre derechos fundamentales (Art. 27 RIA). Excluye los sistemas «en fase de investigación, prueba o desarrollo» (12.4.b) | AIASN es una herramienta de apoyo precisamente para ese tipo de evaluaciones |
| 13 a 41 | Infracciones y sanciones (hasta 35 M€ o el 7 % del volumen de negocios para las prácticas prohibidas) | Se alinea con el régimen del Art. 99 RIA; si la ley no sale adelante, España carece de régimen sancionador propio |

---

## 2. Decisión

1. **El marco jurídico vinculante es el RIA**, que es de aplicación directa. El Ómnibus solo cambia fechas: para AIASN siguen aplicándose hoy las **prácticas prohibidas (Art. 5)** y la **transparencia (Art. 50.3)**; las obligaciones del Anexo III, **si algún día nos alcanzaran**, no serían exigibles hasta el 02/12/2027.
2. **Adelantamos voluntariamente los requisitos de alto riesgo** (gobierno del dato, documentación, registro de eventos, supervisión humana, solidez) aunque no se nos exijan: encajan con nuestra arquitectura y son lo que un cliente B2B o una administración nos pedirá.
3. **El proyecto de ley es nuestro norte y filosofía de uso, no una obligación.** Lo declaramos expresamente así: conocemos el texto, lo hemos leído y lo tomamos como referencia de buen uso; **no se presenta como norma vigente**. De él retenemos tres ideas: (a) un enfoque de **acompañamiento y guías preventivas** frente a uno meramente punitivo (enmiendas del COEINF/CCII, sesión del 16/10, `0:56:00`); (b) la **proporcionalidad y la simplificación**, que justifican una arquitectura ligera; y (c) el **buen uso en el sector público**: inventario, delegado/a de IA y evaluación de sesgo discriminatorio.
4. **Fórmulas de cita** (para README, memoria y presentación):
   * «Reglamento (UE) 2024/1689, tal como lo modifica el Reglamento (UE) 2026/1744».
   * «Proyecto de Ley Orgánica para el buen uso y la gobernanza de la IA (BOCG, Serie A, núm. 97-1, 12/06/2026), que tomamos como referencia no vinculante».

---

## 3. Contraste con lo que hace AIASN

| Norma | Qué exige o prohíbe | Qué hacemos | Evidencia en el repositorio | Estado |
|---|---|---|---|---|
| RIA Art. 5.1.f | Prohíbe el reconocimiento de emociones en el trabajo y la educación | Excluimos la inferencia de emociones | ADR-0009 | Cumple |
| RIA Art. 5.1.e | Prohíbe crear bases de datos de reconocimiento facial mediante *scraping* | No hacemos *scraping* ni guardamos bases faciales | ADR-0004 y ADR-0008; purga en `compliance.py` | Cumple (ver 3.5 del checklist) |
| RIA Art. 5.1.g y Anexo III.1.b | Prohíbe o clasifica como alto riesgo la categorización biométrica por atributos **sensibles** | El género percibido no figura entre los atributos del Art. 5.1.g; el considerando 54 ancla el Anexo III.1.b a los atributos del **Art. 9.1 RGPD**, que no incluye el sexo | `marco_normativo_y_mercado.md` §4.1 | **Interpretación del equipo, pendiente de validar con Ángela/Karina** |
| RIA Art. 50.3 | El responsable del despliegue informa a las personas expuestas a una categorización biométrica | Toda salida declara que opera con «género percibido» | README, `MODEL_CARD.md` | La obligación es del *deployer*; aportamos el texto |
| RIA Art. 2.8 | No se aplica a investigación, prueba o desarrollo previos a la comercialización (las pruebas en condiciones reales quedan fuera de la exención) | Estamos en fase de prototipo; los pilotos reales requerirán consentimiento | `DATASET_CARD.md`, hoja de ruta | Cumple en prototipo |
| RIA Art. 10 | Gobierno del dato | Arquitectura *medallion* (bronze, silver, gold) y manifest por vídeo | `aiasn/storage/` | Implementado |
| RIA Art. 11 y Anexo IV | Documentación técnica | Tarjetas de modelo y de datos, ADR | `MODEL_CARD.md`, `DATASET_CARD.md`, `docs/adr/` | Implementado |
| RIA Art. 12 | Registro de eventos | Manifest por paso; **observabilidad con Langfuse pendiente de subir** | `aiasn/storage/manifest.py` | Parcial |
| RIA Art. 14 | Supervisión humana | Panel de supervisión en el frontend; **las decisiones aún no se persisten** | `frontend-piloto/js/app.js` | Parcial |
| RIA Art. 15 | Exactitud y solidez | Cálculo determinista, abstención con p < 0,80, suite de tests | `tests/` | Implementado |
| Proyecto de ley, Art. 12 | Inventario, delegado/a de IA y evaluación de sesgo | `MODEL_CARD.md` y README recogen proveedor, responsable y categorización del sistema | Documentación | Alineado |

---

## 4. Consecuencias y compromisos

* **Positivas:** decisiones justificadas con cita, un calendario realista (sin sobrerreaccionar a fechas que el Ómnibus ha movido) y una declaración honesta sobre qué es norma y qué es referencia.
* **Compromisos y riesgos:**
  * Las fechas del Ómnibus proceden de fuentes secundarias hasta contrastar el DOUE a mano.
  * Que el proyecto haya decaído es información de las sesiones, no de una fuente oficial.
  * La clasificación de AIASN como «riesgo limitado» es una interpretación del equipo.
* **Preguntas abiertas para Ángela Gasch y Karina Gibert:** (1) ¿Confirman la clasificación de la categorización de género percibido (Anexo III.1.b frente al Art. 50.3)? (2) ¿Quién es, en un despliegue, el *deployer* que debe informar a las personas expuestas? (3) ¿Se ha publicado alguna guía de la AESIA sobre categorización biométrica?

## 5. Fuentes

* BOCG, Congreso de los Diputados, XV Legislatura, Serie A, núm. 97-1, 12/06/2026 (Expediente 121/000096): https://www.congreso.es/public_oficiales/L15/CONG/BOCG/A/BOCG-15-A-97-1.PDF
* Reglamento (UE) 2024/1689 (DOUE, 12/07/2024): ejemplar en `documentacion-tecnica/admin_y_bases/`.
* Reglamento (UE) 2026/1744 (Ómnibus Digital de IA), DOUE 24/07/2026: **texto oficial pendiente de contrastar** en EUR-Lex.
