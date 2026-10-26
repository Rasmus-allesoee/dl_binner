#!/usr/bin/env python3
"""Evaluate only new sealed E023 outputs with existing frozen sequence evaluators.

Baselines are reused as summaries, never rescored. Secondary per-bin tiers do
not select bins or change the primary R95 policy. Requires independent stopped-
provider, all-member and financial admission; cannot invoke science or cloud.
"""
import argparse
from collections import Counter
import csv
import gzip
import json
from pathlib import Path
import sys

ROOT=Path(__file__).absolute().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'scripts')]
from e014_review import (read,require,binding,manifest_bindings,diagnostics,
                         grouping_diagnostics,population_cells,oral_labels,oral_population)
from e017_review import export_contract
from e022_review import admission_contract


def oral_secondary_rows(path, references, mask=False):
    """Stream the admitted origin oracle into common secondary sequence support."""
    from e014_oral_truth import validate_row
    with gzip.open(path,'rt')as f:
        for raw in f:
            row=json.loads(raw);validate_row(row,references)
            ref=row['reference'];masked=mask and(row['shared_forward_query']or row['shared_complete_reference'])
            spans=[]if masked else row['source_intervals']
            n=sum(b-a for a,b in spans)
            yield dict(id=row['id'],length=row['length'],confirmed_query_bp={row['genome']:n}if n else{},
                       source_intervals={ref:spans}if ref is not None and spans else{})


def review(unit,features,inventory,admission,output,dataset,marker_clean,truth_root):
    """Review two frozen alternatives sequentially, preserving all original DNA axes."""
    from threadpoolctl import threadpool_limits
    from dl_binner.multiview.views import load
    from dl_binner.information.export import validate_partition
    from dl_binner.density.bin_quality import summarize
    from dl_binner.density.grouping import policy
    from e012_marker_audit import verify_truth
    from e014_oral_truth import evaluate
    threadpool_limits(4);admitted=admission_contract(admission);unit=Path(unit);output=Path(output)
    require(unit.name==('E009-E022'if dataset=='E009'else'oral-E019'),'Only new E023 units may be evaluated')
    require(read(unit/'audited.json')['status']=='PASS','Native new-output audit missing')
    record=read(unit/'group/completed.json');cfg=policy(ROOT/'experiments/E023-adaptive-density-bins/config.json')
    require(record['status']=='SUCCESS'and record['config']==cfg and record['truth_accessed']is False
            and record['features_sha256']==binding(features)['sha256'],'New grouping policy/input differs')
    data,meta=load(features);ids=data['ids'].tolist();all_work=read(inventory)['all_work_members'];clean=set(read(marker_clean)['clean'])
    output.mkdir(parents=True,exist_ok=False)
    result=dict(status='SUCCESS',dataset=dataset,admission=admitted,arms={},primary_rule_unchanged=True,
                geometry_scope='Preserved fixed native learned 5-NN, not new adaptive-density candidate geometry')
    if dataset=='E009':
        lock=read(ROOT/'experiments/E013-marker-quality/review-lock.json');truth_path=verify_truth(lock)
        truth=read(truth_path/'truth.json');targets=read(truth_path/'targets.json');pop=read(ROOT/lock['population_path'])
        require(ids==truth['ordered_contig_ids'],'E009 complete truth axis differs')
    else:
        lab,quarantine,shared,genomes,truth=oral_labels(truth_root,ids,data['lengths'])
        require(not meta['samples']and meta['fasta_sha256']==truth['model_input']['sha256'],'Oral sequence-only DNA differs')
    for arm in ['density','selected']:
        path=unit/'group'/(arm+'-partition.json');part=validate_partition(data,path,features)
        require(binding(path)==all_work['units/'+unit.name+'/group/'+path.name], 'New partition archive binding differs')
        manifest=read(unit/'export'/arm/'manifest.json')
        manifest_bindings(manifest,'units/'+unit.name+'/export/'+arm,all_work)
        rows,contract=export_contract(part,data,unit/'export'/arm)
        assignments={q:(b if b>=0 else None)for q,b in zip(ids,part['assignment'])}
        if dataset=='E009':
            metrics=diagnostics(truth,rows,part,pop,targets)
            grouped=grouping_diagnostics(truth,rows,pop,targets,clean)
            require(grouped['recovery']==metrics['recovery'],'Frozen primary recovery readers disagree')
            secondary=summarize(({**truth['contigs'][q],'id':q}for q in ids),assignments,
                                truth['reference_axis'],targets['genome_lengths'],targets['targets'])
            value=dict(diagnostics=metrics,grouping=grouped,populations=population_cells(rows,truth,pop,clean),secondary=secondary)
        else:
            evaluated=evaluate(truth_root,path,output/('truth-'+arm))
            refs=truth['references'];lengths=Counter()
            for ref in refs.values():lengths[ref['genome']]+=ref['length']
            secondary={mode:summarize(oral_secondary_rows(Path(truth_root)/'rows.jsonl.gz',refs,masked),assignments,refs,lengths,truth['targets'])
                       for mode,masked in [('provided_origin',False),('known_shared_sensitivity',True)]}
            value=dict(evaluation=evaluated,grouping=oral_population(part,data,lab,quarantine,shared,genomes,truth['targets'],clean),secondary=secondary)
        value['export_contract']=contract;result['arms'][arm]=value
        tables={'sequence':value['secondary']}if dataset=='E009'else value['secondary']
        for mode,table in tables.items():
            with (output/('bin-quality-'+arm+'-'+mode+'.tsv')).open('x')as f:
                fields=['bin_id','bp','dominant_origin','target','full_reference_bp','source_union_bp',
                        'completeness','confirmed_purity','impurity_upper_bound','confirmed_other_origin_bp',
                        'confirmed_other_origin_fraction','unconfirmed_bp','unresolved_fraction','tier']
                writer=csv.DictWriter(f,fieldnames=fields,delimiter='\t',lineterminator='\n')
                writer.writeheader();writer.writerows(table['bins'])
        del part,rows,assignments
    (output/'review.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    return result


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for k in ['unit','features','inventory','admission','output','marker-clean','truth-root']:p.add_argument('--'+k,type=Path,required=True)
    p.add_argument('--dataset',choices=['E009','oral'],required=True);a=p.parse_args()
    review(a.unit,a.features,a.inventory,a.admission,a.output,a.dataset,a.marker_clean,a.truth_root)
