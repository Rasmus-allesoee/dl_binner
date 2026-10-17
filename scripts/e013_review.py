#!/usr/bin/env python3
"""Independently review sealed E013 cached refinements using admitted sequence truth.

Consumes completed partitions only; never proposes/selects bins or modifies the
frozen rule. All-DNA exports, full reference denominators and paired baselines
remain distinct from marker proxy scores and restricted contig metrics.
"""
import argparse
from collections import defaultdict
import importlib.util
import json
from pathlib import Path
import resource
import sys
import time

sys.path.insert(0, str(Path(__file__).absolute().parent))
from e009_common import binding, write_json
from e009_evaluate import read_partition
from e009_controls_review import diagnostics
from e010_review import require, refinement_membership
from e011_review import grouping_diagnostics
from e012_marker_audit import verify_truth
from e012_review import population_cells
from e013_control import REPO, EXP


def verify_choices(pre, old, part, decisions, alternatives):
    """Independently compare complete saved alternatives, noise and reasons by sets."""
    refinement_membership(pre, part)
    parents = defaultdict(list)
    for i, p in enumerate(pre['assignment']):
        if p >= 0:
            parents[p].append(i)
        else:
            require(pre['reason'][i] == part['reason'][i], 'Prior noise/excluded reason changed')
    ledgers = {a['pre_bin']: a for a in alternatives}; chosen = {d['pre_bin']: d['selected'] for d in decisions}
    require(len(ledgers) == len(alternatives) == len(decisions) == len(chosen)
            and set(ledgers) == set(chosen) <= set(parents), 'Duplicate/truncated/unknown alternative ledger')
    for p, members in parents.items():
        route = chosen.get(p, 'parent')
        options = [v for v in ledgers.get(p, {}).get('alternatives', []) if v['route'] == route]
        require(route == 'parent' or len(options) == 1, 'Unknown/duplicate selected route')
        want = [members] if route == 'parent' else options[0]['groups']
        expected_groups = {frozenset(c) for c in want}; actual = defaultdict(list)
        flat = [i for c in want for i in c]
        require(len(flat) == len(set(flat)) and set(flat) <= set(members), 'Alternative duplicate/cross-parent DNA')
        for i in members:
            if part['assignment'][i] >= 0: actual[part['assignment'][i]].append(i)
        require({frozenset(c) for c in actual.values()} == expected_groups, 'Selected whole alternative differs')
        expected_noise = set(members)-set(flat)
        require({i for i in members if part['assignment'][i] < 0} == expected_noise, 'Selected noise differs')
        if route != 'parent':
            decision = next(d for d in decisions if d['pre_bin'] == p)
            require(next(v['eligible'] for v in decision['alternatives'] if v['route'] == route), 'Selected rejected alternative')
        for i in members:
            expected_reason = old['reason'][i] if route == 'retained' and i in expected_noise else pre['reason'][i]
            require(part['reason'][i] == expected_reason, 'Selected alternative reason differs')
    return dict(no_merge_or_new_assignment=True, complete_alternatives_checked=len(parents))


