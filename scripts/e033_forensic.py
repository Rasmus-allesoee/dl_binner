#!/usr/bin/env python3
"""Collect the failed E033 worker and terminal journals without running science.

This held native parent uses the existing stopped task filesystem read-only. It
copies only closed root/workflow logs and small barrier/initial-state receipts to
a fresh source-disk directory, makes a bounded verified archive, uploads/readbacks
it, and exits under the current-boot watcher. No model, BAM reader or science DAG
is called. The original phase and source are immutable inputs.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import sys
import time
import traceback

RETENTION = 1794351600
FIELDS = {'root','repo','original','source_commit','operations_source','old_config',
          'old_boot','old_service','disk_name','disk_id','vm_start_epoch',
          'common_clock_start_epoch','common_deadline_epoch','provider_deadline_epoch',
          'archive_prefix','service_name','user','financial','helpers','task_device',
          'source_initial_used_bytes'}


def binding(path):
    """Hash one regular artifact in bounded blocks."""
    path = Path(path)
    if path.is_symlink() or not path.is_file():
        raise ValueError('Regular artifact required: ' + str(path))
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(1024**2), b''):
            h.update(block)
    return dict(bytes=path.stat().st_size, sha256=h.hexdigest())


def write_metadata(path, value):
    """Finish exclusive setup JSON before its consumer starts."""
    with Path(path).open('x') as f:
        json.dump(value, f, indent=2, allow_nan=False)
        f.write('\n')
        f.flush()
        os.fsync(f.fileno())


def validate_config(c, now=None):
    """Require the complete forensic-only schema, fresh coverage and bounded clock."""
    now = time.time() if now is None else now
    if set(c) != FIELDS:
        raise ValueError('Incomplete/unknown forensic configuration')
    f = c['financial']
    if (not c['service_name'].startswith('e033-forensic-')
        or not all(x.isalnum() or x == '-' for x in c['service_name'])
        or not Path(c['root']).is_relative_to('/srv/dl_binner/experiments/e033')
        or c['root'] == c['original'] or c['repo'] != '/srv/dl_binner/repo'
        or not c['original'].endswith('/multiscale-20261104T152005Z-a940769-r2')
        or c['source_commit'] != '5911e2587d5c8353937fb71260464a038a1f46de'
        or len(c['operations_source']) != 40
        or c['disk_name'] != 'e033-task-1793805630' or c['disk_id'] != '1578633013833953331'
        or not c['vm_start_epoch'] <= now < c['vm_start_epoch'] + 1800
        or not c['common_clock_start_epoch'] <= c['vm_start_epoch']
        or c['common_deadline_epoch'] != c['common_clock_start_epoch'] + 30*3600
        or c['provider_deadline_epoch'] != c['vm_start_epoch'] + 2700
        or c['provider_deadline_epoch'] > c['common_deadline_epoch'] + 900
        or c['common_clock_start_epoch'] + 30.25*3600 >= RETENTION
        or f['coverage_status'] != 'PASS_FOR_SPECIFIED_ORDINARY_FIRST_PARTY_PRODUCTS_ONLY'
        or f['real_money_authorized'] is not False
        or not 0 <= now-f['checked_epoch'] < 7200
        or not 0 <= now-f['credit_checked_epoch'] < 7200
        or not 0 < f['estimated_complete_gross_USD'] <= f['ceiling_USD'] == 20
        or f['collection_ceiling_USD'] != .25
        or c['common_clock_start_epoch'] + 30.25*3600 >= min(f['storage_valid_until_epoch'],f['credit_valid_until_epoch'])):
        raise ValueError('Forensic source/resource/credit/clock contract differs')
    return True


def guard(c):
    """Protect both filesystems and the 256 MiB new forensic working allowance."""
    root = Path(c['root']); task = Path(c['original'])/'task'
    source = shutil.disk_usage(root); current = shutil.disk_usage(task)
    if (os.stat(task).st_dev != c['task_device'] or os.stat(task).st_dev == os.stat(root).st_dev
        or min(source.free,current.free) < 25*1024**3
        or source.used-c['source_initial_used_bytes'] > 256*1024**2):
        raise ValueError('Forensic source/task reserve, device or working cap differs')
    opts = subprocess.check_output(['findmnt','-n','-o','OPTIONS','--target',str(task)],text=True).strip().split(',')
    if 'ro' not in opts:
        raise ValueError('Original task filesystem must be read-only during collection')


def collect(c, engineering=False):
    """Copy closed whitelist records, with before/after bytes and exact omissions.

    Engineering fixtures exercise the same directory selection/copy/cap path;
    only native journalctl and mount/credit prerequisites are outside that fixture.
    """
    root = Path(c['root']); original = Path(c['original'])
    work = root/'closed'; work.mkdir(exist_ok=False)
    source_files = []
    for name in ['terminal.log','completion.json','closed-delivery-tail.json','science-result.json',
                 'config.json','host.json','release.json','started.json','science-plan.json']:
        p = original/name
        if p.exists(): source_files.append((p,Path('root')/name))
    for directory,prefix in [('logs','root/logs'),('task/work/logs','workflow/logs'),
                             ('task/work/benchmarks','workflow/benchmarks'),
                             ('task/work/barrier','workflow/barrier'),
                             ('task/work/.snakemake/log','workflow/scheduler')]:
        at = original/directory
        if at.exists():
            if at.is_symlink(): raise ValueError('Closed journal directory symlink refused')
            source_files.extend((p,Path(prefix)/p.relative_to(at)) for p in sorted(at.rglob('*')) if p.is_file())
    for directory in ['task/work/E009-noGLM/teacher','task/work/E009-GLM','task/work/oral-noGLM']:
        at = original/directory
        if at.exists():
            source_files.extend((p,Path('partial')/p.relative_to(original/'task/work'))
                                for p in sorted(at.rglob('*')) if p.is_file() and p.suffix == '.json')
    required = {'root/terminal.log','root/science-result.json','root/config.json',
                'workflow/logs/E009_noGLM_teacher.log'}
    present = {str(n) for p,n in source_files}
    if not required <= present:
        raise ValueError('Required actual native failure journal missing: '+str(sorted(required-present)))
    if sum(p.stat().st_size for p,n in source_files) > 90*1024**2:
        raise ValueError('Closed journal whitelist exceeds logical forensic cap')
    copied = {}
    for p,name in source_files:
        if p.is_symlink(): raise ValueError('Closed evidence symlink refused')
        before = binding(p); target = work/name; target.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(p,target)
        if before != binding(target) or before != binding(p):
            raise ValueError('Closed original journal changed during copy')
        copied[str(name)] = before
        if not engineering: guard(c)
    journal = dict(native=not engineering)
    if not engineering:
        argv = ['sudo','-n','journalctl','--boot='+c['old_boot'],'--unit='+c['old_service']+'.service',
                '--no-pager','--lines=2000']
        p = subprocess.run(argv,capture_output=True,timeout=45)
        (work/'original-systemd.log').write_bytes(p.stdout+p.stderr)
        if len(p.stdout)+len(p.stderr)>4*1024**2:
            raise ValueError('Systemd forensic output exceeds cap')
        journal.update(argv=argv,exit_code=p.returncode,binding=binding(work/'original-systemd.log'))
    value = dict(status='PASS_CLOSED_FORENSIC_COPY',copied=copied,journal=journal,
                 original_completion_present=(original/'completion.json').exists(),
                 original_closed_tail_present=(original/'closed-delivery-tail.json').exists(),
                 science_executed=False,original_files_unchanged=True)
    (work/'copy-proof.json').write_text(json.dumps(value,indent=2)+'\n')
    return value


def run(path):
    """Hold until current watcher/provider release, collect, upload/read back and exit."""
    path = Path(path); c = json.loads(path.read_text()); validate_config(c)
    root = Path(c['root']); repo = Path(c['repo']); sys.path.insert(0,str(repo/'scripts'))
    from e021_control_json import publish
    from e009_exit_watchdog import identity
    from e009_owner import supervisor
    from e021_portable_node import storage_upload
    from e033_collect import pack
    import e033_collect
    if sys.platform != 'linux': raise ValueError('Native forensic parent required')
    deadline = c['vm_start_epoch']+1800
    signal.signal(signal.SIGALRM,lambda *_: (_ for _ in ()).throw(TimeoutError('Forensic clock exhausted')))
    signal.setitimer(signal.ITIMER_REAL,max(.001,deadline-time.time()))
    publish(dict(pid=os.getpid(),identity=identity(os.getpid()),epoch=time.time()),root/'started.json')
    result = dict(status='FAILED',science_executed=False,stages=[],source=c['source_commit'],operations_source=c['operations_source'])
    try:
        while not (root/'release.json').exists():
            if time.time()>=c['vm_start_epoch']+600: raise TimeoutError('Forensic held setup exhausted')
            time.sleep(.2)
        release = json.loads((root/'release.json').read_text())
        live = json.loads((root/'logs/watchdog-live-before-release.json').read_text())
        if (release['config'] != binding(path) or release['provider_STOP_seconds'] != 2700
            or release['watchdog_verified'] is not True or release['forensics_only'] is not True
            or live['boot_id'] != Path('/proc/sys/kernel/random/boot_id').read_text().strip()
            or live['expected_process'] != identity(os.getpid()) or live['decision'] != 'workflow alive'):
            raise ValueError('Current held-parent/watch/provider release differs')
        if binding(Path(c['original'])/'config.json') != c['old_config']:
            raise ValueError('Original failure config differs')
        if subprocess.check_output(['git','rev-parse','HEAD'],cwd=repo,text=True).strip()!=c['source_commit']:
            raise ValueError('Original read-only scientific checkout differs')
        if subprocess.check_output(['git','status','--porcelain'],cwd=repo,text=True).strip():
            raise ValueError('Original read-only checkout is not clean')
        lock=json.loads((repo/'experiments/E033-multiscale-bam/source-lock.json').read_text())
        for name,wanted in lock['files'].items():
            if binding(repo/name)!=wanted: raise ValueError('Original helper/source byte drift')
        for n,b in c['helpers'].items():
            if binding(root/'helpers'/n)!=b: raise ValueError('Forensic helper bytes differ')
        guard(c)
        sup = supervisor(); env = sup.isolated_env(4)
        r = sup.supervise([sys.executable,'-I','-B',str(Path(__file__).absolute()),'--config',str(path),'--collect'],
                          root/'logs/closed-copy.log',deadline-time.time()-180,8_000_000_000,env,sample_root=os.getpid())
        result['stages'].append(dict(stage='closed-copy',resources=r))
        e033_collect.CAP=128*1024**2; e033_collect.LOGICAL=96*1024**2
        evidence=root/'evidence';evidence.mkdir()
        for name in ['config.json','host.json','started.json','release.json']:
            shutil.copyfile(root/name,evidence/name)
        for p in (root/'helpers').iterdir():shutil.copyfile(p,evidence/p.name)
        proof=pack(root/'closed',evidence,root/'return');result['collection']=proof
        if proof['archive']['bytes']>128*1024**2:raise ValueError('Forensic compressed cap exceeded')
        guard(c);delivered={}
        for name in ['e033-evidence.tar.gz','inventory.json','collection.json','e033-evidence.tar.gz.sha256']:
            print('E033_FORENSIC_DELIVERY',name,flush=True)
            delivered[name]=storage_upload(root/'return'/name,c['archive_prefix']+'/'+name)
        result.update(status='SUCCESS',private_readback_verified=True,delivered=delivered)
    except BaseException as error:
        result.update(error=repr(error),traceback=traceback.format_exc())
        print(result['traceback'],flush=True)
    result['finished_epoch']=time.time()
    publish(result,root/'completion.json')
    try:
        delivery=storage_upload(root/'completion.json',c['archive_prefix']+'/completion.json')
        tail=dict(status='PASS',completion=delivery,collection=result.get('delivered',{}),science_executed=False)
        publish(tail,root/'closed-delivery-tail.json')
        storage_upload(root/'closed-delivery-tail.json',c['archive_prefix']+'/closed-delivery-tail.json')
    except BaseException as error:
        print('FORENSIC_FINAL_DELIVERY_FAILED',repr(error),flush=True)
        return 1
    print('E033_FORENSIC_EXIT',result['status'],flush=True)
    return 0 if result['status']=='SUCCESS' else 1


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config',required=True,type=Path);parser.add_argument('--collect',action='store_true')
    a=parser.parse_args()
    if a.collect:
        c=json.loads(a.config.read_text());validate_config(c);collect(c)
    else:
        raise SystemExit(run(a.config))
