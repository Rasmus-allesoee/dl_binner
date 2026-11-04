#!/usr/bin/env python3
"""Prepared held-parent E033 measurement/learning/collection phase, never a VM start.

The external controller owns fresh credit/resource/source/provider admission and
arms a current-boot/PID watcher before releasing this parent. All work shares the
original VM-start deadline. No provisioning, mapping, new reads or external binner
is exposed here. Failed outputs are preserved; there is no automatic science retry.
"""
import argparse
import json
import math
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time
import threading
import signal
import urllib.request

ROOT=Path(__file__).absolute().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from e024_coverage import binding,write
from e021_control_json import publish
from e009_owner import supervisor
from e009_exit_watchdog import identity

RETENTION=1794351600


def validate_config(c,now=None):
    """Require fresh complete-cost credit coverage and one original clock/source."""
    fields={'root','repo','source_commit','operations_source','vm_start_epoch','review_deadline_epoch',
        'provider_deadline_epoch','setup_deadline_epoch','service_name','user','archive_prefix','plan',
        'python','workflow_python','base','reference','wheel','pysam_wheel','gcloud','samtools','financial',
        'initial_filesystem_used_bytes','initial_filesystem_device','source_filesystem','task_filesystem','limits'}
    if set(c)!=fields:raise ValueError('Incomplete/unknown E033 phase configuration')
    n=time.time() if now is None else now;f=c['financial'];l=c['limits']
    if (c['source_commit']!=c['operations_source'] or len(c['source_commit'])!=40
        or any(x not in '0123456789abcdef' for x in c['source_commit'])
        or c['review_deadline_epoch']!=c['vm_start_epoch']+l['seconds']
        or not c['vm_start_epoch']<=n<c['review_deadline_epoch']
        or not c['review_deadline_epoch']<c['provider_deadline_epoch']<=c['vm_start_epoch']+l['provider_STOP_seconds']
        or c['provider_deadline_epoch']>=RETENTION or l['threads']!=4 or l['RSS_bytes']!=26_000_000_000
        or l['reserve_bytes']!=25*1024**3 or l['extra_bytes']!=60*1024**3
        or f['real_money_authorized'] is not False or f['coverage_status']!='PASS_FOR_SPECIFIED_ORDINARY_FIRST_PARTY_PRODUCTS_ONLY'
        or f['ceiling_USD']!=l['ceiling_USD'] or not 0<=n-f['credit_checked_epoch']<7200 or not 0<=n-f['checked_epoch']<7200
        or not math.isfinite(f['estimated_complete_gross_USD']) or not 0<=f['estimated_complete_gross_USD']<=f['ceiling_USD']
        or c['provider_deadline_epoch']>=min(f['storage_valid_until_epoch'],f['credit_valid_until_epoch'])):
        raise ValueError('E033 source/clock/full-cost/credit/retention contract differs')
    return True


def status(v):
    """Publish only progress; actual stage/collection exits remain authoritative."""
    data=json.dumps(dict(v,epoch=time.time())).encode()
    request=urllib.request.Request('http://metadata.google.internal/computeMetadata/v1/instance/guest-attributes/e033-candidate/status',
        data=data,method='PUT',headers={'Metadata-Flavor':'Google','Content-Type':'application/json'})
    try:
        with urllib.request.urlopen(request,timeout=3) as f:f.read(1024)
    except Exception as e:print('E033_STATUS_UNAVAILABLE',repr(e),flush=True)


