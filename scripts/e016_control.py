#!/usr/bin/env python3
"""Consume retained dev5 inputs for the single positive-only control.

This restore-only research worker cannot prepare features/views, call markers or
invoke an older fit. Its two serial units produce fresh native embeddings, the
unchanged CPM/E013 alternatives, complete exports and independent graph receipts.
Truth and cloud APIs are absent from the science plan and worker.
"""
import argparse
import json
import os
from pathlib import Path
import sys

sys.path.insert(0,str(Path(__file__).absolute().parent))
from e014_collect import binding

UNITS=['E009-positive','oral-positive']


def validate_plan(p):
    """Refuse another learner, training rule, input modality or evaluator path."""
    allowed={'kind','work','units','threads','python','worker','workflow_python','snakefile','config','base_config','hmm','reuse_lock'}
    if set(p)!=allowed or p['threads']!=4 or list(p['units'])!=UNITS:
        raise ValueError('Frozen two-fit control scope differs')
    fields={'fasta','features','views','marker_cache'}
    if any(set(u)!=fields for u in p['units'].values()):raise ValueError('Unexpected science/evaluator path')
    cfg=json.loads(Path(p['config']).read_text());base=json.loads(Path(p['base_config']).read_text())
    from e016_policy import validate_policy
    validate_policy(cfg,base)
    return cfg,base


def stage(plan,unit,name):
    """Execute one fresh stage using only the already admitted read-only cache."""
    p=json.loads(Path(plan).read_text());cfg,base=validate_plan(p)
    if unit not in UNITS:raise ValueError('Unknown unit')
    u=p['units'][unit];root=Path(p['work'])/'units'/unit;root.mkdir(parents=True,exist_ok=True)
    target=root/name
    if target.is_dir() and not any(target.iterdir()):target.rmdir()
    if name=='train':
        from dl_binner.multiview.positive import train
        train(u['features'],u['views'],target,cfg,4)
    elif name=='embed':
        from dl_binner.multiview.positive import embed
        embed(u['features'],root/'train/checkpoint.pt',root/'embeddings.npz',4)
    elif name=='group':
        from dl_binner.multiview.downstream import group
        group(root/'embeddings.npz',u['features'],target,base,4)
    elif name=='refine':
        from dl_binner.multiview.downstream import refine
        refine(u['features'],root/'embeddings.npz',root/'group/partition.json',u['marker_cache'],u['fasta'],p['hmm'],target,base)
    elif name=='export':
        from dl_binner.clustering import export
        from dl_binner.accounting import summarize_arm
        from dl_binner.io import write_json
        target.mkdir();result={}
        for label,part in [('pre',root/'group/partition.json'),('post',root/'refine/partition.json')]:
            export(u['features'],part,u['fasta'],target/label)
            result[label]=summarize_arm(u['features'],target/label)[0]
        write_json(target/'accounting.json',result)
    elif name=='graph-proof':
        from e014_graph_review import review
        review(root,root/'graph-proof.json')
    else:raise ValueError('Only fit/embed/group/refine/export/graph-proof are permitted')


def workflow(plan,dry_run=False):
    """Use the pinned four-core local executor and explicit serial unit barriers."""
    plan=Path(plan).absolute();p=json.loads(plan.read_text());validate_plan(p)
    argv=[p['workflow_python'],'-I','-B','-m','snakemake','--snakefile',p['snakefile'],'--directory',p['work'],
          '--cores','4','--runtime-source-cache-path',str(Path(p['work']).parent/'workflow-source-cache'),'--config','plan='+str(plan),'--printshellcmds','--benchmark-extended']
    if dry_run:argv.append('--dry-run')
    os.execv(argv[0],argv)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--plan',type=Path,required=True)
    p.add_argument('--workflow',action='store_true');p.add_argument('--dry-run',action='store_true')
    p.add_argument('--unit',choices=UNITS);p.add_argument('--stage',choices=['train','embed','group','refine','export','graph-proof']);a=p.parse_args()
    if a.workflow:
        if a.unit or a.stage:p.error('Workflow cannot select an individual stage')
        workflow(a.plan,a.dry_run)
    else:
        if a.dry_run or not a.unit or not a.stage:p.error('Individual stage needs --unit and --stage')
        stage(a.plan,a.unit,a.stage)
