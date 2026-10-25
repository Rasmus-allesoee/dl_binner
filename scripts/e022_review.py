#!/usr/bin/env python3
"""Evaluate only new E022 unit using unchanged admitted E014 evaluator contracts.

The adapter changes expected candidate config/kind and adds strict pair-cache
and exposure gates. Existing token and diagnostic functions are unchanged. Diagnostic/geometry/population/export/evaluator
functions are imported unchanged; all baseline summaries are reused, not rescored.
Requires verified shutdown and complete archive/member admission by the caller.
"""
import argparse
from pathlib import Path
import sys
import time
from collections import defaultdict
sys.path.insert(0,str(Path(__file__).absolute().parent))
from e014_review import (read,REPO,require,binding,write_json,refinement_membership,
    verify_choices,manifest_bindings,export_accounting,synthetic_rows,diagnostics,
    grouping_diagnostics,population_cells,oral_labels,oral_population,parent_geometry)


from e021_review import token_contract


def admission_contract(path):
    """Refuse diagnostics before independent shutdown, member and cost admission."""
    value=read(path)
    require(value.get('provider_status')=='TERMINATED'
        and value.get('archive_and_every_member_verified') is True
        and value.get('cost_and_retention_admitted') is True
        and value.get('workflow_completed') is True,
        'Independent shutdown/archive/member/cost admission required')
    return value


def pair_contract(unit,features,checkpoint):
    """Independently bind returned pair files, exact exposure and absolute ramp.

    This reader uses no origin/truth labels. Pair accuracy is a later diagnostic,
    never a selector. Native feature hashes and manifest inventory remain strict.
    """
    from dl_binner.relational.pairs import load_pairs,policy
    import numpy as np
    pairs,m=load_pairs(Path(unit)/'pairs',features);cfg=policy(checkpoint['config']['relational'])
    require(checkpoint['training_pairs_sha256']==binding(Path(unit)/'pairs/cache.json')['sha256'],
        'Pair checkpoint provenance differs')
    require(checkpoint['samples']==m['samples'] and len(checkpoint['history'])==20,
        'Pair sample/schedule axes differ')
    for h in checkpoint['history']:
        expected=cfg['loss_weight']*min(1.,max(0.,(h['epoch']-cfg['warmup_epochs'])/cfg['ramp_epochs']))
        require(h['relation_pairs_exposed']==len(pairs['left']) and h['relation_weight']==expected
            and np.isfinite([h['relation_positive'],h['relation_negative']]).all(),
            'Pair full exposure/ramp/finite losses differ')
    return dict(status='PASS_EXACT_PAIR_CACHE_AND_TRAINING_EXPOSURE',manifest=binding(Path(unit)/'pairs/cache.json'),
        pairs=len(pairs['left']),sign_counts=m['summary']['sign_counts'],policy=cfg,
        scope='Cache/source/exposure only; not proof every marker constraint is biologically correct')


def pair_label_audit(pairs,labels):
    """Describe conservative dominant-origin label consistency after fitting only.

    Equal labels are not unique-sequence proof; missing/ambiguous labels remain
    unresolved. This diagnostic must never feed the frozen pair selection.
    """
    counts={str(sign):dict(same_admitted_label=0,different_admitted_labels=0,unresolved=0)for sign in [-1,1]}
    for a,b,sign in zip(pairs['left'],pairs['right'],pairs['sign']):
        x,y=labels.get(str(pairs['ids'][a])),labels.get(str(pairs['ids'][b]))
        key='unresolved'if x is None or y is None else 'same_admitted_label'if x==y else 'different_admitted_labels'
        counts[str(int(sign))][key]+=1
    return dict(counts=counts,scope='Conservative dominant-origin label consistency, not unique identity or proof all loci/replicons agree; no feedback into selection')


