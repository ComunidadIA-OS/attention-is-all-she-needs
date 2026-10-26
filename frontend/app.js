// SPDX-FileCopyrightText: 2026 Equipo 1: Attention Is All She Needs (Alba Camiña García, Pilar de la Fuente Diez, Rocío Jiménez Villén)
// SPDX-License-Identifier: Apache-2.0

/**
 * AIASN — Dashboard de Auditoría Audiovisual y Soberanía Algorítmica
 * Lógica cliente para consumo de API REST (FastAPI) y visualización pericial.
 */

// Muestra de auditoría precargada (clip representativo Quanta, quanta IA!)
// Cumple estrictamente la especificación API_SPEC.md de Rocío
const DEMO_PAYLOAD = {
  video_id: "clip_quanta-3f9a",
  status: {
    estado: "ok",
    pasos: { audio: "ok", nlp: "ok", video: "ok", captions: "ok", silver: "ok", gold: "ok" },
    error: null
  },
  resultado: {
    veredicto: {
      resumen_lectura_facil: "En este vídeo intervienen 4 personas. La experta invitada (Sandra Freire, pedagoga) tiene un 25.9 % del tiempo de voz frente al 74.1 % de los participantes masculinos. Supera el test de Bechdel digital al intervenir con cargo técnico declarado y sin mediación temática masculina.",
      alerta_equality_washing: false,
      motivo_alerta: "Presencia en pantalla y voz activa equilibradas. No se detecta presencia ornamental en plano silente.",
      bechdel: {
        puntuacion_0_3: 3,
        criterios: [
          { label: "Mujer con cargo profesional acreditado (OCR)", cumple: true },
          { label: "Intervención activa en ciencia o tecnología", cumple: true },
          { label: "Diálogo directo sin mediación de sesgo", cumple: true }
        ],
        diagnostico: "Supera el Test de Bechdel Conversacional."
      },
      salvaguarda_paridad: {
        cumple: true,
        cuota_femenina: 0.259,
        salvaguarda_activa: true
      },
      valoracion_ciudadana: null
    },
    metricas: {
      voz_pct: { mujer: 25.9, hombre: 74.1, no_determinado: 0.0 },
      pantalla_pct: { mujer: 33.3, hombre: 59.7, no_determinado: 7.0 },
      ratio_voz_pantalla: { mujer: 0.78, hombre: 1.24 },
      referentes: { mujer: 1, hombre: 2 }
    },
    personas: [
      {
        id: "p6",
        nombre: "Sandra Freire",
        cargo: "Pedagoga en Deleitea",
        genero: "mujer",
        rol: "experta",
        autoridad: true,
        pantalla_s: 22.9,
        voz_s: 33.0,
        centralidad: 0.84,
        sesgo_cargo: 0.074
      },
      {
        id: "p1",
        nombre: "Dr. Carles Sierra",
        cargo: "Director IIIA-CSIC",
        genero: "hombre",
        rol: "presentador/experto",
        autoridad: true,
        pantalla_s: 35.1,
        voz_s: 48.2,
        centralidad: 0.91,
        sesgo_cargo: -0.052
      },
      {
        id: "p2",
        nombre: "Marc Torrens",
        cargo: "Profesor ESADE",
        genero: "hombre",
        rol: "experto",
        autoridad: true,
        pantalla_s: 28.4,
        voz_s: 46.0,
        centralidad: 0.77,
        sesgo_cargo: -0.061
      },
      {
        id: "v0",
        nombre: "Locución en off",
        cargo: null,
        genero: "no_determinado",
        rol: "narrador",
        autoridad: false,
        pantalla_s: 0.0,
        voz_s: 14.5,
        centralidad: 0.40,
        sesgo_cargo: null
      }
    ],
    temas: [
      { tema: "educación y pedagogía", genero: "mujer", turnos: 4, pct: 28.5, sesgo: 0.112 },
      { tema: "inteligencia artificial", genero: "hombre", turnos: 6, pct: 42.8, sesgo: -0.038 },
      { tema: "ética y sesgo", genero: "mujer", turnos: 4, pct: 28.7, sesgo: 0.089 }
    ],
    poder: {
      centralidad_media: { mujer: 0.84, hombre: 0.84 },
      personas_distintas: { mujer: 1, hombre: 2, no_determinado: 1 },
      veces_citado_como_referente: { mujer: 1, hombre: 2 }
    },
    roles: [
      { rol: "experta / autoridad", genero: "mujer", voz_s: 33.0 },
      { rol: "experto / dirección", genero: "hombre", voz_s: 94.2 }
    ],
    clima: {
      mujer: { "técnico/asertivo": 70, "colaborativo": 30, "disenso": 0 },
      hombre: { "técnico/asertivo": 75, "colaborativo": 25, "disenso": 0 }
    },
    constelacion: {
      nodos: [
        { id: "p6", tipo: "participante", label: "Sandra Freire", genero: "mujer", size: 33.0, cargo: "Pedagoga en Deleitea" },
        { id: "p1", tipo: "participante", label: "Dr. Carles Sierra", genero: "hombre", size: 48.2, cargo: "Director IIIA-CSIC" },
        { id: "p2", tipo: "participante", label: "Marc Torrens", genero: "hombre", size: 46.0, cargo: "Profesor ESADE" },
        { id: "v0", tipo: "participante", label: "Voz en off", genero: "no_determinado", size: 14.5, cargo: "Locución institucional" },
        { id: "tema:educacion", tipo: "tema", label: "Educación y Pedagogía", size: 16, sesgo: 0.112 },
        { id: "tema:ia", tipo: "tema", label: "Inteligencia Artificial", size: 24, sesgo: -0.038 },
        { id: "tema:etica", tipo: "tema", label: "Ética y Supervisión", size: 16, sesgo: 0.089 }
      ],
      aristas: [
        { source: "p1", target: "p6", tipo: "turno", peso: 3 },
        { source: "p6", target: "p2", tipo: "turno", peso: 2 },
        { source: "p1", target: "p2", tipo: "turno", peso: 4 },
        { source: "p1", target: "p6", tipo: "comparte_plano", peso: 18 },
        { source: "p6", target: "tema:educacion", tipo: "habla_de", peso: 4 },
        { source: "p6", target: "tema:etica", tipo: "habla_de", peso: 3 },
        { source: "p1", target: "tema:ia", tipo: "habla_de", peso: 5 },
        { source: "p2", target: "tema:ia", tipo: "habla_de", peso: 4 },
        { source: "p1", target: "p6", tipo: "menciona", peso: 2 }
      ]
    }
  }
};

