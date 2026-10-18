#!/usr/bin/env python3
"""Derive/review/evaluate explicitly provided-origin oral GSA truth, never features.

This oracle is distinct from E009 unique-alignment support. Publisher origins are
sequence-verified; identical/homologous DNA is not claimed uniquely identifiable.
All DNA, unknowns, source alternatives, full reference lengths and non-ACGT
quarantine stay explicit. No aligner, binner fit or score-selected rule is used.
"""
import argparse
from collections import Counter,defaultdict
import csv
import gzip
import hashlib
from itertools import zip_longest
import json
from pathlib import Path
import re
import sqlite3
import sys

sys.path.insert(0,str(Path(__file__).absolute().parent))
from e014_acquire import ROOT,guard,hashes
from e014_oral_audit import fasta
from e014_opaque_input import opaque
from e009_truth import union


def acgt_intervals(dna,source_start):
    """Map localized ACGT runs to zero-based half-open provided-reference spans."""
    return [[source_start+m.start(),source_start+m.end()]for m in re.finditer('[ACGT]+',dna)]


def validate_row(row,references):
    """Refuse malformed source/quarantine rows without clipping or unknown fallback."""
    if not isinstance(row['id'],str)or not row['id']or type(row['length'])is not int or row['length']<=0:
        raise ValueError('Invalid truth query ID/length')
    if type(row['quarantined_bp'])is not int or row['quarantined_bp']<0:raise ValueError('Invalid quarantined DNA count')
    if any(type(row[k])is not bool for k in ['shared_forward_query','shared_complete_reference']):raise ValueError('Invalid ambiguity flag')
    runs=row['source_intervals']
    if any(len(x)!=2 or any(type(v)is not int for v in x)for x in runs):raise ValueError('Invalid support coordinates')
    support=sum(b-a for a,b in runs)
    if row['genome'] is None:
        if runs or row['reference'] is not None or support:raise ValueError('Unknown query has fabricated support')
    else:
        ref=references.get(row['reference'])
        if ref is None or ref['genome']!=row['genome']:raise ValueError('Truth genome/reference join differs')
        if any(type(row[k])is not int for k in ['start','end'])or not 0<=row['start']<row['end']<=ref['length'] or row['end']-row['start']!=row['length']:
            raise ValueError('Truth full-reference coordinates differ')
        previous=row['start']
        for a,b in runs:
            if not previous<=a<b<=row['end']:raise ValueError('Truth supported intervals overlap/outside query')
            previous=b
    if support+row['quarantined_bp']!=row['length']:raise ValueError('Truth complete DNA/quarantine accounting differs')
    return support


