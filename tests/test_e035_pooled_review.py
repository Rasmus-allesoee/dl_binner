"""Hand-computed locus/terminal-accounting contracts, with no retained science."""
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).absolute().parents[1]/'scripts'))
from e035_pooled_review import endpoint,counter_contract


class ReviewTests(unittest.TestCase):
    def test_complete_endpoint_and_boundary(self):
        blocks={'q':[dict(q0=0,q1=20,genome='A')]}
        self.assertEqual(endpoint('q',5,15,blocks,{}),('A',{'A':10},{}))
        self.assertEqual(endpoint('q',15,25,blocks,{}),(None,{'A':5},{'unsupported':5}))

    def test_competitor_and_ambiguity_override(self):
        blocks={'q':[dict(q0=0,q1=20,genome='A'),dict(q0=10,q1=20,genome='B')]}
        self.assertEqual(endpoint('q',5,15,blocks,{}),(None,{'A':5},{'ambiguous':5}))
        self.assertEqual(endpoint('q',10,15,blocks,{'q':[[10,15]]}),(None,{}, {'quarantined':5}))

    def test_actual_e035_histogram_schema_and_terminal_refusal(self):
        c=dict(templates=5,qualified_both_mates=3,low_or_unknown_template_MAPQ=2,
               cross_contig_qualified_templates=1,qualified_read_length_150=6)
        counter_contract(c,[0,2])
        with self.assertRaises(AssertionError):counter_contract(dict(c,templates=6),[0,2])
        with self.assertRaises(AssertionError):counter_contract(c,[0,3])


if __name__=='__main__':unittest.main()