// Estado global de la aplicación
const state = {
  mode: "demo", // 'demo' o 'live'
  apiBaseUrl: "http://localhost:8000",
  currentVideoId: "clip_quanta-3f9a",
  currentData: null,
  supervisionAsumida: true,
  anonymized: false, // Pseudonimización conforme a Art. 4.5 RGPD
  citizenVotes: { yes: 89, partial: 12, no: 3 },
  userHasVoted: false,
  networkInstance: null
};

// Generador de nombres pseudonimizados (Art. 4.5 y 25 RGPD: Privacidad por Diseño)
function getDisplayName(person, anonymize) {
  if (!person) return "Participante";
  if (!anonymize) {
    return person.nombre || person.label || "Persona sin rótulo";
  }
  const idStr = person.id || "";
  const roleStr = person.cargo ? ` [${person.cargo}]` : "";
  if (person.genero === "mujer") {
    return `Experta ${idStr}${roleStr}`;
  } else if (person.genero === "hombre") {
    return `Experto ${idStr}${roleStr}`;
  } else {
    return `Participante ${idStr}${roleStr}`;
  }
}

// Inicialización al cargar el DOM
document.addEventListener("DOMContentLoaded", () => {
  initUI();
  loadData(DEMO_PAYLOAD);
});

function initUI() {
  // Selector de Modo (Demo vs Live API)
  const modeSelect = document.getElementById("mode-select");
  if (modeSelect) {
    modeSelect.addEventListener("change", (e) => {
      state.mode = e.target.value;
      const apiBadge = document.getElementById("api-status-badge");
      if (state.mode === "demo") {
        if (apiBadge) apiBadge.textContent = "Muestra Local Precargada";
        loadData(DEMO_PAYLOAD);
      } else {
        if (apiBadge) apiBadge.textContent = "Conectando a FastAPI (localhost:8000)...";
        checkApiHealth();
      }
    });
  }

  // Interruptor de Anonimización / Pseudonimización (Art. 4.5 RGPD)
  const anonToggle = document.getElementById("anonymize-toggle");
  if (anonToggle) {
    anonToggle.addEventListener("change", (e) => {
      state.anonymized = e.target.checked;
      if (state.currentData) {
        loadData(state.currentData);
      }
    });
  }

  // Interruptor de Supervisión Humana (Human-in-the-Loop)
  const hitlToggle = document.getElementById("hitl-toggle");
  if (hitlToggle) {
    hitlToggle.addEventListener("change", (e) => {
      state.supervisionAsumida = e.target.checked;
      updateComplianceCertificate();
    });
  }

  // Soporte de clic para el popover del Test de Bechdel
  const bechdelBtn = document.getElementById("bechdel-info-btn");
  const bechdelTooltip = document.getElementById("bechdel-tooltip");
  if (bechdelBtn && bechdelTooltip) {
    bechdelBtn.addEventListener("click", (e) => {
      e.stopPropagation();
      bechdelTooltip.classList.toggle("hidden");
    });
    document.addEventListener("click", (e) => {
      if (!bechdelTooltip.contains(e.target) && e.target !== bechdelBtn) {
        bechdelTooltip.classList.add("hidden");
      }
    });
  }

  // Inicialización del Modo Oscuro Sostenible (Detección SO + Selector Manual)
  initTheme();

  // Micro-encuesta de Soberanía Ciudadana (Vote with your feet)
  setupCitizenVoting();
}

