#!/usr/bin/env python3
"""Summarize new admitted E030 outputs beside immutable reference summaries.

No scoring, bin selection, training or cloud operation occurs. The prospective
criterion and complete integer target table are independently reconstructible.
"""
import argparse
import csv
from datetime import datetime,timezone
import json
from pathlib import Path
import sys

ROOT=Path(__file__).absolute().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from e024_coverage import binding,write
from e027_inspection import read,require
from e029_summary import changed


def disposition(metrics,protocol):
    """Apply the new prospective joint rule; no post-score thresholds or router."""
    pairs=[('E009-GLM','E009_E023'),('oral-noGLM','oral_E026')]
    improves=[];no_loss=[];anchor=[]
    for unit,name in pairs:
        m=metrics[unit];old=protocol['E029_primary_student'][unit]
        improves.append(m['bp_weighted_R95']>old['bp_weighted_R95'])
        no_loss.append(m['at_least_90_percent']>=old['at_least_90_percent'])
        anchor.append(m['bp_weighted_R95']>=protocol['anchors'][name]['R95'])
    return 'KEEP' if all(improves) and all(no_loss) and any(anchor) else 'MODIFY' if any(improves) else 'ABANDON_THIS_FROZEN_BUNDLE'


def table(path):
    """Read a frozen small TSV without rescoring its scientific output."""
    with Path(path).open() as stream:return list(csv.DictReader(stream,delimiter='\t'))


def summarize(base,output):
    """Require six complete three-arm reviews and retain every reference target."""
    base=Path(base).absolute();output=Path(output).absolute();protocol=read(output/'protocol.json')
    admission=read(base/'admission.json');require(admission['workflow_completed'],'Unadmitted native completion')
    oldrows=table(ROOT/'experiments/E029-certifiable-joint-retrieval/comparison-targets.tsv')
    old={(r['unit'],r['role'],r['genome']):r for r in oldrows}
    refs={'E009':{r['genome']:r for r in table(ROOT/'experiments/E023-adaptive-density-bins/comparison-targets.tsv') if r['dataset']=='E009'},
          'oral':{r['genome']:r for r in table(ROOT/'experiments/E026-calibrated-evidence-fusion/comparison-targets.tsv') if r['dataset']=='oral'}}
    arms={};metrics={};target_rows=[];reviews={}
    for unit in ['E009-noGLM','E009-GLM','oral-noGLM']:
        dataset='E009' if unit.startswith('E009') else 'oral'
        for role in ['teacher','student']:
            path=base/('review-'+unit+'-'+role)/'review.json';record=read(path)
            require(record['status']=='SUCCESS' and record['unit']==unit and record['role']==role
                and set(record['arms'])=={'root-only','pre','post'},'Incomplete/unknown E030 review')
            reviews[str(path.relative_to(ROOT))]=binding(path);key=unit+'/'+role;values={};targets={};raw={}
            for arm,value in record['arms'].items():
                primary=value['diagnostics'] if dataset=='E009' else value['evaluation']['origin']
                rows=primary['recovery'];summary=primary['recovery_summary'];axis={r['genome']:r for r in rows}
                require(len(rows)==len(axis)==(156 if dataset=='E009' else 799) and axis.keys()==refs[dataset].keys()
                    and sum(r['reference_bp'] for r in rows)==protocol['full_reference_bp'][dataset],
                    'Full provided target denominator differs')
                require(abs(sum(r['recovered_bp'] for r in rows)/sum(r['reference_bp'] for r in rows)-summary['bp_weighted_R95'])<1e-15,
                    'Integer recovery reconstruction differs')
                for g,r in axis.items():require(r['reference_bp']==int(old[unit,role,g]['reference_bp']),'Reference length differs')
                targets[arm]={g:r['recovered_bp'] for g,r in axis.items()};raw[arm]=axis
                secondary={mode:{k:v for k,v in table.items() if k!='bins'} for mode,table in value['secondary'].items()}
                bins=next(iter(value['secondary'].values()))['bins']
                values[arm]=dict(primary=summary,secondary=secondary,bin_count=len(bins),
                    large_bins=sum(v['bp']>=200000 for v in bins),largest_bin_bp=max((v['bp'] for v in bins),default=0),
                    export=value['export_contract'],partition=value['partition'],
                    restricted_grouping=value['grouping']['restricted_B3'] if dataset=='E009' else value['grouping']['origin_B3'])
                if dataset=='oral':values[arm]['known_shared_sensitivity']=value['evaluation']['known_shared_mask']['recovery_summary']
            prior={g:int(old[unit,role,g]['post_bp']) for g in targets['post']}
            anchor={g:int(refs[dataset][g]['selected_bp' if dataset=='E009' else 'E026_recruited_bp']) for g in targets['post']}
            arms[key]=dict(arms=values,root_only_to_profile_pre=changed(targets['root-only'],targets['pre']),
                profile_pre_to_final=changed(targets['pre'],targets['post']),final_vs_E029=changed(prior,targets['post']),
                final_vs_anchor=changed(anchor,targets['post']),retained_geometry=record['retained_geometry'],
                retained_geometry_binding=record['retained_geometry_binding'])
            if role=='student':metrics[unit]=values['post']['primary']
            for genome in sorted(targets['post']):
                row=raw['post'][genome]
                target_rows.append(dict(dataset=dataset,unit=unit,role=role,genome=genome,reference_bp=row['reference_bp'],
                    assembly_confirmed_bp=row['assembly_confirmed_bp'],root_only_bp=targets['root-only'][genome],
                    pre_bp=targets['pre'][genome],post_bp=targets['post'][genome],E029_bp=prior[genome],anchor_bp=anchor[genome],
                    retained_MetaBAT2_bp=int(old[unit,role,genome]['retained_MetaBAT2_bp']),
                    profile_effect_bp=targets['pre'][genome]-targets['root-only'][genome],
                    supported_update_effect_bp=targets['post'][genome]-targets['pre'][genome],
                    final_vs_E029_bp=targets['post'][genome]-prior[genome],
                    post_best_bin='not_recovered' if row['best_bin'] is None else row['best_bin'],
                    post_confirmed_purity='not_applicable' if row['confirmed_purity'] is None else row['confirmed_purity']))
    with (output/'comparison-targets.tsv').open('w') as stream:
        writer=csv.DictWriter(stream,fieldnames=list(target_rows[0]),delimiter='\t',lineterminator='\n');writer.writeheader();writer.writerows(target_rows)
    result=dict(kind='E030 admitted cached biological construction development comparison',checked_UTC=datetime.now(timezone.utc).isoformat(),
        status='COMPLETED_REVIEWED',phase=admission['phase'],science_source=admission['source'],
        frozen_disposition=disposition(metrics,protocol),criteria=binding(output/'protocol.json'),criteria_unchanged=True,
        primary_student_metrics=metrics,arms=arms,anchors=protocol['anchors'],full_reference_bp=protocol['full_reference_bp'],truth=protocol['truth'],
        target_rows=len(target_rows),target_table=binding(output/'comparison-targets.tsv'),raw_reviews=reviews,
        E009_full_path_GLM_student_R95_effect=metrics['E009-GLM']['bp_weighted_R95']-metrics['E009-noGLM']['bp_weighted_R95'],
        old_baselines_rescored=False,scientific_fits_run=0,geometry_recomputed=False,secondary_not_formal_MIMAG_HQ=True,
        original_Mac_portability_tolerance_unchanged=True,all_DNA_status_length_origin_populations_preserved=True,
        limitations=['Both communities are development data; no independent transfer or SOTA claim.',
            'Oral provided-origin oracle is distinct from unique sequence truth; known-shared sensitivity is incomplete.',
            'E009 retains 156 full references and 3.3034% N quarantine; no changed purity/bin-size decision rule.',
            'This is a downstream construction bundle with learning fixed, not an isolated encoder or feature-family study.',
            'Oral full GLM remains unmeasured after the single newly authorized GPU capacity refusal.'])
    write(output/'comparison-review.json',result);audit_summary(output)
    print(json.dumps(dict(disposition=result['frozen_disposition'],primary=metrics)),flush=True);return result


