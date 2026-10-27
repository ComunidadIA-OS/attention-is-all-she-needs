// SPDX-FileCopyrightText: 2026 Equipo 1: Attention Is All She Needs (Alba Camiña García, Pilar de la Fuente Diez, Rocío Jiménez Villén)
// SPDX-License-Identifier: Apache-2.0

/**
 * AIASN — Panel de auditoría audiovisual de paridad.
 * Renderiza el dictamen a partir de (a) muestras sintéticas locales o (b) la API en vivo (FastAPI).
 *
 * Principios (ADR-0001, 0004, 0005, 0009, 0010):
 *  - Los modelos extraen; el código determinista calcula. Este cliente solo calcula cuando no hay backend
 *    (muestras locales) o cuando la API aún no entrega un campo, y siempre rotula el origen del cálculo.
 *  - La interfaz nunca depende solo del color: icono + texto + forma.
 *  - Sin recursos externos en tiempo de ejecución.
 */
(function () {
  "use strict";

  const M = window.AIASN_METRICS;
  const I = window.AIASN_I18N;
  const DEMO = window.AIASN_DEMO;
  const t = I.t;
  const fmt = I.fmt;

  const POLL_INTERVAL_MS = 2000;
  const POLL_MAX_MS = 10 * 60 * 1000;
  const PIPELINE_STEPS = ["audio", "nlp", "video", "captions", "silver", "gold"];

  const state = {
    datasetKey: "A",
    live: null, // payload bruto de la API
    decisiones: {},
    log: [],
    closed: false,
    confirming: false,
    reopening: false,
    anonymized: false,
    view: null,
    network: null,
    votes: { yes: 0, partial: 0, no: 0 },
    voted: false,
    hashToken: 0,
    focusAfterRender: null,
    fase: "publicado", // preproduccion | edicion | publicado (D-11)
    escaleta: [],
    escSeq: 0,
    ajustes: { personas: {}, nuevas: [], turno_mm: false },
    simSeq: 0,
    previstaMin: null
  };

  const $ = function (id) {
    return document.getElementById(id);
  };

  /** Crea un elemento DOM con atributos y nodos hijos (sin innerHTML: el contenido nunca se interpreta como HTML). */
  function h(tag, attrs) {
    const node = document.createElement(tag);
    if (attrs) {
      Object.keys(attrs).forEach(function (k) {
        const v = attrs[k];
        if (v === null || v === undefined || v === false) return;
        if (k === "class") node.className = v;
        else if (k === "text") node.textContent = v;
        else if (k === "dataset") Object.keys(v).forEach(function (d) { node.dataset[d] = v[d]; });
        else node.setAttribute(k, v === true ? "" : v);
      });
    }
    for (let i = 2; i < arguments.length; i++) {
      const c = arguments[i];
      if (c === null || c === undefined || c === false) continue;
      node.appendChild(typeof c === "string" ? document.createTextNode(c) : c);
    }
    return node;
  }

  function icon(id, cls) {
    const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
    svg.setAttribute("class", "icon" + (cls ? " " + cls : ""));
    svg.setAttribute("aria-hidden", "true");
    const use = document.createElementNS("http://www.w3.org/2000/svg", "use");
    use.setAttribute("href", "#" + id);
    svg.appendChild(use);
    return svg;
  }

  function clear(node) {
    while (node.firstChild) node.removeChild(node.firstChild);
  }

  function announce(msg) {
    const sr = $("sr-status");
    if (!sr) return;
    sr.textContent = "";
    window.setTimeout(function () {
      sr.textContent = msg;
    }, 40);
  }

  function reducedMotion() {
    return Boolean(window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches);
  }

  function cssVar(name, fallback) {
    const v = getComputedStyle(document.documentElement).getPropertyValue(name).trim();
    return v || fallback;
  }

  function mmss(s) {
    const total = Math.max(0, Math.round(Number(s) || 0));
    const m = Math.floor(total / 60);
    const sec = total % 60;
    return String(m).padStart(2, "0") + ":" + String(sec).padStart(2, "0");
  }

  /* ───────────────────────── Modelo de vista ───────────────────────── */

  function buildDemoView() {
    return buildCaseView(DEMO[state.datasetKey]);
  }

  /** Vista a partir de un caso local (muestra sintética o proyección de escaleta). */
  function buildCaseView(caso) {
    const ev = M.evaluar(caso, state.decisiones);
    const nodes = ev.personas.map(function (p) {
      return { id: p.id, tipo: "participante", persona: p };
    });
    (caso.temas || []).forEach(function (tm) {
      nodes.push({ id: tm.id, tipo: "tema", label: tm.label });
    });
    return {
      origin: "client",
      video_id: caso.video_id,
      status: caso.status || { estado: "pending", pasos: {} },
      personas: ev.personas,
      metricas: ev.metricas,
      alertas: ev.alertas,
      salvaguarda: ev.salvaguarda,
      bechdel: ev.bechdel,
      indice: ev.indice_global,
      diagnostico: ev.diagnostico,
      nodes: nodes,
      edges: M.aristasDesdeCaso(caso),
      clima: normClima(caso.clima),
      segmentos: caso.segmentos_dudosos || [],
      canArbitrate: true,
      citizenApi: null,
      apiEasy: null,
      caso: caso,
      proyeccion: Boolean(caso.proyeccion)
    };
  }

  function normClima(c) {
    const out = {};
    ["mujer", "hombre"].forEach(function (g) {
      const src = (c && c[g]) || {};
      out[g] = {
        tecnico_asertivo: Number(src.tecnico_asertivo !== undefined ? src.tecnico_asertivo : src["técnico/asertivo"]) || 0,
        colaborativo: Number(src.colaborativo) || 0,
        disenso: Number(src.disenso) || 0
      };
    });
    return out;
  }

  function buildApiView(payload) {
    const r = payload.resultado || {};
    const v = r.veredicto || {};
    const mt = r.metricas || {};
    const personas = (r.personas || []).map(function (p) {
      return {
        id: p.id,
        nombre: p.nombre,
        cargo: p.cargo,
        rotulo: Boolean(p.cargo),
        genero: p.genero || "no_determinado",
        autoridad: Boolean(p.autoridad),
        pantalla_s: p.pantalla_s,
        voz_s: p.voz_s,
        centralidad: p.centralidad
      };
    });
    function chan(src) {
      const s = src || {};
      return { mujer: s.mujer || 0, hombre: s.hombre || 0, no_binario: s.no_binario || 0, no_determinado_pct: s.no_determinado || 0, no_determinado_s: 0 };
    }
    const metricas = {
      voz_pct: chan(mt.voz_pct),
      pantalla_pct: chan(mt.pantalla_pct),
      ratio_voz_pantalla: { mujer: (mt.ratio_voz_pantalla || {}).mujer, hombre: (mt.ratio_voz_pantalla || {}).hombre }
    };
    const calc = M.alertas(metricas);
    const alertas = {
      equality_washing: {
        activa: typeof v.alerta_equality_washing === "boolean" ? v.alerta_equality_washing : calc.equality_washing.activa,
        condiciones: calc.equality_washing.condiciones
      },
      infrarrepresentacion: v.alerta_infrarrepresentacion
        ? { activa: Boolean(v.alerta_infrarrepresentacion.activa !== undefined ? v.alerta_infrarrepresentacion.activa : v.alerta_infrarrepresentacion), condiciones: calc.infrarrepresentacion.condiciones }
        : calc.infrarrepresentacion
    };
    const sp = v.salvaguarda_paridad || {};
    const salvaguarda = {
      cuota_femenina: sp.cuota_femenina,
      cuota_masculina: sp.cuota_masculina,
      cuota_no_binaria: sp.cuota_no_binaria,
      suelo_femenino_exigido: sp.suelo_femenino_exigido,
      techo_masculino_ajustado: sp.techo_masculino_ajustado,
      regimen_aplicado: sp.regimen_aplicado,
      cumple_salvaguarda_paridad: sp.cumple_salvaguarda_paridad !== undefined ? Boolean(sp.cumple_salvaguarda_paridad) : Boolean(sp.cumple)
    };
    const bd = v.test_bechdel_digital || v.bechdel || {};
    const apl = typeof bd.aplica === "boolean" ? { aplica: bd.aplica, motivo: bd.motivo_no_aplica || null } : M.bechdelAplicabilidad(personas);
    const bechdel = {
      aplica: apl.aplica,
      puntuacion_bechdel_0_3: Number(bd.puntuacion_bechdel_0_3 !== undefined ? bd.puntuacion_bechdel_0_3 : bd.puntuacion_0_3) || 0,
      regla_1_pluralidad_femenina: bd.regla_1_pluralidad_femenina,
      regla_2_identidad_propia: bd.regla_2_identidad_propia,
      regla_3_dialogo_horizontal: bd.regla_3_dialogo_horizontal,
      mujeres_distintas_hablando: bd.mujeres_distintas_hablando,
      mujeres_con_rotulo_identificado: bd.mujeres_con_rotulo_identificado,
      transiciones_mujer_a_mujer: bd.transiciones_mujer_a_mujer,
      diagnostico_bechdel: apl.aplica ? null : apl.motivo,
      diagnostico_texto: bd.diagnostico_bechdel || bd.diagnostico || ""
    };
    let indice = null;
    const ig = v.indice_global;
    if (ig && typeof ig === "object" && ig.dimensiones) indice = ig;
    else if (typeof ig === "number") indice = { total: ig, dimensiones: null };
    let originFlag = "api";
    if (!indice) {
      indice = M.indiceGlobal(
        { pantalla_pct: metricas.pantalla_pct, voz_pct: metricas.voz_pct, ratio_voz_pantalla: metricas.ratio_voz_pantalla },
        personas,
        { referentes: mt.referentes }
      );
      originFlag = "mixed";
    }
    if (!v.alerta_infrarrepresentacion) originFlag = "mixed";

    const con = r.constelacion || { nodos: [], aristas: [] };
    const byId = {};
    personas.forEach(function (p) {
      byId[p.id] = p;
    });
    const nodes = (con.nodos || []).map(function (n) {
      if (n.tipo === "tema") return { id: n.id, tipo: "tema", label: n.label };
      const p = byId[n.id] || { id: n.id, nombre: n.label, cargo: n.cargo, genero: n.genero || "no_determinado", voz_s: n.size || 0, pantalla_s: 0 };
      return { id: n.id, tipo: "participante", persona: p };
    });
    const edges = (con.aristas || []).map(function (e) {
      return { from: e.source, to: e.target, tipo: e.tipo, peso: e.peso };
    });

    const vc = v.valoracion_ciudadana;
    let citizenApi = null;
    if (vc && typeof vc === "object") {
      citizenApi = { yes: vc.yes !== undefined ? vc.yes : vc.si || 0, partial: vc.partial !== undefined ? vc.partial : vc.parcial || 0, no: vc.no || 0 };
    }

    return {
      origin: originFlag,
      video_id: payload.video_id,
      status: payload.status || { estado: "ok", pasos: {} },
      personas: personas,
      metricas: metricas,
      alertas: alertas,
      salvaguarda: salvaguarda,
      bechdel: bechdel,
      indice: indice,
      diagnostico: M.diagnosticoPrincipal(alertas, salvaguarda),
      nodes: nodes,
      edges: edges,
      clima: normClima(r.clima),
      segmentos: r.segmentos_dudosos || [],
      canArbitrate: false,
      citizenApi: citizenApi,
      apiEasy: v.resumen_lectura_facil || null
    };
  }

  function currentView() {
    if (state.fase === "preproduccion") return buildCaseView(M.escaletaACaso(state.escaleta));
    if (state.datasetKey === "live") return state.live ? buildApiView(state.live) : null;
    return buildDemoView();
  }

  /* ───────────────────────── Utilidades de presentación ───────────────────────── */

  function displayName(p) {
    if (state.anonymized) return t("anon.name", { id: p.id });
    return p.nombre || t("people.no_label");
  }

  function genderLabel(g, short) {
    return t("gender." + (g || "no_determinado") + (short ? "_s" : ""));
  }

  function symFor(g) {
    const ns = "http://www.w3.org/2000/svg";
    const svg = document.createElementNS(ns, "svg");
    svg.setAttribute("viewBox", "0 0 16 16");
    svg.setAttribute("class", "sym sym-" + (g === "mujer" ? "f" : g === "hombre" ? "m" : "n"));
    svg.setAttribute("aria-hidden", "true");
    let shape;
    if (g === "mujer") {
      shape = document.createElementNS(ns, "circle");
      shape.setAttribute("cx", "8");
      shape.setAttribute("cy", "8");
      shape.setAttribute("r", "6");
    } else if (g === "hombre") {
      shape = document.createElementNS(ns, "rect");
      shape.setAttribute("x", "2");
      shape.setAttribute("y", "2");
      shape.setAttribute("width", "12");
      shape.setAttribute("height", "12");
    } else {
      shape = document.createElementNS(ns, "path");
      shape.setAttribute("d", "M8 2 14 14H2Z");
    }
    svg.appendChild(shape);
    return svg;
  }

  function setPill(el, kind, label, iconId) {
    el.className = "pill pill-" + kind;
    clear(el);
    if (iconId) el.appendChild(icon(iconId));
    el.appendChild(document.createTextNode(label));
  }

  /** Lista de comprobaciones con icono + texto (nunca solo color). tone: "neutral" | "good". */
  function renderChecks(ul, items, tone) {
    clear(ul);
    items.forEach(function (it) {
      const met = Boolean(it.ok);
      const cls = "check " + (tone === "good" ? (met ? "check-good" : "check-bad") : met ? "check-on" : "check-off");
      ul.appendChild(
        h(
          "li",
          { class: cls },
          icon(met ? "i-ok" : "i-no"),
          h("span", { class: "check-body" }, h("span", { class: "check-label", text: it.label }), it.detail ? " " : null, it.detail ? h("span", { class: "check-detail", text: it.detail }) : null),
          h("span", { class: "sr-only", text: " — " + (met ? t("check.met") : t("check.unmet")) })
        )
      );
    });
  }

  /* ───────────────────────── Render por secciones ───────────────────────── */

  function easyLines(view) {
    const lang = I.getLang();
    if (view.apiEasy && lang === "es") {
      let txt = view.apiEasy;
      if (state.anonymized) {
        view.personas.forEach(function (p) {
          if (p.nombre) txt = txt.split(p.nombre).join(t("anon.name", { id: p.id }));
        });
      }
      return txt.split(/(?<=[.!?])\s+/).filter(Boolean);
    }
    const lines = [];
    lines.push(t("easy.voice", { v: fmt(view.metricas.voz_pct.mujer, 0) }));
    lines.push(t("easy.screen", { p: fmt(view.metricas.pantalla_pct.mujer, 0) }));
    lines.push(t("easy.result." + (view.diagnostico === "salvaguarda" ? "salvaguarda" : view.diagnostico)));
    if (view.bechdel.aplica === false) {
      if (view.bechdel.diagnostico_bechdel === "no_aplica_una_mujer") lines.push(t("easy.bechdel.na_una"));
    } else {
      lines.push(t(view.bechdel.puntuacion_bechdel_0_3 === 3 ? "easy.bechdel.ok" : "easy.bechdel.no"));
    }
    const pend = pendingCount(view);
    if (pend > 0) lines.push(t("easy.pending", { n: pend }));
    return lines;
  }

  function pendingCount(view) {
    return view.segmentos.filter(function (s) {
      return !state.decisiones[s.persona_id];
    }).length;
  }

  function renderVerdict(view) {
    const hero = $("veredicto");
    hero.dataset.state = view.diagnostico === "ok" ? "ok" : "alert";
    $("verdict-eyebrow").textContent = t(state.fase === "preproduccion" ? "verdict.eyebrow_projection" : state.fase === "edicion" ? "verdict.eyebrow_draft" : "verdict.eyebrow");
    const title = $("veredicto-h");
    clear(title);
    title.appendChild(icon(view.diagnostico === "ok" ? "i-ok" : "i-warn", "icon-lg"));
    title.appendChild(document.createTextNode(t("verdict.title." + view.diagnostico)));

    const p = fmt(view.metricas.pantalla_pct.mujer, 1);
    const v = fmt(view.metricas.voz_pct.mujer, 1);
    let sub = t("verdict.sub." + view.diagnostico, { p: p, v: v });
    const pend = pendingCount(view);
    if (pend > 0) sub += " " + t("verdict.pending", { n: pend });
    $("hero-sub").textContent = sub;

    const list = $("easy-read-list");
    clear(list);
    easyLines(view).forEach(function (l) {
      list.appendChild(h("li", { text: l }));
    });

    $("index-total").textContent = fmt(view.indice.total, 0);
    const dims = $("index-dims");
    clear(dims);
    if (view.indice.dimensiones) {
      ["pantalla", "voz", "espacio", "autoridad"].forEach(function (k) {
        const d = view.indice.dimensiones[k];
        if (!d) return;
        const label = t("index.dim." + k);
        const bar = h("div", {
          class: "bar",
          role: "progressbar",
          "aria-valuemin": "0",
          "aria-valuemax": "100",
          "aria-valuenow": String(Math.round(d.puntos)),
          "aria-valuetext": t("index.points", { n: fmt(d.puntos, 0) }),
          "aria-label": label
        }, h("span", { class: "bar-fill", style: "width:" + Math.max(0, Math.min(100, d.puntos)) + "%" }));
        dims.appendChild(
          h("li", null,
            h("div", { class: "dim-head" }, h("span", { text: label }), h("span", { class: "dim-val", text: fmt(d.puntos, 0) })),
            bar,
            h("span", { class: "dim-weight", text: t("index.weight", { w: fmt(d.peso * 100, 0) }) })
          )
        );
      });
    }
  }

  function renderAlerts(view) {
    const m = view.metricas;
    const P = m.pantalla_pct.mujer;
    const V = m.voz_pct.mujer;
    const R = m.ratio_voz_pantalla.mujer;
    const rvpTxt = R === null || R === undefined ? t("metrics.rvp_na") : fmt(R, 2);
    const w = view.alertas.equality_washing;
    const i = view.alertas.infrarrepresentacion;
    const wc = w.condiciones;
    const ic = i.condiciones;

    $("alert-washing").dataset.state = w.activa ? "alert" : "ok";
    setPill($("washing-pill"), w.activa ? "alert" : "ok", w.activa ? t("state.active") : t("state.inactive"), w.activa ? "i-warn" : "i-ok");
    renderChecks($("washing-checks"), [
      { ok: wc.pantalla_ge_35, label: t("cond.pantalla_ge_35"), detail: t("cond.actual", { v: fmt(P, 1) + " %" }) },
      { ok: wc.rvp_lt_030, label: t("cond.rvp_lt_030"), detail: t("cond.actual", { v: rvpTxt }) },
      { ok: wc.voz_lt_20, label: t("cond.voz_lt_20"), detail: t("cond.actual", { v: fmt(V, 1) + " %" }) }
    ], "neutral");
    $("washing-text").textContent = t(w.activa ? "washing.text.on" : "washing.text.off");

    $("alert-infra").dataset.state = i.activa ? "alert" : "ok";
    setPill($("infra-pill"), i.activa ? "alert" : "ok", i.activa ? t("state.active") : t("state.inactive"), i.activa ? "i-warn" : "i-ok");
    renderChecks($("infra-checks"), [
      { ok: ic.pantalla_lt_40, label: t("cond.pantalla_lt_40"), detail: t("cond.actual", { v: fmt(P, 1) + " %" }) },
      { ok: ic.rvp_lt_1, label: t("cond.rvp_lt_1"), detail: t("cond.actual", { v: rvpTxt }) }
    ], "neutral");
    $("infra-text").textContent = t(i.activa ? "infra.text.on" : "infra.text.off");

    const s = view.salvaguarda;
    const cumple = s.cumple_salvaguarda_paridad;
    $("alert-salv").dataset.state = cumple ? "ok" : "alert";
    setPill($("salv-pill"), cumple ? "ok" : "alert", cumple ? t("state.cumple") : t("state.no_cumple"), cumple ? "i-ok" : "i-warn");
    const items = [];
    if (typeof s.cuota_femenina === "number" && typeof s.suelo_femenino_exigido === "number") {
      items.push({
        ok: s.cuota_femenina >= s.suelo_femenino_exigido - 1e-6,
        label: t("salv.suelo", { v: fmt(s.cuota_femenina * 100, 1), s: fmt(s.suelo_femenino_exigido * 100, 1) })
      });
    }
    if (typeof s.cuota_masculina === "number" && typeof s.techo_masculino_ajustado === "number") {
      items.push({
        ok: s.cuota_masculina <= s.techo_masculino_ajustado + 1e-6,
        label: t("salv.techo", { v: fmt(s.cuota_masculina * 100, 1), t: fmt(s.techo_masculino_ajustado * 100, 1) })
      });
    }
    renderChecks($("salv-checks"), items, "good");
    const regimen = s.regimen_aplicado ? t("salv.regimen", { r: t("regimen." + s.regimen_aplicado) }) : "";
    $("salv-text").textContent = (t(cumple ? "salv.text.on" : "salv.text.off") + " " + regimen).trim();
  }

  function renderStack(prefix, canal, label) {
    const c = canal;
    const f = c.mujer || 0;
    const mm = c.hombre || 0;
    const b = c.no_binario || 0;
    const stack = $(prefix + "-stack");
    clear(stack);
    [["f", f], ["m", mm], ["b", b]].forEach(function (x) {
      if (x[1] > 0) stack.appendChild(h("span", { class: "seg seg-" + x[0], style: "width:" + x[1] + "%" }));
    });
    const ndS = c.no_determinado_s || 0;
    stack.setAttribute("aria-label", t("metrics.stack_label", { c: label, f: fmt(f, 1), m: fmt(mm, 1), b: fmt(b, 1), n: fmt(ndS, 0) }));

    const legend = $(prefix + "-legend");
    clear(legend);
    [["mujer", "f", f], ["hombre", "m", mm]].concat(b > 0 ? [["no_binario", "b", b]] : []).forEach(function (x) {
      legend.appendChild(
        h("li", null,
          h("span", { class: "swatch swatch-" + x[1], "aria-hidden": "true" }),
          h("span", { class: "legend-name", text: genderLabel(x[0]) }),
          h("strong", { class: "legend-val", text: fmt(x[2], 1) + " %" })
        )
      );
    });
    let nd = t("metrics.nd_none");
    if (ndS > 0) nd = t("metrics.nd_note", { s: fmt(ndS, 0) });
    else if (c.no_determinado_pct > 0) nd = genderLabel("no_determinado") + ": " + fmt(c.no_determinado_pct, 1) + " %";
    $(prefix + "-nd").textContent = nd;
  }

  function renderMetrics(view) {
    renderStack("voz", view.metricas.voz_pct, t("metrics.voice"));
    renderStack("pantalla", view.metricas.pantalla_pct, t("metrics.screen"));
    const r = view.metricas.ratio_voz_pantalla;
    $("rvp-f").textContent = r.mujer === null || r.mujer === undefined ? t("metrics.rvp_na") : fmt(r.mujer, 2);
    $("rvp-m").textContent = r.hombre === null || r.hombre === undefined ? t("metrics.rvp_na") : fmt(r.hombre, 2);
    const boxNb = $("rvp-b-box");
    if (boxNb) {
      const hasNb = (view.metricas.pantalla_pct && view.metricas.pantalla_pct.no_binario > 0) || (view.metricas.voz_pct && view.metricas.voz_pct.no_binario > 0);
      boxNb.hidden = !hasNb;
      if (hasNb) {
        $("rvp-b").textContent = r.no_binario === null || r.no_binario === undefined ? t("metrics.rvp_na") : fmt(r.no_binario, 2);
      }
    }
    $("rvp-text").textContent = t("metrics.rvp_text");

    const b = view.bechdel;
    const aplica = b.aplica !== false;
    $("m-bechdel").dataset.state = aplica ? "" : "na";
    $("bechdel-score").textContent = aplica ? String(b.puntuacion_bechdel_0_3) : "";
    document.querySelector("#m-bechdel .score").hidden = !aplica;
    const rules = [];
    if (aplica && typeof b.regla_1_pluralidad_femenina === "boolean") {
      rules.push({ ok: b.regla_1_pluralidad_femenina, label: t("bechdel.r1"), detail: t("bechdel.count", { n: b.mujeres_distintas_hablando }) });
      rules.push({ ok: b.regla_2_identidad_propia, label: t("bechdel.r2"), detail: t("bechdel.count", { n: b.mujeres_con_rotulo_identificado }) });
      rules.push({ ok: b.regla_3_dialogo_horizontal, label: t("bechdel.r3"), detail: t("bechdel.count", { n: b.transiciones_mujer_a_mujer }) });
    }
    renderChecks($("bechdel-rules"), rules, "good");
    $("bechdel-rules").hidden = !rules.length;
    $("bechdel-diag").textContent = b.diagnostico_bechdel ? t("bechdel.diag." + b.diagnostico_bechdel) : b.diagnostico_texto;
  }

  /* ── Constelación ── */

  function nodeLabel(n) {
    return n.tipo === "tema" ? n.label : displayName(n.persona);
  }

  function renderGraph(view) {
    const container = $("constellation-network");
    if (!container || !window.vis) return;

    const colors = {
      f: cssVar("--c-woman", "#6b21a8"),
      m: cssVar("--c-man", "#0369a1"),
      b: cssVar("--c-topic", "#b45309"),
      n: cssVar("--c-nd", "#64748b"),
      t: "#d97706",
      text: cssVar("--text", "#0f172a"),
      surface: cssVar("--surface", "#ffffff"),
      edge: cssVar("--edge", "#94a3b8"),
      edgeTopic: cssVar("--edge-topic", "#d97706")
    };

    const nodes = view.nodes.map(function (n) {
      let shape = "hexagon";
      let color = colors.t;
      let size = 18;
      if (n.tipo === "participante") {
        const g = n.persona.genero;
        shape = g === "mujer" ? "dot" : g === "hombre" ? "square" : g === "no_binario" ? "diamond" : "triangle";
        color = g === "mujer" ? colors.f : g === "hombre" ? colors.m : g === "no_binario" ? colors.b : colors.n;
        const weight = (Number(n.persona.voz_s) || 0) + (Number(n.persona.pantalla_s) || 0) * 0.5;
        size = Math.max(14, Math.min(34, 10 + Math.sqrt(weight) * 1.2));
      }
      return {
        id: n.id,
        label: nodeLabel(n),
        shape: shape,
        size: size,
        color: { background: color, border: colors.surface, highlight: { background: color, border: colors.text } },
        font: { face: "system-ui, sans-serif", size: 14, color: colors.text, strokeWidth: 3, strokeColor: colors.surface }
      };
    });

    const edges = view.edges.map(function (e) {
      const topic = e.tipo === "habla_de";
      return {
        from: e.from,
        to: e.to,
        width: Math.min(5, Math.max(1, Math.sqrt(Number(e.peso) || 1))),
        dashes: e.tipo === "comparte_plano" ? [6, 6] : e.tipo === "menciona" ? [2, 4] : false,
        arrows: e.tipo === "turno" || e.tipo === "menciona" ? "to" : "",
        color: { color: topic ? colors.edgeTopic : colors.edge, highlight: colors.text },
        title: t("graph.type." + e.tipo)
      };
    });

    const rm = reducedMotion();
    const options = {
      physics: {
        solver: "barnesHut",
        stabilization: { iterations: 250 },
        barnesHut: { gravitationalConstant: -7000, centralGravity: 0.4, springLength: 150, springConstant: 0.05, damping: 0.5, avoidOverlap: 0.8 }
      },
      interaction: { hover: true, zoomView: false, dragView: true, dragNodes: true, keyboard: false },
      layout: { improvedLayout: true }
    };

    if (state.network) state.network.destroy();
    state.network = new vis.Network(container, { nodes: nodes, edges: edges }, options);
    // Si el navegador descarta el lienzo (GPU / fuera de pantalla), se repinta en cuanto se restaura.
    const canvas = container.querySelector("canvas");
    if (canvas) canvas.addEventListener("contextrestored", redrawGraph);
    state.network.once("stabilizationIterationsDone", function () {
      // Una vez estabilizado se detiene la física: menos CPU y sin movimiento continuo (Green AI, a11y).
      state.network.setOptions({ physics: false });
      state.network.fit({ animation: rm ? false : { duration: 250 } });
    });

    const byId = {};
    view.nodes.forEach(function (n) {
      byId[n.id] = n;
    });
    state.network.on("selectNode", function (params) {
      const n = byId[params.nodes[0]];
      if (!n) return;
      $("graph-selected").textContent =
        n.tipo === "tema"
          ? t("graph.selected_topic", { name: n.label })
          : t("graph.selected_person", { name: displayName(n.persona), voz: fmt(n.persona.voz_s || 0, 0), pantalla: fmt(n.persona.pantalla_s || 0, 0) });
    });
    state.network.on("deselectNode", function () {
      $("graph-selected").textContent = "";
    });

    // Alternativa accesible: descripción y tabla de relaciones
    const nPart = view.nodes.filter(function (n) { return n.tipo === "participante"; }).length;
    const nTem = view.nodes.length - nPart;
    $("graph-desc").textContent = t("graph.desc", { n: nPart, t: nTem });
    container.setAttribute("aria-label", t("graph.title") + ". " + t("graph.desc", { n: nPart, t: nTem }));

    const tbody = $("graph-table-body");
    clear(tbody);
    view.edges.forEach(function (e) {
      const a = byId[e.from];
      const b = byId[e.to];
      if (!a || !b) return;
      tbody.appendChild(
        h("tr", null, h("td", { text: nodeLabel(a) }), h("td", { text: nodeLabel(b) }), h("td", { text: t("graph.type." + e.tipo) }), h("td", { class: "num", text: fmt(e.peso, 0) }))
      );
    });

    renderGraphReading(view, byId);
  }

  function listText(items) {
    try {
      return new Intl.ListFormat(I.getLang(), { style: "long", type: "conjunction" }).format(items);
    } catch (e) {
      return items.join(", ");
    }
  }

  /** Lectura textual del grafo: lo que el dibujo sugiere, dicho con cifras. */
  function renderGraphReading(view, byId) {
    const r = M.interpretarGrafo(view.personas, view.edges);
    const name = function (id) { return byId[id] ? nodeLabel(byId[id]) : id; };
    const lines = [];
    if (!r.total_turnos) {
      lines.push(t("graph.r.no_turns"));
    } else {
      if (r.eje) lines.push(t("graph.r.hub", { name: name(r.eje.id), n: r.eje.turnos, total: r.total_turnos }));
      lines.push(t(r.turnos_mujer_mujer > 0 ? "graph.r.women_turns" : "graph.r.women_turns_no_mm", { n: r.turnos_con_mujer, total: r.total_turnos, mm: r.turnos_mujer_mujer }));
    }
    if (r.menciones.total > 0) lines.push(t("graph.r.mentions", { f: r.menciones.mujer, m: r.menciones.hombre }));
    const tm = r.temas;
    if (tm.solo_mujeres.length) lines.push(t("graph.r.topics_f", { list: listText(tm.solo_mujeres.map(name)) }));
    if (tm.solo_hombres.length) lines.push(t("graph.r.topics_m", { list: listText(tm.solo_hombres.map(name)) }));
    if (tm.compartidos.length) {
      lines.push(t(tm.solo_mujeres.length || tm.solo_hombres.length ? "graph.r.topics_shared" : "graph.r.topics_all_shared", { list: listText(tm.compartidos.map(name)) }));
    }
    if (r.aislados.length) lines.push(t("graph.r.isolated", { list: listText(r.aislados.map(name)) }));

    const ul = $("graph-reading");
    clear(ul);
    lines.forEach(function (l) { ul.appendChild(h("li", { text: l })); });

    const flowBox = $("graph-turn-flow");
    const flowPills = $("turn-flow-pills");
    if (flowBox && flowPills) {
      clear(flowPills);
      const tr = r.transiciones;
      if (r.total_turnos > 0 && tr) {
        flowBox.hidden = false;
        const pctT = function (val) { return Math.round((val / r.total_turnos) * 100); };
        const pillsData = [
          { label: "H → H", val: tr.hh, cls: "sym-m" },
          { label: "M → M", val: tr.mm, cls: "sym-f" },
          { label: "H → M", val: tr.hm, cls: "sym-m" },
          { label: "M → H", val: tr.mh, cls: "sym-f" }
        ];
        if (tr.con_nb > 0) {
          pillsData.push({ label: "↔ Non binario", val: tr.con_nb, cls: "sym-b" });
        }
        pillsData.forEach(function (p) {
          const pill = h("div", { class: "turn-flow-pill" },
            h("span", { class: "sym " + p.cls, "aria-hidden": "true" }),
            h("span", { text: p.label + ":" }),
            h("strong", { text: p.val + " (" + pctT(p.val) + " %)" })
          );
          flowPills.appendChild(pill);
        });
      } else {
        flowBox.hidden = true;
      }
    }
  }

  /**
   * Repintado del grafo. Con la física detenida, vis-network solo redibuja ante una interacción;
   * si el navegador ha descartado el contenido del canvas al salir de pantalla (Chromium lo hace con
   * aceleración por GPU), el grafo aparecería vacío hasta pulsar dentro. Se repinta al volver a verse.
   */
  let graphVisible = false;
  let redrawQueued = false;
  function redrawGraph() {
    if (redrawQueued) return;
    redrawQueued = true;
    window.requestAnimationFrame(function () {
      redrawQueued = false;
      if (state.network) state.network.redraw();
    });
  }

  function setupGraphControls() {
    const container = $("constellation-network");
    if ("IntersectionObserver" in window) {
      new IntersectionObserver(function (entries) {
        graphVisible = entries.some(function (e) { return e.isIntersecting; });
        if (graphVisible) redrawGraph();
      }, { threshold: 0 }).observe(container);
    } else {
      graphVisible = true;
    }
    if ("ResizeObserver" in window) new ResizeObserver(redrawGraph).observe(container);
    window.addEventListener("scroll", function () { if (graphVisible) redrawGraph(); }, { passive: true });
    window.addEventListener("hashchange", redrawGraph);
    document.addEventListener("visibilitychange", function () { if (!document.hidden) redrawGraph(); });
    window.addEventListener("pageshow", redrawGraph);
    function zoom(factor) {
      if (!state.network) return;
      state.network.moveTo({ scale: state.network.getScale() * factor, animation: reducedMotion() ? false : { duration: 180 } });
    }
    $("graph-zoom-in").addEventListener("click", function () { zoom(1.3); });
    $("graph-zoom-out").addEventListener("click", function () { zoom(0.77); });
    $("graph-zoom-fit").addEventListener("click", function () {
      if (state.network) state.network.fit({ animation: reducedMotion() ? false : { duration: 250 } });
    });
    // Ctrl + rueda: zoom intencionado. Sin Ctrl, la rueda hace scroll normal de la página.
    container.addEventListener("wheel", function (e) {
      if (!e.ctrlKey) return;
      e.preventDefault();
      zoom(e.deltaY < 0 ? 1.15 : 0.87);
    }, { passive: false });
  }

  /* ── Personas ── */

  function renderPeople(view) {
    const tbody = $("persons-table-body");
    clear(tbody);
    view.personas.forEach(function (p) {
      const g = p.genero || "no_determinado";
      const role = state.anonymized ? t("people.role_hidden") : p.cargo || "—";
      const nameCell = h("td", { class: "strong" }, displayName(p));
      if (p.validada_por_humano) nameCell.appendChild(h("span", { class: "cell-note", text: " · " + t("people.validated") }));
      tbody.appendChild(
        h("tr", null,
          nameCell,
          h("td", { text: role }),
          h("td", null, h("span", { class: "gender-cell" }, symFor(g), h("span", { text: genderLabel(g, true) }))),
          h("td", null, h("span", { class: "pill " + (p.autoridad ? "pill-ok" : "pill-neutral") }, icon(p.autoridad ? "i-ok" : "i-no"), t(p.autoridad ? "people.auth_yes" : "people.auth_no"))),
          h("td", { class: "num", text: fmt(p.pantalla_s || 0, 0) + " s" }),
          h("td", { class: "num", text: fmt(p.voz_s || 0, 0) + " s" }),
          h("td", { class: "num", text: typeof p.centralidad === "number" ? fmt(p.centralidad, 2) : "—" })
        )
      );
    });
  }

  /* ── Supervisión humana (HitL) ── */

  function personaById(view, id) {
    return view.personas.filter(function (p) { return p.id === id; })[0];
  }

  /** Registro solo de añadido (Art. 12 RIA): se guarda clave + parámetros para re-traducir y anonimizar. */
  function addLog(key, params, personaId) {
    state.log.push({ at: new Date(), key: key, params: params || {}, personaId: personaId || null });
  }

  function logText(view, e) {
    const params = Object.assign({}, e.params);
    if (e.personaId) {
      const p = personaById(view, e.personaId) || { id: e.personaId, nombre: e.personaId };
      params.who = displayName(p);
    }
    if (params.genero) params.g = genderLabel(params.genero, true);
    return t(e.key, params);
  }

  function renderHitl(view) {
    const list = $("arb-list");
    clear(list);
    const pend = pendingCount(view);
    $("arb-count").textContent = String(pend);
    $("arb-count").className = "pill " + (pend > 0 ? "pill-warn" : "pill-ok");

    if (!view.segmentos.length) {
      list.appendChild(h("p", { class: "empty", text: t("hitl.none") }));
    } else if (!view.canArbitrate) {
      list.appendChild(h("p", { class: "note-inline", text: t("hitl.readonly") }));
    } else if (state.closed) {
      list.appendChild(h("p", { class: "note-inline" }, icon("i-ok"), " " + t("hitl.locked")));
    }

    view.segmentos.forEach(function (seg) {
      const base = personaById(view, seg.persona_id) || { id: seg.persona_id, nombre: seg.persona_id, genero: "no_determinado" };
      const dec = state.decisiones[seg.persona_id];
      const card = h("div", { class: "arb-card" + (dec ? " is-done" : ""), role: "group", "aria-label": displayName(base) });
      card.appendChild(
        h("div", { class: "arb-head" },
          h("strong", { text: displayName(base) }),
          h("span", { class: "pill pill-warn" }, icon("i-pending"), t("hitl.review_flag"))
        )
      );
      card.appendChild(
        h("p", { class: "arb-meta", text: t("hitl.channel." + seg.canal) + " · " + mmss(seg.tiempo_i) + "–" + mmss(seg.tiempo_f) + " · " + t("hitl.confidence", { p: fmt(seg.p * 100, 0), u: fmt(M.THRESHOLDS.UMBRAL_ABSTENCION * 100, 0) }) })
      );
      if (seg.evidencia_texto) card.appendChild(h("blockquote", { class: "evidence", text: seg.evidencia_texto }));
      card.appendChild(h("p", { class: "arb-meta", text: t("hitl.proposal", { g: genderLabel(seg.genero_propuesto, true) }) }));

      if (!dec && !state.closed) {
        const selId = "arb-sel-" + seg.persona_id;
        const select = h("select", { id: selId, class: "control control-sm" });
        ["mujer", "hombre", "no_binario"].forEach(function (g) {
          const o = h("option", { value: g, text: genderLabel(g, true) });
          if (g === seg.genero_propuesto) o.selected = true;
          select.appendChild(o);
        });
        const bV = h("button", { type: "button", class: "btn btn-primary btn-sm", text: t("hitl.validate") });
        const bA = h("button", { type: "button", class: "btn btn-sm", text: t("hitl.abstain") });
        bV.addEventListener("click", function () {
          decide(seg, { accion: "validar", genero: select.value });
        });
        bA.addEventListener("click", function () {
          decide(seg, { accion: "abstener" });
        });
        card.appendChild(h("div", { class: "arb-actions" }, h("label", { for: selId, class: "arb-label", text: t("hitl.classify_as") }), select, bV, bA));
      } else if (dec) {
        const stateTxt = dec.accion === "validar" ? t("hitl.state.validated", { g: genderLabel(dec.genero, true) }) : t("hitl.state.abstained");
        const actions = h("div", { class: "arb-actions" }, h("span", { class: "pill pill-ok" }, icon("i-ok"), stateTxt));
        if (!state.closed) {
          const undo = h("button", { type: "button", class: "btn btn-sm", text: t("hitl.undo"), "data-focus": "undo:" + seg.persona_id });
          undo.addEventListener("click", function () {
            delete state.decisiones[seg.persona_id];
            addLog("log.undo", null, seg.persona_id);
            state.focusAfterRender = "decide:" + seg.persona_id;
            refresh(true);
          });
          actions.appendChild(undo);
        }
        card.appendChild(actions);
      }
      list.appendChild(card);
    });

    renderSeal(view, pend);
  }

  function decide(seg, decision) {
    if (state.closed) return;
    state.decisiones[seg.persona_id] = decision;
    if (decision.accion === "validar") {
      addLog("log.validate", { genero: decision.genero, p: fmt(seg.p * 100, 0) }, seg.persona_id);
    } else {
      addLog("log.abstain", null, seg.persona_id);
    }
    state.focusAfterRender = "undo:" + seg.persona_id;
    refresh(true);
  }

  function renderSeal(view, pend) {
    const closed = state.closed;
    const btnClose = $("btn-close");
    btnClose.hidden = closed || state.confirming;
    btnClose.disabled = pend > 0;
    $("close-confirm").hidden = closed || !state.confirming;
    $("btn-reopen").hidden = !closed || state.reopening;
    $("reopen-form").hidden = !closed || !state.reopening;
    $("assume-help").textContent = closed ? t("hitl.closed_note") : pend > 0 ? t("hitl.assume_blocked") : t("hitl.sign_note");

    setPill($("seal-pill"), closed ? "ok" : "warn", closed ? t("seal.ok") : t("seal.draft"), closed ? "i-ok" : "i-pending");
    $("seal-text").textContent = closed ? t("seal.text.ok") : pend > 0 ? t("seal.text.pending", { n: pend }) : t("seal.text.need_assume");

    ["decision-log", "decision-log-draft"].forEach(function (logId) {
      const log = $(logId);
      if (!log) return;
      clear(log);
      if (!state.log.length) {
        log.appendChild(h("li", { class: "empty", text: t("hitl.log_empty") }));
      } else {
        state.log.forEach(function (e) {
          log.appendChild(h("li", null, h("time", { text: e.at.toLocaleTimeString(I.getLang()) + " " }), logText(view, e)));
        });
      }
    });
    updateHash(view, closed);
  }

  function setupSeal() {
    $("btn-close").addEventListener("click", function () {
      state.confirming = true;
      if (state.view) renderSeal(state.view, pendingCount(state.view));
      $("btn-close-confirm").focus();
    });
    $("btn-close-cancel").addEventListener("click", function () {
      state.confirming = false;
      if (state.view) renderSeal(state.view, pendingCount(state.view));
      $("btn-close").focus();
    });
    $("btn-close-confirm").addEventListener("click", function () {
      if (!state.view || pendingCount(state.view) > 0) return;
      state.confirming = false;
      state.closed = true;
      addLog("log.closed");
      state.focusAfterRender = "reopen";
      refresh(true);
    });
    $("btn-reopen").addEventListener("click", function () {
      state.reopening = true;
      $("reopen-reason").value = "";
      $("reopen-error").textContent = "";
      if (state.view) renderSeal(state.view, pendingCount(state.view));
      $("reopen-reason").focus();
    });
    $("btn-reopen-cancel").addEventListener("click", function () {
      state.reopening = false;
      if (state.view) renderSeal(state.view, pendingCount(state.view));
      $("btn-reopen").focus();
    });
    $("reopen-form").addEventListener("submit", function (e) {
      e.preventDefault();
      const reason = $("reopen-reason").value.trim();
      if (reason.length < 10) {
        $("reopen-error").textContent = t("hitl.reopen_error");
        $("reopen-reason").setAttribute("aria-invalid", "true");
        $("reopen-reason").focus();
        return;
      }
      $("reopen-reason").removeAttribute("aria-invalid");
      state.reopening = false;
      state.closed = false;
      addLog("log.reopened", { reason: reason });
      state.focusAfterRender = "close";
      refresh(true);
    });
  }

  function canonical(obj) {
    if (Array.isArray(obj)) return "[" + obj.map(canonical).join(",") + "]";
    if (obj && typeof obj === "object") {
      return "{" + Object.keys(obj).sort().map(function (k) { return JSON.stringify(k) + ":" + canonical(obj[k]); }).join(",") + "}";
    }
    return JSON.stringify(obj === undefined ? null : obj);
  }

  function dictamen(view, sealed) {
    return {
      video_id: view.video_id,
      origen_calculo: view.origin,
      metricas: view.metricas,
      alertas: view.alertas,
      salvaguarda: view.salvaguarda,
      bechdel: view.bechdel,
      indice_global: view.indice,
      diagnostico: view.diagnostico,
      decisiones_humanas: state.decisiones,
      supervision_humana_asumida: sealed
    };
  }

  function updateHash(view, sealed) {
    const out = $("seal-hash");
    const token = ++state.hashToken;
    if (!(window.crypto && window.crypto.subtle)) {
      out.textContent = t("hitl.hash_unavailable");
      return;
    }
    const data = new TextEncoder().encode(canonical(dictamen(view, sealed)));
    window.crypto.subtle.digest("SHA-256", data).then(function (buf) {
      if (token !== state.hashToken) return;
      out.textContent = Array.from(new Uint8Array(buf)).map(function (b) { return b.toString(16).padStart(2, "0"); }).join("");
    });
  }

  /* ── Clima, ciudadanía, trazabilidad ── */

  function renderClimate(view) {
    const tbody = $("climate-body");
    clear(tbody);
    const hasNb = view.clima && view.clima.no_binario && (
      (view.clima.no_binario.tecnico_asertivo || 0) > 0 ||
      (view.clima.no_binario.colaborativo || 0) > 0 ||
      (view.clima.no_binario.disenso || 0) > 0
    );
    const thNb = $("climate-th-nb");
    if (thNb) thNb.hidden = !hasNb;

    ["tecnico_asertivo", "colaborativo", "disenso"].forEach(function (k) {
      const row = [
        h("th", { scope: "row", text: t("climate." + k) }),
        h("td", { class: "num", text: fmt(view.clima.mujer[k], 0) + " %" }),
        h("td", { class: "num", text: fmt(view.clima.hombre[k], 0) + " %" })
      ];
      if (hasNb) {
        row.push(h("td", { class: "num", text: fmt((view.clima.no_binario && view.clima.no_binario[k]) || 0, 0) + " %" }));
      }
      tbody.appendChild(h("tr", null, ...row));
    });
  }

  function renderCitizen(view) {
    const sum = $("citizen-summary");
    const buttons = document.querySelectorAll("[data-vote]");
    if (view.citizenApi) {
      sum.textContent = t("citizen.api", view.citizenApi);
      buttons.forEach(function (b) { b.disabled = true; });
      return;
    }
    const total = state.votes.yes + state.votes.partial + state.votes.no;
    sum.textContent = total === 0 ? t("citizen.empty") : (state.voted ? t("citizen.thanks") + " " : "") + t("citizen.summary", state.votes);
    buttons.forEach(function (b) { b.disabled = state.voted; });
  }

  function renderPipeline(view) {
    const ol = $("pipeline");
    clear(ol);
    const pasos = (view.status && view.status.pasos) || {};
    const overallOk = view.status && view.status.estado === "ok";
    PIPELINE_STEPS.forEach(function (s) {
      let st = pasos[s] || (overallOk ? "ok" : "pending");
      if (["ok", "pending", "running", "error"].indexOf(st) < 0) st = st === "listo" || st === "done" ? "ok" : "pending";
      ol.appendChild(
        h("li", { class: "step step-" + st },
          icon(st === "ok" ? "i-ok" : st === "error" ? "i-no" : "i-pending"),
          h("span", { class: "step-name", text: t("step." + s) }),
          h("span", { class: "step-state", text: t("step.state." + st) })
        )
      );
    });
  }

  /** Aviso visible cuando la interfaz está en una lengua cuya traducción no ha revisado una persona hablante nativa. */
  function renderLangNotice() {
    const box = $("lang-notice");
    clear(box);
    const lang = I.getLang();
    box.hidden = lang !== "eu";
    if (lang !== "eu") return;
    box.appendChild(h("span", { lang: "eu", text: t("lang.unreviewed") }));
    box.appendChild(document.createTextNode(" · "));
    box.appendChild(h("span", { lang: "es", text: I.DICT.es["lang.unreviewed"] }));
  }

  function renderChrome(view) {
    renderLangNotice();
    $("video-id-badge").textContent = view.video_id;
    let originKey = view.origin === "client" ? "origin.client" : view.origin === "api" ? "origin.api" : "origin.mixed";
    if (view.proyeccion) originKey = "origin.projection";
    setPill($("calc-origin-badge"), view.origin === "client" ? "warn" : "neutral", t(originKey));
    $("synthetic-note").hidden = state.datasetKey === "live" || state.fase === "preproduccion";
  }

  /* ───────────────────────── Revisión preventiva (D-11) ───────────────────────── */

  function durText(s) {
    const total = Math.max(0, Math.round(Number(s) || 0));
    const m = Math.floor(total / 60);
    const sec = total % 60;
    if (m === 0) return t("dur.s", { s: sec });
    if (sec === 0) return t("dur.m", { m: m });
    return t("dur.ms", { m: m, s: sec });
  }

  function namesOf(view, ids) {
    const byId = {};
    view.personas.forEach(function (p) { byId[p.id] = p; });
    return listText((ids || []).map(function (id) { return byId[id] ? displayName(byId[id]) : id; }));
  }

  function topicLabel(view, id) {
    const n = view.nodes.filter(function (x) { return x.id === id; })[0];
    return n ? n.label : id;
  }

  const REC_METRIC = {
    pendientes: "rec.m.hitl", voz: "rec.m.voz", pantalla: "rec.m.pantalla", washing: "rec.m.washing",
    una_mujer: "rec.m.bechdel", bechdel_r1: "rec.m.bechdel", bechdel_r3: "rec.m.bechdel", rotulo: "rec.m.bechdel",
    eje: "rec.m.grafo", tema_m: "rec.m.grafo", tema_f: "rec.m.grafo", ok: "rec.m.ok"
  };

  function renderPreventive(view) {
    // Cobertura del material (edición)
    if (state.fase === "edicion") {
      const caso = view.caso || {};
      const analizado = caso.duracion_s || null;
      const input = $("coverage-planned");
      if (state.previstaMin === null && caso.duracion_prevista_s) state.previstaMin = Math.round(caso.duracion_prevista_s / 60);
      if (document.activeElement !== input) input.value = state.previstaMin || "";
      let txt;
      if (!analizado) txt = t("prev.coverage_unknown");
      else if (!state.previstaMin) txt = t("prev.coverage_need", { a: fmt(analizado / 60, 0) });
      else {
        const pct = Math.min(100, (analizado / 60 / state.previstaMin) * 100);
        txt = t(pct >= 99.5 ? "prev.coverage_full" : "prev.coverage", { a: fmt(analizado / 60, 0), p: fmt(state.previstaMin, 0), pct: fmt(pct, 0) });
      }
      $("coverage-text").textContent = txt;
    }

    // Márgenes hasta la paridad
    const tiempos = M.tiempos(view.personas);
    [["voz", "margin-voz"], ["pantalla", "margin-pantalla"]].forEach(function (c) {
      const box = $(c[1]);
      clear(box);
      const m = M.margenParidad(tiempos, c[0]);
      if (m.cumple) {
        box.appendChild(h("p", { class: "margin-ok" }, icon("i-ok"), t("prev.margin_ok")));
      } else if (m.anadir_s === null) {
        box.appendChild(h("p", { class: "card-text", text: t("prev.margin_na") }));
      } else {
        box.appendChild(h("div", { class: "margin-options" },
          h("div", { class: "margin-option" }, h("strong", { text: durText(m.anadir_s) }), " ", h("span", { text: t("prev.margin_add") })),
          h("div", { class: "margin-option" }, h("strong", { text: durText(m.redistribuir_s) }), " ", h("span", { text: t("prev.margin_redist") }))
        ));
      }
    });

    // Recomendaciones
    const ev = { personas: view.personas, tiempos_s: tiempos, alertas: view.alertas, bechdel: view.bechdel };
    const recs = M.recomendaciones(ev, view.edges, { pendientes: pendingCount(view) });
    const ol = $("recs-list");
    clear(ol);
    recs.forEach(function (r) {
      const p = r.params;
      const params = Object.assign({}, p);
      if (p.ids) params.who = namesOf(view, p.ids);
      if (p.tema) params.tema = topicLabel(view, p.tema);
      if (p.add !== undefined) { params.add = durText(p.add); params.redist = durText(p.redist); }
      let clave = r.clave;
      if (clave === "rec.washing" && !(p.ids && p.ids.length)) clave = "rec.washing_generic";
      if (clave === "rec.bechdel_r1" && !(p.ids && p.ids.length)) clave = "rec.bechdel_r1_generic";
      const prioKey = r.prioridad === 1 ? "rec.p1" : r.prioridad === 2 ? "rec.p2" : "rec.p3";
      const prioCls = r.prioridad === 1 ? "pill-alert" : r.prioridad === 2 ? "pill-warn" : "pill-neutral";
      const metric = t(REC_METRIC[r.id.split(":")[0]] || "rec.m.ok");
      ol.appendChild(h("li", null,
        h("span", { class: "pill " + (r.id === "ok" ? "pill-ok" : prioCls) }, r.id === "ok" ? t("rec.p_ok") : t(prioKey)),
        h("span", { class: "rec-body" }, h("span", { text: t(clave, params) }), " ", h("span", { class: "rec-metric", text: metric }))
      ));
    });
  }

  /* ── Simulador «¿y si…?» (solo edición) ── */

  function simBase(view) {
    const caso = view.caso || {};
    return {
      personas: view.personas.map(function (p) { return Object.assign({}, p); }),
      secuencia_turnos: caso.secuencia_turnos || [],
      referentes: caso.referentes,
      apertura_id: caso.apertura_id,
      cierre_id: caso.cierre_id,
      mesa_monografica_diversidad: caso.mesa_monografica_diversidad
    };
  }

  function renderSimTable(view) {
    const tbody = $("sim-body");
    clear(tbody);
    const base = simBase(view);
    const filas = base.personas.concat(state.ajustes.nuevas);
    filas.forEach(function (p) {
      const over = state.ajustes.personas[p.id] || {};
      const cur = Object.assign({}, p, over);
      const isNew = p.id.indexOf("sim") === 0;
      const name = isNew ? t(cur.voz_s > 0 ? "sim.new_voice" : "sim.new_silent", { n: p.id.replace("sim", "") }) : displayName(p);
      const mk = function (field) {
        const inp = h("input", { type: "number", min: "0", step: "5", class: "control control-sm", value: String(Math.round(Number(cur[field]) || 0)), "aria-label": name + " — " + t(field === "voz_s" ? "sim.col_voice" : "sim.col_screen") });
        inp.addEventListener("input", function () { setSim(p.id, field, Math.max(0, Number(inp.value) || 0), isNew); });
        return inp;
      };
      const rot = h("input", { type: "checkbox", "aria-label": name + " — " + t("esc.col_label") });
      rot.checked = Boolean(cur.rotulo);
      rot.addEventListener("change", function () { setSim(p.id, "rotulo", rot.checked, isNew); });
      tbody.appendChild(h("tr", null,
        h("td", { class: "strong", text: name }),
        h("td", null, h("span", { class: "gender-cell" }, symFor(cur.genero), h("span", { text: genderLabel(cur.genero, true) }))),
        h("td", { class: "num" }, mk("voz_s")),
        h("td", { class: "num" }, mk("pantalla_s")),
        h("td", null, rot)
      ));
    });
    $("sim-mm").checked = Boolean(state.ajustes.turno_mm);
  }

  function setSim(id, field, value, isNew) {
    if (isNew) {
      const p = state.ajustes.nuevas.filter(function (x) { return x.id === id; })[0];
      if (p) p[field] = value;
    } else {
      state.ajustes.personas[id] = Object.assign({}, state.ajustes.personas[id] || {}, { [field]: value });
    }
    renderSimResult(state.view, true);
  }

  function simRows(ev) {
    const m = ev.metricas;
    const b = ev.bechdel;
    return [
      { k: "sim.r.voz", v: fmt(m.voz_pct.mujer, 1) + " %", n: m.voz_pct.mujer },
      { k: "sim.r.pantalla", v: fmt(m.pantalla_pct.mujer, 1) + " %", n: m.pantalla_pct.mujer },
      { k: "sim.r.rvp", v: m.ratio_voz_pantalla.mujer === null ? t("metrics.rvp_na") : fmt(m.ratio_voz_pantalla.mujer, 2) },
      { k: "alerts.washing.title", v: t(ev.alertas.equality_washing.activa ? "state.active" : "state.inactive"), bad: ev.alertas.equality_washing.activa },
      { k: "alerts.infra.title", v: t(ev.alertas.infrarrepresentacion.activa ? "state.active" : "state.inactive"), bad: ev.alertas.infrarrepresentacion.activa },
      { k: "alerts.salv.title", v: t(ev.salvaguarda.cumple_salvaguarda_paridad ? "state.cumple" : "state.no_cumple"), bad: !ev.salvaguarda.cumple_salvaguarda_paridad },
      { k: "bechdel.title", v: b.aplica ? b.puntuacion_bechdel_0_3 + " / 3" : t("bechdel.na") },
      { k: "index.title", v: fmt(ev.indice_global.total, 0) + " / 100" }
    ];
  }

  function renderSimResult(view, announceIt) {
    if (!view) return;
    const base = simBase(view);
    const ahora = M.evaluar(base, {});
    const despues = M.evaluar(M.simular(base, state.ajustes), {});
    const a = simRows(ahora);
    const d = simRows(despues);
    const tbody = $("sim-result-body");
    clear(tbody);
    const cambios = [];
    a.forEach(function (row, i) {
      const changed = row.v !== d[i].v;
      if (changed) cambios.push(t(row.k) + ": " + d[i].v);
      const after = h("td", { class: changed ? "changed" : null });
      if (d[i].bad !== undefined) after.appendChild(h("span", { class: "pill " + (d[i].bad ? "pill-alert" : "pill-ok") }, icon(d[i].bad ? "i-warn" : "i-ok"), d[i].v));
      else after.appendChild(document.createTextNode(d[i].v));
      if (changed) after.appendChild(h("span", { class: "delta", text: "← " + row.v }));
      const now = h("td");
      if (row.bad !== undefined) now.appendChild(h("span", { class: "pill " + (row.bad ? "pill-alert" : "pill-ok") }, icon(row.bad ? "i-warn" : "i-ok"), row.v));
      else now.appendChild(document.createTextNode(row.v));
      tbody.appendChild(h("tr", null, h("th", { scope: "row", text: t(row.k) }), now, after));
    });
    if (announceIt) {
      window.clearTimeout(renderSimResult.timer);
      renderSimResult.timer = window.setTimeout(function () {
        $("sim-announce").textContent = cambios.length ? t("sim.changed", { list: cambios.join("; ") }) : t("sim.nochange");
      }, 600);
    }
  }

  function resetSim() {
    state.ajustes = { personas: {}, nuevas: [], turno_mm: false };
    state.simSeq = 0;
  }

  function setupSimulator() {
    function addPerson(voz) {
      state.simSeq++;
      const s = voz ? 120 : 0;
      state.ajustes.nuevas.push({ id: "sim" + state.simSeq, nombre: null, genero: "mujer", voz_s: s, pantalla_s: voz ? 120 : 120, rotulo: Boolean(voz), autoridad: Boolean(voz), centralidad: null });
      renderSimTable(state.view);
      renderSimResult(state.view, true);
    }
    $("sim-add-voice").addEventListener("click", function () { addPerson(true); });
    $("sim-add-silent").addEventListener("click", function () { addPerson(false); });
    $("sim-mm").addEventListener("change", function (e) {
      state.ajustes.turno_mm = e.target.checked;
      renderSimResult(state.view, true);
    });
    $("sim-reset").addEventListener("click", function () {
      resetSim();
      renderSimTable(state.view);
      renderSimResult(state.view, true);
    });
  }

  /* ── Escaleta (preproducción) ── */

  function loadEscaletaDemo() {
    state.escaleta = (window.AIASN_ESCALETA_DEMO || []).map(function (f) { return Object.assign({}, f); });
    state.escSeq = state.escaleta.length;
  }

  let escTimer = null;
  function escChanged() {
    window.clearTimeout(escTimer);
    escTimer = window.setTimeout(function () { refresh(false); }, 250);
  }

  function renderEscaleta() {
    const tbody = $("esc-body");
    clear(tbody);
    state.escaleta.forEach(function (f, idx) {
      const label = f.nombre || t("esc.unnamed", { n: idx + 1 });
      const name = h("input", { type: "text", class: "control control-sm", value: f.nombre || "", "aria-label": t("esc.col_name") + " " + (idx + 1), placeholder: t("esc.placeholder") });
      name.addEventListener("input", function () { f.nombre = name.value; escChanged(); });
      const gen = h("select", { class: "control control-sm", "aria-label": t("esc.col_gender") + " — " + label });
      ["mujer", "hombre", "no_binario"].forEach(function (g) {
        const o = h("option", { value: g, text: genderLabel(g, true) });
        if (g === f.genero) o.selected = true;
        gen.appendChild(o);
      });
      gen.addEventListener("change", function () { f.genero = gen.value; escChanged(); });
      const min = h("input", { type: "number", min: "0", step: "1", class: "control control-sm", value: String(f.minutos || 0), "aria-label": t("esc.col_minutes") + " — " + label });
      min.addEventListener("input", function () { f.minutos = Math.max(0, Number(min.value) || 0); escChanged(); });
      const rot = h("input", { type: "checkbox", "aria-label": t("esc.col_label") + " — " + label });
      rot.checked = Boolean(f.rotulo);
      rot.addEventListener("change", function () { f.rotulo = rot.checked; escChanged(); });
      const del = h("button", { type: "button", class: "btn btn-sm btn-ghost", text: t("esc.remove"), "aria-label": t("esc.remove") + " — " + label });
      const move = function (dir, cls) {
        const b = h("button", { type: "button", class: "btn btn-sm btn-ghost " + cls, text: dir < 0 ? "↑" : "↓", "aria-label": t(dir < 0 ? "esc.up" : "esc.down") + " — " + label });
        b.disabled = dir < 0 ? idx === 0 : idx === state.escaleta.length - 1;
        b.addEventListener("click", function () {
          const j = idx + dir;
          const tmp = state.escaleta[idx];
          state.escaleta[idx] = state.escaleta[j];
          state.escaleta[j] = tmp;
          renderEscaleta();
          refresh(false);
          const target = document.querySelector("#esc-body tr:nth-child(" + (j + 1) + ") ." + cls);
          if (target && !target.disabled) target.focus();
          else { const other = document.querySelector("#esc-body tr:nth-child(" + (j + 1) + ") button:not([disabled])"); if (other) other.focus(); }
          announce(t("esc.moved", { name: label, pos: j + 1 }));
        });
        return b;
      };
      del.addEventListener("click", function () {
        state.escaleta.splice(idx, 1);
        renderEscaleta();
        refresh(false);
        const next = document.querySelector("#esc-body tr:nth-child(" + Math.max(1, idx) + ") input") || $("esc-add");
        next.focus();
      });
      tbody.appendChild(h("tr", null, h("td", null, name), h("td", null, gen), h("td", { class: "num" }, min), h("td", null, rot), h("td", { class: "row-actions" }, move(-1, "mv-up"), move(1, "mv-down"), del)));
    });
  }

  function setupEscaleta() {
    $("esc-add").addEventListener("click", function () {
      state.escSeq++;
      state.escaleta.push({ id: "e" + state.escSeq, nombre: "", genero: "mujer", minutos: 8, rotulo: true });
      renderEscaleta();
      refresh(false);
      const inputs = document.querySelectorAll('#esc-body input[type="text"]');
      if (inputs.length) inputs[inputs.length - 1].focus();
    });
    $("esc-reset").addEventListener("click", function () {
      loadEscaletaDemo();
      renderEscaleta();
      refresh(false);
    });
  }

  /* ── Cambio de fase ── */

  function setFase(fase, opts) {
    const o = opts || {};
    if (["preproduccion", "edicion", "publicado"].indexOf(fase) < 0) return;
    const prev = state.fase;
    state.fase = fase;
    document.body.dataset.fase = fase;
    document.querySelectorAll('input[name="fase"]').forEach(function (r) { r.checked = r.value === fase; });
    // Material inédito: anonimizar por defecto al entrar en revisión preventiva
    if (fase !== "publicado" && prev === "publicado") {
      state.anonymized = true;
      $("anonymize-toggle").checked = true;
    }
    resetSupervision();
    resetSim();
    state.previstaMin = null;
    if (fase === "preproduccion") {
      if (!state.escaleta.length) loadEscaletaDemo();
      renderEscaleta();
      $("live-panel").hidden = true;
    } else {
      $("live-panel").hidden = state.datasetKey !== "live";
    }
    refresh(false);
    if (!o.silent) announce(t("phase.announce." + fase));
  }

  function setupPhase() {
    document.querySelectorAll('input[name="fase"]').forEach(function (r) {
      r.addEventListener("change", function () { if (r.checked) setFase(r.value); });
    });
    $("coverage-planned").addEventListener("input", function (e) {
      const v = Number(e.target.value);
      state.previstaMin = v > 0 ? v : null;
      if (state.view) renderPreventive(state.view);
    });
  }

  /* ───────────────────────── Ciclo de render ───────────────────────── */

  function setEmpty(empty) {
    document.querySelectorAll("main > section:not(.toolbar):not(#empty-state)").forEach(function (s) {
      s.hidden = empty;
    });
    const es = $("empty-state");
    if (es) es.hidden = !empty;
  }

  function refresh(announceChange) {
    renderLangNotice();
    const view = currentView();
    state.view = view;
    if (!view) {
      setEmpty(true);
      $("video-id-badge").textContent = "—";
      setPill($("calc-origin-badge"), "neutral", "—");
      $("synthetic-note").hidden = true;
      return;
    }
    setEmpty(false);
    renderChrome(view);
    renderVerdict(view);
    renderAlerts(view);
    renderMetrics(view);
    renderPeople(view);
    renderHitl(view);
    renderClimate(view);
    renderCitizen(view);
    renderPipeline(view);
    renderGraph(view);
    if (state.fase !== "publicado") renderPreventive(view);
    if (state.fase === "edicion") {
      renderSimTable(view);
      renderSimResult(view, false);
    }

    if (state.focusAfterRender) {
      const key = state.focusAfterRender;
      state.focusAfterRender = null;
      let target = null;
      if (key === "reopen") target = $("btn-reopen");
      else if (key === "close") target = document.querySelector(".arb-card select") || $("btn-close");
      else target = document.querySelector('[data-focus="' + key + '"]') || document.getElementById("arb-sel-" + key.split(":")[1]) || $("btn-close");
      if (target && !target.disabled && !target.hidden) target.focus();
    }
    if (announceChange) {
      announce(t("sr.decision", { title: t("verdict.title." + view.diagnostico) }) + " " + $("hero-sub").textContent);
    }
  }

  /* ───────────────────────── Interacciones ───────────────────────── */

  function applyThemeUi() {
    const dark = document.documentElement.classList.contains("dark");
    const btn = $("theme-toggle");
    btn.setAttribute("aria-pressed", dark ? "true" : "false");
    $("theme-toggle-label").textContent = t(dark ? "ui.theme_to_light" : "ui.theme_to_dark");
  }

  function setupTheme() {
    applyThemeUi();
    $("theme-toggle").addEventListener("click", function () {
      const next = !document.documentElement.classList.contains("dark");
      document.documentElement.classList.toggle("dark", next);
      try { localStorage.setItem("aiasn-theme", next ? "dark" : "light"); } catch (e) {}
      applyThemeUi();
      if (state.view) renderGraph(state.view);
    });
    if (window.matchMedia) {
      window.matchMedia("(prefers-color-scheme: dark)").addEventListener("change", function (e) {
        let saved = null;
        try { saved = localStorage.getItem("aiasn-theme"); } catch (err) {}
        if (saved) return;
        document.documentElement.classList.toggle("dark", e.matches);
        applyThemeUi();
        if (state.view) renderGraph(state.view);
      });
    }
  }

  /* ── Ventana de información (una sola, accesible por teclado) ── */

  const infoState = { btn: null, pinned: false, timer: null };

  function infoPanel() {
    let p = $("info-panel");
    if (!p) {
      p = h("div", { id: "info-panel", class: "info-panel", role: "region", hidden: true, tabindex: "-1" });
      document.body.appendChild(p);
      p.addEventListener("mouseenter", function () { window.clearTimeout(infoState.timer); });
      p.addEventListener("mouseleave", function () { scheduleInfoClose(); });
    }
    return p;
  }

  function positionInfo(btn, panel) {
    const r = btn.getBoundingClientRect();
    const margin = 8;
    const width = Math.min(340, window.innerWidth - margin * 2);
    panel.style.width = width + "px";
    let left = Math.min(Math.max(margin, r.left), window.innerWidth - width - margin);
    let top = r.bottom + 6;
    panel.style.left = left + "px";
    panel.style.top = top + "px";
    const ph = panel.getBoundingClientRect().height;
    if (top + ph > window.innerHeight - margin && r.top - ph - 6 > margin) panel.style.top = r.top - ph - 6 + "px";
  }

  function openInfo(btn, pin) {
    const panel = infoPanel();
    window.clearTimeout(infoState.timer);
    if (infoState.btn && infoState.btn !== btn) infoState.btn.setAttribute("aria-expanded", "false");
    const key = btn.dataset.infoKey;
    clear(panel);
    panel.setAttribute("aria-label", t("info." + key + ".t"));
    panel.appendChild(h("p", { class: "info-title", text: t("info." + key + ".t") }));
    panel.appendChild(h("p", { class: "info-body", text: t("info." + key + ".b") }));
    panel.hidden = false;
    positionInfo(btn, panel);
    btn.setAttribute("aria-expanded", "true");
    infoState.btn = btn;
    infoState.pinned = Boolean(pin);
  }

  function closeInfo(returnFocus) {
    const panel = $("info-panel");
    window.clearTimeout(infoState.timer);
    if (panel) panel.hidden = true;
    if (infoState.btn) {
      infoState.btn.setAttribute("aria-expanded", "false");
      if (returnFocus) infoState.btn.focus();
    }
    infoState.btn = null;
    infoState.pinned = false;
  }

  function scheduleInfoClose() {
    window.clearTimeout(infoState.timer);
    if (infoState.pinned) return;
    infoState.timer = window.setTimeout(function () { closeInfo(false); }, 220);
  }

  function setupInfo() {
    document.querySelectorAll(".info-host[data-info]").forEach(function (host) {
      const key = host.getAttribute("data-info");
      const btn = h("button", { type: "button", class: "info-btn", "aria-expanded": "false", "aria-controls": "info-panel", "data-info-key": key }, icon("i-info"));
      host.appendChild(btn);
      btn.addEventListener("click", function () {
        if (infoState.btn === btn && infoState.pinned) closeInfo(false);
        else openInfo(btn, true);
      });
      btn.addEventListener("mouseenter", function () { if (!infoState.pinned) openInfo(btn, false); });
      btn.addEventListener("mouseleave", scheduleInfoClose);
    });
    labelInfoButtons();
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && infoState.btn) {
        e.preventDefault();
        closeInfo(true);
      }
    });
    document.addEventListener("click", function (e) {
      const panel = $("info-panel");
      if (!infoState.btn) return;
      if (infoState.btn.contains(e.target) || (panel && panel.contains(e.target))) return;
      closeInfo(false);
    });
    window.addEventListener("scroll", function () { if (infoState.btn) closeInfo(false); }, { passive: true });
    window.addEventListener("resize", function () { if (infoState.btn) closeInfo(false); });
  }

  function labelInfoButtons() {
    document.querySelectorAll(".info-btn").forEach(function (b) {
      b.setAttribute("aria-label", t("info.open", { title: t("info." + b.dataset.infoKey + ".t") }));
    });
  }

  /* ── Resto de eventos ── */

  function setupSpeech() {
    const btn = $("btn-speak");
    const label = btn.querySelector("span");
    function setLabel(speaking) { label.textContent = t(speaking ? "easy.stop" : "easy.listen"); }
    btn.addEventListener("click", function () {
      if (!("speechSynthesis" in window)) {
        announce(t("easy.unsupported"));
        return;
      }
      if (window.speechSynthesis.speaking) {
        window.speechSynthesis.cancel();
        setLabel(false);
        return;
      }
      const text = Array.from(document.querySelectorAll("#easy-read-list li")).map(function (li) { return li.textContent; }).join(" ");
      const u = new SpeechSynthesisUtterance(text);
      u.lang = { es: "es-ES", ca: "ca-ES", gl: "gl-ES", eu: "eu-ES", en: "en-GB" }[I.getLang()] || "es-ES";
      u.onend = function () { setLabel(false); };
      u.onerror = function () { setLabel(false); };
      window.speechSynthesis.speak(u);
      setLabel(true);
    });
    document.addEventListener("aiasn:langchange", function () { setLabel(false); });
  }

  function setupExport() {
    $("btn-print").addEventListener("click", function () { window.print(); });
    $("btn-json").addEventListener("click", function () {
      if (!state.view) return;
      const view = state.view;
      const pend = pendingCount(view);
      const data = dictamen(view, state.closed);
      data.generado_en = new Date().toISOString();
      data.fase_material = state.fase;
      data.modo = state.fase === "publicado" ? "certificacion" : "preventivo";
      data.certificable = state.fase === "publicado";
      data.registro_decisiones = state.log.map(function (e) {
        return { momento: e.at.toISOString(), evento: e.key.replace(/^log\./, ""), persona_id: e.personaId, detalle: logText(view, e) };
      });
      data.personas = view.personas.map(function (p) {
        return { id: p.id, nombre: state.anonymized ? t("anon.name", { id: p.id }) : p.nombre, cargo: state.anonymized ? null : p.cargo, genero_percibido: p.genero, autoridad: p.autoridad, pantalla_s: p.pantalla_s, voz_s: p.voz_s };
      });
      data.huella_sha256 = $("seal-hash").textContent;
      const blob = new Blob([JSON.stringify(data, null, 2)], { type: "application/json" });
      const url = URL.createObjectURL(blob);
      const a = h("a", { href: url, download: "dictamen_" + view.video_id + ".json" });
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    });
  }

  function setupVoting() {
    document.querySelectorAll("[data-vote]").forEach(function (b) {
      b.addEventListener("click", function () {
        if (state.voted) return;
        state.votes[b.dataset.vote]++;
        state.voted = true;
        if (state.view) renderCitizen(state.view);
      });
    });

    const btnQr = $("btn-toggle-qr");
    const qrBox = $("citizen-qr-box");
    if (btnQr && qrBox) {
      btnQr.addEventListener("click", function () {
        const exp = btnQr.getAttribute("aria-expanded") === "true";
        btnQr.setAttribute("aria-expanded", String(!exp));
        qrBox.hidden = exp;
        if (!exp) {
          drawCitizenQr();
        }
      });
    }
  }

  function drawCitizenQr() {
    const canvas = $("qr-canvas");
    const urlSpan = $("citizen-share-url");
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    // Generar URL para escanear y participar directamente
    const currentUrl = new URL(window.location.href);
    currentUrl.hash = "ciudadania";
    currentUrl.searchParams.set("caso", state.datasetKey || "A");
    const targetUrl = currentUrl.toString();
    if (urlSpan) urlSpan.textContent = targetUrl;

    const w = canvas.width;
    const h = canvas.height;
    ctx.fillStyle = "#ffffff";
    ctx.fillRect(0, 0, w, h);

    // Generador autónomo y ligero de patrón QR (sin dependencias de red)
    // Dibuja los 3 marcadores de posición canónicos en esquinas + matriz de sincronización determinista
    ctx.fillStyle = "#0f172a";
    const pad = 8;
    const sz = w - pad * 2;
    const grid = 21; // QR versión 1 (21x21 módulos)
    const mod = sz / grid;

    function drawFinder(r0, c0) {
      for (let r = 0; r < 7; r++) {
        for (let c = 0; c < 7; c++) {
          const edge = r === 0 || r === 6 || c === 0 || c === 6;
          const center = r >= 2 && r <= 4 && c >= 2 && c <= 4;
          if (edge || center) {
            ctx.fillRect(pad + (c0 + c) * mod, pad + (r0 + r) * mod, mod, mod);
          }
        }
      }
    }

    drawFinder(0, 0);
    drawFinder(0, 14);
    drawFinder(14, 0);

    // Líneas de sincronización (timing patterns)
    for (let i = 8; i < 13; i += 2) {
      ctx.fillRect(pad + i * mod, pad + 6 * mod, mod, mod);
      ctx.fillRect(pad + 6 * mod, pad + i * mod, mod, mod);
    }

    // Hash determinista del enlace para poblar los módulos de datos
    let hash = 0;
    for (let i = 0; i < targetUrl.length; i++) {
      hash = ((hash << 5) - hash) + targetUrl.charCodeAt(i);
      hash |= 0;
    }

    for (let r = 0; r < grid; r++) {
      for (let c = 0; c < grid; c++) {
        const inFinder = (r < 8 && c < 8) || (r < 8 && c >= 13) || (r >= 13 && c < 8);
        const inTiming = (r === 6 || c === 6);
        if (inFinder || inTiming) continue;
        // Pseudoaleatorio determinista derivado del hash de la URL
        const bit = ((hash ^ (r * 31 + c * 17)) & 1) === 0;
        if (bit) {
          ctx.fillRect(pad + c * mod, pad + r * mod, mod, mod);
        }
      }
    }
  }

  function setupSectionNav() {
    if (!("IntersectionObserver" in window)) return;
    const links = {};
    document.querySelectorAll(".section-nav a").forEach(function (a) { links[a.getAttribute("href").slice(1)] = a; });
    const io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (!en.isIntersecting) return;
        Object.keys(links).forEach(function (k) { links[k].removeAttribute("aria-current"); });
        const l = links[en.target.id];
        if (l) l.setAttribute("aria-current", "true");
      });
    }, { rootMargin: "-20% 0px -70% 0px" });
    Object.keys(links).forEach(function (id) {
      const s = document.getElementById(id);
      if (s) io.observe(s);
    });
  }

  /* ── Modo en vivo (API FastAPI según API_SPEC.md: POST /videos + sondeo GET /videos/{id}) ── */

  function liveMsg(text) {
    $("live-message").textContent = text;
  }

  function currentStep(status) {
    const pasos = (status && status.pasos) || {};
    const next = PIPELINE_STEPS.filter(function (s) { return pasos[s] !== "ok"; })[0];
    return next ? t("step." + next) : "";
  }

  async function runLive(e) {
    e.preventDefault();
    const file = $("video-file").files[0];
    if (!file) {
      liveMsg(t("live.nofile"));
      return;
    }
    const base = $("api-url").value.replace(/\/+$/, "");
    const submit = $("live-submit");
    submit.disabled = true;
    try {
      liveMsg(t("live.sending"));
      const fd = new FormData();
      fd.append("file", file);
      // Revisión preventiva (D-11): el backend no debe certificar ni conservar material inédito
      const preventivo = state.fase !== "publicado";
      fd.append("modo", preventivo ? "preventivo" : "certificacion");
      fd.append("estado_material", preventivo ? "montaje" : "final");
      if (preventivo) fd.append("retencion", "efimera");
      const res = await fetch(base + "/videos", { method: "POST", body: fd });
      if (!res.ok) throw new Error("HTTP " + res.status);
      const created = await res.json();
      const id = created.video_id;
      const started = Date.now();
      for (;;) {
        if (Date.now() - started > POLL_MAX_MS) throw new Error("timeout");
        const r = await fetch(base + "/videos/" + encodeURIComponent(id));
        if (!r.ok) throw new Error("HTTP " + r.status);
        const body = await r.json();
        const estado = body.status && body.status.estado;
        if (estado === "error") throw new Error((body.status && body.status.error) || "error");
        if (estado === "ok" && body.resultado) {
          state.live = body;
          resetSupervision();
          liveMsg(t("live.done"));
          refresh(true);
          return;
        }
        liveMsg(t("live.processing", { step: currentStep(body.status) }));
        await new Promise(function (ok) { window.setTimeout(ok, POLL_INTERVAL_MS); });
      }
    } catch (err) {
      const offline = err instanceof TypeError;
      liveMsg(offline ? t("live.offline") : t("live.error", { msg: err.message }));
    } finally {
      submit.disabled = false;
    }
  }

  function resetSupervision() {
    state.decisiones = {};
    state.log = [];
    state.closed = false;
    state.confirming = false;
    state.reopening = false;
  }

  function setDataset(key) {
    state.datasetKey = key;
    resetSupervision();
    resetSim();
    state.previstaMin = null;
    $("live-panel").hidden = key !== "live";
    refresh(false);
    const v = state.view;
    if (v) announce(t("sr.loaded", { id: v.video_id, title: t("verdict.title." + v.diagnostico) }));
  }

  function setupControls() {
    $("dataset-select").addEventListener("change", function (e) { setDataset(e.target.value); });
    $("anonymize-toggle").addEventListener("change", function (e) {
      state.anonymized = e.target.checked;
      refresh(false);
    });
    $("lang-select").addEventListener("change", function (e) {
      I.setLang(e.target.value);
    });
    $("live-panel").addEventListener("submit", runLive);
    document.addEventListener("aiasn:langchange", function () {
      applyThemeUi();
      labelInfoButtons();
      closeInfo(false);
      refresh(false);
    });
  }

  function setupBackToTop() {
    const btn = $("btn-back-to-top");
    if (!btn) return;
    function checkScroll() {
      if (window.scrollY > 320) {
        btn.hidden = false;
      } else {
        btn.hidden = true;
      }
    }
    window.addEventListener("scroll", checkScroll, { passive: true });
    btn.addEventListener("click", function () {
      window.scrollTo({ top: 0, behavior: "smooth" });
      const main = $("main-content") || $("veredicto");
      if (main) main.focus();
    });
    checkScroll();
  }

  function init() {
    I.init();
    const params = new URLSearchParams(window.location.search);
    if (params.get("lang") && I.SUPPORTED.indexOf(params.get("lang")) >= 0) I.setLang(params.get("lang"));
    $("lang-select").value = I.getLang();
    I.apply(document);
    const wanted = (params.get("caso") || "A").toUpperCase();
    if (DEMO[wanted]) {
      state.datasetKey = wanted;
      $("dataset-select").value = wanted;
    }
    setupTheme();
    setupInfo();
    setupGraphControls();
    setupControls();
    setupSeal();
    setupSpeech();
    setupExport();
    setupVoting();
    setupSectionNav();
    setupPhase();
    setupSimulator();
    setupEscaleta();
    setupBackToTop();
    const fase = params.get("fase");
    setFase(["preproduccion", "edicion", "publicado"].indexOf(fase) >= 0 ? fase : "publicado", { silent: true });
  }

  document.addEventListener("DOMContentLoaded", init);
})();
