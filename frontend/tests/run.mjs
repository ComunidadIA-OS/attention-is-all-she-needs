// SPDX-FileCopyrightText: 2026 Equipo 1: Attention Is All She Needs (Alba Camiña García, Pilar de la Fuente Diez, Rocío Jiménez Villén)
// SPDX-License-Identifier: Apache-2.0

/**
 * Pruebas del frontend sin dependencias: `node frontend/tests/run.mjs`
 *  1. Lógica de métricas (réplica de la spec 21): alertas, Bechdel, salvaguarda, índice, arbitraje HitL.
 *  2. Diccionarios i18n completos y coherentes con el HTML y con app.js.
 */
import { createRequire } from "node:module";
import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import assert from "node:assert/strict";

const require = createRequire(import.meta.url);
const root = join(dirname(fileURLToPath(import.meta.url)), "..");
const M = require(join(root, "js", "metrics.js"));
const DEMO = require(join(root, "js", "demo-data.js"));
const I18N = require(join(root, "js", "i18n.js"));

let passed = 0;
function test(name, fn) {
  try {
    fn();
    passed++;
    console.log("  ok  " + name);
  } catch (e) {
    console.error("FAIL  " + name + "\n      " + e.message);
    process.exitCode = 1;
  }
}
const near = (a, b, eps = 0.06) => assert.ok(Math.abs(a - b) <= eps, `${a} no está cerca de ${b}`);

console.log("Métricas (spec 21)");

test("Muestra A reproduce el caso A de la spec: 26,8 % pantalla, 19,0 % voz, RVP 0,71", () => {
  const r = M.evaluar(DEMO.A, {});
  near(r.metricas.pantalla_pct.mujer, 26.8, 0.1);
  near(r.metricas.voz_pct.mujer, 19.0, 0.1);
  near(r.metricas.ratio_voz_pantalla.mujer, 0.71, 0.01);
});

test("Muestra A: infrarrepresentación activa y equality-washing inactivo", () => {
  const r = M.evaluar(DEMO.A, {});
  assert.equal(r.alertas.infrarrepresentacion.activa, true);
  assert.equal(r.alertas.equality_washing.activa, false);
  assert.equal(r.diagnostico, "infra");
});

test("Muestra A: con una sola mujer el Test de Bechdel no se aplica (no puntúa)", () => {
  const r = M.evaluar(DEMO.A, {});
  assert.equal(r.bechdel.aplica, false);
  assert.equal(r.bechdel.diagnostico_bechdel, "no_aplica_una_mujer");
  assert.equal(r.bechdel.puntuacion_bechdel_0_3, null);
  assert.equal(r.bechdel.supera_bechdel_digital, false);
});

test("Muestra A: si se valida como mujer a la persona sin determinar, el test se aplica y detecta Efecto Token", () => {
  const r = M.evaluar(DEMO.A, { t7: { accion: "validar", genero: "mujer" } });
  assert.equal(r.bechdel.aplica, true);
  assert.equal(r.bechdel.mujeres_presentes, 2);
  assert.equal(r.bechdel.diagnostico_bechdel, "efecto_token");
  assert.equal(r.bechdel.puntuacion_bechdel_0_3, 0);
});

test("Bechdel: no se aplica sin hombres ni sin mujeres", () => {
  const f = (id) => ({ id, genero: "mujer", voz_s: 10, pantalla_s: 10, rotulo: true });
  assert.equal(M.bechdel([f("a"), f("b")], ["a", "b"]).diagnostico_bechdel, "no_aplica_sin_hombres");
  assert.equal(M.bechdel([{ id: "h", genero: "hombre", voz_s: 5 }], []).diagnostico_bechdel, "no_aplica_sin_mujeres");
});

test("Muestra A: la salvaguarda NO cumple con 19 % de voz femenina", () => {
  const r = M.evaluar(DEMO.A, {});
  assert.equal(r.salvaguarda.cumple_salvaguarda_paridad, false);
});

test("Muestra B (diversidad): 15 % voz no binaria, salvaguarda en Fase 1 con techo masculino al 45 %", () => {
  const r = M.evaluar(DEMO.B, {});
  near(r.metricas.pantalla_pct.mujer, 33.3, 0.1);
  near(r.metricas.voz_pct.mujer, 40.0, 0.1);
  near(r.metricas.voz_pct.no_binario, 15.0, 0.1);
  near(r.metricas.voz_pct.hombre, 45.0, 0.1);
  assert.equal(r.salvaguarda.cumple_salvaguarda_paridad, true);
  assert.equal(r.salvaguarda.regimen_aplicado, "FASE_1_ABSORCION_TECHO_MASCULINO");
});

