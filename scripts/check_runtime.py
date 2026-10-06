#!/usr/bin/env python3
"""Validate a fresh standalone runtime's complete inventory and owned imports.

Runs inside its lexical venv Python with -I -B. Accepts only the version-pinned
closure in requirements, plus the installed dev2 binner for that role. No
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
import sys


def normalize(name):
    """Canonicalize distribution names without accepting duplicate identities."""
    return re.sub(r'[-_.]+','-',name.lower())


def main():
    """Retain a complete standalone-prefix inventory after native imports pass."""
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--role',choices=('build','binner','workflow'),required=True)
    p.add_argument('--requirements',type=Path,required=True)
    p.add_argument('--threads',type=int,choices=range(1,5),default=4)
    p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();prefix=Path(sys.prefix).absolute()
    if sys.prefix==sys.base_prefix or site.ENABLE_USER_SITE:raise RuntimeError('A separate isolated venv is required')
    expected={}
    for line in a.requirements.read_text().splitlines():
        line=line.strip()
        if not line or line.startswith('#'):continue
        spec,separator,marker=line.partition(';')
        if separator:
            if marker.strip() not in ('platform_system == "Linux"','platform_system == "Darwin"'):raise ValueError('Unsupported requirement marker')
            if marker.split('"')[1]!=platform.system():continue
        name,version=spec.strip().split('==');expected[normalize(name)]=version
    if a.role=='binner':expected['dl-binner']='0.1.0.dev2'
    distributions={};locations={}
    for d in metadata.distributions():
        name=normalize(d.metadata['Name'])
        if name in distributions:raise RuntimeError('Duplicate distribution: '+name)
        location=Path(d._path).resolve()
        if not location.is_relative_to(prefix.resolve()):raise RuntimeError('Distribution outside prefix: '+str(location))
        distributions[name]=d.version;locations[name]=str(location)
    if distributions!=expected:raise RuntimeError('Complete runtime inventory differs: '+str({k:(expected.get(k),distributions.get(k)) for k in expected.keys()|distributions.keys() if expected.get(k)!=distributions.get(k)}))
    names={'build':['setuptools','wheel'], 'binner':['dl_binner','numpy','torch','networkx','threadpoolctl'], 'workflow':['snakemake']}[a.role]
    origins={}
    for name in names:
        module=importlib.import_module(name);path=Path(module.__file__).resolve()
        if not path.is_relative_to(prefix.resolve()):raise RuntimeError('Import outside owned prefix: '+str(path))
        origins[name]=str(path)
    value=dict(status='passed',role=a.role,prefix=str(prefix),base_prefix=sys.base_prefix,
               python=sys.executable,python_version=platform.python_version(),system=platform.system(),
               user_site_enabled=site.ENABLE_USER_SITE,distributions=distributions,distribution_locations=locations,origins=origins)
    if a.role=='binner':
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
