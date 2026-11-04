#!/usr/bin/env python3
"""Installed real tiny three-mode serial workflow, resume and collector contract.

Only generated DNA/reads and explicit cached synthetic markers/GLM numeric vectors
are used. Native BAM/NumPy/PyTorch/graph/HMM readers and exports are real. Provider,
billing and scientific truth are not mocked into an execution-admission claim.
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


def run(root,workflow_python):
    """Generate once, execute the actual isolated installed workers, verify no-op."""
    from e033_control import product_scope,UNITS
    product_scope()
    from relational_fixture import fixture
    from test_multiscale_learning import measured,source
    from dl_binner.multiscale.model import read_original
    root=Path(root).absolute();root.mkdir(parents=True,exist_ok=False)
    f=fixture(root/'input');features=measured(root/'measured',f)
    units={};previous={}
    for glm in [False,True]:
        checkpoint,frozen=source(root/('source-glm' if glm else 'source-noGLM'),f,glm)
        saved,_=read_original(checkpoint,f['features'],f['views'],f['tokens'],frozen)
        q=json.loads((checkpoint.parents[1]/'proposals/quality.json').read_text())
        quality=root/('physical-glm.json' if glm else 'physical-noGLM.json')
        write(quality,dict(panel_size=4,calls={i:{fam:[v['reliability']] for fam,v in fs.items()} for i,fs in q['calls'].items()}))
        e=dict(features=str(f['features']),views=str(f['views']),fasta=str(f['fasta']),tokens=str(f['tokens']),
            frozen=str(frozen) if frozen else None,original=str(checkpoint),marker_cache=str(f['markers']),hmm=str(f['hmm']),
            marker_evidence=str(quality),community='E009')
        if glm:units['E009-GLM']=e
        else:units['E009-noGLM']=e;units['oral-noGLM']=dict(e,community='oral')
    plan=dict(kind='E033 common multiscale BAM information',engineering=True,work=str(root/'work'),
        units={u:units[u] for u in UNITS},measurements={c:dict(bank=str(root/'measured'),new_features=str(features)) for c in ['E009','oral']},
        python=sys.executable,workflow_python=str(Path(workflow_python).absolute()),worker=str(ROOT/'scripts/e033_control.py'),
        snakefile=str(ROOT/'experiments/E033-multiscale-bam/Snakefile'),limits={})
    write(root/'plan.json',plan)
    argv=[sys.executable,'-I','-B',str(ROOT/'scripts/e033_control.py'),'--plan',str(root/'plan.json'),'--engineering','--workflow']
    def call(name):
        with(root/(name+'.log')).open('x') as f:r=subprocess.run(argv,stdout=f,stderr=subprocess.STDOUT)
        write(root/(name+'.exit.json'),dict(argv=argv,exit_code=r.returncode))
        if r.returncode:raise RuntimeError('Actual E033 DAG failed; retained '+str(root/(name+'.log')))
    call('first');active=None;events=[]
    for line in (root/'first.log').read_text().splitlines():
        if line.startswith('localrule ') and not line.startswith('localrule all:'):
            if active is not None:raise ValueError('Independent science stages overlapped')
            active=line.split()[1].rstrip(':');events.append(active)
        if 'Finished jobid:' in line:active=None
    if len(events)!=40 or events[0]!='barrier':raise ValueError('Incomplete serial three-mode DAG')
    closed={str(p):binding(p) for p in (root/'work').rglob('*') if p.is_file() and '.snakemake' not in p.parts}
    call('resume')
    if 'Nothing to be done' not in (root/'resume.log').read_text() or any(binding(p)!=b for p,b in closed.items()):
        raise ValueError('Sealed resume replayed/changed completed work')
    from e033_collect import pack
    evidence=root/'evidence';evidence.mkdir();write(evidence/'tiny.json',dict(engineering=True,truth_accessed=False))
    archives={}
    for u in UNITS:archives[u]=pack(root/'work'/u,evidence,root/('return-'+u))
    from e033_review import layout,contract
    readers={}
    for u in UNITS:
        collection=root/('return-'+u)
        write(collection/'admission.json',dict(provider_status='TERMINATED',archive_and_every_member_verified=True,
            cost_and_retention_admitted=True,workflow_completed=True,exact_source_schedule_axes_verified=True,
            fixture_only=True,live_provider_or_billing_observed=False))
        staged=root/('review-stage-'+u);(staged/'work').mkdir(parents=True)
        for p in (root/'work'/u).rglob('*'):
            if p.is_file():
                target=staged/'work'/p.relative_to(root/'work'/u);target.parent.mkdir(parents=True,exist_ok=True);os.link(p,target)
        base,view=layout(collection,staged,u,root/('review-layout-'+u))
        readers[u]=contract(base,view,u,'student',features,'learning',engineering=True)[-1]
    # Whole measured cache collection includes generated tiny BAMs here only.
    archives['measurement']=pack(root/'measured',evidence,root/'return-measurements')
    write(root/'completed.json',dict(status='PASS',stages=events,verified_resume_noop=True,no_overlap=True,
        archives=archives,actual_review_contracts=readers,truth_scored=False,actual=['sorted BAM interval measurement','retained DNA views/context','20-epoch teacher and 20-epoch student in all three modes',
        'full state/Adam/EMA restoration','fresh own-teacher graph/pairs','exact same-runtime native reload',
        'unchanged E023/E030 forests and E032 selection/audit','pre/post complete DNA exports','strict complete bounded member/alias verification'],
        synthetic=[str(len(f['data']['ids']))+' contigs / '+str(int(f['data']['lengths'].sum()))+' bp generated DNA','generated reads','hand-authored cached marker domains','GLM inference only'],
        community_or_cloud_work=False,native_Linux_admission=False))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--root',required=True,type=Path);p.add_argument('--workflow-python',required=True,type=Path)
    a=p.parse_args();run(a.root,a.workflow_python)
