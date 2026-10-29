"""Actual isolated entrypoint/collector/failure/gate contracts; no cloud action."""
import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest
from unittest.mock import patch

from e024_coverage import binding, write
from e026_collect import collect_controls, pack, CONTROLS
from e026_phase import admission, service_content, phase_exit, deliver_completion, STOP_SECONDS, SECONDS
from e026_launch import render_host, render_release, start
from e026_review import disposition
from e009_owner import supervisor

ROOT = Path(__file__).absolute().parents[1]


def controls(root):
    """Create closed synthetic controls in the exact production relative layout."""
    for name in CONTROLS+['config.json', 'science-plan.json', 'started.json', 'release.json',
                         'science-result.json', 'science-disk.jsonl', 'external-data.json']:
        p = root/name; p.parent.mkdir(parents=True, exist_ok=True)
        write(p, dict(data_copied=False) if name == 'external-data.json' else {})


class OperationalContracts(unittest.TestCase):
    def test_actual_gate_ready_file_atomic_publish_malformed_and_overwrite_refusal(self):
        from e026_gates import publish_completion
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp)/'completion.json'
            value = dict(status='PASS', full_science_started=False, no_install_or_recopy=True,
                         stages=[dict(resources=dict(exit_code=0))], config=dict(fixture=True))
            bad = copy.deepcopy(value); bad['stages'][0]['resources']['exit_code'] = 7
            with self.assertRaisesRegex(ValueError, 'cannot publish ready'): publish_completion(path, bad)
            self.assertFalse(path.exists())
            # The producer has no live controller; complete ready bytes persist.
            publish_completion(path, value)
            self.assertEqual(json.loads(path.read_text()), value)
            with self.assertRaises(FileExistsError): publish_completion(path, value)
            self.assertEqual(json.loads(path.read_text()), value)

    def test_reissuing_start_refuses_before_any_cloud_operation(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); write(root/'identity.json', dict(previous=True))
            with patch('e026_launch.Cloud', side_effect=AssertionError('Unexpected cloud operation')):
                with self.assertRaisesRegex(ValueError, 'Recorded attempt already exists'):
                    start(root)

    def test_exact_isolated_rendered_consumers_and_review_external_arguments(self):
        for code in [render_host(dict(root='/srv/dl_binner/experiments/e026/tiny', repo='/srv/dl_binner/repo'), {}),
                     render_release(dict(root='/srv/dl_binner/experiments/e026/tiny', repo='/srv/dl_binner/repo'), {})]:
            compile(code, 'actual-E026-rendered-controller', 'exec')
            self.assertNotIn('IDENTITY', code)
        with tempfile.TemporaryDirectory() as tmp:
            for name in ['control', 'information', 'collect', 'review', 'stage_review', 'phase', 'arm', 'gates', 'launch', 'probe', 'tiny']:
                r = subprocess.run([sys.executable, '-I', '-B', str(ROOT/'scripts'/('e026_'+name+'.py')), '--help'],
                                   cwd=tmp, capture_output=True, text=True, timeout=30)
                self.assertEqual(r.returncode, 0, r.stderr)
                if name == 'review':
                    self.assertIn('--external-features', r.stdout); self.assertIn('--external-receipt', r.stdout)
            text = service_content('/tmp/fixture', '/usr/bin/python3', '/tmp/repo/scripts/e026_phase.py', '/tmp/config.json', 'researcher')
            self.assertIn('Restart=no', text); self.assertIn('-I -B', text)

    def test_actual_control_inventory_alias_caps_and_corrupt_archive_refusal(self):
        from e023_collect import verify
        with tempfile.TemporaryDirectory() as tmp:
            r = Path(tmp); phase = r/'phase'; phase.mkdir(); controls(phase)
            evidence = r/'evidence'; evidence.mkdir()
            copied = collect_controls(phase, evidence/'controls')
            self.assertIn('logs/maintenance-restart-refused.json', copied)
            write(evidence/'external-data.json', dict(data_copied=False, fixture=True))
            work = r/'work'; work.mkdir(); write(work/'a.json', dict(test=True))
            (work/'same.json').write_bytes((work/'a.json').read_bytes()); (work/'DNA.fna').write_text('>q\nACGT\n')
            value = pack(work, evidence, r/'return')
            self.assertTrue(value['every_member_verified']); self.assertEqual(len(value['aliases']), 1)
            self.assertIn('DNA.fna', value['omitted_retained_on_disk'])
            with self.assertRaisesRegex(ValueError, 'cap exceeded'): pack(work, evidence, r/'too-small', ceiling=12)
            data = bytearray((r/'return/e026-evidence.tar.gz').read_bytes()); data[len(data)//2] ^= 255
            (r/'corrupt.gz').write_bytes(data)
            with self.assertRaisesRegex(ValueError, 'archive bytes/cap differ'): verify(r/'corrupt.gz', value['archive'])
            phase.joinpath(CONTROLS[0]).unlink()
            with self.assertRaisesRegex(ValueError, 'Missing completed-phase controls'):
                collect_controls(phase, r/'missing')
            collect_controls(phase, r/'failure-controls', True)
            self.assertIn(CONTROLS[0], json.loads((r/'failure-controls/control-inventory.json').read_text())['missing'])

    def test_credit_complete_cost_retention_and_recorded_envelope_are_required(self):
        with tempfile.TemporaryDirectory() as tmp:
            r = Path(tmp)
            for f in ['plan', 'config', 'gate']: write(r/(f+'.json'), {})
            cfg = dict(vm_start_epoch=1000, _path=str(r/'config.json'), plan=str(r/'plan.json'))
            release = dict(config=binding(r/'config.json'), plan=binding(r/'plan.json'), vm_start_epoch=1000,
                credit_gate_passed=True, pending_usage_accounted=True, native_gates_passed=True,
                watchdog_verified=True, provider_STOP_verified=True, existing_VM_only=True,
                full_axes_verified=True, headroom_measured=True, retention_passed=True,
                real_money_authorized=False, estimated_incremental_gross_USD=5.9, ceiling_USD=6,
                provider_STOP_seconds=STOP_SECONDS, storage_retention_extended=False,
                credit_valid_until_epoch=1799740800, storage_valid_until_epoch=1793746800,
                covered_costs=['compute', 'disk', 'storage', 'network', 'operations'],
                gate_files={str(r/'gate.json'): binding(r/'gate.json')})
            admission(cfg, release, 1100)
            # Limits can be revised under standing authorization before execution;
            # arbitrary drift without a matching recorded/source-bound envelope fails.
            for k, v in [('real_money_authorized', True), ('estimated_incremental_gross_USD', float('nan')),
                         ('storage_valid_until_epoch', 1793746801), ('covered_costs', ['compute'])]:
                bad = copy.deepcopy(release); bad[k] = v
                with self.assertRaises(ValueError): admission(cfg, bad, 1100)
            with self.assertRaises(ValueError): admission(cfg, release, 1000+SECONDS)

    def test_failed_actual_worker_and_terminal_delivery_are_not_success(self):
        with tempfile.TemporaryDirectory() as tmp:
            r = Path(tmp); s = supervisor(); log = r/'failed.log'
            with self.assertRaises(RuntimeError):
                s.supervise([sys.executable, '-I', '-B', '-c', 'print("intended-worker-failure",flush=True);raise SystemExit(7)'],
                            log, 10, 8000000000, s.isolated_env(4))
            failure = json.loads(log.with_suffix('.exit.json').read_text())
            self.assertEqual(failure['exit_code'], 7); self.assertIn('intended-worker-failure', log.read_text())
            self.assertEqual(phase_exit(dict(status='FAILED', science_completed=False, collection_readback_verified=True)), 1)
            events = []; result = dict(status='SUCCESS', science_completed=True, collection_readback_verified=True)
            with patch('e026_phase.status', lambda v: events.append(v['status'])):
                deliver_completion(result, r, time.time()+60, lambda path: events.append('upload'))
            self.assertEqual(events, ['upload', 'SUCCESS']); self.assertEqual(phase_exit(result), 0)

    def test_frozen_joint_disposition_no_winner_routing(self):
        anchors = {d: dict(bp_weighted_R95=.1, at_least_50_percent=20, at_least_90_percent=10) for d in ['E009', 'oral']}
        result = copy.deepcopy(anchors); result['oral']['bp_weighted_R95'] = .11
        self.assertEqual(disposition(result, anchors), 'KEEP')
        result['E009']['at_least_90_percent'] = 9
        self.assertEqual(disposition(result, anchors), 'MODIFY')
        self.assertEqual(disposition(anchors, anchors), 'ABANDON_THIS_FROZEN_POLICY')

    def test_actual_legacy_E025_external_data_CLI_on_real_tiny_outputs(self):
        from test_e025_retrieval import retained, CFG as old_cfg
        from e025_information import run as old_run
        from e025_cache_audit import audit as fast_old_audit
        from e025_collect import pack as old_pack
        from dl_binner.information.export import export
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); inp = root/'input'; inp.mkdir(); u, receipt = retained(inp)
            work = root/'work'; work.mkdir()
            old_run(receipt, u['graph'], u['marker_evidence'], work/'group', old_cfg)
            proof = fast_old_audit(receipt, u['graph'], u['marker_evidence'], work/'group', old_cfg)
            for arm in ['density', 'selected']:
                export(inp/'rebound/features.npz', work/'group'/(arm+'-partition.json'),
                       u['reference'], work/'export'/arm, arm == 'selected')
            (work/'audited').mkdir()
            write(work/'audited/done.json', dict(proof=proof))
            evidence = root/'evidence'; evidence.mkdir()
            write(evidence/'external-data.json', dict(data_copied=False, archive=dict(fixture=True),
                files=dict(rebound_features=binding(inp/'rebound/features.npz'), receipt=binding(receipt))))
            old_pack(work, evidence, root/'return')
            write(root/'admission.json', dict(provider_status='TERMINATED', archive_and_every_member_verified=True,
                cost_and_retention_admitted=True, workflow_completed=True, fixture=True))
            argv = [sys.executable, '-I', '-B', str(ROOT/'scripts/e026_review.py'), '--legacy-e025',
                '--contracts-only', '--work', str(work), '--inventory', str(root/'return/inventory.json'),
                '--admission', str(root/'admission.json'), '--external-features', str(inp/'rebound/features.npz'),
                '--external-receipt', str(receipt), '--output', str(root/'review.json')]
            r = subprocess.run(argv, cwd=root, capture_output=True, text=True, timeout=30)
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertFalse(json.loads((root/'review.json').read_text())['truth_opened'])
            missing = argv.copy(); at = missing.index('--external-receipt'); del missing[at:at+2]
            r = subprocess.run(missing, cwd=root, capture_output=True, text=True, timeout=30)
            self.assertNotEqual(r.returncode, 0); self.assertIn('Missing explicit review/external-data arguments', r.stderr)

    def test_new_numeric_axis_mapping_and_population_reader(self):
        import numpy as np
        from dl_binner.calibrated.arrays import save, load
        from e026_review import core_neighborhood_diagnostics
        with tempfile.TemporaryDirectory() as tmp:
            r = Path(tmp); ids = np.array(['opaque-z', 'opaque-a', 'excluded'])
            value = dict(queries=np.array([1, 0]), cores=np.array([0]),
                         neighbors=np.array([[0], [-1]]), counts=np.array([1, 0]))
            save(r/'cache.npz', value, dict(kind='fixture_numeric'), ids)
            a, _ = load(r/'cache.npz', 'fixture_numeric', ids)
            np.testing.assert_array_equal(a['queries'], [1, 0])
            with self.assertRaisesRegex(ValueError, 'external full axis differ'):
                load(r/'cache.npz', 'fixture_numeric', ids[::-1])
            data = dict(ids=ids, lengths=np.array([6000, 900, 80]), depth=np.array([[1.], [0.], [0.]]))
            result = core_neighborhood_diagnostics(data, a, ['target', 'target', None], {'target'}, set())
            self.assertEqual(result['all_queries'], 2); self.assertEqual(result['excluded_or_nonquery_rows'], 1)
            self.assertEqual(result['availability_edges']['measured_zero->positive']['same_origin_weighted_bp'], 900)


if __name__ == '__main__': unittest.main()