test("Muestra C reproduce el caso C (antigua B): 45 % pantalla, 12 % voz, RVP 0,27 → equality-washing", () => {
  const r = M.evaluar(DEMO.C, {});
  near(r.metricas.pantalla_pct.mujer, 45.0, 0.1);
  near(r.metricas.voz_pct.mujer, 12.0, 0.1);
  near(r.metricas.ratio_voz_pantalla.mujer, 0.27, 0.01);
  assert.equal(r.alertas.equality_washing.activa, true);
  assert.equal(r.alertas.infrarrepresentacion.activa, false);
  assert.equal(r.diagnostico, "washing");
});

test("Muestra C: Bechdel = Aislamiento relacional (2 mujeres, ninguna transición M→M)", () => {
  const r = M.evaluar(DEMO.C, {});
  assert.equal(r.bechdel.mujeres_distintas_hablando, 2);
  assert.equal(r.bechdel.transiciones_mujer_a_mujer, 0);
  assert.equal(r.bechdel.diagnostico_bechdel, "aislamiento_relacional");
});

test("Muestra D reproduce el caso D (antigua C): 42 % / 44 %, RVP 1,05 → paridad efectiva y Bechdel 3/3", () => {
  const r = M.evaluar(DEMO.D, {});
  near(r.metricas.pantalla_pct.mujer, 42.0, 0.1);
  near(r.metricas.voz_pct.mujer, 44.0, 0.1);
  near(r.metricas.ratio_voz_pantalla.mujer, 1.05, 0.01);
  assert.equal(r.alertas.equality_washing.activa, false);
  assert.equal(r.alertas.infrarrepresentacion.activa, false);
  assert.equal(r.salvaguarda.cumple_salvaguarda_paridad, true);
  assert.equal(r.bechdel.puntuacion_bechdel_0_3, 3);
  assert.equal(r.diagnostico, "ok");
});

test("El índice global está en 0–100 y D puntúa más que C y A", () => {
  const a = M.evaluar(DEMO.A, {}).indice_global.total;
  const b = M.evaluar(DEMO.B, {}).indice_global.total;
  const c = M.evaluar(DEMO.C, {}).indice_global.total;
  const d = M.evaluar(DEMO.D, {}).indice_global.total;
  [a, b, c, d].forEach((x) => assert.ok(x >= 0 && x <= 100));
  assert.ok(d > a && d > c, `A=${a} B=${b} C=${c} D=${d}`);
});

test("Las ponderaciones del índice suman 1", () => {
  const s = Object.values(M.WEIGHTS).reduce((x, y) => x + y, 0);
  near(s, 1, 1e-9);
});

console.log("Supervisión humana (ADR-0005)");

test("Sin decisiones, los tramos dudosos quedan fuera del denominador", () => {
  const r = M.evaluar(DEMO.A, {});
  assert.equal(r.metricas.voz_pct.no_determinado_s, 40);
  assert.equal(r.metricas.pantalla_pct.no_determinado_s, 30);
  near(r.metricas.voz_pct.mujer + r.metricas.voz_pct.hombre + r.metricas.voz_pct.no_binario, 100, 1e-9);
});

test("Abstención confirmada no altera los porcentajes", () => {
  const base = M.evaluar(DEMO.A, {});
  const r = M.evaluar(DEMO.A, { v0: { accion: "abstener" }, t7: { accion: "abstener" } });
  assert.equal(r.metricas.voz_pct.mujer, base.metricas.voz_pct.mujer);
  assert.equal(r.metricas.pantalla_pct.mujer, base.metricas.pantalla_pct.mujer);
});

test("Validar como mujer los tramos dudosos recalcula los porcentajes", () => {
  const r = M.evaluar(DEMO.A, { v0: { accion: "validar", genero: "mujer" }, t7: { accion: "validar", genero: "mujer" } });
  near(r.metricas.voz_pct.mujer, (95 + 40) / 540 * 100, 0.01);
  near(r.metricas.pantalla_pct.mujer, (161 + 30) / 630 * 100, 0.01);
  assert.equal(r.metricas.voz_pct.no_determinado_s, 0);
});

test("Las decisiones no mutan los datos de origen", () => {
  const antes = JSON.stringify(DEMO.A);
  M.evaluar(DEMO.A, { v0: { accion: "validar", genero: "hombre" } });
  assert.equal(JSON.stringify(DEMO.A), antes);
});

