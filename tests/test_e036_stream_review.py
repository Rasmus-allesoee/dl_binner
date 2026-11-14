"""Exercise the real selective reader, alias closure and corrupt-byte refusal."""
import base64
import hashlib
import io
import json
from pathlib import Path
import subprocess
import sys
import tarfile
import tempfile
import unittest

ROOT = Path(__file__).absolute().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from e036_stream_review import restore


class StreamTests(unittest.TestCase):
    def test_complete_stream_selection_alias_and_corruption(self):
        crc = ROOT / 'artifacts/gcp-workspace/tools/google-cloud-sdk/bin/gcloud-crc32c'
        if not crc.is_file():
            self.fail('Actual SDK CRC32C executable required for retained-evidence test')
        values = {'work/E009-noGLM/student/value': b'kept',
                  'work/oral-noGLM/student-embed/embeddings.npz': b'not-staged'}
        bind = lambda b: dict(bytes=len(b), sha256=hashlib.sha256(b).hexdigest())
        alias = 'work/E009-noGLM/student/alias'
        inv = dict(members={n: bind(b) for n, b in values.items()},
                   aliases={alias: dict(bind(b'kept'), canonical=next(iter(values)))},
                   all_work_members={n.removeprefix('work/'): bind(b)
                                     for n, b in values.items()},
                   omitted_retained_on_disk={})
        inv['all_work_members'][alias.removeprefix('work/')] = bind(b'kept')
        inventory = (json.dumps(inv) + '\n').encode()
        out = io.BytesIO()
        with tarfile.open(fileobj=out, mode='w:gz') as archive:
            for n, b in [('inventory.json', inventory), *values.items()]:
                member = tarfile.TarInfo(n)
                member.size = len(b)
                archive.addfile(member, io.BytesIO(b))
        raw = out.getvalue()
        digest = int(subprocess.run([str(crc), '-'], input=raw,
                                   capture_output=True, check=True).stdout)
        metadata = dict(size=len(raw), generation='1',
                        md5_hash=base64.b64encode(hashlib.md5(raw).digest()).decode(),
                        crc32c=base64.b64encode(digest.to_bytes(4, 'big')).decode())
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            ip = root / 'inventory.json'
            ip.write_bytes(inventory)
            proof = restore(io.BytesIO(raw), metadata, bind(raw), ip,
                            root / 'pass', crc, reserve=0)
            self.assertTrue(proof['full_archive_every_member_and_alias_verified'])
            self.assertEqual(proof['physical_members'], 3)
            self.assertEqual((root / 'pass' / next(iter(values))).stat().st_ino,
                             (root / 'pass' / alias).stat().st_ino)
            self.assertFalse((root / 'pass' / list(values)[1]).exists())
            self.assertFalse((root / 'pass/work/restore-admission.json').exists())
            with self.assertRaisesRegex(ValueError, 'SHA256'):
                restore(io.BytesIO(raw), metadata, dict(bind(raw), sha256='0' * 64),
                        ip, root / 'bad-sha', crc, reserve=0)
            with self.assertRaisesRegex(ValueError, 'CRC32C'):
                restore(io.BytesIO(raw), dict(metadata, crc32c='AAAAAA=='), bind(raw),
                        ip, root / 'bad-crc', crc, reserve=0)
            with self.assertRaisesRegex(ValueError, 'reserve'):
                restore(io.BytesIO(raw), metadata, bind(raw), ip,
                        root / 'bad-space', crc, reserve=10**20)


if __name__ == '__main__':
    unittest.main()
