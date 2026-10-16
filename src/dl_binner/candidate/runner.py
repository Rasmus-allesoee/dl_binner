"""Journaled serial candidate workflow with byte-verified explicit recovery.

Own seven native stages under a single optional wall/RSS safeguard. Never retry or
repair automatically. Failed staging outputs/logs remain; completed stages can
only be reused with identical source/runtime/config/input bytes.
"""
import argparse
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

from .. import __version__
from ..contracts import check_files, digest, file_record, write_json
from ..runner import Tee, arm_deadline, inventory, remaining_seconds, source_records
from ..supervision import isolated_env, progress, supervise

STAGES = ('features', 'markers', 'train', 'embed', 'group', 'refine', 'export')


def completed(root):
    """Verify an immutable serial receipt prefix, including retained native logs."""
    records, previous, missing = [], None, False
    for stage in STAGES:
        path = root/'receipts'/(stage+'.json')
        if not path.exists():
            missing = True
            if (root/stage).exists():
                raise ValueError('Unreceipted candidate stage output: '+stage)
            continue
        if missing:
            raise ValueError('Candidate receipts are not a serial prefix')
        record = json.loads(path.read_text())
        if (record['stage'] != stage or record['manifest_sha256'] != digest(root/'run-manifest.json')
                or record['previous_receipt_sha256'] != previous):
            raise ValueError('Candidate receipt chain mismatch')
        check_files(root/stage, record['files'])
        if inventory(root/stage) != record['files']:
            raise ValueError('Unexpected candidate stage member')
        check_files(root, record['evidence'])
        records.append(record)
        previous = digest(path)
    return records


def worker(root, stage, output):
    """Execute one production stage inside its fresh unpublished output directory."""
    from .views import config
    manifest = json.loads((root/'run-manifest.json').read_text())
    cfg = config(root/'candidate.json')
    fasta, features = Path(manifest['fasta']), root/'features/features.npz'
    if stage == 'features':
        from .views import prepare
        prepare(fasta, manifest['depth'], output, cfg)
    elif stage == 'markers':
        from .markers import cache, load_cache
        if manifest['marker_cache']:
            cache_path = Path(manifest['marker_cache'])
            load_cache(cache_path, fasta)
            for p in cache_path.iterdir():
                shutil.copyfile(p, output/p.name)
            load_cache(output, fasta)
        else:
            cache(fasta, manifest['marker_hmm'], manifest['marker_manifest'], output, manifest['threads'])
    elif stage == 'train':
        from .model import train
        train(features, root/'features/views.npz', output, cfg, manifest['threads'])
    elif stage == 'embed':
        from .model import embed
        embed(features, root/'train/checkpoint.pt', output/'embeddings.npz', manifest['threads'])
    elif stage == 'group':
        from .grouping import group
        group(root/'embed/embeddings.npz', features, output, cfg, manifest['threads'])
    elif stage == 'refine':
        from ..io import load_arrays
        from .views import load
        from .markers import load_cache
        from .grouping import refine_partition
        data, _ = load(features)
        evidence = load_cache(root/'markers', fasta, data['ids'].tolist())
        vectors, _ = load_arrays(root/'embed/embeddings.npz', 'embeddings')
        pre = json.loads((root/'group/partition.json').read_text())
        result = refine_partition(pre, data, vectors['features'], evidence['clean'], cfg)
        result.update(pre_partition_sha256=digest(root/'group/partition.json'),
                      marker_cache_sha256=digest(root/'markers/cache.json'))
        write_json(output/'partition.json', result)
    elif stage == 'export':
        from ..clustering import export
        from ..accounting import summarize_arm
        for arm, partition in (('pre', root/'group/partition.json'), ('post', root/'refine/partition.json')):
            export(features, partition, fasta, output/arm)
        summaries = {arm: summarize_arm(features, output/arm)[0] for arm in ('pre', 'post')}
        write_json(output/'accounting.json', dict(arms=summaries, scientific_quality_assessed=False,
                   limitation='Assignment and marker conflicts are not independent genome quality/recovery'))
    else:
        raise ValueError('Unknown candidate stage')


