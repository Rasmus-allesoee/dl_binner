#!/usr/bin/env python3
"""Run the actual E024 serial DAG on generated reads over a loopback HTTP server.

No public read request or community science is performed. Actual strobealign
indexes/mappings, checksum and gzip feeders, full-axis summaries, rebind, depth
retrieval, hierarchy/marker policy, FASTA exports, archive and completed-resume
are exercised from isolated Python subprocesses outside the checkout.
"""
import argparse
import functools
import gzip
import hashlib
import http.server
import json
import os
from pathlib import Path
import subprocess
import sys
import threading

ROOT = Path(__file__).absolute().parents[1]
sys.path[:0] = [str(ROOT/'src'),str(ROOT/'scripts'),str(ROOT/'tests')]
from e024_coverage import SAMPLES, binding, write
from e024_collect import pack
from test_e024_coverage import fixture, reads, MAPPER, SAMTOOLS


def tiny(root, workflow_python):
    """Execute one fresh 20-job fixture and verify no completed work is replayed."""
    root = Path(root).absolute()
    root.mkdir(parents=True,exist_ok=False)
    inputs = root/'inputs';inputs.mkdir()
    unit,dna = fixture(inputs)
    public = root/'http';public.mkdir()
    records = []
    for j,sample in enumerate(SAMPLES):
        d = public/str(sample);d.mkdir()
        raw,_,_ = reads(d,dna,sample)
        with gzip.open(raw,'at') as f:
            for n in range(1+j%3):
                seq=dna[2][1000+n*200:1150+n*200]
                mate=dna[2][1120+n*200:1270+n*200].translate(str.maketrans('ACGT','TGCA'))[::-1]
                f.write(f'@extra{n}/1\n{seq}\n+\n'+('I'*150)+'\n')
                f.write(f'@extra{n}/2\n{mate}\n+\n'+('I'*150)+'\n')
        payload=raw.read_bytes();mid=len(payload)//2
        parts=[dict(bytes=len(s),md5=hashlib.md5(s).hexdigest()) for s in [payload[:mid],payload[mid:]]]
        records.append(dict(sample=sample,bytes=len(payload),segments=parts))
    class Quiet(http.server.SimpleHTTPRequestHandler):
        def log_message(self,*args):
            pass
    handler=functools.partial(Quiet,directory=str(public))
    server=http.server.ThreadingHTTPServer(('127.0.0.1',0),handler)
    thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
    try:
        for r in records:r['url']=f'http://127.0.0.1:{server.server_port}/{r["sample"]}/raw.fq.gz'
        manifest=root/'reads.json'
        write(manifest,dict(ordered_samples=SAMPLES,total_read_bytes=sum(r['bytes'] for r in records),reads=records))
        plan=json.loads((ROOT/'experiments/E024-oral-measured-coverage/runtime-plan.json').read_text())
        plan.update(work=str(root/'work'),python=sys.executable,workflow_python=str(Path(workflow_python).absolute()),
                    mapper=str(MAPPER),samtools=str(SAMTOOLS),reference=str(unit['reference']),
                    inputs={k:str(v) for k,v in unit.items() if k != 'reference'},read_manifest=str(manifest),
                    policy=str(ROOT/'experiments/E023-adaptive-density-bins/config.json'),
                    worker=str(ROOT/'scripts/e024_control.py'),
                    snakefile=str(ROOT/'experiments/E024-oral-measured-coverage/Snakefile'),engineering=True)
        plan['alignment_archive']=dict(mode='local-fixture-bam',prefix=str(root/'retained-bams'),maximum_total_bytes=130*1024**3,maximum_sample_bytes=13*1024**3)
        write(root/'plan.json',plan)
        argv=[sys.executable,'-I','-B',str(ROOT/'scripts/e024_control.py'),'--plan',str(root/'plan.json'),'--engineering','--workflow']
        env=dict(os.environ,NUMBA_NUM_THREADS='4',NUMBA_CACHE_DIR=str(root/'jit'))
        def invoke(label,extra=None):
            with (root/(label+'.log')).open('x') as log:
                result=subprocess.run(argv+(extra or []),cwd=root,env=env,stdout=log,stderr=subprocess.STDOUT)
            write(root/(label+'.exit.json'),dict(argv=argv+(extra or []),exit=result.returncode))
            if result.returncode:raise RuntimeError('Actual E024 DAG failed: '+str(root/(label+'.log')))
        work=root/'work'
        invoke('accepted-first-sample',['--until-pilot'])
        accepted={str(p.relative_to(work)):binding(p) for name in ['verified','first-acquired','index','samples/6','pilot']
                  for p in (work/name).rglob('*') if p.is_file()}
        invoke('partial-resume-remaining-nine')
        for name,expected in accepted.items():
            if binding(work/name)!=expected:raise ValueError('Partial resume repeated/changed accepted sample6/pilot')
        depth=json.loads((work/'combined/depth.tsv.receipt.json').read_text())
        if depth['samples'] != [f'oral_sample_{s}' for s in SAMPLES] or depth['rows'] != 7:
            raise ValueError('Tiny actual full axis differs')
        if any((work/'downloads'/str(s)/'raw.fq.gz').exists() for s in SAMPLES):
            raise ValueError('Serial released raw unexpectedly retained')
        before={str(p.relative_to(work)):binding(p) for p in work.rglob('*') if p.is_file() and '.snakemake' not in p.parts}
        invoke('completed-resume')
        after={str(p.relative_to(work)):binding(p) for p in work.rglob('*') if p.is_file() and '.snakemake' not in p.parts}
        if before != after:raise ValueError('Completed resume changed/replayed accepted tiny outputs')
        if 'Nothing to be done' not in (root/'completed-resume.log').read_text():
            raise ValueError('Completed workflow did not report no-op')
        evidence=root/'evidence';evidence.mkdir()
        write(evidence/'scope.json',dict(synthetic=True,science='no community',actual_mapper='strobealign0.17.0',actual_summary=True))
        collection=pack(work,evidence,root/'return')
        result=dict(status='PASS',actual_DAG=True,actual_mapping=True,communities=0,samples=SAMPLES,
                    rows=7,bp=25380,serial_raw_released=True,partial_resume_only_remaining=True,completed_resume_noop=True,
                    complete_export=json.loads((work/'export/accounting.json').read_text()),
                    collection=collection,workflow_version=subprocess.check_output([str(workflow_python),'-I','-B','-m','snakemake','--version'],text=True).strip(),
                    pending='Linux3.12.10/Snakemake9.16.3, full GSA/index/RAM/throughput/headroom, credits, watcher and provider STOP')
        write(root/'completed.json',result)
        return result
    finally:
        server.shutdown();server.server_close();thread.join(5)


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root',type=Path,required=True)
    parser.add_argument('--workflow-python',type=Path,required=True)
    a=parser.parse_args()
    print(json.dumps(tiny(a.root,a.workflow_python)),flush=True)
