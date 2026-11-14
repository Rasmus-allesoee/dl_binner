#!/usr/bin/env python3
"""Held optional physical-graph comparison with independent shutdown and bounded delivery.

Only new graph adapters and fixed E032 construction are exposed. Accepted BAM
ledgers and learning are restored, never replayed. Every operation shares the
VM-start clock, including setup and complete evidence collection.
"""
import argparse
import math
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
from e009_owner import supervisor
from e009_exit_watchdog import identity
from e033_recovery import DiskHistory
from e021_portable_node import storage_upload
EXP=ROOT/'experiments/E036-optional-pooled-links'


def freeze_sources():
    """Verify the exact original product and newly frozen optional wrapper."""
    for n,b in json.loads((EXP/'source-lock.json').read_text())['files'].items():
        if binding(ROOT/n)!=b:raise ValueError('Frozen E036 source differs: '+n)


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
        or c['provider_deadline_epoch']>=__import__('datetime').datetime.fromisoformat(l['retention_end']).timestamp() or l['threads']!=4 or l['RSS_bytes']!=26_000_000_000
        or l['reserve_bytes']!=25*1024**3 or l['extra_bytes']!=60*1024**3
        or l!=json.loads((EXP/'limits.json').read_text())
        or not c['root'].startswith('/srv/dl_binner/experiments/e036/')
        or not c['service_name'].startswith('e036-')
        or f['real_money_authorized'] is not False or f['coverage_status']!='PASS_FOR_SPECIFIED_ORDINARY_FIRST_PARTY_PRODUCTS_ONLY'
        or f['ceiling_USD']!=l['ceiling_USD'] or not 0<=n-f['credit_checked_epoch']<7200 or not 0<=n-f['checked_epoch']<7200
        or not math.isfinite(f['estimated_complete_gross_USD']) or not 0<=f['estimated_complete_gross_USD']<=f['ceiling_USD']
        or c['provider_deadline_epoch']>=min(f['storage_valid_until_epoch'],f['credit_valid_until_epoch'])):
        raise ValueError('E033 source/clock/full-cost/credit/retention contract differs')
    if f['Welcome_credit_remaining_DKK']/f['DKK_per_USD']-f['reserve_USD']<f['ceiling_USD']:raise ValueError('Fresh credit headroom insufficient')
    return True


def status(c,value):
    """Publish a compact progress pointer, separately from actual stage exits."""
    q=urllib.request.Request('http://metadata.google.internal/computeMetadata/v1/instance/guest-attributes/e036-candidate/status',
        data=json.dumps(dict(value,root=c['root'],source=c['source_commit'],epoch=time.time())).encode(),method='PUT',headers={'Metadata-Flavor':'Google','Content-Type':'application/json'})
    try:
        with urllib.request.urlopen(q,timeout=3)as f:f.read(1024)
    except Exception as e:print('E036_STATUS_UNAVAILABLE',repr(e),flush=True)


def evidence(root):
    """Snapshot closed logs and all locked sources; exclude histories/auth caches."""
    from e034_phase import evidence as snapshot
    root=Path(root);out=snapshot(root);c=json.loads((root/'config.json').read_text());repo=Path(c['repo'])
    source=out/'source-repository';source.mkdir();names={}
    for label in ['source-lock.json']:
        lock=repo/'experiments/E036-optional-pooled-links'/label
        names[str(lock.relative_to(repo))]=binding(lock)
        names.update(json.loads(lock.read_text())['files'])
    for name,wanted in names.items():
        p=repo/name
        if binding(p)!=wanted:raise ValueError('Source changed before collection: '+name)
        target=source/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,target)
    packet=repo.parent/'experiments/e036/source-transports'/('source-'+c['source_commit']+'.bundle')
    if binding(packet)!=c['financial']['source_transport']['bundle']:raise ValueError('Native exact source bundle differs')
    shutil.copyfile(packet,out/'source.bundle')
    for p in (root/'payload').glob('*.whl'):shutil.copyfile(p,out/p.name)
    return out


