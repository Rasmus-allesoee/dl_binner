"""Source availability cannot double-count repeated/overlapping loci."""
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).absolute().parents[1]/'scripts'))
from e014_origin_union import union_length


class UnionContracts(unittest.TestCase):
    def test_overlap_duplicate_disjoint_and_empty(self):
        self.assertEqual(union_length([(1,10),(5,12),(1,10),(20,20)]),13)
        self.assertEqual(union_length([(4,5),(1,3)]),5)
        self.assertEqual(union_length([]),0)
        for spans in [[(0,10)],[(4,3)]]:
            with self.assertRaisesRegex(ValueError,'coordinates'):union_length(spans)


if __name__=='__main__':unittest.main()