// Gestión del Tema (Detección del Sistema Operativo y Control Manual)
function initTheme() {
  const savedTheme = localStorage.getItem("aiasn-theme");
  const prefersDark = window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches;
  const isDark = savedTheme === "dark" || (!savedTheme && prefersDark);

  applyTheme(isDark);

  const themeBtn = document.getElementById("theme-toggle-btn");
  if (themeBtn) {
    themeBtn.addEventListener("click", () => {
      const currentlyDark = document.documentElement.classList.contains("dark");
      const nextDark = !currentlyDark;
      localStorage.setItem("aiasn-theme", nextDark ? "dark" : "light");
      applyTheme(nextDark);
    });
  }

  // Si el usuario cambia el tema del sistema operativo y no hay forzado manual:
  if (window.matchMedia) {
    window.matchMedia("(prefers-color-scheme: dark)").addEventListener("change", (e) => {
      if (!localStorage.getItem("aiasn-theme")) {
        applyTheme(e.matches);
      }
    });
  }
}

function applyTheme(isDark) {
  if (isDark) {
    document.documentElement.classList.add("dark");
  } else {
    document.documentElement.classList.remove("dark");
  }
  const icon = document.getElementById("theme-toggle-icon");
  if (icon) {
    icon.textContent = isDark ? "☀️" : "🌙";
  }
  // Si la red ya está dibujada, refrescar colores del lienzo
  if (state.currentData && state.networkInstance) {
    renderConstellation(state.currentData.resultado.constelacion);
  }
}

async function checkApiHealth() {
  const apiBadge = document.getElementById("api-status-badge");
  try {
    const res = await fetch(`${state.apiBaseUrl}/health`);
    if (res.ok) {
      if (apiBadge) {
        apiBadge.textContent = "API en línea (FastAPI)";
        apiBadge.className = "text-xs px-2.5 py-0.5 rounded font-mono font-medium badge-certified";
      }
    } else {
      throw new Error("API responded non-200");
    }
  } catch (err) {
    if (apiBadge) {
      apiBadge.textContent = "API desconectada (usando muestra local)";
      apiBadge.className = "text-xs px-2.5 py-0.5 rounded font-mono font-medium badge-review";
    }
  }
}

