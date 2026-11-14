"""Parsea resoluciones UBACyT (acreditación/otorgamiento) -> TSV dir/codir."""
import re, subprocess, sys, os, csv, unicodedata
SRC = sys.argv[1]; OUT = sys.argv[2]
CODE = re.compile(r'^\s{0,12}(2\d{13}(?:BA)?|HyM\d+-\d{4}|H ?F\d{2})(?=\s)\s*(.*)$')
ROLE = re.compile(r'^\s*(CO-?D[I1l]RECTOR[A]?|COD[I1l],?RECTOR[A]?|D[I1l]RECTOR[A]?|Co-?[Dd]irector[a]?|Codirector[a]?|Director[a]?)\s*[:.;]\s*(.+?)\s*(?:D\s*N\s*[I1l]\s*[:.;]?\s*[\d.\s]*)?$')
UA = re.compile(r'^\s*Un[il1]dad\s+Acad\S*\s*[:.]?\s*(.*)$', re.I)
ANEXO = re.compile(r'^(?:\s*|.*\S\s{3,})Anexo\s+([IVXLl1]+)\s*(?:-\s*\d+\s*-)?\s*$')
MONTO = re.compile(r'\s*\$\s*[\d .,]+\s*$')
# (patrón de archivo, año del listado, anexos excluidos = no acreditados/no admitidos, convocatoria)
FILES = [
 ('Res2657', 2011, set(), 'PROGRAMACION CIENTIFICA 2011-2014'),
 ('Res6932-13', 2013, {'VI'}, 'PROGRAMACION CIENTIFICA 2013-2016'),
 ('Res1271-14', 2014, set(), 'PROGRAMACION CIENTIFICA 2014-2017'),
 ('Res1268-14', 2014, set(), 'PROGRAMACION CIENTIFICA 2014-2017 INTERDISCIPLINARIOS'),
 ('Res777-14', 2014, {'II'}, 'PROGRAMACION CIENTIFICA 2014-2017 HISTORIA Y MEMORIA'),
 ('Res4756-16', 2016, {'VIII'}, 'PROGRAMACION CIENTIFICA 2016'),
 ('Res4912-16', 2016, {'V'}, 'PROGRAMACION CIENTIFICA 2016 CLINICOS'),
 ('Res5015-16', 2016, set(), 'PROGRAMACION CIENTIFICA 2016'),
 ('Res6903-17', 2017, {'IV','V'}, 'PROGRAMACION CIENTIFICA 2017'),
 ('Res7053-17', 2017, set(), 'PROGRAMACION CIENTIFICA 2017'),
 ('Res7245-17', 2017, set(), 'PROGRAMACION CIENTIFICA 2017 HISTORIA Y MEMORIA'),
 ('Res1041-18', 2018, {'V'}, 'PROGRAMACION CIENTIFICA 2018'),
 ('Res1244-18', 2018, {'IV'}, 'PROGRAMACION CIENTIFICA 2018'),
 ('Res1359-18', 2018, {'III','IV'}, 'PROGRAMACION CIENTIFICA 2018 CLINICOS'),
 ('RESCS-2020-345', 2020, {'IX','X'}, 'PROGRAMACION CIENTIFICA 2020'),
 ('RESCS-2023-1384', 2023, {'IX','X'}, 'PROGRAMACION CIENTIFICA 2023'),
 ('RESCS-2026-1048', 2026, {'V','VI'}, 'PROGRAMACION CIENTIFICA 2026'),
 ('RESCS-2026-1471', 2026, set(), 'PROGRAMACION CIENTIFICA 2026 INTERDISCIPLINARIOS'),
 ('RESCS-2023-1966', 2024, set(), 'PROGRAMACION CIENTIFICA 2020'),
 ('RESCS-2023-1965', 2024, set(), 'PROGRAMACION CIENTIFICA 2023'),
 ('RESCS-2025-289', 2025, set(), 'PROGRAMACION CIENTIFICA 2020'),
 ('RESCS-2025-288', 2025, set(), 'PROGRAMACION CIENTIFICA 2023'),
]
def roman(s): return s.replace('l','I').replace('1','I')
def norm_ocr_name(s):
    s = re.sub(r'\s+', ' ', s).strip(' .,;')
    return s
