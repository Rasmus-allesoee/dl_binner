#!/usr/bin/env python3
"""Exercise the real new data DAG against tiny loopback HTTP archives on macOS.

Requires explicit existing native runtime paths. Uses the tracked software DNA
fixture, one-thread Mac MEGAHIT and ten actual mapping/depth contracts; no worker,
extractor or aligner is mocked. Prefixes are read-only. Outputs/logs persist in a
new QA directory. This is portable software validation, never GCP throughput or
biological benchmark evidence.
"""
import argparse
import csv
import gzip
import hashlib
import http.server as httpserver
import io
import json
from pathlib import Path
import re
import subprocess
import sys
import tarfile
import threading
import zipfile

sys.path.insert(0,str(Path(__file__).absolute().parent))
from e009_common import binding, write_json
from e009_gcp_run import verify_completed


def put_tar(path, entries):
    """Write fresh byte-exact input members for the production tar reader."""
    with tarfile.open(path,'w:gz') as tar:
        for name,data in entries:
            m=tarfile.TarInfo(name);m.size=len(data);tar.addfile(m,io.BytesIO(data))


def main():
    """Run fresh partial, recovered and completed DAGs, then verify a drift refusal."""
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True)
    p.add_argument('--python',required=True);p.add_argument('--samtools',required=True);p.add_argument('--strobealign',required=True)
    p.add_argument('--minimap2',required=True);p.add_argument('--megahit',required=True);a=p.parse_args()
    root=a.output.absolute();root.mkdir(parents=True,exist_ok=False);http=root/'http';http.mkdir()
    repo=Path(__file__).absolute().parents[1]
    with zipfile.ZipFile(repo/'tests/fixtures/e009-native-inputs-v2.zip') as z:
        raw={n:z.read(n) for n in z.namelist()}
    def member(name):return next(v for k,v in raw.items() if k.endswith('/'+name) or k==name)
    left=member('reads_1.fq').decode().splitlines();right=member('reads_2.fq').decode().splitlines()
    indices=[0,2,3,4,6,9,10,11,14,17];counts={}
    for j,sample in enumerate(indices):
        count=len(left)//4-j*10;counts[sample]=count;mates=[[],[]];origins=[]
        for i in range(count):
            for k,lines in enumerate((left,right)):
                record=lines[4*i:4*i+4];record[0]=f'@S{sample}R{i}/{k+1}';mates[k].extend(record)
                origins.append(f'S{sample}R{i}/{k+1}\tfixture\t1\toriginal{i}/{k+1}\n')
        if j%2==0:
            inter=[]
            for i in range(count):inter.extend(mates[0][4*i:4*i+4]+mates[1][4*i:4*i+4])
            entries=[(f'sample_{sample}/anonymous_reads.fq.gz',gzip.compress(('\n'.join(inter)+'\n').encode()))]
        else:
            entries=[(f'sample_{sample}/reads_{k+1}.fq',('\n'.join(m)+'\n').encode()) for k,m in enumerate(mates)]
        if sample==0:entries.append(('sample_0/reads_mapping.tsv.gz',gzip.compress(
            ('#anonymous_read_id\tgenome_id\ttax_id\tread_id\n'+''.join(origins)).encode())))
        put_tar(http/f'reads_{sample}.tar.gz',entries)
    put_tar(http/'sources.tar.gz',[('sources/fixture.fna',member('assembly.fna')),
                                 ('sources/competitor.fna',member('assembly.fna'))])
    class Quiet(httpserver.SimpleHTTPRequestHandler):
        """Serve tiny local objects without noisy access messages."""
        def __init__(self,*args,**kwargs):super().__init__(*args,directory=str(http),**kwargs)
        def log_message(self,*args):pass
    server=httpserver.ThreadingHTTPServer(('127.0.0.1',0),Quiet)
    thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
    try:
        base=f'http://127.0.0.1:{server.server_port}/'
        def spec(name):return {'url':base+name,**binding(http/name)}
        plan={'samples':[{'sample':s,'subject':f'S{j+1}','column':f'fixture_{s}',**spec(f'reads_{s}.tar.gz')} for j,s in enumerate(indices)],
              'source_genomes':spec('sources.tar.gz'),'development_overlap':{'accessions':[],'canonical_replicon_sha256s':[]},
              'sample0_source_files':['fixture.fna','competitor.fna'],'truth_batch_bp':30000,'source_expanded_bytes_max':1000000,
              'read_archive_expanded_bytes_max':1000000,'eligible_contig_scale_stop':32,'assembly_bp_scale_stop':600000}
        write_json(root/'plan.json',plan)
        runtime={n:getattr(a,n) for n in ('python','samtools','strobealign','minimap2','megahit')}
        write_json(root/'runtime.json',runtime)
        work=root/'work'
        argv=[a.python,'-I','-B',repo/'scripts/e009_gcp_run.py','--execute','--fixture','--root',work,
              '--plan',root/'plan.json','--runtime-json',root/'runtime.json','--allocated-vcpus','4',
              '--allocated-ram-gib','8','--free-gib','0','--hours','.25','--stall-seconds','300']
        results=[]
        def run(label,extra,expected=0):
            log=root/(label+'.log')
            with log.open('xb') as out:r=subprocess.run([str(v) for v in [*argv,*extra]],stdout=out,stderr=subprocess.STDOUT)
            if r.returncode!=expected:raise RuntimeError(f'{label}: expected {expected}, got {r.returncode}; {log}')
            results.append({'label':label,'exit_code':r.returncode,'log':str(log),'file':binding(log)})
        run('fresh-partial',['--fixture-until','assembly'])
        before={str(p):binding(p) for p in (work/'parts').glob('*/done.json')}
        run('recovered',['--resume'])
        if any(binding(p)!=v for p,v in before.items()):raise ValueError('Completed sources/assembly were replayed or changed')
        verify_completed(work)
        done_before={str(p):binding(p) for p in (work/'parts').glob('*/done.json')}
        run('completed',['--resume'])
        if any(binding(p)!=v for p,v in done_before.items()):raise ValueError('Completed DAG outputs changed')
        matrix=list(csv.reader((work/'parts/final/depth.tsv').open(),delimiter='\t'))
        if matrix[0]!=['contig_id',*[f'fixture_{s}' for s in indices]]:raise ValueError('Ten ordered depth columns changed')
        if not any(float(r[1])>0 for r in matrix[1:]):raise ValueError('Actual native mapping/depth has no positive evidence')
        if not any(len(set(map(float,r[1:])))>2 for r in matrix[1:]):
            raise ValueError('Distinct actual ten-sample depth values were not preserved')
        truth=json.loads((work/'parts/final/alignment-truth/truth.json').read_text())
        if not all(c['AMBER_label'] is None and c['ambiguous_query_bp']>0 for c in truth['contigs'].values()):
            raise ValueError('Actual competing genomes across reference batches became a false unique origin')
        for sample in indices:
            stage=json.loads((work/f'parts/map_{sample:04d}/done.json').read_text())['payload']
            if stage['reads']['validation']['pairs']!=counts[sample]:raise ValueError('Native sample identity/count changed')
            if (Path(stage['bam']).parent/'alignment.sam').exists():raise ValueError('Regenerable SAM was not pruned after BAM admission')
        changed=json.loads((root/'plan.json').read_text());changed['truth_batch_bp']+=1
        (root/'plan.json').write_text(json.dumps(changed))
        run('changed-plan-refused',['--resume'],1)
        if 'identical source/config/runtime' not in (root/'changed-plan-refused.log').read_text():
            raise ValueError('Wrong failure caused the negative plan check')
        receipt={'scope':'actual new data DAG; tiny loopback archives; no worker/extractor mocks or binner fits',
                 'native_linux_or_scale_validated':False,'mac_assembly_threads':1,'allocated_vcpus':4,
                 'ordered_sample_ids':indices,'counts':counts,'results':results,'completed_stage_bytes_unchanged':True,
                 'matrix_rows':len(matrix)-1,'positive_depth_observed':True,'benchmark_rules':len(list((work/'benchmarks').glob('*.tsv'))),
                 'distinct_native_depth_values':True,
                 'cross_batch_competing_genomes_remain_ambiguous':True,
                 'source_grouping_and_cellular_taxonomy_not_admitted':True}
        write_json(root/'passed.json',receipt);print(json.dumps(receipt,indent=2))
    finally:server.shutdown();server.server_close();thread.join(timeout=2)


if __name__=='__main__':main()
