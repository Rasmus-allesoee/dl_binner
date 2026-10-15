#!/usr/bin/env python3
"""Independently verify retained E009 assembly/BAM/depth without replaying its DAG.

Read only consumed files, bind them to sealed stage/watchdog receipts, inspect
actual BAM headers with the recorded samtools and check every matrix cell against
the ten ordered depth files. A closed feature matrix in a failed final stage can
be accepted explicitly here; that never seals the failed stage or admits truth.
Write one fresh review directory and retain new read-only native command logs.
"""
import argparse
import csv
import hashlib
import json
import math
from pathlib import Path
import subprocess


def bind(path):
    """Hash a consumed regular file; reject linked inputs and expose large I/O progress."""
    path=Path(path)
    if path.is_symlink()or not path.is_file():raise ValueError('Missing/linked input: '+str(path))
    digest=hashlib.sha256();count=0
    with path.open('rb')as stream:
        while chunk:=stream.read(4*1024**2):
            digest.update(chunk);count+=len(chunk)
            if count%(256*1024**2)==0:print('VERIFY_BYTES '+str(path)+' '+str(count),flush=True)
    return {'bytes':count,'sha256':digest.hexdigest()}


def fasta_axis(path):
    """Return the full ordered FASTA ID/length axis, rejecting duplicate/empty DNA."""
    rows=[];ident=None;length=0;seen=set()
    with Path(path).open()as stream:
        for line in stream:
            if line.startswith('>'):
                if ident is not None:
                    if not length:raise ValueError('Empty assembly contig')
                    rows.append((ident,length))
                ident=line[1:].split()[0];length=0
                if ident in seen:raise ValueError('Duplicate assembly ID')
                seen.add(ident)
            else:
                if ident is None:raise ValueError('DNA before FASTA header')
                length+=len(line.strip())
    if ident is None or not length:raise ValueError('Empty assembly')
    rows.append((ident,length));return rows


def depth_values(path, axis, column):
    """Require an exact ordered, finite nonnegative depth vector, retaining all zeros."""
    values=[]
    with Path(path).open()as stream:
        reader=csv.reader(stream,delimiter='\t')
        if next(reader)!=['contig_id',column]:raise ValueError('Wrong depth column')
        for ident,_ in axis:
            row=next(reader,None)
            if row is None or len(row)!=2 or row[0]!=ident:raise ValueError('Wrong depth contig axis')
            value=float(row[1])
            if not math.isfinite(value)or value<0:raise ValueError('Invalid depth value')
            values.append(value)
        if next(reader,None)is not None:raise ValueError('Extra depth contig')
    return values


def check_matrix(path, axis, columns, vectors):
    """Require exact column/contig order and round-tripped equality of every cell."""
    with Path(path).open()as stream:
        reader=csv.reader(stream,delimiter='\t')
        if next(reader)!=['contig_id',*columns]:raise ValueError('Wrong matrix sample axis')
        for i,(ident,_)in enumerate(axis):
            row=next(reader,None)
            if row is None or row[0]!=ident or len(row)!=len(columns)+1:raise ValueError('Wrong matrix contig axis')
            if [float(v)for v in row[1:]]!=[v[i]for v in vectors]:raise ValueError('Matrix differs from measured depths')
        if next(reader,None)is not None:raise ValueError('Extra matrix contig')