rows=[]
for fn in sorted(os.listdir(SRC)):
    if not fn.endswith('.pdf'): continue
    spec = next((f for f in FILES if f[0] in fn), None)
    if not spec: continue
    pat, year, excl, conv = spec
    # anexo inferido del nombre de archivo (archivos de un solo anexo)
    m = re.search(r'Anexo([IVX]+)', fn); file_anexo = m.group(1) if m else None
    txt = subprocess.run(['pdftotext','-layout',os.path.join(SRC,fn),'-'],capture_output=True,text=True).stdout
    pages = txt.split('\f')
    events=[]  # (page, line, kind, data)
    for pi,pg in enumerate(pages,1):
        for li,l in enumerate(pg.split('\n'),1):
            m = ANEXO.match(l)
            if m: events.append((pi,li,'anexo',roman(m.group(1)))); continue
            m = UA.match(l)
            if m and m.group(1).strip(): events.append((pi,li,'ua',m.group(1).strip())); continue
            m = CODE.match(l)
            if m: events.append((pi,li,'code',(m.group(1), MONTO.sub('',m.group(2)).strip()))); continue
            m = ROLE.match(l)
            if m and ',' in m.group(2): events.append((pi,li,'role',(m.group(1), m.group(2)))); continue
            if events and events[-1][2]=='code' or (events and events[-1][2]=='title'):
                t = MONTO.sub('', l).strip()
                if t and len(t)>2 and not re.match(r'^(EX|EXP|ACS|P[aá]gina|-\d)', t): events.append((pi,li,'title',t))
    fc = next((i for i,e in enumerate(events) if e[2]=='code'), None)
    fu = next((i for i,e in enumerate(events) if e[2]=='ua'), None)
    header_mode = fu is not None and fc is not None and fu < fc
    cur_anexo = file_anexo; last_ua=None; projs=[]; p=None; orphans=0
    for e in events:
        k=e[2]
        if k=='anexo' and not file_anexo: cur_anexo=e[3]
        elif k=='ua':
            last_ua=e[3]
            if not header_mode and p and p['ua'] is None: p['ua']=e[3]
        elif k=='code':
            p={'code':e[3][0],'title':[e[3][1]] if e[3][1] else [],'ua':last_ua if header_mode else None,'roles':[],'anexo':cur_anexo,'page':e[0],'line':e[1]}
            projs.append(p)
        elif k=='title' and p and not p['roles']: p['title'].append(e[3])
        elif k=='role' and p:
            isdir = not re.match(r'(?i)co', e[3][0])
            if isdir and any(not re.match(r'(?i)co', r) for r,_ in p['roles']):
                p=None; orphans+=1; continue  # director de un proyecto sin código legible (OCR)
            p['roles'].append(e[3])
    if orphans: print(fn, 'directores sin código descartados:', orphans, file=sys.stderr)
    for p in projs:
        if p['anexo'] in excl: continue
        title=' '.join(p['title']).strip()
        for i,(r,name) in enumerate(p['roles']):
            role = 'CODIRECTOR' if re.match(r'(?i)co',r) else 'DIRECTOR'
            name = re.sub(r'\s*D\s*N\s*[I1l]\b.*$','',name)
            rows.append([year,p['code'],conv,norm_ocr_name(name),role,title,p['ua'] or '',p['page'],p['line'],fn,p['anexo'] or ''])
with open(OUT,'w',newline='') as f:
    w=csv.writer(f,delimiter='\t'); w.writerow(['anio','codigo','convocatoria','integrante','rol','titulo','unidad','pagina','linea','archivo','anexo']); w.writerows(rows)
print(len(rows),'filas')
