import fs from 'node:fs';
import {UndirectedGraph} from 'graphology';
import forceAtlas2 from 'graphology-layout-forceatlas2';
import louvain from 'graphology-communities-louvain';

const path = new URL('../public/data/graph.json', import.meta.url);
const data = JSON.parse(fs.readFileSync(path, 'utf8'));
const g = new UndirectedGraph();
// Semilla fija: todos los builds tienen las mismas posiciones iniciales.
let seed = 202123;
const random = () => { seed = (Math.imul(seed,1664525)+1013904223) >>> 0; return seed / 4294967296; };
data.nodes.forEach((n,i) => g.addNode(String(i), {x:(random()-.5)*100,y:(random()-.5)*100,size:1}));
data.edges.forEach(([a,b,w]) => g.addEdge(String(a),String(b),{weight:w}));
console.log(`Layout: ${g.order} personas, ${g.size} conexiones`);
// Una semilla por comunidades evita que la vista general arranque como una bola.
// No cambia ni el color ni el tamaño: ambos siguen representando prestigio.
const communities=louvain(g,{rng:random,getEdgeWeight:'weight',resolution:1});
const coarse=new UndirectedGraph();
const sizes=new Map();
g.forEachNode(id=>sizes.set(communities[id],(sizes.get(communities[id])||0)+1));
for(const [id,count] of sizes){
  const angle=id*Math.PI*(3-Math.sqrt(5));
  coarse.addNode(String(id),{x:Math.sqrt(id+1)*Math.cos(angle)*20,y:Math.sqrt(id+1)*Math.sin(angle)*20,size:Math.sqrt(count)});
}
g.forEachEdge((e,a,s,t)=>{
  const x=String(communities[s]),y=String(communities[t]);
  if(x===y)return;
  if(coarse.hasEdge(x,y))coarse.updateEdgeAttribute(x,y,'weight',w=>w+a.weight);
  else coarse.addEdge(x,y,{weight:a.weight});
});
forceAtlas2.assign(coarse,{iterations:300,getEdgeWeight:'weight',settings:{...forceAtlas2.inferSettings(coarse),barnesHutOptimize:true,linLogMode:true,gravity:1,scalingRatio:30,slowDown:3}});
let coarseExtent=1;
coarse.forEachNode((id,a)=>{coarseExtent=Math.max(coarseExtent,Math.abs(a.x),Math.abs(a.y));});
const circles=[...sizes].map(([id,count])=>{
  const p=coarse.getNodeAttributes(String(id));
  return {id,x:p.x/coarseExtent*Math.sqrt(g.order)*1.5,y:p.y/coarseExtent*Math.sqrt(g.order)*1.5,r:Math.sqrt(count)*1.2};
});
// Separar los discos de comunidades sin ocultar los vínculos entre ellos.
for(let step=0;step<900;step++)for(let i=0;i<circles.length;i++)for(let j=i+1;j<circles.length;j++){
  const a=circles[i],b=circles[j],dx=b.x-a.x,dy=b.y-a.y,dist=Math.hypot(dx,dy)||1e-5,min=a.r+b.r+3;
  if(dist>=min)continue;
  const overlap=(min-dist)/dist*.505;
  a.x-=dx*overlap;a.y-=dy*overlap;b.x+=dx*overlap;b.y+=dy*overlap;
}
const localGraphs=new Map(circles.map(c=>[c.id,new UndirectedGraph()]));
g.forEachNode((id,a)=>localGraphs.get(communities[id]).addNode(id,{...a}));
g.forEachEdge((e,a,s,t)=>{if(communities[s]===communities[t])localGraphs.get(communities[s]).addEdge(s,t,{...a});});
console.log(`${sizes.size} comunidades. ForceAtlas2 local: 200 iteraciones por comunidad…`);
for(const circle of circles){
  const local=localGraphs.get(circle.id);
  forceAtlas2.assign(local,{iterations:200,getEdgeWeight:'weight',settings:{...forceAtlas2.inferSettings(local),
    barnesHutOptimize:local.order>100,linLogMode:true,gravity:1,scalingRatio:2,slowDown:2}});
  let meanX=0,meanY=0,radius=1;
  local.forEachNode((id,a)=>{meanX+=a.x;meanY+=a.y;});
  meanX/=local.order;meanY/=local.order;
  local.forEachNode((id,a)=>{radius=Math.max(radius,Math.hypot(a.x-meanX,a.y-meanY));});
  local.forEachNode((id,a)=>g.mergeNodeAttributes(id,{x:circle.x+(a.x-meanX)/radius*circle.r*.9,y:circle.y+(a.y-meanY)/radius*circle.r*.9}));
}
let extent=1;
g.forEachNode((id,a)=>{extent=Math.max(extent,Math.abs(a.x),Math.abs(a.y));});
const maxDegree=Math.max(...data.nodes.map(n=>n[3]));
data.nodes.forEach((n,i)=>{
  const a=g.getNodeAttributes(String(i));
  const x=a.x/extent, y=a.y/extent;
  const angle=Math.atan2(y,x);
  const radius=.09+.91*(1-Math.log1p(n[3])/Math.log1p(maxDegree));
  n.splice(6, n.length-6, +x.toFixed(7),+y.toFixed(7),+(radius*Math.cos(angle)).toFixed(7),+(radius*Math.sin(angle)).toFixed(7));
});
data.meta.layout={algorithm:'ForceAtlas2 multiescala',localIterations:200,coarseIterations:300,seed:202123,initialization:'Louvain, ForceAtlas2 agregado y separación de discos',communities:sizes.size,centrality:'Grado global: vecinos distintos / (personas − 1)'};
fs.writeFileSync(path,JSON.stringify(data));
console.log('Posiciones guardadas.');
