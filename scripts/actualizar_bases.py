"""Ejecuta la notebook existente y reconstruye/verifica el visor. No publica."""
from pathlib import Path
import os,sys,subprocess,json,tempfile
ROOT=Path(__file__).resolve().parents[1]
fallback=ROOT/'tmp/grafos_runtime'
if fallback.exists():sys.path.insert(0,str(fallback))
def run(args):subprocess.run(args,cwd=ROOT,check=True)
def main():
 import nbformat
 from nbclient import NotebookClient
 run([sys.executable,str(ROOT/'scripts/importar_listados_excel.py')])
 path=ROOT/'notebooks/ubacyt_grafo.ipynb';book=nbformat.read(path,as_version=4)
 work=ROOT/'tmp/ejecucion_notebook';work.mkdir(parents=True,exist_ok=True)
 spec=work/'data/kernels/grafo-local';spec.mkdir(parents=True,exist_ok=True)
 env={'GRAFO_UBACYT_RAIZ':str(ROOT)}
 if fallback.exists():env['PYTHONPATH']=str(fallback)
 (spec/'kernel.json').write_text(json.dumps({'argv':[sys.executable,'-m','ipykernel_launcher','-f','{connection_file}'],'display_name':'Grafo local','language':'python','env':env}),encoding='utf-8')
 os.environ['JUPYTER_PATH']=str(work/'data');os.environ['JUPYTER_RUNTIME_DIR']=str(work/'runtime');os.environ['IPYTHONDIR']=str(work/'ipython');(work/'runtime').mkdir(exist_ok=True)
 if os.name=='nt':
  import asyncio
  asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
 NotebookClient(book,timeout=900,kernel_name='grafo-local',resources={'metadata':{'path':str(ROOT)}},allow_errors=False).execute()
 nbformat.validate(book);temp=path.with_suffix('.tmp.ipynb');nbformat.write(book,temp);os.replace(temp,path)
 run([sys.executable,'scripts/build_web_data.py']);run(['node','web/scripts/layout.mjs']);run([sys.executable,'scripts/validate_web_data.py'])
 run(['node','--test','web/tests/filters.test.mjs'])
 subprocess.run(['node','node_modules/vite/bin/vite.js','build','--base=/grafo_investigacion/'],cwd=ROOT/'web',check=True)
 print('Base, notebook y visor actualizados y verificados. No se publicó en GitHub.')
if __name__=='__main__':main()
