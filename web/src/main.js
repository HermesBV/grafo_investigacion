import {UndirectedGraph} from 'graphology';
import Sigma from 'sigma';
import {getThresholdLimits} from './filter-core.mjs';
import {MultiSelect} from './multiselect.mjs';
import './style.css';

const $=id=>document.getElementById(id);
const multi={
  type:new MultiSelect($('project-type-filter'),{id:'project-type',label:'Tipo de proyecto',allLabel:'Todos los tipos',plural:'tipos seleccionados'}),
  unit:new MultiSelect($('unit-filter'),{id:'unit',label:'Unidad académica',allLabel:'Todas las unidades',plural:'unidades seleccionadas'}),
  role:new MultiSelect($('role-filter'),{id:'role',label:'Rol en el proyecto',allLabel:'Todos los roles',plural:'roles seleccionados'}),
};
const format=new Intl.NumberFormat('es-AR');
const num=n=>format.format(n);
const esc=value=>String(value).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const roleLabels={'DIRECTOR':'Director/a','CODIRECTOR':'Codirector/a','ESTUDIANTE':'Estudiante','ESTUDIANTE DE GRADO':'Estudiante de grado','INVESTIGADOR EN FORMACION':'Investigador/a en formación','INVESTIGADOR TESISTA':'Investigador/a tesista','INVESTIGADOR DE APOYO':'Investigador/a de apoyo','INVESTIGADOR ASESOR':'Investigador/a asesor/a','INVESTIGADOR FORMADO':'Investigador/a formado/a','SIN ROL':'Sin rol informado'};
let data,renderer,graph,result,selected=null,worker,requestId=0,visiblePeople=30,moreLabels=false;
let peopleOrder=[],maxPrestige=1;
const filters=()=>({types:multi.type.values(),units:multi.unit.values(),roles:multi.role.values(),name:$('name').value,code:$('code').value,title:$('title').value,neighbors:$('neighbors').checked,minConnections:$('min-connections').value,minProjects:$('min-projects').value});
const isMobile=()=>matchMedia('(max-width: 800px)').matches;

function color(prestige) {
  const t=Math.log1p(prestige)/Math.log1p(maxPrestige);
  const stops=[[53,121,115],[113,162,135],[211,181,102],[183,87,46]];
  const scaled=Math.min(2.9999,t*3), i=Math.floor(scaled), f=scaled-i;
  return `rgb(${stops[i].map((v,j)=>Math.round(v+(stops[i+1][j]-v)*f)).join(',')})`;
}
const size=prestige=>.4+3.4*Math.sqrt(prestige/maxPrestige);
const edgeColor=weight=>weight>=3?'#b96f49':weight===2?'#5b968b':'#8aafa6';
function fade(color,opacity=1) {
  let rgb=color.startsWith('#')?[1,3,5].map(i=>parseInt(color.slice(i,i+2),16)):color.match(/\d+/g).map(Number);
  return `rgb(${rgb.map((v,i)=>Math.round(v*opacity+[244,246,240][i]*(1-opacity))).join(',')})`;
}

function setStatus(title,message,kind='loading') {
  $('status').hidden=false;
  $('status').className=`status ${kind}`;
  $('status').innerHTML=`${kind==='loading'?'<div class="spinner"></div>':''}<h2>${esc(title)}</h2><p>${esc(message)}</p>${kind==='error'?'<button class="button" id="retry">Volver a intentar</button>':''}`;
  $('retry')?.addEventListener('click',()=>location.reload());
}

