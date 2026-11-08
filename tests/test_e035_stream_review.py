"""Actual tiny stream/CRC/member/alias contracts, separate from product tests."""
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

ROOT=Path(__file__).absolute().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from e035_stream_review import verify_stream
CRC=ROOT/'artifacts/gcp-workspace/tools/google-cloud-sdk/bin/gcloud-crc32c'


@unittest.skipUnless(CRC.is_file(),'Research contract requires the retained SDK CRC binary')
class StreamTests(unittest.TestCase):
    def fixture(self,alias='work/a'):
        """Build a real two-name exact-byte fixture with independently bound CRC."""
        data=b'hand-computed payload';b=dict(bytes=len(data),sha256=hashlib.sha256(data).hexdigest())
        inv=dict(members={'work/a':b},aliases={'work/b':dict(b,canonical=alias)},
                 all_work_members={'a':b,'b':b},omitted_retained_on_disk={})
        buf=io.BytesIO()
        with tarfile.open(fileobj=buf,mode='w:gz')as a:
            for n,v in [('inventory.json',json.dumps(inv).encode()),('work/a',data)]:
                m=tarfile.TarInfo(n);m.size=len(v);a.addfile(m,io.BytesIO(v))
        raw=buf.getvalue();crc=int(subprocess.run([str(CRC),'-'],input=raw,capture_output=True,check=True,timeout=10).stdout)
        meta=dict(size=len(raw),generation='fixture',crc32c=base64.b64encode(crc.to_bytes(4,'big')).decode(),md5Hash=base64.b64encode(hashlib.md5(raw).digest()).decode())
        return raw,inv,meta,dict(bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest())

    def test_known_crc_and_actual_alias_bytes(self):
        self.assertEqual(int(subprocess.run([str(CRC),'-'],input=b'123456789',capture_output=True,check=True,timeout=10).stdout),0xe3069283)
        raw,inv,meta,expected=self.fixture()
        with tempfile.TemporaryDirectory()as td:
            out=Path(td)/'out';proof=verify_stream(io.BytesIO(raw),meta,expected,inv,out,CRC,reserve=0)
            self.assertEqual(proof['status'],'PASS')
            self.assertEqual((out/'work/a').read_bytes(),(out/'work/b').read_bytes())
            self.assertEqual((out/'work/a').stat().st_ino,(out/'work/b').stat().st_ino)

    def test_corrupt_whole_hash_and_unsafe_alias_refused(self):
        with tempfile.TemporaryDirectory()as td:
            raw,inv,meta,expected=self.fixture()
            with self.assertRaisesRegex(ValueError,'SHA256'):
                verify_stream(io.BytesIO(raw),meta,dict(expected,sha256='0'*64),inv,Path(td)/'bad-hash',CRC,reserve=0)
            raw,inv,meta,expected=self.fixture('../outside')
            with self.assertRaisesRegex(ValueError,'alias'):
                verify_stream(io.BytesIO(raw),meta,expected,inv,Path(td)/'bad-alias',CRC,reserve=0)
            self.assertFalse((Path(td)/'outside').exists())


if __name__=='__main__':unittest.main()
