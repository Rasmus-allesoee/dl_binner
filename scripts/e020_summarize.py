#!/usr/bin/env python3
"""Summarize closed E020 diagnostics against hash-bound E019; never score or fit.

All four new alternatives and all 955 provided targets remain. Exact base-count
fractions implement the prospective E020 rule; this changes neither evaluation
semantics nor the original failed cross-platform numerical tolerance.
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
ARMS = ['cores', 'pre', 'old', 'post']


def disposition(rows):
    """Apply E020's two-scope no-loss/one-material-gain/count rule exactly."""
    if len(rows) != 2:
        raise ValueError('Exactly two separately scoped communities required')
    changes = []
    for row in rows:
        keys = {'candidate_bp', 'baseline_bp', 'reference_bp', 'candidate_90', 'baseline_90'}
        if (set(row) != keys or any(type(v) is not int or v < 0 for v in row.values())
                or row['reference_bp'] <= 0
                or max(row['candidate_bp'], row['baseline_bp']) > row['reference_bp']):
            raise ValueError('Invalid full-denominator comparison totals')
        changes.append(Fraction(row['candidate_bp']-row['baseline_bp'], row['reference_bp']))
    keep = (all(d >= 0 for d in changes) and any(d >= Fraction(1, 200) for d in changes)
            and all(r['candidate_90'] >= r['baseline_90'] for r in rows))
    improved = any(d > 0 or r['candidate_90'] > r['baseline_90'] for d, r in zip(changes, rows))
    return 'KEEP' if keep else 'MODIFY' if improved else 'ABANDON'


