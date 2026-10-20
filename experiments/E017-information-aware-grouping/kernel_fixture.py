"""Bounded synthetic array throughput fixture, never DNA/truth or community science.

Measures the actual new group/cache/audit kernels with 4,096 long cores and 8,192
short queries. Arrays are explicitly generated features and vectors, not claims
to measured biological DNA or coverage. The real tiny fixture owns FASTA/marker/
export validation. No learning is performed and no policy is selected by scores.
"""
import argparse
import json
from pathlib import Path
import time

import numpy as np


def run(output,config,threads=4):
    """Write fresh synthetic arrays, run one actual core/recruit path and readback."""
    from dl_binner.io import save_arrays,write_json,digest
    from dl_binner.information.grouping import group,policy
    from dl_binner.information.audit import review
    from dl_binner.multiview.views import config as base_config
    root=Path(output);root.mkdir(parents=True,exist_ok=False);rng=np.random.default_rng(2117)
    nc,nq,groups=4096,8192,32;n=nc+nq
    labels=np.arange(n)%groups
    latent=rng.normal(size=(groups,64));latent/=np.linalg.norm(latent,axis=1)[:,None]
    vectors=(latent[labels]+rng.normal(scale=.02,size=(n,64))).astype(np.float32)
    vectors/=np.linalg.norm(vectors,axis=1)[:,None]
    base=rng.dirichlet(np.full(136,.5),size=groups)
    tnf=(base[labels]+rng.dirichlet(np.ones(136),size=n)*.03).astype(np.float32)
    tnf/=tnf.sum(1)[:,None]
    lengths=np.r_[rng.integers(3000,20000,nc),rng.integers(500,2400,nq)].astype(np.int64)
    means=rng.integers(1,50,size=(groups,10))[labels].astype(np.float64)
    means[::19]=0
    ids=np.array([f'engineering-{i:05d}' for i in range(n)])
    f=root/'features.npz';em=root/'embeddings.npz';started=time.monotonic()
    save_arrays(f,dict(ids=ids,lengths=lengths,tnf=tnf,valid_fourmers=lengths-3,depth=means,
                zero_depth=means==0,depth_evidence=(means>0).any(1),sequence_sha256=np.array(['0'*64]*n),
                eligible=np.ones(n,bool),exclusion_reason=np.array(['']*n,dtype='U32')),
                dict(kind='features',fasta_sha256='0'*64,depth_sha256='0'*64,samples=[f'fixture-{i}' for i in range(10)],
                     min_length=500,sequence_dimensions=136,mode='synthetic engineering arrays only',
                     depth_semantics='Generated parent-depth fixture; no measured biological coverage or window variance'))
    save_arrays(em,dict(ids=ids,features=vectors,evidence=np.ones(n,bool)),
                dict(kind='embeddings',features_sha256=digest(f),metric='synthetic engineering unit sphere'))
    before=time.monotonic();group(f,em,root/'group',policy(config),base_config(),threads);group_seconds=time.monotonic()-before
    before=time.monotonic();review(f,em,root/'group',root/'audit.json');audit_seconds=time.monotonic()-before
    size=sum(p.stat().st_size for p in root.rglob('*') if p.is_file())
    write_json(root/'fixture.json',dict(status='PASS',kind='Synthetic array kernels only, no recovery/biology',
                cores=nc,queries=nq,dimensions=200,threads=threads,group_seconds=group_seconds,audit_seconds=audit_seconds,
                total_seconds=time.monotonic()-started,logical_files_bytes=size,
                caution='Mac single-size throughput includes JIT; Linux and more competing profiles may scale differently. This is no full-community affordability pass.'))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);p.add_argument('--config',type=Path,required=True);p.add_argument('--threads',type=int,default=4);a=p.parse_args();run(a.output,a.config,a.threads)
