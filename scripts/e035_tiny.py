#!/usr/bin/env python3
"""Actual tiny classifier/view/three-mode learning/construction/return workflow.

Reuse the byte-verified, completed E031 engineering models without refitting them.
The synthetic-reference MMseqs2 classifier is real. GLM vectors and cached marker
annotations are synthetic retained engineering fixtures; no community is scored.
"""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys

import dl_binner as _owned_product

ROOT=Path(__file__).absolute().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from e024_coverage import binding,write


def prepare(original, binary, root, workflow_python, reference_path=None, classification=None):
    """Verify retained tiny states, then classify only their generated DNA."""
    from e035_control import UNITS,product_scope
    from e024_control import verify_seal
    from e035_fixture import reference
    from dl_binner.taxonomy.classifier import classify
    product_scope();root=Path(root).absolute();root.mkdir(parents=True,exist_ok=False);old=Path(original).absolute()
    p=json.loads((old/'plan.json').read_text());units={};protected={}
    for u in UNITS:
        entry=p['units'][u];state=old/'work'/u/'train/result/checkpoint.pt';vectors=old/'work'/u/'embed/embeddings.npz'
        verify_seal(state.parent.parent);verify_seal(vectors.parent)
        units[u]={k:entry[k] for k in ['features','views','tokens','frozen','fasta','marker_evidence']}
        units[u].update(checkpoint=str(state),embeddings=str(vectors),annotations=str(root/'classification/annotations'),community='oral' if u.startswith('oral') else 'E009')
        for path in [state,state.with_suffix('.json'),vectors,vectors.with_suffix('.json'),Path(entry['features']),Path(entry['views']),Path(entry['tokens'])/'tokens.json']:
            protected[str(path)]=binding(path)
    source=units[UNITS[0]];db=reference(binary,source['fasta'],root/'reference') if reference_path is None else Path(reference_path)
    if classification is None:
        classify(binary,db,source['fasta'],source['features'],root/'classification',engineering=True)
    else:
        from dl_binner.taxonomy.normalization import complete
        from dl_binner.taxonomy.annotations import prepare as prepare_annotations
        from dl_binner.taxonomy.classifier import VERSION,OPTIONS
        c=Path(classification);out=root/'classification';out.mkdir()
        old_provenance=json.loads((c/'provenance.json').read_text())
        exits={n:json.loads((c/(n+'.exit.json')).read_text())for n in ['version','createdb','taxonomy','createtsv']}
        if any(r['exit_code']!=0 for r in exits.values())or exits['taxonomy']['argv'][-len(OPTIONS):]!=OPTIONS or (c/'version.log').read_text().strip()!=VERSION:
            raise ValueError('No verified native classifier stages to reuse')
        reducers=sorted({p.resolve() for p in (c/'tmp').glob('*/orfs_h_swapped.index')})
        if len(reducers)!=1:raise ValueError('Native ORF index missing')
        complete(c/'taxonomy.tsv',c/'query/index.json',c/'queryDB.lookup',reducers[0],out/'complete.tsv')
        old_provenance['zero_ORF_completion']=binding(out/'complete.completion.json');write(out/'provenance.json',old_provenance)
        prepare_annotations(out/'complete.tsv',c/'query/index.json',Path(db).parent/'tree.json',source['features'],out/'provenance.json',out/'annotations',out/'complete.completion.json')
        write(out/'verified-reuse.json',dict(status='PASS',native_classification_not_replayed=True,source=str(c),
            original_exits={n:binding(c/(n+'.exit.json'))for n in exits},raw=binding(c/'taxonomy.tsv')))
    plan=dict(kind='E035 confidence taxonomy',engineering=True,work=str(root/'work'),units=units,
        python=sys.executable,workflow_python=str(Path(workflow_python).absolute()),worker=str(ROOT/'scripts/e035_control.py'),
        snakefile=str(ROOT/'experiments/E035-confidence-taxonomy/Snakefile'),limits={})
    write(root/'plan.json',plan);write(root/'protected-inputs.json',protected)
    return plan


