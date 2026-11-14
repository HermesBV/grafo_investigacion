"""Listas SIGEVA de integrantes UBACyT publicadas por sociales.uba.ar (2010-2016) -> TSV."""
import re, subprocess, sys, os, csv
SRC, OUT = sys.argv[1], sys.argv[2]
SPECS = {  # archivo: (año, columnas en orden, convocatoria)
 '2010-2012_TODOS_UBACyT-PC2010-2012-integrantes-rol_sociales.pdf': (2010, ['code','sipi','name','rol','titulo','unidad'], 'PROGRAMACION CIENTIFICA 2010-2012'),
 '2011-2014_TODOS_UBACyT-PC2011-2014-integrantes-rol_sociales.pdf': (2011, ['code','sipi','ape','nom','rol','titulo','unidad'], 'PROGRAMACION CIENTIFICA 2011-2014'),
 '2012-2015_TODOS_UBACyT-PC2012-2015-integrantes-sin-rol_sociales.pdf': (2012, ['unidad','code','sipi','ape','nom','titulo','ini','fin'], 'PROGRAMACION CIENTIFICA 2012-2015'),
 '2013-2016_TODOS_UBACyT-PC2013-2016-integrantes-sin-rol_sociales.pdf': (2013, ['unidad','code','ape','nom','titulo'], 'PROGRAMACION CIENTIFICA 2013-2016'),
}
CODE = re.compile(r'\b2\d{13}(?:BA)?\b')
def segs(l): return [(m.start(), m.end(), m.group()) for m in re.finditer(r'\S+(?: \S+)*', l)]
rows = []
for fn, (year, cols, conv) in SPECS.items():
    txt = subprocess.run(['pdftotext','-layout',os.path.join(SRC,fn),'-'],capture_output=True,text=True).stdout
    bad = 0
    for pi, pg in enumerate(txt.split('\f'), 1):
        lines = pg.split('\n')
        codes = [i for i,l in enumerate(lines) if CODE.search(l)]
        recs = {}
        for i in codes:
            sg = segs(lines[i])
            # separar segmentos que pegan columnas con un solo espacio (código + SIPI)
            out = []
            for a,b,t in sg:
                m = re.match(r'^(2\d{13}(?:BA)?) (\S+)(?: (.*))?$', t)
                if m and len(sg) < len(cols):
                    out.append((a, a+len(m.group(1)), m.group(1))); out.append((a+len(m.group(1))+1, a+len(m.group(1))+1+len(m.group(2)), m.group(2)))
                    if m.group(3): out.append((b-len(m.group(3)), b, m.group(3)))
                else: out.append((a,b,t))
            sg = out
            # fusionar segmentos hasta tener len(cols) campos: si sobran, error
            if len(sg) < len(cols) - 1 or len(sg) > len(cols):
                # intentar separar por 1 espacio no: registrar
                pass
            recs[i] = {'segs': sg, 'extra': {c: [] for c in cols}}
        for j,l in enumerate(lines):
            if j in recs or not l.strip() or not codes: continue
            if re.search(r'C[oó]digo|Apellido|Unidad Acad', l, re.I) and j < codes[0]: continue
            near = min(codes, key=lambda c: (abs(c-j), c))  # empate: el de abajo (celdas centradas)
            if abs(near - j) > 4: continue
            r = recs[near]
            for a,b,t in segs(l):
                ctr = (a+b)/2
                k = min(range(len(r['segs'])), key=lambda x: abs((r['segs'][x][0]+r['segs'][x][1])/2-ctr))
                r['extra'].setdefault(k, []).append((j, t))
        for i in codes:
            r = recs[i]; sg = r['segs']
            if len(sg) != len(cols): bad += 1; continue
            f = {}
            for k,c in enumerate(cols):
                parts = [(j,t) for j,t in r['extra'].get(k, []) if isinstance(k,int)] + [(i, sg[k][2])]
                f[c] = ' '.join(t for _,t in sorted(parts))
            name = f['name'] if 'name' in f else f"{f['ape']}, {f['nom']}"
            code = CODE.search(f['code']).group()
            rows.append([year, code, conv, re.sub(r'\s+',' ',name), f.get('rol',''), f.get('titulo',''), f.get('unidad',''), pi, i, fn])
    print(fn, 'filas descartadas (columnas no alineadas):', bad, file=sys.stderr)
with open(OUT,'w',newline='') as fo:
    w=csv.writer(fo,delimiter='\t'); w.writerow(['anio','codigo','convocatoria','integrante','rol','titulo','unidad','pagina','linea','archivo']); w.writerows(rows)
print(len(rows))
