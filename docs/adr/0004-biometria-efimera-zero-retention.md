# 0004. Biometría efímera en memoria (*Zero Retention Policy*) frente a persistencia de plantillas

* **Fecha:** 2026-10-16
* **Estado:** Aceptada
* **Decisores:** Equipo AIASN (Alba Camiña García, Rocío Jiménez Villén, Pilar de la Fuente Diez)
* **Directriz de referencia:** Art. 50 del Reglamento Europeo de IA (RIA), RGPD y Dra. Karina Gibert (`1:18:30`, `1:34:20`)

---

## Contexto y Problema

El RGPD (Reglamento UE 2016/679) y el Reglamento Europeo de IA (Art. 50 del RIA) imponen estrictas salvaguardas al tratamiento de datos biométricos identificativos (vectores faciales y huellas acústicas). La Dra. Karina Gibert alertó taxativamente sobre la ilegalidad de almacenar bases de datos biométricas de personas sin su consentimiento informado expreso y sobre los riesgos de re-identificación o vigilancia no consentida.

## Opciones Consideradas

1. **Opción A (Base de Datos Biométricas Vectoriales):** Almacenar embeddings faciales (512D) y descriptores acústicos permanentes para reconocer a los tertulianos en vídeos futuros. *(Descartada por violación de los principios de minimización y finalidad del RGPD y alto riesgo bajo el RIA).*
2. **Opción B (Política de Retención Cero / Zero Retention Policy):** Los vectores biométricos se calculan exclusivamente en memoria volátil (RAM/VRAM) durante la ejecución para seguir al sujeto en la escena, y **se destruyen inmediatamente al finalizar el análisis del clip**. En disco y bases de datos solo se persisten marcas de tiempo, coordenadas delimitadoras (`x1, y1, x2, y2`), ratios agregados y nombres declarados oficialmente en rótulos OCR.

## Decisión Adoptada

Se adopta la **Opción B**. AIASN no persiste, indexa ni comercializa huellas biométricas.

## Consecuencias

* **Positivas:**
  * Cumplimiento estricto del RGPD y del Art. 50 del RIA (*Privacy by Design*).
  * Inmunidad técnica ante fugas de información sensible (no hay vectores biométricos que puedan ser filtrados).
  * Aprobación asegurada en la evaluación ética ALTAI.
* **Compromisos asumidos:**
  * El sistema no recuerda identidades entre vídeos independientes sin el apoyo de rótulos (*chirons*) de texto o metadatos públicos; cada contenido se audita de forma autónoma.

