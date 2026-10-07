#!/usr/bin/env python3
"""Independently retain pilot adapter/integration evidence without repeating work.

Verify all local attempt/return bytes, complete real-DNA fixture exports, native
depth counts, precision/masks/reload and partial/full resume. Publish source pins,
costs, failures and scope exclusions, never fixture scores as scientific utility.
"""
import argparse
import csv
import json
from pathlib import Path
import sys

import numpy as np

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'scripts'))
from e005_smoke import sha, write
from dl_binner.io import load_arrays, read_fasta, validate_features


def inspect(attempt):
    """Verify retained attempt/inventory/return and independently inspect successful data."""
    status=json.loads((attempt/'status.json').read_text())
    inventory=json.loads((attempt/'retained-files.json').read_text())
    for entry in inventory['files']:
        path=attempt/entry['path']
        if not path.resolve().is_relative_to(attempt.resolve()) or sha(path)!=entry['sha256'] or path.stat().st_size!=entry['bytes']:
            raise ValueError('Retained artifact mismatch: '+str(path))
    archive=attempt.parent/'transfer'/(attempt.name+'-return.tar.gz')
    if sha(archive)!=archive.with_name(archive.name+'.sha256').read_text().split()[0]:
        raise ValueError('Local return checksum mismatch')
    costs=[json.loads(l) for l in (attempt/'terminal.log').read_text().splitlines() if l.startswith('{')]
    cost=next(v for v in costs if v['stage']=='cost_through_collection')
    result=dict(locator=str(attempt.relative_to(ROOT)),status=status['status'],
        source_commit=json.loads((attempt/'bundle-manifest.json').read_text())['source_commit'],
        return_sha256=sha(archive),return_bytes=archive.stat().st_size,
        retained_files=len(inventory['files']),retained_bytes=sum(e['bytes'] for e in inventory['files']),
        declared_local_threads=status['allocated_vcpus'],cost=cost,native_linux=status.get('native_linux',False))
    if status['status']!='passed':
        result.update(error=status['error'],checkpoint_created=(attempt/'pilot/checkpoint.pt').exists(),
                      scoring_completed=(attempt/'pilot/learned.evaluation/evaluation.json').exists())
        return result
    if status['native_linux']:
        raise ValueError('This reviewer owns local fixture evidence only')
    cfg=json.loads((attempt/'resolved-config.json').read_text()); work=attempt/'pilot'
    source=dict(read_fasta(cfg['fasta']))
    data,meta=load_arrays(work/'features.npz','features'); validate_features(data,meta)
    if data['ids'].tolist()!=list(source) or meta['samples']!=['GI_sample_1','GI_sample_4'] or data['depth'].dtype!=np.float64:
        raise ValueError('Native feature schema/axis/precision mismatch')
    with (work/'mean-depth.tsv').open() as stream:
        table=list(csv.reader(stream,delimiter='\t'))
    if table[0]!=['contig_id']+meta['samples'] or [r[0] for r in table[1:]]!=list(source):
        raise ValueError('Native mean-depth axis mismatch')
    np.testing.assert_array_equal(data['depth'],np.asarray([r[1:] for r in table[1:]],dtype=np.float64))
    np.testing.assert_array_equal(data['zero_depth'],data['depth']==0)
    np.testing.assert_array_equal(data['depth_evidence'],(data['depth']>0).any(1))
    learned,_=load_arrays(work/'learned.embeddings.npz','embeddings')
    saved,_=load_arrays(work/'checkpoint.reference.npz','embeddings')
    np.testing.assert_array_equal(learned['ids'],saved['ids'])
    np.testing.assert_array_equal(learned['features'],saved['features'])
    accounting={}
    for mode in ('raw','learned'):
        emb,_=load_arrays(work/(mode+'.embeddings.npz'),'embeddings')
        if emb['ids'].tolist()!=list(source) or not np.isfinite(emb['features']).all():
            raise ValueError('Embedding rows/values differ')
        found={}
        folder=work/(mode+'.export')
        for path in folder.glob('*.fna'):
            for ident,dna in read_fasta(path) if path.stat().st_size else []:
                if ident in found: raise ValueError('Repeated exported DNA')
                found[ident]=dna
        if found!=source: raise ValueError('Export missing/changed DNA')
        with (folder/'assignments.tsv').open() as stream:
            rows=list(csv.DictReader(stream,delimiter='\t'))
        if [r['contig_id'] for r in rows]!=list(source): raise ValueError('Assignment omitted ID')
        accounting[mode]={kind:sum(r['status']==kind for r in rows) for kind in ('assigned','unassigned','excluded')}
        evaluation=json.loads((work/(mode+'.evaluation/evaluation.json')).read_text())
        if sum(s['bp'] for s in evaluation['strata'])!=sum(map(len,source.values())):
            raise ValueError('Evaluation lost length strata')
        if any(s['bp']!=sum(s[k+'_bp'] for k in ('assigned','unassigned','excluded')) for s in evaluation['strata']):
            raise ValueError('Evaluation lost excluded/noise bp')
    reused=json.loads((attempt/'partial-reuse-before.json').read_text())
    for name,entry in reused.items():
        path=work/name
        if sha(path)!=entry['sha256'] or path.stat().st_mtime_ns!=entry['mtime_ns']:
            raise ValueError('Completed preprocessing repeated/changed')
    if 'Nothing to be done' not in (attempt/'stages/completed-resume.log').read_text():
        raise ValueError('Completed pilot schedules work')
    native=json.loads((attempt/'adapter-contracts/verified.json').read_text())
    if native['native_depth_base_observations']!=71 or not native['native_AMBER']:
        raise ValueError('New native adapter contract failed')
    training=json.loads((work/'checkpoint.json').read_text())
    result.update(contigs=len(source),bp=sum(map(len,source.values())),samples=meta['samples'],accounting=accounting,
        zero_depth_rows=int((~data['depth_evidence']).sum()),eligible=int(data['eligible'].sum()),
        below_500=int((data['lengths']<500).sum()),reload_max_abs=0,reused_files=len(reused),
        native_contracts=native,stages=status['stages'],
        training={k:training[k] for k in ('numerical_threads','torch_interop','loader_workers','parameter_count',
            'training_wall_seconds','training_process_cpu_seconds','training_average_cpus')},
        fixture=dict(locator=str(Path(cfg['fasta']).relative_to(ROOT)),fasta_sha256=sha(cfg['fasta']),
            role=cfg['role'],samples=cfg['samples'],sampled_pairs=cfg['sampled_pairs']),
        biology='not assessed: partial real-DNA fixture and synthetic matching reads; numerical scores are contract outputs only')
    return result


