#!/usr/bin/env python3
"""Owner-controlled offline CPU/Linux smoke; prepare returns even after failures.

Validate the checksum-bound bundle, create/reprobe separate persistent CPU and
workflow prefixes, run the actual installed CLI DAG and failure/resume contracts,
then stop for returned-evidence review. There is no pilot-launch mode. A named
local harness bypasses only Linux/bootstrap; it never mocks a binner worker.
"""
import argparse
import copy
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import platform
import re
import shutil
import signal
import subprocess
import sys
import tarfile
import tempfile
import time
import traceback

sys.path.insert(0, str(Path(__file__).resolve().parent))
from e005_smoke import progress, run, sha, write

BUNDLE = Path(__file__).resolve().parents[1]


def verify_bundle(folder):
    """Verify every staged source/input/runtime payload against the frozen manifest."""
    manifest = json.loads((Path(folder)/'bundle-manifest.json').read_text())
    for name, entry in manifest['files'].items():
        path = Path(folder)/name
        if not path.resolve().is_relative_to(Path(folder).resolve()) or not path.is_file() or path.is_symlink():
            raise ValueError('Unsafe/missing bundle member: '+name)
        if sha(path) != entry['sha256'] or path.stat().st_size != entry['bytes']:
            raise ValueError('Bundle byte mismatch: '+name)
    return manifest


def unpack_python(archive, prefix):
    """Install a fresh standalone distribution, never relocate an executed prefix.

    Strip its python/ packaging root. Skip the unused bundled terminfo database
    (its case aliases collide on common Mac filesystems); both owner and harness
    use this same policy. Keep interpreter/libraries/licenses unchanged. Reject
    traversals, outside links, devices and writes through links.
    """
    prefix = Path(prefix)
    prefix.mkdir(exist_ok=False)
    with tarfile.open(archive, 'r:gz') as tar:
        members = []
        for source in tar.getmembers():
            parts = PurePosixPath(source.name).parts
            if not parts or parts[0] != 'python' or '..' in parts:
                raise ValueError('Unexpected Python archive path')
            if len(parts) == 1:
                continue
            if parts[1:3] == ('share', 'terminfo'):
                continue
            member = copy.copy(source)
            member.name = '/'.join(parts[1:])
            target = prefix/member.name
            if not target.resolve().is_relative_to(prefix.resolve()):
                raise ValueError('Outside Python archive target')
            if member.islnk():
                lp = PurePosixPath(member.linkname).parts
                if not lp or lp[0] != 'python' or '..' in lp:
                    raise ValueError('Unsafe Python hardlink')
                member.linkname = '/'.join(lp[1:])
                link = prefix/member.linkname
            elif member.issym():
                if PurePosixPath(member.linkname).is_absolute():
                    raise ValueError('Absolute Python symlink')
                link = target.parent/member.linkname
            elif not (member.isfile() or member.isdir()):
                raise ValueError('Special Python archive member')
            else:
                link = target
            if not link.resolve().is_relative_to(prefix.resolve()):
                raise ValueError('Outside Python link')
            members.append(member)
        for member in members:
            target = prefix/member.name
            if not target.parent.resolve().is_relative_to(prefix.resolve()):
                raise ValueError('Archive writes through an outside link')
            tar.extract(member, prefix)


