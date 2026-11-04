#!/usr/bin/env python3
"""Restore/sort one verified retained BAM and produce exact measured intervals.

No acquisition of new reads or remapping is supported. A generation-pinned private
object is streamed through a hash tee into samtools sort, with separate checked
producer/consumer exits. Original BAMs are never modified or deleted. The newly
owned sorted file is regenerable, but its removal is explicit and receipt-bound.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time

ROOT=Path(__file__).absolute().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from e024_coverage import binding,write


def sort_stream(record,output,samtools,gcloud=None,engineering=False):
    """Verify every raw byte during serial sort; refuse drift/failed producers."""
    out=Path(output);out.mkdir(parents=True,exist_ok=False);uri=record['source']
    if record.get('sorted') is not False:raise ValueError('Only explicitly unsorted retained BAMs use serial sort')
    remote=uri.startswith('gs://')
    if remote:
        if engineering or '#' not in uri or not uri.startswith('gs://dl-binner-archive-167650584170/e024/'):
            raise ValueError('Generation-pinned existing private Oral object required')
        if gcloud is None:raise ValueError('Explicit verified private transport required')
    elif not engineering:raise ValueError('Native Oral restore must use frozen private generation')
    last_progress=0
    rawlog=(out/'transport.stderr').open('xb');sortlog=(out/'sort.stderr').open('xb')
    source=None;process=None;stream=None;h=hashlib.sha256();size=0;begin=time.monotonic()
    try:
        if remote:
            source=subprocess.Popen([str(gcloud),'storage','cat',uri],stdout=subprocess.PIPE,stderr=rawlog)
            stream=source.stdout
        else:stream=Path(uri).open('rb')
        argv=[str(samtools),'sort','-@','3','-m','512M','-T',str(out/'spool'),'-o',str(out/'sorted.bam'),'-']
        process=subprocess.Popen(argv,stdin=subprocess.PIPE,stdout=subprocess.DEVNULL,stderr=sortlog)
        for block in iter(lambda:stream.read(1024**2),b''):
            size+=len(block)
            if size>record['bytes']:raise ValueError('Retained BAM transport exceeds byte contract')
            h.update(block);process.stdin.write(block)
            if size-last_progress>=64*1024**2:
                print(json.dumps(dict(stage='retained_BAM_sort_stream',bytes_received_pending_final_SHA=size,total_bytes=record['bytes'])),flush=True);last_progress=size
        process.stdin.close();sort_exit=process.wait();source_exit=source.wait() if source else 0
        if sort_exit or source_exit:raise ValueError('Actual retained-BAM producer/sorter failed: '+str((source_exit,sort_exit)))
        if dict(bytes=size,sha256=h.hexdigest())!={k:record[k] for k in ['bytes','sha256']}:
            raise ValueError('Retained BAM byte/hash differs; no fallback download')
        result=dict(status='PASS',source=record,raw_bytes_verified=size,raw_sha256=h.hexdigest(),
            source_exit=source_exit,sort_exit=sort_exit,sort_argv=argv,sorter=binding(samtools),
            sorted=binding(out/'sorted.bam'),wall_seconds=time.monotonic()-begin,remapped=False)
        write(out/'sort.json',result);return out/'sorted.bam'
    except BaseException as e:
        if process and process.poll() is None:process.kill();process.wait()
        if source and source.poll() is None:source.kill();source.wait()
        write(out/'failure.json',dict(error=repr(e),bytes_received=size,sha256=h.hexdigest(),
            source_exit=source.poll() if source else None,sort_exit=process.poll() if process else None))
        raise
    finally:
        if stream is not None:stream.close()
        rawlog.close();sortlog.close()


def measure(record,features,views,output,samtools,gcloud=None,engineering=False,summary_output=None):
    """Measure once and preserve raw source/sorter/summary evidence without retry."""
    from dl_binner.multiscale.measurement import summarize
    out=Path(output);out.mkdir(parents=True,exist_ok=False)
    if record['sorted']:
        bam=Path(record['source'])
        if binding(bam)!={k:record[k] for k in ['bytes','sha256']}:raise ValueError('Existing original E009 BAM differs')
    else:bam=sort_stream(record,out/'sort',samtools,gcloud,engineering)
    summary=Path(summary_output) if summary_output is not None else out/'measurement'
    r=summarize(bam,features,views,summary,record['sample'])
    write(out/'completed.json',dict(status='PASS',source=record,summary=binding(summary/'sample.json'),summary_path=str(summary.absolute()),
        sorter=binding(out/'sort/sort.json') if not record['sorted'] else None,original_alignment_unchanged=True))
    return r


def release_sorted(path,sort_receipt,summary):
    """Remove only this new closed sorted copy, preserving its exact regeneration."""
    path=Path(path);r=json.loads(Path(sort_receipt).read_text());s=json.loads(Path(summary).read_text())
    if (path.name!='sorted.bam' or path.is_symlink() or r.get('status')!='PASS'
        or r['sorted']!=binding(path) or s.get('kind')!='multiscale_BAM_sample' or s['BAM']!=binding(path)):
        raise ValueError('Sorted temporary release needs exact passed source/measurement bytes')
    # Re-read the new compact member before removing the regenerable sort.
    moments=Path(summary).parent/'moments.npy'
    if binding(moments)!=s['moments']:raise ValueError('Measurement member not closed before sort release')
    write(path.parent/'sorted-released.json',dict(removed=str(path),binding=r['sorted'],source=r['source'],
        summary=binding(summary),reason='New regenerable coordinate sort; original private BAM remains immutable'))
    path.unlink()


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for n in ['record','features','views','output','samtools']:p.add_argument('--'+n,required=True,type=Path)
    p.add_argument('--gcloud',type=Path);p.add_argument('--summary-output',type=Path);p.add_argument('--engineering',action='store_true');a=p.parse_args()
    measure(json.loads(a.record.read_text()),a.features,a.views,a.output,a.samtools,a.gcloud,a.engineering,a.summary_output)
