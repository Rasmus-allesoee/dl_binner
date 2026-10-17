#!/usr/bin/env python3
"""Hold and execute one admitted E014 comparison under a VM-start deadline.

This prepared Linux driver never starts a VM or changes resources. A controller
must bind current credits, source/data/truth/native gates, current-boot held-parent
watchdog and provider STOP before release. Setup and collection share the clock.
Missing gates fail closed; failures remain journals and are never retried here.
"""
import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tarfile
import time

sys.path.insert(0,str(Path(__file__).absolute().parent))
from e009_common import binding,write_json
from e009_controls import PhaseGuard
from e009_owner import supervisor,Tee

SECONDS=12*3600
STOP_SECONDS=12*3600+900


def admission(cfg, release, now):
    """Refuse incomplete/expired funding, truth, source, supervision or retention."""
    if not 0<=now-cfg['vm_start_epoch']<SECONDS-600:
        raise TimeoutError('Original E014 VM-start clock unavailable')
    required=['credit_gate_passed','pending_usage_accounted','oral_truth_admitted',
        'native_runtime_gates_passed','full_input_axes_verified','watchdog_release_verified',
        'no_resource_change','source_and_wheel_verified']
    if any(release.get(k) is not True for k in required):
        raise ValueError('E014 release gate incomplete')
    if release.get('provider_stop_seconds')!=STOP_SECONDS or release.get('incremental_gross_ceiling_usd')!=10:
        raise ValueError('E014 clock/cost envelope differs')
    if release.get('storage_retention_extended') is not False:
        raise ValueError('Storage retention extension refused')
    if set(release.get('covered_costs',[]))!={'compute','disk','storage','network','operations'}:
        raise ValueError('Complete product credit coverage missing')
    if cfg['vm_start_epoch']+STOP_SECONDS>=min(release['credit_valid_until_epoch'],release['storage_valid_until_epoch']):
        raise ValueError('Credit/storage approval expires before STOP')
    if release['phase_config']!=binding(cfg['_path']):
        raise ValueError('Release/config bytes differ')
    if release['estimated_incremental_gross_usd']>10:
        raise ValueError('Complete run exceeds the authorized gross ceiling')
    if [step['name'] for step in cfg['stages']] != ['comparison']:
        raise ValueError('The sole released stage must be the complete serial comparison DAG')


def collect(root, output, ceiling=2*1024**3):
    """Seal compact scientific evidence; retain bulk DNA/banks on the existing disk.

    Inventory binds every regular result, including non-exported FASTA/features.
    The return holds closed logs, receipts, partitions and embeddings, not complete
    duplicate bin FASTAs or crop banks. Links are refused, not followed.
    """
    root,output=Path(root),Path(output)
    files={};retained=[]
    for p in sorted(root.rglob('*')):
        if p.is_symlink():raise ValueError('Scientific result link refused')
        if not p.is_file():continue
        key=str(p.relative_to(root));files[key]=binding(p)
        if p.suffix in ['.json','.log','.tsv','.jsonl'] or p.name in ['embeddings.npz','genes.tsv','calls.tsv','domains.tsv']:
            retained.append(p)
    inventory=output.with_suffix('.inventory.json')
    write_json(inventory,dict(all_result_members=files,retained=[str(p.relative_to(root))for p in retained],
                             omitted_bulk='Full DNA, view banks and parent features retained on work disk; inventory byte-bound.'))
    with tarfile.open(output,'x:gz')as archive:
        archive.add(inventory,arcname='inventory.json',recursive=False)
        for p in retained:
            archive.add(p,arcname='run/'+str(p.relative_to(root)),recursive=False)
            if output.stat().st_size>ceiling:raise ValueError('Compact export cap exceeded')
    if output.stat().st_size>ceiling:raise ValueError('Compact export cap exceeded')
    with tarfile.open(output,'r:gz')as archive:
        for member in archive:
            if member.name=='inventory.json':continue
            import hashlib
            stream=archive.extractfile(member);sha=hashlib.sha256();size=0
            for block in iter(lambda:stream.read(1024**2),b''):sha.update(block);size+=len(block)
            expected=files[member.name.removeprefix('run/')]
            if dict(bytes=size,sha256=sha.hexdigest())!=expected:raise ValueError('Collected member bytes differ')
    result=dict(path=str(output),**binding(output),retained_members=len(retained),all_members=len(files))
    output.with_suffix(output.suffix+'.sha256').write_text(result['sha256']+'  '+output.name+'\n')
    return result


