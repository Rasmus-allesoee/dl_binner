#!/usr/bin/env python3
"""Summarize admitted new E031 partitions beside immutable retained references.

This joins completed frozen diagnostic tables; it never scores an old partition,
fits a model, chooses bins, tunes a criterion or routes datasets to winners.
All target numerators and full-reference denominators are reconstructed as
integers before each unchanged constructor-specific decision is evaluated.
"""
import argparse
import csv
from datetime import datetime, timezone
from fractions import Fraction
import json
from pathlib import Path
import sys

ROOT=Path(__file__).absolute().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from e024_coverage import binding,write
from e029_summary import changed
from e031_decision import disposition,UNITS,REFERENCES


def read(path):
    """Read a closed admitted result."""
    return json.loads(Path(path).read_text())


def table(path):
    """Read source-bound retained target counts without rescoring their science."""
    with Path(path).open()as stream:
        return list(csv.DictReader(stream,delimiter='\t'))


def integer_metrics(rows,unit):
    """Require one exact positive denominator for every provided target."""
    expected=156 if unit.startswith('E009')else 799
    if (len(rows)!=expected or len({r['genome']for r in rows})!=expected
            or sum(int(r['reference_bp'])for r in rows)!=REFERENCES[unit]
            or any(not 0<=int(r['recovered_bp'])<=int(r['reference_bp'])or int(r['reference_bp'])<=0 for r in rows)):
        raise ValueError('Complete target population/integer denominator differs')
    return dict(recovered_bp=sum(int(r['recovered_bp'])for r in rows),reference_bp=REFERENCES[unit],
                target_90=sum(Fraction(int(r['recovered_bp']),int(r['reference_bp']))>=Fraction(9,10)for r in rows))


