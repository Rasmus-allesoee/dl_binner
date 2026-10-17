#!/usr/bin/env python3
"""Stream/index the frozen oral GSA, anonymous FASTA and corrected origin map.

This is source admission, not a binner evaluator. No labels enter features or
training. It preserves malformed/unknown/empty examples and never fills missing
truth by inference. Full source sequences/denominators remain a distinct gate.
"""
from collections import Counter
import csv
from decimal import Decimal
import gzip
import hashlib
import json
from pathlib import Path
import re
import sqlite3
import sys
import time

sys.path.insert(0,str(Path(__file__).absolute().parent))
from e014_acquire import ROOT,guard,hashes

HEADER=re.compile(r'(.+)_from_(\d+)_to_(\d+)_total_(\d+)')
DNA=set('ACGTRYSWKMBDHVN')


def fasta(path):
    """Stream FASTA, preserving empty records for admission rather than discarding them."""
    opening=gzip.open if str(path).endswith('.gz') else open
    with opening(path,'rt') as f:
        name=None;chunks=[]
        for raw in f:
            line=raw.strip()
            if not line:continue
            if line.startswith('>'):
                if name is not None:yield name,''.join(chunks).upper()
                fields=line[1:].split()
                if not fields:raise ValueError('Missing FASTA ID')
                name=fields[0];chunks=[]
            else:
                if name is None:raise ValueError('DNA before FASTA header')
                chunks.append(line)
        if name is None:raise ValueError('Empty FASTA file')
        yield name,''.join(chunks).upper()


def mapping(path):
    """Read the exact seven-field corrected/raw publisher schema with strict coordinates."""
    with Path(path).open() as f:
        expected=['anonymous_contig_id','genome_id','tax_id','contig_id','number_reads','start_position','end_position']
        if f.readline().lstrip('#').split()!=expected:raise ValueError('Unexpected oral mapping header')
        for raw in f:
            a=raw.rstrip('\n').split('\t')
            if len(a)!=7:raise ValueError('Malformed oral mapping row')
            anon,genome,tax,record,count,start,end=a;start,end=int(start),int(end);reads=Decimal(count)
            if not all([anon,genome,tax,record]) or start<1 or end<start or not reads.is_finite() or reads<0:raise ValueError('Invalid oral coordinate/read count')
            yield anon,genome,tax,record,start,end,str(reads)


