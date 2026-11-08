import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {filterGraph,normalizeSearch,getThresholdLimits} from '../src/filter-core.mjs';

const fixture={meta:{edgeMultiplier:1},roles:['DIRECTOR','ESTUDIANTE','SIN ROL'],units:['Sociales','Exactas'],
  nodes:[['a','ANA PÉREZ',6,3,4,2],['b','BETO',2,3,4,2],['c','CARLA',1,2,2,1],['d','DIEGO',6,2,2,1]],
  projects:[
    ['P1',['Política social'],[0],[[0,[0],[2021]],[1,[1],[2021]],[2,[2],[2021]]],[2021]],
    ['P2',['Física'],[1],[[0,[1],[2022]],[1,[1],[2022]],[3,[0],[2022]]],[2022]],
  ]};
const edges = r=>r.edges.map(e=>e.join(':')).sort();
test('búsqueda tolera tildes, mayúsculas y espacios',()=>assert.equal(normalizeSearch('  POLÍTICA\n SOCIAL '),'politica social'));
test('grupos repetidos incrementan peso, no duplican aristas',()=>assert.deepEqual(edges(filterGraph(fixture)),['0:1:2','0:2:1','0:3:1','1:2:1','1:3:1']));
test('filtro de unidad recalcula pesos por grupos visibles',()=>assert.deepEqual(edges(filterGraph(fixture,{unit:'0'})),['0:1:1','0:2:1','1:2:1']));
test('rol se evalúa en el proyecto filtrado',()=>assert.deepEqual(filterGraph(fixture,{unit:'1',role:'0'}).nodes,[3]));
test('rol y nombre de proyectos distintos no se cruzan',()=>assert.equal(filterGraph(fixture,{unit:'1',role:'0',name:'ana'}).nodes.length,0));
test('nombre con colaboradores incluye únicamente sus grupos',()=>assert.deepEqual(filterGraph(fixture,{name:'carla'}).nodes,[0,1,2]));
test('nombre estricto mantiene un nodo aislado',()=>assert.deepEqual(filterGraph(fixture,{name:'ana perez',neighbors:false}).nodes,[0]));
test('código y título se combinan con AND',()=>assert.equal(filterGraph(fixture,{code:'P1',title:'fisica'}).projects.length,0));
test('sin rol se conserva y puede filtrarse',()=>assert.deepEqual(filterGraph(fixture,{role:'2'}).nodes,[2]));
test('cero resultados es válido',()=>assert.deepEqual(filterGraph(fixture,{name:'inexistente'}),{nodes:[],edges:[],projects:[],matches:[]}));
test('rangos se derivan de la base completa',()=>assert.deepEqual(getThresholdLimits(fixture),{maxConnections:3,maxProjects:2}));
test('ceros y campos vacíos conservan toda la red',()=>{
  const all=filterGraph(fixture);
  for(const value of [0,'0','',null])assert.deepEqual(filterGraph(fixture,{minConnections:value,minProjects:value}),all);
});
test('mínimo de conexiones incluye el umbral y cuenta vecinos distintos, no pesos',()=>{
  const r=filterGraph(fixture,{minConnections:'3'});
  assert.deepEqual(r.nodes,[0,1]);
  assert.deepEqual(edges(r),['0:1:2']);
});
test('mínimo de proyectos incluye el máximo permitido',()=>assert.deepEqual(filterGraph(fixture,{minProjects:'2'}).nodes,[0,1]));
test('mínimos globales no se recalculan ni se podan al filtrar la unidad',()=>{
  const r=filterGraph(fixture,{unit:'0',minConnections:3});
  assert.deepEqual(r.nodes,[0,1]);
  assert.deepEqual(edges(r),['0:1:1']);
});
test('nombre y colaboradores también deben cumplir los mínimos',()=>{
  assert.deepEqual(filterGraph(fixture,{name:'ana',minProjects:2}).nodes,[0,1]);
  assert.equal(filterGraph(fixture,{name:'carla',minProjects:2}).nodes.length,0);
});
test('ambos mínimos se combinan con AND',()=>{
  const separate={meta:{edgeMultiplier:1},nodes:[
    ['a','A',1,3,3,1],['b','B',1,3,3,1],['c','C',1,3,3,1],['d','D',1,3,3,1],['e','E',2,1,2,2],['f','F',2,1,2,2]],
    projects:[['T',['Equipo'],[],[[0,[],[]],[1,[],[]],[2,[],[]],[3,[],[]]],[]],['D1',['Dupla 1'],[],[[4,[],[]],[5,[],[]]],[]],['D2',['Dupla 2'],[],[[4,[],[]],[5,[],[]]],[]]]};
  assert.equal(filterGraph(separate,{minConnections:3}).nodes.length,4);
  assert.equal(filterGraph(separate,{minProjects:2}).nodes.length,2);
  assert.equal(filterGraph(separate,{minConnections:3,minProjects:2}).nodes.length,0);
});
test('valores fuera del rango o no enteros se rechazan',()=>{
  for(const field of ['minConnections','minProjects']) {
    for(const value of [-1,1.5,'abc',Infinity,4])assert.throws(()=>filterGraph(fixture,{[field]:value}),RangeError);
  }
});

