"""Actual dependency copying excludes overlays and creates regular owned bytes."""
from pathlib import Path
import gzip
import json
import sys
import tempfile
import unittest
sys.path.insert(0,str(Path(__file__).absolute().parents[1]/'scripts'))
from e014_runtime import copy_dependencies,restore_input
from e009_common import binding
from e014_comparison import validate_plan


class RuntimeCopyContracts(unittest.TestCase):
    def test_science_plan_refuses_evaluator_fields_and_extra_arm(self):
        plan=dict(threads=4,units={n:dict(learning='dev4'if n=='oral-dev4'else'dev5')for n in ['E009-dev5','oral-dev4','oral-dev5']})
        validate_plan(plan)
        with self.assertRaisesRegex(ValueError,'scope'):validate_plan(plan|dict(target_genome_count=799))
        bad={k:dict(v)for k,v in plan['units'].items()};bad['oral-dev5']['truth']='oracle.json'
        with self.assertRaisesRegex(ValueError,'evaluator'):validate_plan(plan|dict(units=bad))

    def test_actual_lossless_transport_restore_and_changed_bytes_refusal(self):
        with tempfile.TemporaryDirectory()as t:
            root=Path(t);original=root/'original.fna';original.write_bytes(b'>Copaque\nACGTNN\n')
            compressed=root/'input.gz'
            with gzip.open(compressed,'wb')as f:f.write(original.read_bytes())
            manifest=root/'manifest.json';manifest.write_text(json.dumps(dict(compressed=binding(compressed),restored=binding(original))))
            target=root/'restored.fna';restore_input(compressed,manifest,target)
            self.assertEqual(target.read_bytes(),original.read_bytes())
            with self.assertRaisesRegex(ValueError,'Fresh input'):restore_input(compressed,manifest,target)
            compressed.write_bytes(b'corrupt')
            with self.assertRaisesRegex(ValueError,'bytes differ'):restore_input(compressed,manifest,root/'new.fna')

    def test_real_copy_owns_library_alias_bytes_and_refuses_existing_site(self):
        with tempfile.TemporaryDirectory()as t:
            root=Path(t);source=root/'source';source.mkdir();package=source/'numerical';package.mkdir()
            (package/'lib.so').write_bytes(b'real tiny library fixture');(package/'alias.so').symlink_to('lib.so')
            (package/'__init__.py').write_text('value=1\n');(package/'__pycache__').mkdir();(package/'__pycache__/old.pyc').write_bytes(b'stale')
            (source/'dl_binner').mkdir();(source/'dl_binner-0.1.dist-info').mkdir();(source/'overlay.pth').write_text('/foreign/site')
            destination=root/'owned';receipt=copy_dependencies(source,destination)
            self.assertFalse((destination/'numerical/alias.so').is_symlink())
            self.assertEqual((destination/'numerical/alias.so').read_bytes(),b'real tiny library fixture')
            self.assertFalse((destination/'overlay.pth').exists());self.assertFalse((destination/'dl_binner').exists())
            self.assertFalse((destination/'numerical/__pycache__').exists());self.assertFalse(receipt['site_links'])
            with self.assertRaisesRegex(ValueError,'Fresh empty'):copy_dependencies(source,destination)


if __name__=='__main__':unittest.main()