def main(output):
    """Collect the fixed retained local attempts and bind the final v4 owner packet."""
    base=ROOT/'artifacts/e005-linux-pilot'
    attempts=[inspect(p.parent) for p in sorted((base/'local-pilot-owner').glob('gi-pilot-*/status.json'))]
    packet=json.loads((base/'pilot-transfer-v4/e005-gi-pilot/bundle-manifest.json').read_text())
    archive=base/'pilot-transfer-v4/e005-gi-pilot-v4.tar.gz'
    if sha(archive)!=archive.with_name(archive.name+'.sha256').read_text().split()[0]: raise ValueError('Transfer mismatch')
    final=[a for a in attempts if a['source_commit']==packet['source_commit'] and a['status']=='passed']
    if len(final)!=1: raise ValueError('Final packet has no unique passed full real fixture')
    write(output,dict(record='E005',date='2026-10-06',decision='native pilot adapters and actual v4 local packet accepted; full owner GI pilot unrun',
        transfer=dict(archive=str(archive.relative_to(ROOT)),bytes=archive.stat().st_size,sha256=sha(archive),source_commit=packet['source_commit']),
        attempts=attempts,final_fixture=final[0]['locator'],
        scope=dict(native_workers_mocked=[],platform='native Mac mapper0.17.0/samtools1.24 and pinned AMBER source/dependencies; accepted installed binner',
            Linux_validation='accepted model smoke only; new full large-read mapping/depth/evaluation runtime/source/lock entry checks await owner run',
            local_only_skips=['Linux ABI/affinity','original large UCloud FASTQs and E001 executed-lock comparison','10-GB provisioning replaced by 1 GB for tiny fixture'],
            costs='local declared four-thread wall budget, not UCloud billing; setup/downloads/tests/review outside driver clock',
            scientific_utility='not measured; no full pilot extraction/training/evaluation or three-way study run')))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True)
    main(p.parse_args().output)