console.log("Salvaguarda (ADR-0006) y umbrales");

test("Salvaguarda: 40/60 cumple; 30/70 no cumple", () => {
  assert.equal(M.salvaguarda(40, 60, 0, false).cumple_salvaguarda_paridad, true);
  assert.equal(M.salvaguarda(30, 70, 0, false).cumple_salvaguarda_paridad, false);
});

test("Salvaguarda: con 10 % no binario el techo masculino baja a 50 %", () => {
  const s = M.salvaguarda(40, 50, 10, false);
  near(s.techo_masculino_ajustado, 0.5, 1e-9);
  assert.equal(s.cumple_salvaguarda_paridad, true);
  assert.equal(M.salvaguarda(35, 55, 10, false).cumple_salvaguarda_paridad, false);
});

test("Salvaguarda: con 30 % no binario se aplica la fase 2 (reparto 50/50)", () => {
  const s = M.salvaguarda(35, 35, 30, false);
  assert.equal(s.regimen_aplicado, "FASE_2_REPARTO_SIMETRICO_50_50");
});

test("Umbrales canónicos de la spec 21", () => {
  assert.equal(M.THRESHOLDS.MASA_CRITICA_PANTALLA, 35);
  assert.equal(M.THRESHOLDS.VOZ_TOKEN_MUDO, 20);
  assert.equal(M.THRESHOLDS.RVP_FIGURACION, 0.3);
  assert.equal(M.THRESHOLDS.SUELO_PARIDAD, 40);
  assert.equal(M.THRESHOLDS.UMBRAL_ABSTENCION, 0.8);
});

console.log("Lectura del grafo");

test("Muestra A: Tomás Ferrer articula 7 de 8 cambios de turno; mujeres en 4, ninguno M→M", () => {
  const r = M.interpretarGrafo(DEMO.A.personas, M.aristasDesdeCaso(DEMO.A));
  assert.equal(r.total_turnos, 8);
  assert.deepEqual(r.eje, { id: "p2", turnos: 7 });
  assert.equal(r.turnos_con_mujer, 4);
  assert.equal(r.turnos_mujer_mujer, 0);
});

test("Muestra A: temas segregados y personas sin turnos", () => {
  const r = M.interpretarGrafo(DEMO.A.personas, M.aristasDesdeCaso(DEMO.A));
  assert.deepEqual(r.temas.solo_mujeres, ["tema:etica"]);
  assert.deepEqual(r.temas.solo_hombres, ["tema:datos"]);
  assert.deepEqual(r.temas.compartidos, ["tema:ia"]);
  assert.deepEqual(r.aislados, ["v0", "t7"]);
});

test("Muestra D: hay turnos M→M, las mujeres son las más citadas y aun así «Ética» queda solo en mujeres", () => {
  const r = M.interpretarGrafo(DEMO.D.personas, M.aristasDesdeCaso(DEMO.D));
  assert.ok(r.turnos_mujer_mujer >= 1);
  assert.deepEqual(r.temas.solo_mujeres, ["tema:etica"]);
  assert.deepEqual(r.temas.solo_hombres, []);
  assert.deepEqual(r.menciones, { mujer: 5, hombre: 0, total: 5 });
  assert.deepEqual(r.aislados, []);
});

test("La lectura del grafo es coherente con la regla 3 de Bechdel", () => {
  for (const k of ["A", "B", "C", "D"]) {
    const r = M.interpretarGrafo(DEMO[k].personas, M.aristasDesdeCaso(DEMO[k]));
    const b = M.evaluar(DEMO[k], {}).bechdel;
    assert.equal(r.turnos_mujer_mujer > 0, Boolean(b.aplica && b.regla_3_dialogo_horizontal), `caso ${k}`);
  }
});

console.log("Revisión preventiva (D-11)");

test("Margen hasta la paridad (muestra A, voz): añadir 175 s o redistribuir 105 s", () => {
  const ev = M.evaluar(DEMO.A, {});
  const m = M.margenParidad(ev.tiempos_s, "voz");
  assert.deepEqual(m, { cumple: false, anadir_s: 175, redistribuir_s: 105 });
  // comprobación: con los segundos añadidos se llega exactamente al 40 %
  assert.ok((95 + 175) / (500 + 175) >= 0.4);
  assert.ok((95 + 105) / 500 >= 0.4);
});

