# Borrador de contrato de servicios y condiciones de uso de AIASN

> **Estado: borrador de trabajo, pendiente de revisión jurídica. No es un contrato listo para firmar ni asesoramiento legal.** Está escrito por el equipo (no por juristas) para ordenar qué habría que acordar si una organización quisiera usar AIASN con su propio contenido. Se apoya en [`plantilla_aviso_art50_y_encargo_tratamiento.md`](./plantilla_aviso_art50_y_encargo_tratamiento.md), en el [`CODE_OF_CONDUCT.md`](../CODE_OF_CONDUCT.md) y en el [ADR-0012](./adr/0012-marco-normativo-omnibus-digital-y-proyecto-de-ley.md). Los textos entre corchetes `[ ]` son datos o decisiones que faltan.
>
> **Estado del software que se describe (v0.1.0, prototipo del reto):** AIASN es un prototipo. Los anexos C y D dicen con franqueza qué medidas existen hoy y cuáles faltan; **no debe ofrecerse como servicio a terceros mientras no estén cubiertas las marcadas «Falta»**.

---

## 0. Dos modalidades de uso

| Modalidad | Qué es | Qué documento se aplica |
|---|---|---|
| **A. Autoalojada** | La organización descarga el código (licencia Apache-2.0) y lo ejecuta en su propia infraestructura. | Solo la licencia Apache-2.0 y la **Parte II** (condiciones de uso). No hay relación de encargo: la organización es única responsable del tratamiento. |
| **B. Servicio gestionado** | El equipo (o una entidad que lo represente) aloja y ejecuta AIASN y la organización le sube su contenido. | **Todo el documento.** La prestadora actúa como **encargada del tratamiento** (Art. 28 RGPD) y la organización como **responsable y *deployer*** (Art. 50.3 RIA). |

Hoy el equipo **no es una entidad con personalidad jurídica propia**; ver decisiones pendientes.

## 1. Decisiones pendientes antes de ofrecer la modalidad B

- [ ] **Quién presta el servicio:** persona física, asociación, entidad vinculada a la UPC u otra. Sin una parte contratante identificable no puede firmarse nada.
- [ ] **Revisión por una persona jurista** (contrato, encargo del tratamiento, responsabilidad, marca).
- [ ] **Delegado de protección de datos y registro de actividades de tratamiento**, si procede.
- [ ] **Evaluación de impacto en protección de datos**, si la categorización de género por modelos de cara o voz sigue activa (ver ADR-0013).
- [ ] **Seguro de responsabilidad civil**, si se ofrece servicio de pago.
- [ ] **Precio, plazos y soporte** (ahora no los hay; la Parte I no promete disponibilidad).
- [ ] **Medidas de seguridad mínimas de producción** del Anexo C (hoy faltan).
- [ ] **Posición definitiva sobre clasificación** (ADR-0012: depende de las directrices finales de la Comisión, previstas a finales de 2026).

---

# PARTE I. Contrato de prestación de servicios (modalidad B)

**Entre:** [ENTIDAD PRESTADORA], con domicilio en [ ] y NIF [ ] («la Prestadora»), y [ORGANIZACIÓN], con domicilio en [ ] y NIF [ ] («la Cliente»).

### 1. Objeto
La Prestadora ejecuta AIASN sobre el contenido audiovisual que la Cliente le facilite y le entrega un informe de **presencia y voz de mujeres y hombres a nivel agregado** (tiempo en pantalla, tiempo de voz, ratio voz/pantalla, Test de Interlocución Femenina y alertas), con trazabilidad al fragmento, marca de tiempo o fotograma. **No** incluye decisiones sobre personas concretas.

### 2. Naturaleza experimental del servicio
AIASN es un **prototipo** de código abierto. El servicio se presta **«tal cual»**, sin compromiso de disponibilidad, tiempos de respuesta ni exactitud de los modelos más allá de lo descrito en `MODEL_CARD.md` y `DATASET_CARD.md`. Las categorías de género son **atribuidas o percibidas**, no verificadas ni identidad. Los casos con confianza inferior a 0,80 quedan «no determinados» y se derivan a revisión humana. *(Apache-2.0, §7 y §8: sin garantías y con limitación de responsabilidad, dentro de lo que permita la ley.)*

