"""Reconstruye la base UBACyT del repo (graph.json) y la amplía con fuentes nuevas.
Salida: base v2 (11 columnas del contrato) + sólo-ampliación + reporte."""
import json, csv, re, sys, os, unicodedata, difflib, collections
GRAPH, RES, FU, OUT, SOC = sys.argv[1:6]
COLS = ['Año del listado','Código proyecto','Convocatoria','Integrante','Rol integrante','Título del proyecto','Unidad académica','Página PDF','Fila en página','Tipo de proyecto','fuente_completa']
DC = 'sólo dirección y codirección'; COMP = 'completa'
def deacc(s): return ''.join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn')
def up(s): return re.sub(r'\s+', ' ', unicodedata.normalize('NFC', s)).strip().upper()
def key(s): return re.sub(r'\s+', ' ', re.sub(r'[^A-Z, ]', ' ', deacc(up(s)))).replace(' ,', ',').strip()
def ekey(s): return re.sub(r'\s*,\s*', ', ', up(s))
def toks(s): return frozenset(t for t in re.split(r'[ ,.]+', up(s)) if t)
ALIAS = {}

# ---------- 1. base reconstruida ----------
g = json.load(open(GRAPH)); labels = [n[1] for n in g['nodes']]; roles = g['roles']
base = []
for p in g['projects']:
    code, titles, units_orig, tipo = p[0], p[1], p[5], p[6]
    title = max(titles, key=len) if titles else ''
    unit = units_orig[0] if units_orig else ''
    for m in p[3]:
        for (y, cov, ri) in m[3]:
            base.append([y, code, '', labels[m[0]], roles[ri], title, unit, '', '', tipo, cov, 'graph.json'])
base_yc = collections.defaultdict(set)  # (año, código) -> coberturas
for r in base: base_yc[(r[0], r[1])].add(r[10])
base_dc = collections.defaultdict(set)  # (año, código) -> {(nombre,rol)} dir/codir
for r in base:
    if r[4] in ('DIRECTOR','CODIRECTOR'): base_dc[(r[0], r[1])].add((key(r[3]), r[4]))

# índice de nombres conocidos (APELLIDO, NOMBRE) -> etiqueta canónica
known = {}; known_cnt = collections.Counter()
known_dk = collections.defaultdict(set)
def add_known(lbl):
    known.setdefault(ekey(lbl), lbl); known_dk[key(lbl)].add(lbl)
for l in labels: add_known(l)
base_labels = set(labels)
by_tokens = collections.defaultdict(set)
def canon(name):
    """'Apellido, Nombre' -> etiqueta existente si coincide sin tildes; si no, mayúsculas NFC."""
    lbl = known.get(ekey(name), ekey(name))
    sim = known_dk.get(key(lbl), set()) - {lbl}
    if lbl not in base_labels and len(sim) == 1: ALIAS[lbl] = next(iter(sim))  # sólo difiere en tildes/puntuación
    return lbl

UNITS = ['Agronomía','Arquitectura, Diseño y Urbanismo','Ciencias Económicas','Ciencias Exactas y Naturales','Ciencias Sociales','Ciencias Veterinarias','Derecho','Farmacia y Bioquímica','Filosofía y Letras','Ingeniería','Medicina','Odontología','Psicología']
UK = {key(u): u for u in UNITS}
def canon_unit(u):
    u = re.split(r'\s{3,}', u.strip())[0]
    k = key(u)
    if not re.search(r'[A-Z]{3}', k): return ''
    if 'RECTORADO' in k: return 'Rectorado'
    if re.search(r'C\W*I\W*C\W*L\W*O|BASICO', k): return 'Ciclo Básico Común'
    k2 = re.sub(r'^(FA\w*|.*\bDE\b)\s+', '', k.replace('FACULTAD DE ', '')).strip()
    k2 = k.replace('FACULTAD DE ', '').replace('FACULLAD DE ', '').replace('FACUITAD DE ', '').strip()
    best = difflib.get_close_matches(k2, UK.keys(), n=1, cutoff=0.6)
    if not best:
        best = difflib.get_close_matches(k2.replace('ARQUITECTURA Y URBANISMO','ARQUITECTURA, DISENO Y URBANISMO'), UK.keys(), n=1, cutoff=0.5)
    if not best: return ''
    u = UK[best[0]]
    return u if u == 'Ciclo Básico Común' else 'Facultad de ' + u

