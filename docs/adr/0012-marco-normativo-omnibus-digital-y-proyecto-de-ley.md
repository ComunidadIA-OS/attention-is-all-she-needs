# ADR-0012: Marco normativo vigente tras el Ómnibus Digital de IA y el Proyecto de Ley Orgánica de gobernanza de la IA como norte no vinculante

* **Estado:** **Propuesta** (pendiente de validación de Pilar y Rocío; consulta abierta a Ángela Gasch y Karina Gibert)
* **Fecha:** 2026-10-28
* **Decisores:** Alba Camiña García (propuesta), Pilar de la Fuente Diez y Rocío Jiménez Villén (validación)
* **Referencias principales:** Reglamento (UE) 2024/1689 (RIA); Reglamento (UE) 2026/1744 («Ómnibus Digital de IA»); Proyecto de Ley Orgánica para el buen uso y la gobernanza de la inteligencia artificial (Expediente 121/000096, BOCG, Congreso de los Diputados, XV Legislatura, Serie A, núm. 97-1, 12 de junio de 2026)

---

## 1. Contexto

Desde el 14 de octubre se han ido concretando dos novedades que afectan a cómo justificamos nuestras decisiones:

1. **El Ómnibus Digital de IA** (Reglamento (UE) 2026/1744 del Parlamento Europeo y del Consejo, de 8 de julio de 2026, publicado en el DOUE el 24/07/2026 y en vigor a los tres días, el 27/07/2026; **texto oficial contrastado**) modifica el RIA. Lo que más nos afecta:
   * **(a)** **Aplaza** las obligaciones del capítulo III, secciones 1 a 3, para los sistemas de alto riesgo del Anexo III al **2 de diciembre de 2027** y para los del Anexo I al **2 de agosto de 2028** (nuevo Art. 113, letra c).
   * **(b)** **No aplaza** las prácticas prohibidas (desde el 02/02/2025) ni la transparencia del **Art. 50**, aplicable desde el **02/08/2026**; solo concede hasta el 02/12/2026 a los generadores de contenido sintético ya comercializados para cumplir el Art. 50.2 (nuevo Art. 111.4).
   * **(c)** Añade prohibiciones sobre material íntimo no consentido y de abuso sexual de menores (Art. 5.1.b bis y b ter, desde el 02/12/2026), que no nos afectan.
   * **(d)** **Suaviza la alfabetización en IA** (Art. 4): se exigen medidas de apoyo, sin garantizar un nivel concreto.
   * **(e)** Crea una **base jurídica excepcional para tratar categorías especiales de datos con el fin de detectar y corregir sesgos** (nuevo Art. 4 bis, que sustituye al antiguo Art. 10.5), con garantías estrictas. El considerando 9 afirma que «la detección y la corrección de sesgos tienen un interés público significativo».
   * **(f)** Retrasa al 02/08/2027 la fecha límite del espacio controlado de pruebas nacional (Art. 57.1).
2. **El Proyecto de Ley Orgánica para el buen uso y la gobernanza de la IA** (Consejo de Ministros, 26/05/2026; presentado en el Congreso el 28/05/2026 y publicado en el BOCG el 12/06/2026; plazo de enmiendas inicial hasta el 30/06/2026, ampliado semanalmente hasta el 07/10/2026) adapta el ordenamiento español al RIA. La **disolución de las Cortes está verificada en el BOE**: el Real Decreto 806/2026, de 5 de octubre (BOE-A-2026-20742, publicado el 06/10/2026), disuelve el Congreso y el Senado y convoca elecciones generales para el **29/11/2026**; las nuevas Cámaras se reunirán el 23/12/2026. Conforme al Art. 207 del Reglamento del Congreso, la disolución provoca el **decaimiento** de los asuntos en tramitación, por lo que el proyecto **ha decaído**: la ficha del expediente en congreso.es (consultada el 28/10/2026) indica «Situación actual: Concluido - (Caducado)» desde el 06/10/2026, lo que coincide con lo que nos trasladaron las mentoras. Para volver a tramitarse, el próximo Gobierno tendría que presentarlo de nuevo. Se cita siempre como «proyecto de ley decaído» y nunca como norma vigente.

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

1. **El marco jurídico vinculante es el RIA**, que es de aplicación directa. El Ómnibus retrasa el alto riesgo y retoca otros puntos, pero no los que nos afectan hoy: para AIASN siguen aplicándose las **prácticas prohibidas (Art. 5)** y la **transparencia (Art. 50.3)**; las obligaciones del Anexo III, **si algún día nos alcanzaran**, no serían exigibles hasta el 02/12/2027.
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
| RIA Art. 4 (modificado por el Ómnibus) | Los proveedores y responsables del despliegue adoptan **medidas de apoyo** a la alfabetización en IA de su personal, sin garantizar un nivel concreto | Guía de uso responsable con preguntas orientativas por áreas éticas (`docs/guia_uso_responsable_y_preguntas_orientativas.md`) | Documentación | Parcial (borrador) |
| RIA Art. 4 bis (nuevo, Ómnibus) | Base **excepcional** para tratar categorías especiales de datos cuando sea **estrictamente necesario** para detectar y corregir sesgos, con garantías: sin alternativa con datos sintéticos o anonimizados, pseudonimización, acceso controlado, sin cesión a terceros, supresión al corregir el sesgo y registro de por qué era necesario | No tratamos categorías especiales de datos con ese fin: el género percibido no es categoría especial y los vectores faciales se descartan. Las garantías coinciden con nuestras prácticas (supresión, sin cesión, registro) | ADR-0004, `compliance.py` | **No la invocamos**; consulta abierta |
| Proyecto de ley, Art. 12 | Inventario, delegado/a de IA y evaluación de sesgo | `MODEL_CARD.md` y README recogen proveedor, responsable y categorización del sistema | Documentación | Alineado |

