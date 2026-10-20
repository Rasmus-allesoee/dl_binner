"""Real sparse/feature readers and prospective core/recruitment refusal contracts."""
import copy
import json
from pathlib import Path

import numpy as np
import unittest
import tempfile
import sys
import os
if os.environ.get("E017_USE_CHECKOUT")=="1":
    sys.path.insert(0,str(Path(__file__).absolute().parents[1]/"src"))

from dl_binner.information.grouping import (CoreIndex, contexts, core_profiles, group,
    joint_coordinates, load_inputs, policy, recruit)
from dl_binner.io import digest, save_arrays
from dl_binner.multiview.views import prepare
from dl_binner.multiview.views import config as base_config
from dl_binner.multiview.arrays import load_arrays

ROOT = Path(__file__).absolute().parents[1]
POLICY = ROOT/'experiments/E017-information-aware-grouping/config.json'


def fixture(tmp, depth=True):
    """Create real DNA/features with unsorted opaque IDs, short/noise and two cores.

    Embeddings are explicitly synthetic engineering vectors, not a neural fit.
    Real readers, core graph, Leiden, recruitment, refiner and export run on them.
    """
    fasta = tmp/'dna.fa'
    ids = ['z|core-A', 'a core-description', 'm|core-B', 'b|core-B', 'y-short',
           'x-negative', 's-excluded', 'r-ambiguous', 'q-missing']
    dna = ['ACGT'*1500, 'ACGT'*1500, 'AAAA'*1500, 'AAAA'*1500,
           'ACGT'*200, 'AAAA'*200, 'ACGT'*40, 'NNNN'*200, 'ACGT'*250]
    fasta.write_text(''.join('>'+i+'\n'+s+'\n' for i,s in zip(ids,dna)))
    ids = [x.split()[0] for x in ids]
    dep = tmp/'depth.tsv'
    dep.write_text('contig_id\t2\t0\tconstant\n'+''.join(
        q+'\t'+('0\t0' if q == 'q-missing' else '10\t1' if j in [0,1,4] else '1\t10')+'\t0\n'
        for j,q in reversed(list(enumerate(ids)))))
    cfg = base_config()
    feat = tmp/'features'
    prepare(fasta, dep if depth else None, feat, cfg)
    f = feat/'features.npz'
    data, meta = load_arrays(f, 'features')
    x = np.zeros((len(ids),64),np.float32)
    for j in np.flatnonzero(data['eligible']):
        x[j,0 if j in [0,1,4,8] else 1] = 1
    emb = tmp/'embeddings.npz'
    save_arrays(emb, dict(ids=data['ids'], features=x, evidence=data['eligible']),
                dict(kind='embeddings',features_sha256=digest(f),metric='unchanged synthetic unit vectors'))
    return f, emb, fasta, cfg


def real_core_recruit_sparse_reload_export(tmp_path,depth):
    f,emb,fasta,base=fixture(tmp_path,depth)
    cfg=policy(POLICY)
    group(f,emb,tmp_path/'group',cfg,base,2)
    data,x,valid,meta=load_inputs(f,emb)
    pre=json.loads((tmp_path/'group/partition.json').read_text())
    cores=json.loads((tmp_path/'group/core-partition.json').read_text())
    graph,gm=load_arrays(tmp_path/'group/graph.npz','information_core_graph')
    cache,cm=load_arrays(tmp_path/'group/recruitment.npz','information_recruitment')
    from dl_binner.information.audit import review
    review(f,emb,tmp_path/'group',tmp_path/'audit.json')
    assert pre['ids']==data['ids'].tolist()==graph['ids'].tolist()==cache['ids'].tolist()
    assert len(pre['assignment'])==9 and pre['valid']==valid.tolist()
    assert len(graph['core_indices'])==4 and all(data['lengths'][graph['core_indices']]>=2500)
    assert pre['assignment'][4]==pre['assignment'][0]>=0
    assert pre['assignment'][5]==pre['assignment'][2]>=0
    assert pre['assignment'][0]!=pre['assignment'][2]
    assert pre['assignment'][6:8]==[-1,-1]
    assert cores['assignment'][4:]==[-1]*5
    assert abs(gm['objective']['gamma']-float(np.median(graph['weights']))/30)<1e-12
    assert cm['audit']['mean_tie_aware_recall']==1
    assert gm['transform']['depth_usable_columns']==([True,True,False] if depth else [])
    assert np.array_equal(load_arrays(emb,'embeddings')[0]['features'],x)
    if depth:
        q=int(np.flatnonzero(cache['query_indices']==8)[0])
        assert not cache['channel_available'][q,:,2].any()
    from dl_binner.clustering import export
    export(f,tmp_path/'group/partition.json',fasta,tmp_path/'export')
    manifest=json.loads((tmp_path/'export/manifest.json').read_text())
    assert manifest['contigs']==9 and manifest['bp']==int(data['lengths'].sum())
    assert manifest['assigned']+manifest['unassigned']+manifest['excluded']==9
    from dl_binner.information.export import export as stream_export
    observed=stream_export(f,tmp_path/'group/partition.json',fasta,tmp_path/'stream-export')
    assert sum(v['contigs'] for v in observed['populations'].values())==9
    assert observed['bp']==manifest['bp']
    assert (tmp_path/'stream-export/assignments.tsv').read_bytes()==(tmp_path/'export/assignments.tsv').read_bytes()
    sys.path.insert(0,str(ROOT/'scripts'))
    from e017_review import export_contract
    rows,checked=export_contract(pre,data,tmp_path/'stream-export')
    assert len(rows)==9 and checked['populations']==observed['populations']
    with unittest.TestCase().assertRaises(FileExistsError):group(f,emb,tmp_path/'group',cfg,base,2)


