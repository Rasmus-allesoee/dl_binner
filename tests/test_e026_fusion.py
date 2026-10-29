"""Actual tiny calibration/index/reader/marker/selection/export contracts.

Synthetic DNA, native vectors and marker calls exercise production consumers;
no accepted community is grouped/scored, no encoder/marker detector is run.
Only the deliberately bad external index is mocked for the refusal contract.
"""
import copy
import json
from pathlib import Path
import pickle
import random
import tempfile
import unittest
from unittest.mock import patch

import numpy as np

from dl_binner.calibrated.fusion import policy, calibrate, fused_metric, quantile_knots, rank_value
from dl_binner.calibrated.retrieval import retrieve, CoreIndex
from dl_binner.calibrated.grouping import construct, biological_utilities, select, recruit
from dl_binner.calibrated.arrays import load as load_numeric
from dl_binner.candidate.grouping import canonical_partition
from dl_binner.io import digest, save_arrays
from dl_binner.multiview.arrays import load_arrays
from e024_coverage import binding, write
from e026_information import inputs, run, audit

ROOT = Path(__file__).absolute().parents[1]
CFG = policy()


def fixture(root):
    """Create real FASTA/TNF/view files and synthetic source-blind cached inputs."""
    from dl_binner.multiview.views import prepare, config
    from dl_binner.candidate.grouping import group
    root = Path(root); rng = random.Random(7281); nr = np.random.default_rng(11)
    sequences, ids, labels = [], [], []
    for b in range(4):
        base = ''.join(rng.choices('ACGT', k=6000))
        for i in range(6):
            dna = ''.join(rng.choice('ACGT') if rng.random() < .01 else c for c in base)
            ids.append('opaque-'+str(len(ids)*17+91)); sequences.append(dna); labels.append(b)
    for b in range(4):
        ids.append('short-'+str(b)); sequences.append(sequences[b*6][:900]); labels.append(b)
    ids.append('excluded'); sequences.append('ACGT'*20); labels.append(-1)
    fasta = root/'input.fna'; fasta.write_text(''.join('>'+q+'\n'+dna+'\n' for q, dna in zip(ids, sequences)))
    depth = root/'depth.tsv'
    with depth.open('x') as f:
        f.write('contig_id\tsample_b\tsample_a\n')
        for q, b in zip(ids, labels):
            values = [0, 0] if b in [-1, 3] else [[30, 1], [2, 40], [15, 15]][b]
            f.write(q+'\t'+'\t'.join(map(str, values))+'\n')
    prepare(fasta, depth, root/'features', config())
    features = root/'features/features.npz'; data, _ = load_arrays(features, 'features')
    vectors = np.zeros((len(ids), 64), np.float32)
    for i, b in enumerate(labels):
        if b >= 0:
            vectors[i] = nr.normal(0, .008, 64); vectors[i, b] += 1
            vectors[i] /= np.linalg.norm(vectors[i])
    embedding = root/'embeddings.npz'
    save_arrays(embedding, dict(ids=data['ids'], features=vectors, evidence=data['eligible']),
                dict(kind='embeddings', features_sha256=digest(features), metric='Synthetic engineering unit vectors'))
    group(embedding, features, root/'native-graph', config(), 4)
    evidence = root/'physical.json'
    write(evidence, dict(panel_size=40, calls={ids[b*6]: {f'm{j}': [.95] for j in range(8)} for b in range(4)}, loci=[]))
    return dict(features=str(features), embeddings=str(embedding), graph=str(root/'native-graph/graph.npz'),
                marker_evidence=str(evidence), fasta=str(fasta), receipt=None)