// Carga y renderizado integral del payload de auditoría
function loadData(payload) {
  state.currentData = payload;
  const res = payload.resultado;

  // 1. Identificadores y Metadatos de Expediente
  document.getElementById("video-id-badge").textContent = payload.video_id;
  
  // 2. Veredicto y Dictamen Regulatorio
  renderVerdict(res.veredicto);

  // 3. Métricas Clave de Paridad (Seeing and Hearing)
  renderMetrics(res.metricas);

  // 4. Constelación de Protagonismo (vis-network)
  renderConstellation(res.constelacion);

  // 5. Tabla de Personas, Autoridad y Poder
  renderPersonsTable(res.personas);

  // 6. Clima Conversacional (Agregado)
  renderClimate(res.clima);

  // 7. Certificado de Conformidad y Sello SHA-256
  updateComplianceCertificate();
}

function renderVerdict(veredicto) {
  // Lectura Fácil (con soporte para modo anonimizado)
  let textoLectura = veredicto.resumen_lectura_facil;
  if (state.anonymized) {
    textoLectura = textoLectura
      .replace(/Sandra Freire/g, "la experta invitada")
      .replace(/Carles Sierra/g, "el participante 1")
      .replace(/Marc Torrens/g, "el participante 2");
  }
  document.getElementById("lectura-facil-text").textContent = textoLectura;

  // Alerta Equality-Washing
  const alertContainer = document.getElementById("equality-washing-card");
  const alertBadge = document.getElementById("equality-washing-badge");
  const alertDesc = document.getElementById("equality-washing-desc");
  
  if (veredicto.alerta_equality_washing) {
    alertContainer.className = "p-4 rounded border border-red-300 bg-red-50";
    alertBadge.textContent = "ALERTA DETECTADA";
    alertBadge.className = "px-2 py-0.5 text-xs font-bold rounded bg-red-600 text-white font-mono";
    alertDesc.textContent = veredicto.motivo_alerta || "Desproporción severa entre presencia visual muda y voz activa.";
  } else {
    alertContainer.className = "p-4 rounded border border-emerald-200 bg-emerald-50/50";
    alertBadge.textContent = "CONFORME (SIN EQUALITY-WASHING)";
    alertBadge.className = "px-2 py-0.5 text-xs font-bold rounded bg-emerald-700 text-white font-mono";
    alertDesc.textContent = veredicto.motivo_alerta || "Presencia en pantalla y voz experta equilibradas.";
  }

  // Bechdel Digital esquemático (3 líneas con checks Sí/No)
  const bechdelScore = document.getElementById("bechdel-score");
  const bechdelChecklist = document.getElementById("bechdel-checklist");
  if (bechdelScore) bechdelScore.textContent = `${veredicto.bechdel.puntuacion_0_3} / 3 Criterios`;

  if (bechdelChecklist) {
    const criterios = veredicto.bechdel.criterios || [
      { label: "Mujer con cargo profesional acreditado (OCR)", cumple: veredicto.bechdel.puntuacion_0_3 >= 1 },
      { label: "Intervención activa en ciencia o tecnología", cumple: veredicto.bechdel.puntuacion_0_3 >= 2 },
      { label: "Diálogo directo sin mediación de sesgo", cumple: veredicto.bechdel.puntuacion_0_3 >= 3 }
    ];
    bechdelChecklist.innerHTML = criterios.map(c => `
      <div class="flex items-center justify-between py-1 border-b border-slate-100 last:border-0">
        <span class="text-[11px] leading-tight ${c.cumple ? 'text-slate-800 font-medium' : 'text-slate-400'}">${c.label}</span>
        <span class="inline-flex items-center justify-center w-5 h-5 rounded text-xs font-mono font-bold ${c.cumple ? 'bg-emerald-100 text-emerald-800' : 'bg-slate-100 text-slate-400'}">
          ${c.cumple ? '✓' : '✗'}
        </span>
      </div>
    `).join("");
  }

  // Salvaguarda de Paridad (ADR-0006)
  const safeguardBadge = document.getElementById("safeguard-badge");
  const cuota = (veredicto.salvaguarda_paridad.cuota_femenina * 100).toFixed(1);
  if (veredicto.salvaguarda_paridad.cumple) {
    safeguardBadge.textContent = `Cumple Mandato (${cuota} %)`;
    safeguardBadge.className = "text-xs font-mono font-medium px-2 py-0.5 rounded badge-certified";
  } else {
    safeguardBadge.textContent = `Incompleto (${cuota} %)`;
    safeguardBadge.className = "text-xs font-mono font-medium px-2 py-0.5 rounded badge-review";
  }
}

