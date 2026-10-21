"""Real tiny installed context/DAG/readers/refinement/export/return contracts.

Only generated DNA/HMMs are fitted. No external community caches, labels, cloud
API or scientific mocks occur. Tensor/graph/marker stages are separate processes.
"""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

import numpy as np

REPO = Path(__file__).absolute().parents[1]
sys.path.insert(0, str(REPO/'scripts'))
sys.path.insert(0, str(REPO/'tests/product'))


class NativeContracts(unittest.TestCase):
    def test_actual_serial_context_DAG_reload_exposure_and_complete_exports(self):
        from candidate_fixture import fixture, asset
        from dl_binner.multiview.views import config, prepare, load
        from dl_binner.context.tokens import policy
        from dl_binner.candidate.markers import cache
        from e019_collect import pack
        from e014_collect import binding
        with tempfile.TemporaryDirectory() as d:
            p = Path(d)
            fasta, depth, rows = fixture(p)
            hmm, manifest = asset(p, fasta)
            marker = p/'markers'
            marker.mkdir()
            cache(fasta, hmm, manifest, marker, 4)
            before_marker = binding(marker/'cache.json')
            base = config()
            base.update(epochs=2, batch_size=4, neighbors=5, min_bin_bp=100, min_bin_contigs=1)
            cfg = base | dict(positive_only=True, predictor_hidden=128, ema_base=.996,
                collapse_rows=8192, collapse_min_std=.001, collapse_min_rank=2, context=policy())
            (p/'base.json').write_text(json.dumps(base))
            (p/'cfg.json').write_text(json.dumps(cfg))
            units = {}
            for name, dep in [('E009-context', depth), ('oral-context', None)]:
                original = p/(name+'-original')
                prepare(fasta, dep, original, base)
                units[name] = dict(fasta=str(fasta), features=str(original/'features.npz'),
                    views=str(original/'views.npz'), marker_cache=str(marker))
            original_members = {name: {str(x): binding(x) for x in Path(unit['features']).parent.iterdir()}
                for name, unit in units.items()}
            plan = dict(kind='E019 window-context candidate', work=str(p/'work'), units=units, threads=4,
                python=sys.executable, worker=str(REPO/'scripts/e019_control.py'),
                workflow_python=os.environ.get('E019_WORKFLOW_PYTHON', sys.executable),
                snakefile=str(REPO/'experiments/E019-window-context/Snakefile'), config=str(p/'cfg.json'),
                base_config=str(p/'base.json'), hmm=str(hmm), reuse_lock='own-engineering-only', candidate_lock='own-engineering-only')
            path = p/'plan.json'
            path.write_text(json.dumps(plan))
            if os.environ.get('E019_WORKFLOW_PYTHON'):
                cmd = [sys.executable, '-I', '-B', str(REPO/'scripts/e019_control.py'), '--plan', str(path), '--workflow', '--engineering']
                result = subprocess.run(cmd, capture_output=True, text=True)
                detail = '\n'.join(str(x)+'\n'+x.read_text() for x in (p/'work/logs').rglob('*.log'))
                self.assertEqual(result.returncode, 0, result.stdout+result.stderr+'\nACTUAL_STAGE_LOGS\n'+detail)
                self.assertIn('15 of 15 steps (100%) done', result.stdout+result.stderr)
            else:
                for unit in units:
                    for name in ['tokens', 'train', 'embed', 'group', 'refine', 'export', 'graph-proof']:
                        result = subprocess.run([sys.executable, '-I', '-B', str(REPO/'scripts/e019_control.py'),
                            '--plan', str(path), '--unit', unit, '--stage', name, '--engineering'], capture_output=True, text=True)
                        self.assertEqual(result.returncode, 0, result.stdout+result.stderr)
            for name, unit in units.items():
                root = p/'work/units'/name
                checkpoint = json.loads((root/'train/checkpoint.json').read_text())
                self.assertEqual(checkpoint['config'], cfg)
                self.assertEqual(checkpoint['training_tokens_sha256'], binding(root/'tokens/tokens.json')['sha256'])
                self.assertTrue(json.loads((root/'embeddings.json').read_text())['reload_exact'])
                data, meta, v, vm = load(unit['features'], unit['views'])
                indices = np.flatnonzero(data['eligible'])
                rng = np.random.default_rng(11)
                expected = []
                for _ in range(2):
                    views_seen = dropped = 0
                    permutation = rng.permutation(indices)
                    for start in range(0, len(indices), cfg['batch_size']):
                        selected = permutation[start:start+cfg['batch_size']]
                        n = len(selected)
                        mask = np.concatenate([np.ones(n, bool)]+[v['usable'][selected, j] for j in range(4)])
                        original = np.tile(data['depth_evidence'][selected], 5)[mask]
                        dropped += int((original & (rng.random(int(mask.sum())) < .5)).sum())
                        views_seen += int(mask.sum())
                    expected.append((views_seen, dropped))
                self.assertEqual([(h['available_views'], h['depth_dropped_views']) for h in checkpoint['history']], expected)
                for h in checkpoint['history']:
                    self.assertEqual(h['parents_seen'], len(indices))
                    self.assertAlmostEqual(h['loss'], h['fused_positive']+.5*h['sequence_positive']+
                        h['composition_reconstruction']+.1*h['depth_reconstruction'], places=5)
                    self.assertGreater(h['composition_reconstruction'], 0)
                accounting = json.loads((root/'export/accounting.json').read_text())
                self.assertEqual(set(accounting), {'pre', 'old', 'post'})
                for arm, record in accounting.items():
                    self.assertEqual(record['contigs'], len(rows))
                    self.assertEqual(record['bp'], sum(len(s) for _, s in rows))
                    self.assertEqual(sum(v['contigs'] for v in record['populations'].values()), len(rows))
                    self.assertEqual(record['includes_full_DNA'], arm == 'post')
                # Read every physically emitted DNA byte independently.
                from dl_binner.multiview.views import fasta_rows
                emitted = {}
                for file in (root/'export/post').glob('*.fna'):
                    for ident, dna in fasta_rows(file):
                        self.assertNotIn(ident, emitted)
                        emitted[ident] = dna
                self.assertEqual(emitted, dict(rows))
                self.assertEqual(original_members[name], {str(x): binding(x) for x in Path(unit['features']).parent.iterdir()})
            self.assertEqual(before_marker, binding(marker/'cache.json'))
            evidence = p/'evidence'
            evidence.mkdir()
            (evidence/'plan.json').write_text(path.read_text())
            result = pack(p/'work', evidence, p/'return')
            self.assertEqual(len(result['aliases']), 2)
            self.assertTrue(any(k.endswith('/tokens/counts.npy') for k in result['omitted_retained_on_disk']))
            # Exercise the new review adapter's real token metadata/inventory
            # contract without reading truth or generating any quality scores.
            from e019_review import token_contract
            from e019_collect import select
            original = select(p/'work')[1]
            for name, unit in units.items():
                root = p/'work/units'/name
                checkpoint = json.loads((root/'train/checkpoint.json').read_text())
                proof = token_contract(root, original, checkpoint, binding(unit['features']))
                self.assertFalse(proof['local_full_token_numeric_reread'])


if __name__ == '__main__':
    unittest.main()
