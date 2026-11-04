"""Real sorter/transport, sealed resume, strict byte collection and release refusal."""
import hashlib
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT=Path(__file__).absolute().parents[1]
sys.path[:0]=[str(ROOT/'scripts'),str(ROOT/'tests/product')]
from e033_measure import sort_stream,release_sorted
from e033_collect import pack,verify
from e033_control import read_plan,constructor_cache,verify_constructor_cache
from e024_coverage import binding,write
from e024_control import seal
from test_multiscale_measurement import fixture
from dl_binner.multiscale.measurement import summarize


class Operations(unittest.TestCase):
    def test_actual_native_local_sort_tee_hash_measure_and_only_new_copy_release(self):
        import pysam
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);f,v,b=fixture(root/'fixture')
            # Wrapper invokes the actual bundled HTSlib sorter, no stand-in SAM parser.
            sorter=root/'samtools';sorter.write_text('#!'+sys.executable+'\nimport sys,pysam\npysam.sort(*sys.argv[2:])\n');sorter.chmod(0o700)
            r=dict(source=str(b),sorted=False,sample='Z9',**binding(b))
            out=sort_stream(r,root/'sorted',sorter,engineering=True)
            self.assertTrue(out.is_file());self.assertEqual(json.loads((root/'sorted/sort.json').read_text())['source_exit'],0)
            summarize(out,f,v,root/'summary','Z9')
            old=binding(b);release_sorted(out,root/'sorted/sort.json',root/'summary/sample.json')
            self.assertFalse(out.exists());self.assertEqual(binding(b),old)
            with self.assertRaisesRegex(ValueError,'Generation-pinned'):
                sort_stream(dict(r,source='gs://dl-binner-archive-167650584170/e024/unpinned.bam'),root/'remote-refused',sorter)
            wrong=dict(r,sha256='0'*64)
            with self.assertRaisesRegex(ValueError,'byte/hash'):
                sort_stream(wrong,root/'bad',sorter,engineering=True)
            self.assertTrue((root/'bad/failure.json').is_file());self.assertFalse((root/'bad/sort.json').exists())

    def test_complete_collection_exact_hardlinks_and_refuse_over_cap_or_corruption(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);work=root/'work';work.mkdir();e=root/'evidence';e.mkdir()
            (work/'a').write_bytes(b'payload');os.link(work/'a',work/'b');(e/'gate.json').write_text('{}\n')
            r=pack(work,e,root/'return');self.assertTrue(r['every_member_verified'])
            self.assertEqual(len(r['aliases']),1);self.assertFalse(r['omitted_retained_on_disk'])
            archive=root/'return/e033-evidence.tar.gz'
            with archive.open('ab') as f:f.write(b'bad')
            with self.assertRaisesRegex(ValueError,'bytes/cap'):verify(archive,r['archive'])
            with patch('e033_collect.LOGICAL',2):
                with self.assertRaisesRegex(ValueError,'logical cap'):pack(work,e,root/'capped')
            (work/'link').symlink_to(work/'a')
            with self.assertRaisesRegex(ValueError,'symlink'):pack(work,e,root/'linked')

    def test_constructor_adapter_does_not_claim_historical_reuse_and_binds_every_member(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder)/'mode';root.mkdir()
            for name in ['forest','construct','e023']:
                p=root/name/('science/result' if name=='e023' else 'result');p.mkdir(parents=True)
                (p/'closed.json').write_text('{}\n');seal(root/name)
            cached=constructor_cache(root,root/'cache')
            r=verify_constructor_cache(root,cached);self.assertIn('NOT historical E031 reuse',r['kind'])
            (cached/'unexpected').write_text('bad')
            with self.assertRaisesRegex(ValueError,'inventory'):verify_constructor_cache(root,cached)

    def test_actual_full_stream_member_alias_verification_with_compact_staging(self):
        from e033_stream import restore
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);work=root/'work';work.mkdir();e=root/'evidence';e.mkdir()
            (work/'select/result').mkdir(parents=True);(work/'select/result/a.json').write_text('{}\n')
            os.link(work/'select/result/a.json',work/'select/result/alias.json')
            (work/'not-needed').write_bytes(b'preserve remotely, hash but do not stage')
            result=pack(work,e,root/'return');archive=root/'return/e033-evidence.tar.gz'
            with archive.open('rb') as stream:
                r=restore(stream,dict(size=archive.stat().st_size,generation='1'),result['archive'],root/'return/inventory.json',root/'staged','mode',reserve=0)
            self.assertTrue(r['full_archive_every_member_verified'])
            self.assertTrue((root/'staged/work/select/result/a.json').is_file())
            self.assertTrue((root/'staged/work/select/result/alias.json').is_file())
            self.assertFalse((root/'staged/work/not-needed').exists())
            self.assertTrue((root/'staged/stream-admission.json').exists())
            with archive.open('rb') as stream:
                with self.assertRaisesRegex(ValueError,'compact staging cap'):
                    restore(stream,dict(size=archive.stat().st_size,generation='1'),result['archive'],root/'return/inventory.json',root/'refused','mode',reserve=0,cap=1)

    def test_phase_fresh_credit_clock_retention_source_and_device_gates(self):
        from e033_phase import validate_config,DiskClock,RETENTION
        now=1793740000.;fields=['root','repo','source_commit','operations_source','vm_start_epoch','review_deadline_epoch',
            'provider_deadline_epoch','setup_deadline_epoch','service_name','user','archive_prefix','plan',
            'python','workflow_python','base','reference','wheel','pysam_wheel','gcloud','samtools','financial',
            'initial_filesystem_used_bytes','initial_filesystem_device','source_filesystem','task_filesystem','limits']
        c={k:'' for k in fields};c.update(source_commit='a'*40,operations_source='a'*40,vm_start_epoch=now-1,
            review_deadline_epoch=now-1+36*3600,provider_deadline_epoch=now-1+36.25*3600,
            limits=dict(seconds=36*3600,provider_STOP_seconds=36.25*3600,ceiling_USD=20,threads=4,RSS_bytes=26_000_000_000,reserve_bytes=25*1024**3,extra_bytes=60*1024**3),
            financial=dict(real_money_authorized=False,coverage_status='PASS_FOR_SPECIFIED_ORDINARY_FIRST_PARTY_PRODUCTS_ONLY',
                ceiling_USD=20,credit_checked_epoch=now,checked_epoch=now,estimated_complete_gross_USD=15,
                storage_valid_until_epoch=RETENTION,credit_valid_until_epoch=RETENTION+3600))
        self.assertTrue(validate_config(c,now))
        for field,value in [('operations_source','b'*40),('provider_deadline_epoch',RETENTION+1)]:
            bad=dict(c);bad[field]=value
            with self.assertRaisesRegex(ValueError,'contract'):validate_config(bad,now)
        bad=dict(c,financial=dict(c['financial'],credit_checked_epoch=now-7201))
        with self.assertRaisesRegex(ValueError,'contract'):validate_config(bad,now)
        with tempfile.TemporaryDirectory() as folder:
            c.update(task_filesystem=folder,initial_filesystem_device=os.stat(folder).st_dev+1)
            with self.assertRaisesRegex(ValueError,'another filesystem'):DiskClock(c).start()

    def test_unknown_truth_native_release_and_engineering_size_not_silently_admitted(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);p=root/'plan.json';write(p,dict(kind='wrong',truth='forbidden'))
            with self.assertRaisesRegex(ValueError,'Unknown'):read_plan(p,True)


if __name__=='__main__':unittest.main()
