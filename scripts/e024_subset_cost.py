#!/usr/bin/env python3
"""Cost one illustrative hash-random 100-genome Oral derivative, without scores.

Truth is used only for this explicitly oracle-defined workload illustration.
It does not enter E024 mapping/features/grouping, choose thresholds or decide a
candidate treatment. No derivative FASTA/features/embeddings or bins are written.
The 799-target full-community denominator is not replaced by this smaller set.
"""
from collections import defaultdict
import gzip
import hashlib
import itertools
import json
from pathlib import Path
import re
import sys

ROOT=Path(__file__).absolute().parents[1]
sys.path[:0]=[str(ROOT/'scripts'),str(ROOT/'src')]
import numpy as np
from e024_coverage import binding,write
from dl_binner.multiview.views import fasta_rows,crops


def audit(output):
    """Count actual selected DNA/views and project from the accepted native probes."""
    base=ROOT/'artifacts/e014-multiview-reconstruction'
    manifest=base/'oral-truth-origin-v1/manifest.json'
    reverse=base/'source-blind-join-v1.tsv.gz'
    fasta=base/'model-input-v1/oral.fna'
    feature=base/'inspection-20261019/verified/work/units/oral-dev5/features/features.npz'
    meta=json.loads((feature.parent/'views.json').read_text())
    origin=json.loads(manifest.read_text())
    rule='E024-cost-only-genome-subset-v1'
    chosen=sorted(origin['targets'],key=lambda g:(hashlib.sha256((rule+'\0'+g).encode()).hexdigest(),g))[:100]
    selected=set(chosen)
    with np.load(feature,allow_pickle=False) as f:eligible=f['eligible'];ids=f['ids']
    native_path=ROOT/'artifacts/e021-portable-admission/20261024T183844Z/native-v5-full-GPU-throughput.json'
    native=json.loads(native_path.read_text())['units']['oral-hybrid']
    strata={(s['view'],s['minimum_bp'],s['maximum_bp_exclusive']):s for s in native['strata']}
    bins=defaultdict(lambda:dict(views=0,bp=0))
    counts=dict(original_contigs=0,original_bp=0,eligible_parents=0,parent_bp=0,available_views=0,exposed_bp=0,minimum_chunks=0)
    with gzip.open(reverse,'rt') as join:
        if join.readline().split('\t')[:3]!=['opaque_id','anonymous_id','genome']:
            raise ValueError('Known source-blind reverse join schema differs')
        for i,pair in enumerate(itertools.zip_longest(fasta_rows(fasta),join)):
            dna_row,raw=pair
            if dna_row is None or raw is None:raise ValueError('Cost reverse/full DNA join truncated')
            ident,dna=dna_row;parts=raw.rstrip('\n').split('\t')
            if len(parts)!=8 or ident!=parts[0] or ident!=ids[i]:raise ValueError('Cost reverse/opaque-ID join differs')
            if parts[2] not in selected:continue
            if hashlib.sha256(dna.encode()).hexdigest()!=parts[7]:raise ValueError('Cost subset DNA differs')
            counts['original_contigs']+=1;counts['original_bp']+=len(dna)
            if not eligible[i]:continue
            counts['eligible_parents']+=1;counts['parent_bp']+=len(dna)
            views=[(0,len(dna))];seen=set()
            for j,(a,b,s) in enumerate(crops(ident,dna,meta['policy']),1):
                h=hashlib.sha256(s.encode()).digest()
                if re.search('[ACGT]{4}',s) and h not in seen:views.append((j,b-a))
                seen.add(h)
            counts['available_views']+=len(views);counts['exposed_bp']+=sum(n for _,n in views)
            counts['minimum_chunks']+=sum((n+3999)//4000 for _,n in views)
            for view,n in views:
                key=next(k for k in strata if k[0]==view and k[1]<=n<k[2])
                bins[key]['views']+=1;bins[key]['bp']+=n
    seconds=tokens=0
    for key,z in bins.items():
        s=strata[key];obs=s['observations']
        seconds+=s['planning_upper_seconds']*z['views']/s['views']
        tokens+=z['bp']*sum(o['tokens'] for o in obs)/sum(o['end']-o['start'] for o in obs)
    result=dict(kind='E024 cost-only illustrative 100 provided-genome derivative',status='PASS',rule=rule,
                genomes=chosen,selected_full_reference_bp=sum(origin['targets'][g] for g in chosen),
                unchanged_full_community_targets=len(origin['targets']),unchanged_full_reference_bp=sum(origin['targets'].values()),
                counts=counts,GPU_hours_planning_projection=seconds/3600,forward_tokens_projection=tokens,
                inputs={p.name:binding(p) for p in [manifest,reverse,fasta,feature,native_path]},
                allowed_interpretation='Oracle-defined small-community engineering/development; not matched full Oral, independent confirmation or unseen genomes',
                denominator='Never silently use selected100 denominator for the original799-target recovery claim',
                no_DNA_or_feature_derivative_written=True,proposed_for_E024=False)
    write(output,result);return result


if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    print(json.dumps(audit(a.output)),flush=True)
