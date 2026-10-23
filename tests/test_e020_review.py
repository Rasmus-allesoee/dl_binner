"""Compact-format adaptation keeps actual legacy membership refusal semantics."""
import copy
from pathlib import Path
import sys
import unittest

sys.path.insert(0,str(Path(__file__).absolute().parents[1]/'scripts'))
from e020_review import legacy_membership_views
from e010_review import refinement_membership


class CompactReview(unittest.TestCase):
    def setUp(self):
        self.part=dict(ids=['opaque_c','opaque_a','opaque_b'],valid=[True,True,False],
            assignment=[0,0,-1],neighbors=[],graph_sha256='g'*64,embedding_sha256='v'*64,
            parent_features_sha256='f'*64,
            neighbor_storage=dict(mode='complete_sparse_numeric_cache',core='graph.npz:candidates',
                recruitment='recruitment.npz:candidate_indices',
                query_axes='core_indices / query_indices; original full FASTA row indices'))
        self.nn=[['opaque_a'],['opaque_c'],[]]
        self.old=copy.deepcopy(self.part)
        for key in ['neighbor_storage','graph_sha256','embedding_sha256']:self.old.pop(key)
        self.old['pre_partition_semantics']='one proposal per pre-bin; no merging; uncertainty may remain unassigned'
        self.post=copy.deepcopy(self.part);self.post.pop('neighbor_storage')

    def test_real_legacy_membership_adapter_keeps_original_bytes_in_memory(self):
        parent=copy.deepcopy(self.part);child=copy.deepcopy(self.post);child['assignment']=[0,1,-1]
        with self.assertRaisesRegex(ValueError,'Malformed/truncated'):
            refinement_membership(parent,child)
        a,old,b=legacy_membership_views([parent,self.old,child],self.nn)
        self.assertTrue(refinement_membership(a,old)['no_merge_or_new_assignment'])
        self.assertTrue(refinement_membership(a,b)['no_merge_or_new_assignment'])
        self.assertEqual(parent,self.part);self.assertEqual(child['neighbors'],[])
        self.assertIs(a['neighbors'],self.nn);self.assertIs(b['neighbors'],self.nn)

    def test_cache_identity_and_full_learned_axis_are_required(self):
        for change in [dict(neighbors=[[]]),dict(graph_sha256='changed'),
                       dict(embedding_sha256='changed'),dict(neighbor_storage={}),
                       dict(parent_features_sha256='changed')]:
            with self.subTest(change=change),self.assertRaises(ValueError):
                legacy_membership_views([self.part,self.old,self.post|change],self.nn)
        with self.assertRaises(ValueError):legacy_membership_views([self.part,self.old,self.post],self.nn[:-1])
        with self.assertRaises(ValueError):legacy_membership_views([self.part,self.old|dict(graph_sha256='invented'),self.post],self.nn)

    def test_truncation_merge_invalid_assignment_and_axis_drift_still_refused(self):
        pre=self.part|dict(assignment=[0,1,-1])
        for change in [dict(assignment=[0,0,-1]),dict(assignment=[0,1,2]),
                       dict(assignment=[0,1]),dict(ids=['changed','opaque_a','opaque_b'])]:
            with self.subTest(change=change),self.assertRaises(ValueError):
                a,old,b=legacy_membership_views([pre,self.old,self.post|change],self.nn)
                refinement_membership(a,b)


if __name__=='__main__':unittest.main()
