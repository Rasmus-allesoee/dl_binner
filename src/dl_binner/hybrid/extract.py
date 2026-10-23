"""Hash-pinned frozen CPU/CUDA DNABERT-S adapter; never download or tune weights."""
import hashlib
import json
from pathlib import Path

from ..io import digest
from .bank import policy,model_pin

RC=str.maketrans('ACGTRYSWKMBDHVN','TGCAYRSWMKVHDBN')


def reverse_complement(dna):
    """Preserve validated IUPAC ambiguity under strand reversal."""
    if not dna or set(dna)-set('ACGTRYSWKMBDHVN'):raise ValueError('Nonempty uppercase IUPAC DNA required')
    return dna.translate(RC)[::-1]


def bounded_chunks(dna,tokenizer,max_bp=4000,max_tokens=1024):
    """Cover canonical view once; recursively split token overflow without truncation."""
    dna=min(dna,reverse_complement(dna));pieces=[]
    def split(a,b):
        seq=dna[a:b];count=max(len(tokenizer(s,truncation=False)['input_ids'])for s in (seq,reverse_complement(seq)))
        if count<=max_tokens:pieces.append((a,b,seq,count))
        elif b-a>1:
            mid=(a+b)//2;split(a,mid);split(mid,b)
        else:raise ValueError('Single base exceeds token budget')
    if max_bp<1 or max_tokens<3:raise ValueError('Invalid frozen chunk limits')
    for a in range(0,len(dna),max_bp):split(a,min(a+max_bp,len(dna)))
    if ''.join(p[2]for p in pieces)!=dna:raise ValueError('Frozen chunk coverage differs')
    return pieces


def reference_attention(model,pin):
    """Select the pinned author's existing float32 Torch attention explicitly.

    Its optional Triton branch casts float32 QKV/bias to float16. That is not
    this frozen reference recipe. No author file, module stub or weights change;
    selecting its existing fallback preserves the already tested CPU mathematics.
    """
    import importlib
    selected={};layers=0
    for layer in model.modules():
        if type(layer).__name__!='BertUnpadSelfAttention':continue
        module=importlib.import_module(type(layer).__module__);source=Path(module.__file__)
        expected=pin['files']['bert_layers.py']
        if source.stat().st_size!=expected['bytes']or digest(source)!=expected['sha256']:raise ValueError('Dynamic pinned attention source differs')
        if not hasattr(module,'flash_attn_qkvpacked_func'):raise ValueError('Published reference attention selector missing')
        module.flash_attn_qkvpacked_func=None;selected[str(source)]=expected['sha256'];layers+=1
    if layers!=model.config.num_hidden_layers or not layers:raise ValueError('Pinned reference attention layer inventory differs')
    return dict(backend='pinned_author_torch_float32_reference',layers=layers,sources=selected,source_files_unchanged=True)


class Extractor:
    """Load verified local custom code/tokenizer/weights and freeze every parameter.

    CUDA is an explicit future execution option, not an automatic fallback or a
    proven compatible runtime. Device choice never changes pooling, chunks or dtype.
    """
    def __init__(self,model_dir,pin_path,device='cpu'):
        p=Path(model_dir);self.pin=json.loads(Path(pin_path).read_text());self.cfg=policy()
        if self.pin!=model_pin():raise ValueError('Frozen model revision differs')
        for name,b in self.pin['files'].items():
            f=p/name
            if f.is_symlink()or not f.is_file()or f.stat().st_size!=b['bytes']or digest(f)!=b['sha256']:raise ValueError('Frozen model bytes differ: '+name)
        if device not in ['cpu','cuda']:raise ValueError('Explicit CPU/CUDA device required')
        import torch
        from transformers import AutoModel,AutoTokenizer
        self.torch=torch;self.device=device
        self.tokenizer=AutoTokenizer.from_pretrained(str(p),trust_remote_code=True,local_files_only=True)
        self.model=AutoModel.from_pretrained(str(p),trust_remote_code=True,local_files_only=True).to(device).eval()
        self.attention_backend=reference_attention(self.model,self.pin)
        from ..io import emit
        emit('hybrid_reference_attention',**self.attention_backend)
        self.model.requires_grad_(False)
        if any(x.requires_grad for x in self.model.parameters()):raise ValueError('Backbone not frozen')

    def pool(self,sequences):
        """Mean all attended tokens including specials; mask padding explicitly."""
        torch=self.torch;t=self.tokenizer(sequences,return_tensors='pt',padding=True,truncation=False)
        if t['input_ids'].shape[1]>self.cfg['max_tokens']:raise ValueError('Unchunked token overflow')
        t={k:v.to(self.device)for k,v in t.items()}
        with torch.inference_mode():
            h=self.model(**t)[0];mask=t['attention_mask'].unsqueeze(-1);x=(h*mask).sum(1)/mask.sum(1)
        if not torch.isfinite(x).all():raise ValueError('Nonfinite frozen sequence embedding')
        return x.cpu().numpy()

    def extract(self,rows):
        """Extract view-exact both-strand/bp-weighted vectors and complete chunk details."""
        import numpy as np
        if len({x[0]for x in rows})!=len(rows):raise ValueError('Duplicate extraction IDs')
        values=[];details=[]
        for ident,dna in rows:
            parts=bounded_chunks(dna,self.tokenizer,self.cfg['chunk_bp'],self.cfg['max_tokens'])
            pieces=[s for _,_,seq,_ in parts for s in (seq,reverse_complement(seq))]
            ids=[self.tokenizer(s,truncation=False)['input_ids']for s in pieces]
            encoded=np.concatenate([self.pool(pieces[a:a+self.cfg['batch_size']])for a in range(0,len(pieces),self.cfg['batch_size'])])
            weights=np.asarray([b-a for a,b,_,_ in parts],np.float64)
            values.append(np.average(encoded.reshape(len(parts),2,768).mean(1),axis=0,weights=weights).astype(np.float32))
            details.append(dict(id=ident,bp=len(dna),chunks=len(parts),tokens=list(map(len,ids)),unknown_tokens=sum(z.count(self.tokenizer.unk_token_id)for z in ids),intervals=[[a,b]for a,b,_,_ in parts]))
        return np.stack(values),details
