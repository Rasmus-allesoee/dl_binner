#!/usr/bin/env python3
"""Evaluate new E030 partitions with admitted, unchanged sequence-truth readers.

No fitting, inference, new neighbors, selection or threshold changes occur.
Sparse arrays supply a lazy, explicitly named joint-score 5-NN diagnostic view;
this never substitutes for or rewrites retained native learned geometry.
"""
import argparse
from collections import Counter
import csv
import gc
import json
from pathlib import Path
import sys

ROOT=Path(__file__).absolute().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
# Pin the actual installed wheel before legacy review helpers add checkout paths.
from e030_control import product_scope
if __name__=='__main__':product_scope()
from e024_coverage import binding,write
from e027_inspection import read,require


def profile_contract(group,features,data,inventory,prefix,reuse_lock=None):
    """Read actual new numeric profiles, immutable reuse bindings and all result bytes."""
    import numpy as np
    from dl_binner.calibrated.arrays import load
    group=Path(group);record=read(group/'completed.json')
    from dl_binner.construction.grouping import policy
    require(record['status']=='SUCCESS' and record['truth_accessed'] is False and record['config']==policy() and
        record['input_sha256']['features']==binding(features)['sha256'],'New construction feature/source differs')
    for name,wanted in record['files'].items():
        require(inventory[prefix+'/'+name]==wanted,'New result inventory differs')
        if (group/name).exists():require(binding(group/name)==wanted,'Staged result bytes differ')
    a,m=load(group/'candidate-profiles.npz','supported_candidate_profiles',data['ids'])
    n=len(a['nodes'])
    require(a['nodes'].dtype.kind in 'iu' and a['nodes'].shape==(n,) and len(set(a['nodes'].tolist()))==n
        and a['composition_mean'].shape==(n,136) and a['depth_mean'].ndim==2 and a['depth_mean'].shape[0]==n
        and a['support'].shape==(n,2) and np.isfinite(a['support']).all()
        and ((a['support']>=0)&(a['support']<=1)).all()
        and all(np.isfinite(v).all() for v in a.values()),'New profile numeric axes differ')
    require(m['calibration']==read(group/'profile-calibration.json'),'Profile calibration differs')
    reuse=read(group/'accepted-reuse.json');old=reuse_lock if reuse_lock is not None else read(ROOT/'experiments/E030-supported-biological-bins/reuse-lock.json')
    accepted_prefix=prefix+'/'
    require(all(old['accepted_members'][accepted_prefix+k]==v for k,v in reuse['files'].items()),'Accepted neighbors/forests altered')
    require(record['accepted']==old['accepted_members'][accepted_prefix+'completed.json'],'Accepted result binding differs')
    return dict(status='PASS_ACTUAL_NEW_NUMERIC_PROFILE_READER',rows=len(data['ids']),candidates=n,
        full_bp=int(data['lengths'].sum()),features=binding(features),retained_native_choices_and_updates_reproduced=True,
        no_neighbor_or_MST_or_learning_repeated=True,calibration=m['calibration'])


