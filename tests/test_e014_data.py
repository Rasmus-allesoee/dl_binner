"""Actual tiny streaming acquisition checks, without scientific or cloud work."""
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
import threading

spec=importlib.util.spec_from_file_location('e014_acquire',Path(__file__).parents[1]/'scripts/e014_acquire.py')
acq=importlib.util.module_from_spec(spec);spec.loader.exec_module(acq)


class AcquisitionContracts(unittest.TestCase):
    def test_actual_HTTP_range_recovery_keeps_prefix_and_original_clock(self):
        payload=b'known byte-bound payload'
        class Handler(BaseHTTPRequestHandler):
            def do_GET(self):
                a,b=map(int,self.headers['Range'].removeprefix('bytes=').split('-'))
                self.send_response(206);self.send_header('Content-Range',f'bytes {a}-{b}/{len(payload)}')
                self.send_header('Content-Length',str(b-a+1));self.end_headers();self.wfile.write(payload[a:b+1])
            def log_message(self,*_):pass
        server=ThreadingHTTPServer(('127.0.0.1',0),Handler);thread=threading.Thread(target=server.serve_forever);thread.start()
        try:
            with tempfile.TemporaryDirectory() as d:
                root=Path(d);(root/'oral').mkdir();(root/'oral/a.partial').write_bytes(payload[:5])
                plan=dict(base_url=f'http://127.0.0.1:{server.server_port}/',files=[dict(path='a',bytes=len(payload),md5=hashlib.md5(payload).hexdigest())])
                with self.assertRaisesRegex(ValueError,'explicit repair'):acq.acquire(root,plan)
                original=(root/'acquisition-clock.json').read_bytes()
                acq.acquire(root,plan,resume_partial=True)
                self.assertEqual((root/'oral/a').read_bytes(),payload)
                self.assertEqual((root/'acquisition-clock.json').read_bytes(),original)
        finally:server.shutdown();thread.join();server.server_close()

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

    def test_runtime_interpreter_alias_is_separate_from_scientific_output_links(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);(p/'envs').mkdir();(p/'target').write_text('x');(p/'envs/python').symlink_to(p/'target')
            acq.guard(p,dict(started_epoch=__import__('time').time(),seconds=10))
            (p/'data-link').symlink_to(p/'target')
            with self.assertRaisesRegex(ValueError,'scientific output link'):acq.guard(p,dict(started_epoch=__import__('time').time(),seconds=10))
