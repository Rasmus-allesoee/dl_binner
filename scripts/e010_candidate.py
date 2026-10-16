#!/usr/bin/env python3
"""Prepare or run one separately approved frozen dev4 E009 development candidate.

Default is read-only. The operator owns fresh credits/prices, complete independent
Python3.12 setup, exact clean source sync and verified boot/process watchdog/STOP.
Their time/storage count from VM start, not this launcher. No cloud APIs, installs,
baseline refit, scoring, retry, resume or resource changes occur here.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import shutil
import sys
import tarfile
import time
import zipfile
sys.path.insert(0,str(Path(__file__).absolute().parent))
from e009_common import binding,write_json
from e009_controls import PhaseGuard,run_serial
from e009_owner import Tee

ROOT=Path(__file__).absolute().parents[1]
EXP=ROOT/'experiments/E010-coherent-prototype'


def candidate_command(python,fasta,depth,hmm,manifest,output,seconds):
    """Use only the frozen integrated defaults and complete ten-depth inputs."""
    if not 0<seconds<=14400:raise TimeoutError('Candidate phase clock exhausted')
    return list(map(str,[python,'-I','-B','-m','dl_binner','candidate','--fasta',fasta,
        '--depth',depth,'--marker-hmm',hmm,'--marker-manifest',manifest,
        '--output',output,'--threads',8,'--memory-gb',26,'--timeout',seconds]))


def verify_wheel(path,lock):
    """Verify archive and all installed package/default members against the frozen lock."""
    if binding(path)!=lock['wheel']:raise ValueError('Candidate wheel bytes changed')
    with zipfile.ZipFile(path)as archive:
        names=archive.namelist()
        if len(names)!=len(set(names)):raise ValueError('Duplicate candidate wheel member')
        package={n.removeprefix('dl_binner/'):archive.read(n) for n in names if n.startswith('dl_binner/')and not n.endswith('/')}
    actual={n:dict(bytes=len(b),sha256=hashlib.sha256(b).hexdigest()) for n,b in package.items()}
    if actual!=lock['package_files']:raise ValueError('Candidate package/default bytes changed')


def verify_approval(approval,now):
    """Fail closed on missing human-approved budget/coverage/supervision receipts."""
    required={'experiment':'E010','incremental_gross_ceiling_usd':2,'credit_gate_passed':True,
        'pending_usage_accounted':True,'provider_stop_seconds':15300,'watchdog_release_verified':True,
        'no_resource_change':True,'storage_retention_extended':False}
    if any(approval.get(k)!=v for k,v in required.items()):raise ValueError('New E010 approval/gate receipt missing or different')
    if not approval['vm_start_epoch']+15300<min(approval['credit_valid_until_epoch'],approval['storage_valid_until_epoch']):
        raise ValueError('Credit/storage approval expired')
    if set(approval['covered_costs'])!={'compute','disk','storage','network','operations'}:
        raise ValueError('Incomplete credit cost coverage')
    elapsed=now-approval['vm_start_epoch']
    if not 0<=elapsed<14100:raise TimeoutError('Original four-hour phase allowance unavailable')
    return 14400-elapsed


def collect(root):
    """Retain all closed science/log bytes, excluding environments and native JIT cache."""
    root=Path(root);paths=[]
    for p in sorted(root.rglob('*')):
        relative=p.relative_to(root)
        if 'native-cache' in relative.parts:continue
        if p.is_symlink():raise ValueError('Linked candidate evidence refused')
        if p.is_file()and p!=root/'terminal.log':paths.append(p)
    inventory={'files':{str(p.relative_to(root)):binding(p) for p in paths},
        'excludes':['native-cache (regenerable JIT compilation)','live terminal.log (closed snapshot retained)']}
    record=root/'collection-inventory.json';write_json(record,inventory);paths.append(record)
    archive=root.parent/(root.name+'-evidence.tar.gz')
    with archive.open('xb')as stream,tarfile.open(fileobj=stream,mode='w:gz',compresslevel=1)as tar:
        for p in paths:tar.add(p,arcname=str(p.relative_to(root)),recursive=False)
    if archive.stat().st_size>2*1024**3:raise ValueError('Evidence exceeds 2-GiB export budget; no automatic transfer')
    expected={str(p.relative_to(root)):binding(p)for p in paths}
    with tarfile.open(archive)as tar:
        members=tar.getmembers()
        if len(members)!=len(expected)or{m.name for m in members}!=set(expected):raise ValueError('Evidence member set mismatch')
        for m in members:
            if not m.isfile():raise ValueError('Non-file evidence member')
            h=hashlib.sha256()
            with tar.extractfile(m)as reader:
                for block in iter(lambda:reader.read(1024*1024),b''):h.update(block)
            if {'bytes':m.size,'sha256':h.hexdigest()}!=expected[m.name]:raise ValueError('Evidence member bytes differ')
    checksum=archive.with_name(archive.name+'.sha256')
    with checksum.open('x')as stream:stream.write(binding(archive)['sha256']+'  '+archive.name+'\n')
    return {'archive':binding(archive),'path':str(archive),'members':len(paths),
            'logical_member_bytes':sum(p.stat().st_size for p in paths),'inventory':binding(record)}


def execute(args):
    """Verify frozen bytes/runtime, fit once and collect within the original boot clock."""
    approval=json.loads(args.approval.read_text());now=time.time()
    seconds=verify_approval(approval,now)
    if platform.system()!='Linux'or sys.version_info[:2]!=(3,12):raise ValueError('Native Linux Python3.12 launcher required')
    if os.cpu_count()!=8 or not os.path.ismount('/srv/dl_binner'):raise ValueError('Expected existing 8-vCPU mounted GCP VM')
    ram_kib=int(next(line.split()[1]for line in Path('/proc/meminfo').read_text().splitlines()if line.startswith('MemTotal:')))
    if not 30*1024**2<=ram_kib<=35*1024**2:raise ValueError('Expected existing 32-GiB VM RAM')
    if not args.output.resolve().is_relative_to(Path('/srv/dl_binner')):raise ValueError('Candidate output must use the existing work disk')
    if Path('/proc/sys/kernel/random/boot_id').read_text().strip()!=approval['boot_id']:raise ValueError('Watchdog boot identity differs')
    import subprocess
    if subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()!=approval['source_commit']:
        raise ValueError('Source commit differs from approval')
    if subprocess.check_output(['git','status','--porcelain'],cwd=ROOT,text=True).strip():raise ValueError('Clean source required')
    lock=json.loads((EXP/'candidate-lock.json').read_text())
    out=args.output.absolute();out.mkdir(parents=True,exist_ok=False)
    initial_growth=max(0,shutil.disk_usage(out).used-approval['initial_filesystem_used_bytes'])
    if initial_growth>=20*1024**3:raise ValueError('Setup exhausted working disk allowance')
    result={'status':'FAILED','fit_completed':False,'source_commit':approval['source_commit']}
    start=time.monotonic();deadline=start+seconds
    prior_out,prior_err=sys.stdout,sys.stderr
    terminal=(out/'terminal.log').open('x')
    sys.stdout,sys.stderr=Tee(prior_out,terminal),Tee(prior_err,terminal)
    try:
        with PhaseGuard(out,seconds,growth_bytes=20*1024**3-initial_growth) as guard:
            verify_wheel(args.wheel,lock)
            for key,path in [('fasta',args.fasta),('depth',args.depth),('marker_hmm',args.marker_hmm)]:
                if binding(path)!=lock['inputs'][key]:raise ValueError('Frozen input changed: '+key)
            if binding(EXP/'marker-asset.json')!=lock['inputs']['marker_manifest']:raise ValueError('Marker manifest changed')
            write_json(out/'approval.json',approval)
            write_json(out/'lock.json',lock)
            installed=out/'installed.json'
            probe="from dl_binner.runner import source_records;from dl_binner.contracts import write_json;import sys;assert sys.version_info[:2]==(3,12),'Owned runtime must use Python3.12';write_json(sys.argv[1],source_records())"
            stages=[('runtime',lambda t:[str(args.python),'-I','-B',str(ROOT/'scripts/check_runtime.py'),
                       '--role','candidate','--requirements',str(ROOT/'requirements/candidate-cpu.txt'),
                       '--threads','8','--output',str(out/'runtime.json')]),
                    ('installed-source',lambda t:[str(args.python),'-I','-B','-c',probe,str(installed)])]
            run_serial(stages,out,deadline,collect_reserve=300)
            if json.loads(installed.read_text())!=lock['package_files']:raise ValueError('Installed source/default lock differs')
            run_serial([('production-marker-contract',lambda t:[str(args.python),'-I','-B',str(ROOT/'scripts/e010_marker_contract.py'),
                '--profile',str(args.marker_hmm),'--manifest',str(EXP/'marker-asset.json'),
                '--threads','8','--output',str(out/'marker-contract')]),
                ('native-contracts',lambda t:[sys.executable,'-I','-B',str(ROOT/'scripts/test_product.py'),
                '--python',str(args.python),'--threads','2','--timeout',str(min(600,t)),'--output',str(out/'native-contracts')]),
                ('candidate',lambda t:candidate_command(args.python,args.fasta,args.depth,args.marker_hmm,
                    EXP/'marker-asset.json',out/'candidate',t))],out,deadline,collect_reserve=300)
            if not (out/'candidate/completion.json').is_file():raise ValueError('Candidate completion missing')
            result.update(status='SUCCESS',fit_completed=True,wall_seconds=time.monotonic()-start,
                          disk_observations=guard.observations)
            write_json(out/'fit-result.json',result)
            terminal.flush();(out/'terminal.snapshot.log').write_bytes((out/'terminal.log').read_bytes())
            result['collection']=collect(out)
    except BaseException as exc:result['error']=f'{type(exc).__name__}: {exc}'
    finally:
        if 'error' in result:result['status']='FAILED'
        write_json(out/'phase-result.json',result)
        sys.stdout,sys.stderr=prior_out,prior_err;terminal.close()
    return 0 if result['status']=='SUCCESS'else 1


def main():
    """Print the read-only proposal by default; execution requires every explicit path."""
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--execute',action='store_true')
    for name in ['approval','python','wheel','fasta','depth','marker-hmm','output']:p.add_argument('--'+name,type=Path)
    a=p.parse_args()
    if not a.execute:
        print(json.dumps(dict(execution=False,experiment='E010',fits=1,external_binners=False,
            gross_ceiling_usd=2,cumulative_VM_seconds=14400,provider_stop_seconds=15300,
            free_reserve_GiB=25,max_extra_GiB=20,resources='existing e2-standard-8 / 32 GiB / 300-GiB disk',
            prerequisites='fresh human approval, credits/pending usage/prices/storage, native runtime, frozen bytes and verified boot/process watchdog')))
        return 0
    if any(getattr(a,name) is None for name in ['approval','python','wheel','fasta','depth','marker_hmm','output']):p.error('All explicit execution paths required')
    return execute(a)


if __name__=='__main__':raise SystemExit(main())
