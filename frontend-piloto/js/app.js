// SPDX-FileCopyrightText: 2026 Equipo 1: Attention Is All She Needs (Alba Camiña García, Pilar de la Fuente Diez, Rocío Jiménez Villén)
// SPDX-License-Identifier: Apache-2.0

/* Constelación del Protagonismo: the mock-up of the pilot, drawn with its sample data, and the same page filled with
   the result of the API when a video is analysed (AIASNAdapter turns the API result into this page's data). */
(function () {
"use strict";
document.documentElement.lang='es';
const P={f:'#c06be0',fGlow:'205,150,245',m:'#74a0b4',mGlow:'140,175,195',u:'#9298b4',uGlow:'150,156,185',star:'235,235,255',edge:'150,140,215',edgeOn:'200,140,240',topic:'185,172,238',neb1:'124,90,220',neb2:'190,88,200'};
const SAMPLE={
  people:[
    {id:"marc",name:"Marc Vidal",role:"Moderador",g:"m",protag:.92,screen:22,voice:24,nx:.80,ny:.22,topics:["Liderazgo","Tecnología"],note:"Abre y cierra el acto. La mayor centralidad argumental de la mesa."},
    {id:"javier",name:"Prof. Javier Soto",role:"Experto",g:"m",protag:.86,screen:28,voice:31,nx:.57,ny:.46,topics:["Tecnología","Liderazgo","Financiación"],note:"El mayor tiempo de voz. Citado tres veces como referente."},
    {id:"carlos",name:"Carlos Mena",role:"Experto",g:"m",protag:.52,screen:19,voice:22,nx:.83,ny:.60,topics:["Tecnología","Financiación"],note:"Interrumpe en cuatro ocasiones a lo largo del debate."},
    {id:"elena",name:"Dra. Elena Ruiz",role:"Experta",g:"f",protag:.58,screen:15,voice:12,nx:.30,ny:.30,topics:["Ética","Tecnología"],note:"Experta en la materia, pero con menos voz que sus pares hombres."},
    {id:"nuria",name:"Nuria Camps",role:"Experta",g:"f",protag:.26,screen:9,voice:4,nx:.17,ny:.66,topics:["Cuidados","Ética"],note:"Aparece en pantalla pero apenas habla: presencia figurativa."},
    {id:"laura",name:"Laura Gil",role:"Testimonio",g:"f",protag:.2,screen:3,voice:3,nx:.41,ny:.80,topics:["Cuidados"],note:"Intervención breve, relegada al tramo final."},
    {id:"desc",name:"Interviniente",role:"Sin identificar",g:"u",protag:.12,screen:4,voice:4,nx:.55,ny:.15,topics:[],note:"Confianza de clasificación por debajo del umbral → «desconocido»."}
  ],
  topics:{"Tecnología":[.50,.37],"Liderazgo":[.70,.42],"Financiación":[.72,.24],"Ética":[.39,.53],"Cuidados":[.26,.85]},
  tlabel:{"Cuidados":"Cuidados / Conciliación"},
  edges:[["marc","Tecnología"],["marc","Liderazgo"],["javier","Tecnología"],["javier","Liderazgo"],["javier","Financiación"],["carlos","Tecnología"],["carlos","Financiación"],["elena","Ética"],["elena","Tecnología"],["nuria","Cuidados"],["nuria","Ética"],["laura","Cuidados"]],
  themes:[{t:"Cuidados / Conciliación",f:46,m:6},{t:"Ética",f:28,m:14},{t:"Tecnología",f:18,m:34},{t:"Liderazgo",f:5,m:24},{t:"Financiación",f:3,m:22}],
  irm:[{k:"Presencia en pantalla",v:27,w:"peso 30 %"},{k:"Tiempo de voz",v:19,w:"peso 30 %"},{k:"Protagonismo visual",v:38,w:"peso 20 %"},{k:"Autoridad · citas, abre/cierra",v:13,w:"peso 20 %"}]
};
let DATA=SAMPLE,LIVE=false;
const pr=id=>DATA.people.find(p=>p.id===id);
const gname=g=>g==='f'?'MUJER':g==='m'?'HOMBRE':g==='n'?'NO BINARIO':'DESCONOCIDO';
const reduce=matchMedia('(prefers-reduced-motion:reduce)').matches;
const $=id=>document.getElementById(id);
// Names and texts of a real video come from OCR and the LLM: always escaped before going into the page
const esc=s=>String(s==null?'':s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const es1=x=>x==null?'—':(Math.round(x*10)/10).toString().replace('.',',');
const es2=x=>x==null?'—':x.toFixed(2).replace('.',',');
const PEND='<span class="pend" title="Pendiente: el backend aún no lo calcula">—</span>';

/* ---- canvas ---- */
const cv=$('cv'),ctx=cv.getContext('2d');
let W=0,H=0,dpr=1,hover=null;
const field=Array.from({length:110},()=>({x:Math.random(),y:Math.random(),r:Math.random()*1.1+.3,a:Math.random()*.5+.15,ph:Math.random()*6.28}));
function resize(){const r=cv.getBoundingClientRect();dpr=Math.min(2,devicePixelRatio||1);W=r.width;H=r.height;cv.width=W*dpr;cv.height=H*dpr;ctx.setTransform(dpr,0,0,dpr,0,0)}
const px=(x,y)=>[x*W,y*H];
function neb(x,y,r,rgb,a){const g=ctx.createRadialGradient(x,y,0,x,y,r);g.addColorStop(0,`rgba(${rgb},${a})`);g.addColorStop(1,`rgba(${rgb},0)`);ctx.fillStyle=g;ctx.fillRect(0,0,W,H)}
function draw(t){
  ctx.clearRect(0,0,W,H);
  let bg=ctx.createLinearGradient(0,0,W,H);bg.addColorStop(0,'#0b0e22');bg.addColorStop(1,'#070912');ctx.fillStyle=bg;ctx.fillRect(0,0,W,H);
  neb(W*.62,H*.3,Math.max(W,H)*.55,P.neb1,.14);neb(W*.24,H*.86,Math.max(W,H)*.4,P.neb2,.1);
  for(const s of field){const[x,y]=px(s.x,s.y);const a=reduce?s.a:s.a*(.75+.25*Math.sin(t/900+s.ph));ctx.beginPath();ctx.arc(x,y,s.r,0,6.283);ctx.fillStyle=`rgba(${P.star},${a})`;ctx.fill()}
  // people on screen together: dotted, brighter the longer they share the frame
  const maxShared=Math.max(1,...(DATA.shared||[]).map(s=>s[2]));
  // always between people with a name or a voice; those of people who only appear, when hovering them
  for(const[a,b,sec] of DATA.shared||[]){const p=pr(a),q=pr(b),on=hover===a||hover===b;if(!on&&!(p.labeled&&q.labeled))continue;const[ax,ay]=px(p.nx,p.ny),[bx,by]=px(q.nx,q.ny);
    ctx.save();ctx.setLineDash([2,4]);ctx.beginPath();ctx.moveTo(ax,ay);ctx.lineTo(bx,by);
    ctx.strokeStyle=`rgba(${P.star},${on?.75:(hover?.08:.18+.4*sec/maxShared)})`;ctx.lineWidth=on?1.6:1.2;ctx.stroke();ctx.restore()}
  for(const[pid,top] of DATA.edges){const p=pr(pid),[tx,ty]=px(...DATA.topics[top]),[sx,sy]=px(p.nx,p.ny),on=hover===pid;ctx.beginPath();ctx.moveTo(sx,sy);ctx.lineTo(tx,ty);ctx.strokeStyle=on?`rgba(${P.edgeOn},.6)`:`rgba(${P.edge},${hover?.07:.16})`;ctx.lineWidth=on?1.6:1;ctx.stroke()}
  for(const key in DATA.topics){const[x,y]=px(...DATA.topics[key]);ctx.save();ctx.translate(x,y);ctx.rotate(Math.PI/4);ctx.strokeStyle=`rgba(${P.topic},${hover?.4:.6})`;ctx.lineWidth=1.3;ctx.strokeRect(-4,-4,8,8);ctx.restore()}
  for(const p of DATA.people){
    const[x,y]=px(p.nx,p.ny),base=7+p.protag*17,r=base*(hover===p.id?1.12:1),dim=hover&&hover!==p.id?.4:1;
    const glow=p.g==='f'?P.fGlow:p.g==='m'?P.mGlow:P.uGlow,core=p.g==='f'?P.f:p.g==='m'?P.m:P.u,tw=reduce?1:(.9+.1*Math.sin(t/700+p.nx*9));
    let b=ctx.createRadialGradient(x,y,0,x,y,r*3.4);b.addColorStop(0,`rgba(${glow},${.5*dim*tw})`);b.addColorStop(.4,`rgba(${glow},${.18*dim})`);b.addColorStop(1,`rgba(${glow},0)`);
    ctx.fillStyle=b;ctx.beginPath();ctx.arc(x,y,r*3.4,0,6.283);ctx.fill();
    let c=ctx.createRadialGradient(x-r*.3,y-r*.3,0,x,y,r);c.addColorStop(0,'#fff');c.addColorStop(.35,core);c.addColorStop(1,core);
    ctx.globalAlpha=dim;ctx.fillStyle=c;ctx.beginPath();ctx.arc(x,y,r,0,6.283);ctx.fill();
    if(p.g==='m'){ctx.lineWidth=Math.max(1,r*.09);ctx.strokeStyle='rgba(255,255,255,.62)';ctx.beginPath();ctx.arc(x,y,r,0,6.283);ctx.stroke();}
    else if(p.g!=='f'){ctx.lineWidth=1.5;ctx.strokeStyle='rgba(240,238,255,.9)';ctx.setLineDash([3,2.5]);ctx.beginPath();ctx.arc(x,y,r+1.6,0,6.283);ctx.stroke();ctx.setLineDash([]);}
    ctx.globalAlpha=1;
  }
}
// The sky twinkles only while it is on screen: off screen it would keep the main thread busy and make scrolling stutter
let raf,skyVisible=true;const loop=t=>{draw(t);raf=skyVisible?requestAnimationFrame(loop):0};
function start(){cancelAnimationFrame(raf);reduce?draw(0):raf=requestAnimationFrame(loop)}
new IntersectionObserver(([e])=>{const was=skyVisible;skyVisible=e.isIntersecting;if(skyVisible&&!was&&!reduce)start()}).observe(cv);

/* ---- overlay ---- */
const ov=$('ov');
function shortName(p){
  if(LIVE)return p.name.length>22?p.name.slice(0,21)+'…':p.name;
  return (p.name.startsWith('Dr')||p.name.startsWith('Prof'))?p.name:p.name.split(' ').slice(-1)[0];
}
function buildOverlay(){
  ov.innerHTML='';
  for(const key in DATA.topics){const[x,y]=DATA.topics[key];const l=document.createElement('div');l.className='tlabel';l.style.left=x*100+'%';l.style.top='calc('+y*100+'% + 10px)';l.textContent=DATA.tlabel[key]||key;ov.appendChild(l)}
  DATA.people.forEach(p=>{
    const base=7+p.protag*17,b=document.createElement('button');b.className='hit';b.type='button';
    b.style.left=p.nx*100+'%';b.style.top=p.ny*100+'%';b.style.width=b.style.height=(base*2.6)+'px';
    b.setAttribute('aria-label',LIVE?`${p.name}, ${gname(p.g).toLowerCase()}, ${es1(p.voice)} por ciento del tiempo de voz`:`${p.name}, ${gname(p.g).toLowerCase()}, protagonismo ${Math.round(p.protag*100)} por ciento`);
    const set=()=>{hover=p.id;showPerson(p.id);if(reduce)draw(0)};
    b.addEventListener('mouseenter',set);b.addEventListener('focus',set);b.addEventListener('click',set);ov.appendChild(b);
    if(LIVE&&!p.labeled)return;   // people on screen who never speak and have no name: star only
    const lab=document.createElement('div');lab.className='plabel';lab.style.left=p.nx*100+'%';lab.style.top='calc('+p.ny*100+'% + '+(base+9)+'px)';
    lab.innerHTML=p.g==='u'?`${esc(shortName(p))}<small>sin identificar</small>`:esc(shortName(p));ov.appendChild(lab);
  });
}
document.querySelector('.sky').addEventListener('mouseleave',()=>{hover=null;showDefault();if(reduce)draw(0)});

/* ---- tarjeta ---- */
const read=$('read');
function showDefault(){
  read.innerHTML=LIVE
    ?`<div class="rtag">Observación</div><h2>Lee el cielo</h2><div class="cue"><div>Cada estrella es una persona del vídeo; su <b>tamaño</b> es su tiempo de voz.</div><div class="m">El color y la forma indican el género percibido; los rombos, los temas de los que se habla.</div><div class="a">Pasa el cursor o toca una estrella para ver su ficha.</div></div>`
    :`<div class="rtag">Observación</div><h2>Lee el cielo</h2><div class="cue"><div>Las estrellas grandes concentran el <b>protagonismo</b>. Aquí, casi todas son de hombres.</div><div class="m">Las mujeres brillan en oro, pero son estrellas <b>pequeñas</b>: presentes, poco protagonistas.</div><div class="a">Pasa el cursor o toca una estrella para ver su ficha.</div></div>`;
}
function sharedWith(id){
  const w=(DATA.shared||[]).filter(s=>s[0]===id||s[1]===id).map(s=>[pr(s[0]===id?s[1]:s[0]),s[2]]).sort((a,b)=>b[1]-a[1]);
  return w.length?`<div class="pc-topics">Comparte plano con ${w.slice(0,4).map(([q,sec])=>`<span class="chip">${esc(q.name)} · ${es1(sec)} s</span>`).join('')}${w.length>4?` y ${w.length-4} más`:''}</div>`:'';
}
function showPerson(id){
  const p=pr(id),ratio=p.screen?p.voice/p.screen:null;
  const gcss=p.g==='f'?'background:rgba(192,107,224,.18);color:#d08ce8':p.g==='m'?'background:rgba(116,160,180,.18);color:#93b8c9':'background:var(--sky-line);color:var(--sky-mut)';
  const core=p.g==='f'?P.f:p.g==='m'?P.m:P.u,glow=p.g==='f'?P.fGlow:p.g==='m'?P.mGlow:P.uGlow;
  // with real data, how central and how big they are on screen; the mock-up's prominence and ratio otherwise
  const c3=LIVE?['Centralidad en plano',p.centralidad==null?PEND:es2(p.centralidad)]:['Protagonismo',Math.round(p.protag*100)];
  const c4=LIVE?['Área en plano',p.area==null?PEND:es1(p.area*100)+'%']
    :['Ratio voz / pantalla',`<span style="color:${ratio<.9?'#f0576e':'#6fcf9f'}">${ratio.toFixed(2)}</span>`];
  read.innerHTML=`<div class="pc-head"><span class="pc-star" style="background:radial-gradient(circle at 35% 35%,#fff,${core});box-shadow:0 0 20px 2px rgba(${glow},.6)"></span><div style="min-width:0"><div class="pc-name">${esc(p.name)}</div><div class="pc-role">${esc(p.role)}</div></div><span class="pc-g" style="${gcss}">${gname(p.g)}</span></div>
  <div class="pc-grid"><div class="pc-cell"><div class="ck">Tiempo en pantalla</div><div class="cv tnum">${LIVE?es1(p.screen):p.screen}%</div></div><div class="pc-cell"><div class="ck">Tiempo de voz</div><div class="cv tnum">${LIVE?es1(p.voice):p.voice}%</div></div><div class="pc-cell"><div class="ck">${c3[0]}</div><div class="cv tnum">${c3[1]}</div></div><div class="pc-cell"><div class="ck">${c4[0]}</div><div class="cv tnum">${c4[1]}</div></div></div>
  <div class="pc-topics">${p.topics.length?'Habla de '+p.topics.map(t=>`<span class="chip">${esc(DATA.tlabel[t]||t)}</span>`).join(''):'<span class="chip">Sin tema asignado</span>'}</div>${LIVE&&p.sesgoCargo!=null?`<div class="pc-topics">Su cargo en word2vec <span class="chip">«${esc(p.cargoEn)}» · sesgo ${p.sesgoCargo>0?'+':''}${es2(p.sesgoCargo)} ${p.sesgoCargo>.02?'hacia «she»':p.sesgoCargo<-.02?'hacia «he»':'neutro'}</span></div>`:''}${LIVE?sharedWith(p.id):''}<div class="pc-note">${esc(p.note)}</div>`;
}

/* ---- segregación (espejo) ---- */
const mirror=$('mirror');
// word2vec gender bias of the topic on the same axis as the mirror: towards "he" left, towards "she" right
const BIAS_MAX=.4;
function bias(s){
  if(s==null)return '<span class="mb none">sin dato de sesgo</span>';
  const x=50+Math.max(-1,Math.min(1,s/BIAS_MAX))*50,side=s>.02?'f':s<-.02?'m':'';
  return `<span class="mb" title="Sesgo de género en word2vec: ${s>0?'+':''}${es2(s)}"><span class="mb-track"><i class="${side}" style="left:${x}%"></i></span><span class="mb-v ${side}">${s>0?'+':''}${es2(s)}</span></span>`;
}
function renderMirror(){
  mirror.classList.toggle('bias',LIVE);
  mirror.innerHTML=LIVE&&!DATA.themes.length?'<div class="comp-pend">Sin datos.</div>':'';
  const MAX=LIVE?Math.max(1,...DATA.themes.map(th=>Math.max(th.f,th.m))):46;
  DATA.themes.forEach(th=>{
    const row=document.createElement('div');row.className='mrow';
    row.innerHTML=`<div class="mside l"><span class="bar" style="width:${th.m/MAX*100}%"></span><span class="bv">${LIVE?es1(th.m):th.m}</span></div><div class="mcat">${esc(th.t)}${LIVE?bias(th.sesgo):''}</div><div class="mside r"><span class="bar" style="width:${th.f/MAX*100}%"></span><span class="bv">${LIVE?es1(th.f):th.f}</span></div>`;
    mirror.appendChild(row);
  });
}

/* ---- mancuerna pantalla–voz ---- */
const dumb=$('dumb');
function renderDumb(rows){
  dumb.innerHTML=rows.length?'':'<div class="comp-pend">Sin datos.</div>';
  rows.forEach(d=>{
    const diff=d.voice-d.screen,neg=diff<0,dc=neg?'var(--crit)':'var(--good)';
    const lo=Math.min(d.screen,d.voice),hi=Math.max(d.screen,d.voice);
    const el=document.createElement('div');
    el.innerHTML=`<div class="db-top"><span class="db-name"><i style="background:${d.col}"></i>${d.name}</span><span class="db-gap" style="color:${dc}">${neg?'−':'+'}${Math.abs(diff).toFixed(1).replace('.',',')} pp de voz</span></div>
    <div class="db-track"><span class="db-seg" style="left:${lo}%;width:${hi-lo}%;background:color-mix(in srgb,${dc} 55%,transparent)"></span>
    <span class="db-dot p" style="left:${d.screen}%;color:${d.col}"></span>
    <span class="db-dot v" style="left:${d.voice}%;color:${d.col}"></span>
    <span class="db-cap up" style="left:${d.screen}%"><span>pantalla </span><b>${d.screen.toString().replace('.',',')}%</b></span>
    <span class="db-cap down" style="left:${d.voice}%"><b>${d.voice.toString().replace('.',',')}%</b><span> voz</span></span></div>`;
    dumb.appendChild(el);
  });
}

/* ---- composición índice ---- */
const comp=$('comp');
function renderComp(){
  comp.innerHTML='';
  if(!DATA.irm){comp.innerHTML='<div class="comp-pend">El índice de representación y sus cuatro señales aún no los calcula el backend: se mostrarán aquí cuando el equipo cierre su definición.</div>';return}
  DATA.irm.forEach(r=>{
    const c=r.v==null?'var(--faint)':r.v<40?'var(--crit)':r.v<70?'var(--warn)':'var(--good)';
    const el=document.createElement('div');el.className='crow';
    el.innerHTML=`<div><div class="cl">${r.k}</div><div class="cw">${r.w}</div></div><div class="cbar"><div class="cv" style="color:${c}">${r.v==null?'—':r.v}</div><div class="ctrack"><i style="width:${r.v||0}%;background:${c}"></i></div></div>`;
    comp.appendChild(el);
  });
}

/* ---- tabla para lectores de pantalla ---- */
function renderSr(){
  const tb=$('srdata');tb.innerHTML='';
  DATA.people.forEach(p=>{const tr=document.createElement('tr');tr.innerHTML=`<th scope="row">${esc(p.name)}</th><td>${gname(p.g).toLowerCase()}</td><td>${esc(p.role)}</td><td>${LIVE?es1(p.screen):p.screen}%</td><td>${LIVE?es1(p.voice):p.voice}%</td><td>${LIVE?'pendiente':Math.round(p.protag*100)}</td>`;tb.appendChild(tr)});
}

/* ---- tema ---- */
const tb=$('theme');
const curT=()=>document.documentElement.getAttribute('data-theme')||(matchMedia('(prefers-color-scheme:dark)').matches?'dark':'light');
tb.addEventListener('click',()=>{const n=curT()==='dark'?'light':'dark';document.documentElement.setAttribute('data-theme',n);try{localStorage.setItem('aiasn-t',n)}catch(e){}});
try{const s=localStorage.getItem('aiasn-t');if(s)document.documentElement.setAttribute('data-theme',s)}catch(e){}

/* ---- la misma página con el resultado de la API ---- */
const FLAG_ICON='<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M12 9v4M12 17h.01"/><path d="M10.3 3.9 1.8 18a2 2 0 0 0 1.7 3h17a2 2 0 0 0 1.7-3L13.7 3.9a2 2 0 0 0-3.4 0z"/></svg>';
const INFO_ICON='<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><circle cx="12" cy="12" r="9"/><path d="M12 11v5M12 8h.01"/></svg>';
// Test de Interlocución Femenina (doc 26 §5): what each state and diagnosis means, in plain words
const TIF_MOTIVO={sin_datos:'No hay tramos de género determinado.',sin_conversacion:'Solo habla una persona: no hay conversación.',
  sin_hombres:'Solo participan mujeres: el test mide si dialogan sin la mediación de un hombre.',
  sin_mujeres:'No aparece ninguna mujer.',una_mujer:'Solo aparece una mujer: no puede dialogar con otra.'};
const TIF_DIAG={supera:'Dos o más mujeres acreditadas dialogan directamente entre ellas.',
  parcial:'Dialogan entre ellas, pero falta el rótulo de nombre o cargo de alguna.',
  aislamiento_relacional:'Aislamiento relacional: las mujeres solo hablan a través de un hombre.',
  mujer_sin_voz:'Hay mujeres presentes que no llegan a hablar.'};
const TIF_REGLAS=[['regla_1_pluralidad_femenina','dos o más mujeres con voz'],['regla_2_identidad_propia','dos o más mujeres con rótulo'],
  ['regla_3_dialogo_horizontal','una mujer responde a otra']];
function tifLine(t){
  const name='<b>Test de Interlocución Femenina</b> <span class="rule">adaptación del test de Bechdel · orientativo</span>';
  if(t.estado==='no_evaluable')return[INFO_ICON,' ok',`${name} — <b>no evaluable</b>: ${esc(TIF_MOTIVO[t.motivo]||'')}`];
  if(t.estado==='no_supera')return[FLAG_ICON,'',`${name} — <b>no supera</b>: ${esc(TIF_MOTIVO[t.motivo]||'')}`];
  const ok=t.puntuacion===3,rules=TIF_REGLAS.map(([k,l])=>`${t.reglas[k]?'✓':'✕'} ${l}`).join(' · ');
  return[ok?OK_ICON:FLAG_ICON,ok?' ok':'',`${name} — <b>${ok?'supera':'no supera'} (${t.puntuacion}/3)</b>: ${esc(TIF_DIAG[t.diagnostico]||'')} <span class="rule">${rules}</span>`];
}
const OK_ICON='<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M20 6 9 17l-5-5"/></svg>';
function flag(el,on,html){el.className='vflag'+(on?'':' ok');el.innerHTML=(on?FLAG_ICON:OK_ICON)+`<div>${html}</div>`}
const pct=x=>x==null?'—':es1(x)+'<span class="unit">%</span>';

// empty: no video analysed yet, every figure blank (no sample data passed off as a result)
function renderLive(v,empty=false){
  LIVE=true;document.body.classList.add('live-data');   // real data: the report stacks its sections (see styles.css)
  // the roles section keeps the expert comparison in its card; authority, ideas and titles go in a row below it
  if(!$('role-more'))document.querySelector('.role').insertAdjacentHTML('afterend','<div class="role-more" id="role-more"><div id="role-auth"></div><div id="role-side"></div></div>');
  $('role-auth').innerHTML=$('role-side').innerHTML='';
  const W8={pantalla:['Presencia en pantalla','peso 30 %'],voz:['Tiempo de voz','peso 20 %'],espacio:['Protagonismo espacial · centralidad y área','peso 25 %'],autoridad:['Autoridad · provisional','peso 25 %']};
  const irm=v.index?Object.keys(W8).map(k=>({k:W8[k][0],w:W8[k][1],v:v.index.dims[k]==null?null:Math.round(v.index.dims[k])})):null;
  DATA={people:v.people,topics:v.topics,tlabel:{},edges:v.edges,shared:v.shared,themes:v.themes,irm:irm};
  const nf=v.people.filter(p=>p.g==='f').length,nm=v.people.filter(p=>p.g==='m').length;
  const tag=$('src-tag');tag.textContent=empty?'Sin datos':'Datos reales';tag.classList.toggle('real',!empty);
  $('src-desc').textContent=empty?'Elige un vídeo y pulsa «Analizar».':`Vídeo analizado · ${v.videoId} · ${v.people.length} personas`;
  $('legend-size').innerHTML='<span class="lg-shared">··· comparten plano</span> El tamaño de cada estrella es su tiempo de voz';
  cv.setAttribute('aria-label','Constelación del vídeo analizado: cada estrella es una persona; su tamaño es su tiempo de voz y su color y forma, el género percibido. Los datos completos están en la tabla siguiente.');

  // veredicto
  // the index: the gauge in the verdict, and its four signals in "Cómo se compone el índice"
  const ix=v.index,ixc=x=>x<40?'#f0576e':x<70?'#e0b14a':'#6fcf9f';   // the sky's critical, warning and good hues
  if(ix){
    const t=Math.round(ix.total);
    $('gauge').setAttribute('aria-label',`Índice de Representación ${t} sobre 100${ix.provisional?', provisional':''}`);
    $('gauge-arc').style.display='';$('gauge-arc').setAttribute('stroke-dasharray',`${t} 100`);$('gauge-arc').setAttribute('stroke',ixc(t));
    $('gauge-num').textContent=t;$('gauge-num').setAttribute('fill',ixc(t));
  }else{
    $('gauge').setAttribute('aria-label','Índice de Representación sin datos');
    $('gauge-arc').style.display='none';$('gauge-num').textContent='—';
  }
  document.querySelector('.vgauge .vg-s').textContent=ix&&ix.provisional?'0–100 · legal 40 · provisional':'0–100 · legal 40';
  $('v-screen').innerHTML=pct(v.screen.f);
  $('v-screen-s').textContent=`frente al ${es1(v.screen.m)} % de hombres`+(v.coverage.pantalla?` · ${es1(v.coverage.pantalla)} % sin género conocido`:'');
  $('v-ratio').textContent=es2(v.ratio);$('v-ratio').style.color=v.ratio!=null&&v.ratio<1?'var(--sky-crit)':'var(--sky-fg)';
  $('v-ratio-s').textContent=empty?'':v.ratio==null?'sin tiempo en pantalla':v.ratio<1?'aparecen más de lo que hablan':'hablan tanto o más de lo que aparecen';
  if(empty)$('v-screen-s').textContent='';
  $('v-refs').textContent=empty?'—':`${v.refs.f} : ${v.refs.m}`;
  flag($('flag-1'),v.underrep.on,v.underrep.on
    ?`<b>Infrarrepresentación.</b> ${esc(v.underrep.text)}`
    :'<b>Infrarrepresentación</b> — <b>no activada</b>: las mujeres alcanzan el 40 % del tiempo en pantalla, o hablan más de lo que aparecen.');
  const suelo=es1(v.parity.suelo==null?40:v.parity.suelo*100),cuota=es1(v.parity.cuota==null?null:v.parity.cuota*100);
  flag($('flag-4'),!v.parity.ok,v.parity.ok
    ?`<b>Salvaguarda de paridad cumplida.</b> Las mujeres tienen el ${cuota} % de la voz de género conocido; el mínimo es el ${suelo} %.`
    :`<b>Salvaguarda de paridad no cumplida.</b> Las mujeres tienen el ${cuota} % de la voz de género conocido, por debajo del mínimo del ${suelo} %.`);
  if(v.tif){const[ic,cls,html]=tifLine(v.tif),el=$('flag-3');el.className='vflag'+cls;el.innerHTML=ic+`<div>${html}</div>`}
  ['flag-1','flag-2','flag-4'].forEach(id=>{$(id).style.display=empty?'none':''});
  $('flag-3').style.display=empty||!v.tif?'none':'';
  flag($('flag-2'),v.washing.on,v.washing.on
    ?`<b>Equality-washing activado.</b> ${esc(v.washing.text)}`
    :'<b>Equality-washing</b> — <b>no activado</b>: no se da una alta presencia en pantalla (≥ 35 %) con poca voz (< 20 % o ratio voz/pantalla < 0,30).');

  // lectura fácil
  $('ez-list').innerHTML=(v.easy.length?v.easy:[empty?'Todavía no se ha analizado ningún vídeo.':'El resumen en lectura fácil no está disponible para este vídeo.']).map(s=>`<li>${esc(s)}</li>`).join('')
    +'<li>Cuando el sistema no está seguro de quién es una persona, una persona del equipo lo revisa.</li>';

  // i · temas
  $('cap-themes').textContent='De qué habla cada género: cada tema, como porcentaje de los temas que tratan sus hablantes. Bajo cada tema, ◆ su sesgo de género en word2vec: hacia la derecha se asocia a «she», hacia la izquierda a «he».';
  $('mirror-mc').textContent=empty?'':'◆ sesgo word2vec';
  mirror.setAttribute('aria-label','Segregación temática por género, como porcentaje de los temas que trata cada grupo, y sesgo de género de cada tema en word2vec (positivo hacia mujer, negativo hacia hombre). '+v.themes.map(t=>`${t.t}: mujeres ${es1(t.f)}, hombres ${es1(t.m)}, sesgo ${t.sesgo==null?'sin dato':es2(t.sesgo)}`).join('. ')+'.');
  renderMirror();

  // ii · pantalla–voz
  const rows=[{name:'Mujeres',screen:v.screen.f||0,voice:v.voice.f||0,col:'var(--f)'},{name:'Hombres',screen:v.screen.m||0,voice:v.voice.m||0,col:'var(--m)'}];
  dumb.setAttribute('aria-label','Brecha entre tiempo en pantalla y tiempo de voz. '+rows.map(d=>`${d.name}: ${es1(d.screen)} por ciento en pantalla y ${es1(d.voice)} por ciento de voz`).join('. ')+'.');
  renderDumb(empty?[]:rows);
  // the three quadrants of each gender's time: does she speak when she is on screen?
  const oldQ=$('quads');if(oldQ)oldQ.remove();
  const QS=[['c1','habla en pantalla'],['c2','en pantalla sin hablar'],['c3','habla fuera de pantalla']];
  const qbar=(name,q)=>!q?'':`<div class="q-row"><div class="q-name">${name} <span class="who">${es1(q.total)} s</span></div>`
    +`<div class="q-bar" role="img" aria-label="${name}: ${QS.map(([k,l])=>`${es1(q.pct[k])} por ciento ${l}`).join(', ')}.">`
    +QS.filter(([k])=>q.pct[k]).map(([k])=>`<span class="q ${k}" style="width:${q.pct[k]}%">${q.pct[k]>=8?Math.round(q.pct[k])+'%':''}</span>`).join('')+'</div></div>';
  if(!empty&&(v.quadrants.f||v.quadrants.m))dumb.insertAdjacentHTML('afterend',`<div class="quads" id="quads"><div class="q-t">Cómo se reparte su tiempo</div>`
    +qbar('Mujeres',v.quadrants.f)+qbar('Hombres',v.quadrants.m)
    +`<div class="q-lg">${QS.map(([k,l])=>`<span><i class="q ${k}"></i>${l}</span>`).join('')}</div>`
    +`<div class="q-note">Los tres cuadrantes de Vilaplana: si se ven y se oyen, si se ven pero no se oyen, o si se oyen sin verse.</div></div>`);

  // iii · poder (who opens, closes or interrupts is out of the pilot: only the mock-up shows it)
  document.querySelector('#s-poder .ex-cap').textContent='Señales de rol más allá de aparecer: cuántas personas distintas, dónde y cuánto ocupan en el plano y a quién se cita como referente.';
  const fig=(x,g)=>`<td class="fig ${g}">${empty?PEND:x}</td>`;
  $('power').innerHTML=
    `<tr><td>Personas distintas</td>${fig(v.power.distinct.f,'f')}${fig(v.power.distinct.m,'m')}</tr>`+
    `<tr><td>Centralidad media en plano<span class="who">1 en el centro del plano, 0 en una esquina</span></td>${fig(es2(v.power.central.f),'f')}${fig(es2(v.power.central.m),'m')}</tr>`+
    `<tr><td>Área media en plano<span class="who">parte del encuadre que ocupan</span></td>${fig(v.power.area.f==null?'—':es1(v.power.area.f*100)+' %','f')}${fig(v.power.area.m==null?'—':es1(v.power.area.m*100)+' %','m')}</tr>`+
    `<tr><td>Veces citado como referente</td>${fig(v.power.cited.f,'f')}${fig(v.power.cited.m,'m')}</tr>`;

  // iii · who is cited as a reference, by whom
  const old=$('refs-list');if(old)old.remove();
  if(!empty)$('power').closest('table').insertAdjacentHTML('afterend',`<div class="refs" id="refs-list"><div class="refs-t">Referentes citados</div>`
    +(v.power.references.length?'<ul>'+v.power.references.map(r=>`<li><span class="rchip ${r.g==='f'||r.g==='m'?r.g:'u'}">${esc(r.name)}</span><span class="who">${gname(r.g).toLowerCase()} · ${r.times} ${r.times===1?'vez':'veces'} · por ${r.by.map(esc).join(', ')||'—'}</span></li>`).join('')+'</ul>'
      :'<div class="who">Nadie cita a ninguna persona como referente en este vídeo.</div>')+'</div>');

  // iv · roles
  const chip=p=>`<span class="rchip ${p.g==='f'||p.g==='m'?p.g:'u'}">${esc(p.name)}</span>`;
  $('ladder').innerHTML=v.roles.map(r=>`<div class="rl-row"><div class="rl-tier">${esc(r.rol.charAt(0).toUpperCase()+r.rol.slice(1))}</div><div class="rl-people">${r.people.map(chip).join('')}</div></div>`).join('')
    +(v.undetermined?`<div class="rl-row"><div class="rl-tier">Sin identificar<span class="rl-sub">confianza bajo umbral</span></div><div class="rl-people"><span class="rchip u">${v.undetermined} ${v.undetermined===1?'interviniente':'intervinientes'}</span><span class="hil">Human-in-the-Loop · revisión humana</span></div></div>`:'');
  if(empty&&!v.roles.length)$('ladder').innerHTML='<div class="comp-pend">Sin datos.</div>';
  $('role-gap').innerHTML=empty?'<div class="rg-title">Misma etiqueta, distinta voz</div><div class="rg-cap">Sin datos.</div>':v.expertVoice
    ?`<div class="rg-title">Misma etiqueta, distinta voz</div><div class="rg-cap">Tiempo de voz de quienes figuran como <b>experto/a</b>, sobre el total del vídeo:</div><div class="rg-pair"><div class="rg-cell"><div class="rg-num" style="color:var(--f-ink)">${es1(v.expertVoice.f)} %</div><div class="rg-lab">Expertas</div></div><div class="rg-vs">frente a</div><div class="rg-cell"><div class="rg-num" style="color:var(--m-ink)">${es1(v.expertVoice.m)} %</div><div class="rg-lab">Expertos</div></div></div>`
    :`<div class="rg-title">Misma etiqueta, distinta voz</div><div class="rg-cap">${v.experts?'Quienes figuran como experto/a en este vídeo no tienen un género determinado: no hay comparación posible.':'En este vídeo nadie figura como experto/a.'}</div>`;

  // iv · autoridad: from what each gender speaks, how they are introduced and what ideas they bring
  const share=x=>x==null?'—':es1(x)+' %',arow=(label,sub,o)=>`<tr><td>${label}<span class="who">${sub}</span></td><td class="fig f">${empty?PEND:share(o.f)}</td><td class="fig m">${empty?PEND:share(o.m)}</td></tr>`;
  $('role-auth').insertAdjacentHTML('beforeend',`<table class="ledger auth"><caption class="sr-only">Autoridad, presentación e ideas, por género</caption><thead><tr><th>Dentro de cada género</th><th class="fig">Mujeres</th><th class="fig">Hombres</th></tr></thead><tbody>`
    +arow('Voz desde la autoridad','por rol o por rótulo con cargo',v.authority.voice)
    +arow('Presentadas con su cargo','al mencionarlas en la conversación',v.authority.title)+'</tbody></table>');
  // key ideas: who brings each, in groups that add up to 100
  const ideaSegs=[['f','solo mujeres',v.ideas.f],['m','solo hombres',v.ideas.m],['sh','compartidas entre géneros',v.ideas.shared],['u','solo voces sin género conocido',v.ideas.u]].filter(x=>x[2]);
  $('role-side').insertAdjacentHTML('beforeend',empty||!v.ideas.total?'':`<div class="ideas"><div class="ideas-t">Ideas clave de la pieza <span class="who">${v.ideas.total} ideas, según quién las aporta</span></div>`
    +`<div class="ideas-bar" role="img" aria-label="Ideas clave: ${ideaSegs.map(x=>`${es1(x[2])} por ciento ${x[1]}`).join(', ')}.">${ideaSegs.map(x=>`<span class="ib ${x[0]}" style="width:${x[2]}%">${Math.round(x[2])}%</span>`).join('')}</div>`
    +`<div class="ideas-lg">${ideaSegs.map(x=>`<span><i class="ib ${x[0]}"></i>${x[1]} · ${es1(x[2])} %</span>`).join('')}</div></div>`);

  // vii · supervisión humana (front only for now: decisions are not stored)
  renderReview(empty?[]:v.doubtful,empty);

  // iv · cargos: the word2vec gender bias of each title, on the same axis as the topics
  const titled=v.people.filter(p=>p.sesgoCargo!=null);
  if(!empty&&titled.length)$('role-side').insertAdjacentHTML('beforeend',`<table class="ledger auth titles"><caption class="sr-only">Sesgo de género en word2vec de cada cargo</caption><thead><tr><th>Cargo · persona</th><th class="fig">Sesgo word2vec</th></tr></thead><tbody>`
    +titled.map(p=>`<tr><td>${esc(p.cargoEn)}<span class="who">${esc(p.name)}</span></td><td class="fig">${bias(p.sesgoCargo)}</td></tr>`).join('')
    +`</tbody></table><div class="rg-note">◆ hacia la derecha, el cargo se asocia a «she»; hacia la izquierda, a «he» (w2vNEWS, Bolukbasi 2016).</div>`);

  // v · clima
  const bar=(name,col,c)=>!c?'':`<div class="cl-row"><div class="cl-top"><div class="cl-name"><i style="background:${col}"></i>${name}</div></div><div class="cl-bar" role="img" aria-label="${name}: ${es1(c.tec)} por ciento técnico-asertivo, ${es1(c.col)} por ciento colaborativo, ${es1(c.dis)} por ciento disenso.">${c.tec?`<div class="cl-seg tec" style="width:${c.tec}%">${Math.round(c.tec)}%</div>`:''}${c.col?`<div class="cl-seg col" style="width:${c.col}%">${Math.round(c.col)}%</div>`:''}${c.dis?`<div class="cl-seg dis" style="width:${c.dis}%">${Math.round(c.dis)}%</div>`:''}</div></div>`;
  $('clima-rows').innerHTML=(bar('Mujeres','var(--f)',v.clima.f)+bar('Hombres','var(--m)',v.clima.m))||`<div class="cl-note">${empty?'Sin datos.':'No hay turnos clasificados por tono en este vídeo.'}</div>`;
  $('clima-note').innerHTML='Los registros <b>técnico-asertivo</b> y <b>disenso</b> son los que una mesa suele leer como autoridad. No se trata de que un registro valga más: lo relevante es cómo se reparten entre géneros.';

  // vi · índice y cierre
  $('cap-comp').textContent='Media ponderada de cuatro señales (0–100), contrastada con la línea legal del 40 %. Provisional: la señal de autoridad aún está por definir con el equipo; hoy compara la voz desde la autoridad de mujeres y hombres y cuenta las mujeres entre los referentes citados.';
  renderComp();
  const mk=$('mk-screen');mk.hidden=empty;   // the scale ends at 50 %: beyond it, at the edge with its figure
  mk.style.left=Math.min(97,Math.max(0,(v.screen.f||0)*2))+'%';mk.querySelector('.num').textContent=es1(v.screen.f)+' %';
  $('foot-data').innerHTML=empty?'<b>Sin datos</b>: analiza un vídeo para ver aquí sus resultados. Proyecto de código abierto.':`<b>Datos reales</b> del vídeo ${esc(v.videoId)}, procesados por el backend de AIASN. Lo que el backend aún no calcula se marca con «—». Proyecto de código abierto.`;

  hover=null;buildOverlay();showDefault();renderSr();repaint();
}

/* ---- supervisión humana: decide each doubtful span; kept in memory until the backend stores them ---- */
let decisions={};
const CHOICES=[['mujer','Mujer'],['hombre','Hombre'],['no_determinable','No determinable']];
const mmss=s=>`${Math.floor(s/60)}:${String(Math.round(s%60)).padStart(2,'0')}`;
function renderReview(spans,empty){
  decisions={};
  const box=$('review'),tab=$('tab-supervision');
  box.style.display=tab.style.display=empty?'none':'';
  const body=$('rv-body');
  if(!spans.length){body.innerHTML='<tr><td colspan="3">No hay tramos dudosos en este vídeo: todos tienen un género determinado.</td></tr>';reviewCount(0);return}
  // one row and one decision per person, with the spans where they show
  body.innerHTML=spans.map(p=>{
    const when=p.spans.slice(0,4).map(([a,b])=>`${mmss(a)}–${mmss(b)}`).join(', ')+(p.spans.length>4?` y ${p.spans.length-4} más`:'');
    const said=p.textos.length?` · «${esc(p.textos[0].length>90?p.textos[0].slice(0,89)+'…':p.textos[0])}»`:'';
    return `<tr data-key="${esc(p.id)}"><td>${esc(p.persona)}<span class="who">${p.spans.length} ${p.spans.length===1?'tramo':'tramos'} · ${es1(p.segundos)} s</span></td>`
      +`<td class="rv-when">${when}<span class="who">${said||'sin voz en estos tramos'}</span></td>`
      +`<td><div class="rv-choices" role="group" aria-label="Género de ${esc(p.persona)}">`
      +CHOICES.map(([k,l])=>`<button type="button" class="rv-btn" data-choice="${k}" aria-pressed="false">${l}</button>`).join('')+'</div></td></tr>';
  }).join('');
  reviewCount(spans.length);
}
function reviewCount(total){
  const done=Object.keys(decisions).length;
  $('rv-count').innerHTML=total?`<b>${done} de ${total}</b> ${total===1?'persona revisada':'personas revisadas'}`:'Nada que revisar';
}
$('rv-body').addEventListener('click',e=>{
  const b=e.target.closest('.rv-btn');if(!b)return;
  const row=b.closest('tr'),key=row.dataset.key,again=decisions[key]===b.dataset.choice;
  if(again)delete decisions[key];else decisions[key]=b.dataset.choice;   // pressing the chosen one again undoes it
  row.querySelectorAll('.rv-btn').forEach(x=>x.setAttribute('aria-pressed',String(!again&&x===b)));
  reviewCount($('rv-body').querySelectorAll('tr[data-key]').length);
});

/* ---- análisis de un vídeo con la API ---- */
// Served by the front container, the API is under /api on the same origin; elsewhere, ?api=http://localhost:8000
const API=(new URLSearchParams(location.search).get('api')||'/api').replace(/\/+$/,'');
// In the order they run: audio → lenguaje and vídeo → rótulos side by side, then unificación and indicadores
const STEPS={audio:'audio',nlp:'NLP',video:'vídeo',captions:'OCR',silver:'unificación',gold:'KPIs'};
const SLOW_MS=60*1000;   // audio or vídeo still running after this: the first video downloads the models
const POLL_MS=3000,POLL_MAX_MS=60*60*1000,BUSY_RETRIES=3,BUSY_WAIT_MS=5000;
const sleep=ms=>new Promise(ok=>setTimeout(ok,ms));
const msg=t=>{$('live-msg').textContent=t};
function running(status){
  const pasos=(status&&status.pasos)||{},keys=Object.keys(STEPS);
  const run=keys.filter(k=>pasos[k]==='running'),next=keys.filter(k=>pasos[k]!=='ok')[0];
  return (run.length?run:next?[next]:[]).map(k=>STEPS[k]).join(' + ');
}
let tick;
function showSteps(status,t0){
  const pasos=(status&&status.pasos)||{},keys=Object.keys(STEPS),el=$('steps');
  const s=Math.round((Date.now()-t0)/1000),done=keys.filter(k=>pasos[k]==='ok').length;
  const slow=Date.now()-t0>SLOW_MS&&['audio','video'].some(k=>pasos[k]==='running');
  const state=k=>pasos[k]==='ok'?['done','✓','hecho']:pasos[k]==='running'?['run','●','en marcha']:pasos[k]==='error'?['err','✕','con error']:['todo','○','pendiente'];
  el.innerHTML=keys.map(k=>{const[c,ic,txt]=state(k);return `<li class="${c}"><span class="ic" aria-hidden="true">${ic}</span>${STEPS[k].charAt(0).toUpperCase()+STEPS[k].slice(1)}<span class="sr-only">: ${txt}</span></li>`}).join('')
    +`<li class="count">${done}/${keys.length} · ${Math.floor(s/60)}:${String(s%60).padStart(2,'0')}</li>`
    +(slow?'<li class="note">El primer vídeo descarga los modelos: puede tardar unos minutos más.</li>':'');
  el.style.display='';
  $('live-msg').classList.add('sr-only');   // the row says it; the message stays for screen readers
}
function hideSteps(){$('steps').style.display='none';$('live-msg').classList.remove('sr-only')}
$('live-file').addEventListener('change',e=>{const f=e.target.files[0];$('live-name').textContent=f?f.name:'Elegir vídeo'});
// Polls a video until it has a result, showing its steps; also after a reload (?video=ID while processing)
async function follow(id,t0){
  let last={pasos:{}};
  showSteps(last,t0);clearInterval(tick);tick=setInterval(()=>showSteps(last,t0),1000);   // the clock runs between polls
  try{
    for(;;){
      if(Date.now()-t0>POLL_MAX_MS)throw new Error('el análisis tarda demasiado');
      const r=await fetch(API+'/videos/'+encodeURIComponent(id));
      if(!r.ok)throw new Error(r.status===404?'vídeo desconocido':'HTTP '+r.status);
      const body=await r.json(),estado=body.status&&body.status.estado;
      last=body.status||last;showSteps(last,t0);
      if(estado==='error')throw new Error((body.status&&body.status.error)||'error');
      if(estado==='ok'&&body.resultado){renderLive(AIASNAdapter.toView(body));return}
      msg(estado==='en_cola'?'En cola…':`Procesando: ${running(body.status)} (${Object.values(last.pasos||{}).filter(x=>x==='ok').length} de 6)…`);
      await sleep(POLL_MS);
    }
  }finally{   // a failed step stays marked with its ✕ next to the error message
    clearInterval(tick);
    if($('steps').querySelector('.err'))$('live-msg').classList.remove('sr-only');else hideSteps();
  }
}
const failed=(err,what)=>msg(err instanceof TypeError?`No se pudo conectar con la API (${API}).`:what+err.message);

$('live').addEventListener('submit',async e=>{
  e.preventDefault();
  const file=$('live-file').files[0];
  if(!file){msg('Elige primero un vídeo.');return}
  const go=$('live-go'),t0=Date.now();go.disabled=true;
  try{
    msg('Enviando el vídeo…');
    const fd=new FormData();fd.append('file',file);
    let res=await fetch(API+'/videos',{method:'POST',body:fd});
    for(let i=0;res.status===409&&i<BUSY_RETRIES;i++){await sleep(BUSY_WAIT_MS);res=await fetch(API+'/videos',{method:'POST',body:fd})}
    if(res.status===409){msg('Ya se está procesando otro vídeo. Vuelve a intentarlo en unos minutos.');return}
    if(!res.ok)throw new Error('HTTP '+res.status);
    const id=(await res.json()).video_id;
    const u=new URL(location.href);u.searchParams.set('video',id);history.replaceState(null,'',u);   // a reload keeps following it
    await follow(id,t0);
    msg('Análisis completado.');listVideos();
  }catch(err){failed(err,'No se pudo completar el análisis: ')}
  finally{go.disabled=false}
});

// Videos already in the lake: one opens without processing it again
async function listVideos(){
  try{
    const r=await fetch(API+'/videos');if(!r.ok)return;
    const ok=(await r.json()).filter(v=>v.estado==='ok'),sel=$('live-open');
    sel.length=1;ok.forEach(v=>sel.add(new Option(v.video_id,v.video_id)));
    sel.style.display=ok.length?'':'none';
    if(opened)sel.value=opened;
  }catch(e){}   // without the API the page still works: the list just stays hidden
}
$('live-open').addEventListener('change',e=>{
  const id=e.target.value;if(!id)return;
  const u=new URL(location.href);u.searchParams.set('video',id);history.replaceState(null,'',u);
  openVideo(id);
});

// ?video=ID opens a video (to share or reload its result) without uploading it again
async function openVideo(id){
  try{msg('Cargando el resultado…');await follow(id,Date.now());msg('')}
  catch(err){failed(err,'No se pudo abrir el vídeo: ')}
}

renderMirror();renderDumb([{name:'Mujeres',screen:26.8,voice:19,col:'var(--f)'},{name:'Hombres',screen:69,voice:77,col:'var(--m)'}]);renderComp();renderSr();
buildOverlay();showDefault();resize();start();
function repaint(){resize();if(reduce)draw(performance.now())}
requestAnimationFrame(repaint);addEventListener('load',repaint);
setTimeout(repaint,180);setTimeout(repaint,600);setTimeout(repaint,1400);
let rt;addEventListener('resize',()=>{clearTimeout(rt);rt=setTimeout(repaint,120)});
/* ---- pestañas: la sección en la que está la lectura, y el alto de la cabecera fija para no taparla ---- */
(function(){
  const top=document.querySelector('.top'),links=[...document.querySelectorAll('.tabs a')];
  const tabs=document.querySelector('.tabs'),root=document.documentElement.style;
  const setTop=()=>{   // the fixed bars, so that a section does not land under them
    root.setProperty('--top-h',(getComputedStyle(top).position==='sticky'?top.offsetHeight:0)+'px');
    root.setProperty('--tabs-h',tabs.offsetHeight+'px');
  };
  setTop();addEventListener('resize',setTop);
  // The current section: the last one whose start has gone past 40 % of the screen; the first one at the top
  const sections=links.map(a=>[a,document.getElementById(a.getAttribute('href').slice(1))]).filter(([,el])=>el);
  let shown=null,queued=false;
  const mark=()=>{
    queued=false;
    const line=innerHeight*.4;
    let current=sections[0];
    for(const s of sections)if(s[1].offsetParent!==null&&s[1].getBoundingClientRect().top<=line)current=s;   // hidden: skip
    if(current[0]===shown)return;
    if(shown)shown.removeAttribute('aria-current');
    shown=current[0];shown.setAttribute('aria-current','true');
    // keep it visible in the tab strip on a phone, moving only the strip (scrollIntoView would also move the page)
    const ul=shown.closest('ul'),a=shown.offsetLeft,b=a+shown.offsetWidth;
    if(a<ul.scrollLeft)ul.scrollLeft=a-8;else if(b>ul.scrollLeft+ul.clientWidth)ul.scrollLeft=b-ul.clientWidth+8;
  };
  addEventListener('scroll',()=>{if(!queued){queued=true;requestAnimationFrame(mark)}},{passive:true});
  addEventListener('resize',mark);mark();
})();

const params=new URLSearchParams(location.search),opened=params.get('video');
if(!params.has('demo'))renderLive(AIASNAdapter.toView({resultado:{}}),true);   // ?demo: the mock-up with its sample data
if(opened)openVideo(opened);
listVideos();
})();
