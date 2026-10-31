"""Exercise the exact two-intermediate-plus-final immutable publication path."""
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0,str(Path(__file__).absolute().parents[1]/'scripts'))
from e027_initialization_audit import variant_record_path
from e024_coverage import write


class Publication(unittest.TestCase):
    def test_two_variants_then_final_and_refuse_overwrite(self):
        with tempfile.TemporaryDirectory() as temp:
            output=Path(temp)/'result.json'
            for name in ['executed_partial_native','prospective_complete_global']:
                write(variant_record_path(output,name),dict(variant=name))
            write(output,dict(status='PASS'))
            self.assertEqual(len(list(Path(temp).glob('*.json'))),3)
            with self.assertRaises(FileExistsError):write(output,dict(status='replacement'))
            with self.assertRaises(ValueError):variant_record_path(output,'undeclared-grid')


if __name__=='__main__':unittest.main()
