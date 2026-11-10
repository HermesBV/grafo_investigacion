"""Integra listados parciales verificados, conservando las columnas originales."""
from pathlib import Path
from hashlib import sha256
from copy import copy
from collections import Counter
import json,os,shutil,sys
import openpyxl
from openpyxl.worksheet.table import TableColumn
ROOT=Path(__file__).resolve().parents[1]
def main():
 base=ROOT/'output/xlsx/UBACYT-consolidado-2021-2022-2023.xlsx'
 before=sha256(base.read_bytes()).hexdigest();w=openpyxl.load_workbook(base);s=w['Datos']
 headers=[c.value for c in s[1]];oldrows=list(s.values);original_columns=len(headers)
 if 'fuente_completa' not in headers:
  assert original_columns==10
  s.cell(1,11,'fuente_completa')._style=copy(s.cell(1,10)._style)
  for i in range(2,s.max_row+1):s.cell(i,11,'completa')._style=copy(s.cell(i,10)._style)
  headers.append('fuente_completa');s.column_dimensions['K'].width=38
  for t in s.tables.values():t.tableColumns.append(TableColumn(id=11,name='fuente_completa'))
 seen={tuple(r[i] for i in [0,1,2,3,4,5,6,9,10]) for r in list(s.values)[1:]}
 catalog=json.loads((ROOT/'fuentes-ubacyt.json').read_text(encoding='utf-8'));report=[];new=[]
 for e in catalog['entries']:
  if e['year'] not in [2024,2026] or e.get('level')!='proyectos':continue
  path=ROOT/e['file'];assert sha256(path.read_bytes()).hexdigest()==e['sha256']
  source=openpyxl.load_workbook(path,read_only=True);sheet=source[e['sheet']];rows=sheet.iter_rows(values_only=True);cols=next(rows);count=0;members=0
  for rownum,values in enumerate(rows,2):
   d=dict(zip(cols,values));code=d.get('Código Proyecto')
   if not code:continue
   count+=1;code=str(code).strip();kind='PDE' if code.upper().startswith('PDE') else 'UBACYT' if str(d.get('Convocatoria','')).upper().startswith('UBACYT') else None
   assert kind,('Revisar tipo',code)
   last=d['Apellido Director/a'];first=d['Nombres Director/a'];assert last and first,(code,'Sin director')
   people=[(f'{last}, {first}','DIRECTOR')]
   for co in str(d.get('Codirector/es') or '').split(';'):
    if co.strip():
     assert ',' in co,('Codirector ambiguo',code,co)
     people.append((co.strip(),'CODIRECTOR'))
   for person,role in people:
    members+=1;r=[e['year'],code,d.get('Convocatoria'),person,role,d.get('Título del proyecto') or d.get('Título'),d['Unidad Académica'],0,rownum,kind,'sólo dirección y codirección']
    key=tuple(r[i] for i in [0,1,2,3,4,5,6,9,10])
    if key not in seen:new.append(r);seen.add(key)
  source.close();assert count==e['rows_with_code']
  report.append({'año':e['year'],'registros_fuente':count,'participaciones_leídas':members,'url':e['url'],'sha256':e['sha256']})
 if not new and original_columns==11:
  w.close();print('Importación idempotente: sin cambios');return
 for row in new:
  index=s.max_row+1;s.append(row)
  for col in range(1,12):s.cell(index,col)._style=copy(s.cell(2,min(col,10))._style)
  s.row_dimensions[index].height=60
 ref=f'A1:K{s.max_row}'
 for t in s.tables.values():
  t.ref=ref
  if t.autoFilter:t.autoFilter.ref=ref
 if s.auto_filter.ref:s.auto_filter.ref=ref
 backup=base.parent/'respaldos'/f'{base.stem}.antes_cobertura_{before[:12]}.xlsx';backup.parent.mkdir(exist_ok=True)
 if not backup.exists():shutil.copy2(base,backup)
 temp=base.with_name(base.stem+'.importacion.tmp.xlsx');w.save(temp);w.close()
 check=openpyxl.load_workbook(temp,read_only=True);out=list(check['Datos'].values)
 assert all(tuple(r[:original_columns])==tuple(o) for r,o in zip(out,oldrows) if r is not out[0])
 assert len(out)==len(oldrows)+len(new)
 expected_complete=sum(r[10]=='completa' for r in oldrows[1:]) if original_columns==11 else len(oldrows)-1
 assert Counter(r[10] for r in out[1:])['completa']==expected_complete
 check.close();assert sha256(base.read_bytes()).hexdigest()==before;os.replace(temp,base)
 (ROOT/'tmp/importacion_cobertura.json').write_text(json.dumps({'filas_agregadas':len(new),'fuentes':report,'filas_totales':len(out)-1},ensure_ascii=False,indent=2),encoding='utf-8')
 print(json.dumps({'filas_agregadas':len(new),'filas_totales':len(out)-1,'fuentes':report},ensure_ascii=False))
if __name__=='__main__':main()
