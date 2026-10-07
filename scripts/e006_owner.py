#!/usr/bin/env python3
"""Bounded owner-controlled E006 generic-command smoke, with failure returns.

Runs from the checksum-bound packet using stdlib before package setup. Native
Linux is mandatory except for an explicitly named local harness. The accepted
E005 prefixes are probed and byte-bound read-only; only a new versioned package
venv is written. This does not launch E005 science or install dependencies.
"""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import platform
import re
import shutil
import signal
import sys
import tarfile
import tempfile
import time
import traceback

BUNDLE = Path(__file__).absolute().parents[1]
EXP = 'experiments/E006-cli-usability'


def record(path):
    """Hash regular file bytes incrementally; never follow a packet symlink."""
    path = Path(path)
    if path.is_symlink() or not path.is_file():
        raise ValueError('Missing/linked file: '+str(path))
    value = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024*1024), b''):
            value.update(chunk)
    return dict(bytes=path.stat().st_size, sha256=value.hexdigest())


def write(path, data):
    """Exclusively write a small attempt record with real JSON and newlines."""
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x') as stream:
        json.dump(data, stream, indent=2, sort_keys=True, allow_nan=False)
        stream.write('\n')


def verify_bundle(folder):
    """Verify the complete packet inventory, rejecting added/unsafe members."""
    folder = Path(folder).absolute()
    data = json.loads((folder/'bundle-manifest.json').read_text())
    actual = set()
    for path in folder.rglob('*'):
        if path.is_symlink():
            raise ValueError('Linked packet member: '+str(path))
        if path.is_file() and path != folder/'bundle-manifest.json':
            actual.add(str(path.relative_to(folder)))
    if actual != set(data['files']):
        raise ValueError('Packet file set changed')
    for name, expected in data['files'].items():
        path = folder/name
        if Path(name).is_absolute() or '..' in Path(name).parts or not path.resolve().is_relative_to(folder.resolve()):
            raise ValueError('Unsafe packet member: '+name)
        if record(path) != expected:
            raise ValueError('Packet bytes changed: '+name)
    return data


