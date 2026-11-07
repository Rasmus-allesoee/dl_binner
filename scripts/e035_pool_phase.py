#!/usr/bin/env python3
"""Held all-ten E035 support audit with independent shutdown and bounded delivery.

No binner, taxonomy classifier, mapping or truth path is exposed. All twenty
readers close before their community's frozen pooled utility decision. Every
operation shares the VM-start clock, including setup and evidence collection.
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
from e009_owner import supervisor
from e009_exit_watchdog import identity
from e033_phase import validate_config as common_configuration
from e033_recovery import DiskHistory
from e021_portable_node import storage_upload
EXP=ROOT/'experiments/E035-confidence-taxonomy'


def freeze_sources():
    """Require the unchanged prepared science plus new operational source lock."""
    for name in ['source-lock.json','pooled-native-launch-lock.json']:
        for n,b in json.loads((EXP/name).read_text())['files'].items():
            if binding(ROOT/n)!=b:raise ValueError('Frozen E035 science/operation differs: '+n)


def validate_plan(p):
    """Validate actual host-produced fields without importing numerical libraries."""
    frozen=json.loads((EXP/'pooled-audit-plan.json').read_text())
    if set(p)!=set(frozen)or any(p[k]!=frozen[k]for k in ['kind','engineering','features','limits']):
        raise ValueError('Unknown or altered audit scientific/envelope schema')
    if set(p['BAMs'])!=set(frozen['BAMs']):raise ValueError('Both original communities required')
    for c in frozen['BAMs']:
        if len(p['BAMs'][c])!=10:raise ValueError('All ten ordered samples required')
        for actual,wanted in zip(p['BAMs'][c],frozen['BAMs'][c]):
            if set(actual)!=set(wanted)or {k:v for k,v in actual.items()if k!='local'}!={k:v for k,v in wanted.items()if k!='local'}:
                raise ValueError('Original ordered BAM generation/bytes differ')
    return True


def validate_config(c,now=None):
    """Require the full tested producer schema, current credits and fixed audit scope."""
    common_configuration(c,now)
    native=json.loads((EXP/'pooled-native-plan.json').read_text())
    if (not c['root'].startswith('/srv/dl_binner/experiments/e035/pooled-')or not c['service_name'].startswith('e035-pooled-')
            or c['limits']!=native['limits']or c['financial']['ceiling_USD']!=4):
        raise ValueError('Pooled-only phase/resource/credit scope differs')
    return True


def status(c,value):
    """Publish a compact progress pointer, separately from actual stage exits."""
    q=urllib.request.Request('http://metadata.google.internal/computeMetadata/v1/instance/guest-attributes/e035-pooled/status',
        data=json.dumps(dict(value,root=c['root'],source=c['source_commit'],epoch=time.time())).encode(),method='PUT',headers={'Metadata-Flavor':'Google','Content-Type':'application/json'})
    try:
        with urllib.request.urlopen(q,timeout=3)as f:f.read(1024)
    except Exception as e:print('E035_POOL_STATUS_UNAVAILABLE',repr(e),flush=True)


def evidence(root):
    """Snapshot closed logs and all locked sources; exclude histories/auth caches."""
    from e034_phase import evidence as snapshot
    root=Path(root);out=snapshot(root);c=json.loads((root/'config.json').read_text());repo=Path(c['repo'])
    source=out/'source-repository';source.mkdir();names={}
    for label in ['source-lock.json','pooled-native-launch-lock.json']:
        lock=repo/'experiments/E035-confidence-taxonomy'/label
        names[str(lock.relative_to(repo))]=binding(lock)
        names.update(json.loads(lock.read_text())['files'])
    for name,wanted in names.items():
        p=repo/name
        if binding(p)!=wanted:raise ValueError('Source changed before collection: '+name)
        target=source/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,target)
    packet=repo.parent/'experiments/e035/source-transports'/('source-'+c['source_commit']+'.bundle')
    if binding(packet)!=c['financial']['source_transport']['bundle']:raise ValueError('Native exact source bundle differs')
    shutil.copyfile(packet,out/'source.bundle')
    for p in (root/'payload').glob('*.whl'):shutil.copyfile(p,out/p.name)
    return out


def schedule(samples,remaining):
    """Admit all remaining readers from actual first-library work, never utility."""
    if set(samples)!={'E009','oral'}or any(v['status']!='PASS'for v in samples.values()):raise ValueError('Both first-reader measurements required')
    forecast=sum(v['wall_seconds']*9*1.5 for v in samples.values())+1800
    rss=4*1024**3+max(v['observations']for v in samples.values())*10*2*512
    if forecast>remaining or rss>26_000_000_000:raise ValueError('Measured complete remainder/RSS refused; preserve both ledgers')
    return dict(status='PASS_COMPLETE_REMAINDER',forecast_seconds=forecast,remaining_seconds=remaining,forecast_pool_RSS_bytes=rss,
        formula='Nine remaining complete reader/restore times per community times 1.5, plus 30 minutes pooling/collection/shutdown; no biological utility stop',utility_used=False)


def collect(c,result):
    """Deliver every support ledger/pool member/alias and bound closed worker logs."""
    from e035_collect import pack,verify
    root=Path(c['root']);task=Path(c['task_filesystem']);source=Path(c['plan']).parent/'task/support';source.mkdir(parents=True,exist_ok=True)
    work=task/'support-return';work.mkdir()
    scratch={}
    for p in source.rglob('*'):
        if p.is_symlink():raise ValueError('Scientific support symlink refused')
        if not p.is_file():continue
        n=str(p.relative_to(source))
        if p.name.startswith('collate.')and p.suffix=='.bam':
            scratch[n]=dict(binding(p),reason='Regenerable failed QNAME collator temporary; original source generation remains; retained on task disk')
        else:
            target=work/n;target.parent.mkdir(parents=True,exist_ok=True);os.link(p,target)
    write(work/'excluded-collator-temporaries.json',scratch)
    # Restoration journals are unique evidence; only completed source copies
    # and incomplete recoverable originals remain on disk outside this payload.
    restore_return=work/'restore-evidence';restore_return.mkdir()
    omitted={}
    for p in (task/'restores').rglob('*'):
        if p.is_file():
            n=str(p.relative_to(task/'restores'))
            if p.name in ['source.bam','source.part']:omitted[n]=dict(bytes=p.stat().st_size,reason='Retained disposable original/partial BAM; exact immutable source generation remains; no unique science silently omitted')
            elif 'hash-cli-config'not in p.parts:
                target=restore_return/n;target.parent.mkdir(parents=True,exist_ok=True);os.link(p,target)
    write(restore_return/'excluded-original-copies.json',omitted)
    returned=task/'return';packed=pack(work,evidence(root),returned);verify(returned)
    files=[f for f in sorted(returned.rglob('*'))if f.is_file()and not any(n.startswith('stage-')for n in f.relative_to(returned).parts)]
    total=sum(f.stat().st_size for f in files);delivered={}
    if total+2*1024**2>c['limits']['compressed_export_bytes']:raise ValueError('Complete return/tail cap exceeded before any upload; no omission fallback')
    for file in files:
        relative=str(file.relative_to(returned))
        delivered[relative]=storage_upload(file,c['archive_prefix']+'support/'+relative)
    result.update(collections=delivered,collection_readback_verified=True,aggregate_export_bytes=total,
        complete_support_members=len(packed['all_work_members']))


def run(path):
    """Hold for boot/process/STOP release, audit serially, collect and exit once."""
    c=json.loads(Path(path).read_text());validate_config(c);root=Path(c['root']);task=Path(c['task_filesystem']);p=json.loads(Path(c['plan']).read_text());validate_plan(p)
    sup=supervisor();env=sup.isolated_env(4);env.update(NUMBA_NUM_THREADS='4',NUMBA_CACHE_DIR=str(task/'numba-cache'),TMPDIR=str(task/'tmp'),
        E034_HASH_CONFIG=str(root/'tmp/hash-cli-config'),E035_SUPPORT_RELEASE_FILE=str(root/'release.json'))
    publish(dict(pid=os.getpid(),identity=identity(os.getpid()),epoch=time.time()),root/'started.json')
    result=dict(status='FAILED',audit_completed=False,community_models_fit=False,taxonomy_acquired=False,stages=[],source=c['source_commit'],root=str(root));disk=None
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
        command('owned-package-install',[str(Path(c['base'])/'bin/python'),'-I','-B',ROOT/'scripts/e033_install.py','--base',c['base'],'--destination',str(Path(c['python']).parent.parent),'--wheel',c['wheel'],'--pysam-wheel',c['pysam_wheel'],'--lock',EXP/'pooled-native-package-lock.json','--output',root/'gates/install.json'])
        command('complete-native-runtime',python([ROOT/'scripts/e035_pool_runtime.py','--base',c['base'],'--reference',c['reference'],'--candidate-lock',EXP/'pooled-native-package-lock.json','--pysam-wheel',c['pysam_wheel'],'--output',root/'gates/runtime.json']))
        worker=ROOT/'scripts/e035_pool_native.py'
        command('original-inputs-before',python([worker,'--plan',c['plan'],'--action','inputs','--output',root/'gates/inputs-before.json']))
        command('actual-native-tiny',python([worker,'--action','tiny','--output',root/'gates/tiny.json']))
        samples={}
        for community in ['E009','oral']:
            command('sample-'+community+'-00',python([worker,'--plan',c['plan'],'--action','sample','--community',community,'--index','0']))
            samples[community]=json.loads((Path(p['work'])/community/'sample-00-transport.json').read_text())
        write(root/'gates/complete-remainder.json',schedule(samples,c['review_deadline_epoch']-time.time()))
        for community in ['E009','oral']:
            for index in range(1,10):
                command('sample-'+community+'-%02d'%index,python([worker,'--plan',c['plan'],'--action','sample','--community',community,'--index',index]))
            command('pool-'+community,python([worker,'--plan',c['plan'],'--action','pool','--community',community]))
        result.update(status='SUCCESS_INFORMATION_AUDIT',audit_completed=True,information={c:json.loads((Path(p['work'])/c/'information-result.json').read_text())for c in ['E009','oral']})
    except BaseException as error:
        result.update(status='FAILED',error=repr(error),traceback=traceback.format_exc());print(result['traceback'],flush=True)
        known={v['stage']for v in result['stages']}
        for f in (root/'logs').glob('*.exit.json'):
            name=f.name.removesuffix('.exit.json')
            if name not in known:result['stages'].append(dict(stage=name,resources=json.loads(f.read_text())))
    try:
        if (root/'gates/inputs-before.json').exists():
            command('original-inputs-after',python([ROOT/'scripts/e035_pool_native.py','--plan',c['plan'],'--action','inputs','--output',root/'gates/inputs-after.json']),reserve=900)
            if json.loads((root/'gates/inputs-before.json').read_text())!=json.loads((root/'gates/inputs-after.json').read_text()):raise ValueError('Original feature bytes/axes changed')
    except BaseException as error:result.update(status='FAILED',after_error=repr(error),after_traceback=traceback.format_exc())
    try:
        collect(c,result)
        if disk is not None:
            result['filesystem']=disk.close();result['filesystem_delivery']=storage_upload(root/'logs/filesystem.jsonl',c['archive_prefix']+'filesystem.jsonl')
            if result['filesystem']['monitor_error']is not None:result['status']='FAILED'
        result['finished_epoch']=time.time();publish(result,root/'completion.json');delivered=storage_upload(root/'completion.json',c['archive_prefix']+'completion.json')
        tail=dict(status='PASS',completion=delivered,audit_completed=result['audit_completed'],epoch=time.time())
        publish(tail,root/'closed-delivery-tail.json');storage_upload(root/'closed-delivery-tail.json',c['archive_prefix']+'closed-delivery-tail.json')
        status(c,dict(status=result['status'],audit_completed=result['audit_completed'],completion_delivery_verified=True));return 0 if result['status']!='FAILED'else 1
    except BaseException as error:
        detail=traceback.format_exc();print('E035_POOL_FINAL_DELIVERY_FAILED',repr(error),detail,flush=True)
        failed=dict(status='FAILED_FINAL_DELIVERY',audit_completed=result['audit_completed'],error=repr(error),traceback=detail,
            root=str(root),source=c['source_commit'],science_replayed=False,evidence_retained_on_disk=True,finished_epoch=time.time())
        target=root/('completion-failure-'+str(time.time_ns())+'.json');publish(failed,target)
        try:storage_upload(target,c['archive_prefix']+target.name)
        except Exception as upload_error:print('E035_POOL_FAILURE_RECEIPT_UPLOAD_FAILED',repr(upload_error),flush=True)
        status(c,dict(status='FAILED_FINAL_DELIVERY',error=repr(error)));return 1


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--config',type=Path,required=True);raise SystemExit(run(parser.parse_args().config))
