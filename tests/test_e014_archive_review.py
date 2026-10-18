"""Real tar stream/checksum/alias and selective extraction refusal contracts."""
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0,str(Path(__file__).absolute().parents[1]/'scripts'))
from e014_collect import pack,binding
from e014_archive_review import verify_archive,extract_selected
import test_e014_collect as collector_tests


class ArchiveContracts(unittest.TestCase):
    def test_actual_stream_and_selective_bytes_and_corruption_refusal(self):
        with tempfile.TemporaryDirectory()as t:
            root=Path(t);work,inventory,phase,proofs=collector_tests.CollectionContracts().fixture(root)
            # Native graph proofs have deterministic expected unit names.
            for i,u in enumerate(['E009-dev5','oral-dev4','oral-dev5']):(proofs/('graph-'+str(i)+'.json')).rename(proofs/('graph-'+u+'.json'))
            r=pack(work,inventory,phase,proofs,root/'return');archive=root/'return/e014-review.tar.gz';collection=root/'return/collection.json'
            verified=root/'verified';v=verify_archive(archive,collection,verified)
            self.assertTrue(v['every_archive_member_verified']);self.assertFalse((verified/'work/result.json').exists())
            out=root/'copies';extract_selected(archive,verified,out,lambda n,s:n=='work/result.json',budget_root=root)
            self.assertEqual(binding(out/'work/result.json'),binding(work/'result.json'))
            with self.assertRaisesRegex(ValueError,'storage cap'):extract_selected(archive,verified,root/'too-small',lambda n,s:n=='work/result.json',ceiling=1,budget_root=root)
            archive.write_bytes(archive.read_bytes()+b'corrupt')
            with self.assertRaisesRegex(ValueError,'bytes/cap'):verify_archive(archive,collection,root/'bad')


if __name__=='__main__':unittest.main()
