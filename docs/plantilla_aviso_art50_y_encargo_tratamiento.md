# Plantilla de aviso (Art. 50.3 RIA) y de encargo del tratamiento para organizaciones que usen AIASN

> **Estado: borrador de trabajo, pendiente de revisión jurídica.** No es asesoramiento legal ni un contrato listo para firmar. Sirve para ordenar qué hay que decidir y dejar por escrito cuando una organización use AIASN con contenido propio. Las referencias al RIA son a las directrices de la Comisión sobre el Art. 50 (adoptadas el 20/07/2026) y deben revisarse cuando se publiquen las directrices finales de clasificación.

## 1. Reparto de papeles

| Papel | Quién | Qué implica |
|---|---|---|
| **Responsable del tratamiento y *deployer*** | La organización que analiza su contenido | Decide para qué y cómo se usa; informa a las personas que salen; responde ante la persona afectada y la autoridad |
| **Proveedor del *software*** | Equipo AIASN (código abierto, Apache-2.0) | Entrega el código y su documentación; no accede a los datos de la organización |
| **Encargado del tratamiento (Art. 28 RGPD)** | AIASN **solo si** aloja y ejecuta el servicio por cuenta de la organización | Necesita un contrato de encargo con el contenido mínimo de la sección 3 |
| **Subencargado** | Proveedor de los modelos remotos (hoy, los *endpoints* de OVHcloud AI) | Debe constar en el contrato y estar sujeto a las mismas obligaciones |

## 2. Aviso a las personas expuestas (Art. 50.3 RIA)

**Cuándo hace falta.** Si AIASN se ejecuta con los modelos que estiman el género por la cara o la voz (ADR-0013: «modo investigación»), es un sistema de categorización biométrica y la **organización que lo despliega** debe informar a las personas expuestas. Las directrices de la Comisión aclaran que:

* la obligación alcanza también al análisis posterior a la grabación (apartado 100);
* se informa a todas las personas expuestas, incluidos los niños (apartado 106);
* debe darse **como tarde en la primera exposición**, de forma clara y distinguible y accesible (apartados 107 y 108, Art. 50.5);
* puede ser por escrito, con iconos u oralmente.

Si AIASN se ejecuta solo con evidencias textuales (modo de producción propuesto en el ADR-0013), no se hace categorización biométrica, pero **sigue habiendo tratamiento de datos personales** (nombres de los rótulos, transcripción) y el deber de informar del RGPD (Arts. 13 y 14).

**Texto modelo (adaptar a cada caso):**

> Este contenido se analiza con AIASN, una herramienta de código abierto que mide la presencia y la voz de mujeres y hombres. [Si se usan modelos de imagen o voz: Para ello, un sistema de inteligencia artificial estima el género percibido a partir de rasgos del rostro o de la voz.] Los resultados se usan de forma agregada, no para tomar decisiones sobre personas concretas. Responsable: [organización]. Más información y ejercicio de derechos: [contacto].

**Formas de darlo:** nota visible al inicio de la pieza, icono estandarizado, aviso oral en la grabación, o cláusula en la comunicación previa a quien participa. Debe poder leerse con lector de pantalla y en lenguaje claro.

## 3. Contenido mínimo del contrato de encargo (Art. 28.3 RGPD)

Solo si AIASN actúa como encargada. A completar y revisar por un jurista:

1. **Objeto, duración, naturaleza y finalidad:** auditoría de presencia y voz de mujeres y hombres en contenido audiovisual de la organización.
2. **Tipo de datos y categorías de interesados:** vídeo, audio, transcripción, nombres y cargos de rótulos; personas que aparecen o hablan en el contenido.
3. **Instrucciones documentadas:** solo para ese análisis; **sin entrenar ni afinar modelos con el contenido** de la organización.
4. **Confidencialidad** de quienes accedan.
5. **Seguridad:** acceso restringido y autenticado, cifrado en tránsito y en reposo, y registro de accesos. Hoy la API del piloto no tiene autenticación ni TLS: **no debe exponerse públicamente** tal como está (ver hoja de ruta).
6. **Subencargados:** lista de los que intervienen (hoy, OVHcloud AI Endpoints para transcripción y LLM) y aviso previo de cambios.
7. **Asistencia** para atender derechos de las personas afectadas.
8. **Conservación y supresión:** qué se borra y cuándo. En el estado actual del código, `tmp/` y el vídeo de `landing/` se conservan tras el análisis (la opción de borrado está en una rama pendiente de revisión), y las **tablas derivadas** (`bronze`, `silver`, `gold`: género atribuido, tramos, transcripción, nombres de rótulos) se conservan. El contrato debe fijar su plazo y la devolución o supresión al terminar.
9. **Auditorías** y devolución de la información necesaria para demostrar el cumplimiento.
10. **Trazas de observabilidad:** si se activa Langfuse (opcional), las llamadas a los LLM pueden incluir fragmentos de la transcripción; indicar dónde se alojan y cuánto se conservan.

## 4. Condiciones de uso que conviene dejar por escrito

* AIASN audita la **presencia agregada**; no debe usarse para evaluar, sancionar o seleccionar a personas concretas (por ejemplo, en empleo): eso podría situarlo en otro punto del Anexo III del RIA.
* Las categorías de género son **atribuidas o percibidas**, no verificadas ni identidad.
* Todo informe pasa por revisión humana de los casos dudosos.
* El **Sello oficial** y el nombre solo se usan según las condiciones del proyecto (ver `docs/marco_normativo_y_mercado.md`).
* No se redistribuye el contenido bruto sujeto a derechos de autor.

## 5. Lista previa a un despliegue

- [ ] ¿Qué papel tiene cada parte (sección 1)?
- [ ] ¿Se va a usar el modo con modelos de cara o voz? Si sí, aviso del Art. 50.3 preparado y accesible.
- [ ] Contrato de encargo firmado, si AIASN aloja el servicio.
- [ ] Plazo de conservación fijado para ficheros temporales y tablas derivadas.
- [ ] API protegida (autenticación y TLS) y no expuesta a Internet sin ello.
- [ ] Persona responsable de la revisión humana designada.
- [ ] Revisión jurídica de esta plantilla.

## 6. Pendiente de revisión jurídica

* Encaje de AIASN como encargada frente a simple proveedora de código abierto.
* Base jurídica del tratamiento de nombres de personas públicas y de las que aparecen en rótulos (consulta a Karina Gibert y Ángela Gasch).
* Texto definitivo del aviso y su idoneidad en cada soporte.
* Revisión de las directrices finales de clasificación de la Comisión cuando se adopten.