def collect(c,result):
    """Retain every new closed science member, fallback proof and source/log tail."""
    from e035_collect import pack,verify
    root=Path(c['root']);task=Path(c['task_filesystem']);source=task/'science';source.mkdir(exist_ok=True)
    work=task/'science-return';work.mkdir();excluded=[]
    for p in source.rglob('*'):
        if '.snakemake'in p.parts:
            if p.is_file():excluded.append(dict(name=str(p.relative_to(source)),reason='Regenerable scheduler metadata; actual DAG stdout/stderr and scientific stage receipts retained'))
            continue
        if p.is_symlink():raise ValueError('Scientific return symlink refused')
        if p.is_file():
            q=work/p.relative_to(source);q.parent.mkdir(parents=True,exist_ok=True);os.link(p,q)
    write(work/'scheduler-exclusions.json',excluded)
    e=evidence(root);returned=task/'return';packed=pack(work,e,returned);verify(returned)
    files=[p for p in sorted(returned.rglob('*'))if p.is_file()and not any(x.startswith('stage-')for x in p.relative_to(returned).parts)]
    total=sum(p.stat().st_size for p in files)
    if total>c['limits']['aggregate_compressed_bytes']:raise ValueError('Complete return exceeds frozen aggregate cap; no omission fallback')
    delivered={str(p.relative_to(returned)):storage_upload(p,c['archive_prefix']+'comparison/'+str(p.relative_to(returned)))for p in files}
    result.update(collections=delivered,collection_readback_verified=True,aggregate_export_bytes=total,complete_science_members=len(packed['all_work_members']))


