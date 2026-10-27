// SPDX-FileCopyrightText: 2026 Equipo 1: Attention Is All She Needs (Alba Camiña García, Pilar de la Fuente Diez, Rocío Jiménez Villén)
// SPDX-License-Identifier: Apache-2.0

/**
 * From the API result (GET /videos/{id}) to what the page draws. Pure functions, no DOM.
 * Only reshapes: every KPI comes from the backend (ADR-0001); what the API does not give yet stays null and the page
 * shows it as pending. Shares of one person's seconds over everyone's are presentation, like the original mock-up.
 */
(function (root, factory) {
  if (typeof module === "object" && module.exports) module.exports = factory();
  else root.AIASNAdapter = factory();
})(typeof self !== "undefined" ? self : this, function () {
  "use strict";

  const G = { mujer: "f", hombre: "m", no_binario: "n" };
  const ROLE_ORDER = ["presentador/a", "moderador/a", "entrevistador/a", "experto/a", "testimonio", "narrador/a en off"];

  const num = (x) => (typeof x === "number" && isFinite(x) ? x : null);
  const round1 = (x) => Math.round(x * 10) / 10;
  const gcode = (genero) => G[genero] || "u";

  /** Topics in the middle on an ellipse, each person towards the topics they talk about, then pushed apart. */
  function layout(people, topicKeys) {
    const topics = {};
    topicKeys.forEach((k, i) => {
      const a = (2 * Math.PI * i) / Math.max(1, topicKeys.length) - Math.PI / 2;
      topics[k] = topicKeys.length === 1 ? [0.5, 0.48] : [0.5 + 0.2 * Math.cos(a), 0.48 + 0.22 * Math.sin(a)];
    });
    const loose = people.filter((p) => !p.topics.length);
    people.forEach((p) => {
      let a;
      if (p.topics.length) {
        const sx = p.topics.reduce((s, t) => s + topics[t][0] - 0.5, 0);
        const sy = p.topics.reduce((s, t) => s + topics[t][1] - 0.48, 0);
        a = sx === 0 && sy === 0 ? 0 : Math.atan2(sy, sx);
      } else {
        a = (2 * Math.PI * loose.indexOf(p)) / Math.max(1, loose.length) + Math.PI / 7;
      }
      const r = p.topics.length ? 0.34 : 0.42;
      p.nx = 0.5 + r * Math.cos(a);
      p.ny = 0.48 + r * 0.9 * Math.sin(a);
    });
    for (let it = 0; it < 80; it++) {   // keep stars and their labels from overlapping
      for (let i = 0; i < people.length; i++) {
        for (let j = i + 1; j < people.length; j++) {
          const a = people[i], b = people[j];
          let dx = b.nx - a.nx, dy = b.ny - a.ny;
          const d = Math.hypot(dx, dy), min = 0.11;
          if (d < min) {
            if (d === 0) { dx = Math.cos(i + j); dy = Math.sin(i + j); }
            const k = (min - d) / 2 / (d || 1);
            a.nx -= dx * k; a.ny -= dy * k; b.nx += dx * k; b.ny += dy * k;
          }
        }
      }
      people.forEach((p) => {
        p.nx = Math.min(0.92, Math.max(0.08, p.nx));
        p.ny = Math.min(0.8, Math.max(0.1, p.ny));
      });
    }
    return topics;
  }

  function byGender(obj) {
    const o = obj || {};
    return { f: num(o.mujer), m: num(o.hombre) };
  }

  /** The easy-read summary of the API, one sentence per item, without its "Lectura Facil (UNE 153101):" label. */
  function easySentences(text) {
    if (!text) return [];
    return String(text).replace(/^\s*Lectura F[aá]cil[^:]*:\s*/i, "").split(/(?<=\.)\s+/).map((s) => s.trim()).filter(Boolean);
  }

  /** The spans of undetermined gender grouped by person, for the human review: one decision per person. */
  function doubtfulPeople(spans, labelOf) {
    const by = new Map();
    spans.forEach((s) => {
      const id = s.persona || "?";
      const p = by.get(id) || { id: id, persona: labelOf[id] || s.persona || "Sin identificar", segundos: 0, spans: [], textos: [] };
      p.segundos += num(s.segundos) || 0;
      p.spans.push([num(s.inicio) || 0, num(s.fin) || 0]);
      if (s.texto) p.textos.push(s.texto);
      by.set(id, p);
    });
    return Array.from(by.values()).map((p) => Object.assign(p, { segundos: round1(p.segundos) }));
  }

  function toView(payload) {
    const r = (payload && payload.resultado) || {};
    const v = r.veredicto || {};
    const mt = r.metricas || {};
    const pw = r.poder || {};
    const nodes = (r.constelacion && r.constelacion.nodos) || [];
    const edges = (r.constelacion && r.constelacion.aristas) || [];
    const labelOf = {};
    nodes.forEach((n) => { labelOf[n.id] = n.label; });

    const personas = r.personas || [];
    const totScreen = personas.reduce((s, p) => s + (num(p.pantalla_s) || 0), 0);
    const totVoice = personas.reduce((s, p) => s + (num(p.voz_s) || 0), 0);
    const maxVoice = personas.reduce((s, p) => Math.max(s, num(p.voz_s) || 0), 0);

    const talks = {};
    edges.filter((e) => e.tipo === "habla_de").forEach((e) => {
      (talks[e.source] = talks[e.source] || []).push(labelOf[e.target] || e.target);
    });
    const people = personas.map((p) => {
      const voz = num(p.voz_s) || 0, pant = num(p.pantalla_s) || 0;
      return {
        id: p.id,
        name: p.nombre || labelOf[p.id] || p.id,
        named: Boolean(p.nombre),
        role: p.rol || (p.genero === "no_determinado" ? "Sin identificar" : "Sin rol asignado"),
        g: gcode(p.genero),
        protag: maxVoice ? voz / maxVoice : 0,   // star size: voice time until the backend gives prominence
        screen: totScreen ? round1((pant / totScreen) * 100) : 0,
        voice: totVoice ? round1((voz / totVoice) * 100) : 0,
        topics: Array.from(new Set(talks[p.id] || [])),
        note: p.cargo || "",
        area: num(p.area), centralidad: num(p.centralidad),
        cargoEn: p.cargo_en || null, sesgoCargo: num(p.sesgo_cargo),
        labeled: Boolean(p.nombre) || voz > 0
      };
    });
    const topicKeys = Array.from(new Set(people.flatMap((p) => p.topics)));
    const topics = layout(people, topicKeys);

    const themes = {};
    (r.temas || []).forEach((t) => {
      const th = (themes[t.tema] = themes[t.tema] || { t: t.tema, f: 0, m: 0, sesgo: num(t.sesgo) });
      if (t.genero === "mujer") th.f = num(t.pct) || 0;
      if (t.genero === "hombre") th.m = num(t.pct) || 0;
    });

    const screen = byGender(mt.pantalla_pct), voice = byGender(mt.voz_pct);
    const refs = mt.referentes || {};
    const sp = v.salvaguarda_paridad || {};

    const roles = {};
    people.filter((p) => personas.find((x) => x.id === p.id).rol).forEach((p) => {
      (roles[p.role] = roles[p.role] || []).push({ name: p.name, g: p.g });
    });
    const roleList = Object.keys(roles)
      .sort((a, b) => (ROLE_ORDER.indexOf(a) + 1 || 99) - (ROLE_ORDER.indexOf(b) + 1 || 99))
      .map((rol) => ({ rol: rol, people: roles[rol] }));
    const experts = {};
    (r.roles || []).filter((x) => x.rol === "experto/a").forEach((x) => { experts[gcode(x.genero)] = num(x.voz_s) || 0; });

    function tone(g) {
      const c = (r.clima || {})[g];
      if (!c) return null;
      return { tec: num(c["técnico/asertivo"]) || 0, col: num(c.colaborativo) || 0, dis: num(c.disenso) || 0 };
    }

    return {
      videoId: payload && payload.video_id,
      people: people,
      topics: topics,
      edges: people.flatMap((p) => p.topics.map((t) => [p.id, t])),
      themes: Object.values(themes).filter((t) => t.f || t.m).sort((a, b) => (b.f - b.m) - (a.f - a.m)),
      screen: screen,
      voice: voice,
      ratio: num((mt.ratio_voz_pantalla || {}).mujer),
      refs: { f: refs.mujer || 0, m: refs.hombre || 0 },
      washing: { on: Boolean(v.alerta_equality_washing), text: v.motivo_alerta || "" },
      underrep: { on: Boolean(v.alerta_infrarrepresentacion), text: v.motivo_infrarrepresentacion || "" },
      parity: { ok: sp.cumple === true, cuota: num(sp.cuota_femenina), suelo: num(sp.suelo_femenino_exigido) },
      coverage: { voz: num((mt.sin_determinar_pct || {}).voz), pantalla: num((mt.sin_determinar_pct || {}).pantalla) },
      tif: v.bechdel && v.bechdel.estado ? {
        estado: v.bechdel.estado, motivo: v.bechdel.motivo || null, diagnostico: v.bechdel.diagnostico || null,
        puntuacion: num(v.bechdel.puntuacion_0_3), reglas: v.bechdel.reglas || {}
      } : null,
      index: num(v.indice_global),   // not computed by the backend yet
      easy: easySentences(v.resumen_lectura_facil),
      power: {
        distinct: { f: (pw.personas_distintas || {}).mujer || 0, m: (pw.personas_distintas || {}).hombre || 0 },
        central: byGender(pw.centralidad_media),
        area: byGender(pw.area_media),
        cited: { f: (pw.veces_citado_como_referente || {}).mujer || 0, m: (pw.veces_citado_como_referente || {}).hombre || 0 }
      },
      roles: roleList,
      undetermined: people.filter((p) => p.g === "u").length,
      experts: (r.roles || []).some((x) => x.rol === "experto/a"),
      expertVoice: totVoice && (experts.f !== undefined || experts.m !== undefined)
        ? { f: round1(((experts.f || 0) / totVoice) * 100), m: round1(((experts.m || 0) / totVoice) * 100) }
        : null,
      clima: { f: tone("mujer"), m: tone("hombre") },
      doubtful: doubtfulPeople(r.segmentos_dudosos || [], labelOf),
      authority: {   // shares within each gender, as the API gives them
        voice: byGender((r.autoridad || {}).voz_con_autoridad_pct),
        title: byGender((r.autoridad || {}).presentacion_con_cargo_pct)
      },
      // key ideas in groups that add up to 100, as the API gives them
      ideas: (() => {
        const i = (r.autoridad || {}).ideas || {}, solo = i.solo_pct || {};
        return { total: i.total || 0, f: num(solo.mujer), m: num(solo.hombre), u: num(solo.no_determinado),
                 shared: num(i.compartidas_pct) };
      })()
    };
  }

  return { toView: toView, layout: layout, easySentences: easySentences };
});
