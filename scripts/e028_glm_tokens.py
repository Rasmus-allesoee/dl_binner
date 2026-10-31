#!/usr/bin/env python3
"""Verify retained published tokenizer + real CPU pooling on an analytic model.

No download, DNABERT forward, native GPU acceptance or community DNA is involved.
The tokenizer/source identity is real; the model is explicitly synthetic.
"""
import argparse,json,os,sys
from pathlib import Path
ROOT=Path(__file__).absolute().parents[1]
sys.path[:0]=[str(ROOT/'scripts'),str(ROOT/'tests/product')]
from e024_coverage import binding,write


def run(model_dir,output):
    """Compare exact recursive chunk exposure, tokens, QC and pooling across recipes."""
    os.environ['TOKENIZERS_PARALLELISM']='false';os.environ['RAYON_NUM_THREADS']='4'
    from transformers import AutoTokenizer
    from dl_binner.hybrid.bank import model_pin
    from dl_binner.hybrid.extract import Extractor
    from dl_binner.hybrid.batched import BatchedExtractor,execution_policy
    from test_batched_frozen import adapter
    pin=model_pin();files={}
    for name,b in pin['files'].items():
        if name.startswith('tokenizer') or name=='special_tokens_map.json':
            if binding(Path(model_dir)/name)!={k:b[k] for k in ['bytes','sha256']}:raise ValueError('Retained published tokenizer differs')
            files[name]=b
    tokenizer=AutoTokenizer.from_pretrained(str(Path(model_dir).absolute()),local_files_only=True,trust_remote_code=False)
    old=adapter(Extractor);new=adapter(BatchedExtractor);old.tokenizer=new.tokenizer=tokenizer
    rows=[('opaque-real-tokenizer-A','ACGT'*2100),('opaque-real-tokenizer-B','ANCGTRYSWKMBDHVN'*91),('opaque-real-tokenizer-C','GGTCA'*170)]
    a,ad=old.extract(rows);b,bd=new.extract(rows)
    import numpy as np
    np.testing.assert_array_equal(a,b)
    if ad!=bd:raise ValueError('Actual published token/chunk/QC semantics differ')
    write(output,dict(status='PASS_RETAINED_TOKENIZER_REAL_POOL_MOCK_MODEL',tokenizer_files=files,
        execution=execution_policy(),details=bd,pooling_max_abs_difference=float(np.max(np.abs(a-b))),
        native_DNABERT_or_GPU_forward=False,native_numerical_throughput_admission=False,network_acquisition=False))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--model-dir',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();run(a.model_dir,a.output)