def run(path):
    """Hold for boot/process/STOP release, audit serially, collect and exit once."""
    c=json.loads(Path(path).read_text());validate_config(c);root=Path(c['root']);task=Path(c['task_filesystem']);p=json.loads(Path(c['plan']).read_text());__import__('e036_control').read_plan(c['plan'],held=True)
    sup=supervisor();env=sup.isolated_env(4);env.update(NUMBA_NUM_THREADS='4',NUMBA_CACHE_DIR=str(task/'numba-cache'),TMPDIR=str(task/'tmp'),
        E034_HASH_CONFIG=str(root/'tmp/hash-cli-config'),E036_RELEASE_FILE=str(root/'release.json'))
    publish(dict(pid=os.getpid(),identity=identity(os.getpid()),epoch=time.time()),root/'started.json')
    result=dict(status='FAILED',science_completed=False,taxonomy_acquired=False,stages=[],source=c['source_commit'],root=str(root));disk=None
    def command(label,argv,reserve=1800):
        """Capture the scientific worker's actual exit within the common clock."""
        remaining=c['review_deadline_epoch']-time.time()-reserve
        if remaining<10:raise TimeoutError('Original audit clock exhausted')
        status(c,dict(status='RUNNING',stage=label))
        r=sup.supervise(list(map(str,argv)),root/'logs'/(label+'.log'),remaining,26_000_000_000,env,sample_root=os.getpid())
        result['stages'].append(dict(stage=label,resources=r));return r
    def python(args):return [c['python'],'-I','-B',*args]
    try:
        while not(root/'release.json').exists():
            if time.time()>=c['setup_deadline_epoch']:raise TimeoutError('Held setup deadline exhausted')
            time.sleep(.2)
        release=json.loads((root/'release.json').read_text());watch=json.loads((root/'logs/watchdog-live-before-release.json').read_text())
        if release['config']!=binding(path)or release['plan']!=binding(c['plan'])or not release['watchdog_verified']or not release['provider_STOP_verified']or watch['decision']!='workflow alive':raise ValueError('Fresh supervised release differs')
        freeze_sources()
        if subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()!=c['source_commit']or subprocess.check_output(['git','status','--porcelain'],cwd=ROOT,text=True).strip():raise ValueError('Exact clean source required')
        disk=DiskHistory(c);disk.start();(task/'tmp').mkdir()
        command('owned-package-install',[str(Path(c['base'])/'bin/python'),'-I','-B',ROOT/'scripts/e033_install.py','--base',c['base'],'--destination',str(Path(c['python']).parent.parent),'--wheel',c['wheel'],'--pysam-wheel',c['pysam_wheel'],'--lock',EXP/'candidate-lock.json','--output',root/'gates/install.json'])
        command('complete-native-runtime',python([ROOT/'scripts/e035_pool_runtime.py','--base',c['base'],'--reference',c['reference'],'--candidate-lock',EXP/'candidate-lock.json','--pysam-wheel',c['pysam_wheel'],'--output',root/'gates/runtime.json']))
        from e036_control import UNITS
        command('original-inputs-before',python([ROOT/'scripts/e036_native.py','--plan',c['plan'],'--action','inputs','--output',root/'gates/inputs-before.json']))
        command('actual-native-tiny',python([ROOT/'scripts/e036_tiny.py','--root',task/'tiny','--workflow-python',c['workflow_python']]))
        for kind in ['pooled','baseline','bootstrap','measurements']:
            command('restore-'+kind,python([ROOT/'scripts/e036_restore.py','--kind',kind,'--output',task/('original-'+kind)]))
        command('full-native-admission',python([ROOT/'scripts/e036_native.py','--plan',c['plan'],'--action','probe']))
        command('serial-three-mode-optional-graph',python([ROOT/'scripts/e036_control.py','--plan',c['plan'],'--workflow']))
        command('native-result-contracts',python([ROOT/'scripts/e036_native.py','--plan',c['plan'],'--action','final']))
        result.update(status='SUCCESS',science_completed=True)

    except BaseException as error:
        result.update(status='FAILED',error=repr(error),traceback=traceback.format_exc());print(result['traceback'],flush=True)
        known={v['stage']for v in result['stages']}
        for f in (root/'logs').glob('*.exit.json'):
            name=f.name.removesuffix('.exit.json')
            if name not in known:result['stages'].append(dict(stage=name,resources=json.loads(f.read_text())))
    try:
        if (root/'gates/inputs-before.json').exists():
            command('original-inputs-after',python([ROOT/'scripts/e036_native.py','--plan',c['plan'],'--action','inputs','--output',root/'gates/inputs-after.json']),reserve=900)
            if json.loads((root/'gates/inputs-before.json').read_text())!=json.loads((root/'gates/inputs-after.json').read_text()):raise ValueError('Original feature bytes/axes changed')
    except BaseException as error:result.update(status='FAILED',after_error=repr(error),after_traceback=traceback.format_exc())
    try:
        if (task/'science').exists():
            for kind in ['pooled','baseline','bootstrap','measurements']:
                if (task/('original-'+kind)/'stream-admission.json').exists():command('verify-reused-'+kind,python([ROOT/'scripts/e036_restore.py','--kind',kind,'--output',task/('original-'+kind)]),reserve=600)
        collect(c,result)
        if disk is not None:
            result['filesystem']=disk.close();result['filesystem_delivery']=storage_upload(root/'logs/filesystem.jsonl',c['archive_prefix']+'filesystem.jsonl')
            if result['filesystem']['monitor_error']is not None:result['status']='FAILED'
        result['finished_epoch']=time.time();publish(result,root/'completion.json');delivered=storage_upload(root/'completion.json',c['archive_prefix']+'completion.json')
        tail=dict(status='PASS',completion=delivered,science_completed=result['science_completed'],epoch=time.time())
        publish(tail,root/'closed-delivery-tail.json');storage_upload(root/'closed-delivery-tail.json',c['archive_prefix']+'closed-delivery-tail.json')
        status(c,dict(status=result['status'],science_completed=result['science_completed'],completion_delivery_verified=True));return 0 if result['status']!='FAILED'else 1
    except BaseException as error:
        detail=traceback.format_exc();print('E036_FINAL_DELIVERY_FAILED',repr(error),detail,flush=True)
        failed=dict(status='FAILED_FINAL_DELIVERY',science_completed=result['science_completed'],error=repr(error),traceback=detail,
            root=str(root),source=c['source_commit'],science_replayed=False,evidence_retained_on_disk=True,finished_epoch=time.time())
        target=root/('completion-failure-'+str(time.time_ns())+'.json');publish(failed,target)
        try:storage_upload(target,c['archive_prefix']+target.name)
        except Exception as upload_error:print('E036_FAILURE_RECEIPT_UPLOAD_FAILED',repr(upload_error),flush=True)
        status(c,dict(status='FAILED_FINAL_DELIVERY',error=repr(error)));return 1


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--config',type=Path,required=True);raise SystemExit(run(parser.parse_args().config))