def tree_binding(folder):
    """Bind dependency bytes and relative names, including bytecode already present.

    Finder .DS_Store is ignored as volatile Mac-only metadata. Scientific and
    library files are never excluded. Links are recorded by target and bytes;
    directories are not traversed through links.
    """
    folder = Path(folder)
    files = {}
    for path in sorted(folder.rglob('*')):
        if path.name == '.DS_Store':
            continue
        if path.is_file():
            resolved = path.resolve()
            value = record(resolved)
            if path.is_symlink(): value['link'] = os.readlink(path)
            files[str(path.relative_to(folder))] = value
    digest = hashlib.sha256(json.dumps(files, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
    return dict(root=str(folder), files=len(files), bytes=sum(v['bytes'] for v in files.values()),
                tree_sha256=digest, excluded_metadata=['.DS_Store'])


def link_dependencies(source, destination):
    """Link only reviewed dependencies into a fresh site directory, never old code.

    No system-site/PYTHONPATH overlay or .pth import path injection. Pip itself is
    borrowed read-only solely to install the new no-dependency wheel locally.
    The new package remains owned by destination; its base prefix must persist.
    """
    links = {}
    for path in sorted(Path(source).iterdir()):
        name = path.name
        if name in ('dl_binner', '__pycache__', '.DS_Store') or name.startswith('dl_binner-') or path.suffix == '.pth':
            continue
        target = Path(destination)/name
        if target.exists() or target.is_symlink():
            raise ValueError('New site directory is not fresh: '+str(target))
        target.symlink_to(path.absolute(), target_is_directory=path.is_dir())
        links[name] = str(path.absolute())
    return links


def normalized(distributions):
    """Normalize distribution spellings and reject duplicates before comparison."""
    result = {}
    for name, version in distributions.items():
        key = re.sub(r'[-_.]+', '-', name).lower()
        if key in result: raise ValueError('Duplicate distribution: '+key)
        result[key] = version
    return result


class Tee:
    """Capture readable driver progress, errors and exit codes inside the attempt."""
    def __init__(self, terminal, log): self.terminal, self.log = terminal, log
    def write(self, value): self.terminal.write(value); self.log.write(value); self.flush()
    def flush(self): self.terminal.flush(); self.log.flush()


def execute(args, attempt, manifest, started):
    """Probe read-only assets, install one wheel, run real contracts, verify reuse."""
    spec = json.loads((BUNDLE/EXP/'linux-smoke.json').read_text())
    if args.allocated_vcpus != 4 or args.allocated_ram_gb != 12:
        raise ValueError('Frozen smoke allocation is exactly 4 vCPUs / 12 GB RAM')
    local = json.loads(args.local_runtimes.read_text()) if args.local_runtimes else None
    if not local:
        if platform.system() != 'Linux' or platform.machine() != 'x86_64' or not Path('/proc/self/stat').exists():
            raise RuntimeError('Native Linux x86_64 with /proc required')
        allowed = sorted(os.sched_getaffinity(0))
        if len(allowed) < 4: raise RuntimeError('Effective CPU affinity smaller than four declared CPUs')
        os.sched_setaffinity(0, allowed[:4])
    helper = BUNDLE/'payload/supervision.py'
    module_spec = importlib.util.spec_from_file_location('e006_supervision', helper)
    supervisor = importlib.util.module_from_spec(module_spec); module_spec.loader.exec_module(supervisor)
    env = supervisor.isolated_env(4)
    env.update(TMPDIR=tempfile.mkdtemp(prefix='e006-', dir='/tmp'),
               XDG_CACHE_HOME=str(attempt/'cache'), PIP_DISABLE_PIP_VERSION_CHECK='1')
    deadline = started+spec['execution_seconds_ceiling']
    setup_deadline = started+spec['setup_seconds_ceiling']
    signal.setitimer(signal.ITIMER_REAL, max(.001, setup_deadline-time.monotonic()))
    setting_up = True
    stages = attempt/'stages'; stages.mkdir()
    def stage(command, name, ceiling=120):
        supervisor.progress('Owner stage: '+name)
        remaining = min(deadline, setup_deadline if setting_up else deadline)-time.monotonic()
        if remaining <= 0: raise TimeoutError('Frozen stage/phase ceiling exceeded')
        return supervisor.supervise(command, stages/(name+'.log'), min(ceiling, remaining),
                                    spec['working_rss_bytes_ceiling'], env, sample_root=os.getpid())
    accepted = json.loads((BUNDLE/'runtime-baseline.json').read_text())
    runtime, bindings = {}, {}
    for role in ('binner', 'workflow'):
        expected = local[role] if local else accepted[role]
        python = Path(expected['python']).absolute()  # never resolve a venv interpreter
        cfg = dict(prefix=str(python.parent.parent), dependency_prefix=str(python.parent.parent),
                   role=role, local=bool(local), expected_distributions=expected['distributions'],
                   expected_python=expected['python_version'], expected_origins=expected.get('origins',{}))
        path = attempt/(role+'-probe-config.json'); write(path, cfg)
        stage([python, '-I', '-B', '-S', '-u', BUNDLE/'scripts/e006_runtime.py', path], role+'-entry-probe')
        inv = json.loads(next(line.split('=',1)[1] for line in (stages/(role+'-entry-probe.log')).read_text().splitlines()
                             if line.startswith('INVENTORY_JSON=')))
        stage([python, '-I', '-B', '-m', 'pip', 'check'], role+'-pip-check')
        bindings[role] = tree_binding(inv['site_directory'])
        runtime[role] = dict(python=str(python), inventory=inv, reuse='read-only accepted prefix; no install')
        write(attempt/(role+'-readonly-before.json'), bindings[role])
    write(attempt/'accepted-runtime.json', runtime)
    if time.monotonic()-started >= spec['setup_seconds_ceiling']:
        raise TimeoutError('Frozen setup ceiling exceeded')
    # venv is newly created; the existing interpreter/stdlib/dependencies stay in place.
    env_root = args.root/'envs'; env_root.mkdir(exist_ok=True)
    prefix = Path(tempfile.mkdtemp(prefix='binner-run-0.1.0.dev1-v1-', dir=env_root))/'runtime'
    stage([runtime['binner']['python'], '-I', '-B', '-m', 'venv', '--without-pip', '--symlinks', prefix], 'new-package-venv')
    python = prefix/'bin/python'
    site_path = stages/'new-site.log'
    stage([python, '-I', '-B', '-c', 'import sysconfig; print(sysconfig.get_path("purelib"))'], 'new-site')
    destination = Path(site_path.read_text().splitlines()[0])
    if not destination.is_relative_to(prefix): raise ValueError('New package site outside its prefix')
    links = link_dependencies(runtime['binner']['inventory']['site_directory'], destination)
    write(attempt/'dependency-links.json', dict(prefix=str(prefix), links=links, policy='new Linux venv; explicit read-only dependencies; no old dl_binner/.pth'))
    wheel = BUNDLE/spec['wheel']
    stage([python, '-I', '-B', '-m', 'pip', 'install', '--no-index', '--no-deps', wheel], 'new-wheel-install')
    stage([python, '-I', '-B', '-m', 'pip', 'check'], 'new-wheel-pip-check')
    expected = dict(runtime['binner']['inventory']['distributions'])
    expected = {k:v for k,v in expected.items() if normalized({k:v}) != {'dl-binner':v}}
    expected['dl-binner'] = spec['package_version']
    cfg = dict(prefix=str(prefix), dependency_prefix=str(Path(runtime['binner']['python']).parent.parent),
               role='binner', local=bool(local), expected_distributions=expected,
               expected_python=runtime['binner']['inventory']['python_version'], own_package=True,
               package_files=manifest['package_files'])
    path = attempt/'new-probe-config.json'; write(path, cfg)
    stage([python, '-I', '-B', '-S', '-u', BUNDLE/'scripts/e006_runtime.py', path], 'new-package-probe')
    if time.monotonic()-started >= spec['setup_seconds_ceiling']:
        raise TimeoutError('Frozen setup ceiling exceeded')
    write(attempt/'runtime.json', dict(package_python=str(python), workflow_python=runtime['workflow']['python'], prefix=str(prefix),
          policy='new owned wheel, accepted stdlib/numerical libraries/workflow read-only; source prefix must persist'))
    setting_up = False
    signal.setitimer(signal.ITIMER_REAL, max(.001, deadline-time.monotonic()))
    try:
        stage([python, '-I', '-B', '-u', BUNDLE/'scripts/e006_smoke.py', '--output', attempt/'smoke',
               '--workflow-python', runtime['workflow']['python'], '--bundle', BUNDLE],
              'generic-native-contracts', spec['smoke_seconds_ceiling'])
    finally:
        after = {role:tree_binding(runtime[role]['inventory']['site_directory']) for role in runtime}
        write(attempt/'readonly-after.json', dict(bindings=after, unchanged=after==bindings))
        if after != bindings: raise RuntimeError('Read-only runtime bytes changed; preserve evidence')
    return dict(status='passed', native_linux=not bool(local), package_prefix=str(prefix),
                readonly_dependency_bytes_unchanged=True, source_commit=manifest['source_commit'],
                scope='Generic-command software smoke only; no biological scoring or E005 stages')


def collect(attempt, transfer):
    """Archive all bounded evidence, omit caches/runtimes, never remove an attempt."""
    files = [p for p in sorted(attempt.rglob('*')) if p.is_file() and not p.is_symlink()
             and not any(v in ('cache', 'source-cache', '.snakemake') for v in p.relative_to(attempt).parts)]
    write(attempt/'retained-files.json', dict(files={str(p.relative_to(attempt)):record(p) for p in files
                                               if p.name != 'terminal.log'},
          scope='open terminal and self excluded from inventory; archive checksum binds captured terminal snapshot'))
    archive = transfer/(attempt.name+'-return.tar.gz')
    archived_bytes = 0
    with archive.open('xb') as stream, tarfile.open(fileobj=stream, mode='w:gz') as tar:
        for path in files+[attempt/'retained-files.json']:
            member = tar.gettarinfo(path, arcname=attempt.name+'/'+str(path.relative_to(attempt)))
            with path.open('rb') as source:
                tar.addfile(member, source)
            archived_bytes += member.size
    checksum = archive.with_name(archive.name+'.sha256')
    checksum.write_text(record(archive)['sha256']+'  '+archive.name+'\n')
    print('RETURN_ARCHIVE='+str(archive)+'\nRETURN_CHECKSUM='+str(checksum), flush=True)
    return dict(archive=str(archive), archive_bytes=record(archive), checksum=str(checksum),
                retained_files=len(files)+1, retained_logical_bytes=archived_bytes,
                storage_scope='Exact uncompressed archive members, including inventory and captured terminal snapshot; excludes caches/runtime prefixes')


def main():
    """Cover verification/setup/children with one clock, retain intended failures."""
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root', type=Path, required=True)
    p.add_argument('--allocated-vcpus', type=int, required=True)
    p.add_argument('--allocated-ram-gb', type=float, required=True)
    p.add_argument('--entry-start-epoch', type=float)
    p.add_argument('--local-runtimes', type=Path, help='Explicit Mac harness only; never native Linux credit')
    a = p.parse_args()
    if not a.root.is_absolute(): p.error('--root must be absolute')
    if not a.local_runtimes and a.root != Path('/work/Home/dl_binner/e006'):
        p.error('Owner root must be /work/Home/dl_binner/e006')
    a.root.mkdir(parents=True, exist_ok=True)
    transfer = a.root/'transfer'; transfer.mkdir(exist_ok=True)
    attempt = Path(tempfile.mkdtemp(prefix='generic-linux-smoke-', dir=a.root))
    elapsed_entry = max(0, time.time()-a.entry_start_epoch) if a.entry_start_epoch else 0
    started = time.monotonic()-elapsed_entry
    code, status = 1, dict(status='failed', verification_passed=False, native_linux=False)
    original = sys.stdout, sys.stderr
    handlers = {s:signal.getsignal(s) for s in (signal.SIGALRM, signal.SIGTERM, signal.SIGINT)}
    with (attempt/'terminal.log').open('x') as log:
        sys.stdout, sys.stderr = Tee(original[0], log), Tee(original[1], log)
        def ceiling(signum, frame): raise TimeoutError('Frozen E006 execution/collection ceiling reached')
        def cancel(signum, frame): raise KeyboardInterrupt('Owner cancelled '+str(signum))
        signal.signal(signal.SIGALRM, ceiling)
        signal.signal(signal.SIGTERM, cancel); signal.signal(signal.SIGINT, cancel)
        try:
            spec = json.loads((BUNDLE/EXP/'linux-smoke.json').read_text())
            signal.setitimer(signal.ITIMER_REAL, max(.001, spec['execution_seconds_ceiling']-elapsed_entry))
            # Retain the submitted manifest even if any later byte/prerequisite fails.
            shutil.copyfile(BUNDLE/'bundle-manifest.json', attempt/'bundle-manifest.json')
            manifest = verify_bundle(BUNDLE)
            status['verification_passed'] = True
            write(attempt/'verification.json', dict(passed=True, manifest=record(attempt/'bundle-manifest.json')))
            if shutil.disk_usage(a.root).free < 500000000:
                raise RuntimeError('At least 0.5 GB free required for small new package/evidence; old dependencies reused')
            status = execute(a, attempt, manifest, started)
            status['verification_passed'] = True; code = 0
        except BaseException as error:
            status.update(status='failed', error=repr(error)); traceback.print_exc()
        finally:
            signal.setitimer(signal.ITIMER_REAL, 0)
            elapsed = time.monotonic()-started
            status.update(exit_code=code, allocated_vcpus=a.allocated_vcpus, allocated_ram_gb=a.allocated_ram_gb,
                driver_seconds_before_collection=elapsed, allocated_vcpu_hours_before_collection=a.allocated_vcpus*elapsed/3600,
                entry_before_python_seconds=elapsed_entry, accounting='allocation times entry-to-driver wall; setup included; idle/upload excluded',
                native_linux=not bool(a.local_runtimes) and platform.system()=='Linux',
                host_cpu_count=os.cpu_count(), host_report_is_allocation=False)
            write(attempt/'status.json', status)
            print('DRIVER_STATUS='+json.dumps(status, sort_keys=True), flush=True)
            try:
                signal.setitimer(signal.ITIMER_REAL, 120)
                collected = collect(attempt, transfer)
                elapsed = time.monotonic()-started
                collected.update(driver_seconds_through_collection=elapsed,
                                 allocated_vcpu_hours_through_collection=a.allocated_vcpus*elapsed/3600,
                                 status=status['status'], exit_code=code)
                write(transfer/(attempt.name+'-collection.json'), collected)
                print('COLLECTION_STATUS='+json.dumps(collected, sort_keys=True), flush=True)
            except BaseException:
                traceback.print_exc(); code = 1
            signal.setitimer(signal.ITIMER_REAL, 0)
            for sig, handler in handlers.items(): signal.signal(sig, handler)
            sys.stdout, sys.stderr = original
    return code


if __name__ == '__main__': raise SystemExit(main())
