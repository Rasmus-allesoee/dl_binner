#!/usr/bin/env python3
"""Independently admit closed E036 receipts before frozen diagnostic scoring.

The caller supplies already verified generation-bound streams and fresh financial
records. This module never launches compute, mutates native outputs or scores a
baseline. Unstaged members are checked against the complete verified inventory.
"""
import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).absolute().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from e024_coverage import binding, write
from e036_dispatch import order


def require(condition, message):
    """Refuse a missing contract even when Python assertions are disabled."""
    if not condition:
        raise ValueError(message)


def admit(base):
    """Close actual exits, source, all seals, input reuse, fallback and delivery."""
    base = Path(base)
    read = lambda p: json.loads(Path(p).read_text())
    evidence = base / 'restored/evidence'
    work = base / 'restored/work'
    inv = read(base / 'objects/comparison/inventory.json')['all_work_members']
    complete = read(base / 'completion.json')
    provider = read(base / 'control/provider.json')
    integrity = read(base / 'integrity.json')
    require(provider['status'] == 'TERMINATED', 'Independent shutdown missing')
    require(integrity['status'] == 'PASS' and integrity['complete_global_union']
            and integrity['all_aliases_verified'], 'Complete byte/alias union missing')
    require(complete['status'] == 'SUCCESS' and complete['science_completed']
            and complete['collection_readback_verified'], 'Scientific/delivery failure')
    tail = read(base / 'closed-delivery-tail.json')
    require(tail['status'] == 'PASS' and tail['science_completed']
            and tail['completion']['binding'] == binding(base / 'completion.json'),
            'Later completion delivery differs')
    guest = read(base / 'control/guest.json')
    require(len(guest) == 1, 'Guest status is ambiguous')
    guest = json.loads(guest[0]['value'])
    require(guest['status'] == 'SUCCESS' and guest['science_completed']
            and guest['completion_delivery_verified'] and guest['root'] == complete['root']
            and guest['source'] == complete['source'], 'Final guest status differs')
    cfg = read(evidence / 'config.json')
    plan = read(evidence / 'science-plan.json')
    release = read(evidence / 'release.json')
    require(release['config'] == binding(evidence / 'config.json')
            and release['plan'] == binding(evidence / 'science-plan.json')
            and release['watchdog_verified'] and release['provider_STOP_verified'],
            'Actual held-parent release differs')
    require(complete['source'] == cfg['source_commit']
            == '2c81c808e791ff7bccff8e192ee9b8e86c80535d', 'Operational source differs')
    watch = read(base / 'watchdog-exit.json')
    armed = read(evidence / 'logs/supervision.json')
    require(watch['shutdown'] and watch['decision'] == 'workflow exited'
            and watch['workflow_root'] == complete['root']
            and watch['boot_id'] == armed['boot_id']
            and watch['expected_process'] == armed['process']
            and watch['observed_process'] is None, 'Boot/process-bound shutdown differs')
    source = evidence / 'effective-source-repository'
    lock = read(ROOT / 'experiments/E036-optional-pooled-links/source-lock.json')
    repair = read(ROOT / 'experiments/E036-optional-pooled-links/repair-lock.json')
    names = dict(lock['files'])
    names.update({n: b['after'] for n, b in repair['overrides'].items()})
    names.update(repair['extra_files'])
    for n, wanted in names.items():
        require(binding(source / n) == wanted, 'Effective native source differs: ' + n)
    require(binding(evidence / 'source.bundle') == cfg['financial']['source_transport']['bundle'],
            'Exact source transport differs')
    require(binding(source / 'experiments/E036-optional-pooled-links/source-lock.json')
            == repair['parent_source_lock'], 'Original source freeze rewritten')
    candidate = read(ROOT / 'experiments/E036-optional-pooled-links/candidate-lock.json')
    runtime = read(evidence / 'gates/runtime.json')
    require(runtime['status'] == 'PASS_COMPLETE_READONLY_BASE_AND_NEW_OWNED_PACKAGE'
            and runtime['package_files'] == candidate['package_files']
            and runtime['actual_installed_console_help']
            and len(runtime['distributions']) == 42
            and runtime['python'].startswith('3.10.15'), 'Complete native runtime differs')
    require(binding(evidence / 'dl_binner-0.1.0.dev11-py3-none-any.whl')
            == candidate['wheel'], 'Executed wheel differs')
    schema = read(ROOT / 'experiments/E036-optional-pooled-links/runtime-plan.json')
    schema = json.loads(json.dumps(schema).replace(
        'NEW_PHASE', 'optional-20261114T003409Z-7aa7bf7'))
    require(plan == schema, 'Frozen native information/resource policy differs')
    barrier = read(work / 'barrier/proof.json')
    axes = read(ROOT / 'experiments/E036-optional-pooled-links/reuse-lock.json')['axes']
    require(barrier['status'] == 'PASS' and barrier['truth_accessed'] is False
            and all(barrier['axes'][u]['axis'] == axis for u, axis in axes.items())
            and [barrier['axes'][u]['available'] for u in axes] == [True, True, False],
            'Full axes/shared optional policy differs')
    before, after = [read(evidence / ('gates/inputs-' + n + '.json'))
                     for n in ['before', 'after']]
    expected = read(ROOT / 'experiments/E036-optional-pooled-links/reuse-lock.json')['external_files']
    consumed = {v for row in plan['units'].values() for k, v in row.items()
                if k in {'features', 'views', 'fasta', 'marker_evidence'}}
    consumed |= {str(Path(n).with_suffix('.json')) for n in list(consumed)
                 if n.endswith('.npz')}
    require(before == after and set(before) == consumed
            and all(expected.get(n) == v for n, v in before.items()),
            'Complete accepted input before/after bindings differ')
    exits = {}
    for stage in complete['stages']:
        name = stage['stage']
        q = read(evidence / ('logs/' + name + '.exit.json'))
        require(q == stage['resources'] and q['exit_code'] == 0
                and q['stop_reason'] is None, 'Actual stage exit differs: ' + name)
        exits[name] = 0
    require(len(exits) == 15, 'Incomplete outer stage axis')
    for i, (unit, stage) in enumerate(order()):
        relative = 'barrier' if unit is None else unit + '/' + stage
        seal = read(work / relative / 'done.json')
        require(seal['status'] == 'PASS', 'Scientific seal failed: ' + relative)
        for n, wanted in seal['files'].items():
            require(inv[relative + '/' + n] == wanted,
                    'Scientific seal/member differs: ' + relative + '/' + n)
        dispatch = read(work / ('dispatch/%03d.json' % i))
        require(dispatch == dict(status='PASS', ordinal=i, unit=unit, stage=stage,
                                 science_seal=binding(work / relative / 'done.json'),
                                 child_exit=0), 'Actual serial closure differs')
    require(len(list((work / 'dispatch').glob('*.json'))) == 31,
            'Extra/missing serial closures')
    final = read(work / 'final-contracts.json')
    require(final['status'] == 'PASS_COMPLETE_NATIVE_RESULTS' and final['stages'] == 31
            and final['truth_accessed'] is False, 'Native final contract missing')
    for unit in ['E009-noGLM', 'E009-GLM']:
        r = final['units'][unit]
        require(r['status'] == 'PASS_NEW_GRAPH_OUTPUTS' and r['active_rows'] == 3074
                and r['edges'] == 1671 and r['unlinked_exact'] and r['reload_exact'],
                'Changed-graph native contract differs')
    oral = final['units']['oral-noGLM']
    require(oral['status'] == 'PASS_EXACT_ACCEPTED_FALLBACK' and not oral['new_fit']
            and not oral['baseline_rescored'], 'Exact Oral fallback missing')
    require(read(evidence / 'gates/reuse.json')['old_science_replayed'] is False,
            'Accepted work was replayed')
    for n in ['pooled', 'baseline', 'bootstrap', 'measurements']:
        require('after-reused-' + n in exits, 'Post-run reuse verification missing')
    reuse = read(ROOT / 'experiments/E036-optional-pooled-links/reuse-lock.json')
    historical = {}
    for kind, path in [
        ('bootstrap', 'artifacts/e031-bootstrap-preserving-learning/learning-inspection-20261103/inventory.json'),
        ('baseline', 'artifacts/e032-biological-candidate-selection/inspection/inventory.json')
    ]:
        require(binding(ROOT / path) == reuse['archives'][kind]['inventory'],
                'Accepted comparator inventory differs')
        historical[kind] = read(ROOT / path)['all_work_members']
    oral_prefix = 'oral-noGLM/select/result/'
    old_oral = {n: v for n, v in historical['baseline'].items()
                if n.startswith(oral_prefix)}
    require(old_oral == {n: v for n, v in inv.items() if n.startswith(oral_prefix)},
            'Oral complete pre/post fallback byte union differs')
    for unit in axes:
        original = historical['bootstrap'][unit + '/embed/embeddings.npz']
        original_graph = historical['bootstrap'][unit + '/graph/result/graph.npz']
        for stage in ['node-features', 'student', 'student-embed', 'student-graph',
                      'retrieve', 'forest', 'construct', 'e023', 'select', 'audit']:
            inputs = read(work / unit / stage / 'done.json')['inputs']
            require(inputs['original_vectors'] == original
                    and inputs['original_graph'] == original_graph,
                    'Immutable bootstrap provenance differs')
        if unit == 'oral-noGLM':
            require(inv[unit + '/student-embed/embeddings.npz'] == original
                    and inv[unit + '/student-graph/result/graph.npz'] == original_graph,
                    'Oral fallback geometry bytes differ')
    require(complete['filesystem_delivery']['binding']
            == binding(base / 'objects/filesystem.jsonl'), 'Later filesystem log missing')
    require(not complete['filesystem']['monitor_error'], 'Native disk monitor failed')
    result = dict(status='PASS_COMPLETED_SCIENCE_AND_DELIVERY_BEFORE_DIAGNOSTICS',
                  provider_status='TERMINATED', archive_and_every_member_verified=True,
                  cost_and_retention_admitted=read(base / 'export-admission.json')['status']
                  == 'PASS_BEFORE_ARCHIVE_EXPORT', workflow_completed=True,
                  exact_source_schedule_axes_verified=True,
                  native_source_runtime_information_policy_verified=True,
                  candidate_lock=binding(ROOT / 'experiments/E036-optional-pooled-links/candidate-lock.json'),
                  source_files_verified=len(names), actual_outer_exits=exits,
                  actual_serial_closures=31, final_contracts=final,
                  original_inputs_unchanged=True, old_science_replayed=False,
                  shutdown_watchdog_verified=True, final_numeric_parent_exit_available=False,
                  local_model_inference=False, original_Mac_tolerance_unchanged=True)
    write(base / 'native-admission.json', result)
    write(base / 'admission.json', result)
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base', type=Path, required=True)
    print(admit(parser.parse_args().base)['status'])
