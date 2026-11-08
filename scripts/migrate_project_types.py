"""Agrega Tipo de proyecto a la base histórica sin alterar sus datos originales.

La inferencia se usa solo al migrar las nueve columnas históricas de UBACyT/PDE/
PIUBAS. Las bases ampliadas deben declarar el tipo explícitamente en cada fila.
"""
from collections import Counter
from copy import copy
from hashlib import sha256
from pathlib import Path
from tempfile import NamedTemporaryFile
import argparse, json, os, re, shutil
import openpyxl
from openpyxl.comments import Comment
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.table import TableColumn

ROOT=Path(__file__).resolve().parents[1]
LEGACY_COLUMNS=['Año del listado','Código proyecto','Convocatoria','Integrante','Rol integrante','Título del proyecto','Unidad académica','Página PDF','Fila en página']

def infer_legacy_type(code,call=''):
    code=re.sub(r'\s+',' ',str(code or '')).strip().upper()
    call=re.sub(r'\s+',' ',str(call or '')).strip().upper()
    if code.startswith('PDE'):return 'PDE'
    if code.startswith('PIUBA'):return 'PIUBAS'
    if call.startswith('UBACYT') or re.fullmatch(r'\d{14,16}(?:BA)?',code):return 'UBACYT'
    raise ValueError(f'No se puede inferir el tipo histórico: {code}. Informarlo explícitamente.')

def migrate(path):
    initial_hash=sha256(path.read_bytes()).hexdigest()
    wb=openpyxl.load_workbook(path)
    ws=wb['Datos']
    headers=[c.value for c in ws[1]]
    if 'Tipo de proyecto' in headers:
        index=headers.index('Tipo de proyecto')+1
        values=[ws.cell(r,index).value for r in range(2,ws.max_row+1)]
        if any(not isinstance(v,str) or not v.strip() for v in values):raise ValueError('Hay tipos de proyecto vacíos; revisarlos antes de procesar.')
        wb.close()
        return {'modified':False,'rows':len(values),'types':dict(Counter(values)),'sha256':initial_hash}
    if headers!=LEGACY_COLUMNS:raise ValueError('La migración requiere exactamente las nueve columnas históricas.')
    originals=list(ws.iter_rows(min_row=2,values_only=True))
    original_styles=[tuple(c.style_id for c in row) for row in ws.iter_rows()]
    other_sheets={s.title:[tuple((c.value,c.style_id,c.number_format) for c in row) for row in s.iter_rows()] for s in wb if s.title!=ws.title}
    original_freeze=ws.freeze_panes
    original_auto_filter=ws.auto_filter.ref
    original_widths={name:dimension.width for name,dimension in ws.column_dimensions.items()}
    types=[infer_legacy_type(row[1],row[2]) for row in originals]
    backup=path.parent/'respaldos'/f'{path.stem}.antes_tipo_proyecto_{initial_hash[:12]}.xlsx'
    backup.parent.mkdir(parents=True,exist_ok=True)
    if backup.exists():assert sha256(backup.read_bytes()).hexdigest()==initial_hash
    else:shutil.copy2(path,backup)
    col=len(headers)+1
    ws.cell(1,col,'Tipo de proyecto')._style=copy(ws.cell(1,7)._style)
    ws.cell(1,col).comment=Comment('Tipo explícito para integrar financiamientos. La migración histórica distingue UBACYT, PDE y PIUBAS; las nuevas bases deben informar su tipo en cada fila.','Criterios del grafo')
    ws.column_dimensions[get_column_letter(col)].width=22
    for row,value in enumerate(types,start=2):
        cell=ws.cell(row,col,value)
        cell._style=copy(ws.cell(row,5)._style)
        cell.number_format='@'
    new_ref=f'A1:{get_column_letter(col)}{ws.max_row}'
    if ws.auto_filter.ref:ws.auto_filter.ref=new_ref
    for table in ws.tables.values():
        table.ref=new_ref
        table.tableColumns.append(TableColumn(id=max(c.id for c in table.tableColumns)+1,name='Tipo de proyecto'))
        if table.autoFilter is not None:table.autoFilter.ref=new_ref
    with NamedTemporaryFile(prefix='tipo_proyecto_',suffix='.xlsx',dir=path.parent,delete=False) as handle:
        temporary=Path(handle.name)
    try:
        wb.save(temporary);wb.close()
        check=openpyxl.load_workbook(temporary,read_only=False,data_only=False)
        rows=list(check['Datos'].iter_rows(min_row=2,values_only=True))
        assert len(rows)==len(originals)
        assert all(tuple(row[:9])==tuple(original) and row[9]==kind for row,original,kind in zip(rows,originals,types))
        assert [tuple(c.style_id for c in row) for row in check['Datos'].iter_rows(max_col=9)]==original_styles
        assert {s.title:[tuple((c.value,c.style_id,c.number_format) for c in row) for row in s.iter_rows()] for s in check if s.title!='Datos'}==other_sheets
        structure=check
        assert structure['Datos'].freeze_panes==original_freeze
        assert all(structure['Datos'].column_dimensions[name].width==width for name,width in original_widths.items())
        assert structure['Datos'].auto_filter.ref==(new_ref if original_auto_filter else original_auto_filter)
        assert all(t.ref==new_ref and [c.name for c in t.tableColumns]==headers+['Tipo de proyecto'] for t in structure['Datos'].tables.values())
        structure.close()
        assert sha256(path.read_bytes()).hexdigest()==initial_hash,'El archivo cambió durante la migración; no se reemplaza.'
        os.replace(temporary,path)
    finally:
        if temporary.exists():temporary.unlink()
    return {'modified':True,'rows':len(types),'types':dict(Counter(types)),
            'backup':str(backup),'beforeSha256':initial_hash,'afterSha256':sha256(path.read_bytes()).hexdigest(),
            'originalCellsPreserved':len(originals)*len(LEGACY_COLUMNS),'originalStylesAndOtherSheetsPreserved':True}

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--excel',type=Path,default=ROOT/'output/xlsx/UBACYT-consolidado-2021-2022-2023.xlsx')
    result=migrate(parser.parse_args().excel)
    print(json.dumps(result,ensure_ascii=False))
