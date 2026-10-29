#!/usr/bin/env python3
"""New isolated review entrypoints; preserve incomplete historical E025 CLI bytes.

No evaluation is automatic. A stopped-provider/member/cost admission and exact
new-output contracts precede truth. `--legacy-e025 --contracts-only` tests the
repaired external-data argument path without opening truth or rescoring anything.
"""
import argparse
from collections import Counter
import csv
import json
from pathlib import Path
import sys

ROOT = Path(__file__).absolute().parents[1]
sys.path[:0] = [str(ROOT/'scripts'), str(ROOT/'src')]
from e024_coverage import binding, write
from e022_review import admission_contract
from e014_review import read, require, manifest_bindings
from e017_review import export_contract


def review_inputs(unit, done, review_paths=None):
    """Resolve external copies by bytes without rewriting native receipts or caches.

    A native Oral receipt contains native absolute paths. Review uses its exact
    admitted bytes and explicit local feature/graph/marker mappings; it must not
    dereference those old paths or reconstruct/reinfer a native vector bank.
    Original vector verification is the bound native in-place contract, not a
    claimed local reread or a relaxed Mac portability check.
    """
    import numpy as np
    from dl_binner.multiview.views import load
    from dl_binner.multiview.arrays import load_arrays
    paths = dict(unit if review_paths is None else review_paths)
    needed = ['features', 'graph', 'marker_evidence']+(['receipt'] if unit.get('receipt') else [])
    for key in needed:
        require(unit[key] == done['inputs'][key]['path'], 'Native unit locator differs from completed provenance')
        require(key in paths and binding(paths[key]) == {k: done['inputs'][key][k] for k in ['bytes', 'sha256']},
                'External review input binding differs: '+key)
    for key in ['features', 'graph']:
        metadata = Path(paths[key]).with_suffix('.json')
        require(binding(metadata) == {k: done['inputs'][key+'_metadata'][k] for k in ['bytes', 'sha256']},
                'External review metadata binding differs: '+key)
    data, meta = load(paths['features'])
    graph, gm = load_arrays(paths['graph'], 'candidate_sparse_graph')
    valid = data['eligible']; nn = graph['neighbors']; n = len(data['ids'])
    require(graph['ids'].tolist() == data['ids'].tolist() and nn.ndim == 2 and nn.shape[0] == n
            and nn.dtype.kind in 'iu' and np.all(nn[~valid] == -1)
            and gm['embedding_sha256'] == done['inputs']['embeddings']['sha256'],
            'Local native sparse axis/vector provenance differs')
    for i in np.flatnonzero(valid):
        row = nn[i]
        require(np.all((row >= 0) & (row < n)) and i not in row
                and len(set(map(int, row))) == len(row) and np.all(valid[row]),
                'Malformed native display-neighbour row')
    require(done['samples'] == meta['samples'] and done['rows'] == n
            and done['bp'] == int(data['lengths'].sum()), 'Completed full data/sample axis differs')
    if unit.get('receipt'):
        receipt = read(paths['receipt'])
        require(receipt['status'] == 'PASS' and receipt['all_cells_observed'] is True
                and receipt['training_cache_rewritten'] is False and receipt['native_vector_bytes_unchanged'] is True
                and receipt['files']['rebound_features'] == binding(paths['features'])
                and receipt['files']['original_embeddings'] == {k: done['inputs']['embeddings'][k] for k in ['bytes', 'sha256']},
                'Admitted grouping-only Oral receipt differs')
    return data, meta, graph, paths


