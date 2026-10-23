#!/usr/bin/env python3
"""Restore-only fixed-learning E020 consumer; never starts a VM or reads truth.

One serial core/recruitment -> unchanged E013 -> export -> independent readback
DAG per community. No training, inference, feature preparation, detector, old
score, alternative policy or fallback is reachable from the stage interface.
"""
import argparse
import json
import os
from pathlib import Path
import sys

sys.path.insert(0,str(Path(__file__).absolute().parent))

UNITS=['E009-context','oral-context']


def validate_plan(p):
    """Admit only the frozen cached two-community grouping preparation schema."""
    expected={'kind','work','units','threads','python','worker','workflow_python','snakefile','config','base_config','hmm','reuse_lock'}
    if set(p)!=expected or p['kind']!='E020 cached E019 learning original E017 grouping' or p['threads']!=4 or list(p['units'])!=UNITS:
        raise ValueError('Cached grouping scope differs')
    fields={'fasta','features','embeddings','marker_cache'}
    if any(set(u)!=fields for u in p['units'].values()):raise ValueError('Unexpected learning/truth input')
    from dl_binner.information.grouping import policy
    cfg=policy(p['config']);base=json.loads(Path(p['base_config']).read_text())
    import dl_binner
    original=json.loads((Path(dl_binner.__file__).parent/'resources/multiview.json').read_text())
    reuse=json.loads(Path(p['reuse_lock']).read_text())
    if p['units']!=reuse['units'] or p['hmm']!=reuse['hmm']:
        raise ValueError('Science plan does not consume the exact sealed input locators')
    if base!=original or base['seed']!=11 or base['neighbors']!=30 or base['output']!=64 or base['min_length']!=500:
        raise ValueError('Preserved E019/E013 downstream contract differs')
    return cfg,base


def stage(plan,unit,name):
    """Run one fresh authorized stage using the original retained vectors/cache."""
    p=json.loads(Path(plan).read_text());cfg,base=validate_plan(p)
    if unit not in UNITS:raise ValueError('Unknown development unit')
    if name=='group' and not os.environ.get('NUMBA_CACHE_DIR'):
        raise ValueError('Explicit job-owned NUMBA_CACHE_DIR required before approximate grouping')
    u=p['units'][unit];root=Path(p['work'])/'units'/unit;root.mkdir(parents=True,exist_ok=True)
    target=root/name
    # Only a scheduler-created empty parent is admissible, never partial evidence.
    if target.is_dir() and not any(target.iterdir()):target.rmdir()
    if name=='group':
        from dl_binner.information.grouping import group
        group(u['features'],u['embeddings'],target,cfg,base,4)
    elif name=='refine':
        from dl_binner.multiview.downstream import refine
        refine(u['features'],u['embeddings'],root/'group/partition.json',u['marker_cache'],u['fasta'],p['hmm'],target,base)
    elif name=='export':
        from dl_binner.information.export import export
        from dl_binner.io import write_json
        target.mkdir();accounting={}
        for arm,path in [('cores',root/'group/core-partition.json'),('pre',root/'group/partition.json'),
                         ('old',root/'refine/old-partition.json'),('post',root/'refine/partition.json')]:
            accounting[arm]=export(u['features'],path,u['fasta'],target/arm,include_dna=arm=='post')
        write_json(target/'accounting.json',accounting)
    elif name=='audit':
        from dl_binner.information.audit import review
        review(u['features'],u['embeddings'],root/'group',root/'audit.json')
    else:raise ValueError('Only group/refine/export/audit are authorized')


def workflow(plan,dry_run=False):
    """Run the pinned local executor with four cores and explicit serial barriers."""
    plan=Path(plan).absolute();p=json.loads(plan.read_text());validate_plan(p)
    argv=[p['workflow_python'],'-I','-B','-m','snakemake','--snakefile',p['snakefile'],'--directory',p['work'],
          '--cores','4','--runtime-source-cache-path',str(Path(p['work']).parent/'workflow-source-cache'),
          '--config','plan='+str(plan),'--printshellcmds','--benchmark-extended']
    if dry_run:argv.append('--dry-run')
    os.execv(argv[0],argv)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--plan',type=Path,required=True)
    p.add_argument('--workflow',action='store_true');p.add_argument('--dry-run',action='store_true')
    p.add_argument('--unit',choices=UNITS);p.add_argument('--stage',choices=['group','refine','export','audit']);a=p.parse_args()
    if a.workflow:
        if a.unit or a.stage:p.error('Workflow cannot choose an individual stage')
        workflow(a.plan,a.dry_run)
    else:
        if a.dry_run or not a.unit or not a.stage:p.error('Stage requires --unit and --stage')
        stage(a.plan,a.unit,a.stage)
