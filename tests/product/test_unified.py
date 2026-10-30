"""Real tiny common information-path contracts; no community or ignored assets.

DNA/views/HMM/cache/graph/training/reload/export are actual readers and arithmetic.
Marker annotations are hand-authored synthetic fixtures. Only frozen-model
inference is mocked by NumericExtractor; this does not certify a GPU backend.
"""
import json
from pathlib import Path
import tempfile
import unittest
import subprocess
import sys

import numpy as np
import torch

from relational_fixture import fixture, NumericExtractor
from dl_binner.context.tokens import binding
from dl_binner.hybrid.bank import prepare as frozen_prepare, model_pin
from dl_binner.io import digest, save_arrays, write_json
from dl_binner.multiview.arrays import load_arrays
from dl_binner.multiview.views import load
from dl_binner.relational.pairs import prepare as prepare_pairs, load_pairs
from dl_binner.relational.model import embed as reload_student
from dl_binner.unified import cache, training, graph, grouping
from dl_binner.model import configure_torch


class Unified(unittest.TestCase):
    def setUp(self):
        configure_torch(4)

    def test_pure_configuration_matches_both_inherited_defaults_without_tensor_import(self):
        from dl_binner.context.model import config as context
        from dl_binner.hybrid.model import config as hybrid
        self.assertEqual(training.configuration(False), context())
        self.assertEqual(training.configuration(True), hybrid())
        code = 'import sys;from dl_binner.unified.training import configuration;configuration(False);configuration(True);assert "torch" not in sys.modules'
        subprocess.run([sys.executable, '-I', '-B', '-c', code], check=True)

    def test_complete_depth_training_admission_and_immutable_originals(self):
        with tempfile.TemporaryDirectory() as folder:
            f = fixture(folder, measured=False)
            before = {str(p): binding(p) for d in [f['root']/'data', f['tokens']] for p in d.iterdir()}
            data, meta = load(f['features'])
            n = len(data['ids']); depth = np.arange(n*10, dtype=np.float32).reshape(n, 10)
            depth[0] = 0
            rebound = dict(data, depth=depth, zero_depth=depth == 0, depth_evidence=(depth > 0).any(1))
            samples = ['opaque-'+str(j) for j in range(10)]
            nm = dict(meta, samples=samples, depth_sha256='a'*64)
            save_arrays(f['root']/'measured.npz', rebound, nm)
            receipt = f['root']/'measurement.json'
            write_json(receipt, dict(status='PASS', all_cells_measured=True, missing_cells=0,
                samples=samples, rows=n, reference=dict(sha256=meta['fasta_sha256']), matrix=dict(sha256='a'*64)))
            out = f['root']/'admitted'
            with self.assertRaisesRegex(ValueError, 'requires'):
                cache.admit(f['features'], f['root']/'measured.npz', f['views'], f['tokens'], out)
            r = cache.admit(f['features'], f['root']/'measured.npz', f['views'], f['tokens'], out, receipt)
            self.assertEqual(r['actual_missing_cells'], 0)
            self.assertEqual(r['measured_all_zero_rows'], 1)
            self.assertEqual(before, {str(p): binding(p) for d in [f['root']/'data', f['tokens']] for p in d.iterdir()})
            self.assertEqual((out/'views.npz').stat().st_ino, f['views'].stat().st_ino)
            changed = dict(rebound); changed['lengths'] = rebound['lengths'].copy(); changed['lengths'][0] += 1
            save_arrays(f['root']/'bad.npz', changed, nm)
            with self.assertRaisesRegex(ValueError, 'DNA'):
                cache.admit(f['features'], f['root']/'bad.npz', f['views'], f['tokens'], f['root']/'bad-admit', receipt)

    def test_graded_formula_zero_contrast_fixed_denominator_and_compiled_equivalence(self):
        rng = np.random.default_rng(11); n = 64
        vectors = rng.normal(size=(n, 64)).astype(np.float32); vectors /= np.linalg.norm(vectors, axis=1)[:, None]
        comp = rng.dirichlet(np.ones(136), n).astype(np.float32)
        depth = rng.integers(0, 100, (n, 10)).astype(np.float32); depth[:12] = 0
        data = dict(ids=np.array(['q'+str(i) for i in range(n)]), tnf=comp, depth=depth,
            lengths=np.arange(n, dtype=np.int64)*37+500, eligible=np.ones(n, bool))
        cfg = grouping.policy(); values, positive, scales, _, r = grouping.channels(data, vectors, data['eligible'], cfg)
        self.assertEqual(r['actual_missing_cells'], 0); self.assertEqual(r['measured_all_zero_rows'], 12)
        packed = np.column_stack([*values, data['lengths'], positive]).astype(np.float32)
        for i in [0, 11, 12, 63]:
            pool = np.array([j for j in range(n) if j != i])
            exact = grouping.distances(data, values, positive, scales, cfg, i, pool)
            actual = np.array([grouping.metric(packed[i], packed[j], 64, 136, *scales, 2500, 1e-6) for j in pool])
            np.testing.assert_allclose(exact, actual, rtol=1e-12, atol=1e-12)
        # Identical sequence/native evidence cannot turn co-zero into measured agreement.
        a = grouping.distances(data, values, positive, scales, cfg, 0, np.array([1]))[0]
        without = (np.square(vectors[1].astype(float)-vectors[0]).sum()/scales[0])
        self.assertGreater(a*a*3, without+0.9)
        with self.assertRaisesRegex(ValueError, 'Unfrozen'):
            bad = cfg.copy(); bad['neighbors'] = 31
            p = Path(tempfile.gettempdir())/'e027-bad-policy.json'; p.write_text(json.dumps(bad))
            try: grouping.policy(p)
            finally: p.unlink()

    def test_supported_singleton_is_not_a_blanket_long_contig_assignment(self):
        data = dict(ids=np.array(['long-reliable', 'long-marker-negative', 'short-kept']),
                    lengths=np.array([200000, 200000, 700], np.int64))
        valid = np.ones(3, bool); selected = np.arange(3, dtype=np.int64)
        nn = np.empty((3, 0), np.int32); dd = np.empty((3, 0), np.float64)
        evidence = dict(panel_size=4, calls={'long-reliable': {'a': [.9], 'b': [.9]}})
        arms, tree, alternatives, choices = grouping.partitions(data, valid, selected, nn, dd, evidence, grouping.policy())
        self.assertEqual(arms['post']['assignment'], [0, -1, -1])
        self.assertEqual(len(arms['post']['ids']), 3)
        self.assertEqual(arms['post']['unassigned'], 2)
        with self.assertRaisesRegex(ValueError, 'marker axis'):
            grouping.validate_evidence(dict(panel_size=4, calls={'unknown': {'a': [1.]}}), data['ids'].tolist())
        with self.assertRaisesRegex(ValueError, 'marker weight'):
            grouping.validate_evidence(dict(panel_size=4, calls={'long-reliable': {'a': [float('nan')]}}), data['ids'].tolist())

    def test_actual_full_teacher_pair_student_reload_graph_refinement_and_export_both_modes(self):
        from dl_binner.information.export import export
        with tempfile.TemporaryDirectory() as folder:
            f = fixture(folder)
            cache.admit(f['features'], f['features'], f['views'], f['tokens'], f['root']/'admission')
            views = f['root']/'admission/views.npz'; tokens = f['root']/'admission/tokens'
            frozen_prepare(f['fasta'], f['features'], f['views'], f['root']/'frozen', NumericExtractor(), model_pin())
            evidence = f['root']/'physical.json'
            write_json(evidence, dict(panel_size=4, calls={q: {'family-0': [1.]} for q in f['data']['ids'][:12]}))
            old = binding(f['root']/'frozen/vectors.npy')
            teachers = []; pairs_by_mode = []
            for glm in [False, True]:
                root = f['root']/('on' if glm else 'off'); root.mkdir()
                cfg = training.configuration(glm); cfg.update(epochs=f['cfg']['epochs'], min_bin_bp=1, min_bin_contigs=1)
                frozen = f['root']/'frozen' if glm else None
                training.bootstrap(f['features'], views, tokens, frozen, root/'bootstrap', cfg)
                training.reload_bootstrap(f['features'], views, tokens, frozen, root/'bootstrap/checkpoint.pt', root/'teacher.npz')
                def native_graph(embeddings, destination):
                    code = 'import json,sys;from dl_binner.unified.graph import prepare;a=json.loads(sys.argv[1]);prepare(*a[:3],a[3]);assert "torch" not in sys.modules'
                    argv = [str(f['features']), str(embeddings), str(destination), cfg]
                    subprocess.run([sys.executable, '-I', '-B', '-c', code, json.dumps(argv)], check=True)
                native_graph(root/'teacher.npz', root/'teacher-graph')
                prepare_pairs(f['features'], root/'teacher.npz', root/'teacher-graph/graph.npz', f['markers'], f['hmm'], root/'pairs')
                a, m = load_pairs(root/'pairs', f['features']); pairs_by_mode.append(m)
                self.assertEqual(m['inputs']['embeddings'], binding(root/'teacher.npz'))
                training.student(f['features'], views, tokens, frozen, root/'pairs', root/'student', cfg)
                reload_student(f['features'], views, tokens, frozen, root/'pairs', root/'student/checkpoint.pt', root/'student.npz', 4)
                native_graph(root/'student.npz', root/'student-graph')
                code = '''import json,sys
from pathlib import Path
from dl_binner.unified.grouping import run,audit
a=json.loads(sys.argv[1])
run(*a,force_native=True)
audit(*a)
if 'torch' in sys.modules:raise RuntimeError('Graph-only worker imported tensor backend')
from threadpoolctl import threadpool_info
pools=threadpool_info()
if any(p['prefix']=='libiomp'for p in pools)and any(p['prefix']=='libomp'for p in pools):raise RuntimeError('Incompatible graph OpenMP runtimes')
'''
                argv = [str(p) for p in [f['features'], root/'student.npz', root/'student-graph/graph.npz', evidence, root/'group']]
                subprocess.run([sys.executable, '-I', '-B', '-c', code, json.dumps(argv)], check=True)
                result = json.loads((root/'group/completed.json').read_text())
                self.assertFalse(result['truth_accessed'])
                self.assertEqual(grouping.audit(f['features'], root/'student.npz', root/'student-graph/graph.npz', evidence, root/'group')['status'], 'PASS')
                for arm in ['parent', 'post']:
                    account = export(f['features'], root/'group'/(arm+'-partition.json'), f['fasta'], root/('export-'+arm), include_dna=True)
                    self.assertEqual(account['contigs'], len(f['data']['ids']))
                    self.assertEqual(account['bp'], int(f['data']['lengths'].sum()))
                checkpoint = torch.load(root/'bootstrap/checkpoint.pt', weights_only=True)
                teachers.append(checkpoint['model_state'])
                student = json.loads((root/'student/checkpoint.json').read_text())
                self.assertEqual(len(student['history']), 20)
                self.assertTrue(all(h['parents_seen'] == int(f['data']['eligible'].sum()) for h in student['history']))
                self.assertTrue(all(h['relation_pairs_exposed'] == len(a['left']) for h in student['history']))
                self.assertEqual(training.information_contract(glm)['proposal_teacher_GLM'], glm)
                self.assertEqual(('hybrid' in checkpoint['config']), glm)
            self.assertTrue(any(not torch.equal(v, teachers[1][k]) for k, v in teachers[0].items()))
            self.assertEqual(old, binding(f['root']/'frozen/vectors.npy'))
            self.assertNotEqual(pairs_by_mode[0]['inputs']['embeddings'], pairs_by_mode[1]['inputs']['embeddings'])


if __name__ == '__main__':
    unittest.main()
