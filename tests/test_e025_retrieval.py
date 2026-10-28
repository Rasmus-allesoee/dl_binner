"""Real compiled joint discovery, source-blind cache and complete export contracts."""
import copy
import json
from pathlib import Path
import pickle
import tempfile
import unittest
from unittest.mock import patch

import numpy as np
from e024_coverage import binding
from e024_information import rebind,load_rebound
from e025_information import JointIndex,joint_metric,exact_distances,candidates,run,audit,POLICY
from dl_binner.density.grouping import context_channels,policy
from dl_binner.multiview.arrays import load_arrays
from test_e024_coverage import fixture,matrix_fixture

ROOT=Path(__file__).absolute().parents[1]
CFG=policy(ROOT/'experiments/E023-adaptive-density-bins/config.json')


def retained(root):
    """Build actual tiny DNA/rebind/cache schemas; vectors and marker calls synthetic."""
    u,_=fixture(root);summary=root/'summary';summary.mkdir()
    matrix=matrix_fixture(summary,u['reference'])
    rebind(u['features'],u['views'],u['embeddings'],matrix,u['reference'],root/'rebound')
    return u,root/'rebound/rebind.json'


class Retrieval(unittest.TestCase):
    def test_compiled_metric_exact_pair_weights_missing_and_constant_depth(self):
        self.assertEqual(POLICY,json.loads((ROOT/'experiments/E025-joint-distance-retrieval/index-policy.json').read_text()))
        n=96;rng=np.random.default_rng(11)
        vectors=rng.normal(size=(n,64)).astype(np.float32)
        vectors/=np.linalg.norm(vectors,axis=1)[:,None]
        data=dict(ids=np.array([f'opaque-{i:04}' for i in range(n)]),lengths=rng.integers(500,20000,n),
            tnf=rng.dirichlet(np.ones(136),n).astype(np.float32),
            depth=rng.uniform(0,20,(n,10)).astype(np.float32),eligible=np.ones(n,bool),depth_evidence=np.ones(n,bool))
        data['depth'][::3]=0;data['depth_evidence'][::3]=False
        data['depth'][data['depth_evidence'],9]=5
        cfg=copy.deepcopy(CFG);channels,available,scales,_=context_channels(data,vectors,np.arange(n),cfg)
        old=dict(neighbors=np.array([[(i+j)%n for j in range(1,31)] for i in range(n)]))
        index=JointIndex(data,channels,available,scales,np.arange(n),old,cfg,4,True)
        self.assertIsNotNone(index.native)
        for i in [0,1,7]:
            exact=exact_distances(data,channels,available,scales,cfg,i,np.arange(n))
            actual=np.array([joint_metric(index.x[i],x,*index.args.values()) for x in index.x])
            np.testing.assert_allclose(actual,exact,rtol=1e-12,atol=1e-12)
            self.assertTrue(np.isfinite(actual).all())
        # Actual compiled query and native pickle/reload; no fake index or CLI.
        q,d=index.native.query(index.x[:4],k=31)
        restored=pickle.loads(pickle.dumps(index.native))
        q2,d2=restored.query(index.x[:4],k=31)
        np.testing.assert_array_equal(q,q2);np.testing.assert_array_equal(d,d2)
        recalls=[]
        for i in range(4):
            exact=exact_distances(data,channels,available,scales,cfg,i,np.arange(n))
            exact[i]=np.inf;threshold=np.sort(exact)[29]
            chosen=q[i][q[i]!=i][:30]
            recalls.append(np.mean(exact[chosen]<=threshold+1e-10))
        self.assertGreaterEqual(np.mean(recalls),.9)
        with tempfile.TemporaryDirectory() as tmp:
            _,nn,dd,observed=candidates(data,vectors,data['eligible'],old,cfg,4,
                Path(tmp)/'compiled-consumer',force_native=True)
            self.assertEqual(nn.shape,(n,30))
            self.assertTrue(observed['exact_native_metric'])
            self.assertGreaterEqual(observed['final_composite_recall'],.9)

    def test_real_rebind_sparse_mapping_hierarchy_marker_exports_and_reload(self):
        from dl_binner.information.export import export
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);u,receipt=retained(root)
            before={k:binding(v) for k,v in u.items() if isinstance(v,Path) and v.is_file()}
            result=run(receipt,u['graph'],u['marker_evidence'],root/'new',CFG)
            self.assertEqual(result['audit']['final_composite_recall'],1.)
            self.assertEqual(audit(receipt,u['graph'],u['marker_evidence'],root/'new',CFG)['status'],'PASS')
            a,m=load_arrays(root/'new/retrieval/neighbors.npz','E025_joint_candidates')
            self.assertEqual(a['ids'].tolist(),json.loads((root/'new/selected-partition.json').read_text())['ids'])
            self.assertEqual(m['audit']['index_policy'],POLICY)
            for arm in ['density','selected']:
                emitted=export(root/'rebound/features.npz',root/'new'/(arm+'-partition.json'),u['reference'],root/arm,True)
                self.assertEqual(sum(v['contigs'] for v in emitted['populations'].values()),len(a['ids']))
            self.assertEqual(before,{k:binding(u[k]) for k in before})
            with self.assertRaises(FileExistsError):run(receipt,u['graph'],u['marker_evidence'],root/'new',CFG)

    def test_failed_gate_persists_numeric_answers_and_arrays(self):
        # Patch only proposals to emulate an inaccurate external index; score,
        # exhaustive audit, writer and actual exception are production consumers.
        n=96;rng=np.random.default_rng(11);v=rng.normal(size=(n,64)).astype(np.float32)
        data=dict(ids=np.array([f'q-{i:04}' for i in range(n)]),lengths=np.full(n,1000),
            tnf=rng.dirichlet(np.ones(136),n).astype(np.float32),depth=np.zeros((n,10),np.float32),
            eligible=np.ones(n,bool),depth_evidence=np.zeros(n,bool))
        original=dict(neighbors=np.array([[(i+j)%n for j in range(1,31)] for i in range(n)]))
        with tempfile.TemporaryDirectory() as tmp,patch.object(JointIndex,'proposals',lambda s,i:np.arange(31)):
            out=Path(tmp)/'failed'
            with self.assertRaisesRegex(ValueError,'numeric evidence retained'):
                candidates(data,v,data['eligible'],original,CFG,4,out)
            observed=json.loads((out/'audit.json').read_text())
            self.assertEqual(observed['status'],'FAILED_RECALL_GATE')
            self.assertLess(observed['final_composite_recall'],.9)
            self.assertEqual(len(observed['queries']),32)
            self.assertTrue(all(q['exact_ids'] and q['returned_distances'] for q in observed['queries']))
            load_arrays(out/'neighbors.npz','E025_joint_candidates')

    def test_empty_singleton_ties_and_malformed_lengths(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);u,receipt=retained(root)
            data,v,valid,_,_=load_rebound(receipt)
            original,_=__import__('dl_binner.density.grouping',fromlist=['sparse_input']).sparse_input(u['graph'],data['ids'].tolist(),valid,u['embeddings'])
            for n in [0,1]:
                mask=np.zeros_like(valid);mask[np.flatnonzero(valid)[:n]]=True
                # No original neighbors are consulted for no/one query candidate.
                orig=dict(neighbors=np.full((len(mask),0),-1,np.int64))
                _,nn,dd,r=candidates(data,v,mask,orig,CFG,4,root/str(n))
                self.assertEqual(nn.shape,(n,0));self.assertEqual(r['final_composite_recall'],1.)
            # All informative channels tied: actual compiled native proposals,
            # exact opaque-ID tie ordering, explicit self-neighbor removal.
            tied=copy.deepcopy(data);tied['tnf'][:]=data['tnf'][0]
            tied['depth'][:]=0;tied['depth_evidence'][:]=False
            tied_vectors=np.zeros_like(v);tied_vectors[valid,0]=1
            selected,nn,dd,observed=candidates(tied,tied_vectors,valid,original,CFG,4,root/'ties',force_native=True)
            self.assertEqual(observed['final_composite_recall'],1.)
            self.assertTrue(np.all(dd==CFG['distance_floor']))
            self.assertTrue(all(i not in row and len(set(row))==len(row) for i,row in enumerate(nn)))
            channels,available,scales,_=context_channels(data,v,np.flatnonzero(valid),CFG)
            changed=copy.deepcopy(data);changed['lengths'][0]=2**24+1
            with self.assertRaisesRegex(ValueError,'Length packing'):
                JointIndex(changed,channels,available,scales,np.flatnonzero(valid),original,CFG)


if __name__=='__main__':unittest.main()
