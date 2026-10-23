#!/usr/bin/env python3
"""Summarize only admitted E019 diagnostics against retained E016 results.

This reader does not run evaluators or select partitions. All provided targets
and parent/old/E013 alternatives remain in the table. The frozen practical rule
uses exact recovered-base fractions, avoiding float rounding at 0.5 percentage
point without relaxing the criterion or changing any score.
"""
import argparse
import csv
import datetime
from fractions import Fraction
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).absolute().parent))
from e016_summarize import binding, metrics, paired, read

REPO = Path(__file__).absolute().parents[1]
ARMS = ['pre', 'old', 'post']


def disposition(comparisons):
    """Apply the original both-community 0.005/count rule to exact base totals.

    Each of two rows supplies candidate and baseline recovered bp, the unchanged
    full reference denominator, and candidate/baseline >=90% target counts.
    These are read from closed evaluations, never used to choose a bin or fit.
    """
    if len(comparisons) != 2:
        raise ValueError('Exactly two separately scoped communities required')
    changes = []
    for row in comparisons:
        keys = {'candidate_bp', 'baseline_bp', 'reference_bp', 'candidate_90', 'baseline_90'}
        if set(row) != keys or any(type(v) is not int or v < 0 for v in row.values()) or row['reference_bp'] <= 0:
            raise ValueError('Invalid frozen comparison totals')
        if max(row['candidate_bp'], row['baseline_bp']) > row['reference_bp']:
            raise ValueError('Recovery exceeds full provided denominator')
        changes.append(Fraction(row['candidate_bp']-row['baseline_bp'], row['reference_bp']))
    keep = (all(delta >= Fraction(1, 200) for delta in changes)
            and all(r['candidate_90'] >= r['baseline_90'] for r in comparisons))
    any_improvement = any(delta > 0 or row['candidate_90'] > row['baseline_90']
                          for delta, row in zip(changes, comparisons))
    return 'KEEP' if keep else 'MODIFY' if any_improvement else 'ABANDON'


def compact_verification(path):
    """Bind the complete external inventory without duplicating thousands of DNA hashes.

    Every physical member was verified by the admitted archive reader. Keep the
    full proof and its binding locally, with explicit omission totals and aliases;
    omitted scientific bytes remain on the VM and are not backed up by hashes.
    """
    value = read(path)
    if value['status'] != 'SUCCESS' or value['every_member_verified'] is not True:
        raise ValueError('Complete archive verification required')
    omitted = value['omitted_retained_on_disk']
    return {k: value[k] for k in ['status', 'archive', 'regular_members',
        'logical_member_bytes', 'every_member_verified', 'aliases']} | dict(
        full_verification=binding(path), omitted_member_count=len(omitted),
        omitted_bytes=sum(row['bytes'] for row in omitted.values()),
        omitted_member_hashes='Complete checksum-bound archive inventory and external verification proof',
        omitted_bytes_are_not_backed_up=True)


