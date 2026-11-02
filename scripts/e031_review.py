#!/usr/bin/env python3
"""Frozen new-output E031 diagnostics after independent shutdown/byte/cost admission.

The E009 GLM E023 bridge actor is accepted reuse and is never rescored. Original
evaluators, provided-reference denominators, quarantine and secondary tiers are
unchanged. This module has no training, grouping, selection or cloud entry point.
"""
import argparse
from collections import Counter
import csv
import gc
import json
from pathlib import Path
import sys

ROOT=Path(__file__).absolute().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from e031_control import product_scope,UNITS
from e024_coverage import binding,write


def contract(base,staged,unit,role,features,comparison,engineering=False):
    """Read actual actor/partition/export contracts without looking at truth."""
    product_scope()
    from e022_review import admission_contract
    from dl_binner.information.export import validate_partition
    from dl_binner.multiview.views import load
    from e014_review import manifest_bindings
    base,staged=Path(base),Path(staged)
    if unit not in UNITS or role not in ['teacher','student'] or comparison not in ['bridge','learning','learning-E023']:
        raise ValueError('Unknown E031 review actor')
    if comparison=='bridge' and (unit,role)==('E009-GLM','student'):
        raise ValueError('Accepted E023 actor: reuse its bound summary, do not rescore')
    if comparison.startswith('learning') and role!='student':raise ValueError('No new teacher output to score')
    admission=admission_contract(base/'admission.json')
    if admission.get('exact_source_schedule_axes_verified') is not True:raise ValueError('Independent exact source/schedule/axes admission required')
    inv=json.loads((base/'inventory.json').read_text())['all_work_members']
    data,meta=load(features)
    axis=dict(rows=len(data['ids']),bp=int(data['lengths'].sum()),eligible=int(data['eligible'].sum()),samples=meta['samples'])
    if not engineering:
        expected=json.loads((ROOT/'experiments/E031-bootstrap-preserving-learning/reuse-lock.json').read_text())['axes'][unit]
        if axis!=expected:raise ValueError('Full contig/ordered ten-depth source axis differs')
    elif axis['rows']>128 or axis['bp']>1_000_000:raise ValueError('Tiny review fixture exceeded')
    density=comparison in ['bridge','learning-E023']
    prefix='actors/'+unit+'/'+role+'/science' if comparison=='bridge' else unit+'/e023/science' if density else unit
    group=staged/'work'/prefix/('result' if density else 'construct/result')
    export_prefix=prefix+'/export';root=staged/'work'/export_prefix
    complete=json.loads((group/'completed.json').read_text())
    if complete['status']!='SUCCESS' or complete['truth_accessed'] is not False:raise ValueError('New scientific completion absent')
    feature_sha=complete.get('features_sha256',complete.get('input_sha256',{}).get('features'))
    if feature_sha!=binding(features)['sha256']:raise ValueError('New feature bytes differ')
    if density:
        from dl_binner.density.grouping import policy
        if complete['config']!=policy(ROOT/'experiments/E023-adaptive-density-bins/config.json'):raise ValueError('E023 policy differs')
        proof=json.loads((staged/'work'/prefix/'bridge.json').read_text())
        if proof['audit']['status']!='PASS' or proof['accepted_science_reused'] is not False:raise ValueError('New actor native cached audit missing')
        arms=['density','selected']
    else:
        from dl_binner.construction.grouping import policy
        if complete['config']!=policy():raise ValueError('Fixed E030 downstream policy differs')
        proof=json.loads((staged/'work'/unit/'audit/proof.json').read_text())
        if proof['status']!='PASS':raise ValueError('Native new learning construction audit missing')
        arms=['root-only','pre','post']
    group_prefix=str(group.relative_to(staged/'work'))
    for p in [group/'completed.json',staged/'work'/prefix/'bridge.json' if density else staged/'work'/unit/'audit/proof.json']:
        if binding(p)!=inv[str(p.relative_to(staged/'work'))]:raise ValueError('Native completion/audit inventory bytes differ')
    for arm in arms:
        p=group/(arm+'-partition.json');validate_partition(data,p,features)
        if binding(p)!=inv[group_prefix+'/'+p.name]:raise ValueError('New partition member bytes differ')
        manifest_bindings(json.loads((root/arm/'manifest.json').read_text()),export_prefix+'/'+arm,inv)
    return data,meta,group,root,arms,dict(status='PASS',comparison=comparison,unit=unit,role=role,
        axis=axis,features=binding(features),native_numeric_audit_verified=True,
        independent_archive_admission=admission,local_model_inference=False,
        original_Mac_portability_tolerance_unchanged=True)


