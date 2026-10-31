"""Tiny complete-population census contracts, including unknown neighbor DNA."""
from pathlib import Path
import sys
import unittest
import numpy as np

sys.path.insert(0, str(Path(__file__).absolute().parents[1]/'scripts'))
from e027_learning_review import neighborhood_census, frozen_manifest_contract


class CensusContract(unittest.TestCase):
    """Unknown endpoints must remain in five-neighbor and full-DNA denominators."""
    def test_full_strata_and_unknown_endpoints(self):
        ids = np.array(['a', 'a2', 'v', 'u', 'b', 'v2', 'excluded'])
        data = dict(ids=ids, lengths=np.array([500,1000,10000,900,1500,2000,400]),
                    eligible=np.array([True]*6+[False]), depth_evidence=np.array([True,True,True,False,False,True,False]))
        nn = np.full((7,5), -1, np.int64)
        for i in range(6): nn[i] = [j for j in range(6) if j != i]
        labels = dict(a='G', a2='G', v='V', u=None, b='H', v2='V', excluded=None)
        r = neighborhood_census(data, nn, labels, {'G','H'}, {'a'})
        self.assertEqual(r['full_rows'], 7)
        self.assertEqual(r['full_bp'], 16300)
        self.assertEqual(sum(v['contigs'] for v in r['cells'].values()), 7)
        target = r['summary']['positive_cellular_target']
        self.assertEqual(target['queries'], 3)
        self.assertEqual(target['unknown_endpoints'], 3)
        self.assertAlmostEqual(target['same_origin_fraction'], 2/15)
        self.assertAlmostEqual(target['bp_weighted_same_origin'], .1)
        self.assertIsNone(r['summary']['unattributed']['same_origin_fraction'])
        self.assertTrue(any('excluded' in k for k in r['cells']))

    def test_exact_context_omission_and_required_hybrid_provenance(self):
        frozen_manifest_contract(dict(kind='context_checkpoint',config={}),None)
        frozen_manifest_contract(dict(kind='relational_checkpoint',config={},training_frozen_sha256=None),None)
        frozen_manifest_contract(dict(kind='hybrid_checkpoint',config={'hybrid':{}},training_frozen_sha256='a'*64),'a'*64)
        for m,wanted in [(dict(kind='context_checkpoint',config={},training_frozen_sha256=None),None),
                         (dict(kind='hybrid_checkpoint',config={'hybrid':{}}),'a'*64),
                         (dict(kind='relational_checkpoint',config={}),None)]:
            with self.assertRaises(ValueError): frozen_manifest_contract(m,wanted)


if __name__ == '__main__': unittest.main()
