#!/usr/bin/env python3
"""One bounded local standalone-package check from a committed clean snapshot.

Creates fresh independent build/binner/workflow venvs, installs read-only cached
wheels offline, builds/inspects wheel+sdist, tests a rebuilt wheel outside the
checkout, and retains status/progress/log/resource/hash evidence on failure too.
No accepted science, source environment or remote service is modified/executed.
The overall clock includes snapshot, cache verification, build and installation.
"""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import platform
import signal
import subprocess
import sys
import tarfile
import time
import traceback
import zipfile

PROJECT=Path(__file__).absolute().parents[2]


def record(path):
    """Incrementally bind one regular file without importing numerical libraries."""
    path=Path(path);h=hashlib.sha256()
    with path.open('rb') as stream:
        for part in iter(lambda:stream.read(1024*1024),b''):h.update(part)
    return dict(bytes=path.stat().st_size,sha256=h.hexdigest())


def write(path,value):
    """Exclusively write finite JSON evidence; do not replace prior attempts."""
    with Path(path).open('x') as stream:json.dump(value,stream,sort_keys=True,indent=2,allow_nan=False);stream.write('\n')


def library_tree(python):
    """Hash existing site-library regular bytes, including pyc, with metadata exclusion."""
    prefix=Path(python).parent.parent
    paths=sorted((prefix/'lib').glob('python*/site-packages'))
    if len(paths)!=1:raise RuntimeError('Expected one explicit base site directory: '+str(prefix))
    site=paths[0];h=hashlib.sha256();total=count=0
    for path in sorted(site.rglob('*')):
        if not path.is_file() or path.name=='.DS_Store':continue
        value=record(path);h.update((str(path.relative_to(site))+'\0'+value['sha256']+'\n').encode())
        total+=value['bytes'];count+=1
    return dict(site=str(site),files=count,bytes=total,tree_sha256=h.hexdigest(),excluded_metadata=['.DS_Store'])


class Tee:
    """Retain parent output while showing timestamped progress and failures."""
    def __init__(self,terminal,log):self.terminal,self.log=terminal,log
    def write(self,value):self.terminal.write(value);self.log.write(value);self.flush()
    def flush(self):self.terminal.flush();self.log.flush()