function renderMetrics(metricas) {
  // Porcentajes de Voz
  const vFem = metricas.voz_pct.mujer || 0;
  const vMasc = metricas.voz_pct.hombre || 0;
  const vUndet = metricas.voz_pct.no_determinado || 0;

  document.getElementById("voice-fem-val").textContent = `${vFem.toFixed(1)} %`;
  document.getElementById("voice-masc-val").textContent = `${vMasc.toFixed(1)} %`;
  document.getElementById("voice-bar-fem").style.width = `${vFem}%`;
  document.getElementById("voice-bar-masc").style.width = `${vMasc}%`;

  // Porcentajes de Pantalla
  const pFem = metricas.pantalla_pct.mujer || 0;
  const pMasc = metricas.pantalla_pct.hombre || 0;
  const pUndet = metricas.pantalla_pct.no_determinado || 0;

  document.getElementById("screen-fem-val").textContent = `${pFem.toFixed(1)} %`;
  document.getElementById("screen-masc-val").textContent = `${pMasc.toFixed(1)} %`;
  document.getElementById("screen-bar-fem").style.width = `${pFem}%`;
  document.getElementById("screen-bar-masc").style.width = `${pMasc}%`;

  // Ratio Voz/Pantalla
  const ratioFem = metricas.ratio_voz_pantalla.mujer || 0;
  const ratioMasc = metricas.ratio_voz_pantalla.hombre || 0;
  document.getElementById("ratio-fem-val").textContent = ratioFem.toFixed(2);
  document.getElementById("ratio-masc-val").textContent = ratioMasc.toFixed(2);
}

function renderConstellation(data) {
  const container = document.getElementById("constellation-network");
  if (!container || !window.vis) return;

  const isDark = document.documentElement.classList.contains("dark");
  const nodeFontColor = isDark ? "#f8fafc" : "#1e293b";
  const nodeStrokeColor = isDark ? "#0f172a" : "#ffffff";
  const defaultEdgeColor = isDark ? "#334155" : "#cbd5e1";

  // Mapeo riguroso de nodos con colores institucionales
  const visNodes = data.nodos.map(n => {
    let color = "#64748b"; // Gris neutro
    let shape = "dot";
    let size = Math.max(12, Math.min(36, Math.sqrt(n.size || 10) * 4));

    if (n.tipo === "participante") {
      if (n.genero === "mujer") {
        color = { background: "#7c3aed", border: "#5b21b6", highlight: { background: "#6d28d9", border: "#4c1d95" } };
      } else if (n.genero === "hombre") {
        color = { background: "#0284c7", border: "#0369a1", highlight: { background: "#0ea5e9", border: "#0284c7" } };
      } else {
        color = { background: "#94a3b8", border: "#64748b" };
      }
    } else if (n.tipo === "tema") {
      shape = "hexagon";
      color = { background: "#d97706", border: "#b45309", highlight: { background: "#f59e0b", border: "#d97706" } };
      size = 18;
    }

    const displayName = n.tipo === "participante" 
      ? getDisplayName({ nombre: n.label, id: n.id, genero: n.genero, cargo: n.cargo }, state.anonymized)
      : n.label;

    return {
      id: n.id,
      label: displayName,
      title: `${displayName}${n.cargo && !state.anonymized ? ' (' + n.cargo + ')' : ''}`,
      color: color,
      shape: shape,
      size: size,
      font: { face: "Inter", size: 12, color: nodeFontColor, strokeWidth: 2, strokeColor: nodeStrokeColor }
    };
  });

  // Mapeo de aristas
  const visEdges = data.aristas.map(e => {
    let dashes = false;
    let edgeColor = defaultEdgeColor;
    let width = Math.min(4, Math.max(1, e.peso || 1));

    if (e.tipo === "menciona") {
      edgeColor = "#818cf8";
      dashes = [4, 4];
    } else if (e.tipo === "comparte_plano") {
      edgeColor = defaultEdgeColor;
    } else if (e.tipo === "habla_de") {
      edgeColor = "#fcd34d";
    }

    return {
      from: e.source,
      to: e.target,
      color: { color: edgeColor, highlight: "#6366f1" },
      width: width,
      dashes: dashes,
      arrows: e.tipo === "menciona" || e.tipo === "turno" ? "to" : ""
    };
  });

  const options = {
    physics: {
      stabilization: { iterations: 120 },
      barnesHut: { gravitationalConstant: -3000, springLength: 90, springConstant: 0.04 }
    },
    interaction: {
      hover: true,
      zoomView: false, // BLOQUEADO: El scroll con rueda no secuestra la página
      dragView: true,  // Permite arrastrar el lienzo libremente con el ratón
      dragNodes: true
    }
  };

  if (state.networkInstance) {
    state.networkInstance.destroy();
  }

  state.networkInstance = new vis.Network(container, { nodes: visNodes, edges: visEdges }, options);

  // Inicialización de controles de zoom externos (solo una vez)
  setupGraphControls(container);
}

