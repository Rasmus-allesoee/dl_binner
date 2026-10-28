#!/usr/bin/env python3
"""Actual cached-only tiny serial DAG, partial/full reuse and bounded collection.

DNA/features/embeddings/marker calls are synthetic engineering fixtures. The real
rebind, sparse readers, grouping, marker selection, exports, isolated dispatcher,
Snakemake and archive verifier run. No acquisition, mapper or cloud transport runs.
"""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).absolute().parents[1]
sys.path[:0]=[str(ROOT/'scripts'),str(ROOT/'src'),str(ROOT/'tests')]
from e024_coverage import binding,write
from e025_collect import pack
from test_e025_retrieval import retained


def tiny(root,workflow_python):
    """Verify accepted verify/group stages are not scheduled again on partial reuse."""
    root=Path(root).absolute();root.mkdir(parents=True,exist_ok=False)
    inputs=root/'inputs';inputs.mkdir();u,receipt=retained(inputs)
    p=json.loads((ROOT/'experiments/E025-joint-distance-retrieval/runtime-plan.json').read_text())
    p.update(work=str(root/'work'),python=sys.executable,workflow_python=str(Path(workflow_python).absolute()),
        worker=str(ROOT/'scripts/e025_control.py'),snakefile=str(ROOT/'experiments/E025-joint-distance-retrieval/Snakefile'),
        policy=str(ROOT/'experiments/E023-adaptive-density-bins/config.json'),reference=str(u['reference']),
        graph=str(u['graph']),marker_evidence=str(u['marker_evidence']),receipt=str(receipt),engineering=True)
    write(root/'plan.json',p)
    argv=[sys.executable,'-I','-B',str(ROOT/'scripts/e025_control.py'),'--plan',str(root/'plan.json'),'--engineering']
    env=dict(os.environ,NUMBA_NUM_THREADS='4',NUMBA_CACHE_DIR=str(root/'jit'))
    def call(label,extra):
        with (root/(label+'.log')).open('x') as f:
            value=subprocess.run(argv+extra,cwd=root,env=env,stdout=f,stderr=subprocess.STDOUT)
        write(root/(label+'.exit.json'),dict(exit_code=value.returncode,argv=argv+extra))
        if value.returncode:raise RuntimeError('Actual cached DAG failed: '+str(root/(label+'.log')))
    call('first-verify',['--stage','verify']);call('first-group',['--stage','group'])
    work=root/'work'
    before={str(q.relative_to(work)):binding(q) for name in ['verified','group'] for q in (work/name).rglob('*') if q.is_file()}
    call('partial-resume',['--workflow'])
    if any(binding(work/k)!=v for k,v in before.items()):raise ValueError('Partial resume repeated/changed accepted retrieval')
    text=(root/'partial-resume.log').read_text()
    if 'rule group:' in text or 'rule verify:' in text:raise ValueError('Accepted science scheduled again')
    call('completed-resume',['--workflow'])
    if 'Nothing to be done' not in (root/'completed-resume.log').read_text():raise ValueError('Completed resume not no-op')
    evidence=root/'evidence';evidence.mkdir()
    write(evidence/'external-data.json',dict(data_copied=False,archive=p['data_archive'],fixture=True,
        files=dict(rebound_features=binding(inputs/'rebound/features.npz'),receipt=binding(receipt))))
    returned=pack(work,evidence,root/'return')
    # Exercise the real new-output review admission/reader with separately
    # retained data; no origin truth or quality scoring is opened by contracts.
    from e025_review import contracts
    admit=root/'review-admission.json'
    write(admit,dict(provider_status='TERMINATED',archive_and_every_member_verified=True,
        cost_and_retention_admitted=True,workflow_completed=True,fixture=True))
    contracts(work,root/'return/inventory.json',admit,inputs/'rebound/features.npz',receipt)
    write(root/'completed.json',dict(status='PASS',actual_partial_reuse=True,actual_completed_noop=True,
        actual_export=True,actual_collection=returned,community_science=False,
        mocked='Synthetic DNA/vectors/marker calls; no cloud transport',retained_inputs={k:binding(v) for k,v in u.items()}))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--root',type=Path,required=True)
    p.add_argument('--workflow-python',required=True);a=p.parse_args();tiny(a.root,a.workflow_python)
