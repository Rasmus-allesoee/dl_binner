#!/usr/bin/env python3
"""Exercise the installed cached DAG, exact resume and bounded collection path."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).absolute().parents[1]
sys.path[:0]=[str(ROOT/'scripts'),str(ROOT/'tests/product')]
from e024_coverage import binding,write


def run(root,workflow_python):
    """Use real tiny DNA/readers with synthetic native vectors and physical calls."""
    from e030_control import product_scope,UNITS,COMPONENTS
    product_scope()
    from discovery_fixture import fixture
    from dl_binner.discovery import exact
    from e030_collect import CONTROLS,pack,collect_controls,verify
    root=Path(root).absolute();root.mkdir(parents=True,exist_ok=False);f=fixture(root/'input',64)
    source=root/'accepted-learning';accepted=root/'accepted-results'
    cache=root/'fixture-cache';original=root/'fixture-result'
    exact.prepare(f['features'],f['embeddings'],f['graph'],cache)
    exact.run(f['features'],f['embeddings'],f['graph'],f['evidence'],cache,original)
    for u,r in COMPONENTS:
        for label,path in [(r+'-embed/embeddings.npz',f['embeddings']),(r+'-embed/embeddings.json',f['embeddings'].with_suffix('.json')),(r+'-graph/graph.npz',f['graph']),(r+'-graph/graph.json',f['graph'].with_suffix('.json'))]:
            dst=source/'units'/u/label;dst.parent.mkdir(parents=True,exist_ok=True);os.link(path,dst)
        for path in original.rglob('*'):
            if path.is_file():
                dst=accepted/'groups'/u/r/'result'/path.relative_to(original);dst.parent.mkdir(parents=True,exist_ok=True);os.link(path,dst)
    p=json.loads((ROOT/'experiments/E030-supported-biological-bins/runtime-plan.json').read_text())
    p.update(work=str(root/'work'),source_work=str(source),accepted_work=str(accepted),python=sys.executable,
        workflow_python=str(Path(workflow_python).absolute()),worker=str(ROOT/'scripts/e030_control.py'),
        snakefile=str(ROOT/'experiments/E030-supported-biological-bins/Snakefile'),engineering=True,
        units={u:dict(features=str(f['features']),fasta=str(f['fasta']),marker_evidence=str(f['evidence']),frozen=None) for u in UNITS})
    write(root/'plan.json',p)
    argv=[sys.executable,'-I','-B',str(ROOT/'scripts/e030_control.py'),'--plan',str(root/'plan.json'),'--engineering','--workflow']
    def call(name):
        with (root/(name+'.log')).open('x') as log:v=subprocess.run(argv,stdout=log,stderr=subprocess.STDOUT)
        write(root/(name+'.exit.json'),dict(argv=argv,exit_code=v.returncode))
        if v.returncode:raise RuntimeError('Actual cached tiny DAG failed: '+str(root/(name+'.log')))
    call('first');events=[];active=None
    for line in (root/'first.log').read_text().splitlines():
        if line.startswith('localrule ') and not line.startswith('localrule all:'):
            if active is not None:raise ValueError('Independent ready rules overlapped')
            active=line.split()[1].rstrip(':');events.append(active)
        if 'Finished jobid:' in line:active=None
    if len(events)!=13 or events[0]!='barrier':raise ValueError('Actual barrier/schedule differs: '+repr(events))
    before={str(p):binding(p) for p in (root/'work').rglob('*') if p.is_file() and '.snakemake' not in p.parts}
    call('verified-resume')
    if 'Nothing to be done' not in (root/'verified-resume.log').read_text() or any(binding(p)!=b for p,b in before.items()):raise ValueError('Verified resume replayed/changed accepted work')
    phase=root/'phase';phase.mkdir();evidence=root/'evidence';evidence.mkdir()
    for name in CONTROLS+['config.json','science-plan.json','started.json','release.json','science-result.json','science-disk.jsonl','external-data.json']:
        d=phase/name;d.parent.mkdir(parents=True,exist_ok=True);write(d,dict(data_copied=False,fixture=True) if name=='external-data.json' else dict(fixture=True))
    collect_controls(phase,evidence/'controls');write(evidence/'external-data.json',dict(data_copied=False))
    result=pack(root/'work',evidence,root/'return');verify(root/'return/e030-evidence.tar.gz',result['archive'])
    write(root/'completed.json',dict(status='PASS',ready_rule_events=events,no_overlap=True,verified_resume_noop=True,
        real=['installed sparse/profile/whole-child/update readers','complete DNA export','serial native workflow adapter','member/alias collector'],
        synthetic=['fixture vectors','hand authored physical calls'],actual_archive=result,community_science=False))


if __name__=='__main__':
    a=argparse.ArgumentParser(description=__doc__);a.add_argument('--root',type=Path,required=True)
    a.add_argument('--workflow-python',type=Path,required=True);v=a.parse_args();run(v.root,v.workflow_python)