---

## 4. Consecuencias y compromisos

* **Positivas:** decisiones justificadas con cita, un calendario realista (sin sobrerreaccionar a fechas que el Ómnibus ha movido) y una declaración honesta sobre qué es norma y qué es referencia.
* **Compromisos y riesgos:**
  * El Ómnibus está contrastado con el texto oficial del DOUE; un cambio posterior de calendario habría que revisarlo.
  * El decaimiento del proyecto está verificado en el BOE (Real Decreto 806/2026) y en la ficha del expediente en congreso.es («Concluido - (Caducado)» desde el 06/10/2026).
  * La clasificación de AIASN como «riesgo limitado» es una interpretación del equipo.
  * **Identificación biométrica remota:** el Art. 3.41 RIA la define por la comparación de datos biométricos con una **base de datos de referencia**. AIASN agrupa apariciones de una misma persona dentro de un vídeo y no compara con ninguna base de referencia, por lo que no encaja en esa definición (Anexo III.1.a). Esto dejaría de ser así si se añadiera reconocimiento facial contra listas de referencia.
  * **Categorización biométrica:** el Art. 3.40 define el sistema de categorización biométrica por incluir a personas en categorías «en función de sus datos biométricos». Estimar el género percibido a partir de los rasgos faciales encaja en esa definición. El Anexo III.1.b habla de atributos «sensibles o **protegidos**»; el considerando 54 los ancla al Art. 9.1 RGPD (que no incluye el sexo), pero la letra del Anexo deja margen, así que es una pregunta abierta y no una certeza.
  * **Código abierto:** el Art. 2.12 excluye los sistemas publicados con licencia libre, pero no los que se pongan en servicio dentro del ámbito de los Arts. 5 o 50.
* **Preguntas abiertas para Ángela Gasch y Karina Gibert:** (1) ¿Confirman la clasificación de la categorización de género percibido (Anexo III.1.b frente al Art. 50.3)? (2) ¿Quién es, en un despliegue, el *deployer* que debe informar a las personas expuestas? (3) ¿Existe o se prevé alguna guía de la AESIA sobre el Art. 50 o la categorización biométrica? (Las guías 06, 07, 08, 11 y 12 del piloto de sandbox, leídas por secciones, tratan los requisitos de alto riesgo y no esta cuestión.) (4) ¿Podría el nuevo Art. 4 bis respaldar el tratamiento biométrico transitorio para auditar sesgos, o solo cubre los sesgos de los propios sistemas de IA? La guía 07 del sandbox reproduce el Art. 4 bis (el apartado 2 se extiende a otros sistemas y a quien los despliega, sin crear obligación); falta confirmar si los embeddings faciales cuentan como categoría especial. (5) ¿Es admisible declarar el género percibido de una persona sin rótulo solo por sus rasgos faciales, o debe limitarse a atribución por texto en pantalla, transcripción o revisión humana?

## 5. Fuentes

* BOCG, Congreso de los Diputados, XV Legislatura, Serie A, núm. 97-1, 12/06/2026 (Expediente 121/000096): https://www.congreso.es/public_oficiales/L15/CONG/BOCG/A/BOCG-15-A-97-1.PDF
* Ficha del expediente 121/000096 en congreso.es (consultada el 28/10/2026), Situación actual «Concluido - (Caducado)»: https://www.congreso.es/es/busqueda-de-iniciativas?p_p_id=iniciativas&p_p_lifecycle=0&p_p_state=normal&p_p_mode=view&_iniciativas_mode=mostrarDetalle&_iniciativas_legislatura=XV&_iniciativas_id=121%2F000096
* Real Decreto 806/2026, de 5 de octubre, de disolución del Congreso de los Diputados y del Senado y de convocatoria de elecciones (BOE-A-2026-20742, 06/10/2026): https://www.boe.es/diario_boe/txt.php?id=BOE-A-2026-20742
* Reglamento (UE) 2024/1689 (DOUE, 12/07/2024): ejemplar en `documentacion-tecnica/admin_y_bases/`.
* Reglamento (UE) 2026/1744 (Ómnibus Digital de IA), de 8 de julio de 2026, DOUE L 2026/1744, 24/07/2026 (ELI: http://data.europa.eu/eli/reg/2026/1744/oj): texto oficial leído y contrastado (copia aportada por Alba el 28/10/2026).