// Vinculación de botones de zoom y soporte opcional de Ctrl + Rueda
let graphControlsConfigured = false;
function setupGraphControls(container) {
  if (graphControlsConfigured) return;
  graphControlsConfigured = true;

  const btnIn = document.getElementById("graph-zoom-in");
  const btnOut = document.getElementById("graph-zoom-out");
  const btnFit = document.getElementById("graph-zoom-fit");

  if (btnIn) {
    btnIn.addEventListener("click", () => {
      if (!state.networkInstance) return;
      const scale = state.networkInstance.getScale();
      state.networkInstance.moveTo({ scale: scale * 1.3, animation: { duration: 200 } });
    });
  }

  if (btnOut) {
    btnOut.addEventListener("click", () => {
      if (!state.networkInstance) return;
      const scale = state.networkInstance.getScale();
      state.networkInstance.moveTo({ scale: scale * 0.77, animation: { duration: 200 } });
    });
  }

  if (btnFit) {
    btnFit.addEventListener("click", () => {
      if (!state.networkInstance) return;
      state.networkInstance.fit({ animation: { duration: 300 } });
    });
  }

  // Si el usuario mantiene pulsada la tecla Ctrl, permite zoom intencionado con la rueda
  if (container) {
    container.addEventListener("wheel", (e) => {
      if (e.ctrlKey) {
        e.preventDefault();
        if (!state.networkInstance) return;
        const scale = state.networkInstance.getScale();
        const factor = e.deltaY < 0 ? 1.15 : 0.85;
        state.networkInstance.moveTo({ scale: scale * factor });
      }
      // Sin Ctrl, la rueda hace scroll normal por toda la página web sin interrupción
    }, { passive: false });
  }
}

function renderPersonsTable(personas) {
  const tbody = document.getElementById("persons-table-body");
  if (!tbody) return;
  tbody.innerHTML = "";

  personas.forEach(p => {
    const tr = document.createElement("tr");
    
    // Distintivo de género
    let gBadge = `<span class="px-2 py-0.5 rounded text-xs font-mono font-medium bg-slate-100 text-slate-700">${p.genero}</span>`;
    if (p.genero === "mujer") {
      gBadge = `<span class="px-2 py-0.5 rounded text-xs font-mono font-medium bg-purple-100 text-purple-800">Mujer</span>`;
    } else if (p.genero === "hombre") {
      gBadge = `<span class="px-2 py-0.5 rounded text-xs font-mono font-medium bg-sky-100 text-sky-800">Hombre</span>`;
    }

    // Autoridad institucional
    const authIcon = p.autoridad 
      ? `<span class="text-xs px-1.5 py-0.5 rounded font-mono bg-emerald-100 text-emerald-800 font-semibold" title="Rótulo OCR de Autoridad Institucional">Acreditada</span>`
      : `<span class="text-xs px-1.5 py-0.5 rounded font-mono bg-slate-100 text-slate-500">Testimonio</span>`;

    const displayName = getDisplayName(p, state.anonymized);
    const displayCargo = state.anonymized && p.cargo ? "Acreditado (Rótulo OCR)" : (p.cargo || "—");

    tr.innerHTML = `
      <td class="font-medium text-slate-900">${displayName}</td>
      <td class="text-slate-600">${displayCargo}</td>
      <td>${gBadge}</td>
      <td>${authIcon}</td>
      <td class="font-mono text-right">${p.pantalla_s ? p.pantalla_s.toFixed(1) + ' s' : '0.0 s'}</td>
      <td class="font-mono text-right font-medium">${p.voz_s ? p.voz_s.toFixed(1) + ' s' : '0.0 s'}</td>
      <td class="font-mono text-right text-slate-600">${p.centralidad !== undefined ? p.centralidad.toFixed(2) : '—'}</td>
    `;
    tbody.appendChild(tr);
  });
}

