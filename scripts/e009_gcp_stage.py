#!/usr/bin/env python3
"""Serial E009 data-stage workers; no binner fitting or quality scoring.

The committed plan supplies ordered samples and provisional read object identities.
Every completed stage seals its output bytes. Failed/unsealed directories are kept
and require assessment rather than automatic overwrite. Truth files stay separate
from FASTQ/assembly/depth inputs. This module also serves the tiny local fixture DAG.
"""
import argparse
import csv
import gzip
import hashlib
import json
import os
from pathlib import Path
import shutil
import sys
import tarfile
import time

sys.path.insert(0, str(Path(__file__).absolute().parent))
from e009_common import acquire, binding, extract, fasta, safe_name, write_json
from e009_data import (assembly_axis, assemble, combine_depth, competitive_reference,
                       map_sample, mean_depth, run_native, source_catalog, validate_fastq_pair)
from e009_truth import construct


def progress(key, completed):
    """Report actual byte/record progress for monitors, separately from heartbeats."""
    print('DLBINNER WORK_PROGRESS_JSON='+json.dumps(
        {'work_key':str(key),'completed_bytes':completed}), flush=True)


def stage_folder(root, name):
    """Allocate one fresh stage; preserve unsealed failures for explicit assessment."""
    target=Path(root)/'parts'/name
    # Snakemake creates output parents before invoking the shell command.
    if target.exists() and (target.is_symlink() or any(target.iterdir())):
        raise ValueError(f'Preserved stage already exists: {target}; assess incomplete outputs before recovery')
    target.mkdir(parents=True,exist_ok=True)
    write_json(target/'started.json',{'stage':name,'started_epoch':time.time()})
    return target


def seal(folder, payload):
    """Bind closed outputs and write the completion marker last, including failure-sensitive logs."""
    files={str(p.relative_to(folder)):binding(p,lambda n,p=p:progress(p,n))
           for p in sorted(folder.rglob('*')) if p.is_file()}
    value={'payload':payload,'files':files}
    write_json(folder/'done.json',value)
    return value


def read_stage(root, name):
    """Read an already verified completion manifest rather than inferring consumer paths."""
    return json.loads((Path(root)/'parts'/name/'done.json').read_text())['payload']


def unpack_reads(archive, folder, sample, max_expanded_bytes):
    """Inspect all tar members and retain only FASTQ plus sample-0 read-origin metadata.

    Plain FASTQ is losslessly gzip-compressed while streaming; nested gzip stays
    byte-identical. Thus all ten samples never coexist as expanded text. Every
    member is inventoried; links, traversal, duplicate names and unsupported read
    layouts fail. Source archives are retained. The evaluator alone uses origins.
    """
    files=[];inventory=[];names=set();expanded=0;last=time.monotonic()
    with tarfile.open(archive,mode='r|gz') as tar:
        for member in tar:
            rel=safe_name(member.name)
            if str(rel) in names or not (member.isdir() or member.isfile()):
                raise ValueError('Duplicate or nonregular read archive member')
            names.add(str(rel));expanded+=member.size
            if expanded>max_expanded_bytes:raise ValueError('Read archive exceeds declared expansion allowance')
            inventory.append({'name':member.name,'bytes':member.size,'directory':member.isdir()})
            if member.isdir():continue
            fastq=member.name.lower().endswith(('.fq','.fastq','.fq.gz','.fastq.gz'))
            origin=sample==0 and rel.name=='reads_mapping.tsv.gz'
            if not (fastq or origin):continue
            parent=folder/('reads' if fastq else 'evaluator-inputs')
            parent.mkdir(exist_ok=True)
            target=parent/(rel.name if rel.name.endswith('.gz') else rel.name+'.gz')
            if target.exists():raise ValueError('Archive basenames collide')
            source=tar.extractfile(member)
            with source, target.open('xb') as raw:
                writer=raw if rel.name.endswith('.gz') else gzip.GzipFile(fileobj=raw,mode='wb',mtime=0)
                try:
                    copied=0
                    while chunk:=source.read(1024*1024):
                        writer.write(chunk);copied+=len(chunk)
                        if time.monotonic()-last>=5:progress(member.name,copied);last=time.monotonic()
                finally:
                    if writer is not raw:writer.close()
            if fastq:files.append(target)
    if len(files) not in (1,2):raise ValueError('Expected one interleaved or two paired FASTQ members')
    files.sort()
    # Full mate validation will reject swapped mates rather than guessing a repair.
    first,second=files[0], files[1] if len(files)==2 else None
    validation=validate_fastq_pair(first,second)
    write_json(folder/'read-inventory.json',{'archive':binding(archive),'members':inventory,
               'expanded_member_bytes':expanded,'retained_fastq':list(map(str,files)),
               'layout':'paired' if second else 'interleaved','validation':validation})
    return {'first':str(first),'second':str(second) if second else None,
            'validation':validation,'archive':str(archive)}


