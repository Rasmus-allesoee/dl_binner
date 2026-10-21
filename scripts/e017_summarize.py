#!/usr/bin/env python3
"""Summarize closed E017 diagnostics against unchanged checksum-bound E016 results.

No partition is selected, rescored or tuned here. Conservative E009-v2 and oral
provided-origin recovery stay separate, with all full-reference target rows and
population cells retained. Criteria come from the pre-outcome E017 protocol.
"""
import argparse
import csv
import datetime
import json
from pathlib import Path
import sys

sys.path.insert(0,str(Path(__file__).absolute().parent))
from e016_summarize import binding,metrics,numerical_keep,paired,read

REPO=Path(__file__).absolute().parents[1]
ARMS=['cores','pre','old','post']


def summarize(root,output):
    """Write complete paired target table and a compact, scoped bundle review."""
    root,output=Path(root),Path(output);exp=REPO/'experiments/E017-information-aware-grouping'
    protocol=read(exp/'protocol.json');old_path=REPO/protocol['baselines']['E016']['path']
    assert binding(old_path)==protocol['baselines']['E016']['binding']
    accepted=read(old_path);assert read(root/'native-receipts-review.json')['status']=='SUCCESS'
    assert read(root/'cache-contract-review.json')['status']=='PASS'
    assert read(root/'verified/verification.json')['every_member_verified']
    output.mkdir(exist_ok=True)
    for name in ['comparison-review.json','comparison-targets.tsv']:
        if(output/name).exists():raise ValueError('Preserve prior summary; explicit reviewed recovery required')
    units={};targets=[];current_summaries=[];prior_summaries=[];evidence={}
    for unit,dataset in [('E009-positive','E009_conservative_v2'),('oral-positive','oral_provided_origin_oracle')]:
        path=root/('diagnostics-E009-positive-attempt3'if unit=='E009-positive'else'diagnostics-oral-positive')/'review.json'
        prior_path=REPO/'artifacts/e016-positive-only-multiview/review-20261020'/('diagnostics-'+unit)/'review.json'
        assert binding(prior_path)==accepted['evidence'][str(prior_path.relative_to(REPO))]
        new,prior=read(path),read(prior_path);assert new['status']==prior['status']=='SUCCESS'
        post,baseline=metrics(new,'post'),metrics(prior,'post')
        assert len(post['recovery'])==(156 if unit=='E009-positive'else 799)
        assert sum(x['reference_bp']for x in post['recovery'])==(554661890 if unit=='E009-positive'else 2083072211)
        pairs,rows=paired(post['recovery'],baseline['recovery'])
        by_arm={a:{x['genome']:x for x in metrics(new,a)['recovery']}for a in ARMS}
        old_arms={a:{x['genome']:x for x in metrics(prior,a)['recovery']}for a in ['pre','old','post']}
        for row in rows:
            g=row['genome'];targets.append(dict(dataset=dataset,genome=g,reference_bp=row['reference_bp'],
                **{'E016_'+a+'_bp':old_arms[a][g]['recovered_bp']for a in old_arms},
                **{'E017_'+a+'_bp':by_arm[a][g]['recovered_bp']for a in ARMS},delta_vs_E016_post_bp=row['delta_bp']))
        arms={}
        for arm in ARMS:
            value=new['arms'][arm];group=value['grouping'];is_e009=unit=='E009-positive'
            geometry=value['diagnostics']['geometry']if is_e009 else group['geometry']
            prior_geometry=prior['arms']['post']['diagnostics']['geometry']if is_e009 else prior['arms']['post']['grouping']['geometry']
            assert geometry==prior_geometry,'Fixed learned-neighbor diagnostic changed'
            arms[arm]=dict(recovery=metrics(new,arm)['recovery_summary'],
                grouping=group['restricted_B3']if is_e009 else group['origin_B3'],
                geometry=geometry,populations=value['populations']if is_e009 else group['population_cells'],
                length_strata=group['length_strata']if is_e009 else group['geometry']['length_strata'])
            if is_e009:arms[arm]['geometry_by_lineage']=value['diagnostics']['geometry_by_lineage']
            else:
                masked=value['evaluation']['known_shared_mask']
                arms[arm]['known_shared_mask']=dict(summary=masked['recovery_summary'],
                    all_target_recovery_identical=[(x['genome'],x['recovered_bp'],x['whole_reference_R95'])for x in metrics(new,arm)['recovery']]
                    ==[(x['genome'],x['recovered_bp'],x['whole_reference_R95'])for x in masked['recovery']])
                arms[arm]['large_bins']=group['large_bins'];arms[arm]['large_bins_below95']=group['large_bins_below95']
        transitions={}
        for before,after in [('cores','pre'),('pre','old'),('old','post'),('pre','post')]:
            transitions[before+'_to_'+after]=paired(metrics(new,after)['recovery'],metrics(new,before)['recovery'])[0]
        units[unit]=dict(dataset=dataset,arms=arms,baseline_E016_post=baseline['recovery_summary'],
            baseline_E014_post=accepted['units'][unit]['baseline_E014_post'],baseline_E015_post=accepted['units'][unit]['baseline_E015_post'],
            paired_vs_E016=pairs,paired_transitions=transitions,accounting=new['contracts'],
            baseline_E016_accounting=prior['contracts']['post'],
            target_gains=sorted((x for x in rows if x['delta_bp']>0),key=lambda x:-x['delta_bp']),
            target_losses=sorted((x for x in rows if x['delta_bp']<0),key=lambda x:x['delta_bp']),
            cache=read(root/'cache-contract-review.json')['units'][unit],
            gate_overlap=read(root/'gate-overlap-review.json')['units'][unit],
            fixed_learned_geometry_equal=True)
        current_summaries.append(post['recovery_summary']);prior_summaries.append(baseline['recovery_summary'])
        evidence.update({str(p.relative_to(REPO)):binding(p)for p in [path,prior_path]})
    keep=numerical_keep(current_summaries,prior_summaries)
    improved=any(c['bp_weighted_R95']>b['bp_weighted_R95']or c['at_least_90_percent']>b['at_least_90_percent']for c,b in zip(current_summaries,prior_summaries))
    disposition='KEEP'if keep else'MODIFY'if improved else'ABANDON'
    table=output/'comparison-targets.tsv';fields=list(targets[0])
    with table.open('x')as stream:
        writer=csv.DictWriter(stream,fieldnames=fields,delimiter='\t',lineterminator='\n');writer.writeheader();writer.writerows(targets)
    result=dict(record='E017 fixed-learning information-aware grouping review',status='COMPLETED_VERIFIED; FROZEN_NEW_OUTPUT_DIAGNOSTICS',
        reviewed_UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),science_source=read(root/'completion.json')['source'],
        phase='information-20261020T232634Z-e78d766',protocol=binding(exp/'protocol.json'),
        candidate_lock=binding(exp/'candidate-lock.json'),native_launch_lock=binding(exp/'native-launch-lock.json'),
        local_reader_repair=binding(exp/'review-repair-lock.json'),archive=read(root/'verified/verification.json'),
        native_ledger=binding(root/'native-receipts-review.json'),units=units,full_target_table=binding(table),
        preserved_context=accepted['preserved_context'],
        decision=dict(disposition=disposition,frozen_keep=keep,criterion=protocol['decision'],
            scope='Development grouping bundle only; no default promotion, per-dataset/per-bin oracle, causal ingredient proof or product-family decision.'),
        limitations=['Both communities are development; skin remains frozen and unacquired.',
            'E009 conservative v2: full 156 references, 554661890 bp; 7653205 bp / 3.3034% N-quarantine.',
            'Oral provided-origin oracle: full 799 references, 2083072211 bp; unique support unadmitted; known-shared sensitivity kept.',
            'The two communities differ in source, assembly, length distribution and depth availability; this does not isolate depth.',
            'Core, affinity and recruitment changes form a bundle. Approximate candidate recall is sampled in joint feature space, not all profile/depth affinities.',
            'Original failed Mac numerical tolerance is unchanged; native vectors remain hash-bound. Local format adapter repair does not make portability pass.',
            'Native final FASTAs/shared inputs/runtimes are not backed up merely by return hashes.'],evidence=evidence)
    (output/'comparison-review.json').write_text(json.dumps(result,indent=2)+'\n')
    print('E017_FROZEN_DISPOSITION',disposition,[(u,v['arms']['post']['recovery'])for u,v in units.items()],flush=True)
    return result


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--root',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();summarize(a.root,a.output)
