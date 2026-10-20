#!/usr/bin/env python3
"""Post-shutdown E017 diagnostics of new outputs only; never launch or regroup.

The caller must independently admit termination, original budget/retention and
all archive/member bytes. Uses the unchanged conservative-v2 and oral-origin
engines; older scalar results and fixed E016 learned geometry are read, not
rescored. Compact partitions name numeric neighbor caches. In-memory diagnostic views use
the verified original E016 learned-neighbor lists, without rescoring old bins or
calling the new joint-core graph a matched learned-geometry comparison.
"""
import argparse
import csv
import json
from pathlib import Path
import sys
import time
sys.path.insert(0,str(Path(__file__).absolute().parent))
from e014_review import (read,require,binding,write_json,synthetic_rows,diagnostics,
                        grouping_diagnostics,population_cells,oral_labels,oral_population)
from e013_review import verify_choices
from e010_review import refinement_membership

REPO=Path(__file__).absolute().parents[1]
ARMS={'cores':'group/core-partition.json','pre':'group/partition.json',
      'old':'refine/old-partition.json','post':'refine/partition.json'}


def export_contract(part,data,folder):
    """Independently verify complete TSV axes, status/reason and base denominators."""
    folder=Path(folder);meta=read(folder/'manifest.json');totals={k:dict(contigs=0,bp=0) for k in ['assigned','unassigned','excluded']}
    require(binding(folder/'assignments.tsv')==meta['files']['assignments.tsv'],'Assignment bytes differ')
    rows=synthetic_rows(part,data);n=0
    with (folder/'assignments.tsv').open() as f:
        reader=csv.DictReader(f,delimiter='\t')
        require(reader.fieldnames==['contig_id','length','bin_id','status','reason'],'Assignment schema differs')
        for i,row in enumerate(reader):
            require(i<len(rows) and row==rows[i],'Full assignment axis/status/reason differs')
            cell=totals[row['status']];cell['contigs']+=1;cell['bp']+=int(row['length']);n+=1
    require(n==len(rows)==meta['contigs'] and meta['bp']==int(data['lengths'].sum())
            and totals==meta['populations'],'Full-DNA accounting differs')
    return rows,dict(contigs=n,bp=meta['bp'],populations=totals,full_DNA_manifest=meta['includes_full_DNA'])


