#!/usr/bin/env python3
"""Derive/review a separately named skin provided-origin oracle and blind FASTA.

Unique competitive alignment truth, ANI independence, host links and assembly-
error performance are not admitted. Labels/reverse joins never enter model paths.
"""
import argparse
from collections import Counter,defaultdict
import gzip,hashlib,itertools,json,sqlite3,sys,time
from pathlib import Path
sys.path.insert(0,str(Path(__file__).absolute().parent))
from e021_skin import opaque,write
from e021_acquire import guard,hashes
from e014_oral_audit import fasta
from e014_oral_truth import acgt_intervals,validate_row


def derive(root):
    """Consume only reviewed exact-source/index bytes, retaining all provided targets."""
    root=Path(root);clock=json.loads((root/'acquisition-clock.json').read_text());guard(root,clock);src=root/'admission-v2'
    audit=json.loads((src/'review.json').read_text());pop=json.loads((src/'population.json').read_text());den=json.loads((src/'denominators.json').read_text());raw=json.loads((src/'references.json').read_text())
    if audit['status']!='EXACT_SOURCE_REVIEWED_TRUTH_PROVISIONAL'or audit['fixed_unmatched_or_unverified']or audit['observed_non_skin_positive']:raise ValueError('Exact source/sample origin audit incomplete')
    if any(z['raw_bp']!=z['exact_DNA_deduplicated_bp']for z in den.values()):raise ValueError('Within-genome exact duplicate records require a separate denominator/alias policy')
    if any(pop['domains'][g]=='unknown'for g in pop['skin_positive_genomes']):raise ValueError('Positive cellular taxonomy unresolved')
    references={};full=defaultdict(int);by_hash=defaultdict(set)
    for z in raw:
        for g in z['genomes']:
            key=g+'|'+z['record']
            if key in references:raise ValueError('Duplicate provided genome/record axis')
            references[key]=dict(genome=g,record=z['record'],length=z['bp'],molecule=z['molecule_header_evidence'],host='not inferred',canonical_sha256=z['canonical_sha256']);full[g]+=z['bp'];by_hash[z['canonical_sha256']].add(g)
    if set(full)!=set(den)or any(full[g]!=den[g]['raw_bp']for g in full):raise ValueError('Full-reference source/denominator disagreement')
    targets={g:full[g]for g in sorted(pop['skin_positive_genomes'])if pop['domains'][g]in ['2','2157','2759']}
    shared={g+'|'+z['record']for z in raw for g in z['genomes']if len(by_hash[z['canonical_sha256']])>1}
    out=root/'truth-origin-v1';out.mkdir(exist_ok=False);model=root/'model-input-v1';model.mkdir(exist_ok=False)
    db=sqlite3.connect((src/'joins.sqlite').absolute().as_uri()+'?mode=ro',uri=True);db.execute('PRAGMA cache_size=-65536')
    dup={s for s, in db.execute('SELECT sha FROM fixed GROUP BY sha HAVING count(distinct genome)>1')};counts=Counter();seen=set()
    with gzip.open(out/'queries.jsonl.gz','xt')as queries,(model/'skin.fna').open('x')as dnaout,gzip.open(out/'reverse-join.tsv.gz','xt')as reverse:
        reverse.write('opaque_id\tanonymous_id\tgenome\trecord\tstart_1based\tend_inclusive\tDNA_sha256\n')
        for anon,dna in fasta(root/'skin/gsa.tsv.gz'):
            row=db.execute('SELECT genome,record,start,end,sha,matched,verified FROM fixed WHERE anon=?',(anon,)).fetchone()
            if not row or row[-2:]!=(1,1)or row[4]!=hashlib.sha256(dna.encode()).hexdigest()or row[3]-row[2]+1!=len(dna):raise ValueError('Verified original DNA/origin changed')
            g,r,a,b,sha,_,_=row;ident=opaque(anon)
            if ident in seen:raise ValueError('Opaque ID collision/duplicate')
            seen.add(ident);rid=g+'|'+r;runs=acgt_intervals(dna,a-1)
            q=dict(id=ident,length=len(dna),genome=g,reference=rid,start=a-1,end=b,source_intervals=runs,quarantined_bp=len(dna)-sum(y-x for x,y in runs),shared_forward_query=sha in dup,shared_complete_reference=rid in shared,DNA_sha256=sha)
            validate_row(q,references);queries.write(json.dumps(q,separators=(',',':'))+'\n');dnaout.write('>'+ident+'\n'+dna+'\n');reverse.write('\t'.join(map(str,[ident,anon,g,r,a,b,sha]))+'\n')
            counts['queries']+=1;counts['bp']+=len(dna);counts['quarantined_bp']+=q['quarantined_bp'];counts['known_shared_queries']+=int(q['shared_forward_query']or q['shared_complete_reference'])
            if counts['queries']%50000==0:queries.flush();dnaout.flush();guard(root,clock);print('SKIN_ORIGIN_DERIVE',counts['queries'],flush=True)
    db.close()
    if counts['queries']!=audit['fixed_rows']or counts['bp']!=audit['anonymous']['bp']:raise ValueError('Complete anonymous/model input accounting differs')
    write(out/'references.json',references);write(out/'targets.json',targets)
    policy=dict(name='CAMI-II-HMB-skin-provided-origin-oracle-v1',unique_support_admitted=False,target_policy='Every positive skin cellular source, complete provided genome/record lengths including zero origins; every provided competitor retained',source_join='Exact anonymous/source bytes, one-based inclusive -> zero-based half-open coordinates; no clipping or invented circular/host aliases',quarantine='Every non-ACGT query base localized and excluded from supported spans; full provided reference lengths remain',known_shared='Exact cross-origin query/full-reference alternatives flagged; sensitivity masks both, not an exhaustive near-homology mask',no_depth_or_assembly_errors=True,namespace='CAMI-II-Toy-HMB-skin-E021-opaque-v1')
    write(out/'policy.json',policy)
    files={p.name:hashes(p)for p in out.iterdir()if p.is_file()};files['model-input-v1/skin.fna']=hashes(model/'skin.fna')
    result=dict(status='DERIVED_PENDING_INDEPENDENT_ORIGIN_REVIEW',counts=dict(counts),provided_reference_genomes=len(full),provided_reference_bp=sum(full.values()),targets=len(targets),full_target_bp=sum(targets.values()),zero_origin_targets=[g for g in targets if not den[g]['origin_queries']],files=files,original_zero_bp_records=audit['GSA'].get('zero_bp_records',0),policy=policy,source_review=hashes(src/'review.json'))
    write(out/'derivation.json',result);guard(root,clock);return result


