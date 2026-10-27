#!/usr/bin/env python3
"""Audit retained Oral GLM workload/cutoff alternatives without model execution.

Reads the accepted FASTA/parent cache and replays only its deterministic crop
coordinates/availability for costing. No feature/crop bank, embedding, grouping
or score is produced. Full 500-bp view/bp totals must match the passed E021 Linux
reader. Native token/chunk/time observations are retained measurements; full-bank
tokens and changed-cutoff runtime are explicitly extrapolations, not new inference.
"""
import argparse
from collections import defaultdict
import hashlib
import json
from pathlib import Path
import re
import sys

ROOT=Path(__file__).absolute().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'scripts')]
import numpy as np
from e024_coverage import binding,write
from dl_binner.multiview.views import fasta_rows,crops


def audit(output):
    """Return exact eligible length/view/base counts and measured-source projections."""
    base=ROOT/'artifacts/e014-multiview-reconstruction'
    fasta=base/'model-input-v1/oral.fna'
    cache=base/'inspection-20261019/verified/work/units/oral-dev5/features/features.npz'
    meta=json.loads(cache.with_suffix('.json').read_text())
    view_meta=json.loads((cache.parent/'views.json').read_text())
    throughput=ROOT/'artifacts/e021-portable-admission/20261024T183844Z/native-v5-full-GPU-throughput.json'
    native=json.loads(throughput.read_text())['units']['oral-hybrid']
    if binding(cache)['sha256'] != view_meta['parent_features_sha256'] or binding(fasta)['sha256'] != meta['fasta_sha256']:
        raise ValueError('Original retained input byte contract differs')
    with np.load(cache,allow_pickle=False) as a:
        ids,lengths,eligible,shas=[a[k] for k in ['ids','lengths','eligible','sequence_sha256']]
    cutoffs=[500,1000,1500,2000]
    counts={c:dict(parents=0,parent_bp=0,available_views=0,exposed_bp=0,minimum_4000bp_chunks=0) for c in cutoffs}
    bins={c:defaultdict(lambda:dict(views=0,bp=0)) for c in cutoffs}
    strata={(s['view'],s['minimum_bp'],s['maximum_bp_exclusive']):s for s in native['strata']}
    seen=0
    for i,(ident,dna) in enumerate(fasta_rows(fasta)):
        if ident != ids[i] or len(dna) != lengths[i] or hashlib.sha256(dna.encode()).hexdigest() != shas[i]:
            raise ValueError('Cost audit DNA/opaque-ID axis differs')
        seen+=1
        if not eligible[i]:continue
        views=[(0,len(dna))]
        hashes=set()
        for j,(a,b,seq) in enumerate(crops(ident,dna,view_meta['policy']),1):
            h=hashlib.sha256(seq.encode()).digest()
            if re.search('[ACGT]{4}',seq) and h not in hashes:views.append((j,b-a))
            hashes.add(h)
        for cutoff in cutoffs:
            if len(dna)<cutoff:continue
            r=counts[cutoff];r['parents']+=1;r['parent_bp']+=len(dna)
            r['available_views']+=len(views);r['exposed_bp']+=sum(n for _,n in views)
            r['minimum_4000bp_chunks']+=sum((n+3999)//4000 for _,n in views)
            for view,n in views:
                keys=[key for key in strata if key[0]==view and key[1]<=n<key[2]]
                if len(keys)!=1:raise ValueError('Native cost-stratum join differs')
                key=keys[0];bins[cutoff][key]['views']+=1;bins[cutoff][key]['bp']+=n
        if seen%100000==0:print('E024_COST_METADATA_PARENTS',seen,flush=True)
    if seen!=len(ids) or counts[500]['parents']!=native['eligible'] or counts[500]['available_views']!=native['available_views'] or counts[500]['exposed_bp']!=native['exposed_bp']:
        raise ValueError('Replayed cost metadata does not equal accepted full-bank view/bp totals')
    for cutoff in cutoffs:
        r=counts[cutoff];tokens=seconds=0
        observed_tokens=observed_chunks=observed_views=0
        for key,z in bins[cutoff].items():
            s=strata[key];obs=s['observations']
            # Preserve the native label-free stratum recipe's measured upper
            # forecast, scaled by actual included view counts, not truth scores.
            seconds+=s['planning_upper_seconds']*z['views']/s['views']
            tokens+=z['bp']*sum(o['tokens'] for o in obs)/sum(o['end']-o['start'] for o in obs)
            observed_tokens+=sum(o['tokens'] for o in obs)
            observed_chunks+=sum(o['chunks'] for o in obs)
            observed_views+=len(obs)
        r.update(GPU_seconds_planning_projection=seconds,forward_tokens_projection=tokens,
                 native_sample_forward_tokens=observed_tokens,native_sample_chunks=observed_chunks,
                 native_sample_views=observed_views,
                 fixed_five_slot_vector_bytes=r['parents']*5*768*4,
                 view_fraction= r['available_views']/counts[500]['available_views'],
                 exposure_fraction=r['exposed_bp']/counts[500]['exposed_bp'],
                 parent_bp_fraction_of_full_GSA=r['parent_bp']/int(lengths.sum()),
                 excluded_original_records=len(ids)-r['parents'],
                 excluded_original_bp=int(lengths.sum())-r['parent_bp'])
    result=dict(kind='E024 exact retained-DNA length/view cost audit',status='PASS',
                inputs=dict(fasta=binding(fasta),features=binding(cache),view_metadata=binding(cache.parent/'views.json'),
                            native_stratum_timing=binding(throughput)),full_contigs=len(ids),full_bp=int(lengths.sum()),
                cutoffs={str(c):v for c,v in counts.items()},
                exact='Parent counts/bp, available frozen-policy views/exposed bp and minimum bp chunks; 500bp totals independently agree with accepted Linux reader',
                estimated='Full tokens and changed-cutoff time use actual native sampled token/chunk/timing observations; recursive token splits are not recomputed, min chunks are lower counts only',
                scope='Cost-only coordinate/availability replay; no crop/feature bank, model inference, fit, grouping, truth or score produced',
                original_full_bank_GPU_planning_hours=native['planning_upper_seconds']/3600)
    write(output,result)
    return result


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    a=parser.parse_args();print(json.dumps(audit(a.output)),flush=True)
