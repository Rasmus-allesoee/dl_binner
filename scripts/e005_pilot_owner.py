#!/usr/bin/env python3
"""Owner-run E005 GI pilot using accepted runtimes/assets, with bounded fail-fast DAG.

Never install or repair an environment, rerun the accepted smoke or execute other
studies. Reprobe read-only prefixes and pinned input/source contracts, then run
the frozen pilot in a unique attempt. Returns/logs stay inside transfer/. An
explicit local fixture overrides data/platform only, retaining the real workers.
"""
import argparse
import copy
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

sys.path.insert(0, str(Path(__file__).resolve().parent))
from e005_owner import Tee, isolated_env, local_scheduler_options, verify_bundle
from e005_smoke import progress, run, sha, write

BUNDLE = Path(__file__).resolve().parents[1]
EXP = 'experiments/E005-linux-pilot/'


def collect(attempt, transfer):
    """Return bounded evidence, hash inventory all files and retain heavy native assets.

    FASTQs, original SAM and sorted BAM remain in the attempt and have hashes and
    byte counts in the inventory/receipts. Include their headers, commands, logs,
    selection IDs, depths, arrays/checkpoint, all exports and native evaluations.
    """
    files = [p for p in sorted(attempt.rglob('*')) if p.is_file() and not p.is_symlink()
             and not any(part in ('cache', 'mpl-cache', 'source-cache') for part in p.relative_to(attempt).parts)]
    def heavy(p):
        return p.suffix in ('.fq', '.bam') or (p.parent.name == 'mapping' and p.name.endswith('.sam') and '.header.' not in p.name)
    inventory = dict(files=[dict(path=str(p.relative_to(attempt)), sha256=sha(p), bytes=p.stat().st_size,
                                 in_return=not heavy(p)) for p in files if p.name != 'terminal.log'],
                     scope='open terminal and this inventory excluded from their own snapshot; heavy native files stay in attempt')
    write(attempt/'retained-files.json', inventory)
    archive = transfer/(attempt.name+'-return.tar.gz')
    with archive.open('xb') as stream, tarfile.open(fileobj=stream, mode='w:gz') as tar:
        for p in [p for p in files if not heavy(p)]+[attempt/'retained-files.json']:
            tar.add(p, arcname=attempt.name+'/'+str(p.relative_to(attempt)), recursive=False)
    checksum = archive.with_name(archive.name+'.sha256')
    with checksum.open('x') as stream:
        stream.write(sha(archive)+'  '+archive.name+'\n')
    progress('return_ready', archive=str(archive), checksum=str(checksum), bytes=archive.stat().st_size,
             retained_files=len(inventory['files']), retained_bytes=sum(e['bytes'] for e in inventory['files']),
             heavy_files=[e for e in inventory['files'] if not e['in_return']])


def inventory_from_log(path):
    """Read the child-emitted inventory, preserving pre-site progress separately."""
    lines = Path(path).read_text().splitlines()
    return json.loads(next(l.split('=', 1)[1] for l in lines if l.startswith('INVENTORY_JSON=')))


def normalize_distribution_name(name):
    """Apply pip's normalized spelling for package names used in lock comparisons."""
    return re.sub(r'[-_.]+', '-', name).lower()


def readonly_python(python, *args):
    """Build an isolated Python command that cannot write bytecode to reused prefixes."""
    return [str(python), '-I', '-B', *args]


def parse_amber_lock(text):
    """Parse the exact-pinned and direct-reference entries in the retained pip freeze."""
    pinned, direct = {}, {}
    for number, raw in enumerate(text.splitlines(), 1):
        line = raw.strip()
        if not line or line.startswith('#'):
            continue
        if ' @ ' in line:
            name, url = line.split(' @ ', 1)
            destination = direct
            value = url
        elif '==' in line:
            name, value = line.split('==', 1)
            destination = pinned
        else:
            raise ValueError(f'Unsupported AMBER lock entry on line {number}: {line}')
        name = normalize_distribution_name(name.strip())
        value = value.strip()
        if not name or not value or name in pinned or name in direct:
            raise ValueError(f'Invalid or duplicate AMBER lock entry on line {number}: {line}')
        destination[name] = value
    return pinned, direct


