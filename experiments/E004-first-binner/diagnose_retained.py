#!/usr/bin/env python3
"""Check retained E004 neighborhoods/metrics and diagnose its mixed utility.

Never train, extract features or refit communities. Independently recompute
neighbors and B-cubed contributions from byte-bound arrays/partitions, check
embedding collapse, and reconstruct label-blind batch exposure retrospectively.
Co-genomic negatives are an observed assumption violation, not a causal test.
"""
from collections import Counter
import json
from pathlib import Path

import numpy as np

from dl_binner.io import digest, load_arrays, write_json

ROOT = Path(__file__).resolve().parents[2]
RUN = ROOT/'artifacts/e004-first-binner/run-001'


def main():
    """Publish a small full-denominator diagnostic of the sole accepted run."""
    panel = json.loads((ROOT/'experiments/E003-representation-screen/panel.json').read_text())
    evaluation = json.loads((RUN/'evaluation.json').read_text())
    rows = panel['rows']
    ids = [r['id'] for r in rows]
    truth = np.array([r['genome'] for r in rows])
    totals = Counter(truth)
    diagnostics = {}
    for mode in ('raw', 'learned'):
        arrays, _ = load_arrays(RUN/f'{mode}.embeddings.npz', 'embeddings')
        part = json.loads((RUN/f'{mode}.partition.json').read_text())
        assert arrays['ids'].tolist() == part['ids'] == ids
        x = arrays['features'].astype(np.float64)
        valid = arrays['evidence'] & (np.linalg.norm(x, axis=1) > 0)
        mean, std = x[valid].mean(0), x[valid].std(0)
        usable = std > 1e-8
        z = (x[:, usable]-mean[usable])/std[usable]
        z[~valid] = 0
        norms = np.linalg.norm(z, axis=1)
        valid &= norms > 1e-12
        z[valid] /= norms[valid, None]
        cosine = np.clip(z@z.T, -1, 1)
        expected_neighbors = [[ids[j] for j in sorted((j for j in range(len(ids)) if valid[i] and valid[j] and i != j),
                               key=lambda j: (-cosine[i, j], ids[j]))[:5]] for i in range(len(ids))]
        assert expected_neighbors == part['neighbors']
        labels = np.array(part['assignment'])
        origin_map = dict(zip(ids, truth))
        for i, scored in enumerate(evaluation['scores'][mode]['per_fragment']):
            precision = recall = 0
            if labels[i] >= 0:
                group = labels == labels[i]
                same = sum(truth[group] == truth[i])
                precision, recall = same/sum(group), same/totals[truth[i]]
            nn = sum(origin_map[n] == truth[i] for n in part['neighbors'][i])/5
            np.testing.assert_allclose([nn, precision, recall], [scored[k] for k in ('neighbor_purity', 'b3_precision', 'b3_recall')], rtol=0, atol=1e-12)
        diagnostics[mode] = dict(shape=list(x.shape), finite=bool(np.isfinite(x).all()),
                                  distinct_rows=len(np.unique(x, axis=0)), nonconstant_dimensions=int(usable.sum()),
                                  norm_min=float(np.linalg.norm(x[valid], axis=1).min()),
                                  norm_max=float(np.linalg.norm(x[valid], axis=1).max()),
                                  short_neighbor_by_origin={g:float(np.mean([r['neighbor_purity'] for r in evaluation['scores'][mode]['per_fragment'] if r['genome'] == g and r['bp'] < 2500])) for g in sorted(totals)})
    training = json.loads((RUN/'checkpoint.json').read_text())
    cfg = training['config']
    assert training['eligible'] == len(ids)  # This actual panel has no transformed-zero rows.
    rng = np.random.default_rng(cfg['seed'])
    co_genomic, comparisons, exposures = 0, 0, 0
    for _ in range(cfg['epochs']):
        shuffled = rng.permutation(len(ids))
        for start in range(0, len(ids), cfg['batch_size']):
            group = truth[shuffled[start:start+cfg['batch_size']]]
            counts = Counter(group)
            co_genomic += sum(n*(n-1) for n in counts.values())
            comparisons += len(group)*(len(group)-1)
            exposures += len(group)
    write_json(ROOT/'experiments/E004-first-binner/diagnostics.json', dict(
        inputs={f'{mode}.embeddings.npz':digest(RUN/f'{mode}.embeddings.npz') for mode in ('raw', 'learned')},
        independent_neighbors_and_per_fragment_metrics=True, embeddings=diagnostics,
        negative_exposure=dict(co_genomic_ID_pairs=co_genomic, negative_ID_pairs=comparisons,
                               fraction=co_genomic/comparisons, mean_per_anchor=co_genomic/exposures),
        interpretation='No constant-output collapse. ID-discrimination objective includes co-genomic negatives and can reduce genome neighborhoods; exposure is measured, causation untested. Grouping/recall improves while precision and short-neighbor purity fall. No retraining/tuning performed.'))
    print(json.dumps(dict(independent_review='passed', co_genomic_negative_fraction=co_genomic/comparisons,
                          mean_co_genomic_negatives_per_anchor=co_genomic/exposures)))


if __name__ == '__main__':
    main()
