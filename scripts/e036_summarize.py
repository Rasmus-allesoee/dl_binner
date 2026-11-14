#!/usr/bin/env python3
"""Summarize only completed E036 diagnostics; reuse accepted comparator scores.

This is arithmetic over already evaluated new target rows and immutable old
summaries, not another evaluator, a fit or a truth-selected bin decision.
"""
from collections import Counter
import csv
import json
from pathlib import Path
import sys

ROOT = Path(__file__).absolute().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from e024_coverage import binding, write


def summarize(base, output):
    """Write paired recovery, complete target rows and secondary per-bin tiers."""
    base, output = Path(base), Path(output)
    output.mkdir(parents=True, exist_ok=False)
    units, targets, bins = {}, [], []
    for unit in ['E009-noGLM', 'E009-GLM']:
        newpath = base / ('review-' + unit) / 'review.json'
        oldpath = ROOT / 'artifacts/e032-biological-candidate-selection/inspection' / ('review-' + unit) / 'review.json'
        new, old = [json.loads(p.read_text()) for p in [newpath, oldpath]]
        baseline = {r['genome']: r for r in old['arms']['post']['grouping']['recovery']}
        arms = {}
        for arm, value in new['arms'].items():
            part = json.loads((base / 'restored/work' / unit / 'select/result'
                               / (arm + '-partition.json')).read_text())
            counts = Counter('bin_%06d' % n for n in part['assignment'] if n >= 0)
            recovery = value['grouping']['recovery']
            single, multi = [], []
            for r in recovery:
                members = counts[r['best_bin']] if r['best_bin'] is not None else 0
                row = dict(unit=unit, arm=arm, **r, best_bin_contigs=members,
                           baseline_E032_post_recovered_bp=baseline[r['genome']]['recovered_bp'],
                           delta_recovered_bp=r['recovered_bp'] - baseline[r['genome']]['recovered_bp'])
                targets.append(row)
                (single if members == 1 else multi).append(r)
            total = sum(r['reference_bp'] for r in recovery)
            represented = sum(r['assembly_confirmed_bp'] for r in recovery)
            tier = value['secondary']['conservative_sequence']
            for row in tier['bins']:
                bins.append(dict(unit=unit, arm=arm, **row))
            arms[arm] = dict(primary=value['grouping']['recovery_summary'],
                represented_confirmed_bp=represented, representation_upper_bound=represented / total,
                pooled_assembly_conditional_R95=sum(r['recovered_bp'] for r in recovery) / represented,
                represented_ceiling_not_attainability=True,
                singleton_R95=sum(r['recovered_bp'] for r in single) / total,
                multi_contig_R95=sum(r['recovered_bp'] for r in multi) / total,
                singleton_T90=sum(r['whole_reference_R95'] >= .9 for r in single),
                multi_contig_T90=sum(r['whole_reference_R95'] >= .9 for r in multi),
                full_DNA=value['export_contract'],
                secondary={k: v for k, v in tier.items() if k != 'bins'},
                population_keys=value['populations']['keys'],
                all_population_cells=value['populations']['cells'])
        current = arms['post']['primary']
        previous = old['arms']['post']['grouping']['recovery_summary']
        oldpart_path = (ROOT / 'artifacts/e032-biological-candidate-selection/inspection/verified/work'
                        / unit / 'select/result/post-partition.json')
        oldpart = json.loads(oldpart_path.read_text())
        if binding(oldpart_path) != old['arms']['post']['partition']:
            raise ValueError('Accepted comparator partition bytes differ')
        oldcounts = Counter('bin_%06d' % n for n in oldpart['assignment'] if n >= 0)
        oldmulti = sum(oldcounts[r['best_bin']] > 1 for r in baseline.values()
                       if r['whole_reference_R95'] >= .9)
        units[unit] = dict(arms=arms, retained_E032_post=previous,
            new_diagnostic=binding(newpath), retained_comparator=binding(oldpath),
            delta_R95_percentage_points=100 * (current['bp_weighted_R95'] - previous['bp_weighted_R95']),
            delta_T90=current['at_least_90_percent'] - previous['at_least_90_percent'],
            retained_E032_multi_contig_T90=oldmulti,
            delta_multi_contig_T90=arms['post']['multi_contig_T90'] - oldmulti,
            singleton_semantics='Number of all contigs in the selected best bin; a multi-contig bin need not require fragmented-source recovery',
            geometry=binding(base / ('geometry-' + unit + '.json')))
    for filename, rows in [('targets.tsv', targets), ('bin-quality.tsv', bins)]:
        with (output / filename).open('x') as stream:
            writer = csv.DictWriter(stream, fieldnames=list(rows[0]), delimiter='\t', lineterminator='\n')
            writer.writeheader()
            writer.writerows(rows)
    oralpath = ROOT / 'artifacts/e032-biological-candidate-selection/inspection/review-oral-noGLM/review.json'
    oral = json.loads(oralpath.read_text())
    result = dict(status='PASS_FROZEN_NEW_OUTPUT_DIAGNOSTICS', units=units,
        oral_exact_fallback=dict(new_fit=False, rescored=False,
                                retained_summary=binding(oralpath),
                                retained_summary_path=str(oralpath.relative_to(ROOT)),
                                primary={mode: {k: v for k, v in value.items()
                                                if k in {'recovery_summary', 'accounting', 'mode'}}
                                         for mode, value in oral['arms']['post']['evaluation'].items()},
                                accepted_full_DNA=oral['arms']['post']['export_contract']),
        primary_denominators=dict(E009_targets=156, E009_reference_bp=554661890,
            E009_N_quarantine_percent=3.3034, oral_targets=799,
            oral_reference_bp=2083072211, truth_scopes_are_different=True),
        secondary_label='Full-reference sequence tiers, contamination upper bound; no RNA screen, not formal MIMAG HQ',
        old_scores_recomputed=False, targets=binding(output / 'targets.tsv'),
        per_bin_secondary=binding(output / 'bin-quality.tsv'))
    anchors = json.loads((ROOT / 'experiments/E032-biological-candidate-selection/comparison-review.json').read_text())['modes']
    criteria = dict(exact_Oral_fallback=True,
        no_E032_R95_or_T90_regression=all(v['delta_R95_percentage_points'] >= 0 and v['delta_T90'] >= 0
                                          for v in units.values()),
        stronger_E031_anchors={u: v['arms']['post']['primary']['bp_weighted_R95'] >= anchors[u]['prospective_anchor']['R95']
                              and v['arms']['post']['primary']['at_least_90_percent'] >= anchors[u]['prospective_anchor']['T90']
                              for u, v in units.items()},
        half_percentage_point_or_three_multi_T90=any(v['delta_R95_percentage_points'] >= .5
                                                     or v['delta_multi_contig_T90'] >= 3 for v in units.values()))
    criteria['joint_KEEP'] = (criteria['exact_Oral_fallback'] and criteria['no_E032_R95_or_T90_regression']
                             and all(criteria['stronger_E031_anchors'].values())
                             and criteria['half_percentage_point_or_three_multi_T90'])
    result.update(frozen_criteria=criteria, disposition='MODIFY_NOT_PROMOTED',
                  interpretation='Smaller R95 gains with target trade-offs; no new T90, strong anchors and joint KEEP unmet. Preserve optional path; do not tune to these labels.')
    write(output / 'comparison-review.json', result)
    return result


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    print(summarize(**vars(parser.parse_args()))['status'])
