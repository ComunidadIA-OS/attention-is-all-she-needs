<!--
SPDX-FileCopyrightText: 2026 Equipo 1: Attention Is All She Needs (Alba Camiña García, Pilar de la Fuente Diez, Rocío Jiménez Villén)
SPDX-License-Identifier: Apache-2.0
-->

# 0011. Frontend estático sin framework ni paso de compilación (HTML + CSS + JavaScript) frente a Vite + React

* **Fecha:** 2026-10-27
* **Estado:** Propuesta, por consenso por silencio (CONTRIBUTING §5.1): plazo de objeciones hasta el **jueves 29/10/2026 a las 12:00 h**. Puede reabrirse después.
* **Decisores:** Alba Camiña García (propuesta); Pilar de la Fuente Diez y Rocío Jiménez Villén (validación)
* **Issue relacionada:** [#5](https://github.com/ComunidadIA-OS/attention-is-all-she-needs/issues/5)
* **Directriz de referencia:** ADR-0001 (separación inferencia/cálculo), ADR-0002 (monolito modular), ADR-0010 (accesibilidad y reutilización en AAPP), Algoritmos Verdes y Art. 10 de las Bases (independencia tecnológica)

---

## Contexto y Problema

El panel de auditoría (`frontend/`) debe:

1. **Ejecutarse en cualquier equipo sin instalar nada**: el jurado del 4 de noviembre, analistas de medios, organismos reguladores y administraciones públicas sin entorno de desarrollo.
2. **Funcionar sin conexión** durante la demostración presencial y en redes institucionales restringidas.
3. **No enviar datos a terceros** (CDN, fuentes remotas), por coherencia con el RGPD y con la privacidad por diseño (ADR-0004).
4. **Ser reutilizable entre administraciones** (Art. 157 Ley 40/2015, ADR-0010) con el menor coste de mantenimiento posible.
5. **Entregarse antes del 30/10/2026 a las 08:00 h** con un equipo de tres personas que reparte su tiempo entre backend, documentación y frontend.

La primera versión del panel usaba Tailwind desde CDN, `vis-network` desde `unpkg` y Google Fonts, y no funcionaba sin red. Se plantea si conviene reconstruirlo sobre un framework de componentes (Vite + React) o mantenerlo estático.

## Opciones Consideradas

1. **Opción A — Vite + React (+ TypeScript):** Componentes declarativos, ecosistema maduro (`react-i18next`, Testing Library, `axe-core`) y tipado del contrato con la API.
   * *Inconvenientes:* exige Node y paso de compilación; el resultado no se abre con doble clic (los navegadores bloquean los módulos ES en `file://`), lo que obliga a servirlo o a añadir un empaquetado en fichero único; añade cientos de paquetes npm al árbol de dependencias (licencias que declarar para REUSE y riesgo de cadena de suministro); reescribir ~3.000 líneas probadas a tres días de la entrega.
2. **Opción B — Vite + Preact o Svelte:** Mismas ventajas que A con menor peso (Preact ≈ 4 KB frente a ≈ 45 KB de React + ReactDOM comprimidos).
   * *Inconvenientes:* los mismos de compilación, servidor y plazo que A.
3. **Opción C — HTML + CSS + JavaScript estándar, sin framework ni compilación:** Página estática con dependencias incluidas en el repositorio (`frontend/vendor/`).
   * *Inconvenientes:* renderizado imperativo (la vista se repinta entera y el foco se recoloca a mano), sin tipado estático y con componentes implementados como funciones que construyen DOM.

## Decisión Adoptada

Se adopta la **Opción C** para el prototipo del reto, con estas reglas:

1. **Sin paso de compilación y sin recursos remotos:** `index.html` se abre directamente (`file://`) o desde cualquier servidor estático. La única dependencia de terceros, `vis-network` (Apache-2.0), se incluye en `frontend/vendor/` con su fichero `.license` (REUSE).
2. **Lógica separada de la presentación:** Las reglas de la especificación 21 (alertas, Test de Bechdel, salvaguarda ADR-0006, Índice Global, lectura del grafo, arbitraje HitL) viven en `frontend/js/metrics.js` como **funciones puras sin DOM**, cubiertas por pruebas ejecutables con `node frontend/tests/run.mjs` sin instalar paquetes. Esta capa es independiente del framework y se reutilizaría íntegra en una migración.
3. **Seguridad del renderizado:** El contenido se inserta con `textContent` y nodos DOM (función `h()`), nunca con `innerHTML`, para evitar inyección de HTML desde los datos de la API.
4. **Accesibilidad e idiomas sin dependencias:** WCAG 2.2 AA (foco visible, objetivos ≥ 24 px, alternativa tabular del grafo, `prefers-reduced-motion`) e interfaz en `es`, `ca`, `gl`, `eu` y `en` mediante un diccionario propio (`frontend/js/i18n.js`) con pruebas de completitud.
5. **Visualización en Canvas 2D Isométrico frente a Esferas 3D (WebGL / Three.js):**
   * *Anti-oclusión pericial:* En 3D los nodos grandes de oradores dominantes ocultan físicamente a los nodos situados detrás según la rotación de cámara. En auditoría pericial es inadmisible ocultar ponentes mujeres o no binarias por perspectiva.
   * *Isometría métrica:* En 3D el tamaño del nodo ($\text{voz} + 0{,}5 \times \text{pantalla}$) se falsea visualmente por el punto de fuga; en Canvas 2D la escala es isométrica y matemáticamente fidedigna.
   * *Accesibilidad (ADR-0010):* WebGL es una caja negra para lectores de pantalla (`NVDA`/`JAWS`), mientras que el Canvas 2D se traduce de forma biunívoca a una tabla accesible alternativa.
   * *Algoritmos Verdes (Green AI):* Frente al consumo continuo de 30–70 W en la GPU del cliente que provocan los bucles a 60 fps en 3D, el Canvas 2D congela la física tras estabilizarse (*cooling*), consumiendo **0 W en reposo**.
   * *Avance interactivo 3D Fase 2 (Galaxia 3D):* Se incorpora un modo alternativo conmutable («🔭 Galaxia 3D») desarrollado en Canvas 2D puro mediante proyección matemática trigonométrica (cero dependencias externas, cero npm/CDN). Permite rotar en 360°, viajar por las capas de profundidad y ver los impulsos luminosos de diálogo para divulgación y pitch, desactivando el bucle de renderizado automáticamente al volver al Planisferio 2D o cuando la pestaña no es visible (cumplimiento estricto de Green AI).
   * *Fundamentación científica:* Tamara Munzner (*Visualization Analysis and Design*) y McInnes et al. (UMAP, 2018) demuestran que el 3D introduce fatiga cognitiva y no aporta separación interpretable para grafos de menos de 50 entidades.

### Tamaño actual (27/10/2026)

| Fichero | Líneas | Tamaño |
| :--- | ---: | ---: |
| `index.html` | 545 | 33 KB |
| `styles.css` | 435 | 25 KB |
| `js/app.js` | 1.376 | 57 KB |
| `js/i18n.js` (5 idiomas) | 1.686 | 111 KB |
| `js/metrics.js` | 488 | 18 KB |
| `js/demo-data.js` | 101 | 7 KB |
| `vendor/vis-network.min.js` | — | 689 KB |

## Criterios de Revisión (cuándo migrar a componentes)

Se reabrirá esta decisión y se migrará a **Vite + Preact (o React) + TypeScript**, conservando `metrics.js` y sus pruebas, cuando se cumpla **cualquiera** de estas condiciones:

* El panel necesite **más de una vista** (listado e histórico de expedientes, comparativas entre piezas, panel por rol).
* Se incorporen **autenticación, persistencia o firma real** de dictámenes en el cliente.
* **Más de una persona** trabaje en el frontend de forma simultánea y continuada.
* `app.js` supere las **~2.500 líneas** o el repintado completo cause problemas medibles de rendimiento o de foco.

## Consecuencias

* **Positivas:**
  * Se abre con doble clic y funciona sin conexión: demostración robusta ante el jurado y despliegue trivial en cualquier administración.
  * Ninguna petición a terceros en tiempo de ejecución (coherencia con RGPD, ADR-0004 y Algoritmos Verdes).
  * Cero dependencias de compilación: sin `node_modules`, sin auditoría de cientos de licencias y superficie de cadena de suministro mínima.
  * La lógica pericial está probada y desacoplada, lo que abarata una migración futura.
* **Compromisos asumidos:**
  * Renderizado imperativo: cada cambio repinta la vista completa y la gestión del foco se hace a mano (`focusAfterRender`). Debe mantenerse cubierta por las comprobaciones de interacción.
  * Sin tipado estático del contrato con la API: los nombres de campo se normalizan en `buildApiView()` y deben revisarse con cada cambio del backend.
  * **El mayor peso no es el código propio, sino `vis-network` (≈ 689 KB).** Queda como mejora pendiente cargarlo solo cuando la sección de la constelación sea visible, o sustituirlo por una alternativa más ligera.

