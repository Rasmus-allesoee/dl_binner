"""Actual release refusal and compact archive/member contracts; no cloud calls."""
import json
from pathlib import Path
import sys
import tarfile
import tempfile
import time
import unittest

sys.path.insert(0,str(Path(__file__).absolute().parents[1]/'scripts'))
import e014_phase as phase


class PhaseContracts(unittest.TestCase):
    def test_release_needs_all_gates_and_original_expiry(self):
        with tempfile.TemporaryDirectory()as t:
            path=Path(t)/'config.json';path.write_text('{}');now=time.time()
            cfg=dict(_path=str(path),vm_start_epoch=now,stages=[dict(name='comparison')])
            release={k:True for k in ['credit_gate_passed','pending_usage_accounted','oral_truth_admitted',
                'native_runtime_gates_passed','full_input_axes_verified','watchdog_release_verified','no_resource_change','source_and_wheel_verified']}
            release.update(provider_stop_seconds=phase.STOP_SECONDS,incremental_gross_ceiling_usd=10,
                storage_retention_extended=False,covered_costs=['compute','disk','storage','network','operations'],
                credit_valid_until_epoch=now+999999,storage_valid_until_epoch=now+999999,
                estimated_incremental_gross_usd=6,phase_config=phase.binding(path))
            phase.admission(cfg,release,now)
            for key in ['oral_truth_admitted','credit_gate_passed','native_runtime_gates_passed','watchdog_release_verified']:
                bad=release|{key:False}
                with self.assertRaisesRegex(ValueError,'gate incomplete'):phase.admission(cfg,bad,now)
            with self.assertRaisesRegex(TimeoutError,'clock'):phase.admission(cfg,release,now+phase.SECONDS)
            with self.assertRaisesRegex(ValueError,'expires'):phase.admission(cfg,release|dict(storage_valid_until_epoch=now+60),now)
            with self.assertRaisesRegex(ValueError,'sole released'):phase.admission(cfg|dict(stages=[]),release,now)

    def test_real_archive_retains_compact_and_binds_bulk(self):
        with tempfile.TemporaryDirectory()as t:
            root=Path(t)/'run';root.mkdir();(root/'partition.json').write_text('{"x":0}')
            (root/'full.fna').write_text('>x\nACGT\n');(root/'features.npz').write_bytes(b'bulk exact fixture')
            archive=Path(t)/'return.tar.gz';result=phase.collect(root,archive)
            self.assertEqual(result['all_members'],3);self.assertEqual(result['retained_members'],1)
            with tarfile.open(archive)as tar:self.assertEqual(set(tar.getnames()),{'inventory.json','run/partition.json'})
            inventory=json.loads(archive.with_suffix('.inventory.json').read_text())
            self.assertEqual(inventory['all_result_members']['full.fna'],phase.binding(root/'full.fna'))
            with self.assertRaisesRegex(ValueError,'cap exceeded'):phase.collect(root,Path(t)/'small.tar.gz',ceiling=1)
            (root/'link.json').symlink_to(root/'partition.json')
            with self.assertRaisesRegex(ValueError,'link refused'):phase.collect(root,Path(t)/'links.tar.gz')


if __name__=='__main__':unittest.main()
