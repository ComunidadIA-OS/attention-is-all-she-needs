# Informe de Conformidad de Accesibilidad — Dashboard *Constelación del Protagonismo*

**Proyecto:** AIASN — Reto «Mujeres por la IA Abierta» · **Issue #18** (Accesibilidad Universal por Diseño)
**Componente:** Dashboard / frontend de resultados.
**Normas de referencia:** WCAG 2.2 AA · UNE 153101 EX (Lectura Fácil) · RD 1112/2018 · Directiva (UE) 2019/882 (EAA).
**Método de verificación:** auditoría automática **axe-core 4.10** en headless (tema claro y oscuro), cálculo de ratios de contraste WCAG y simulación de daltonismo (Machado 2009).

---

## Resultado global

| Comprobación | Resultado |
| :--- | :--- |
| axe-core (WCAG 2.0/2.1/2.2 · A y AA) — tema claro | **0 violaciones** |
| axe-core (WCAG 2.0/2.1/2.2 · A y AA) — tema oscuro | **0 violaciones** |
| Contraste de texto | **≥ 4,5:1 verificado** en todos los pares |
| Distinción por daltonismo (par mujer/hombre) | **Supera las 3 CVD** |

---

## 1. Uso del color — doble codificación (WCAG 1.4.1)

Ninguna información se transmite solo por color:

- **Constelación:** la mujer es un disco lleno; el hombre, un disco con **anillo**; el caso sin identificar, un **contorno discontinuo**. Cada estrella lleva además su nombre.
- **Clima comunicativo:** los tres registros se distinguen por **textura** (sólido / rayas ↗ / rayas ↘), no solo por color, replicada en la leyenda.
- **Alertas y métricas:** estado legible por icono + texto ("no activada", etiquetas explícitas).

### Verificación frente a daltonismo (ΔE76, Machado 2009 severidad 1.0)

| Par mujer/hombre | Normal | Deuteranopia | Protanopia | Tritanopia |
| :--- | :-: | :-: | :-: | :-: |
| Tema claro | 77 | 31 | 45 | 55 |
| Tema oscuro | 64 | 24 | 37 | 49 |

*(Umbral de confusión ≈ 10; todos los valores quedan muy por encima.)* No fue necesario alterar la paleta feminista: ya era distinguible.

---

## 2. Contraste (WCAG 1.4.3 / 1.4.11)

Tokens corregidos al mínimo necesario (solo luminosidad, mismo tono):

| Token | Antes | Ratio | Después | Ratio |
| :--- | :-- | :-: | :-- | :-: |
| `--faint` (claro) | `#938da8` | 2,87 | `#71698a` | 4,64 |
| `--crit` (claro) | `#db3b5c` | 3,96 | `#d1264a` | 4,64 |
| `--good` (claro) | `#1a8f66` | 3,67 | `#177c58` | 4,67 |
| `--warn` (claro) | `#b9800e` | 3,08 | `#91640b` | 4,71 |
| `--faint` (oscuro) | `#6f6890` | 3,82 | `#827ba2` | 4,66 |
| `--sky-faint` | `#726a9e` | 3,89 | `#7d75a5` | 4,68 |
| Clima «colaborativo» | `#2f8f9d` | 3,79 | `#2a7f8c` | 4,65 |
| Clima «disenso» | `#b25b92` | 4,37 | `#af558e` | 4,65 |

---

## 3. Lectura Fácil (UNE 153101 EX)

Resumen del veredicto en lenguaje claro: frases cortas, una idea por frase, vocabulario común y sin jerga ("RVP", "equality-washing" traducidos a lenguaje llano). Presentado como salida de `generar_resumen_lectura_facil()`.

---

## 4. Lectores de pantalla, estructura y teclado

- **Idioma** declarado (`lang="es"`) — WCAG 3.1.1.
- **Alternativa textual del canvas:** `role="img"` + descripción y **tabla de datos oculta** (`sr-only`) con cada persona, género, rol, % pantalla, % voz y protagonismo — WCAG 1.1.1.
- **Gráficos** (segregación, brecha, clima, índice): `role="img"` con descripción numérica; tabla del *ledger* con `caption` y `scope` — WCAG 1.1.1 / 1.3.1.
- **Iconos decorativos** ocultos (`aria-hidden`).
- **Landmarks** (`banner`, `main`, `contentinfo`) y jerarquía de encabezados — WCAG 1.3.1 / 2.4.1 (enlace «Saltar al contenido»).
- **Teclado:** cada estrella es un botón enfocable y operable; **foco visible** reforzado — WCAG 2.1.1 / 2.4.7.
- **Mensajes de estado:** la ficha de persona se anuncia (`aria-live="polite"`) — WCAG 4.1.3.
- Movimiento respetuoso con `prefers-reduced-motion`.

---

## 5. Declaración

El dashboard se ha diseñado y verificado conforme a **WCAG 2.2 nivel AA**, en línea con el RD 1112/2018 y la Directiva (UE) 2019/882. La auditoría automática no detecta violaciones; las comprobaciones manuales de contraste, color y estructura se recogen en este informe. Pendiente: validación con usuarios reales y con lector de pantalla (NVDA/VoiceOver) como siguiente capa.
