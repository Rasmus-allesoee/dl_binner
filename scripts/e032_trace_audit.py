#!/usr/bin/env python3
"""Audit closed E032 choice/update traces against already reviewed partitions.

No binner or evaluator runs here. Counts distinguish whole/residual candidates,
joint recruitment and recovery associated with single-contig bins. Origin truth
is used only after the native selection has finished, never as a selector.
"""
import argparse
from collections import Counter, defaultdict
import csv
import json
from pathlib import Path
import sys

ROOT = Path(__file__).absolute().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from e024_coverage import binding, write


def audit(base, output):
    """Check complete trace arithmetic and write bounded diagnostic summaries."""
    base, output = Path(base), Path(output)
    old = ROOT / 'artifacts/e031-bootstrap-preserving-learning/learning-inspection-20261103/summary/learning-targets.tsv'
    expected = json.loads((ROOT / 'experiments/E031-bootstrap-preserving-learning/learning-review.json').read_text())['target_table']
    if binding(old) != expected:
        raise ValueError('Retained target summary differs')
    with old.open() as handle:
        prior = {(r['unit'], r['genome']): r for r in csv.DictReader(handle, delimiter='\t')}
    result = dict(status='PASS', source_blind_native_selection=True,
        truth_used_only_for_completed_output_diagnostics=True,
        new_scores_fits_grouping_or_selection=False, modes={})
    for unit in ['E009-noGLM', 'E009-GLM', 'oral-noGLM']:
        folder = base / 'verified-all/work' / unit / 'select/result'
        read = lambda n: json.loads((folder / n).read_text())
        choices, pool, updates = read('choices.json'), read('candidates.json'), read('updates.json')
        raw = json.loads((base / ('review-' + unit) / 'review.json').read_text())
        selected = [r for r in choices if r['reason'].startswith('selected_')]
        pre, post = read('pre-partition.json'), read('post-partition.json')
        assigned_pre = raw['arms']['pre']['export_contract']['populations']['assigned']
        assigned_post = raw['arms']['post']['export_contract']['populations']['assigned']
        if (sum(r['stats']['rows'] for r in selected) != assigned_pre['contigs']
                or sum(r['stats']['bp'] for r in selected) != assigned_pre['bp']
                or len(selected) != pre['clusters'] or pre['clusters'] != post['clusters']):
            raise ValueError('Native choice/export accounting differs')
        accepted = [g for g in updates['groups'] if g['accepted']]
        if (sum(len(g['proposed_rows']) for g in accepted)
                != assigned_post['contigs'] - assigned_pre['contigs']):
            raise ValueError('Joint-update/export row accounting differs')
        by_kind = defaultdict(lambda: dict(bins=0, bp=0, contigs=0))
        for c in selected:
            source = pool[c['candidate']]
            key = source['key'].split(':', 1)[0] + '/' + source['kind'] + '/' + c['reason']
            for k, value in [('bins', 1), ('bp', c['stats']['bp']), ('contigs', c['stats']['rows'])]:
                by_kind[key][k] += value
        counts = Counter(v for v in post['assignment'] if v is not None and v >= 0)
        if unit.startswith('E009'):
            targets = raw['arms']['post']['grouping']['recovery']
            reference = raw['arms']['post']['grouping']['recovery_summary']['reference_bp']
            baseline = 'E023_selected_bp'
        else:
            targets = raw['arms']['post']['evaluation']['origin']['recovery']
            reference = raw['arms']['post']['evaluation']['origin']['recovery_summary']['reference_bp']
            baseline = 'E030_post_bp'
        singleton = [t for t in targets if t['best_bin'] is not None and counts[t['best_bin']] == 1]
        gained_t90_singleton = [t for t in singleton
            if 10*int(prior[unit, t['genome']][baseline]) < 9*t['reference_bp'] <= 10*t['recovered_bp']]
        result['modes'][unit] = dict(choice_reasons=dict(Counter(r['reason'] for r in choices)),
            selected_sources=dict(by_kind), selected_marker_negative_bins=sum(r['stats']['breadth'] == 0 for r in selected),
            joint_groups=len(updates['groups']), accepted_groups=len(accepted),
            recruitment_reasons=dict(Counter(r['reason'] for r in updates['proposals'])),
            assigned_bp_change=assigned_post['bp'] - assigned_pre['bp'],
            bins=post['clusters'], single_contig_bins=sum(n == 1 for n in counts.values()),
            T90_single_contig=sum(10*t['recovered_bp'] >= 9*t['reference_bp'] for t in singleton),
            new_T90_single_contig_versus_stronger_E031=len(gained_t90_singleton),
            single_contig_best_recovered_bp=sum(t['recovered_bp'] for t in singleton),
            single_contig_best_weighted_R95=sum(t['recovered_bp'] for t in singleton)/reference,
            full_reference_bp=reference,
            singleton_association_is_not_a_matched_component_ablation=True)
    write(output, result)
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    audit(args.base, args.output)
