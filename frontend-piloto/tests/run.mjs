// SPDX-FileCopyrightText: 2026 Equipo 1: Attention Is All She Needs (Alba Camiña García, Pilar de la Fuente Diez, Rocío Jiménez Villén)
// SPDX-License-Identifier: Apache-2.0

/** Tests of the API adapter, no dependencies: `node frontend-piloto/tests/run.mjs` */
import { createRequire } from "node:module";
import assert from "node:assert/strict";

const require = createRequire(import.meta.url);
const A = require("../js/adapter.js");

let failed = 0;
function test(name, fn) {
  try {
    fn();
    console.log("  ok  " + name);
  } catch (e) {
    failed++;
    console.error("FAIL  " + name + "\n      " + e.message);
  }
}

// Synthetic result with the shape of GET /videos/{id} (aiasn/api/schemas.py); no real people
const PAYLOAD = {
  video_id: "mesa-1a2b",
  status: { estado: "ok", pasos: {}, error: null },
  resultado: {
    veredicto: {
      resumen_lectura_facil: "Lectura Facil (UNE 153101): INFRARREPRESENTACION: Las mujeres hablan poco. Tiempo de voz de mujeres: 25.0%.",
      alerta_equality_washing: false, motivo_alerta: "",
      alerta_infrarrepresentacion: true, motivo_infrarrepresentacion: "Por debajo del 40 %.",
      bechdel: { estado: "no_supera", motivo: "una_mujer", puntuacion_0_3: null, diagnostico: "una_mujer",
                 reglas: { regla_1_pluralidad_femenina: null } },
      salvaguarda_paridad: { cumple: false, cuota_femenina: 0.25, suelo_femenino_exigido: 0.4 },
      valoracion_ciudadana: null
    },
    metricas: {
      voz_pct: { mujer: 25.0, hombre: 75.0, no_binario: 0.0, no_determinado: 0.0 },
      pantalla_pct: { mujer: 40.0, hombre: 50.0, no_binario: 0.0 },
      sin_determinar_pct: { voz: 0.0, pantalla: 10.0 },
      ratio_voz_pantalla: { mujer: 0.42, hombre: 0.9, no_binario: null, no_determinado: 0.0 },
      referentes: { hombre: 2 }
    },
    personas: [
      { id: "p1", nombre: "Ana Pérez", cargo: "Investigadora", genero: "mujer", rol: "experto/a", autoridad: true, pantalla_s: 40, voz_s: 25,
        area: 0.3, centralidad: 0.8, cargo_en: "researcher", sesgo_cargo: 0.09 },
      { id: "p2", nombre: null, cargo: null, genero: "hombre", rol: "presentador/a", autoridad: true, pantalla_s: 50, voz_s: 75 },
      { id: "p3", nombre: null, cargo: null, genero: "no_determinado", rol: null, autoridad: null, pantalla_s: 10, voz_s: 0 }
    ],
    temas: [
      { tema: "cuidados", clave: "care", genero: "mujer", personas: 2, pct: 66.7, sesgo: 0.1 },
      { tema: "tecnología", clave: "technology", genero: "mujer", personas: 1, pct: 33.3, sesgo: 0.0 },
      { tema: "tecnología", clave: "technology", genero: "hombre", personas: 3, pct: 100.0, sesgo: 0.0 }
    ],
    poder: { centralidad_media: { mujer: 0.8, hombre: 0.6, no_binario: null }, area_media: { mujer: 0.3, hombre: 0.2 },
             personas_distintas: { mujer: 1, hombre: 1, no_determinado: 1 }, veces_citado_como_referente: { hombre: 2 },
             referentes: [{ nombre: "Alan Turing", genero: "hombre", veces: 2, citado_por: ["Ana Pérez"] }] },
    roles: [{ rol: "experto/a", genero: "mujer", voz_s: 25 }, { rol: "presentador/a", genero: "hombre", voz_s: 75 }],
    clima: { mujer: { "colaborativo": 50.0, "técnico/asertivo": 50.0 }, hombre: { "disenso": 100.0 } },
    autoridad: { voz_con_autoridad_pct: { mujer: 100.0, hombre: 81.5 }, presentacion_con_cargo_pct: {},
                 ideas: { total: 5, solo_pct: { mujer: 40.0, hombre: 40.0 }, compartidas_pct: 20.0 } },
    constelacion: {
      nodos: [
        { id: "p1", tipo: "participante", label: "Ana Pérez" }, { id: "p2", tipo: "participante", label: "Persona 2" },
        { id: "p3", tipo: "participante", label: "Persona 3" },
        { id: "tema:care", tipo: "tema", label: "cuidados" }, { id: "tema:technology", tipo: "tema", label: "tecnología" }
      ],
      aristas: [
        { source: "p1", target: "tema:care", tipo: "habla_de", peso: 2 },
        { source: "p1", target: "tema:technology", tipo: "habla_de", peso: 1 },
        { source: "p2", target: "tema:technology", tipo: "habla_de", peso: 3 },
        { source: "p1", target: "p2", tipo: "turno", peso: 1 },
        { source: "p1", target: "p2", tipo: "comparte_plano", peso: 12.5 }
      ]
    },
    kpis: [],
    segmentos_dudosos: [{ inicio: 100.5, fin: 109.4, segundos: 3.1, cuadrante: 2, tipo: "Presencia muda en pantalla",
                          genero: "no_determinado", persona: "p3", texto: null },
                        { inicio: 110, fin: 112, segundos: 2, cuadrante: 2, tipo: "Presencia muda en pantalla",
                          genero: "no_determinado", persona: "p3", texto: null }]
  }
};