function makeRenderer() {
  const options={stagePadding:55,itemSizesReference:'screen',minEdgeThickness:.3,labelDensity:.35,labelGridCellSize:110,labelRenderedSizeThreshold:8,
    hideEdgesOnMove:false,hideLabelsOnMove:false,minCameraRatio:.003,maxCameraRatio:3,enableEdgeEvents:true,enableCameraRotation:false,
    labelColor:{color:'#213f3d'},labelSize:11,labelFont:'Arial',zIndex:true,
    nodeReducer:(id,a)=>({...a,color:fade(a.color,a.opacity),forceLabel:a.focused,highlighted:a.focused,zIndex:a.focused?1:0}),
    defaultDrawNodeLabel:(context,node,settings)=>{
      if(!node.label)return;
      context.font=`${settings.labelWeight} ${settings.labelSize}px ${settings.labelFont}`;
      context.fillStyle=settings.labelColor.color;
      const width=context.measureText(node.label).width;
      const canvasWidth=context.canvas.width/context.getTransform().a;
      let x=node.x+node.size+4;
      if(x+width>canvasWidth-6)x=Math.max(6,node.x-node.size-4-width);
      context.fillText(node.label,x,node.y+settings.labelSize/3);
    },
    edgeReducer:(id,a)=>({...a,color:fade(a.color,a.opacity)})};
  renderer=new Sigma(graph,$('graph'),options);
  renderer.on('clickNode',({node})=>selectPerson(Number(node),false));
  renderer.on('clickStage',()=>clearSelection());
  renderer.on('clickEdge',({edge})=>{
    const [a,b]=graph.extremities(edge).map(Number), weight=graph.getEdgeAttribute(edge,'weight');
    const common=result.projects.filter(pi=>{
      const m=data.projects[pi][3].map(m=>m[0]);return m.includes(a)&&m.includes(b);
    });
    $('inspector').hidden=false;
    $('inspector').innerHTML=`<div class="inspector-top"><span class="eyebrow">CONEXIÓN</span><button class="icon-button" data-action="close" aria-label="Cerrar detalle">×</button></div><h2>${esc(data.nodes[a][1])}</h2><p class="connection-and">↔</p><h2>${esc(data.nodes[b][1])}</h2><div class="connection-weight"><strong>${num(weight)}</strong> ${weight===1?'proyecto compartido':'proyectos compartidos'}</div><div class="project-list">${common.map(projectCard).join('')}</div>`;
  });
}

function applyResult(next) {
  result=next;
  graph=new UndirectedGraph();
  const central=$('layout').value==='centrality';
  const viewScale=result.nodes.length<150?3:result.nodes.length<1500?1.5:1;
  for (const i of result.nodes) {
    const n=data.nodes[i];
    graph.addNode(String(i),{label:n[1],x:n[central?8:6],y:n[central?9:7],size:size(n[2])*viewScale,color:color(n[2]),opacity:1,focused:false});
  }
  for (const [a,b,w] of result.edges) graph.addEdge(String(a),String(b),{weight:w,size:(.45+1.15*Math.log2(w))*viewScale,color:edgeColor(w),opacity:w>=3?.85:w===2?.65:.4,label:`${w} ${w===1?'proyecto':'proyectos'}`});
  try {
    if(renderer)renderer.setGraph(graph); else makeRenderer();
    renderer.setSetting('labelRenderedSizeThreshold',result.nodes.length<150?0:moreLabels?2:8);
    renderer.refresh();
    renderer.getCamera().animatedReset({duration:300});
    $('status').hidden=true;
  } catch(error) {
    console.error(error);
    setStatus('No se pudo iniciar el grafo','Este visor necesita WebGL 2. Podés seguir consultando las personas y sus proyectos en la lista.','error');
  }
  $('node-count').textContent=num(result.nodes.length);
  $('edge-count').textContent=num(result.edges.length);
  $('project-count').textContent=num(result.projects.length);
  $('graph').setAttribute('aria-busy','false');
  $('map-tip').hidden=result.nodes.length===0;
  if(!result.nodes.length)setStatus('No encontramos coincidencias','Probá con menos filtros o con otra palabra.','empty');
  let active=['name','code','title'].filter(id=>$(id).value.trim()).length+Object.values(multi).filter(select=>select.values().length>0).length
    +['min-connections','min-projects'].filter(id=>$(id).valueAsNumber>0).length;
  $('filter-count').textContent=active?`${active} ${active===1?'filtro activo':'filtros activos'}`:'Sin filtros activos';
  $('mobile-count').textContent=active?`(${active})`:'';
  peopleOrder=[...(result.matches.length?result.matches:result.nodes)].sort((a,b)=>data.nodes[b][2]-data.nodes[a][2]||data.nodes[a][1].localeCompare(data.nodes[b][1],'es'));
  visiblePeople=30;
  renderPeople();
  if(selected!==null && graph.hasNode(String(selected)))selectPerson(selected,false);else {selected=null;$('inspector').hidden=true;}
  document.documentElement.dataset.ready='true';
}

function renderPeople() {
  $('people-title').textContent=result.matches.length?'Integrantes encontrados':'Personas visibles';
  $('people-total').textContent=num(peopleOrder.length);
  $('people-help').textContent=result.matches.length&&$('neighbors').checked?'La red también incluye sus colaboradores.':'Ordenadas por prestigio acumulado.';
  $('people').innerHTML=peopleOrder.slice(0,visiblePeople).map(i=>{
    const n=data.nodes[i];return `<button class="person-row ${selected===i?'active':''}" data-node="${i}"><i style="background:${color(n[2])}"></i><span><strong>${esc(n[1])}</strong><small>${num(n[5])} ${n[5]===1?'proyecto':'proyectos'}</small></span><b title="Prestigio acumulado">${num(n[2])}</b></button>`;
  }).join('')+(peopleOrder.length>visiblePeople?`<button class="load-more text-button" id="more-people">Ver 30 personas más <span>↓</span></button>`:'')+(!peopleOrder.length?'<p class="people-empty">No hay personas con estos filtros.</p>':'');
  $('more-people')?.addEventListener('click',()=>{visiblePeople+=30;renderPeople();});
}