function renderClimate(clima) {
  const container = document.getElementById("climate-container");
  if (!container || !clima) return;

  const mTec = clima.mujer?.["técnico/asertivo"] || 0;
  const mCol = clima.mujer?.["colaborativo"] || 0;
  const hTec = clima.hombre?.["técnico/asertivo"] || 0;
  const hCol = clima.hombre?.["colaborativo"] || 0;

  document.getElementById("clima-fem-tec").textContent = `${mTec} %`;
  document.getElementById("clima-fem-col").textContent = `${mCol} %`;
  document.getElementById("clima-masc-tec").textContent = `${hTec} %`;
  document.getElementById("clima-masc-col").textContent = `${hCol} %`;
}

function updateComplianceCertificate() {
  const certBadge = document.getElementById("cert-status-badge");
  const sealHash = document.getElementById("cert-sha256-hash");
  const certDesc = document.getElementById("cert-status-desc");

  if (state.supervisionAsumida) {
    certBadge.textContent = "CONFORME · ART. 14 RIA ASUMIDO";
    certBadge.className = "px-3 py-1 text-xs font-mono font-bold rounded badge-certified";
    sealHash.textContent = "SHA-256: 4e8b89d9f1c79e65c0b8923a1a6f0d98e762c94f58f7129548b26127cb4165ea";
    certDesc.textContent = "Supervisión humana formalmente asumida por la persona operadora. Dictamen válido como auditoría audiovisual de paridad.";
  } else {
    certBadge.textContent = "BORRADOR · REVISIÓN INTERNA";
    certBadge.className = "px-3 py-1 text-xs font-mono font-bold rounded badge-review";
    sealHash.textContent = "SHA-256: [BLOQUEADO POR REVISIÓN HUMANA]";
    certDesc.textContent = "ADVERTENCIA: La operadora ha revocado la asunción técnica. Este documento no es apto como sello público conforme al Reglamento Europeo de IA.";
  }
}

function setupCitizenVoting() {
  const btnYes = document.getElementById("vote-yes-btn");
  const btnPartial = document.getElementById("vote-partial-btn");
  const btnNo = document.getElementById("vote-no-btn");
  const countEl = document.getElementById("citizen-vote-count");
  const statusEl = document.getElementById("citizen-status-msg");

  function updateDisplay() {
    const total = state.citizenVotes.yes + state.citizenVotes.partial + state.citizenVotes.no;
    const approval = Math.round((state.citizenVotes.yes / total) * 100);
    if (countEl) countEl.textContent = `${approval} % de aprobación (${total} valoraciones registradas)`;
  }

  updateDisplay();

  const handleVote = (type) => {
    if (state.userHasVoted) return;
    state.citizenVotes[type]++;
    state.userHasVoted = true;
    updateDisplay();

    if (statusEl) {
      statusEl.textContent = "¡Voto ciudadano registrado en el expediente! Gracias por auditar la soberanía informativa.";
      statusEl.className = "text-xs font-medium text-purple-700 bg-purple-50 p-2 rounded border border-purple-200 mt-2";
    }

    [btnYes, btnPartial, btnNo].forEach(btn => {
      if (btn) btn.disabled = true;
    });
  };

  if (btnYes) btnYes.addEventListener("click", () => handleVote("yes"));
  if (btnPartial) btnPartial.addEventListener("click", () => handleVote("partial"));
  if (btnNo) btnNo.addEventListener("click", () => handleVote("no"));
}