def test_input_drift_and_policy_refusal(tmp_path):
    f,emb,_,_=fixture(tmp_path)
    original=emb.read_bytes();emb.write_bytes(original+b'bad')
    with unittest.TestCase().assertRaisesRegex(ValueError,'hash mismatch'):load_inputs(f,emb)
    p=json.loads(POLICY.read_text());p['truth_K']=3
    q=tmp_path/'policy.json';q.write_text(json.dumps(p))
    with unittest.TestCase().assertRaisesRegex(ValueError,'single rule'):policy(q)


def test_ambiguous_recruitment_and_no_propagation(tmp_path):
    f,emb,_,base=fixture(tmp_path)
    data,x,valid,_=load_inputs(f,emb);cfg=policy(POLICY)
    cores=np.array([0,1,2,3]);channels,available,scales,_=contexts(data,x,cores,cfg)
    pre=dict(ids=data['ids'].tolist(),assignment=[0,0,1,1,-1,-1,-1,-1,-1],clusters=2,
             reason=['']*9,config=base)
    # Same evidence/profile on both bins must never be forced by ID ties.
    channels=tuple(np.ones_like(v) for v in channels)
    out,e=recruit(data,valid,channels,available,scales,pre,np.array([4,5]),
                  np.array([[0,1,2,3],[0,1,2,3]]),np.ones((2,4)),cfg)
    assert out['assignment'][4:6]==[-1,-1]
    assert e['accepted_bins'].tolist()==[-1,-1]
    assert all(v=='ambiguous_core_margin' for v in e['reasons'])
    assert np.array_equal(e['profile_core_counts'],[2,2])


def test_native_approximate_index_and_fixed_recall():
    # Actual NNDescent and numba, tiny synthetic points; no benchmark DNA.
    rng=np.random.default_rng(11);x=rng.normal(size=(96,8)).astype(np.float32)
    cfg=policy(POLICY);cfg['exact_threshold']=32
    index=CoreIndex(x,[f'opaque-{j:03}' for j in range(len(x))],cfg,2)
    nn,dd=index.query(x,np.arange(len(x)))
    audit=index.audit(x,index.ids,nn,dd,np.arange(len(x)))
    assert index.native is not None and audit['mean_tie_aware_recall']>=.9
    assert all(i not in row for i,row in enumerate(nn))


def test_empty_core_population_preserves_all_rows(tmp_path):
    f,emb,_,base=fixture(tmp_path)
    cfg=policy(POLICY);cfg['core_min_bp']=100000
    group(f,emb,tmp_path/'group',cfg,base,2)
    result=json.loads((tmp_path/'group/partition.json').read_text())
    assert result['assignment']==[-1]*9
    assert result['clusters']==0