test("Margen hasta la paridad: la muestra D ya cumple", () => {
  const ev = M.evaluar(DEMO.D, {});
  assert.equal(M.margenParidad(ev.tiempos_s, "voz").cumple, true);
  assert.equal(M.margenParidad(ev.tiempos_s, "pantalla").cumple, true);
});

test("Simulador anti-washing: añadir una mujer en plano sin voz a la muestra A dispara el equality-washing", () => {
  const sim = M.simular(DEMO.A, { nuevas: [{ id: "sim1", genero: "mujer", voz_s: 0, pantalla_s: 120 }] });
  const r = M.evaluar(sim, {});
  assert.equal(r.alertas.equality_washing.activa, true);
  assert.equal(M.evaluar(DEMO.A, {}).alertas.equality_washing.activa, false);
});

test("Simulador: dar voz a una experta añadida mejora el índice y no muta el caso original", () => {
  const antes = JSON.stringify(DEMO.A);
  const base = M.evaluar(DEMO.A, {}).indice_global.total;
  const sim = M.simular(DEMO.A, { nuevas: [{ id: "sim1", genero: "mujer", voz_s: 180, pantalla_s: 180, rotulo: true, autoridad: true }], turno_mm: true });
  const r = M.evaluar(sim, {});
  assert.ok(r.indice_global.total > base);
  assert.equal(r.bechdel.aplica, true);
  assert.equal(r.bechdel.regla_3_dialogo_horizontal, true);
  assert.equal(JSON.stringify(DEMO.A), antes);
});

test("Escaleta de ejemplo: proyección con una sola mujer (21 % de voz) y Bechdel no aplicable", () => {
  const caso = M.escaletaACaso(DEMO.ESCALETA_DEMO);
  const r = M.evaluar(caso, {});
  near(r.metricas.voz_pct.mujer, 8 / 38 * 100, 0.01);
  assert.equal(r.bechdel.diagnostico_bechdel, "no_aplica_una_mujer");
  assert.equal(r.salvaguarda.cumple_salvaguarda_paridad, false);
  assert.equal(caso.proyeccion, true);
});

test("Escaleta: el orden de la lista se usa como orden de turnos (Bechdel R3)", () => {
  const filas = [
    { id: "a", genero: "hombre", minutos: 5, rotulo: true },
    { id: "b", genero: "mujer", minutos: 8, rotulo: true },
    { id: "c", genero: "mujer", minutos: 8, rotulo: true }
  ];
  const r = M.evaluar(M.escaletaACaso(filas), {});
  assert.equal(r.bechdel.regla_3_dialogo_horizontal, true);
  assert.equal(r.bechdel.puntuacion_bechdel_0_3, 3);
});

test("Recomendaciones muestra A: prioridad alta para pendientes, voz y efecto token; ordenadas", () => {
  const ev = M.evaluar(DEMO.A, {});
  const recs = M.recomendaciones(ev, M.aristasDesdeCaso(DEMO.A), { pendientes: 2 });
  const ids = recs.map((r) => r.id);
  for (const id of ["pendientes", "voz", "una_mujer", "eje", "tema_m:tema:datos"]) assert.ok(ids.includes(id), id);
  assert.ok(recs.every((r, i) => i === 0 || recs[i - 1].prioridad <= r.prioridad));
});

test("Recomendaciones muestra D: sin recomendaciones de voz ni washing", () => {
  const ev = M.evaluar(DEMO.D, {});
  const ids = M.recomendaciones(ev, M.aristasDesdeCaso(DEMO.D), {}).map((r) => r.id);
  assert.ok(!ids.includes("voz") && !ids.includes("washing") && !ids.includes("una_mujer"));
});

test("Todas las claves de recomendación existen en los 5 idiomas", () => {
  const claves = ["rec.pendientes", "rec.voz", "rec.pantalla", "rec.washing", "rec.washing_generic", "rec.una_mujer", "rec.bechdel_r1", "rec.bechdel_r1_generic", "rec.bechdel_r3", "rec.rotulo", "rec.eje", "rec.tema_m", "rec.tema_f", "rec.ok"];
  for (const l of ["es", "ca", "gl", "eu", "en"]) for (const k of claves) assert.ok(I18N.DICT[l][k], `${l}:${k}`);
});

console.log("Internacionalización");

const html = readFileSync(join(root, "index.html"), "utf8");
const appJs = readFileSync(join(root, "js", "app.js"), "utf8");
const { DICT } = I18N;

