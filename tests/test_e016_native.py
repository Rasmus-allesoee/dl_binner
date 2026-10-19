"""Real tiny positive-only training, retained-cache and downstream contracts.

All science here is generated engineering DNA. Community consumers are absent.
Tensor and graph processes stay separate; the biological community marker panel
is not redetected. The native cached-marker/refiner path uses a real synthetic HMM.
"""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

REPO=Path(__file__).absolute().parents[1]
sys.path.insert(0,str(REPO/'scripts'));sys.path.insert(0,str(REPO/'tests/product'))
import numpy as np


class NativeContracts(unittest.TestCase):
    def test_actual_cached_two_modalities_train_exact_reload_graph_refine_export(self):
        from candidate_fixture import fixture,asset
        from dl_binner.multiview.views import config,prepare,load
        from dl_binner.candidate.markers import cache
        from e014_collect import binding
        from e016_collect import pack
        with tempfile.TemporaryDirectory() as t:
            p=Path(t);f,depth,rows=fixture(p);hmm,manifest=asset(p,f)
            marker=p/'markers';marker.mkdir();cache(f,hmm,manifest,marker,4);before=binding(marker/'cache.json')
            base=config();base.update(epochs=2,batch_size=4,sequence_hidden=16,sequence_output=8,depth_hidden=4,
                fusion_hidden=8,output=4,neighbors=5,min_bin_bp=100,min_bin_contigs=1)
            zero=base|dict(positive_only=True,predictor_hidden=128,ema_base=.996,collapse_rows=8192,collapse_min_std=.001,collapse_min_rank=2)
            (p/'base.json').write_text(json.dumps(base));(p/'zero.json').write_text(json.dumps(zero));units={}
            for name,dep in [('E009-positive',depth),('oral-positive',None)]:
                source=p/(name+'-retained');prepare(f,dep,source,base)
                units[name]=dict(fasta=str(f),features=str(source/'features.npz'),views=str(source/'views.npz'),marker_cache=str(marker))
            plan=dict(kind='Tiny engineering only',work=str(p/'work'),units=units,threads=4,python=sys.executable,
                worker=str(REPO/'scripts/e016_control.py'),workflow_python=os.environ.get('E016_WORKFLOW_PYTHON',sys.executable),
                snakefile=str(REPO/'experiments/E016-positive-only-multiview/Snakefile'),config=str(p/'zero.json'),
                base_config=str(p/'base.json'),hmm=str(hmm),reuse_lock='tiny-owned-fixture')
            (p/'plan.json').write_text(json.dumps(plan))
            if os.environ.get('E016_WORKFLOW_PYTHON'):
                r=subprocess.run([sys.executable,'-I','-B',str(REPO/'scripts/e016_control.py'),'--plan',str(p/'plan.json'),'--workflow'],capture_output=True,text=True)
                detail='\n'.join(str(x)+'\n'+x.read_text() for x in (p/'work/logs').rglob('*.log'))
                self.assertEqual(r.returncode,0,r.stdout+r.stderr+'\nNATIVE_STAGE_LOGS\n'+detail)
                self.assertIn('13 of 13 steps (100%) done',r.stdout+r.stderr)
            for name in units:
                bank=binding(units[name]['views'])
                for stage in ([] if os.environ.get('E016_WORKFLOW_PYTHON') else ['train','embed','group','refine','export','graph-proof']):
                    r=subprocess.run([sys.executable,'-I','-B',str(REPO/'scripts/e016_control.py'),'--plan',str(p/'plan.json'),
                        '--unit',name,'--stage',stage],capture_output=True,text=True)
                    self.assertEqual(r.returncode,0,r.stdout+r.stderr)
                root=p/'work/units'/name;ck=json.loads((root/'train/checkpoint.json').read_text())
                self.assertEqual(ck['config'],zero);self.assertEqual(ck['training_views_sha256'],bank['sha256'])
                data,meta,v,vm=load(units[name]['features'],units[name]['views'])
                ix=np.flatnonzero(data['eligible']);expected=[]
                rng=np.random.default_rng(zero['seed'])
                for epoch in range(zero['epochs']):
                    count=dropped=0;permutation=rng.permutation(ix)
                    for i in range(0,len(ix),zero['batch_size']):
                        selected=permutation[i:i+zero['batch_size']];n=len(selected)
                        mask=np.concatenate([np.ones(n,bool)]+[v['usable'][selected,j]for j in range(4)])
                        original=np.tile(data['depth_evidence'][selected],5)[mask]
                        dropped+=int((original&(rng.random(int(mask.sum()))<.5)).sum());count+=int(mask.sum())
                    expected.append((count,dropped))
                self.assertEqual([(h['available_views'],h['depth_dropped_views'])for h in ck['history']],expected)
                for h in ck['history']:
                    self.assertAlmostEqual(h['loss'],h['fused_positive']+.5*h['sequence_positive']+h['composition_reconstruction']+.1*h['depth_reconstruction'],places=5)
                    self.assertGreater(h['composition_reconstruction'],0.)
                    self.assertGreaterEqual(h['ema_updates'],1)
                    self.assertFalse(any(g['catastrophic_collapse'] for m in h['geometry'].values() for g in m.values()))
                self.assertGreater(ck['reconstruction_only_parents'],0)
                if name=='oral-positive':
                    self.assertTrue(all(h['depth_reconstruction']==0 and h['depth_dropped_views']==0 for h in ck['history']))
                self.assertTrue(json.loads((root/'embeddings.json').read_text())['reload_exact'])
                accounting=json.loads((root/'export/accounting.json').read_text())
                for a in accounting.values():
                    self.assertEqual(a['contigs'],len(rows));self.assertEqual(a['bp'],sum(len(s)for _,s in rows))
                self.assertEqual(bank,binding(units[name]['views']))
            self.assertEqual(before,binding(marker/'cache.json'))
            evidence=p/'evidence';evidence.mkdir();(evidence/'plan.json').write_text((p/'plan.json').read_text())
            r=pack(p/'work',evidence,p/'return');self.assertEqual(len(r['aliases']),2)


if __name__=='__main__':unittest.main()