def contracts(unit, unit_root, inventory, admission, review_paths=None):
    """Read actual numeric/partition/export contracts without truth or new grouping."""
    from dl_binner.calibrated.fusion import policy
    from dl_binner.calibrated.arrays import load
    from dl_binner.information.export import validate_partition
    admitted = admission_contract(admission); root = Path(unit_root)
    done = read(root/'group/completed.json')
    require(done['policy'] == policy() and done['status'] == 'SUCCESS'
            and done['truth_accessed'] is False and done['learning_changed'] is False
            and read(root/'audited/done.json')['proof']['status'] == 'PASS',
            'Native fixed-learning completion/reload proof absent')
    data, meta, original, paths = review_inputs(unit, done, review_paths)
    cache, cm = load(root/'group/retrieval/neighbors.npz', 'calibrated_core_neighbors', data['ids'])
    require(cm['audit'] == done['retrieval_audit'] and cm['audit']['status'] == 'PASS', 'New-score recall gate absent')
    inv = read(inventory); prefix = 'units/'+root.name+'/'
    require(all(v == inv['all_work_members'][prefix+'group/'+k] for k, v in done['files'].items()),
            'Native complete grouping seal and all-member inventory differ')
    # Independent structural reload: no native path dereference, MST or search.
    import numpy as np
    forest, fm = load(root/'group/forest.npz', 'calibrated_biological_forest', data['ids'])
    cores = np.array(sorted(np.flatnonzero(data['eligible'] & (data['lengths'] >= 2500)),
                            key=lambda i: str(data['ids'][i])), np.int64)
    queries = np.array(sorted(np.flatnonzero(data['eligible']), key=lambda i: str(data['ids'][i])), np.int64)
    require(np.array_equal(cache['cores'], cores) and np.array_equal(cache['queries'], queries)
            and fm['retrieval'] == binding(root/'group/retrieval/neighbors.npz')
            and fm['features'] == binding(paths['features']), 'Local core/full-query/forest binding differs')
    n, size = len(cores), len(forest['mass']); seen = np.zeros(size, np.int32)
    require(n <= size <= max(n, 2*n-1) and forest['children'].shape == (size, 2)
            and np.array_equal(forest['mass'][:n], data['lengths'][cores]), 'Local forest leaf accounting differs')
    for node in range(n, size):
        a, b = map(int, forest['children'][node])
        require(0 <= a < b < node and forest['mass'][node] == forest['mass'][a]+forest['mass'][b]
                and forest['count'][node] == forest['count'][a]+forest['count'][b]
                and forest['level'][node] >= max(forest['level'][a], forest['level'][b]),
                'Local forest parent/child accounting differs')
        seen[a] += 1; seen[b] += 1
    require(np.all(seen <= 1) and np.array_equal(forest['roots'], np.flatnonzero(seen == 0)),
            'Local forest roots do not cover every core exactly once')
    accounts = {}
    for arm in ['core', 'recruited']:
        p = root/'group'/(arm+'-partition.json')
        require(binding(p) == inv['all_work_members'][prefix+'group/'+p.name], 'New partition archive binding differs')
        part = validate_partition(data, p, paths['features'])
        manifest_bindings(read(root/'export'/arm/'manifest.json'), prefix+'export/'+arm, inv['all_work_members'])
        _, accounts[arm] = export_contract(part, data, root/'export'/arm)
    return admitted, data, meta, cache, accounts, original, paths


def disposition(results, anchors):
    """Apply frozen joint practical criteria; no per-bin or per-community routing."""
    keys = ['bp_weighted_R95', 'at_least_50_percent', 'at_least_90_percent']
    nonregression = all(results[d][k] >= anchors[d][k] for d in ['E009', 'oral'] for k in keys)
    meaningful = any(results[d]['bp_weighted_R95'] >= anchors[d]['bp_weighted_R95']+.005 for d in ['E009', 'oral'])
    if nonregression and meaningful: return 'KEEP'
    improved = any(results[d][k] > anchors[d][k] for d in ['E009', 'oral'] for k in keys)
    return 'MODIFY' if improved else 'ABANDON_THIS_FROZEN_POLICY'