def reconcile_amber_inventory(lock_text, lock_sha256, observed, policy):
    """Match the live prefix to a clean baseline and reconcile the noisy legacy lock.

    The exact lock hash binds the original file. Its four known user-site-only
    entries are excluded, and its direct references resolve against the complete
    clean-prefix inventory preserved by E001's environment review.
    """
    expected_hash = policy['pip_freeze_sha256']
    if lock_sha256 != expected_hash:
        raise ValueError(f"Retained E001 AMBER lock SHA mismatch: expected {expected_hash}, observed {lock_sha256}")
    pinned, direct = parse_amber_lock(lock_text)
    outside = {normalize_distribution_name(k): v for k, v in policy['outside_prefix_entries'].items()}
    direct_versions = {normalize_distribution_name(k): v
                       for k, v in policy['direct_reference_versions'].items()}
    if set(pinned) & set(direct):
        raise ValueError('AMBER lock repeats a package as both a pin and direct reference')
    if not set(outside).issubset(pinned):
        raise ValueError('Invalid AMBER outside-prefix reconciliation policy')
    for name, version in outside.items():
        if pinned.get(name) != version:
            raise ValueError(f'AMBER lock exception differs from reviewed user-site entry: {name}')
    if set(direct) != set(direct_versions):
        raise ValueError('AMBER lock direct-reference package names differ from the reviewed set')

    inventory_record = policy['verified_prefix_inventory']
    baseline = {}
    for name, version in inventory_record['distributions'].items():
        normalized = normalize_distribution_name(name)
        if normalized in baseline:
            raise ValueError(f'Duplicate normalized baseline AMBER distribution: {normalized}')
        baseline[normalized] = version
    lock_inventory = {name: version for name, version in pinned.items() if name not in outside}
    lock_inventory.update(direct_versions)
    lock_missing = sorted(set(baseline)-set(lock_inventory))
    lock_unexpected = sorted(set(lock_inventory)-set(baseline))
    lock_versions = {name: {'expected_clean_prefix': baseline[name], 'from_lock': lock_inventory[name]}
                     for name in sorted(set(baseline) & set(lock_inventory))
                     if baseline[name] != lock_inventory[name]}
    if lock_missing or lock_unexpected or lock_versions:
        raise ValueError('AMBER lock does not reconcile with the reviewed clean-prefix inventory: '+json.dumps(
            dict(missing=lock_missing, unexpected=lock_unexpected, versions=lock_versions), sort_keys=True))

    actual = {}
    for name, version in observed.items():
        normalized = normalize_distribution_name(name)
        if normalized in actual:
            raise ValueError(f'Duplicate normalized AMBER distribution name: {normalized}')
        actual[normalized] = version
    missing = sorted(set(baseline)-set(actual))
    unexpected = sorted(set(actual)-set(baseline))
    mismatched = {name: {'expected': baseline[name], 'observed': actual[name]}
                  for name in sorted(set(baseline) & set(actual)) if baseline[name] != actual[name]}
    if missing or unexpected or mismatched:
        raise ValueError('AMBER isolated inventory mismatch: '+json.dumps(
            dict(missing=missing, unexpected=unexpected, versions=mismatched), sort_keys=True))
    return dict(status='passed', pip_freeze_sha256=lock_sha256,
                isolated_distributions=len(actual),
                verified_inventory_member_sha256=inventory_record['source_member_sha256'],
                excluded_outside_prefix_lock_entries=outside,
                direct_reference_resolved_versions=direct_versions)


def audit_amber_inventory(attempt, lock_record, observed, policy):
    """Persist the actual lock and inventory before validating their relationship."""
    receipt = dict(amber=dict(inventory=observed, original_lock=lock_record,
                              reconciliation_policy=policy))
    path = Path(attempt)/'runtime-preflight.json'
    write(path, receipt)
    try:
        result = reconcile_amber_inventory(lock_record['text'], lock_record['sha256'],
                                           observed, policy)
    except ValueError as error:
        write(Path(attempt)/'runtime-preflight-check.json',
              dict(status='failed', error=str(error)))
        raise
    write(Path(attempt)/'runtime-preflight-check.json', result)
    return result


