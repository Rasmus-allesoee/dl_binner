#!/usr/bin/env python3
"""Review retained E007 software receipts without running any native/scientific stage.

Requires the ignored local E007 attempts and copied outside-repository evidence.
Checks byte/provenance and intended outcomes, then writes one exclusive compact
acceptance record. This evidence review is separate from ordinary product tests;
it does not establish standalone Linux CI or biological utility.
"""
import argparse
import hashlib
import json
from pathlib import Path
import stat
import subprocess

ROOT = Path(__file__).absolute().parents[2]


def record(path):
    """Bind retained regular-file bytes without reading the entire payload into RAM."""
    path = Path(path)
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for part in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(part)
    return dict(bytes=path.stat().st_size, sha256=h.hexdigest())


def read(path):
    """Read a retained JSON receipt; absence or malformed data is a failed review."""
    return json.loads(Path(path).read_text())


def storage(path):
    """Count owned regular bytes and links, excluding their external targets."""
    total = files = links = 0
    for p in Path(path).rglob('*'):
        mode = p.lstat().st_mode
        if stat.S_ISREG(mode):
            files += 1
            total += p.stat().st_size
        elif stat.S_ISLNK(mode):
            links += 1
    return dict(regular_files=files, regular_bytes=total, symbolic_links=links,
                scope='Closed retained files; no link target bytes, filesystem blocks or old external caches')


