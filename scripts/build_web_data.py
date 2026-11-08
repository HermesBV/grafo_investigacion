"""Construye el visor desde el Excel y coteja TODAS las personas y conexiones.

Ejecutar después de la notebook. No modifica el Excel ni los CSV originales.
"""
from __future__ import annotations
import argparse, csv, hashlib, itertools, json, math, re, unicodedata
from collections import defaultdict, Counter
from pathlib import Path
import openpyxl

ROOT = Path(__file__).resolve().parents[1]

def spaces(value):
    return re.sub(r'\s+', ' ', unicodedata.normalize('NFC', str(value or ''))).strip()

def role(value):
    text = ''.join(c for c in unicodedata.normalize('NFKD', spaces(value).upper()) if not unicodedata.combining(c))
    return re.sub(r'CO\s*-\s*DIRECTOR', 'CODIRECTOR', re.sub(r'/A\b', '', text)) or 'SIN ROL'

def person_id(name):
    return 'p_' + hashlib.sha256(name.encode('utf-8')).hexdigest()[:20]

def canonical_unit(value):
    text = spaces(value).upper()
    text = ''.join(c for c in unicodedata.normalize('NFKD',text) if not unicodedata.combining(c))
    text = re.sub(r'^(?:FAC\. DE |FACULTAD DE )','',text).replace('CS. ', 'CIENCIAS ')
    names = {
        'AGRONOMIA':'Agronomía',
        'ARQUITECTURA, DISENO Y URBANISMO':'Arquitectura, Diseño y Urbanismo',
        'ARQUITECTURA, DISSENO Y URBANISMO':'Arquitectura, Diseño y Urbanismo',
        'ARQUITECTURA Y URBANISMO':'Arquitectura, Diseño y Urbanismo',
        'CICLO BASICO COMUN':'Ciclo Básico Común',
        'CIENCIAS ECONOMICAS':'Ciencias Económicas',
        'CIENCIAS EXACTAS Y NATURALES':'Ciencias Exactas y Naturales',
        'CIENCIAS EXACTAS Y NATURALESS':'Ciencias Exactas y Naturales',
        'CIENCIAS SOCIALES':'Ciencias Sociales',
        'CIENCIAS VETERINARIAS':'Ciencias Veterinarias',
        'DERECHO':'Derecho',
        'FARMACIA Y BIOQUIMICA':'Farmacia y Bioquímica',
        'FILOSOFIA Y LETRAS':'Filosofía y Letras',
        'INGENIERIA':'Ingeniería',
        'MEDICINA':'Medicina',
        'ODONTOLOGIA':'Odontología',
        'PSICOLOGIA':'Psicología',
        '':'Sin unidad informada',
    }
    if text not in names:
        raise ValueError(f'Unidad nueva sin equivalencia revisada: {value}')
    return names[text]

