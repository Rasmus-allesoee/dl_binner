#!/usr/bin/env python3
"""Assess publisher source-abundance variation for data-planning only.

Uses existing small metadata, not mapped reads or binner outcomes. Source/genome
labels here cannot enter E024 features, bins, thresholds, index coordinates or
training. This expected-source check is not a substitute for measured depth,
whole-community recovery or a guarantee that reads discriminate shared sequence.
"""
import argparse
import json
from pathlib import Path
import sys

ROOT=Path(__file__).absolute().parents[1]
sys.path[:0]=[str(ROOT/'scripts')]
import numpy as np
from e024_coverage import SAMPLES,binding,write


def audit(output):
    """Join publisher target identities and describe expected ten-sample variation."""
    base=ROOT/'artifacts/e014-multiview-reconstruction'
    target_manifest=base/'oral-truth-origin-v1/manifest.json'
    targets=sorted(json.loads(target_manifest.read_text())['targets'])
    values=[];inputs={str(target_manifest.relative_to(ROOT)):binding(target_manifest)}
    for s in SAMPLES:
        path=base/'metadata'/f'setup-abundance{s}.tsv'
        data=dict(line.split('\t') for line in path.read_text().splitlines())
        if not set(targets)<=set(data):raise ValueError('Expected source-abundance ID join differs')
        a=np.asarray([float(data[g]) for g in targets])
        if not np.isfinite(a).all() or (a<0).any() or not a.sum()>0:raise ValueError('Invalid publisher source abundances')
        values.append(a/a.sum());inputs[str(path.relative_to(ROOT))]=binding(path)
    x=np.asarray(values).T
    variable=np.ptp(x,axis=1)>1e-12
    positive=(x>0).any(1)
    norm=np.linalg.norm(x,axis=1);unit=np.divide(x,norm[:,None],out=np.zeros_like(x),where=norm[:,None]>0)
    cosine=unit@unit.T;np.fill_diagonal(cosine,-np.inf)
    nearest=cosine[positive].max(1)
    from collections import Counter
    profiles=Counter(tuple(np.round(z,12)) for z in unit[positive])
    sample_norm=x/np.linalg.norm(x,axis=0)
    result=dict(kind='E024 source-metadata planning assessment, not measured coverage/features',status='PASS',
                samples=SAMPLES,targets=len(targets),positive_sources=int(positive.sum()),
                sources_with_between_sample_variation=int((variable&positive).sum()),
                distinct_normalized_sample_columns=len({tuple(x[:,j]) for j in range(10)}),
                sources_positive_in_exactly_one_sample=int(((x>0).sum(1)==1).sum()),
                distinct_source_profile_directions_at_12_decimals=len(profiles),
                sources_in_shared_profile_direction_groups=sum(n for n in profiles.values() if n>1),
                largest_profile_direction_group=max(profiles.values()),
                sample_cosine=(sample_norm.T@sample_norm).tolist(),
                nearest_other_source_profile_cosine_quantiles=dict(zip(['min','q25','median','q75','max'],np.quantile(nearest,[0,.25,.5,.75,1]).tolist())),
                inputs=inputs,used_to_choose_thresholds_or_bins=False,
                interpretation='Publisher table entries vary across samples but many directions can be shared. Table units are not asserted to be measured depth or unique genome barcodes. Actual MAPQ-filtered contig depth, sampling and reference competition remain unmeasured.')
    write(output,result);return result


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    print(json.dumps(audit(a.output)),flush=True)