def summarize(root, output):
    """Write checksum-bound paired diagnostics and all 955 provided target rows."""
    root, output = Path(root), Path(output)
    exp = REPO/'experiments/E019-window-context'
    prior_summary_path = REPO/'experiments/E016-positive-only-multiview/comparison-review.json'
    prior_summary = read(prior_summary_path)
    assert read(root/'verified/verification.json')['every_member_verified']
    assert read(root/'native-receipts-review.json')['status'] == 'SUCCESS'
    assert read(root/'learning-receipts-review.json')['status'] == 'PASS'
    assert read(root/'review-admission.json')['workflow_completed']
    output.mkdir(exist_ok=True)
    if any((output/n).exists() for n in ['comparison-review.json', 'comparison-targets.tsv']):
        raise ValueError('Preserve prior comparison; use an explicit reviewed attempt')
    units, targets, exact, evidence = {}, [], [], {}
    for unit, oldunit, dataset in [('E009-context', 'E009-positive', 'E009_conservative_v2'),
                                     ('oral-context', 'oral-positive', 'oral_provided_origin_oracle')]:
        path = root/('diagnostics-'+unit)/'review.json'
        oldpath = REPO/'artifacts/e016-positive-only-multiview/review-20261020'/('diagnostics-'+oldunit)/'review.json'
        assert binding(oldpath) == prior_summary['evidence'][str(oldpath.relative_to(REPO))]
        new, old = read(path), read(oldpath)
        assert new['status'] == old['status'] == 'SUCCESS'
        post, baseline = metrics(new, 'post'), metrics(old, 'post')
        n, bp = (156, 554661890) if unit == 'E009-context' else (799, 2083072211)
        assert len(post['recovery']) == len(baseline['recovery']) == n
        assert sum(q['reference_bp'] for q in post['recovery']) == bp
        pair, rows = paired(post['recovery'], baseline['recovery'])
        by_arm = {a: {q['genome']: q for q in metrics(new, a)['recovery']} for a in ARMS}
        old_arms = {a: {q['genome']: q for q in metrics(old, a)['recovery']} for a in ARMS}
        for row in rows:
            g = row['genome']
            targets.append(dict(dataset=dataset, genome=g, reference_bp=row['reference_bp'],
                **{'E016_'+a+'_bp': old_arms[a][g]['recovered_bp'] for a in ARMS},
                **{'E019_'+a+'_bp': by_arm[a][g]['recovered_bp'] for a in ARMS}, delta_vs_E016_post_bp=row['delta_bp']))
        arms = {}
        for arm in ARMS:
            value = new['arms'][arm]; group = value['grouping']; is_e009 = unit == 'E009-context'
            arms[arm] = dict(recovery=metrics(new, arm)['recovery_summary'],
                grouping=group['restricted_B3'] if is_e009 else group['origin_B3'],
                geometry=value['diagnostics']['geometry'] if is_e009 else group['geometry'],
                populations=value['populations'] if is_e009 else group['population_cells'],
                length_strata=group['length_strata'] if is_e009 else group['geometry']['length_strata'])
            if is_e009:
                arms[arm]['geometry_by_lineage'] = value['diagnostics']['geometry_by_lineage']
            else:
                masked = value['evaluation']['known_shared_mask']
                arms[arm]['known_shared_mask'] = dict(summary=masked['recovery_summary'],
                    all_target_recovery_identical=[(q['genome'], q['recovered_bp']) for q in metrics(new, arm)['recovery']]
                    == [(q['genome'], q['recovered_bp']) for q in masked['recovery']])
                arms[arm]['large_bins'] = group['large_bins']
                arms[arm]['large_bins_below95'] = group['large_bins_below95']
        transitions = {a+'_to_'+b: paired(metrics(new, b)['recovery'], metrics(new, a)['recovery'])[0]
                       for a, b in [('pre', 'old'), ('old', 'post'), ('pre', 'post')]}
        selected = {}
        for q in read(root/'verified/work/units'/unit/'refine/decisions.json'):
            selected[q['selected']] = selected.get(q['selected'], 0)+1
        c, b = post['recovery_summary'], baseline['recovery_summary']
        total = dict(candidate_bp=sum(q['recovered_bp'] for q in post['recovery']),
            baseline_bp=sum(q['recovered_bp'] for q in baseline['recovery']), reference_bp=bp,
            candidate_90=c['at_least_90_percent'], baseline_90=b['at_least_90_percent'])
        exact.append(total)
        assert abs(total['candidate_bp']/bp-c['bp_weighted_R95']) < 1e-12
        units[unit] = dict(dataset=dataset, arms=arms, baseline_E016_arms={a: metrics(old, a)['recovery_summary'] for a in ARMS},
            baseline_E016_post=b, baseline_E014_post=prior_summary['units'][oldunit]['baseline_E014_post'],
            baseline_E015_post=prior_summary['units'][oldunit]['baseline_E015_post'],
            paired_vs_E016=pair, paired_transitions=transitions, accounting=new['contracts'],
            baseline_E016_accounting=old['contracts'],
            target_gains=sorted((q for q in rows if q['delta_bp'] > 0), key=lambda q: -q['delta_bp']),
            target_losses=sorted((q for q in rows if q['delta_bp'] < 0), key=lambda q: q['delta_bp']),
            marker_selection=selected, token_contract=new['token_contract'],
            raw_learned_geometry={k: v for k, v in new['raw_learned_geometry'].items() if k != 'queries'},
            baseline_E016_raw_learned_geometry={k: v for k, v in old['raw_learned_geometry'].items() if k != 'queries'},
            baseline_E016_geometry=prior_summary['units'][oldunit]['arms']['post']['geometry'],
            native_neighbor_audit={k: v for k, v in new['native_graph_review']['geometry'].items() if k != 'queries'},
            training={k: new['checkpoint'][k] for k in ['config', 'parameter_count', 'teacher_parameter_count',
                'predictor_parameter_count', 'samples', 'training_parents', 'positive_parents', 'ema_updates',
                'threads', 'loader_workers', 'wall_seconds', 'process_cpu_seconds']},
            geometry_history=dict(initial=new['checkpoint']['initial_geometry'], epochs=[dict(epoch=h['epoch'], geometry=h['geometry']) for h in new['checkpoint']['history']]),
            exact_criterion_totals=total)
        evidence.update({str(p.relative_to(REPO)): binding(p) for p in [path, oldpath]})
    table = output/'comparison-targets.tsv'
    with table.open('x') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(targets[0]), delimiter='\t', lineterminator='\n')
        writer.writeheader(); writer.writerows(targets)
    result = dict(record='E019 frozen context bundle completed development comparison',
        status='COMPLETED_VERIFIED_FROZEN_DIAGNOSTICS', reviewed_UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        science_source=read(root/'completion.json')['source'], phase=read(exp/'native-observed.json')['phase'],
        protocol=binding(exp/'protocol.json'), candidate_lock=binding(exp/'candidate-lock.json'), reuse_lock=binding(exp/'reuse-lock.json'),
        archive=compact_verification(root/'verified/verification.json'), native_ledger=binding(root/'native-receipts-review.json'),
        learning_audit=binding(root/'learning-receipts-review.json'), units=units, full_target_table=binding(table),
        preserved_context=prior_summary['preserved_context'], reused_E016_summary=binding(prior_summary_path),
        decision=dict(disposition=disposition(exact), frozen_keep=read(exp/'protocol.json')['keep'],
            frozen_modify=read(exp/'protocol.json')['modify'], frozen_abandon=read(exp/'protocol.json')['abandon'],
            exact_fraction_rule='Both recovered-bp/full-reference gains >=1/200 and no >=90% count decrease; no float tolerance or metric change.',
            scope='One information/encoder bundle on two development communities. No isolated causal attention, optimality, product-default, feature-family or generalization claim.'),
        limitations=['Conservative E009 v2: full 156 references /554661890 bp, 3.3034% N quarantine.',
            'Oral provided-origin oracle: full 799 references /2083072211 bp including zero-GSA targets; unique source support unadmitted, known-shared sensitivity retained.',
            'All original short/marker-negative/unknown/non-target/excluded/noise DNA retained; no truth-selected partitions or baseline rescore.',
            'Native token count/coordinate bytes and full DNA remain on disk: manifest/hash/native-consumption proof is not a local numeric reread or backup.',
            'Original failed Mac tolerance remains failed; strict native reload and original vectors admitted without local neural inference.',
            'Only final tensor/optimizer states and epoch histories exist, not every historical gradient or complete initial community tensor snapshot.',
            'Both communities are development; untouched skin admission/acquisition/protocol/cost/retention remain separate.'], evidence=evidence)
    (output/'comparison-review.json').write_text(json.dumps(result, indent=2)+'\n')
    print('E019_FROZEN_DISPOSITION', result['decision']['disposition'],
        [(u, v['arms']['post']['recovery']) for u, v in units.items()], flush=True)
    return result


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root', type=Path, required=True); p.add_argument('--output', type=Path, required=True)
    a = p.parse_args(); summarize(a.root, a.output)