def run(args):
    """Run/reuse a candidate invocation; parent setup, hashing and collection are timed."""
    started = time.monotonic()
    deadline = started+args.timeout if args.timeout else None
    root = args.output.absolute()
    if args.resume:
        if not (root/'run-manifest.json').is_file():
            raise ValueError('Candidate --resume needs a prior run manifest')
    elif root.exists() and any(root.iterdir()):
        raise FileExistsError('Fresh candidate output required; explicit --resume only for verified matching work')
    root.mkdir(parents=True, exist_ok=True)
    lock = root/'.run-lock'
    with lock.open('x') as stream:
        json.dump(dict(pid=os.getpid(), host=platform.node()), stream)
    invocation = root/'logs'/('invocation-'+uuid.uuid4().hex[:12])
    invocation.mkdir(parents=True)
    old_handlers = {s: signal.getsignal(s) for s in (signal.SIGALRM, signal.SIGINT, signal.SIGTERM)}
    old_timer = signal.getitimer(signal.ITIMER_REAL)
    prior_out, prior_err = sys.stdout, sys.stderr
    code, status, error_text = 1, 'failed', None
    with (invocation/'terminal.log').open('x') as terminal:
        sys.stdout, sys.stderr = Tee(prior_out, terminal), Tee(prior_err, terminal)
        def stop(sig, frame):
            if sig == signal.SIGALRM:
                arm_deadline(deadline)
            else:
                raise KeyboardInterrupt('Candidate cancelled; no automatic retry')
        for sig in old_handlers:
            signal.signal(sig, stop)
        try:
            arm_deadline(deadline)
            from .views import config
            cfg = config(args.config)
            def location(p):
                return str(p.resolve()) if p else None
            paths = {name: location(getattr(args, name)) for name in
                     ('fasta', 'depth', 'marker_cache', 'marker_hmm', 'marker_manifest')}
            inputs = {name: file_record(p) for name, p in paths.items() if p and name != 'marker_cache'}
            if paths['marker_cache']:
                from .markers import load_cache
                load_cache(paths['marker_cache'], paths['fasta'])
                inputs['marker_cache'] = file_record(Path(paths['marker_cache'])/'cache.json')
            manifest = dict(kind='candidate_run', version=1, package_version=__version__,
                python=sys.executable, prefix=sys.prefix, source=source_records(),
                runtime={d.metadata['Name']: d.version for d in importlib.metadata.distributions()},
                threads=args.threads, memory_bytes=int(args.memory_gb*1e9) if args.memory_gb else None,
                config=cfg, inputs=inputs, **paths)
            if args.resume:
                if json.loads((root/'run-manifest.json').read_text()) != manifest:
                    raise ValueError('Candidate source/runtime/input/config/resource identity changed')
                if json.loads((root/'candidate.json').read_text()) != cfg:
                    raise ValueError('Retained candidate configuration changed')
            else:
                write_json(root/'run-manifest.json', manifest)
                write_json(root/'candidate.json', cfg)
            records = completed(root)
            if (root/'completion.json').exists():
                done = json.loads((root/'completion.json').read_text())
                if len(records) != len(STAGES) or done['manifest_sha256'] != digest(root/'run-manifest.json'):
                    raise ValueError('Candidate completion mismatch')
                check_files(root, done['receipts'])
                status, code = 'reused_complete', 0
                progress('Candidate already verified complete; no training, marker scan or grouping scheduled')
                return code
            target = STAGES.index(args.stop_after)+1 if args.stop_after else len(STAGES)
            env = isolated_env(args.threads)
            env.update(NUMBA_NUM_THREADS=str(args.threads), NUMBA_CACHE_DIR=str(root/'native-cache'))
            for stage in STAGES[len(records):target]:
                remaining_seconds(deadline)
                stage_start = time.monotonic_ns()
                temporary = root/'staging'/(stage+'-'+uuid.uuid4().hex[:8])
                temporary.mkdir(parents=True)
                log = invocation/(stage+'.native.log')
                progress('Candidate '+stage+' starting')
                result = supervise([sys.executable, '-I', '-B', '-m', 'dl_binner.candidate.runner',
                    '--root', str(root), '--stage', stage, '--output', str(temporary)], log,
                    remaining_seconds(deadline), manifest['memory_bytes'], env, sample_root=os.getpid())
                temporary.rename(root/stage)
                evidence = {str(p.relative_to(root)): file_record(p) for p in
                            (log, log.with_suffix('.exit.json'), log.with_suffix('.samples.jsonl'))}
                write_json(root/'receipts'/(stage+'.json'), dict(stage=stage,
                    manifest_sha256=digest(root/'run-manifest.json'),
                    previous_receipt_sha256=digest(root/'receipts'/(STAGES[STAGES.index(stage)-1]+'.json')) if STAGES.index(stage) else None,
                    start_monotonic_ns=stage_start, end_monotonic_ns=time.monotonic_ns(),
                    files=inventory(root/stage), evidence=evidence, resources=result))
                progress('Candidate '+stage+' complete')
            records = completed(root)
            if len(records) < len(STAGES):
                status, code = 'partial', 0
            else:
                write_json(root/'completion.json', dict(kind='candidate_complete', version=1,
                    manifest_sha256=digest(root/'run-manifest.json'), checkpoint_reload_exact=True,
                    scientific_quality_assessed=False,
                    receipts={str(p.relative_to(root)): file_record(p) for p in sorted((root/'receipts').glob('*.json'))}))
                status, code = 'completed', 0
            return code
        except BaseException as error:
            error_text = str(error)
            code = 130 if isinstance(error, KeyboardInterrupt) else 1
            print('error: '+error_text, file=sys.stderr, flush=True)
            traceback.print_exc(file=terminal)
            progress('Candidate stopped; staging/logs retained, no retry')
            return code
        finally:
            signal.setitimer(signal.ITIMER_REAL, 0)
            elapsed = time.monotonic()-started
            write_json(invocation/'status.json', dict(status=status, exit_code=code, error=error_text,
                wall_seconds=elapsed, threads=args.threads, thread_wall_hours=args.threads*elapsed/3600,
                scope='Current local invocation through status, including setup/hash/collection; excludes environment installation; no provider cost inferred'))
            progress(f'Candidate {status}, exit={code}, {elapsed:.2f}s; {invocation}')
            sys.stdout, sys.stderr = prior_out, prior_err
            for sig, handler in old_handlers.items():
                signal.signal(sig, handler)
            signal.setitimer(signal.ITIMER_REAL, *old_timer)
            lock.unlink()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Internal candidate production stage')
    parser.add_argument('--root', type=Path, required=True)
    parser.add_argument('--stage', choices=STAGES, required=True)
    parser.add_argument('--output', type=Path, required=True)
    a = parser.parse_args()
    try:
        worker(a.root, a.stage, a.output)
    except BaseException:
        traceback.print_exc()
        sys.stdout.flush()
        sys.stderr.flush()
        os._exit(1)
