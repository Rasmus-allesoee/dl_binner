#!/usr/bin/env python3
"""Verify a new package-only E033 prefix against its accepted complete CPU base.

Use e033_install.py for actual pinned installation. This read-only probe checks
every distribution and owned project member, then isolates tensor/graph/marker
imports in separate processes. Accepted native library targets are content-bound;
unused headers, tests and CUDA environments are not recursively rehashed.
"""
import argparse
import hashlib
import importlib.metadata as metadata
import json
from pathlib import Path
import re
import subprocess
import sys


def main():
    """Require the frozen package, full versions/origins and accepted math libraries."""
    p=argparse.ArgumentParser(description=__doc__)
    for name in ['base','reference','candidate-lock','output','pysam-wheel']:p.add_argument('--'+name,type=Path,required=True)
    a=p.parse_args();base=a.base.absolute();prefix=Path(sys.prefix).absolute();reference=json.loads(a.reference.read_text());lock=json.loads(a.candidate_lock.read_text())
    if not sys.flags.isolated or not sys.dont_write_bytecode or prefix==base:raise ValueError('New isolated bytecode-free prefix required')
    before=reference.get('inventory',reference);expected={k:(v['version']if isinstance(v,dict)else v)for k,v in before['distributions'].items()}
    import platform
    expected_python=before.get('python_version',before.get('python','').split()[0] if before.get('python') else None)
    if expected_python!=platform.python_version():raise ValueError('Accepted interpreter version differs')
    expected['dl-binner']='0.1.0.dev9';expected['pysam']='0.23.3';normalize=lambda x:re.sub(r'[-_.]+','-',x.lower())
    actual={};locations={}
    for d in metadata.distributions():
        name=normalize(d.metadata['Name']);location=Path(d._path).resolve()
        if name in actual:raise ValueError('Duplicate distribution')
        allowed=prefix if name in ['dl-binner','pysam'] else base
        if not location.is_relative_to(allowed.resolve()):raise ValueError('Foreign distribution origin '+name)
        actual[name]=d.version;locations[name]=str(location)
    if actual!=expected:raise ValueError('Complete accepted dependency inventory differs')
    import dl_binner
    package=Path(dl_binner.__file__).parent
    def bound(path):return dict(bytes=path.stat().st_size,sha256=hashlib.sha256(path.read_bytes()).hexdigest())
    if package.is_symlink()or not package.is_relative_to(prefix):raise ValueError('New product is not owned')
    files={str(f.relative_to(package)):bound(f)for f in package.rglob('*')if f.is_file()and f.suffix in ['.py','.json']}
    if files!=lock['package_files']:raise ValueError('Installed candidate source/defaults differ')
    def hashes(value):
        if isinstance(value,dict):
            if set(value)>={'bytes','sha256'}:yield value['sha256']
            for v in value.values():yield from hashes(v)
        elif isinstance(value,list):
            for v in value:yield from hashes(v)
    accepted=set(hashes(reference.get('loaded_library_aliases',reference.get('isolated_native_probe',{}).get('libraries',reference.get('groups',{})))))
    if not accepted:raise ValueError('Accepted library content bindings missing')
    groups={}
    for label,names in {'tensor':['numpy','torch'],'graph':['scipy','sklearn','numba','pynndescent','igraph','leidenalg'],'markers':['pyhmmer','pyrodigal','archspec'],'BAM':['pysam']}.items():
        code='''import importlib,json,sys,hashlib
from pathlib import Path
origins={n:str(Path(importlib.import_module(n).__file__).resolve())for n in sys.argv[1].split(',')}
if 'torch'in sys.modules:
 t=sys.modules['torch'];t.set_num_threads(4);t.set_num_interop_threads(1)
 if t.version.cuda is not None:raise ValueError('CPU runtime required')
if 'numba'in sys.modules:sys.modules['numba'].set_num_threads(4)
from threadpoolctl import threadpool_info
pools=threadpool_info();libs={}
if any(x['num_threads']>4 for x in pools):raise ValueError('Numerical thread budget exceeded')
if any(x['prefix']=='libiomp'for x in pools)and any(x['prefix']=='libomp'for x in pools):raise ValueError('Conflicting OpenMP families')
for x in pools:
 p=Path(x['filepath']).resolve(strict=True);libs[x['filepath']]=dict(resolved=str(p),bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest())
print(json.dumps(dict(origins=origins,pools=pools,libraries=libs)))'''
        result=subprocess.run([sys.executable,'-I','-B','-c',code,','.join(names)],capture_output=True,text=True,check=True,timeout=180)
        g=json.loads(result.stdout.splitlines()[-1]);groups[label]=g
        for name,f in g['origins'].items():
            allowed=prefix if name=='pysam' else base
            if not Path(f).is_relative_to(allowed.resolve()):raise ValueError('Foreign native import '+name)
        if not set(hashes(g['libraries']))<=accepted:raise ValueError('Loaded native library content changed')
    # Bind owned HTSlib extension and vendored libraries to the exact installed
    # platform wheel, distinct from the accepted old numerical-base family.
    import zipfile
    if bound(a.pysam_wheel)!=lock['pysam_wheel']:raise ValueError('Pinned pysam wheel differs')
    owned={}
    with zipfile.ZipFile(a.pysam_wheel) as z:
        for n in z.namelist():
            if n.endswith('/') or n.endswith('.dist-info/RECORD'):continue
            if n.startswith('/') or '..' in Path(n).parts or '.data' in Path(n).parts:raise ValueError('Unexpected pysam wheel layout')
            p=prefix/'lib'/('python'+str(sys.version_info.major)+'.'+str(sys.version_info.minor))/'site-packages'/n
            b=dict(bytes=len(z.read(n)),sha256=hashlib.sha256(z.read(n)).hexdigest())
            if p.is_symlink() or bound(p)!=b:raise ValueError('Owned pysam file differs: '+n)
            owned[n]=b
    cli=subprocess.run([str(prefix/'bin/dl-binner'),'--help'],capture_output=True,text=True,
        cwd=a.output.parent,timeout=30)
    if cli.returncode or 'context-stage' not in cli.stdout or 'relation-stage' not in cli.stdout:
        raise ValueError('Actual installed console entry point differs')
    value=dict(status='PASS_COMPLETE_READONLY_BASE_AND_NEW_OWNED_PACKAGE',prefix=str(prefix),base=str(base),
        python=sys.version,distributions=actual,locations=locations,package_files=files,groups=groups,
        actual_installed_console_help=True,pysam_wheel_owned_files=owned,
        scope='Complete distribution versions/origins, own package source and actual loaded native libraries; not whole-prefix nonmutation',portable=False)
    with a.output.open('x')as f:json.dump(value,f,indent=2);f.write('\n')
    print('E033_RUNTIME_PASS',len(actual),len(files),flush=True)


if __name__=='__main__':main()
