"""Real sparse-candidate selection contracts, independent of ignored research data."""
import unittest
import numpy as np
from dl_binner.selection import grouping as s


def context(n=8):
    """Use actual measured parent profiles and physical calls, no truth labels."""
    comp=np.tile([.8,.6],(n,1));depth=np.zeros((n,1))
    weights=(np.full(n,100000.),np.full(n,100000.))
    measured=np.ones(n,bool);positive=np.zeros(n,bool)
    ids=[f'opaque-{i:03}' for i in range(n)]
    evidence=dict(panel_size=10,calls={q:{'family-'+str(i):[1.]} for i,q in enumerate(ids)})
    return ((comp,depth),weights,measured,positive,np.full(n,100000,np.int64),ids,evidence,np.ones(2),np.ones(2,bool))


class Selection(unittest.TestCase):
    def test_shared_intervals_and_malformed_branch_refusal(self):
        tree=dict(children=np.array([[-1,-1],[-1,-1],[-1,-1],[0,1],[2,3]]),
                  roots=np.array([4]),core=np.ones(3))
        order,lo,hi=s.forest_layout(tree)
        self.assertEqual(order.tolist(),[2,0,1]);self.assertEqual((lo[3],hi[3]),(1,3))
        view=s.Membership.create(order,3)
        s.occupancy_update(view.bit,view.inverse[np.array([0])],-1)
        self.assertEqual(s.occupancy_count(view.bit,lo[3],hi[3]),1)
        tree['children'][4]=[0,3]
        with self.assertRaisesRegex(ValueError,'shared child'):s.forest_layout(tree)

    def test_fixed_overlap_residual_and_whole_child_alternatives(self):
        ctx=context(4);cfg=s.policy();view=s.Membership.create(np.arange(4),4)
        pool=[]
        for key,lo,hi in [('whole',0,3),('child',0,2),('overlap',1,4)]:
            stats,_=s.measured_stats(np.arange(lo,hi),*ctx[:4],ctx[4],ctx[5],ctx[6],ctx[7],ctx[8],cfg)
            pool.append(dict(stats,key=key,view=0,lo=lo,hi=hi))
        assign,trace=s.select(pool,[view],ctx,cfg)
        self.assertTrue(np.all(assign>=0));self.assertEqual(len(set(assign)),2)
        self.assertTrue(any(t['reason']=='selected_residual' for t in trace))
        self.assertTrue(any(t['reason']=='fully_claimed' for t in trace))

    def test_marker_negative_long_and_short_accounting(self):
        cfg=s.policy();long=dict(bp=300000,breadth=0.,score=.1)
        self.assertTrue(s.admissible(long,cfg));self.assertFalse(s.admissible(dict(long,bp=10000),cfg))
        self.assertGreater(s.score(300000,0.,0.,[1.,.5],cfg),0)
        with self.assertRaises(ValueError):s.policy(__file__)

    def test_positive_zero_and_missing_profile_semantics(self):
        ctx=context(4);cfg=s.policy()
        stats,center=s.measured_stats(np.arange(4),*ctx,cfg)
        self.assertEqual(stats['support'][1],.5);self.assertTrue(center['measured']);self.assertFalse(center['positive'])
        missing=list(ctx);missing[2]=np.zeros(4,bool);missing[1]=(ctx[1][0],np.zeros(4))
        _,center=s.measured_stats(np.arange(4),*missing,cfg)
        self.assertFalse(center['measured'])

    def test_joint_duplicate_damage_retains_unchanged_parent(self):
        ctx=list(context(4));ctx[6]=dict(panel_size=10,calls={q:{'same-family':[1.]} for q in ctx[5]})
        assign=np.array([0,0,-1,-1]);near=np.array([[1,2],[0,2],[0,1],[0,1]])
        dist=np.ones((4,2));after,trace=s.joint_updates(assign,[(near.astype(np.int32),dist),(near,dist.astype(np.float32))],tuple(ctx),s.policy())
        self.assertEqual(after.tolist(),assign.tolist())
        self.assertTrue(trace['groups']);self.assertFalse(trace['groups'][0]['accepted'])
        self.assertTrue(all(r['reason']=='joint_update_abstention' for r in trace['proposals']))

    def test_distinct_support_does_not_double_count_two_geometries(self):
        near=np.array([[1,2],[0,2],[0,1]]);dist=np.ones((3,2))
        labels,votes,support,runner=s.propose(np.array([-1,0,-1]),near,dist,near,dist,2,2/3,1.5)
        self.assertEqual(support[0],1);self.assertEqual(labels[0],-1)

    def test_supported_joint_gain_accepts_the_complete_group(self):
        ctx=context(4);assign=np.array([0,0,-1,-1]);near=np.array([[1,2],[0,2],[0,1],[0,1]])
        dist=np.ones((4,2));after,trace=s.joint_updates(assign,[(near,dist),(near,dist)],ctx,s.policy())
        self.assertEqual(after.tolist(),[0,0,0,0]);self.assertTrue(trace['groups'][0]['accepted'])
        self.assertEqual(trace['groups'][0]['proposed_rows'],[2,3])


if __name__=='__main__':unittest.main()
