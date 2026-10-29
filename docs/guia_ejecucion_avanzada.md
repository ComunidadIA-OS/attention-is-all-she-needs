<!--
SPDX-FileCopyrightText: 2026 Equipo 1: Attention Is All She Needs (Alba Camiña García, Pilar de la Fuente Diez, Rocío Jiménez Villén)
SPDX-License-Identifier: Apache-2.0
-->

# Guía de ejecución avanzada

Complementa la sección «Cómo probarlo» del README: ejecución sin Docker, trazas del LLM con Langfuse y vídeo anotado.

[← Volver al README](../README.md)

---

## A. Demo sin Docker

```bash
uv sync --extra worker --extra api    # ~7 GB (PyTorch y CUDA)
uv run uvicorn aiasn.api.app:create_app --factory --port 8000
python -m http.server 8080 --directory frontend-piloto   # front en http://localhost:8080/?api=http://localhost:8000
```

Sin la imagen `aiasn-worker`, la API lanza el *worker* como proceso (`API__LAUNCHER=process` para forzarlo) y guarda el lake en `data/`. También se puede procesar un vídeo sin la API:

```bash
uv run python -m aiasn.run_pipelines --file video.mp4
```

## B. Trazas del LLM con Langfuse (opcional)

Langfuse, autoalojado, guarda cada llamada al LLM: prompt, respuesta, modelo, duración y tokens. Sin él, el análisis funciona igual.

1. En `.env` (copiado de `.env.example`), activa las trazas y pon tus valores:
   ```env
   LANGFUSE_ENABLED=true
   LANGFUSE_PUBLIC_KEY=pk-lf-...          # inventadas: Langfuse crea el proyecto con estas claves al arrancar
   LANGFUSE_SECRET_KEY=sk-lf-...
   LANGFUSE_INIT_USER_EMAIL=admin@aiasn.local
   LANGFUSE_INIT_USER_PASSWORD=...        # tu usuario de la web de Langfuse
   ```
   Cambia también los secretos del servidor (`LANGFUSE_NEXTAUTH_SECRET`, `LANGFUSE_SALT`, `LANGFUSE_ENCRYPTION_KEY` y las contraseñas de Postgres, ClickHouse y Redis); genera cada uno con `openssl rand -hex 32`.
2. Arranca la demo con Langfuse. Si ya estaba construida, reconstruye las imágenes, porque el *worker* necesita el paquete `langfuse`:
   ```bash
   docker compose --profile jobs build
   docker compose --profile langfuse up -d   # la demo y Langfuse en http://localhost:3000
   ```
   Sin Docker, `LANGFUSE_BASE_URL=http://localhost:3000` apunta al mismo servidor.
3. Analiza un vídeo y abre <http://localhost:3000> con tu usuario → proyecto «AIASN piloto» → **Sessions**. Hay una sesión por vídeo, con su `video_id`, y en ella sus llamadas al LLM, cada una con el nombre de su tarea.

Si las claves no coinciden o Langfuse no está arrancado, el *worker* lo avisa en su log y sigue sin trazas.

## C. Vídeo anotado: comprobar el resultado a ojo

Dibuja sobre el vídeo lo que ha detectado el pipeline:
* una caja por persona con `P<id> | F/M`;
* una caja verde *speaking* en la cara de quien habla;
* en amarillo, los textos que lee el OCR.

Funciona **sin Docker**, después de procesar el vídeo, porque usa los fotogramas que quedan en `tmp/<video_id>/video/frames`. Con Docker, esos fotogramas se borran con el contenedor del *worker*.

```bash
uv run python scripts/annotate_video.py <video_id>   # → tmp/<video_id>/video/annotated.mp4
```
