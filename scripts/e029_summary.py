#!/usr/bin/env python3
"""Summarize only admitted E029 diagnostics and reuse frozen reference tables.

Applies the original KEEP/MODIFY/ABANDON rule without bin selection or scoring.
Writes complete per-target comparisons and compact result/provenance records.
"""
import argparse
from collections import Counter
import csv
from datetime import datetime,timezone
import json
from pathlib import Path
import sys

ROOT=Path(__file__).absolute().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from e024_coverage import binding,write
from e027_inspection import read,require


def changed(before,after):
    """Compare existing duplicate-safe target unions without rescoring either arm."""
    require(before.keys()==after.keys(),'Target populations differ')
    delta={g:after[g]-before[g]for g in before}
    return dict(gains=sum(v>0 for v in delta.values()),losses=sum(v<0 for v in delta.values()),
        unchanged=sum(v==0 for v in delta.values()),net_recovered_bp=sum(delta.values()),
        largest_gains=sorted(((g,v)for g,v in delta.items()if v>0),key=lambda x:(-x[1],x[0]))[:10],
        largest_losses=sorted(((g,v)for g,v in delta.items()if v<0),key=lambda x:(x[1],x[0]))[:10])


def disposition(metrics,protocol):
    """Apply the pre-outcome primary-arm rule, preserving all failed criteria."""
    pairs=[(metrics['E009-GLM'],protocol['anchors']['E009_E023'],protocol['keep']['E009_GLM_R95_gain_over_E023']),
           (metrics['oral-noGLM'],protocol['anchors']['oral_E026'],protocol['keep']['oral_noGLM_R95_gain_over_E026'])]
    keep=all(m['bp_weighted_R95']>=a['R95']+gain and m['at_least_50_percent']>=a['target50']
             and m['at_least_90_percent']>=a['target90']for m,a,gain in pairs)
    improve=any(m['bp_weighted_R95']>a['R95']or m['at_least_50_percent']>a['target50']
                or m['at_least_90_percent']>a['target90']for m,a,gain in pairs)
    return 'KEEP'if keep else'MODIFY'if improve else'ABANDON_THIS_FROZEN_BUNDLE'


