"""Independent hand-computed full-denominator/replicon/purity evaluator contracts.

No community partitions, scores or threshold changes. These tiny counterexamples
make the restrictions of the unchanged recovery diagnostic explicit.
"""
from pathlib import Path
import sys
import unittest

sys.path.insert(0,str(Path(__file__).absolute().parents[1]/'scripts'))
from e009_truth import recovery


class EvaluationFoundation(unittest.TestCase):
    def test_full_reference_and_duplicate_safe_replicon_union(self):
        refs={'chrom':dict(genome='g',length=100),'plasmid':dict(genome='g',length=20),'zero':dict(genome='absent',length=50)}
        c={'a':dict(length=60,confirmed_query_bp={'g':60},source_intervals={'chrom':[[0,60]]}),
           'duplicate':dict(length=60,confirmed_query_bp={'g':60},source_intervals={'chrom':[[0,60]]}),
           'p':dict(length=20,confirmed_query_bp={'g':20},source_intervals={'plasmid':[[0,20]]})}
        r=recovery(c,{q:'bin'for q in c},refs,{'g':120,'absent':50},['g','absent'],min_bin=1)
        by={x['genome']:x for x in r};self.assertEqual(by['g']['recovered_bp'],80)
        self.assertEqual(by['g']['whole_reference_R95'],80/120);self.assertEqual(by['g']['assembly_conditional_R95'],1.)
        self.assertEqual(by['absent']['whole_reference_R95'],0.)

    def test_unresolved_DNA_is_not_dropped_from_purity(self):
        refs={'r':dict(genome='g',length=100)}
        c={'known':dict(length=94,confirmed_query_bp={'g':94},source_intervals={'r':[[0,94]]}),
           'unknown':dict(length=6,confirmed_query_bp={},source_intervals={})}
        r=recovery(c,{'known':'bin','unknown':'bin'},refs,{'g':100},['g'],min_bin=1)[0]
        self.assertEqual(r['recovered_bp'],0);self.assertEqual(r['assembly_confirmed_bp'],94)
        # This says conservative all-bin support <95%, not measured foreign DNA.
        r=recovery(c,{'known':'bin','unknown':None},refs,{'g':100},['g'],min_bin=1)[0]
        self.assertEqual(r['recovered_bp'],94)

    def test_small_singletons_and_missing_axes_cannot_silently_become_MAGs(self):
        refs={'r':dict(genome='g',length=300000)}
        c={'a':dict(length=150000,confirmed_query_bp={'g':150000},source_intervals={'r':[[0,150000]]})}
        r=recovery(c,{'a':'bin'},refs,{'g':300000},['g'])[0]
        self.assertEqual(r['recovered_bp'],0);self.assertEqual(r['assembly_confirmed_bp'],150000)
        with self.assertRaisesRegex(ValueError,'axis'):recovery(c,{},refs,{'g':300000},['g'])
        with self.assertRaisesRegex(ValueError,'denominator'):recovery(c,{'a':'bin'},refs,{'g':150000},['g'])


if __name__=='__main__':unittest.main()
