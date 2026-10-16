#!/usr/bin/env python3
"""Plan or launch only the bounded GCP E009 acquisition/assembly/depth/truth DAG.

Default mode prints a plan without writes or downloads. Explicit execution requires
a clean committed source, Linux, the persistent mount and declared allocation.
Setup uses a complete independently owned locked data environment, never old
UCloud prefixes. Setup, source hashing, resume checks and children share one clock.
The fixture mode is restricted to tiny loopback HTTP objects and runs the same DAG.
"""
import argparse
import contextlib
from datetime import datetime, timezone
import hashlib
import json
import math
import os
from pathlib import Path
import platform
import signal
import subprocess
import sys
import threading
import time
from urllib.parse import urlparse

sys.path.insert(0,str(Path(__file__).absolute().parent))
from e009_common import acquire, binding, extract, write_json
from e009_data import run_native
from e009_gcp_stage import progress
from e009_owner import Tee, supervisor
from e009_retry import verify_conda_identity
from e009_startup import supervise_activity

REPO=Path(__file__).absolute().parents[1]
EXP=REPO/'experiments/E009-competitive-benchmark'
CODE=['scripts/e009_gcp_run.py','scripts/e009_gcp_stage.py','scripts/e009_common.py',
      'scripts/e009_data.py','scripts/e009_truth.py','scripts/e009_native.py','scripts/e009_owner.py',
      'scripts/e009_retry.py','scripts/e009_startup.py','src/dl_binner/supervision.py',
      'workflows/e009-data/Snakefile']


class ClockAndDisk:
    """Raise in the main thread on the shared deadline or low working-disk reserve.

    The supervisor's finally block then stops/reaps native children. A disk watcher
    samples real free bytes every two seconds; its messages cannot refresh the
    native activity clock. No filesystem deletion or cloud mutation is performed.
    """
    def __init__(self, root, seconds, free_bytes, log=None):
        self.root,self.seconds,self.free_bytes=Path(root),seconds,free_bytes
        self.finished=threading.Event();self.reason=None;self.log=log;self.peak_used=0
    def __enter__(self):
        import shutil
        self.old=signal.getsignal(signal.SIGALRM)
        def expired(signum,frame):raise RuntimeError(self.reason or 'E009 overall data-stage clock exhausted')
        signal.signal(signal.SIGALRM,expired);signal.setitimer(signal.ITIMER_REAL,self.seconds)
        self.output=Path(self.log).open('x') if self.log else None
        def watch():
            last_report=0
            while not self.finished.wait(2):
                usage=shutil.disk_usage(self.root);free=usage.free;self.peak_used=max(self.peak_used,usage.used)
                now=time.monotonic()
                if self.output and now-last_report>=10:
                    self.output.write(json.dumps({'epoch':time.time(),'filesystem_total_bytes':usage.total,
                        'filesystem_used_bytes':usage.used,'filesystem_free_bytes':free,'peak_observed_used_bytes':self.peak_used,
                        'scope':'actual whole working filesystem; two-second samples, ten-second retained observations'})+'\n')
                    self.output.flush();last_report=now
                if free<self.free_bytes:
                    self.reason=f'E009 disk reserve violated: {free} < {self.free_bytes} bytes; preserve outputs'
                    os.kill(os.getpid(),signal.SIGALRM);return
        self.thread=threading.Thread(target=watch,daemon=True);self.thread.start()
        return self
    def __exit__(self,*exc):
        self.finished.set();self.thread.join(timeout=3)
        if self.output:self.output.close()
        signal.setitimer(signal.ITIMER_REAL,0);signal.signal(signal.SIGALRM,self.old)


def verify_completed(root):
    """Verify sealed bytes and file sets before explicit resume; fail on output drift.

    Failed unsealed stages are preserved and refused. Missing stages are eligible
    for the DAG; completed stages are never scheduled solely to collect metrics.
    """
    parts=Path(root)/'parts'
    for folder in sorted(parts.iterdir()) if parts.exists() else []:
        done=folder/'done.json'
        if not folder.is_dir() or folder.is_symlink() or not done.is_file():
            raise ValueError(f'Unsealed stage needs assessment: {folder}; no automatic retry')
        seal=json.loads(done.read_text())
        actual={str(p.relative_to(folder)) for p in folder.rglob('*') if p.is_file() and p!=done}
        if actual!=set(seal['files']):raise ValueError('Completed stage file set changed: '+str(folder))
        for name,expected in seal['files'].items():
            path=folder/name
            if Path(name).is_absolute() or '..' in Path(name).parts or binding(path,lambda n:progress(path,n))!=expected:
                raise ValueError('Completed output bytes changed: '+str(path))


