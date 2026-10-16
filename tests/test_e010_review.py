"""Hand-counted retained-reader contracts; no fit, native index or cloud work."""
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).absolute().parents[1]/'scripts'))
from e010_review import unit_neighbors,refinement_membership,sparse_graph_contract


class RetainedCandidateReviewTests(unittest.TestCase):
    def fixture(self):
        """Seven known unit points, opaque IDs and one retained invalid DNA row."""
        import numpy as np
        ids=['c','h','a','f','x','z','d','short']
        angles=np.arange(7)*.7
        x=np.vstack([np.stack([np.cos(angles),np.sin(angles)],1),np.zeros((1,2))])
        valid=np.array([True]*7+[False]);matrix=np.full((8,6),-1,dtype=np.int64);neighbors=[[]for _ in ids]
        for i in range(7):
            choices=sorted([j for j in range(7)if j!=i],key=lambda j:ids[j])
            choices=sorted(choices,key=lambda j:-float(x[i]@x[j]))
            matrix[i]=choices;neighbors[i]=[ids[j]for j in choices[:5]]
        return x,ids,valid,neighbors,matrix

    def test_unit_geometry_and_all_DNA_axis_without_population_zscore(self):
        x,ids,valid,neighbors,matrix=self.fixture()
        out=unit_neighbors(x,ids,valid,neighbors,matrix,6)
        self.assertEqual(out['native_rows_checked'],7)
        self.assertEqual(out['native_neighbor_entries'],42)
        self.assertEqual(out['mean_recall_k'],1)
        self.assertEqual(out['mean_recall_5'],1)
        self.assertEqual(neighbors[-1],[])
        z=x.copy();z[:7]=(z[:7]-z[:7].mean(0))/z[:7].std(0)
        with self.assertRaisesRegex(ValueError,'unit sphere'):
            unit_neighbors(z,ids,valid,neighbors,matrix,6)

    def test_wrong_self_duplicate_unknown_and_axis_neighbors_refused(self):
        for fault in ['self','duplicate','unknown','top_five','nonfinite']:
            with self.subTest(fault=fault):
                x,ids,valid,neighbors,matrix=self.fixture()
                if fault=='self':matrix[0,0]=0
                elif fault=='duplicate':matrix[0,1]=matrix[0,0]
                elif fault=='unknown':matrix[0,0]=7
                elif fault=='top_five':neighbors[0]=neighbors[0][::-1]
                else:x[0,0]=float('nan')
                with self.assertRaises(ValueError):unit_neighbors(x,ids,valid,neighbors,matrix,6)

    def test_refinement_splits_or_unassigns_but_cannot_merge_or_rescue_noise(self):
        pre=dict(ids=['a','b','c','d','short'],valid=[True]*4+[False],neighbors=[[]]*5,assignment=[0,0,1,-1,-1])
        post=dict(pre,assignment=[0,1,2,-1,-1])
        self.assertTrue(refinement_membership(pre,post)['no_merge_or_new_assignment'])
        post['assignment']=[0,-1,1,-1,-1]
        self.assertEqual(refinement_membership(pre,post)['counts']['assigned_to_noise'],1)
        for labels in [[0,0,0,-1,-1],[0,0,1,2,-1],[0,0,1,-1,2]]:
            with self.assertRaises(ValueError):refinement_membership(pre,dict(post,assignment=labels))
        for labels in [[0,0,1], [0,0,1,-1,-2], [0,0,1,-1,False]]:
            with self.assertRaisesRegex(ValueError,'Malformed/truncated'):
                refinement_membership(pre,dict(post,assignment=labels))

    def test_sparse_edges_follow_ID_order_even_when_integer_indices_descend(self):
        import numpy as np
        ids=['z','a','m','short'];valid=[True,True,True,False]
        # a->z and a->m map to descending and ascending FASTA indices respectively.
        edges=np.array([[1,0],[1,2],[2,0]],dtype=np.int64);weights=np.array([.5,.8,1.])
        self.assertEqual(sparse_graph_contract(edges,weights,ids,valid)['edges'],3)
        for broken in [np.array([[0,1]]),np.array([[1,1]]),np.array([[1,3]]),np.array([[1,0],[1,0]])]:
            with self.assertRaises(ValueError):sparse_graph_contract(broken,np.ones(len(broken)),ids,valid)
        for value in [0.,-1.,float('nan'),1.01]:
            with self.assertRaises(ValueError):sparse_graph_contract(edges,np.full(3,value),ids,valid)

    def test_bin_source_diagnostic_keeps_unknown_DNA_and_duplicate_safe_loci(self):
        import importlib.util
        source=Path(__file__).parents[1]/'experiments/E010-coherent-prototype/review_diagnostics.py'
        spec=importlib.util.spec_from_file_location('e010_bin_diagnostic',source)
        module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        rows=[dict(contig_id=q,bin_id='mixed')for q in ['a','duplicate','virus','unknown']]
        truth=dict(reference_axis={'r':dict(genome='A'),'v':dict(genome='V')},contigs={})
        for q,g,ref in [('a','A','r'),('duplicate','A','r'),('virus','V','v'),('unknown',None,None)]:
            truth['contigs'][q]=dict(length=100000,confirmed_query_bp={g:100000}if g else{},
                source_intervals={ref:[[0,100000]]}if ref else{})
        population=dict(genomes={'A':dict(lineage_class='bacterial'),'V':dict(lineage_class='viral')})
        result=module.bin_sources(rows,truth,population,['A'])
        self.assertEqual(result['bins'][0]['bp'],400000)
        self.assertEqual(result['bins'][0]['confirmed_purity'],.5)
        self.assertEqual(result['bins'][0]['unconfirmed_bp'],100000)
        self.assertEqual(result['targets'][0]['best_source_union_bp'],100000)
        self.assertEqual(result['large_bins_below_95pct_purity'],1)


if __name__=='__main__':unittest.main()