### 3. Roles de protección de datos y del RIA
1. **La Cliente** es **responsable del tratamiento** (Arts. 4.7 y 24 RGPD) y ***deployer*** a efectos del RIA. Decide para qué se usa el contenido y responde de su licitud y de informar a las personas que salen.
2. **La Prestadora** es **encargada del tratamiento** (Art. 28 RGPD) y **proveedora** del sistema. Solo trata el contenido siguiendo instrucciones documentadas de la Cliente.
3. **Subencargados:** los del Anexo B, con aviso previo de cualquier cambio y las mismas obligaciones por contrato.

### 4. Obligaciones de la Cliente
1. Garantizar que **tiene derecho a subir y analizar el contenido** (derechos de autor, imagen, cesiones de los participantes) y que no lo ha obtenido por *scraping* ni vulnerando condiciones de plataformas.
2. **Informar a las personas expuestas** (Art. 50.3 RIA y Arts. 13 y 14 RGPD) con el texto y por los medios de la plantilla del Art. 50.3, **como tarde en la primera exposición**, y de forma accesible. Las directrices de la Comisión (C(2026) 5054) aclaran que la obligación alcanza también a los niños y al análisis posterior a la grabación.
3. **No subir** contenido en que aparezcan **menores** o datos de **salud u otras categorías especiales** sin una base jurídica específica comunicada por escrito a la Prestadora.
4. Designar a la **persona responsable de la revisión humana** de los casos dudosos y usar el informe sin delegar en él la decisión final.
5. Respetar las **condiciones de uso** de la Parte II.

### 5. Obligaciones de la Prestadora
1. Tratar el contenido **solo** para generar el informe pedido, **sin entrenar ni afinar modelos con él** y sin cederlo a terceros distintos de los subencargados del Anexo B.
2. Aplicar las **medidas de seguridad** del Anexo C y avisar a la Cliente **sin dilación indebida** de cualquier violación de seguridad que afecte al contenido.
3. Ayudar a la Cliente a atender los derechos de las personas afectadas y a cumplir sus obligaciones de seguridad y de evaluación de impacto.
4. Poner a disposición la **información necesaria para demostrar el cumplimiento** y permitir auditorías razonables.
5. Mantener la **trazabilidad** de cada métrica y alerta, y la documentación técnica (`MODEL_CARD.md`, `DATASET_CARD.md`, ADR).

### 6. Datos tratados y conservación
- **Qué se trata:** vídeo, audio, transcripción, nombres y cargos de los rótulos, coordenadas de personas y género atribuido por persona (Anexo A).
- **Qué se conserva y cuánto:** [plazo a fijar]. En el estado actual (v0.1.0) los ficheros temporales (`tmp/`) y el vídeo original (`landing/`) **no se borran automáticamente**; la opción de borrado está en la PR #32, pendiente de revisión. Las **tablas derivadas** (`bronze`, `silver`, `gold`) se conservan hasta que la Cliente pida su supresión.
- **Al terminar el contrato:** devolución o supresión de todo lo anterior, a elección de la Cliente, en [ ] días, con **certificado de supresión**.

### 7. Propiedad intelectual y resultados
1. El **código** de AIASN se licencia bajo **Apache-2.0**. La licencia **no concede** derecho alguno sobre el nombre «Attention Is All She Needs / AIASN», sus logotipos ni el Sello (Apache-2.0, §6).
2. La Cliente conserva todos los derechos sobre **su contenido**.
3. Los **informes y métricas** generados sobre el contenido de la Cliente son de la Cliente. La Prestadora puede usar **datos estadísticos agregados y anonimizados** de forma que no identifiquen a la Cliente ni a personas, **solo si la Cliente lo autoriza expresamente** [ ].

### 8. Confidencialidad
Ambas partes mantienen en secreto la información no pública de la otra durante el contrato y [ ] años después, salvo obligación legal.

### 9. Responsabilidad
1. Dentro de los límites que establece la ley (no pueden excluirse el dolo ni la culpa grave), la responsabilidad de la Prestadora se limita a [importe o criterio].
2. La Prestadora **no responde** de decisiones que la Cliente adopte sobre personas basándose en el informe, ni de contenido subido sin derechos, ni de la ausencia de información a las personas expuestas.

