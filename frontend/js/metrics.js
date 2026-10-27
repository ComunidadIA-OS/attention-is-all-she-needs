// SPDX-FileCopyrightText: 2026 Equipo 1: Attention Is All She Needs (Alba Camiña García, Pilar de la Fuente Diez, Rocío Jiménez Villén)
// SPDX-License-Identifier: Apache-2.0

/**
 * AIASN — Lógica de referencia de métricas (réplica de docs/especificacion_alertas_dashboard_y_hitl.md,
 * SSoT «21») para el modo demostración y el recálculo tras arbitraje humano (HitL, ADR-0005).
 *
 * IMPORTANTE (ADR-0001): en producción el veredicto lo calcula el motor determinista en Python
 * (`aiasn/core/fusion.py`). Este módulo SOLO se usa cuando la API no entrega un campo
 * (p. ej. `alerta_infrarrepresentacion`, `indice_global`) o en la muestra local sin backend.
 * La interfaz etiqueta siempre el origen del cálculo («cliente» o «API»).
 *
 * Son funciones puras, sin DOM: se pueden probar con `node frontend/tests/run.mjs`.
 */
(function (root, factory) {
  if (typeof module === "object" && module.exports) {
    module.exports = factory();
  } else {
    root.AIASN_METRICS = factory();
  }
})(typeof self !== "undefined" ? self : this, function () {
  "use strict";

  /** Umbrales canónicos de la spec 21 (§3, §4, §5). */
  const THRESHOLDS = Object.freeze({
    MASA_CRITICA_PANTALLA: 35, // % — Kanter (1977), Directiva UE 2022/2381
    VOZ_TOKEN_MUDO: 20, // % — GMMP 2020 / Gender Gap Tracker
    RVP_FIGURACION: 0.3, // Cuadrante 2 de Vilaplana
    SUELO_PARIDAD: 40, // % — LO 2/2024
    RVP_EQUILIBRIO: 1.0,
    UMBRAL_ABSTENCION: 0.8 // p < 0,80 → no_determinado (ADR-0005)
  });

  /** Ponderaciones del Índice Global (spec 21 §4). */
  const WEIGHTS = Object.freeze({ pantalla: 0.3, voz: 0.2, espacio: 0.25, autoridad: 0.25 });

  const GENEROS = ["mujer", "hombre", "no_binario", "no_determinado"];

  function round(x, d) {
    const f = Math.pow(10, d);
    return Math.round(x * f) / f;
  }

  function normGenero(g) {
    const v = String(g || "").toLowerCase();
    return GENEROS.indexOf(v) >= 0 ? v : "no_determinado";
  }

  /**
   * Aplica las decisiones del arbitraje humano a las personas.
   * decisiones[persona_id] = { accion: "validar", genero } | { accion: "abstener" }
   * (La abstención mantiene `no_determinado`: se excluye del denominador, spec 21 §5.3.)
   */
  function personasEfectivas(personas, decisiones) {
    const dec = decisiones || {};
    return personas.map(function (p) {
      const d = dec[p.id];
      if (d && d.accion === "validar" && d.genero) {
        return Object.assign({}, p, { genero: normGenero(d.genero), validada_por_humano: true });
      }
      return Object.assign({}, p, { genero: normGenero(p.genero) });
    });
  }

  /** Segundos de voz y pantalla agregados por género. */
  function tiempos(personas) {
    const out = { voz: {}, pantalla: {} };
    GENEROS.forEach(function (g) {
      out.voz[g] = 0;
      out.pantalla[g] = 0;
    });
    personas.forEach(function (p) {
      const g = normGenero(p.genero);
      out.voz[g] += Number(p.voz_s) || 0;
      out.pantalla[g] += Number(p.pantalla_s) || 0;
    });
    return out;
  }

  /**
   * Porcentajes sobre el total DETERMINADO (excluye `no_determinado`, igual que el motor Python
   * y la spec 21 §5.3); `no_determinado_s` se devuelve aparte para mostrarlo con transparencia.
   */
  function porcentajes(t) {
    function pct(canal) {
      const det = t[canal].mujer + t[canal].hombre + t[canal].no_binario;
      const f = function (s) {
        return det > 0 ? (s / det) * 100 : 0;
      };
      return {
        mujer: f(t[canal].mujer),
        hombre: f(t[canal].hombre),
        no_binario: f(t[canal].no_binario),
        total_determinado_s: det,
        no_determinado_s: t[canal].no_determinado
      };
    }
    const voz = pct("voz");
    const pantalla = pct("pantalla");
    function rvp(g) {
      return pantalla[g] > 0 ? voz[g] / pantalla[g] : null;
    }
    return {
      voz_pct: voz,
      pantalla_pct: pantalla,
      ratio_voz_pantalla: { mujer: rvp("mujer"), hombre: rvp("hombre"), no_binario: rvp("no_binario") }
    };
  }

  /** Alertas deterministas de la spec 21 §3 (dos alertas independientes). */
  function alertas(m) {
    const P = m.pantalla_pct.mujer;
    const V = m.voz_pct.mujer;
    const R = m.ratio_voz_pantalla.mujer;
    const rvpBajo = R !== null && R < THRESHOLDS.RVP_FIGURACION;
    const washing = {
      activa: P >= THRESHOLDS.MASA_CRITICA_PANTALLA && (rvpBajo || V < THRESHOLDS.VOZ_TOKEN_MUDO),
      condiciones: {
        pantalla_ge_35: P >= THRESHOLDS.MASA_CRITICA_PANTALLA,
        rvp_lt_030: rvpBajo,
        voz_lt_20: V < THRESHOLDS.VOZ_TOKEN_MUDO
      }
    };
    const rvpMenor1 = R === null ? V < P : R < THRESHOLDS.RVP_EQUILIBRIO;
    const infra = {
      activa: P < THRESHOLDS.SUELO_PARIDAD && rvpMenor1,
      condiciones: {
        pantalla_lt_40: P < THRESHOLDS.SUELO_PARIDAD,
        rvp_lt_1: rvpMenor1
      }
    };
    return { equality_washing: washing, infrarrepresentacion: infra };
  }

  /** Salvaguarda de paridad no binaria en 3 fases (ADR-0006) — réplica de fusion.py. */
  function salvaguarda(tMujeres, tHombres, tNoBinario, mesaMonografica) {
    const sueloMin = 0.4;
    const techoBase = 0.6;
    const total = tMujeres + tHombres + tNoBinario;
    if (total <= 0) {
      return {
        cuota_femenina: 0,
        cuota_masculina: 0,
        cuota_no_binaria: 0,
        suelo_femenino_exigido: sueloMin,
        techo_masculino_ajustado: techoBase,
        regimen_aplicado: "SIN_DATOS_DETERMINADOS",
        cumple_salvaguarda_paridad: false
      };
    }
    const cm = tMujeres / total;
    const ch = tHombres / total;
    const cnb = tNoBinario / total;
    const margen = round(techoBase - sueloMin, 4);
    let suelo;
    let techo;
    let regimen;
    if (cnb <= margen) {
      suelo = sueloMin;
      techo = Math.max(0, techoBase - cnb);
      regimen = "FASE_1_ABSORCION_TECHO_MASCULINO";
    } else {
      const exceso = cnb - margen;
      suelo = Math.max(0, sueloMin - exceso / 2);
      techo = Math.max(0, sueloMin - exceso / 2);
      regimen = "FASE_2_REPARTO_SIMETRICO_50_50";
    }
    let cumpleSuelo;
    let cumpleTecho;
    if (mesaMonografica || cnb > 0.6) {
      regimen = "FASE_3_MESA_MONOGRAFICA_DIVERSIDAD_LGTBIQ";
      cumpleTecho = ch <= techo + 1e-6;
      cumpleSuelo = cm + cnb >= 1 - techo - 1e-6;
    } else {
      cumpleSuelo = cm >= suelo - 1e-6;
      cumpleTecho = ch <= techo + 1e-6;
    }
    return {
      cuota_femenina: round(cm, 4),
      cuota_masculina: round(ch, 4),
      cuota_no_binaria: round(cnb, 4),
      suelo_femenino_exigido: round(suelo, 4),
      techo_masculino_ajustado: round(techo, 4),
      regimen_aplicado: regimen,
      cumple_salvaguarda_paridad: Boolean(cumpleSuelo && cumpleTecho)
    };
  }

  /**
   * Condición previa del Test de Bechdel digital (decisión de equipo, 27/10/2026):
   * solo tiene sentido si en la pieza APARECEN O HABLAN al menos 2 mujeres y 1 hombre.
   * Con una sola mujer el resultado es trivial (efecto token, ya cubierto por las alertas);
   * sin hombres no puede haber mediación masculina. Se cuenta presencia (voz o pantalla),
   * no solo voz, para que el test detecte a la mujer presente que nunca toma la palabra.
   */
  function bechdelAplicabilidad(personas) {
    const presente = function (p) {
      return (Number(p.voz_s) || 0) > 0 || (Number(p.pantalla_s) || 0) > 0;
    };
    const mujeres = personas.filter(function (p) { return normGenero(p.genero) === "mujer" && presente(p); }).length;
    const hombres = personas.filter(function (p) { return normGenero(p.genero) === "hombre" && presente(p); }).length;
    let motivo = null;
    if (mujeres === 0) motivo = "no_aplica_sin_mujeres";
    else if (mujeres < 2) motivo = "no_aplica_una_mujer";
    else if (hombres < 1) motivo = "no_aplica_sin_hombres";
    return { aplica: motivo === null, motivo: motivo, mujeres_presentes: mujeres, hombres_presentes: hombres };
  }

  /**
   * Test de Bechdel Digital / Conversacional (spec 21 §1.5, `evaluar_bechdel_conversacional`).
   * Regla 1: ≥ 2 mujeres distintas con voz activa. Regla 2: ≥ 2 mujeres con rótulo OCR.
   * Regla 3: ≥ 1 transición directa de turno Mujer_A → Mujer_B (A ≠ B).
   * Si no se cumple la condición previa (`bechdelAplicabilidad`), `aplica = false` y no se puntúa.
   */
  function bechdel(personas, secuenciaTurnos) {
    const porId = {};
    personas.forEach(function (p) {
      porId[p.id] = p;
    });
    const hablan = personas.filter(function (p) {
      return p.genero === "mujer" && (Number(p.voz_s) || 0) > 0;
    });
    const rotuladas = personas.filter(function (p) {
      return p.genero === "mujer" && p.rotulo === true;
    });
    let transiciones = 0;
    const seq = secuenciaTurnos || [];
    for (let i = 0; i < seq.length - 1; i++) {
      const a = porId[seq[i]];
      const b = porId[seq[i + 1]];
      if (a && b && a.genero === "mujer" && b.genero === "mujer" && a.id !== b.id) transiciones++;
    }
    const r1 = hablan.length >= 2;
    const r2 = rotuladas.length >= 2;
    const r3 = transiciones >= 1;
    const puntuacion = Number(r1) + Number(r2) + Number(r3);
    const ap = bechdelAplicabilidad(personas);
    let diagnostico;
    if (!personas.length) diagnostico = "sin_datos";
    else if (!ap.aplica) diagnostico = ap.motivo;
    else if (puntuacion === 3) diagnostico = "supera";
    else if (!r1) diagnostico = "efecto_token";
    else if (!r3) diagnostico = "aislamiento_relacional";
    else diagnostico = "parcial";
    return {
      aplica: ap.aplica,
      mujeres_presentes: ap.mujeres_presentes,
      hombres_presentes: ap.hombres_presentes,
      mujeres_distintas_hablando: hablan.length,
      mujeres_con_rotulo_identificado: rotuladas.length,
      transiciones_mujer_a_mujer: transiciones,
      regla_1_pluralidad_femenina: r1,
      regla_2_identidad_propia: r2,
      regla_3_dialogo_horizontal: r3,
      puntuacion_bechdel_0_3: ap.aplica ? puntuacion : null,
      supera_bechdel_digital: ap.aplica && puntuacion === 3,
      diagnostico_bechdel: diagnostico
    };
  }

  function clamp100(x) {
    return Math.max(0, Math.min(100, x));
  }

  function mediaCentralidad(personas, genero) {
    const xs = personas.filter(function (p) {
      return p.genero === genero && (Number(p.pantalla_s) || 0) > 0 && typeof p.centralidad === "number";
    });
    if (!xs.length) return null;
    return (
      xs.reduce(function (a, p) {
        return a + p.centralidad;
      }, 0) / xs.length
    );
  }

  /**
   * Índice Global de Representación 0–100 (spec 21 §4).
   * S_autoridad: la spec no fija la fórmula; se usa una definición operativa PROVISIONAL
   * (media de: ratio de expertas acreditadas, cuota de citas como referente y apertura/cierre
   * por mujeres, todas normalizadas contra el suelo del 40 %). Marcada como tal en la interfaz.
   */
  function indiceGlobal(m, personas, extra) {
    const e = extra || {};
    const sPantalla = clamp100((m.pantalla_pct.mujer / THRESHOLDS.SUELO_PARIDAD) * 100);
    const sVoz = clamp100((m.voz_pct.mujer / THRESHOLDS.SUELO_PARIDAD) * 100);

    const cf = mediaCentralidad(personas, "mujer");
    const cm = mediaCentralidad(personas, "hombre");
    let sEspacio = 0;
    if (cf !== null && cm !== null && cf > 0 && cm > 0) sEspacio = Math.min(cf / cm, cm / cf) * 100;

    const componentes = [];
    const conAutoridad = personas.filter(function (p) {
      return p.autoridad === true;
    });
    if (conAutoridad.length) {
      const f = conAutoridad.filter(function (p) {
        return p.genero === "mujer";
      }).length;
      componentes.push(clamp100((f / conAutoridad.length / 0.4) * 100));
    }
    if (e.referentes) {
      const tot = (e.referentes.mujer || 0) + (e.referentes.hombre || 0);
      if (tot > 0) componentes.push(clamp100(((e.referentes.mujer || 0) / tot / 0.4) * 100));
    }
    const porId = {};
    personas.forEach(function (p) {
      porId[p.id] = p;
    });
    if (e.apertura_id || e.cierre_id) {
      let pts = 0;
      [e.apertura_id, e.cierre_id].forEach(function (id) {
        if (id && porId[id] && porId[id].genero === "mujer") pts += 50;
      });
      componentes.push(pts);
    }
    const sAutoridad = componentes.length
      ? componentes.reduce(function (a, b) {
          return a + b;
        }, 0) / componentes.length
      : 0;

    const total =
      WEIGHTS.pantalla * sPantalla + WEIGHTS.voz * sVoz + WEIGHTS.espacio * sEspacio + WEIGHTS.autoridad * sAutoridad;
    return {
      total: round(total, 1),
      dimensiones: {
        pantalla: { puntos: round(sPantalla, 1), peso: WEIGHTS.pantalla },
        voz: { puntos: round(sVoz, 1), peso: WEIGHTS.voz },
        espacio: { puntos: round(sEspacio, 1), peso: WEIGHTS.espacio },
        autoridad: { puntos: round(sAutoridad, 1), peso: WEIGHTS.autoridad, provisional: true }
      }
    };
  }

  /**
   * Aristas del grafo a partir de una muestra local: turnos (secuencia), planos compartidos,
   * menciones y temas tratados. Formato: { from, to, tipo, peso }.
   */
  function aristasDesdeCaso(caso) {
    const edges = [];
    const counts = {};
    const seq = caso.secuencia_turnos || [];
    for (let i = 0; i < seq.length - 1; i++) {
      if (seq[i] === seq[i + 1]) continue;
      const k = seq[i] + ">" + seq[i + 1];
      counts[k] = (counts[k] || 0) + 1;
    }
    Object.keys(counts).forEach(function (k) {
      const p = k.split(">");
      edges.push({ from: p[0], to: p[1], tipo: "turno", peso: counts[k] });
    });
    [["planos_compartidos", "comparte_plano"], ["menciones", "menciona"], ["habla_de", "habla_de"]].forEach(function (d) {
      (caso[d[0]] || []).forEach(function (e) {
        edges.push({ from: e[0], to: e[1], tipo: d[1], peso: e[2] });
      });
    });
    return edges;
  }

  /**
   * Lectura textual del grafo (alternativa interpretativa, no solo descriptiva):
   * quién articula la conversación, cuánto participan las mujeres en los cambios de turno,
   * a quién se cita y qué temas quedan segregados por género.
   */
  function interpretarGrafo(personas, edges) {
    const gen = {};
    personas.forEach(function (p) {
      gen[p.id] = normGenero(p.genero);
    });
    const w = function (e) {
      return Number(e.peso) || 1;
    };
    const turnos = edges.filter(function (e) {
      return e.tipo === "turno" && gen[e.from] && gen[e.to] && e.from !== e.to;
    });
    let total = 0;
    let conMujer = 0;
    let mujerMujer = 0;
    const implicacion = {};
    const transiciones = { mm: 0, hh: 0, mh: 0, hm: 0, con_nb: 0 };
    turnos.forEach(function (e) {
      const x = w(e);
      total += x;
      implicacion[e.from] = (implicacion[e.from] || 0) + x;
      implicacion[e.to] = (implicacion[e.to] || 0) + x;
      const gf = gen[e.from];
      const gt = gen[e.to];
      if (gf === "no_binario" || gt === "no_binario") transiciones.con_nb += x;
      else if (gf === "mujer" && gt === "mujer") transiciones.mm += x;
      else if (gf === "hombre" && gt === "hombre") transiciones.hh += x;
      else if (gf === "mujer" && gt === "hombre") transiciones.mh += x;
      else if (gf === "hombre" && gt === "mujer") transiciones.hm += x;
      const fm = gf === "mujer";
      const tm = gt === "mujer";
      if (fm || tm) conMujer += x;
      if (fm && tm) mujerMujer += x;
    });
    let eje = null;
    personas.forEach(function (p) {
      const n = implicacion[p.id] || 0;
      if (n > 0 && (!eje || n > eje.turnos)) eje = { id: p.id, turnos: n };
    });

    const menciones = { mujer: 0, hombre: 0, total: 0 };
    edges.forEach(function (e) {
      if (e.tipo !== "menciona" || !gen[e.to]) return;
      menciones.total += w(e);
      if (gen[e.to] === "mujer") menciones.mujer += w(e);
      if (gen[e.to] === "hombre") menciones.hombre += w(e);
    });

    const porTema = {};
    edges.forEach(function (e) {
      if (e.tipo !== "habla_de" || !gen[e.from]) return;
      (porTema[e.to] = porTema[e.to] || {})[gen[e.from]] = true;
    });
    const temas = { solo_mujeres: [], solo_hombres: [], compartidos: [] };
    Object.keys(porTema).forEach(function (id) {
      const g = porTema[id];
      if (g.mujer && g.hombre) temas.compartidos.push(id);
      else if (g.mujer) temas.solo_mujeres.push(id);
      else if (g.hombre) temas.solo_hombres.push(id);
    });

    const aislados = personas
      .filter(function (p) {
        return !implicacion[p.id];
      })
      .map(function (p) {
        return p.id;
      });

    return {
      total_turnos: total,
      eje: eje,
      turnos_con_mujer: conMujer,
      turnos_mujer_mujer: mujerMujer,
      transiciones: transiciones,
      menciones: menciones,
      temas: temas,
      aislados: aislados
    };
  }

  /* ─────────────── Revisión preventiva (material no publicado) — decisión D-11 ─────────────── */

  /**
   * Margen hasta el suelo de paridad (40 %) en un canal (voz o pantalla), sobre el total determinado.
   * Dos vías con implicaciones distintas para la producción:
   *  - añadir: segundos NUEVOS de mujeres necesarios (alarga la pieza): (0,4·T − F) / 0,6
   *  - redistribuir: segundos a TRASLADAR de hombres a mujeres sin alargar: 0,4·T − F
   */
  function margenParidad(t, canal) {
    const f = t[canal].mujer;
    const total = t[canal].mujer + t[canal].hombre + t[canal].no_binario;
    const suelo = THRESHOLDS.SUELO_PARIDAD / 100;
    if (total <= 0) return { cumple: false, anadir_s: null, redistribuir_s: null };
    const falta = suelo * total - f;
    if (falta <= 1e-9) return { cumple: true, anadir_s: 0, redistribuir_s: 0 };
    return {
      cumple: false,
      anadir_s: Math.ceil(falta / (1 - suelo)),
      redistribuir_s: Math.ceil(falta)
    };
  }

  /**
   * Escenario «¿y si…?»: aplica ajustes sobre una copia del caso, sin mutarlo.
   * ajustes = { personas: { id: { voz_s, pantalla_s, rotulo } }, nuevas: [persona], turno_mm: bool }
   */
  function simular(caso, ajustes) {
    const a = ajustes || {};
    const over = a.personas || {};
    const personas = caso.personas.map(function (p) {
      return Object.assign({}, p, over[p.id] || {});
    }).concat((a.nuevas || []).map(function (p) { return Object.assign({}, p); }));
    let seq = (caso.secuencia_turnos || []).slice();
    if (a.turno_mm) {
      const hablan = personas.filter(function (p) { return normGenero(p.genero) === "mujer" && (Number(p.voz_s) || 0) > 0; });
      if (hablan.length >= 2) seq = seq.concat([hablan[0].id, hablan[1].id]);
    }
    return Object.assign({}, caso, { personas: personas, secuencia_turnos: seq });
  }

  /**
   * Proyección desde una escaleta (preproducción, sin vídeo). Cada fila: { id, nombre, genero, minutos, rotulo }.
   * Supuestos explícitos: la voz es el tiempo previsto de intervención; la presencia en pantalla se iguala
   * a la voz (RVP = 1, sin planos de escucha) y el orden de la escaleta es el orden de turnos.
   */
  function escaletaACaso(escaleta) {
    const filas = (escaleta || []).filter(function (f) { return (Number(f.minutos) || 0) > 0; });
    const personas = filas.map(function (f) {
      const s = Math.round((Number(f.minutos) || 0) * 60);
      return {
        id: f.id,
        nombre: f.nombre || f.id,
        cargo: f.cargo || null,
        rotulo: Boolean(f.rotulo),
        genero: normGenero(f.genero),
        autoridad: Boolean(f.rotulo),
        voz_s: s,
        pantalla_s: s,
        centralidad: null
      };
    });
    return {
      video_id: "escaleta",
      personas: personas,
      secuencia_turnos: filas.map(function (f) { return f.id; }),
      segmentos_dudosos: [],
      temas: [],
      habla_de: [],
      planos_compartidos: [],
      menciones: [],
      proyeccion: true
    };
  }

  /**
   * Recomendaciones de producción, cada una ligada a la métrica que la dispara (trazabilidad).
   * Devuelve [{ id, prioridad: 1 (alta) | 2 | 3, clave, params }]; los textos se resuelven en la interfaz.
   */
  function recomendaciones(ev, edges, opciones) {
    const op = opciones || {};
    const out = [];
    const add = function (id, prioridad, clave, params) { out.push({ id: id, prioridad: prioridad, clave: clave, params: params || {} }); };
    const personas = ev.personas;
    const t = ev.tiempos_s;

    if (op.pendientes > 0) add("pendientes", 1, "rec.pendientes", { n: op.pendientes });

    const mv = margenParidad(t, "voz");
    if (!mv.cumple && mv.anadir_s !== null) add("voz", 1, "rec.voz", { add: mv.anadir_s, redist: mv.redistribuir_s });
    const mp = margenParidad(t, "pantalla");
    if (!mp.cumple && mp.anadir_s !== null) add("pantalla", 2, "rec.pantalla", { add: mp.anadir_s, redist: mp.redistribuir_s });

    if (ev.alertas.equality_washing.activa) {
      const mudas = personas.filter(function (p) {
        return p.genero === "mujer" && (Number(p.pantalla_s) || 0) > 0 && (Number(p.voz_s) || 0) / Math.max(1, Number(p.pantalla_s)) < THRESHOLDS.RVP_FIGURACION;
      }).map(function (p) { return p.id; });
      add("washing", 1, "rec.washing", { ids: mudas });
    }

    const b = ev.bechdel;
    if (b.diagnostico_bechdel === "no_aplica_una_mujer") add("una_mujer", 1, "rec.una_mujer");
    if (b.aplica) {
      if (!b.regla_1_pluralidad_femenina) {
        const calladas = personas.filter(function (p) { return p.genero === "mujer" && !(Number(p.voz_s) > 0); }).map(function (p) { return p.id; });
        add("bechdel_r1", 2, "rec.bechdel_r1", { ids: calladas });
      }
      if (!b.regla_3_dialogo_horizontal) add("bechdel_r3", 2, "rec.bechdel_r3");
    }
    personas.filter(function (p) {
      return p.genero === "mujer" && !p.rotulo && ((Number(p.voz_s) || 0) > 0 || (Number(p.pantalla_s) || 0) > 0);
    }).forEach(function (p) { add("rotulo:" + p.id, 2, "rec.rotulo", { ids: [p.id] }); });

    const g = interpretarGrafo(personas, edges || []);
    if (g.eje && g.total_turnos >= 4 && g.eje.turnos / g.total_turnos > 0.6) {
      add("eje", 3, "rec.eje", { ids: [g.eje.id], n: g.eje.turnos, total: g.total_turnos });
    }
    g.temas.solo_hombres.forEach(function (id) { add("tema_m:" + id, 3, "rec.tema_m", { tema: id }); });
    g.temas.solo_mujeres.forEach(function (id) { add("tema_f:" + id, 3, "rec.tema_f", { tema: id }); });

    out.sort(function (x, y) { return x.prioridad - y.prioridad; });
    if (!out.length) add("ok", 3, "rec.ok");
    return out;
  }

  /** Diagnóstico principal para el titular del veredicto. */
  function diagnosticoPrincipal(al, sal) {
    if (al.equality_washing.activa) return "washing";
    if (al.infrarrepresentacion.activa) return "infra";
    if (!sal.cumple_salvaguarda_paridad) return "salvaguarda";
    return "ok";
  }

  /** Evaluación completa a partir de personas (con decisiones HitL aplicadas) y datos de contexto. */
  function evaluar(caso, decisiones) {
    const personas = personasEfectivas(caso.personas, decisiones);
    const t = tiempos(personas);
    const m = porcentajes(t);
    const al = alertas(m);
    const sal = salvaguarda(t.voz.mujer, t.voz.hombre, t.voz.no_binario, Boolean(caso.mesa_monografica_diversidad));
    const bd = bechdel(personas, caso.secuencia_turnos);
    const idx = indiceGlobal(m, personas, {
      referentes: caso.referentes,
      apertura_id: caso.apertura_id,
      cierre_id: caso.cierre_id
    });
    return {
      personas: personas,
      tiempos_s: t,
      metricas: m,
      alertas: al,
      salvaguarda: sal,
      bechdel: bd,
      indice_global: idx,
      diagnostico: diagnosticoPrincipal(al, sal)
    };
  }

  return {
    THRESHOLDS: THRESHOLDS,
    WEIGHTS: WEIGHTS,
    personasEfectivas: personasEfectivas,
    tiempos: tiempos,
    porcentajes: porcentajes,
    alertas: alertas,
    salvaguarda: salvaguarda,
    bechdel: bechdel,
    bechdelAplicabilidad: bechdelAplicabilidad,
    indiceGlobal: indiceGlobal,
    diagnosticoPrincipal: diagnosticoPrincipal,
    aristasDesdeCaso: aristasDesdeCaso,
    interpretarGrafo: interpretarGrafo,
    margenParidad: margenParidad,
    simular: simular,
    escaletaACaso: escaletaACaso,
    recomendaciones: recomendaciones,
    evaluar: evaluar
  };
});