def summarize(base,output):
    """Refuse incomplete reviews; expose all six roles and full target denominators."""
    base=Path(base).absolute();output=Path(output).absolute();protocol=read(output/'protocol.json')
    admission=read(base/'admission-final.json');require(admission['workflow_completed'],'Unadmitted workflow')
    with (ROOT/'experiments/E023-adaptive-density-bins/comparison-targets.tsv').open()as f:
        e023={r['genome']:r for r in csv.DictReader(f,delimiter='\t')if r['dataset']=='E009'}
    with (ROOT/'experiments/E026-calibrated-evidence-fusion/comparison-targets.tsv').open()as f:
        e026={r['genome']:r for r in csv.DictReader(f,delimiter='\t')if r['dataset']=='oral'}
    with (ROOT/'experiments/E027-common-information-binner/oral-metabat2-targets.tsv').open()as f:
        oral_reference={r['genome']:r for r in csv.DictReader(f,delimiter='\t')}
    retained=dict(E009=e023,oral=e026);arms={};reviews={};target_rows=[];metrics={}
    for unit in ['E009-noGLM','E009-GLM','oral-noGLM']:
        dataset='E009'if unit.startswith('E009')else'oral';old=retained[dataset]
        for role in ['teacher','student']:
            path=base/('review-'+unit+'-'+role)/'review.json';record=read(path)
            require(record['status']=='SUCCESS'and record['unit']==unit and record['role']==role,'Incomplete review')
            reviews[str(path.relative_to(ROOT))]=binding(path);key=unit+'/'+role;values={};targets={}
            for arm,value in record['arms'].items():
                if dataset=='E009':primary=value['diagnostics'];geometry=primary['geometry']
                else:primary=value['evaluation']['origin'];geometry=value['grouping']['geometry']
                r=primary['recovery'];summary=primary['recovery_summary'];axis={x['genome']:x for x in r}
                require(axis.keys()==old.keys()and len(r)==(156 if dataset=='E009'else 799)
                    and sum(x['reference_bp']for x in r)==protocol['full_reference_bp'][dataset],
                    'Complete target denominators differ')
                require(abs(sum(x['recovered_bp']for x in r)/sum(x['reference_bp']for x in r)-summary['bp_weighted_R95'])<1e-15,
                        'Independent complete-target weighted reconstruction differs')
                require(all(int(old[g]['reference_bp'])==v['reference_bp']for g,v in axis.items()),'Reference lengths differ')
                targets[arm]={g:v['recovered_bp']for g,v in axis.items()}
                secondary={mode:{k:v for k,v in table.items()if k!='bins'}for mode,table in value['secondary'].items()}
                bins=next(iter(value['secondary'].values()))['bins']
                values[arm]=dict(primary=summary,geometry=geometry,secondary=secondary,export=value['export_contract'],
                    partition=value['partition'],bin_count=len(bins),large_bins=sum(b['bp']>=200000 for b in bins),
                    largest_bin_bp=max((b['bp']for b in bins),default=0),
                    large_below95=sum(b['bp']>=200000 and b['confirmed_purity']<.95 for b in bins),
                    joint_geometry_scope=record['geometry_scope'])
                if dataset=='E009':
                    values[arm]['geometry_by_lineage']=value['diagnostics']['geometry_by_lineage']
                    values[arm]['restricted_B3']=value['diagnostics']['restricted_B3']
                else:
                    values[arm]['known_shared_sensitivity']=value['evaluation']['known_shared_mask']['recovery_summary']
                    values[arm]['origin_B3']=value['grouping']['origin_B3']
                    values[arm]['measured_depth_population']=value['measured_depth_population']
            baseline={g:int(row['selected_bp']if dataset=='E009'else row['E026_recruited_bp'])for g,row in old.items()}
            arms[key]=dict(arms=values,paired_marker_selection=changed(targets['parent'],targets['post']),
                post_vs_frozen_anchor=changed(baseline,targets['post']))
            if role=='student':metrics[unit]=values['post']['primary']
            first=record['arms']['parent'];second=record['arms']['post']
            parent=(first['diagnostics']['recovery']if dataset=='E009'else first['evaluation']['origin']['recovery'])
            post=(second['diagnostics']['recovery']if dataset=='E009'else second['evaluation']['origin']['recovery'])
            for before,after in zip(parent,post):
                g=before['genome'];require(g==after['genome'],'Paired target ordering differs')
                target_rows.append(dict(dataset=dataset,unit=unit,role=role,genome=g,reference_bp=after['reference_bp'],
                    assembly_confirmed_bp=after['assembly_confirmed_bp'],anchor_bp=baseline[g],
                    retained_MetaBAT2_bp=int(old[g]['retained_MetaBAT_bp']if dataset=='E009'else oral_reference[g]['MetaBAT2_bp']),
                    parent_bp=before['recovered_bp'],post_bp=after['recovered_bp'],
                    marker_effect_bp=after['recovered_bp']-before['recovered_bp'],delta_vs_anchor_bp=after['recovered_bp']-baseline[g],
                    parent_best_bin='not_recovered'if before['best_bin']is None else before['best_bin'],
                    post_best_bin='not_recovered'if after['best_bin']is None else after['best_bin'],
                    post_confirmed_purity='not_applicable'if after['confirmed_purity']is None else after['confirmed_purity']))
    with (output/'comparison-targets.tsv').open('w')as f:
        writer=csv.DictWriter(f,fieldnames=list(target_rows[0]),delimiter='\t',lineterminator='\n');writer.writeheader();writer.writerows(target_rows)
    result=dict(kind='E029 frozen common-version cached comparison; completed and independently reviewed',
        checked_UTC=datetime.now(timezone.utc).isoformat(),phase=admission['phase'],science_source=admission['source'],
        status='COMPLETED_REVIEWED',frozen_disposition=disposition(metrics,protocol),
        criteria=binding(output/'protocol.json'),criteria_unchanged=True,arms=arms,
        primary_student_metrics=metrics,anchors=protocol['anchors'],
        retained_Oral_MetaBAT2=read(ROOT/'experiments/E027-common-information-binner/oral-reference-review.json')['provided_origin'],
        E009_full_path_GLM_student_R95_effect=metrics['E009-GLM']['bp_weighted_R95']-metrics['E009-noGLM']['bp_weighted_R95'],
        raw_reviews=reviews,complete_per_target_table=binding(output/'comparison-targets.tsv'),
        complete_per_target_rows=len(target_rows),old_baselines_rescored=False,scientific_fits_run=0,
        truth_policies=protocol['truth'],full_reference_bp=protocol['full_reference_bp'],
        all_DNA_unknown_non_target_short_marker_negative_excluded_unassigned_retained=True,
        secondary_not_formal_MIMAG_HQ=True,original_Mac_portability_tolerance_unchanged=True,
        native_learning_geometry='Reused accepted E027 exact native reload/exposure/unit-vector/neighborhood receipts; no new inference',
        current_joint_geometry='Separate retained joint-score top-5 population, technical recall audited independently from source homogeneity',
        limitations=['Both communities are development data; no unseen-genome, independent transfer or SOTA claim.',
            'Oral is a provided-origin oracle; known-shared sensitivity does not exhaust partial/reverse/near competitors.',
            'E009 keeps conservative v2, 7,653,205 bp / 3.3034% N quarantine and all provided denominators.',
            'GLM-on E009 includes bootstrap/proposals/student; Oral GLM qualification has no GPU model execution because capacity was unavailable.',
            'Exact Oral retrieval is an audited quadratic completion route, not a solved scalable default.',
            'Density-only and physical-marker-selected partitions are the frozen pair; this is not a new encoder causal ablation.'])
    write(output/'comparison-review.json',result);print(json.dumps(dict(disposition=result['frozen_disposition'],primary=metrics)),flush=True)
    return result