def summarize(root, output):
    """Write only closed-review comparisons, complete populations and paired targets."""
    root, output = Path(root), Path(output)
    exp = REPO/'experiments/E020-context-information-integration'
    protocol = read(exp/'protocol.json'); prior_file = REPO/protocol['baseline']['path']
    if binding(prior_file) != protocol['baseline']['binding']:
        raise ValueError('Frozen baseline summary differs')
    prior_summary = read(prior_file)
    if not (read(root/'verified/verification.json')['every_member_verified']
            and read(root/'native-receipts-review.json')['status'] == 'SUCCESS'
            and read(root/'cache-contract-review.json')['status'] == 'PASS'
            and read(root/'review-admission.json')['workflow_completed']):
        raise ValueError('Completed byte/native/cache admission required')
    output.mkdir(exist_ok=True)
    if any((output/n).exists() for n in ['comparison-review.json', 'comparison-targets.tsv']):
        raise ValueError('Preserve earlier summary; explicit fresh reviewed attempt required')
    units, targets, exact, evidence = {}, [], [], {}
    for unit, dataset, n, bp in [('E009-context', 'E009_conservative_v2', 156, 554661890),
                                 ('oral-context', 'oral_provided_origin_oracle', 799, 2083072211)]:
        path = root/('diagnostics-'+unit)/'review.json'
        oldpath = REPO/'artifacts/e019-window-context/review-20261023'/('diagnostics-'+unit)/'review.json'
        if binding(oldpath) != prior_summary['evidence'][str(oldpath.relative_to(REPO))]:
            raise ValueError('Retained E019 diagnostic bytes differ')
        new, old = read(path), read(oldpath)
        if new['status'] != 'SUCCESS' or old['status'] != 'SUCCESS':
            raise ValueError('Both closed reviews must succeed')
        post, baseline = metrics(new, 'post'), metrics(old, 'post')
        if (len(post['recovery']) != n or len(baseline['recovery']) != n
                or sum(q['reference_bp'] for q in post['recovery']) != bp):
            raise ValueError('Full provided reference population differs')
        pair, rows = paired(post['recovery'], baseline['recovery'])
        by_arm = {a: {q['genome']: q for q in metrics(new, a)['recovery']} for a in ARMS}
        old_arms = {a: {q['genome']: q for q in metrics(old, a)['recovery']} for a in ['pre', 'old', 'post']}
        for a in ARMS:
            paired(metrics(new, a)['recovery'], post['recovery'])
        for row in rows:
            g = row['genome']
            targets.append(dict(dataset=dataset, genome=g, reference_bp=row['reference_bp'],
                **{'E019_'+a+'_bp': old_arms[a][g]['recovered_bp'] for a in old_arms},
                **{'E020_'+a+'_bp': by_arm[a][g]['recovered_bp'] for a in ARMS},
                delta_vs_E019_post_bp=row['delta_bp']))
        arms = {}
        is_e009 = unit == 'E009-context'
        for arm in ARMS:
            value = new['arms'][arm]; group = value['grouping']
            geometry = value['diagnostics']['geometry'] if is_e009 else group['geometry']
            prior_geometry = old['arms']['post']['diagnostics']['geometry'] if is_e009 else old['arms']['post']['grouping']['geometry']
            if geometry != prior_geometry:
                raise ValueError('Fixed E019 learned-neighbor diagnostic changed')
            arms[arm] = dict(recovery=metrics(new, arm)['recovery_summary'],
                grouping=group['restricted_B3'] if is_e009 else group['origin_B3'],
                geometry=geometry, populations=value['populations'] if is_e009 else group['population_cells'],
                length_strata=group['length_strata'] if is_e009 else group['geometry']['length_strata'])
            if is_e009:
                arms[arm]['geometry_by_lineage'] = value['diagnostics']['geometry_by_lineage']
            else:
                masked = value['evaluation']['known_shared_mask']
                arms[arm]['known_shared_mask'] = dict(summary=masked['recovery_summary'],
                    all_target_recovery_identical=[(q['genome'], q['recovered_bp']) for q in metrics(new, arm)['recovery']]
                    == [(q['genome'], q['recovered_bp']) for q in masked['recovery']])
                arms[arm]['large_bins'] = group['large_bins']; arms[arm]['large_bins_below95'] = group['large_bins_below95']
        transitions = {a+'_to_'+b: paired(metrics(new, b)['recovery'], metrics(new, a)['recovery'])[0]
                       for a, b in [('cores', 'pre'), ('pre', 'old'), ('old', 'post'), ('pre', 'post')]}
        totals = dict(candidate_bp=sum(q['recovered_bp'] for q in post['recovery']),
            baseline_bp=sum(q['recovered_bp'] for q in baseline['recovery']), reference_bp=bp,
            candidate_90=post['recovery_summary']['at_least_90_percent'], baseline_90=baseline['recovery_summary']['at_least_90_percent'])
        exact.append(totals)
        if abs(totals['candidate_bp']/bp-post['recovery_summary']['bp_weighted_R95']) >= 1e-12:
            raise ValueError('Closed target totals and displayed aggregate disagree')
        units[unit] = dict(dataset=dataset, arms=arms,
            baseline_E019_arms={a: metrics(old, a)['recovery_summary'] for a in old_arms},
            paired_vs_E019=pair, paired_transitions=transitions, accounting=new['contracts'],
            baseline_E019_accounting=old['contracts'],
            target_gains=sorted((q for q in rows if q['delta_bp'] > 0), key=lambda q: -q['delta_bp']),
            target_losses=sorted((q for q in rows if q['delta_bp'] < 0), key=lambda q: q['delta_bp']),
            marker_selection=new['choices'], joint_core_cache=read(root/'cache-contract-review.json')['units'][unit],
            fixed_E019_learned_geometry_equal=True, exact_criterion_totals=totals)
        evidence.update({str(p.relative_to(REPO)): binding(p) for p in [path, oldpath]})
    table = output/'comparison-targets.tsv'
    with table.open('x') as f:
        writer = csv.DictWriter(f, fieldnames=list(targets[0]), delimiter='\t', lineterminator='\n')
        writer.writeheader(); writer.writerows(targets)
    result = dict(record='E020 fixed E019 learning original E017 grouping completed development comparison',
        status='COMPLETED_VERIFIED; FROZEN_NEW_OUTPUT_DIAGNOSTICS',
        reviewed_UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        science_source=read(root/'completion.json')['source'], phase=read(exp/'native-observed.json')['phase'],
        protocol=binding(exp/'protocol.json'), candidate_lock=binding(exp/'candidate-lock.json'),
        reuse_lock=binding(exp/'reuse-lock.json'), archive=read(root/'verified/verification.json'),
        native_ledger=binding(root/'native-receipts-review.json'), cache_review=binding(root/'cache-contract-review.json'),
        units=units, full_target_table=binding(table), reused_E019_summary=binding(prior_file),
        preserved_context=prior_summary['preserved_context'],
        decision=dict(disposition=disposition(exact), original_criterion=protocol['criterion'], exact_totals=exact,
            scope='Development interaction bundle; no ingredient-causal, generalization, per-community/bin oracle, default or SOTA claim.'),
        limitations=['Both communities are development; untouched skin stays unacquired.',
            'E009 conservative v2: all 156 full references; 7,653,205 bp / 3.3034% N quarantine.',
            'Oral provided-origin oracle: all 799 full references, including zero-GSA targets; unique support unadmitted; known-shared sensitivity preserved.',
            'Original failed Mac numerical tolerance is unchanged. Native vectors and original features/markers are byte-identical.',
            'Joint-core candidate recall is sampled in joint learned/composition space, distinct from fixed E019 learned-neighbor metrics and not all depth/profile affinities.',
            'Omitted native full FASTAs/shared inputs/runnable environments are not backed up by inventories or hashes.'], evidence=evidence)
    (output/'comparison-review.json').write_text(json.dumps(result, indent=2)+'\n')
    print('E020_FROZEN_DISPOSITION', result['decision']['disposition'],
          [(u, v['arms']['post']['recovery']) for u, v in units.items()], flush=True)
    return result


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root', type=Path, required=True); p.add_argument('--output', type=Path, required=True)
    a = p.parse_args(); summarize(a.root, a.output)
