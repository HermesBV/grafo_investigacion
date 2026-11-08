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
    projects:data.projects.map(p=>({code:normalizeSearch(p[0]), title:normalizeSearch(p[1].join(' '))})),
  };
}

export function filterGraph(data, filters={}, index=prepareData(data)) {
  const name=normalizeSearch(filters.name), code=normalizeSearch(filters.code), title=normalizeSearch(filters.title);
  const role=filters.role === '' || filters.role == null ? null : Number(filters.role);
  const unit=filters.unit === '' || filters.unit == null ? null : Number(filters.unit);
  const neighbors=filters.neighbors !== false;
  const minConnections=minimum(filters.minConnections,index.limits.maxConnections,'Mínimo de conexiones');
  const minProjects=minimum(filters.minProjects,index.limits.maxProjects,'Mínimo de proyectos');
  // Los umbrales usan los totales globales; ocultar vecinos no cambia la elegibilidad.
  const eligible=data.nodes.map(n=>n[3]>=minConnections&&n[5]>=minProjects);
  const visible=new Set(), matches=new Set(), projects=[], pairs=new Map();
  for (let pi=0; pi<data.projects.length; pi++) {
    const p=data.projects[pi], search=index.projects[pi];
    if (unit!==null && !p[2].includes(unit)) continue;
    if (code && !search.code.includes(code)) continue;
    if (title && !search.title.includes(title)) continue;
    let members=p[3].filter(m=>eligible[m[0]]&&(role===null || m[1].includes(role))).map(m=>m[0]);
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
      pairs.set(key,(pairs.get(key)||0)+data.meta.edgeMultiplier);
    }
  }
  const edges=[...pairs].map(([key,w])=>[Math.floor(key/data.nodes.length),key%data.nodes.length,w]);
  return {nodes:[...visible].sort((a,b)=>a-b),edges,projects,matches:[...matches].sort((a,b)=>a-b)};
}
