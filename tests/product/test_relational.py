"""Actual installed readers/loss/learning/export contracts on own tiny evidence."""
import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

import numpy as np
import torch
from torch import nn
from torch.nn import functional as F

from relational_fixture import fixture, NumericExtractor
from dl_binner.relational.evidence import restore
from dl_binner.relational.pairs import policy, prepare, load_pairs, protein_near
from dl_binner.relational.model import config, initialize, signed_loss, pair_epoch, train, embed
from dl_binner.model import configure_torch
from dl_binner.io import digest


class Relational(unittest.TestCase):
    def setUp(self): configure_torch(4)

    def make_pairs(self, f, name='pairs'):
        """Execute real cache/profile/sparse readers and source-blind selection."""
        out = f['root']/name
        prepare(f['features'], f['embeddings'], f['graph'], f['markers'], f['hmm'], out)
        return out

    def test_actual_sparse_cache_mapping_conflicts_and_readonly_inputs(self):
        with tempfile.TemporaryDirectory() as folder:
            f=fixture(folder); originals={str(p):digest(p)for p in f['markers'].iterdir()}
            original_vectors=digest(f['embeddings']); p=self.make_pairs(f); a,m=load_pairs(p,f['features'])
            self.assertEqual(m['full_contigs'],35); self.assertEqual(m['samples'],f['metadata']['samples'])
            self.assertGreater(int((a['sign']==1).sum()),0); self.assertGreater(int((a['sign']==-1).sum()),0)
            self.assertLessEqual(m['summary']['degree_max'],4); self.assertFalse(m['truth_accessed'])
            self.assertEqual(original_vectors,digest(f['embeddings']))
            self.assertEqual(originals,{str(p):digest(p)for p in f['markers'].iterdir()})
            self.assertFalse(set(f['data']['ids'][np.r_[a['left'],a['right']]]) & {'short','marker-negative','no-signal'})
            with self.assertRaises(FileExistsError): self.make_pairs(f)
            with (p/'pairs.npz').open('r+b')as s:s.seek(-1,2);s.write(b'!')
            with self.assertRaisesRegex(ValueError,'Corrupt'):load_pairs(p,f['features'])

    def test_reliability_partial_overlap_multifamily_and_protein_veto(self):
        with tempfile.TemporaryDirectory() as folder:
            f=fixture(folder);f['genes']['gene-0']['partial_begin']=True
            f['domains'][1]['score']=25.
            ambiguous=dict(f['domains'][2],marker='family-3');f['domains'].append(ambiguous)
            f['domains'].append(dict(f['domains'][3])) # exact physical overlap deduplicates
            f['seal']();q,seq=restore(f['markers'],f['hmm'],f['data'],f['metadata'],policy())
            reasons=[r for x in q['withheld']for r in x['reasons']]
            self.assertIn('partial_gene',reasons);self.assertIn('near_trusted_cutoff',reasons)
            self.assertIn('multi_family_protein',reasons);self.assertGreater(len(q['consolidated']),0)
            self.assertTrue(protein_near('ACDEFGHIKLMN','ACDEFGHIKLMN',policy()))
            self.assertFalse(protein_near('ACDEFGHIKLMN','WWWWWWWWWWWW',policy()))
            f['domains'][0]['protein_to']=999;f['seal']=lambda:None
            # Corruption is refused before any best-effort coordinate repair.
            (f['markers']/'domains.json').write_text(json.dumps(f['domains']))
            with self.assertRaisesRegex(ValueError,'Corrupt'):restore(f['markers'],f['hmm'],f['data'],f['metadata'],policy())

    def test_missing_depth_abstains_and_retains_every_parent(self):
        with tempfile.TemporaryDirectory() as folder:
            f=fixture(folder,measured=False);p=self.make_pairs(f);a,m=load_pairs(p,f['features'])
            self.assertEqual(len(a['left']),0);self.assertEqual(m['summary']['calibration']['status'],'ABSTAIN_MISSING_MEASURED_CONTEXT')
            self.assertTrue(np.array_equal(a['ids'],f['data']['ids']));self.assertEqual(m['samples'],[])

    def test_strict_policy_types_and_unpermitted_tuning(self):
        cfg=policy();cfg['margin_bits']=9
        with self.assertRaises(ValueError):policy(cfg)
        cfg=policy();cfg['version']=True
        with self.assertRaises(ValueError):policy(cfg)
        cfg=policy();cfg['loss_weight']=0;self.assertEqual(policy(cfg)['loss_weight'],0)

    def test_signed_gradient_stopped_targets_confidence_and_margin(self):
        torch.manual_seed(11)
        online=[F.normalize(torch.randn(3,2,8),dim=-1).detach().requires_grad_()for _ in range(2)]
        target=[x.detach().clone().requires_grad_()for x in online];heads=[nn.Linear(8,8,bias=False)for _ in range(2)]
        signs=torch.tensor([1,-1,1],dtype=torch.int8);weights=torch.tensor([1.,.5,.1])
        a,b=signed_loss(online,target,heads,signs,weights,.2);(a+b).backward()
        self.assertTrue(all(x.grad is not None and torch.isfinite(x.grad).all()for x in online))
        self.assertTrue(all(x.grad is None for x in target));self.assertGreater(float(a),0)
        lo,_=signed_loss(online,target,heads,signs,weights*.5,.2)
        self.assertAlmostEqual(float(lo),float(a)*.5,6)
        schedule=pair_epoch(37,5,policy(),0)
        self.assertEqual(sorted(np.concatenate(schedule).tolist()),list(range(37)))
        self.assertTrue(all(len(x)<=256 for x in schedule))

    def test_negative_hinge_moves_similar_endpoints_apart(self):
        x=torch.tensor([[[1.,0.],[.9,.4358899]]],requires_grad=True)
        x=F.normalize(x,dim=-1);x.retain_grad()
        p,n=signed_loss([x,x],[x.detach(),x.detach()],[nn.Identity(),nn.Identity()],torch.tensor([-1]),torch.ones(1),.2)
        n.backward();self.assertGreater(float(n),0);self.assertGreater(float(x.grad[0,0,1]),0)
        self.assertEqual(float(p),0)

    def test_context_only_no_depth_training_reload_keeps_all_DNA(self):
        with tempfile.TemporaryDirectory()as folder:
            f=fixture(folder,measured=False);p=self.make_pairs(f)
            cfg=config(frozen=False);cfg.update(min_bin_bp=1,min_bin_contigs=1)
            train(f['features'],f['views'],f['tokens'],None,p,f['root']/'train-context',cfg,4)
            embed(f['features'],f['views'],f['tokens'],None,p,f['root']/'train-context/checkpoint.pt',f['root']/'context.npz',4)
            from dl_binner.multiview.arrays import load_arrays
            a,m=load_arrays(f['root']/'context.npz','embeddings')
            self.assertTrue(m['reload_exact']);self.assertEqual(a['ids'].tolist(),f['data']['ids'].tolist())
            h=json.loads((f['root']/'train-context/checkpoint.json').read_text())['history']
            self.assertTrue(all(x['relation_pairs_exposed']==0 for x in h))

    def test_initialization_and_RNG_match_both_immutable_encoders(self):
        from dl_binner.context.model import initialize as context
        from dl_binner.hybrid.model import initialize as hybrid
        for frozen,base in [(False,context),(True,hybrid)]:
            cfg=config(frozen=frozen);torch.manual_seed(11);old=base(10,cfg);rng=torch.get_rng_state()
            torch.manual_seed(11);new=initialize(10,cfg)
            self.assertTrue(torch.equal(rng,torch.get_rng_state()))
            for a,b in zip(old,new):
                for key,value in a.state_dict().items():self.assertTrue(torch.equal(value,b.state_dict()[key]),key)

    def test_actual_installed_CLI_outside_checkout_and_truth_refusal(self):
        with tempfile.TemporaryDirectory() as folder:
            r=subprocess.run([sys.executable,'-I','-B','-m','dl_binner','relation-stage','--help'],cwd=folder,capture_output=True,text=True)
            self.assertEqual(r.returncode,0,r.stderr);self.assertIn('--pairs',r.stdout)
            r=subprocess.run([sys.executable,'-I','-B',str(Path(sys.executable).parent/'dl-binner'),'relation-stage','--help'],cwd=folder,capture_output=True,text=True)
            self.assertEqual(r.returncode,0,r.stderr)
            r=subprocess.run([sys.executable,'-I','-B','-m','dl_binner','relation-stage','--stage','train','--output','unused','--truth','x'],cwd=folder,capture_output=True,text=True)
            self.assertNotEqual(r.returncode,0);self.assertIn('unrecognized arguments: --truth',r.stderr)

    def test_zero_weight_anchor_exact_and_active_twenty_epoch_reload_export(self):
        from dl_binner.hybrid.bank import prepare as frozen_bank,model_pin
        from dl_binner.hybrid.model import train as anchor_train
        from dl_binner.multiview.downstream import group,refine
        from dl_binner.clustering import export
        from dl_binner.accounting import summarize_arm
        from dl_binner.multiview.arrays import load_arrays
        with tempfile.TemporaryDirectory() as folder:
            f=fixture(folder);p=self.make_pairs(f)
            frozen_bank(f['fasta'],f['features'],f['views'],f['root']/'frozen',NumericExtractor(),model_pin())
            cfg=config();cfg.update(min_bin_bp=1,min_bin_contigs=1)
            zero=copy.deepcopy(cfg);zero['relational']['loss_weight']=0
            anchor_cfg={k:v for k,v in cfg.items()if k!='relational'}
            anchor_train(f['features'],f['views'],f['tokens'],f['root']/'frozen',f['root']/'anchor-train',anchor_cfg,4)
            train(f['features'],f['views'],f['tokens'],f['root']/'frozen',p,f['root']/'zero',zero,4)
            left=torch.load(f['root']/'anchor-train/checkpoint.pt',weights_only=True)
            right=torch.load(f['root']/'zero/checkpoint.pt',weights_only=True)
            for key in ['model_state','target_state','predictor_state']:
                for name,value in left[key].items():self.assertTrue(torch.equal(value,right[key][name]),key+'/'+name)
            train(f['features'],f['views'],f['tokens'],f['root']/'frozen',p,f['root']/'active',cfg,4)
            embed(f['features'],f['views'],f['tokens'],f['root']/'frozen',p,f['root']/'active/checkpoint.pt',f['root']/'new.npz',4)
            result,meta=load_arrays(f['root']/'new.npz','embeddings');self.assertTrue(meta['reload_exact'])
            h=json.loads((f['root']/'active/checkpoint.json').read_text())['history']
            self.assertEqual(len(h),20);self.assertTrue(all(x['parents_seen']==int(f['data']['eligible'].sum())for x in h))
            self.assertEqual(h[0]['relation_weight'],0);self.assertEqual(h[4]['relation_weight'],.1)
            self.assertGreater(h[-1]['relation_pairs_exposed'],0)
            self.assertTrue(any(not torch.equal(v,torch.load(f['root']/'active/checkpoint.pt',weights_only=True)['model_state'][k])for k,v in right['model_state'].items()))
            group(f['root']/'new.npz',f['features'],f['root']/'new-group',f['cfg'],4)
            refine(f['features'],f['root']/'new.npz',f['root']/'new-group/partition.json',f['markers'],f['fasta'],f['hmm'],f['root']/'refine',f['cfg'])
            for name,partition in [('pre',f['root']/'new-group/partition.json'),('post',f['root']/'refine/partition.json')]:
                export(f['features'],partition,f['fasta'],f['root']/name)
                counts=summarize_arm(f['features'],f['root']/name)[0]
                self.assertEqual(counts['contigs'],len(f['data']['ids']))


if __name__=='__main__':unittest.main()