def owned_runtime(plan, root, env, deadline):
    """Install an exact complete data-only Conda recipe once and verify its identities.

    Payload SHA256s are checked before offline installation. Healthy existing GCP
    prefixes are reused after exact Conda identities and native version checks;
    failed partial prefixes are preserved. No solver runs on the VM.
    """
    lock_path=EXP/'gcp-data-linux-lock.json';lock=json.loads(lock_path.read_text())
    ident=binding(lock_path)['sha256'][:12]
    home=Path(root).parent;cache=home/'cache'/('data-v1-'+ident)
    prefix=home/'envs'/('data-cpu-v1-'+ident)
    cache.mkdir(parents=True,exist_ok=True);prefix.parent.mkdir(parents=True,exist_ok=True)
    env.update(MAMBA_ROOT_PREFIX=str(home/'mamba-data-v1'),E009_PARENT_DEADLINE=str(deadline))
    os.environ.update(env)
    if not prefix.exists():
        boot=cache/'micromamba.tar.bz2';spec=plan['micromamba']
        acquire(spec,boot,resume=boot.exists())
        if not (cache/'bootstrap').exists():extract(boot,cache/'bootstrap')
        package_dir=cache/'packages';package_dir.mkdir(exist_ok=True)
        entries=[]
        for pkg in lock['packages']:
            target=package_dir/pkg['fn'];spec={k:pkg[k] for k in ('url','sha256')};spec['bytes']=pkg['size']
            acquire(spec,target,resume=target.exists())
            entries.append(target.absolute().as_uri()+'#'+pkg['md5'])
        explicit=cache/'explicit.txt'
        if not explicit.exists():explicit.write_text('@EXPLICIT\n'+'\n'.join(entries)+'\n')
        run_native([cache/'bootstrap/bin/micromamba','--no-rc','create','-y','-p',prefix,'--offline','--file',explicit],
                   Path(root)/'logs/runtime-install.log')
    verify_conda_identity(prefix,lock)
    runtime={n:str(prefix/'bin'/n) for n in ('python','samtools','strobealign','minimap2','megahit')}
    env['PATH']=str(prefix/'bin')+':'+env.get('PATH','')
    return runtime


def validate_runtime(runtime, root, env, fixture):
    """Check lexical Python, Snakemake and the actual selected native binary versions.

    This is new-host identity/health admission, not another five-binner preflight
    or community-scale performance test. Bound executable bytes and library recipe.
    """
    probe=[runtime['python'],'-I','-B','-c',
        'import sys,json,snakemake;print(json.dumps({"python":sys.version,"prefix":sys.prefix,"snakemake":snakemake.__version__,"snakemake_origin":snakemake.__file__}));assert snakemake.__version__=="9.16.3"']
    run_native(probe,Path(root)/'logs/python-identity.log')
    python_identity=json.loads((Path(root)/'logs/python-identity.log').read_text().splitlines()[0])
    expected_prefix=Path(runtime['python']).parent.parent
    if Path(python_identity['prefix'])!=expected_prefix or not Path(python_identity['snakemake_origin']).is_relative_to(expected_prefix):
        raise ValueError('Lexical Python/Snakemake origins differ from the selected data prefix')
    if not fixture and not python_identity['python'].startswith('3.12.10 '):
        raise ValueError('Pinned independent data Python version changed')
    identities={'interpreter':python_identity}
    for tool,version in [('samtools','1.24'),('strobealign','0.17.0'),('minimap2','2.30'),('megahit','1.2.9')]:
        log=Path(root)/'logs'/f'{tool}-identity.log'
        # Resume identity checks need new closed logs, leaving older evidence intact.
        if log.exists():log=log.with_name(log.stem+'-'+str(time.time_ns())+'.log')
        run_native([runtime[tool],'--version'],log)
        if version not in log.read_text():raise ValueError('Native data version differs: '+tool)
        identities[tool]={'path':runtime[tool],'file':binding(Path(runtime[tool]).resolve()),'version':version}
    identities['python']={'lexical':runtime['python'],'file':binding(Path(runtime['python']).resolve())}
    return identities