class DiskClock:
    """Monitor actual source/task devices and the original deadline continuously."""
    def __init__(self,c):
        self.c=c;self.done=threading.Event();self.reason=None;self.samples=[]

    def start(self):
        """Install one main-thread alarm; disk violation interrupts supervised work."""
        c=self.c
        if os.stat(c['task_filesystem']).st_dev!=c['initial_filesystem_device']:
            raise ValueError('Task baseline belongs to another filesystem/device')
        self.previous=signal.getsignal(signal.SIGALRM)
        def alarm(signum,frame):raise TimeoutError(self.reason or 'Original cumulative E033 deadline exhausted')
        signal.signal(signal.SIGALRM,alarm);signal.setitimer(signal.ITIMER_REAL,max(.001,c['review_deadline_epoch']-time.time()))
        def sample():
            while not self.done.wait(.2):
                try:
                    task=shutil.disk_usage(c['task_filesystem']);source=shutil.disk_usage(c['source_filesystem'])
                    if os.stat(c['task_filesystem']).st_dev!=c['initial_filesystem_device']:raise ValueError('Task device changed')
                    if not self.samples or time.monotonic()-self.samples[-1]['monotonic']>=2:
                        self.samples.append(dict(monotonic=time.monotonic(),epoch=time.time(),task_used=task.used,task_free=task.free,source_free=source.free))
                    if min(task.free,source.free)<25*1024**3:self.reason='Actual source/task 25 GiB reserve violated'
                    if task.used-c['initial_filesystem_used_bytes']>60*1024**3:self.reason='Actual cumulative task 60 GiB growth violated'
                except BaseException as e:self.reason='Disk monitoring failed: '+repr(e)
                if self.reason:os.kill(os.getpid(),signal.SIGALRM);return
        self.thread=threading.Thread(target=sample,daemon=True);self.thread.start()

    def close(self):
        """Stop sampling and restore the caller's signal handler without extensions."""
        self.done.set()
        if hasattr(self,'thread'):self.thread.join(timeout=2)
        if hasattr(self,'previous'):
            signal.setitimer(signal.ITIMER_REAL,0);signal.signal(signal.SIGALRM,self.previous)


