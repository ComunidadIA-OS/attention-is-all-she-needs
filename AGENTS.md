<!--
SPDX-FileCopyrightText: 2026 Equipo 1: Attention Is All She Needs (Alba Camiña García, Pilar de la Fuente Diez, Rocío Jiménez Villén)
SPDX-License-Identifier: Apache-2.0
-->

# 🤖 AGENTS.md — Guardarraíles de Seguridad, Licencias y Ética para Agentes de Código
## Proyecto: «Attention Is All She Needs» (AIASN)

Este archivo define las **reglas e invariantes inquebrantables** que cualquier agente de programación asistida por IA (GitHub Copilot, Cursor, Claude Code, Google Antigravity, Windsurf, etc.) y cualquier persona contribuidora deben respetar al leer, generar o modificar código en este repositorio.

---

## 1. Las 7 Invariantes Inquebrantables del Código (*Hard Guardrails*)

Ningún cambio, refactorización o Pull Request generado por un agente puede vulnerar estas 7 reglas:

1. **Separación Estricta entre Inferencia y Cálculo Determinista (ADR-0001 — Anti-Inyección de Prompts):**
   * Los modelos de IA (`Whisper`, `YOLOX`/`YOLO11m`, `miVOLO`, `EasyOCR`, `GLiNER`, `Qwen`, `Llama`) **jamás deben calcular porcentajes, sumas de tiempos ni emitir el veredicto de paridad**.
   * El 100 % de la aritmética temporal, el solape de intervalos y la matriz de los 4 cuadrantes se calcula de forma determinista en Python (`pandas`) dentro de `aiasn/core/`.
2. **Aislamiento Estricto de Licencias Permisivas en el Núcleo (ADR-0002 / ADR-0008 — Cortafuegos Anti-AGPL):**
   * Queda **estrictamente prohibido** añadir `import ultralytics` o cualquier dependencia con licencia copyleft (`GPL` / `AGPL-3.0`) dentro de `aiasn/core/`, `aiasn/model_adapters/` o en la lista `dependencies` base de `pyproject.toml`.
   * El núcleo (`[core]`) y el perfil corporativo B2B (`[permissive-vision]`) deben mantenerse 100 % bajo licencias permisivas compatibles con **Apache-2.0** (`MIT`, `BSD-3-Clause`, `Apache-2.0`, como `YOLOX`, `ONNX Runtime`, `InsightFace`, `EasyOCR`). Las librerías experimentales con AGPL viven exclusivamente aisladas en el perfil opcional `[notebooks-research]` y se comunican por archivo plano (`.csv`/`.tsv`) a través de `CSVPrecomputedAdapter`.
3. **Biometría Efímera y Purga en RAM (*Zero Facial Retention* — ADR-0004 / RGPD):**
   * Queda **prohibido** guardar en disco, exportar en `.csv`/`.parquet` o devolver en DataFrames vectores biométricos faciales o vocales (`embedding`, `face_embedding`, `face_vector`, `biometric_hash`).
   * Todo adaptador visual debe pasar obligatoriamente por `BaseVisionAdapter.validar_y_sanitizar_contrato()`, que purga dichas columnas en memoria RAM.
4. **Prohibición Absoluta de Reconocimiento Biométrico de Emociones (Art. 5.1.f RIA — ADR-0009):**
   * Queda **prohibido** introducir modelos o funciones que infieran emociones, estados de ánimo o rasgos psicológicos a partir de expresiones faciales o del tono/timbre de voz.
5. **Cortafuegos de Abstención Ética ($p < 0{,}80 \rightarrow \text{"no\_determinado"}$ — ADR-0005):**
   * Nunca se debe eliminar ni rebajar por debajo de `0.80` el umbral de confianza por defecto ni forzar una clasificación binaria (`H`/`M`) cuando la certeza sea baja. Los segmentos con $p < 0{,}80$ deben etiquetarse siempre como `"no_determinado"` para supervisión humana (*Human-in-the-Loop*).
6. **Integridad Criptográfica del Sello Oficial (`SHA-256`) y Protección contra Lavado de Cara (Art. 6 Apache-2.0):**
   * La función `emitir_sello_auditoria()` y el modelo `ElegibilidadEticaEntidad` en `aiasn/model_adapters/vision_adapter.py` no deben modificarse para eludir la comprobación de ausencia de sanciones graves (ventana de 3 años o vía de rehabilitación *Self-Cleaning* con informes históricos), la muestra sin *cherry-picking*, la firma del operador (`operador_supervision_id`) ni el cálculo del hash `SHA-256`.
7. **Conformidad REUSE (FSFE) y Seguridad de Credenciales:**
   * Todo archivo nuevo creado en el repositorio debe incluir en sus primeras líneas la cabecera SPDX oficial (`SPDX-FileCopyrightText: 2026 Equipo 1: Attention Is All She Needs...` y `SPDX-License-Identifier: Apache-2.0`).
   * Jamás se deben escribir tokens, claves de API de OVHcloud ni datos personales reales en el código fuente o en los tests.

---

## 2. Verificación Obligatoria Antes de Proponer Cambios

Antes de dar por válida cualquier modificación en el código, el agente debe ejecutar y verificar que pasa el 100 % de la suite de pruebas deterministas y de cumplimiento:

```bash
python -m pytest tests/ -v
```

---

## 3. Mapa Rápido del Repositorio para Agentes

* `aiasn/core/`: Motor matemático determinista de fusión multimodal, solapes y cálculo de los 4 cuadrantes (*Seeing and Hearing*). **Cero llamadas a red, cero GPUs, 100 % Apache-2.0.**
* `aiasn/model_adapters/`: Adaptadores desacoplados (`CSVPrecomputedAdapter`, `PermissiveYOLOXAdapter`), purga biométrica en RAM y emisión del Sello Oficial con firma `SHA-256` (`emitir_sello_auditoria`).
* `tests/`: Pruebas unitarias de contratos de datos (`test_contracts.py`), adaptadores, purga biométrica, rehabilitación corporativa a 3 años y firma `SHA-256` (`test_compliance_adapters.py`).
* `CODE_OF_CONDUCT.md`: Código Ético a medida, Estatuto de Propósito Social (*Social Open Steward*), Círculo Virtuoso sin reentrenamiento (`Top Rosies Talent` / `WikiMujeres`) y Cláusula Anti-Lavado de Cara.
* `SECURITY.md`: Modelo de amenazas frente a ataques adversarios (Art. 15 RIA y OWASP ML/LLM) y protocolo de divulgación coordinada.
* `GLOSSARY.md`: Glosario canónico de los 25 términos y elementos arquitectónicos de la solución.

