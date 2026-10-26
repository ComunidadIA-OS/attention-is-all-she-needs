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
    assume: false,
    anonymized: false,
    view: null,
    network: null,
    votes: { yes: 0, partial: 0, no: 0 },
    voted: false,
    hashToken: 0,
    focusAfterRender: null
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

  function buildEdgesFromCase(caso) {
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
    (caso.planos_compartidos || []).forEach(function (e) {
      edges.push({ from: e[0], to: e[1], tipo: "comparte_plano", peso: e[2] });
    });
    (caso.menciones || []).forEach(function (e) {
      edges.push({ from: e[0], to: e[1], tipo: "menciona", peso: e[2] });
    });
    (caso.habla_de || []).forEach(function (e) {
      edges.push({ from: e[0], to: e[1], tipo: "habla_de", peso: e[2] });
    });
    return edges;
  }

  function buildDemoView() {
    const caso = DEMO[state.datasetKey];
    const ev = M.evaluar(caso, state.decisiones);
    const nodes = ev.personas.map(function (p) {
      return { id: p.id, tipo: "participante", persona: p };
    });
    caso.temas.forEach(function (tm) {
      nodes.push({ id: tm.id, tipo: "tema", label: tm.label });
    });
    return {
      origin: "client",
      video_id: caso.video_id,
      status: caso.status,
      personas: ev.personas,
      metricas: ev.metricas,
      alertas: ev.alertas,
      salvaguarda: ev.salvaguarda,
      bechdel: ev.bechdel,
      indice: ev.indice_global,
      diagnostico: ev.diagnostico,
      nodes: nodes,
      edges: buildEdgesFromCase(caso),
      clima: caso.clima,
      segmentos: caso.segmentos_dudosos || [],
      canArbitrate: true,
      citizenApi: null,
      apiEasy: null
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
    const bechdel = {
      puntuacion_bechdel_0_3: Number(bd.puntuacion_bechdel_0_3 !== undefined ? bd.puntuacion_bechdel_0_3 : bd.puntuacion_0_3) || 0,
      regla_1_pluralidad_femenina: bd.regla_1_pluralidad_femenina,
      regla_2_identidad_propia: bd.regla_2_identidad_propia,
      regla_3_dialogo_horizontal: bd.regla_3_dialogo_horizontal,
      mujeres_distintas_hablando: bd.mujeres_distintas_hablando,
      mujeres_con_rotulo_identificado: bd.mujeres_con_rotulo_identificado,
      transiciones_mujer_a_mujer: bd.transiciones_mujer_a_mujer,
      diagnostico_bechdel: null,
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
          h("span", { class: "check-body" }, h("span", { class: "check-label", text: it.label }), it.detail ? h("span", { class: "check-detail", text: it.detail }) : null),
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
    lines.push(t(view.bechdel.puntuacion_bechdel_0_3 === 3 ? "easy.bechdel.ok" : "easy.bechdel.no"));
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
    $("rvp-text").textContent = t("metrics.rvp_text");

    const b = view.bechdel;
    $("bechdel-score").textContent = String(b.puntuacion_bechdel_0_3);
    const rules = [];
    if (typeof b.regla_1_pluralidad_femenina === "boolean") {
      rules.push({ ok: b.regla_1_pluralidad_femenina, label: t("bechdel.r1"), detail: t("bechdel.count", { n: b.mujeres_distintas_hablando }) });
      rules.push({ ok: b.regla_2_identidad_propia, label: t("bechdel.r2"), detail: t("bechdel.count", { n: b.mujeres_con_rotulo_identificado }) });
      rules.push({ ok: b.regla_3_dialogo_horizontal, label: t("bechdel.r3"), detail: t("bechdel.count", { n: b.transiciones_mujer_a_mujer }) });
    }
    renderChecks($("bechdel-rules"), rules, "good");
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
      n: cssVar("--c-nd", "#64748b"),
      t: cssVar("--c-topic", "#b45309"),
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
        shape = g === "mujer" ? "dot" : g === "hombre" ? "square" : "triangle";
        color = g === "mujer" ? colors.f : g === "hombre" ? colors.m : colors.n;
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
  }

  function setupGraphControls() {
    const container = $("constellation-network");
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

  function addLog(text) {
    state.log.push({ at: new Date(), text: text });
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

      if (!dec) {
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
          decide(seg, { accion: "validar", genero: select.value }, "validate:" + seg.persona_id);
        });
        bA.addEventListener("click", function () {
          decide(seg, { accion: "abstener" }, "abstain:" + seg.persona_id);
        });
        card.appendChild(h("div", { class: "arb-actions" }, h("label", { for: selId, class: "arb-label", text: t("hitl.classify_as") }), select, bV, bA));
      } else {
        const stateTxt = dec.accion === "validar" ? t("hitl.state.validated", { g: genderLabel(dec.genero, true) }) : t("hitl.state.abstained");
        const undo = h("button", { type: "button", class: "btn btn-sm", text: t("hitl.undo"), "data-focus": "undo:" + seg.persona_id });
        undo.addEventListener("click", function () {
          delete state.decisiones[seg.persona_id];
          addLog(t("log.undo", { who: displayName(base) }));
          state.focusAfterRender = "decide:" + seg.persona_id;
          refresh(true);
        });
        card.appendChild(h("div", { class: "arb-actions" }, h("span", { class: "pill pill-ok" }, icon("i-ok"), stateTxt), undo));
      }
      list.appendChild(card);
    });

    renderSeal(view, pend);
  }

  function decide(seg, decision, focusKey) {
    const view = state.view;
    const base = personaById(view, seg.persona_id) || { id: seg.persona_id, nombre: seg.persona_id };
    state.decisiones[seg.persona_id] = decision;
    if (decision.accion === "validar") {
      addLog(t("log.validate", { who: displayName(base), g: genderLabel(decision.genero, true), p: fmt(seg.p * 100, 0) }));
    } else {
      addLog(t("log.abstain", { who: displayName(base) }));
    }
    state.focusAfterRender = "undo:" + seg.persona_id;
    refresh(true);
  }

  function renderSeal(view, pend) {
    const assume = $("assume-toggle");
    if (pend > 0 && state.assume) {
      state.assume = false;
      addLog(t("log.assume_off"));
    }
    assume.disabled = pend > 0;
    assume.checked = state.assume;
    $("assume-help").textContent = pend > 0 ? t("hitl.assume_blocked") : t("hitl.sign_note");

    const sealed = pend === 0 && state.assume;
    setPill($("seal-pill"), sealed ? "ok" : "warn", sealed ? t("seal.ok") : t("seal.draft"), sealed ? "i-ok" : "i-pending");
    $("seal-text").textContent = pend > 0 ? t("seal.text.pending", { n: pend }) : sealed ? t("seal.text.ok") : t("seal.text.need_assume");

    const log = $("decision-log");
    clear(log);
    if (!state.log.length) {
      log.appendChild(h("li", { class: "empty", text: t("hitl.log_empty") }));
    } else {
      state.log.forEach(function (e) {
        log.appendChild(h("li", null, h("time", { text: e.at.toLocaleTimeString(I.getLang()) + " " }), e.text));
      });
    }
    updateHash(view, sealed);
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
    ["tecnico_asertivo", "colaborativo", "disenso"].forEach(function (k) {
      tbody.appendChild(
        h("tr", null,
          h("th", { scope: "row", text: t("climate." + k) }),
          h("td", { class: "num", text: fmt(view.clima.mujer[k], 0) + " %" }),
          h("td", { class: "num", text: fmt(view.clima.hombre[k], 0) + " %" })
        )
      );
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

  function renderChrome(view) {
    $("video-id-badge").textContent = view.video_id;
    const originKey = view.origin === "client" ? "origin.client" : view.origin === "api" ? "origin.api" : "origin.mixed";
    setPill($("calc-origin-badge"), view.origin === "client" ? "warn" : "neutral", t(originKey));
    $("synthetic-note").hidden = state.datasetKey === "live";
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

    if (state.focusAfterRender) {
      const key = state.focusAfterRender;
      state.focusAfterRender = null;
      let target = document.querySelector('[data-focus="' + key + '"]');
      if (!target) {
        const id = key.split(":")[1];
        target = document.getElementById("arb-sel-" + id) || $("assume-toggle");
      }
      if (target && !target.disabled) target.focus();
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
      u.lang = { es: "es-ES", ca: "ca-ES", en: "en-GB" }[I.getLang()] || "es-ES";
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
      const data = dictamen(view, pend === 0 && state.assume);
      data.generado_en = new Date().toISOString();
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
          state.decisiones = {};
          state.log = [];
          state.assume = false;
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

  function setDataset(key) {
    state.datasetKey = key;
    state.decisiones = {};
    state.log = [];
    state.assume = false;
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
    $("assume-toggle").addEventListener("change", function (e) {
      state.assume = e.target.checked;
      addLog(t(state.assume ? "log.assume_on" : "log.assume_off"));
      refresh(true);
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
    setupSpeech();
    setupExport();
    setupVoting();
    setupSectionNav();
    refresh(false);
  }

  document.addEventListener("DOMContentLoaded", init);
})();
