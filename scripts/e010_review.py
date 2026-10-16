#!/usr/bin/env python3
"""Inspect one retained dev4 candidate without fitting, detection or regrouping.

The operator verifies shutdown and archive/member bytes first. This reader checks
source/runtime/input journals, actual windows, reload, unchanged unit geometry,
cached markers and complete exports. It reuses the tested sequence-truth evaluator
for new local diagnostics. No cloud API, input acquisition or candidate selection.
"""
import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import resource
import signal
import sys
import time
sys.path.insert(0, str(Path(__file__).absolute().parent))
from e009_common import binding, write_json
from e009_controls_review import diagnostics, BOUNDS
from e009_evaluate import read_partition


def require(condition, message):
    """Refuse an invalid retained contract, independently of Python assertion flags."""
    if not condition:
        raise ValueError(message)


def unit_neighbors(vectors, ids, valid, neighbors, matrix, k, queries=128):
    """Check native unit vectors and sampled exact thresholds without a new index.

    All native rows/IDs and top-five exports are checked. The first SHA256-ID
    queries receive independent exact cosine cutoffs at k and five. Ties within
    1e-6 follow the predeclared production audit. This is no global recall proof.
    """
    import numpy as np
    x = np.asarray(vectors); valid = np.asarray(valid, bool); matrix = np.asarray(matrix)
    n = len(ids); selected = np.flatnonzero(valid)
    require(x.ndim == 2 and x.shape[0] == n and valid.shape == (n,)
            and len(set(ids)) == n and np.isfinite(x).all(), 'Invalid embedding axes/values')
    require(np.allclose(np.linalg.norm(x[valid], axis=1), 1, atol=1e-5)
            and np.count_nonzero(x[~valid]) == 0, 'Geometry is not unchanged unit sphere')
    require(matrix.shape == (n, k) and matrix.dtype.kind in 'iu'
            and np.all(matrix[~valid] == -1), 'Invalid native graph neighbor axis')
    m = matrix[valid]
    require(np.all((m >= 0) & (m < n)) and np.all(valid[m])
            and not np.any(m == selected[:, None])
            and not np.any(np.diff(np.sort(m, axis=1), axis=1) == 0), 'Invalid native neighbor membership')
    require(len(neighbors) == n, 'Native top-five axis differs')
    for i in range(n):
        expected = [ids[j] for j in matrix[i, :5]] if valid[i] else []
        require(neighbors[i] == expected, 'Native top-five and graph differ: '+ids[i])
    chosen = sorted(selected, key=lambda i: hashlib.sha256(ids[i].encode()).digest())[:queries]
    z = x[selected].astype(np.float64)
    result = []
    for i in chosen:
        exact = np.clip(z @ x[i].astype(np.float64), -1, 1)
        exact[selected == i] = -np.inf
        cutoff = np.partition(exact, -k)[-k]
        fifth = np.partition(exact, -5)[-5]
        actual = np.clip(x[matrix[i]].astype(np.float64) @ x[i].astype(np.float64), -1, 1)
        require(not np.any(np.diff(actual) > 1e-12), 'Native cosine rerank differs')
        result.append(dict(id=ids[i], recall_k=float(np.mean(actual >= cutoff-1e-6)),
                           recall_5=float(np.mean(actual[:5] >= fifth-1e-6))))
    return dict(metric='retained unit vectors, cosine; no post-learning z-score', queries=result,
                native_rows_checked=int(valid.sum()), native_neighbor_entries=int(m.size),
                query_selection='first128 SHA256(contigID), label blind', tolerance=1e-6,
                mean_recall_k=float(np.mean([r['recall_k'] for r in result])),
                mean_recall_5=float(np.mean([r['recall_5'] for r in result])))