def isolated_env(threads):
    """Clear inherited Python/user-site paths and reconcile serial CPU pool limits."""
    env = os.environ.copy()
    for name in ('PYTHONPATH', 'PYTHONHOME', 'PYTHONUSERBASE'):
        env.pop(name, None)
    env.update(PYTHONNOUSERSITE='1', PYTHONDONTWRITEBYTECODE='1', PIP_DISABLE_PIP_VERSION_CHECK='1')
    for name in ('OMP_NUM_THREADS', 'MKL_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'VECLIB_MAXIMUM_THREADS', 'NUMEXPR_NUM_THREADS'):
        env[name] = str(threads)
    return env


class Tee:
    """Mirror owner progress/errors into an attempt-local terminal log."""
    def __init__(self, terminal, log):
        self.terminal, self.log = terminal, log

    def write(self, value):
        self.terminal.write(value)
        self.log.write(value)
        self.flush()

    def flush(self):
        self.terminal.flush()
        self.log.flush()


def execute(args, attempt, manifest):
    """Set up or read-only reuse runtimes, then execute only the bounded smoke."""
    started = time.monotonic()
    spec = json.loads((BUNDLE/'experiments/E005-linux-pilot/smoke.json').read_text())
    if not 1 <= args.allocated_vcpus <= 4 or args.allocated_ram_gb < 12:
        raise ValueError('Smoke requires explicit 1–4 allocated vCPUs and at least 12 GB RAM')
    threads = args.allocated_vcpus
    if not args.local_binner_python:
        if platform.system() != 'Linux' or platform.machine() != 'x86_64':
            raise RuntimeError('Owner entry point requires Linux x86_64')
        if not Path('/proc/self/stat').is_file():
            raise RuntimeError('Linux /proc sampling unavailable')
        allowed = sorted(os.sched_getaffinity(0))
        if len(allowed) < threads:
            raise RuntimeError('Effective cpuset smaller than declared allocation')
        os.sched_setaffinity(0, allowed[:threads])
    env = isolated_env(threads)
    env['TMPDIR'] = tempfile.mkdtemp(prefix='e005-', dir='/tmp')  # short Unix-socket-safe job-local path
    env['MPLCONFIGDIR'] = str(attempt/'mpl-cache')
    env['XDG_CACHE_HOME'] = str(attempt/'cache')
    receipts = []
    setting_up = True

    def stage(command, name, ceiling):
        remaining = spec['total_seconds_ceiling']-(time.monotonic()-started)
        if setting_up:
            remaining = min(remaining, spec['setup_seconds_ceiling']-(time.monotonic()-started))
        if remaining <= 0:
            raise TimeoutError('Total smoke ceiling exceeded')
        result = run(command, attempt/'stages', name, min(ceiling, remaining),
                     spec['ram_bytes_ceiling'], threads, env)
        receipts.append(dict(name=name, **result))
        return result

    runtime = {}
    for role in ('binner', 'workflow'):
        completion = None
        supplied = args.local_binner_python if role == 'binner' else args.local_workflow_python
        if supplied:
            prefix = Path(supplied).absolute().parent.parent
            python = Path(supplied).absolute()
            reuse = 'explicit local harness; Linux/bootstrap not tested'
        else:
            lock = BUNDLE/f'experiments/E005-linux-pilot/{role}-linux.lock'
            python_payload = BUNDLE/'payload'/spec['python_payload']
            fingerprint = hashlib.sha256((sha(lock)+sha(python_payload)+spec['installation_policy']).encode()).hexdigest()
            registry = args.root/'envs'/(role+'-'+fingerprint[:16]+'.json')
            registry.parent.mkdir(parents=True, exist_ok=True)
            if registry.exists():
                record = json.loads(registry.read_text())
                if record['fingerprint'] != fingerprint:
                    raise ValueError('Environment completion fingerprint mismatch')
                prefix = Path(record['prefix'])
                if not prefix.is_relative_to(args.root/'envs'):
                    raise ValueError('Unexpected persistent prefix')
                python, reuse = prefix/'bin/python3', 'completed prefix reprobed, no installation'
            else:
                prefix = Path(tempfile.mkdtemp(prefix=role+'-cpu-v1-', dir=args.root/'envs'))/'runtime'
                unpack_python(python_payload, prefix)
                python, reuse = prefix/'bin/python3', 'fresh isolated offline prefix'
                stage([python, '-I', '-S', '-u', '-c', 'import sys; print("before_ssl",sys.version,sys.prefix,flush=True); import ssl; print(ssl.OPENSSL_VERSION,flush=True)'], role+'-interpreter', 60)
                stage([python, '-I', '-m', 'pip', 'install', '--no-index', '--no-deps', '--require-hashes',
                       '--find-links', BUNDLE/f'payload/{role}-wheels', '-r', lock], role+'-install', spec['setup_seconds_ceiling'])
                stage([python, '-I', '-m', 'pip', 'check'], role+'-pip-check', 60)
                completion = (registry, dict(prefix=str(prefix), fingerprint=fingerprint,
                              lock_sha256=sha(lock), source_bundle_commit=manifest['source_commit']))
        stage([python, '-I', '-m', 'pip', 'check'], role+'-entry-pip-check', 60)
        stage([python, '-I', '-S', '-u', BUNDLE/'scripts/e005_probe.py', prefix, role, threads,
               'local' if supplied else 'linux'], role+'-probe', 120)
        log = (attempt/'stages'/(role+'-probe.log')).read_text()
        inventory = json.loads(next(l.split('=', 1)[1] for l in log.splitlines() if l.startswith('INVENTORY_JSON=')))
        if not supplied:
            normalize = lambda name: re.sub(r'[-_.]+', '-', name).lower()
            expected = dict(line.split(' --hash=', 1)[0].split('==') for line in lock.read_text().splitlines()
                            if line and not line.startswith('#'))
            observed = {normalize(k): v for k, v in inventory['distributions'].items()}
            if expected != observed or inventory['python'].split()[0] != '3.12.10':
                raise ValueError('Native prefix inventory differs from frozen exact-wheel lock')
        if role == 'binner':
            code_root = Path(inventory['origins']['dl_binner']).parent
            for name, value in spec['package_code_sha256'].items():
                if sha(code_root/name) != value:
                    raise ValueError('Installed accepted package source mismatch: '+name)
        elif inventory['distributions'].get('snakemake') != '9.16.3':
            raise ValueError('Pinned workflow version mismatch')
        if completion:
            write(*completion)
        runtime[role] = dict(python=str(python), reuse=reuse, inventory=inventory)
    write(attempt/'runtime.json', runtime)
    pilot = json.loads((BUNDLE/'experiments/E005-linux-pilot/pilot.json').read_text())
    locators = [pilot['sources']['retained_source_fasta_ucloud'],
                *[s['reads'] for s in pilot['samples']],
                '/work/Home/dl_binner/e001/e001-gate0/envs/amber/bin/python',
                '/work/Home/dl_binner/e001/e001-gate0/sources/AMBER_evaluation/cami_amber/binning_classes.py']
    write(attempt/'pilot-asset-locators.json', dict(
          files={name: dict(exists=Path(name).is_file(), bytes=Path(name).stat().st_size if Path(name).is_file() else None)
                 for name in locators}, scope='read-only existence/size inventory, not byte acceptance or pilot execution'))
    setting_up = False
    config = copy.deepcopy(spec['workflow'])
    for key in ('fasta', 'depth', 'training', 'tnf_cache', 'tnf_receipt', 'tnf_panel', 'fresh_fasta'):
        config[key] = str(BUNDLE/config[key])
    config.update(python=runtime['binner']['python'], threads=threads,
                  resolved_config=str(attempt/'resolved-config.json'))
    write(attempt/'resolved-config.json', config)
    smoke = attempt/'smoke'
    smoke.mkdir()
    command = [runtime['workflow']['python'], '-I', '-m', 'snakemake', '--snakefile',
               str(BUNDLE/'workflows/first-binner/linux_smoke.smk'), '--configfile', str(attempt/'resolved-config.json'),
               '--directory', str(smoke), '--cores', str(threads), '--jobs', '1', '--resources', 'mem_mb=8000',
               '--scheduler', 'greedy',
               '--benchmark-extended', '--runtime-source-cache-path', str(attempt/'source-cache'),
               '--keep-incomplete', '--printshellcmds', '--latency-wait', '2']
    stage(command, 'native-smoke', spec['smoke_seconds_ceiling'])
    stage(command+['--dry-run'], 'completed-resume', 60)
    if 'Nothing to be done' not in (attempt/'stages/completed-resume.log').read_text():
        raise RuntimeError('Completed smoke unexpectedly schedules work')
    # Fail actual package adapters, not a replacement worker. The expectation
    # checker converts only the expected nonzero exit into contract success.
    stage([runtime['binner']['python'], '-I', '-u', BUNDLE/'scripts/e005_failure_checks.py',
           config['fasta'], config['depth'], smoke/'checkpoint.pt', smoke/'features.npz',
           attempt/'failure-checks', threads], 'fatal-input-contracts', 60)
    return dict(status='passed', native_linux=not bool(args.local_binner_python),
                source_commit=manifest['source_commit'], allocated_vcpus=threads,
                allocated_ram_gb=args.allocated_ram_gb, loader_workers=0, serial=True,
                affinity=sorted(os.sched_getaffinity(0)) if hasattr(os, 'sched_getaffinity') else None,
                host_report=dict(platform=platform.platform(), cpu_count=os.cpu_count(),
                                 scope='host report is not allocated CPUs/RAM'),
                stages=receipts, scope='deployment software smoke only; pilot not launched')


def collect(attempt):
    """Collect bounded attempt evidence, excluding runtimes/payload/cache duplication."""
    archive = attempt.parent/(attempt.name+'-return.tar.gz')
    files = [p for p in sorted(attempt.rglob('*')) if p.is_file() and not p.is_symlink()
             and not any(part in ('cache', 'source-cache', 'mpl-cache') for part in p.relative_to(attempt).parts)]
    write(attempt/'retained-files.json', dict(files=[dict(path=str(p.relative_to(attempt)),
          sha256=sha(p), bytes=p.stat().st_size) for p in files if p.name != 'terminal.log'],
          scope='terminal is still open at this snapshot; archive binds its later bytes'))
    with tarfile.open(archive, 'w:gz') as tar:
        for path in files+[attempt/'retained-files.json']:
            tar.add(path, arcname=attempt.name+'/'+str(path.relative_to(attempt)), recursive=False)
    checksum = archive.with_name(archive.name+'.sha256')
    checksum.write_text(sha(archive)+'  '+archive.name+'\n')
    progress('return_ready', archive=str(archive), checksum=str(checksum), bytes=archive.stat().st_size)


def main():
    """Create a unique retained attempt; global failures stop smoke and still collect."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, required=True)
    parser.add_argument('--allocated-vcpus', type=int, required=True)
    parser.add_argument('--allocated-ram-gb', type=float, required=True)
    parser.add_argument('--local-binner-python', type=Path)
    parser.add_argument('--local-workflow-python', type=Path)
    args = parser.parse_args()
    if not args.root.is_absolute() or bool(args.local_binner_python) != bool(args.local_workflow_python):
        parser.error('Absolute root and both/none explicit local runtimes required')
    args.root.mkdir(parents=True, exist_ok=True)
    attempt = Path(tempfile.mkdtemp(prefix='linux-smoke-', dir=args.root))
    started, status, code = time.monotonic(), {}, 1
    terminal_out, terminal_err = sys.stdout, sys.stderr
    with (attempt/'terminal.log').open('x') as log:
        sys.stdout = Tee(terminal_out, log)
        sys.stderr = Tee(terminal_err, log)
        handlers = {sig: signal.getsignal(sig) for sig in (signal.SIGINT, signal.SIGTERM)}
        def cancelled(signum, frame):
            raise KeyboardInterrupt('Owner signal '+str(signum))
        for sig in handlers:
            signal.signal(sig, cancelled)
        alarm_handler = signal.getsignal(signal.SIGALRM)
        def budget_exceeded(signum, frame):
            raise TimeoutError('Total owner-driver ceiling exceeded')
        signal.signal(signal.SIGALRM, budget_exceeded)
        try:
            # Cover parent-side verification/extraction as well as child stages.
            limits = json.loads((BUNDLE/'experiments/E005-linux-pilot/smoke.json').read_text())
            signal.setitimer(signal.ITIMER_REAL, limits['total_seconds_ceiling'])
            manifest = verify_bundle(BUNDLE)
            write(attempt/'bundle-manifest.json', manifest)
            if shutil.disk_usage(args.root).free < 4*10**9:
                raise RuntimeError('At least 4 GB free required for new smoke runtimes/evidence')
            status = execute(args, attempt, manifest)
            code = 0
        except BaseException as error:
            status = dict(status='failed', error=repr(error), pilot_launched=False)
            traceback.print_exc()
        finally:
            # Preserve bounded evidence collection even after an execution timeout.
            signal.setitimer(signal.ITIMER_REAL, 0)
            signal.signal(signal.SIGALRM, alarm_handler)
            elapsed = time.monotonic()-started
            status.update(driver_seconds_before_collection=elapsed,
                          allocated_vcpus=args.allocated_vcpus, allocated_ram_gb=args.allocated_ram_gb,
                          allocated_vcpu_hours_before_collection=args.allocated_vcpus*elapsed/3600,
                          accounting='declared allocation times complete driver wall, setup included; excludes owner idle/upload')
            write(attempt/'status.json', status)
            progress('driver_end', **status)
            try:
                collect(attempt)
                elapsed = time.monotonic()-started
                progress('cost_through_collection', driver_seconds=elapsed,
                         allocated_vcpu_hours=args.allocated_vcpus*elapsed/3600)
            except BaseException:
                traceback.print_exc()
                code = 1
            for sig, handler in handlers.items():
                signal.signal(sig, handler)
            sys.stdout, sys.stderr = terminal_out, terminal_err
    return code


if __name__ == '__main__':
    raise SystemExit(main())
