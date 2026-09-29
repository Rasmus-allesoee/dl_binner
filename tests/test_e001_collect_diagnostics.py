"""Exercise actual hash verification and tar I/O on fresh/reused source layouts."""
import hashlib
import json
from pathlib import Path
import sys
import tarfile
import tempfile
import unittest
import numpy as np

REPO=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(REPO/'scripts'))
import e001_collect_diagnostics as collect


class CollectionTests(unittest.TestCase):
    def test_real_binary_io_repeated_collection_and_tamper(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); old=root/'retained-C0'; new=root/'resumed-CT'
            old.mkdir(); new.mkdir(); files=[]
            for tag,path in [('C0',old),('CT',new)]:
                np.save(path/'labels.npy',np.array([0,1,1],dtype=np.int32))
                p=path/'labels.npy'; files.append(dict(root=tag,path='labels.npy',member=tag+'/labels.npy',bytes=p.stat().st_size,sha256=collect.digest(p)))
            manifest=root/'manifest.json'; manifest.write_text(json.dumps(dict(roots={'C0':str(old),'CT':str(new)},files=files)))
            first,status=collect.collect(manifest,root/'out',1,4)
            second,_=collect.collect(manifest,root/'out',1,4); self.assertNotEqual(first,second)
            self.assertEqual(status['status'],'completed')
            archive=first/'e001-diagnostics.tar.gz'
            self.assertEqual(collect.digest(archive),(first/'e001-diagnostics.tar.gz.sha256').read_text().split()[0])
            with tarfile.open(archive) as tar:
                for f in files:
                    data=tar.extractfile(f['member']).read()
                    self.assertEqual(hashlib.sha256(data).hexdigest(),f['sha256'])
            np.save(new/'labels.npy',np.array([9,1,1],dtype=np.int32))
            with self.assertRaisesRegex(ValueError,'checksum mismatch'): collect.collect(manifest,root/'out',1,4)
            failed=[p for p in (root/'out').iterdir() if json.loads((p/'collection-status.json').read_text())['status']=='failed']
            self.assertEqual(len(failed),1); self.assertFalse((failed[0]/'e001-diagnostics.tar.gz.sha256').exists())
            (new/'labels.npy').unlink()
            with self.assertRaises(FileNotFoundError): collect.collect(manifest,root/'out',1,4)

    def test_unsafe_members_and_escaped_symlinks(self):
        for n in ['/absolute','../escape','a/../escape','a//b','']:
            with self.assertRaises(ValueError): collect.relative(n)
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); source=root/'source'; source.mkdir(); external=root/'outside'; external.write_text('x')
            (source/'link').symlink_to(external)
            m=root/'m.json'; m.write_text(json.dumps(dict(roots={'source':str(source)},files=[dict(root='source',path='link',member='link',bytes=1,sha256=collect.digest(external))])))
            with self.assertRaisesRegex(ValueError,'escapes'): collect.collect(m,root/'out',1,4)
