"""Actual split/member/alias/receiver and bounded failure-evidence contracts."""
import json
from pathlib import Path
import sys
import tempfile
import unittest
import os

sys.path.insert(0,str(Path(__file__).absolute().parents[1]/'scripts'))
import e035_collect as c


class Collection(unittest.TestCase):
    def test_actual_maximum_oral_view_file_shape_through_streaming_verifier(self):
        # Exact worst-case cache shape: all 508,763 eligible Oral parents,
        # five views, two 64-d heads, float32, plus the NPY header allowance.
        # The temporary zero fixture is sparse on disk and regenerable; native
        # work/checkpoints are never touched. The archive verifier reads every byte.
        logical=508763*5*2*64*4+128
        with tempfile.TemporaryDirectory()as folder:
            root=Path(folder);work=root/'work';work.mkdir();e=root/'e';e.mkdir()
            with (work/'maximum-view-shape.npy.fixture').open('xb')as f:f.truncate(logical)
            os.link(work/'maximum-view-shape.npy.fixture',work/'exact-alias.fixture')
            m=c.pack(work,e,root/'return');proof=c.verify(root/'return')
            self.assertEqual(len(m['slices']),1);self.assertEqual(proof['members'],2)
            print('FULL_SHAPE_RETURN_CONTRACT',json.dumps(dict(logical_regular_bytes=logical,compressed_bytes=proof['compressed_bytes'],exact_aliases=1,all_bytes_verified=True)),flush=True)

    def test_cross_stage_alias_group_complete_restore_and_repeated_verification(self):
        with tempfile.TemporaryDirectory()as folder:
            root=Path(folder);work=root/'work';work.mkdir();evidence=root/'evidence';evidence.mkdir()
            (work/'one').write_bytes(b'a'*80);(work/'two').write_bytes(b'b'*80)
            (work/'alias').write_bytes(b'a'*80);(evidence/'terminal.log').write_text('actual retained fixture terminal\n')
            m=c.pack(work,evidence,root/'return',physical_limit=100)
            self.assertEqual(len(m['slices']),2);before=c.binding(root/'return/inventory.json')
            c.verify(root/'return');self.assertEqual(c.binding(root/'return/inventory.json'),before)
            c.restore(root/'return',root/'restored')
            self.assertEqual((root/'restored/work/one').read_bytes(),b'a'*80)
            self.assertEqual((root/'restored/work/alias').stat().st_ino,(root/'restored/work/one').stat().st_ino)
            record=m['slices'][0];archive=root/'return'/record['folder']/'e033-evidence.tar.gz'
            with archive.open('r+b')as out:out.seek(-1,2);out.write(b'X')
            with self.assertRaises(ValueError):c.verify(root/'return')

    def test_oversized_member_and_scientific_symlink_are_refused_without_fallback(self):
        with tempfile.TemporaryDirectory()as folder:
            root=Path(folder);work=root/'work';work.mkdir();e=root/'e';e.mkdir();(work/'large').write_bytes(b'x'*101)
            with self.assertRaisesRegex(ValueError,'Individual'):c.pack(work,e,root/'bad',100)
            (work/'link').symlink_to(work/'large')
            with self.assertRaisesRegex(ValueError,'symlink'):c.pack(work,e,root/'bad-link',1000)

    def test_failed_classifier_stderr_retained_without_claiming_completion(self):
        with tempfile.TemporaryDirectory()as folder:
            root=Path(folder);source=root/'classifier';source.mkdir()
            (source/'taxonomy.log').write_text('native scientific worker error, not scheduler trailer\n')
            (source/'taxonomy.exit.json').write_text('{"exit_code":1}\n')
            c.compact_classification(source,root/'returned',allow_failure=True)
            m=json.loads((root/'returned/compact-stage.json').read_text());self.assertEqual(m['status'],'FAILED_INPUT_PRESERVED')
            self.assertFalse(m['native_scientific_completion']);self.assertIn('worker error',(root/'returned/taxonomy.log').read_text())


if __name__=='__main__':unittest.main()
