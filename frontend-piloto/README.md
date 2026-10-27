<!--
SPDX-FileCopyrightText: 2026 Equipo 1: Attention Is All She Needs (Alba Camiña García, Pilar de la Fuente Diez, Rocío Jiménez Villén)
SPDX-License-Identifier: Apache-2.0
-->

# Frontend del piloto — Constelación del Protagonismo

Réplica de la maqueta «Constelación del Protagonismo» conectada a la API del backend. Es HTML, CSS y JS sin compilación ni dependencias. Las fuentes IBM Plex se sirven desde `fonts/`, sin Google Fonts, así que funciona sin conexión y no envía datos de quien la visita.

## Uso

```bash
docker compose up -d                                        # API en http://localhost:8000 (ver README principal)
python -m http.server 8080 --directory frontend-piloto      # y abrir http://localhost:8080
```

* **Al abrirla** muestra los datos de muestra de la maqueta, tal cual.
* **«Elegir vídeo» → «Analizar»** sube un vídeo a la API, sigue su procesado y repinta la página con el resultado. La dirección de la página guarda el vídeo (`?video=<id>`) para volver a abrirlo o compartirlo.
* **`?api=http://localhost:8010`** cambia la dirección de la API, que por defecto es `http://localhost:8000`.

## Con datos reales

El front no calcula indicadores: todo viene de la API (ADR-0001). `js/adapter.js` solo traduce la respuesta de la API a lo que dibuja la página. Lo que el backend aún no calcula se muestra como «—»:

* **Índice de representación** y su composición.
* **Protagonismo de cada persona.** Mientras tanto, el tamaño de cada estrella es su tiempo de voz, y la leyenda lo indica.
* **Quién abre y cierra** e **interrupciones recibidas**.
* **Ratio voz/pantalla por persona.** El ratio del veredicto es el de la API, cuya definición está pendiente de unificar con la de la maqueta.

Las posiciones de las estrellas se calculan solas: cada persona se coloca cerca de los temas de los que habla.

## Estructura

| Fichero | Función |
|---|---|
| `index.html`, `styles.css` | Marcado y estilos de la maqueta, con identificadores en las cifras que cambian y el control de subida en la cabecera. |
| `js/app.js` | Cielo (`canvas`), ficha, gráficos, tema claro u oscuro y modo con datos reales. |
| `js/adapter.js` | Respuesta de la API → datos de la página. Funciones puras. |
| `fonts/` | IBM Plex (OFL-1.1, © IBM Corp.). |
| `tests/run.mjs` | Pruebas del adaptador: `node frontend-piloto/tests/run.mjs`. |
