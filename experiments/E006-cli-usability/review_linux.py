#!/usr/bin/env python3
"""Independently inspect the frozen E006 Linux return; never execute its workers.

Reads an already safely extracted return plus the original archive/checksum/log
and collection receipt. Recounts retained DNA, arrays, assignments and schedules
without importing the binner, training, inference, clustering or remote access.
Writes one exclusive compact review receipt. NumPy is the sole non-stdlib reader.
"""
import argparse
from collections import Counter
import csv
import hashlib
import json
from pathlib import Path
import re
import tarfile

import numpy as np

PROJECT = Path(__file__).resolve().parents[2]
STAGES = ('features', 'train', 'raw-embed', 'raw-cluster', 'raw-export',
          'learned-embed', 'learned-cluster', 'learned-export')
FOLDERS = ('features', 'training', 'raw/embedding', 'raw/clustering', 'raw/bins',
           'learned/embedding', 'learned/clustering', 'learned/bins')
BOUNDS = (1, 500, 768, 1000, 2500, 10000)


def load(path):
    """Read a retained JSON record, never evaluate returned code."""
    return json.loads(Path(path).read_text())


def normalized(inventory):
    """Compare distribution names using their canonical punctuation and case."""
    result = {re.sub(r'[-_.]+', '-', k.lower()): v for k,v in inventory.items()}
    assert len(result) == len(inventory), 'Duplicate normalized distribution names'
    return result


def record(path):
    """Hash one regular file incrementally; reject links/missing evidence."""
    path = Path(path)
    assert path.is_file() and not path.is_symlink(), path
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for part in iter(lambda: stream.read(1024*1024), b''):
            h.update(part)
    return dict(bytes=path.stat().st_size, sha256=h.hexdigest())


def check_files(root, files):
    """Check a byte-bound inventory including safe relative member names."""
    for name, expected in files.items():
        relative = Path(name)
        assert not relative.is_absolute() and '..' not in relative.parts, name
        path = root/relative
        assert not any((root/Path(*relative.parts[:i])).is_symlink()
                       for i in range(1, len(relative.parts)+1)), name
        assert record(path) == expected, name


def fasta(path):
    """Parse retained FASTA independently, preserving order and duplicate detection."""
    rows = {}
    ident = None
    for line in Path(path).read_text().splitlines():
        if line.startswith('>'):
            ident = line[1:].split()[0]
            assert ident not in rows, ident
            rows[ident] = ''
        elif line.strip():
            assert ident is not None
            rows[ident] += line.strip().upper()
    assert all(rows.values())
    return rows


def arrays(path):
    """Load only non-pickled NPZ arrays and verify their sidecar byte hash."""
    meta = load(path.with_suffix('.json'))
    assert meta['sha256'] == record(path)['sha256']
    with np.load(path, allow_pickle=False) as data:
        return {k: data[k] for k in data.files}, meta


def recount_export(folder, source, feature, summary, partition):
    """Recount both complete DNA exports, status/reason/length and zero masks."""
    manifest = load(folder/'manifest.json')
    check_files(folder, manifest['files'])
    assert {p.name for p in folder.iterdir()} == set(manifest['files']) | {'manifest.json'}
    with (folder/'assignments.tsv').open() as stream:
        records = list(csv.DictReader(stream, delimiter='\t'))
    assert [r['contig_id'] for r in records] == list(source)
    exported, buckets = {}, {}
    for name in manifest['files']:
        if name.endswith('.fna'):
            for ident, dna in fasta(folder/name).items():
                assert ident not in exported
                exported[ident], buckets[ident] = dna, Path(name).stem
    assert exported == source, 'Missing/changed/duplicated exported DNA'
    statuses = {s: dict(contigs=0, bp=0) for s in ('assigned', 'unassigned', 'excluded')}
    reasons = {s: Counter() for s in statuses}
    bins = {}
    strata = [dict(lower_bp=lo, upper_bp=BOUNDS[i+1] if i < 5 else None,
                   contigs=0, bp=0, statuses={s: dict(contigs=0, bp=0) for s in statuses}, reasons={})
              for i, lo in enumerate(BOUNDS)]
    for i, row in enumerate(records):
        ident, bp, status = row['contig_id'], int(row['length']), row['status']
        label = partition['assignment'][i]
        expected = 'excluded' if not feature['eligible'][i] else 'unassigned' if label < 0 else 'assigned'
        reason = str(feature['exclusion_reason'][i]) if expected == 'excluded' else partition['reason'][i]
        bucket = f'bin_{label+1:06d}' if expected == 'assigned' else expected
        assert status == expected and buckets[ident] == bucket and bp == len(source[ident])
        assert row['bin_id'] == (bucket if status == 'assigned' else '') and row['reason'] == reason
        statuses[status]['contigs'] += 1; statuses[status]['bp'] += bp
        if reason: reasons[status][reason] += 1
        if status == 'assigned':
            value = bins.setdefault(bucket, dict(contigs=0, bp=0))
            value['contigs'] += 1; value['bp'] += bp
        stratum = strata[max(j for j, lo in enumerate(BOUNDS) if bp >= lo)]
        stratum['contigs'] += 1; stratum['bp'] += bp
        stratum['statuses'][status]['contigs'] += 1; stratum['statuses'][status]['bp'] += bp
        if reason: stratum['reasons'][reason] = stratum['reasons'].get(reason, 0)+1
    assert summary['statuses'] == statuses and summary['bins'] == bins and summary['length_strata'] == strata
    assert summary['reasons'] == {s: dict(v) for s, v in reasons.items()}
    assert manifest['bins'] == summary['bin_count'] == len(bins)
    assert all(manifest[s] == statuses[s]['contigs'] for s in statuses)
    assert manifest['contigs'] == len(source) and manifest['bp'] == sum(map(len, source.values()))
    return dict(bin_count=len(bins), statuses=statuses, reasons=summary['reasons'])


