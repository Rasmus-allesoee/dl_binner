#!/usr/bin/env python3
"""Create a source-blind oral FASTA while preserving every verified nonempty base.

The publisher anonymous FASTA omits exactly the two zero-bp raw GSA records.
Opaque IDs depend only on the frozen dataset namespace and anonymous PC ID, never
genome/taxonomy/coordinates. The compressed reverse join stays outside all model
input paths. Original inputs and provisional truth are not modified or admitted.
"""
import gzip
import hashlib
import json
from pathlib import Path
import sqlite3
import sys
import time

sys.path.insert(0,str(Path(__file__).absolute().parent))
from e014_acquire import ROOT,guard,hashes
from e014_oral_audit import fasta

NAMESPACE='CAMI-II-Toy-HMB-oral-E014-opaque-v1'


def opaque(anonymous):
    """Return a deterministic full SHA256 ID independent of any source label."""
    if not anonymous or any(c.isspace() for c in anonymous):raise ValueError('Invalid anonymous ID')
    return 'C'+hashlib.sha256((NAMESPACE+'\0'+anonymous).encode()).hexdigest()


def prepare(root=ROOT):
    """Stream verified anonymous DNA and publish a separate checksum-bound origin join."""
    root=Path(root);clock=json.loads((root/'acquisition-clock.json').read_text());guard(root,clock)
    source=root/'oral/gsa.tsv.gz';receipt=json.loads(source.with_suffix(source.suffix+'.receipt.json').read_text())
    if hashes(source)!=receipt['hashes']:raise ValueError('Anonymous FASTA bytes changed')
    db=sqlite3.connect((root/'admission-v1/joins.sqlite').absolute().as_uri()+'?mode=ro',uri=True)
    review=json.loads((root/'admission-v1/review.json').read_text())
    if review['fixed_unmatched'] or review['anonymous_FASTA'].get('no_mapping',0):raise ValueError('Anonymous join remains unresolved')
    dest=root/'model-input-v1';dest.mkdir(exist_ok=False)
    truth=root/'source-blind-join-v1.tsv.gz';seen=set();total=0;rows=0;started=time.monotonic()
    with (dest/'oral.fna').open('x')as output,gzip.open(truth,'xt')as labels:
        labels.write('opaque_id\tanonymous_id\tgenome\ttaxon\trecord\tstart_1based\tend_inclusive\tDNA_sha256\n')
        for ident,dna in fasta(source):
            row=db.execute('SELECT genome,tax,record,start,end,sha FROM fixed WHERE anon=?',(ident,)).fetchone()
            sha=hashlib.sha256(dna.encode()).hexdigest()
            if not dna or row is None or sha!=row[-1] or len(dna)!=row[4]-row[3]+1:raise ValueError('Verified anonymous/source join differs')
            name=opaque(ident)
            if name in seen:raise ValueError('Opaque ID collision/duplicate')
            seen.add(name);output.write('>'+name+'\n'+dna+'\n')
            labels.write('\t'.join(map(str,[name,ident,*row]))+'\n');total+=len(dna);rows+=1
            if rows%50000==0:
                output.flush();guard(root,clock);print('OPAQUE_DNA',rows,total,flush=True)
    db.close()
    if total!=review['supplied_GSA']['bp'] or rows!=review['fixed_rows']:raise ValueError('Complete DNA/contig accounting differs')
    result=dict(status='INPUT_DERIVATIVE_VERIFIED_TRUTH_NOT_ADMITTED',namespace=NAMESPACE,
        anonymous_input=receipt['hashes'],model_input=hashes(dest/'oral.fna'),reverse_join=hashes(truth),
        records=rows,bp=total,original_empty_records=review['examples'],
        zero_bp_record_policy='Two original empty records retained in raw input and this accounting; no DNA removed or invented.',
        training_boundary='Only model-input-v1/oral.fna enters features; source-blind-join-v1.tsv.gz is evaluator-only.',
        seconds=time.monotonic()-started,original_clock=clock)
    (dest/'receipt.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n');guard(root,clock)
    print('OPAQUE_COMPLETE',rows,total,flush=True)
    return result


if __name__=='__main__':prepare()