def split_interleaved(first, folder):
    """Losslessly split sample-0 interleaved FASTQ into compressed MEGAHIT mates only."""
    left,right=folder/'assembly_R1.fq.gz',folder/'assembly_R2.fq.gz'
    with gzip.open(first,'rt',encoding='ascii') as inp, gzip.open(left,'xt') as a, gzip.open(right,'xt') as b:
        count=0
        while True:
            lines=[inp.readline() for _ in range(8)]
            if not lines[0]:
                if any(lines[1:]):raise ValueError('Trailing interleaved FASTQ data')
                break
            if not all(lines):raise ValueError('Truncated interleaved pair')
            a.writelines(lines[:4]);b.writelines(lines[4:]);count+=1
            if count%100000==0:progress('deinterleaved_pairs',count)
    return left,right


def acquire_sample(plan, sample, folder):
    """Acquire exactly one selected object; never silently reuse a partial download."""
    spec=next(s for s in plan['samples'] if s['sample']==sample)
    archive=folder/'reads.tar.gz'
    acquire({k:v for k,v in spec.items() if k in ('url','bytes','sha256','etag')},archive)
    return unpack_reads(archive,folder,sample,plan['read_archive_expanded_bytes_max'])


def source_stage(cfg, folder):
    """Reacquire unavailable source DNA by its accepted SHA, without replaying science.

    The retained sample-0 filename inventory defines the conservative reference
    universe. Its grouping/taxonomy and read-origin join need independent review
    before fitting/scoring; no filename is used to guess a cellular target class.
    """
    plan={**cfg['plan'],**json.loads(Path(cfg['evaluator_config']).read_text())}
    archive=folder/'source_genomes.tar.gz'
    acquire(plan['source_genomes'],archive)
    extract(archive,folder/'unpacked',max_bytes=plan['source_expanded_bytes_max'])
    catalog=source_catalog(folder/'unpacked',plan['development_overlap'],folder/'catalog.json')
    selected=plan['sample0_source_files']
    competitive_reference(catalog,selected,folder/'reference.fna')
    batch=0;size=0;stream=None;batches=[]
    try:
        for ident,seq in fasta(folder/'reference.fna'):
            if stream is None or size+len(seq)>plan['truth_batch_bp']:
                if stream:stream.close()
                path=folder/f'reference_{batch:04d}.fna';stream=path.open('x')
                batches.append(str(path));batch+=1;size=0
            stream.write(f'>{ident}\n{seq}\n');size+=len(seq)
    finally:
        if stream:stream.close()
    return {'catalog':str(folder/'catalog.json'),'reference':str(folder/'reference.fna'),
            'axis':str(folder/'reference.fna.axis.json'),'batches':batches,
            'source_file_universe':selected,'genome_grouping_and_target_taxonomy_admitted':False}


def origin_summary(path, pairs, output):
    """Inventory all simulator read origins, refusing malformed or inconsistent taxonomy.

    Counts must match the complete paired FASTQ count. This is a population audit,
    not an exact FASTQ-to-origin ID join or a cellular taxonomy classification.
    Those limits are explicit and remain review dependencies before any scores.
    """
    genomes={};rows=0;previous=None
    with gzip.open(path,'rt') as stream:
        reader=csv.DictReader(stream,delimiter='\t')
        if reader.fieldnames!=['#anonymous_read_id','genome_id','tax_id','read_id']:
            raise ValueError('Provider read-origin header changed')
        for row in reader:
            rid=row['#anonymous_read_id']
            if not rid.startswith('S0R') or not rid.endswith(('/1','/2')) or rid==previous:
                raise ValueError('Malformed/adjacent duplicate sample-0 origin ID')
            item=genomes.setdefault(row['genome_id'],{'tax_id':row['tax_id'],'read_records':0})
            if item['tax_id']!=row['tax_id']:raise ValueError('Provider genome/taxon relation changed')
            item['read_records']+=1;rows+=1;previous=rid
            if rows%1000000==0:progress('origin_rows',rows)
    if rows!=2*pairs:raise ValueError('Origin/FASTQ record counts differ')
    value={'file':binding(path),'rows':rows,'genomes':genomes,
           'claim_limit':'counts and provider IDs/taxa; exact read-ID join, reference grouping and target taxonomy need review'}
    write_json(output,value)
    return value


