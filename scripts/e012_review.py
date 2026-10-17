#!/usr/bin/env python3
"""Bounded sequence-truth diagnostics after restore-only selection has completed.

Truth never enters the selector. Full provided denominators, all exported DNA,
unknown/non-target populations and original N-quarantine remain explicit.
"""
import argparse
from collections import Counter, defaultdict
import csv
import importlib.util
import json
from pathlib import Path
import resource
import sys
import time

sys.path.insert(0, str(Path(__file__).absolute().parent))
from e009_common import binding, write_json
from e009_evaluate import read_partition
from e009_controls_review import diagnostics, BOUNDS
from e010_review import require, refinement_membership
from e011_review import grouping_diagnostics
from e012_acceptance import REPO, EXP, verify_inputs
from e012_marker_audit import verify_truth


def paired_targets(selected, previous, context):
    """Pair all targets, including zero recovery, with both preserved alternatives."""
    require({r['genome'] for r in selected} == {r['genome'] for r in previous}, 'Paired target set differs')
    old = {r['genome']: r for r in previous}; rows = []
    pre_key, post_key = ('RB-pre', 'RB-post') if context == 'RB' else ('cpm-pre', 'cpm-post')
    for r in selected:
        p = old[r['genome']]
        require(r['reference_bp'] == p['reference_bp'], 'Full provided reference length differs')
        before, child, after = p['recovered_bp'][pre_key], p['recovered_bp'][post_key], r['recovered_bp']
        rows.append(dict(genome=r['genome'], reference_bp=r['reference_bp'], parent_bp=before,
                         old_children_bp=child, selected_bp=after,
                         selected_minus_parent_bp=after-before, selected_minus_old_children_bp=after-child))
    return rows


def population_cells(rows, truth, population, clean):
    """Cross-tabulate every length/origin/eligibility/status/marker row, including unknowns."""
    table = defaultdict(Counter)
    for row in rows:
        q = row['contig_id']; item = truth['contigs'][q]; bp = item['length']; g = item['AMBER_label']
        lineage = population['genomes'][g]['lineage_class'] if g else 'not_attributable'
        low = max(b for b in BOUNDS if bp >= b)
        key = '|'.join([str(low), lineage, 'candidate_eligible' if bp >= 500 else 'candidate_excluded',
                        row['status'], 'clean_marker' if q in clean else 'no_clean_marker'])
        v = table[key]; v['contigs'] += 1; v['all_bp'] += bp
        for kind in ['ambiguous_query_bp', 'nn_quarantined_query_bp', 'unsupported_query_bp']:
            v[kind] += item[kind]
        for genome, confirmed in item['confirmed_query_bp'].items():
            v['confirmed_'+population['genomes'][genome]['lineage_class']+'_bp'] += confirmed
    require(sum(v['all_bp'] for v in table.values()) == sum(i['length'] for i in truth['contigs'].values()),
            'Population cross-tab lost DNA')
    return dict(keys=['lower_bp', 'attributable_lineage', 'candidate_eligibility', 'status', 'clean_marker'],
                cells={k: dict(v) for k, v in table.items()})


