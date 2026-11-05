#!/usr/bin/env python3
"""Run only the unchanged six-fit E033 DAG from verified retained measurements.

The logging-only repaired package has an explicit effective source/candidate lock.
All original acquisition, sort, measurement, sealing and state restore commands
are absent. A newly held parent, current-boot watcher and provider STOP release
this worker. Failures retain actual worker stderr and compact final delivery;
filesystem histories are separate bound files, never inlined into control JSON.
"""
import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time
import traceback
import urllib.request

ROOT=Path(__file__).absolute().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from e024_coverage import binding,write
from e021_control_json import publish
from e033_recovery import admit,DiskHistory,ORIGINAL,upload as storage_upload
from e009_owner import supervisor
from e009_exit_watchdog import identity

FIELDS={'root','repo','source_commit','operations_source','vm_start_epoch','boot_start_epoch',
 'review_deadline_epoch','provider_deadline_epoch','setup_deadline_epoch','service_name','user',
 'archive_prefix','plan','python','workflow_python','base','reference','wheel','pysam_wheel',
 'gcloud','financial','initial_filesystem_used_bytes','initial_filesystem_device',
 'source_filesystem','task_filesystem','limits','repair_lock','candidate_lock'}


def validate_config(c,now=None):
    """Admit the authorized common clock, unchanged resources and fresh full coverage."""
    now=time.time() if now is None else now
    if set(c)!=FIELDS:raise ValueError('Incomplete/unknown E033 resume configuration')
    f=c['financial'];l=c['limits']
    if (c['source_commit']!=c['operations_source'] or len(c['source_commit'])!=40
        or c['review_deadline_epoch']!=c['vm_start_epoch']+108000
        or not c['vm_start_epoch']<=c['boot_start_epoch']<=now<c['review_deadline_epoch']
        or not c['review_deadline_epoch']<c['provider_deadline_epoch']<=c['vm_start_epoch']+108900
        or c['provider_deadline_epoch']>=1794351600 or l['threads']!=4 or l['RSS_bytes']!=26_000_000_000
        or l['reserve_bytes']!=25*1024**3 or l['extra_bytes']!=60*1024**3
        or c['initial_filesystem_used_bytes']!=24576 or c['task_filesystem']!=ORIGINAL+'/task'
        or f['real_money_authorized']is not False or f['coverage_status']!='PASS_FOR_SPECIFIED_ORDINARY_FIRST_PARTY_PRODUCTS_ONLY'
        or not 0<=now-f['checked_epoch']<7200 or not 0<=now-f['credit_checked_epoch']<7200
        or not 0<f['estimated_complete_gross_USD']<=f['ceiling_USD']==20
        or c['provider_deadline_epoch']>=min(f['storage_valid_until_epoch'],f['credit_valid_until_epoch'])):
        raise ValueError('E033 recovery source/resource/clock/coverage differs')
    return True


def status(c,value):
    """Publish compact current phase progress; actual exits remain authoritative."""
    data=json.dumps(dict(value,root=c['root'],epoch=time.time())).encode()
    request=urllib.request.Request('http://metadata.google.internal/computeMetadata/v1/instance/guest-attributes/e033-candidate/status',data=data,method='PUT',headers={'Metadata-Flavor':'Google','Content-Type':'application/json'})
    try:
        with urllib.request.urlopen(request,timeout=3) as f:f.read(1024)
    except Exception as e:print('RECOVERY_GUEST_STATUS_UNAVAILABLE',repr(e),flush=True)


