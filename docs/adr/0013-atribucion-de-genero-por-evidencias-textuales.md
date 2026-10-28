# ADR-0013: Atribución del género por evidencias textuales, sin decidirlo solo por la voz o la imagen

* **Estado:** **Propuesta** (pendiente de validación de Pilar y Rocío; implementación pendiente de la decisión de Rocío sobre el código)
* **Fecha:** 2026-10-28
* **Decisores:** Alba Camiña García (propuesta), Pilar de la Fuente Diez y Rocío Jiménez Villén (validación)
* **Referencias principales:** Reglamento (UE) 2024/1689 (Art. 3.40, Art. 5.1.g, Art. 50.3, Anexo III.1.b); directrices de la Comisión sobre el Art. 50 (C(2026) 5054 final, 20/07/2026); borrador de directrices de la Comisión sobre clasificación de alto riesgo (19/05/2026); ADR-0004, ADR-0005, ADR-0006, ADR-0011 y ADR-0012

---

## 1. Contexto

Hoy el género de cada participante se decide en `silver` a partir de **modelos que miran la cara y escuchan la voz**:

* `aiasn/core/silver/gender.py` (`fuse_gender`) combina el género estimado por el modelo visual (por votación de los fotogramas con cara) y por el clasificador de voz, y guarda de dónde sale en `genero_fuente` (`video`, `audio`, `ambos`, `conflicto` o `ninguna`). Si los dos se contradicen, queda `no_determinado` para revisión humana (ADR-0005).
* `aiasn/model_adapters/nlp/mentions.py` ya extrae del texto las alusiones a quienes participan: nombre, cargo, **género gramatical** con el que se alude a la persona, hablante aludido y la frase literal comprobada. Esa información se guarda en `bronze`, pero **no interviene** en la decisión de género de ninguna persona.
* `video_captions` extrae el nombre y el cargo de los rótulos, sin género.

Lo que dicen las fuentes oficiales sobre este caso:

* **Art. 3.40 RIA:** un sistema de categorización biométrica asigna a personas a categorías «en función de sus datos biométricos». Estimar el género por la cara o la voz encaja en esa definición.
* **Directrices del Art. 50 (adoptadas, 20/07/2026, apartado 104):** el Art. 50(3) se aplica a cualquier sistema de categorización biométrica, y cita la «clasificación de edad o género basada en datos biométricos», sea o no de alto riesgo. La obligación de informar recae en **quien despliega** y alcanza también al análisis posterior a la grabación (apartados 99 a 108).
* **Borrador de directrices de alto riesgo (19/05/2026, apartados 169 y 170 y ejemplos):** el género no es un atributo sensible o protegido del Art. 9.1 RGPD, de modo que inferirlo de imágenes faciales **no** es alto riesgo por el Anexo III.1.b. Es un borrador no vinculante, con adopción final prevista a finales de 2026.

Es decir: la estimación biométrica del género no está prohibida ni es de alto riesgo, pero nos sitúa en el Art. 50(3), nos deja con errores de modelo que ya conocemos (diapositiva 91 de Verónica Vilaplana: la mitad de las mujeres caía en «unknown») y es lo que menos defendible resulta ante la pregunta «¿con qué derecho declara usted el género de una persona por cómo se ve o cómo suena?».

## 2. Decisión (propuesta)

**No asignar género a una persona únicamente por su voz o por su imagen física.** El género atribuido a un participante se decide solo cuando hay una **evidencia textual señalable**; si no la hay, queda `no_determinado` («sin atribuir»).

### 2.1 Evidencias admitidas

| Nivel | Evidencia | Origen |
|---|---|---|
| **Fuerte** | Otro orador la presenta o se refiere a ella con un género gramatical concreto («la doctora Marta Ruiz», «mi compañero») | `nlp_mentions` (ya extraída; falta conectarla a la decisión) |
| **Fuerte** | Ella misma se refiere a sí misma con un género gramatical («encantada», «soy la directora») | Ampliación del extractor de menciones |
| **Fuerte** | Título, tratamiento o cargo del rótulo con género («Directora», «Sra.», «Doctor») | `video_captions` |
| **Débil** | Solo el nombre de pila | Rótulo o transcripción |

* La evidencia **débil no decide por sí sola**: hay nombres neutros, extranjeros o mal transcritos. Requiere una segunda evidencia o confirmación humana.
* Si dos evidencias **se contradicen**, queda `no_determinado` y se deriva a revisión humana.
* Cada atribución guarda **la evidencia que la sostiene** (frase literal y marca de tiempo, o fotograma del rótulo) en `genero_fuente` (por ejemplo `alusion`, `autoreferencia`, `rotulo_cargo`, `nombre`), conforme al principio de trazabilidad.

### 2.2 Los modelos de cara y de voz

* Dejan de decidir el género en el modo de producción **una vez completada la transición** (ver 5).
* Se conservan **únicamente en un «modo investigación»**, activado por configuración (propuesta: `silver.gender_sources`, con valores `texto`, `video` y `audio`), con aviso visible de que en ese modo el sistema es de categorización biométrica a efectos del Art. 50(3).
* Los modelos de **detección y seguimiento** (personas, caras para reidentificar dentro del vídeo, hablante activo) no cambian: no asignan género.

### 2.3 Cobertura y métricas

