#!/usr/bin/env python3
"""Summarize only completed E032 reviews and checksum-bound retained summaries.

This read-only arithmetic layer does not load DNA, fit, group, select bins, or
change truth. It checks integer recovery totals, preserves all target rows, and
applies the prospective decision to the same common post-recruitment policy.
"""
import argparse
import csv
import json
from pathlib import Path
import sys

ROOT = Path(__file__).absolute().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from e024_coverage import binding, write

UNITS = ('E009-noGLM', 'E009-GLM', 'oral-noGLM')


def comparison(rows, before, after):
    """Compare stored integer target recovery without a new score calculation."""
    deltas = [dict(genome=r['genome'], reference_bp=r['reference_bp'],
                   before_bp=r[before], after_bp=r[after],
                   delta_bp=r[after] - r[before]) for r in rows]
    return dict(gained_targets=sum(r['delta_bp'] > 0 for r in deltas),
        lost_targets=sum(r['delta_bp'] < 0 for r in deltas),
        unchanged_targets=sum(r['delta_bp'] == 0 for r in deltas),
        gained_bp=sum(max(0, r['delta_bp']) for r in deltas),
        lost_bp=-sum(min(0, r['delta_bp']) for r in deltas),
        T90_gained=sum(10*r[before] < 9*r['reference_bp'] <= 10*r[after] for r in rows),
        T90_lost=sum(10*r[after] < 9*r['reference_bp'] <= 10*r[before] for r in rows),
        largest_gains=sorted((r for r in deltas if r['delta_bp'] > 0),
                            key=lambda r: (-r['delta_bp'], r['genome']))[:5],
        largest_losses=sorted((r for r in deltas if r['delta_bp'] < 0),
                             key=lambda r: (r['delta_bp'], r['genome']))[:5])


