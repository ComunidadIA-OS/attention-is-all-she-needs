# 0008. Ingesta agnóstica parametrizable y régimen legal de fuentes (Garantía UPC y Compliance Profesional Independiente)

* **Fecha:** 2026-10-21
* **Estado:** Aceptada
* **Decisores:** Equipo AIASN (Alba Camiña García, Rocío Jiménez Villén, Pilar de la Fuente Diez)
* **Directriz de referencia:** Orientación de la Dra. Karina Gibert (Decana COEINF / Directora IDEAI-UPC), Art. 67 del RDL 24/2021, Art. 32.1 LPI y Art. 50 del RIA

---

## Contexto y Problema

Ante dudas sobre los derechos de autor de emisiones audiovisuales públicas y los términos de servicio de plataformas de vídeo, el equipo elevó consulta formal a la **Dra. Karina Gibert**. Las directrices vinculantes recibidas confirmaron:
1. *Audio:* Los datos de habla de TV3 son gentileza académica formal de la UPC (grupo del Dr. Adrián Fonollosa).
2. *Vídeo y Prototipo:* El equipo debe posicionarse como un equipo de profesionales independiente que entrega una auditoría ética y *compliant*.

## Opciones Consideradas

1. **Opción A (Web Scraper masivo automatizado):** Descargar automáticamente vídeos institucionales de internet. *(Descartada por vulnerar ToS y prohibición expresa de scraping sin licencia).*
2. **Opción B (Pipeline acoplado a un único archivo local):** *(Descartada por incumplir el principio de interoperabilidad).*
3. **Opción C (Ingesta agnóstica desacoplada + régimen legal diferenciado):**
   * El software recibe la fuente como parámetro agnóstico (`archivo local` o `URL autorizada`), entregando al núcleo el mismo contrato de datos `Pydantic`.
   * En el MVP del reto, las pruebas se realizan exclusivamente con datos cedidos (UPC) o muestras breves bajo excepción legal de cita y análisis científico (Art. 67 RDL 24/2021 y Art. 32.1 LPI), sin almacenar archivos de vídeo en GitHub.
   * En fase de producción comercial, las entidades auditadas son clientes directos que aportan sus contenidos bajo convenio o API privada.

## Decisión Adoptada

Se adopta la **Opción C**.

## Consecuencias

* **Positivas:**
  * Respaldo institucional formal en audio (UPC).
  * Repositorio de código abierto 100 % limpio de archivos multimedia con copyright de terceros.
  * Neutralidad jurídica asegurada para la presentación en el Auditorio Vèrtex de la UPC.
* **Compromisos asumidos:**
  * La documentación técnica debe explicitar el fundamento legal de cada fuente y la nota de transparencia del Art. 50 del RIA.

