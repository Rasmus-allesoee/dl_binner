"""Real cached-marker/group/refiner/export fixture with explicit synthetic vectors.

No encoder is fit or reloaded. Synthetic DNA and HMM are generated solely for
engineering. Native Pyrodigal/PyHMMER create this tiny cache once; every science
consumer is restore-only and must leave it unchanged. Neither community is read.
"""
import argparse
import importlib.util
import json
from pathlib import Path
import sys
import time

import numpy as np


def run(output, fixture_source, threads=4):
    """Run both measured-depth and explicitly absent-depth contracts outside checkout."""
    from dl_binner.candidate.markers import cache, load_cache
    from dl_binner.multiview.views import config, prepare
    from dl_binner.multiview.arrays import load_arrays
    from dl_binner.multiview.downstream import refine
    from dl_binner.information.grouping import group, policy
    from dl_binner.information.export import export
    from dl_binner.information.audit import review
    from dl_binner.io import digest, save_arrays, write_json
    root=Path(output);root.mkdir(parents=True,exist_ok=False);started=time.monotonic()
    spec=importlib.util.spec_from_file_location('owned_e017_engineering_fixture',fixture_source)
    fixture=importlib.util.module_from_spec(spec);spec.loader.exec_module(fixture)
    fasta,depth,rows=fixture.fixture(root);hmm,manifest=fixture.asset(root,fasta)
    markers=root/'markers';markers.mkdir();cache(fasta,hmm,manifest,markers,threads)
    marker_before=digest(markers/'cache.json');base=config();results={}
    cfg=policy(Path(__file__).absolute().parent/'config.json')
    for name,dep in [('depth',depth),('sequence',None)]:
        unit=root/name;unit.mkdir();prepare(fasta,dep,unit/'features',base)
        features=unit/'features/features.npz';data,_=load_arrays(features,'features')
        # Native learned vectors are inputs in the real run. This fixture states
        # honestly that its unit vectors are synthetic; it cannot validate a fit.
        vectors=np.zeros((len(rows),64),np.float32)
        for i in np.flatnonzero(data['eligible']):vectors[i,0]=1
        embeddings=unit/'embeddings.npz'
        save_arrays(embeddings,dict(ids=data['ids'],features=vectors,evidence=data['eligible']),
                    dict(kind='embeddings',features_sha256=digest(features),metric='synthetic engineering unit vectors'))
        group(features,embeddings,unit/'group',cfg,base,threads)
        review(features,embeddings,unit/'group',unit/'audit.json')
        refine(features,embeddings,unit/'group/partition.json',markers,fasta,hmm,unit/'refine',base)
        accounting={}
        for arm,part in [('cores',unit/'group/core-partition.json'),('pre',unit/'group/partition.json'),
                         ('old',unit/'refine/old-partition.json'),('post',unit/'refine/partition.json')]:
            accounting[arm]=export(features,part,fasta,unit/('export-'+arm),arm=='post')
            if accounting[arm]['contigs']!=len(rows) or accounting[arm]['bp']!=sum(len(s)for _,s in rows):
                raise ValueError('Tiny full-DNA accounting differs')
        evidence=load_cache(markers,fasta,data['ids'].tolist())
        if digest(markers/'cache.json')!=marker_before:raise ValueError('Cached tiny markers mutated')
        results[name]=dict(contigs=len(rows),bp=sum(len(s)for _,s in rows),clean_markers=len(evidence['clean']),
                           audit=json.loads((unit/'audit.json').read_text()),accounting=accounting)
    result=dict(status='PASS',kind='engineering only; synthetic DNA/HMM/unit vectors; actual native graph/cache/refiner/export',
                results=results,wall_seconds=time.monotonic()-started,threads=threads,
                marker_cache_unchanged=True,encoder_fit=False,community_grouping=False)
    write_json(root/'fixture.json',result);return result


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True)
    p.add_argument('--fixture-source',type=Path,required=True);p.add_argument('--threads',type=int,default=4);a=p.parse_args()
    print(json.dumps(run(a.output,a.fixture_source,a.threads)),flush=True)