def unit_review(unit,features,original_inventory,output,dataset,marker_clean,truth_root,graph_proof,reuse_lock,admission):
    """Review one complete retained unit and its parent/old/selected alternatives."""
    admitted=admission_contract(admission)
    import numpy as np
    from threadpoolctl import threadpool_limits
    from dl_binner.multiview.views import load
    from dl_binner.multiview.arrays import load_arrays
    from e012_marker_audit import verify_truth
    from e014_oral_truth import evaluate
    started=time.monotonic();unit,features,output=Path(unit),Path(features),Path(output);output.mkdir(exist_ok=False);threadpool_limits(4)
    original=read(original_inventory)['all_work_members'];reuse=read(reuse_lock);data,meta=load(features);ids=data['ids'].tolist();checkpoint=read(unit/'train/checkpoint.json')
    cfg=read(REPO/'experiments/E022-marker-informed-learning/config.json')
    require(checkpoint['config']==cfg and checkpoint['threads']==4 and checkpoint['loader_workers']==0
        and len(checkpoint['history'])==20 and [h['epoch']for h in checkpoint['history']]==list(range(1,21))
        and all(h['parents_seen']==checkpoint['training_parents']and np.isfinite(h['loss'])for h in checkpoint['history']),'Frozen schedule/exposure differs')
    require(checkpoint['training_features_sha256']==binding(features)['sha256']and checkpoint['sha256']==binding(unit/'train/checkpoint.pt')['sha256'],'Training feature/checkpoint bindings differ')
    require(checkpoint['kind']=='relational_checkpoint' and checkpoint['teacher_parameter_count']==checkpoint['parameter_count']
        and checkpoint['predictor_parameter_count']>0 and checkpoint['ema_updates']==20*((checkpoint['training_parents']+255)//256)
        and 0<=checkpoint['positive_parents']<=checkpoint['training_parents']
        and all(not g['catastrophic_collapse'] for h in checkpoint['history'] for m in h['geometry'].values() for g in m.values()),
        'Positive-only target/predictor/exposure/noncollapse contracts differ')
    require(checkpoint['training_views_sha256']==reuse['files'][reuse['units'][unit.name]['views']]['sha256'],'Training view bank differs')
    if unit.name!='oral-dev4':require(checkpoint['training_parents']==int(data['eligible'].sum()),'Not every eligible parent trained')
    pair_receipts=pair_contract(unit,features,checkpoint)
    require(binding(unit/'pairs/cache.json')==read(REPO/'experiments/E022-marker-informed-learning/input-lock.json')['pair_members']['cache.json'], 'Prospectively frozen E009 pair cache differs')
    token_receipts=token_contract(unit,original,checkpoint,binding(features))
    require(binding(unit/'accepted-context.json')==reuse['files'][reuse['units'][unit.name]['tokens']+'/tokens.json'],'Retained original context manifest differs')
    em=read(unit/'embeddings.json');require(em['reload_exact']and em['checkpoint_sha256']==checkpoint['sha256']and em['features_sha256']==binding(features)['sha256'],'Native exact reload receipt differs')
    require(original['units/'+unit.name+'/embeddings.npz']==original['units/'+unit.name+'/train/reference.npz'],'Native before/after reload arrays differ')
    pre,old,post=[read(unit/p)for p in ['group/partition.json','refine/old-partition.json','refine/partition.json']]
    require(pre['ids']==old['ids']==post['ids']==ids and pre['config']==read(REPO/'src/dl_binner/resources/multiview.json'),'Full axes/downstream freeze differs')
    proof=read(graph_proof);audit=pre['audit'];sample=proof['geometry']['queries'][:pre['config']['audit_queries']]
    require(proof['status']=='PASS'and proof['partition']==binding(unit/'group/partition.json')
        and proof['graph']==original['units/'+unit.name+'/group/graph.npz']
        and proof['embedding']==original['units/'+unit.name+'/embeddings.npz']
        and proof['embedding_metadata']==em and proof['objective']==pre['objective']
        and pre['parent_features_sha256']==binding(features)['sha256']
        and pre['transform']=='none; learned unit sphere preserved','Native geometry/source bindings differ')
    require([r['id']for r in sample]==audit['query_ids']
        and np.mean([r['recall_k']for r in sample])==audit['mean_tie_aware_recall']
        and min(r['recall_k']for r in sample)==audit['min_query_recall']
        and audit['mean_tie_aware_recall']>=pre['config']['min_neighbor_recall'],'Independent native neighbor audit differs')
    refinement_membership(pre,old)
    choices=verify_choices(pre,old,post,read(unit/'refine/decisions.json'),read(unit/'refine/alternatives.json'))
    completed=read(unit/'refine/completed.json');require(completed['status']=='SUCCESS'and not completed['truth_accessed']and completed['policy']=='unchanged E013','Native refinement gate differs')
    require(completed['parent_sha256']==binding(unit/'group/partition.json')['sha256']
        and completed['features_sha256']==binding(features)['sha256']
        and completed['embeddings_sha256']==proof['embedding']['sha256']
        and completed['partition_sha256']==binding(unit/'refine/partition.json')['sha256'],'Refinement retained input/output bindings differ')
    account=read(unit/'export/accounting.json');clean=set(read(marker_clean)['clean']);checks={}
    for arm,part in [('pre',pre),('old',old),('post',post)]:
        manifest=read(unit/'export'/arm/'manifest.json');manifest_bindings(manifest,'units/'+unit.name+'/export/'+arm,original)
        require(manifest['features_sha256']==binding(features)['sha256']and manifest['fasta_sha256']==meta['fasta_sha256'],'Export input hashes differ')
        from e017_review import export_contract
        _,checks[arm]=export_contract(part,data,unit/'export'/arm)
        require(account[arm]==manifest and manifest['includes_full_DNA']==(arm=='post'),'Three-arm manifest/DNA scope differs')
    result=dict(status='SUCCESS',unit=unit.name,dataset=dataset,source='E022 frozen reliable cross-contig learning; phase source is in the verified native receipt',admission=admitted,contracts=checks,choices=choices,
        checkpoint=checkpoint,features_metadata=meta,embedding_metadata=em,refinement=completed,native_graph_review=proof,token_contract=token_receipts,pair_contract=pair_receipts,arms={},
        portability='Original E010 Mac allclose remains failed. Use original E022 native output vectors and passing native exact reload; no local model inference. Context and full GLM NPY bytes remain on the stopped VM; local review verifies their immutable inventory/manifest bindings, not an independent local vector reread.')
    if dataset=='E009':
        lock=read(REPO/'experiments/E013-marker-quality/review-lock.json');truth_path=verify_truth(lock);truth=read(truth_path/'truth.json');targets=read(truth_path/'targets.json');pop=read(REPO/lock['population_path'])
        require(ids==truth['ordered_contig_ids']and meta['samples']==read(REPO/'experiments/E010-coherent-prototype/candidate-lock.json')['ordered_depth_columns'],'E009 full truth/depth axes differ')
        for arm,part in [('pre',pre),('old',old),('post',post)]:
            rows=synthetic_rows(part,data);metrics=diagnostics(truth,rows,part,pop,targets)
            grouped=grouping_diagnostics(truth,rows,pop,targets,clean);require(grouped['recovery']==metrics['recovery'],'Independent E009 recovery contracts disagree')
            result['arms'][arm]=dict(diagnostics=metrics,populations=population_cells(rows,truth,pop,clean),grouping=grouped)
        labels={q:truth['contigs'][q]['AMBER_label']for q in ids}
    else:
        lab,quarantine,shared,genomes,truth=oral_labels(truth_root,ids,data['lengths']);require(not meta['samples'],'Oral depth is not admitted')
        require(meta['fasta_sha256']==truth['model_input']['sha256'],'Oral source-blind DNA differs')
        for arm,part,path in [('pre',pre,unit/'group/partition.json'),('old',old,unit/'refine/old-partition.json'),('post',post,unit/'refine/partition.json')]:
            evaluated=evaluate(truth_root,path,output/('truth-'+arm))
            result['arms'][arm]=dict(evaluation=evaluated,grouping=oral_population(part,data,lab,quarantine,shared,genomes,truth['targets'],clean))
        labels={q:(genomes[int(lab[i])]if lab[i]>=0 else None)for i,q in enumerate(ids)}
    from dl_binner.relational.pairs import load_pairs
    new_pairs,_=load_pairs(unit/'pairs',features)
    result['constraint_label_consistency']=pair_label_audit(new_pairs,labels)
    # Saved alternatives are fully checked/evaluated; retain only the parent
    # during the bounded raw-matrix diagnostic, rather than three million-row
    # Python partition objects alongside its numerical temporaries.
    del old,post,part
    result['raw_learned_geometry']=parent_geometry(data,checkpoint['transform'],pre,labels)
    query_groups=defaultdict(list)
    for row in result['raw_learned_geometry']['queries']:
        lineage=pop['genomes'][row['origin_label']]['lineage_class']if dataset=='E009'else'provided_bacterial_source'
        query_groups[lineage].append(row)
    result['raw_learned_geometry']['by_lineage']={g:dict(queries=len(rows),raw_mean=sum(x['raw_same']for x in rows)/len(rows),
        learned_mean=sum(x['learned_same']for x in rows)/len(rows))for g,rows in query_groups.items()}
    result['local_wall_seconds']=time.monotonic()-started;write_json(output/'review.json',result)
    print('E022_UNIT_REVIEWED',unit.name,{a:(v['diagnostics']['recovery_summary']if dataset=='E009'else v['evaluation']['origin']['recovery_summary'])for a,v in result['arms'].items()},flush=True)
    return result

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for k in ['unit','features','original-inventory','output','marker-clean','truth-root','graph-proof','reuse-lock','admission']:p.add_argument('--'+k,type=Path,required=True)
    p.add_argument('--dataset',choices=['E009'],required=True);a=p.parse_args()
    unit_review(a.unit,a.features,a.original_inventory,a.output,a.dataset,a.marker_clean,a.truth_root,a.graph_proof,a.reuse_lock,a.admission)