function projectCard(pi,person=null) {
  const p=data.projects[pi];
  const member=person===null?null:p[3].find(m=>m[0]===person);
  return `<article class="project-card"><div class="project-type-tag">${esc((p[6]??'UBACYT')==='UBACYT'?'UBACyT':p[6])}</div><button class="project-code" data-project="${pi}" title="Filtrar este proyecto">${esc(p[0])} ↗</button><h3>${esc(p[1][0]||'Sin título informado')}</h3>${p[1].length>1?`<details><summary>Otras versiones del título (${p[1].length-1})</summary>${p[1].slice(1).map(t=>`<p>${esc(t)}</p>`).join('')}</details>`:''}<p>${p[2].map(u=>esc(data.units[u])).join(' · ')}</p>${member?`<p class="project-role">${member[1].map(r=>esc(roleLabels[data.roles[r]]||data.roles[r])).join(' · ')}</p>`:''}<small>Listados ${p[4].join(' · ')}</small></article>`;
}

function selectPerson(i,focus=true) {
  selected=i;
  if(!graph?.hasNode(String(i)))return;
  const n=data.nodes[i], key=String(i), near=new Set(graph.neighbors(key));near.add(key);
  graph.updateEachNodeAttributes((id,a)=>({...a,opacity:near.has(id)?1:.15,focused:id===key}));
  graph.updateEachEdgeAttributes((edge,a,source,target)=>({...a,opacity:(source===key||target===key) ? .9 : .06}));
  const projects=result.projects.filter(pi=>data.projects[pi][3].some(m=>m[0]===i));
  $('inspector').hidden=false;
  $('inspector').innerHTML=`<div class="inspector-top"><span class="eyebrow">INTEGRANTE</span><button class="icon-button" data-action="close" aria-label="Cerrar detalle">×</button></div><h2>${esc(n[1])}</h2><div class="person-metrics"><div><strong style="color:${color(n[2])}">${num(n[2])}</strong><span>prestigio</span></div><div><strong>${num(n[3])}</strong><span>colaboradores¹</span></div><div><strong>${num(n[5])}</strong><span>proyectos¹</span></div></div><p class="centrality-value">Centralidad de grado¹: ${(100*n[3]/Math.max(1,data.nodes.length-1)).toLocaleString('es-AR',{maximumFractionDigits:2})}%</p><button class="button primary full-width" data-action="groups">Ver sus grupos</button><div class="inspector-section"><h3>Proyectos en esta vista <span>${num(projects.length)}</span></h3></div><div class="project-list">${projects.map(pi=>projectCard(pi,i)).join('')}</div><p class="detail-note">¹ Valores acumulados en toda la base. En esta vista: ${num(graph.degree(key))} colaboradores. Los roles corresponden a los listados disponibles.</p>`;
  renderPeople();
  if(focus && renderer){
    const p=renderer.getNodeDisplayData(key);
    renderer.getCamera().animate({x:p.x,y:p.y,ratio:Math.min(renderer.getCamera().getState().ratio,.18)},{duration:500});
  }
  if(isMobile())document.body.classList.remove('filters-open');
}

function clearSelection() {
  selected=null;
  $('inspector').hidden=true;
  if(graph){
    graph.updateEachNodeAttributes((id,a)=>({...a,opacity:1,focused:false}));
    graph.updateEachEdgeAttributes((id,a)=>({...a,opacity:a.weight>=3?.85:a.weight===2?.65:.4}));
  }
  if(data&&result)renderPeople();
}

function requestFilter() {
  if(!worker||!data)return;
  const minimumInputs=[$('min-connections'),$('min-projects')];
  minimumInputs.forEach(input=>input.setAttribute('aria-invalid',String(!input.validity.valid)));
  const invalid=minimumInputs.find(input=>!input.validity.valid);
  $('minimum-error').hidden=!invalid;
  $('minimum-error').textContent=invalid?`Ingresá un entero entre 0 y ${num(Number(invalid.max))} para el mínimo de ${invalid.id==='min-connections'?'conexiones':'proyectos'}. La red se actualiza con valores válidos.`:'';
  if(invalid) {
    requestId++;
    $('graph').setAttribute('aria-busy','false');
    document.documentElement.dataset.ready='true';
    return;
  }
  $('graph').setAttribute('aria-busy','true');
  document.documentElement.dataset.ready='false';
  worker.postMessage({type:'filter',id:++requestId,filters:filters()});
}

