#!/usr/bin/env python3
"""Build a candidate from a fresh minimal source snapshot, not a stale build tree.

Requires a preinstalled independent builder Python. Copies package/reproducibility
inputs only, records every byte, builds wheel/sdist in separate backend processes,
rebuilds the sdist, then inspects both. No dependency installation or publication.
Logs/failed snapshots are retained; timeout covers preparation through inspection.
"""
import argparse
import importlib.util
import json
from pathlib import Path
import shutil
import sys
import time


def main():
    """Create one exclusive bounded build record, preserving its lexical interpreter."""
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--python',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--threads',type=int,choices=range(1,5),default=2)
    parser.add_argument('--timeout',type=float,default=300)
    args=parser.parse_args()
    root=Path(__file__).absolute().parents[1]
    out=args.output.absolute();out.mkdir(parents=True,exist_ok=False)
    spec=importlib.util.spec_from_file_location('build_supervision',root/'src/dl_binner/supervision.py')
    supervision=importlib.util.module_from_spec(spec);spec.loader.exec_module(supervision)
    contract_spec=importlib.util.spec_from_file_location('build_contracts',root/'src/dl_binner/contracts.py')
    contracts=importlib.util.module_from_spec(contract_spec);contract_spec.loader.exec_module(contracts)
    started=time.monotonic()
    source=out/'source';source.mkdir()
    for name in ('src/dl_binner','tests/product','requirements'):
        shutil.copytree(root/name,source/name,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
    for name in ('README.md','pyproject.toml','MANIFEST.in','docs/PROTOTYPE.md','docs/INSTALLATION.md',
                 'scripts/test_product.py','scripts/check_runtime.py','scripts/check_distribution.py','scripts/build_candidate.py'):
        target=source/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(root/name,target)
    contracts.write_json(out/'source.json',{str(p.relative_to(source)):contracts.file_record(p) for p in sorted(source.rglob('*')) if p.is_file()})
    python=str(args.python.absolute())
    dist=out/'dist';dist.mkdir();rebuilt=out/'rebuilt';rebuilt.mkdir()
    env=supervision.isolated_env(args.threads)
    import os
    previous=Path.cwd();os.chdir(source)
    try:
        for label,command in [('sdist',[python,'-I','-B','-c','from setuptools.build_meta import build_sdist;import sys;build_sdist(sys.argv[1])',str(dist)]),
                              ('wheel',[python,'-I','-B','-c','from setuptools.build_meta import build_wheel;import sys;build_wheel(sys.argv[1])',str(dist)])]:
            supervision.supervise(command,out/(label+'.log'),args.timeout-(time.monotonic()-started),2_000_000_000,env)
        archive=next(dist.glob('*.tar.gz'))
        supervision.supervise([python,'-I','-B','-m','pip','--isolated','wheel','--no-deps','--no-build-isolation',
            '--no-cache-dir','--wheel-dir',str(rebuilt),str(archive)],out/'rebuild.log',
            args.timeout-(time.monotonic()-started),2_000_000_000,env)
        supervision.supervise([python,'-I','-B',str(root/'scripts/check_distribution.py'),
            '--wheel',str(next(dist.glob('*.whl'))),'--sdist',str(archive),
            '--rebuilt-wheel',str(next(rebuilt.glob('*.whl'))),'--output',str(out/'inspection.json')],
            out/'inspection.log',args.timeout-(time.monotonic()-started),2_000_000_000,env)
        contracts.write_json(out/'build.json',dict(status='passed',wall_seconds=time.monotonic()-started,
            threads=args.threads,python=python,scope='Fresh snapshot wheel/sdist/rebuilt wheel, no installs or science'))
    finally:os.chdir(previous)


if __name__=='__main__':main()
