#!/usr/bin/env python3
"""Run one explicit stage of the frozen comparison; no truth or cloud APIs.

The serial Snakemake DAG calls this in isolated tensor/graph/marker processes.
Science plans contain DNA/depth/cache paths only. Release admission, clock/RAM,
watchdog, costs and final collection are external, before this consumer runs.
"""
import argparse
import json
import os
from pathlib import Path
import sys


def validate_plan(p):
    """Keep the three science units and their inputs distinct from evaluator labels."""
    allowed={'kind','work','units','threads','python','worker','candidate_config','legacy_config','hmm','asset_manifest',
             'oral_marker_cache','workflow_python','snakefile'}
    if set(p)-allowed or p['threads']!=4 or set(p['units'])!={'E009-dev5','oral-dev4','oral-dev5'}:
        raise ValueError('Frozen science plan scope differs')
    unit_fields={'learning','fasta','depth','parent_features','features','marker_cache'}
    for name,u in p['units'].items():
        if set(u)-unit_fields or u['learning']!=('dev4'if name=='oral-dev4'else'dev5'):
            raise ValueError('Unexpected science/evaluator input or learner')


def legacy_bank(fasta,features,output,cfg):
    """Produce exactly frozen dev4 windows while reusing the same full-parent arrays.

    A native tiny parity test compares every bank array with the original writer.
    This is new-data preparation, not regeneration of accepted E009 evidence.
    """
    import numpy as np
    from dl_binner.io import load_arrays,digest,save_arrays,write_json
    from dl_binner.candidate.views import windows,composition,load
    from dl_binner.multiview.views import fasta_rows
    data,meta=load(features);n=len(data['ids']);out=Path(output);out.mkdir(parents=True,exist_ok=False)
    if digest(fasta)!=meta['fasta_sha256']:raise ValueError('Legacy bank DNA differs')
    bank=np.zeros((n,4,136),np.float32);counts=np.zeros((n,4),np.int64);coords=np.full((n,4,2),-1,np.int64)
    hashes=np.full((n,4),'',dtype='<U64')
    import hashlib
    seen=0
    for i,(ident,dna) in enumerate(fasta_rows(fasta)):
        if ident!=data['ids'][i] or len(dna)!=data['lengths'][i]:raise ValueError('Legacy parent axis differs')
        for j,(a,b,s) in enumerate(windows(ident,dna,cfg)):
            bank[i,j],counts[i,j]=composition(s);coords[i,j]=a,b;hashes[i,j]=hashlib.sha256(s.encode()).hexdigest()
        seen+=1
    if seen!=n:raise ValueError('Legacy bank row count differs')
    trainable=data['eligible']&(counts>0).all(1)
    save_arrays(out/'views.npz',dict(ids=data['ids'],tnf=bank,valid_fourmers=counts,coordinates=coords,
        sequence_sha256=hashes,trainable=trainable),dict(kind='candidate_views',parent_features_sha256=digest(features),
        fasta_sha256=digest(fasta),policy=cfg,coordinates='zero-based half-open',depth_semantics=meta['depth_semantics'],training_parents=int(trainable.sum())))
    load(features,out/'views.npz');write_json(out/'prepared.json',dict(features=str(Path(features).absolute()),
        features_sha256=digest(features),views_sha256=digest(out/'views.npz'),parent_features_reused=True,legacy_writer='unchanged dev4 windows/composition'))


def stage(plan,unit,name):
    """Consume a source-frozen method stage in a fresh directory without hidden fallback."""
    from dl_binner.multiview.views import config,prepare
    from dl_binner.io import load_arrays,digest,write_json
    from dl_binner.candidate.views import config as legacy_config
    p=json.loads(Path(plan).read_text());validate_plan(p);u=p['units'][unit];root=Path(p['work'])/'units'/unit
    cfg=config(p['candidate_config']);old=legacy_config(p['legacy_config']);root.mkdir(parents=True,exist_ok=True)
    # Snakemake creates declared output parents before dispatch. Admit only that
    # empty directory; never delete or reinterpret a partial/completed payload.
    target=Path(p['oral_marker_cache']) if name=='markers' else root/name
    if name!='embed' and target.is_dir() and not any(target.iterdir()):target.rmdir()
    if name=='features':
        if u['learning']=='dev4':legacy_bank(u['fasta'],u['features'],root/'features',old)
        else:prepare(u['fasta'],u.get('depth'),root/'features',cfg,u.get('parent_features'))
        return
    if name=='markers':
        from dl_binner.candidate.markers import cache
        dest=Path(p['oral_marker_cache']);dest.mkdir(parents=True,exist_ok=False)
        cache(u['fasta'],p['hmm'],p['asset_manifest'],dest,p['threads']);return
    if name=='train':
        if u['learning']=='dev4':
            from dl_binner.candidate.model import train
            (root/'train').mkdir();train(u['features'],root/'features/views.npz',root/'train',old,p['threads'])
        else:
            from dl_binner.multiview.model import train
            train(u['features'],root/'features/views.npz',root/'train',cfg,p['threads'])
    elif name=='embed':
        if u['learning']=='dev4':from dl_binner.candidate.model import embed
        else:from dl_binner.multiview.model import embed
        embed(u['features'],root/'train/checkpoint.pt',root/'embeddings.npz',p['threads'])
    elif name=='group':
        from dl_binner.multiview.downstream import group
        group(root/'embeddings.npz',u['features'],root/'group',cfg,p['threads'])
    elif name=='refine':
        from dl_binner.multiview.downstream import refine
        refine(u['features'],root/'embeddings.npz',root/'group/partition.json',u['marker_cache'],u['fasta'],p['hmm'],root/'refine',cfg)
    elif name=='export':
        from dl_binner.clustering import export
        from dl_binner.accounting import summarize_arm
        out=root/'export';out.mkdir()
        results={}
        for label,partition in [('pre',root/'group/partition.json'),('post',root/'refine/partition.json')]:
            export(u['features'],partition,u['fasta'],out/label);results[label]=summarize_arm(u['features'],out/label)[0]
        write_json(out/'accounting.json',results)
    else:raise ValueError('Unknown comparison stage')


def workflow(plan,dry_run=False):
    """Replace this process with the pinned local Snakemake executor, four cores only."""
    plan=Path(plan).absolute();p=json.loads(plan.read_text());validate_plan(p)
    if p['threads']!=4:raise ValueError('Frozen four-thread comparison required')
    argv=[p['workflow_python'],'-I','-B','-m','snakemake','--snakefile',p['snakefile'],
          '--directory',p['work'],'--cores','4','--config','plan='+str(plan),'--printshellcmds','--benchmark-extended']
    if dry_run:argv.append('--dry-run')
    os.execv(argv[0],argv)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--plan',type=Path,required=True)
    p.add_argument('--workflow',action='store_true');p.add_argument('--dry-run',action='store_true');p.add_argument('--unit');p.add_argument('--stage',choices=['features','markers','train','embed','group','refine','export'])
    a=p.parse_args()
    if a.workflow:
        if a.unit or a.stage:p.error('Workflow entry cannot select another individual stage')
        workflow(a.plan,a.dry_run)
    else:
        if a.dry_run:p.error('--dry-run requires --workflow')
        if not a.unit or not a.stage:p.error('Individual stage needs --unit and --stage')
        stage(a.plan,a.unit,a.stage)
