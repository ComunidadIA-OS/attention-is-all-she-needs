# SPDX-FileCopyrightText: 2026 Equipo 1: Attention Is All She Needs (Alba Camiña García, Pilar de la Fuente Diez, Rocío Jiménez Villén)
# SPDX-License-Identifier: Apache-2.0

# The front: the static pages, and /api passed on to the API so both share one origin (no CORS, no API port to set)
FROM nginx:1.29.8-alpine
COPY docker/front.nginx.conf /etc/nginx/conf.d/default.conf
COPY frontend-piloto /usr/share/nginx/html