def summarize(base,reviews,output):
    """Compare both frozen constructors on the same three admitted new models."""
    base,reviews,output=[Path(p).absolute()for p in [base,reviews,output]]
    admission=read(base/'admission.json');native=read(base/'native-review-admission.json')
    if not admission['workflow_completed']or not native['archive_and_every_member_verified']or native['provider_status']!='TERMINATED':
        raise ValueError('Independent scientific and diagnostic return admission required')
    old={(r['unit'],r['role'],r['genome']):r for r in table(ROOT/'experiments/E030-supported-biological-bins/comparison-targets.tsv')}
    bridge={(r['unit'],r['role'],r['genome']):r for r in table(ROOT/'experiments/E031-bootstrap-preserving-learning/bridge-targets.tsv')}
    anchors={}
    for unit,experiment,field in [('E009-GLM','E023-adaptive-density-bins','selected_bp'),
                                 ('oral-noGLM','E026-calibrated-evidence-fusion','E026_recruited_bp')]:
        dataset='E009'if unit.startswith('E009')else'oral'
        rows=[dict(genome=r['genome'],reference_bp=int(r['reference_bp']),recovered_bp=int(r[field]))
              for r in table(ROOT/'experiments'/experiment/'comparison-targets.tsv')if r['dataset']==dataset]
        anchors[unit]=integer_metrics(rows,unit)
    actors={};all_targets=[];new_metrics={'E023':{},'E030':{}};old_metrics={};raw_bindings={}
    for unit in UNITS:
        maps={};values={}
        for family,comparison,arms in [('E023','learning-E023',['density','selected']),('E030','learning',['root-only','pre','post'])]:
            path=reviews/('review-'+unit+'-'+comparison)/'review.json';result=read(path)
            if result['contract']['status']!='PASS'or result['contract']['unit']!=unit or result['contract']['comparison']!=comparison:
                raise ValueError('New frozen reviewer identity differs')
            raw_bindings[str(path.relative_to(ROOT))]=binding(path)
            for arm in arms:
                key=family+'/'+arm;value=result['arms'][arm]
                primary=value['grouping']if unit.startswith('E009')else value['evaluation']['origin']
                rows=primary['recovery'];metric=integer_metrics(rows,unit);summary=primary['recovery_summary']
                if abs(metric['recovered_bp']/metric['reference_bp']-summary['bp_weighted_R95'])>1e-15 or metric['target_90']!=summary['at_least_90_percent']:
                    raise ValueError('Independent integer reconstruction differs')
                maps[key]={r['genome']:r for r in rows}
                values[key]=dict(primary=summary,integer=metric,partition=value['partition'],export=value['export_contract'],
                    secondary={mode:{k:v for k,v in quality.items()if k!='bins'}for mode,quality in value['secondary'].items()},
                    known_shared_sensitivity=None if unit.startswith('E009')else value['evaluation']['known_shared_mask']['recovery_summary'])
            new_metrics[family][unit]=values[family+'/'+arms[-1]]['integer']
        genomes=maps['E023/selected']
        prior={g:int(old[unit,'student',g]['post_bp'])for g in genomes}
        old_metrics[unit]=integer_metrics([dict(genome=g,recovered_bp=prior[g],reference_bp=int(old[unit,'student',g]['reference_bp']))for g in genomes],unit)
        paired={}
        for family,final in [('E023','selected'),('E030','post')]:
            after={g:r['recovered_bp']for g,r in maps[family+'/'+final].items()}
            field='selected_bp'if family=='E023'else'post_bp';source=bridge if family=='E023'else old
            paired[family]=dict(vs_previous_student=changed({g:int(source[unit,'student',g][field])for g in genomes},after),
                vs_initialized_teacher=changed({g:int(source[unit,'teacher',g][field])for g in genomes},after))
        effects={label:changed({g:r['recovered_bp']for g,r in maps[a].items()},
                              {g:r['recovered_bp']for g,r in maps[b].items()})for label,a,b in [
            ('E023_density_to_selection','E023/density','E023/selected'),
            ('E030_root_to_pre','E030/root-only','E030/pre'),('E030_pre_to_post','E030/pre','E030/post'),
            ('same_new_learning_E030_to_E023','E030/post','E023/selected')]}
        actors[unit]=dict(arms=values,paired_continuation=paired,construction_effects=effects)
        for g,row in sorted(genomes.items()):
            refs=[int(source[unit,role,g]['reference_bp'])for source in [old,bridge]for role in ['teacher','student']]
            if any(x!=row['reference_bp']for x in refs):raise ValueError('Retained matched reference axis differs')
            all_targets.append(dict(unit=unit,genome=g,reference_bp=row['reference_bp'],assembly_confirmed_bp=row['assembly_confirmed_bp'],
                **{k.replace('/','_').replace('-','_')+'_bp':m[g]['recovered_bp']for k,m in maps.items()},
                E030_previous_student_bp=prior[g],E030_initialized_teacher_bp=int(old[unit,'teacher',g]['post_bp']),
                E023_previous_student_bp=int(bridge[unit,'student',g]['selected_bp']),
                E023_initialized_teacher_bp=int(bridge[unit,'teacher',g]['selected_bp']),
                retained_MetaBAT2_bp=int(old[unit,'student',g]['retained_MetaBAT2_bp'])))
    if len(all_targets)!=1111:raise ValueError('Full three-mode target axis differs')
    output.mkdir(parents=True,exist_ok=True);target=output/'learning-targets.tsv'
    with target.open('x')as stream:
        w=csv.DictWriter(stream,fieldnames=list(all_targets[0]),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(all_targets)
    result=dict(status='COMPLETED_REVIEWED',phase=admission['phase'],source=admission['source'],
        checked_UTC=datetime.now(timezone.utc).isoformat(),actors=actors,
        frozen_decisions={family:disposition('learning',old_metrics,new_metrics[family],anchors)for family in ['E023','E030']},
        primary_integer_metrics=new_metrics,retained_E030_integer_metrics=old_metrics,anchors=anchors,
        target_table=binding(target),target_rows=len(all_targets),new_models=3,new_partitions=15,
        raw_review_bindings=raw_bindings,baselines_rescored=False,new_fits_in_review=0,
        unchanged_full_denominators=True,N_quarantine_percent=3.3034,
        Oral_semantics='Provided-origin oracle and unchanged known-shared sensitivity; not exhaustive unique truth',
        one_shared_binner_no_dataset_router=True,secondary_tiers_not_formal_MIMAG_HQ=True,
        whole_learning_bundle_not_component_causality=True,independent_confirmation=False)
    write(output/'learning-review.json',result);return result


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for name in ['base','reviews','output']:p.add_argument('--'+name,type=Path,required=True)
    a=p.parse_args();r=summarize(a.base,a.reviews,a.output)
    print(json.dumps(dict(decisions=r['frozen_decisions'],primary=r['primary_integer_metrics'])))
