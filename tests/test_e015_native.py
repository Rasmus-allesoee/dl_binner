"""Real tiny zero-loss, initialization, retained-cache and downstream contracts.

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
    def test_same_initialization_RNG_zero_reconstruction_gradient_and_nonzero_contrastive(self):
        import torch
        from torch.nn import functional as F
        from dl_binner.multiview.model import Encoder,multiview_loss,parent_average
        from dl_binner.model import configure_torch
        from dl_binner.multiview.views import config
        configure_torch(4);base=config();zero=base|dict(composition_reconstruction_weight=0.,depth_reconstruction_weight=0.)
        for samples in [0,10]:
            torch.manual_seed(11);a=Encoder(samples,base);after_a=torch.get_rng_state().clone()
            torch.manual_seed(11);b=Encoder(samples,zero);after_b=torch.get_rng_state().clone()
            self.assertTrue(torch.equal(after_a,after_b));self.assertEqual(list(a.state_dict()),list(b.state_dict()))
            for k in a.state_dict():self.assertTrue(torch.equal(a.state_dict()[k],b.state_dict()[k]),k)
            x=F.normalize(torch.randn(6,136),dim=1);d=torch.randn(6,samples);mask=torch.tensor([1,0,1,0,1,0],dtype=torch.bool)
            z,s=b(x,d,mask);owners=torch.tensor([0,1,2,0,1,2]);w=torch.ones(3)
            cf=multiview_loss(z,owners,.2,w);cs=multiview_loss(s,owners,.2,w)
            rc=parent_average((F.normalize(b.composition_decoder(z),dim=1)-x).square().sum(1),owners,w)
            rd=z.sum()*0 if samples==0 else F.smooth_l1_loss(b.depth_decoder(z),d)
            loss=cf+zero['sequence_loss_weight']*cs+zero['composition_reconstruction_weight']*rc+zero['depth_reconstruction_weight']*rd
            self.assertTrue(torch.equal(loss,cf+.5*cs));loss.backward()
            for name,p in b.named_parameters():
                if 'decoder' in name:self.assertIsNotNone(p.grad);self.assertEqual(float(p.grad.abs().sum()),0.,name)
            self.assertTrue(any(p.grad is not None and p.grad.abs().sum()>0 for n,p in b.named_parameters() if 'decoder'not in n))

    def test_actual_cached_two_modalities_train_exact_reload_graph_refine_export(self):
        from candidate_fixture import fixture,asset
        from dl_binner.multiview.views import config,prepare,load
        from dl_binner.candidate.markers import cache
        from e014_collect import binding
        from e015_collect import pack
        with tempfile.TemporaryDirectory() as t:
            p=Path(t);f,depth,rows=fixture(p);hmm,manifest=asset(p,f)
            marker=p/'markers';marker.mkdir();cache(f,hmm,manifest,marker,4);before=binding(marker/'cache.json')
            base=config();base.update(epochs=2,batch_size=4,sequence_hidden=16,sequence_output=8,depth_hidden=4,
                fusion_hidden=8,output=4,neighbors=5,min_bin_bp=100,min_bin_contigs=1)
            zero=base|dict(composition_reconstruction_weight=0.,depth_reconstruction_weight=0.)
            (p/'base.json').write_text(json.dumps(base));(p/'zero.json').write_text(json.dumps(zero));units={}
            for name,dep in [('E009-zero',depth),('oral-zero',None)]:
                source=p/(name+'-retained');prepare(f,dep,source,base)
                units[name]=dict(fasta=str(f),features=str(source/'features.npz'),views=str(source/'views.npz'),marker_cache=str(marker))
            plan=dict(kind='Tiny engineering only',work=str(p/'work'),units=units,threads=4,python=sys.executable,
                worker=str(REPO/'scripts/e015_control.py'),workflow_python=os.environ.get('E015_WORKFLOW_PYTHON',sys.executable),
                snakefile=str(REPO/'experiments/E015-zero-reconstruction/Snakefile'),config=str(p/'zero.json'),
                base_config=str(p/'base.json'),hmm=str(hmm),reuse_lock='tiny-owned-fixture')
            (p/'plan.json').write_text(json.dumps(plan))
            if os.environ.get('E015_WORKFLOW_PYTHON'):
                r=subprocess.run([sys.executable,'-I','-B',str(REPO/'scripts/e015_control.py'),'--plan',str(p/'plan.json'),'--workflow'],capture_output=True,text=True)
                detail='\n'.join(str(x)+'\n'+x.read_text() for x in (p/'work/logs').rglob('*.log'))
                self.assertEqual(r.returncode,0,r.stdout+r.stderr+'\nNATIVE_STAGE_LOGS\n'+detail)
                self.assertIn('13 of 13 steps (100%) done',r.stdout+r.stderr)
            for name in units:
                bank=binding(units[name]['views'])
                for stage in ([] if os.environ.get('E015_WORKFLOW_PYTHON') else ['train','embed','group','refine','export','graph-proof']):
                    r=subprocess.run([sys.executable,'-I','-B',str(REPO/'scripts/e015_control.py'),'--plan',str(p/'plan.json'),
                        '--unit',name,'--stage',stage],capture_output=True,text=True)
                    self.assertEqual(r.returncode,0,r.stdout+r.stderr)
                root=p/'work/units'/name;ck=json.loads((root/'train/checkpoint.json').read_text())
                self.assertEqual(ck['config'],zero);self.assertEqual(ck['training_views_sha256'],bank['sha256'])
                for h in ck['history']:
                    self.assertAlmostEqual(h['loss'],h['fused_contrastive']+.5*h['sequence_contrastive'],places=5)
                    self.assertGreater(h['composition_reconstruction'],0.)
                self.assertTrue(json.loads((root/'embeddings.json').read_text())['reload_exact'])
                accounting=json.loads((root/'export/accounting.json').read_text())
                for a in accounting.values():
                    self.assertEqual(a['contigs'],len(rows));self.assertEqual(a['bp'],sum(len(s)for _,s in rows))
                self.assertEqual(bank,binding(units[name]['views']))
            self.assertEqual(before,binding(marker/'cache.json'))
            evidence=p/'evidence';evidence.mkdir();(evidence/'plan.json').write_text((p/'plan.json').read_text())
            r=pack(p/'work',evidence,p/'return');self.assertEqual(len(r['aliases']),2)


if __name__=='__main__':unittest.main()