def review(root, output):
    """Recheck complete exports/alternatives and pair every target with frozen controls."""
    from dl_binner.accounting import summarize_arm
    root, output = Path(root), Path(output); output.mkdir(parents=True, exist_ok=False)
    started = time.monotonic(); cpu = time.process_time()
    lock = json.loads((EXP/'input-lock.json').read_text()); rlock = json.loads((EXP/'review-lock.json').read_text())
    done = json.loads((root/'completed.json').read_text()); inputs = REPO/lock['cache']/'candidate'
    require(done['status'] == 'SUCCESS' and not done['truth_accessed'] and done['encoder_graph_seed_unchanged']
            and done['input_lock'] == binding(EXP/'input-lock.json') and done['protocol'] == binding(EXP/'protocol.json'),
            'No successful frozen E013 control')
    for key, name in [('partition', 'partition.json'), ('decisions', 'decisions.json'), ('alternatives', 'alternatives.json'),
                      ('quality_evidence', 'quality-evidence.json'), ('context_transforms', 'context-transforms.json'), ('graph_audit', 'selected-graph-audit.json')]:
        require(binding(root/name) == done[key], 'Completed E013 member differs: '+name)
    require(binding(REPO/rlock['E012_raw_review_path']) == rlock['E012_raw_review']
            and binding(REPO/'experiments/E012-marker-acceptance/review.json') == rlock['E012_review'], 'Accepted E012 control differs')
    previous = json.loads((REPO/rlock['E012_raw_review_path']).read_text())
    truth_root = verify_truth(rlock); truth = json.loads((truth_root/'truth.json').read_text())
    targets = json.loads((truth_root/'targets.json').read_text()); pop = json.loads((REPO/rlock['population_path']).read_text())
    pre, old = [json.loads((REPO/p).read_text()) for p in lock['contexts']['CPM']]
    part = json.loads((root/'partition.json').read_text()); decisions = json.loads((root/'decisions.json').read_text())
    alternatives = json.loads((root/'alternatives.json').read_text()); evidence = json.loads((root/'quality-evidence.json').read_text())
    choice_check = verify_choices(pre, old, part, decisions, alternatives)
    accounting = summarize_arm(inputs/'features/features.npz', root/'export')[0]
    require(accounting == done['accounting'], 'Independent all-DNA accounting differs')
    rows, assignments = read_partition(root/'export/assignments.tsv', truth)
    require([assignments[q] for q in part['ids']] == [f'bin_{v+1:06d}' if v >= 0 else None for v in part['assignment']], 'Export labels differ')
    clean = json.loads((inputs/'markers/evidence.json').read_text())['clean']
    grouped = grouping_diagnostics(truth, rows, pop, targets, clean); checked = diagnostics(truth, rows, part, pop, targets)
    require(grouped['recovery'] == checked['recovery'], 'Full-denominator contracts disagree')
    for key in ['precision', 'recall', 'f1']:
        require(abs(grouped['restricted_B3'][key]-checked['restricted_B3'][key]) < 1e-12, 'Independent B3 differs')
    require(checked['geometry'] == previous['arms']['CPM']['retained_geometry'], 'Native neighbor geometry changed')
    old_targets = {r['genome']: r for r in previous['arms']['CPM']['targets']}
    require(set(old_targets) == set(targets['targets']), 'Frozen target axes differ')
    pairs = []
    for r in grouped['recovery']:
        b = old_targets[r['genome']]; require(r['reference_bp'] == b['reference_bp'], 'Provided reference length differs')
        pairs.append(dict(genome=r['genome'], reference_bp=r['reference_bp'], protected_CPM_bp=b['selected_bp'],
            old_refinement_bp=b['old_children_bp'], candidate_bp=r['recovered_bp'],
            delta_vs_protected_bp=r['recovered_bp']-b['selected_bp'], delta_vs_old_bp=r['recovered_bp']-b['old_children_bp']))
    spec = importlib.util.spec_from_file_location('e010_sources', REPO/'experiments/E010-coherent-prototype/review_diagnostics.py')
    source = importlib.util.module_from_spec(spec); spec.loader.exec_module(source)
    graph = json.loads((root/'selected-graph-audit.json').read_text())
    result = dict(status='SUCCESS', completed=binding(root/'completed.json'), truth=rlock['manifest'], choices=choice_check,
        diagnostics=grouped, retained_geometry=checked['geometry'], accounting=accounting,
        all_populations=population_cells(rows, truth, pop, clean),
        source_bins=source.bin_sources(rows, truth, pop, targets['targets']), targets=pairs,
        baseline_summary=previous['baseline_summary'], selection=done['selection'], new_proposals=done['new_proposals'],
        selected_negative_graph_gains=sum(not r['graph_gain_positive'] for r in graph.values()),
        paired=dict(gained_vs_protected=sum(p['delta_vs_protected_bp'] > 0 for p in pairs),
                    lost_vs_protected=sum(p['delta_vs_protected_bp'] < 0 for p in pairs),
                    total_delta_vs_protected_bp=sum(p['delta_vs_protected_bp'] for p in pairs),
                    gained_vs_old=sum(p['delta_vs_old_bp'] > 0 for p in pairs), lost_vs_old=sum(p['delta_vs_old_bp'] < 0 for p in pairs),
                    total_delta_vs_old_bp=sum(p['delta_vs_old_bp'] for p in pairs)),
        limits=['one development assembly; no generalization, optimality or product feature-family verdict',
                '3.3034% N-quarantine; full provided reference denominators and all-bin DNA purity; not MAG quality',
                'panel/lineage-dependent marker proxies are not calibrated completeness/contamination',
                'no new AMBER, inference, detector, neighbors, aligner, external tool or cloud phase',
                'original strict Mac allclose failure preserved; original native vectors unchanged'],
        local_resources=dict(wall_seconds=time.monotonic()-started, process_cpu_seconds=time.process_time()-cpu,
            peak_own_RSS_native_units=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss, platform=sys.platform))
    write_json(output/'review.json', result)
    print('E013_REVIEW', grouped['recovery_summary'], result['paired'], flush=True)
    return result


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__); p.add_argument('--root', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True); a = p.parse_args(); review(a.root, a.output)
