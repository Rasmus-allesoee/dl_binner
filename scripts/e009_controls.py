#!/usr/bin/env python3
"""Prepare or explicitly launch only E009's unchanged, separately approved controls.

Default: print a read-only plan. Execution needs an explicit new $2 approval,
admitted truth, Linux 8-CPU/32-GiB mount and fresh owned environment/output paths.
Setup, hashing, native runtime verification, two serial paired invocations and
compact collection share four hours. No scoring, architecture change, external
binner, cloud API, retry or implicit resume. Provider STOP/watchdog are operator
prerequisites; this process cannot start, resize or stop a VM itself.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import importlib.metadata
import json
import math
import os
from pathlib import Path
import platform
import re
import shutil
import signal
import sys
import tarfile
import threading
import time
import zipfile
sys.path.insert(0,str(Path(__file__).absolute().parent))
from e009_common import binding, write_json
from e009_owner import supervisor, Tee

REPO=Path(__file__).absolute().parents[1]
EXP=REPO/'experiments/E009-competitive-benchmark'
SECONDS=14400


def verify_wheel(wheel, lock):
    """Refuse any changed wheel or package/default byte relative to immutable dev3."""
    if binding(wheel)!=lock['wheel']:raise ValueError('Frozen dev3 wheel bytes changed')
    with zipfile.ZipFile(wheel)as z:
        names=z.namelist()
        if len(names)!=len(set(names)):raise ValueError('Duplicate wheel member')
        package={n.removeprefix('dl_binner/'):n for n in names if n.startswith('dl_binner/')and not n.endswith('/')}
        if set(package)!=set(lock['package_files']):raise ValueError('Wheel package file set changed')
        for name,entry in package.items():
            data=z.read(entry);actual={'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()}
            if actual!=lock['package_files'][name]:raise ValueError('Wheel package source/default changed')


def paired_command(python, fasta, depth, output, remaining):
    """Use the accepted installed product command; never pass truth or tuning options."""
    if not math.isfinite(remaining)or remaining<=0:raise TimeoutError('Shared control-phase clock exhausted')
    argv=[str(python),'-I','-B','-m','dl_binner','run','--fasta',str(fasta),'--output',str(output),
          '--threads','8','--min-length','500','--memory-gb','26','--timeout',str(remaining)]
    if depth is not None:argv+=['--depth',str(depth)]
    return argv


class PhaseGuard:
    """Bound parent-side setup/hash/collection and sampled disk growth, as well as children.

    An alarm raises in the main thread so native supervision stops/reaps its owned
    process group. Never delete files to restore a reserve. Disk observations are
    whole-filesystem measurements, not exact attributable output sizes.
    """
    def __init__(self, root, seconds, reserve_bytes=25*1024**3, growth_bytes=20*1024**3):
        self.root=Path(root);self.seconds=seconds;self.reserve=reserve_bytes;self.growth=growth_bytes
        self.finished=threading.Event();self.reason=None;self.observations=[]

    def __enter__(self):
        initial=shutil.disk_usage(self.root);self.initial=initial.used
        if initial.free<self.reserve:raise RuntimeError('Control phase free-space reserve unavailable')
        self.previous=signal.getsignal(signal.SIGALRM)
        def expired(signum,frame):raise TimeoutError(self.reason or 'Whole control-phase clock exhausted')
        signal.signal(signal.SIGALRM,expired);signal.setitimer(signal.ITIMER_REAL,self.seconds)
        def watch():
            while not self.finished.wait(.2):
                try:
                    usage=shutil.disk_usage(self.root)
                    if not self.observations or time.monotonic()-self.observations[-1]['monotonic']>=2:
                        self.observations.append({'monotonic':time.monotonic(),'used':usage.used,'free':usage.free,
                                                  'growth':usage.used-self.initial})
                    if usage.free<self.reserve:self.reason='Control phase disk reserve violated'
                    if usage.used-self.initial>self.growth:self.reason='Control phase 20-GiB growth allowance exhausted'
                except OSError as exc:self.reason='Disk monitoring failed: '+str(exc)
                if self.reason:os.kill(os.getpid(),signal.SIGALRM);return
        self.thread=threading.Thread(target=watch,daemon=True);self.thread.start();return self

    def __exit__(self,*exc):
        self.finished.set();self.thread.join(timeout=2)
        signal.setitimer(signal.ITIMER_REAL,0);signal.signal(signal.SIGALRM,self.previous)


def run_serial(stages, output, deadline, ram_bytes=30_000_000_000, env=None, collect_reserve=120):
    """Run each real command only after its predecessor succeeds, with one deadline.

    Stage factories receive the remaining shared time; tests substitute only the
    child programs to verify safety/serial placement without fitting a binner.
    Preserve failed logs, refuse existing logs, never retry or schedule a successor.
    """
    output=Path(output);sup=supervisor();receipts=[]
    for name,factory in stages:
        remaining=deadline-time.monotonic()-collect_reserve
        if remaining<=0:raise TimeoutError('Shared control-phase work clock exhausted')
        argv=factory(remaining)
        print('CONTROL_STAGE '+name,flush=True)
        receipt=sup.supervise(argv,output/(name+'.log'),remaining,ram_bytes,env or sup.isolated_env(8),sample_root=os.getpid())
        receipts.append({'stage':name,'receipt':receipt})
    return receipts


def probe(prefix, lock_path, requirements_path, output):
    """Inspect the actual fresh installed source, complete distribution closure and origins.

    Imports only; no tiny training run. Native scientific/readers are previously
    accepted product contracts, distinct from these new launcher safety checks.
    """
    prefix=Path(prefix).absolute();lock=json.loads(Path(lock_path).read_text())
    if sys.version_info[:2]!=(3,12):raise ValueError('Pinned native CPU recipe requires Python 3.12')
    if Path(sys.prefix).absolute()!=prefix or sys.base_prefix==sys.prefix:raise ValueError('Fresh owned venv required')
    import dl_binner,numpy,torch,networkx,threadpoolctl
    if torch.version.cuda is not None:raise ValueError('CPU-only torch required')
    expected={'dl-binner':lock['package']}
    normal=lambda s:re.sub(r'[-_.]+','-',s).lower()
    for raw in Path(requirements_path).read_text().splitlines():
        raw=raw.strip()
        if not raw or raw.startswith('#'):continue
        versioned,*marker=raw.split(';')
        if marker and 'Darwin'in marker[0]:continue
        name,version=versioned.strip().split('==');expected[normal(name)]=version
    actual={normal(d.metadata['Name']):d.version for d in importlib.metadata.distributions()}
    if actual!=expected:raise ValueError('Complete owned runtime distribution closure differs: '+str(actual))
    package=Path(dl_binner.__file__).parent
    if not package.is_relative_to(prefix):raise ValueError('Package outside owned environment')
    records={str(p.relative_to(package)):binding(p)for p in package.rglob('*')if p.is_file()and p.suffix in('.py','.json')}
    if records!=lock['package_files']:raise ValueError('Installed dev3 source/default bytes differ')
    origins={m.__name__:str(Path(m.__file__).absolute())for m in [dl_binner,numpy,torch,networkx,threadpoolctl]}
    if any(not Path(p).is_relative_to(prefix)for p in origins.values()):raise ValueError('Borrowed numerical runtime refused')
    write_json(output,{'distributions':actual,'origins':origins,'package_files':records,
                       'prefix':sys.prefix,'base_prefix':sys.base_prefix,'lexical_python':sys.executable,'fit_executed':False})


def collect_complete(root, terminal=None):
    """Archive closed control outputs/logs without environments, caches or an open log.

    Capture the terminal bytes as an explicitly immutable snapshot. Inventory all
    retained regular members including its inventory length in logical-byte totals;
    the inventory cannot hash itself. Leave bulk originals and failure partials in
    place; the shared parent clock/disk guard also covers hashing and compression.
    """
    root=Path(root)
    if terminal is not None:
        (root/'terminal.snapshot.log').write_bytes(Path(terminal).read_bytes())
    paths=[]
    for p in sorted(root.iterdir()):
        if p.is_symlink():raise ValueError('Linked control output refused')
        if p.is_file():paths.append(p)
        elif p.name in ('ten-depth','tnf-only'):
            for child in sorted(p.rglob('*')):
                if child.is_symlink():raise ValueError('Linked product output refused')
                if child.is_file():paths.append(child)
    inventory={'files':{str(p.relative_to(root)):binding(p)for p in paths},
               'excludes':['env','cache'],'terminal_scope':'closed snapshot, never later live-log size'}
    record=root/'collection-inventory.json';write_json(record,inventory);paths.append(record)
    archive=root/'controls-evidence.tar.gz'
    with archive.open('xb')as stream,tarfile.open(fileobj=stream,mode='w:gz')as tar:
        for p in paths:tar.add(p,arcname=str(p.relative_to(root)),recursive=False)
    result={'archive':binding(archive),'filename':archive.name,'regular_members':len(paths),
            'logical_member_bytes':sum(p.stat().st_size for p in paths),'inventory':binding(record)}
    (root/'controls-evidence.tar.gz.sha256').write_text(result['archive']['sha256']+'  '+archive.name+'\n')
    return result


def execute(args):
    """Run only an explicitly approved fresh phase after externally verified cloud gates.

    The admission record binds the truth manifest but truth is never passed to
    feature/training commands. This launcher performs no binner evaluation. A
    failed phase is evidence, not permission to resume, resize or extend.
    """
    started=time.monotonic();root=args.output.absolute()
    approval=json.loads(args.approval.read_text())
    if approval.get('approved')is not True or approval.get('scope')!='e009-unchanged-controls-v1' or approval.get('new_budget_usd')!=2:
        raise ValueError('Explicit separate $2 control approval required')
    if approval.get('credit_gate_passed')is not True or approval.get('provider_stop_seconds')!=15300 or approval.get('watchdog_verified')is not True:
        raise ValueError('Fresh external credit/provider STOP/live watchdog gate required')
    if platform.system()!='Linux' or os.cpu_count()!=8 or not os.path.ismount('/srv/dl_binner'):
        raise ValueError('Existing mounted eight-CPU Linux VM required')
    if not root.is_relative_to(Path('/srv/dl_binner/experiments/e009')):raise ValueError('Use persistent E009 output path')
    if root.exists():raise ValueError('Fresh control phase root required; no automatic resume')
    root.mkdir(parents=True);result={'status':'FAILED','started_utc':datetime.now(timezone.utc).isoformat(),'no_scores':True}
    guard=PhaseGuard(root,SECONDS-(time.monotonic()-started));error=None
    try:
        with guard:
            lock=json.loads(args.package_lock.read_text());verify_wheel(args.wheel,lock)
            if binding(args.requirements)!=lock['requirements']:raise ValueError('Frozen requirements changed')
            admission=json.loads(args.truth_admission.read_text())
            if admission.get('admitted')is not True or approval.get('truth_admission_sha256')!=binding(args.truth_admission)['sha256']:
                raise ValueError('Admitted versioned truth/approval binding required')
            inputs=json.loads(args.inputs.read_text())
            if inputs!=json.loads((EXP/'diagnostic-feature-inputs.json').read_text()):
                raise ValueError('Frozen feature acceptance contract differs')
            if admission.get('assembly')!=inputs['fasta']:
                raise ValueError('Truth and accepted feature assembly differ')
            for name,path in [('fasta',args.fasta),('depth',args.depth)]:
                if binding(path)!=inputs[name]:raise ValueError('Accepted feature bytes differ: '+name)
            phase_bindings={n:binding(p)for n,p in [('inputs',args.inputs),('approval',args.approval),
                ('truth_admission',args.truth_admission),('wheel',args.wheel),('package_lock',args.package_lock),('requirements',args.requirements)]}
            write_json(root/'phase-inputs.json',phase_bindings)
            py=root/'env/bin/python';deadline=started+SECONDS
            pip=[py,'-I','-B','-m','pip','--isolated','--cache-dir',root/'cache']
            stages=[('01-create-env',lambda t:[args.base_python,'-I','-B','-m','venv','--copies',root/'env']),
                ('02-bootstrap',lambda t:pip+['install','--only-binary=:all:','pip==25.1.1','setuptools==65.5.0','wheel==0.45.1']),
                ('03-cpu-torch',lambda t:pip+['install','--no-deps','--only-binary=:all:','torch==2.2.2+cpu','--index-url','https://download.pytorch.org/whl/cpu']),
                ('04-dependencies',lambda t:pip+['install','--only-binary=:all:','-r',args.requirements]),
                ('05-dev3',lambda t:pip+['install','--no-deps',args.wheel]),
                ('06-pip-check',lambda t:pip+['check']),
                ('07-runtime-probe',lambda t:[py,'-I','-B',Path(__file__).absolute(),'--probe','--prefix',root/'env',
                    '--package-lock',args.package_lock,'--requirements',args.requirements,'--probe-output',root/'runtime.json']),
                ('08-cli-help',lambda t:[py,'-I','-B','-m','dl_binner','run','--help']),
                ('09-ten-depth',lambda t:paired_command(py,args.fasta,args.depth,root/'ten-depth',t)),
                ('10-tnf-only',lambda t:paired_command(py,args.fasta,None,root/'tnf-only',t))]
            result['stages']=run_serial(stages,root,deadline)
            # Verify inputs and compact journals, never duplicate large exports or environments.
            for name,path in [('fasta',args.fasta),('depth',args.depth)]:
                if binding(path)!=inputs[name]:raise ValueError('Consumed input mutated: '+name)
            terminal=root.with_name(root.name+'-terminal.log')
            result['collection']=collect_complete(root,terminal if terminal.exists()else None)
            result.update(status='SUCCESS',four_arms_completed=True)
    except BaseException as exc:error=exc;result['error']=f'{type(exc).__name__}: {exc}'
    finally:
        result.update(wall_seconds=time.monotonic()-started,disk_observations=guard.observations,
                      phase_seconds_ceiling=SECONDS,no_retry_or_extension=True)
        write_json(root/'phase-result.json',result)
    if error:raise error
    return result


def main():
    """Read-only plan by default; execution is a separate human-authorized operation."""
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--execute',action='store_true');p.add_argument('--probe',action='store_true')
    for n in ['approval','truth_admission','inputs','fasta','depth','output','wheel','base_python','prefix','probe_output']:
        p.add_argument('--'+n.replace('_','-'),type=Path)
    p.add_argument('--package-lock',type=Path,default=EXP/'diagnostic-package-lock.json')
    p.add_argument('--requirements',type=Path,default=REPO/'requirements/binner-cpu.txt')
    a=p.parse_args()
    if a.probe:
        if a.execute:p.error('Probe and execution are separate modes')
        probe(a.prefix,a.package_lock,a.requirements,a.probe_output);return
    if not a.execute:
        print(json.dumps({'execution':False,'scope':'four unchanged dev3 arms from two serial product runs',
                          'new_approval_usd':2,'cumulative_seconds':SECONDS,'provider_STOP_seconds':15300,
                          'threads':8,'RAM_GiB':32,'child_memory_GB':26,'reserve_GiB':25,'growth_allowance_GiB':20,
                          'fresh_owned_runtime_setup_in_clock':True,'truth_sent_to_binner':False,'no_scores':True,
                          'native_full_scale_affordability_unmeasured':True},indent=2));return
    for n in ['approval','truth_admission','inputs','fasta','depth','output','wheel','base_python']:
        if getattr(a,n)is None:p.error('--'+n.replace('_','-')+' is required for execution')
    # Capture terminal output even for prerequisites that fail before root creation.
    terminal=a.output.absolute().with_name(a.output.name+'-terminal.log')
    terminal.parent.mkdir(parents=True,exist_ok=True)
    old_out,old_err=sys.stdout,sys.stderr
    with terminal.open('x')as log:
        sys.stdout=Tee(old_out,log);sys.stderr=Tee(old_err,log)
        try:execute(a)
        except BaseException:
            import traceback
            traceback.print_exc();raise
        finally:sys.stdout,sys.stderr=old_out,old_err


if __name__=='__main__':main()
