#!/usr/bin/env python3
"""Audit sealed sample-0 read IDs, positive origins, source joins and taxonomy.

This read-only evaluator consumes completed E009 sources/reads manifests and an
explicit provider sample-0 taxonomic profile. It writes a fresh review directory,
never changes stage journals/FASTA/BAM/depth, and never opens bins or scores.
Exact anonymous-ID sets are checked with bounded bitsets, without assuming table
order. Taxonomic lineage is not proof of chromosome/plasmid or genome-copy meaning;
the report deliberately does not admit a whole-genome truth denominator.
"""
import argparse
from collections import Counter, defaultdict
import csv
import gzip
import hashlib
import io
import json
from pathlib import Path
import re


def bind(path):
    """Bind one actual regular input file without following a symbolic-link input."""
    path=Path(path)
    if path.is_symlink() or not path.is_file():raise ValueError('Missing/linked review input: '+str(path))
    digest=hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda:stream.read(1024*1024),b''):digest.update(chunk)
    return {'bytes':path.stat().st_size,'sha256':digest.hexdigest()}


class ReadIDs:
    """Verify a complete canonical sample-0 mate-ID set with two bits per pair.

    Both independently checked sets must cover exactly S0R0..S0R(pairs-1), /1,/2.
    A late duplicate cannot be hidden by the correct total record count.
    """
    def __init__(self,pairs):
        if pairs<=0:raise ValueError('Expected positive complete pair count')
        self.pairs=pairs;self.bits=bytearray((2*pairs+7)//8);self.count=0
    def add(self,ident):
        """Mark one canonical mate ID; reject out-of-range IDs and any duplicate."""
        match=re.fullmatch(r'S0R(0|[1-9][0-9]*)/([12])',ident)
        if not match:raise ValueError('Noncanonical sample-0 read ID: '+ident)
        pair,mate=map(int,match.groups())
        if pair>=self.pairs:raise ValueError('Read ID outside the full declared pair range')
        offset=2*pair+mate-1;byte,bit=divmod(offset,8);mask=1<<bit
        if self.bits[byte]&mask:raise ValueError('Duplicate anonymous read ID: '+ident)
        self.bits[byte]|=mask;self.count+=1
    def finish(self):
        """Require the full expected set and return its explicit cardinality."""
        if self.count!=2*self.pairs:raise ValueError('Incomplete anonymous read-ID set')
        return {'records':self.count,'pairs':self.pairs,'complete_canonical_ID_set':True}


def source_id(read_id,records):
    """Resolve observed ART or WGSIM ID syntax to an exact unique source record.

    The inspected CAMISIM writer uses a final hyphen for ART and five underscore
    fields for WGSIM. Actual membership must prove the format; no filename/species
    heuristic, substring match or silent fallback is allowed.
    """
    candidates=set()
    if '-' in read_id:candidates.add(read_id.rsplit('-',1)[0])
    if read_id.count('_')>=5:candidates.add(read_id.rsplit('_',5)[0])
    found=candidates&records.keys()
    if len(found)!=1:raise ValueError('Unknown/ambiguous source read-ID join: '+read_id)
    return next(iter(found))


def profiles(path):
    """Read explicit provider genome IDs and full lineages, retaining zero entries."""
    with Path(path).open() as stream:lines=stream.read().splitlines()
    if '@SampleID:0' not in lines:raise ValueError('Need the provider sample-0 profile')
    start=next(i for i,line in enumerate(lines)if line.startswith('@@'))
    rows=csv.DictReader(io.StringIO('\n'.join(lines[start:])[2:]),delimiter='\t');result={}
    for row in rows:
        gid=row['_CAMI_genomeID']
        if not gid:continue
        if gid in result:raise ValueError('Duplicate provider genome ID')
        path_ids=row['TAXPATH'].split('|');path_names=row['TAXPATHSN'].split('|')
        if len(path_ids)!=len(path_names):raise ValueError('Provider lineage axes differ')
        lineage=dict(zip(path_ids,path_names));kind='other'
        for ident,name,label in [('2','Bacteria','bacterial'),('2157','Archaea','archaeal'),
                                  ('2759','Eukaryota','eukaryotic'),('10239','Viruses','viral')]:
            if ident in lineage:
                if lineage[ident]!=name:raise ValueError('Provider lineage ID/name mismatch')
                if kind!='other':raise ValueError('Conflicting cellular/acellular lineage')
                kind=label
        result[gid]={**row,'lineage_class':kind}
    if not result:raise ValueError('No provider genome rows')
    return result


def fastq_ids(path):
    """Stream IDs from already byte-bound, fully validated FASTQ without DNA changes."""
    opener=gzip.open if str(path).endswith('.gz') else open
    with opener(path,'rt',encoding='ascii') as stream:
        while True:
            head=stream.readline()
            if not head:return
            seq,plus,quality=(stream.readline()for _ in range(3))
            if not head.startswith('@') or not seq or not plus.startswith('+') or not quality:
                raise ValueError('Truncated/malformed sealed FASTQ')
            yield head[1:].split()[0]


def review(root,profile_path,output):
    """Check exact read/origin sets and observed record/genome/lineage associations.

    Hash only inputs actually consumed. Sealed source DNA is not rehashed or read;
    its already verified catalog supplies immutable record/sequence identities.
    Unobserved records and multiple genome/file associations remain explicit.
    """
    root,output=Path(root),Path(output);output.mkdir(parents=True,exist_ok=False)
    source_folder=root/'parts/sources';read_folder=root/'parts/reads_0000'
    source_done=json.loads((source_folder/'done.json').read_text());read_done=json.loads((read_folder/'done.json').read_text())
    checked={}
    def sealed(path,folder,done):
        path=Path(path);name=str(path.relative_to(folder));actual=bind(path)
        if actual!=done['files'][name]:raise ValueError('Consumed sealed bytes changed: '+str(path))
        checked[str(path)]=actual;return path
    catalog_path=sealed(source_done['payload']['catalog'],source_folder,source_done)
    axis_path=sealed(source_done['payload']['axis'],source_folder,source_done)
    catalog=json.loads(catalog_path.read_text());axis=json.loads(axis_path.read_text())
    records={}
    for item in catalog['files']:
        for record in item['replicons']:
            rid=record['replicon_id']
            if rid in records:raise ValueError('Nonunique source catalog record ID')
            records[rid]={'file':item['name'],'length':record['length']}
    reference_ids={v['original_replicon_id']for v in axis['reference_axis'].values()}
    provider=profiles(profile_path);checked[str(profile_path)]=bind(profile_path)
    payload=read_done['payload'];pairs=payload['validation']['pairs'];reads=ReadIDs(pairs)
    for path in [payload['first'],payload['second']]:
        if path is None:continue
        path=sealed(path,read_folder,read_done)
        for ident in fastq_ids(path):
            reads.add(ident)
            if reads.count%1000000==0:print('REVIEW_FASTQ_IDS='+str(reads.count),flush=True)
    read_check=reads.finish();del reads
    origins=ReadIDs(pairs);origin_path=sealed(read_folder/'evaluator-inputs/reads_mapping.tsv.gz',read_folder,read_done)
    genomes={};by_record=defaultdict(set);by_file=defaultdict(set)
    with gzip.open(origin_path,'rt') as stream:
        rows=csv.DictReader(stream,delimiter='\t')
        if rows.fieldnames!=['#anonymous_read_id','genome_id','tax_id','read_id']:raise ValueError('Origin fields changed')
        for row in rows:
            origins.add(row['#anonymous_read_id']);gid=row['genome_id'];tax=row['tax_id']
            if gid not in provider:raise ValueError('Positive origin absent from provider profile: '+gid)
            p=provider[gid]
            if tax not in p['TAXPATH'].split('|'):raise ValueError('Origin tax ID not on explicit provider lineage')
            rid=source_id(row['read_id'],records)
            if rid not in reference_ids:raise ValueError('Positive source record absent from competitive universe: '+rid)
            item=genomes.setdefault(gid,{'tax_id':tax,'read_records':0,'lineage_class':p['lineage_class'],
                'provider_strain_tax_id':p['TAXID'],'HOST':p['HOST'],'profile_percentage':p['PERCENTAGE']})
            if item['tax_id']!=tax:raise ValueError('Positive origin genome/taxon relation changed')
            item['read_records']+=1;by_record[rid].add(gid);by_file[records[rid]['file']].add(gid)
            if origins.count%1000000==0:print('REVIEW_ORIGIN_IDS='+str(origins.count),flush=True)
    origin_check=origins.finish()
    classes=Counter();class_genomes=Counter()
    for item in genomes.values():classes[item['lineage_class']]+=item['read_records'];class_genomes[item['lineage_class']]+=1
    result={'status':'exact read/origin/source/profile joins passed; truth denominator remains provisional',
        'consumed_files':checked,'source_stage_manifest':bind(source_folder/'done.json'),'read_stage_manifest':bind(read_folder/'done.json'),
        'fastq_IDs':read_check,'origin_IDs':origin_check,'sets_equal':True,'positive_genomes':genomes,
        'read_records_by_lineage':dict(classes),'positive_genomes_by_lineage':dict(class_genomes),
        'source_record_to_observed_genomes':{k:sorted(v)for k,v in by_record.items()},
        'source_file_to_observed_genomes':{k:sorted(v)for k,v in by_file.items()},
        'unobserved_competitive_records':sorted(reference_ids-by_record.keys()),
        'multiple_genome_source_records':{k:sorted(v)for k,v in by_record.items()if len(v)>1},
        'multiple_genome_source_files':{k:sorted(v)for k,v in by_file.items()if len(v)>1},
        'scientific_truth_admitted':False,'no_fits_or_scores':True,
        'remaining_review':['Meaning/grouping of permuted copies and zero-origin source records',
            'Chromosome/plasmid/viral molecule identity independent of a bacterial lineage',
            'Whole provided genome grouping/denominator and final competitive alignment interpretation']}
    with (output/'review.json').open('x')as stream:json.dump(result,stream,indent=2,sort_keys=True);stream.write('\n')
    return result


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root',type=Path,required=True);parser.add_argument('--profile',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True);args=parser.parse_args()
    result=review(args.root,args.profile,args.output)
    print(json.dumps({k:result[k]for k in ['status','sets_equal','read_records_by_lineage','positive_genomes_by_lineage','scientific_truth_admitted']}))