class FusionContracts(unittest.TestCase):
    def test_actual_compiled_metric_query_pickle_reload_and_exact_reference(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); unit = fixture(root)
            data, vectors, valid, _, original, _ = inputs(unit)
            model = calibrate(data, vectors, valid, original, CFG)
            index = CoreIndex(model, data, valid, original, 4, True)
            self.assertIsNotNone(index.native)
            for i in [0, 7, 18, 24]:
                exact = model.distances(i, index.cores)
                compiled = np.array([fused_metric(model.packed(np.array([i]))[0], x, *model.metric_args().values()) for x in index.x])
                np.testing.assert_allclose(compiled, exact, rtol=1e-12, atol=1e-12)
            near, dd = index.native.query(model.packed(np.array([0, 7, 24])), k=10)
            restored = pickle.loads(pickle.dumps(index.native))
            n2, d2 = restored.query(model.packed(np.array([0, 7, 24])), k=10)
            np.testing.assert_array_equal(near, n2); np.testing.assert_array_equal(dd, d2)
            arrays, observed = retrieve(model, data, valid, original, root/'native', 4, True)
            self.assertTrue(observed['native_custom_index'])
            self.assertTrue(all(v['mean_recall'] is None or v['mean_recall'] >= .9 for v in observed['strata'].values()))
            self.assertEqual(len(arrays['cores']), 24)
            self.assertEqual(len(arrays['queries']), 28)

    def test_measured_zeros_partial_channels_constants_and_fixed_denominator(self):
        knots, ranks = quantile_knots(np.r_[np.zeros(90), np.arange(1., 11.)], 129)
        self.assertEqual(knots[0], 0.); self.assertEqual(ranks[0], 0.)
        query = np.r_[np.linspace(-1, 15, 997), knots]
        actual = np.array([rank_value(v, knots, ranks, len(knots)) for v in query])
        np.testing.assert_allclose(actual, np.interp(query, knots, ranks), rtol=1e-14, atol=1e-14)
        with tempfile.TemporaryDirectory() as tmp:
            unit = fixture(Path(tmp)); data, vectors, valid, _, original, _ = inputs(unit)
            model = calibrate(data, vectors, valid, original, CFG)
            _, ranks, available = model.distances(18, np.array([19, 0]), True)
            self.assertFalse(available[0, 2]); self.assertEqual(ranks[0, 2], .5)
            self.assertTrue(available[1, 2])
            partial = np.ones(len(valid), bool); partial[0] = False
            model = calibrate(data, vectors, valid, original, CFG, partial)
            distance, ranks, available = model.distances(0, np.array([1]), True)
            self.assertFalse(available[0, 2]); self.assertEqual(ranks[0, 2], .5)
            self.assertEqual(model.record['incomplete_measurement_rows'], 1)
            const = copy.deepcopy(data); const['tnf'][:] = data['tnf'][0]; const['depth'][:] = 0
            v = np.zeros_like(vectors); v[valid, 0] = 1
            empty = calibrate(const, v, valid, original, CFG)
            self.assertFalse(empty.active.any())
            np.testing.assert_array_equal(empty.distances(0, np.arange(5)), np.full(5, .5))
            absent = copy.deepcopy(data); absent['depth'] = np.empty((len(valid), 0), np.float32)
            no_depth = calibrate(absent, vectors, valid, original, CFG)
            self.assertEqual(no_depth.record['all_zero_rows'], 0)
            self.assertEqual(no_depth.record['no_depth_modality_rows'], len(valid))
            with self.assertRaisesRegex(ValueError, 'measurement mask'):
                calibrate(data, vectors, valid, original, CFG, np.zeros(len(valid)))

    def test_real_fasta_sparse_axes_marker_choices_full_exports_and_reload(self):
        from dl_binner.information.export import export
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); unit = fixture(root)
            before = {k: binding(v) for k, v in unit.items() if v}
            result = run(unit, root/'new', CFG)
            self.assertTrue(result['arms']['core']['bins'] > 0)
            self.assertFalse(result['truth_accessed']); self.assertFalse(result['learning_changed'])
            # Actual reload must not invoke index discovery or MST reconstruction.
            with patch('dl_binner.calibrated.retrieval.CoreIndex.__init__', side_effect=AssertionError('index replay')), \
                 patch('scipy.sparse.csgraph.minimum_spanning_tree', side_effect=AssertionError('MST replay')):
                self.assertEqual(audit(unit, root/'new', CFG)['status'], 'PASS')
            for arm in ['core', 'recruited']:
                result = export(unit['features'], root/'new'/(arm+'-partition.json'), unit['fasta'], root/arm, arm == 'recruited')
                self.assertEqual(result['contigs'], 29)
                self.assertEqual(result['populations']['excluded']['contigs'], 1)
                if arm == 'recruited':
                    self.assertEqual(sum(p.read_text().count('>') for p in (root/arm).glob('*.fna')), 29)
            self.assertEqual(before, {k: binding(unit[k]) for k in before})
            with self.assertRaises(FileExistsError): run(unit, root/'new', CFG)
            (root/'new/choices.json').write_text('[]')
            with self.assertRaisesRegex(ValueError, 'member corrupted'): audit(unit, root/'new', CFG)

    def test_moments_match_dense_distinct_pair_calculation(self):
        with tempfile.TemporaryDirectory() as tmp:
            unit = fixture(Path(tmp)); data, vectors, valid, _, original, evidence = inputs(unit)
            model = calibrate(data, vectors, valid, original, CFG)
            # A hand-built mixed zero/positive three-leaf tree exercises OR
            # denominators and unequal parent weights, independent of discovery.
            cores = np.array([0, 18, 24]); lengths = data['lengths'][cores]
            tree = dict(children=np.array([[-1, -1]]*3+[[0, 1], [2, 3]]),
                        mass=np.r_[lengths, lengths[:2].sum(), lengths.sum()])
            q = biological_utilities(tree, cores, data, model, evidence)
            for node, rows in [(3, cores[:2]), (4, cores)]:
                pairs = [(i, j) for i in rows for j in rows if i != j]
                weights = np.array([float(data['lengths'][i])*data['lengths'][j] for i, j in pairs])
                mean_rel = np.average([np.sqrt(float(data['lengths'][i])/(data['lengths'][i]+2500)
                                           *float(data['lengths'][j])/(data['lengths'][j]+2500)) for i, j in pairs], weights=weights)
                rank = np.full(3, .5)
                for c, x in enumerate(model.channels):
                    obs = np.array([bool(model.available[i, c] and model.available[j, c]
                        and (c != 2 or model.positive[i] or model.positive[j])) for i, j in pairs])
                    if not model.active[c] or not obs.any(): continue
                    d = np.array([float(((x[i].astype(np.float64)-x[j])**2).sum()) for i, j in pairs])
                    value = np.average(d[obs], weights=weights[obs])
                    r = np.interp(value, model.knot_x[c, :model.counts[c]], model.knot_y[c, :model.counts[c]])
                    factor = weights[obs].sum()/weights.sum()*(mean_rel if c else 1)
                    rank[c] = .5+factor*(r-.5)
                self.assertAlmostEqual(q['coherence'][node], 1-rank[model.active].mean(), places=11)

    def test_parent_ties_fragmentation_margin_and_marker_negative_alternative(self):
        tree = {}; branches = [dict(node=0, parent=-1, children=[1, 2]),
            dict(node=1, parent=0, children=[]), dict(node=2, parent=0, children=[])]
        for children, expected in [(50., [0]), (52.5, [0]), (53., [1, 2])]:
            quality = dict(utility=np.array([100., children, children]), coherence=np.full(3, .9),
                           breadth=np.zeros(3), excess=np.zeros(3))
            kept, _ = select(tree, branches, quality, CFG)
            self.assertEqual(sorted(kept), expected)

    def test_single_pass_recruitment_accumulates_marker_guard_without_propagation(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); unit = fixture(root); data, vectors, valid, _, original, evidence = inputs(unit)
            model = calibrate(data, vectors, valid, original, CFG)
            retrieval, _ = retrieve(model, data, valid, original, root/'retrieval')
            pre = canonical_partition(data['ids'].tolist(), valid, [[0, 1, 4, 5]], data['lengths'], CFG)
            ids = data['ids'].tolist()
            evidence = dict(panel_size=20, calls={ids[i]: {'repeat': [1.]} for i in [0, 2, 3]}, loci=[])
            # Exercise exact support/recruitment with a fixture in which these
            # six members have identical composition/native/depth, so available
            # channel ranks are the strongest observed agreement, without mocks.
            changed = copy.deepcopy(data); v = vectors.copy()
            for i in [1, 2, 3, 4, 5]:
                changed['tnf'][i] = changed['tnf'][0]; v[i] = v[0]
            model = calibrate(changed, v, valid, original, CFG)
            retrieval, _ = retrieve(model, changed, valid, original, root/'recruit')
            post, trace = recruit(pre, retrieval, model, changed, evidence)
            chosen = [i for i in [2, 3] if post['assignment'][i] >= 0]
            self.assertEqual(len(chosen), 1, repr([r for r in trace if r['id'] in [ids[2], ids[3]]]))
            rejected = [r for r in trace if r['id'] in [ids[2], ids[3]] and r['reason'] == 'accumulated_reliable_marker_excess_guard']
            self.assertEqual(len(rejected), 1)
            self.assertTrue(all(set(r['accepted_core_neighbors']) <= set(retrieval['cores']) for r in trace))

    def test_recruitment_retains_core_to_final_bin_relabeling(self):
        with tempfile.TemporaryDirectory() as tmp:
            ids = np.array(['z0', 'z1', 'y0', 'y1', 'a'])
            vectors = np.zeros((5, 64), np.float32); vectors[[0, 1, 4], 0] = 1; vectors[[2, 3], 1] = 1
            tnf = np.zeros((5, 136), np.float32); tnf[[0, 1, 4], 0] = 1; tnf[[2, 3], 1] = 1
            data = dict(ids=ids, lengths=np.array([6000, 6000, 6000, 6000, 900]), tnf=tnf,
                depth=np.array([[10], [10], [30], [30], [10]], np.float32),
                valid_fourmers=np.ones(5, np.int64), eligible=np.ones(5, bool))
            original = dict(neighbors=np.array([[j for j in range(5) if j != i] for i in range(5)]))
            model = calibrate(data, vectors, data['eligible'], original, CFG)
            cache, _ = retrieve(model, data, data['eligible'], original, Path(tmp)/'retrieval')
            pre = canonical_partition(ids.tolist(), data['eligible'], [[0, 1], [2, 3]], data['lengths'], CFG)
            post, trace = recruit(pre, cache, model, data, dict(panel_size=40, calls={}))
            self.assertEqual(post['core_bin_to_final_bin'], [1, 0])
            row = next(r for r in trace if r['id'] == 'a')
            self.assertEqual(row['best_core_bin'], 1); self.assertEqual(row['final_bin'], 0)

    def test_refused_recall_retains_numeric_proof_empty_core_and_bad_evidence(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); unit = fixture(root); data, vectors, valid, _, original, evidence = inputs(unit)
            model = calibrate(data, vectors, valid, original, CFG)
            # Mock only external proposals; real score/rerank/writer/refusal run.
            cfg = dict(CFG, neighbors=3)
            model.cfg = cfg
            original['neighbors'] = np.full((len(valid), 0), -1, np.int64)
            with patch.object(CoreIndex, 'query', lambda s, rows: np.tile(np.arange(4), (len(rows), 1))):
                with self.assertRaisesRegex(ValueError, 'numeric evidence retained'):
                    retrieve(model, data, valid, original, root/'bad')
            record = json.loads((root/'bad/audit.json').read_text())
            self.assertEqual(record['status'], 'FAILED_RECALL_GATE')
            load_numeric(root/'bad/neighbors.npz', 'calibrated_core_neighbors', data['ids'])
            small = copy.deepcopy(data); small['lengths'][:] = 900
            model = calibrate(small, vectors, valid, original, CFG)
            arrays, _ = retrieve(model, small, valid, original, root/'no-cores')
            arms, *_ = construct(small, valid, model, arrays, evidence)
            self.assertEqual(arms['recruited']['unassigned'], len(valid))
            small['lengths'][0] = 6000
            model = calibrate(small, vectors, valid, original, CFG)
            arrays, _ = retrieve(model, small, valid, original, root/'one-core')
            self.assertEqual(len(arrays['cores']), 1)
            own = int(np.flatnonzero(arrays['queries'] == 0)[0])
            self.assertEqual(arrays['counts'][own], 0)
            self.assertEqual(arrays['neighbors'][own, 0], -1)
            bad = copy.deepcopy(evidence); bad['calls']['outside'] = {'x': [1.]}
            with self.assertRaisesRegex(ValueError, 'marker axis'): construct(small, valid, model, arrays, bad)
            with self.assertRaisesRegex(ValueError, 'Unfrozen'): policy(ROOT/'experiments/E023-adaptive-density-bins/config.json')

    def test_actual_Oral_rebound_consumer_and_complete_zero_population(self):
        from test_e025_retrieval import retained
        from dl_binner.information.export import export
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); u, receipt = retained(root)
            unit = dict(features=str(receipt.parent/'features.npz'), embeddings=str(u['embeddings']),
                graph=str(u['graph']), marker_evidence=str(u['marker_evidence']),
                fasta=str(u['reference']), receipt=str(receipt))
            data, _, _, meta, _, _ = inputs(unit)
            self.assertEqual(data['depth'].shape[1], 10)
            self.assertTrue((data['depth'] == 0).all(1).any())
            before = binding(receipt)
            result = run(unit, root/'new-rebound', CFG)
            self.assertEqual(result['samples'], meta['samples'])
            self.assertEqual(audit(unit, root/'new-rebound', CFG)['status'], 'PASS')
            emitted = export(unit['features'], root/'new-rebound/recruited-partition.json',
                             u['reference'], root/'all-DNA', True)
            self.assertEqual(emitted['contigs'], 7); self.assertEqual(binding(receipt), before)
            bad = dict(unit, features=str(u['features']))
            with self.assertRaisesRegex(ValueError, 'rebind path differs'): inputs(bad)


if __name__ == '__main__': unittest.main()