def load_csv(path):
    with path.open(encoding='utf-8-sig', newline='') as stream:
        return list(csv.DictReader(stream))

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--excel', type=Path, default=ROOT/'output/xlsx/UBACYT-consolidado-2021-2022-2023.xlsx')
    parser.add_argument('--aliases', type=Path, help='JSON con las mismas equivalencias de ALIAS_PERSONAS en la notebook')
    args = parser.parse_args()
    source = ROOT/'output/grafos/ubacyt'
    config = json.loads((source/'ultima_ejecucion.json').read_text(encoding='utf-8'))
    included_types=set(config['tipos_incluidos'])
    for kind in included_types:
        weights=config['pesos_tipo'].get(kind,{})
        if set(weights)!={'nodos','conexiones'} or any(not isinstance(v,(int,float)) or isinstance(v,bool) or not math.isfinite(v) or v<=0 for v in weights.values()):
            raise ValueError(f'Falta definir la ponderación de nodos y conexiones para {kind}.')
    aliases = json.loads(args.aliases.read_text(encoding='utf-8')) if args.aliases else {}
    aliases = {spaces(k).upper(): spaces(v).upper() for k,v in aliases.items()}
    node_csv = load_csv(source/'nodos_ubacyt.csv')
    nodes = sorted(node_csv, key=lambda n: n['Id'])
    ids = {row['Id']: i for i,row in enumerate(nodes)}
    assert len(ids) == len(nodes), 'IDs de personas repetidos'
    roles = sorted(config['puntos_rol'])
    role_ids = {value: i for i,value in enumerate(roles)}
    projects = {}
    years = set()
    wb = openpyxl.load_workbook(args.excel, read_only=True, data_only=True)
    rows = wb['Datos'].iter_rows(values_only=True)
    columns = next(rows)
    if 'Tipo de proyecto' not in columns:
        raise ValueError('Falta Tipo de proyecto en el Excel. Migrar la base histórica antes de generar el visor.')
    seen = set()
    source_rows = 0
    for values in rows:
        row = dict(zip(columns, values))
        code = spaces(row['Código proyecto']).upper()
        kind = spaces(row['Tipo de proyecto']).upper()
        if not kind:
            raise ValueError(f'Falta Tipo de proyecto: {code}')
        if kind not in included_types:
            continue
        year = int(row['Año del listado'])
        if year not in config['anios']:
            continue
        source_rows += 1
        exact = tuple(row[c] for c in ['Año del listado','Código proyecto','Convocatoria','Integrante','Rol integrante','Título del proyecto','Unidad académica','Tipo de proyecto'])
        assert exact not in seen, 'Ejecutar primero la deduplicación de la notebook'
        seen.add(exact)
        name = spaces(row['Integrante']).upper()
        name = aliases.get(name, name)
        pid = person_id(name)
        if pid not in ids:
            raise ValueError(f'Persona no presente en el CSV: {name}. Revisar años y ALIAS_PERSONAS.')
        index = ids[pid]
        assert nodes[index]['Label'] == name
        canonical_role = role(row['Rol integrante'])
        if canonical_role not in role_ids:
            raise ValueError(f'Rol sin puntaje: {canonical_role}')
        p = projects.setdefault((kind,code), {'titles':set(), 'units':set(), 'raw_units':set(), 'years':set(), 'members':{}})
        p['titles'].add(spaces(row['Título del proyecto']))
        p['units'].add(canonical_unit(row['Unidad académica']))
        p['raw_units'].add(spaces(row['Unidad académica']))
        p['years'].add(year)
        member = p['members'].setdefault(index, {'roles':set(), 'years':set()})
        member['roles'].add(role_ids[canonical_role])
        member['years'].add(year)
        years.add(year)
    wb.close()
    units = sorted({u for p in projects.values() for u in p['units']})
    unit_ids = {value: i for i,value in enumerate(units)}
    prestige = Counter()
    project_counts = Counter()
    edges = Counter()
    output_projects = []
    for (kind,code),p in sorted(projects.items()):
        node_multiplier=config['pesos_tipo'][kind]['nodos']
        edge_multiplier=config['pesos_tipo'][kind]['conexiones']
        members = sorted(p['members'])
        for index, member in p['members'].items():
            prestige[index] += max(config['puntos_rol'][roles[r]] for r in member['roles']) * node_multiplier
            project_counts[index] += 1
        for a,b in itertools.combinations(members,2):
            edges[a,b] += edge_multiplier
        output_projects.append([code, sorted(p['titles']), sorted(unit_ids[u] for u in p['units']),
                                [[index, sorted(p['members'][index]['roles']), sorted(p['members'][index]['years'])] for index in members], sorted(p['years']), sorted(p['raw_units']),kind])
    for i,n in enumerate(nodes):
        assert prestige[i] == float(n['prestigio']), f'Prestigio distinto: {n["Label"]}'
    expected = Counter()
    for e in load_csv(source/'conexiones_ubacyt.csv'):
        assert e['Type'] == 'Undirected'
        a,b = sorted((ids[e['Source']], ids[e['Target']]))
        assert a != b and (a,b) not in expected
        expected[a,b] = float(e['peso'])
    assert edges == expected, 'Las conexiones reconstruidas difieren del CSV'
    degree = Counter()
    strength = Counter()
    for (a,b),weight in edges.items():
        degree[a] += 1; degree[b] += 1
        strength[a] += weight; strength[b] += weight
    output_nodes = [[n['Id'], n['Label'], float(n['prestigio']), degree[i], strength[i], project_counts[i]] for i,n in enumerate(nodes)]
    sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
    catalog = json.loads((ROOT/'fuentes-ubacyt.json').read_text(encoding='utf-8'))
    sources = [{'year':e['year'],'url':e['url'],'type':e.get('project_type','UBACYT').upper()} for e in catalog['entries'] if e.get('level')=='integrantes' and e['year'] in years and e.get('project_type','UBACYT').upper() in included_types]
    observed={(kind,year) for (kind,_),p in projects.items() for year in p['years']}
    assert observed <= {(s['type'],s['year']) for s in sources}, 'Falta registrar una fuente anual por tipo en fuentes-ubacyt.json'
    output = {
        'schemaVersion':2,
        'meta': {'years':sorted(years), 'nodes':len(nodes), 'edges':len(edges), 'projects':len(projects),
                 'memberships':sum(len(p['members']) for p in projects.values()), 'sourceRows':source_rows,
                 'totalPrestige':sum(prestige.values()), 'totalEdgeWeight':sum(edges.values()),
                 'projectTypeWeights':{kind:config['pesos_tipo'][kind] for kind in sorted(included_types)}, 'roleScores':config['puntos_rol'],
                 'sourceHashes':{'excel':sha(args.excel), 'nodes':sha(source/'nodos_ubacyt.csv'), 'edges':sha(source/'conexiones_ubacyt.csv')},
                 'sources':sorted(sources,key=lambda s:s['year'])},
        'roles':roles, 'units':units, 'types':sorted({kind for kind,_ in projects}),'nodes':output_nodes, 'projects':output_projects,
        'edges':[[a,b,w] for (a,b),w in sorted(edges.items())]
    }
    path = ROOT/'web/public/data/graph.json'
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(output,ensure_ascii=False,separators=(',',':')),encoding='utf-8')
    print(json.dumps({'path':str(path), 'bytes':path.stat().st_size, **output['meta']},ensure_ascii=False))

if __name__ == '__main__':
    main()
