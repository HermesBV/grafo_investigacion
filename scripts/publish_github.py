"""Publica el repositorio solicitado usando GitHub CLI, con control de cuenta.

Requiere haber iniciado sesión con `gh auth login` en bustosthl. No recibe tokens.
"""
from __future__ import annotations
import json, shutil, subprocess, sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
REPO='bustosthl/grafo_investigacion'
URL='https://bustosthl.github.io/grafo_investigacion/'
GH=shutil.which('gh') or str(ROOT/'tmp/github-cli/gh.exe')

def command(args, payload=None, check=True):
    result=subprocess.run(args,cwd=ROOT,input=payload,text=True,capture_output=True)
    if check and result.returncode:
        raise RuntimeError(result.stderr.strip() or result.stdout.strip())
    return result

def api(path, method='GET', body=None, check=True):
    args=[GH,'api','--method',method,path]
    if body is not None: args.extend(['--input','-'])
    result=command(args,json.dumps(body) if body is not None else None,check=check)
    return result, json.loads(result.stdout) if result.returncode==0 and result.stdout.strip() else None

def main():
    _,user=api('user')
    if user['login'] != 'bustosthl':
        raise RuntimeError(f'Cuenta conectada: {user["login"]}. Solo se publica desde bustosthl.')
    root=command(['git','rev-parse','--show-toplevel']).stdout.strip()
    assert Path(root).resolve()==ROOT, 'Repositorio local incorrecto'
    assert command(['git','branch','--show-current']).stdout.strip()=='main', 'Publicar desde main'
    assert not command(['git','log','--format=%H','main','--','output/xlsx']).stdout.strip(), 'El historial de main incluye Excel de trabajo. Usar el historial público antes de publicar.'
    assert command(['git','status','--porcelain','--untracked-files=no']).stdout.strip()=='', 'Hay cambios sin confirmar'
    remote=command(['git','remote','get-url','origin']).stdout.strip()
    assert remote=='https://github.com/'+REPO+'.git', 'Destino remoto incorrecto'
    result,repo=api('repos/'+REPO,check=False)
    if result.returncode:
        if '404' not in result.stderr:raise RuntimeError(result.stderr)
        result=command([GH,'repo','create',REPO,'--public','--description','Explorador de personas, proyectos y colaboraciones UBACyT 2021–2023','--homepage',URL])
        print(result.stdout.strip())
    else:
        assert repo['owner']['login']=='bustosthl' and not repo['private'], 'Revisar propietario o visibilidad'
    # Credencial temporal para este comando; no cambia los helpers globales de Git.
    helper='!"'+str(Path(GH).resolve()).replace('\\','/')+'" auth git-credential'
    result=command(['git','-c','credential.helper=','-c','credential.helper='+helper,'push','--set-upstream','origin','main'])
    print(result.stdout.strip() or result.stderr.strip())
    response,pages=api('repos/'+REPO+'/pages',check=False)
    if response.returncode:
        if '404' not in response.stderr:raise RuntimeError(response.stderr)
        _,pages=api('repos/'+REPO+'/pages','POST',{'build_type':'workflow'})
    elif pages['build_type']!='workflow':
        _,pages=api('repos/'+REPO+'/pages','PUT',{'build_type':'workflow'})
    print(json.dumps({'repository':'https://github.com/'+REPO,'site':pages.get('html_url',URL),'build_type':pages.get('build_type'),'account':user['login']},ensure_ascii=False))

if __name__=='__main__':
    try:main()
    except Exception as error:
        print(str(error),file=sys.stderr)
        raise SystemExit(1)