new = []; report = collections.Counter(); diffs = []
# ---------- 2a. resoluciones (dir/codir) ----------
res = list(csv.DictReader(open(RES), delimiter='\t'))
code_unit = {}
for r in res:
    cu = canon_unit(r['unidad'])
    if cu: code_unit.setdefault(r['codigo'], cu)
for p in g['projects']:
    if p[5]:
        cu = canon_unit(p[5][0])
        if cu: code_unit.setdefault(p[0], cu)
for r in res:
    nm = r['integrante']
    if not re.search(r',', nm) or len(key(nm)) < 5: report['res_nombre_invalido'] += 1; continue
    unit = canon_unit(r['unidad']) or code_unit.get(r['codigo'], '')
    new.append([int(r['anio']), r['codigo'], r['convocatoria'], canon(nm), r['rol'], r['titulo'], unit,
                int(r['pagina']), int(r['linea']), 'UBACYT', DC, r['archivo']])
for r in new: add_known(r[3])
# índice por tokens para nombres en orden natural
for k, l in known.items(): by_tokens[toks(l)].add(l)
first_by_surname = collections.defaultdict(set)
for l in set(known.values()):
    if ',' in l:
        sur, giv = l.split(',', 1); gt = up(giv).split()
        if gt: first_by_surname[(up(sur), gt[0])].add(l)
SURN = {up(l.split(',',1)[0]) for l in set(known.values()) if ',' in l and len(key(l.split(',',1)[0]).split())>1}
PART = {'DE','DEL','LA','LAS','LOS','DA','DI','VAN','VON','Y','DOS','DAS'}
def natural(name):
    """'Nombre Apellido' -> etiqueta. Coincidencia exacta de tokens; si no, apellido = último(s) token(s)."""
    name = re.sub(r'\s+', ' ', name).strip(' .;,')
    if ',' in name: return canon(name), 'coma'
    t = toks(name)
    c = by_tokens.get(t)
    if c and len(c) == 1: return next(iter(c)), 'tokens'
    w = up(name).split()
    for k in (2, 1):
        if len(w) > k:
            sur, giv = ' '.join(w[-k:]), w[:-k]
            cand = first_by_surname.get((up(sur), up(giv[0])))
            if cand and len(cand) == 1: return next(iter(cand)), 'apellido+nombre'
    for k in (3, 2):
        if len(w) > k and up(' '.join(w[-k:])) in SURN:
            return canon(f"{' '.join(w[-k:])}, {' '.join(w[:-k])}"), 'heuristica'
    i = len(w) - 1
    while i > 1 and w[i-1] in PART: i -= 1
    return canon(f"{' '.join(w[i:])}, {' '.join(w[:i])}"), 'heuristica'

ROLEMAP = [(r'co-?direct', 'CODIRECTOR'), (r'^direct', 'DIRECTOR'), (r'formad', 'INVESTIGADOR FORMADO'),
           (r'en formaci', 'INVESTIGADOR EN FORMACION'), (r'tesista', 'INVESTIGADOR TESISTA'),
           (r'de apoyo', 'INVESTIGADOR DE APOYO'), (r'asesor', 'INVESTIGADOR ASESOR'),
           (r'estudiante de grado', 'ESTUDIANTE DE GRADO'), (r'estudiante', 'ESTUDIANTE'),
           (r'colaborador', 'INVESTIGADOR COLABORADOR')]
def maprole(r):
    r = deacc((r or '').strip().lower())
    if not r: return 'SIN ROL'
    for pat, v in ROLEMAP:
        if re.search(pat, r): return v
    return 'SIN ROL'