def run(path):
    """Wait while guarded, verify native release identity, execute the serial DAG once."""
    cfg=json.loads(Path(path).read_text());cfg['_path']=str(path)
    phase=Path(cfg['phase_root']);logs=phase/'logs';logs.mkdir(exist_ok=True)
    write_json(phase/'started.json',dict(pid=os.getpid(),config=binding(path),epoch=time.time()))
    remaining=SECONDS-(time.time()-cfg['vm_start_epoch'])
    if remaining<600:raise TimeoutError('No original clock remains')
    deadline=time.monotonic()+remaining;sup=supervisor();env=sup.isolated_env(4)
    initial_growth=max(0,shutil.disk_usage(phase).used-cfg['initial_filesystem_used_bytes'])
    cap=45*1024**3
    if initial_growth>=cap:raise ValueError('Preparation exhausted the frozen space envelope')
    outcome=dict(status='FAILED',source_commit=cfg['source_commit'],stages=[],community_completed=False)
    guard=None
    try:
        with PhaseGuard(phase,remaining,growth_bytes=cap-initial_growth)as guard:
            print('E014_HELD_FOR_CURRENT_BOOT_WATCHDOG',os.getpid(),flush=True)
            while not Path(cfg['release_file']).exists():time.sleep(.2)
            release=json.loads(Path(cfg['release_file']).read_text());admission(cfg,release,time.time())
            from e009_exit_watchdog import identity
            watched=json.loads((logs/'watchdog-live-before-release.json').read_text())
            if (watched['decision']!='workflow alive' or watched['expected_process']!=identity(os.getpid())
                    or watched['boot_id']!=Path('/proc/sys/kernel/random/boot_id').read_text().strip()):
                raise ValueError('Current boot/held-parent watchdog differs')
            if subprocess.check_output(['git','rev-parse','HEAD'],cwd=cfg['repo'],text=True).strip()!=cfg['source_commit']:
                raise ValueError('Exact clean source commit missing')
            if subprocess.check_output(['git','status','--porcelain'],cwd=cfg['repo'],text=True).strip():
                raise ValueError('VM source checkout is dirty')
            if os.cpu_count()!=8 or not os.path.ismount('/srv/dl_binner'):
                raise ValueError('Existing VM/allocation/mount contract differs')
            for item in cfg['bindings']:
                if binding(item['path'])!=item['binding']:raise ValueError('Bound input/runtime bytes differ')
            for step in cfg['stages']:
                left=deadline-time.monotonic()-600
                if left<=0:raise TimeoutError('Original setup/fit/collection clock exhausted')
                print('E014_STAGE_START',step['name'],flush=True)
                receipt=sup.supervise(step['argv'],logs/(step['name']+'.log'),left,26_000_000_000,env,sample_root=os.getpid())
                outcome['stages'].append(dict(name=step['name'],resources=receipt))
            outcome.update(status='SUCCESS',community_completed=True)
    except BaseException as exc:outcome.update(error=f'{type(exc).__name__}: {exc}')
    outcome['disk_observations']=guard.observations if guard else []
    outcome['elapsed_since_VM_start_seconds']=time.time()-cfg['vm_start_epoch']
    (phase/'work').mkdir(exist_ok=True)
    write_json(phase/'work/phase-result.json',outcome)
    try:
        growth=max(0,shutil.disk_usage(phase).used-cfg['initial_filesystem_used_bytes'])
        with PhaseGuard(phase,deadline-time.monotonic(),growth_bytes=cap-growth)as collection_guard:
            left=deadline-time.monotonic()
            if left<30:raise TimeoutError('No clock for evidence collection')
            copied=phase/'work/phase-evidence';copied.mkdir()
            for p in logs.iterdir():
                if p.is_file():
                    target=copied/('terminal.snapshot.log' if p.name=='parent-terminal.log' else p.name)
                    shutil.copyfile(p,target)
            for p in [Path(path),phase/'started.json',Path(cfg['release_file'])]:
                if p.is_file():shutil.copyfile(p,copied/p.name)
            # Collection/hashing itself is a supervised child inside the original clock.
            argv=[sys.executable,'-I','-B',__file__,'--collect',str(phase/'work'),'--output',str(phase/'e014-evidence.tar.gz')]
            sup.supervise(argv,logs/'collection.log',left,26_000_000_000,env,sample_root=os.getpid())
            outcome['archive']=binding(phase/'e014-evidence.tar.gz')
            for name in ['e014-evidence.tar.gz','e014-evidence.tar.gz.sha256']:
                left=deadline-time.monotonic()
                if left<20:raise TimeoutError('No clock for private upload/readback')
                uri=cfg['archive_prefix']+'/'+name
                sup.supervise(['/snap/bin/gcloud','storage','cp','--if-generation-match=0',str(phase/name),uri,'--quiet'],logs/('upload-'+name+'.log'),left,26_000_000_000,env,sample_root=os.getpid())
                back=phase/('readback-'+name)
                sup.supervise(['/snap/bin/gcloud','storage','cp',uri,str(back),'--quiet'],logs/('readback-'+name+'.log'),deadline-time.monotonic(),26_000_000_000,env,sample_root=os.getpid())
                if binding(back)!=binding(phase/name):raise ValueError('Private archive readback differs')
            outcome['private_readback_verified']=True
        outcome['collection_disk_observations']=collection_guard.observations
    except BaseException as exc:outcome.update(status='FAILED',collection_error=str(exc))
    write_json(phase/'completion.json',outcome)
    try:
        left=deadline-time.monotonic()
        if left<10:raise TimeoutError('No original clock for compact completion upload')
        sup.supervise(['/snap/bin/gcloud','storage','cp','--if-generation-match=0',str(phase/'completion.json'),cfg['archive_prefix']+'/completion.json','--quiet'],logs/'completion-upload.log',left,26_000_000_000,env,sample_root=os.getpid())
    except BaseException as exc:
        outcome['completion_upload_error']=str(exc)
        write_json(phase/'completion.json',outcome)
    # Current-boot external watcher stops on this parent's exit; STOP is independent.
    print('E014_PHASE_EXIT',json.dumps(outcome),flush=True)
    return 0 if outcome['status']=='SUCCESS'else 1


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--config',type=Path)
    p.add_argument('--collect',type=Path);p.add_argument('--output',type=Path);a=p.parse_args()
    if a.collect:
        if not a.output:p.error('--collect requires --output')
        print(json.dumps(collect(a.collect,a.output)));raise SystemExit(0)
    if not a.config:p.error('--config required')
    cfg=json.loads(a.config.read_text());terminal=Path(cfg['phase_root'])/'logs/parent-terminal.log'
    terminal.parent.mkdir(parents=True,exist_ok=True)
    with terminal.open('x')as stream:
        old=sys.stdout,sys.stderr;sys.stdout=Tee(sys.stdout,stream);sys.stderr=Tee(sys.stderr,stream)
        try:code=run(a.config)
        finally:sys.stdout,sys.stderr=old
    raise SystemExit(code)
