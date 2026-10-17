"""Actual tiny streaming acquisition checks, without scientific or cloud work."""
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

spec=importlib.util.spec_from_file_location('e014_acquire',Path(__file__).parents[1]/'scripts/e014_acquire.py')
acq=importlib.util.module_from_spec(spec);spec.loader.exec_module(acq)


class AcquisitionContracts(unittest.TestCase):
    def test_real_stream_readback_verified_reuse_and_corruption_refusal(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);source=p/'a.fa';source.write_bytes(b'>opaque\nACGT\n')
            plan=dict(base_url=p.as_uri()+'/',files=[dict(path='a.fa',bytes=source.stat().st_size,
                      md5=hashlib.md5(source.read_bytes()).hexdigest())])
            r=acq.acquire(p/'out',plan);self.assertEqual(r['status'],'SUCCESS')
            self.assertEqual(r['files'][0]['hashes']['sha256'],hashlib.sha256(source.read_bytes()).hexdigest())
            self.assertEqual(acq.acquire(p/'out',plan)['files'],r['files'])
            (p/'out/oral/a.fa').write_bytes(b'corrupt')
            with self.assertRaisesRegex(ValueError,'bytes differ'):acq.acquire(p/'out',plan)

    def test_wrong_publisher_checksum_and_expired_clock_are_explicit(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);(p/'a').write_bytes(b'actual')
            plan=dict(base_url=p.as_uri()+'/',files=[dict(path='a',bytes=6,md5='0'*32)])
            with self.assertRaisesRegex(ValueError,'checksum'):acq.acquire(p/'out',plan)
            self.assertTrue((p/'out/oral/a.partial').exists())
            (p/'out/acquisition-clock.json').write_text(json.dumps(dict(started_epoch=0,seconds=1)))
            with self.assertRaisesRegex(TimeoutError,'clock exhausted'):acq.acquire(p/'out',plan)