def test_positive_support_and_corrupt_graph_refusal(tmp_path):
    f,emb,_,base=fixture(tmp_path)
    data,x,valid,_=load_inputs(f,emb);cfg=policy(POLICY)
    channels,available,scales,_=contexts(data,x,np.array([0,1,2,3]),cfg)
    pre=dict(ids=data['ids'].tolist(),assignment=[0,0,1,1,-1,-1,-1,-1,-1],clusters=2,
             reason=['']*9,config=base)
    result,e=recruit(data,valid,channels,available,scales,pre,np.array([4]),np.array([[0,1]]),np.array([[1.,0.]]),cfg)
    assert result['assignment'][4]==-1 and e['reasons'][0]=='insufficient_distinct_core_support'
    group(f,emb,tmp_path/'group',cfg,base,2)
    graph,meta=load_arrays(tmp_path/'group/graph.npz','information_core_graph')
    graph['edges'][0,0]=-1
    # Use a fresh writer to exercise schema refusal, not just the outer checksum.
    damaged=tmp_path/'damaged';damaged.mkdir()
    import shutil
    for p in (tmp_path/'group').iterdir():
        if p.name not in ['graph.npz','graph.json']:shutil.copyfile(p,damaged/p.name)
    save_arrays(damaged/'graph.npz',graph,{k:v for k,v in meta.items() if k not in ['version','sha256','ids_sha256']})
    # Rebind dependent metadata to reach the actual malformed sparse-reader gate.
    cm=json.loads((damaged/'recruitment.json').read_text());cm['graph_sha256']=digest(damaged/'graph.npz')
    (damaged/'recruitment.json').write_text(json.dumps(cm))
    from dl_binner.information.audit import review
    with unittest.TestCase().assertRaisesRegex(ValueError,'Malformed sparse core graph'):
        review(f,emb,damaged,tmp_path/'refused.json')


class InformationGrouping(unittest.TestCase):
    def test_worker_requires_owned_jit_cache_before_output(self):
        from unittest.mock import patch
        sys.path.insert(0,str(ROOT/'scripts'))
        from e017_control import stage
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);f,emb,_,_=fixture(p)
            units={u:dict(fasta=str(p/'dna.fa'),features=str(f),embeddings=str(emb),marker_cache=str(p/'unused-markers'))
                   for u in ['E009-positive','oral-positive']}
            reuse=p/'reuse.json';reuse.write_text(json.dumps(dict(units=units,hmm='unused-fixture.hmm')))
            plan=dict(kind='E017 fixed-learning cached grouping',units=units,threads=4,work=str(p/'work'),
                      python=sys.executable,worker=str(ROOT/'scripts/e017_control.py'),workflow_python=sys.executable,
                      snakefile=str(ROOT/'experiments/E017-information-aware-grouping/Snakefile'),config=str(POLICY),
                      base_config=str(ROOT/'src/dl_binner/resources/multiview.json'),hmm='unused-fixture.hmm',reuse_lock=str(reuse))
            path=p/'plan.json';path.write_text(json.dumps(plan))
            with patch.dict(os.environ):
                os.environ.pop('NUMBA_CACHE_DIR',None)
                with self.assertRaisesRegex(ValueError,'job-owned NUMBA_CACHE_DIR'):
                    stage(path,'E009-positive','group')
            self.assertFalse((p/'work').exists())
    def test_depth_present_full_contract(self):
        with tempfile.TemporaryDirectory() as d:real_core_recruit_sparse_reload_export(Path(d),True)
    def test_sequence_only_full_contract(self):
        with tempfile.TemporaryDirectory() as d:real_core_recruit_sparse_reload_export(Path(d),False)
    def test_drift(self):
        with tempfile.TemporaryDirectory() as d:test_input_drift_and_policy_refusal(Path(d))
    def test_ambiguity(self):
        with tempfile.TemporaryDirectory() as d:test_ambiguous_recruitment_and_no_propagation(Path(d))
    def test_approximate_index(self):
        test_native_approximate_index_and_fixed_recall()
    def test_empty_cores(self):
        with tempfile.TemporaryDirectory() as d:test_empty_core_population_preserves_all_rows(Path(d))
    def test_positive_support_and_corrupt_reader(self):
        with tempfile.TemporaryDirectory() as d:test_positive_support_and_corrupt_graph_refusal(Path(d))

if __name__=='__main__':unittest.main()
