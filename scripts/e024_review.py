#!/usr/bin/env python3
"""Inspect only new E024 outputs with frozen Oral provided-origin diagnostics.

No cloud/science command is reachable. Independent shutdown, archive/member and
finance admission precede evaluation. Complete original DNA/full references,
known-shared sensitivity and secondary conservative impurity tiers are retained.
E023/E019 and older summaries are read as immutable baselines, never rescored.
"""
from collections import Counter
import csv
import json
from pathlib import Path
import sys

ROOT=Path(__file__).absolute().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'scripts')]
from e014_review import read,require,binding,manifest_bindings,oral_labels,oral_population
from e017_review import export_contract
from e022_review import admission_contract
from e023_review import oral_secondary_rows


def disposition(r95,at50,at90,neighbor_gain):
    """Apply the prospectively frozen practical rule; never change a bin or threshold."""
    if r95>=.06507729606498985+.005 and at50>=43 and at90>=33:
        return 'KEEP'
    if r95<=.04093190555264913 and at90<=10 and neighbor_gain<=0:
        return 'ABANDON_THIS_FROZEN_RETRIEVAL_POLICY'
    return 'MODIFY'


def contracts(work,inventory,admission):
    """Refuse missing native/source/full-axis proofs before any truth is opened."""
    import numpy as np
    from dl_binner.multiview.views import load
    from dl_binner.density.grouping import policy
    admitted=admission_contract(admission);work=Path(work)
    require(read(work/'audited/done.json')['proof']['status']=='PASS','Native new-output audit missing')
    record=read(work/'group/completed.json')
    require(record['status']=='SUCCESS' and record['cfg']==policy(ROOT/'experiments/E023-adaptive-density-bins/config.json')
            and record['truth_accessed'] is False and record['encoder_changed'] is False,
            'Native fixed grouping/source contract differs')
    features=work/'rebound/features.npz';data,meta=load(features)
    require(meta['samples']==[f'oral_sample_{s}' for s in [6,7,8,13,14,15,16,17,18,19]]
            and data['depth'].shape[1]==10 and np.isfinite(data['depth']).all(),
            'Measured ordered ten-depth features required')
    all_work=read(inventory)['all_work_members']
    require(record['rebind']==binding(work/'rebound/rebind.json')
            and binding(features)==all_work['rebound/features.npz'],'Rebind/new feature archive bytes differ')
    return admitted,data,meta,all_work


def review(work,inventory,admission,marker_clean,truth_root,output):
    """Evaluate new partitions only; bind all exports and full provided denominators."""
    import numpy as np
    from threadpoolctl import threadpool_limits
    from dl_binner.information.export import validate_partition
    from dl_binner.density.bin_quality import summarize
    from dl_binner.multiview.arrays import load_arrays
    from e014_oral_truth import evaluate
    threadpool_limits(4)
    admitted,data,meta,all_work=contracts(work,inventory,admission)
    work,output=Path(work),Path(output);ids=data['ids'].tolist()
    lab,quarantine,shared,genomes,truth=oral_labels(truth_root,ids,data['lengths'])
    require(len(truth['targets'])==799 and sum(truth['targets'].values())==2083072211
            and meta['fasta_sha256']==truth['model_input']['sha256'],
            'Full admitted Oral DNA/reference denominator differs')
    clean=set(read(marker_clean)['clean'])
    protocol=read(ROOT/'experiments/E024-oral-measured-coverage/protocol.json')
    for name,wanted in protocol['baseline_summaries'].items():
        require(binding(ROOT/name)==wanted,'Retained baseline summary changed')
    output.mkdir(parents=True,exist_ok=False)
    result=dict(status='SUCCESS',dataset='oral_provided_origin_oracle',admission=admitted,arms={},
                geometry_scope='Partition display neighbors are unchanged E019 native geometry; new composite neighbors are separately named',
                primary_rule_unchanged=True)
    h,_=load_arrays(work/'group/hierarchy.npz','E024_depth_hierarchy')
    # Compare precisely the fixed eligible-attributable query population used
    # by the retained E023 cached-neighbor review. This is not new search.
    result['new_composite_neighbors']=neighbor_summary(h,lab,data['lengths'])
    del h
    refs=truth['references'];lengths=Counter()
    for ref in refs.values():lengths[ref['genome']]+=ref['length']
    for arm in ['density','selected']:
        path=work/'group'/(arm+'-partition.json');part=validate_partition(data,path,work/'rebound/features.npz')
        require(binding(path)==all_work['group/'+path.name],'New partition archive binding differs')
        manifest=read(work/'export'/arm/'manifest.json')
        manifest_bindings(manifest,'export/'+arm,all_work)
        rows,contract=export_contract(part,data,work/'export'/arm)
        assignments={q:(b if b>=0 else None) for q,b in zip(ids,part['assignment'])}
        evaluated=evaluate(truth_root,path,output/('truth-'+arm))
        secondary={mode:summarize(oral_secondary_rows(Path(truth_root)/'rows.jsonl.gz',refs,masked),assignments,refs,lengths,truth['targets'])
                   for mode,masked in [('provided_origin',False),('known_shared_sensitivity',True)]}
        value=dict(evaluation=evaluated,grouping=oral_population(part,data,lab,quarantine,shared,genomes,truth['targets'],clean),
                   secondary=secondary,export_contract=contract,
                   measured_depth_population=coverage_populations(data,part,lab,genomes,truth['targets'],clean))
        for mode,table in secondary.items():
            with (output/('bin-quality-'+arm+'-'+mode+'.tsv')).open('x') as f:
                fields=['bin_id','bp','dominant_origin','target','full_reference_bp','source_union_bp','completeness',
                        'confirmed_purity','impurity_upper_bound','confirmed_other_origin_bp','confirmed_other_origin_fraction',
                        'unconfirmed_bp','unresolved_fraction','tier']
                writer=csv.DictWriter(f,fieldnames=fields,delimiter='\t',lineterminator='\n')
                writer.writeheader();writer.writerows(table['bins'])
        result['arms'][arm]=value
        del part,rows,assignments
    old=read(ROOT/'experiments/E023-adaptive-density-bins/comparison-review.json')
    previous=old['cached_neighbor_diagnostic']['oral-E019']['new_composite']
    new=result['new_composite_neighbors']
    require(new['queries']==previous['queries'] and new['bp']==previous['query_bp'],
            'Changed composite-neighbor query population; no paired claim')
    summary=result['arms']['selected']['evaluation']['origin']['recovery_summary']
    gain=new['same_origin_bp_weighted']-previous['nn_purity_bp_weighted']
    result['frozen_disposition']=disposition(summary['bp_weighted_R95'],summary['at_least_50_percent'],
                                            summary['at_least_90_percent'],gain)
    result['matched_composite_neighbor_gain']=gain
    with (ROOT/'experiments/E023-adaptive-density-bins/comparison-targets.tsv').open() as f:
        previous_targets={r['genome']:r for r in csv.DictReader(f,delimiter='\t') if r['dataset']=='oral'}
    require(set(previous_targets)==set(truth['targets']),'Retained full target table differs')
    density={r['genome']:r for r in result['arms']['density']['evaluation']['origin']['recovery']}
    with (output/'comparison-targets.tsv').open('x') as f:
        fields=['genome','reference_bp','retained_E019_bp','retained_E023_bp','new_density_bp','new_selected_bp',
                'delta_vs_E023_bp','delta_vs_E019_bp','new_marker_effect_bp']
        writer=csv.DictWriter(f,fieldnames=fields,delimiter='\t',lineterminator='\n');writer.writeheader()
        for row in result['arms']['selected']['evaluation']['origin']['recovery']:
            g=row['genome'];before=previous_targets[g]
            require(int(before['reference_bp'])==row['reference_bp'],'Target reference denominator changed')
            n=row['recovered_bp'];d=density[g]['recovered_bp'];e23=int(before['selected_bp']);e19=int(before['baseline_bp'])
            writer.writerow(dict(genome=g,reference_bp=row['reference_bp'],retained_E019_bp=e19,retained_E023_bp=e23,
                                 new_density_bp=d,new_selected_bp=n,delta_vs_E023_bp=n-e23,
                                 delta_vs_E019_bp=n-e19,new_marker_effect_bp=n-d))
    with (output/'review.json').open('x') as f:json.dump(result,f,indent=2,allow_nan=False);f.write('\n')
    return result


