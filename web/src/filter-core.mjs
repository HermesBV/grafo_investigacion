// Esquema compacto documentado en docs/visor_web.md. Sin dependencias del DOM.
export const normalizeSearch = value => String(value ?? '').normalize('NFD').replace(/\p{M}/gu,'').toLocaleLowerCase('es').replace(/\s+/g,' ').trim();

export function getThresholdLimits(data) {
  return data.nodes.reduce((limits,node)=>({
    maxConnections:Math.max(limits.maxConnections,node[3]),
    maxProjects:Math.max(limits.maxProjects,node[5]),
  }),{maxConnections:0,maxProjects:0});
}

function minimum(value,max,label) {
  const parsed=value==null||String(value).trim()===''?0:Number(value);
  if(!Number.isSafeInteger(parsed)||parsed<0||parsed>max) {
    throw new RangeError(`${label}: ingresá un número entero entre 0 y ${max}.`);
  }
  return parsed;
}

export function prepareData(data) {
  return {
    limits:getThresholdLimits(data),
    names:data.nodes.map(n=>normalizeSearch(n[1])),
    projects:data.projects.map(p=>{
      const type=p[6]??'UBACYT';
      const weight=data.meta.projectTypeWeights?.[type]?.conexiones??(data.schemaVersion!==2?data.meta.edgeMultiplier:undefined);
      if(!Number.isFinite(weight)||weight<=0)throw new Error(`Falta el peso de conexiones para ${type}.`);
      return {code:normalizeSearch(p[0]),title:normalizeSearch(p[1].join(' ')),type,weight};
    }),
  };
}

function selection(values,numeric=false) {
  const selected=(Array.isArray(values)?values:[values]).filter(v=>v!==''&&v!=null).map(v=>numeric?Number(v):String(v));
  return selected.length?new Set(selected):null;
}

export function filterGraph(data, filters={}, index=prepareData(data)) {
  const name=normalizeSearch(filters.name), code=normalizeSearch(filters.code), title=normalizeSearch(filters.title);
  const roles=selection(filters.roles??filters.role,true), units=selection(filters.units??filters.unit,true);
  const types=selection(filters.types);
  const neighbors=filters.neighbors !== false;
  const minConnections=minimum(filters.minConnections,index.limits.maxConnections,'Mínimo de conexiones');
  const minProjects=minimum(filters.minProjects,index.limits.maxProjects,'Mínimo de proyectos');
  // Los umbrales usan los totales globales; ocultar vecinos no cambia la elegibilidad.
  const eligible=data.nodes.map(n=>n[3]>=minConnections&&n[5]>=minProjects);
  const visible=new Set(), matches=new Set(), projects=[], pairs=new Map();
  for (let pi=0; pi<data.projects.length; pi++) {
    const p=data.projects[pi], search=index.projects[pi];
    if(types&&!types.has(search.type))continue;
    if(units&&!p[2].some(u=>units.has(u)))continue;
    if (code && !search.code.includes(code)) continue;
    if (title && !search.title.includes(title)) continue;
    let members=p[3].filter(m=>eligible[m[0]]&&(!roles||m[1].some(r=>roles.has(r)))).map(m=>m[0]);
    if (name) {
      const selected=members.filter(n=>index.names[n].includes(name));
      if (!selected.length) continue;
      selected.forEach(n=>matches.add(n));
      if (!neighbors) members=selected;
    }
    if (!members.length) continue;
    projects.push(pi);
    members.forEach(n=>visible.add(n));
    for (let a=0; a<members.length; a++) for (let b=a+1; b<members.length; b++) {
      const x=Math.min(members[a],members[b]), y=Math.max(members[a],members[b]);
      const key=x*data.nodes.length+y;
      pairs.set(key,(pairs.get(key)||0)+search.weight);
    }
  }
  const edges=[...pairs].map(([key,w])=>[Math.floor(key/data.nodes.length),key%data.nodes.length,w]);
  return {nodes:[...visible].sort((a,b)=>a-b),edges,projects,matches:[...matches].sort((a,b)=>a-b)};
}
