#!/usr/bin/env python3
"""Actual installed serial three-mode graph learning/construction/export contract.

Generated DNA/BAMs, synthetic frozen vectors and cached marker annotations only.
This exercises real readers, graph training, native graph libraries, fixed E032
construction, strict collections and verified no-op resume; no biological score.
"""
import argparse,json,os
from pathlib import Path
import subprocess,sys
ROOT=Path(__file__).absolute().parents[1];sys.path[:0]=[str(ROOT/'scripts'),str(ROOT/'tests/product')]
from e024_coverage import binding,write


def run(root,workflow_python):
    """Generate tiny accepted inputs once and execute actual isolated workers."""
    from e036_control import product_scope,UNITS,STAGES
    product_scope();from relational_fixture import fixture
    from test_multiscale_learning import measured
    from test_genomegraph_model import physical
    root=Path(root).absolute();root.mkdir(parents=True,exist_ok=False);f=fixture(root/'input');measured(root/'measured',f);links=physical(root/'physical',f)
    restored=root/'original';units={}
    quality=root/'quality.json';write(quality,dict(panel_size=4,calls={str(q):{'family-'+str(i%4):[1.]} for i,q in enumerate(f['data']['ids'][:32])}))
    for u in UNITS:
        at=restored/'work'/u;at.joinpath('embed').mkdir(parents=True);at.joinpath('graph/result').mkdir(parents=True)
        for source,target in [(f['embeddings'],at/'embed/embeddings.npz'),(f['embeddings'].with_suffix('.json'),at/'embed/embeddings.json'),(f['graph'],at/'graph/result/graph.npz'),(f['graph'].with_suffix('.json'),at/'graph/result/graph.json')]:os.link(source,target)
        units[u]=dict(features=str(f['features']),views=str(f['views']),fasta=str(f['fasta']),marker_evidence=str(quality),community='oral' if u.startswith('oral') else 'E009')
    p=dict(kind='E036 optional pooled graph',engineering=True,work=str(root/'work'),source_cache=str(restored),measurement_cache={c:str(root/'measured') for c in ['E009','oral']},physical={c:str(links) for c in ['E009','oral']},units=units,
        python=sys.executable,workflow_python=str(Path(workflow_python).absolute()),worker=str(ROOT/'scripts/e036_control.py'),snakefile=str(ROOT/'experiments/E036-optional-pooled-links/Snakefile'),limits={},baseline_cache=str(root/'baseline'),optional_policy=json.loads((ROOT/'experiments/E036-optional-pooled-links/runtime-plan.json').read_text())['optional_policy'])
    from e036_test_fixture import empty_physical,baseline
    p['physical']['oral']=str(empty_physical(root/'empty-physical',f))
    baseline(root/'baseline',f,quality,restored)
    write(root/'plan.json',p);argv=[sys.executable,'-I','-B',str(ROOT/'scripts/e036_control.py'),'--plan',str(root/'plan.json'),'--engineering','--workflow']
    def call(name):
        with (root/(name+'.log')).open('x') as out:r=subprocess.run(argv,stdout=out,stderr=subprocess.STDOUT)
        write(root/(name+'.exit.json'),dict(argv=argv,exit_code=r.returncode))
        if r.returncode:raise RuntimeError('Actual E036 tiny DAG failed; inspect '+str(root/(name+'.log')))
    call('first');finish(root,argv,f['features'])


def finish(root,argv,features,first_label='first'):
    """Verify/collect one closed real DAG, also after recorded operational repair."""
    from e036_control import UNITS
    def call(name):
        with (root/(name+'.log')).open('x') as out:r=subprocess.run(argv,stdout=out,stderr=subprocess.STDOUT)
        write(root/(name+'.exit.json'),dict(argv=argv,exit_code=r.returncode))
        if r.returncode:raise RuntimeError('Actual E036 tiny DAG failed; inspect '+str(root/(name+'.log')))
    events=[];active=None
    for line in (root/(first_label+'.log')).read_text().splitlines():
        if line.startswith('localrule ') and not line.startswith('localrule all:'):
            if active is not None:raise ValueError('Actual E036 scientific stages overlapped')
            active=line.split()[1].rstrip(':');events.append(active)
        if 'Finished jobid:' in line:active=None
    if len(events)!=31 or events[0]!='barrier':raise ValueError('Actual serial E036 job population differs')
    closed={str(p.relative_to(root/'work')):binding(p) for p in (root/'work').rglob('*') if p.is_file() and '.snakemake' not in p.parts}
    call('resume')
    if any(binding(root/'work'/n)!=b for n,b in closed.items()):raise ValueError('Passed E036 science repeated/changed during no-op resume')
    if 'Nothing to be done' not in (root/'resume.log').read_text():raise ValueError('Native workflow did not verify no-op')
    from e034_collect import pack
    evidence=root/'evidence';evidence.mkdir();write(evidence/'fixture.json',dict(engineering=True,actual='BAM/collator/window/graph/train/reload/refinement/export',synthetic='DNA/frozen vectors/marker calls; no GLM inference or biological truth'))
    archives={u:pack(root/'work'/u,evidence,root/('return-'+u))['archive'] for u in UNITS}
    from e033_review import layout
    from e036_review import contract
    contracts={}
    for u in UNITS:
        collection=root/('return-'+u)
        write(collection/'admission.json',dict(provider_status='TERMINATED',archive_and_every_member_verified=True,cost_and_retention_admitted=True,workflow_completed=True,exact_source_schedule_axes_verified=True,fixture_only=True,live_provider_or_billing_observed=False))
        staged=root/('review-stage-'+u);(staged/'work').mkdir(parents=True)
        for file in (root/'work'/u).rglob('*'):
            if file.is_file():
                target=staged/'work'/file.relative_to(root/'work'/u);target.parent.mkdir(parents=True,exist_ok=True);os.link(file,target)
        base,view=layout(collection,staged,u,root/('review-layout-'+u))
        contracts[u]=contract(base,view,u,'student',features,'learning',engineering=True)[-1]
    write(root/'completed.json',dict(status='PASS',serial_scientific_seals=31,new_graph_fits=2,exact_no_link_fallbacks=1,stages=events,verified_resume_noop=True,full_DNA_audits={u:json.loads((root/'work'/u/'audit/proof.json').read_text()) for u in UNITS},archives=archives,actual_review_contracts=contracts,community_science=False))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--root',type=Path,required=True);p.add_argument('--workflow-python',type=Path,required=True);a=p.parse_args();run(a.root,a.workflow_python)
