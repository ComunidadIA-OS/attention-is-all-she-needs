# Registro de Decisiones de Arquitectura (ADRs)
## Proyecto: «Attention Is All She Needs» (AIASN)

Este directorio contiene los **Registros de Decisiones de Arquitectura (*Architectural Decision Records* - ADRs)** del proyecto AIASN, siguiendo la metodología estándar de [Michael Nygard](http://thinkrelevance.com/blog/2011/11/15/documenting-architecture-decisions) ampliamente adoptada en proyectos de código abierto de la Cloud Native Computing Foundation (CNCF), Apache Software Foundation y Python Software Foundation.

Cada registro documenta el **contexto técnico o legal**, las **alternativas analizadas**, la **decisión colegiada adoptada** y las **consecuencias y compromisos (*trade-offs*)** asumidos por el equipo de ingeniería paritario (**Alba Camiña García**, **Pilar de la Fuente Diez** y **Rocío Jiménez Villén**).

---

## Índice de Decisiones de Arquitectura

| Número | Título de la Decisión | Estado | Fecha | Directriz / Referencia Principal |
| :---: | :--- | :---: | :---: | :--- |
| [**0001**](0001-separacion-estricta-inferencia-calculo.md) | Separación estricta entre extracción heurística por IA y cálculo estadístico determinista en Python | **Aceptada** | 2026-10-16 | Karina Gibert (IDEAI-UPC) y Robustez Técnica ALTAI |
| [**0002**](0002-monolito-modular-perfiles-opcionales.md) | Monolito modular desacoplado (`[core]`, `[local-ai]`, `[gpu]`) frente a microservicios | **Aceptada** | 2026-10-17 | Bases Art. 10 y Montse Guàrdia (Consell Social UPC) |
| [**0003**](0003-muestreo-selectivo-stride-green-ai.md) | Muestreo selectivo de fotogramas (`STRIDE` 1–5 fps) guiado por audio frente a 30 fps continuos | **Aceptada** | 2026-10-16 | Verónica Vilaplana (TALP-UPC) y Algoritmos Verdes |
| [**0004**](0004-biometria-efimera-zero-retention.md) | Biometría efímera en memoria (*Zero Retention Policy*) frente a persistencia de plantillas | **Aceptada** | 2026-10-16 | Art. 50 RIA, RGPD y Karina Gibert (IDEAI-UPC) |
| [**0005**](0005-tratamiento-incertidumbre-abstencion-hitl.md) | Tratamiento de la incertidumbre: abstención ($p < 0.80$) y pantalla operativa HitL («Asumo / No asumo») | **Aceptada** | 2026-10-16 | *Gender Shades*, Diap. 91 Vilaplana y Karina Gibert |
| [**0006**](0006-salvaguarda-algoritmica-paridad-no-binaria.md) | Salvaguarda algorítmica de paridad: minoración del techo masculino ante identidades no binarias | **Aceptada** | 2026-10-14 | Directriz inaugural Karina Gibert (Líneas 62–65) |
| [**0007**](0007-estrategia-dual-datasets-agora-quanta.md) | Estrategia dual de datasets: calibración en laboratorio (`Àgora`) vs. inferencia en producción (*«Quanta»*) | **Aceptada** | 2026-10-19 | Adrián Fonollosa (TALP-UPC) y ALTAI |
| [**0008**](0008-ingesta-agnostica-regimen-legal-fuentes.md) | Ingesta agnóstica parametrizable y régimen legal de fuentes (Garantía UPC y Compliance Profesional) | **Aceptada** | 2026-10-21 | Dra. Karina Gibert, Art. 67 RDL 24/2021 y Art. 50 RIA |
| [**0009**](0009-exclusion-emociones-ai-act-postergacion-sentiment.md) | Exclusión de inferencia biométrica de emociones (AI Act) y rescate desacoplado del Índice de Clima Conversacional | **Aceptada** | 2026-10-23 | Art. 5.1.f AI Act, Directrices C(2025) 884 y Adela Cortina |
| [**0010**](0010-soberania-linguistica-cooficial-accesibilidad-universal-aapp.md) | Soberanía lingüística cooficial (`es/ca/gl/eu/en`) y Accesibilidad Universal por Diseño (`WCAG 2.2 AA` / `UNE 153101 EX`) | **Aceptada** | 2026-10-25 | Art. 3 y 49 CE, Art. 157 LRJSP y Directiva UE 2019/882 |
| [**0011**](0011-adopcion-test-interlocucion-femenina-tif.md) | Adopción del Test de Interlocución Femenina (TIF) como Adaptación Pericial del Test de Bechdel-Wallace | **Aceptada** | 2026-10-27 | Alison Bechdel, GMMP 2020 y Debate Colegiado D-10 |
| [**0012**](0012-marco-normativo-omnibus-digital-y-proyecto-de-ley.md) | Marco normativo tras el Ómnibus Digital de IA y Proyecto de Ley Orgánica de gobernanza de la IA como norte no vinculante | **Propuesta** | 2026-10-28 | RIA, Reglamento (UE) 2026/1744 y BOCG A-97-1 |
