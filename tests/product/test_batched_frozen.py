"""Real DNA/view/token/pooling/reload paths; analytic CPU model is an explicit mock."""
from pathlib import Path
import tempfile
import unittest
import numpy as np
import torch
from dl_binner.hybrid.extract import Extractor,bounded_chunks
from dl_binner.hybrid.batched import BatchedExtractor,planned_chunks,prepare,BatchedBank
from dl_binner.hybrid.bank import Bank,model_pin
from dl_binner.multiview.views import prepare as prepare_views,load,config


class Tokenizer:
    """Deterministic tiny tokenizer with real Torch padding/masks and special tokens."""
    unk_token_id=9
    def __call__(self,seq,truncation=False,return_tensors=None,padding=False):
        if isinstance(seq,str):return {'input_ids':[1]+[{'A':3,'C':4,'G':5,'T':6}.get(s,9) for s in seq]+[2]}
        return self.pad([self(s) for s in seq],padding=True,return_tensors=return_tensors)
    def pad(self,rows,padding=True,return_tensors='pt'):
        width=max(len(z['input_ids']) for z in rows)
        return dict(input_ids=torch.tensor([z['input_ids']+[0]*(width-len(z['input_ids'])) for z in rows]),attention_mask=torch.tensor([[1]*len(z['input_ids'])+[0]*(width-len(z['input_ids'])) for z in rows]))


class AnalyticModel:
    """Padding-sensitive per-token arithmetic, without claiming DNABERT inference."""
    def __call__(self,input_ids,attention_mask,token_type_ids=None):
        return (input_ids.float().unsqueeze(-1)+torch.arange(768).float().reshape(1,1,-1)/768,)


def adapter(cls):
    x=object.__new__(cls);x.torch=torch;x.device='cpu';x.cfg={'chunk_bp':4000,'max_tokens':1024,'batch_size':2};x.tokenizer=Tokenizer();x.model=AnalyticModel();return x


class Batched(unittest.TestCase):
    def setUp(self):torch.set_num_threads(4)
    def test_original_boundaries_tokens_strands_and_vectors(self):
        rows=[('opaque-b','ACGT'*1800),('opaque-a','ANCGT'*177),('opaque-c','TTTAC'*160)]
        old=adapter(Extractor);new=adapter(BatchedExtractor)
        a,ad=old.extract(rows);b,bd=new.extract(rows)
        np.testing.assert_array_equal(a,b);self.assertEqual(ad,bd)
        for ident,dna in rows:
            p=planned_chunks(dna,new.tokenizer);q=bounded_chunks(dna,new.tokenizer)
            self.assertEqual([(a,b) for a,b,_ in p],[(a,b) for a,b,_,_ in q])
        self.assertEqual(sum(x['chunks']*2 for x in ad),sum(len(x['tokens']) for x in bd))
        with self.assertRaises(ValueError):new.extract([('same','ACGT'),('same','TTAA')])
    def test_streamed_actual_view_cache_reload_and_missing_native_admission(self):
        with tempfile.TemporaryDirectory() as t:
            r=Path(t);fasta=r/'source.fa';fasta.write_text('>opaque-A\n'+'ACGT'*900+'\n>opaque-B\n'+'AGGTT'*700+'\n>short\nACGT\n')
            prepare_views(fasta,None,r/'data',config());f=r/'data/features.npz';v=r/'data/views.npz'
            data,meta,views,vm=load(f,v);out=r/'new-bank'
            m=prepare(fasta,f,v,out,adapter(BatchedExtractor),model_pin())
            self.assertEqual(m['views'],int(data['eligible'].sum()+views['usable'].sum()))
            b=BatchedBank(out,f,v,data,meta,views,engineering=True);state=b.fit()
            x,q=b.batch(np.array([0,1]),np.array([0,1]),state);self.assertEqual(x.shape,(2,768));self.assertTrue(np.isfinite(x).all())
            with self.assertRaises(ValueError):BatchedBank(out,f,v,data,meta,views)
            with self.assertRaises(ValueError):Bank(out,f,v,data,meta,views)
            with (out/'vectors.npy').open('r+b') as stream:stream.seek(-1,2);stream.write(b'!')
            with self.assertRaises(ValueError):BatchedBank(out,f,v,data,meta,views,engineering=True)


if __name__=='__main__':unittest.main()
