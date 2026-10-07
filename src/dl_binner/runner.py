"""Installed serial workflow, immutable run contracts and explicit safe recovery.

Stages use the accepted native CLI without changing the scientific algorithms.
Only successful outputs are published from unique staging folders. Failed
attempts remain inspectable; resume verifies completed bytes before scheduling.
"""
import argparse
from decimal import Decimal, ROUND_CEILING
import importlib.metadata
import json
import os
from pathlib import Path
import platform
import shutil
import signal
import sys
import time
import traceback
import uuid

from . import __version__
from .contracts import check_files, digest, file_record, write_json
from .supervision import isolated_env, process_sample, progress, supervise

STAGES = ('features', 'train', 'raw-embed', 'raw-cluster', 'raw-export',
          'learned-embed', 'learned-cluster', 'learned-export')
FOLDERS = ('features', 'training', 'raw/embedding', 'raw/clustering', 'raw/bins',
           'learned/embedding', 'learned/clustering', 'learned/bins')
PACKAGE = Path(__file__).parent


def receipt_name(stage):
    """Return the stable receipt target used by the built-in serial dispatcher."""
    return f'receipts/{STAGES.index(stage)+1:02d}-{stage}.json'


def source_records():
    """Bind installed code/defaults, independent of checkout or Git availability."""
    return {str(p.relative_to(PACKAGE)): file_record(p) for p in sorted(PACKAGE.rglob('*'))
            if p.is_file() and p.suffix in ('.py', '.smk', '.json')}


def inventory(folder):
    """Bind all published stage files, including empty bin/noise/exclusion FASTAs."""
    return {str(p.relative_to(folder)): file_record(p) for p in sorted(Path(folder).rglob('*'))
            if p.is_file() or p.is_symlink()}


def validate_completed(root):
    """Verify a prefix of completed stages and reject unreceipted final artifacts."""
    root = Path(root)
    completed, previous = [], None
    manifest_sha = digest(root/'run-manifest.json')
    missing = False
    for stage, folder in zip(STAGES, FOLDERS):
        receipt = root/receipt_name(stage)
        output = root/folder
        if not receipt.exists():
            missing = True
            if output.exists():
                raise ValueError(f'Unreceipted published output: {output}; preserve it and use a fresh run')
            continue
        if missing:
            raise ValueError('Completed stages are not a serial prefix')
        data = json.loads(receipt.read_text())
        if data['stage'] != stage or data['manifest_sha256'] != manifest_sha or data['previous_receipt_sha256'] != previous:
            raise ValueError(f'Stage receipt identity mismatch: {receipt}')
        check_files(output, data['files'])
        if inventory(output) != data['files']:
            raise ValueError(f'Unexpected published files: {output}')
        for name, record in data['evidence_files'].items():
            check_files(root, {name: record})
        completed.append(data)
        previous = digest(receipt)
    return completed


def stage_command(root, manifest, stage, destination):
    """Build native stage argv with exact accepted inputs and lexical Python path."""
    base = [manifest['binner_python'], '-I', '-B', '-m', 'dl_binner', '--threads', str(manifest['threads'])]
    features, checkpoint = root/'features/features.npz', root/'training/checkpoint.pt'
    if stage == 'features':
        args = ['prepare', '--fasta', manifest['fasta'], '--min-length', str(manifest['min_length']),
                '--output', destination/'features.npz']
        if manifest['depth']:
            args += ['--depth', manifest['depth']]
    elif stage == 'train':
        args = ['train', '--features', features, '--config', root/'.run/training.json',
                '--output', destination/'checkpoint.pt']
    else:
        arm, operation = stage.split('-')
        if operation == 'embed':
            args = ['embed', '--features', features, '--output', destination/'embeddings.npz']
            args += ['--raw'] if arm == 'raw' else ['--checkpoint', checkpoint]
        elif operation == 'cluster':
            args = ['cluster', '--embeddings', root/f'{arm}/embedding/embeddings.npz',
                    '--output', destination/'partition.json']
        else:
            args = ['export', '--features', features, '--fasta', manifest['fasta'],
                    '--partition', root/f'{arm}/clustering/partition.json', '--output', destination/'bins']
    return [str(a) for a in base+args]