def review(root):
    """Independently reread every blind query/DNA and target sum without any score."""
    from decimal import Decimal
    root=Path(root);clock=json.loads((root/'acquisition-clock.json').read_text());guard(root,clock);out=root/'truth-origin-v1';src=root/'admission-v2'
    d=json.loads((out/'derivation.json').read_text());references=json.loads((out/'references.json').read_text());targets=json.loads((out/'targets.json').read_text());pop=json.loads((src/'population.json').read_text());den=json.loads((src/'denominators.json').read_text())
    for name,b in d['files'].items():
        path=root/name if name.startswith('model-input-v1/')else out/name
        if hashes(path)!=b:raise ValueError('Origin artifact member changed')
    sums=defaultdict(int)
    for ref in references.values():sums[ref['genome']]+=ref['length']
    if any(sums[g]!=n for g,n in targets.items())or set(targets)!={g for g in pop['skin_positive_genomes']if pop['domains'][g]in ['2','2157','2759']}:raise ValueError('Target axes/full denominators differ')
    samples={}
    for i in pop['skin_sample_indices']:
        values={g:Decimal(v)for g,v in (l.split('\t')for l in(root/'metadata'/f'abundance{i}.tsv').read_text().splitlines())}
        samples[i]={g for g,v in values.items()if v>0}
        if sorted(samples[i])!=pop['samples'][str(i)]['positive']:raise ValueError('Exact Decimal-positive sample join differs')
    if set().union(*samples.values())!=set(pop['skin_positive_genomes']):raise ValueError('Full ten-sample positive population differs')
    ref_hashes=defaultdict(set)
    for ref in references.values():ref_hashes[ref['canonical_sha256']].add(ref['genome'])
    shared_refs={key for key,z in references.items()if len(ref_hashes[z['canonical_sha256']])>1}
    counts=Counter();origin_counts=Counter();lengths=defaultdict(Counter);seen=set();db=sqlite3.connect((src/'joins.sqlite').absolute().as_uri()+'?mode=ro',uri=True)
    shared_queries={z for z, in db.execute('SELECT sha FROM fixed GROUP BY sha HAVING count(distinct genome)>1')}
    with gzip.open(out/'queries.jsonl.gz','rt')as stream,gzip.open(out/'reverse-join.tsv.gz','rt')as labels:
        if not labels.readline().startswith('opaque_id\t'):raise ValueError('Reverse join header differs')
        for raw,row,line in itertools.zip_longest(fasta(root/'model-input-v1/skin.fna'),stream,labels):
            if raw is None or row is None or line is None:raise ValueError('DNA/truth/reverse join length differs')
            ident,dna=raw;q=json.loads(row);fields=line.rstrip('\n').split('\t')
            if len(fields)!=7 or fields[0]!=ident or opaque(fields[1])!=ident or ident!=q['id']or ident in seen:raise ValueError('Source-blind ID/reverse mapping differs')
            seen.add(ident);sha=hashlib.sha256(dna.encode()).hexdigest();support=validate_row(q,references)
            source=db.execute('SELECT genome,record,start,end,sha FROM fixed WHERE anon=?',(fields[1],)).fetchone()
            if (q['genome'],q['reference'],q['start'],q['end'])!=(fields[2],fields[2]+'|'+fields[3],int(fields[4])-1,int(fields[5]))or q['shared_forward_query']!=(sha in shared_queries)or q['shared_complete_reference']!=(q['reference']in shared_refs)or source!=(fields[2],fields[3],int(fields[4]),int(fields[5]),fields[6])or sha!=fields[6]or sha!=q['DNA_sha256']or q['source_intervals']!=acgt_intervals(dna,q['start']):raise ValueError('Exact independent source/coordinate/quarantine join differs')
            n=len(dna);label='<500'if n<500 else'500-999'if n<1000 else'1000-2499'if n<2500 else'2500-9999'if n<10000 else'>=10000'
            lengths[label]['contigs']+=1;lengths[label]['bp']+=n
            counts['queries']+=1;counts['bp']+=len(dna);counts['quarantined_bp']+=len(dna)-support;counts['known_shared_queries']+=int(q['shared_forward_query']or q['shared_complete_reference']);origin_counts[q['genome']]+=1
            if counts['queries']%50000==0:guard(root,clock);print('SKIN_ORIGIN_REVIEW',counts['queries'],flush=True)
    from e014_origin_union import union_length
    availability={g:0 for g in targets};current=None;spans=[]
    def finish():
        if current is not None:
            g,r=current
            if g not in availability:raise ValueError('Observed DNA outside admitted positive targets')
            availability[g]+=union_length(spans)
    for g,r,a,b in db.execute('SELECT genome,record,start,end FROM fixed ORDER BY genome,record,start,end'):
        if current!=(g,r):finish();current=(g,r);spans=[]
        if not 1<=a<=b<=references[g+'|'+r]['length']:raise ValueError('Availability union outside full source')
        spans.append((a,b))
    finish();db.close()
    if any(availability[g]>targets[g]for g in targets):raise ValueError('Source union exceeds full denominator')
    if dict(counts)!=d['counts']or any(origin_counts[g]!=z['origin_queries']for g,z in den.items()):raise ValueError('Complete origin/zero-origin accounting differs')
    result=dict(status='ADMITTED_PROVIDED_ORIGIN_ORACLE_ONLY',counts=dict(counts),targets=len(targets),full_target_bp=sum(targets.values()),provided_competitor_genomes=len(den),length_strata={k:dict(v)for k,v in lengths.items()},raw_source_union_bp=sum(availability.values()),raw_source_union_per_target=availability,availability_is_not_binner_score=True,zero_origin_targets=[g for g in targets if not origin_counts[g]],original_zero_bp_records=d['original_zero_bp_records'],derivation=hashes(out/'derivation.json'),limits=['Unique competitive/near-homology support unadmitted; origin labels do not prove sequence identifiability.','Molecule/host annotations incomplete; use provided source grouping, no biological host or circular alias inference.','Exact/near/pretraining overlap limits unseen-genome claims.','Sequence-only GSA has no assembly errors or measured contig-level depth.','No candidate/community/confirmation score or labels in training.'])
    write(out/'independent-admission.json',result);guard(root,clock);return result

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('operation',choices=['derive','review']);p.add_argument('--root',type=Path,required=True);a=p.parse_args();print(json.dumps((derive if a.operation=='derive'else review)(a.root)),flush=True)
