"""Diagnostic semantics on independent hand-counted retained-output fixtures."""
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).absolute().parents[1]/'scripts'))
from e009_controls_review import diagnostics,check_geometry


class DiagnosticContracts(unittest.TestCase):
    def test_exact_geometry_ties_use_opaque_ID_and_refuse_wrong_neighbors(self):
        import numpy as np
        ids=['b','a','c','f','e','d'];x=np.array([[1.,1.]]*3+[[-1.,-1.]]*3)
        # All non-self candidates are needed; same sign precedes opposite sign,
        # and ID order resolves identical cosine scores within each sign.
        neighbors=[sorted([n for n in ids[:3]if n!=q])+sorted(ids[3:])for q in ids[:3]]
        neighbors += [sorted([n for n in ids[3:]if n!=q])+sorted(ids[:3])for q in ids[3:]]
        p=dict(neighbors=neighbors,valid=[True]*6,transform=dict(mean=[0.,0.],std=[1.,1.]))
        a=dict(features=x,evidence=np.ones(6,dtype=bool),ids=np.array(ids))
        self.assertEqual(check_geometry(a,p)['verified_queries'],6)
        p['neighbors'][0]=p['neighbors'][0][::-1]
        with self.assertRaises(ValueError):check_geometry(a,p)

    def test_unknown_neighbors_and_non_target_assigned_DNA_remain_visible(self):
        ids=['a','b','c','d','e','f'];labels=['A','A','V',None,'A','A']
        contigs={q:dict(length=100000,AMBER_label=g,confirmed_query_bp={g:100000}if g else {},
                       source_intervals={},ambiguous_query_bp=0,nn_quarantined_query_bp=100000 if g is None else 0,
                       unsupported_query_bp=0)for q,g in zip(ids,labels)}
        truth=dict(ordered_contig_ids=ids,contigs=contigs,reference_axis={'r':dict(genome='A',length=400000)})
        rows=[dict(contig_id=q,length='100000',bin_id='x'if q in 'abcd'else'',status='assigned'if q in 'abcd'else'excluded',reason='')for q in ids]
        # Two A queries have three same-genome, one viral and one unknown neighbor.
        # Viral query has no same-genome neighbor. e/f are excluded with no neighbors.
        partition=dict(ids=ids,neighbors=[[n for n in ids if n!=q]if q in 'abcd'else[]for q in ids])
        p=dict(genomes={'A':dict(lineage_class='bacterial'),'V':dict(lineage_class='viral')})
        r=diagnostics(truth,rows,partition,p,dict(genome_lengths={'A':400000},targets=['A']))
        self.assertAlmostEqual(r['geometry']['nn_purity'],.4)
        self.assertEqual(r['geometry']['attributable_eligible_queries'],3)
        self.assertEqual(r['origin_by_status']['assigned']['all_bp'],400000)
        self.assertEqual(r['origin_by_status']['assigned']['viral_confirmed_bp'],100000)
        self.assertEqual(r['origin_by_status']['assigned']['nn_quarantined_query_bp'],100000)
        self.assertEqual(r['recovery_summary']['macro_R95'],0)
        self.assertAlmostEqual(r['restricted_B3']['precision'],1/3)
        self.assertAlmostEqual(r['restricted_B3']['recall'],.4)