const real=JSON.parse(fs.readFileSync(new URL('../public/data/graph.json',import.meta.url)));
test('grafo real: todos los nodos, proyectos, pesos y aristas coinciden con la base',()=>{
  const r=filterGraph(real);
  assert.equal(r.nodes.length,real.meta.nodes);
  assert.equal(r.projects.length,real.meta.projects);
  assert.deepEqual(edges(r),edges({edges:real.edges}));
  assert.equal(real.nodes.reduce((s,n)=>s+n[2],0),real.meta.totalPrestige);
});
test('grafo real: IDs, miembros, roles, unidades y posiciones son válidos',()=>{
  assert.equal(new Set(real.nodes.map(n=>n[0])).size,real.nodes.length);
  for(const n of real.nodes){assert.equal(n.length,10);assert.ok(n.slice(2).every(Number.isFinite));}
  for(const p of real.projects){
    assert.equal(new Set(p[3].map(m=>m[0])).size,p[3].length);
    for(const u of p[2])assert.ok(u>=0&&u<real.units.length);
    for(const m of p[3]){assert.ok(real.nodes[m[0]]);for(const role of m[1])assert.ok(real.roles[role]);}
  }
});
test('grafo real: los mínimos conservan exactamente los nodos elegibles y sus aristas',()=>{
  const allowed=new Set(real.nodes.flatMap((n,i)=>n[3]>=30&&n[5]>=2?[i]:[]));
  const r=filterGraph(real,{minConnections:30,minProjects:2});
  assert.ok(allowed.size>0&&allowed.size<real.nodes.length);
  assert.deepEqual(r.nodes,[...allowed]);
  assert.deepEqual(edges(r),edges({edges:real.edges.filter(([a,b])=>allowed.has(a)&&allowed.has(b))}));
  assert.deepEqual(r.projects,real.projects.flatMap((p,i)=>p[3].some(m=>allowed.has(m[0]))?[i]:[]));
});
test('grafo real: todo el rango, incluidos ambos máximos, se puede utilizar',()=>{
  const limits=getThresholdLimits(real);
  const degree=Array(real.nodes.length).fill(0), memberships=Array(real.nodes.length).fill(0);
  for(const [a,b] of real.edges){degree[a]++;degree[b]++;}
  for(const p of real.projects)for(const [i] of p[3])memberships[i]++;
  assert.deepEqual(limits,{maxConnections:Math.max(0,...degree),maxProjects:Math.max(0,...memberships)});
  for(const [field,index,max] of [['minConnections',3,limits.maxConnections],['minProjects',5,limits.maxProjects]]) {
    assert.deepEqual(filterGraph(real,{[field]:max}).nodes,real.nodes.flatMap((n,i)=>n[index]>=max?[i]:[]));
  }
});