def refinement_membership(pre, post):
    """Check that refinement only splits/unassigns old bins and preserves invalid DNA."""
    require(pre['ids'] == post['ids'] and pre['valid'] == post['valid']
            and pre['neighbors'] == post['neighbors'], 'Refinement axes/geometry changed')
    require(len(pre['assignment']) == len(post['assignment']) == len(pre['valid']) == len(pre['ids'])
            and len(pre['neighbors']) == len(pre['ids'])
            and all(type(v) is int and v >= -1 for v in pre['assignment']+post['assignment']),
            'Malformed/truncated refinement assignments')
    parents = defaultdict(set); changes = Counter()
    for before, after, valid in zip(pre['assignment'], post['assignment'], pre['valid']):
        require(valid or (before < 0 and after < 0), 'Invalid geometry became assigned')
        if after >= 0:
            require(before >= 0, 'Refinement newly assigned prior noise')
            parents[after].add(before)
        changes['assigned_to_noise' if before >= 0 and after < 0 else 'remains_assigned' if after >= 0 else 'remains_noise_or_excluded'] += 1
    require(all(len(v) == 1 for v in parents.values()), 'Refinement merged old bins')
    return dict(counts=dict(changes), no_merge_or_new_assignment=True)


def sparse_graph_contract(edges, weights, ids, valid):
    """Check undirected native edges ordered by opaque ID, not FASTA row number."""
    import numpy as np
    edges = np.asarray(edges); weights = np.asarray(weights); valid = np.asarray(valid, bool)
    require(edges.ndim == 2 and edges.shape[1] == 2 and edges.dtype.kind in 'iu'
            and len(edges) == len(weights) and weights.ndim == 1
            and np.all((edges >= 0) & (edges < len(ids)))
            and np.all(np.isfinite(weights) & (weights > 0) & (weights <= 1)), 'Malformed sparse edge/weight contract')
    # The writer builds its graph after sorting eligible opaque IDs, then maps
    # endpoints back to the original FASTA axis. Integer endpoint order can flip.
    rank = np.empty(len(ids), np.int64)
    rank[sorted(range(len(ids)), key=lambda i: ids[i])] = np.arange(len(ids))
    require(np.all(rank[edges[:,0]] < rank[edges[:,1]]) and np.all(valid[edges])
            and len(np.unique(edges, axis=0)) == len(edges), 'Duplicate/ineligible/noncanonical sparse edge')
    return dict(edges=len(edges), endpoint_order='opaque-ID lexicographic, mapped to full FASTA row indices')