def populations(metadata,taxonomy_path=None,taxonomy_expected=None):
    """Keep simulator IDs, source paths, tax nodes and oral/GI sample sets separate."""
    m=Path(metadata);sources=dict(line.split('\t',1) for line in (m/'setup-genome_to_id.tsv').read_text().splitlines())
    with (m/'setup-metadata.tsv').open() as f:rows=list(csv.DictReader(f,delimiter='\t'))
    tax={r['genome_ID']:r for r in rows}
    if len(tax)!=len(rows) or set(tax)!=set(sources):raise ValueError('Setup genome/source/tax axes differ')
    oral=[6,7,8,13,14,15,16,17,18,19];gi=sorted(set(range(20))-set(oral));positive={};by_sample={};tax_differences={};missing_profiles={}
    for sample in range(20):
        values={g:Decimal(v) for g,v in (l.split('\t') for l in (m/f'setup-abundance{sample}.tsv').read_text().splitlines())}
        if set(values)!=set(tax) or any(not v.is_finite() or v<0 for v in values.values()):raise ValueError('Abundance sample/source axis differs')
        by_sample[sample]=set(g for g,v in values.items() if v>0)
    for sample in oral:
        path=m/f'setup-taxonomic_profile_{sample}.txt';present={}
        for line in path.read_text().splitlines():
            if not line or line.startswith('@'):continue
            fields=line.split('\t')
            if len(fields)>=6:
                g=fields[5]
                if g not in tax:raise ValueError('Simulator genome/profile ID join differs')
                # The writer emits species-rank profiles even when metadata's
                # NCBI node is a strain. Keep both IDs; do not invent ancestry.
                if fields[0]!=tax[g]['NCBI_ID']:
                    difference=dict(metadata_tax_ID=tax[g]['NCBI_ID'],profile_tax_ID=fields[0],
                                    profile_rank=fields[1],profile_taxpath=fields[2],relationship='unverified')
                    if g in tax_differences and tax_differences[g]!=difference:raise ValueError('Profile taxon relationship changed across samples')
                    tax_differences[g]=difference
                if g in present:raise ValueError('Duplicate profile genome join')
                present[g]=fields[2].split('|')[0]
        missing_profiles[sample]=sorted(by_sample[sample]-set(present))
        for g in by_sample[sample]:
            if g not in present:
                positive.setdefault(g,'unknown');continue
            if g in positive and positive[g] not in ('unknown',present[g]):raise ValueError('Inconsistent cellular superkingdom')
            positive[g]=present[g]
    gi_positive=set().union(*(by_sample[s] for s in gi))
    # Reuse the publisher-linked historical CAMI taxonomy already accepted in
    # E001; do not substitute current taxonomy or equate strain/species nodes.
    if taxonomy_path is None:
        repo=Path(__file__).absolute().parents[1]
        taxonomy_path=repo/'artifacts/e001-taxonomy-reviewed/nodes.dmp'
        member=json.loads((repo/'experiments/E001-coverage-thinning/taxonomy-policy.json').read_text())['members']['nodes.dmp']
        taxonomy_expected=dict(bytes=member['size'],sha256=member['sha256'])
    actual=hashes(taxonomy_path)
    if actual['bytes']!=taxonomy_expected['bytes'] or actual['sha256']!=taxonomy_expected['sha256']:
        raise ValueError('Historical CAMI taxonomy bytes differ')
    parents={}
    with Path(taxonomy_path).open() as f:
        for line in f:
            fields=line.split('|');parents[int(fields[0])]=int(fields[1])
    def lineage(taxon):
        result=[];seen=set();node=int(taxon)
        while node not in seen:
            seen.add(node);result.append(node)
            if node==1:return result
            if node not in parents:raise ValueError('Historical taxonomy node absent: '+str(node))
            node=parents[node]
        raise ValueError('Taxonomy ancestry cycle')
    taxon_joins={}
    for g in positive:
        path=lineage(tax[g]['NCBI_ID']);domain=next((str(x) for x in path if x in [2,2157,2759,10239]),'other')
        if positive[g] not in ['unknown',domain]:raise ValueError('Source/profile cellular taxonomy disagrees')
        positive[g]=domain
        d=tax_differences.get(g)
        if d:d['relationship']='verified_profile_ancestor' if int(d['profile_tax_ID']) in path else 'unresolved_nonancestor'
        taxon_joins[g]=dict(metadata_tax_ID=tax[g]['NCBI_ID'],domain_tax_ID=domain,lineage=path)
    return dict(sources=sources,tax=tax,oral_samples=oral,oral_positive=positive,profile_taxon_differences=tax_differences,
                missing_profile_positive_by_sample=missing_profiles,
                taxonomy=dict(path=str(Path(taxonomy_path).absolute()),bytes=actual['bytes'],sha256=actual['sha256'],source='publisher-linked CAMI toy historical nodes, reused from E001',joins=taxon_joins),
                GI_positive=sorted(gi_positive),exact_simulator_genome_overlap_with_GI=sorted(set(positive)&gi_positive),
                source_basename_overlap_with_GI=sorted({Path(sources[g]).name for g in positive}&{Path(sources[g]).name for g in gi_positive}))


