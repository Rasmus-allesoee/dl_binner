#!/usr/bin/env python3
"""Supervise, evaluate and review E004's first native learned-binner integration.

The run mode invokes the installed package through a serial Snakemake DAG. Only
evaluate mode reads chromosome-origin truth after partitions exist. Review mode
checks retained outputs without repeating training/extraction and writes a small
result receipt. This is development fragment grouping, not whole-MAG evaluation.
"""
import argparse
import csv
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]


def stop_tree(members):
    """Terminate only observed children of this launched job; prevent orphan hangs."""
    import psutil
    live = []
    for key in members:
        try:
            process = psutil.Process(key[0])
            if process.create_time() == key[1]:
                process.terminate()
                live.append(process)
        except psutil.NoSuchProcess:
            pass
    _, alive = psutil.wait_procs(live, timeout=3)
    for process in alive:
        try:
            process.kill()
        except psutil.NoSuchProcess:
            pass


def supervise(command, directory, seconds=7200, ram_bytes=8000000000):
    """Capture command/log/progress and sampled whole-subtree CPU/RSS; enforce caps.

    Track each observed PID with creation time so terminated children retain CPU
    samples and stale PID reuse cannot target unrelated processes. RAM sampling
    is not an exact high-water mark; CPU sampling can miss very short processes.
    """
    import psutil
    from dl_binner.io import emit, write_json
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=False)
    started, peak, samples, members, reason = time.monotonic(), 0, {}, {}, None
    process = None
    original_handlers = {sig: signal.getsignal(sig) for sig in (signal.SIGINT, signal.SIGTERM)}

    def interrupt(signum, frame):
        raise KeyboardInterrupt(f'Signal {signum}')

    for sig in original_handlers:
        signal.signal(sig, interrupt)
    with (directory/'terminal.log').open('x') as log, (directory/'resources.jsonl').open('x') as metrics:
        try:
            process = subprocess.Popen(command, stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
            root = psutil.Process(process.pid)
            heartbeat, sampled = 0.0, 0.0
            while process.poll() is None:
                now = time.monotonic()
                rss = 0
                try:
                    current = [root]+root.children(recursive=True)
                except psutil.NoSuchProcess:
                    current = []
                for child in current:
                    try:
                        key = (child.pid, child.create_time())
                        members[key] = True
                        rss += child.memory_info().rss
                        cpu = child.cpu_times()
                        samples[key] = max(samples.get(key, 0), cpu.user+cpu.system)
                    except psutil.NoSuchProcess:
                        pass
                peak = max(peak, rss)
                if now-sampled >= 1:
                    metrics.write(json.dumps(dict(seconds=now-started, rss_bytes=rss,
                                                  sampled_cumulative_cpu_seconds=sum(samples.values())))+'\n')
                    metrics.flush()
                    sampled = now
                if now-heartbeat >= 20:
                    emit('workflow_heartbeat', seconds=now-started, rss_bytes=rss,
                         log=str(directory/'terminal.log'))
                    heartbeat = now
                if rss > ram_bytes:
                    reason = 'RAM ceiling'
                    break
                if now-started > seconds:
                    reason = 'Time ceiling'
                    break
                time.sleep(0.05)
        except KeyboardInterrupt as error:
            reason = 'Cancelled: '+str(error)
        except Exception as error:
            import traceback
            reason = 'Monitor/launch failure: '+repr(error)
            traceback.print_exc(file=log)
        finally:
            if process is not None:
                stop_tree(members)
                try:
                    os.killpg(process.pid, signal.SIGTERM)
                except ProcessLookupError:
                    pass
                try:
                    process.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    os.killpg(process.pid, signal.SIGKILL)
                    process.wait()
            for sig, handler in original_handlers.items():
                signal.signal(sig, handler)
    elapsed = time.monotonic()-started
    result = dict(command=command, exit_code=process.returncode if process else None,
                  stop_reason=reason, wall_seconds=elapsed, peak_sampled_rss_bytes=peak,
                  sampled_process_cpu_seconds=sum(samples.values()), sampled_average_cpus=sum(samples.values())/elapsed,
                  thread_budget=4, four_thread_wall_hours=4*elapsed/3600,
                  scope='local sampled descendant accounting; not UCloud billing or exact total CPU')
    write_json(directory/'supervisor.json', result)
    return result


def evaluate(config, run_dir, output):
    """Score fixed partitions only, checking pre-save/reload and complete exports."""
    import numpy as np
    from dl_binner.io import digest, load_arrays, read_fasta, write_json
    from e003_representation_screen import score
    run_dir = Path(run_dir)
    panel = json.loads((ROOT/config['truth_panel']).read_text())
    data, _ = load_arrays(run_dir/'features.npz', 'features')
    learned, _ = load_arrays(run_dir/'learned.embeddings.npz', 'embeddings')
    reference, _ = load_arrays(run_dir/'checkpoint.reference.npz', 'embeddings')
    if reference['ids'].tolist() != learned['ids'].tolist():
        raise ValueError('Pre-save/reload reference ID mismatch')
    np.testing.assert_allclose(learned['features'], reference['features'], rtol=0, atol=1e-7)
    np.testing.assert_array_equal(learned['evidence'], reference['evidence'])
    results = {}
    for mode in ('raw', 'learned'):
        partition = json.loads((run_dir/f'{mode}.partition.json').read_text())
        results[mode] = score(partition, panel)
        folder = run_dir/f'{mode}.export'
        exported = {}
        for path in folder.glob('*.fna'):
            if not path.stat().st_size:
                continue
            for ident, dna in read_fasta(path):
                if ident in exported:
                    raise ValueError('Contig exported more than once')
                exported[ident] = dna
        source = dict(read_fasta(ROOT/config['fasta']))
        if exported != source:
            raise ValueError('Complete export DNA/ID accounting failed')
        with (folder/'assignments.tsv').open() as stream:
            table = list(csv.DictReader(stream, delimiter='\t'))
        if [r['contig_id'] for r in table] != data['ids'].tolist():
            raise ValueError('Export assignment axis mismatch')
        manifest = json.loads((folder/'manifest.json').read_text())
        for name, entry in manifest['files'].items():
            if digest(folder/name) != entry['sha256'] or (folder/name).stat().st_size != entry['bytes']:
                raise ValueError('Export byte hash mismatch')
    reference_path = config.get('raw_partition_reference')
    if reference_path:
        old = json.loads((ROOT/reference_path).read_text())
        new = json.loads((run_dir/'raw.partition.json').read_text())
        for key in ('ids', 'assignment', 'neighbors', 'valid', 'clusters', 'unassigned', 'edges'):
            if old[key] != new[key]:
                raise ValueError('Native raw-control partition differs from accepted E003')
    write_json(output, dict(source_commit=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
                          scores=results, reload_max_abs=float(np.max(np.abs(learned['features']-reference['features']))),
                          checks=dict(complete_export_accounting=True, raw_matches_e003=bool(reference_path),
                                      checkpoint_reload=True, labels_used_only_after_partition=True),
                          limits='transductive development fragments; not independent or whole-MAG recovery; no utility tuning'))


def review(config, run_dir, output):
    """Publish actual costs, retained hashes and utility with no training rerun."""
    from dl_binner.io import digest, write_json
    run_dir, output = Path(run_dir).resolve(), Path(output)
    result = json.loads((run_dir/'evaluation.json').read_text())
    resource = json.loads((run_dir/'supervisor.json').read_text())
    training = json.loads((run_dir/'checkpoint.json').read_text())
    if resource['exit_code'] != 0 or resource['stop_reason'] or resource['wall_seconds'] > config['limits']['seconds'] or resource['peak_sampled_rss_bytes'] > config['limits']['ram_bytes']:
        raise ValueError('Integration resource/success gate did not pass')
    source_commit = result['source_commit']
    current = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    if current != source_commit:
        # Result records may be committed later; scientific source bytes must remain unchanged.
        for path in [*ROOT.glob('src/dl_binner/*.py'), ROOT/'workflows/first-binner/Snakefile']:
            name = str(path.relative_to(ROOT))
            committed = subprocess.check_output(['git', 'show', f'{source_commit}:{name}'], cwd=ROOT)
            import hashlib
            if hashlib.sha256(committed).hexdigest() != digest(path):
                raise ValueError('Scientific source drift during retained-output review')
        # The receipt writer may be repaired after science; run/evaluator contracts may not.
        import ast
        name = 'scripts/e004_integration.py'
        original = ast.parse(subprocess.check_output(['git', 'show', f'{source_commit}:{name}'], cwd=ROOT, text=True))
        actual = ast.parse((ROOT/name).read_text())
        for function in ('stop_tree', 'supervise', 'evaluate', 'main'):
            before = next(n for n in original.body if isinstance(n, ast.FunctionDef) and n.name == function)
            after = next(n for n in actual.body if isinstance(n, ast.FunctionDef) and n.name == function)
            if ast.dump(before) != ast.dump(after):
                raise ValueError('Scientific driver function drift: '+function)
    retained = [dict(path=str(p.relative_to(ROOT)), bytes=p.stat().st_size, sha256=digest(p))
                for p in sorted(run_dir.rglob('*')) if p.is_file()]
    compact = {mode: {key: value for key, value in values.items() if key != 'per_fragment'}
               for mode, values in result['scores'].items()}
    write_json(output, dict(record='E004', date='2026-10-04', attempt=run_dir.name, execution='completed',
        software_outcome='accepted native first train-save-reload-embed-cluster-export implementation',
        scientific_source_commit=source_commit, resource=resource, training=training,
        scores=compact, checks=result['checks'], reload_max_abs=result['reload_max_abs'],
        run_locator=str(run_dir.relative_to(ROOT)), retained_files=retained,
        retained_bytes=sum(f['bytes'] for f in retained),
        config=config, claims=result['limits']))
    with output.with_suffix('.metrics.tsv').open('x') as stream:
        writer = csv.writer(stream, delimiter='\t', lineterminator='\n')
        writer.writerow(['method', 'stratum', 'fragments', 'bp', 'neighbor_purity', 'b3_precision', 'b3_recall', 'b3_f1', 'assigned_fraction'])
        for mode, values in compact.items():
            subsets = {key: values[key] for key in ('all', 'base_weighted', 'short', 'long')}
            subsets.update(values['by_length'])
            for stratum, metrics in subsets.items():
                writer.writerow([mode, stratum, *[metrics[key] for key in ('fragments', 'bp', 'neighbor_purity', 'b3_precision', 'b3_recall', 'b3_f1', 'assigned_fraction')]])


def main():
    """Dispatch fresh supervised execution or retained-only evaluation/review."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--mode', choices=('run', 'evaluate', 'review'), required=True)
    parser.add_argument('--config', type=Path, required=True)
    parser.add_argument('--run-dir', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    for name in ('PYTHONPATH', 'PYTHONHOME', 'PYTHONUSERBASE'):
        os.environ.pop(name, None)
    os.environ['PYTHONNOUSERSITE'] = '1'
    for name in ('OMP_NUM_THREADS', 'MKL_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'VECLIB_MAXIMUM_THREADS', 'NUMEXPR_NUM_THREADS'):
        os.environ[name] = '4'
    from dl_binner.io import digest
    config = json.loads(args.config.read_text())
    if args.mode == 'run':
        if config['limits'] != dict(threads=4, ram_bytes=8000000000, seconds=7200):
            raise ValueError('Use the precommitted E004 resource limits')
        for name, expected in config['input_hashes'].items():
            if digest(ROOT/name) != expected:
                raise ValueError('Frozen input/config byte mismatch: '+name)
        if (ROOT/config['config_path']).resolve() != args.config.resolve() or Path(config['python']).absolute() != Path(sys.executable).absolute():
            raise ValueError('Driver/config/runtime path mismatch')
        import dl_binner.io
        package_root = Path(dl_binner.io.__file__).parent
        for name, expected in config.get('package_code_sha256', {}).items():
            if digest(package_root/name) != expected:
                raise ValueError('Installed package/source byte mismatch: '+name)
        command = [config['snakemake'], '--snakefile', str(ROOT/'workflows/first-binner/Snakefile'),
                   '--configfile', str(args.config.resolve()), '--directory', str(args.output.resolve()),
                   '--cores', '4', '--jobs', '1', '--resources', 'mem_mb=8000', '--benchmark-extended',
                   '--runtime-source-cache-path', str(args.output.resolve()/'snakemake-source-cache'),
                   '--keep-incomplete', '--printshellcmds', '--latency-wait', '2']
        result = supervise(command, args.output, config['limits']['seconds'], config['limits']['ram_bytes'])
        raise SystemExit(0 if result['exit_code'] == 0 and result['stop_reason'] is None else 1)
    if args.run_dir is None:
        parser.error('--run-dir is required for retained-output modes')
    (evaluate if args.mode == 'evaluate' else review)(config, args.run_dir, args.output)


if __name__ == '__main__':
    main()
