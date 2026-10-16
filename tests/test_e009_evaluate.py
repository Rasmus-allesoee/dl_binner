"""Actual native export/truth evaluator boundary; no binner fitting or cloud calls."""
import csv
from pathlib import Path
import sys
import tempfile
import unittest
sys.path.insert(0,str(Path(__file__).absolute().parents[1]/'scripts'))
from e009_evaluate import read_partition
from e009_truth import recovery


class PartitionContracts(unittest.TestCase):
    def test_native_status_reason_and_axis_refusals(self):
        truth={'ordered_contig_ids':['a','b','c'],'contigs':{q:{'length':n}for q,n in [('a',500),('b',600),('c',300)]}}
        rows=[['a',500,'bin_0','assigned',''],['b',600,'','unassigned','isolated_graph'],['c',300,'','excluded','below_min_length']]
        with tempfile.TemporaryDirectory()as tmp:
            p=Path(tmp)/'assignments.tsv'
            def put(rr,header=None):
                with p.open('w')as f:
                    w=csv.writer(f,delimiter='\t');w.writerow(header or ['contig_id','length','bin_id','status','reason']);w.writerows(rr)
            put(rows);self.assertEqual(read_partition(p,truth)[1],{'a':'bin_0','b':None,'c':None})
            bad=[rows[::-1],rows[:-1],rows+[rows[0]], [['a',501,'bin_0','assigned','']]+rows[1:],
                 [rows[0]+['extra']]+rows[1:], [rows[0][:-1]]+rows[1:],
                 [['a',500,'','assigned','']]+rows[1:], [['a',500,'bin_0','assigned','unexpected']]+rows[1:],
                 rows[:1]+[['b',600,'','unassigned','']]+rows[2:]]
            for rr in bad:
                put(rr)
                with self.assertRaises(ValueError):read_partition(p,truth)
            put(rows,['contig_id','length','bin_id','status','exclusion_reason'])
            with self.assertRaises(ValueError):read_partition(p,truth)

    def test_recovery_counts_unknown_nontarget_noise_and_duplicate_loci(self):
        def item(bp,confirmed,loci):return dict(length=bp,confirmed_query_bp=confirmed,source_intervals=loci)
        contigs={'a':item(200000,{'A':200000},{'r':[[0,200000]]}),
                 'dup':item(200000,{'A':200000},{'r':[[0,200000]]}),
                 'noise':item(100000,{'A':100000},{'r':[[200000,300000]]}),
                 'other':item(100000,{'V':100000},{'v':[[0,100000]]}),
                 'unknown':item(10000,{}, {})}
        refs={'r':dict(genome='A',length=400000),'v':dict(genome='V',length=100000)}
        assigned=dict(a='b',dup='b',noise=None,other='b',unknown='b')
        r=recovery(contigs,assigned,refs,{'A':400000},['A'])[0]
        self.assertEqual(r['whole_reference_R95'],0) # all other/unknown bin DNA stays in denominator
        assigned.update(other=None,unknown=None)
        r=recovery(contigs,assigned,refs,{'A':400000},['A'])[0]
        self.assertEqual(r['recovered_bp'],200000) # duplicate query cannot duplicate source recovery
        self.assertEqual(r['whole_reference_R95'],.5)
        self.assertAlmostEqual(r['assembly_conditional_R95'],2/3)
        with self.assertRaises(ValueError):recovery(contigs,assigned,refs,{'A':300000},['A'])