test("es, ca, gl, eu y en tienen exactamente las mismas claves", () => {
  const es = Object.keys(DICT.es).sort();
  for (const l of ["ca", "gl", "eu", "en"]) {
    const keys = Object.keys(DICT[l]).sort();
    const faltan = es.filter((k) => !keys.includes(k));
    const sobran = keys.filter((k) => !es.includes(k));
    assert.deepEqual({ faltan, sobran }, { faltan: [], sobran: [] }, `idioma ${l}`);
  }
});

test("Ninguna traducción está vacía y los marcadores {x} coinciden entre idiomas", () => {
  const ph = (s) => (s.match(/\{[a-z]+\}/g) || []).sort().join(",");
  for (const k of Object.keys(DICT.es)) {
    for (const l of ["es", "ca", "gl", "eu", "en"]) assert.ok(DICT[l][k] && DICT[l][k].trim().length > 0, `${l}:${k} vacía`);
    assert.equal(ph(DICT.ca[k]), ph(DICT.es[k]), `marcadores distintos en ca:${k}`);
    assert.equal(ph(DICT.en[k]), ph(DICT.es[k]), `marcadores distintos en en:${k}`);
    assert.equal(ph(DICT.gl[k]), ph(DICT.es[k]), `marcadores distintos en gl:${k}`);
    assert.equal(ph(DICT.eu[k]), ph(DICT.es[k]), `marcadores distintos en eu:${k}`);
  }
});

test("Todas las claves data-i18n* del HTML existen en el diccionario", () => {
  const re = /data-i18n(?:-title|-aria)?="([^"]+)"/g;
  const faltan = [];
  let m;
  while ((m = re.exec(html))) if (!DICT.es[m[1]]) faltan.push(m[1]);
  assert.deepEqual(faltan, []);
});

test("Todas las claves t(\"…\") literales de app.js existen en el diccionario", () => {
  const re = /\bt\(\s*"([^"]+)"/g;
  const faltan = [];
  let m;
  while ((m = re.exec(appJs))) if (!m[1].endsWith(".") && !DICT.es[m[1]]) faltan.push(m[1]);
  assert.deepEqual(faltan, []);
});

test("Cada .info-host del HTML tiene título y cuerpo en los 5 idiomas", () => {
  const re = /data-info="([^"]+)"/g;
  let m;
  while ((m = re.exec(html))) {
    for (const l of ["es", "ca", "gl", "eu", "en"]) {
      assert.ok(DICT[l][`info.${m[1]}.t`], `${l}: info.${m[1]}.t`);
      assert.ok(DICT[l][`info.${m[1]}.b`], `${l}: info.${m[1]}.b`);
    }
  }
});

test("Claves dinámicas (prefijo + valor) cubiertas", () => {
  const prefijos = {
    "verdict.title.": ["washing", "infra", "salvaguarda", "ok"],
    "verdict.sub.": ["washing", "infra", "salvaguarda", "ok"],
    "easy.result.": ["washing", "infra", "salvaguarda", "ok"],
    "bechdel.diag.": ["supera", "efecto_token", "aislamiento_relacional", "parcial", "sin_datos", "no_aplica_una_mujer", "no_aplica_sin_mujeres", "no_aplica_sin_hombres"],
    "graph.type.": ["turno", "comparte_plano", "menciona", "habla_de"],
    "climate.": ["tecnico_asertivo", "colaborativo", "disenso"],
    "step.": ["audio", "nlp", "video", "captions", "silver", "gold"],
    "step.state.": ["ok", "pending", "running", "error"],
    "hitl.channel.": ["voz", "pantalla"],
    "gender.": ["mujer", "hombre", "no_binario", "no_determinado", "mujer_s", "hombre_s", "no_binario_s", "no_determinado_s"],
    "index.dim.": ["pantalla", "voz", "espacio", "autoridad"],
    "phase.announce.": ["preproduccion", "edicion", "publicado"],
    "verdict.eyebrow": ["", "_draft", "_projection"],
    "regimen.": ["FASE_1_ABSORCION_TECHO_MASCULINO", "FASE_2_REPARTO_SIMETRICO_50_50", "FASE_3_MESA_MONOGRAFICA_DIVERSIDAD_LGTBIQ", "SIN_DATOS_DETERMINADOS"]
  };
  const faltan = [];
  for (const [p, vs] of Object.entries(prefijos)) for (const v of vs) if (!DICT.es[p + v]) faltan.push(p + v);
  assert.deepEqual(faltan, []);
});

console.log(`\n${passed} pruebas correctas${process.exitCode ? " — HAY FALLOS" : ""}`);
