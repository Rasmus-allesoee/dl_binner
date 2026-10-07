"""Check E003 counting, truth-blind geometry, full-denominator metrics and decisions."""
from collections import Counter
from pathlib import Path
import sys
import subprocess
import tempfile
import unittest
import numpy as np

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import e003_representation_screen as screen


class ScreenTests(unittest.TestCase):
    def test_nested_native_cleanup_and_stale_pid_safety(self):
        import psutil
        with tempfile.TemporaryDirectory() as tmp:
            record=Path(tmp)/'native.json'
            child=subprocess.Popen([sys.executable,'-c','import time;time.sleep(120)'],start_new_session=True)
            try:
                created=psutil.Process(child.pid).create_time()
                screen.prior.write_json(record,dict(pid=child.pid,created=created-1))
                screen.cleanup_native(record)
                self.assertIsNone(child.poll())
                screen.prior.write_json(record,dict(pid=child.pid,created=created))
                screen.cleanup_native(record)
                child.wait(timeout=3)
                # psutil.wait can reap this child before Popen.wait sees its status.
                self.assertFalse(psutil.pid_exists(child.pid))
            finally:
                if child.poll() is None:child.kill();child.wait()
    def test_tnf_strand_ambiguity_and_independent_counts(self):
        seq = 'AAAACGTACGTNNAAAA'
        x, counts = screen.tnf([('a',seq),('b',screen.prior.reverse_complement(seq)),('z','NNNNNN')])
        np.testing.assert_array_equal(x[0],x[1])
        self.assertEqual(counts[0],sum(set(seq[i:i+4])<=set('ACGT') for i in range(len(seq)-3)))
        self.assertEqual(counts[-1],0)
        self.assertEqual(x.shape,(3,136))
        self.assertAlmostEqual(x[0].sum(),1)
        self.assertTrue((x[-1]==0).all())

    def test_geometry_noise_ties_and_no_oracle_count(self):
        ids = ['b','a','c','d','e','f','z']
        x = np.array([[2,1],[2,1],[2,1],[1,2],[1,2],[1,2],[0,0]],dtype=np.float32)
        result = screen.geometry(x,ids,k=2,min_size=3)
        self.assertEqual(result['clusters'],2)
        self.assertEqual(result['assignment'][-1],-1)
        self.assertNotIn('genome',result)
        self.assertEqual(result['neighbors'][0][0],'a')
        with self.assertRaises(ValueError):screen.geometry(x,[ids[0]]*7)

    def test_metrics_keep_unassigned_and_missing_neighbors(self):
        panel={'rows':[dict(id='a',genome='g',bp=500),dict(id='b',genome='g',bp=768),
                       dict(id='c',genome='h',bp=1000),dict(id='d',genome='h',bp=2500),
                       dict(id='e',genome='j',bp=10000)]}
        partition=dict(ids=['a','b','c','d','e'],assignment=[0,0,-1,-1,-1],
                       neighbors=[['b'],['a'],[],[],[]],clusters=1,unassigned=3)
        result=screen.score(partition,panel)
        self.assertAlmostEqual(result['all']['b3_f1'],.4)
        self.assertAlmostEqual(result['all']['neighbor_purity'],.08)
        self.assertEqual(result['by_length']['10000']['b3_f1'],0)
        changed={'rows':[dict(r,genome='j') for r in panel['rows']]}
        self.assertEqual(partition['assignment'],[0,0,-1,-1,-1])
        self.assertNotEqual(screen.score(partition,changed)['all']['b3_f1'],result['all']['b3_f1'])

    def test_predeclared_joint_decision(self):
        cfg={'decision':dict(short_neighbor_gain_min=.1,long_neighbor_delta_min=-.05,base_weighted_b3_gain_min=.05)}
        def values(n,l,b):return dict(short=dict(neighbor_purity=n),long=dict(neighbor_purity=l),base_weighted=dict(b3_f1=b))
        scores={'tnf':values(.4,.8,.5),'glm':values(.6,.8,.7)}
        self.assertTrue(screen.decide(scores,cfg)['include_frozen_glm'])
        scores['glm']=values(.5,.75,.55)
        self.assertTrue(screen.decide(scores,cfg)['include_frozen_glm'])
        scores['glm']['long']['neighbor_purity']=.7
        self.assertFalse(screen.decide(scores,cfg)['include_frozen_glm'])


if __name__=='__main__':unittest.main()