def summarize(base, baseline_table, output):
    """Write compact paired results and a complete, duplicate-safe target table."""
    base, baseline_table, output = map(Path, (base, baseline_table, output))
    output.mkdir(parents=True, exist_ok=False)
    old = json.loads((ROOT / 'experiments/E031-bootstrap-preserving-learning/learning-review.json').read_text())
    protocol = json.loads((ROOT / 'experiments/E032-biological-candidate-selection/protocol.json').read_text())
    if binding(baseline_table) != old['target_table']:
        raise ValueError('Retained E031 target summary differs; no baseline rescore')
    with baseline_table.open() as handle:
        prior = list(csv.DictReader(handle, delimiter='\t'))
    completed = json.loads((base / 'completion.json').read_text())
    if completed['status'] != 'SUCCESS' or not completed['science_completed']:
        raise ValueError('Verified complete E032 output required')
    result = dict(status='COMPLETED_REVIEWED', modes={}, baselines_rescored=False,
        phase=Path(completed['root']).name, scientific_source=completed['source'],
        new_fits_in_review=0, unchanged_full_denominators=True,
        N_quarantine_percent=3.3034,
        Oral_semantics='provided-origin oracle; known-shared mask is not exhaustive uniqueness',
        shared_policy=True, learning_vectors_forests_unchanged=True,
        primary_rule_unchanged=True, secondary_tiers_not_formal_MIMAG_HQ=True,
        protocol=binding(ROOT / 'experiments/E032-biological-candidate-selection/protocol.json'),
        retained_target_table=binding(baseline_table), raw_reviews={})
    all_rows = []
    for unit in UNITS:
        raw_path = base / ('review-' + unit) / 'review.json'
        raw = json.loads(raw_path.read_text())
        result['raw_reviews'][unit] = binding(raw_path)
        rows = [dict(r) for r in prior if r['unit'] == unit]
        for r in rows:
            for k in r:
                if k not in ('unit', 'genome'):
                    r[k] = int(r[k])
        if len({r['genome'] for r in rows}) != len(rows):
            raise ValueError('Duplicate retained target row')
        mode = dict(arms={})
        for arm, value in raw['arms'].items():
            if unit.startswith('E009'):
                primary = value['grouping']['recovery_summary']
                targets = value['grouping']['recovery']
                b3 = value['grouping']['restricted_B3']
                sensitivity = None
            else:
                primary = value['evaluation']['origin']['recovery_summary']
                targets = value['evaluation']['origin']['recovery']
                b3 = value['grouping']['origin_B3']
                sensitivity = value['evaluation']['known_shared_mask']['recovery_summary']
            by_id = {v['genome']: v for v in targets}
            if len(by_id) != len(rows) or set(by_id) != {r['genome'] for r in rows}:
                raise ValueError('Full provided target axes differ')
            for r in rows:
                t = by_id[r['genome']]
                if any(t[k] != r[k] for k in ['reference_bp', 'assembly_confirmed_bp']):
                    raise ValueError('Reference or attributable assembly denominator differs')
                r['E032_' + arm + '_bp'] = t['recovered_bp']
            total = sum(t['recovered_bp'] for t in targets)
            denominator = sum(t['reference_bp'] for t in targets)
            t90 = sum(10*t['recovered_bp'] >= 9*t['reference_bp'] for t in targets)
            if (abs(total/denominator - primary['bp_weighted_R95']) > 1e-14
                    or denominator != primary['reference_bp']
                    or t90 != primary['at_least_90_percent']):
                raise ValueError('Integer target totals and reported primary differ')
            secondary = {n: {k: v for k, v in table.items() if k != 'bins'}
                         for n, table in value['secondary'].items()}
            mode['arms'][arm] = dict(primary=primary,
                integer=dict(recovered_bp=total, reference_bp=denominator, T90=t90),
                known_shared_sensitivity=sensitivity, B3=b3, secondary=secondary,
                export=value['export_contract'], partition=value['partition'])
        anchor = protocol['anchors'][unit]
        post = mode['arms']['post']['primary']
        mode['prospective_anchor'] = anchor
        mode['delta_R95_percentage_points'] = 100*(post['bp_weighted_R95'] - anchor['R95'])
        mode['delta_T90'] = post['at_least_90_percent'] - anchor['T90']
        mode['paired_recruitment'] = comparison(rows, 'E032_pre_bp', 'E032_post_bp')
        mode['versus_retained_E023'] = comparison(rows, 'E023_selected_bp', 'E032_post_bp')
        mode['versus_retained_E030'] = comparison(rows, 'E030_post_bp', 'E032_post_bp')
        mode['versus_retained_MetaBAT2'] = comparison(rows, 'retained_MetaBAT2_bp', 'E032_post_bp')
        result['modes'][unit] = mode
        all_rows.extend(rows)
    deltas = [v['delta_R95_percentage_points'] for v in result['modes'].values()]
    no_loss = all(v['delta_R95_percentage_points'] >= 0 and v['delta_T90'] >= 0
                  for v in result['modes'].values())
    abandon = max(deltas) <= 0 or (min(deltas) <= -1 and max(deltas) < .5)
    result['frozen_disposition'] = 'ABANDON' if abandon else 'KEEP' if no_loss and max(deltas) >= .5 else 'MODIFY'
    result['criterion_results'] = dict(no_mode_R95_T90_loss=no_loss,
        at_least_half_point_gain=max(deltas) >= .5,
        no_mode_R95_gain=max(deltas) <= 0,
        point_loss_without_half_point_gain=min(deltas) <= -1 and max(deltas) < .5)
    with (output / 'targets.tsv').open('x') as handle:
        writer = csv.DictWriter(handle, fieldnames=list(all_rows[0]), delimiter='\t', lineterminator='\n')
        writer.writeheader()
        writer.writerows(all_rows)
    result['target_rows'] = len(all_rows)
    result['target_table'] = binding(output / 'targets.tsv')
    write(output / 'review.json', result)
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ['base', 'baseline-table', 'output']:
        parser.add_argument('--' + name, type=Path, required=True)
    args = parser.parse_args()
    summarize(args.base, args.baseline_table, args.output)
