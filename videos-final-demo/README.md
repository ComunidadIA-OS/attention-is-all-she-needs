<!--
SPDX-FileCopyrightText: 2026 Equipo 1: Attention Is All She Needs (Alba Camiña García, Pilar de la Fuente Diez, Rocío Jiménez Villén)
SPDX-License-Identifier: Apache-2.0
-->

# Vídeos de la demo

Todos tienen licencia libre: se pueden compartir y analizar citando la autoría.

| Fichero | Duración | Qué muestra | Original y autoría | Licencia |
|---|---|---|---|---|
| `clip_1_wikimania.mp4` | 3:38 | Panel con dos mujeres y dos hombres | [Wikipedia Five Pillars Panel](https://commons.wikimedia.org/wiki/File:Wikimania_2015_-_Wikipedia_Five_Pillars_Panel.webm), Wikimedia México (Wikimania 2015) | CC BY-SA 3.0 |
| `clip_2_wikimania.mp4` | 5:12 | El mismo panel, otro tramo | El mismo | CC BY-SA 3.0 |
| `clip_mesa_redonda.mp4` | 5:11 | Videollamada con dos mujeres y dos hombres | [Mesa redonda FLISoL Tenerife 2021](https://archive.org/details/flisoltenerife20211mesa-redonda), FLISoL Tenerife | CC BY-SA 4.0 |
| `csic_javier_oroz.mp4` | 1:24 | Solo habla él; las investigadoras salen sin voz | [CSIC Cicerón: Javier Oroz](https://www.youtube.com/watch?v=V6I84IL-L0o), CSIC Comunicación | CC BY 4.0 |
| `margarita_salas.mp4` | 5:00 | Conferencia con rótulos; cita a Severo Ochoa como referente | [Dra. Margarita Salas, «Mujer y Ciencia: mi propia experiencia»](https://www.youtube.com/watch?v=2nlMCQlT58g), Vall d'Hebron Barcelona Hospital Campus | CC BY 4.0 |
| `cultura_igualdad.mp4` | 4:56 | Diálogo con rótulos de nombre y cargo | [Diálogo entre Ernest Urtasun y Nerea Pérez de las Heras](https://www.youtube.com/watch?v=IW9_5ngb4Nc), Ministerio de Cultura | CC BY 4.0 |

- Todos menos el del CSIC son recortes del original (Margarita Salas y Cultura: los 5 primeros minutos; Cultura, sin los 4 s del cartel inicial). Los CC BY-SA llevan su misma licencia (*ShareAlike*). El vídeo del CSIC está completo y sin cambios.
- No aparecen menores. Las personas intervienen en público y en actos grabados para difundirse.
- Al mostrarlos hay que citar la autoría, la licencia y, en los clips, que están recortados.
- Los `.mp4` no están en git: se comparten por Drive.

## Medición (29/10/2026)

En Ubuntu 24.04 con un Ryzen 7 7840HS, 30 GB de RAM y una RTX 4060 Laptop (8 GB), con Docker y los modelos ya descargados. Audio y vídeo van en paralelo, así que el total no es la suma de los pasos. Tiempos en segundos.

| Fichero | Audio | Total | Audio (transcripción) | Vídeo: detección · hablante · OCR | NLP | Rótulos | Silver + gold |
|---|---|---|---|---|---|---|---|
| `clip_1_wikimania.mp4` | 3,6 min | 348 | 22 | 310: 204 · 61 · 32 | 49 | 13 | 5 |
| `clip_2_wikimania.mp4` | 5,2 min | 455 | 26 | 424: 283 · 81 · 43 | 59 | 7 | 5 |
| `clip_mesa_redonda.mp4` | 5,2 min | 523 | 26 | 453: 290 · 84 · 67 | 214 | 51 | 0,4 |
| `csic_javier_oroz.mp4` | 1,4 min | 108 | 7 | 75: 50 · 7 · 13 | 16 | 10 | 5 |
| `margarita_salas.mp4` | 5,0 min | 377 | 22 | 322: 246 · 43 · 20 | 64 | 30 | 5 |
| `cultura_igualdad.mp4` | 4,9 min | 374 | 30 | 237: 189 · 25 · 14 | 76 | 113 | 5 |

Tokens del LLM (OVHcloud AI Endpoints), medidos con el `usage` de LiteLLM:

| Fichero | Llama 3.3 70B: llamadas · entrada · salida | gpt-oss-120b (referentes): llamadas · entrada · salida |
|---|---|---|
| `clip_1_wikimania.mp4` | 11 · 9.134 · 3.156 | 1 · 1.239 · 281 |
| `clip_2_wikimania.mp4` | 6 · 7.602 · 2.659 | 1 · 1.445 · 116 |
| `clip_mesa_redonda.mp4` | 14 · 14.081 · 5.397 | 1 · 1.831 · 246 |
| `csic_javier_oroz.mp4` | 10 · 5.514 · 1.912 | 1 · 665 · 175 |
| `margarita_salas.mp4` | 13 · 12.494 · 5.145 | 1 · 1.638 · 1.124 |
| `cultura_igualdad.mp4` | 36 · 26.012 · 9.143 | 1 · 1.757 · 936 |

La transcripción (Whisper large v3) se cobra por duración del audio. Los rótulos son la tarea que más llamadas hace: una por cada 4 bloques de texto leídos por el OCR.

SHA-256 de los ficheros:

```
1bc959e4da17d302ce13ef6e9013c77ada060fceb022f15992e5ece2b37da0e6  clip_1_wikimania.mp4
3c556965eb4bfe94f8cad5c46efcdba3bd8a5655008fec106f4459e05fcdbc92  clip_2_wikimania.mp4
71b1fa48023d223fc5e270ab65ac1181d73759cead0e08889b6bc9137565f7bf  clip_mesa_redonda.mp4
5c4a1cda5cc45685cc3c4b69195a2313a8a8583514408c8b94f736ad8d077583  csic_javier_oroz.mp4
bd2e98c5e5fe5063d03df96e65221e00669677eb1c0bd057d83ef4cd054775a4  margarita_salas.mp4
2e8c54f97ffe93ad9843eb17ca6f9c0f7ba68b6b2b8530c903b1b8826bc5d2f7  cultura_igualdad.mp4
```
