#!/usr/bin/env python3
"""Time the real exact backend on full Oral dimensions without community labels.

Only 128 query rows are evaluated against 508,763 synthetic candidates. The
partial certificate cannot be restored as a scientific cache. Initialization,
BLAS, top-k boundary expansion and original-score reranking are timed together.
"""
import argparse,json,sys,time
from pathlib import Path
ROOT=Path(__file__).absolute().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from e024_coverage import write


def probe(output):
    """Forecast both serial Oral consumers plus unchanged downstream/collection reserve."""
    import numpy as np
    from dl_binner.discovery.exact import exact_neighbors
    from dl_binner.unified.grouping import policy
    n=508763;rng=np.random.default_rng(11);u=rng.normal(size=(n,64)).astype(np.float32)
    u/=np.linalg.norm(u,axis=1)[:,None]
    c=rng.random((n,136),dtype=np.float32);c/=np.linalg.norm(c,axis=1)[:,None]
    d=np.tanh(rng.normal(size=(n,10))).astype(np.float32);d[:191567]=0
    ids=np.array([f'opaque-{i:07d}'for i in range(n)]);lengths=rng.integers(500,10000,n,dtype=np.int64)
    data=dict(ids=ids,lengths=lengths);positive=(d!=0).any(1);scales=np.array([2.,.1,5.])
    start=time.monotonic()
    _,_,proof=exact_neighbors(data,(u,c,d),positive,scales,np.arange(n),policy(),engineering_query_count=128)
    elapsed=time.monotonic()-start
    # The first candidate-map build is deliberately charged once per measured
    # query block, making this forecast conservative. Four E009 caches are reused.
    seconds=2*elapsed*n/128*1.5+7200
    result=dict(status='PASS'if seconds<=208800 else 'FORECAST_REQUIRES_REASSESSMENT',
        full_candidate_rows=n,measured_query_rows=128,measured_seconds=elapsed,
        planning_remaining_science_seconds=seconds,planning_safety_factor=1.5,
        downstream_collection_reserve_seconds=7200,partial_engineering_certificate=proof,
        source_blind_synthetic=True,community_science_started=False,
        byte_projection=dict(conservative_complete_growth_bytes=int(3.8*1024**3),extra_cap_bytes=4*1024**3,
            compressed_cap_bytes=2*1024**3,no_quadratic_score_storage=True))
    write(output,result);print(json.dumps(result),flush=True)
    if result['status']!='PASS':raise ValueError('Measured complete schedule needs recorded covered reassessment')


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);probe(p.parse_args().output)
