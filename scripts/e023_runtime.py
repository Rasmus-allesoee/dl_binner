#!/usr/bin/env python3
"""Read-only native E023 dependency inventory against the admitted E022 prefix.

Verify every installed distribution and original package/default member; import
only the exercised graph family in a separate process, accepting normal loader
aliases by resolved bytes. The changed research source is bound separately.
"""
import argparse
import hashlib
import importlib.metadata as metadata
import json
from pathlib import Path
import platform
import re
import subprocess
import sys


def bound(path):
    """Bind a regular resolved library target or owned original package member."""
    p=Path(path);return dict(bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest())


def main():
    """Require exact isolated lexical prefix, versions, installed source and graph libs."""
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--reference',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True);a=p.parse_args();ref=json.loads(a.reference.read_text())
    if not sys.flags.isolated or not sys.dont_write_bytecode or str(Path(sys.prefix).absolute())!=ref['prefix']:
        raise ValueError('Accepted isolated lexical numerical prefix required')
    if platform.python_version()!=ref['python'].split()[0]:raise ValueError('Accepted Python version differs')
    normalize=lambda x:re.sub(r'[-_.]+','-',x.lower());actual={};locations={}
    for d in metadata.distributions():
        name=normalize(d.metadata['Name'])
        if name in actual:raise ValueError('Duplicate distribution')
        actual[name]=d.version;locations[name]=str(Path(d._path).resolve())
    if actual!=ref['distributions']or locations!=ref['locations']:raise ValueError('Complete native distribution versions/origins differ')
    import dl_binner
    package=Path(dl_binner.__file__).parent
    files={str(f.relative_to(package)):bound(f)for f in package.rglob('*')if f.is_file()and f.suffix in ['.py','.json']}
    if files!=ref['package_files']:raise ValueError('Original installed comparator source/defaults differ')
    code='''import importlib,json,hashlib
from pathlib import Path
names=['scipy','sklearn','numba','pynndescent','igraph','leidenalg']
origins={n:str(Path(importlib.import_module(n).__file__).resolve())for n in names}
import numba
numba.set_num_threads(4)
from threadpoolctl import threadpool_info
pools=threadpool_info();libraries={}
if any(p['num_threads']>4 for p in pools):raise ValueError('Native thread cap exceeded')
if any(p['prefix']=='libiomp'for p in pools)and any(p['prefix']=='libomp'for p in pools):raise ValueError('Conflicting OpenMP families')
for x in pools:
 p=Path(x['filepath']).resolve(strict=True)
 libraries[x['filepath']]=dict(bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest(),resolved=str(p))
print(json.dumps(dict(origins=origins,pools=pools,libraries=libraries)))'''
    child=subprocess.run([sys.executable,'-I','-B','-c',code],check=True,capture_output=True,text=True,timeout=180)
    graph=json.loads(child.stdout.splitlines()[-1]);accepted=ref['groups']['graph']
    if graph['origins']!=accepted['origins']:raise ValueError('Native graph import origins differ')
    old={b['sha256'] for b in accepted['libraries'].values()}
    if not graph['libraries']or not{b['sha256']for b in graph['libraries'].values()}<=old:raise ValueError('Native loaded graph library bytes differ')
    result=dict(status='PASS_COMPLETE_RETAINED_DISTRIBUTIONS_SOURCE_AND_GRAPH_LIBRARIES',python=sys.version,prefix=sys.prefix,
                distributions=actual,locations=locations,graph=graph,package_files=files,reference=bound(a.reference),
                scope='Complete distributions/origins and old package; exercised graph libraries only, no tensor import or whole-prefix claim')
    with a.output.open('x')as f:json.dump(result,f,indent=2);f.write('\n')
    print('E023_NATIVE_RUNTIME_PASS',len(actual),len(files),flush=True)


if __name__=='__main__':main()