def retained(c,output):
    """Hash all twenty passed summaries/arrays and original payloads without redoing science."""
    from e024_control import verify_seal
    root=Path(ORIGINAL);plan=json.loads(Path(c['plan']).read_text())
    inventory=json.loads((root/'task/return-measurements/inventory.json').read_text())
    collection=json.loads((root/'task/return-measurements/collection.json').read_text())
    if binding(root/'task/return-measurements/e033-evidence.tar.gz')!=collection['archive']:
        raise ValueError('Retained accepted measurement archive differs')
    checked={}
    for name,wanted in inventory['all_work_members'].items():
        p=root/'task/measurements'/name
        if binding(p)!=wanted:raise ValueError('Passed measurement bytes differ; no fallback: '+name)
        checked[name]=wanted
    manifest=json.loads((ROOT/'experiments/E033-multiscale-bam/BAM-manifest.json').read_text())
    for i,record in enumerate(manifest['records']):
        p=root/'task/transports'/('%02d'%i)/'completed.json';r=json.loads(p.read_text())
        if r['status']!='PASS' or r['source']!=record or not r['original_alignment_unchanged']:
            raise ValueError('Passed original BAM source/sort path differs')
        if binding(r['summary_path']+'/sample.json')!=r['summary']:
            raise ValueError('Passed measurement receipt differs')
        if not record['sorted']:
            s=p.parent/'sort/sort.json';sort=json.loads(s.read_text())
            if binding(s)!=r['sorter'] or sort['source_exit'] or sort['sort_exit'] or sort['source']!=record:
                raise ValueError('Passed original sort contract differs')
    gate=json.loads((root/'gates/full-schedule.json').read_text())
    if gate['status']!='PASS':raise ValueError('Original full-shape schedule not admitted')
    for u in plan['units']:
        p=root/'gates'/('probe-'+u+'.json');v=json.loads(p.read_text())
        if v['status']!='PASS_FULL_SHAPE_PROBE' or not v['temporary_updates_not_consumed']:
            raise ValueError('Original full-shape probe differs')
    # Admit the actual completed independent global barrier, now recovered.
    old_barrier=verify_seal(root/'task/work/barrier')
    from e033_control import inputs
    if old_barrier['inputs']!=inputs(plan,'E009-noGLM'):
        raise ValueError('Old completed barrier does not match exact reused inputs')
    new=Path(plan['work'])/'barrier';new.parent.mkdir(parents=True,exist_ok=True)
    if not new.exists():shutil.copytree(root/'task/work/barrier',new)
    verify_seal(new)
    value=dict(status='PASS_VERIFIED_REUSE',measurements=checked,measurement_archive=collection['archive'],
        measurement_inventory=binding(root/'task/return-measurements/inventory.json'),
        original_barrier=binding(root/'task/work/barrier/done.json'),barrier_reused=True,
        BAM_measurement_sort_state_restore_replayed=False,actual_originals_after_separate_command=True)
    write(output,value);return value


def seal_evidence(root,plan):
    """Copy closed phase and actual global worker logs, excluding live resource history."""
    root=Path(root);out=root/'sealed-evidence';out.mkdir()
    for n in ['config.json','host.json','started.json','release.json','science-plan.json','science-result.json']:
        if(root/n).is_file():shutil.copyfile(root/n,out/n)
    logs=out/'logs';logs.mkdir()
    for p in (root/'logs').iterdir():
        if p.is_file() and p.name!='filesystem.jsonl':shutil.copyfile(p,logs/p.name)
    shutil.copytree(root/'gates',out/'gates')
    work=Path(plan['work'])
    for n,label in [('logs','workflow-logs'),('benchmarks','benchmarks'),('.snakemake/log','workflow-scheduler'),('barrier','barrier')]:
        if(work/n).exists():shutil.copytree(work/n,out/label)
    # Preserve remaining old global failure metadata before any eventual task release.
    for n in ['metadata','log']:
        p=Path(ORIGINAL)/'task/work/.snakemake'/n
        if p.exists():shutil.copytree(p,out/('old-workflow-'+n))
    src=out/'repair-source';src.mkdir()
    for n in ['repair-lock.json','repair-candidate-lock.json','source-lock.json','candidate-lock.json','protocol.json']:
        shutil.copyfile(ROOT/'experiments/E033-multiscale-bam'/n,src/n)
    return out


