"""Actual NPZ sparse/opaque-ID/unit-neighbor readers on small numeric artifacts."""
from pathlib import Path
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0,str(Path(__file__).absolute().parents[1]/'scripts'))
from e014_collect import binding
from e014_graph_review import review


class NativeGraphReaderContracts(unittest.TestCase):
    def test_actual_unsorted_opaque_axes_and_corruption_refusal(self):
        import numpy as np
        from dl_binner.io import save_arrays
        from dl_binner.candidate.grouping import rank_candidates
        with tempfile.TemporaryDirectory()as t:
            unit=Path(t)/'oral-dev5';(unit/'group').mkdir(parents=True)
            ids=['opaque_'+str(i)for i in [7,1,9,3,11,2,6,0,10,4,8,5]]
            x=np.random.default_rng(17).uniform(.1,1,(12,64)).astype(np.float32);x/=np.linalg.norm(x,axis=1)[:,None]
            candidates=np.tile(np.arange(12),(12,1));nn,_=rank_candidates(x,ids,candidates,5)
            edges=np.array([(i,j)for i in range(12)for j in range(12)if ids[i]<ids[j]],np.int64);weights=np.full(len(edges),.7,np.float64)
            save_arrays(unit/'embeddings.npz',dict(ids=np.array(ids),features=x,evidence=np.ones(12,bool)),dict(kind='embeddings',metric='unit cosine',features_sha256='fixture'))
            save_arrays(unit/'group/graph.npz',dict(ids=np.array(ids),neighbors=nn,edges=edges,weights=weights),dict(kind='candidate_sparse_graph',embedding_sha256=binding(unit/'embeddings.npz')['sha256'],audit=dict(mode='tiny exact fixture')))
            pre=dict(ids=ids,valid=[True]*12,neighbors=[[ids[j]for j in n]for n in nn],graph_sha256=binding(unit/'group/graph.npz')['sha256'],embedding_sha256=binding(unit/'embeddings.npz')['sha256'],config=dict(neighbors=5),objective=dict(gamma=float(np.median(weights))/5,node_sizes=1,seed=11))
            (unit/'group/partition.json').write_text(json.dumps(pre))
            result=review(unit,Path(t)/'proof.json');self.assertEqual(result['status'],'PASS');self.assertEqual(result['geometry']['native_rows_checked'],12)
            transfer=Path(t)/'transfer';transfer.mkdir();scripts=Path(__file__).absolute().parents[1]/'scripts'
            for name in ['e014_collect.py','e014_graph_review.py']:shutil.copyfile(scripts/name,transfer/name)
            env={k:v for k,v in os.environ.items()if k not in ['PYTHONPATH','PYTHONHOME','PYTHONUSERBASE']}
            env.update(PYTHONNOUSERSITE='1',OMP_NUM_THREADS='4',OPENBLAS_NUM_THREADS='4',MKL_NUM_THREADS='4')
            subprocess.run([sys.executable,'-I','-B',str(transfer/'e014_graph_review.py'),'--unit',str(unit),
                '--output',str(Path(t)/'transferred-proof.json'),'--research-scripts',str(scripts)],
                cwd=t,env=env,check=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
            self.assertEqual(json.loads((Path(t)/'transferred-proof.json').read_text())['status'],'PASS')
            pre['neighbors'][0][0]=ids[0];(unit/'group/partition.json').write_text(json.dumps(pre))
            with self.assertRaisesRegex(ValueError,'top-five'):review(unit,Path(t)/'refused.json')


if __name__=='__main__':unittest.main()
