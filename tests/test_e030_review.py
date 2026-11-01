"""Prospective decision boundaries, real profile reader and unchanged summary reuse."""
import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT=Path(__file__).absolute().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from e030_control import product_scope
product_scope()
from e030_summary import disposition
from e024_coverage import binding


class NumericReview(unittest.TestCase):
    def test_real_profile_reader_reuse_axes_and_corrupt_bytes(self):
        sys.path.insert(0,str(ROOT/'tests/product'))
        from discovery_fixture import fixture
        from dl_binner.discovery import exact
        from dl_binner.construction import grouping as g
        from e030_review import profile_contract
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);f=fixture(root/'fixture',64);cache=root/'cache';old=root/'old';out=root/'new'
            exact.prepare(f['features'],f['embeddings'],f['graph'],cache)
            exact.run(f['features'],f['embeddings'],f['graph'],f['evidence'],cache,old)
            g.run(f['features'],f['embeddings'],f['graph'],f['evidence'],old,out)
            prefix='tiny';inv={prefix+'/'+p.name:binding(p) for p in out.iterdir() if p.is_file()}
            reused={prefix+'/'+str(p.relative_to(old)):binding(p) for p in old.rglob('*') if p.is_file()}
            proof=profile_contract(out,f['features'],f['data'],inv,prefix,dict(accepted_members=reused))
            self.assertEqual(proof['status'],'PASS_ACTUAL_NEW_NUMERIC_PROFILE_READER')
            reordered=dict(f['data'],ids=f['data']['ids'][::-1].copy())
            with self.assertRaises(ValueError):profile_contract(out,f['features'],reordered,inv,prefix,dict(accepted_members=reused))
            with (out/'candidate-profiles.npz').open('ab') as stream:stream.write(b'corrupt')
            with self.assertRaises(ValueError):profile_contract(out,f['features'],f['data'],inv,prefix,dict(accepted_members=reused))


class FrozenDecision(unittest.TestCase):
    def setUp(self):
        self.protocol=json.loads((ROOT/'experiments/E030-supported-biological-bins/protocol.json').read_text())
        self.metrics=copy.deepcopy(self.protocol['E029_primary_student'])

    def test_equality_is_not_new_improvement(self):
        self.assertEqual(disposition(self.metrics,self.protocol),'ABANDON_THIS_FROZEN_BUNDLE')

    def test_one_primary_gain_modifies(self):
        self.metrics['oral-noGLM']['bp_weighted_R95']+=.001
        self.assertEqual(disposition(self.metrics,self.protocol),'MODIFY')

    def test_both_gains_without_anchor_still_modify(self):
        for unit in ['E009-GLM','oral-noGLM']:self.metrics[unit]['bp_weighted_R95']+=.001
        self.assertEqual(disposition(self.metrics,self.protocol),'MODIFY')

    def test_joint_gain_one_anchor_and_no_target90_loss_keep(self):
        self.metrics['E009-GLM']['bp_weighted_R95']=self.protocol['anchors']['E009_E023']['R95']
        self.metrics['oral-noGLM']['bp_weighted_R95']+=.001
        self.assertEqual(disposition(self.metrics,self.protocol),'KEEP')
        self.metrics['oral-noGLM']['at_least_90_percent']-=1
        self.assertEqual(disposition(self.metrics,self.protocol),'MODIFY')


if __name__=='__main__':unittest.main()
