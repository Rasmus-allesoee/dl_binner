"""Installed dev5 native contracts on tiny owned DNA/HMMs; no community labels."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

import numpy as np

from dl_binner.io import digest,load_arrays,save_arrays
from dl_binner.multiview import views
from candidate_fixture import fixture,asset
from fixtures import THREADS


class MultiviewContracts(unittest.TestCase):
    def test_lean_reader_preserves_original_values_ID_hash_and_corruption_refusal(self):
        from dl_binner.multiview.arrays import load_arrays as lean
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'a.npz';arrays=dict(ids=np.array(['opaque-æ','with"quote','back\\slash']),values=np.arange(15,dtype=np.float32).reshape(3,5))
            save_arrays(p,arrays,dict(kind='tiny_owned'))
            a,ma=load_arrays(p,'tiny_owned');b,mb=lean(p,'tiny_owned')
            self.assertEqual(ma,mb)
            for k in a:np.testing.assert_array_equal(a[k],b[k])
            self.assertTrue(all(v.flags.owndata for v in b.values()))
            p.write_bytes(p.read_bytes()+b'corrupt')
            with self.assertRaisesRegex(ValueError,'byte hash'):lean(p,'tiny_owned')

    def test_variable_real_crops_short_exposure_zeros_and_malformed_refusal(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);f,depth,rows=fixture(p);cfg=views.config();out=p/'features'
            views.prepare(f,depth,out,cfg);a,m,v,vm=views.load(out/'features.npz',out/'views.npz')
            self.assertEqual(m['samples'],['Z-last','A-first']);self.assertEqual(a['ids'].tolist(),[i for i,_ in rows])
            self.assertFalse(v['usable'][2].any()) # 500 bp: full-parent training only.
            self.assertTrue(v['usable'][3].any()) # 767 bp: now real positive crops.
            for i,(ident,dna) in enumerate(rows):
                for j,(start,end,s) in enumerate(views.crops(ident,dna,cfg)):
                    self.assertEqual(s,dna[start:end]);self.assertEqual(v['sequence_sha256'][i,j].decode(),hashlib.sha256(s.encode()).hexdigest())
                    np.testing.assert_array_equal(v['tnf'][i,j],views.composition(s)[0])
                if len(dna)>=512:
                    self.assertLessEqual(v['coordinates'][i,0,1],v['coordinates'][i,1,0])
            dna=rows[-3][1];self.assertNotEqual(views.crops(rows[-3][0],dna,cfg)[:2],views.crops(rows[-3][0],dna,cfg)[2:])
            reuse=p/'reuse';views.prepare(f,depth,reuse,cfg,parent_features=out/'features.npz')
            self.assertTrue(json.loads((reuse/'prepared.json').read_text())['parent_features_reused'])
            bad=dict(v);bad['usable']=~v['usable'];save_arrays(p/'bad.npz',bad,vm)
            with self.assertRaisesRegex(ValueError,'crop mask|fabricated crop'):views.load(out/'features.npz',p/'bad.npz')
            f.write_text('>duplicate\nACGT\n>duplicate\nACGT\n')
            with self.assertRaisesRegex(ValueError,'duplicate'):list(views.fasta_rows(f))

    def test_all_positive_loss_matches_two_view_NTXent_and_independent_oracle(self):
        import torch
        from dl_binner.model import nt_xent,configure_torch
        from dl_binner.multiview.model import multiview_loss
        configure_torch(THREADS);torch.manual_seed(11)
        a=torch.nn.functional.normalize(torch.randn(3,8),dim=1);b=torch.nn.functional.normalize(torch.randn(3,8),dim=1)
        z=torch.cat([a,b]).requires_grad_();owners=torch.tensor([0,1,2,0,1,2]);weights=torch.ones(3)
        loss=multiview_loss(z,owners,.2,weights)
        torch.testing.assert_close(loss,nt_xent(a,b,.2));loss.backward();self.assertTrue(torch.isfinite(z.grad).all())
        zz=torch.cat([a,b,a[:1]]);groups=torch.tensor([0,1,2,0,1,2,0]);weights=torch.tensor([.7,1.,2.])
        x=zz.numpy();g=groups.numpy();per={}
        for i in range(len(x)):
            others=[j for j in range(len(x)) if j!=i];positives=[j for j in others if g[j]==g[i]]
            logits=x@x[i]/.2;maximum=max(logits[others]);den=maximum+np.log(np.exp(logits[others]-maximum).sum())
            per.setdefault(int(g[i]),[]).append(float(np.mean([den-logits[j] for j in positives])))
        oracle=sum(np.mean(per[k])*weights[k].item() for k in per)/weights.sum().item()
        self.assertAlmostEqual(multiview_loss(zz,groups,.2,weights).item(),oracle,places=5)
        self.assertEqual(multiview_loss(a,torch.arange(3),.2,torch.ones(3)).item(),0)

    def test_actual_installed_train_reload_native_marker_CPM_refine_and_complete_exports(self):
        # Each native stage is a process: Torch and LLVM/OpenMP graph libraries
        # must not be loaded together in the caller or hidden with workarounds.
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);f,depth,rows=fixture(root);hmm,manifest=asset(root,f)
            cfg=views.config();cfg.update(epochs=2,batch_size=4,sequence_hidden=16,sequence_output=8,
                depth_hidden=4,fusion_hidden=8,output=4,neighbors=5,min_bin_bp=100,min_bin_contigs=1)
            cp=root/'cfg.json';cp.write_text(json.dumps(cfg));cache=root/'markers'
            def call(stage,out,**args):
                cmd=[sys.executable,'-I','-B','-m','dl_binner','--threads',str(THREADS),'multiview-stage',
                     '--stage',stage,'--output',str(out),'--config',str(cp)]
                for k,v in args.items():cmd += ['--'+k.replace('_','-'),str(v)]
                result=subprocess.run(cmd,capture_output=True,text=True,cwd=root)
                (root/(str(stage)+'-'+out.name+'.log')).write_text(result.stdout+result.stderr)
                self.assertEqual(result.returncode,0,result.stdout+result.stderr)
            call('markers',cache,fasta=f,marker_hmm=hmm,marker_manifest=manifest)
            marker_hash=digest(cache/'cache.json')
            for mode,dp in [('depth',depth),('sequence',None)]:
                p=root/mode;p.mkdir();kw=dict(fasta=f)
                if dp:kw['depth']=dp
                call('features',p/'features',**kw);features=p/'features/features.npz';bank=p/'features/views.npz'
                call('train',p/'train',features=features,views=bank)
                receipt=json.loads((p/'train/checkpoint.json').read_text());data,_=views.load(features)
                self.assertTrue(all(h['parents_seen']==int(data['eligible'].sum()) for h in receipt['history']))
                self.assertGreater(receipt['training_parents'],2)
                if mode=='sequence':self.assertTrue(all(h['depth_reconstruction']==0 and h['depth_dropped_views']==0 for h in receipt['history']))
                else:self.assertTrue(any(h['depth_dropped_views']>0 for h in receipt['history']))
                call('embed',p/'embeddings.npz',features=features,checkpoint=p/'train/checkpoint.pt')
                v,vm=load_arrays(p/'embeddings.npz','embeddings');self.assertTrue(vm['reload_exact'])
                np.testing.assert_allclose(np.linalg.norm(v['features'][v['evidence']],axis=1),1,atol=1e-6)
                call('group',p/'group',features=features,embeddings=p/'embeddings.npz')
                parent=p/'group/partition.json';partition=json.loads(parent.read_text());graph,gm=load_arrays(p/'group/graph.npz','candidate_sparse_graph')
                self.assertAlmostEqual(partition['objective']['gamma'],float(np.median(graph['weights']))/5)
                self.assertEqual(partition['embedding_sha256'],digest(p/'embeddings.npz'))
                call('refine',p/'refine',features=features,embeddings=p/'embeddings.npz',parent=parent,marker_cache=cache,fasta=f,marker_hmm=hmm)
                for label,part in [('pre',parent),('post',p/'refine/partition.json')]:
                    call('export',p/label,features=features,parent=part,fasta=f)
                    from dl_binner.accounting import summarize_arm
                    accounting=summarize_arm(features,p/label)[0]
                    self.assertEqual(accounting['contigs'],len(rows));self.assertEqual(accounting['bp'],sum(len(s) for _,s in rows))
                self.assertEqual(digest(cache/'cache.json'),marker_hash)
                # Corruption must be refused by the actual independent reloader.
                saved=(p/'train/checkpoint.pt').read_bytes();(p/'train/checkpoint.pt').write_bytes(saved+b'broken')
                result=subprocess.run([sys.executable,'-I','-B','-m','dl_binner','multiview-stage','--stage','embed',
                    '--features',str(features),'--checkpoint',str(p/'train/checkpoint.pt'),'--output',str(p/'bad.npz')],capture_output=True,text=True)
                self.assertNotEqual(result.returncode,0);self.assertIn('checkpoint/input bytes differ',result.stderr)