def inspect_run(root, source, depth, remote_root):
    """Verify completed stage chains, native flags and arrays without recomputation."""
    manifest = load(root/'run-manifest.json'); summary = load(root/'run-summary.json')
    assert manifest['threads'] == 4 and manifest['memory_bytes'] == 8000000000
    assert manifest['source_files'] == {str(p.relative_to(PROJECT/'src/dl_binner')): record(p)
        for p in (PROJECT/'src/dl_binner').rglob('*') if p.is_file() and p.suffix in ('.py', '.json', '.smk')}
    feature, meta = arrays(root/'features/features.npz')
    ids = list(source); lengths = np.array([len(s) for s in source.values()])
    assert feature['ids'].tolist() == ids and np.array_equal(feature['lengths'], lengths)
    counts = np.array([sum(all(b in 'ACGT' for b in s[j:j+4]) for j in range(len(s)-3)) for s in source.values()])
    assert np.array_equal(feature['valid_fourmers'], counts)
    eligible = (lengths >= 500) & (counts > 0)
    assert np.array_equal(feature['eligible'], eligible)
    assert np.array_equal(feature['sequence_sha256'], [hashlib.sha256(s.encode()).hexdigest() for s in source.values()])
    assert np.isfinite(feature['tnf']).all() and feature['tnf'].shape == (len(ids), 136)
    assert np.allclose(feature['tnf'].sum(axis=1), (counts > 0).astype(float))
    assert np.array_equal(feature['depth'], depth)
    assert np.array_equal(feature['zero_depth'], depth == 0)
    assert np.array_equal(feature['depth_evidence'], (depth > 0).any(axis=1))
    training = load(root/'training/checkpoint.json')
    assert training['config'] == load(PROJECT/'experiments/E004-first-binner/training.json')
    assert [v['epoch'] for v in training['epochs']] == list(range(1, 21))
    assert all(v['contigs_seen'] == int(eligible.sum()) and np.isfinite(v['loss']) for v in training['epochs'])
    assert training['numerical_threads'] == 4 and training['torch_interop'] == 1 and training['loader_workers'] == 0
    assert all(v['num_threads'] == 4 for v in training['library_pools'])
    assert training['torch_version'] == '2.2.2+cpu'
    assert training['sha256'] == record(root/'training/checkpoint.pt')['sha256']
    ref, _ = arrays(root/'training/checkpoint.reference.npz')
    reload, _ = arrays(root/'learned/embedding/embeddings.npz')
    assert ref.keys() == reload.keys() and all(np.array_equal(ref[k], reload[k]) for k in ref)
    assert summary['checkpoint_reload_exact'] and summary['scientific_quality_assessed'] is False
    completion = load(root/'completion.json')
    check_files(root, completion['files']); check_files(root, completion['stage_receipts'])
    manifest_hash = record(root/'run-manifest.json')['sha256']
    assert completion['manifest_sha256'] == manifest_hash
    stages = []
    previous = None
    for i, (stage, folder) in enumerate(zip(STAGES, FOLDERS)):
        path = root/f'receipts/{i+1:02d}-{stage}.json'; receipt = load(path)
        check_files(root/folder, receipt['files']); check_files(root, receipt['evidence_files'])
        assert {str(p.relative_to(root/folder)) for p in (root/folder).rglob('*') if p.is_file()} == set(receipt['files'])
        assert receipt['stage'] == stage and receipt['manifest_sha256'] == manifest_hash
        assert receipt['previous_receipt_sha256'] == previous
        previous = record(path)['sha256']
        resource = receipt['resources']; argv = resource['command']
        assert resource['exit_code'] == 0 and resource['stop_reason'] is None
        assert resource['peak_sampled_rss_bytes'] <= 8000000000
        assert '-I' in argv and '-B' in argv and argv[argv.index('--threads')+1] == '4'
        assert argv[0] == manifest['binner_python']
        stages.append(receipt)
    assert all(a['end_monotonic_ns'] <= b['start_monotonic_ns'] for a, b in zip(stages, stages[1:]))
    # Summary's absolute source locators refer to the returned attempt, not this extraction.
    attempt = next(p for p in root.parents if p.name == remote_root.name)
    for name, expected in summary['source_files'].items():
        assert record(attempt/Path(name).relative_to(remote_root)) == expected
    arms = {}
    for arm in ('raw', 'learned'):
        embedding, emeta = arrays(root/f'{arm}/embedding/embeddings.npz')
        assert embedding['ids'].tolist() == ids and np.isfinite(embedding['features']).all()
        assert emeta['features_sha256'] == record(root/'features/features.npz')['sha256']
        assert emeta['feature_manifest_sha256'] == record(root/'features/features.json')['sha256']
        assert emeta['checkpoint_sha256'] == (training['sha256'] if arm == 'learned' else None)
        partition = load(root/f'{arm}/clustering/partition.json')
        assert partition['ids'] == ids and partition['clustering'] == dict(expected_cluster_count=None, k=5, min_size=3,
            mutual=True, positive_weights=True, query_block=128, resolution=1.0)
        assert partition['embedding_sha256'] == record(root/f'{arm}/embedding/embeddings.npz')['sha256']
        assert partition['embedding_manifest_sha256'] == record(root/f'{arm}/embedding/embeddings.json')['sha256']
        export = load(root/f'{arm}/bins/manifest.json')
        assert export['partition_sha256'] == record(root/f'{arm}/clustering/partition.json')['sha256']
        assert export['features_sha256'] == record(root/'features/features.npz')['sha256']
        value = summary['arms'][arm]
        assert value['masks']['eligible_contigs'] == int(eligible.sum())
        assert value['masks']['all_zero_depth_contigs'] == (int((~feature['depth_evidence']).sum()) if depth.shape[1] else None)
        assert value['masks']['zero_depth_by_sample'] == {s: int(feature['zero_depth'][:, j].sum()) for j,s in enumerate(meta['samples'])}
        arms[arm] = recount_export(root/f'{arm}/bins', source, feature, value, partition)
    return dict(contigs=len(ids), bp=int(lengths.sum()), masks=summary['arms']['raw']['masks'],
                arms=arms, native_stage_count=len(stages), checkpoint_reload_exact=True,
                training_seconds=training['training_wall_seconds'], training_average_cpus=training['training_average_cpus'])


