#!/usr/bin/env python3
"""Exercise real restored forest/marker/selection/export readers on tiny DNA.

Creates only a 64-contig engineering fixture. Its vectors/calls are synthetic;
no marker detector, GLM, training, community data or truth evaluator is invoked.
The original local/native fixture machinery supplies genuine serialized caches.
"""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).absolute().parents[1]
sys.path[:0]=[str(ROOT/'scripts'),str(ROOT/'tests/product')]
from e024_coverage import binding,write


def run(root,workflow_python=None):
    """Build tiny cached candidates once, then test actual new readers and reload."""
    from discovery_fixture import fixture
    from dl_binner.discovery import exact
    from dl_binner.density import grouping as density
    from dl_binner.construction import grouping as old
    from dl_binner.selection import grouping as new
    import dl_binner
    if not Path(dl_binner.__file__).is_relative_to(Path(sys.prefix)):
        raise ValueError('Actual owned installed wheel required')
    root=Path(root).absolute();root.mkdir(parents=True,exist_ok=False)
    f=fixture(root/'input',64);work=root/'work';unit=work/'tiny'
    cache=root/'tiny-cache';exact.prepare(f['features'],f['embeddings'],f['graph'],cache)
    exact.run(f['features'],f['embeddings'],f['graph'],f['evidence'],cache,unit/'forest/result')
    old.run(f['features'],f['embeddings'],f['graph'],f['evidence'],unit/'forest/result',unit/'construct/result')
    density.run(f['features'],f['embeddings'],f['graph'],f['evidence'],unit/'e023/science/result',
        density.policy(ROOT/'experiments/E023-adaptive-density-bins/config.json'),4)
    write(work/'restore-admission.json',dict(status='PASS',every_member_verified=True,
        omitted_work_members=0,engineering=True,cloud_or_community_admission=False))
    before={str(p):binding(p) for p in root.rglob('*') if p.is_file()}
    args=(f['features'],f['embeddings'],f['graph'],f['evidence'],unit)
    result=new.run(*args,f['fasta'],root/'new')
    audit=new.audit(*args,root/'new')
    if any(binding(p)!=v for p,v in before.items()):raise ValueError('Tiny restore mutated retained input')
    workflow_proof=None
    if workflow_python is not None:
        from e032_control import UNITS
        restored=root/'dag-restored';(restored/'work').mkdir(parents=True)
        for u in UNITS:
            for p in unit.rglob('*'):
                if p.is_file():
                    target=restored/'work'/u/p.relative_to(unit);target.parent.mkdir(parents=True,exist_ok=True)
                    os.link(p,target)
            for name,source in [('embed/embeddings.npz',f['embeddings']),('embed/embeddings.json',f['embeddings'].with_suffix('.json')),
                                ('graph/result/graph.npz',f['graph']),('graph/result/graph.json',f['graph'].with_suffix('.json'))]:
                target=restored/'work'/u/name;target.parent.mkdir(parents=True,exist_ok=True)
                os.link(source,target)
        write(restored/'work/restore-admission.json',json.loads((work/'restore-admission.json').read_text()))
        plan=json.loads((ROOT/'experiments/E032-biological-candidate-selection/runtime-plan.json').read_text())
        plan.update(engineering=True,work=str(root/'dag-work'),restored=str(restored),python=sys.executable,
            workflow_python=str(Path(workflow_python).absolute()),worker=str(ROOT/'scripts/e032_control.py'),
            snakefile=str(ROOT/'experiments/E032-biological-candidate-selection/Snakefile'),
            units={u:dict(features=str(f['features']),fasta=str(f['fasta']),marker_evidence=str(f['evidence'])) for u in UNITS})
        write(root/'dag-plan.json',plan)
        argv=[sys.executable,'-I','-B',str(ROOT/'scripts/e032_control.py'),'--plan',str(root/'dag-plan.json'),'--engineering','--workflow']
        def call(label):
            with(root/(label+'.log')).open('x') as f:
                result=subprocess.run(argv,stdout=f,stderr=subprocess.STDOUT)
            if result.returncode:raise RuntimeError('Actual tiny serial DAG failed: '+str(root/(label+'.log')))
        call('dag-first');active=None;events=[]
        for line in (root/'dag-first.log').read_text().splitlines():
            if line.startswith('localrule ') and not line.startswith('localrule all:'):
                if active is not None:raise ValueError('Actual tiny DAG overlapped independent stages')
                active=line.split()[1].rstrip(':');events.append(active)
            if 'Finished jobid:' in line:active=None
        if len(events)!=7:raise ValueError('All seven serial stages must execute')
        closed={str(p):binding(p) for p in (root/'dag-work').rglob('*') if p.is_file() and '.snakemake' not in p.parts}
        call('dag-resume')
        if 'Nothing to be done' not in (root/'dag-resume.log').read_text() or any(binding(p)!=v for p,v in closed.items()):
            raise ValueError('Verified resume repeated/changed closed science')
        workflow_proof=dict(status='PASS',actual_events=events,no_overlap=True,resume_noop=True)
        from e032_collect import pack
        from e032_review import contract
        evidence=root/'tiny-closed-evidence';evidence.mkdir();write(evidence/'fixture.json',dict(engineering=True))
        packed=pack(root/'dag-work',evidence,root/'tiny-return')
        base=root/'review-contract';base.mkdir()
        write(base/'inventory.json',json.loads((root/'tiny-return/inventory.json').read_text()))
        write(base/'admission.json',dict(provider_status='TERMINATED',archive_and_every_member_verified=True,
            cost_and_retention_admitted=True,workflow_completed=True,exact_source_schedule_axes_verified=True,
            fixture_only=True,live_provider_or_billing_observed=False))
        staged=root/'review-stage'
        for name in closed:
            path=Path(name);target=staged/'work'/path.relative_to(root/'dag-work')
            target.parent.mkdir(parents=True,exist_ok=True);os.link(path,target)
        review_contracts={}
        for u in UNITS:
            review_contracts[u]=contract(base,staged,u,'student',f['features'],'learning',engineering=True)[-1]
        workflow_proof.update(exact_byte_collector=packed,actual_review_contracts=review_contracts,
            provider_admission_fixture_only=True,truth_scored=False)
    write(root/'completed.json',dict(status='PASS',new_result=result,audit=audit,
        actual=['NPZ sparse and forest readers','opaque ID remapping','cached physical marker weights',
                'whole/child/residual decisions','pre/post complete DNA exports','strict decision reload'],
        synthetic=['64-contig DNA and model vectors','physical marker calls'],
        actual_serial_workflow=workflow_proof,training_or_marker_detection=False,community_or_cloud_work=False))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--root',type=Path,required=True)
    p.add_argument('--workflow-python',type=Path)
    a=p.parse_args();run(a.root,a.workflow_python)