let debounce;
$('filters').addEventListener('submit',e=>e.preventDefault());
$('filters').addEventListener('input',e=>{clearTimeout(debounce);debounce=setTimeout(requestFilter,e.target.tagName==='INPUT'&&['search','number'].includes(e.target.type)?220:0);});
$('filters').addEventListener('reset',()=>{clearTimeout(debounce);setTimeout(()=>{Object.values(multi).forEach(select=>{select.refresh();select.setOpen(false);});requestFilter();},0);});
$('people').addEventListener('click',e=>{const button=e.target.closest('[data-node]');if(button)selectPerson(Number(button.dataset.node));});
$('inspector').addEventListener('click',e=>{
  const action=e.target.closest('[data-action]')?.dataset.action;
  if(action==='close')clearSelection();
  if(action==='groups'&&selected!==null){$('name').value=data.nodes[selected][1];$('neighbors').checked=true;requestFilter();}
  const project=e.target.closest('[data-project]');
  if(project){const p=data.projects[Number(project.dataset.project)];$('code').value=p[0];multi.type.setValues([p[6]??'UBACYT']);$('name').value='';requestFilter();}
});
$('layout').addEventListener('change',()=>{
  if(!graph)return;
  const central=$('layout').value==='centrality';
  $('layout-description').textContent=central?'Más colaboradores, más cerca del centro.':'Las colaboraciones acercan a las personas.';
  $('map-caption').textContent=central?'CENTRALIDAD DE GRADO · BASE COMPLETA':'UN PROYECTO COMPARTIDO, UNA CONEXIÓN';
  graph.updateEachNodeAttributes((id,a)=>({...a,x:data.nodes[Number(id)][central?8:6],y:data.nodes[Number(id)][central?9:7]}));
  renderer?.getCamera().animatedReset({duration:400});
});
$('zoom-in').addEventListener('click',()=>renderer?.getCamera().animatedZoom({duration:200}));
$('zoom-out').addEventListener('click',()=>renderer?.getCamera().animatedUnzoom({duration:200}));
$('fit').addEventListener('click',()=>renderer?.getCamera().animatedReset({duration:300}));
$('labels').addEventListener('click',()=>{
  moreLabels=!moreLabels;$('labels').setAttribute('aria-pressed',String(moreLabels));
  renderer?.setSetting('labelDensity',moreLabels?2:.35);
  renderer?.setSetting('labelRenderedSizeThreshold',moreLabels?0:result.nodes.length<150?0:8);
});
$('open-filters').addEventListener('click',()=>document.body.classList.add('filters-open'));
$('close-filters').addEventListener('click',()=>document.body.classList.remove('filters-open'));
const closeAbout=()=>$('methodology').close();
$('about').addEventListener('click',()=>$('methodology').showModal());
$('sources').addEventListener('click',()=>$('methodology').showModal());
$('close-about').addEventListener('click',closeAbout);$('done-about').addEventListener('click',closeAbout);
$('methodology').addEventListener('click',e=>{if(e.target===$('methodology'))closeAbout();});