def review(unit,features,admission,output,dataset,marker_clean,truth_root,fixed_neighbors,reuse_lock):
    """Evaluate core/recruited/old/E013 partitions sequentially with frozen truths."""
    from dl_binner.multiview.views import load
    from dl_binner.information.export import validate_partition
    from e012_marker_audit import verify_truth
    from e014_oral_truth import evaluate
    from threadpoolctl import threadpool_limits
    threadpool_limits(4);started=time.monotonic();unit,output=Path(unit),Path(output)
    admitted=read(admission)
    require(admitted['provider_status']=='TERMINATED' and admitted['archive_and_every_member_verified'] is True
            and admitted['cost_and_retention_admitted'] is True,'Independent shutdown/byte/cost admission required')
    require(read(unit/'audit.json')['status']=='PASS','Native complete-cache readback missing')
    data,meta=load(features);ids=data['ids'].tolist();clean=set(read(marker_clean)['clean'])
    locked=read(reuse_lock)
    expected=next((v for k,v in locked['files'].items() if k.endswith('/work/units/'+unit.name+'/group/partition.json')),None)
    require(expected is not None and binding(fixed_neighbors)==expected,'Preserved E016 neighbor source differs')
    fixed=read(fixed_neighbors)
    require(fixed['ids']==ids and len(fixed['neighbors'])==len(ids),'Preserved full learned-neighbor axis differs')
    fixed_nn=fixed['neighbors'];fixed_embedding=fixed['embedding_sha256'];del fixed
    native=read(unit/'audit.json');group=read(unit/'group/completed.json')
    require(native['original_embeddings_sha256']==fixed_embedding and native['graph_sha256']==binding(unit/'group/graph.npz')['sha256']
            and native['recruitment_sha256']==binding(unit/'group/recruitment.npz')['sha256']
            and group['features_sha256']==binding(features)['sha256'],'Native cache proof/input binding differs')
    output.mkdir(parents=True,exist_ok=False)
    # Check parent alternatives together once, then release them for sequential metrics.
    pre,old,post=[validate_partition(data,unit/ARMS[k],features) for k in ['pre','old','post']]
    refinement_membership(pre,old)
    choices=verify_choices(pre,old,post,read(unit/'refine/decisions.json'),read(unit/'refine/alternatives.json'))
    completed=read(unit/'refine/completed.json')
    require(completed['status']=='SUCCESS' and completed['policy']=='unchanged E013'
            and completed['parent_sha256']==binding(unit/ARMS['pre'])['sha256']
            and completed['partition_sha256']==binding(unit/ARMS['post'])['sha256'], 'Fixed-refiner output/source binding differs')
    del pre,old,post
    # Truth remains outside the native plan and feature/training namespace.
    result=dict(status='SUCCESS',dataset=dataset,arms={},choices=choices,contracts={},
                truth_modes='E009 conservative v2; oral provided-origin oracle, never pooled',
                geometry='Preserved E016 learned-neighbor arrays are attached only to in-memory diagnostic views of NEW labels. No old partition is rescored or neighbor index rebuilt. These 5NN metrics describe fixed learning, not the new joint-core graph; its sampled audits are separate.',
                native_cache_proof=native,features_metadata=meta)
    if dataset=='E009':
        lock=read(REPO/'experiments/E013-marker-quality/review-lock.json');truth_path=verify_truth(lock)
        require(Path(truth_root).resolve()==truth_path.resolve(),'Supplied E009 truth locator differs from admitted v2')
        truth=read(truth_path/'truth.json');targets=read(truth_path/'targets.json');pop=read(REPO/lock['population_path'])
        require(ids==truth['ordered_contig_ids'] and meta['samples']==read(REPO/'experiments/E010-coherent-prototype/candidate-lock.json')['ordered_depth_columns'],
                'Complete E009 ordered depth/truth axes differ')
    else:
        lab,quarantine,shared,genomes,truth=oral_labels(truth_root,ids,data['lengths'])
        require(not meta['samples'] and meta['fasta_sha256']==truth['model_input']['sha256'],'Sequence-only oracle/source differs')
    for arm,path in ARMS.items():
        part=validate_partition(data,unit/path,features)
        rows,account=export_contract(part,data,unit/'export'/arm);result['contracts'][arm]=account
        population_only=dict(part,neighbors=fixed_nn)
        if dataset=='E009':
            metrics=diagnostics(truth,rows,population_only,pop,targets)
            grouped=grouping_diagnostics(truth,rows,pop,targets,clean)
            require(grouped['recovery']==metrics['recovery'],'Independent E009 evaluators disagree')
            result['arms'][arm]=dict(diagnostics=metrics,populations=population_cells(rows,truth,pop,clean),grouping=grouped)
        else:
            evaluated=evaluate(truth_root,unit/path,output/('truth-'+arm))
            result['arms'][arm]=dict(evaluation=evaluated,grouping=oral_population(population_only,data,lab,quarantine,shared,genomes,truth['targets'],clean))
        del part,rows
    result['wall_seconds']=time.monotonic()-started
    write_json(output/'review.json',result);return result


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for k in ['unit','features','admission','output','marker-clean','truth-root','fixed-neighbors','reuse-lock']:p.add_argument('--'+k,type=Path,required=True)
    p.add_argument('--dataset',choices=['E009','oral'],required=True);a=p.parse_args()
    review(a.unit,a.features,a.admission,a.output,a.dataset,a.marker_clean,a.truth_root,a.fixed_neighbors,a.reuse_lock)
