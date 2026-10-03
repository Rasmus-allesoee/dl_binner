#!/usr/bin/env python3
"""Prepare, extract, cluster and score E003's final bounded representation screen.

Each Snakemake rule invokes one mode. Truth is read only by scoring; geometry
uses feature IDs and vectors. This is a development fragment-grouping screen,
not a binner, a comparison with trained TNF, or a whole-genome benchmark.
"""
import argparse
from collections import Counter
import hashlib
import itertools
import json
import os
import signal
from pathlib import Path
import subprocess
import sys
import time

import dnabert_s_cpu_spike as prior

ROOT = Path(__file__).resolve().parents[1]
LENGTHS = (500, 768, 1000, 2500, 10000)


def emit(stage, **values):
    """Print timestamped progress to the rule's captured log."""
    print(json.dumps(dict(stage=stage, utc=time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
                          **values)), flush=True)


def cleanup_native(record):
    """Stop the explicitly registered native session on outer cancellation/failure.

    Nested native supervision starts a separate process group. Match PID creation
    time before signalling, so a stale receipt cannot kill a reused unrelated PID.
    This closes the cancellation path without changing the accepted E002 guard.
    """
    import psutil
    record = Path(record)
    if not record.exists():
        return
    receipt = json.loads(record.read_text())
    try:
        process = psutil.Process(receipt['pid'])
        if process.create_time()!=receipt['created'] or os.getpgid(process.pid)!=process.pid:
            return
        os.killpg(process.pid,signal.SIGTERM)
        try:
            process.wait(timeout=3)
        except psutil.TimeoutExpired:
            os.killpg(process.pid,signal.SIGKILL)
    except (psutil.NoSuchProcess,ProcessLookupError):
        pass


def cancel_supervisor(signum, frame):
    """Raise through Python's finally blocks so nested guards clean up their worker."""
    raise SystemExit(128+signum)