### 10. Duración y resolución
Duración: [ ]. Cualquiera de las partes puede resolver con [ ] días de preaviso, y de inmediato por incumplimiento grave de los puntos 4 o 5 o de las condiciones de la Parte II.

### 11. Ley aplicable y jurisdicción
Legislación española. Juzgados y tribunales de [ ]. [A revisar por jurista: posibles vías previas de mediación.]

---

# PARTE II. Condiciones de uso (modalidades A y B)

### 12. Usos permitidos
Auditoría de **presencia agregada** de mujeres y hombres en contenido audiovisual propio de la organización, con fines de **autodiagnóstico, rendición de cuentas, investigación o divulgación**, con revisión humana de los casos dudosos.

### 13. Usos prohibidos
1. **Evaluar, calificar, sancionar, seleccionar o vigilar a personas concretas** (empleo, disciplina, policía, seguros, crédito). Ese uso entraría en otros puntos del Anexo III del RIA y no lo ofrece el equipo.
2. **Identificar a personas** por su cara o su voz, comparar con bases de referencia o construir bases de datos biométricas.
3. **Reconocer emociones** o inferir opiniones, origen étnico, orientación sexual, salud u otras categorías sensibles.
4. Subir contenido **sin derechos** o conseguido por *scraping* masivo.
5. Presentar el informe como **certificado público** o usar el Sello sin superar el proceso de la Parte III.
6. **Entrenar o afinar** otros modelos con el contenido de terceros procesado.
7. Ocultar o alterar la leyenda de categoría percibida y de revisión humana de los resultados.

### 14. Transparencia hacia las personas
Quien despliega AIASN con modelos que estiman el género por rasgos biométricos **debe informar a las personas expuestas** (plantilla del Art. 50.3). Si solo se usan evidencias textuales (ADR-0013, propuesta), no hay categorización biométrica, pero **sigue habiendo tratamiento de datos personales** (nombres, transcripción) y deber de informar conforme al RGPD.

### 15. Revisión humana
Los resultados con confianza inferior a 0,80 se derivan a una persona. El panel actual **no guarda aún las decisiones** de revisión; mientras tanto, la organización debe registrar por su cuenta quién revisó y cuándo.

### 16. Incumplimiento
El incumplimiento de esta Parte permite al equipo **suspender el servicio** (modalidad B) y, en la modalidad A, retirar el derecho a usar el nombre, los logotipos y el Sello.

---

# PARTE III. Condiciones de uso del Sello (diseño; no operativo en v0.1.0)

> Hoy existe la función `emitir_sello_auditoria` (`aiasn/core/compliance.py`) con sus tests como **librería**; **no está integrada** en la API ni en el frontend. Lo que sigue es el diseño previsto en el `CODE_OF_CONDUCT.md`.

1. **Reserva de marca:** el nombre, los logotipos y el Sello «AIASN Trust Verified» no se pueden usar con fines comerciales, de licitación o de comunicación externa sin superar antes la auditoría de elegibilidad ética y la validación criptográfica.
2. **Muestra íntegra:** no se admite certificar una pieza aislada (*cherry-picking*); hace falta una muestra temporal continua y representativa de la comunicación de la entidad.
3. **Cláusula anti-lavado de cara:** no se emite a entidades con sanciones o infracciones relevantes en los últimos 36 meses, con vía de **rehabilitación verificada** (informes de al menos 2 a 3 periodos de evolución sostenida).
4. **Integridad:** cada sello incorpora una huella **SHA-256** de las tablas de entrada, los umbrales y el identificador pseudonimizado de la persona supervisora; cualquier alteración posterior invalida el certificado.
5. **Revocación:** ante infracción o manipulación, el comité del proyecto revoca el sello y lo hace público. Las valoraciones ciudadanas, si algún día existen, **no modifican** el sello ni las métricas.
6. **Pendiente de revisión jurídica:** forma de acreditar el Sello, responsabilidad por su mal uso y procedimiento de revocación.

---

## Anexo A. Descripción del tratamiento (Art. 28.3 RGPD)