# ---------- 2b. FFyL Omeka ----------
for fn, year in (('2023-2027_FFYL-UBA_UBACyT-PC2023-integrantes-rol_omeka.tsv', 2023), ('2026-2028_FFYL-UBA_UBACyT-PC2026-integrantes-rol_omeka.tsv', 2026)):
    for i, r in enumerate(csv.DictReader(open(os.path.join(FU, fn)), delimiter='\t'), 2):
        if not r['integrante'].strip() or not re.match(r'2\d{13}BA', r['codigo'] or ''): report['omeka_descartada'] += 1; continue
        rol = maprole(r['rol']); nm, how = natural(r['integrante']); report['omeka_'+how] += 1
        new.append([year, r['codigo'], up(r['convocatoria'] + (' ' + r['modalidad'] if r['modalidad'] else '')), nm, rol, r['titulo'],
                    'Facultad de Filosofía y Letras', 0, i, 'UBACYT', COMP, fn])

# ---------- 2c. Derecho (páginas por proyecto) ----------
def split_members(txt):
    out = []
    for item in re.split(r'\s*\|\s*', txt or ''):
        item = item.strip().rstrip('.')
        if not item: continue
        m = re.match(r'^(.*?)\s*;\s*(.+)$', item)
        if m: out.append((m.group(1), m.group(2))); continue
        m = re.match(r'^(.*?)\s*\(([^)]*)\)\s*$', item)
        if m:  # "A, B y C (rol)"
            names, rol = m.group(1), m.group(2)
            parts = re.split(r'\s*,\s*|\s+y\s+', names) if not re.search(r'^[^,]+,\s*[^,]+$', names) or ' y ' in names else [names]
            # si los elementos parecen "Apellido, Nombre" (2 partes sin ' y '), mantener
            out += [(n, rol) for n in parts if n.strip()]; continue
        out.append((item, ''))
    return out
FDER = sorted(f for f in os.listdir(FU) if 'FDER-UBA_UBACyT-proyectos-integrantes_web.tsv' in f)
for fn in FDER:
    year = int(fn[:4])
    for i, r in enumerate(csv.DictReader(open(os.path.join(FU, fn)), delimiter='\t'), 2):
        m = re.match(r'\s*(2\d{13}(?:BA)?)', r['Código'] or '')
        if not m: report['fder_sin_codigo'] += 1; continue
        code = m.group(1); title = (r['Título'] or '').strip()
        conv = up(r['Tipo de proyecto'] or '') or f'PROGRAMACION {fn[:9]}'
        people = []
        for col, rol in (('Director','DIRECTOR'),('Directora','DIRECTOR'),('Director/a','DIRECTOR'),('Codirector','CODIRECTOR'),('Codirectora','CODIRECTOR'),('Codirector/a','CODIRECTOR'),('Co-director','CODIRECTOR'),('Co-directora','CODIRECTOR')):
            for n in re.split(r'\s*;\s*|\s+y\s+', r.get(col) or ''):
                if n.strip(): people.append((n, rol))
        for n, rol in split_members(r['integrantes']): people.append((n, maprole(rol)))
        seen = set()
        for n, rol in people:
            n = re.sub(r'^(Dr|Dra|Lic|Abog|Prof)\.?\s+', '', n.strip())
            if len(n) < 5 or len(n.split()) < 2 or re.search(r'\d', n): report['fder_nombre_descartado'] += 1; continue
            nm, how = natural(n); report['fder_'+how] += 1
            if (nm, rol) in seen or ((nm,'DIRECTOR') in seen) or ((nm,'CODIRECTOR') in seen): continue
            seen.add((nm, rol))
            new.append([year, code, conv, nm, rol, title, 'Facultad de Derecho', 0, i, 'UBACYT', COMP, fn])

# ---------- 2d. listas SIGEVA de integrantes (sociales.uba.ar, 2010-2016) ----------
for i, r in enumerate(csv.DictReader(open(SOC), delimiter='\t')):
    nm = r['integrante']
    if ',' not in nm or len(key(nm)) < 5: report['soc_nombre_invalido'] += 1; continue
    unit = code_unit.get(r['codigo']) or canon_unit(r['unidad'])
    new.append([int(r['anio']), r['codigo'], r['convocatoria'], canon(nm), maprole(r['rol']), r['titulo'], unit,
                int(r['pagina']), int(r['linea']), 'UBACYT', COMP, r['archivo']])
    report['soc'] += 1