def derive(root,clock_path,output):
    """Stream actual anonymous DNA/SQLite origins into a fresh compact oracle artifact."""
    root,output=Path(root),Path(output);clock=json.loads(Path(clock_path).read_text());guard(root,clock)
    policy_path=Path(__file__).absolute().parents[1]/'experiments/E014-multiview-reconstruction/oral-truth-policy.json'
    source=root/'source-validation-v2';review=json.loads((source/'review.json').read_text())
    if review['status']!='SOURCE_VALIDATED_TRUTH_STILL_PROVISIONAL':raise ValueError('Accepted exact-source audit missing')
    denominators=json.loads((source/'denominators.json').read_text());available=json.loads((root/'origin-union-v1.json').read_text())
    reference_rows=json.loads((source/'references.json').read_text());references={};shared=set()
    for group in review['exact_duplicate_record_groups']:
        for row in group:
            for g in row['genomes']:shared.add((g,row['record']))
    for row in reference_rows:
        for genome in row['genomes']:
            rid=genome+'|'+row['record']
            if rid in references:raise ValueError('Duplicate reference identity')
            references[rid]=dict(genome=genome,record=row['record'],length=row['bp'],molecule='unannotated')
    full=defaultdict(int)
    for row in references.values():full[row['genome']]+=row['length']
    if any(full[g]!=d['raw_bp']or d['raw_bp']!=d['exact_DNA_deduplicated_bp']for g,d in denominators.items()):
        raise ValueError('Provided full-reference denominator contract differs')
    targets={g:full[g]for g in available['genomes']}
    db=sqlite3.connect((root/'admission-v1/joins.sqlite').absolute().as_uri()+'?mode=ro',uri=True)
    duplicated={sha for sha, in db.execute('SELECT sha FROM fixed GROUP BY sha HAVING count(distinct genome)>1')}
    output.mkdir(exist_ok=False);counts=Counter();seen=set()
    with gzip.open(output/'rows.jsonl.gz','xt')as out:
        for anon,dna in fasta(root/'oral/gsa.tsv.gz'):
            record=db.execute('SELECT genome,record,start,end,sha FROM fixed WHERE anon=?',(anon,)).fetchone()
            if record is None:raise ValueError('Unknown anonymous origin')
            g,r,a,b,sha=record;ident=opaque(anon)
            if ident in seen or g not in targets or hashlib.sha256(dna.encode()).hexdigest()!=sha:
                raise ValueError('Origin/DNA/opaque axis differs')
            seen.add(ident);runs=acgt_intervals(dna,a-1);support=sum(y-x for x,y in runs)
            row=dict(id=ident,length=len(dna),genome=g,reference=g+'|'+r,start=a-1,end=b,
                source_intervals=runs,quarantined_bp=len(dna)-support,
                shared_forward_query=sha in duplicated,shared_complete_reference=(g,r)in shared)
            validate_row(row,references);out.write(json.dumps(row,separators=(',',':'))+'\n')
            counts['contigs']+=1;counts['bp']+=len(dna);counts['quarantined_bp']+=len(dna)-support
            counts['known_shared_contigs']+=bool(row['shared_forward_query']or row['shared_complete_reference'])
            if row['shared_forward_query']or row['shared_complete_reference']:counts['known_shared_bp']+=len(dna)
            if counts['contigs']%50000==0:guard(root,clock);print('ORIGIN_TRUTH_ROWS',dict(counts),flush=True)
    db.close()
    model=json.loads((root/'model-input-v1/receipt.json').read_text())
    if counts['contigs']!=model['records']or counts['bp']!=model['bp']:raise ValueError('Full origin input DNA changed')
    metadata=dict(kind='E014_provided_source_origin_oracle',version=1,admitted=False,policy=hashes(policy_path),
        rows=hashes(output/'rows.jsonl.gz'),model_input=model['model_input'],reverse_join=model['reverse_join'],
        references=references,targets=targets,counts=dict(counts),source_proof=hashes(source/'review.json'),
        source_references=hashes(source/'references.json'),original_zero_bp_records=model['original_empty_records'],
        scope='Provided-source origin; no unique-sequence support, physical host or MAG-quality claim.',validation_clock=clock)
    (output/'manifest.json').write_text(json.dumps(metadata,indent=2,sort_keys=True)+'\n');guard(root,clock)
    print('ORIGIN_TRUTH_DERIVED',dict(counts),flush=True)
    return metadata


