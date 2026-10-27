// SPDX-FileCopyrightText: 2026 Equipo 1: Attention Is All She Needs (Alba Camiña García, Pilar de la Fuente Diez, Rocío Jiménez Villén)
// SPDX-License-Identifier: Apache-2.0

/**
 * AIASN — Muestras SINTÉTICAS de demostración.
 *
 * Los tres casos reproducen los escenarios A, B y C de la spec 21 §3.3 (tabla comparativa de alertas).
 * Los nombres, cargos y tiempos son FICTICIOS: no corresponden a personas ni emisiones reales.
 * Las métricas no se escriben a mano: se derivan de los tiempos por persona con `AIASN_METRICS`.
 * Formato por persona: id, nombre, cargo, rotulo (¿rótulo OCR?), genero, genero_p (confianza),
 * autoridad, pantalla_s, voz_s, centralidad.
 */
(function (root) {
  "use strict";

  const DEMO_CASES = {
    A: {
      video_id: "demo-A",
      duracion_s: 600,
      duracion_prevista_s: 1800,
      status: { estado: "ok", pasos: { audio: "ok", nlp: "ok", video: "ok", captions: "ok", silver: "ok", gold: "ok" }, error: null },
      personas: [
        { id: "p1", nombre: "Dra. Irene Valls", cargo: "Investigadora principal", rotulo: true, genero: "mujer", genero_p: 0.97, autoridad: true, pantalla_s: 161, voz_s: 95, centralidad: 0.72 },
        { id: "p2", nombre: "Dr. Tomás Ferrer", cargo: "Director del instituto", rotulo: true, genero: "hombre", genero_p: 0.99, autoridad: true, pantalla_s: 250, voz_s: 215, centralidad: 0.88 },
        { id: "p3", nombre: "Prof. Jordi Casals", cargo: "Catedrático", rotulo: true, genero: "hombre", genero_p: 0.98, autoridad: true, pantalla_s: 189, voz_s: 190, centralidad: 0.79 },
        { id: "v0", nombre: "Locución en off", cargo: null, rotulo: false, genero: "no_determinado", genero_p: 0.62, autoridad: false, pantalla_s: 0, voz_s: 40, centralidad: null },
        { id: "t7", nombre: "Persona sin rótulo (plano de fondo)", cargo: null, rotulo: false, genero: "no_determinado", genero_p: 0.55, autoridad: false, pantalla_s: 30, voz_s: 0, centralidad: null }
      ],
      segmentos_dudosos: [
        { persona_id: "v0", canal: "voz", tiempo_i: 12, tiempo_f: 52, p: 0.62, genero_propuesto: "mujer", evidencia_texto: "«Bienvenidos al ciclo de conferencias sobre inteligencia artificial responsable…»" },
        { persona_id: "t7", canal: "pantalla", tiempo_i: 301, tiempo_f: 331, p: 0.55, genero_propuesto: "mujer", evidencia_texto: "Rostro parcial (giro de cabeza), sin rótulo OCR ni turno de palabra asociado." }
      ],
      secuencia_turnos: ["p2", "p1", "p2", "p3", "p2", "p3", "p1", "p2", "p3"],
      referentes: { mujer: 1, hombre: 3 },
      apertura_id: "p2",
      cierre_id: "p2",
      temas: [
        { id: "tema:ia", label: "Inteligencia artificial" },
        { id: "tema:datos", label: "Gobernanza de datos" },
        { id: "tema:etica", label: "Ética y sesgos" }
      ],
      habla_de: [["p2", "tema:ia", 5], ["p3", "tema:ia", 4], ["p1", "tema:ia", 2], ["p2", "tema:datos", 3], ["p3", "tema:datos", 3], ["p1", "tema:etica", 3]],
      planos_compartidos: [["p2", "p1", 18], ["p2", "p3", 24]],
      menciones: [["p2", "p1", 2], ["p3", "p2", 1]],
      clima: { mujer: { tecnico_asertivo: 70, colaborativo: 30, disenso: 0 }, hombre: { tecnico_asertivo: 75, colaborativo: 25, disenso: 0 } }
    },

    B: {
      video_id: "demo-B",
      duracion_s: 600,
      status: { estado: "ok", pasos: { audio: "ok", nlp: "ok", video: "ok", captions: "ok", silver: "ok", gold: "ok" }, error: null },
      personas: [
        { id: "p1", nombre: "Dra. Clara Ruiz", cargo: "Investigadora en Bioética", rotulo: true, genero: "mujer", genero_p: 0.98, autoridad: true, pantalla_s: 140, voz_s: 120, centralidad: 0.82 },
        { id: "p2", nombre: "Alex Morante", cargo: "Especialista en Derechos Digitales", rotulo: true, genero: "no_binario", genero_p: 0.96, autoridad: true, pantalla_s: 120, voz_s: 45, centralidad: 0.74 },
        { id: "p3", nombre: "Dr. Sergio Blanco", cargo: "Coordinador del Encuentro", rotulo: true, genero: "hombre", genero_p: 0.99, autoridad: true, pantalla_s: 160, voz_s: 135, centralidad: 0.85 }
      ],
      segmentos_dudosos: [],
      secuencia_turnos: ["p3", "p1", "p2", "p1", "p3", "p2", "p3", "p1"],
      referentes: { mujer: 2, hombre: 1 },
      apertura_id: "p3",
      cierre_id: "p1",
      temas: [
        { id: "tema:derechos", label: "Derechos y diversidad" },
        { id: "tema:gobernanza", label: "Gobernanza de la IA" }
      ],
      habla_de: [["p1", "tema:derechos", 4], ["p2", "tema:derechos", 3], ["p3", "tema:gobernanza", 4]],
      planos_compartidos: [["p1", "p2", 30], ["p3", "p2", 25], ["p3", "p1", 28]],
      menciones: [["p2", "p1", 2], ["p1", "p2", 1]],
      clima: {
        mujer: { tecnico_asertivo: 65, colaborativo: 30, disenso: 5 },
        hombre: { tecnico_asertivo: 60, colaborativo: 30, disenso: 10 },
        no_binario: { tecnico_asertivo: 70, colaborativo: 30, disenso: 0 }
      }
    },

    C: {
      video_id: "demo-C",
      duracion_s: 600,
      status: { estado: "ok", pasos: { audio: "ok", nlp: "ok", video: "ok", captions: "ok", silver: "ok", gold: "ok" }, error: null },
      personas: [
        { id: "p1", nombre: "Marta Roig", cargo: "Directora de Comunicación", rotulo: true, genero: "mujer", genero_p: 0.96, autoridad: true, pantalla_s: 150, voz_s: 36, centralidad: 0.55 },
        { id: "p2", nombre: "Laia Serra", cargo: "Responsable de Sostenibilidad", rotulo: true, genero: "mujer", genero_p: 0.95, autoridad: true, pantalla_s: 120, voz_s: 24, centralidad: 0.48 },
        { id: "p3", nombre: "Albert Pons", cargo: "Consejero delegado", rotulo: true, genero: "hombre", genero_p: 0.99, autoridad: true, pantalla_s: 200, voz_s: 250, centralidad: 0.92 },
        { id: "p4", nombre: "Ramón Vidal", cargo: "Director financiero", rotulo: true, genero: "hombre", genero_p: 0.98, autoridad: true, pantalla_s: 130, voz_s: 190, centralidad: 0.81 }
      ],
      segmentos_dudosos: [],
      secuencia_turnos: ["p3", "p1", "p3", "p4", "p3", "p2", "p4", "p3"],
      referentes: { mujer: 0, hombre: 4 },
      apertura_id: "p3",
      cierre_id: "p3",
      temas: [
        { id: "tema:resultados", label: "Resultados financieros" },
        { id: "tema:esg", label: "Sostenibilidad corporativa" }
      ],
      habla_de: [["p3", "tema:resultados", 6], ["p4", "tema:resultados", 5], ["p1", "tema:esg", 2], ["p2", "tema:esg", 2]],
      planos_compartidos: [["p3", "p1", 40], ["p3", "p2", 35], ["p4", "p1", 22]],
      menciones: [["p3", "p4", 3]],
      clima: { mujer: { tecnico_asertivo: 40, colaborativo: 60, disenso: 0 }, hombre: { tecnico_asertivo: 80, colaborativo: 10, disenso: 10 } }
    },

    D: {
      video_id: "demo-D",
      duracion_s: 600,
      status: { estado: "ok", pasos: { audio: "ok", nlp: "ok", video: "ok", captions: "ok", silver: "ok", gold: "ok" }, error: null },
      personas: [
        { id: "p1", nombre: "Dra. Nuria Camps", cargo: "Catedrática de Informática", rotulo: true, genero: "mujer", genero_p: 0.98, autoridad: true, pantalla_s: 140, voz_s: 130, centralidad: 0.85 },
        { id: "p2", nombre: "Dra. Eva Solé", cargo: "Directora de proyectos de IA", rotulo: true, genero: "mujer", genero_p: 0.97, autoridad: true, pantalla_s: 112, voz_s: 90, centralidad: 0.8 },
        { id: "p3", nombre: "Joan Mas", cargo: "Moderador", rotulo: true, genero: "hombre", genero_p: 0.99, autoridad: false, pantalla_s: 190, voz_s: 150, centralidad: 0.83 },
        { id: "p4", nombre: "Pere Bosch", cargo: "Investigador sénior", rotulo: true, genero: "hombre", genero_p: 0.98, autoridad: true, pantalla_s: 158, voz_s: 130, centralidad: 0.78 }
      ],
      segmentos_dudosos: [],
      secuencia_turnos: ["p3", "p1", "p2", "p4", "p2", "p1", "p3", "p4", "p1", "p2"],
      referentes: { mujer: 3, hombre: 3 },
      apertura_id: "p3",
      cierre_id: "p2",
      temas: [
        { id: "tema:modelos", label: "Modelos abiertos" },
        { id: "tema:etica", label: "Ética y supervisión" },
        { id: "tema:educacion", label: "Educación" }
      ],
      habla_de: [["p1", "tema:modelos", 4], ["p4", "tema:modelos", 4], ["p2", "tema:etica", 4], ["p1", "tema:etica", 2], ["p4", "tema:educacion", 3], ["p2", "tema:educacion", 2]],
      planos_compartidos: [["p1", "p2", 30], ["p3", "p4", 26]],
      menciones: [["p1", "p2", 2], ["p2", "p1", 2], ["p4", "p1", 1]],
      clima: { mujer: { tecnico_asertivo: 60, colaborativo: 35, disenso: 5 }, hombre: { tecnico_asertivo: 60, colaborativo: 30, disenso: 10 } }
    }
  };

  root.AIASN_DEMO = DEMO_CASES;
  if (typeof module === "object" && module.exports) module.exports = DEMO_CASES;

  /**
   * Escaleta de ejemplo para la fase de preproducción (ficticia). El orden es el orden de turnos previsto.
   * Con una sola mujer y 8 de 38 minutos, la proyección dispara la infrarrepresentación: el ejemplo invita
   * a editarla y ver cómo cambian las alertas antes de grabar.
   */
  root.AIASN_ESCALETA_DEMO = [
    { id: "e1", nombre: "Moderador", genero: "hombre", minutos: 6, rotulo: true },
    { id: "e2", nombre: "Dra. Laura Pons", genero: "mujer", minutos: 8, rotulo: true },
    { id: "e3", nombre: "Dr. Joan Riera", genero: "hombre", minutos: 12, rotulo: true },
    { id: "e4", nombre: "Prof. Pau Vidal", genero: "hombre", minutos: 12, rotulo: true }
  ];
  if (typeof module === "object" && module.exports) module.exports.ESCALETA_DEMO = root.AIASN_ESCALETA_DEMO;
})(typeof self !== "undefined" ? self : this);
