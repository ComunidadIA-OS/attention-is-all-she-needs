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

Parámetros de URL útiles para demostraciones: `?caso=A|B|C`, `?lang=es|ca|en`, `?theme=dark|light`.

## Estructura

| Fichero | Función |
|---|---|
| `index.html` | Estructura semántica y accesible (landmarks, `skip-link`, tablas con `caption`). |
| `styles.css` | Tokens de color (claro/oscuro), componentes, impresión y movimiento reducido. |
| `js/metrics.js` | Réplica de la spec `21` (alertas, Bechdel, salvaguarda ADR-0006, índice, arbitraje HitL). Funciones puras. |
| `js/demo-data.js` | Tres muestras **sintéticas** que reproducen los casos A, B y C de la spec `21` §3.3. |
| `js/i18n.js` | Interfaz en castellano, català y English (ADR-0010). |
| `js/app.js` | Render, supervisión humana, grafo, modo en vivo. |
| `vendor/` | `vis-network` incluido localmente (sin CDN). |
| `tests/run.mjs` | Pruebas sin dependencias. |

## Principios y decisiones

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
- Gallego y euskera en la interfaz (revisión por hablantes).
