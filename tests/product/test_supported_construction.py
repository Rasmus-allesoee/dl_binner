"""Real cached readers, biological selection, profile/update and DNA contracts."""
import json
from pathlib import Path
import tempfile
import unittest

import numpy as np

from discovery_fixture import fixture
from dl_binner.construction import grouping as g
from dl_binner.discovery import exact
from dl_binner.information.export import export
from dl_binner.context.tokens import binding


class SupportedConstruction(unittest.TestCase):
    def test_real_restore_run_reload_full_DNA_export_and_corruption_refusal(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);f=fixture(root/'input',64);names=['features','embeddings','graph','fasta','evidence']
            before={k:binding(f[k]) for k in names};cache=root/'cache';old=root/'accepted'
            exact.prepare(f['features'],f['embeddings'],f['graph'],cache)
            exact.run(f['features'],f['embeddings'],f['graph'],f['evidence'],cache,old)
            args=[f[k] for k in ['features','embeddings','graph','evidence']]+[old]
            out=root/'new';m=g.run(*args,out)
            self.assertEqual(m['status'],'SUCCESS');self.assertEqual(g.audit(*args,out)['status'],'PASS')
            for arm in ['root-only','pre','post']:
                result=export(f['features'],out/(arm+'-partition.json'),f['fasta'],root/('export-'+arm),include_dna=True)
                self.assertEqual(result['bp'],int(f['data']['lengths'].sum()))
                part=json.loads((out/(arm+'-partition.json')).read_text())
                self.assertEqual(len(part['ids']),len(f['data']['ids']))
                self.assertEqual(sum(x<0 for x in part['assignment']),part['unassigned'])
            self.assertEqual(before,{k:binding(f[k]) for k in names})
            with (old/'forest.npz').open('ab') as stream:stream.write(b'corrupt')
            with self.assertRaisesRegex(ValueError,'Missing/corrupt accepted'):g.restore(*args)

    def test_additive_tree_moments_match_explicit_subtree(self):
        children=np.array([[-1,-1],[-1,-1],[-1,-1],[0,1],[2,3]],np.int64)
        x=np.array([[1.,2.],[3.,4.],[8.,2.]]);w=np.array([2.,3.,4.])
        m,s,q=g.reduce_moments(children,w,x)
        for node,rows in [(0,[0]),(3,[0,1]),(4,[0,1,2])]:
            self.assertEqual(m[node],w[rows].sum());np.testing.assert_allclose(s[node],(w[rows,None]*x[rows]).sum(0))
            self.assertEqual(q[node],(w[rows]*np.square(x[rows]).sum(1)).sum())

    def test_root_bias_refused_and_marker_negative_children_eligible(self):
        tree=dict(children=np.array([[-1,-1]]*4+[[0,1],[2,3],[4,5]]),mass=np.array([10000]*4+[20000,20000,40000]),core=np.ones(4),roots=np.array([6]))
        candidates=[dict(node=6,parent=-1,children=[1,2],stability=1e12,birth=0.),
            dict(node=4,parent=0,children=[],stability=100.),dict(node=5,parent=0,children=[],stability=100.)]
        evidence=dict(panel_size=10,calls={});stats=dict(support=np.ones((3,2)))
        for control in [False,True]:
            kept,choices=g.select(tree,candidates,np.array([10000]*4),['a','b','c','d'],evidence,stats,g.policy(),control)
            self.assertEqual(set(kept),{1,2});self.assertTrue(choices[0]['internal_root_excluded'])

    def test_explicit_missing_zero_positive_and_constant_depth(self):
        ids=np.array(['q0','q1','q2','q3']);valid=np.ones(4,bool);nn=np.array([[1,2,3],[0,2,3],[0,1,3],[0,1,2]])
        data=dict(ids=ids,lengths=np.array([1000,1500,2500,3000]),tnf=np.array([[.8,.2],[.6,.4],[.3,.7],[.2,.8]]),depth=np.array([[0.,0.],[0.,0.],[4.,2.],[0.,0.]]),depth_measured=np.array([True,True,True,False]))
        _,_,measured,positive,radii,active,m=g.profiles(data,valid,np.arange(4),nn,g.policy())
        self.assertEqual((m['measured_zero_rows'],m['missing_rows'],m['positive_rows']),(2,1,1))
        self.assertTrue(active[1]);self.assertEqual(positive.tolist(),[False,False,True,False])
        data['depth']=np.zeros((4,0));data['depth_measured']=np.zeros(4,bool)
        _,_,_,_,_,active,m=g.profiles(data,valid,np.arange(4),nn,g.policy())
        self.assertFalse(active[1]);self.assertEqual(m['missing_rows'],4)
        center=dict(mean=[np.array([0.]),np.array([0.])],scatter=[0.,0.],positive=True,measured=True)
        value=g.compatibility([np.array([0.]),np.array([99.])],False,center,np.ones(2),np.ones(2,bool),1.,g.policy(),False)
        self.assertEqual(value,.75)  # perfect composition + neutral missing depth

    def test_reliable_physical_copies_are_soft_and_partial_weights_retained(self):
        cfg=g.policy();clean={'m':[1.]};partial={'m':[.1]};repeat={'m':[1.]}
        weak=g.marker_change(clean,partial,10,cfg);strong=g.marker_change(clean,repeat,10,cfg)
        self.assertGreater(weak,strong);self.assertGreater(strong,-1)
        center=dict(mean=[np.zeros(1),np.zeros(1)],scatter=[0.,0.],positive=True,measured=True)
        score=g.compatibility([np.zeros(1),np.array([10.])],True,center,np.ones(2),np.ones(2,bool),1.,cfg)
        self.assertGreater(score,.5)  # one bad channel is not an automatic veto

    def test_recruitment_is_synchronous_ambiguous_abstains_and_all_rows_survive(self):
        # Two established bins, a supported unassigned row and a tied unassigned
        # row. Only existing neighbor votes and fixed parent profiles are used.
        assign=np.array([0,0,1,1,-1,-1]);nn=np.array([[1,4,5],[0,4,5],[3,5,4],[2,5,4],[0,1,5],[0,2,4]])
        dd=np.ones((6,3));coords=(np.zeros((6,2)),np.zeros((6,1)));weights=(np.ones(6)*10000,np.ones(6)*10000)
        measured=np.ones(6,bool);positive=np.zeros(6,bool);lengths=np.ones(6,dtype=np.int64)*10000
        result,trace=g.supported_updates(assign,nn,dd,coords,weights,measured,positive,lengths,list('abcdef'),dict(panel_size=10,calls={}),np.ones(2),np.array([True,False]),g.policy())
        self.assertEqual(result[4],0);self.assertEqual(result[5],-1)
        self.assertFalse(trace['recruited_rows_can_recruit']);self.assertEqual(len(trace['recruitment']),2)
        np.testing.assert_array_equal(assign,np.array([0,0,1,1,-1,-1]))

    def test_singleton_root_keeps_existing_long_supported_leaf(self):
        tree=dict(children=np.array([[-1,-1]]),mass=np.array([250000]),core=np.ones(1),roots=np.array([0]))
        candidates=[dict(node=0,parent=-1,children=[],stability=100.,birth=0.)]
        evidence=dict(panel_size=10,calls={'a':{'m':[1.],'n':[.9]}})
        kept,choices=g.select(tree,candidates,np.array([250000]),['a'],evidence,dict(support=np.ones((1,2))),g.policy())
        self.assertEqual(kept,[0]);self.assertFalse(choices[0]['internal_root_excluded'])
        candidates[0]['stability']=0.
        kept,_=g.select(tree,candidates,np.array([250000]),['a'],dict(panel_size=10,calls={}),dict(support=np.ones((1,2))),g.policy())
        self.assertEqual(kept,[0])

    def test_mutual_supported_merge_and_context_rejection_use_real_update_path(self):
        assignment=np.array([0,0,1,1]);nn=np.array([[1,2,3],[0,2,3],[0,1,3],[0,1,2]])
        dd=np.ones((4,3));lengths=np.full(4,10000,np.int64);weights=(lengths.astype(float),lengths.astype(float))
        measured=np.ones(4,bool);positive=np.zeros(4,bool);evidence=dict(panel_size=10,calls={})
        for conflict in [False,True]:
            comp=np.zeros((4,2))
            if conflict:comp[2:]=100.
            result,trace=g.supported_updates(assignment,nn,dd,(comp,np.zeros((4,1))),weights,measured,positive,
                lengths,list('abcd'),evidence,np.ones(2),np.array([True,False]),g.policy())
            self.assertEqual(len(trace['merge_candidates']),1)
            self.assertEqual(trace['merge_candidates'][0]['accepted'],not conflict)
            self.assertEqual(len(set(result)),2 if conflict else 1)
            self.assertEqual(trace,json.loads(json.dumps(trace)))
            self.assertEqual(set(trace['pre_internal_to_canonical']),{'0','1'})
            self.assertTrue(trace['fixed_post_merge_profiles'])

    def test_policy_refuses_grid_and_untyped_overrides(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'policy.json';cfg=g.policy();cfg['merge_score']=.5;p.write_text(json.dumps(cfg))
            with self.assertRaises(ValueError):g.policy(p)


if __name__=='__main__':unittest.main()
