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

test("Muestra A: Bechdel = Efecto Token (una sola mujer) y no supera", () => {
  const r = M.evaluar(DEMO.A, {});
  assert.equal(r.bechdel.supera_bechdel_digital, false);
  assert.equal(r.bechdel.diagnostico_bechdel, "efecto_token");
  assert.equal(r.bechdel.mujeres_distintas_hablando, 1);
});

test("Muestra A: la salvaguarda NO cumple con 19 % de voz femenina", () => {
  const r = M.evaluar(DEMO.A, {});
  assert.equal(r.salvaguarda.cumple_salvaguarda_paridad, false);
});

test("Muestra B reproduce el caso B: 45 % pantalla, 12 % voz, RVP 0,27 → equality-washing", () => {
  const r = M.evaluar(DEMO.B, {});
  near(r.metricas.pantalla_pct.mujer, 45.0, 0.1);
  near(r.metricas.voz_pct.mujer, 12.0, 0.1);
  near(r.metricas.ratio_voz_pantalla.mujer, 0.27, 0.01);
  assert.equal(r.alertas.equality_washing.activa, true);
  assert.equal(r.alertas.infrarrepresentacion.activa, false);
  assert.equal(r.diagnostico, "washing");
});

test("Muestra B: Bechdel = Aislamiento relacional (2 mujeres, ninguna transición M→M)", () => {
  const r = M.evaluar(DEMO.B, {});
  assert.equal(r.bechdel.mujeres_distintas_hablando, 2);
  assert.equal(r.bechdel.transiciones_mujer_a_mujer, 0);
  assert.equal(r.bechdel.diagnostico_bechdel, "aislamiento_relacional");
});

test("Muestra C reproduce el caso C: 42 % / 44 %, RVP 1,05 → paridad efectiva y Bechdel 3/3", () => {
  const r = M.evaluar(DEMO.C, {});
  near(r.metricas.pantalla_pct.mujer, 42.0, 0.1);
  near(r.metricas.voz_pct.mujer, 44.0, 0.1);
  near(r.metricas.ratio_voz_pantalla.mujer, 1.05, 0.01);
  assert.equal(r.alertas.equality_washing.activa, false);
  assert.equal(r.alertas.infrarrepresentacion.activa, false);
  assert.equal(r.salvaguarda.cumple_salvaguarda_paridad, true);
  assert.equal(r.bechdel.puntuacion_bechdel_0_3, 3);
  assert.equal(r.diagnostico, "ok");
});

test("El índice global está en 0–100 y C puntúa más que B y A", () => {
  const a = M.evaluar(DEMO.A, {}).indice_global.total;
  const b = M.evaluar(DEMO.B, {}).indice_global.total;
  const c = M.evaluar(DEMO.C, {}).indice_global.total;
  [a, b, c].forEach((x) => assert.ok(x >= 0 && x <= 100));
  assert.ok(c > a && c > b, `A=${a} B=${b} C=${c}`);
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

console.log("Internacionalización");

const html = readFileSync(join(root, "index.html"), "utf8");
const appJs = readFileSync(join(root, "js", "app.js"), "utf8");
const { DICT } = I18N;

test("es, ca y en tienen exactamente las mismas claves", () => {
  const es = Object.keys(DICT.es).sort();
  for (const l of ["ca", "en"]) {
    const keys = Object.keys(DICT[l]).sort();
    const faltan = es.filter((k) => !keys.includes(k));
    const sobran = keys.filter((k) => !es.includes(k));
    assert.deepEqual({ faltan, sobran }, { faltan: [], sobran: [] }, `idioma ${l}`);
  }
});

test("Ninguna traducción está vacía y los marcadores {x} coinciden entre idiomas", () => {
  const ph = (s) => (s.match(/\{[a-z]+\}/g) || []).sort().join(",");
  for (const k of Object.keys(DICT.es)) {
    for (const l of ["es", "ca", "en"]) assert.ok(DICT[l][k] && DICT[l][k].trim().length > 0, `${l}:${k} vacía`);
    assert.equal(ph(DICT.ca[k]), ph(DICT.es[k]), `marcadores distintos en ca:${k}`);
    assert.equal(ph(DICT.en[k]), ph(DICT.es[k]), `marcadores distintos en en:${k}`);
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

test("Cada .info-host del HTML tiene título y cuerpo en los 3 idiomas", () => {
  const re = /data-info="([^"]+)"/g;
  let m;
  while ((m = re.exec(html))) {
    for (const l of ["es", "ca", "en"]) {
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
    "bechdel.diag.": ["supera", "efecto_token", "aislamiento_relacional", "parcial", "sin_datos"],
    "graph.type.": ["turno", "comparte_plano", "menciona", "habla_de"],
    "climate.": ["tecnico_asertivo", "colaborativo", "disenso"],
    "step.": ["audio", "nlp", "video", "captions", "silver", "gold"],
    "step.state.": ["ok", "pending", "running", "error"],
    "hitl.channel.": ["voz", "pantalla"],
    "gender.": ["mujer", "hombre", "no_binario", "no_determinado", "mujer_s", "hombre_s", "no_binario_s", "no_determinado_s"],
    "index.dim.": ["pantalla", "voz", "espacio", "autoridad"],
    "regimen.": ["FASE_1_ABSORCION_TECHO_MASCULINO", "FASE_2_REPARTO_SIMETRICO_50_50", "FASE_3_MESA_MONOGRAFICA_DIVERSIDAD_LGTBIQ", "SIN_DATOS_DETERMINADOS"]
  };
  const faltan = [];
  for (const [p, vs] of Object.entries(prefijos)) for (const v of vs) if (!DICT.es[p + v]) faltan.push(p + v);
  assert.deepEqual(faltan, []);
});

console.log(`\n${passed} pruebas correctas${process.exitCode ? " — HAY FALLOS" : ""}`);