def finish(root, first='first'):
    """Read actual stage scheduling, verify no-op resume and all packed bytes/aliases."""
    from e035_control import UNITS,STAGES
    from e034_collect import pack
    from e024_control import verify_seal
    from dl_binner.taxonomy.cache import read
    from dl_binner.taxonomy.model import policy
    root=Path(root);p=json.loads((root/'plan.json').read_text());argv=[p['python'],'-I','-B',p['worker'],'--plan',str(root/'plan.json'),'--engineering','--workflow']
    events=[];active=None
    for line in (root/(first+'.log')).read_text().splitlines():
        if line.startswith('localrule ')and not line.startswith('localrule all:'):
            if active is not None:raise ValueError('Actual tiny stages overlapped')
            active=line.split()[1].rstrip(':');events.append(active)
        if 'Finished jobid:'in line:active=None
    if len(events)!=31 or events[0]!='barrier':raise ValueError('Complete 31-stage taxonomy workflow was not exercised')
    before={str(q.relative_to(root/'work')):binding(q)for q in (root/'work').rglob('*')if q.is_file()and '.snakemake'not in q.parts}
    with (root/'resume.log').open('x')as log:r=subprocess.run(argv,stdout=log,stderr=subprocess.STDOUT)
    write(root/'resume.exit.json',dict(argv=argv,exit_code=r.returncode))
    if r.returncode or 'Nothing to be done'not in (root/'resume.log').read_text() or any(binding(root/'work'/n)!=b for n,b in before.items()):
        raise ValueError('Taxonomy verified resume replayed or changed sealed science')
    units={}
    for u in UNITS:
        at=root/'work'/u;e=p['units'][u]
        for name in STAGES:verify_seal(at/name)
        read(at/'view-cache/result',e['features'],e['annotations'])
        r=json.loads((at/'student/result/completed.json').read_text())
        if r['policy']!=policy() or len(r['history'])!=20 or r['exact_reload']is not True or r['old_encoder_refit']is not False or r['exact_reference_free_fallback']is not True:raise ValueError('Actual tiny taxonomy learning contract differs')
        units[u]=dict(learning=r,full_DNA=json.loads((at/'audit/proof.json').read_text()))
    protected=json.loads((root/'protected-inputs.json').read_text())
    if any(binding(q)!=b for q,b in protected.items()):raise ValueError('Accepted tiny E031 inputs changed')
    evidence=root/'evidence';evidence.mkdir();write(evidence/'scope.json',dict(engineering=True,community_scored=False,
        actual='native MMseqs2 translated synthetic-reference classification; E031 crop/cache; hierarchical gradients; three fits; E032 constructors/refinement/export; archive aliases',
        synthetic='reference organisms/taxa, generated DNA, retained NumericExtractor GLM vectors and hand-authored cached marker calls'))
    packed=pack(root/'work',evidence,root/'return')
    write(root/'completed.json',dict(status='PASS',serial_stages=events,stage_count=31,no_overlap=True,verified_noop_resume=True,
        units=units,archive=packed,old_E031_state_reused_not_refit=True,protected_input_count=len(protected),
        actual_native_classifier=True,community_data_or_scoring=False,real_GLMinference=False,real_marker_detection=False))


def run(original,binary,root,workflow_python,reference_path=None,classification=None):
    """Execute only the fresh three-mode engineering plan and close its evidence."""
    p=prepare(original,binary,root,workflow_python,reference_path,classification);root=Path(root).absolute()
    argv=[sys.executable,'-I','-B',p['worker'],'--plan',str(root/'plan.json'),'--engineering','--workflow']
    with (root/'first.log').open('x')as log:r=subprocess.run(argv,stdout=log,stderr=subprocess.STDOUT)
    write(root/'first.exit.json',dict(argv=argv,exit_code=r.returncode))
    if r.returncode:raise RuntimeError('Actual E035 tiny workflow failed: '+str(root/'first.log'))
    finish(root)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for name in ['original','binary','root','workflow-python']:p.add_argument('--'+name,type=Path,required=True)
    p.add_argument('--reference',type=Path)
    p.add_argument('--classification',type=Path)
    a=p.parse_args();run(a.original,a.binary,a.root,a.workflow_python,a.reference,a.classification)