def prepare(sources_path, output):
    """Create opaque IDs and disjoint hash-selected chromosome windows, before scoring.

    Select 20 different 20-kb cells per chromosome by SHA256, then hash offsets;
    four windows at each fixed length. Preserve ambiguity, duplicates and coordinates.
    """
    sources = json.loads(Path(sources_path).read_text())['sources']
    output = Path(output)
    output.mkdir(parents=True, exist_ok=False)
    rows, sequences = [], {}
    for source in sources:
        path = ROOT / source['fasta_path']
        assert prior.digest(path) == source['fasta_sha256']
        records = list(prior.fasta(path))
        assert len(records) == 1
        dna = records[0][1]
        assert len(dna) == source['length']
        assert hashlib.sha256(dna.encode()).hexdigest() == source['sequence_sha256']
        accession = source['accession_version']
        cells = sorted(range(len(dna)//20000), key=lambda i:hashlib.sha256(
            f'E003-v1:{accession}:cell:{i}'.encode()).hexdigest())[:20]
        assert len(cells) == 20
        for index, cell in enumerate(cells):
            length = LENGTHS[index//4]
            offset = int(hashlib.sha256(f'E003-v1:{accession}:offset:{index}'.encode()).hexdigest(),16)
            start = cell*20000 + offset % (20000-length+1)
            seq = dna[start:start+length]
            ident = 'F'+hashlib.sha256(f'{accession}:{start}:{length}'.encode()).hexdigest()[:16]
            assert ident not in sequences
            sequences[ident] = seq
            rows.append(dict(id=ident, genome=accession, organism=source['organism'],
                             start=start, end=start+length, bp=length,
                             sequence_sha256=hashlib.sha256(seq.encode()).hexdigest(),
                             strand_invariant_sha256=hashlib.sha256(min(seq,prior.reverse_complement(seq)).encode()).hexdigest(),
                             ambiguity_bases=sum(b not in 'ACGT' for b in seq)))
    rows.sort(key=lambda r:r['id'])
    assert len(rows) <= 320 and sum(r['bp'] for r in rows) <= 1000000
    with (output/'fragments.fna').open('w') as f:
        for row in rows:
            f.write(f'>{row["id"]}\n{sequences[row["id"]]}\n')
    duplicates = Counter(row['strand_invariant_sha256'] for row in rows)
    prior.write_json(output/'panel.json', dict(
        role='controlled development fragments; no assembly or whole-MAG truth',
        source_manifest_sha256=prior.digest(sources_path), sampling='E003-v1 SHA-ranked 20kb cells and offsets',
        bp=sum(r['bp'] for r in rows), windows=len(rows),
        fna_sha256=prior.digest(output/'fragments.fna'),
        duplicate_sequence_groups={key:count for key,count in duplicates.items() if count>1}, rows=rows))
    emit('panel_prepared', windows=len(rows), bp=sum(r['bp'] for r in rows))


def read_input(config):
    """Verify frozen panel/DNA hashes and return ordered raw DNA, without using truth."""
    manifest = ROOT/config['panel_manifest']
    assert prior.digest(manifest) == config['panel_manifest_sha256']
    metadata = json.loads(manifest.read_text())
    path = ROOT/config['panel_fasta']
    assert prior.digest(path) == metadata['fna_sha256']
    rows = list(prior.fasta(path))
    assert [name for name,_ in rows] == [r['id'] for r in metadata['rows']]
    for (_,seq), receipt in zip(rows,metadata['rows']):
        assert hashlib.sha256(seq.encode()).hexdigest() == receipt['sequence_sha256']
    return rows


def tnf(rows):
    """Return 136 strand-collapsed fourmer frequencies, skipping ambiguous fourmers.

    Independent implementation; no copied tool kernel or pretrained composition
    model. Zero-count rows remain present with an explicit evidence mask.
    """
    import numpy as np
    kmers = [''.join(x) for x in itertools.product('ACGT',repeat=4)]
    canonical = sorted({min(k,prior.reverse_complement(k)) for k in kmers})
    assert len(canonical) == 136
    lookup = np.array([canonical.index(min(k,prior.reverse_complement(k))) for k in kmers])
    encode = np.full(256,-1,dtype=np.int32)
    encode[np.frombuffer(b'ACGT',dtype=np.uint8)] = np.arange(4)
    result, counts = [], []
    for _,seq in rows:
        a = encode[np.frombuffer(seq.encode(),dtype=np.uint8)]
        valid = (a[:-3]>=0)&(a[1:-2]>=0)&(a[2:-1]>=0)&(a[3:]>=0)
        code = a[:-3]*64+a[1:-2]*16+a[2:-1]*4+a[3:]
        c = np.bincount(lookup[code[valid]],minlength=136).astype(np.float64)
        total = int(c.sum())
        counts.append(total)
        result.append(c/max(total,1))
    return np.array(result,dtype=np.float32), counts


def save_features(path, rows, features, config, detail):
    """Publish ID-aligned features and an input/config/byte-bound receipt."""
    import numpy as np
    path = Path(path)
    assert features.shape[0] == len(rows) and np.isfinite(features).all()
    np.savez(path,ids=[name for name,_ in rows],features=features.astype(np.float32))
    prior.write_json(path.with_suffix('.json'),dict(
        sha256=prior.digest(path), shape=list(features.shape),
        panel_manifest_sha256=config['panel_manifest_sha256'],
        source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        config_sha256=hashlib.sha256(json.dumps(config,sort_keys=True).encode()).hexdigest(), detail=detail))


def extract_glm(config, output):
    """Run the accepted frozen extractor on the new panel once; retain per-row progress."""
    import psutil
    process = psutil.Process()
    prior.write_json(Path(output).parent/'native-process.json',dict(pid=process.pid,created=process.create_time()))
    emit('native_worker_entered',pid=process.pid)
    import numpy as np
    import torch
    from threadpoolctl import threadpool_info
    torch.set_num_threads(4)
    torch.set_num_interop_threads(1)
    pin = json.loads((ROOT/config['model_pin']).read_text())
    model_path = ROOT/config['model_directory']
    for filename, receipt in pin['files'].items():
        assert prior.digest(model_path/filename) == receipt['sha256']
    rows = read_input(config)
    emit('load_frozen_model', model_revision=pin['revision'], windows=len(rows))
    model = prior.Extractor(str(model_path),config['glm_settings'])
    assert all(pool['num_threads'] <= 4 for pool in threadpool_info())
    import importlib
    module = importlib.import_module(type(model.model).__module__)
    assert prior.digest(module.__file__) == pin['files']['bert_layers.py']['sha256']
    assert module.flash_attn_qkvpacked_func is None
    prefix = Path(sys.executable).parent.parent.resolve()
    assert all(Path(__import__(name).__file__).resolve().is_relative_to(prefix)
               for name in ('torch','numpy','transformers','networkx'))
    arrays, detail = [], []
    start = time.monotonic()
    for index,row in enumerate(rows):
        x, d = model.extract([row])
        arrays.append(x)
        detail += d
        if index%8 == 0 or index == len(rows)-1:
            emit('glm_progress', completed=index+1,total=len(rows),seconds=time.monotonic()-start)
    features = np.concatenate(arrays)
    assert features.shape == (len(rows),768)
    assert all(p.grad is None and not p.requires_grad for p in model.model.parameters())
    save_features(output,rows,features,config,dict(
        model_revision=pin['revision'], model_files=pin['files'], chunk_records=detail,
        extraction_seconds=time.monotonic()-start, torch_intraop=4, torch_interop=1,
        loader_workers=0, library_pools=threadpool_info(), frozen=True,
        imports={name:__import__(name).__file__ for name in ('torch','numpy','transformers','networkx')},
        unknown_tokens=sum(d['unknown_tokens'] for d in detail)))
    emit('glm_complete',seconds=time.monotonic()-start,shape=list(features.shape))


def geometry(features, ids, k=5, resolution=1.0, min_size=3):
    """Standardize columns, normalize rows, build mutual cosine-kNN and cluster.

    Never consume labels or an expected number of genomes. Greedy weighted
    modularity determines the communities. Zero vectors, isolates and communities
    below min_size remain unassigned (-1); all rows retain neighbors/assignments.
    """
    import numpy as np
    import networkx as nx
    x = np.asarray(features,dtype=np.float64)
    if len(set(ids)) != len(ids) or x.ndim != 2 or len(x) != len(ids) or not np.isfinite(x).all():
        raise ValueError('Invalid feature axes or nonfinite values')
    evidence = np.linalg.norm(x,axis=1)>0
    mu = x[evidence].mean(0) if evidence.any() else np.zeros(x.shape[1])
    sd = x[evidence].std(0) if evidence.any() else np.zeros(x.shape[1])
    usable = sd>1e-8
    z = np.zeros_like(x)
    z[:,usable] = (x[:,usable]-mu[usable])/sd[usable]
    z[~evidence] = 0
    norms = np.linalg.norm(z,axis=1)
    valid = evidence & (norms>1e-12)
    z[valid] /= norms[valid,None]
    sim = np.clip(z@z.T,-1,1)
    nn = []
    for i in range(len(ids)):
        eligible = [j for j in range(len(ids)) if valid[i] and valid[j] and i != j]
        nn.append(sorted(eligible,key=lambda j:(-sim[i,j],ids[j]))[:k])
    graph = nx.Graph()
    graph.add_nodes_from(range(len(ids)))
    for i in range(len(ids)):
        for j in nn[i]:
            if i < j and i in nn[j] and sim[i,j]>0:
                graph.add_edge(i,j,weight=float(sim[i,j]))
    assignments = np.full(len(ids),-1,dtype=np.int32)
    communities = (nx.community.greedy_modularity_communities(graph,weight='weight',resolution=resolution)
                   if graph.number_of_edges() else [])
    accepted = sorted((sorted(c) for c in communities if len(c)>=min_size),key=lambda c:min(ids[i] for i in c))
    for label,community in enumerate(accepted):
        assignments[community] = label
    return dict(ids=ids,neighbors=[[ids[j] for j in row] for row in nn],
                assignment=assignments.tolist(), valid=valid.tolist(),
                edges=graph.number_of_edges(), clusters=len(accepted),
                unassigned=int((assignments<0).sum()),
                geometry='column population z-score (sd>1e-8), row L2; exact cosine',
                clustering=dict(k=k,mutual=True,positive_weights=True,resolution=resolution,min_size=min_size,
                                expected_cluster_count=None),
                transform=dict(mean=mu.tolist(),std=sd.tolist(),usable=usable.tolist()))


def score(partition, panel):
    """Score all fragments against chromosome-origin truth with fixed denominators.

    Report neighbor purity and B-cubed precision/recall/F1, including unassigned
    rows as zero. B-cubed completeness refers to sampled fragments, not MAGs.
    Length endpoints are exact points, not support for all lengths in each stratum.
    """
    ids = [r['id'] for r in panel['rows']]
    if partition['ids'] != ids:
        raise ValueError('Partition/truth axes mismatch')
    truth = {r['id']:r['genome'] for r in panel['rows']}
    totals = Counter(truth.values())
    labels = dict(zip(ids,partition['assignment']))
    sizes = Counter(v for v in labels.values() if v>=0)
    origins = Counter((labels[i],truth[i]) for i in ids if labels[i]>=0)
    per = []
    for row,neighbors in zip(panel['rows'],partition['neighbors']):
        i, g = row['id'],row['genome']
        nn_purity = sum(truth[n]==g for n in neighbors)/5  # Missing neighbors remain in denominator.
        label = labels[i]
        p = origins[(label,g)]/sizes[label] if label>=0 else 0.0
        r = origins[(label,g)]/totals[g] if label>=0 else 0.0
        per.append(dict(id=i,genome=g,bp=row['bp'],neighbor_purity=nn_purity,
                        b3_precision=p,b3_recall=r,assigned=label>=0))

    def aggregate(rows, weighted=False):
        weights = [r['bp'] if weighted else 1 for r in rows]
        total = sum(weights)
        avg = lambda key:sum(w*r[key] for w,r in zip(weights,rows))/total
        p,r = avg('b3_precision'),avg('b3_recall')
        return dict(fragments=len(rows),bp=sum(r['bp'] for r in rows),
                    neighbor_purity=avg('neighbor_purity'),b3_precision=p,b3_recall=r,
                    b3_f1=2*p*r/(p+r) if p+r else 0,assigned_fraction=avg('assigned'))
    return dict(all=aggregate(per),base_weighted=aggregate(per,True),
                short=aggregate([r for r in per if r['bp']<2500]),
                long=aggregate([r for r in per if r['bp']>=2500]),
                by_length={str(length):aggregate([r for r in per if r['bp']==length]) for length in LENGTHS},
                per_fragment=per,clusters=partition['clusters'],unassigned=partition['unassigned'])


def decide(scores, config):
    """Apply the precommitted utility criteria; laptop projections are not a veto."""
    tnf_score,glm_score = scores['tnf'],scores['glm']
    rule = config['decision']
    values = dict(short_neighbor_gain=glm_score['short']['neighbor_purity']-tnf_score['short']['neighbor_purity'],
                  long_neighbor_delta=glm_score['long']['neighbor_purity']-tnf_score['long']['neighbor_purity'],
                  base_weighted_b3_gain=glm_score['base_weighted']['b3_f1']-tnf_score['base_weighted']['b3_f1'])
    passed = dict(short_neighbor_gain=values['short_neighbor_gain']+1e-12>=rule['short_neighbor_gain_min'],
                  long_neighbor_delta=values['long_neighbor_delta']+1e-12>=rule['long_neighbor_delta_min'],
                  base_weighted_b3_gain=values['base_weighted_b3_gain']+1e-12>=rule['base_weighted_b3_gain_min'])
    return dict(include_frozen_glm=all(passed.values()),values=values,criteria_passed=passed,
                scope='final development screen versus raw TNF, not contrastive-trained TNF or genome recovery')


def main():
    """Invoke one explicit stage; supervise native GLM and the whole serial workflow."""
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--mode',required=True,choices=['prepare','tnf','glm','glm-native','partition','score','run'])
    p.add_argument('--config',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    p.add_argument('--input',type=Path)
    args = p.parse_args()
    config = json.loads(args.config.read_text())
    if args.mode=='prepare':
        prepare(ROOT/config['sources_manifest'],args.output)
        return
    if args.mode=='run':
        signal.signal(signal.SIGTERM,cancel_supervisor)
        assert config['limits']['threads']==4 and config['limits']['total_run_seconds']<=7200
        assert config['limits']['ram_bytes']<=8000000000
        os.environ.update(PYTHONNOUSERSITE='1',TOKENIZERS_PARALLELISM='false',HF_HUB_OFFLINE='1',
                          TRANSFORMERS_OFFLINE='1',HF_HOME=str(args.output.resolve()/'hf-cache'),
                          OMP_NUM_THREADS='4',MKL_NUM_THREADS='4',OPENBLAS_NUM_THREADS='4',
                          VECLIB_MAXIMUM_THREADS='4',NUMEXPR_NUM_THREADS='4')
        for name in ('PYTHONPATH','PYTHONHOME','PYTHONUSERBASE'):os.environ.pop(name,None)
        command = [config['snakemake'],'--snakefile',str(ROOT/'workflows/e003-screen/Snakefile'),
                   '--configfile',str(args.config.resolve()),'--directory',str(args.output.resolve()),
                   '--cores','4','--jobs','1','--resources','mem_mb=8000','--benchmark-extended',
                   '--runtime-source-cache-path',str(args.output.resolve()/'snakemake-source-cache'),
                   '--printshellcmds','--rerun-incomplete','--latency-wait','2']
        try:
            result = prior.supervise(command,args.output,config['limits']['total_run_seconds'],config['limits']['ram_bytes'])
        finally:
            cleanup_native(args.output/'native-process.json')
        raise SystemExit(0 if result['exit_code']==0 and result['stop_reason'] is None else 1)
    if args.mode=='glm':
        signal.signal(signal.SIGTERM,cancel_supervisor)
        assert config['limits']['feature_seconds']<=3600 and config['limits']['ram_bytes']<=8000000000
        command = [sys.executable,'-u',str(Path(__file__).resolve()),'--mode','glm-native',
                   '--config',str(args.config.resolve()),'--output',str(args.output.resolve())]
        result = prior.supervise(command,args.output.parent/'glm-monitor',config['limits']['feature_seconds'],config['limits']['ram_bytes'])
        if result['exit_code'] != 0 or result['stop_reason'] is not None:
            raise RuntimeError('Native feature stage failed: '+str(result))
        return
    if args.mode=='glm-native':
        extract_glm(config,args.output)
    elif args.mode=='tnf':
        rows = read_input(config)
        features, counts = tnf(rows)
        save_features(args.output,rows,features,config,dict(valid_fourmers=counts,untrained=True))
        emit('tnf_complete',shape=list(features.shape))
    elif args.mode=='partition':
        import numpy as np
        receipt = json.loads(args.input.with_suffix('.json').read_text())
        assert prior.digest(args.input) == receipt['sha256']
        assert receipt['panel_manifest_sha256'] == config['panel_manifest_sha256']
        with np.load(args.input,allow_pickle=False) as z:
            result = geometry(z['features'],z['ids'].tolist(),**config['clustering'])
        prior.write_json(args.output,result)
        emit('partition_complete',clusters=result['clusters'],unassigned=result['unassigned'])
    elif args.mode=='score':
        assert prior.digest(ROOT/config['panel_manifest']) == config['panel_manifest_sha256']
        panel = json.loads((ROOT/config['panel_manifest']).read_text())
        scores = {name:score(json.loads((args.input/f'{name}.partition.json').read_text()),panel)
                  for name in ('tnf','glm')}
        prior.write_json(args.output,dict(source_commit=subprocess.check_output(
            ['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),config=config,
            scores=scores,decision=decide(scores,config)))
        emit('scoring_complete',decision=decide(scores,config))


if __name__=='__main__':
    try:
        main()
    except Exception:
        import traceback
        traceback.print_exc()
        sys.stdout.flush();sys.stderr.flush()
        os._exit(1)  # Fail promptly, including native-library teardown.