def main():
    """Execute the frozen E007 protocol once and retain a bounded outcome receipt."""
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--source-commit',required=True)
    parser.add_argument('--timeout',type=float,default=7200,help='Remaining campaign seconds, positive and at most 7200')
    for role in ('build','binner','workflow'):parser.add_argument('--'+role+'-python',type=Path,required=True)
    parser.add_argument('--wheelhouse',type=Path,action='append',required=True)
    a=parser.parse_args();a.output=a.output.absolute()
    if not 0<a.timeout<=7200:parser.error('--timeout must be positive and at most 7200')
    bases={role:getattr(a,role+'_python').absolute() for role in ('build','binner','workflow')}
    caches=[p.absolute() for p in a.wheelhouse]
    a.output.mkdir(parents=True,exist_ok=False)
    started=time.monotonic();deadline=started+a.timeout;status='failed';error=None
    oldout,olderr=sys.stdout,sys.stderr;resources={};before={};cache_records={}
    spec=importlib.util.spec_from_file_location('e007_supervision',PROJECT/'src/dl_binner/supervision.py')
    sup=importlib.util.module_from_spec(spec);spec.loader.exec_module(sup)
    env=sup.isolated_env(4);env.update(PIP_DISABLE_PIP_VERSION_CHECK='1',PIP_CACHE_DIR=str(a.output/'pip-cache'))
    def ceiling(signum,frame):raise TimeoutError('Frozen two-hour E007 integration ceiling')
    old=signal.signal(signal.SIGALRM,ceiling);signal.setitimer(signal.ITIMER_REAL,a.timeout)
    with (a.output/'terminal.log').open('x') as log:
        sys.stdout,sys.stderr=Tee(oldout,log),Tee(olderr,log)
        try:
            if subprocess.check_output(['git','rev-parse','HEAD'],cwd=PROJECT,text=True).strip()!=a.source_commit:
                raise RuntimeError('Source commit must equal the committed current snapshot')
            protocol=json.loads((PROJECT/'experiments/E007-pr-readiness/protocol.json').read_text())
            for name,value in protocol['unchanged_package_files'].items():
                if record(PROJECT/name)!=value:raise RuntimeError('Accepted package source changed: '+name)
            if record(PROJECT/protocol['accepted_wheel']['path'])!={k:protocol['accepted_wheel'][k] for k in ('bytes','sha256')}:
                raise RuntimeError('Accepted dev1 wheel bytes changed')
            for role,path in bases.items():
                before[role]=library_tree(path)
            write(a.output/'base-readonly-before.json',before)
            for folder in caches:
                if not folder.is_dir():raise FileNotFoundError(folder)
                for path in sorted(folder.glob('*.whl')):cache_records[str(path)]=record(path)
            write(a.output/'cache-inputs.json',cache_records)
            snapshot=a.output/'snapshot';snapshot.mkdir();archive=a.output/'source.tar'
            with archive.open('xb') as stream:subprocess.run(['git','archive',a.source_commit],cwd=PROJECT,stdout=stream,check=True)
            with tarfile.open(archive) as source:
                members=source.getmembers()
                if any(not (m.isdir() or m.isfile()) or Path(m.name).is_absolute() or '..' in Path(m.name).parts for m in members):raise ValueError('Unsafe source archive')
                source.extractall(snapshot,filter='data')
            if any((snapshot/name).exists() for name in ('artifacts','agent_context','.git')):raise RuntimeError('Snapshot contains local context/cache/Git')
            os.chdir(snapshot);stages=a.output/'stages';stages.mkdir();prefixes=a.output/'envs';prefixes.mkdir()
            def stage(command,name,seconds=300):
                """Run one serial command under remaining overall/RSS budget, retaining receipts."""
                remaining=min(seconds,deadline-time.monotonic())
                if remaining<=0:raise TimeoutError('Overall integration clock exhausted')
                sup.progress('E007 '+name)
                logpath=stages/(name+'.log')
                try:sup.supervise(command,logpath,remaining,8000000000,env,sample_root=os.getpid())
                finally:
                    receipt=logpath.with_suffix('.exit.json')
                    if receipt.exists():resources[name]=json.loads(receipt.read_text())
            pythons={}
            pip_flags=['--isolated','install','--no-index','--only-binary=:all:']
            for folder in caches:pip_flags+=['--find-links',folder]
            for role in bases:
                prefix=prefixes/(role+'-0.1.0.dev2-v1')
                stage([bases[role],'-I','-B','-m','venv','--copies',prefix],role+'-create')
                python=prefix/'bin/python';pythons[role]=python
                requirements=snapshot/'requirements'/({'build':'build','binner':'binner-cpu','workflow':'workflow'}[role]+'.txt')
                stage([python,'-I','-B','-m','pip',*pip_flags,'-r',requirements],role+'-install')
            dist=a.output/'dist';dist.mkdir();rebuild=a.output/'rebuilt';rebuild.mkdir()
            build=pythons['build'];binner=pythons['binner'];workflow=pythons['workflow']
            stage([build,'-I','-B',snapshot/'scripts/check_runtime.py','--role','build','--requirements',snapshot/'requirements/build.txt','--output',a.output/'build-runtime.json'],'build-probe')
            stage([build,'-I','-B','-c','from setuptools.build_meta import build_sdist,build_wheel; import sys; build_sdist(sys.argv[1]); build_wheel(sys.argv[1])',dist],'build-distributions')
            wheel=dist/'dl_binner-0.1.0.dev2-py3-none-any.whl';sdist=dist/'dl_binner-0.1.0.dev2.tar.gz'
            stage([build,'-I','-B','-m','pip','--isolated','wheel','--no-index','--no-deps','--no-build-isolation','--wheel-dir',rebuild,sdist],'sdist-rebuild')
            rebuilt=rebuild/wheel.name
            stage([build,'-I','-B',snapshot/'scripts/check_distribution.py','--wheel',wheel,'--sdist',sdist,'--rebuilt-wheel',rebuilt,'--output',a.output/'inspection.json'],'artifact-inspection')
            # Install the sdist-rebuilt wheel: the product test checks both artifact paths.
            stage([binner,'-I','-B','-m','pip','--isolated','install','--no-index','--no-deps',rebuilt],'package-install')
            for role in ('binner','workflow'):
                python=pythons[role];requirements=snapshot/'requirements'/('binner-cpu.txt' if role=='binner' else 'workflow.txt')
                stage([python,'-I','-B','-m','pip','check'],role+'-pip-check')
                stage([python,'-I','-B',snapshot/'scripts/check_runtime.py','--role',role,'--requirements',requirements,'--threads','4','--output',a.output/(role+'-runtime.json')],role+'-probe')
            stage([bases['build'],'-I','-B',snapshot/'scripts/test_product.py','--python',binner,'--workflow-python',workflow,
                   '--threads','4','--timeout','1800','--output',a.output/'product'],'installed-product-suite',1900)
            # Retain actual corrupted wheel evidence; require its intended byte failure.
            damaged=a.output/'damaged-wheel.whl'
            with zipfile.ZipFile(wheel) as source,zipfile.ZipFile(damaged,'w') as target:
                for name in source.namelist():target.writestr(name,source.read(name)+(b'\n# damaged' if name=='dl_binner/io.py' else b''))
            inspector=importlib.util.spec_from_file_location('distribution_check',snapshot/'scripts/check_distribution.py')
            module=importlib.util.module_from_spec(inspector);inspector.loader.exec_module(module)
            accepted=json.loads((snapshot/'tests/product/accepted-package.json').read_text())
            try:module.inspect_wheel(damaged,accepted)
            except ValueError as failure:
                if 'RECORD bytes changed' not in str(failure):raise
                write(a.output/'damaged-wheel-check.json',dict(status='passed',intended_failure=str(failure),file=record(damaged)))
            else:raise RuntimeError('Damaged wheel unexpectedly passed')
            stage([bases['build'],'-I','-B',snapshot/'scripts/check_docs.py'],'clean-snapshot-docs')
            status='passed'
        except BaseException as failure:
            error=repr(failure);traceback.print_exc()
        finally:
            elapsed=time.monotonic()-started
            try:
                remaining=deadline-time.monotonic()
                if remaining<=0:raise TimeoutError('No remaining integration clock for final byte checks')
                signal.setitimer(signal.ITIMER_REAL,remaining)
                after={role:library_tree(path) for role,path in bases.items()}
                unchanged=not before or before==after
                if not unchanged:status='failed';error='Accepted base library bytes changed'
                write(a.output/'base-readonly-after.json',dict(bindings=after,unchanged=unchanged))
                if any(record(Path(path))!=entry for path,entry in cache_records.items()):
                    status='failed';error='Read-only cache bytes changed'
            except BaseException as failure:status='failed';error=repr(failure);traceback.print_exc()
            signal.setitimer(signal.ITIMER_REAL,0)
            elapsed=time.monotonic()-started
            receipt=dict(status=status,error=error,source_commit=a.source_commit,protocol=record(PROJECT/'experiments/E007-pr-readiness/protocol.json'),
                seconds=elapsed,local_four_thread_wall_hours=4*elapsed/3600,peak_sampled_stage_rss_bytes=max((v['peak_sampled_rss_bytes'] for v in resources.values()),default=0),
                numerical_threads_max=4,loader_workers=0,resources=resources,platform=platform.platform(),bases={k:str(v) for k,v in bases.items()},
                scope='All serial measured snapshot/setup/build/install/probe/test stages; includes final read-only/hash checks. Source development/acquisition/final review and idle excluded; not UCloud billing.',
                sampled_scope='Stage samples include coordinator; parent hashing between child stages is wall-accounted but not continuously RSS sampled',
                accepted_work_repeated=False,workers_mocked=[])
            write(a.output/'observed.json',receipt)
            print('E007_STATUS='+json.dumps(dict(status=status,error=error,seconds=elapsed,peak_rss=receipt['peak_sampled_stage_rss_bytes']),sort_keys=True),flush=True)
            sys.stdout,sys.stderr=oldout,olderr;signal.signal(signal.SIGALRM,old)
    return 0 if status=='passed' else 1


if __name__=='__main__':raise SystemExit(main())