def review(run_root, output, base=REPO):
    """Independently recheck selection/export and evaluate without modifying any partition."""
    from dl_binner.accounting import summarize_arm
    base, run_root, output = Path(base), Path(run_root), Path(output)
    output.mkdir(parents=True, exist_ok=False); started = time.monotonic(); cpu = time.process_time()
    inputs = json.loads((base/'experiments/E012-marker-acceptance/input-lock.json').read_text())
    lock = json.loads((base/'experiments/E012-marker-acceptance/review-lock.json').read_text())
    verify_inputs(inputs, base); truth_root = verify_truth(lock, base)
    done = json.loads((run_root/'completed.json').read_text())
    require(done['status'] == 'SUCCESS' and done['truth_accessed'] is False
            and done['input_lock'] == binding(EXP/'input-lock.json')
            and done['protocol'] == binding(EXP/'protocol.json'), 'No successful frozen selection')
    for name, expected in lock['baseline_files'].items():
        require(binding(base/lock['baseline_root']/name) == expected, 'Accepted baseline differs: '+name)
    previous = json.loads((base/lock['baseline_root']/'grouping-diagnostics-v2.json').read_text())
    native_review = json.loads((base/lock['baseline_root']/'local-review-v3/review.json').read_text())
    truth = json.loads((truth_root/'truth.json').read_text()); targets = json.loads((truth_root/'targets.json').read_text())
    pop = json.loads((base/lock['population_path']).read_text())
    cache = base/inputs['cache']/'candidate'; evidence = json.loads((cache/'markers/evidence.json').read_text())
    result = dict(status='SUCCESS', selection=binding(run_root/'completed.json'), review_lock=binding(EXP/'review-lock.json'),
                  truth=lock['manifest'], baseline_summary=previous['summary'], arms={},
                  portability='Original E010 Mac allclose rtol1e-5/atol2e-6 failure remains; no inference or tolerance change',
                  limits=['one development assembly; no confirmation/generalization or product feature-family verdict',
                          '156 primary bacterial targets; no primary archaeal target',
                          'full supplied-reference R95, all-bin DNA purity; not MIMAG quality',
                          '3.3034% N-quarantine (7653205bp) remains unknown',
                          'restricted B3 omits unattributable truth labels; full-bin purity does not',
                          'no new AMBER execution; tested full-reference R95 and independent grouping diagnostics used'])
    spec = importlib.util.spec_from_file_location('e010_bin_sources', base/'experiments/E010-coherent-prototype/review_diagnostics.py')
    source = importlib.util.module_from_spec(spec); spec.loader.exec_module(source)
    for context, files in inputs['contexts'].items():
        pre, post = [json.loads((base/p).read_text()) for p in files]
        part_path = run_root/context/'partition.json'; decision_path = run_root/context/'decisions.json'
        require(binding(part_path) == done['contexts'][context]['partition']
                and binding(decision_path) == done['contexts'][context]['decisions'], 'New selection bytes differ')
        part = json.loads(part_path.read_text()); decisions = json.loads(decision_path.read_text())
        refinement_membership(pre, part)
        # Independent whole-alternative check: pairwise label equality and noise
        # must exactly match the chosen old alternative for each original parent.
        choices = {r['pre_bin']: r['accepted'] for r in decisions}; members = defaultdict(list)
        for i, parent in enumerate(pre['assignment']):
            if parent >= 0: members[parent].append(i)
        for parent, indices in members.items():
            reference = post if choices.get(parent, False) else pre
            forward, reverse = {}, {}
            for i in indices:
                want, have = reference['assignment'][i], part['assignment'][i]
                require((want < 0) == (have < 0), 'Selected alternative noise differs')
                require(reference['reason'][i] == part['reason'][i], 'Selected alternative reason differs')
                if want >= 0:
                    require(forward.setdefault(want, have) == have and reverse.setdefault(have, want) == want,
                            'Selected alternative partition differs')
        accounting, _ = summarize_arm(cache/'features/features.npz', run_root/context/'export')
        require(accounting == done['contexts'][context]['accounting'], 'Independent full-DNA accounting differs')
        rows, assignments = read_partition(run_root/context/'export/assignments.tsv', truth)
        require([assignments[q] for q in part['ids']] == [f'bin_{v+1:06d}' if v >= 0 else None for v in part['assignment']],
                'Export/partition label axis differs')
        grouped = grouping_diagnostics(truth, rows, pop, targets, evidence['clean'])
        checked = diagnostics(truth, rows, part, pop, targets)
        require(checked['recovery'] == grouped['recovery'], 'Evaluator recovery contracts disagree')
        for metric in ['precision', 'recall', 'f1']:
            require(abs(checked['restricted_B3'][metric]-grouped['restricted_B3'][metric]) < 1e-12,
                    'Independent B3 contracts disagree')
        # Every selected arm shares the original native top-five neighborhoods.
        require(checked['geometry'] == native_review['arms']['cpm-pre']['retained_geometry'],
                'Unchanged native neighborhood diagnostics differ')
        pairs = paired_targets(grouped['recovery'], previous['target_deltas'], context)
        result['arms'][context] = dict(accounting=accounting, decisions=decisions, diagnostics=grouped,
            retained_geometry=checked['geometry'], all_populations=population_cells(rows, truth, pop, evidence['clean']),
            source_bin_diagnostics=source.bin_sources(rows, truth, pop, targets['targets']),
            targets=pairs, paired=dict(
                recovered_bp_change_from_parent=sum(r['selected_minus_parent_bp'] for r in pairs),
                recovered_bp_change_from_old_children=sum(r['selected_minus_old_children_bp'] for r in pairs),
                targets_losing_vs_parent=sum(r['selected_minus_parent_bp'] < 0 for r in pairs),
                targets_gaining_vs_parent=sum(r['selected_minus_parent_bp'] > 0 for r in pairs),
                targets_losing_vs_old_children=sum(r['selected_minus_old_children_bp'] < 0 for r in pairs),
                targets_gaining_vs_old_children=sum(r['selected_minus_old_children_bp'] > 0 for r in pairs)))
        print('E012_REVIEW '+context+' '+json.dumps(grouped['recovery_summary']), flush=True)
    result['local_resources'] = dict(wall_seconds=time.monotonic()-started, process_cpu_seconds=time.process_time()-cpu,
        own_peak_rss_native_units=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss, platform=sys.platform)
    write_json(output/'review.json', result)
    return result


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--run', type=Path, required=True); p.add_argument('--output', type=Path, required=True)
    a = p.parse_args(); review(a.run, a.output)
