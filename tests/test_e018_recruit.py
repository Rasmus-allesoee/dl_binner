"""Decision-changing E018 cache contracts, including exact stored boundaries."""
import copy
from pathlib import Path
import sys
import unittest
import numpy as np
sys.path.insert(0,str(Path(__file__).absolute().parents[1]/'scripts'))
from e018_recruit import choose,partition_from_selection


class CachedDecision(unittest.TestCase):
    def fixture(self):
        return dict(offered_bins=np.array([[0,1,-1],[0,1,-1],[0,1,-1],[0,1,-1],[0,1,-1]],np.int32),
            normalized_scores=np.array([[.1,.6,-1],[.5,.6,-1],[1,2,-1],[.1,.2,-1],[.1,.2,-1]],np.float32),
            vote_fractions=np.array([[.1,.9,0],[.8,.2,0],[2/3,1/3,0],[.6,.4,0],[.9,.1,0]],np.float32),
            distinct_support=np.array([[1,3,0],[3,1,0],[2,1,0],[3,3,0],[1,3,0]],np.int32),
            accepted_bins=np.array([-1,-1,0,-1,-1],np.int32))

    def test_vote_can_choose_other_profile_winner_or_pass_old_margin(self):
        selected,columns=choose(self.fixture())
        self.assertEqual(selected.tolist(),[1,0,0,-1,-1])
        self.assertEqual(columns.tolist(),[1,0,0,-1,-1])

    def test_stored_thresholds_are_not_relaxed(self):
        c=self.fixture();c['vote_fractions'][2,0]=np.nextafter(np.float32(2/3),np.float32(0));c['accepted_bins'][2]=-1
        self.assertEqual(choose(c)[0][2],-1)
        c=self.fixture();c['normalized_scores'][2,0]=np.nextafter(np.float32(1),np.float32(2));c['accepted_bins'][2]=-1
        self.assertEqual(choose(c)[0][2],-1)

    def test_missing_corrupt_ambiguous_and_old_subset_refusals(self):
        for key,value,error in [('normalized_scores',np.nan,'Nonfinite'),('vote_fractions',-.1,'Nonfinite')]:
            c=self.fixture();c[key][0,0]=value
            with self.subTest(key=key),self.assertRaisesRegex(ValueError,error):choose(c)
        c=self.fixture();c['vote_fractions'][0,:2]=.8
        with self.assertRaisesRegex(ValueError,'vote normalization'):choose(c)
        c=self.fixture();c['accepted_bins'][0]=0
        with self.assertRaisesRegex(ValueError,'Previously accepted'):choose(c)
        c=self.fixture();c['distinct_support']=c['distinct_support'][:-1]
        with self.assertRaisesRegex(ValueError,'axes differ'):choose(c)
        c=self.fixture();c.pop('offered_bins')
        with self.assertRaises(KeyError):choose(c)

    def test_inputs_are_not_mutated(self):
        c=self.fixture();before=copy.deepcopy(c);choose(c)
        self.assertTrue(all(np.array_equal(c[k],before[k])for k in c))

    def test_no_core_offers_or_no_queries_remain_fully_accounted(self):
        for n in [0,3]:
            c=dict(offered_bins=np.empty((n,0),np.int32),normalized_scores=np.empty((n,0),np.float32),
                vote_fractions=np.empty((n,0),np.float32),distinct_support=np.empty((n,0),np.int32),
                accepted_bins=np.full(n,-1,np.int32))
            labels,cols=choose(c)
            self.assertEqual(labels.tolist(),[-1]*n);self.assertEqual(cols.tolist(),[-1]*n)

    def test_opaque_ID_canonical_label_permutation_preserves_core_identity(self):
        data=dict(ids=np.array(['z1','z2','x1','x2','a_query','m_query','excluded']),
            lengths=np.array([3000,3000,3000,3000,500,500,200]),eligible=np.array([True]*6+[False]))
        core=dict(clusters=2,assignment=[1,1,0,0,-1,-1,-1],reason=['']*4+['unsupported']*3)
        old=dict(config=dict(min_bin_contigs=2,min_bin_bp=2000),neighbors=[],
            parent_features_sha256='f',embedding_sha256='v',graph_sha256='g',information_config={},neighbor_storage={})
        parent,mapping=partition_from_selection(data,core,old,dict(query_indices=np.array([4,5])),np.array([1,0]))
        self.assertEqual(mapping,{1:0,0:1})
        self.assertEqual(parent['assignment'],[0,0,1,1,0,1,-1])
        self.assertEqual(parent['valid'],[True]*6+[False])


if __name__=='__main__':unittest.main()