def neighbor_summary(h,labels,lengths):
    """Read cached local-row indices against compact origin labels, including unknown neighbors."""
    successes=weighted=weight=queries=0
    for i,row in enumerate(h['selected']):
        source=int(labels[row])
        if source<0:continue
        near=h['selected'][h['neighbors'][i,:5]]
        value=sum(int(labels[j])==source for j in near)/len(near) if len(near) else 0.
        queries+=1;successes+=value;weighted+=value*int(lengths[row]);weight+=int(lengths[row])
    return dict(queries=queries,bp=weight,same_origin_mean=successes/queries if queries else None,
                same_origin_bp_weighted=weighted/weight if weight else None,
                meaning='Provided origin, not exhaustive unique-source support; fixed eligible attributable queries, unknown neighbors remain in denominator')


def coverage_populations(data,part,labels,genomes,targets,clean):
    """Account measured zeros with complete length/origin/eligibility/marker/status strata."""
    import numpy as np
    from collections import defaultdict
    zero=(data['depth']==0).all(1)
    cells=defaultdict(lambda:dict(contigs=0,bp=0))
    for i,q in enumerate(part['ids']):
        n=int(data['lengths'][i]);g=int(labels[i]);eligible=bool(data['eligible'][i])
        origin='unknown' if g<0 else 'target' if genomes[g] in targets else 'non_target'
        length=max(v for v in [0,500,768,1000,2500,10000] if n>=v)
        status='excluded' if not eligible else 'assigned' if part['assignment'][i]>=0 else 'unassigned'
        key='|'.join([str(length),origin,'eligible' if eligible else 'excluded',status,
                      'clean_marker' if q in clean else 'no_clean_marker','measured_all_zero' if zero[i] else 'measured_positive'])
        cells[key]['contigs']+=1;cells[key]['bp']+=n
    require(sum(c['contigs'] for c in cells.values())==len(part['ids'])
            and sum(c['bp'] for c in cells.values())==int(data['lengths'].sum()),'Measured zero cross-population accounting differs')
    return dict(cells=dict(cells),all_zero_contigs=int(zero.sum()),all_zero_bp=int(data['lengths'][zero].sum()),
                zero_cells_per_sample=(data['depth']==0).sum(0).tolist(),missing_cells=0,
                semantics='Measured full-parent means; all-zero differs from missing; no per-base/window variance')


if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser(description=__doc__)
    for k in ['work','inventory','admission','marker-clean','truth-root','output']:p.add_argument('--'+k,type=Path,required=True)
    a=p.parse_args();review(a.work,a.inventory,a.admission,a.marker_clean,a.truth_root,a.output)
