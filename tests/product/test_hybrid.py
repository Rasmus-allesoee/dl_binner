"""Installed hybrid contracts on own DNA; fake extractor is explicitly isolated.

The fake supplies deterministic numeric vectors only for cache reader tests.
Separate E021 journals must establish actual pinned transformer inference.
"""
import copy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

import numpy as np
import torch
from torch.nn import functional as F

from dl_binner.hybrid.bank import prepare, Bank, policy, model_pin
from dl_binner.hybrid.extract import bounded_chunks, reverse_complement, reference_attention
from dl_binner.hybrid.model import config, initialize, parent_evidence
from dl_binner.context.model import initialize as anchor
from dl_binner.context.tokens import prepare as tokens
from dl_binner.multiview.views import prepare as views, config as base_config, load
from dl_binner.multiview.positive import update_target
from dl_binner.model import configure_torch


class FakeExtractor:
    """Mock only external native inference; deterministic DNA-specific 768D vectors."""
    def extract(self,rows):
        out=[];details=[]
        for ident,dna in rows:
            rng=np.random.default_rng(int(hashlib.sha256(dna.encode()).hexdigest()[:16],16));out.append(rng.normal(size=768).astype(np.float32))
            details.append(dict(id=ident,bp=len(dna),chunks=1,tokens=[len(dna)+2]*2,unknown_tokens=0,intervals=[[0,len(dna)]]))
        return np.stack(out),details


class Hybrid(unittest.TestCase):
    def setUp(self):configure_torch(4)

    def test_view_cache_real_DNA_coordinates_masks_and_refusal(self):
        with tempfile.TemporaryDirectory()as tmp:
            r=Path(tmp);f=r/'data.fa';f.write_text('>opaque-z\n'+'ACGT'*701+'\n>opaque-a\n'+'AGCT'*126+'\n>short\nACG\n>unknown\n'+'N'*900+'\n')
            views(f,None,r/'data',base_config());feat,view=r/'data/features.npz',r/'data/views.npz';data,meta,v,vm=load(feat,view)
            prepare(f,feat,view,r/'glm',FakeExtractor(),model_pin())
            b=Bank(r/'glm',feat,view,data,meta,v);self.assertFalse(b.values.flags.writeable);self.assertEqual(b.rows.tolist(),[0,1]);self.assertEqual(b.usable[1].tolist(),[True,False,False,False,False])
            state=b.fit();x,q=b.batch(np.array([0,1]),np.array([0,0]),state);self.assertTrue(np.isfinite(x).all());self.assertTrue(np.allclose(np.linalg.norm(x,axis=1),1))
            with self.assertRaisesRegex(ValueError,'Unavailable'):b.batch(np.array([1]),np.array([1]),state)
            d=json.loads((r/'glm/bank.json').read_text());self.assertEqual(d['views'],1+int(v['usable'][0].sum())+1)
            with(r/'glm/vectors.npy').open('r+b')as out:out.seek(-1,2);out.write(b'!')
            with self.assertRaisesRegex(ValueError,'corrupt'):Bank(r/'glm',feat,view,data,meta,v)
            self.assertFalse((r/'glm/fallback').exists())

    def test_canonical_exact_chunks_no_truncation_and_token_overflow(self):
        tokenizer=lambda s,**kwargs:dict(input_ids=list(range(len(s)+2)))
        dna='ACGTRYSWKMBDHVN'*17
        a=bounded_chunks(dna,tokenizer,73,41);b=bounded_chunks(reverse_complement(dna),tokenizer,73,41)
        self.assertEqual(a,b);self.assertEqual(sum(y-x for x,y,_,_ in a),len(dna));self.assertTrue(all(n<=41 for _,_,_,n in a));self.assertEqual(a[0][0],0);self.assertEqual(a[-1][1],len(dna))
        with self.assertRaises(ValueError):bounded_chunks('A-',tokenizer)
        with self.assertRaises(ValueError):bounded_chunks('AC',tokenizer,max_tokens=2)

    def test_reference_backend_refuses_uninventoried_attention(self):
        class WrongModel:
            config=type('Config',(),dict(num_hidden_layers=12))()
            def modules(self):return []
        with self.assertRaisesRegex(ValueError,'layer inventory'):reference_attention(WrongModel(),model_pin())

    def test_GLM_only_evidence_is_retained_without_fabricating_missing_signal(self):
        z=np.zeros((2,136));f=np.zeros((2,768));f[0,0]=1
        self.assertEqual(parent_evidence(z,np.zeros(2,bool),np.zeros(2,bool),f).tolist(),[True,False])

    def test_initial_anchor_gradient_stopped_target_EMA_and_missing_depth(self):
        cfg=config();torch.manual_seed(11);old,ot,op=anchor(10,{k:v for k,v in cfg.items()if k!='hybrid'})
        torch.manual_seed(11);model,target,predictors=initialize(10,cfg)
        for k,v in old.state_dict().items():self.assertTrue(torch.equal(v,model.state_dict()[k]),k)
        for x,y in zip(op.parameters(),predictors.parameters()):self.assertTrue(torch.equal(x,y))
        self.assertTrue(all(not p.requires_grad for p in target.parameters()))
        mask=torch.tensor([True,False]*4)
        args=[F.normalize(torch.randn(8,136),dim=1),torch.randn(8,10),mask,torch.randn(8,8,136),torch.rand(8,8,3),torch.ones(8,8,dtype=torch.bool)]
        extra=[F.normalize(torch.randn(8,768),dim=1),torch.rand(8,2)]
        self.assertTrue(torch.equal(old(*args)[0],model(*args,*extra)[0]))
        opt=torch.optim.AdamW(model.parameters(),lr=.001)
        for i in range(2):
            opt.zero_grad();loss=(model(*args,*extra)[0]-F.normalize(torch.randn(8,cfg['output']),dim=1)).square().sum();loss.backward()
            self.assertGreater(float(model.frozen_residual.weight.grad.abs().sum()),0)
            if i:self.assertGreater(float(model.frozen_branch[0].weight.grad.abs().sum()),0)
            self.assertTrue(all(p.grad is None for p in target.parameters()));opt.step()
        before=copy.deepcopy(target.state_dict());update_target(model,target,.9)
        self.assertTrue(any(not torch.equal(before[k],v)for k,v in target.state_dict().items()))
        changed=list(args);changed[1]=args[1].clone();changed[1][~mask]=10000
        self.assertTrue(torch.equal(model(*args,*extra)[0],model(*changed,*extra)[0]))
        self.assertTrue(torch.allclose(torch.linalg.vector_norm(model(*args,*extra)[0],dim=1),torch.ones(8),atol=1e-6))
        with self.assertRaisesRegex(ValueError,'frozen'):model(*args,extra[0][:,:7],extra[1])


if __name__=='__main__':unittest.main()
