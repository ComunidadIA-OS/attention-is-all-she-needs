<!--
SPDX-FileCopyrightText: 2026 Equipo 1: Attention Is All She Needs (Alba Camiña García, Pilar de la Fuente Diez, Rocío Jiménez Villén)
SPDX-License-Identifier: Apache-2.0
-->

# Frontend — Panel de auditoría AIASN

Panel estático (HTML + CSS + JS, sin paso de compilación) que presenta el dictamen de paridad de un vídeo.
Funciona abriendo `index.html` directamente o con cualquier servidor estático, **sin conexión a internet**.

```bash
python -m http.server 8080 --directory frontend   # opcional
node frontend/tests/run.mjs                        # pruebas de lógica e i18n
```

Parámetros de URL útiles para demostraciones: `?caso=A|B|C`, `?fase=preproduccion|edicion|publicado`, `?lang=es|ca|gl|eu|en`, `?theme=dark|light`.

## Fases del material (D-11)

| Fase | Qué hace |
|---|---|
| **Preproducción** | Proyección desde una escaleta editable (persona, género, minutos, rótulo; el orden es el orden de turnos). |
| **Grabación y edición** | Revisión preventiva: franja de borrador, sin sello, anonimización por defecto, margen hasta la paridad, recomendaciones y simulador «¿y si…?». |
| **Publicado** | Auditoría certificable con supervisión humana y huella SHA-256. |

Todo es determinista (spec 21 §8): no hay modelos predictivos. En modo en vivo, la fase se envía a la API como `modo`, `estado_material` y `retencion`.

## Estructura

| Fichero | Función |
|---|---|
| `index.html` | Estructura semántica y accesible (landmarks, `skip-link`, tablas con `caption`). |
| `styles.css` | Tokens de color (claro/oscuro), componentes, impresión y movimiento reducido. |
| `js/metrics.js` | Réplica de la spec `21` (alertas, Bechdel, salvaguarda ADR-0006, índice, arbitraje HitL). Funciones puras. |
| `js/demo-data.js` | Tres muestras **sintéticas** que reproducen los casos A, B y C de la spec `21` §3.3. |
| `js/i18n.js` | Interfaz en castellano, català, galego, euskara y English (ADR-0010). |
| `js/app.js` | Render, supervisión humana, grafo, modo en vivo. |
| `vendor/` | `vis-network` incluido localmente (sin CDN). |
| `tests/run.mjs` | Pruebas sin dependencias. |

## Principios y decisiones

- **ADR-0011 (sin framework ni compilación):** el panel es HTML + CSS + JS estándar para abrirse con doble clic, funcionar sin conexión y no depender de npm. El ADR fija los criterios para migrar a Vite + Preact/React + TypeScript conservando `metrics.js` y sus pruebas.
- **ADR-0001 (inferencia ≠ cálculo):** en producción el veredicto lo entrega la API (motor Python). El cliente solo calcula en las muestras locales o cuando la API aún no devuelve un campo (`alerta_infrarrepresentacion`, `indice_global`). El origen se rotula siempre («Cliente», «API» o «API + cliente»).
- **ADR-0004 / RGPD:** sin biometría en el cliente; «Anonimizar nombres» sustituye nombres y oculta cargos.
- **ADR-0005 / Art. 14 RIA:** los tramos con confianza < 80 % quedan `no_determinado` y se arbitran en pantalla (validar o asumir abstención). La abstención excluye el tramo del denominador. El sello solo pasa a «CONFORME» sin pendientes y con la supervisión asumida. La huella SHA-256 es de integridad; la firma real la emite el backend.
- **ADR-0009:** el clima conversacional es agregado, sobre texto, nunca por persona.
- **ADR-0010 / WCAG 2.2 AA:** icono + texto + forma (nunca solo color), objetivos ≥ 24 px, foco visible, alternativa tabular del grafo, `prefers-reduced-motion`, Lectura Fácil con lectura en voz alta.
- **Green AI / RGPD:** sin CDN ni fuentes remotas; la física del grafo se detiene tras estabilizar.

## Pendiente con backend

- Contrato definitivo de `POST /videos` (campo del fichero) y de `segmentos_dudosos`, `alerta_infrarrepresentacion` e `indice_global` en `resultado.veredicto`.
- Umbrales: el motor Python usa hoy `RVP < 0,40` y `voz < 25 %` para equality-washing; la spec `21` fija `RVP < 0,30` y `voz < 20 %`. Este panel sigue la spec `21`.
- Definición de la dimensión de autoridad del Índice Global (`S_autoridad`), provisional en `metrics.js`.
- **Estado de las traducciones de la interfaz:** castellano (redacción del equipo); **galego revisado por Alba Camiña García**; catalán e inglés con traducción asistida por IA y sin revisión nativa registrada; **euskara con traducción asistida por IA y sin revisar por hablantes** (el equipo no puede revisarla; se declara en la propia interfaz con un aviso visible y en `MODEL_CARD.md`). Se agradece la revisión de personas hablantes.