def execute(args, attempt, manifest, started):
    """Reprobe runtimes and native contracts; run one serial prospectively capped pilot."""
    spec = json.loads((BUNDLE/EXP/'pilot.json').read_text())
    limits = spec['resources']
    if args.allocated_vcpus != 4 or args.allocated_ram_gb < 12:
        raise ValueError('This first pilot command requires explicit 4-vCPU / at-least-12-GB allocation')
    local = json.loads(args.local_fixture.read_text()) if args.local_fixture else None
    if not local:
        if platform.system() != 'Linux' or platform.machine() != 'x86_64' or not Path('/proc/self/stat').is_file():
            raise RuntimeError('Linux x86_64 and /proc required')
        allowed = sorted(os.sched_getaffinity(0))
        if len(allowed) < 4:
            raise RuntimeError('Effective cpuset smaller than declared allocation')
        os.sched_setaffinity(0, allowed[:4])
    env = isolated_env(4)
    env.update(TMPDIR=tempfile.mkdtemp(prefix='e005-p-', dir='/tmp'),
               MPLCONFIGDIR=str(attempt/'mpl-cache'), XDG_CACHE_HOME=str(attempt/'cache'))
    receipts, setting_up = [], True

    def stage(command, name, ceiling):
        remaining = limits['total_driver_seconds_ceiling']-(time.monotonic()-started)
        if setting_up:
            remaining = min(remaining, limits['setup_seconds_ceiling']-(time.monotonic()-started))
        if remaining <= 0:
            raise TimeoutError('Frozen overall/setup ceiling exceeded')
        result = run(command, attempt/'stages', name, min(ceiling, remaining),
                     limits['working_rss_bytes_ceiling'], 4, env)
        receipts.append(dict(name=name, **result))

    accepted = json.loads((BUNDLE/EXP/'linux-observed.json').read_text())
    smoke = json.loads((BUNDLE/EXP/'smoke.json').read_text())
    runtime = {}
    for role in ('binner', 'workflow'):
        python = Path(local[role+'_python'] if local else accepted['runtime'][role]['python'])
        prefix = python.parent.parent
        if not local and not prefix.is_relative_to(args.root/'envs'):
            raise ValueError('Accepted runtime outside this E005 root')
        stage(readonly_python(python, '-m', 'pip', 'check'), role+'-pip-check', 60)
        stage(readonly_python(python, '-S', '-u', BUNDLE/'scripts/e005_probe.py', prefix, role, '4',
               'local' if local else 'linux'), role+'-probe', 120)
        inv = inventory_from_log(attempt/'stages'/(role+'-probe.log'))
        if not local:
            expected = {normalize_distribution_name(k): v for k, v in accepted['runtime'][role]['inventory']['distributions'].items()}
            actual = {normalize_distribution_name(k): v for k, v in inv['distributions'].items()}
            if actual != expected or inv['python'].split()[0] != '3.12.10':
                raise ValueError('Accepted runtime inventory changed')
        if role == 'binner':
            code = Path(inv['origins']['dl_binner']).parent
            if any(sha(code/name) != value for name, value in smoke['package_code_sha256'].items()):
                raise ValueError('Accepted installed binner source changed')
        elif inv['distributions'].get('snakemake') != '9.16.3':
            raise ValueError('Wrong workflow version')
        runtime[role] = dict(python=str(python), inventory=inv, reuse='read-only current probe; no install')
    external = json.loads((BUNDLE/EXP/'external-runtime.json').read_text())
    mapping = Path(local['mapping_prefix'] if local else external['mapping']['prefix'])
    binaries = {name: mapping/'bin'/name for name in ('strobealign', 'samtools')}
    for name, binary in binaries.items():
        if not binary.resolve().is_relative_to(mapping.resolve()):
            raise ValueError('Native executable outside accepted mapping prefix')
        stage([binary, '--version'], name+'-version', 60)
        first = (attempt/'stages'/(name+'-version.log')).read_text().splitlines()[0]
        actual = first.split()[1] if name == 'samtools' else first.split()[-1].lstrip('v')
        if actual != external['mapping']['versions'][name]:
            raise ValueError('Native tool version mismatch')
    amber = Path(local['amber_python'] if local else external['amber']['prefix']+'/bin/python')
    amber_source = Path(local['amber_source'] if local else external['amber']['source'])
    stage(readonly_python(amber, '-m', 'pip', 'check'), 'amber-pip-check', 60)
    stage(readonly_python(amber, '-S', '-u', BUNDLE/'scripts/e005_external_probe.py', amber.parent.parent, amber_source,
           BUNDLE/EXP/'external-runtime.json', 'local' if local else 'linux'), 'amber-probe', 120)
    amber_inv = inventory_from_log(attempt/'stages/amber-probe.log')
    original_locks = {}
    amber_lock_reconciliation = None
    if not local:
        e001 = mapping.parent.parent
        for role in ('mapping', 'amber'):
            lock = e001/'locks'/role/'pip-freeze.txt'
            if not lock.is_file():
                raise ValueError('Retained E001 provenance lock missing: '+str(lock))
            original_locks[role] = dict(path=str(lock), sha256=sha(lock), text=lock.read_text())
        policy = external['amber']['lock_reconciliation']
        amber_lock_reconciliation = audit_amber_inventory(
            attempt, original_locks['amber'], amber_inv['distributions'], policy)
    runtime.update(mapping=dict(prefix=str(mapping), versions=external['mapping']['versions'],
                                binaries={k: dict(path=str(v), sha256=sha(v)) for k, v in binaries.items()}),
                   amber=dict(python=str(amber), inventory=amber_inv,
                              lock_reconciliation=amber_lock_reconciliation,
                              reuse='read-only; no source or prefix writes'),
                   original_e001_locks=original_locks)
    write(attempt/'runtime.json', runtime)
    cfg = dict(fasta=str(BUNDLE/'input/pilot/assembly.fna'), contigs=str(BUNDLE/EXP/'pilot-contigs.tsv'),
        samples=copy.deepcopy(spec['samples']), columns=spec['mean_depth']['columns'],
        sampled_pairs=spec['reads']['sampled_pairs_per_sample'], max_source_pairs=spec['reads']['max_source_pairs'],
        training=str(BUNDLE/'experiments/E004-first-binner/training.json'), threads=4, loader_workers=0,
        rss_bytes=limits['working_rss_bytes_ceiling'], python=runtime['binner']['python'],
        amber_python=str(amber), amber_source=str(amber_source),
        strobealign=str(binaries['strobealign']), samtools=str(binaries['samtools']),
        resolved_config=str(attempt/'resolved-config.json'), rule_receipts=str(attempt/'rules'),
        role=spec['role'], source_commit=manifest['source_commit'])
    if local:
        for key in ('fasta', 'contigs', 'samples', 'sampled_pairs', 'max_source_pairs', 'role'):
            cfg[key] = local[key]
        write(attempt/'local-fixture.json', local)
    else:
        meta = json.loads((BUNDLE/EXP/'pilot-inputs.json').read_text())
        if sha(cfg['fasta']) != meta['fasta_sha256'] or sha(cfg['contigs']) != meta['contig_manifest_sha256']:
            raise ValueError('Frozen reference/contig-manifest byte mismatch')
    for sample in cfg['samples']:
        if not Path(sample['reads']).is_file():
            raise ValueError('Retained source reads missing: '+sample['reads'])
    write(attempt/'resolved-config.json', cfg)
    # Tiny real input/native flag/API checks address changed adapters, not a repeat
    # of the accepted Linux model smoke. A failure blocks science immediately.
    stage(readonly_python(cfg['python'], '-u', BUNDLE/'experiments/E005-linux-pilot/native_contracts.py',
           '--mapping-prefix', mapping, '--amber-python', amber, '--amber-source', amber_source,
           '--root', attempt/'adapter-contracts'), 'adapter-contracts', 300)
    setting_up = False
    work = attempt/'pilot'; work.mkdir()
    command = [runtime['workflow']['python'], '-I', '-B', '-m', 'snakemake', '--snakefile',
        BUNDLE/'workflows/first-binner/gi_pilot.smk', '--configfile', attempt/'resolved-config.json',
        '--directory', work, *local_scheduler_options(4),
        '--benchmark-extended', '--runtime-source-cache-path', attempt/'source-cache',
        '--keep-incomplete', '--printshellcmds', '--latency-wait', '2']
    science_start = time.monotonic()
    reused = {}
    if local and local.get('preprocess_first'):
        # Exercise a real partial-DAG recovery in the same workdir, not a mocked
        # extractor or guessed copy. Production launches the complete DAG once.
        stage(command+['mean-depth.tsv'], 'partial-preprocess', limits['science_seconds_ceiling'])
        for part in ('reads', 'mapping', 'depth'):
            for path in (work/part).rglob('*'):
                if path.is_file():
                    reused[str(path.relative_to(work))] = dict(sha256=sha(path), mtime_ns=path.stat().st_mtime_ns)
        for path in (work/'mean-depth.tsv', work/'mean-depth.depth.json'):
            reused[str(path.relative_to(work))] = dict(sha256=sha(path), mtime_ns=path.stat().st_mtime_ns)
        write(attempt/'partial-reuse-before.json', reused)
    stage(command, 'gi-pilot', limits['science_seconds_ceiling']-(time.monotonic()-science_start))
    if reused:
        for name, entry in reused.items():
            path = work/name
            if sha(path) != entry['sha256'] or path.stat().st_mtime_ns != entry['mtime_ns']:
                raise RuntimeError('Partial recovery reran/changed completed adapter: '+name)
        write(attempt/'partial-reuse-verified.json', dict(status='completed', files=len(reused),
              source='same workdir, actual manifest consumers; hashes and nanosecond mtimes unchanged'))
    stage(command+['--dry-run'], 'completed-resume', 60)
    if 'Nothing to be done' not in (attempt/'stages/completed-resume.log').read_text():
        raise RuntimeError('Completed pilot schedules work again')
    bytes_retained = sum(p.stat().st_size for p in attempt.rglob('*') if p.is_file() and not p.is_symlink())
    return dict(status='passed', native_linux=not bool(local), source_commit=manifest['source_commit'],
        stages=receipts, allocated_vcpus=4, allocated_ram_gb=args.allocated_ram_gb, loader_workers=0, serial=True,
        affinity=sorted(os.sched_getaffinity(0)) if hasattr(os, 'sched_getaffinity') else None,
        role=cfg['role'], working_bytes=bytes_retained,
        storage_review_exceeded=bytes_retained > limits['new_working_storage_review_gb']*10**9,
        scientific_results={mode: json.loads((work/(mode+'.evaluation/evaluation.json')).read_text()) for mode in ('raw', 'learned')},
        scope='software success does not require superiority; scientific interpretation awaits returned review')