# ---------- 2e. FADU IEH (fichas por proyecto) ----------
fn = '2020-2026_FADU-UBA_UBACyT-PDE-IEH-fichas-integrantes-rol.tsv'
for i, r in enumerate(csv.DictReader(open(os.path.join(FU, fn)), delimiter='\t'), 2):
    if not re.match(r'2\d{13}BA$', r['codigo'] or ''): report['fadu_no_ubacyt'] += 1; continue
    nm, how = natural(r['integrante']); report['fadu_'+how] += 1
    new.append([int(r['anio_inicio']), r['codigo'], '', nm, maprole(r['rol']), r['titulo'], 'Facultad de Arquitectura, Diseño y Urbanismo', 0, i, 'UBACYT', COMP, fn])
# ---------- 3. fusión sin pisar ----------
def dkey(r): return (r[0], r[1], key(r[3]), r[4], r[9], r[10])
basekeys = {dkey(r) for r in base}
added = []; seen = set()
for r in new:
    yc = (r[0], r[1])
    if r[10] in base_yc.get(yc, set()):
        # misma cobertura y mismo año/proyecto ya en la base: la base manda; registrar diferencias
        if r[4] in ('DIRECTOR','CODIRECTOR') and (key(r[3]), r[4]) not in base_dc[yc]:
            diffs.append(r)
        report['omitida_ya_en_base'] += 1; continue
    k = dkey(r)
    if k in basekeys or k in seen: report['duplicada'] += 1; continue
    seen.add(k); added.append(r)

os.makedirs(OUT, exist_ok=True)
def w(fn, rows, extra=True):
    with open(os.path.join(OUT, fn), 'w', newline='', encoding='utf-8') as f:
        wr = csv.writer(f); wr.writerow(COLS + (['archivo_fuente'] if extra else [])); wr.writerows([r if extra else r[:11] for r in rows])
base.sort(key=lambda r: (r[0], r[1], r[3])); added.sort(key=lambda r: (r[0], r[1], r[3]))
w('base_reconstruida.csv', base); w('ampliacion.csv', added); w('diferencias.csv', diffs)
allrows = base + added; allrows.sort(key=lambda r: (r[0], r[1], r[3]))
w('UBACYT-consolidado-v2.csv', allrows)
import openpyxl
wb = openpyxl.Workbook(); ws = wb.active; ws.title = 'Datos'; ws.append(COLS)
for r in allrows: ws.append([v if v != '' else None for v in r[:11]])
wp = wb.create_sheet('Procedencia'); wp.append(['Origen de la fila (archivo_fuente)', 'Filas'])
for k, v in sorted(collections.Counter(r[11] for r in allrows).items()): wp.append([k, v])
wb.save(os.path.join(OUT, 'UBACYT-consolidado-v2.xlsx'))
print('base', len(base), 'nuevas', len(new), 'agregadas', len(added), 'v2', len(allrows))
print(dict(report))
c = collections.Counter((r[0], r[10]) for r in added); print(sorted(c.items()))
cb = collections.Counter((r[0], r[10]) for r in base); print(sorted(cb.items()))
print('roles agregadas', collections.Counter(r[4] for r in added))
print('unidades', collections.Counter(r[6] for r in added))
print('proyectos v2', len({(r[9], r[1]) for r in allrows}), 'base', len({(r[9], r[1]) for r in base}))
print('personas v2', len({key(r[3]) for r in allrows}), 'base', len({key(r[3]) for r in base}))
print('diferencias dir/codir mismo año', len(diffs))
used = {r[3] for r in added}
al = {k: v for k, v in sorted(ALIAS.items()) if k in used}
json.dump(al, open(os.path.join(OUT, 'alias_sugeridos.json'), 'w'), ensure_ascii=False, indent=1)
print('alias sugeridos', len(al))
