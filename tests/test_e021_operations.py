"""Actual capped collector and closed release contracts; no cloud API mutation."""
import importlib.util,json,os,sys,tempfile,unittest
from unittest.mock import patch
import tarfile
from pathlib import Path
sys.path.insert(0,str(Path(__file__).absolute().parents[1]/'scripts'))
from e021_collect import pack,verify,binding,CappedWriter
from e021_phase import admission,configuration,SECONDS,STOP_SECONDS


class Operations(unittest.TestCase):
    def test_real_inventory_gzip_return_and_explicit_GLMS_omissions(self):
        with tempfile.TemporaryDirectory()as tmp:
            r=Path(tmp);w=r/'work';e=r/'evidence';w.mkdir();e.mkdir();p=w/'units/u/frozen';p.mkdir(parents=True)
            (p/'vectors.npy').write_bytes(b'new native vectors');(p/'bank.json').write_text('{}');(p/'views.jsonl').write_text('{}\n'*30000);(p/'ids.npy').write_bytes(b'opaque ids');(e/'source.json').write_text('{}')
            out=pack(w,e,r/'return',ceiling=20000);self.assertLess(out['archive']['bytes'],20000);self.assertTrue(out['every_member_verified']);self.assertIn('units/u/frozen/vectors.npy',out['omitted_retained_on_disk']);self.assertEqual(verify(r/'return/e021-evidence.tar.gz')['archive'],out['archive'])
            (w/'embeddings.npz').write_bytes(os.urandom(50000))
            with self.assertRaisesRegex(ValueError,'Compressed return cap'):pack(w,e,r/'limited',ceiling=1000)
            self.assertFalse((r/'limited/e021-evidence.tar.gz').exists());self.assertTrue((r/'limited/e021-evidence.tar.gz.partial').exists())
            self.assertLessEqual((r/'limited/e021-evidence.tar.gz.partial').stat().st_size,1000)

    def test_manifest_counts_inside_logical_cap_on_writer_and_reader(self):
        with tempfile.TemporaryDirectory()as tmp:
            r=Path(tmp);w=r/'work';e=r/'evidence';w.mkdir();e.mkdir();(w/'events.json').write_bytes(b'x'*1000)
            pack(w,e,r/'first');archive=r/'first/e021-evidence.tar.gz'
            with tarfile.open(archive,'r:gz')as t:sizes=[m.size for m in t]
            cap=max(sizes)+1
            self.assertGreater(sum(sizes),cap)
            # Only the budget is mocked; actual tar reader and writer run.
            with patch('e021_collect.LOGICAL_CAP',cap):
                with self.assertRaisesRegex(ValueError,'Manifest-inclusive'):pack(w,e,r/'limited-logical')
                self.assertFalse((r/'limited-logical/e021-evidence.tar.gz.partial').exists())
                with self.assertRaisesRegex(ValueError,'archive member'):verify(archive)
            with patch('e021_collect.MANIFEST_CAP',1):
                with self.assertRaisesRegex(ValueError,'bounded manifest'):verify(archive)

    def test_actual_configuration_translates_source_and_new_wheel(self):
        with tempfile.TemporaryDirectory()as tmp:
            root=Path(tmp);identity=dict(root=str(root),source='a'*40,service_name='held',vm_start_epoch=1792780000,archive_prefix='gs://private/e021')
            cfg=configuration(identity,root,100,{})
            self.assertEqual(cfg['source_commit'],'a'*40)
            self.assertTrue(cfg['wheel'].endswith('dl_binner-0.1.0.dev8-py3-none-any.whl'))
            self.assertEqual(cfg['science_plan'],str(root/'science-plan.json'))

    def test_fresh_release_requires_real_runtime_credit_watchdog_and_no_extension(self):
        with tempfile.TemporaryDirectory()as tmp:
            p=Path(tmp)/'config.json';p.write_text('{}');start=1792780000
            cfg=dict(vm_start_epoch=start,_path=str(p),storage_authorization_sha256='storage')
            release={k:True for k in ['credit_gate_passed','pending_usage_accounted','native_gates_passed','watchdog_verified','existing_VM_only','full_axes_verified','frozen_extraction_runtime_passed','full_scale_RAM_passed','native_throughput_and_return_admitted','local_review_headroom_passed']}
            release.update(config=binding(p),provider_STOP_seconds=STOP_SECONDS,ceiling_USD=25,estimated_incremental_gross_USD=24.0,storage_authorization_sha256='storage',compressed_export_GiB=2,storage_retention_extended=False,covered_costs=['compute','disk','storage','network','operations'],credit_valid_until_epoch=1800000000,storage_valid_until_epoch=1793142000)
            admission(cfg,release,start+10)
            with self.assertRaises(ValueError):admission(cfg,release|dict(full_scale_RAM_passed=False),start+10)
            with self.assertRaises(ValueError):admission(cfg,release|dict(estimated_incremental_gross_USD=26),start+10)
            with self.assertRaises(ValueError):admission(cfg,release|dict(storage_valid_until_epoch=1793142001),start+10)
            with self.assertRaises(TimeoutError):admission(cfg,release,start+SECONDS)

if __name__=='__main__':unittest.main()