def worker(config_path, stage):
    """Run one real native stage under limits and publish outputs only on success."""
    cfg = json.loads(Path(config_path).read_text())
    root = Path(cfg['root'])
    manifest = json.loads((root/'run-manifest.json').read_text())
    existing = validate_completed(root)
    at = STAGES.index(stage)
    if at < len(existing):
        progress(f'{at+1}/8 {stage}: verified completed outputs, reused')
        return
    if at != len(existing):
        raise ValueError('Serial predecessor is missing')
    staging = root/'staging'/f'{stage}-{uuid.uuid4().hex[:10]}'
    staging.mkdir(parents=True)
    destination = staging/'outputs'
    destination.mkdir()
    progress(f'{at+1}/8 {stage}: starting')
    log = root/cfg['invocation']/f'{at+1:02d}-{stage}.native.log'
    started_ns = time.monotonic_ns()
    result = supervise(stage_command(root, manifest, stage, destination), log,
                       remaining_seconds(cfg['deadline']), manifest['memory_bytes'],
                       isolated_env(manifest['threads']), sample_root=os.getpid())
    # Export creates its own fresh directory; publish that directory, not a wrapper.
    final = root/FOLDERS[at]
    final.parent.mkdir(parents=True, exist_ok=True)
    if final.exists():
        raise FileExistsError(f'Published stage already exists: {final}')
    (destination/'bins' if stage.endswith('-export') else destination).rename(final)
    evidence = {str(p.relative_to(root)): file_record(p) for p in
                (log, log.with_suffix('.exit.json'), log.with_suffix('.samples.jsonl'))}
    write_json(root/receipt_name(stage), dict(stage=stage, files=inventory(final),
        manifest_sha256=digest(root/'run-manifest.json'), previous_receipt_sha256=(
            digest(root/receipt_name(STAGES[at-1])) if at else None), evidence_files=evidence,
        start_monotonic_ns=started_ns, end_monotonic_ns=time.monotonic_ns(), resources=result))
    progress(f'{at+1}/8 {stage}: complete ({result["wall_seconds"]:.1f}s)')


class Tee:
    """Capture the parent's readable terminal output, including its final exit code."""
    def __init__(self, terminal, log):
        self.terminal, self.log = terminal, log

    def write(self, value):
        self.terminal.write(value); self.log.write(value)
        self.flush()

    def flush(self):
        self.terminal.flush(); self.log.flush()


def remaining_seconds(deadline):
    """Return an optional remaining invocation safeguard; refuse already expired work."""
    if deadline is None:
        return None
    remaining = deadline-time.monotonic()
    if remaining <= 0:
        raise TimeoutError('Overall run wall-time limit reached')
    return remaining


def arm_deadline(deadline):
    """Arm a bounded OS timer pulse without imposing a product timeout maximum.

    Large finite user deadlines can exceed platform time_t. Re-arm day-sized
    pulses until the actual deadline; None disables this invocation's timer.
    """
    remaining = remaining_seconds(deadline)
    signal.setitimer(signal.ITIMER_REAL, min(remaining, 86400) if remaining is not None else 0)


def native_failure(folder):
    """Return the failed native stage's concise cause/log, beyond scheduler trailers."""
    for path in sorted(Path(folder).glob('*.native.exit.json'), reverse=True):
        try:
            data=json.loads(path.read_text())
            log=path.with_name(path.name.replace('.exit.json','.log'))
            lines=log.read_text().splitlines()
        except (OSError, ValueError):
            continue  # A hard cancellation may leave an unfinished receipt.
        if data['exit_code']==0 and data['stop_reason'] is None:
            continue
        errors=[line[len('error: '):] for line in lines if line.startswith('error: ')]
        cause=errors[-1] if errors else data['stop_reason'] or f'Native worker exited with code {data["exit_code"]}'
        return dict(stage=path.name.split('.native')[0],cause=cause,log=str(log))
    return None


def finalize(root, manifest, stages, workflow_resources, started):
    """Verify checkpoint parity and both exports; publish byte-bound neutral summaries."""
    import numpy as np
    from .io import load_arrays
    from .accounting import summarize_arm, write_summary_tsv
    reference, _ = load_arrays(root/'training/checkpoint.reference.npz', 'embeddings')
    reloaded, _ = load_arrays(root/'learned/embedding/embeddings.npz', 'embeddings')
    if any(not np.array_equal(reference[k], reloaded[k]) for k in ('ids', 'features', 'evidence')):
        raise ValueError('Saved checkpoint reload differs from its retained training reference')
    arms, sources = {}, {}
    for arm in ('raw', 'learned'):
        arms[arm], inputs = summarize_arm(root/'features/features.npz', root/f'{arm}/bins')
        sources.update(inputs)
    for i, data in enumerate(stages):
        if i and stages[i-1]['end_monotonic_ns'] > data['start_monotonic_ns']:
            raise ValueError('Native stage timings overlap despite the serial contract')
        sources[str(root/receipt_name(data['stage']))] = file_record(root/receipt_name(data['stage']))
    sources[str(root/'run-manifest.json')] = file_record(root/'run-manifest.json')
    if 'run-summary.json' in {p.name for p in root.iterdir()} or (root/'run-summary.tsv').exists():
        raise ValueError('Unreceipted summary exists; preserve it and use a fresh output directory')
    elapsed = time.monotonic()-started
    summary = dict(version=1, kind='label_free_run_accounting', arms=arms, source_files=sources,
        checkpoint_reload_exact=True, scientific_quality_assessed=False,
        limitation='Bin assignment/size is not genome recovery, completeness, contamination or MAG quality',
        budget=dict(threads=manifest['threads'], torch_interop=1, loader_workers=0,
                    memory_bytes=manifest['memory_bytes'], serial_stages=True),
        stage_resources={s['stage']: s['resources'] for s in stages},
        current_invocation=dict(seconds_to_summary=elapsed, thread_wall_hours_to_summary=manifest['threads']*elapsed/3600,
                                workflow=workflow_resources),
        clock_scope='Current invocation starts before input hashing/probe. Summary final serialization/exit logging excluded; final invocation status includes them. Previous stages retain their original invocation costs. Thread-wall hours are local planning, not provider charges.')
    memory, _ = process_sample(os.getpid(), {})
    if manifest['memory_bytes'] is not None and memory > manifest['memory_bytes']:
        raise MemoryError('Accounting exceeded the working RSS limit')
    write_json(root/'run-summary.json', summary)
    write_summary_tsv(root/'run-summary.tsv', arms)
    write_json(root/'completion.json', dict(version=1, manifest_sha256=digest(root/'run-manifest.json'),
        files={name: file_record(root/name) for name in ('run-summary.json', 'run-summary.tsv')},
        stage_receipts={receipt_name(s): file_record(root/receipt_name(s)) for s in STAGES}))
    return arms