def execute(args, plan):
    """Capture launch evidence, enforce cumulative budget, supervise the actual DAG."""
    started=time.monotonic();root=args.root.absolute();root.mkdir(parents=True,exist_ok=True)
    (root/'logs').mkdir(exist_ok=True)
    attempt=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S')+'-'+str(time.time_ns())
    terminal=root/'logs'/('terminal-'+attempt+'.log');status={'status':'failed','fixture':args.fixture,
        'allocated_vcpus':args.allocated_vcpus,'allocated_ram_gib':args.allocated_ram_gib,
        'hostname':platform.node(),'platform':platform.platform(),'phase':'data only; no fits or quality scores'}
    oldout,olderr=sys.stdout,sys.stderr
    with terminal.open('x') as stream:
        sys.stdout=Tee(oldout,stream);sys.stderr=Tee(olderr,stream)
        try:
            spent=sum(json.loads(p.read_text())['elapsed_seconds'] for p in root.glob('attempt-*.json'))
            remaining=args.hours*3600-spent
            if remaining<=0:raise ValueError('Approved cumulative phase budget exhausted; no automatic extension')
            deadline=started+remaining
            with ClockAndDisk(root,remaining,args.free_gib*1024**3,root/'logs'/('disk-'+attempt+'.jsonl')) as guard:
                head=subprocess.check_output(['git','-C',str(REPO),'rev-parse','HEAD'],text=True).strip()
                if not args.fixture:
                    if platform.system()!='Linux' or not os.path.ismount('/srv/dl_binner'):
                        raise ValueError('Direct GCP execution requires Linux and the persistent /srv/dl_binner mount')
                    libc,version=platform.libc_ver()
                    if platform.machine()!='x86_64' or libc!='glibc' or tuple(map(int,version.split('.')[:2]))<(2,34):
                        raise ValueError('Locked data runtime requires Linux x86-64 and glibc >=2.34')
                    if not root.is_relative_to(Path('/srv/dl_binner/experiments/e009')):
                        raise ValueError('Use the established GCP E009 persistent subtree')
                    if head!=args.source_commit or subprocess.check_output(['git','-C',str(REPO),'status','--porcelain'],text=True):
                        raise ValueError('Clean exact committed source required before scientific preparation')
                else:
                    for spec in [*plan['samples'],plan['source_genomes']]:
                        if urlparse(spec['url']).hostname not in ('127.0.0.1','localhost') or spec['bytes']>2_000_000:
                            raise ValueError('Fixture permits tiny loopback objects only')
                if hasattr(os,'sched_getaffinity'):
                    cpus=sorted(os.sched_getaffinity(0))
                    if len(cpus)<args.allocated_vcpus:raise ValueError('Declared allocation exceeds available CPU affinity')
                    os.sched_setaffinity(0,cpus[:args.allocated_vcpus])
                env=supervisor().isolated_env(1);env['E009_PARENT_DEADLINE']=str(deadline)
                # Parent-side setup children need the same isolation as DAG workers.
                os.environ.clear();os.environ.update(env)
                # Full input bytes and verification are inside this same clock.
                code={name:binding(REPO/name) for name in CODE}
                runtime=json.loads(args.runtime_json.read_text()) if args.runtime_json else owned_runtime(plan,root,env,deadline)
                # Give each attempt its own identity logs; no overwrite on resume.
                identity_root=root/'runtime-attempts'/attempt;(identity_root/'logs').mkdir(parents=True)
                identities=validate_runtime(runtime,identity_root,env,args.fixture)
                truth_keys=('sample0_source_files','development_overlap','source_manifest_provenance')
                evaluator={k:plan[k] for k in truth_keys if k in plan}
                evaluator_path=root/'evaluator-config.json'
                if evaluator_path.exists():
                    if not args.resume or json.loads(evaluator_path.read_text())!=evaluator:
                        raise ValueError('Explicit resume needs identical source/config/runtime bytes')
                else:write_json(evaluator_path,evaluator)
                feature_plan={k:v for k,v in plan.items() if k not in truth_keys}
                cfg={'repo':str(REPO),'root':str(root),'plan':feature_plan,'runtime':runtime,'runtime_identities':identities,
                     'evaluator_config':str(evaluator_path),'evaluator_binding':binding(evaluator_path),
                     'data_environment_lock':binding(EXP/'gcp-data-linux-lock.json'),
                     'source_commit':head,'code':code,'fixture':args.fixture,'threads':args.allocated_vcpus,
                     'assembly_threads':1 if args.fixture else args.allocated_vcpus,
                     'assembly_mem_bytes':int(args.allocated_ram_gib*1024**3*.75),
                     'working_rss_bytes':int(args.allocated_ram_gib*1024**3*.82),
                     'hours':args.hours,'free_gib':args.free_gib}
                path=root/'stage-config.json'
                if path.exists():
                    if not args.resume or json.loads(path.read_text())!=cfg:
                        raise ValueError('Explicit resume needs identical source/config/runtime bytes')
                    verify_completed(root)
                else:
                    if args.resume:raise ValueError('Resume has no original configuration')
                    write_json(path,cfg)
                command=[runtime['python'],'-I','-B','-m','snakemake','--snakefile',str(REPO/'workflows/e009-data/Snakefile'),
                         '--directory',str(root),*supervisor().local_scheduler_options(args.allocated_vcpus,cfg['working_rss_bytes']//1000000),
                         '--benchmark-extended','--printshellcmds','--config','stage_config='+str(path)]
                if args.fixture_until:command.insert(5,str(root/'parts'/args.fixture_until/'done.json'))
                write_json(root/('command-'+attempt+'.json'),{'argv':command,'deadline_remaining_seconds':deadline-time.monotonic()})
                log=root/'logs'/('dag-'+attempt+'.log')
                code_result=supervise_activity(supervisor(),command,log,deadline-time.monotonic(),
                    cfg['working_rss_bytes'],env,sample_root=os.getpid(),idle_seconds=args.stall_seconds)
                if code_result['exit_code']:raise RuntimeError('Native data DAG failed; inspect '+str(log))
                status.update(status='passed',source_commit=head,final_manifest=str(root/'parts/final/done.json') if not args.fixture_until else None,
                              fixture_until=args.fixture_until,scientific_scoring_admitted=False,
                              peak_sampled_filesystem_used_bytes=guard.peak_used,native_dag_receipt=code_result)
        except BaseException as exc:
            status['error']=repr(exc);print('E009_DATA_FAILURE='+repr(exc),flush=True)
        finally:
            status['elapsed_seconds']=time.monotonic()-started
            status['allocated_vcpu_hours']=status['elapsed_seconds']*args.allocated_vcpus/3600
            status['terminal_log']=str(terminal)
            print('E009_DATA_STATUS='+json.dumps(status),flush=True)
            sys.stdout,sys.stderr=oldout,olderr
    status['closed_terminal']=binding(terminal)
    write_json(root/('attempt-'+attempt+'.json'),status)
    return 0 if status['status']=='passed' else 1


def main():
    """Default to inspection; require explicit execution and positive allocation bounds."""
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--plan',type=Path,default=EXP/'gcp-data-plan.json');p.add_argument('--root',type=Path,
                    default=Path('/srv/dl_binner/experiments/e009/data-stage-v1'))
    p.add_argument('--source-commit');p.add_argument('--execute',action='store_true');p.add_argument('--resume',action='store_true')
    p.add_argument('--allocated-vcpus',type=int,default=8);p.add_argument('--allocated-ram-gib',type=float,default=32)
    p.add_argument('--hours',type=float,default=24);p.add_argument('--free-gib',type=float,default=25)
    p.add_argument('--stall-seconds',type=float,default=1800)
    p.add_argument('--runtime-json',type=Path,help='Explicit existing data runtime; fixture or reviewed native host only')
    p.add_argument('--fixture',action='store_true');p.add_argument('--fixture-until',choices=['sources','assembly'])
    a=p.parse_args()
    if not all(math.isfinite(v) for v in (a.allocated_ram_gib,a.hours,a.free_gib,a.stall_seconds)) or min(a.allocated_vcpus,a.allocated_ram_gib,a.hours,a.stall_seconds)<=0 or a.free_gib<0:
        p.error('Declare positive CPUs/RAM/clock/stall and nonnegative disk reserve')
    if a.allocated_vcpus<2:p.error('Depth needs reducer and native main process')
    if a.fixture_until and not a.fixture:p.error('Partial fixture target is local QA only')
    plan=json.loads(a.plan.read_text())
    if not a.execute:
        print(json.dumps({'mode':'plan only; no writes/downloads','samples':plan['samples'],'root':str(a.root),
                          'vcpus':a.allocated_vcpus,'ram_gib':a.allocated_ram_gib,'cumulative_hours':a.hours},indent=2));return 0
    return execute(a,plan)


if __name__=='__main__':raise SystemExit(main())