* Se publica como cifra la **cobertura**: el porcentaje del tiempo en pantalla y de voz con género atribuido.
* Los umbrales de paridad y de infrarrepresentación se calculan **solo sobre el tiempo atribuido**. Si la cobertura queda por debajo de un mínimo, el informe se marca **«no evaluable»** en lugar de calcular sobre una parte pequeña. El mínimo lo fijará el equipo tras medir el vídeo de prueba; no se propone una cifra sin ese dato.
* El TIF (ADR-0011) encaja sin cambios: ya exige mujeres con voz y con rótulo.

### 2.4 Revisión humana

El panel de revisión **no permite asignar género mirando a la persona**. La persona revisora **confirma o refuta la evidencia textual** que se le muestra, o deja «no determinable». Esto cambia las opciones actuales del panel («Mujer», «Hombre», «No determinable»).

## 3. Alternativas consideradas

| Alternativa | Por qué no |
|---|---|
| **A. Mantener cara y voz** (estado actual) | Sitúa al sistema en el Art. 50(3) y arrastra los errores del modelo visual. No es una exigencia de alto riesgo, pero es la parte más difícil de justificar. |
| **B. Solo revisión humana mirando la imagen** | Traslada la misma inferencia (género por rasgos físicos) a una persona, sin evidencia que se pueda señalar. |
| **C. Mixta sin distinguir modo** | Mantiene la ambigüedad legal: no se sabría en qué modo se ha producido cada dato. |
| **D. Solo listas de nombres** | Reproduce los sesgos de los nombres (unisex, extranjeros, errores de transcripción) sin otra evidencia. |

## 4. Consecuencias

* **Positivas:**
  * El sistema deja de hacer categorización biométrica por defecto, lo que simplifica la posición ante el Art. 50(3) para quien lo despliegue, aunque sigan aplicándose los datos personales del RGPD (nombres de los rótulos).
  * Mejor trazabilidad: cada género tiene una evidencia que se puede enseñar.
  * Ahorro de cómputo (*Green AI*): el modo de producción no necesita el clasificador de género de cara ni el de voz.
* **Negativas y riesgos:**
  * **Cobertura menor.** Las personas sin rótulo ni alusión (público, fondo) quedarán «sin atribuir» y no contarán en la paridad. Hay que explicarlo, y la cifra de cobertura debe verse siempre junto a las métricas.
  * **Idiomas.** El extractor trabaja con español, catalán e inglés. En inglés el género gramatical de la autorreferencia es mucho menos informativo; dependerá más de títulos y pronombres.
  * **Género atribuido, no identidad.** El género gramatical con el que se habla de alguien no equivale a su identidad. Se mantiene la salvaguarda de ADR-0006 para identidades no binarias, y el campo se documenta como «género atribuido por evidencia textual».
  * **Trabajo de implementación** (ver 5) y revisión por parte de Rocío, con la congelación del jueves.
* **No cambia:** el reparto entre inferencia y cálculo (los modelos extraen evidencias; los números los calcula Python), ni el resto de principios del ADR-0004 (vectores efímeros).

## 5. Plan

1. **Fase 1, documentación (hasta el 30/10):** registrar esta decisión, actualizar los documentos y presentarla en la entrega como **limitación conocida y siguiente paso**. No se afirma que esté implementada.
2. **Fase 2, código (a decidir con Rocío; no antes del cierre salvo acuerdo):**
   * Etapa nueva `core/silver/gender_text.py`, que combina las evidencias.
   * Ajuste de `IdentitySilver._people` y de `fuse_gender` para usar solo las fuentes configuradas.
   * Opción `silver.gender_sources`. **Durante la transición, el valor por defecto sigue siendo el actual (`video`, `audio`)** para no cambiar los tests, la demostración ni los resultados ya publicados. Se pasará a `texto` por defecto solo después de medir la cobertura en el vídeo de prueba (punto 3) y con acuerdo del equipo.
   * Ampliación del extractor de menciones para la autorreferencia.
   * Pruebas unitarias y cambio del panel de revisión.
3. **Verificación:** ejecutar el vídeo de prueba `robot-social-csic-1526` con las dos configuraciones y comparar género atribuido, cobertura y alertas. El resultado se documenta antes de fijar el mínimo de cobertura.

## 6. Fuentes

* Reglamento (UE) 2024/1689: Arts. 3.40, 5.1.g, 50.3 y Anexo III.1.b; ejemplar en `documentacion-tecnica/admin_y_bases/`.
* Comisión Europea, *Guidelines on the implementation of the transparency obligations for certain AI systems under Article 50 of the AI Act*, C(2026) 5054 final, 20/07/2026 (apartados 99 a 108 y 153): https://digital-strategy.ec.europa.eu/en/library/guidelines-transparency-obligations-providers-and-deployers-ai-systems
* Comisión Europea, *Draft Commission guidelines on the classification of high-risk AI systems*, 19/05/2026 (Anexo III, punto 1.b, apartados 165 a 170): https://digital-strategy.ec.europa.eu/en/library/draft-guidelines-high-risk
* Código: `aiasn/core/silver/gender.py`, `aiasn/core/silver/identity.py`, `aiasn/model_adapters/nlp/mentions.py` (estado en `dev` a 28/10/2026).