def review(base,staged,unit,role,output):
    """Evaluate one teacher/student pair of parent/post exports; reuse old summaries only."""
    import numpy as np
    from threadpoolctl import threadpool_limits
    from dl_binner.multiview.views import load
    from dl_binner.information.export import validate_partition
    from dl_binner.density.bin_quality import summarize
    from e022_review import admission_contract
    from e014_review import manifest_bindings,diagnostics,grouping_diagnostics,population_cells,oral_labels,oral_population
    from e017_review import export_contract
    from e023_review import oral_secondary_rows
    from e025_review import coverage_populations
    from e012_marker_audit import verify_truth
    from e014_oral_truth import evaluate
    threadpool_limits(4);base=Path(base);stage=Path(staged);output=Path(output)
    require(unit in ['E009-noGLM','E009-GLM','oral-noGLM']and role in ['teacher','student'],'Unfrozen review arm')
    admitted=admission_contract(base/'admission.json');inv=read(base/'inventory.json')['all_work_members']
    paths=dict(E009=ROOT/'artifacts/e011-cached-grouping-reference/restore-local/candidate/features/features.npz',
        oral=ROOT/'artifacts/e024-inspection/20261028T193107Z/verified/work/rebound/features.npz')
    dataset='E009'if unit.startswith('E009')else'oral';features=paths[dataset]
    data,meta=load(features);ids=data['ids'].tolist();axis=admitted['axes'][unit]
    require(len(ids)==axis['rows'] and int(data['lengths'].sum())==axis['bp']
            and int(data['eligible'].sum())==axis['eligible'] and meta['samples']==axis['samples']
            and data['depth'].shape==(len(ids),10) and np.isfinite(data['depth']).all(),
            'Independent feature/source/ordered ten-depth axes differ')
    prefix='groups/'+unit+'/'+role+'/result';group=stage/'work'/prefix
    numeric=profile_contract(group,features,data,inv,prefix)
    marker=ROOT/('artifacts/e022-inspection/20261026/verified/work/units/E009-relational/refine/quality-evidence.json'
        if dataset=='E009'else'artifacts/e019-window-context/review-20261023/verified/work/units/oral-context/refine/quality-evidence.json')
    require(binding(marker)['sha256']==read(group/'completed.json')['input_sha256']['evidence'],'Cached marker evidence differs')
    clean_path=ROOT/('artifacts/e011-cached-grouping-reference/restore-local/candidate/markers/evidence.json'
        if dataset=='E009'else'artifacts/e014-multiview-reconstruction/inspection-20261019/oral-marker-review.json')
    clean=set(read(clean_path)['clean'])
    clean_binding=(read(ROOT/'experiments/E022-marker-informed-learning/reuse-lock.json')['files']
        if dataset=='E009'else None)
    if clean_binding:
        candidates=[v for k,v in clean_binding.items()if k.endswith('/candidate/markers/evidence.json')]
        require(len(candidates)==1 and binding(clean_path)==candidates[0],'Clean-marker strata source differs')
    else:
        require(binding(clean_path)==read(ROOT/'experiments/E014-multiview-reconstruction/comparison-review.json')['evidence'][str(clean_path.relative_to(ROOT))],
                'Retained Oral clean-marker review differs')
    result=dict(status='SUCCESS',unit=unit,role=role,numeric_contract=numeric,arms={},
        features=binding(features),marker_evidence=binding(marker),marker_clean=binding(clean_path),
        geometry_scope='Identical E029 joint-score geometry reused as admitted summaries; no new geometry calculation',
        original_Mac_portability_tolerance_unchanged=True,primary_rule_unchanged=True)
    output.mkdir(parents=True,exist_ok=False)
    if dataset=='E009':
        lock=read(ROOT/'experiments/E013-marker-quality/review-lock.json');source=verify_truth(lock)
        truth=read(source/'truth.json');targets=read(source/'targets.json');pop=read(ROOT/lock['population_path'])
        require(ids==truth['ordered_contig_ids']and len(targets['targets'])==156
                and sum(targets['genome_lengths'][g]for g in targets['targets'])==554661890,'E009 truth/denominator differs')
    else:
        truth_root=ROOT/'artifacts/e014-multiview-reconstruction/oral-truth-origin-v1'
        lab,quarantine,shared,genomes,truth=oral_labels(truth_root,ids,data['lengths'])
        require(len(truth['targets'])==799 and sum(truth['targets'].values())==2083072211
                and meta['fasta_sha256']==truth['model_input']['sha256'],'Oral full-reference/source truth differs')
    old_path=ROOT/('artifacts/e029-certifiable-joint-retrieval/inspection/review-'+unit+'-'+role)/'review.json'
    old_review=read(old_path);old_lock=read(ROOT/'experiments/E029-certifiable-joint-retrieval/review-lock.json')
    require(binding(old_path)==old_lock['files'][str(old_path.relative_to(ROOT))] and old_review['features']==binding(features),
        'Retained E029 geometry summary/input binding differs')
    result['retained_geometry']=(old_review['arms']['post']['diagnostics']['geometry'] if dataset=='E009' else old_review['arms']['post']['grouping']['geometry'])
    result['retained_geometry_binding']=binding(old_path)
    # No empty-neighbor value is reported as a measurement. This adapter supplies
    # only population/grouping bookkeeping; geometry is reused separately above.
    neighbors=[[]]*len(ids)
    for arm in ['root-only','pre','post']:
        path=group/(arm+'-partition.json');part=validate_partition(data,path,features)
        require(binding(path)==inv[prefix+'/'+path.name],'Partition original bytes differ')
        export_prefix=unit+'/export/'+role+'-'+arm;folder=stage/'work'/export_prefix
        manifest_bindings(read(folder/'manifest.json'),export_prefix,inv)
        rows,account=export_contract(part,data,folder);part['neighbors']=neighbors
        assignments={q:b if b>=0 else None for q,b in zip(ids,part['assignment'])}
        if dataset=='E009':
            grouped=grouping_diagnostics(truth,rows,pop,targets,clean)
            primary={k:grouped[k] for k in ['recovery','recovery_summary','restricted_B3']}
            secondary={'conservative_sequence':summarize(({**truth['contigs'][q],'id':q}for q in ids),
                assignments,truth['reference_axis'],targets['genome_lengths'],targets['targets'])}
            value=dict(diagnostics=primary,grouping=grouped,populations=population_cells(rows,truth,pop,clean),secondary=secondary)
        else:
            evaluated=evaluate(truth_root,path,output/('truth-'+arm));refs=truth['references'];lengths=Counter()
            for ref in refs.values():lengths[ref['genome']]+=ref['length']
            secondary={mode:summarize(oral_secondary_rows(truth_root/'rows.jsonl.gz',refs,masked),assignments,refs,lengths,truth['targets'])
                       for mode,masked in [('provided_origin',False),('known_shared_sensitivity',True)]}
            grouped=oral_population(part,data,lab,quarantine,shared,genomes,truth['targets'],clean)
            grouped.pop('geometry')
            value=dict(evaluation=evaluated,grouping=grouped,
                measured_depth_population=coverage_populations(data,part,lab,genomes,truth['targets'],clean),secondary=secondary)
        value['export_contract']=account;value['partition']=binding(path);result['arms'][arm]=value
        for mode,table in secondary.items():
            with (output/('bin-quality-'+arm+'-'+mode+'.tsv')).open('x')as stream:
                writer=csv.DictWriter(stream,fieldnames=list(table['bins'][0])if table['bins']else['bin_id'],delimiter='\t',lineterminator='\n')
                writer.writeheader();writer.writerows(table['bins'])
        # Keep compact results, not full temporary query-row dictionaries.
        del part,rows,assignments;gc.collect()
        write(output/('review-through-'+arm+'.json'),result)
        summary=value['diagnostics']['recovery_summary']if dataset=='E009'else value['evaluation']['origin']['recovery_summary']
        print(unit,role,arm,json.dumps(summary),flush=True)
    write(output/'review.json',result);return result


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for name in ['base','staged','output']:p.add_argument('--'+name,type=Path,required=True)
    p.add_argument('--unit',required=True);p.add_argument('--role',choices=['teacher','student'],required=True)
    a=p.parse_args();review(a.base,a.staged,a.unit,a.role,a.output)
