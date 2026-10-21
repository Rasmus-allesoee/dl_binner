#!/usr/bin/env python3
"""Serial restore-only E018 selection/refinement/export/audit DAG; no grouping fit."""
import argparse
import json
import os
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).absolute().parent))
UNITS=['E009-positive','oral-positive']


def validate_plan(p):
    """Accept only exact retained E017 input locators and unchanged package defaults."""
    expected={'kind','work','units','threads','python','worker','workflow_python','snakefile','base_config','hmm','reuse_lock'}
    if set(p)!=expected or p['kind']!='E018 cached vote-led recruitment' or p['threads']!=4 or list(p['units'])!=UNITS:
        raise ValueError('Cached acceptance scope differs')
    lock=json.loads(Path(p['reuse_lock']).read_text())
    if p['units']!=lock['units']or p['hmm']!=lock['hmm']or any(set(u)!={'fasta','features','embeddings','marker_cache','retained_group'}for u in p['units'].values()):
        raise ValueError('Sealed input locators or allowed fields differ')
    import dl_binner
    base=json.loads(Path(p['base_config']).read_text())
    if base!=json.loads((Path(dl_binner.__file__).parent/'resources/multiview.json').read_text()):
        raise ValueError('Unchanged E013/default package contract differs')
    return base


def audit(features,retained,group,output):
    """Independently read complete new labels against saved offers and fixed cores.

    Does not rerun selection, grouping or refinement. The scalar predicate and
    core-identity map provide a separate readback of the vectorized selector.
    """
    import numpy as np
    from e018_recruit import read_inputs
    from dl_binner.information.export import validate_partition
    from dl_binner.multiview.arrays import load_arrays
    from dl_binner.io import digest,write_json
    from dl_binner.information.grouping import require
    data,meta,core,old,cache,gm=read_inputs(features,retained)
    group=Path(group);part=validate_partition(data,group/'partition.json',features)
    selection,sm=load_arrays(group/'selection.npz','E018_cached_selection')
    require(selection['ids'].tolist()==data['ids'].tolist()
            and np.array_equal(selection['query_indices'],cache['query_indices'])
            and sm['parent_sha256']==digest(group/'partition.json')
            and sm['source_recruitment_sha256']==digest(Path(retained)/'recruitment.npz'), 'New selection bindings differ')
    mapping={};seen=set()
    for i,b in enumerate(core['assignment']):
        if b>=0:
            new=part['assignment'][i];require(new>=0 and mapping.setdefault(b,new)==new,'Core changed')
    require(len(set(mapping.values()))==len(mapping),'Core bins merged')
    for row,i in enumerate(cache['query_indices']):
        offers=[(int(b),col)for col,b in enumerate(cache['offered_bins'][row])if b>=0
                and cache['normalized_scores'][row,col]<=1.
                and cache['vote_fractions'][row,col]>=2/3 and cache['distinct_support'][row,col]>=2]
        require(len(offers)<=1,'Multiple admissible candidates')
        selected,col=offers[0]if offers else(-1,-1)
        require(int(selection['accepted_bins'][row])==selected and int(selection['chosen_offer'][row])==col
                and part['assignment'][i]==(mapping[selected]if selected>=0 else-1),'Independent cached selection differs')
        require(cache['accepted_bins'][row]<0 or cache['accepted_bins'][row]==selected,'Old recruit lost')
        seen.add(int(i))
    require(seen==set(np.flatnonzero(data['eligible']&(np.asarray(core['assignment'])<0))), 'Query coverage incomplete')
    write_json(output,dict(status='PASS',rows=len(data['ids']),bp=int(data['lengths'].sum()),samples=meta['samples'],
        graph_sha256=old['graph_sha256'],original_embeddings_sha256=old['embedding_sha256'],
        recruitment_sha256=digest(Path(retained)/'recruitment.npz'),original_core_sha256=digest(Path(retained)/'core-partition.json'),
        parent_sha256=digest(group/'partition.json'),complete_DNA_axes=True,old_accepted_subset=True,
        index_rebuilt=False,cores_regrouped=False,profiles_recomputed=False,marker_detection=False,truth_used=False))


def stage(plan,unit,name):
    """Run exactly one fresh new-output consumer; no fallback or old science replay."""
    p=json.loads(Path(plan).read_text());base=validate_plan(p)
    if unit not in UNITS:raise ValueError('Unknown unit')
    u=p['units'][unit];root=Path(p['work'])/'units'/unit;root.mkdir(parents=True,exist_ok=True);target=root/name
    if target.is_dir()and not any(target.iterdir()):target.rmdir()
    if name=='group':
        from e018_recruit import consume
        consume(u['features'],u['retained_group'],target)
    elif name=='refine':
        from dl_binner.multiview.downstream import refine
        refine(u['features'],u['embeddings'],root/'group/partition.json',u['marker_cache'],u['fasta'],p['hmm'],target,base)
    elif name=='export':
        from dl_binner.information.export import export
        from dl_binner.io import write_json
        target.mkdir();account={}
        for arm,part in [('pre',root/'group/partition.json'),('old',root/'refine/old-partition.json'),('post',root/'refine/partition.json')]:
            account[arm]=export(u['features'],part,u['fasta'],target/arm,include_dna=arm=='post')
        write_json(target/'accounting.json',account)
    elif name=='audit':audit(u['features'],u['retained_group'],root/'group',root/'audit.json')
    else:raise ValueError('Only cached group/refine/export/audit permitted')


def workflow(plan,dry_run=False):
    """Use the accepted four-core serial local executor and explicit unit barrier."""
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
        if a.unit or a.stage:p.error('No individual stage with workflow')
        workflow(a.plan,a.dry_run)
    else:
        if a.dry_run or not a.unit or not a.stage:p.error('Stage requires unit/name')
        stage(a.plan,a.unit,a.stage)
