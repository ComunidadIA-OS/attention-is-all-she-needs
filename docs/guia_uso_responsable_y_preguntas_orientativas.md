# Guía de uso responsable y preguntas orientativas para quien despliegue AIASN

> **Estado:** borrador para revisión del equipo · 28/10/2026
> **Qué es:** una lista de preguntas que debería hacerse una organización antes de adoptar AIASN, con la respuesta honesta de lo que hacemos hoy y su estado real. Es también nuestra **medida de apoyo a la alfabetización en IA** del Art. 4 del RIA, tal como lo redacta el Reglamento (UE) 2026/1744.

## 1. De dónde sale el formato

Adoptamos el formato de las **preguntas orientativas** de las *Directrices para educadores sobre el uso ético de la inteligencia artificial y los datos en la enseñanza y el aprendizaje*, Comisión Europea, Oficina de Publicaciones de la Unión Europea, Luxemburgo, edición revisada de 2026 (manuscrito finalizado en noviembre de 2025; referencia NC-01-25-186-ES-N). Esas directrices **no se aplican a AIASN**: están pensadas para la educación y AIASN es una herramienta de auditoría de medios. Nos sirven como **modelo contrastado de preguntas** para que quien adopta una herramienta de IA dialogue con quien la ofrece. **No afirmamos cumplir esas directrices**; usamos su estructura de ocho áreas.

## 2. Preguntas por áreas y estado real

| Área | Pregunta que debería hacerse quien despliega | Qué hace AIASN hoy | Estado |
|---|---|---|---|
| **Capacidad de acción y supervisión humanas** | ¿Puedo revisar y corregir lo que propone antes de usarlo? | Panel de supervisión humana en el frontend: los tramos dudosos se revisan persona a persona, y por debajo de p = 0,80 el sistema se abstiene en lugar de forzar una etiqueta. **Las decisiones del panel aún no se guardan en el backend.** Como referencia de diseño para la hoja de ruta, la Guía 06 de vigilancia humana del piloto de sandbox (Ministerio para la Transformación Digital y de la Función Pública, v2.0, 17/07/2026) propone, frente al sesgo de automatización, un modo de «error forzado», documentar el nivel de autonomía (HITL/HOTL) y poder descartar o interrumpir; ninguna de esas medidas está aplicada todavía. | Parcial |
| **Transparencia y explicabilidad** | ¿Entiendo por qué sale cada resultado? | Las métricas las calcula código determinista y reproducible, no un modelo; hay resumen en palabras sencillas, fichas de modelo y de datos y un registro de decisiones (ADR). | Implementado en lo esencial |
| **Diversidad e inclusión** | ¿Es accesible y funciona en distintas lenguas? | Informe de accesibilidad (WCAG 2.2 AA, `docs/informe_conformidad_accesibilidad.md`), resumen en lectura fácil y soporte declarado de `es`, `ca`, `gl`, `eu` y `en` (ADR-0010). | Implementado |
| **Equidad y no discriminación** | ¿Se ha probado si falla más con unos grupos que con otros? | Los datos declarados (rótulos) prevalecen sobre la inferencia visual y se registra la abstención. El estimador visual de género puede fallar más con ciertos grupos, como documenta la literatura (*Gender Shades*, Buolamwini y Gebru, 2018). **La validación frente a anotaciones humanas está pendiente.** | Parcial |
| **Bienestar social y medioambiental** | ¿Qué efectos tiene sobre las personas y el entorno? | No se infieren emociones (ADR-0009). El muestreo selectivo de fotogramas reduce el cómputo; las cifras de ahorro son estimaciones pendientes de *benchmark*. | Parcial |
| **Solidez técnica y seguridad** | ¿Es fiable y está protegida? | Suite de tests automatizados y cálculo determinista. **La API de la demo no tiene autenticación ni HTTPS y no debe exponerse públicamente tal cual.** | Parcial |
| **Privacidad y gobernanza de datos** | ¿Qué datos personales trata y durante cuánto tiempo? | Los vectores faciales no se guardan y la edad no se estima ni se almacena en la rama de minimización (`feat/delete-media-after-run`, pendiente de fusionar). **Mientras tanto, el vídeo y los fotogramas temporales no se borran automáticamente** (ver `ETHICS_CHECKLIST.md`, 3.5). | Parcial |
| **Rendición de cuentas** | ¿Quién responde y puede auditarse? | Registro de decisiones (ADR), historial de PRs con coautoría, fichas de modelo y de datos. La observabilidad con Langfuse está pendiente. Conviene distinguir qué responde cada parte: AIASN como proveedor (calidad del modelo y de la documentación), la organización que despliega (uso y decisiones) y la persona que revisa (su arbitraje). Las decisiones del panel de revisión aún no se guardan; la Guía 12 de registros del sandbox sirve de referencia para los campos del futuro registro (quién, cuándo, versión del modelo, entrada, salida y alertas), sin conservar datos biométricos. | Parcial |

## 3. Qué debe hacer quien despliega AIASN

1. **Informar a las personas que aparecen en el contenido** de que se aplica una categorización de género percibido (Art. 50.3 del RIA). La obligación es de quien despliega; nosotras aportamos el texto.
2. **Firmar un contrato de encargo de tratamiento** cuando una empresa suba su contenido (Art. 28 del RGPD): ella es la responsable del tratamiento y AIASN, la encargada.
3. **Mantener supervisión humana** sobre los resultados y no usarlos para decisiones individuales sobre personas (laborales, disciplinarias o policiales). AIASN audita la **presencia agregada** en medios.
4. **No activar inferencias de emociones** ni usos prohibidos por el Art. 5 del RIA.
5. **Declarar los límites**: el género es siempre *percibido*, no se atribuye sexo biológico ni identidad, y los casos dudosos quedan como «no determinado».

## 4. Cómo se mantiene

Esta guía se actualiza cuando cambie el estado de alguna fila (por ejemplo, al fusionar la rama de minimización de datos o al persistir las decisiones de supervisión). Cada cambio de estado debe reflejarse también en `ETHICS_CHECKLIST.md` y en la presentación.
