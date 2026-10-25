#!/usr/bin/env python3
"""Build fresh E022 wheel/sdist/rebuilt wheel with separate pinned backend hooks.

Reads only explicit project sources, excludes bytecode/build leftovers, and
compares logical wheel members. Never installs into an accepted environment.
"""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tarfile
import zipfile


def main():
    """Create a new source/build layout and record actual distribution identities."""
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    repo=Path(__file__).absolute().parents[1];out=a.output.absolute();out.mkdir(parents=True,exist_ok=False)
    source=out/'source';source.mkdir();files={}
    for path in [repo/'pyproject.toml',repo/'README.md',repo/'LICENSE']+sorted((repo/'src').rglob('*')):
        if not path.is_file() or path.suffix in ['.pyc','.pyo'] or '__pycache__' in path.parts or path.name=='.DS_Store' or any(x.endswith('.egg-info') for x in path.parts):continue
        if path.is_symlink():raise ValueError('Unexpected source link')
        relative=path.relative_to(repo);dest=source/relative;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(path,dest)
        files[str(relative)]=dict(bytes=dest.stat().st_size,sha256=hashlib.sha256(dest.read_bytes()).hexdigest())
    import importlib.metadata as m
    if m.version('setuptools')!='78.1.1' or m.version('wheel')!='0.45.1' or not (3,10)<=sys.version_info[:2]<(3,13):raise ValueError('Pinned supported builder required')
    dist=out/'dist';dist.mkdir()
    for hook in ['build_sdist','build_wheel']:
        subprocess.run([sys.executable,'-I','-B','-c',f'import setuptools.build_meta as b; b.{hook}({str(dist)!r})'],cwd=source,check=True)
    sdist=next(dist.glob('*.tar.gz'));rebuilt=out/'rebuilt';rebuilt.mkdir()
    with tarfile.open(sdist)as archive:archive.extractall(rebuilt,filter='data')
    rebuild_source=next(p for p in rebuilt.iterdir()if p.is_dir());redist=out/'redist';redist.mkdir()
    subprocess.run([sys.executable,'-I','-B','-c',f'import setuptools.build_meta as b; b.build_wheel({str(redist)!r})'],cwd=rebuild_source,check=True)
    def members(path):
        with zipfile.ZipFile(path)as z:return {n:hashlib.sha256(z.read(n)).hexdigest()for n in z.namelist()if not n.endswith('/')}
    wheel=next(dist.glob('*.whl'));again=next(redist.glob('*.whl'))
    if members(wheel)!=members(again):raise ValueError('Rebuilt wheel logical members differ')
    (out/'packaging.json').write_text(json.dumps(dict(status='PASS_WHEEL_SDIST_REBUILT_LOGICAL_CONTENT',source=files,
        wheel=str(wheel),sdist=str(sdist),logical_members=members(wheel),builder=dict(python=sys.version,setuptools=m.version('setuptools'),wheel=m.version('wheel'))),indent=2)+'\n')
    print('E022_PACKAGING_PASS',wheel,flush=True)


if __name__=='__main__':main()
