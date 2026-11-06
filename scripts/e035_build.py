#!/usr/bin/env python3
"""Build a fresh E035 wheel/sdist and own its package over a read-only CPU base.

No dependency resolution, platform upgrade or base modification is performed.
The retained 3.10 local CPU runtime is engineering provenance, not Linux 3.12
admission. Each attempt has a new destination and immutable command logs.
"""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import zipfile

ROOT=Path(__file__).absolute().parents[1]


def run(root,builder,base):
    """Exercise separate packaging hooks and install the actual newly built wheel."""
    root=Path(root).absolute();root.mkdir(parents=True,exist_ok=False);build=root/'source';build.mkdir()
    for n in ['pyproject.toml','README.md']:shutil.copy2(ROOT/n,build/n)
    shutil.copytree(ROOT/'src',build/'src',ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
    def command(name,argv,cwd=None):
        with (root/(name+'.log')).open('x')as log:r=subprocess.run(list(map(str,argv)),stdout=log,stderr=subprocess.STDOUT,cwd=cwd)
        (root/(name+'.exit.json')).write_text(json.dumps(dict(argv=list(map(str,argv)),exit_code=r.returncode),indent=2)+'\n')
        if r.returncode:raise RuntimeError('Packaging failed; inspect '+str(root/(name+'.log')))
    wheel_dir=root/'dist';wheel_dir.mkdir()
    command('wheel',[builder,'-I','-B','-m','pip','--isolated','--cache-dir',root/'pip-cache','wheel','--no-deps','--no-index','--no-build-isolation','--wheel-dir',wheel_dir,build])
    command('sdist',[builder,'-I','-B','-c','import setuptools.build_meta as b;b.build_sdist("'+str(wheel_dir)+'")'],build)
    wheel=next(wheel_dir.glob('*.whl'));sdist=next(wheel_dir.glob('*.tar.gz'))
    import tarfile
    target=root/'sdist-rebuild';target.mkdir()
    with tarfile.open(sdist)as t:
        for m in t.getmembers():
            p=Path(m.name)
            if p.is_absolute()or '..'in p.parts or not (m.isfile()or m.isdir()):raise ValueError('Unsafe sdist member')
        t.extractall(target)
    command('rebuilt-wheel',[builder,'-I','-B','-m','pip','--isolated','--cache-dir',root/'pip-cache','wheel','--no-deps','--no-index','--no-build-isolation','--wheel-dir',root/'rebuilt',next(target.iterdir())])
    rebuilt=next((root/'rebuilt').glob('*.whl'))
    def source(path):
        with zipfile.ZipFile(path)as z:return {n:hashlib.sha256(z.read(n)).hexdigest()for n in z.namelist()if n.startswith('dl_binner/')}
    if source(wheel)!=source(rebuilt):raise ValueError('Rebuilt wheel package logical contents differ')
    command('install',[Path(base)/'bin/python','-I','-B',ROOT/'scripts/e019_runtime.py','create','--base',base,'--destination',root/'env','--wheel',wheel,'--output',root/'installed.json'])
    receipt=dict(status='PASS',builder=str(builder),read_only_dependency_base=str(base),python=str(root/'env/bin/python'),
        wheel=dict(bytes=wheel.stat().st_size,sha256=hashlib.sha256(wheel.read_bytes()).hexdigest()),
        sdist=dict(bytes=sdist.stat().st_size,sha256=hashlib.sha256(sdist.read_bytes()).hexdigest()),
        source_members=source(wheel),sdist_rebuilt_package_equal=True)
    (root/'completed.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps({k:v for k,v in receipt.items()if k!='source_members'}))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for name in ['root','builder','base']:p.add_argument('--'+name,type=Path,required=True)
    a=p.parse_args();run(a.root,a.builder.absolute(),a.base.absolute())
