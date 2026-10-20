"""Actual isolated launcher/reuse/collector refusal contracts; no cloud calls."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest

REPO=Path(__file__).absolute().parents[1]
sys.path.insert(0,str(REPO/'scripts'))
from e014_collect import binding
from e017_collect import pack,verify
from e017_phase import configuration,admission,science_command,SECONDS,STOP_SECONDS
from e017_bootstrap import source_lock
from e017_reuse import verify as verify_reuse


class Operations(unittest.TestCase):
    def test_system_parent_uses_owned_lexical_science_interpreter(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);plan=root/'science-plan.json'
            # Use the running lexical environment, retaining the exact argv from
            # the parent rather than accidentally executing its system Python.
            plan.write_text(json.dumps(dict(python=sys.executable)))
            command=science_command(dict(science_plan=str(plan),repo=str(REPO)))
            self.assertEqual(command,[sys.executable,'-I','-B',str(REPO/'scripts/e017_control.py'),
                                      '--plan',str(plan),'--workflow'])
            r=subprocess.run(command+['--help'],cwd=root,capture_output=True,text=True,timeout=20)
            self.assertEqual(r.returncode,0,r.stdout+r.stderr)
            plan.write_text(json.dumps(dict(python='/job/owned-env/bin/python')))
            self.assertEqual(science_command(dict(science_plan=str(plan),repo=str(REPO)))[0],
                             '/job/owned-env/bin/python')

    def test_native_repair_preserves_original_scientific_freeze(self):
        original=json.loads((REPO/'experiments/E017-information-aware-grouping/candidate-lock.json').read_text())
        current=source_lock(REPO)
        changes={p for p in original['files'] if original['files'][p]!=current['files'][p]}
        self.assertEqual(changes,{'scripts/e017_phase.py','scripts/e017_bootstrap.py','tests/test_e017_operations.py'})
        for p,b in current['files'].items():self.assertEqual(binding(REPO/p),b,p)
        self.assertEqual(current['tested_wheel'],original['tested_wheel'])
        self.assertEqual(current['source_package_members'],original['source_package_members'])

    def test_isolated_help_actual_entrypoints_outside_checkout(self):
        for name in ['control','collect','reuse','phase','arm','runtime','bootstrap']:
            with self.subTest(name=name),tempfile.TemporaryDirectory() as d:
                r=subprocess.run([sys.executable,'-I','-B',str(REPO/f'scripts/e017_{name}.py'),'--help'],
                                 cwd=d,capture_output=True,text=True,timeout=20)
                self.assertEqual(r.returncode,0,r.stdout+r.stderr)

    def test_current_source_storage_and_new_budget_clock_are_separate(self):
        self.assertEqual((SECONDS,STOP_SECONDS),(10800,11700))
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);plan=root/'science-plan.json';plan.write_text('{}')
            ident=dict(root=str(root),service_name='tiny',source='a'*40,vm_start_epoch=time.time(),archive_prefix='gs://private-existing/test')
            cfg=configuration(ident,REPO,100,{str(plan):binding(plan)})
            p=root/'phase-config.json';p.write_text(json.dumps(cfg));cfg['_path']=str(p)
            release={k:True for k in ['credit_gate_passed','pending_usage_accounted','native_gates_passed','watchdog_verified','existing_VM_only','full_axes_verified']}
            release.update(config=binding(p),provider_STOP_seconds=11700,ceiling_USD=2,estimated_incremental_gross_USD=1.2,
                           compressed_export_GiB=3,
                           storage_authorization_sha256=cfg['storage_authorization_sha256'],
                           covered_costs=['compute','disk','storage','network','operations'],
                           credit_valid_until_epoch=time.time()+100000,storage_valid_until_epoch=time.time()+100000)
            admission(cfg,release,time.time())
            for drift in [dict(provider_STOP_seconds=15300),dict(ceiling_USD=3),dict(estimated_incremental_gross_USD=2.1),
                          dict(storage_authorization_sha256='bad'),dict(watchdog_verified=False),dict(storage_valid_until_epoch=1),
                          dict(estimated_incremental_gross_USD=float('nan')),dict(compressed_export_GiB=4)]:
                with self.subTest(drift=drift),self.assertRaises((ValueError,TimeoutError)):
                    admission(cfg,release|drift,time.time())
            with self.assertRaises(TimeoutError):admission(cfg,release,cfg['vm_start_epoch']+10800)
            self.assertEqual(cfg['reuse_lock'],str(REPO/'experiments/E017-information-aware-grouping/reuse-lock.json'))

    def test_actual_collection_keeps_new_graph_and_recruitment_caches(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);work=p/'work';u=work/'units/tiny/group';u.mkdir(parents=True);e=p/'evidence';e.mkdir()
            (u/'graph.npz').write_bytes(b'tiny graph fixture')
            (u/'recruitment.npz').write_bytes(b'tiny recruitment fixture')
            (u/'partition.json').write_text('{"ids":["opaque"],"assignment":[-1]}')
            (u/'complete.fna').write_text('>opaque\nACGTN\n')
            (e/'native.json').write_text('{"status":"PASS"}')
            result=pack(work,e,p/'return');self.assertTrue(result['every_member_verified'])
            receipt=verify(p/'return/e017-evidence.tar.gz',result['archive'],p/'verified')
            self.assertTrue(receipt['every_member_verified'])
            inv=json.loads((p/'verified/inventory.json').read_text())
            self.assertIn('work/units/tiny/group/recruitment.npz',inv['members'])
            self.assertIn('units/tiny/group/complete.fna',inv['omitted_DNA_retained_on_disk'])
            (u/'linked.npz').symlink_to(u/'graph.npz')
            with self.assertRaisesRegex(ValueError,'link refused'):pack(work,e,p/'refused')
            (p/'return/e017-evidence.tar.gz').write_bytes(b'corruption')
            with self.assertRaisesRegex(ValueError,'bytes/cap'):verify(p/'return/e017-evidence.tar.gz',result['archive'])
            (u/'linked.npz').unlink()
            with self.assertRaisesRegex(ValueError,'logical return bound'):
                pack(work,e,p/'too-small',ceiling=100)

    def test_reuse_refuses_corruption_without_recopy(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d).resolve();original=p/'sealed.bin';original.write_bytes(b'accepted bytes')
            lock=p/'lock.json';lock.write_text(json.dumps(dict(kind='E017 in-place sealed E016 reuse',files={str(original):binding(original)})))
            result=verify_reuse(lock,p/'pass.json');self.assertFalse(result['copy_fallback'])
            original.write_bytes(b'corrupt')
            with self.assertRaisesRegex(ValueError,'no recopy'):verify_reuse(lock,p/'failure.json')
            self.assertFalse((p/'failure.json').exists());self.assertEqual(original.read_bytes(),b'corrupt')

    def test_DAG_has_only_serial_cached_stages(self):
        s=(REPO/'experiments/E017-information-aware-grouping/Snakefile').read_text()
        self.assertNotIn('rule train:',s);self.assertNotIn('rule embed:',s);self.assertNotIn('rule markers:',s)
        self.assertIn("input: previous_unit",s);self.assertIn("UNITS[i-1]+'/audit.json'",s)
        self.assertEqual(s.count('threads: 4'),4)
        control=(REPO/'scripts/e017_control.py').read_text();self.assertIn("'--cores','4'",control);self.assertNotIn("'--jobs'",control)


if __name__=='__main__':unittest.main()
