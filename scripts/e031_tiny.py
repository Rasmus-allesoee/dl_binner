#!/usr/bin/env python3
"""Exercise actual E031 bridge/learning DAGs, verified resume and bounded return.

Generated tiny DNA and explicit synthetic marker/GLM evidence only. No retained
community file or cloud operation is reachable. Isolated graph workers preserve
the project's numerical-library separation.
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


def run(root,workflow_python,comparison):
    """Build own real inputs, run the prepared serial worker, then resume without work."""
    from e031_control import product_scope,UNITS
    product_scope()
    root=Path(root).absolute();root.mkdir(parents=True,exist_ok=False)
    if comparison=='bridge':
        from discovery_fixture import fixture
        from dl_binner.density import grouping
        from dl_binner.bootstrap.bridge import MEMBERS
        f=fixture(root/'inputs',64)
        cfg=grouping.policy(ROOT/'experiments/E023-adaptive-density-bins/config.json')
        grouping.run(f['features'],f['embeddings'],f['graph'],f['evidence'],root/'accepted',cfg)
        expected={n:binding(root/'accepted'/n) for n in MEMBERS}
        units={u:dict(features=str(f['features']),fasta=str(f['fasta']),marker_evidence=str(f['evidence']),
            **{r:dict(embeddings=str(f['embeddings']),graph=str(f['graph']),
                      accepted=str(root/'accepted') if (u,r)==('E009-GLM','student') else None,
                      members=expected if (u,r)==('E009-GLM','student') else None) for r in ['teacher','student']}) for u in UNITS}
    else:
        from relational_fixture import fixture,NumericExtractor
        from dl_binner.unified.training import bootstrap,reload_bootstrap,configuration
        from dl_binner.hybrid.bank import prepare as frozen_bank,model_pin
        from dl_binner.multiview.downstream import group
        from dl_binner.relational.pairs import prepare
        f=fixture(root/'inputs');units={}
        for glm in [False,True]:
            prefix=root/('glm' if glm else 'no-glm');prefix.mkdir();frozen=None
            if glm:
                frozen=prefix/'frozen';frozen_bank(f['fasta'],f['features'],f['views'],frozen,NumericExtractor(),model_pin())
            cfg=configuration(glm);cfg.update(min_bin_bp=1,min_bin_contigs=1)
            bootstrap(f['features'],f['views'],f['tokens'],frozen,prefix/'bootstrap',cfg)
            reload_bootstrap(f['features'],f['views'],f['tokens'],frozen,prefix/'bootstrap/checkpoint.pt',prefix/'teacher.npz')
            group(prefix/'teacher.npz',f['features'],prefix/'graph',f['cfg'],4)
            prepare(f['features'],prefix/'teacher.npz',prefix/'graph/graph.npz',f['markers'],f['hmm'],prefix/'pairs')
            q=json.loads((prefix/'pairs/quality.json').read_text())
            physical=dict(panel_size=4,calls={i:{fam:[v['reliability']] for fam,v in fs.items()} for i,fs in q['calls'].items()})
            write(prefix/'physical.json',physical)
            entry=dict(features=str(f['features']),fasta=str(f['fasta']),marker_evidence=str(prefix/'physical.json'),
                views=str(f['views']),tokens=str(f['tokens']),frozen=str(frozen) if frozen else None,
                bootstrap=str(prefix/'bootstrap/checkpoint.pt'),source_pairs=str(prefix/'pairs'),
                embeddings=str(prefix/'teacher.npz'),graph=str(prefix/'graph/graph.npz'))
            if glm:units['E009-GLM']=entry
            else:
                units['E009-noGLM']=entry;units['oral-noGLM']=dict(entry)
        units={u:units[u] for u in UNITS}
    p=json.loads((ROOT/'experiments/E031-bootstrap-preserving-learning'/(comparison+'-plan.json')).read_text())
    p.update(work=str(root/'work'),units=units,python=sys.executable,workflow_python=str(Path(workflow_python).absolute()),
             worker=str(ROOT/'scripts/e031_control.py'),snakefile=str(ROOT/'experiments/E031-bootstrap-preserving-learning'/(comparison+'.smk')),engineering=True)
    write(root/'plan.json',p)
    argv=[sys.executable,'-I','-B',str(ROOT/'scripts/e031_control.py'),'--plan',str(root/'plan.json'),'--engineering','--workflow']
    def call(label):
        with (root/(label+'.log')).open('x') as log:result=subprocess.run(argv,stdout=log,stderr=subprocess.STDOUT)
        write(root/(label+'.exit.json'),dict(argv=argv,exit_code=result.returncode))
        if result.returncode:raise RuntimeError('Actual E031 DAG failed: '+str(root/(label+'.log')))
    call('first');active=None;events=[]
    for line in (root/'first.log').read_text().splitlines():
        if line.startswith('localrule ') and not line.startswith('localrule all:'):
            if active is not None:raise ValueError('Independent ready stages overlapped')
            active=line.split()[1].rstrip(':');events.append(active)
        if 'Finished jobid:' in line:active=None
    expected_stages=10 if comparison=='bridge' else 28
    if len(events)!=expected_stages or events[0]!='barrier':raise ValueError('Serial E031 scheduling contract differs')
    before={str(p):binding(p) for p in (root/'work').rglob('*') if p.is_file() and '.snakemake' not in p.parts}
    # An operational clock change in the engineering plan must not change the
    # scientific-stage identity or rerun a completed fit. Native revisions still
    # require a fresh complete source/runtime/credit/STOP admission.
    p['limits']['seconds']+=1
    (root/'plan.json').write_text(json.dumps(p,indent=2)+'\n')
    call('verified-resume')
    if 'Nothing to be done' not in (root/'verified-resume.log').read_text() or any(binding(p)!=b for p,b in before.items()):
        raise ValueError('Verified E031 resume replayed or changed closed science')
    from e031_collect import collect_controls,CONTROLS,pack,verify
    phase=root/'phase';phase.mkdir();evidence=root/'evidence';evidence.mkdir()
    for name in CONTROLS+['config.json','science-plan.json','started.json','release.json','science-result.json','science-disk.jsonl','external-data.json']:
        path=phase/name;path.parent.mkdir(parents=True,exist_ok=True)
        write(path,dict(data_copied=False,fixture=True) if name=='external-data.json' else dict(fixture=True))
    collect_controls(phase,evidence/'controls');write(evidence/'external-data.json',dict(data_copied=False))
    packed=pack(root/'work',evidence,root/'return');verify(root/'return/e031-evidence.tar.gz',packed['archive'])
    # Test the actual post-shutdown reader with explicitly simulated external
    # admission, without labels, evaluator calls or community-size data.
    import shutil
    from e031_review import contract
    review_base=root/'review-contract';review_base.mkdir()
    shutil.copyfile(root/'return/inventory.json',review_base/'inventory.json')
    write(review_base/'admission.json',dict(provider_status='TERMINATED',archive_and_every_member_verified=True,
        cost_and_retention_admitted=True,workflow_completed=True,exact_source_schedule_axes_verified=True,
        fixture_only=True,live_provider_or_billing_observed=False))
    role='teacher' if comparison=='bridge' else 'student'
    parsed=contract(review_base,root,'E009-noGLM',role,f['features'],comparison,engineering=True)[-1]
    if parsed['status']!='PASS':raise ValueError('Actual post-shutdown actor/export reader failed')
    if comparison=='bridge':
        try:contract(review_base,root,'E009-GLM','student',f['features'],comparison,engineering=True)
        except ValueError as exc:
            if 'do not rescore' not in str(exc):raise
        else:raise ValueError('Accepted E023 actor was allowed into new evaluation')
    write(root/'completed.json',dict(status='PASS',comparison=comparison,actual_ready_events=events,
        no_overlap=True,verified_resume_noop=True,archive=packed,
        actual=['installed stage consumer','real DNA windows/context/parent depth','cached sparse reader/selection',
                'complete DNA export','strict source/state/byte reload','Snakemake serial scheduling','bounded deduplicated collector','post-shutdown new-output contract reader'],
        synthetic=['engineering vector/marker annotations']+(['GLM model inference only'] if comparison=='learning' else []),
        native_Linux_or_community_admission=False))


if __name__=='__main__':
    a=argparse.ArgumentParser(description=__doc__);a.add_argument('--root',required=True,type=Path)
    a.add_argument('--workflow-python',required=True,type=Path);a.add_argument('--comparison',required=True,choices=['bridge','learning'])
    v=a.parse_args();run(v.root,v.workflow_python,v.comparison)