def audit_summary(output):
    """Reconstruct aggregate endpoints from every exported target row, using integers."""
    output=Path(output);result=read(output/'comparison-review.json');groups={}
    require(binding(output/'comparison-targets.tsv')==result['complete_per_target_table'],'Target table drift')
    with (output/'comparison-targets.tsv').open()as stream:
        for row in csv.DictReader(stream,delimiter='\t'):
            key=row['unit']+'/'+row['role'];groups.setdefault(key,[]).append(row)
    require(groups.keys()==result['arms'].keys(),'Missing/extra summarized component')
    for key,rows in groups.items():
        require(len({r['genome']for r in rows})==len(rows),'Duplicate target row')
        reference=sum(int(r['reference_bp'])for r in rows)
        for arm in ['parent','post']:
            records=result['arms'][key]['arms'][arm];summary=records['primary']
            recovered=[int(r[arm+'_bp'])for r in rows];denominators=[int(r['reference_bp'])for r in rows]
            require(len(rows)==summary['targets'] and abs(sum(recovered)/reference-summary['bp_weighted_R95'])<1e-15
                and sum(2*n>=d for n,d in zip(recovered,denominators))==summary['at_least_50_percent']
                and sum(10*n>=9*d for n,d in zip(recovered,denominators))==summary['at_least_90_percent'],
                'Independent integer endpoint reconstruction differs')
            account=records['export'];require(sum(v['contigs']for v in account['populations'].values())==account['contigs']
                and sum(v['bp']for v in account['populations'].values())==account['bp'],'Complete DNA totals differ')
            for table in records['secondary'].values():
                require(sum(table['counts'].values())==records['bin_count']
                        and table['assigned_bp']==account['populations']['assigned']['bp']
                        and table['query_count']==account['contigs'],'Secondary bin/status accounting differs')
    expected=disposition(result['primary_student_metrics'],read(output/'protocol.json'))
    require(expected==result['frozen_disposition'],'Frozen disposition differs')
    return dict(status='PASS_INDEPENDENT_INTEGER_TARGET_DNA_SECONDARY_AND_CRITERIA',
        target_rows=sum(len(v)for v in groups.values()),partitions=2*len(groups),old_outputs_rescored=False)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--base',type=Path);p.add_argument('--output',type=Path,required=True)
    p.add_argument('--audit',action='store_true');a=p.parse_args()
    if a.audit:print(json.dumps(audit_summary(a.output)))
    elif a.base:summarize(a.base,a.output)
    else:p.error('--base required when creating a summary')
