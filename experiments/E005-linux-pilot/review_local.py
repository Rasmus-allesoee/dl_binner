#!/usr/bin/env python3
"""Publish E005 deployment receipts from retained evidence without rerunning work.

Verify transfer/return checksums and retained file inventories, native cache axes,
checkpoint parity, complete exports and failure stops. These are Mac software
fixtures, not Linux acceptance, biological scores or a performance benchmark.
"""
import argparse
import csv
import json
from pathlib import Path
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'scripts'))
from e005_smoke import sha, write
from dl_binner.io import load_arrays, read_fasta, validate_features


def inspect(attempt):
    """Validate one retained attempt and compact its status/cost/contract evidence."""
    attempt = Path(attempt)
    state = json.loads((attempt/'status.json').read_text())
    archive = attempt.with_name(attempt.name+'-return.tar.gz')
    checksum = archive.with_name(archive.name+'.sha256')
    if sha(archive) != checksum.read_text().split()[0]:
        raise ValueError('Return archive checksum mismatch')
    inventory = json.loads((attempt/'retained-files.json').read_text())
    for entry in inventory['files']:
        path = attempt/entry['path']
        if sha(path) != entry['sha256'] or path.stat().st_size != entry['bytes']:
            raise ValueError('Retained file mismatch: '+str(path))
    value = dict(locator=str(attempt.relative_to(ROOT)), status=state['status'],
                 source_commit=state.get('source_commit'), native_linux=state.get('native_linux', False),
                 declared_local_thread_budget=state['allocated_vcpus'],
                 driver_seconds_before_collection=state['driver_seconds_before_collection'],
                 declared_thread_wall_hours=state['allocated_vcpu_hours_before_collection'],
                 return_sha256=sha(archive), return_bytes=archive.stat().st_size,
                 retained_inventory_sha256=sha(attempt/'retained-files.json'),
                 retained_files=len(inventory['files']), retained_logical_bytes=sum(e['bytes'] for e in inventory['files']))
    if state['status'] != 'passed':
        value.update(error=state['error'], checkpoint_created=(attempt/'smoke/checkpoint.pt').exists())
        native = attempt/'stages/native-smoke.json'
        if native.exists():
            value['native_stage'] = json.loads(native.read_text())
        return value
    if state['native_linux']:
        raise ValueError('This collector owns local-only observations, not Linux acceptance')
    smoke = attempt/'smoke'
    verified = json.loads((smoke/'verified.json').read_text())
    if verified['status'] != 'passed' or verified['reload_max_abs'] != 0:
        raise ValueError('Native smoke/parity failed')
    data, meta = load_arrays(smoke/'features.npz', 'features')
    validate_features(data, meta)
    config = json.loads((attempt/'resolved-config.json').read_text())
    original = dict(read_fasta(config['fasta']))
    learned, _ = load_arrays(smoke/'learned.embeddings.npz', 'embeddings')
    reference, _ = load_arrays(smoke/'checkpoint.reference.npz', 'embeddings')
    np.testing.assert_array_equal(learned['ids'], reference['ids'])
    np.testing.assert_array_equal(learned['features'], reference['features'])
    if data['ids'].tolist() != config['expectations']['ids'] or meta['samples'] != ['smoke_A', 'smoke_B']:
        raise ValueError('Axis mismatch')
    accounting = {}
    for mode in ('raw', 'learned'):
        folder, found = smoke/(mode+'.export'), {}
        for path in folder.glob('*.fna'):
            for ident, dna in read_fasta(path) if path.stat().st_size else []:
                if ident in found:
                    raise ValueError('Duplicate exported ID')
                found[ident] = dna
        if found != original:
            raise ValueError('Export loss')
        with (folder/'assignments.tsv').open() as stream:
            rows = list(csv.DictReader(stream, delimiter='\t'))
        accounting[mode] = {kind: sum(r['status'] == kind for r in rows) for kind in ('assigned', 'unassigned', 'excluded')}
        if len(rows) != 14 or accounting[mode]['excluded'] != 2:
            raise ValueError('Exclusion accounting lost')
    training = json.loads((smoke/'checkpoint.json').read_text())
    if training['numerical_threads'] != state['allocated_vcpus'] or training['loader_workers'] != 0 or training['torch_interop'] != 1:
        raise ValueError('Effective resource plan mismatch')
    for epoch in training['epochs']:
        if epoch['contigs_seen'] != 12:
            raise ValueError('Eligible row omitted in training')
    if 'Nothing to be done' not in (attempt/'stages/completed-resume.log').read_text():
        raise ValueError('Completed stages rescheduled')
    failure = json.loads((attempt/'failure-checks/verified.json').read_text())
    if failure['status'] != 'passed' or any(c['exit_code'] == 0 or c['seconds'] >= 10 for c in failure['cases'].values()):
        raise ValueError('Fatal input/overwrite contract failed')
    value.update(checks=verified, accounting=accounting, contigs=14, bp=sum(len(s) for s in original.values()),
                 eligible=12, samples=meta['samples'], checkpoint_sha256=sha(smoke/'checkpoint.pt'),
                 actual_training={k: training[k] for k in ('numerical_threads', 'loader_workers', 'torch_interop',
                     'parameter_count', 'training_wall_seconds', 'training_process_cpu_seconds', 'training_average_cpus', 'library_pools')},
                 stages=state['stages'], failure_checks=failure,
                 runtime_inventory_sha256=sha(attempt/'runtime.json'))
    return value


def main(output):
    """Collect the fixed local attempts and final immutable transfer receipt."""
    base = ROOT/'artifacts/e005-linux-pilot'
    attempts = []
    for folder in ('local-owner-v1', 'local-owner-v2', 'local-owner-fatal'):
        for status in sorted((base/folder).glob('linux-smoke-*/status.json')):
            attempts.append(inspect(status.parent))
    final = [a for a in attempts if '/local-owner-v2/' in a['locator']]
    if len(final) != 1 or final[0]['status'] != 'passed':
        raise ValueError('Final v2 native local harness is not accepted')
    archive = base/'transfer-v2/e005-linux-smoke-v2.tar.gz'
    if sha(archive) != archive.with_name(archive.name+'.sha256').read_text().split()[0]:
        raise ValueError('Transfer checksum mismatch')
    write(output, dict(record='E005', date='2026-10-05', execution='local deployment fixtures complete; owner/Linux pending; pilot unrun',
        transfer=dict(archive=str(archive.relative_to(ROOT)), sha256=sha(archive), bytes=archive.stat().st_size,
                      source_commit=final[0]['source_commit']), attempts=attempts,
        scope=dict(native_workers_mocked=[], linux_bootstrap_or_ABI_executed=False,
                   real_upstream_archive_filesystem_test=True, target_wheel_dependency_closure=True,
                   local_platform='Mac, isolated binner Python 3.10.15 and workflow Python 3.13.12',
                   target_platform='Linux x86_64, separate standalone Python 3.12.10 prefixes',
                   numerical_threads_tested=[1, 4], biology='not assessed; synthetic depth only',
                   retained_old_coordinator='read-only rejected preflight; missing setuptools; not modified',
                   costs='local declared-thread budgets; not UCloud billing; prefix creation outside driver clock')))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    main(args.output)
