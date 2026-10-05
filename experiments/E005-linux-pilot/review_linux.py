#!/usr/bin/env python3
"""Accept byte-bound Linux smoke evidence without repeating any native work.

Inputs are the returned archive/checksum, safely extracted attempt, terminal log
and the matching local smoke input. Inspect arrays and exports independently;
write a compact receipt. This checks software, not biological bin quality.
"""
import argparse
import csv
import json
from pathlib import Path
import re
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'scripts'))
from e005_smoke import sha, write
from dl_binner.io import load_arrays, read_fasta, validate_features


def inspect(attempt, archive, terminal, input_root):
    """Validate retained hashes, real axes/masks, inference parity and complete DNA."""
    attempt, archive, terminal, input_root = (p.resolve() for p in (attempt, archive, terminal, input_root))
    checksum = archive.with_name(archive.name+'.sha256')
    if sha(archive) != checksum.read_text().split()[0]:
        raise ValueError('Return checksum mismatch')
    retained = json.loads((attempt/'retained-files.json').read_text())
    for entry in retained['files']:
        path = attempt/entry['path']
        if not path.resolve().is_relative_to(attempt.resolve()):
            raise ValueError('Unsafe retained path')
        if sha(path) != entry['sha256'] or path.stat().st_size != entry['bytes']:
            raise ValueError('Retained file mismatch: '+entry['path'])
    status = json.loads((attempt/'status.json').read_text())
    if status['status'] != 'passed' or not status['native_linux']:
        raise ValueError('Native Linux gate did not pass')
    bundle = json.loads((attempt/'bundle-manifest.json').read_text())
    if status['source_commit'] != '2f0b9a58bcf86f29f23b0f3bed16f31171a359f4':
        raise ValueError('Unexpected smoke source')
    for name, item in bundle['files'].items():
        if name.startswith('input/smoke/'):
            path = input_root/Path(name).name
        elif name.startswith(('scripts/', 'workflows/', 'experiments/')):
            # The executed snapshot remains recoverable in Git even if live docs change.
            import subprocess
            content = subprocess.check_output(['git', 'show', status['source_commit']+':'+name], cwd=ROOT)
            import hashlib
            if hashlib.sha256(content).hexdigest() != item['sha256']:
                raise ValueError('Executed source hash mismatch: '+name)
            continue
        else:
            continue
        if sha(path) != item['sha256'] or path.stat().st_size != item['bytes']:
            raise ValueError('Input hash mismatch')
    runtime = json.loads((attempt/'runtime.json').read_text())
    prefixes = []
    normalize = lambda n: re.sub(r'[-_.]+', '-', n).lower()
    for role in ('binner', 'workflow'):
        inv = runtime[role]['inventory']
        prefix = Path(inv['prefix'])
        prefixes.append(prefix)
        if inv['python'].split()[0] != '3.12.10' or inv['affinity'] != [0, 1, 2, 3]:
            raise ValueError('Interpreter/affinity mismatch')
        if inv['base_prefix'] != str(prefix) or not all(Path(p).is_relative_to(prefix) for p in inv['origins'].values()):
            raise ValueError('Runtime origin contamination')
        lock = (ROOT/f'experiments/E005-linux-pilot/{role}-linux.lock').read_text()
        expected = dict(line.split(' --hash=', 1)[0].split('==') for line in lock.splitlines()
                        if line and not line.startswith('#'))
        observed = {normalize(k): v for k, v in inv['distributions'].items()}
        if expected != observed:
            raise ValueError('Inventory differs from accepted lock')
        log = (attempt/f'stages/{role}-probe.log').read_text()
        if 'before_site' not in log or 'after_site' not in log or '/.local/' in log:
            raise ValueError('Pre-site isolation evidence missing')
    if prefixes[0] == prefixes[1]:
        raise ValueError('Shared runtime base')
    inv = runtime['binner']['inventory']
    if inv['torch_version'] != '2.2.2+cpu' or inv['torch_cuda'] is not None:
        raise ValueError('Unexpected CUDA/non-CPU build')
    if (inv['torch_threads'], inv['interop'], inv['loader_workers']) != (4, 1, 0) or any(p['num_threads'] != 4 for p in inv['pools']):
        raise ValueError('CPU budgets disagree')
    cfg = json.loads((attempt/'resolved-config.json').read_text())
    expected, smoke = cfg['expectations'], attempt/'smoke'
    data, meta = load_arrays(smoke/'features.npz', 'features')
    validate_features(data, meta)
    if data['ids'].tolist() != expected['ids'] or meta['samples'] != expected['samples']:
        raise ValueError('Sample/contig axes differ')
    np.testing.assert_array_equal(data['depth'], expected['depth'])
    np.testing.assert_array_equal(data['zero_depth'], data['depth'] == 0)
    np.testing.assert_array_equal(data['depth_evidence'], (data['depth'] > 0).any(1))
    np.testing.assert_array_equal(data['eligible'], expected['eligible'])
    fresh, _ = load_arrays(smoke/'fresh.npz', 'features')
    at = [expected['ids'].index(i) for i in fresh['ids']]
    for key in ('tnf', 'valid_fourmers'):
        np.testing.assert_array_equal(fresh[key], data[key][at])
    learned, _ = load_arrays(smoke/'learned.embeddings.npz', 'embeddings')
    reference, _ = load_arrays(smoke/'checkpoint.reference.npz', 'embeddings')
    for key in ('ids', 'features', 'evidence'):
        np.testing.assert_array_equal(learned[key], reference[key])
    source = dict(read_fasta(input_root/'assembly.fna'))
    accounting = {}
    for mode in ('raw', 'learned'):
        folder, found = smoke/(mode+'.export'), {}
        for path in folder.glob('*.fna'):
            for ident, dna in read_fasta(path) if path.stat().st_size else []:
                if ident in found:
                    raise ValueError('Duplicate DNA export')
                found[ident] = dna
        if found != source:
            raise ValueError('Export lost/changed DNA')
        with (folder/'assignments.tsv').open() as stream:
            rows = list(csv.DictReader(stream, delimiter='\t'))
        if [r['contig_id'] for r in rows] != expected['ids']:
            raise ValueError('Incomplete/reordered assignments')
        for row, eligible, reason in zip(rows, expected['eligible'], expected['exclusion_reason']):
            if not eligible and (row['status'], row['reason']) != ('excluded', reason):
                raise ValueError('Exclusion reason lost')
        accounting[mode] = {k: sum(r['status'] == k for r in rows) for k in ('assigned', 'unassigned', 'excluded')}
    training = json.loads((smoke/'checkpoint.json').read_text())
    if sha(smoke/'checkpoint.pt') != training['sha256'] or (training['numerical_threads'], training['torch_interop'], training['loader_workers']) != (4, 1, 0):
        raise ValueError('Checkpoint/resource mismatch')
    if len(training['epochs']) != 20 or any(e['contigs_seen'] != 12 for e in training['epochs']):
        raise ValueError('Native schedule/eligible rows differ')
    failure = json.loads((attempt/'failure-checks/verified.json').read_text())
    if failure['status'] != 'passed' or any(v['exit_code'] == 0 or v['seconds'] >= 10 for v in failure['cases'].values()):
        raise ValueError('Fatal CLI failure checks did not stop')
    if 'Nothing to be done' not in (attempt/'stages/completed-resume.log').read_text():
        raise ValueError('Completed work scheduled again')
    if status['allocated_vcpus'] != 4 or status['allocated_ram_gb'] != 12 or len(status['affinity']) != 4:
        raise ValueError('Allocation mismatch')
    for stage in status['stages']:
        if stage['exit_code'] != 0 or stage['stop_reason'] or stage['peak_sampled_rss_bytes'] > 8_000_000_000:
            raise ValueError('Stage/resources failed')
    lines = [json.loads(l) for l in terminal.read_text().splitlines() if l.startswith('{')]
    cost = next(v for v in lines if v['stage'] == 'cost_through_collection')
    if abs(cost['allocated_vcpu_hours']-4*cost['driver_seconds']/3600) > 1e-10 or cost['driver_seconds'] > 3600:
        raise ValueError('Cost/ceiling mismatch')
    return dict(record='E005', date='2026-10-05', decision='native Linux software smoke accepted; do not repeat',
        archive=dict(locator=str(archive.relative_to(ROOT)), bytes=archive.stat().st_size, sha256=sha(archive)),
        terminal=dict(locator=str(terminal.relative_to(ROOT)), sha256=sha(terminal)), source_commit=status['source_commit'],
        retained_files=len(retained['files']), retained_logical_bytes=sum(e['bytes'] for e in retained['files']),
        accounting=accounting, contigs=len(source), bp=sum(map(len, source.values())), samples=meta['samples'],
        reload_max_abs=0, epochs=20, runtime=runtime, stages=status['stages'], failure_checks=failure,
        actual_cost=cost, actual_training={k: training[k] for k in ('numerical_threads', 'torch_interop', 'loader_workers',
            'parameter_count', 'training_wall_seconds', 'training_process_cpu_seconds', 'training_average_cpus')},
        pilot_assets=json.loads((attempt/'pilot-asset-locators.json').read_text()),
        limitations=['synthetic depth, no bin-quality result', 'tiny stage timing is not bulk throughput',
          'sampled RSS/CPU are not exact peaks or invoice; owner idle/upload excluded',
          'prefix/payload disk usage not returned; retained inventory excludes open terminal and itself'])


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    for name in ('attempt', 'archive', 'terminal', 'input-root', 'output'):
        p.add_argument('--'+name, type=Path, required=True)
    a = p.parse_args()
    result = inspect(a.attempt, a.archive, a.terminal, a.input_root)
    write(a.output, result)
    print(json.dumps(dict(decision=result['decision'], retained_files=result['retained_files'],
                         accounting=result['accounting'], actual_cost=result['actual_cost'])))
