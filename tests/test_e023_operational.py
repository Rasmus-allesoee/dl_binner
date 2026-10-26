"""Pure production admission/restore/collector contracts; no cloud or community work."""
import copy
import json
from pathlib import Path
import tempfile
import unittest

from e023_control import verify_reuse, verify_source, validate_plan
from e023_phase import admission, compact_collection, configuration
from e023_arm import service_content
from e023_collect import pack, verify
from e014_collect import binding

ROOT=Path(__file__).absolute().parents[1]


class Operational(unittest.TestCase):
    def test_rendered_workflow_probe_compiles_before_native_execution(self):
        from e023_gates import workflow_probe
        code=workflow_probe('3.12.10','9.16.3')
        compile(code,'actual-rendered-workflow-probe','exec')
        self.assertIn("('3.12.10', '9.16.3')",code)

    def test_large_member_receipt_stays_out_of_atomic_completion_control(self):
        with tempfile.TemporaryDirectory()as d:
            p=Path(d)/'collection.json'
            p.write_text(json.dumps(dict(status='SUCCESS',archive=dict(bytes=1,sha256='frozen'),regular_members=10003,
                logical_member_bytes=100000,every_member_verified=True,aliases={},
                omitted_retained_on_disk={str(i):dict(bytes=1,sha256='frozen')for i in range(10000)})))
            value=compact_collection(p)
            self.assertEqual(value['omitted_retained_members'],10000)
            self.assertEqual(value['collection_receipt'],binding(p))
            self.assertLess(len(json.dumps(value)),2048)

    def test_actual_source_freeze_reader_refuses_source_drift(self):
        with tempfile.TemporaryDirectory()as d:
            p=Path(d);f=p/'actual.py';f.write_text('pass\n')
            lock=p/'source.json';lock.write_text(json.dumps(dict(kind='E023 exact prospective research overlay and execution source',files={'actual.py':binding(f)})))
            self.assertEqual(verify_source(lock,p)['members'],1)
            f.write_text('print(1)\n')
            with self.assertRaisesRegex(ValueError,'source/default/helper'):verify_source(lock,p)

    def test_real_restore_reader_refuses_missing_corrupt_and_links(self):
        with tempfile.TemporaryDirectory()as d:
            p=Path(d);f=p/'retained';f.write_text('accepted')
            lock=p/'lock.json';lock.write_text(json.dumps(dict(kind='E023 restore-only dual-anchor reuse',files={str(f):binding(f)})))
            self.assertEqual(verify_reuse(lock)['files'],1)
            f.write_text('corrupt')
            with self.assertRaisesRegex(ValueError,'no fallback'):verify_reuse(lock)
            f.unlink();f.symlink_to(lock)
            with self.assertRaisesRegex(ValueError,'link'):verify_reuse(lock)

    def test_fresh_credit_clock_storage_and_watchdog_scope(self):
        with tempfile.TemporaryDirectory()as d:
            p=Path(d)/'config.json';p.write_text('{}')
            cfg=dict(_path=str(p),vm_start_epoch=1793000000,storage_authorization_sha256='frozen-storage')
            release=dict(config=binding(p),provider_STOP_seconds=8100,ceiling_USD=3,
                real_money_authorized=False,estimated_incremental_gross_USD=2.1,storage_retention_extended=False,
                storage_authorization_sha256='frozen-storage',storage_valid_until_epoch=1793746800,
                credit_valid_until_epoch=1800000000,covered_costs=['compute','disk','storage','network','operations'])
            release.update({k:True for k in ['credit_gate_passed','pending_usage_accounted','native_gates_passed','watchdog_verified','existing_VM_only','full_axes_verified']})
            admission(cfg,release,1793000020)
            for key,value in [('ceiling_USD',4),('real_money_authorized',True),('watchdog_verified',False),
                              ('storage_valid_until_epoch',1793746801),('storage_authorization_sha256','wrong'),
                              ('estimated_incremental_gross_USD',float('nan'))]:
                bad=copy.deepcopy(release);bad[key]=value
                with self.subTest(key=key),self.assertRaises((ValueError,TimeoutError)):admission(cfg,bad,1793000020)
            with self.assertRaises(TimeoutError):admission(cfg,release,1793010000)
            service=service_content(Path('/repo'),Path('/work'),'research',Path('/config'),600)
            self.assertIn('Restart=no',service);self.assertIn('RefuseManualStop=yes',service)
            self.assertIn('e023_phase.py',service);self.assertIn('RuntimeMaxSec=600',service)

    def test_exact_new_hierarchy_collector_and_cap(self):
        with tempfile.TemporaryDirectory()as d:
            p=Path(d);w=p/'work';w.mkdir();e=p/'evidence';e.mkdir()
            (w/'hierarchy.npz').write_bytes(b'actual-opaque-tiny-inventory-member')
            (w/'decisions.json').write_text('{}');(w/'all.fna').write_text('>q\nACGT\n')
            r=pack(w,e,p/'return');self.assertTrue(r['every_member_verified'])
            self.assertEqual(r['planned_science_fits'],0);self.assertEqual(len(r['omitted_retained_on_disk']),1)
            self.assertEqual(verify(p/'return/e023-evidence.tar.gz',r['archive'])['archive'],r['archive'])
            with self.assertRaisesRegex(ValueError,'cap exceeded'):pack(w,e,p/'too-small',ceiling=8)

    def test_source_plan_rejects_truth_path_and_expansion(self):
        plan=json.loads((ROOT/'experiments/E023-adaptive-density-bins/plan-template.json').read_text())
        plan['config']=str(ROOT/'experiments/E023-adaptive-density-bins/config.json')
        validate_plan(plan,True)
        plan['units']['oral-E019']['truth']='/not-a-feature'
        with self.assertRaisesRegex(ValueError,'truth/training'):validate_plan(plan,True)

    def test_new_review_refuses_unadmitted_outputs_before_any_truth_read(self):
        from e023_review import review
        with tempfile.TemporaryDirectory()as d:
            p=Path(d);a=p/'admission.json';a.write_text('{}')
            with self.assertRaisesRegex(ValueError,'Independent shutdown'):
                review(p/'E009-E022',p/'missing',p/'missing',a,p/'out','E009',p/'missing',p/'missing')
            self.assertFalse((p/'out').exists())


if __name__=='__main__':unittest.main()