def review(a):
    """Check immutable native contracts and evaluate both retained partitions locally."""
    import numpy as np
    import torch
    from threadpoolctl import threadpool_limits
    from dl_binner.runner import source_records
    from dl_binner.candidate.runner import completed, STAGES
    from dl_binner.candidate.views import load
    from dl_binner.candidate.model import Encoder, infer, configure_torch
    from dl_binner.candidate.markers import load_cache
    from dl_binner.io import read_fasta, read_depth, load_arrays, digest, id_digest
    from dl_binner.accounting import summarize_arm
    start = time.perf_counter(); cpu = time.process_time()
    a.output.mkdir(parents=True, exist_ok=False)
    threadpool_limits(4); configure_torch(4)
    repo = Path(__file__).absolute().parents[1]; exp = repo/'experiments/E010-coherent-prototype'
    lock = json.loads((exp/'candidate-lock.json').read_text()); root = a.root/'candidate'
    require(source_records() == lock['package_files'], 'Local installed candidate differs from frozen source')
    for name, expected in lock['recipes'].items():
        require(binding(repo/name) == expected, 'Frozen execution recipe changed: '+name)
    manifest = json.loads((root/'run-manifest.json').read_text()); cfg = manifest['config']
    require(manifest['source'] == lock['package_files'] and cfg == lock['packaged_defaults']
            and manifest['inputs'] == lock['inputs'] and manifest['threads'] == 8
            and manifest['package_version'] == lock['package'], 'Native source/config/input/allocation differs')
    native_runtime = json.loads((a.root/'runtime.json').read_text())
    require(native_runtime['status'] == 'passed' and native_runtime['python_version'] == '3.12.10'
            and native_runtime['system'] == 'Linux' and not native_runtime['user_site_enabled'], 'Native runtime gate absent')
    installed = json.loads((a.root/'installed.json').read_text())
    require(installed == lock['package_files'], 'Native installed source lock differs')
    completed_rows = completed(root)
    done = json.loads((root/'completion.json').read_text())
    require(len(completed_rows) == 7 and done['checkpoint_reload_exact']
            and done['manifest_sha256'] == digest(root/'run-manifest.json'), 'Incomplete native stage chain')
    previous_end = None; stages = {}
    for name, row in zip(STAGES, completed_rows):
        r = row['resources']
        require(r['exit_code'] == 0 and r['stop_reason'] is None, 'Failed native stage: '+name)
        require(previous_end is None or row['start_monotonic_ns'] >= previous_end, 'Native stages overlap')
        previous_end = row['end_monotonic_ns']; stages[name] = r
    for name in ['runtime','installed-source','production-marker-contract','native-contracts','candidate']:
        r = json.loads((a.root/(name+'.exit.json')).read_text())
        require(r['exit_code'] == 0 and r['stop_reason'] is None, 'Failed prerequisite: '+name)
    data, meta, views, viewmeta = load(root/'features/features.npz', root/'features/views.npz')
    require(binding(a.fasta) == lock['inputs']['fasta'] and binding(a.depth) == lock['inputs']['depth'], 'Local accepted input differs')
    dna = read_fasta(a.fasta); ids = [q for q, _ in dna]; lengths = np.array([len(s) for _, s in dna])
    require(ids == data['ids'].tolist() and len(ids) == lock['contigs'] and int(lengths.sum()) == lock['bp']
            and np.array_equal(lengths, data['lengths']), 'Full DNA axis/length differs')
    hashes = [hashlib.sha256(s.encode()).hexdigest() for _, s in dna]
    require(hashes == data['sequence_sha256'].tolist(), 'Parent DNA hashes differ')
    samples, depth = read_depth(a.depth, ids)
    require(samples == lock['ordered_depth_columns'] == meta['samples'] and np.array_equal(depth, data['depth'])
            and np.array_equal(data['zero_depth'], depth == 0), 'Ordered full depth matrix differs')
    baseline, _ = load_arrays(a.baseline/'ten-depth/features/features.npz', 'features')
    require(np.array_equal(data['tnf'], baseline['tnf']) and np.array_equal(data['eligible'], baseline['eligible'])
            and np.array_equal(data['ids'], baseline['ids']), 'Candidate and dev3 parent population/features differ')
    window_count = 0
    for i, (_, sequence) in enumerate(dna):
        for j, (left, right) in enumerate(views['coordinates'][i]):
            if left < 0:
                continue
            require(hashlib.sha256(sequence[left:right].encode()).hexdigest() == views['sequence_sha256'][i,j], 'Actual window DNA differs')
            window_count += 1
    del dna, baseline, depth
    print('FULL_AXES_REAL_WINDOWS_PASS', len(ids), window_count, flush=True)
    checkpoint = json.loads((root/'train/checkpoint.json').read_text())
    require(checkpoint['config'] == cfg and checkpoint['samples'] == samples and checkpoint['threads'] == 8
            and checkpoint['loader_workers'] == 0 and checkpoint['training_parents'] == int(views['trainable'].sum()), 'Training contract differs')
    require(len(checkpoint['history']) == cfg['epochs'] and all(h['epoch'] == j+1 and h['parents_seen'] == checkpoint['training_parents']
            and np.isfinite([h['loss'], h['sequence_loss']]).all() for j,h in enumerate(checkpoint['history'])), 'Incomplete/changed epoch schedule')
    saved = torch.load(root/'train/checkpoint.pt', weights_only=True, map_location='cpu')
    require(saved['config'] == cfg and saved['samples'] == samples and saved['transform'] == checkpoint['transform'], 'Reload tensor schema differs')
    model = Encoder(len(samples), cfg); model.load_state_dict(saved['model_state'], strict=True)
    values, valid = infer(model, data, saved['transform'], cfg)
    embeddings, emeta = load_arrays(root/'embed/embeddings.npz', 'embeddings')
    reference, _ = load_arrays(root/'train/reference.npz', 'embeddings')
    require(np.array_equal(reference['features'], embeddings['features']) and np.array_equal(reference['evidence'], embeddings['evidence'])
            and emeta['reload_exact'], 'Native pre-save/reload arrays differ')
    require(np.array_equal(valid, embeddings['evidence']), 'Independent inference evidence mask differs')
    difference = np.abs(values-embeddings['features'])
    portability = dict(passed=bool(np.allclose(values, embeddings['features'], rtol=1e-5, atol=2e-6)),
        tolerance=dict(rtol=1e-5, atol=2e-6), max_absolute_error=float(difference.max()),
        coordinates_outside_tolerance=int((difference > 2e-6+1e-5*np.abs(embeddings['features'])).sum()),
        total_coordinates=int(difference.size), evidence_mask_equal=True,
        scope='Mac inference diagnostic; native Linux pre-save/reload parity is a separate exact contract')
    # Preserve the failed portability contract, never widen its tolerance or
    # replace native embeddings. Explicit evidence-only mode evaluates the
    # checksum-bound Linux outputs while reporting this unresolved limitation.
    require(portability['passed'] or a.native_artifact_diagnostics,
            'Independent cross-platform inference differs; native-artifact diagnostics require explicit scope')
    delta = portability['max_absolute_error']; del values, reference, views, model, saved, difference
    pre = json.loads((root/'group/partition.json').read_text()); post = json.loads((root/'refine/partition.json').read_text())
    require(pre['config'] == cfg and pre['transform'] == 'none; learned unit sphere preserved'
            and pre['embedding_sha256'] == digest(root/'embed/embeddings.npz')
            and pre['ids'] == ids and np.array_equal(pre['valid'], data['eligible'] & embeddings['evidence'])
            and pre['parent_features_sha256'] == digest(root/'features/features.npz'), 'Geometry/config binding changed')
    graph, gm = load_arrays(root/'group/graph.npz', 'candidate_sparse_graph')
    require(np.array_equal(graph['ids'], data['ids']) and gm['audit'] == pre['audit'] and pre['graph_sha256'] == digest(root/'group/graph.npz'), 'Graph binding differs')
    oracle = unit_neighbors(embeddings['features'], ids, pre['valid'], pre['neighbors'], graph['neighbors'], cfg['neighbors'])
    require([r['id'] for r in oracle['queries'][:cfg['audit_queries']]] == pre['audit']['query_ids'], 'Native audit query selection changed')
    rec = [r['recall_k'] for r in oracle['queries'][:cfg['audit_queries']]]
    require(np.mean(rec) == pre['audit']['mean_tie_aware_recall'] and min(rec) == pre['audit']['min_query_recall']
            and np.mean(rec) >= cfg['min_neighbor_recall'], 'Independent native audit differs')
    edges = graph['edges']; weights = graph['weights']
    graph_contract = sparse_graph_contract(edges, weights, ids, pre['valid'])
    print('UNIT_GEOMETRY_RELOAD_PASS', delta, oracle['mean_recall_k'], flush=True)
    marker = load_cache(root/'markers', a.fasta, ids)  # restore-only, re-reduces retained rows; never detection
    cache = json.loads((root/'markers/cache.json').read_text())
    require(cache['hmm'] == lock['inputs']['marker_hmm'] and cache['asset_manifest'] == lock['inputs']['marker_manifest'], 'Marker asset differs')
    require(post['marker_cache_sha256'] == digest(root/'markers/cache.json') and post['pre_partition_sha256'] == digest(root/'group/partition.json'), 'Refinement input binding differs')
    refinement = refinement_membership(pre, post)
    marker_lineage = defaultdict(Counter); marker_lengths = defaultdict(Counter)
    truth_manifest = a.truth/'manifest.json'; admission = json.loads((repo/'experiments/E009-competitive-benchmark/truth-v2-admission.json').read_text())
    require(admission['admitted'] and binding(truth_manifest) == admission['artifact_manifest'], 'Truth admission differs')
    for name, expected in json.loads(truth_manifest.read_text())['files'].items():
        require(binding(a.truth/name) == expected, 'Admitted truth member differs: '+name)
    truth = json.loads((a.truth/'truth.json').read_text()); targets = json.loads((a.truth/'targets.json').read_text())
    population = json.loads((repo/'experiments/E009-competitive-benchmark/truth-population-review.json').read_text())
    require(truth['ordered_contig_ids'] == ids, 'Truth axis differs')
    for i,q in enumerate(ids):
        label = truth['contigs'][q]['AMBER_label']; lineage = population['genomes'][label]['lineage_class'] if label else 'not_attributable'
        length = max(b for b in BOUNDS if int(data['lengths'][i]) >= b)
        for counter in [marker_lineage[lineage], marker_lengths[str(length)]]:
            counter['all_contigs'] += 1; counter['all_bp'] += int(data['lengths'][i])
            counter['clean_marker_contigs'] += q in marker['clean']; counter['clean_family_calls'] += len(marker['clean'].get(q,[]))
            counter['clean_marker_bp'] += int(data['lengths'][i]) if q in marker['clean'] else 0
    result = dict(source_commit='6917c3f027bb975db43e771e979fecda0ab6c415', source_lock=binding(exp/'candidate-lock.json'),
        frozen_confirmation=binding(exp/'confirmation-plan.json'), full_input_axes=True, contigs=len(ids), bp=int(lengths.sum()),
        depth_columns=samples, depth_cells=int(data['depth'].size), zero_depth_rows=int((data['depth']==0).all(1).sum()),
        training_parents=checkpoint['training_parents'], actual_DNA_windows_verified=window_count, config=cfg,
        native_stages=stages, training=checkpoint, native_reload_exact=True, independent_reload_max_absolute_error=delta,
        independent_reload_tolerance=dict(rtol=1e-5,atol=2e-6), cross_platform_reload=portability,
        native_artifact_diagnostics_only=a.native_artifact_diagnostics, geometry_oracle=oracle, sparse_edges=len(edges),
        graph_contract=graph_contract,
        marker=dict(genes=marker['gene_count'],domains=cache['domains'],profiles=marker['profile_count'],canonical_families=marker['canonical_families'],
            clean_contigs=len(marker['clean']),clean_family_calls=sum(map(len,marker['clean'].values())),ambiguous_proteins=len(marker['ambiguous']),
            multicopy_contig_families=len(marker['multicopy']),raw_cache_reduction_verified=True,by_lineage=dict(marker_lineage),by_length=dict(marker_lengths)),
        refinement=dict(**refinement,attempts=post['attempts'],unresolved=post['unresolved_conflicts']),arms={})
    native_accounting = json.loads((root/'export/accounting.json').read_text())['arms']
    for name, part in [('pre', pre), ('post', post)]:
        accounting, _ = summarize_arm(root/'features/features.npz', root/'export'/name)
        require(accounting == native_accounting[name], 'Independent all-DNA export/accounting differs')
        rows, assignment = read_partition(root/'export'/name/'assignments.tsv', truth)
        expected = [f'bin_{v+1:06d}' if v >= 0 else None for v in part['assignment']]
        require([assignment[q] for q in ids] == expected, 'Native partition/export differs')
        print('DIAGNOSTICS_ARM', name, flush=True)
        result['arms'][name] = dict(accounting=accounting, diagnostics=diagnostics(truth, rows, part, population, targets))
    result['local_resources'] = dict(wall_seconds=time.perf_counter()-start, process_CPU_seconds=time.process_time()-cpu,
        peak_own_RSS_native_units=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss, platform=sys.platform,threads=4,
        scope='read-only validation, reload inference and diagnostics; no fitting/marker detection/grouping')
    write_json(a.output/'review.json', result); print('REVIEW_COMPLETE',flush=True)


if __name__ == '__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for name in ['root','truth','fasta','depth','baseline','output']:p.add_argument('--'+name,type=Path,required=True)
    p.add_argument('--native-artifact-diagnostics', action='store_true',
        help='Explicitly evaluate original Linux bytes while retaining a failed Mac inference tolerance; no tolerance relaxation')
    a=p.parse_args()
    def expired(*_):raise TimeoutError('Local E010 review exceeded 15-minute bound')
    signal.signal(signal.SIGALRM,expired);signal.alarm(900)
    review(a)