def main():
    """Preserve unique attempts and failure evidence; parent deadline covers verification."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, required=True)
    parser.add_argument('--allocated-vcpus', type=int, required=True)
    parser.add_argument('--allocated-ram-gb', type=float, required=True)
    parser.add_argument('--local-fixture', type=Path, help='explicit local data/platform fixture; production workers unchanged')
    args = parser.parse_args()
    if not args.root.is_absolute():
        parser.error('Absolute persistent experiment root required')
    args.root.mkdir(parents=True, exist_ok=True)
    transfer = args.root/'transfer'; transfer.mkdir(exist_ok=True)
    attempt = Path(tempfile.mkdtemp(prefix='gi-pilot-', dir=args.root))
    started, status, code = time.monotonic(), {}, 1
    out, err = sys.stdout, sys.stderr
    with (attempt/'terminal.log').open('x') as log:
        sys.stdout, sys.stderr = Tee(out, log), Tee(err, log)
        handlers = {sig: signal.getsignal(sig) for sig in (signal.SIGINT, signal.SIGTERM, signal.SIGALRM)}
        def cancelled(signum, frame):
            raise KeyboardInterrupt('Owner cancellation '+str(signum))
        def timeout(signum, frame):
            raise TimeoutError('Overall E005 pilot ceiling exceeded')
        for sig in (signal.SIGINT, signal.SIGTERM):
            signal.signal(sig, cancelled)
        signal.signal(signal.SIGALRM, timeout)
        try:
            limits = json.loads((BUNDLE/EXP/'pilot.json').read_text())['resources']
            signal.setitimer(signal.ITIMER_REAL, limits['total_driver_seconds_ceiling'])
            manifest = verify_bundle(BUNDLE)
            write(attempt/'bundle-manifest.json', manifest)
            if args.allocated_vcpus != 4 or args.allocated_ram_gb < 12:
                raise ValueError('First pilot requires explicit 4-vCPU / at-least-12-GB allocation')
            # Explicit tiny local data fixtures need 1 GB, not the production
            # two-million-pair provision. Native worker/time/RSS caps stay intact.
            required_free = (1 if args.local_fixture else 10)*10**9
            if shutil.disk_usage(args.root).free < required_free:
                raise RuntimeError('Provision at least 10 GB free for the frozen pilot; do not shrink inputs')
            status = execute(args, attempt, manifest, started)
            code = 0
        except BaseException as error:
            traceback.print_exc()
            status = dict(status='failed', error=repr(error), scientific_result='execution failure; not biological rejection')
        finally:
            signal.setitimer(signal.ITIMER_REAL, 0)
            elapsed = time.monotonic()-started
            status.update(driver_seconds_before_collection=elapsed, allocated_vcpus=args.allocated_vcpus,
                allocated_ram_gb=args.allocated_ram_gb, allocated_vcpu_hours_before_collection=args.allocated_vcpus*elapsed/3600,
                accounting='complete driver wall including probes/setup; evidence collection reported afterward; outer checksum/upload/owner idle excluded')
            write(attempt/'status.json', status)
            progress('driver_end', status=status['status'], driver_seconds=elapsed,
                     allocated_vcpu_hours=status['allocated_vcpu_hours_before_collection'], attempt=str(attempt))
            try:
                collect(attempt, transfer)
                elapsed = time.monotonic()-started
                progress('cost_through_collection', driver_seconds=elapsed, allocated_vcpu_hours=args.allocated_vcpus*elapsed/3600)
            except BaseException:
                traceback.print_exc(); code = 1
            for sig, handler in handlers.items():
                signal.signal(sig, handler)
            sys.stdout, sys.stderr = out, err
    return code


if __name__ == '__main__':
    raise SystemExit(main())