def review(base,staged,unit,role,features,comparison,marker_clean,truth_root,output):
    """Evaluate only new partitions, sequentially, through the unchanged truth readers."""
    data,meta,group,export_root,arms,proof=contract(base,staged,unit,role,features,comparison)
    lock=json.loads((ROOT/'experiments/E031-bootstrap-preserving-learning/review-lock.json').read_text())
    for name,wanted in lock['files'].items():
        if binding(ROOT/name)!=wanted:raise ValueError('Frozen truth/retained-summary source bytes differ: '+name)
    from threadpoolctl import threadpool_limits
    from dl_binner.density.bin_quality import summarize
    from e012_marker_audit import verify_truth
    from e014_review import grouping_diagnostics,population_cells,oral_labels,oral_population
    from e014_oral_truth import evaluate
    from e017_review import export_contract
    from e023_review import oral_secondary_rows
    from e025_review import coverage_populations
    threadpool_limits(4);output=Path(output);output.mkdir(parents=True,exist_ok=False)
    dataset='E009' if unit.startswith('E009') else 'oral';ids=data['ids'].tolist()
    clean=set(json.loads(Path(marker_clean).read_text())['clean'])
    if dataset=='E009':
        old=json.loads((ROOT/'experiments/E022-marker-informed-learning/reuse-lock.json').read_text())['files']
        expected=[v for n,v in old.items() if n.endswith('/candidate/markers/evidence.json')]
        if len(expected)!=1 or binding(marker_clean)!=expected[0]:raise ValueError('Frozen clean-marker strata bytes differ')
    else:
        old=json.loads((ROOT/'experiments/E014-multiview-reconstruction/comparison-review.json').read_text())['evidence']
        expected=old['artifacts/e014-multiview-reconstruction/inspection-20261019/oral-marker-review.json']
        if binding(marker_clean)!=expected:raise ValueError('Frozen Oral marker strata bytes differ')
    result=dict(contract=proof,arms={},dataset=dataset,baselines_rescored=False,
        geometry_scope='Native E023/native learned compact query view is separate; no inference or changed search',
        full_DNA_populations_preserved=True,primary_rule_unchanged=True,secondary_not_formal_MIMAG_HQ=True)
    if dataset=='E009':
        lock=json.loads((ROOT/'experiments/E013-marker-quality/review-lock.json').read_text());truth_path=verify_truth(lock)
        truth=json.loads((truth_path/'truth.json').read_text());targets=json.loads((truth_path/'targets.json').read_text())
        pop=json.loads((ROOT/lock['population_path']).read_text())
        if ids!=truth['ordered_contig_ids'] or len(targets['targets'])!=156 or sum(targets['genome_lengths'][g] for g in targets['targets'])!=554661890:
            raise ValueError('Conservative v2/full reference denominator differs')
    else:
        lab,quarantine,shared,genomes,truth=oral_labels(truth_root,ids,data['lengths'])
        if len(truth['targets'])!=799 or sum(truth['targets'].values())!=2083072211 or meta['fasta_sha256']!=truth['model_input']['sha256']:
            raise ValueError('Oral provided-origin/full reference denominator differs')
    for arm in arms:
        path=group/(arm+'-partition.json');part=json.loads(path.read_text());rows,account=export_contract(part,data,export_root/arm)
        assignments={q:b if b>=0 else None for q,b in zip(ids,part['assignment'])}
        if dataset=='E009':
            grouped=grouping_diagnostics(truth,rows,pop,targets,clean)
            secondary={'conservative_sequence':summarize(({**truth['contigs'][q],'id':q} for q in ids),assignments,
                truth['reference_axis'],targets['genome_lengths'],targets['targets'])}
            value=dict(grouping=grouped,populations=population_cells(rows,truth,pop,clean),secondary=secondary)
        else:
            evaluated=evaluate(truth_root,path,output/('truth-'+arm));refs=truth['references'];lengths=Counter()
            for ref in refs.values():lengths[ref['genome']]+=ref['length']
            secondary={mode:summarize(oral_secondary_rows(Path(truth_root)/'rows.jsonl.gz',refs,masked),assignments,refs,lengths,truth['targets'])
                       for mode,masked in [('provided_origin',False),('known_shared_sensitivity',True)]}
            # Empty display neighbors avoid claiming new native learned geometry;
            # its actual compact cache reader is a separately named diagnostic.
            part['neighbors']=[[]]*len(ids)
            grouped=oral_population(part,data,lab,quarantine,shared,genomes,truth['targets'],clean);grouped.pop('geometry')
            value=dict(evaluation=evaluated,grouping=grouped,secondary=secondary,
                       measured_depth_population=coverage_populations(data,part,lab,genomes,truth['targets'],clean))
        value.update(export_contract=account,partition=binding(path));result['arms'][arm]=value
        for name,table in secondary.items():
            with (output/('bin-quality-'+arm+'-'+name+'.tsv')).open('x') as stream:
                writer=csv.DictWriter(stream,fieldnames=list(table['bins'][0]) if table['bins'] else ['bin_id'],delimiter='\t',lineterminator='\n')
                writer.writeheader();writer.writerows(table['bins'])
        del rows,part,assignments;gc.collect();write(output/('review-through-'+arm+'.json'),result)
    write(output/'review.json',result);return result


if __name__=='__main__':
    a=argparse.ArgumentParser(description=__doc__)
    for key in ['base','staged','features','marker-clean','truth-root','output']:a.add_argument('--'+key,type=Path,required=True)
    a.add_argument('--unit',choices=UNITS,required=True);a.add_argument('--role',choices=['teacher','student'],required=True)
    a.add_argument('--comparison',choices=['bridge','learning','learning-E023'],required=True);v=a.parse_args()
    review(v.base,v.staged,v.unit,v.role,v.features,v.comparison,v.marker_clean,v.truth_root,v.output)