def audit(root=ROOT,taxonomy_path=None,taxonomy_expected=None):
    """Validate every fixed row and both FASTAs with disk-indexed joins and full accounting."""
    root=Path(root);clock=json.loads((root/'acquisition-clock.json').read_text());guard(root,clock)
    acquisition=json.loads((root/'acquisition.json').read_text())
    if acquisition['status']!='SUCCESS':raise ValueError('No completed acquisition')
    for row in acquisition['files']:
        if hashes(row['path'])!=row['hashes']:raise ValueError('Acquired input bytes changed')
    out=root/'admission-v1';out.mkdir(exist_ok=False);db=sqlite3.connect(out/'joins.sqlite')
    db.execute('PRAGMA cache_size=-65536');db.execute('PRAGMA temp_store=FILE')
    db.execute('CREATE TABLE fixed (anon TEXT PRIMARY KEY, genome TEXT, tax TEXT, record TEXT, start INTEGER, end INTEGER, reads TEXT, sha TEXT, matched INTEGER DEFAULT 0)')
    db.execute('CREATE INDEX locus ON fixed(record,start,end)')
    db.execute('CREATE TABLE gsa (id TEXT PRIMARY KEY,length INTEGER,sha TEXT,genome TEXT,tax TEXT,record TEXT,start INTEGER,end INTEGER,status TEXT)')
    pop=populations(root/'metadata',taxonomy_path,taxonomy_expected);start=time.monotonic();fixed_count=0
    for row in mapping(root/'oral/gsa_pooled_mapping_fixed.tsv'):
        anon,g,t,r,a,b,c=row
        if g not in pop['tax'] or t!=pop['tax'][g]['NCBI_ID']:raise ValueError('Fixed truth genome/tax metadata differs')
        db.execute('INSERT INTO fixed(anon,genome,tax,record,start,end,reads) VALUES(?,?,?,?,?,?,?)',row);fixed_count+=1
        if fixed_count%20000==0:db.commit();guard(root,clock);print('FIXED_MAP',fixed_count,flush=True)
    db.commit();anonymous=Counter();missing_anon=[]
    for ident,dna in fasta(root/'oral/gsa.tsv.gz'):
        if set(dna)-DNA:raise ValueError('Invalid anonymous DNA alphabet')
        row=db.execute('SELECT start,end,sha FROM fixed WHERE anon=?',(ident,)).fetchone()
        anonymous['records']+=1;anonymous['bp']+=len(dna)
        if row is None:
            if len(missing_anon)<30:missing_anon.append(dict(id=ident,bp=len(dna)))
            anonymous['no_mapping']+=1;continue
        if row[2] is not None:raise ValueError('Duplicate anonymous FASTA ID')
        if row[1]-row[0]+1!=len(dna):raise ValueError('Anonymous/fixed coordinate length mismatch')
        db.execute('UPDATE fixed SET sha=? WHERE anon=?',(hashlib.sha256(dna.encode()).hexdigest(),ident))
        if anonymous['records']%20000==0:db.commit();guard(root,clock);print('ANONYMOUS_FASTA',anonymous['records'],flush=True)
    db.commit();summary=Counter();examples=[]
    for ident,dna in fasta(root/'oral/gsa.fa'):
        if set(dna)-DNA:raise ValueError('Invalid supplied GSA DNA alphabet')
        summary['records']+=1;summary['bp']+=len(dna);summary['ambiguous_base_bp']+=sum(dna.count(c) for c in DNA-set('ACGT'))
        match=HEADER.fullmatch(ident);sha=hashlib.sha256(dna.encode()).hexdigest()
        if not dna:
            summary['empty_records']+=1;examples.append(dict(id=ident,bp=0,issue='empty_original_record'));continue
        if not match:raise ValueError('Nonempty GSA header has no source-coordinate contract')
        record,a,b,n=match.groups();a,b,n=map(int,[a,b,n])
        if a<1 or b-a+1!=n or n!=len(dna):raise ValueError('GSA source coordinates/length differ')
        rows=db.execute('SELECT anon,genome,tax,sha FROM fixed WHERE record=? AND start=? AND end=?',(record,a,b)).fetchall()
        matched=[r for r in rows if r[3]==sha]
        status='verified_publisher_sequence_join' if len(matched)==1 else 'unresolved_source_join'
        g,t=(matched[0][1:3] if len(matched)==1 else (None,None))
        db.execute('INSERT INTO gsa VALUES(?,?,?,?,?,?,?,?,?)',(ident,n,sha,g,t,record,a,b,status))
        summary[status+'_contigs']+=1;summary[status+'_bp']+=n
        if len(matched)==1:db.execute('UPDATE fixed SET matched=matched+1 WHERE anon=?',(matched[0][0],))
        elif len(examples)<50:examples.append(dict(id=ident,bp=n,issue=status,fixed_candidates=len(rows),sequence_matches=len(matched)))
        if summary['records']%20000==0:db.commit();guard(root,clock);print('SUPPLIED_GSA',summary['records'],flush=True)
    db.commit();raw=Counter()
    for row in mapping(root/'oral/gsa_pooled_mapping.tsv'):
        found=db.execute('SELECT genome,tax,record,start,end,reads FROM fixed WHERE anon=?',(row[0],)).fetchone()
        raw['rows']+=1;raw['exact_corrected_row' if found==tuple(row[1:]) else 'historical_wrong_or_unjoined_row']+=1
        if raw['rows']%100000==0:guard(root,clock);print('RAW_MAP',raw['rows'],flush=True)
    fixed_unmatched=db.execute('SELECT count(*) FROM fixed WHERE matched!=1 OR sha IS NULL').fetchone()[0]
    genomes=[dict(genome=g,contigs=n,bp=b,tax=pop['tax'][g]['NCBI_ID'],source_file=pop['sources'][g],superkingdom=pop['oral_positive'].get(g))
             for g,n,b in db.execute('SELECT genome,count(*),sum(length) FROM gsa WHERE genome IS NOT NULL GROUP BY genome')]
    headers_path=root/'metadata/all-oral-bam-headers.json';headers=json.loads(headers_path.read_text()) if headers_path.exists() else dict(records=[])
    valid_headers={h['filename_genome_ID']:h for h in headers['records'] if h.get('source_matches_setup') and not h.get('error')}
    # A positive source absent from the GSA still needs its complete reference
    # denominator; never make eligibility depend on how much happened to assemble.
    wanted_genomes=set(pop['oral_positive'])|set(g['genome'] for g in genomes)
    missing_header_genomes=sorted(wanted_genomes-set(valid_headers))
    header_refs={g:{r['SN']:r['LN'] for r in h['references']} for g,h in valid_headers.items()}
    coordinate_errors=[];coordinate_error_count=0
    for g,r,a,b in db.execute('SELECT DISTINCT genome,record,start,end FROM gsa WHERE genome IS NOT NULL'):
        if g in header_refs and (r not in header_refs[g] or b>header_refs[g][r]):
            coordinate_error_count+=1
            if len(coordinate_errors)<30:coordinate_errors.append(dict(genome=g,record=r,start=a,end=b))
    # Never substitute GSA span sums, observed maxima or read counts for complete
    # supplied-reference lengths. Partial metadata/header probes do not validate
    # full source FASTA bytes, annotations or competitor homology.
    unresolved=['Full source FASTA bytes/replicon annotations and whole setup archive checksum are unverified.',
                'Full supplied-reference denominators missing for '+str(len(missing_header_genomes))+' abundance-supported or observed genomes.',
                'Independent exact/near source overlap and competitive homology cannot be completed without source-reference admission.']
    unverified_tax=[g for g,d in pop['profile_taxon_differences'].items() if g in pop['oral_positive'] and d['relationship']!='verified_profile_ancestor']
    if unverified_tax:unresolved.append(str(len(unverified_tax))+' metadata taxon versus species-profile relationships remain nonancestor; keep nodes separate.')
    if fixed_unmatched:unresolved.append(str(fixed_unmatched)+' corrected mapping rows lack exactly one full supplied-GSA sequence match.')
    if summary['unresolved_source_join_contigs']:unresolved.append(str(summary['unresolved_source_join_contigs'])+' supplied GSA contigs retain unresolved origins.')
    if summary['empty_records']:unresolved.append(str(summary['empty_records'])+' original empty records need an explicit byte-preserving derivative contract before native feature input.')
    result=dict(status='PROVISIONAL_NOT_ADMITTED',source='publisher sequence/coordinate joins, independent of marker features/binner output',
        fixed_rows=fixed_count,fixed_unmatched=fixed_unmatched,anonymous_FASTA=dict(anonymous),anonymous_unmapped_examples=missing_anon,
        supplied_GSA=dict(summary),examples=examples,raw_mapping_audit=dict(raw),observed_genomes=genomes,
        population=dict(oral_samples=pop['oral_samples'],oral_positive_genomes=len(pop['oral_positive']),
            profile_taxon_differences=pop['profile_taxon_differences'],
            missing_profile_positive_by_sample=pop['missing_profile_positive_by_sample'],
            historical_taxonomy=pop['taxonomy'],
            observed_nonpositive_genomes=sorted(set(g['genome'] for g in genomes)-set(pop['oral_positive'])),
            exact_simulator_genome_overlap_with_GI=pop['exact_simulator_genome_overlap_with_GI'],source_basename_overlap_with_GI=pop['source_basename_overlap_with_GI']),
        full_reference_header_genomes=len(valid_headers),positive_or_observed_genomes_missing_header=missing_header_genomes,
        source_coordinate_error_count=coordinate_error_count,source_coordinate_errors=coordinate_errors,
        unresolved=unresolved,full_reference_denominators_admitted=False,near_overlap_admitted=False,seconds=time.monotonic()-start,
        original_clock=clock,scope='All provided DNA retained; corrected map and anonymous sequence equality do not prove complete independent provided-reference truth.')
    db.close();guard(root,clock);(out/'review.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print('ADMISSION',result['status'],dict(summary),'unresolved',unresolved,flush=True)
    return result


if __name__=='__main__':audit()
