<!--
SPDX-FileCopyrightText: 2026 Equipo 1: Attention Is All She Needs (Alba Camiña García, Pilar de la Fuente Diez, Rocío Jiménez Villén)
SPDX-License-Identifier: Apache-2.0
-->

# Frontend del piloto — Constelación del Protagonismo

Réplica de la maqueta «Constelación del Protagonismo» conectada a la API del backend. Es HTML, CSS y JS sin compilación ni dependencias. Las fuentes IBM Plex se sirven desde `fonts/`, sin Google Fonts, así que funciona sin conexión y no envía datos de quien la visita.

## Uso

Con Docker, el contenedor `front` la sirve en <http://localhost:8080> y le pasa `/api` a la API (ver README principal):

```bash
docker compose up -d
```

Sin Docker, sírvela con cualquier servidor estático e indícale dónde está la API:

```bash
python -m http.server 8080 --directory frontend-piloto      # y abrir http://localhost:8080/?api=http://localhost:8000
```

* **Al abrirla** sale vacía hasta que se analiza un vídeo. Con `?demo` muestra la maqueta con sus datos de muestra, tal cual.
* **«Elegir vídeo» → «Analizar»** sube un vídeo a la API, sigue su procesado y repinta la página con el resultado. La dirección de la página guarda el vídeo (`?video=<id>`) para volver a abrirlo o compartirlo.
* **`?api=<url>`** cambia la dirección de la API. Por defecto es `/api`, la del contenedor `front`.

## Con datos reales

El front no calcula indicadores: todo viene de la API (ADR-0001). `js/adapter.js` solo traduce la respuesta de la API a lo que dibuja la página. Lo que el backend aún no calcula se muestra como «—»:

* **Protagonismo de cada persona.** Mientras tanto, el tamaño de cada estrella es su tiempo de voz, y la leyenda lo indica.
* **Ratio voz/pantalla por persona.** El del veredicto sí viene de la API (% de voz ÷ % de pantalla).

El índice de representación es provisional hasta que se cierre la definición de su señal de autoridad. Quién abre y cierra la pieza y las interrupciones quedan fuera del piloto: solo aparecen en la maqueta (`?demo`).

Las posiciones de las estrellas se calculan solas: cada persona se coloca cerca de los temas de los que habla, separada de las demás según su tamaño.

## Estructura

| Fichero | Función |
|---|---|
| `index.html`, `styles.css` | Marcado y estilos de la maqueta, con identificadores en las cifras que cambian y el control de subida en la cabecera. |
| `js/app.js` | Cielo (`canvas`), ficha, gráficos, tema claro u oscuro y modo con datos reales. |
| `js/adapter.js` | Respuesta de la API → datos de la página. Funciones puras. |
| `fonts/` | IBM Plex (OFL-1.1, © IBM Corp.). |
| `tests/run.mjs` | Pruebas del adaptador: `node frontend-piloto/tests/run.mjs`. |
