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
      ratio_voz_pantalla: { mujer: rvp("mujer"), hombre: rvp("hombre") }
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
   * Test de Bechdel Digital / Conversacional (spec 21 §1.5, `evaluar_bechdel_conversacional`).
   * Regla 1: ≥ 2 mujeres distintas con voz activa. Regla 2: ≥ 2 mujeres con rótulo OCR.
   * Regla 3: ≥ 1 transición directa de turno Mujer_A → Mujer_B (A ≠ B).
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
    let diagnostico;
    if (!personas.length) diagnostico = "sin_datos";
    else if (puntuacion === 3) diagnostico = "supera";
    else if (!r1) diagnostico = "efecto_token";
    else if (!r3) diagnostico = "aislamiento_relacional";
    else diagnostico = "parcial";
    return {
      mujeres_distintas_hablando: hablan.length,
      mujeres_con_rotulo_identificado: rotuladas.length,
      transiciones_mujer_a_mujer: transiciones,
      regla_1_pluralidad_femenina: r1,
      regla_2_identidad_propia: r2,
      regla_3_dialogo_horizontal: r3,
      puntuacion_bechdel_0_3: puntuacion,
      supera_bechdel_digital: puntuacion === 3,
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
    indiceGlobal: indiceGlobal,
    diagnosticoPrincipal: diagnosticoPrincipal,
    evaluar: evaluar
  };
});
