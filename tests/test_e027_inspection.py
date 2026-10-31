"""Real tiny archive/staging and strict incomplete-target admission contracts."""
import hashlib
import io
import json
from pathlib import Path
import sys
import tarfile
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).absolute().parents[1]/'scripts'))
from e027_inspection import archive_contract, stage, seal_from_inventory, scoped_admission, shutdown_contract
from e027_collect import verify
from e022_review import admission_contract


def binding_bytes(data):
    """Bind fixture bytes with the same public schema as native members."""
    return dict(bytes=len(data), sha256=hashlib.sha256(data).hexdigest())


class InspectionContracts(unittest.TestCase):
    """Do not equate intact failure evidence with successful scientific outputs."""

    def fixture(self, root):
        """Create a real compressed return with canonical, alias and omitted bytes."""
        canonical = 'work/units/E009-noGLM/teacher/checkpoint.json'
        alias = 'work/units/E009-GLM/teacher/checkpoint.json'
        payload = b'{"fixture":true}\n'; b = binding_bytes(payload)
        omitted = 'units/E009-noGLM/admit/views.npz'; omitted_b = binding_bytes(b'protected-original')
        inv = dict(kind='E027 exact-byte calibrated grouping return', members={canonical: b},
            aliases={alias: dict(b, canonical=canonical)},
            all_work_members={canonical[5:]: b, alias[5:]: b, omitted: omitted_b},
            omitted_retained_on_disk={omitted: dict(omitted_b, reason='Verified accepted input, not copied')},
            incomplete_failure_evidence=True)
        path = root/'return.tar.gz'
        with tarfile.open(path, 'w:gz') as out:
            for name, data in [('inventory.json', json.dumps(inv).encode()), (canonical, payload)]:
                m = tarfile.TarInfo(name); m.size = len(data); out.addfile(m, io.BytesIO(data))
        return path, inv, binding_bytes(path.read_bytes())

    def test_actual_streamed_members_and_cross_arm_alias(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp); archive, inv, expected = self.fixture(root)
            proof = archive_contract(archive, expected, root/'verified')
            self.assertTrue(proof['every_member_verified'])
            result = stage(archive, root/'verified', 'E009-GLM', root/'staged', reserve=0)
            self.assertEqual(result['status'], 'PASS')
            self.assertEqual(result['aliases'], 1)
            self.assertEqual((root/'staged/work/units/E009-GLM/teacher/checkpoint.json').read_bytes(),
                             b'{"fixture":true}\n')
            self.assertFalse((root/'staged/work/units/E009-noGLM/admit/views.npz').exists())
            with self.assertRaises(FileExistsError):
                stage(archive, root/'verified', 'E009-GLM', root/'staged', reserve=0)
            with self.assertRaises(ValueError):
                stage(archive, root/'verified', 'E009-GLM', root/'oversize', cap=1, reserve=0)

    def test_corruption_refused_even_with_new_whole_archive_hash(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp); archive, inv, expected = self.fixture(root)
            with tarfile.open(root/'bad.tar.gz', 'w:gz') as out:
                for name, data in [('inventory.json', json.dumps(inv).encode()),
                                   (next(iter(inv['members'])), b'{"fixture":false}\n')]:
                    m = tarfile.TarInfo(name); m.size = len(data); out.addfile(m, io.BytesIO(data))
            with self.assertRaises(ValueError):
                verify(root/'bad.tar.gz', binding_bytes((root/'bad.tar.gz').read_bytes()))

    def test_seals_refuse_extra_missing_and_corrupt_members(self):
        data = binding_bytes(b'real fixture'); prefix = 'units/opaque/student'
        seal = dict(status='PASS', files={'checkpoint.pt': data})
        inv = dict(all_work_members={prefix+'/checkpoint.pt': data, prefix+'/done.json': binding_bytes(b'seal')})
        self.assertEqual(seal_from_inventory(seal, prefix, inv)['status'], 'PASS')
        inv['all_work_members'][prefix+'/extra.json'] = data
        with self.assertRaises(ValueError): seal_from_inventory(seal, prefix, inv)
        del inv['all_work_members'][prefix+'/extra.json']
        inv['all_work_members'][prefix+'/checkpoint.pt'] = binding_bytes(b'corrupt')
        with self.assertRaises(ValueError): seal_from_inventory(seal, prefix, inv)

    def test_failed_global_workflow_stays_failed_for_closed_reference(self):
        args = ('reference', dict(provider_status='TERMINATED', workflow_completed=False),
                dict(cost_and_retention_admitted=True), dict(every_member_verified=True),
                dict(status='PASS'), dict(status='PASS', target='reference', native_exit=0,
                    all_dependency_seals_checked=True, independent_retained_inputs_verified=True,
                    complete_DNA_accounting_verified=True, frozen_rule_verified=True))
        v = scoped_admission(*args)
        self.assertFalse(v['global_workflow_completed'])
        self.assertTrue(v['global_failed_gate_not_waived'])
        with tempfile.TemporaryDirectory() as temp:
            p = Path(temp)/'scope.json'; p.write_text(json.dumps(v))
            with self.assertRaises(ValueError): admission_contract(p)
        for i, replacement in [(1, dict(provider_status='RUNNING', workflow_completed=False)),
                               (2, dict(cost_and_retention_admitted=False)),
                               (3, dict(every_member_verified=False)),
                               (5, dict(status='PARTIAL_UNSEALED')),
                               (5, dict(status='PASS'))]:
            bad = list(args); bad[i] = replacement
            with self.assertRaises(ValueError): scoped_admission(*bad)

    def test_shutdown_requires_matching_private_exit_boot_and_all_readbacks(self):
        identity = dict(pid=123, start_ticks=17, command_sha256='b'*64)
        stages = [dict(name='workflow', resources=dict(exit_code=1)),
                  dict(name='collect', resources=dict(exit_code=0))]
        for n in ['e027-evidence.tar.gz', 'e027-evidence.tar.gz.sha256', 'collection.json',
                  'collection-disk.jsonl', 'terminal-disk.json']:
            stages += [dict(name=p+n, resources=dict(exit_code=0)) for p in ['upload-', 'readback-']]
        completion = dict(status='FAILED', science_completed=False, stages=stages,
                          collection_readback_verified=True)
        b = binding_bytes(json.dumps(completion).encode())
        provider = dict(status='TERMINATED', lastStartTimestamp='2026-10-30T22:33:00+00:00',
                        lastStopTimestamp='2026-10-31T03:33:00+00:00')
        guest = [dict(namespace='e027-candidate', key='status', value=json.dumps(
            dict(status='FAILED', science_completed=False, completion=b)))]
        watchdog = dict(shutdown=True, decision='workflow exited', boot_id='boot', expected_process=identity)
        live = dict(boot_id='boot', expected_process=identity, observed_process=identity,
                    decision='workflow alive', shutdown=False)
        args = [provider, guest, completion, b, watchdog, dict(identity=identity), live,
                dict(measured_allocation_seconds=18000, cost_and_retention_admitted=True)]
        result = shutdown_contract(*args)
        self.assertFalse(result['workflow_completed'])
        self.assertTrue(result['collection_completed'])
        for i, replacement in [(0, dict(provider, status='RUNNING')),
                               (3, binding_bytes(b'different completion')),
                               (4, dict(watchdog, boot_id='different')),
                               (6, dict(live, observed_process=None)),
                               (7, dict(measured_allocation_seconds=17999, cost_and_retention_admitted=True))]:
            bad = list(args); bad[i] = replacement
            with self.assertRaises(ValueError): shutdown_contract(*bad)
        completion['stages'][-1]['resources']['exit_code'] = 1
        with self.assertRaises(ValueError): shutdown_contract(*args)


if __name__ == '__main__':
    unittest.main()