const v = A.toView(PAYLOAD);

test("people: gender, names from the graph when unnamed, shares of screen and voice", () => {
  assert.deepEqual(v.people.map((p) => [p.id, p.g, p.name]), [["p1", "f", "Ana Pérez"], ["p2", "m", "Persona 2"], ["p3", "u", "Persona 3"]]);
  assert.deepEqual(v.people.map((p) => [p.screen, p.voice]), [[40, 25], [50, 75], [10, 0]]);
  assert.equal(v.people[0].role, "experto/a");
  assert.equal(v.people[2].role, "Sin identificar");
});

test("star size is the voice time relative to the person who speaks most", () => {
  assert.deepEqual(v.people.map((p) => Math.round(p.protag * 100)), [33, 100, 0]);
});

test("only people with a name or voice are labelled in the sky", () => {
  assert.deepEqual(v.people.map((p) => p.labeled), [true, true, false]);
});

test("topics come from the 'habla_de' edges, labelled in Spanish", () => {
  assert.deepEqual(v.people[0].topics, ["cuidados", "tecnología"]);
  assert.deepEqual(Object.keys(v.topics).sort(), ["cuidados", "tecnología"]);
  assert.deepEqual(v.edges, [["p1", "cuidados"], ["p1", "tecnología"], ["p2", "tecnología"]]);
});

test("layout keeps stars inside the sky and apart, by their size, in pixels", () => {
  const W = 660, H = 470, r = (p) => 7 + p.protag * 17;
  // a crowded sky: 16 people, as in a real video, plus the ones of the payload
  const many = JSON.parse(JSON.stringify(PAYLOAD));
  for (let i = 4; i < 20; i++) many.resultado.personas.push({ id: `p${i}`, genero: "hombre", pantalla_s: 3, voz_s: 0 });
  for (const view of [v, A.toView(many)]) {
    for (const p of view.people) assert.ok(p.nx > 0 && p.nx < 1 && p.ny > 0 && p.ny < 1);
    for (let i = 0; i < view.people.length; i++)
      for (let j = i + 1; j < view.people.length; j++) {
        const a = view.people[i], b = view.people[j];
        assert.ok(Math.hypot((a.nx - b.nx) * W, (a.ny - b.ny) * H) >= r(a) + r(b) + 20, `${a.id} and ${b.id} overlap`);
      }
  }
});