| Concepto | Contenido |
|---|---|
| Objeto y finalidad | Auditoría agregada de presencia y voz de mujeres y hombres en contenido audiovisual de la Cliente |
| Naturaleza | Transcripción y diarización de voz; detección y seguimiento de personas; lectura de rótulos (nombre y cargo); atribución de género; cálculo determinista de métricas |
| Tipos de datos | Vídeo, audio, transcripción, nombres y cargos de rótulos, coordenadas, género atribuido por persona |
| Categorías de interesados | Personas que aparecen o hablan en el contenido |
| Categorías especiales | **No se pretenden tratar.** Si el contenido revela salud u otras categorías, aplica el punto 4.3 |
| Duración | La del contrato; luego, supresión (punto 6) |

## Anexo B. Subencargados (estado a 28/10/2026)

| Subencargado | Qué recibe | Observación |
|---|---|---|
| **OVHcloud AI Endpoints** (`oai.endpoints.kepler.ai.cloud.ovh.net`) | Audio (transcripción con Whisper) y texto de la transcripción (modelo de lenguaje para menciones, referencias, tono) | Datos salen a un tercero. **Falta** el contrato de encargo con OVHcloud y la comprobación de su ubicación y condiciones |
| **Langfuse** (opcional, autoalojado) | Llamadas al modelo de lenguaje, con fragmentos de transcripción | **Desactivado por defecto**; si se activa, indicar dónde se aloja y cuánto se conserva |
| Almacenamiento (SeaweedFS compatible S3) | Tablas derivadas y vídeo original | Autoalojado en el despliegue |

## Anexo C. Medidas de seguridad: estado actual y lo que falta

| Medida | Estado en v0.1.0 | ¿Hace falta para ofrecer el servicio? |
|---|---|---|
| Autenticación y control de acceso por roles | **Falta**: la API y el front no tienen | **Sí** |
| Cifrado en tránsito (HTTPS/TLS) | **Falta** | **Sí** |
| Cifrado en reposo del vídeo y de las tablas | **Falta** | **Sí** |
| CORS restringido | **Falta**: está abierto (`*`) | **Sí** |
| Aislamiento del lanzador de contenedores | **Falta**: la API monta `docker.sock` | **Sí** |
| Borrado de ficheros temporales | Opcional, **pendiente de PR #32** | **Sí** |
| Cola de procesado | **Falta**: un vídeo cada vez | Según volumen |
| Registro de accesos y de decisiones de revisión | **Falta** (Langfuse solo traza llamadas al modelo de lenguaje) | **Sí** |
| Análisis de vulnerabilidades en dependencias | **Falta** | Recomendado |
| Contenedores reproducibles y secretos fuera del código | Sí | — |

Referencia de buenas prácticas voluntarias: Guía 11 de ciberseguridad del piloto español de *sandbox* regulatorio de IA (Ministerio para la Transformación Digital y de la Función Pública, v2.0, 17/07/2026), pensada para alto riesgo y no vinculante.

## Anexo D. Lista previa a la firma

- [ ] Prestadora identificada y con capacidad para contratar.
- [ ] Revisión jurídica de este documento.
- [ ] Medidas «Sí» del Anexo C cubiertas.
- [ ] Contrato de encargo con OVHcloud y ubicación de los datos comprobada.
- [ ] Plazo de conservación fijado y supresión probada.
- [ ] Aviso a las personas preparado (plantilla del Art. 50.3) y accesible.
- [ ] Persona de la Cliente designada para la revisión humana.
- [ ] Confirmado que el contenido no incluye menores ni categorías especiales (o base jurídica documentada).
- [ ] Decisión sobre el uso de cara y voz para el género (ADR-0013).
- [ ] Registro de actividades de tratamiento y, si procede, evaluación de impacto.

## Referencias

- RGPD (Reglamento (UE) 2016/679): Arts. 4, 9, 13, 14, 24, 28 y 32.
- Reglamento (UE) 2024/1689 (RIA), modificado por el Reglamento (UE) 2026/1744: Arts. 3.40, 5, 50.3 y Anexo III.
- Comisión Europea, directrices sobre el Art. 50 (C(2026) 5054, 20/07/2026) y borrador de clasificación de alto riesgo (19/05/2026).
- Licencia Apache-2.0, §6 (marcas), §7 (exclusión de garantías) y §8 (limitación de responsabilidad).
- `CODE_OF_CONDUCT.md`, `ETHICS_CHECKLIST.md`, ADR-0012 y ADR-0013, y `docs/plantilla_aviso_art50_y_encargo_tratamiento.md`.

