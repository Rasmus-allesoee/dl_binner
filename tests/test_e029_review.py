"""Real numeric-reader and source-blind display contracts for E029 inspection."""
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT=Path(__file__).absolute().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from e029_control import product_scope
product_scope()
import numpy as np
from dl_binner.calibrated.arrays import save
from dl_binner.density.grouping import hierarchy
from dl_binner.unified.grouping import policy
from e024_coverage import binding,write
from e029_review import JointNeighbors,sparse_contract
from e029_summary import disposition


class ReviewReaders(unittest.TestCase):
    """Use actual compressed numeric artifacts, unequal opaque IDs and exclusion."""
    def fixture(self,root):
        ids=np.array(['C'+str(i*17+11) for i in range(32)])
        eligible=np.ones(32,bool);eligible[7]=False
        lengths=np.arange(32,dtype=np.int64)+1000
        selected=np.array(sorted(np.flatnonzero(eligible),key=lambda i:str(ids[i])),np.int64)
        n=len(selected);nn=np.array([[j for j in range(n)if j!=i]for i in range(n)],np.int32)
        dd=np.ones((n,n-1),np.float64)
        features=root/'features.fixture';features.write_bytes(b'Bound tiny source, not community DNA')
        group=root/'result';(group/'retrieval').mkdir(parents=True)
        save(group/'retrieval/neighbors.npz',dict(selected=selected,neighbors=nn,distances=dd),
             dict(kind='unified_graded_neighbors'),ids)
        tree=hierarchy(nn,dd,lengths[selected],policy())
        save(group/'forest.npz',{k:v for k,v in tree.items()if isinstance(v,np.ndarray)},
             dict(kind='unified_density_forest'),ids)
        files={str(p.relative_to(group)):binding(p)for p in group.rglob('*')if p.is_file()}
        write(group/'completed.json',dict(input_sha256=dict(features=binding(features)['sha256']),
              truth_accessed=False,files=files))
        inventory={'tiny/'+k:v for k,v in files.items()}
        data=dict(ids=ids,eligible=eligible,lengths=lengths)
        return group,features,data,inventory

    def test_real_cache_forest_and_excluded_full_axis(self):
        with tempfile.TemporaryDirectory()as folder:
            group,features,data,inventory=self.fixture(Path(folder))
            a,proof=sparse_contract(group,features,data,inventory,'tiny')
            self.assertEqual(proof['rows'],32);self.assertEqual(proof['eligible'],31)
            adapter=JointNeighbors(data['ids'].tolist(),a['selected'],a['neighbors'])
            self.assertEqual(len(adapter),32);self.assertEqual(adapter[7],[])
            for local,full in enumerate(a['selected']):
                self.assertEqual(adapter[int(full)],data['ids'][a['selected'][a['neighbors'][local,:5]]].tolist())
                self.assertNotIn(data['ids'][full],adapter[int(full)])

    def test_real_reader_refuses_corrupt_bytes(self):
        with tempfile.TemporaryDirectory()as folder:
            group,features,data,inventory=self.fixture(Path(folder))
            with (group/'retrieval/neighbors.npz').open('ab')as f:f.write(b'corrupt')
            with self.assertRaises(ValueError):sparse_contract(group,features,data,inventory,'tiny')

    def test_full_axis_reordering_refused(self):
        with tempfile.TemporaryDirectory()as folder:
            group,features,data,inventory=self.fixture(Path(folder))
            data['ids']=data['ids'][::-1].copy()
            with self.assertRaises(ValueError):sparse_contract(group,features,data,inventory,'tiny')

    def test_matching_bytes_do_not_admit_self_neighbors(self):
        with tempfile.TemporaryDirectory()as folder:
            root=Path(folder);group,features,data,inventory=self.fixture(root)
            path=group/'retrieval/neighbors.npz'
            with np.load(path,allow_pickle=False)as z:a={k:z[k]for k in z.files}
            a['neighbors'][0,0]=0;path.unlink();path.with_suffix('.json').unlink()
            save(path,a,dict(kind='unified_graded_neighbors'),data['ids'])
            record=json.loads((group/'completed.json').read_text())
            for name in ['retrieval/neighbors.npz','retrieval/neighbors.json']:
                record['files'][name]=binding(group/name);inventory['tiny/'+name]=binding(group/name)
            (group/'completed.json').unlink();write(group/'completed.json',record)
            with self.assertRaises(ValueError):sparse_contract(group,features,data,inventory,'tiny')


class FrozenDecision(unittest.TestCase):
    """Exercise failed criteria and boundary cases independently of community scores."""
    def setUp(self):
        self.protocol=json.loads((ROOT/'experiments/E029-certifiable-joint-retrieval/protocol.json').read_text())
        self.metrics={}
        for name,anchor in [('E009-GLM','E009_E023'),('oral-noGLM','oral_E026')]:
            a=self.protocol['anchors'][anchor]
            self.metrics[name]=dict(bp_weighted_R95=a['R95'],at_least_50_percent=a['target50'],at_least_90_percent=a['target90'])

    def test_no_improvement_abandons_only_frozen_bundle(self):
        self.assertEqual(disposition(self.metrics,self.protocol),'ABANDON_THIS_FROZEN_BUNDLE')

    def test_target_gain_with_recovery_loss_is_modify(self):
        self.metrics['oral-noGLM']['bp_weighted_R95']-=.01
        self.metrics['oral-noGLM']['at_least_90_percent']+=1
        self.assertEqual(disposition(self.metrics,self.protocol),'MODIFY')

    def test_exact_frozen_gain_and_no_count_loss_pass(self):
        for value in self.metrics.values():value['bp_weighted_R95']+=.005
        self.assertEqual(disposition(self.metrics,self.protocol),'KEEP')

    def test_large_recovery_gain_does_not_hide_target_regression(self):
        for value in self.metrics.values():value['bp_weighted_R95']+=.02
        self.metrics['E009-GLM']['at_least_50_percent']-=1
        self.assertEqual(disposition(self.metrics,self.protocol),'MODIFY')


if __name__=='__main__':unittest.main()