def execute(cfg, name):
    """Execute one bounded worker's actual contract and seal successful outputs last."""
    root=Path(cfg['root']);plan=cfg['plan'];runtime=cfg['runtime'];threads=cfg['threads']
    folder=stage_folder(root,name)
    if name=='sources':payload=source_stage(cfg,folder)
    elif name=='reads_0000':payload=acquire_sample(plan,0,folder)
    elif name=='assembly':
        reads=read_stage(root,'reads_0000');first,second=reads['first'],reads['second']
        if second is None:first,second=split_interleaved(first,folder)
        result=assemble(runtime['megahit'],first,second,cfg['assembly_threads'],
                        cfg['assembly_mem_bytes'],folder/'megahit',folder/'megahit.log')
        if result['eligible_500']>plan['eligible_contig_scale_stop'] or result['bp']>plan['assembly_bp_scale_stop']:
            raise ValueError('Assembly scale requires prospective reassessment; preserve all DNA')
        payload={'reference':str(folder/'megahit/final.contigs.fa'),'axis':result}
    elif name.startswith('map_'):
        sample=int(name[4:]);spec=next(s for s in plan['samples'] if s['sample']==sample)
        reads=read_stage(root,'reads_0000') if sample==0 else acquire_sample(plan,sample,folder)
        reference=read_stage(root,'assembly')['reference']
        bam=map_sample(runtime['strobealign'],runtime['samtools'],reference,reads['first'],reads['second'],
                       sample,spec['column'],threads,folder/'mapping',
                       bam_name=f'sample_{sample:04d}.sorted.bam',cleanup_sam=True)
        depth=folder/'depth.tsv'
        mean_depth(runtime['samtools'],reference,bam,spec['column'],threads,depth)
        payload={'sample':sample,'column':spec['column'],'bam':str(bam),'depth':str(depth),'reads':reads}
    elif name=='final':
        reference=read_stage(root,'assembly')['reference']
        samples=[read_stage(root,f'map_{s["sample"]:04d}') for s in plan['samples']]
        combine_depth(reference,[s['column'] for s in samples],[s['depth'] for s in samples],folder/'depth.tsv')
        # Feature/depth work is complete before any evaluator metadata is opened.
        source=read_stage(root,'sources');axis=json.loads(Path(source['axis']).read_text())
        pafs=[]
        for i,batch in enumerate(source['batches']):
            paf=folder/f'truth_{i:04d}.paf';pafs.append(paf)
            run_native([runtime['minimap2'],'-x','asm5','-P','-c','--eqx','-m','100','-s','100','-n','2',
                        '-t',threads-1,batch,reference],folder/f'truth_{i:04d}.log',stdout=paf)
        paf=folder/'all_competing_chains.paf'
        with paf.open('xb') as out:
            for part in pafs:
                with part.open('rb') as inp:shutil.copyfileobj(inp,out)
        construct(reference,paf,axis['reference_axis'],folder/'alignment-truth')
        reads=read_stage(root,'reads_0000');origin=Path(reads['first']).parent.parent/'evaluator-inputs/reads_mapping.tsv.gz'
        if origin.exists():origin_summary(origin,reads['validation']['pairs'],folder/'read-origin-summary.json')
        elif not cfg['fixture']:raise ValueError('Sample-0 read-origin file missing; truth population not admitted')
        payload={'reference':reference,'ordered_samples':samples,'matrix':str(folder/'depth.tsv'),
                 'alignment_truth':str(folder/'alignment-truth/truth.json'),'reference_axis':source['axis'],
                 'no_fits_or_quality_scores':True,'scientific_scoring_admitted':False,
                 'review_required':['actual read/source bytes and ordered native axes','source genome/replicon grouping',
                                    'sample-0 positive-origin join and cellular target taxonomy','scale, cost and new GCP runtimes']}
    else:raise ValueError('Unknown data stage: '+name)
    seal(folder,payload)
    print('E009_DATA_STAGE_COMPLETE='+name,flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config',type=Path,required=True);parser.add_argument('--stage',required=True)
    args=parser.parse_args();execute(json.loads(args.config.read_text()),args.stage)