def core_neighborhood_diagnostics(data, cache, labels, targets, clean):
    """Describe retained new query-to-core links, never build/search a neighbour index.

    Unknown/non-target queries and unknown endpoints remain explicit. This core
    target population differs from E025 all-eligible retrieval; no matched search
    improvement is inferred. Five-edge means use each actual available row count.
    """
    from collections import defaultdict
    cells = defaultdict(lambda: dict(queries=0, query_bp=0, attributable_queries=0,
        attributable_bp=0, same_origin_sum=0., same_origin_weighted_bp=0., edges=0,
        unknown_endpoints=0))
    edge_cells = defaultdict(lambda: dict(edges=0, query_bp_repeated=0., same_origin_weighted_bp=0.))
    ids = data['ids'].tolist(); is_core = set(map(int, cache['cores']))
    positive = (data['depth'] > 0).any(1)
    depth_status = lambda i: ('depth_absent' if not data['depth'].shape[1] else
                              'positive' if positive[i] else 'measured_zero')
    for at, i in enumerate(cache['queries']):
        g = labels[i]; bp = int(data['lengths'][i]); n = min(5, int(cache['counts'][at]))
        near = cache['cores'][cache['neighbors'][at, :n]]
        origin = 'unknown' if g is None else 'target' if g in targets else 'non_target'
        lower = max(x for x in [0, 500, 768, 1000, 2500, 10000] if bp >= x)
        key = '|'.join([str(lower), origin, 'core' if int(i) in is_core else 'noncore',
                        depth_status(i), 'clean_marker' if ids[i] in clean else 'marker_negative'])
        row = cells[key]; row['queries'] += 1; row['query_bp'] += bp; row['edges'] += n
        row['unknown_endpoints'] += sum(labels[j] is None for j in near)
        if g is not None and n:
            same = sum(labels[j] == g for j in near)/n
            row['attributable_queries'] += 1; row['attributable_bp'] += bp
            row['same_origin_sum'] += same; row['same_origin_weighted_bp'] += bp*same
        for j in near:
            key = depth_status(i)+'->'+depth_status(j)
            e = edge_cells[key]; e['edges'] += 1; e['query_bp_repeated'] += bp
            if g is not None and labels[j] == g: e['same_origin_weighted_bp'] += bp
    return dict(cells=dict(cells), availability_edges=dict(edge_cells),
        all_queries=sum(v['queries'] for v in cells.values()), full_input_rows=len(ids),
        excluded_or_nonquery_rows=len(ids)-len(cache['queries']),
        meaning='Provided origins/AMBER-attributable labels, not exhaustive unique support; unknown endpoints remain; new core target pool is different from retained all-eligible search')


def review(unit, unit_root, inventory, admission, output, dataset, marker_clean, truth_root, review_paths=None):
    """Evaluate only two new partitions with existing independently tested truth APIs.

    Original native display neighbours are restored in memory from the byte-bound
    sparse input, explicitly distinguished from the new bipartite core retrieval.
    They are never rewritten into accepted or new scientific partition artifacts.
    """
    from threadpoolctl import threadpool_limits
    from dl_binner.information.export import validate_partition
    from dl_binner.density.bin_quality import summarize
    from e014_review import diagnostics, grouping_diagnostics, population_cells, oral_labels, oral_population
    from e023_review import oral_secondary_rows
    from e025_review import coverage_populations
    from e012_marker_audit import verify_truth
    from e014_oral_truth import evaluate
    threadpool_limits(4)
    admitted, data, meta, cache, account, original, paths = contracts(unit, unit_root, inventory, admission, review_paths)
    root, output = Path(unit_root), Path(output); output.mkdir(parents=True, exist_ok=False)
    ids = data['ids'].tolist(); clean = set(read(marker_clean)['clean'])
    valid = data['eligible']
    native_neighbors = [[ids[j] for j in original['neighbors'][i, :5]] if valid[i] else [] for i in range(len(ids))]
    result = dict(status='SUCCESS', dataset=dataset, admission=admitted, arms={},
        scope='New outputs only; fixed native display geometry; separate new query-to-core population',
        original_Mac_portability_tolerance_unchanged=True, primary_rule_changed=False)
    protocol = read(ROOT/'experiments/E026-calibrated-evidence-fusion/protocol.json')
    for path, wanted in protocol['baseline_summaries'].items(): require(binding(ROOT/path) == wanted, 'Retained baseline changed')
    if dataset == 'E009':
        lock = read(ROOT/'experiments/E013-marker-quality/review-lock.json')
        source = verify_truth(lock); truth = read(source/'truth.json'); targets = read(source/'targets.json')
        pop = read(ROOT/lock['population_path']); require(ids == truth['ordered_contig_ids']
            and len(targets['targets']) == 156, 'E009 truth full axis/denominator differs')
        labels = [truth['contigs'][q]['AMBER_label'] for q in ids]
        result['new_core_neighborhoods'] = core_neighborhood_diagnostics(data, cache, labels, targets['targets'], clean)
    else:
        lab, quarantine, shared, genomes, truth = oral_labels(truth_root, ids, data['lengths'])
        require(len(truth['targets']) == 799 and sum(truth['targets'].values()) == 2083072211
                and meta['fasta_sha256'] == truth['model_input']['sha256'], 'Full Oral reference/input contract differs')
        labels = [genomes[int(i)] if i >= 0 else None for i in lab]
        result['new_core_neighborhoods'] = core_neighborhood_diagnostics(data, cache, labels, truth['targets'], clean)
    for arm in ['core', 'recruited']:
        path = root/'group'/(arm+'-partition.json'); part = validate_partition(data, path, paths['features'])
        rows, _ = export_contract(part, data, root/'export'/arm)
        part['neighbors'] = native_neighbors  # Explicit display adapter, not a changed assignment/cache.
        assignments = {q: b if b >= 0 else None for q, b in zip(ids, part['assignment'])}
        if dataset == 'E009':
            primary = diagnostics(truth, rows, part, pop, targets)
            grouped = grouping_diagnostics(truth, rows, pop, targets, clean)
            require(primary['recovery'] == grouped['recovery'], 'Independent E009 recovery readers disagree')
            secondary = {'conservative_sequence': summarize(({**truth['contigs'][q], 'id': q} for q in ids),
                assignments, truth['reference_axis'], targets['genome_lengths'], targets['targets'])}
            value = dict(diagnostics=primary, grouping=grouped,
                populations=population_cells(rows, truth, pop, clean), secondary=secondary)
        else:
            primary = evaluate(truth_root, path, output/('truth-'+arm))
            refs = truth['references']; lengths = Counter()
            for ref in refs.values(): lengths[ref['genome']] += ref['length']
            secondary = {mode: summarize(oral_secondary_rows(Path(truth_root)/'rows.jsonl.gz', refs, mask),
                assignments, refs, lengths, truth['targets']) for mode, mask in [('provided_origin', False), ('known_shared_sensitivity', True)]}
            value = dict(evaluation=primary, grouping=oral_population(part, data, lab, quarantine, shared, genomes, truth['targets'], clean),
                measured_depth_population=coverage_populations(data, part, lab, genomes, truth['targets'], clean), secondary=secondary)
        value['export_contract'] = account[arm]; result['arms'][arm] = value
        for mode, table in secondary.items():
            with (output/('bin-quality-'+arm+'-'+mode+'.tsv')).open('x') as f:
                fields = list(table['bins'][0]) if table['bins'] else ['bin_id']
                writer = csv.DictWriter(f, fieldnames=fields, delimiter='\t', lineterminator='\n')
                writer.writeheader(); writer.writerows(table['bins'])
    write(output/'review.json', result)
    return result