async function init() {
  try {
    const response=await fetch(`${import.meta.env.BASE_URL}data/graph.json`);
    if(!response.ok)throw new Error(`Datos: HTTP ${response.status}`);
    data=await response.json();
    if(![1,2].includes(data.schemaVersion)||data.nodes.some(n=>n.length!==10))throw new Error('Formato de datos o layout inválido');
    maxPrestige=Math.max(...data.nodes.map(n=>n[2]));
    const limits=getThresholdLimits(data);
    for(const [id,max] of [['min-connections',limits.maxConnections],['min-projects',limits.maxProjects]]) {
      $(id).max=String(max);
      $(id).disabled=false;
      $(`${id}-range`).textContent=`Rango: 0–${num(max)}`;
    }
    $('prestige-min').textContent=num(Math.min(...data.nodes.map(n=>n[2])));
    $('prestige-max').textContent=num(maxPrestige);
    $('years').textContent=data.meta.years.join(' · ');
    multi.type.setOptions((data.types??['UBACYT']).map(t=>({value:t,label:t==='UBACYT'?'UBACyT':t})));
    multi.unit.setOptions(data.units.map((u,i)=>({value:i,label:u})));
    multi.role.setOptions(data.roles.map((r,i)=>({value:i,label:roleLabels[r]||r})));
    $('methodology-content').innerHTML=`<p>Una persona es un nodo. Dos personas están conectadas cuando integran un mismo proyecto de investigación. La red reúne los listados ${data.meta.years.join(', ')}: <strong>${num(data.meta.nodes)} personas, ${num(data.meta.edges)} conexiones y ${num(data.meta.projects)} proyectos</strong>.</p><h3>Prestigio → tamaño y color</h3><p>Es la suma de puntos por proyecto distinto. Si una persona tiene varios roles en el mismo proyecto, se toma el mayor puntaje observado. El valor se conserva al filtrar.</p><table><thead><tr><th>Rol</th><th>Puntos</th></tr></thead><tbody>${Object.entries(data.meta.roleScores).map(([r,p])=>`<tr><td>${esc(roleLabels[r]||r)}</td><td>${p}</td></tr>`).join('')}</tbody></table><h3>Peso → grosor y color de la conexión</h3><p>El peso suma las ponderaciones de los proyectos compartidos según su tipo. Actualmente cada proyecto UBACyT suma 1. Los pesos se vuelven a calcular con los proyectos seleccionados. El color distingue peso 1, 2 y 3 o más; el grosor sigue aumentando con el peso.</p><h3>Dos formas de ordenar la red</h3><p><strong>Colaboraciones</strong> detecta comunidades con Louvain y ordena las personas con ForceAtlas2. Los vínculos con mayor peso atraen más. Las posiciones se calculan con la red completa y se mantienen al filtrar; se ajusta el encuadre. <strong>Centralidad de grado</strong> coloca más cerca del centro a quienes tienen más colaboradores distintos en la base completa, con una escala logarítmica de la distancia. Cambiar la distribución no cambia el prestigio.</p><h3>Cómo se combinan los filtros</h3><p>Tipo, unidad, código y título seleccionan proyectos. El rol selecciona integrantes dentro de esos proyectos. Podés marcar varias opciones por desplegable: se incluyen las coincidencias con cualquiera de ellas (OR). Entre campos se deben cumplir todos los filtros (AND). Sin opciones marcadas se incluye todo. Integrante busca sin distinguir tildes o mayúsculas: con “Ver sus colaboradores” muestra sus grupos; al desactivarlo conserva solo las personas cuyo nombre coincide. Todos los campos se combinan. Los listados y los roles se acumulan entre años.</p><p>Los mínimos de conexiones y proyectos se aplican a los totales de cada persona en toda la base y deben cumplirse ambos. Conexiones cuenta colaboradores distintos; proyectos cuenta proyectos distintos. Admiten cualquier entero del rango indicado. Un mínimo de 0 o un campo vacío no restringe.</p><h3>Alcance de los datos</h3><p>Son proyectos vigentes en los listados, no exclusivamente proyectos aprobados en ese año. Un proyecto se cuenta una sola vez aunque figure en varios años. Compartir un proyecto en la red acumulada no garantiza coincidencia temporal. Los nombres conservan sus tildes y puntuación para identificar personas; homónimos y variantes de escritura pueden necesitar revisión. El término “prestigio” designa únicamente el puntaje acordado.</p><h3>Fuentes originales</h3><ul>${data.meta.sources.filter(s=>data.meta.years.includes(s.year)).map(s=>`<li><a href="${esc(s.url)}" target="_blank" rel="noreferrer">Listado ${esc(s.type==='UBACYT'||!s.type?'UBACyT':s.type)} ${s.year} ↗</a></li>`).join('')}</ul><p><a href="https://github.com/bustosthl/grafo_investigacion/blob/main/docs/criterios_grafo_ubacyt.md" target="_blank" rel="noreferrer">Ver los criterios completos y la notebook ↗</a></p>`;
    worker=new Worker(new URL('./filter-worker.mjs',import.meta.url),{type:'module'});
    worker.onerror=e=>{console.error(e);setStatus('No se pudo procesar la red','Volvé a cargar la página para reintentar.','error');};
    worker.onmessage=({data:message})=>{
      if(message.type==='ready')requestFilter();
      if(message.type==='result'&&message.id===requestId)applyResult(message.result);
      if(message.type==='error'&&message.id===requestId) {
        $('graph').setAttribute('aria-busy','false');
        document.documentElement.dataset.ready='true';
        setStatus('No se pudieron aplicar los filtros',message.message,'empty');
      }
    };
    worker.postMessage({type:'init',data});
  } catch(error) {
    console.error(error);setStatus('No se pudieron cargar los datos','Revisá la conexión y volvé a intentar.','error');
  }
}
init();