def review(root,artifact,clock_path):
    """Independently check every model DNA/reverse-join/truth row before admission."""
    root,artifact=Path(root),Path(artifact);clock=json.loads(Path(clock_path).read_text());guard(root,clock)
    metadata=json.loads((artifact/'manifest.json').read_text());references=metadata['references'];counts=Counter();genomes=set()
    source=root/'source-validation-v2';source_review=json.loads((source/'review.json').read_text())
    if hashes(source/'review.json')!=metadata['source_proof']or hashes(source/'references.json')!=metadata['source_references']:
        raise ValueError('Accepted source proof bytes changed')
    policy=Path(__file__).absolute().parents[1]/'experiments/E014-multiview-reconstruction/oral-truth-policy.json'
    if hashes(policy)!=metadata['policy']:raise ValueError('Prospective origin policy changed')
    expected_references={g+'|'+r['record']:dict(genome=g,record=r['record'],length=r['bp'],molecule='unannotated')
        for r in json.loads((source/'references.json').read_text())for g in r['genomes']}
    if references!=expected_references:raise ValueError('Independent complete reference axis differs')
    shared={(g,r['record'])for group in source_review['exact_duplicate_record_groups']for r in group for g in r['genomes']}
    db=sqlite3.connect((root/'admission-v1/joins.sqlite').absolute().as_uri()+'?mode=ro',uri=True)
    duplicated={sha for sha, in db.execute('SELECT sha FROM fixed GROUP BY sha HAVING count(distinct genome)>1')};db.close()
    if hashes(artifact/'rows.jsonl.gz')!=metadata['rows']:raise ValueError('Derived oracle bytes changed')
    if hashes(root/'model-input-v1/oral.fna')!=metadata['model_input']or hashes(root/'source-blind-join-v1.tsv.gz')!=metadata['reverse_join']:
        raise ValueError('Independent model DNA/source join bytes changed')
    with gzip.open(artifact/'rows.jsonl.gz','rt')as truth,gzip.open(root/'source-blind-join-v1.tsv.gz','rt')as labels:
        joined=csv.DictReader(labels,delimiter='\t')
        for dna_row,label,raw in zip_longest(fasta(root/'model-input-v1/oral.fna'),joined,truth):
            if dna_row is None or label is None or raw is None:raise ValueError('Oracle/model/source row count differs')
            ident,dna=dna_row;row=json.loads(raw);g=label['genome'];record=label['record'];start=int(label['start_1based'])-1;end=int(label['end_inclusive'])
            if (ident!=label['opaque_id']or row['id']!=ident or ident!=opaque(label['anonymous_id'])
                    or row['genome']!=g or row['reference']!=g+'|'+record or row['length']!=len(dna)
                    or row['start']!=start or row['end']!=end or hashlib.sha256(dna.encode()).hexdigest()!=label['DNA_sha256']):
                raise ValueError('Independent exact DNA/origin/coordinate join differs')
            # Independent complement-of-ambiguity construction, not the writer's
            # positive-regex helper; every ambiguous position remains in bin DNA.
            runs=[];at=0
            for m in re.finditer('[^ACGT]+',dna):
                if m.start()>at:runs.append([start+at,start+m.start()])
                at=m.end()
            if at<len(dna):runs.append([start+at,start+len(dna)])
            if row['source_intervals']!=runs:raise ValueError('Independent non-ACGT quarantine differs')
            if row['shared_forward_query']!=(label['DNA_sha256']in duplicated)or row['shared_complete_reference']!=((g,record)in shared):
                raise ValueError('Independent ambiguity flag differs')
            support=validate_row(row,references);counts['contigs']+=1;counts['bp']+=len(dna);counts['quarantined_bp']+=len(dna)-support;genomes.add(g)
            counts['known_shared_contigs']+=bool(row['shared_forward_query']or row['shared_complete_reference'])
            if row['shared_forward_query']or row['shared_complete_reference']:counts['known_shared_bp']+=len(dna)
            if counts['contigs']%50000==0:guard(root,clock);print('ORIGIN_TRUTH_REVIEW',counts['contigs'],flush=True)
    first=json.loads((root/'admission-v1/review.json').read_text());available=json.loads((root/'origin-union-v1.json').read_text())
    if dict(counts)!=metadata['counts']or counts['quarantined_bp']!=first['supplied_GSA']['ambiguous_base_bp']:
        raise ValueError('Independent complete source population/quarantine differs')
    if genomes!={r['genome']for r in first['observed_genomes']}or metadata['targets']!={g:r['reference_bp']for g,r in available['genomes'].items()}:
        raise ValueError('Independent genome target population differs')
    if len(genomes)!=available['GSA_observed_genomes']or sum(metadata['targets'].values())!=available['full_positive_reference_bp']:
        raise ValueError('Independent full provided denominators differ')
    result=dict(admitted=True,mode='provided_source_origin_oracle',unique_sequence_support_admitted=False,
        counts=dict(counts),observed_genomes=len(genomes),targets=len(metadata['targets']),reference_bp=sum(metadata['targets'].values()),
        manifest=hashes(artifact/'manifest.json'),scope=metadata['scope'],
        limits=['Partial/reverse/circular/near competitors remain unlocalized; known-shared-mask is only a sensitivity.',
                'Source assembly groups are provided units; molecule/host annotations and pretraining overlap remain unknown.',
                'Oral origin-R95 and E009 conservative R95 are separate truth scopes; no pooled quality or unseen-genome claim.'],validation_clock=clock)
    (artifact/'admission.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n');guard(root,clock)
    print('ORIGIN_TRUTH_ADMITTED',dict(counts),flush=True);return result


