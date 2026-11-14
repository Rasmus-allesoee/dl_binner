#!/usr/bin/env python3
"""Inspect admitted graph tensors, fixed neighbors and link populations locally.

No model forward, fitting, search/index construction or truth-selected change is
performed. Native exact reload remains separate from failed Mac portability.
"""
import argparse
from collections import Counter
import gc
import json
from pathlib import Path
import sys

ROOT = Path(__file__).absolute().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from e024_coverage import binding, write
from e036_completed_inspection import require


def inspect(base, unit, features, marker_clean, output):
    """Check actual cached arrays/checkpoint and diagnose every DNA population."""
    import numpy as np
    import torch
    from threadpoolctl import threadpool_limits
    from dl_binner.genomegraph.model import policy
    from dl_binner.genomegraph.links import read as read_links
    from dl_binner.multiview.views import load
    from dl_binner.multiview.arrays import load_arrays
    from e010_review import unit_neighbors, sparse_graph_contract
    from e012_marker_audit import verify_truth
    from e014_review import parent_geometry, BOUNDS
    from e025_review import coverage_populations
    threadpool_limits(4)
    torch.set_num_threads(4)
    torch.set_num_interop_threads(1)
    base, features = Path(base), Path(features)
    require(unit in ['E009-noGLM', 'E009-GLM'], 'Only new E009 geometry is admitted')
    admission = json.loads((base / 'native-admission.json').read_text())
    require(admission['status'] == 'PASS_COMPLETED_SCIENCE_AND_DELIVERY_BEFORE_DIAGNOSTICS',
            'Independent native admission missing')
    inv = json.loads((base / 'inventory.json').read_text())['all_work_members']
    root = base / 'restored/work' / unit
    for n in ['node-features/result/features.npz', 'student/result/checkpoint.pt',
              'student/result/completed.json', 'student-embed/embeddings.npz',
              'student-graph/result/graph.npz']:
        require(binding(root / n) == inv[unit + '/' + n], 'Staged numeric byte drift')
    data, meta = load(features)
    a, am = load_arrays(root / 'node-features/result/features.npz', 'genome_graph_features')
    emb, em = load_arrays(root / 'student-embed/embeddings.npz', 'embeddings')
    graph, gm = load_arrays(root / 'student-graph/result/graph.npz', 'candidate_sparse_graph')
    require(np.array_equal(data['ids'], a['ids']) and np.array_equal(a['ids'], emb['ids'])
            and np.array_equal(emb['ids'], graph['ids'])
            and np.array_equal(data['eligible'], emb['evidence'])
            and np.array_equal(data['eligible'], a['eligible']), 'Complete numeric axes differ')
    require(am['samples'] == meta['samples'] and am['inputs']['features'] == binding(features),
            'Ten measured parent-depth axes differ')
    active = a['active']
    require(int(active.sum()) == 3074 and np.all(a['eligible'][active]),
            'Physical active population differs')
    physical_root = ROOT / 'artifacts/e035-confidence-taxonomy/pooled-inspection/restored/work/E009/pooled'
    links, lm = read_links(physical_root)
    require(binding(physical_root / 'completed.json') == am['inputs']['physical'],
            'Pooled graph source differs')
    eligible = links['eligible'][links['edges']].all(1)
    require(np.array_equal(a['edges'], links['edges'][eligible])
            and np.array_equal(a['edge_weights'], links['weights'][eligible])
            and len(a['edges']) == 1671, 'Admitted pooled edge/weight bytes differ')
    require(np.array_equal(a['bootstrap'][~active], emb['features'][~active]),
            'Inactive/unknown/excluded vectors changed')
    norm = np.linalg.norm(emb['features'][data['eligible']], axis=1)
    require(np.allclose(norm, 1, rtol=0, atol=1e-6), 'Original unit geometry failed')
    saved = torch.load(root / 'student/result/checkpoint.pt', map_location='cpu', weights_only=True)
    require(saved['policy'] == policy() and saved['cache']
            == binding(root / 'node-features/result/features.npz'), 'Checkpoint policy/cache differs')
    require(all(torch.isfinite(v).all() for v in saved['state'].values()),
            'Nonfinite saved model state')
    steps = Counter(float(s['step']) for s in saved['optimizer']['state'].values() if 'step' in s)
    require(set(steps) == {140.0}, 'Actual optimizer schedule differs')
    require(all(g['lr'] == .001 and g['weight_decay'] == .0001
                for g in saved['optimizer']['param_groups']), 'Actual optimizer defaults differ')
    checkpoint_shapes = {n: list(v.shape) for n, v in saved['state'].items()}
    del saved
    gc.collect()
    ids = data['ids'].tolist()
    neighbors = [[ids[j] for j in row[:5]] if valid else []
                 for row, valid in zip(graph['neighbors'], data['eligible'])]
    sparse = sparse_graph_contract(graph['edges'], graph['weights'], ids, data['eligible'])
    numeric = unit_neighbors(emb['features'], ids, data['eligible'], neighbors,
                             graph['neighbors'], graph['neighbors'].shape[1])
    lock = json.loads((ROOT / 'experiments/E013-marker-quality/review-lock.json').read_text())
    truth_root = verify_truth(lock)
    truth = json.loads((truth_root / 'truth.json').read_text())
    pop = json.loads((ROOT / lock['population_path']).read_text())
    targets = json.loads((truth_root / 'targets.json').read_text())['targets']
    require(ids == truth['ordered_contig_ids'] and len(targets) == 156,
            'Admitted truth/full axis differs')
    labels = {q: truth['contigs'][q]['AMBER_label'] for q in ids}
    genomes = sorted({g for g in labels.values() if g is not None})
    codes = {g: i for i, g in enumerate(genomes)}
    encoded = np.asarray([codes.get(labels[q], -1) for q in ids], np.int32)
    lineage = np.asarray([pop['genomes'][labels[q]]['lineage_class']
                          if labels[q] is not None else 'unknown' for q in ids], dtype=object)
    clean = set(json.loads(Path(marker_clean).read_text())['clean'])
    cosine = np.clip((a['bootstrap'] * emb['features']).sum(1), -1, 1)
    edges = a['edges']
    relation = np.where((encoded[edges] < 0).any(1), 'unresolved',
                        np.where(encoded[edges[:, 0]] == encoded[edges[:, 1]],
                                 'same_dominant_origin', 'different_dominant_origins'))
    edge_diagnostic = {}
    for name in sorted(set(relation)):
        e = edges[relation == name]
        edge_diagnostic[name] = dict(edges=len(e),
            cosine_before=float((a['bootstrap'][e[:, 0]] * a['bootstrap'][e[:, 1]]).sum(1).mean()),
            cosine_after=float((emb['features'][e[:, 0]] * emb['features'][e[:, 1]]).sum(1).mean()))
    learned_census = {}
    attributable = data['eligible'] & (encoded >= 0)
    same = np.zeros(len(ids), dtype=np.float32)
    rows = np.flatnonzero(attributable)
    same[rows] = (encoded[graph['neighbors'][rows, :5]] == encoded[rows, None]).mean(1)
    for name, mask in [('active', active), ('inactive_eligible', ~active & data['eligible']),
                       ('excluded', ~data['eligible'])]:
        at = mask & attributable
        learned_census[name] = dict(contigs=int(mask.sum()), bp=int(data['lengths'][mask].sum()),
            attributable_contigs=int(at.sum()), unknown_contigs=int((mask & (encoded < 0)).sum()),
            same_origin_5NN=float(same[at].mean()) if at.any() else None,
            bp_weighted_same_origin_5NN=float(np.dot(same[at], data['lengths'][at])
                                               / data['lengths'][at].sum()) if at.any() else None,
            by_lineage={l: dict(contigs=int((mask & (lineage == l)).sum()),
                               bp=int(data['lengths'][mask & (lineage == l)].sum()))
                        for l in sorted(set(lineage))},
            by_length={str(low): dict(contigs=int((mask & (data['lengths'] >= low)
                           & (data['lengths'] < next((v for v in BOUNDS if v > low), 10**15))).sum()))
                       for low in BOUNDS})
    original = json.loads((ROOT / 'artifacts/e031-bootstrap-preserving-learning/learning-inspection-20261103/verified/work'
                            / unit / 'train/result/checkpoint.json').read_text())
    raw = parent_geometry(data, original['transform'], dict(ids=ids, neighbors=neighbors), labels)
    partitions = {}
    for arm in ['pre', 'post']:
        part = json.loads((root / ('select/result/' + arm + '-partition.json')).read_text())
        assignment = np.asarray(part['assignment'])
        partitions[arm] = dict(coverage=coverage_populations(data, part, encoded, genomes, targets, clean),
            link_assignment={name: dict(contigs=int(mask.sum()), bp=int(data['lengths'][mask].sum()),
                assigned_contigs=int((mask & (assignment >= 0)).sum()),
                assigned_bp=int(data['lengths'][mask & (assignment >= 0)].sum()),
                unassigned_or_excluded_contigs=int((mask & (assignment < 0)).sum()),
                clean_marker_contigs=sum(ids[i] in clean for i in np.flatnonzero(mask)))
                for name, mask in [('active', active), ('inactive_eligible', ~active & data['eligible']),
                                    ('excluded', ~data['eligible'])]})
    result = dict(status='PASS', unit=unit, local_model_inference=False,
        geometry='New E036 graph output; fixed E031 bootstrap remains distinct',
        checkpoint_shapes=checkpoint_shapes, optimizer_step_histogram=dict(steps),
        native_reload_exact=True, original_Mac_portability_tolerance_unchanged=True,
        all_inactive_vectors_exact=True, unit_max_error=float(abs(norm - 1).max()),
        active_bootstrap_cosine=dict(min=float(cosine[active].min()),
                                     mean=float(cosine[active].mean()),
                                     median=float(np.median(cosine[active]))),
        physical_link_diagnostic=edge_diagnostic,
        physical_label_limit='Whole-contig dominant origins are not mate-locus identity; no truth filter or training feedback',
        native_sparse=sparse, fixed_128_query_numeric_contract=numeric,
        raw_learned_geometry=raw, full_learned_link_census=learned_census,
        partitions=partitions)
    write(output, result)
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    for n in ['base', 'features', 'marker-clean', 'output']:
        parser.add_argument('--' + n, type=Path, required=True)
    parser.add_argument('--unit', choices=['E009-noGLM', 'E009-GLM'], required=True)
    args = parser.parse_args()
    print(inspect(args.base, args.unit, args.features, args.marker_clean, args.output)['status'])