def cli(argv=None):
    """Expose every external-data argument through the actual isolated production argv."""
    p = argparse.ArgumentParser(description=__doc__); p.add_argument('--legacy-e025', action='store_true')
    p.add_argument('--contracts-only', action='store_true')
    for name in ['unit', 'unit-root', 'work', 'inventory', 'admission', 'marker-clean', 'truth-root',
                 'output', 'external-features', 'external-receipt']:
        p.add_argument('--'+name, type=Path)
    p.add_argument('--review-paths', type=Path)
    p.add_argument('--dataset', choices=['E009', 'oral']); a = p.parse_args(argv)
    needed = ['inventory', 'admission', 'output'] + (['work', 'external_features', 'external_receipt'] if a.legacy_e025 else ['unit', 'unit_root'])
    if not a.contracts_only: needed += ['marker_clean', 'truth_root'] + ([] if a.legacy_e025 else ['dataset'])
    if any(getattr(a, k) is None for k in needed): p.error('Missing explicit review/external-data arguments')
    if a.legacy_e025:
        import e025_review as legacy
        if a.contracts_only:
            legacy.contracts(a.work, a.inventory, a.admission, a.external_features, a.external_receipt)
            value = dict(status='PASS', legacy_E025_external_arguments=True, truth_opened=False)
        else:
            return legacy.review(a.work, a.inventory, a.admission, a.marker_clean, a.truth_root,
                                  a.output, a.external_features, a.external_receipt)
    elif a.contracts_only:
        contracts(read(a.unit), a.unit_root, a.inventory, a.admission, read(a.review_paths) if a.review_paths else None)
        value = dict(status='PASS', actual_new_output_contracts=True, truth_opened=False)
    else:
        return review(read(a.unit), a.unit_root, a.inventory, a.admission, a.output, a.dataset, a.marker_clean, a.truth_root,
                      read(a.review_paths) if a.review_paths else None)
    write(a.output, value); return value


if __name__ == '__main__': cli()