def main(args):
    """Produce acceptance only after all independent checks and native assertions agree."""
    root = args.root; remote_root = Path('/work/Home/dl_binner/e006')/root.name
    archive = record(args.archive)
    assert args.checksum.read_text().split() == [archive['sha256'], args.archive.name]
    with tarfile.open(args.archive) as tf:
        members = tf.getmembers()
        assert len({m.name for m in members}) == len(members)
        assert all(m.isfile() and not Path(m.name).is_absolute() and '..' not in Path(m.name).parts for m in members)
        for member in members:
            assert (root.parent/member.name).read_bytes() == tf.extractfile(member).read()
    inventory = load(root/'retained-files.json')['files']; check_files(root, inventory)
    extras = {str(p.relative_to(root)) for p in root.rglob('*') if p.is_file()} - set(inventory)
    assert extras == {'retained-files.json'} | {str(p.relative_to(root)) for p in root.rglob('terminal.log')}
    status = load(root/'status.json'); collection = load(args.collection)
    assert status['native_linux'] and status['exit_code'] == collection['exit_code'] == 0
    assert status['allocated_vcpus'] == 4 and status['allocated_ram_gb'] == 12
    assert status['source_commit'] == 'a8010cb4b4ded237a1f2d4c0b1cfc82a385cb809'
    assert collection['archive_bytes'] == archive and collection['retained_files'] == len(members)
    archive_logical_bytes = sum(m.size for m in members)
    # Executed collector excluded the inventory itself and statted the live
    # parent log after printing return locators. Preserve its report; correct
    # storage from the immutable archive, not the subsequently growing file.
    inventory_bytes = record(root/'retained-files.json')['bytes']
    log_growth = collection['retained_logical_bytes']-(archive_logical_bytes-inventory_bytes)
    assert log_growth >= 0
    assert collection['driver_seconds_through_collection'] < 1800+120
    assert np.isclose(collection['allocated_vcpu_hours_through_collection'], 4*collection['driver_seconds_through_collection']/3600)
    terminal = args.terminal.read_text()
    assert 'EXIT_CODE=0' in terminal and 'COLLECTION_STATUS='+json.dumps(collection, sort_keys=True) in terminal
    packet = PROJECT/'artifacts/e006-cli-usability/transfer/v1/e006-linux-smoke-v1.tar.gz'
    with tarfile.open(packet) as tf:
        assert tf.extractfile('e006-linux-smoke/bundle-manifest.json').read() == (root/'bundle-manifest.json').read_bytes()
    baseline = load(PROJECT/'experiments/E006-cli-usability/runtime-baseline.json')
    accepted = load(root/'accepted-runtime.json'); after = load(root/'readonly-after.json')
    assert after['unchanged'] and status['readonly_dependency_bytes_unchanged']
    for role in ('binner', 'workflow'):
        inv = accepted[role]['inventory']; expected = baseline[role]
        assert inv['distributions'] == normalized(expected['distributions']) and inv['origins'] == expected['origins']
        assert inv['executable'] == expected['python'] and inv['python_version'] == expected['python_version']
        assert inv['prefix'] == str(Path(expected['python']).parent.parent) and inv['native_linux']
        assert load(root/f'{role}-readonly-before.json') == after['bindings'][role]
    new = json.loads(next(v.split('=', 1)[1] for v in (root/'stages/new-package-probe.log').read_text().splitlines() if v.startswith('INVENTORY_JSON=')))
    expected = normalized(baseline['binner']['distributions']); expected['dl-binner'] = '0.1.0.dev1'
    assert new['distributions'] == expected and new['prefix'] == status['package_prefix']
    assert new['torch_cuda'] is None and new['torch_version'] == '2.2.2+cpu' and new['torch_threads'] == 4 and new['interop'] == 1
    assert all(v['num_threads'] == 4 for v in new['pools'])
    assert new['origins']['dl_binner'].startswith(new['prefix']+'/')
    assert all(v == baseline['binner']['origins'][k] for k,v in new['origins'].items() if k != 'dl_binner')
    links = load(root/'dependency-links.json')['links']
    assert not any(k == 'dl_binner' or k.startswith('dl_binner-') or k.endswith('.pth') for k in links)
    assert all(v.startswith(after['bindings']['binner']['root']+'/') for v in links.values())
    source = fasta(root/'smoke/fixture inputs/assembly.fna')
    assert len(source) == 13 and sum(map(len, source.values())) == 42311
    assert record(root/'smoke/fixture inputs/assembly.fna') == load(PROJECT/'experiments/E006-cli-usability/linux-smoke.json')['input_files']['assembly.fna']
    with (root/'smoke/fixture inputs/mean-depth.tsv').open() as stream:
        depth_rows = list(csv.reader(stream, delimiter='\t'))
    assert depth_rows[0] == ['contig_id','software_S1','software_S2']
    by_id = {r[0]: list(map(float,r[1:])) for r in depth_rows[1:]}
    assert len(by_id) == len(depth_rows)-1 and set(by_id) == set(source)
    results = {}
    for name, data, depths in (('sequence run', source, np.empty((13,0))),
                             ('depth run', source, np.array([by_id[i] for i in source])),
                             ('empty partition', fasta(root/'smoke/fixture inputs/empty-partition.fna'), np.empty((4,0)))):
        results[name] = inspect_run(root/'smoke'/name, data, depths, remote_root)
    observation = load(root/'smoke/observed.json'); cases = observation['cases']
    assert observation['status'] == 'passed' and observation['workers_mocked'] == [] and len(cases) == 21
    for name, case in cases.items():
        if name.startswith('supervisor-'): continue
        assert record(root/'smoke'/f'{name}.log') == case['log']
        assert load(root/'smoke'/f'{name}.exit.json') == case['receipt']
        assert not case['intended_message'] or case['intended_message'] in (root/'smoke'/f'{name}.log').read_text()
    fatal = cases['supervisor-fatal']; memory = cases['supervisor-memory']
    assert fatal['exit_code'] == 7 and fatal['wall_seconds'] < 5 and fatal['stop_reason'] is None
    assert 'intended fatal worker' in (root/'smoke/fatal-supervisor.log').read_text()
    assert 'MemoryError: Sampled working RSS' in memory['stop_reason'] and memory['wall_seconds'] < 5
    assert any('Still running (10s' in line and 'heartbeat-supervisor.log' in line for line in terminal.splitlines())
    stops = [load(p) for p in (root/'smoke/overall-timeout/logs').glob('invocation-*/*.exit.json')]
    assert any('wall-time limit' in (v['stop_reason'] or '') for v in stops)
    assert all('Cleanup failed' not in (v['stop_reason'] or '') for v in stops)
    invocations = {}
    for path in (root/'smoke/depth run/logs').glob('invocation-*/status.json'):
        value = load(path); native = sorted(p.name for p in path.parent.glob('*.native.log'))
        if value['status'] == 'partial': assert native == ['01-features.native.log','02-train.native.log']
        elif value['status'] == 'completed': assert native == [f'{i+1:02d}-{s}.native.log' for i,s in enumerate(STAGES) if i >= 2]
        else: assert native == []
        invocations[path.parent.name] = dict(status=value['status'], native_logs=native)
    assert Counter(v['status'] for v in invocations.values()) == dict(partial=1, completed=1, reused_complete=1, failed=4)
    for name in ('scheduler-cpu','scheduler-memory'):
        times = [load(root/'smoke'/name/f'{v}.json') for v in ('a','b')]
        assert min(v['end'] for v in times) <= max(v['start'] for v in times)
        argv = cases[name]['receipt']['command']
        assert '--jobs' not in argv and argv[argv.index('--cores')+1] == '4' and 'mem_mb=global' in argv
    resource = [load(p) for p in (root/'stages').glob('*.exit.json')]
    assert all(v['exit_code'] == 0 and v['stop_reason'] is None for v in resource)
    assert all('-I' in v['command'] and '-B' in v['command'] for v in resource)
    peak = max(v['peak_sampled_rss_bytes'] for v in resource)
    assert peak < 8000000000
    suite = load(root/'stages/generic-native-contracts.exit.json')
    result = dict(status='accepted', date='2026-10-06', scope='Native Linux generic command software contracts only',
        sources={str(p.absolute().relative_to(PROJECT)): record(p) for p in (args.archive,args.checksum,args.terminal,args.collection)},
        review_source=record(Path(__file__)), source_commit=status['source_commit'],
        package_prefix=status['package_prefix'], workflow_python=baseline['workflow']['python'],
        packet_sha256=record(packet)['sha256'], verified_inventory_files=len(inventory), archive_files=len(members),
        read_only_trees=after['bindings'], dependencies_verified_read_only=True,
        runs=results, cases=list(cases), native_workers_mocked=[], depth_resume_invocations=invocations,
        cost=collection, storage_correction=dict(reported_logical_bytes=collection['retained_logical_bytes'],
            archived_logical_bytes=archive_logical_bytes, omitted_inventory_bytes=inventory_bytes,
            later_parent_log_growth_bytes=log_growth,
            reason='Executed collector omits its own inventory and stats an open log after archive creation'),
        peak_sampled_rss_bytes=peak, native_suite_resources=suite,
        limitations=['No biological/MAG-quality/generalization or bulk-scaling claim',
            'Stage /proc samples include coordinator; brief peaks/parent hashing outside stage samples not exact peaks',
            'Runtime byte trees are native retained before/after receipts; remote libraries not returned for local rehash',
            'Orphan absence is native suite ps assertion, not a retained process-list snapshot or current remote query',
            'Completed bytes are independently receipt-bound; mtime preservation is native suite assertion, not archive metadata',
            'Owned package-prefix/cache storage not inventoried in return; shared dependency bytes are pre-existing, not new storage',
            'Allocation time excludes owner upload/idle/teardown and is not an invoice'],
        next_step='One bounded private-PR readiness milestone; no science rerun, publication or architecture gate')
    with args.output.open('x') as stream:
        json.dump(result, stream, sort_keys=True, indent=2, allow_nan=False); stream.write('\n')
    print(json.dumps(dict(status=result['status'],files=len(inventory),runs=results,
        seconds=collection['driver_seconds_through_collection'],allocated_vcpu_hours=collection['allocated_vcpu_hours_through_collection'],
        peak_sampled_rss_bytes=peak), sort_keys=True))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('root', 'archive', 'checksum', 'terminal', 'collection', 'output'):
        parser.add_argument('--'+name, type=Path, required=True)
    main(parser.parse_args())
