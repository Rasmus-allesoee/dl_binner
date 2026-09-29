"""Check closure-specific marker arithmetic and frozen retained-data contracts."""
from collections import Counter
from pathlib import Path
import sys
import tempfile
import unittest
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import e001_close_diagnostics as close


class ClosureTests(unittest.TestCase):
    def test_grouped_markers_multiplicity_and_strict_threshold(self):
        groups=[{'a','b'},{'c'}]
        individual,complete,contaminated=close.marker_quality(Counter(a=2,c=1),groups)
        self.assertEqual((individual,complete,contaminated),(100,75,25))
        hits={'bac':{'x':Counter(a=1)},'ar':{}}
        result=close.marker_counts(['x'],np.array([0]),hits,{'bac':[{'a','b'}],'ar':[{'z'}]})
        self.assertEqual(result['sum'],0)  # exactly 50 is not >50
        hits['bac']['x']['b']=1
        result=close.marker_counts(['x'],np.array([0]),hits,{'bac':[{'a','b'}],'ar':[{'z'}]})
        self.assertEqual(result['sum'],6)
        self.assertEqual(result['sum_cont5'],3)

    def test_domain_choice_uses_individual_score_before_grouped_score(self):
        hits={'bac':{'x':Counter(a=2)},'ar':{'x':Counter(z=1)}}
        result=close.marker_counts(['x'],np.array([0]),hits,{'bac':[{'a'}],'ar':[{'z'}]})
        self.assertEqual(result['sum'],0)  # bac selected despite cleaner archaea

    def test_marker_gene_suffix_and_adjacent_gene_contract(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'markers.tsv'
            p.write_text('bin\tmarker\tgene\n0\tM1\tcontig_a_1&&contig_a_2\n0\tM1\tcontig_a_3\n')
            self.assertEqual(close.marker_hits(p,{'contig_a'}),{'contig_a':Counter(M1=2)})
            with self.assertRaises(ValueError):close.marker_hits(p,{'other'})

    def test_equal_blocks_preserve_zero_and_balance_scale(self):
        x=close.unit([[0,0],[3,4]])
        np.testing.assert_array_equal(x[0],[0,0])
        np.testing.assert_allclose(x[1],[.6,.8])
        np.testing.assert_allclose(x,close.unit([[0,0],[30,40]]))

    def test_recovery_requires_primary_qualifying_bin(self):
        pop={'unique_origins':{'a':'g','b':'g','c':'h'}}
        result={'per_genome':{'g':{'bin':'1'},'h':{'bin':None}}}
        self.assertEqual(close.recovered(pop,{'a':'1','b':'2'},result),{'a'})

    def test_triage_keeps_fixed_denominator_and_lost_intersection(self):
        probes={name:{'a':{'purity':.6},'b':{'purity':None}} for name in ['composition','coverage','equal_blocks']}
        probes['embedding']={'a':{'purity':.5},'b':{'purity':.2}}
        result=close.representation_triage(probes,['a','b'],{'a':10,'b':90},{'b'})
        self.assertAlmostEqual(result['equal_blocks']['short_base_fraction'],.1)
        self.assertEqual(result['equal_blocks']['lost_short_overlap_base_fraction_of_lost'],0)

    def test_retained_scale_controls(self):
        p=ROOT/'artifacts/e001-diagnostics-reviewed'
        if not p.exists():self.skipTest('Optional owner collection absent')
        result=close.scale_controls(p)
        self.assertEqual(result['comebin_raw_scaling'],'exact')
        self.assertLess(max(result['comebin_normalized_max_abs_difference_per_view']),3e-6)


if __name__=='__main__':unittest.main()
