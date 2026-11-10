"""Verifica todos los datos públicos sin requerir el Excel de trabajo local."""
from collections import Counter
from hashlib import sha256
from itertools import combinations
from pathlib import Path
import csv
import json
import math

ROOT = Path(__file__).resolve().parents[1]

def read_csv(path):
    with path.open(encoding='utf-8-sig', newline='') as source:
        return list(csv.DictReader(source))

def number(value):
    parsed = float(value)
    assert math.isfinite(parsed), 'Valor numérico no finito'
    return parsed

def main():
    graph = json.loads((ROOT/'web/public/data/graph.json').read_text(encoding='utf-8'))
    base = ROOT/'output/grafos/ubacyt'
    config = json.loads((base/'ultima_ejecucion.json').read_text(encoding='utf-8'))
    assert graph['schemaVersion'] == 3
    assert graph['meta']['roleScores'] == config['puntos_rol']
    assert graph['meta']['projectTypeWeights'] == {kind:config['pesos_tipo'][kind] for kind in config['tipos_incluidos']}
    nodes = graph['nodes']
    ids = {n[0]: i for i,n in enumerate(nodes)}
    assert len(ids) == len(nodes), 'IDs de personas repetidos'
    for n in nodes:
        assert len(n) == 10 and n[1]
        assert all(math.isfinite(v) for v in n[2:]), 'Posiciones o atributos inválidos'
    csv_nodes = read_csv(base/'nodos_ubacyt.csv')
    assert {n['Id'] for n in csv_nodes} == set(ids) and len(csv_nodes) == len(ids)
    for row in csv_nodes:
        node = nodes[ids[row['Id']]]
        assert node[1] == row['Label'] and node[2] == number(row['prestigio'])
    prestige, project_counts, reconstructed = Counter(), Counter(), Counter()
    codes = set()
    memberships = 0
    for p in graph['projects']:
        code, titles, units, members, years = p[:5]
        assert len(p)==8
        assert set(p[7])<=set(graph['coverages'])
        kind=p[6]
        assert kind in graph['types'] and kind in config['tipos_incluidos']
        assert code and (kind,code) not in codes, 'Clave de proyecto repetida o vacía'
        codes.add((kind,code))
        node_multiplier=config['pesos_tipo'][kind]['nodos']
        edge_multiplier=config['pesos_tipo'][kind]['conexiones']
        assert titles and years
        assert all(0 <= u < len(graph['units']) for u in units)
        indexes = [m[0] for m in members]
        assert len(indexes) == len(set(indexes)), 'Participaciones repetidas'
        memberships += len(members)
        for index, roles, observed_years, observations in members:
            assert observations
            assert {o[0] for o in observations}==set(observed_years)
            assert {o[2] for o in observations}==set(roles)
            assert all(o[1] in p[7] for o in observations)
            assert 0 <= index < len(nodes) and roles and observed_years
            assert len(roles) == len(set(roles))
            assert all(0 <= r < len(graph['roles']) for r in roles)
            prestige[index] += max(config['puntos_rol'][graph['roles'][r]] for r in roles) * node_multiplier
            project_counts[index] += 1
        for a,b in combinations(sorted(indexes),2):
            reconstructed[a,b] += edge_multiplier
    graph_edges = Counter()
    for a,b,weight in graph['edges']:
        assert 0 <= a < b < len(nodes) and (a,b) not in graph_edges
        assert number(weight) > 0
        graph_edges[a,b] = weight
    csv_edges = Counter()
    for e in read_csv(base/'conexiones_ubacyt.csv'):
        assert e['Type'] == 'Undirected'
        a,b = sorted((ids[e['Source']],ids[e['Target']]))
        assert a != b and (a,b) not in csv_edges
        csv_edges[a,b] = number(e['peso'])
    assert reconstructed == graph_edges == csv_edges, 'Conexiones o pesos inconsistentes'
    degree, strength = Counter(), Counter()
    for (a,b),weight in graph_edges.items():
        degree[a] += 1; degree[b] += 1
        strength[a] += weight; strength[b] += weight
    for i,n in enumerate(nodes):
        assert n[2:6] == [prestige[i],degree[i],strength[i],project_counts[i]], f'Atributos distintos para {n[0]}'
    meta = graph['meta']
    assert set(graph['types'])=={kind for kind,_ in codes}
    assert meta['nodes'] == len(nodes) and meta['edges'] == len(graph_edges)
    assert meta['projects'] == len(codes) and meta['memberships'] == memberships
    assert meta['totalPrestige'] == sum(prestige.values())
    assert meta['totalEdgeWeight'] == sum(graph_edges.values())
    for key,file in [('nodes','nodos_ubacyt.csv'),('edges','conexiones_ubacyt.csv')]:
        assert sha256((base/file).read_bytes()).hexdigest() == meta['sourceHashes'][key]
    print(json.dumps({'nodes':len(nodes),'edges':len(graph_edges),'projects':len(codes),
                      'memberships':memberships,'totalPrestige':sum(prestige.values()),
                      'totalEdgeWeight':sum(graph_edges.values()),'validation':'complete'},ensure_ascii=False))

if __name__ == '__main__':
    main()