def review(root, output, snapshot, samtools):
    """Verify actual feature bytes and native headers; never open a bin or truth label."""
    root=Path(root);output=Path(output);output.mkdir(parents=True,exist_ok=False)
    snap=json.loads(Path(snapshot).read_text())['snapshot'];checked={};manifests={}
    for folder in sorted((root/'parts').iterdir()):
        path=folder/'done.json'
        if not path.exists():continue
        actual=bind(path)
        if actual!=snap['stages'][folder.name]['manifest']:raise ValueError('Watchdog/stage manifest drift')
        manifests[folder.name]=json.loads(path.read_text());checked[str(path)]=actual
    def sealed(path,stage):
        path=Path(path);actual=bind(path)
        if actual!=manifests[stage]['files'][str(path.relative_to(root/'parts'/stage))]:raise ValueError('Sealed byte drift: '+str(path))
        checked[str(path)]=actual;return actual
    cfg=json.loads((root/'stage-config.json').read_text());samples=cfg['plan']['samples']
    expected=[0,2,3,4,6,9,10,11,14,17]
    if [s['sample']for s in samples]!=expected:raise ValueError('Frozen sample order changed')
    assembly=manifests['assembly']['payload'];reference=Path(assembly['reference'])
    reference_binding=sealed(reference,'assembly');axis=fasta_axis(reference)
    if len(axis)!=assembly['axis']['contigs']or sum(n for _,n in axis)!=assembly['axis']['bp']:raise ValueError('Assembly count/base disagreement')
    rows=[];vectors=[];columns=[s['column']for s in samples]
    for spec in samples:
        sample=spec['sample'];stage=f'map_{sample:04d}';payload=manifests[stage]['payload']
        if payload['sample']!=sample or payload['column']!=spec['column']:raise ValueError('Stage sample/column mismatch')
        bam=Path(payload['bam']);bam_binding=sealed(bam,stage);sealed(str(bam)+'.bai',stage)
        receipt_path=bam.with_suffix('.mapped.json');sealed(receipt_path,stage);mapped=json.loads(receipt_path.read_text())
        depth=Path(payload['depth']);sealed(depth,stage);receipt_path=depth.with_suffix('.receipt.json');sealed(receipt_path,stage)
        receipt=json.loads(receipt_path.read_text())
        if any(x['reference']!=reference_binding or x['bam']!=bam_binding or x['column']!=spec['column']for x in [receipt,mapped]):raise ValueError('BAM/depth identity mismatch')
        with (output/f'quickcheck-{sample:04d}.log').open('wb')as log:
            subprocess.run([samtools,'quickcheck','-v',bam],stdout=log,stderr=subprocess.STDOUT,check=True,timeout=30)
        result=subprocess.run([samtools,'view','-H',bam],capture_output=True,check=True,timeout=30)
        (output/f'header-{sample:04d}.sam').write_bytes(result.stdout)
        header=result.stdout.decode().splitlines();sq=[]
        if not any(line.startswith('@HD\t')and'SO:coordinate'in line.split('\t')for line in header):raise ValueError('BAM not coordinate sorted')
        for line in header:
            if line.startswith('@SQ\t'):
                tags=dict(s.split(':',1)for s in line.split('\t')[1:]);sq.append((tags['SN'],int(tags['LN'])))
        if sq!=axis:raise ValueError('Actual BAM SQ axis differs')
        values=depth_values(depth,axis,spec['column']);vectors.append(values)
        zeros=sum(v==0 for v in values)
        if zeros!=receipt['zero_rows']:raise ValueError('Depth zero count differs')
        native=[]
        for path in sorted((root/'parts'/stage).rglob('*.exit.json')):
            sealed(path,stage);v=json.loads(path.read_text());native.append(v)
            if v.get('exit_code')!=0:raise ValueError('Nonzero native stage exit')
        rows.append({'sample':sample,'column':spec['column'],'bam':str(bam),'bam_binding':bam_binding,
                     'read_pairs':mapped['reads']['pairs'],'read_bp':mapped['reads']['bp'],
                     'zero_depth_contigs':zeros,'positive_depth_contigs':len(values)-zeros,
                     'native_exit_receipts_checked':len(native),'actual_SQ_axis_matches':True})
        print('ACCEPTANCE_SAMPLE '+str(sample),flush=True)
    matrix=root/'parts/final/depth.tsv';manifest_path=Path(str(matrix)+'.manifest.json');matrix_manifest=json.loads(manifest_path.read_text())
    if matrix_manifest['matrix']!=bind(matrix)or matrix_manifest['reference']!=reference_binding or matrix_manifest['ordered_columns']!=columns:raise ValueError('Combined matrix receipt mismatch')
    if matrix_manifest['depth_files']!=[checked[str(root/'parts'/f'map_{s["sample"]:04d}'/'depth.tsv')]for s in samples]:raise ValueError('Combined source depth bindings differ')
    check_matrix(matrix,axis,columns,vectors);checked[str(matrix)]=bind(matrix);checked[str(manifest_path)]=bind(manifest_path)
    result={'status':'retained assembly, ten BAM/depths and closed combined feature matrix verified',
            'full_DAG_succeeded':False,'failed_final_stage_sealed':False,'truth_admitted':False,
            'assembly':{k:v for k,v in assembly['axis'].items()if k!='rows'},'samples':rows,
            'ordered_columns':columns,'matrix_rows':len(axis),'matrix_cells_verified':len(axis)*len(columns),
            'all_zero_rows':sum(all(v[i]==0 for v in vectors)for i in range(len(axis))),
            'checked_inputs':checked,'native_samtools':samtools,
            'verification_scope':'critical consumed feature bytes, watchdog/stage seals, actual native BAM headers/quickcheck; bulk read archives/sources and unused intermediates not rehashed'}
    (output/'acceptance.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n');return result


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ['root','output','snapshot','samtools']:parser.add_argument('--'+name,type=Path,required=True)
    args=parser.parse_args();review(args.root,args.output,args.snapshot,str(args.samtools))