test("people seen together on screen", () => {
  assert.deepEqual(v.shared, [["p1", "p2", 12.5]]);
});

test("themes by gender, most female-leaning first", () => {
  assert.deepEqual(v.themes, [{ t: "cuidados", f: 66.7, m: 0, sesgo: 0.1 }, { t: "tecnología", f: 33.3, m: 100, sesgo: 0 }]);
});

test("verdict figures are the API ones, none computed here", () => {
  assert.deepEqual([v.screen, v.voice, v.ratio], [{ f: 40, m: 50 }, { f: 25, m: 75 }, 0.42]);
  assert.deepEqual(v.refs, { f: 0, m: 2 });
  assert.deepEqual(v.parity, { ok: false, cuota: 0.25, suelo: 0.4 });
  assert.deepEqual(v.underrep, { on: true, text: "Por debajo del 40 %." });
  assert.deepEqual(v.coverage, { voz: 0, pantalla: 10 });
  assert.deepEqual([v.tif.estado, v.tif.motivo, v.tif.puntuacion], ["no_supera", "una_mujer", null]);
  assert.equal(v.washing.on, false);
  assert.equal(v.index, null);   // the index is not in the API yet: the page shows it as pending
});

test("easy read: the API summary, one sentence per item", () => {
  assert.deepEqual(v.easy, ["INFRARREPRESENTACION: Las mujeres hablan poco.", "Tiempo de voz de mujeres: 25.0%."]);
});

test("themes nobody of known gender talks about are left out", () => {
  const p = JSON.parse(JSON.stringify(PAYLOAD));
  p.resultado.temas.push({ tema: "política", clave: "politics", genero: "no_determinado", turnos: 1, pct: 100, sesgo: null });
  assert.deepEqual(A.toView(p).themes.map((t) => t.t), ["cuidados", "tecnología"]);
});

test("power, roles and climate", () => {
  assert.deepEqual(v.power, { distinct: { f: 1, m: 1 }, central: { f: 0.8, m: 0.6 }, area: { f: 0.3, m: 0.2 },
                             cited: { f: 0, m: 2 }, references: [{ name: "Alan Turing", g: "m", times: 2, by: ["Ana Pérez"] }] });
  assert.deepEqual([v.people[0].area, v.people[0].centralidad, v.people[1].area], [0.3, 0.8, null]);
  assert.deepEqual([v.people[0].cargoEn, v.people[0].sesgoCargo, v.people[1].sesgoCargo], ["researcher", 0.09, null]);
  assert.deepEqual(v.roles.map((r) => r.rol), ["presentador/a", "experto/a"]);
  assert.equal(v.undetermined, 1);
  assert.deepEqual(v.expertVoice, { f: 25, m: 0 });
  assert.equal(v.experts, true);
  assert.deepEqual(v.authority, { voice: { f: 100, m: 81.5 }, title: { f: null, m: null } });
  assert.deepEqual(v.ideas, { total: 5, f: 40, m: 40, u: null, shared: 20 });
  assert.deepEqual(v.clima, { f: { tec: 50, col: 50, dis: 0 }, m: { tec: 0, col: 0, dis: 100 } });
});

test("spans to review grouped by person, with the name the graph gives them", () => {
  assert.deepEqual(v.doubtful.map((d) => [d.persona, d.spans, d.segundos]), [["Persona 3", [[100.5, 109.4], [110, 112]], 5.1]]);
});

test("an empty or partial result does not break the page", () => {
  const e = A.toView({ video_id: "x", resultado: {} });
  assert.deepEqual([e.people, e.themes, e.easy, e.roles], [[], [], [], []]);
  assert.equal(e.ratio, null);
  assert.equal(e.expertVoice, null);
  assert.equal(e.tif, null);   // an old result without the TIF state: the line is not shown
  assert.deepEqual(e.doubtful, []);
});

console.log(failed ? `\n${failed} pruebas fallidas` : "\nTodas las pruebas correctas");
process.exitCode = failed ? 1 : 0;