def audit_summary(output):
    """Reconstruct every arm's aggregate recovery/counts from full integer rows."""
    output=Path(output);r=read(output/'comparison-review.json');require(binding(output/'comparison-targets.tsv')==r['target_table'],'Target table bytes differ')
    rows=table(output/'comparison-targets.tsv')
    require(len(rows)==r['target_rows']==2222,'Complete six-component target population differs')
    for key,component in r['arms'].items():
        unit,role=key.split('/');selected=[v for v in rows if v['unit']==unit and v['role']==role]
        den=sum(int(v['reference_bp']) for v in selected)
        for arm,field in [('root-only','root_only_bp'),('pre','pre_bp'),('post','post_bp')]:
            p=component['arms'][arm]['primary'];bp=sum(int(v[field]) for v in selected)
            require(abs(bp/den-p['bp_weighted_R95'])<1e-15 and
                sum(int(v[field])/int(v['reference_bp'])>=.5 for v in selected)==p['at_least_50_percent'] and
                sum(int(v[field])/int(v['reference_bp'])>=.9 for v in selected)==p['at_least_90_percent'],
                'Independent complete-target reconstruction differs')
    return dict(status='PASS_COMPLETE_INTEGER_TABLE_RECONSTRUCTION',rows=len(rows),partitions=18)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--base',type=Path);p.add_argument('--output',type=Path,required=True);p.add_argument('--audit',action='store_true');a=p.parse_args()
    if a.audit:print(json.dumps(audit_summary(a.output)))
    else:summarize(a.base,a.output)