def run(path):
    """Gate, pilot, verify reused measurements, execute once, collect and exit."""
    path=Path(path);c=json.loads(path.read_text());validate_config(c)
    root=Path(c['root']);plan=json.loads(Path(c['plan']).read_text());deadline=c['review_deadline_epoch']
    root.joinpath('logs').mkdir(exist_ok=True);root.joinpath('gates').mkdir(exist_ok=True)
    task=Path(c['task_filesystem'])
    (root/'tmp').mkdir(exist_ok=True)
    disk=None
    result=dict(status='FAILED',science_completed=False,measurements_completed=False,stages=[])
    publish(dict(pid=os.getpid(),identity=identity(os.getpid()),epoch=time.time()),root/'started.json')
    sup=supervisor();env=sup.isolated_env(4);env.update(NUMBA_NUM_THREADS='4',NUMBA_CACHE_DIR=str(task/'native-cache'),
        TMPDIR=str(root/'tmp'),E033_RELEASE_FILE=str(root/'release.json'),HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1',TOKENIZERS_PARALLELISM='false')
    def guard():
        if os.stat(task).st_dev!=c['initial_filesystem_device']:raise ValueError('Current task device differs from baseline')
        used=shutil.disk_usage(task);source=shutil.disk_usage(c['source_filesystem'])
        if min(used.free,source.free)<25*1024**3 or used.used-c['initial_filesystem_used_bytes']>60*1024**3:
            raise RuntimeError('Original task/source reserve or cumulative growth refused')
    def command(label,argv,reserve=1200):
        guard();remaining=deadline-time.time()-reserve
        if remaining<10:raise TimeoutError('Original cumulative E033 clock exhausted')
        status(dict(status='RUNNING',stage=label,root=str(root)))
        try:r=sup.supervise(list(map(str,argv)),root/'logs'/(label+'.log'),remaining,26_000_000_000,env,sample_root=os.getpid())
        except BaseException:
            p=root/'logs'/(label+'.exit.json');result['stages'].append(dict(stage=label,resources=json.loads(p.read_text()) if p.exists() else dict(exit_code=None)))
            raise
        result['stages'].append(dict(stage=label,resources=r));guard();return r
    try:
        status(dict(status='HELD',root=str(root)))
        while not(root/'release.json').exists():
            if time.time()>=c['setup_deadline_epoch']:raise TimeoutError('Held setup clock exhausted')
            time.sleep(.2)
        release=json.loads((root/'release.json').read_text());watch=json.loads((root/'logs/watchdog-live-before-release.json').read_text())
        if (release['config']!=binding(path) or release['plan']!=binding(c['plan']) or not release['provider_STOP_verified']
            or watch['expected_process']!=identity(os.getpid()) or watch['boot_id']!=Path('/proc/sys/kernel/random/boot_id').read_text().strip()):
            raise ValueError('Current boot/process/source/provider release differs')
        if subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()!=c['source_commit'] or subprocess.check_output(['git','status','--porcelain'],cwd=ROOT,text=True).strip():
            raise ValueError('Exact clean scientific source required')
        source=json.loads((ROOT/'experiments/E033-multiscale-bam/source-lock.json').read_text())
        for n,b in source['files'].items():
            if binding(ROOT/n)!=b:raise ValueError('Frozen source drift: '+n)
        if not task.is_dir():raise ValueError('Controller-admitted task filesystem missing')
        disk=DiskClock(c);disk.start()
        for p in [task/'measurements',task/'transports',Path(plan['work'])]:p.mkdir(parents=True,exist_ok=True)
        from e023_gates import workflow_probe
        command('workflow-origin',[c['workflow_python'],'-I','-B','-c',workflow_probe('3.12.10','9.16.3')])
        command('package-install',[Path(c['base'])/'bin/python','-I','-B',ROOT/'scripts/e033_install.py','--base',c['base'],
            '--destination',task/'env','--wheel',c['wheel'],'--pysam-wheel',c['pysam_wheel'],'--lock',ROOT/'experiments/E033-multiscale-bam/candidate-lock.json','--output',root/'gates/install.json'])
        command('native-complete-runtime',[c['python'],'-I','-B',ROOT/'scripts/e033_runtime.py','--base',c['base'],'--reference',c['reference'],
            '--candidate-lock',ROOT/'experiments/E033-multiscale-bam/candidate-lock.json','--pysam-wheel',c['pysam_wheel'],'--output',root/'gates/runtime.json'])
        command('native-plan-contract',[c['python'],'-I','-B',ROOT/'scripts/e033_control.py','--plan',c['plan'],'--check-plan'])
        from e029_gates import unit_command
        for module in ['test_multiscale_measurement','test_multiscale_learning']:
            command('native-'+module,[c['python'],'-I','-B','-c',unit_command(ROOT,module)])
        command('actual-native-serial-tiny',[c['python'],'-I','-B',ROOT/'scripts/e033_tiny.py','--root',root/'gates/tiny','--workflow-python',c['workflow_python']])
        reuse=json.loads((ROOT/'experiments/E033-multiscale-bam/reuse-lock.json').read_text())
        for n,b in reuse['external_files'].items():
            if binding(n)!=b:raise ValueError('Missing/corrupt original input, no fallback: '+n)
        command('restore-original-E031-states',['/usr/bin/python3','-I','-B',ROOT/'scripts/e033_restore.py',
            '--lock',ROOT/'experiments/E032-biological-candidate-selection/restore-lock.json','--root',task/'restored','--gcloud',c['gcloud']])
        manifest=json.loads((ROOT/'experiments/E033-multiscale-bam/BAM-manifest.json').read_text());records=manifest['records']
        # Keep the largest Oral BAM and the first E009 as accepted pilot summaries;
        # later iteration verifies/uses them rather than measuring again.
        pilots=[next(i for i,r in enumerate(records) if r['sample']==s) for s in manifest['pilot_samples']]
        completed={};sample_rows={};elapsed={}
        for at in pilots+[i for i in range(20) if i not in pilots]:
            record=records[at];community=record['community'];members=[r for r in records if r['community']==community]
            j=next(j for j,r in enumerate(members) if r['sample']==record['sample'])
            unit='oral-noGLM' if community=='oral' else 'E009-noGLM';entry=plan['units'][unit]
            bank=Path(plan['measurements'][community]['bank']);bank.mkdir(exist_ok=True)
            sample_out=bank/('sample-%02d'%j);transport=task/'transports'/('%02d'%at);record_path=root/('record-%02d.json'%at)
            write(record_path,record);start=time.monotonic()
            command('sample-%02d'%at,[c['python'],'-I','-B',ROOT/'scripts/e033_measure.py','--record',record_path,
                '--features',entry['features'],'--views',entry['views'],'--output',transport,'--summary-output',sample_out,
                '--samtools',c['samtools'],'--gcloud',c['gcloud']])
            elapsed[at]=time.monotonic()-start;completed[at]=binding(sample_out/'sample.json')
            if not record['sorted']:
                from e033_measure import release_sorted
                release_sorted(transport/'sort/sorted.bam',transport/'sort/sort.json',sample_out/'sample.json')
            if len(completed)==2:
                estimates={}
                for k in pilots:
                    r=records[k];estimates[r['community']]=elapsed[k]*sum(x['bytes'] for x in records if x['community']==r['community'])/r['bytes']*2
                remaining_measurements=sum(estimates.values())-sum(elapsed.values())
                # This pre-fit pilot covers measurement only. A conservative
                # 18-hour learning/construction and 2-hour closure allowance
                # must fit now; later full-shape probes must independently pass.
                needed=remaining_measurements+20*3600
                write(root/'gates/BAM-pilot.json',dict(status='PASS' if needed<deadline-time.time() else 'REFUSED',pilot_indices=pilots,
                    pilot_elapsed=elapsed,measurement_forecast=estimates,remaining_total_seconds=needed,remaining_clock=deadline-time.time()))
                if needed>=deadline-time.time():raise ValueError('Pilot complete schedule needs prospective credit-covered revision')
        for community,mode in [('E009','E009-noGLM'),('oral','oral-noGLM')]:
            e=plan['units'][mode];m=plan['measurements'][community]
            command('seal-'+community,[c['python'],'-I','-B',ROOT/'scripts/e033_bank.py','--root',m['bank'],'--features',e['features'],'--views',e['views'],'--output',m['new_features']])
        result['measurements_completed']=True
        forecast=0.
        for u,e in plan['units'].items():
            m=plan['measurements'][e['community']];out=root/'gates'/('probe-'+u+'.json')
            argv=[c['python'],'-I','-B',ROOT/'scripts/e033_probe.py','--features',e['features'],'--new-features',m['new_features'],
                '--views',e['views'],'--tokens',e['tokens'],'--measurements',m['bank'],'--original',e['original'],'--output',out]
            if e['frozen']:argv+=['--frozen',e['frozen']]
            command('full-shape-'+u,argv);forecast+=json.loads(out.read_text())['two_fit_estimate_with_student_and_uncertainty_seconds']
        forecast+=3*3600
        write(root/'gates/full-schedule.json',dict(status='PASS' if forecast<deadline-time.time()-1200 else 'REFUSED',forecast_remaining=forecast,remaining=deadline-time.time()))
        if forecast>=deadline-time.time()-1200:raise ValueError('Native full schedule requires a recorded covered revision before fits')
        command('serial-six-fit-three-mode',[c['python'],'-I','-B',ROOT/'scripts/e033_control.py','--plan',c['plan'],'--workflow'])
        if not all((Path(plan['work'])/u/'audit/done.json').is_file() for u in plan['units']):raise ValueError('Every scientific final target required')
        command('readonly-inputs-after',['/usr/bin/python3','-I','-B',ROOT/'scripts/e033_verify.py','--plan',c['plan'],'--output',root/'gates/inputs-after.json'])
        result['science_completed']=True
    except BaseException as e:result['error']=repr(e)
    result['status']='SCIENCE_COMPLETED_PENDING_COLLECTION' if result['science_completed'] else 'FAILED'
    publish(result,root/'science-result.json')
    # Seal only bounded closed logs/gates. Temporary sorted BAMs stay outside
    # scientific collections and are never silently mistaken for retained inputs.
    try:
        evidence=root/'sealed-evidence';evidence.mkdir()
        for name in ['config.json','host.json','release.json','started.json','science-result.json']:
            if(root/name).is_file():shutil.copyfile(root/name,evidence/name)
        shutil.copytree(root/'logs',evidence/'logs');shutil.copytree(root/'gates',evidence/'gates')
        for p in root.glob('record-*.json'):shutil.copyfile(p,evidence/p.name)
        for p in (task/'transports').rglob('*'):
            if p.is_file() and p.suffix in ['.json','.stderr']:
                target=evidence/'transports'/p.relative_to(task/'transports');target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,target)
        collections=[]
        sources=[('measurements',task/'measurements')]+[(u,Path(plan['work'])/u) for u in plan['units'] if (Path(plan['work'])/u).exists()]
        for label,work in sources:
            out=task/('return-'+label)
            command('collect-'+label,['/usr/bin/python3','-I','-B',ROOT/'scripts/e033_collect.py','--work',work,'--evidence',evidence,'--output',out],reserve=900)
            from e030_phase import upload_command
            prefix=c['archive_prefix']+label+'/'
            for name in ['e033-evidence.tar.gz','inventory.json','collection.json','e033-evidence.tar.gz.sha256']:
                local=out/name;uri=prefix+name
                command('upload-'+label+'-'+name,upload_command(c['gcloud'],local,uri),reserve=180)
                command('readback-'+label+'-'+name,['/usr/bin/python3','-I','-B',ROOT/'scripts/e030_phase.py','--readback',uri,'--gcloud',c['gcloud'],
                    '--bytes',str(local.stat().st_size),'--sha256',binding(local)['sha256']],reserve=120)
            collections.append(dict(label=label,prefix=prefix,archive=binding(out/'e033-evidence.tar.gz'),inventory=binding(out/'inventory.json')))
        result.update(collections=collections,collection_readback_verified=True,status='SUCCESS' if result['science_completed'] else 'FAILED')
    except BaseException as e:result['collection_error']=repr(e)
    result.update(finished_epoch=time.time(),source=c['source_commit'],root=str(root),
        filesystem_samples=disk.samples if disk is not None else [],initial_filesystem_used_bytes=c['initial_filesystem_used_bytes'],
        filesystem_scope='continuously sampled actual source/task devices, including collection; not exact kernel peak')
    publish(result,root/'completion.json')
    from e021_portable_node import storage_upload
    try:
        if time.time()>=deadline-30:raise TimeoutError('Original clock cannot admit final delivery')
        delivered=storage_upload(root/'completion.json',c['archive_prefix']+'completion.json')
        write(root/'logs/completion-upload.exit.json',dict(exit_code=0,private_readback=delivered,epoch=time.time()))
        tail=storage_upload(root/'logs/completion-upload.exit.json',c['archive_prefix']+'completion-upload-exit.json')
        write(root/'closed-delivery-tail.json',dict(status='PASS',completion=delivered,completion_exit=tail))
    except BaseException as e:
        status(dict(status='FAILED_FINAL_DELIVERY',error=repr(e),science_completed=result['science_completed']))
        if disk is not None:disk.close()
        return 1
    status(dict(status=result['status'],science_completed=result['science_completed'],completion_delivery_verified=True))
    if disk is not None:disk.close()
    return 0 if result['status']=='SUCCESS' else 1


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--config',required=True,type=Path);sys.exit(run(p.parse_args().config))