def run_pipeline(args):
    """Own a serial invocation with optional safeguards and byte-verified recovery."""
    root = args.output.absolute()
    if args.resume:
        if not (root/'run-manifest.json').is_file():
            raise ValueError('--resume needs a prior run-manifest.json in this output directory')
    elif root.exists() and any(root.iterdir()):
        raise FileExistsError(f'Output directory is populated: {root}. Use --resume for matching inputs, or choose a fresh --output')
    root.mkdir(parents=True, exist_ok=True)
    lock = root/'.run-lock'
    try:
        with lock.open('x') as stream:
            stream.write(json.dumps(dict(pid=os.getpid(), host=platform.node()))+'\n')
    except FileExistsError:
        raise RuntimeError(f'Run lock exists: {lock}. Check its PID/host; remove only after confirming that run has stopped')
    invocation = root/'logs'/('invocation-'+time.strftime('%Y%m%dT%H%M%S', time.gmtime())+'-'+uuid.uuid4().hex[:8])
    invocation.mkdir(parents=True)
    started = time.monotonic()
    deadline = started+args.timeout if args.timeout is not None else None
    prior_out, prior_err = sys.stdout, sys.stderr
    handlers = {s: signal.getsignal(s) for s in (signal.SIGINT, signal.SIGTERM, signal.SIGALRM)}
    code, status = 1, 'failed'
    old_timer = signal.getitimer(signal.ITIMER_REAL)
    with (invocation/'terminal.log').open('x') as log:
        sys.stdout, sys.stderr = Tee(prior_out, log), Tee(prior_err, log)
        def stop(signum, frame):
            if signum == signal.SIGALRM:
                arm_deadline(deadline)  # Raises only at the actual user deadline.
                return
            raise KeyboardInterrupt('Run cancelled; completed stages can be resumed')
        for sig in handlers:
            signal.signal(sig, stop)
        try:
            arm_deadline(deadline)
            progress(f'dl-binner {__version__} | output: {root}')
            progress(f'{args.threads} CPU threads, loader workers 0; built-in serial stages; matched raw control enabled')
            progress(f'Optional safeguards: RAM={args.memory_gb} GB, time={args.timeout} seconds (None means disabled)')
            fasta = args.fasta.resolve()
            depth = args.depth.resolve() if args.depth else None
            training = args.training_config.resolve() if args.training_config else PACKAGE/'resources/training.json'
            python = Path(sys.executable).absolute()  # Never resolve a virtual-environment interpreter.
            bindings = dict(version=2, engine="builtin-serial", package_version=__version__, source_files=source_records(),
                binner_python=str(python), binner_prefix=sys.prefix,
                distributions={name: importlib.metadata.version(name) for name in ('dl-binner', 'numpy', 'torch', 'networkx', 'threadpoolctl')},
                fasta=str(fasta), fasta_bytes=file_record(fasta), depth=str(depth) if depth else None,
                depth_bytes=file_record(depth) if depth else None, training_bytes=file_record(training),
                runtime_inventory={d.metadata['Name']: d.version for d in importlib.metadata.distributions()},
                threads=args.threads, memory_bytes=int((Decimal(str(args.memory_gb))*10**9).to_integral_value(rounding=ROUND_CEILING)) if args.memory_gb is not None else None,
                min_length=args.min_length)
            if args.resume:
                previous = json.loads((root/'run-manifest.json').read_text())
                if bindings != previous:
                    raise ValueError('Input/config/package/runtime/budget changed since this run. Restore the original bytes/settings or use a fresh output directory')
                check_files(root/'.run', {'training.json': bindings['training_bytes']})
                stages = validate_completed(root)
                progress(f'Verified {len(stages)}/8 completed stages; they will be reused')
                if (root/'completion.json').exists():
                    completion = json.loads((root/'completion.json').read_text())
                    if completion['manifest_sha256'] != digest(root/'run-manifest.json'):
                        raise ValueError('Completion manifest changed')
                    check_files(root, completion['files']); check_files(root, completion['stage_receipts'])
                    progress(f'Already complete. No feature extraction, training or clustering scheduled. Summary: {root/"run-summary.tsv"}')
                    status, code = 'reused_complete', 0
                    return code
            if args.resume:
                manifest = previous
            else:
                (root/'.run').mkdir()
                shutil.copyfile(training, root/'.run/training.json')
                manifest = bindings
                write_json(root/'run-manifest.json', manifest)
            config = invocation/'config.json'
            write_json(config, dict(root=str(root), invocation=str(invocation.relative_to(root)),
                                    deadline=deadline, python=str(python), threads=args.threads))
            # The journal already defines a strictly serial prefix; no scheduler
            # runtime or parallel job system is needed to dispatch its remainder.
            existing = validate_completed(root)
            target = STAGES.index(args.stop_after)+1 if args.stop_after else len(STAGES)
            for stage in STAGES[len(existing):target]:
                remaining_seconds(deadline)
                worker(config, stage)
            resources = dict(engine='builtin-serial', stages_executed=list(STAGES[len(existing):target]),
                             seconds=time.monotonic()-started, timeout_seconds=args.timeout)
            stages = validate_completed(root)
            if len(stages) != 8:
                progress(f'Paused after {len(stages)}/8 stages. Continue with the same command plus --resume (omit --stop-after)')
                status, code = 'partial', 0
                return code
            arms = finalize(root, manifest, stages, resources, started)
            for name, value in arms.items():
                counts = value['statuses']
                progress(f'{name}: {value["bin_count"]} bins; {counts["assigned"]["contigs"]} assigned, {counts["unassigned"]["contigs"]} unassigned, {counts["excluded"]["contigs"]} excluded')
            progress(f'Complete. Assignments/FASTA: learned/bins/ and raw/bins/; summary: {root/"run-summary.tsv"}')
            status, code = 'completed', 0
        except BaseException as error:
            code = 130 if isinstance(error, KeyboardInterrupt) else 1
            failure=native_failure(invocation)
            if failure:
                print(f'error: {failure["stage"]} failed: {failure["cause"]}\nNative log: {failure["log"]}',file=sys.stderr,flush=True)
                if 'IUPAC' in failure['cause']:
                    print('Check the named FASTA record: IDs must be unique and DNA must use valid IUPAC letters. Changed inputs require a fresh --output.',file=sys.stderr,flush=True)
                elif 'eligible' in failure['cause'] or 'nonconstant' in failure['cause']:
                    print('Training needs at least two eligible contigs with different usable features. Inspect feature exclusions; changed inputs require a fresh --output.',file=sys.stderr,flush=True)
            else:
                print(f'error: {str(error).splitlines()[0]}', file=sys.stderr, flush=True)
            traceback.print_exc(file=log)
            progress(f'Stopped safely. Logs and failed-stage files retained: {invocation}. Resume matching inputs with --resume; no automatic repairs')
        finally:
            signal.setitimer(signal.ITIMER_REAL, 0)
            elapsed = time.monotonic()-started
            write_json(invocation/'status.json', dict(status=status, exit_code=code, wall_seconds=elapsed,
                threads=args.threads, thread_wall_hours=args.threads*elapsed/3600,
                engine='builtin-serial', memory_gb=args.memory_gb, timeout_seconds=args.timeout,
                failure=native_failure(invocation),
                scope='Current invocation through status; includes hashing/accounting, excludes installation and final status serialization. Local planning, not a provider invoice.'))
            progress(f'exit_code={code} | {status} | {elapsed:.2f}s | terminal log: {invocation/"terminal.log"}')
            for sig, handler in handlers.items():
                signal.signal(sig, handler)
            signal.setitimer(signal.ITIMER_REAL, *old_timer)
            sys.stdout, sys.stderr = prior_out, prior_err
            lock.unlink()
    return code


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Internal installed serial stage adapter')
    parser.add_argument('--config', type=Path, required=True)
    parser.add_argument('--stage', choices=STAGES, required=True)
    args = parser.parse_args()
    try:
        worker(args.config, args.stage)
    except BaseException:
        traceback.print_exc()
        sys.stdout.flush(); sys.stderr.flush()
        os._exit(1)