def run(path):
    """Gate only changed runtime/repair paths, reuse passed science, then run once."""
    path=Path(path);c=json.loads(path.read_text());validate_config(c);root=Path(c['root'])
    plan=json.loads(Path(c['plan']).read_text());deadline=c['review_deadline_epoch']
    result=dict(status='FAILED',science_completed=False,measurements_reused=True,stages=[])
    sup=supervisor();env=sup.isolated_env(4);env.update(NUMBA_NUM_THREADS='4',NUMBA_CACHE_DIR=str(Path(c['task_filesystem'])/'native-cache-r3'),
        TMPDIR=str(root/'tmp'),E033_RELEASE_FILE=str(root/'release.json'),HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1',TOKENIZERS_PARALLELISM='false')
    disk=None;final_history=None
    def command(label,argv,reserve=1200):
        left=deadline-time.time()-reserve
        if left<10:raise TimeoutError('Common E033 recovery deadline exhausted')
        status(c,dict(status='RUNNING',stage=label))
        try:r=sup.supervise(list(map(str,argv)),root/'logs'/(label+'.log'),left,26_000_000_000,env,sample_root=os.getpid())
        except BaseException:
            p=root/'logs'/(label+'.exit.json');result['stages'].append(dict(stage=label,resources=json.loads(p.read_text()) if p.exists() else dict(exit_code=None)));raise
        result['stages'].append(dict(stage=label,resources=r));disk.sample();return r
    publish(dict(pid=os.getpid(),identity=identity(os.getpid()),epoch=time.time()),root/'started.json')
    status(c,dict(status='HELD'))
    try:
        while not(root/'release.json').exists():
            if time.time()>=c['setup_deadline_epoch']:raise TimeoutError('Held recovery setup exhausted')
            time.sleep(.2)
        release=json.loads((root/'release.json').read_text());live=json.loads((root/'logs/watchdog-live-before-release.json').read_text())
        if (release['config']!=binding(path) or release['plan']!=binding(c['plan']) or not release['provider_STOP_verified']
            or live['expected_process']!=identity(os.getpid()) or live['boot_id']!=Path('/proc/sys/kernel/random/boot_id').read_text().strip()):
            raise ValueError('Recovery release source/boot/process/plan differs')
        if subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()!=c['source_commit'] or subprocess.check_output(['git','status','--porcelain'],cwd=ROOT,text=True).strip():
            raise ValueError('Clean exact recovery checkout required')
        repair,_,candidate=admit(c['repair_lock'])
        if c['limits']!=repair['limits'] or binding(candidate)!=binding(c['candidate_lock']):raise ValueError('Prospective effective runtime/limits differ')
        disk=DiskHistory(c);disk.start()
        command('original-inputs-before',['/usr/bin/python3','-I','-B',ROOT/'scripts/e033_verify.py','--plan',c['plan'],'--output',root/'gates/inputs-before.json'])
        retained(c,root/'gates/reuse.json')
        command('repaired-package-install',[Path(c['base'])/'bin/python','-I','-B',ROOT/'scripts/e033_install.py','--base',c['base'],'--destination',Path(c['python']).parents[1],
            '--wheel',c['wheel'],'--pysam-wheel',c['pysam_wheel'],'--lock',c['candidate_lock'],'--output',root/'gates/install.json'])
        command('repaired-complete-runtime',[c['python'],'-I','-B',ROOT/'scripts/e033_runtime.py','--base',c['base'],'--reference',c['reference'],'--candidate-lock',c['candidate_lock'],
            '--pysam-wheel',c['pysam_wheel'],'--output',root/'gates/runtime.json'])
        command('repaired-plan',[c['python'],'-I','-B',ROOT/'scripts/e033_control.py','--plan',c['plan'],'--check-plan'])
        from e029_gates import unit_command
        command('actual-progress-64-and-learning',[c['python'],'-I','-B','-c',unit_command(ROOT,'test_multiscale_progress')])
        command('actual-repaired-serial-tiny',[c['python'],'-I','-B',ROOT/'scripts/e033_tiny.py','--root',root/'gates/tiny','--workflow-python',c['workflow_python']])
        forecast=json.loads((Path(ORIGINAL)/'gates/full-schedule.json').read_text())['forecast_remaining']
        if forecast>=deadline-time.time()-1200:raise ValueError('Remaining complete schedule needs a prospective covered revision')
        write(root/'gates/full-schedule.json',dict(status='PASS_REUSED_MATH_IDENTICAL_FORECAST',forecast_seconds=forecast,remaining=deadline-time.time(),no_probe_replayed=True))
        command('serial-six-fit-three-mode',[c['python'],'-I','-B',ROOT/'scripts/e033_control.py','--plan',c['plan'],'--workflow'])
        if not all((Path(plan['work'])/u/'audit/done.json').is_file() for u in plan['units']):raise ValueError('Every scientific final target required')
        command('original-inputs-after',['/usr/bin/python3','-I','-B',ROOT/'scripts/e033_verify.py','--plan',c['plan'],'--output',root/'gates/inputs-after.json'])
        if json.loads((root/'gates/inputs-before.json').read_text())!=json.loads((root/'gates/inputs-after.json').read_text()):raise ValueError('Original inputs-after differs')
        result['science_completed']=True
    except BaseException as error:
        result.update(error=repr(error),traceback=traceback.format_exc());print(result['traceback'],flush=True)
    result['status']='SCIENCE_COMPLETED_PENDING_COLLECTION' if result['science_completed'] else 'FAILED'
    publish(result,root/'science-result.json')
    try:
        evidence=seal_evidence(root,plan)
        old=Path(ORIGINAL)/'task/return-measurements'
        old_collection=json.loads((old/'collection.json').read_text())
        collections=[dict(label='measurements',reused=True,prefix='gs://dl-binner-archive-167650584170/e033/multiscale-20261104T152005Z-a940769-r2/measurements/',
                          archive=old_collection['archive'],inventory=binding(old/'inventory.json'))]
        total=old_collection['archive']['bytes']
        for u in plan['units']:
            at=Path(plan['work'])/u
            if not at.exists():continue
            out=Path(c['task_filesystem'])/('return-repair-'+u)
            command('collect-'+u,['/usr/bin/python3','-I','-B',ROOT/'scripts/e033_collect.py','--work',at,'--evidence',evidence,'--output',out],900)
            value=json.loads((out/'collection.json').read_text());total+=value['archive']['bytes']
            if total>12*1024**3:raise ValueError('Aggregate complete return cap exceeded')
            delivered={}
            for name in ['e033-evidence.tar.gz','inventory.json','collection.json','e033-evidence.tar.gz.sha256']:
                status(c,dict(status='RUNNING',stage='delivery-'+u+'-'+name))
                delivered[name]=storage_upload(out/name,c['archive_prefix']+u+'/'+name)
            collections.append(dict(label=u,reused=False,archive=value['archive'],inventory=binding(out/'inventory.json'),delivered=delivered))
        result.update(collections=collections,collection_readback_verified=True,status='SUCCESS' if result['science_completed'] else 'FAILED')
    except BaseException as error:
        result.update(status='FAILED',collection_error=repr(error),collection_traceback=traceback.format_exc());print(result['collection_traceback'],flush=True)
    result.update(source=c['source_commit'],root=str(root),finished_epoch=time.time(),repair_lock=binding(c['repair_lock']),candidate_lock=binding(c['candidate_lock']))
    # All long histories and actual post-collector logs are outside the compact
    # completion control, including on a first-science failure.
    try:
        post=root/'closed-delivery-evidence';post.mkdir();(post/'logs').mkdir()
        for p in (root/'logs').iterdir():
            if p.is_file() and p.name!='filesystem.jsonl':shutil.copyfile(p,post/'logs'/p.name)
        publish(result,post/'result-before-completion.json')
        from e033_collect import pack
        empty=root/'closed-delivery-empty';empty.mkdir()
        proof=pack(post,empty,root/'closed-delivery-return')
        result['closed_delivery_archive']=storage_upload(root/'closed-delivery-return/e033-evidence.tar.gz',c['archive_prefix']+'closed-delivery/e033-evidence.tar.gz')
        result['closed_delivery_inventory']=storage_upload(root/'closed-delivery-return/inventory.json',c['archive_prefix']+'closed-delivery/inventory.json')
        if disk is not None:
            final_history=disk.close();result['filesystem']=final_history
            if final_history['monitor_error'] is not None:result['status']='FAILED'
            result['filesystem_delivery']=storage_upload(root/'logs/filesystem.jsonl',c['archive_prefix']+'filesystem.jsonl')
        if time.time()>=deadline-15:raise TimeoutError('Common clock cannot admit final delivery')
        publish(result,root/'completion.json')
        delivered=storage_upload(root/'completion.json',c['archive_prefix']+'completion.json')
        tail=dict(status='PASS',completion=delivered,epoch=time.time(),science_completed=result['science_completed'])
        publish(tail,root/'closed-delivery-tail.json');storage_upload(root/'closed-delivery-tail.json',c['archive_prefix']+'closed-delivery-tail.json')
    except BaseException as error:
        print('RECOVERY_FINAL_DELIVERY_FAILED',repr(error),flush=True);status(c,dict(status='FAILED_FINAL_DELIVERY',error=repr(error)));return 1
    status(c,dict(status=result['status'],science_completed=result['science_completed'],completion_delivery_verified=True))
    return 0 if result['status']=='SUCCESS' else 1


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--config',required=True,type=Path)
    raise SystemExit(run(p.parse_args().config))
