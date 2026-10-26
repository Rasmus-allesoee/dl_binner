#!/usr/bin/env python3
"""Secondary sequence-quality context from accepted E011 MetaBAT2 outputs only.

No binner execution, primary rescore, changed partition, RNA screen or truth
construction. Exact accepted inputs/truth/assignments/native and exported FASTA
bytes must pass before the common E023 secondary completeness/impurity reader.
"""
import argparse
import csv
import hashlib
import json
from pathlib import Path
import re
import sys
import time
ROOT=Path(__file__).absolute().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'scripts')]
from e009_common import binding,fasta
from e009_evaluate import read_partition
from e012_marker_audit import verify_truth
from dl_binner.density.bin_quality import summarize


def fasta_contract(path,expected,source,seen):
    """Stream one retained FASTA, checking exact membership and original DNA hashes."""
    observed=set();bp=0
    for q,dna in fasta(path):
        if q not in expected or q in seen or q not in source:
            raise ValueError('Retained FASTA membership/duplicate differs')
        if (len(dna),hashlib.sha256(dna.encode()).hexdigest())!=source[q]:
            raise ValueError('Retained FASTA original DNA differs')
        observed.add(q);seen.add(q);bp+=len(dna)
    if observed!=set(expected):raise ValueError('Retained FASTA omitted assigned DNA')
    return dict(contigs=len(observed),bp=bp,binding=binding(path))


def run(output):
    """Check retained contracts, then write per-bin and secondary tier tables locally."""
    started=time.monotonic();output=Path(output);output.mkdir(parents=True,exist_ok=False)
    r=ROOT/'artifacts/e011-cached-grouping-reference/recovery-20261017';members=r/'members'
    accepted=json.loads((ROOT/'experiments/E011-cached-grouping-reference/review.json').read_text())
    old=json.loads((r/'local-review-v3/review.json').read_text())
    if binding(r/'local-review-v3/review.json')!=accepted['analysis_bindings']['local-review-v3/review.json']:
        raise ValueError('Accepted MetaBAT review differs')
    recovery=json.loads((ROOT/'experiments/E011-cached-grouping-reference/recovery-observed.json').read_text())
    inventory=members/'collection-inventory.json'
    if binding(inventory)!=recovery['archive']['inventory']:raise ValueError('Accepted original member inventory differs')
    files=json.loads(inventory.read_text())['files']
    verified={}
    for n,b in files.items():
        if n.startswith(('metabat-export/','metabat-native/')):
            if binding(members/n)!=b:raise ValueError('Retained MetaBAT member differs: '+n)
            verified[n]=b
    protocol=json.loads((ROOT/'experiments/E011-cached-grouping-reference/protocol.json').read_text())
    if binding(ROOT/'experiments/E011-cached-grouping-reference/protocol.json')!=accepted['protocol']:
        raise ValueError('Original E011 input/protocol differs')
    original=ROOT/'artifacts/e009-gcp-review/20261015/returned/data-stage-v1'
    assembly=original/'parts/assembly/megahit/final.contigs.fa';depth=original/'parts/final/depth.tsv'
    for name,p in [('fasta',assembly),('depth',depth)]:
        if binding(p)!=protocol['inputs'][name]:raise ValueError('Accepted E009 input differs')
    lock=json.loads((ROOT/'experiments/E013-marker-quality/review-lock.json').read_text());truthroot=verify_truth(lock)
    truth=json.loads((truthroot/'truth.json').read_text());targets=json.loads((truthroot/'targets.json').read_text())
    from dl_binner.multiview.views import load
    features=ROOT/'artifacts/e011-cached-grouping-reference/restore-local/candidate/features/features.npz'
    data,meta=load(features)
    ordered=json.loads((ROOT/'experiments/E010-coherent-prototype/candidate-lock.json').read_text())['ordered_depth_columns']
    if meta['samples']!=old['depth_columns']or meta['samples']!=ordered or meta['fasta_sha256']!=binding(assembly)['sha256']:
        raise ValueError('E009 ordered measured-depth/assembly identity differs')
    ids=truth['ordered_contig_ids']
    if data['ids'].tolist()!=ids or len(ids)!=145702 or sum(int(n)for n in data['lengths'])!=231678157:
        raise ValueError('Complete E009 truth/feature axes differ')
    source={q:(len(dna),hashlib.sha256(dna.encode()).hexdigest())for q,dna in fasta(assembly)}
    if list(source)!=ids or [source[q][1]for q in ids]!=data['sequence_sha256'].tolist():
        raise ValueError('Complete source DNA differs')
    rows,assignments=read_partition(members/'metabat-export/assignments.tsv',truth)
    checks={};seen=set();native_seen=set()
    for p in sorted((members/'metabat-export').glob('*.fna')):
        expected={v['contig_id']for v in rows if (v['bin_id']==p.stem if p.stem.startswith('bin_')else v['status']==p.stem)}
        checks[p.name]=fasta_contract(p,expected,source,seen)
        if p.stem.startswith('bin_'):
            number=p.stem.removeprefix('bin_');native=members/'metabat-native'/('bin.'+number+'.fa')
            checks[native.name]=fasta_contract(native,expected,source,native_seen)
    if seen!=set(ids)or native_seen!={q for q,b in assignments.items()if b is not None}:
        raise ValueError('Complete native/export DNA accounting differs')
    table=summarize(({**truth['contigs'][q],'id':q}for q in ids),assignments,truth['reference_axis'],targets['genome_lengths'],targets['targets'])
    if table['assigned_bp']!=old['arms']['metabat']['accounting']['statuses']['assigned']['bp']:
        raise ValueError('Retained assigned DNA total differs')
    summary={k:v for k,v in table.items()if k!='bins'}
    summary['target_at_least_200kb_counts']=dict(__import__('collections').Counter(x['tier']for x in table['bins']if x['target']and x['bp']>=200000))
    with (output/'bin-quality.tsv').open('x')as f:
        writer=csv.DictWriter(f,fieldnames=list(table['bins'][0]),delimiter='\t',lineterminator='\n');writer.writeheader();writer.writerows(table['bins'])
    value=dict(status='SUCCESS_SECONDARY_RETAINED_METABAT_CONTEXT',source=binding(__file__),original_E011_review=binding(ROOT/'experiments/E011-cached-grouping-reference/review.json'),input_protocol=binding(ROOT/'experiments/E011-cached-grouping-reference/protocol.json'),original_inventory=binding(inventory),verified_members=verified,FASTA_contracts=checks,complete_contigs=len(ids),complete_bp=231678157,ordered_depth_columns=ordered,truth_manifest=binding(truthroot/'manifest.json'),full_targets=156,full_reference_bp=554661890,N_quarantine_percent=3.3034,secondary=summary,bins=table['bins'],retained_primary_summary=accepted['summary']['metabat'],primary_rescored=False,tool_rerun=False,formal_MIMAG_HQ=False,elapsed_seconds=time.monotonic()-started,limits='Native whole-tool context: seed cutoff 2500 bp, later eligibility 1000 bp, cvExt variance=mean assumption; not matched cutoff/encoder or formal MAG-quality certification. Confirmed foreign-origin and unresolved DNA remain separate.')
    (output/'review.json').write_text(json.dumps(value,indent=2,allow_nan=False)+'\n')
    print(json.dumps(dict(status=value['status'],secondary=summary,elapsed_seconds=value['elapsed_seconds'])),flush=True)
    return value

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',required=True,type=Path);a=p.parse_args();run(a.output)
