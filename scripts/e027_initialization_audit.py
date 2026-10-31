#!/usr/bin/env python3
"""Reproduce the E027 initialization trap on one tiny synthetic graph.

Calls the real pinned PyNNDescent implementation and unchanged E027 distance.
Two predeclared initializations are compared: the executed partial native warm
start and one complete, source-blind global fill. No community data, labels,
training, resolution grid, production repair or recovery score is used.
"""
import argparse
import hashlib
import importlib.metadata
import json
from pathlib import Path
import sys
import time
import warnings

ROOT = Path(__file__).absolute().parents[1]
sys.path.insert(0, str(ROOT/'scripts'))
from e024_coverage import binding, write
from e027_inspection import require


def variant_record_path(output, variant):
    """Use distinct immutable journals; intermediate records never overwrite ready."""
    output = Path(output)
    require(variant in ['executed_partial_native', 'prospective_complete_global'], 'Unknown fixture variant')
    return output.with_name(output.stem+'-'+variant+output.suffix)


def run(output):
    """Record actual missing candidates and exact tiny recall, including failures."""
    import numpy as np
    import numba
    import pynndescent
    from pynndescent import NNDescent
    from dl_binner.unified.grouping import policy, channels, distances, metric
    numba.set_num_threads(4)
    require(importlib.metadata.version('pynndescent') == '0.5.13', 'Pinned library differs')
    rng = np.random.default_rng(11); cfg = policy(); n = 256; block = 32
    ids = np.array([f'opaque-{i:04d}' for i in range(n)])
    vectors = np.eye(64, dtype=np.float32)[np.arange(n)//block]+rng.normal(0, .001, (n,64)).astype(np.float32)
    vectors /= np.linalg.norm(vectors, axis=1)[:,None]
    data = dict(ids=ids, lengths=rng.integers(500,20000,n,dtype=np.int64),
        tnf=rng.dirichlet(np.ones(136),n).astype(np.float32), depth=rng.uniform(0,30,(n,10)).astype(np.float32))
    data['depth'][np.arange(n)//block % 2 == 0] = 0
    values, positive, scales, selected, transform = channels(data, vectors, np.ones(n,bool), cfg)
    packed = np.ascontiguousarray(np.column_stack([x[selected] for x in values]+
        [data['lengths'][selected],positive[selected]]),dtype=np.float32)
    native = np.empty((n,30),np.int32)
    for i in range(n):
        rows = np.arange(i//block*block,(i//block+1)*block); rows = rows[rows!=i]
        score = np.square(vectors[rows].astype(np.float64)-vectors[i]).sum(1)
        native[i] = rows[np.argsort(score)[:30]]
    partial = np.full((n,61),-1,np.int32)
    for i in range(n): partial[i,:31] = np.r_[i,native[i]]
    complete = partial.copy(); fill_rng = np.random.default_rng(11)
    for i in range(n):
        available = np.setdiff1d(np.arange(n),partial[i,:31],assume_unique=True)
        complete[i,31:] = fill_rng.choice(available,30,replace=False)
    args = dict(native_dim=64,composition_dim=136,s0=float(scales[0]),s1=float(scales[1]),
                s2=float(scales[2]),length_scale=cfg['length_scale_bp'],floor=cfg['distance_floor'])
    result = dict(kind='Tiny source-grounded initialization reproduction, no community outcomes',
        audit_script=binding(Path(__file__)),
        fixture_rows=n, isolated_seed_components=8, seed_component_size=block,
        executed_known_initial_candidates=31, discovery_width=61, retained_width=30,
        numerical_threads=4, library=importlib.metadata.version('pynndescent'),
        library_source=binding(Path(pynndescent.__file__).parent/'pynndescent_.py'),
        frozen_distance_source=binding(ROOT/'src/dl_binner/unified/grouping.py'),
        exposure_or_model_changed=False, native_vectors_or_graph_changed=False, outcomes={})
    for name, init in [('executed_partial_native',partial),('prospective_complete_global',complete)]:
        before=init.copy(); started=time.monotonic()
        with warnings.catch_warnings(record=True) as caught:
            index=NNDescent(packed,metric=metric,metric_kwds=args,n_neighbors=61,init_graph=init,
                tree_init=False,random_state=11,n_jobs=4,low_memory=True,max_candidates=60,n_iters=15,delta=.001)
        near=index.neighbor_graph[0]; missing=int((near<0).sum()); rows_missing=int((near<0).any(1).sum()); recall=[]
        for i in range(n):
            valid=near[i][near[i]>=0]; pool=np.unique(np.r_[valid,native[i]]);pool=pool[pool!=i]
            score=distances(data,values,positive,scales,cfg,i,pool)
            chosen=np.lexsort((ids[pool],score))[:30]; other=np.arange(n);other=other[other!=i]
            exact=distances(data,values,positive,scales,cfg,i,other); cutoff=np.partition(exact,29)[29]
            recall.append(float((score[chosen]<=cutoff+1e-10).mean()))
        result['outcomes'][name]=dict(missing_entries=missing,rows_with_missing=rows_missing,
            would_pass_executed_missing_candidate_gate=not missing, exact_tiny_recall=float(np.mean(recall)),
            warning=[str(w.message) for w in caught], caller_init_unchanged=bool(np.array_equal(init,before)),
            wall_seconds=time.monotonic()-started)
        write(variant_record_path(output,name),result)
    require(result['outcomes']['executed_partial_native']['rows_with_missing']>0,'Fixture did not reproduce incomplete discovery')
    require(result['outcomes']['prospective_complete_global']['missing_entries']==0,'Complete source-blind initialization failed')
    result['status']='PASS_REPRODUCTION_AND_ONE_FEASIBILITY_EXAMPLE'
    result['limitation']='One synthetic fixture; no community recall, biological recovery or optimality claim. Native failed E009 proposal arrays were not persisted, so their exact missing-row census remains unavailable.'
    write(output,result);return result


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True)
    print(json.dumps(run(p.parse_args().output)),flush=True)
