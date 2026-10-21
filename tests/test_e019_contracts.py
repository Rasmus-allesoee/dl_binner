"""Stdlib-only E019 scope, held release and manifest-inclusive collection contracts."""
import copy
import json
from pathlib import Path
import sys
import tempfile
import subprocess
import unittest

REPO = Path(__file__).absolute().parents[1]
sys.path.insert(0, str(REPO/'scripts'))
from e014_collect import binding
from e019_phase import admission, configuration, SECONDS, STOP_SECONDS
from e019_collect import select, pack, verify, CAP


class E019Contracts(unittest.TestCase):
    def test_reserve_and_whole_remaining_space_are_admitted_before_science(self):
        from e019_bootstrap import require_headroom
        gib = 1024**3
        require_headroom(45*gib, 100*gib, 100*gib)
        require_headroom(44*gib, 101*gib, 100*gib)
        for free, used in [(44*gib, 100*gib), (25*gib, 119*gib), (100*gib, 121*gib)]:
            with self.assertRaisesRegex(ValueError, 'allowance'):
                require_headroom(free, used, 100*gib)

    def test_original_VM_clock_credit_retention_budget_and_release_refusals(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d)/'config.json'
            p.write_text('{}')
            cfg = dict(_path=str(p), vm_start_epoch=1000)
            release = dict(config=binding(p), provider_STOP_seconds=STOP_SECONDS, ceiling_USD=5,
                estimated_incremental_gross_USD=4, storage_retention_extended=False,
                covered_costs=['compute', 'disk', 'storage', 'network', 'operations'],
                credit_valid_until_epoch=100000, storage_valid_until_epoch=100000)
            for k in ['credit_gate_passed', 'pending_usage_accounted', 'native_gates_passed',
                    'watchdog_verified', 'existing_VM_only', 'full_axes_verified']:
                release[k] = True
            admission(cfg, release, 1100)
            for key, value in [('watchdog_verified', False), ('native_gates_passed', False),
                    ('ceiling_USD', 1), ('estimated_incremental_gross_USD', 5.01),
                    ('provider_STOP_seconds', 999999), ('storage_retention_extended', True),
                    ('covered_costs', ['compute']), ('storage_valid_until_epoch', 1000+STOP_SECONDS)]:
                changed = release | {key: value}
                with self.assertRaises(ValueError, msg=key):
                    admission(cfg, changed, 1100)
            with self.assertRaises(TimeoutError):
                admission(cfg, release, 1000+SECONDS)
            launch = dict(root=d, source='a'*40, vm_start_epoch=1000, service_name='e019-held', archive_prefix='gs://existing-private/prefix')
            built = configuration(launch, REPO, 123, {})
            self.assertEqual(built['source_commit'], launch['source'])
            self.assertIn('E019-window-context', built['reuse_lock'])
            self.assertTrue(built['wheel'].endswith('/payload/dl_binner-0.1.0.dev7-py3-none-any.whl'))
            self.assertEqual(SECONDS, 28800)
            self.assertEqual(STOP_SECONDS, 29700)

    def test_real_collection_all_members_aliases_named_token_omissions_and_caps(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            work, evidence = root/'work', root/'evidence'
            unit = work/'units/fixture'
            for folder in ['tokens', 'train', 'group', 'export/post']:
                (unit/folder).mkdir(parents=True)
            evidence.mkdir()
            (evidence/'source.json').write_text('{}')
            for name in ['counts', 'coordinates', 'rows', 'flipped']:
                (unit/'tokens'/f'{name}.npy').write_bytes(b'opaque engineering bytes')
            (unit/'tokens/tokens.json').write_text('{}')
            (unit/'embeddings.npz').write_bytes(b'exact byte embedding')
            (unit/'train/reference.npz').write_bytes(b'exact byte embedding')
            (unit/'train/checkpoint.pt').write_bytes(b'checkpoint')
            (unit/'group/graph.npz').write_bytes(b'sparse engineering bytes')
            (unit/'export/post/unassigned.fna').write_text('>opaque\nACGT\n')
            result = pack(work, evidence, root/'return')
            self.assertEqual(result['status'], 'SUCCESS')
            self.assertEqual(len(result['aliases']), 1)
            self.assertEqual(len(result['omitted_retained_on_disk']), 5)
            verify(root/'return/e019-evidence.tar.gz', result['archive'])
            # Exercise the exact isolated subprocess and sibling-helper layout
            # outside the checkout, rather than giving an in-process import credit.
            called = subprocess.run([sys.executable, '-I', '-B', str(REPO/'scripts/e019_collect.py'),
                '--work', str(work), '--evidence', str(evidence), '--output', str(root/'cli-return')],
                cwd=root, capture_output=True, text=True)
            self.assertEqual(called.returncode, 0, called.stdout+called.stderr)
            self.assertTrue(json.loads(called.stdout)['every_member_verified'])
            with self.assertRaisesRegex(ValueError, 'prospective'):
                pack(work, evidence, root/'too-small', ceiling=8)
            self.assertFalse((root/'too-small/e019-evidence.tar.gz').exists())
            (unit/'train/reference.npz').write_bytes(b'not identical')
            with self.assertRaisesRegex(ValueError, 'exact bytes'):
                select(work)
            failed = pack(work, evidence, root/'failed-stage-return', allow_incomplete=True)
            self.assertTrue(failed['incomplete_failure_evidence'])
            self.assertFalse(failed['aliases'])
            verify(root/'failed-stage-return/e019-evidence.tar.gz', failed['archive'])
            (unit/'embeddings.npz').unlink()
            missing = pack(work, evidence, root/'missing-reload-return', allow_incomplete=True)
            self.assertTrue(missing['every_member_verified'])
            (unit/'embeddings.npz').write_bytes(b'exact byte embedding')
            (unit/'train/reference.npz').write_bytes(b'exact byte embedding')
            (unit/'tokens/unrecognized.npy').write_bytes(b'wrong')
            with self.assertRaisesRegex(ValueError, 'Unknown context'):
                select(work)

    def test_no_hidden_truth_input_or_unadmitted_engineering_schedule(self):
        from e019_control import validate_plan
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            base = json.loads((REPO/'src/dl_binner/resources/multiview.json').read_text())
            base['epochs'] = 2
            cfg = json.loads((REPO/'experiments/E019-window-context/config.json').read_text())
            cfg['epochs'] = 2
            (root/'base.json').write_text(json.dumps(base))
            (root/'config.json').write_text(json.dumps(cfg))
            unit = {k: 'opaque-unused-engineering' for k in ['fasta', 'features', 'views', 'marker_cache']}
            plan = dict(kind='E019 window-context candidate', work=d,
                units={'E009-context': unit, 'oral-context': unit.copy()}, threads=4, python=sys.executable,
                worker=str(REPO/'scripts/e019_control.py'), workflow_python=sys.executable,
                snakefile=str(REPO/'experiments/E019-window-context/Snakefile'), config=str(root/'config.json'),
                base_config=str(root/'base.json'), hmm='unused-tiny', reuse_lock='unused', candidate_lock='unused')
            validate_plan(plan, engineering=True)
            with self.assertRaisesRegex(ValueError, 'seed/schedule'):
                validate_plan(plan)
            changed = copy.deepcopy(plan)
            changed['units']['oral-context']['truth'] = 'forbidden'
            with self.assertRaisesRegex(ValueError, 'truth path'):
                validate_plan(changed, engineering=True)

    def test_review_refuses_unverified_shutdown_members_or_cost_before_truth(self):
        from e019_review import admission_contract
        with tempfile.TemporaryDirectory() as d:
            path = Path(d)/'admission.json'
            valid = dict(provider_status='TERMINATED', archive_and_every_member_verified=True,
                cost_and_retention_admitted=True, workflow_completed=True)
            path.write_text(json.dumps(valid))
            self.assertEqual(admission_contract(path), valid)
            for key, value in [('provider_status', 'RUNNING'), ('archive_and_every_member_verified', False),
                    ('cost_and_retention_admitted', False), ('workflow_completed', False)]:
                path.write_text(json.dumps(valid | {key: value}))
                with self.assertRaisesRegex(ValueError, 'admission'):
                    admission_contract(path)


if __name__ == '__main__':
    unittest.main()
