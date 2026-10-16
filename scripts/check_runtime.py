#!/usr/bin/env python3
"""Validate a fresh standalone runtime's complete inventory and owned imports.

Runs inside its lexical venv Python with -I -B. Accepts only the version-pinned
closure in requirements, plus the installed dev3 binner for that role. No
scientific stage runs. Reports native prefix/origins, CPU pools and inventory,
rejecting foreign/user-site distributions or linked numerical dependencies.
"""
import argparse
import importlib
import importlib.metadata as metadata
import importlib.util
import json
from pathlib import Path
import platform
import re
import site
import subprocess
import sys


def normalize(name):
    """Canonicalize distribution names without accepting duplicate identities."""
    return re.sub(r'[-_.]+','-',name.lower())


def main():
    """Retain a complete standalone-prefix inventory after native imports pass."""
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--role',choices=('build','binner','candidate','workflow'),required=True)
    p.add_argument('--requirements',type=Path,required=True)
    p.add_argument('--threads',type=int,choices=range(1,9),default=4)
    p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();prefix=Path(sys.prefix).absolute()
    if sys.prefix==sys.base_prefix or site.ENABLE_USER_SITE:raise RuntimeError('A separate isolated venv is required')
    expected={}
    def lines(path):
        """Read explicit sibling requirement includes, never shell/pip option text."""
        for line in path.read_text().splitlines():
            if line.startswith('-r '):
                name=line[3:].strip()
                if Path(name).name!=name:raise ValueError('Unsafe requirement include')
                yield from lines(path.parent/name)
            else:yield line
    for line in lines(a.requirements):
        line=line.strip()
        if not line or line.startswith('#'):continue
        spec,separator,marker=line.partition(';')
        if separator:
            if marker.strip() not in ('platform_system == "Linux"','platform_system == "Darwin"'):raise ValueError('Unsupported requirement marker')
            if marker.split('"')[1]!=platform.system():continue
        name,version=spec.strip().split('==');expected[normalize(name)]=version
    if a.role in ('binner','candidate'):
        from dl_binner import __version__
        expected['dl-binner']=__version__
    distributions={};locations={}
    for d in metadata.distributions():
        name=normalize(d.metadata['Name'])
        if name in distributions:raise RuntimeError('Duplicate distribution: '+name)
        location=Path(d._path).resolve()
        if not location.is_relative_to(prefix.resolve()):raise RuntimeError('Distribution outside prefix: '+str(location))
        distributions[name]=d.version;locations[name]=str(location)
    if distributions!=expected:raise RuntimeError('Complete runtime inventory differs: '+str({k:(expected.get(k),distributions.get(k)) for k in expected.keys()|distributions.keys() if expected.get(k)!=distributions.get(k)}))
    names={'build':['setuptools','wheel'], 'binner':['dl_binner','numpy','torch','networkx','threadpoolctl'],
        'candidate':['dl_binner','numpy','torch','threadpoolctl','scipy','sklearn','numba','pynndescent','igraph','leidenalg','pyrodigal','pyhmmer','archspec'],
        'workflow':['snakemake']}[a.role]
    if a.role=='candidate':
        # Torch's Intel OpenMP and sklearn's LLVM OpenMP conflict on macOS.
        # Inventory all origins with separate native processes, mirroring the
        # production train/embed versus graph stage boundary. No suppression or
        # KMP_DUPLICATE_LIB_OK workaround is used.
        probes={}
        for label,modules in {'tensor':['dl_binner','numpy','torch','threadpoolctl'],
                             'graph':['scipy','sklearn','numba','pynndescent','igraph','leidenalg'],
                             'markers':['pyrodigal','pyhmmer','archspec']}.items():
            print('Native isolated group begin: '+label,flush=True)
            code='''import importlib,json,sys
from pathlib import Path
origins={}
for name in sys.argv[1].split(','):
 module=importlib.import_module(name);path=Path(module.__file__).resolve()
 if not path.is_relative_to(Path(sys.prefix).resolve()):raise RuntimeError('Foreign import '+str(path))
 origins[name]=str(path)
if 'torch' in sys.modules:
 t=sys.modules['torch'];t.set_num_threads(int(sys.argv[2]));t.set_num_interop_threads(1)
 if t.version.cuda is not None:raise RuntimeError('CPU Torch required')
if 'numba' in sys.modules:sys.modules['numba'].set_num_threads(int(sys.argv[2]))
from threadpoolctl import threadpool_info
pools=threadpool_info()
if any(p['num_threads']>int(sys.argv[2]) for p in pools):raise RuntimeError('Native pools exceed budget')
if any(p['prefix']=='libiomp' for p in pools) and any(p['prefix']=='libomp' for p in pools):raise RuntimeError('Conflicting OpenMP runtimes')
print(json.dumps(dict(origins=origins,pools=pools)))'''
            result=subprocess.run([sys.executable,'-I','-B','-c',code,','.join(modules),str(a.threads)],
                                  capture_output=True,text=True,check=True,timeout=240)
            probes[label]=json.loads(result.stdout.splitlines()[-1])
            print('Native isolated group verified: '+label,flush=True)
        value=dict(status='passed',role=a.role,prefix=str(prefix),base_prefix=sys.base_prefix,
            python=sys.executable,python_version=platform.python_version(),system=platform.system(),
            user_site_enabled=site.ENABLE_USER_SITE,distributions=distributions,distribution_locations=locations,
            isolated_native_groups=probes,threads=a.threads)
        with a.output.open('x') as stream:json.dump(value,stream,sort_keys=True,indent=2);stream.write('\n')
        print(json.dumps(dict(status='passed',role=a.role,prefix=str(prefix))))
        return
    origins={}
    for name in names:
        print('Native import begin: '+name, flush=True)
        module=importlib.import_module(name);path=Path(module.__file__).resolve()
        if not path.is_relative_to(prefix.resolve()):raise RuntimeError('Import outside owned prefix: '+str(path))
        origins[name]=str(path)
        print('Native import verified: '+name, flush=True)
    value=dict(status='passed',role=a.role,prefix=str(prefix),base_prefix=sys.base_prefix,
               python=sys.executable,python_version=platform.python_version(),system=platform.system(),
               user_site_enabled=site.ENABLE_USER_SITE,distributions=distributions,distribution_locations=locations,origins=origins)
    if a.role in ('binner','candidate'):
        import torch
        from threadpoolctl import threadpool_info
        torch.set_num_threads(a.threads);torch.set_num_interop_threads(1)
        if torch.version.cuda is not None:raise RuntimeError('CPU-only Torch required')
        pools=threadpool_info()
        if any(v['num_threads']>a.threads for v in pools):raise RuntimeError('Numerical CPU pool over budget')
        value.update(torch_threads=torch.get_num_threads(),torch_interop=torch.get_num_interop_threads(),torch_cuda=torch.version.cuda,pools=pools)
    with a.output.open('x') as stream:json.dump(value,stream,sort_keys=True,indent=2);stream.write('\n')
    print(json.dumps(value,sort_keys=True))


if __name__=='__main__':main()
