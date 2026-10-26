#!/usr/bin/env python3
"""Run the exact serial two-unit grouping/export DAG on new tiny real fixtures.

Only DNA/features and declared synthetic engineering vectors/annotations are
created. No neural fit, detector, community grouping or score is performed.
Run from outside the checkout with isolated Python to exercise actual adapters.
"""
import argparse
import json
from pathlib import Path
import subprocess
import sys
import time

ROOT=Path(__file__).absolute().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'scripts'),str(ROOT/'tests')]
from test_e023_density import fixture
from e023_control import UNITS,verify_reuse
from e014_collect import binding
from e023_collect import pack,verify


def main():
    """Keep inputs, real helper logs, resource tables and all-member return evidence."""
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--root',type=Path,required=True)
    p.add_argument('--workflow-python',type=Path,required=True);a=p.parse_args()
    root=a.root.absolute();root.mkdir(exist_ok=False);units={};files={}
    for unit,depth in zip(UNITS,[True,False]):
        r=root/unit;r.mkdir();f,e,g,m,fa,data=fixture(r,depth)
        units[unit]=dict(features=str(f),embeddings=str(e),graph=str(g),marker_evidence=str(m),fasta=str(fa),baseline_partition=str(g.parent/'partition.json'))
        for item in units[unit].values():files[item]=binding(item)
    reuse=root/'reuse.json';reuse.write_text(json.dumps(dict(kind='E023 restore-only dual-anchor reuse',units=units,files=files,numerical_python=sys.executable)))
    work=root/'work';work.mkdir()
    plan=dict(kind='E023 fixed-learning density hierarchy',units=units,threads=4,python=sys.executable,
              workflow_python=str(a.workflow_python.absolute()),work=str(work),worker=str(ROOT/'scripts/e023_control.py'),
              snakefile=str(ROOT/'experiments/E023-adaptive-density-bins/Snakefile'),
              config=str(ROOT/'experiments/E023-adaptive-density-bins/config.json'),reuse_lock=str(reuse))
    path=root/'plan.json';path.write_text(json.dumps(plan,indent=2))
    command=[sys.executable,'-I','-B',str(ROOT/'scripts/e023_control.py'),'--plan',str(path),'--workflow','--engineering']
    subprocess.run(command,check=True)
    # Explicit verified Snakemake resume must not touch any successful science output.
    before={str(p):binding(p)for p in work.glob('units/*/group/*')if p.is_file()}
    subprocess.run(command,check=True)
    if before!={str(p):binding(p)for p in work.glob('units/*/group/*')if p.is_file()}:raise ValueError('Resume repeated accepted tiny science')
    verify_reuse(reuse,root/'reuse-after.json')
    evidence=root/'evidence';evidence.mkdir();(evidence/'actual.json').write_text(json.dumps(dict(actual='two-mode sparse/native index/forest/selection/FASTA export/exact helper argv/Snakemake/collector',synthetic='tiny vectors and marker annotations; no learned or biological result')))
    returned=pack(work,evidence,root/'return');verify(root/'return/e023-evidence.tar.gz',returned['archive'])
    print('E023_TINY_SERIAL_DAG_REUSE_RETURN_PASS',json.dumps(returned),flush=True)


if __name__=='__main__':main()