def recovery(rows,assignments,references,targets,min_bin=200000,purity=.95,mask_known_shared=False):
    """Count full-bin origin purity and duplicate-safe best-bin reference unions.

    This pure adapter is also exercised on tiny real fixture rows. Unknown/non-
    target/unassigned DNA is retained; unknown or masked support cannot add credit.
    """
    lengths=defaultdict(int)
    for ref in references.values():lengths[ref['genome']]+=ref['length']
    if any(lengths[g]!=n or n<=0 for g,n in targets.items()):raise ValueError('Full provided target denominator differs')
    bin_bp=defaultdict(int);supported=defaultdict(lambda:defaultdict(int));loci=defaultdict(list);available=defaultdict(list);seen=set();accounting=Counter()
    for row in rows:
        support=validate_row(row,references);ident=row['id']
        if ident in seen or ident not in assignments:raise ValueError('Incomplete/duplicate query axis')
        seen.add(ident);label=assignments[ident];accounting['contigs']+=1;accounting['bp']+=row['length'];accounting['quarantined_bp']+=row['quarantined_bp']
        runs=[]if mask_known_shared and(row['shared_forward_query']or row['shared_complete_reference'])else row['source_intervals']
        if row['reference']is not None:available[row['reference']].extend(runs)
        if label is None:accounting['unassigned_bp']+=row['length'];continue
        bin_bp[label]+=row['length']
        if runs:
            supported[label][row['genome']]+=sum(b-a for a,b in runs);loci[(label,row['reference'])].extend(runs)
    if seen!=set(assignments):raise ValueError('Extra query assignment axis')
    merged={key:sum(b-a for a,b in union(spans))for key,spans in loci.items()};represented=defaultdict(int)
    for rid,spans in available.items():represented[references[rid]['genome']]+=sum(b-a for a,b in union(spans))
    candidates=defaultdict(list);by_bin_genome=defaultdict(int)
    for (label,rid),n in merged.items():by_bin_genome[(label,references[rid]['genome'])]+=n
    for label,gcounts in supported.items():
        if bin_bp[label]<min_bin:continue
        for g,n in gcounts.items():
            if g not in targets or n/bin_bp[label]<purity:continue
            recovered=by_bin_genome[(label,g)]
            if recovered>targets[g]:raise ValueError('Origin source union exceeds full reference')
            candidates[g].append((recovered,label,n/bin_bp[label]))
    rows=[]
    for g,n in sorted(targets.items()):
        best=sorted(candidates[g],key=lambda x:(-x[0],x[1]))[0]if candidates[g]else(0,None,None)
        rows.append(dict(genome=g,reference_bp=n,assembly_confirmed_bp=represented[g],best_bin=best[1],confirmed_purity=best[2],
            recovered_bp=best[0],whole_reference_R95=best[0]/n,assembly_conditional_R95=best[0]/represented[g]if represented[g]else 0.))
    return dict(recovery=rows,accounting=dict(accounting),bin_DNA_bp=dict(bin_bp),
        recovery_summary=dict(targets=len(rows),reference_bp=sum(targets.values()),bp_weighted_R95=sum(x['recovered_bp']for x in rows)/sum(targets.values()),
                              macro_R95=sum(x['whole_reference_R95']for x in rows)/len(rows),at_least_50_percent=sum(x['whole_reference_R95']>=.5 for x in rows),at_least_90_percent=sum(x['whole_reference_R95']>=.9 for x in rows)),
        mode='provided-origin'if not mask_known_shared else'provided-origin-known-shared-mask sensitivity; not exhaustive uniqueness')


def evaluate(artifact,partition,output):
    """Evaluate only an admitted byte-bound oracle, with complete ordered query axes."""
    artifact,output=Path(artifact),Path(output);metadata=json.loads((artifact/'manifest.json').read_text());admission=json.loads((artifact/'admission.json').read_text())
    if any(p.is_symlink()for p in [artifact/'manifest.json',artifact/'admission.json',artifact/'rows.jsonl.gz',Path(partition)]):raise ValueError('Scientific truth/partition link refused')
    if metadata['kind']!='E014_provided_source_origin_oracle'or not admission['admitted']or admission['manifest']!=hashes(artifact/'manifest.json')or hashes(artifact/'rows.jsonl.gz')!=metadata['rows']:
        raise ValueError('Oracle admission/bytes differ')
    p=json.loads(Path(partition).read_text());ids=p['ids'];labels=p['assignment']
    if len(ids)!=len(labels)or len(set(ids))!=len(ids):raise ValueError('Invalid partition axis')
    if any(b is not None and(type(b)is not int or b< -1)for b in labels):raise ValueError('Invalid partition labels')
    assignments={i:(b if b is not None and b>=0 else None)for i,b in zip(ids,labels)}
    result={}
    for mode,masked in [('origin',False),('known_shared_mask',True)]:
        with gzip.open(artifact/'rows.jsonl.gz','rt')as f:
            def ordered():
                for expected,raw in zip_longest(ids,f):
                    if expected is None or raw is None:raise ValueError('Partition/truth ordered count differs')
                    row=json.loads(raw)
                    if row['id']!=expected:raise ValueError('Partition/truth ordered ID differs')
                    yield row
            result[mode]=recovery(ordered(),assignments,metadata['references'],metadata['targets'],mask_known_shared=masked)
    output.mkdir(exist_ok=False);(output/'evaluation.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    return result


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('operation',choices=['derive','review','evaluate']);p.add_argument('--root',type=Path,default=ROOT)
    p.add_argument('--artifact',type=Path,required=True);p.add_argument('--clock',type=Path);p.add_argument('--partition',type=Path);p.add_argument('--output',type=Path);a=p.parse_args()
    if a.operation=='derive':derive(a.root,a.clock,a.artifact)
    elif a.operation=='review':review(a.root,a.artifact,a.clock)
    else:evaluate(a.artifact,a.partition,a.output)