def main():
    """Bind local acceptance to immutable attempts, built artifacts and test receipts."""
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    base = ROOT / 'artifacts/e007-pr-readiness'
    protocol = read(ROOT / 'experiments/E007-pr-readiness/protocol.json')
    for name, expected in protocol['unchanged_package_files'].items():
        assert record(ROOT / name) == expected, name
    accepted = protocol['accepted_wheel']
    assert record(ROOT / accepted['path']) == {k: accepted[k] for k in ('bytes', 'sha256')}
    attempts = {}
    for name, status in [('run-001', 'failed'), ('run-002', 'failed'), ('run-003', 'passed')]:
        root = base / name
        data = read(root / 'observed.json')
        assert data['status'] == status
        before, after = read(root / 'base-readonly-before.json'), read(root / 'base-readonly-after.json')
        assert after['unchanged'] and before == after['bindings']
        stages = [read(f) for f in sorted((root / 'stages').glob('*.exit.json'))]
        # Include run-001's failed-stage file omitted by its original summary.
        attempts[name] = dict(status=status, source_commit=data['source_commit'],
            seconds=data['seconds'], receipt=record(root / 'observed.json'),
            peak_sampled_stage_rss_bytes=max(v['peak_sampled_rss_bytes'] for v in stages),
            base_libraries_unchanged=True, retained_storage=storage(root))
    run = base / 'run-003'
    cache = read(run / 'cache-inputs.json')
    assert all(record(name) == value for name, value in cache.items())
    inspection = read(run / 'inspection.json')
    assert inspection['status'] == 'passed' and inspection['accepted_package_bytes_unchanged']
    assert 'RECORD bytes changed' in read(run / 'damaged-wheel-check.json')['intended_failure']
    runtimes = {}
    for role in ('build', 'binner', 'workflow'):
        value = read(run / (role + '-runtime.json'))
        assert value['status'] == 'passed' and not value['user_site_enabled']
        assert all(Path(v).is_relative_to(Path(value['prefix'])) for v in value['origins'].values())
        runtimes[role] = dict(python=value['python_version'], distributions=value['distributions'],
                             receipt=record(run / (role + '-runtime.json')), imports_owned=True)
    binner = read(run / 'binner-runtime.json')
    assert binner['torch_threads'] == 4 and binner['torch_interop'] == 1 and binner['torch_cuda'] is None
    suites = {}
    for name, root, threads in [('four-thread', run / 'product', 4),
                                ('outside-two-thread', base / 'external-two-thread-001/product', 2)]:
        result = read(root / 'product-tests.exit.json')
        data = read(root / 'native-run/observed.json')
        log = (root / 'product-tests.log').read_text()
        assert result['exit_code'] == 0 and result['stop_reason'] is None and '\nOK\n' in log
        assert 'Ran 11 tests' in log and 'skipped=' not in log
        assert data['status'] == 'passed' and len(data['cases']) == 18 and data['workers_mocked'] == []
        assert data['fixture']['contigs'] == 13 and data['fixture']['bp'] == 42311
        for mode in ('sequence', 'depth'):
            summary = read(root / 'native-run' / (mode + ' run') / 'run-summary.json')
            assert summary['checkpoint_reload_exact'] and not summary['scientific_quality_assessed']
            for arm in ('raw', 'learned'):
                s = summary['arms'][arm]
                assert sum(v['contigs'] for v in s['statuses'].values()) == 13
                assert sum(v['bp'] for v in s['statuses'].values()) == 42311
                assert len(s['length_strata']) == 6 and all(v['contigs'] for v in s['length_strata'])
                assert s['reasons']['excluded'] == {'below_min_length': 2, 'no_valid_fourmers': 1}
                assert s['masks']['all_zero_depth_contigs'] == (3 if mode == 'depth' else None)
        cases = data['cases']
        assert cases['supervisor-fatal']['exit_code'] == 7 and cases['supervisor-fatal']['wall_seconds'] < 5
        assert 'MemoryError: Sampled working RSS' in cases['supervisor-memory']['stop_reason']
        # Supervisor progress is parent output, retained by the enclosing suite;
        # the individual worker log contains only that child's stdout/stderr.
        assert any('Still running (' in line and 'heartbeat-supervisor.log' in line for line in log.splitlines())
        orphan = read(root / 'native-run/orphan-status.json')
        assert not orphan['state'] or orphan['state'].startswith('Z')
        for scheduler in ('cpu', 'memory'):
            intervals = cases['scheduler-' + scheduler]['intervals']
            assert min(v['end'] for v in intervals) <= max(v['start'] for v in intervals)
        suites[name] = dict(tests=11, native_cases=18, threads=threads, skipped=0,
            seconds=result['wall_seconds'], peak_sampled_rss_bytes=result['peak_sampled_rss_bytes'],
            receipt=record(root / 'product-tests.exit.json'), native_receipt=record(root / 'native-run/observed.json'),
            fatal_seconds=cases['supervisor-fatal']['wall_seconds'], orphan_state=orphan['state'],
            fixture=data['fixture'], scientific_quality_assessed=False)
    outside = read(base / 'external-two-thread-001/invocation.json')
    assert outside['status'] == 'passed' and not Path(outside['output']).is_relative_to(ROOT)
    assert outside['cwd'] == '/private/tmp'
    preflight = read(base / 'artifact-preflight-001/observed.json')
    assert preflight['status'] == 'passed'
    total = sum(v['seconds'] for v in attempts.values()) + preflight['seconds'] + outside['wall_seconds']
    assert total < protocol['integration_seconds_max']
    tracked = subprocess.check_output(['git', 'ls-files'], cwd=ROOT, text=True).splitlines()
    assert not any(v.startswith(('agent_context/', 'artifacts/')) for v in tracked)
    historical = subprocess.check_output(['git', 'rev-list', '--objects', 'HEAD'], cwd=ROOT, text=True).splitlines()
    history = [line.partition(' ')[2] for line in historical if line.partition(' ')[2].startswith('agent_context/')]
    value = dict(status='accepted-local-private-pr-readiness', scientific_quality_assessed=False,
        source_commit=attempts['run-003']['source_commit'], accepted_source=protocol['accepted_package_source'],
        accepted_wheel=accepted, protocol=record(ROOT / 'experiments/E007-pr-readiness/protocol.json'),
        artifacts={k: {**{f: v for f, v in inspection[k].items() if f != 'path'},
                       'path': str(Path(inspection[k]['path']).relative_to(ROOT))} for k in ('wheel', 'sdist', 'rebuilt_wheel')},
        wheel_members=len(inspection['wheel_members']), sdist_files=len(inspection['sdist_members']),
        logical_rebuild_equal=True, unchanged_package_files=len(protocol['unchanged_package_files']),
        attempts=attempts, artifact_only_preflight_seconds=preflight['seconds'],
        outside_two_thread_parent_seconds=outside['wall_seconds'], suites=suites, runtimes=runtimes,
        campaign_seconds=total, campaign_four_thread_upper_budget_hours=4 * total / 3600,
        campaign_budget_hours=(4 * (total - outside['wall_seconds']) + 2 * outside['wall_seconds']) / 3600,
        campaign_scope='Known serial measured attempts, artifact preflight and outside test invocation. Source development, dependency acquisition, review/debug/idle and this retained review excluded. Local thread-budget wall hours, not CPU time or provider billing.',
        rss_scope='Sampled stage process trees; no exact peak or continuous between-stage parent/hash sampling',
        cache_inputs=dict(files=len(cache), bytes=sum(v['bytes'] for v in cache.values()), unchanged=True,
                          receipt=record(run / 'cache-inputs.json'), scope='Pre-existing read-only wheels; no new numerical cache copy'),
        retained_e007_storage=storage(base), outside_evidence_copy_storage=storage(base / 'external-two-thread-001'),
        packaging_audit=dict(source_commit=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
            tracked_files=len(tracked), tracked_inbox_or_heavy_artifacts=0,
            historical_context_objects=len(history), historical_context_paths=len(set(history)),
            project_license_selected=False, scope='Bounded tree/archive/history locator audit, not complete security/legal clearance; no history rewrite'),
        prepared_linux_ci=dict(executed=False, threads=2, python='3.12', installation='Standalone owned dependencies; pending real authorized CI'),
        blockers_before_opening_private_pr=[], before_merge=['Real Linux CI success', 'Implementation review', 'Explicit owner merge authorization'],
        science_repeated=False, architecture_changed=False, remote_actions_taken=False)
    with a.output.open('x') as stream:
        json.dump(value, stream, indent=2, sort_keys=True, allow_nan=False)
        stream.write('\n')
    print(json.dumps(dict(status=value['status'], campaign_seconds=total, retained_bytes=value['retained_e007_storage']['regular_bytes'])))


if __name__ == '__main__':
    main()
