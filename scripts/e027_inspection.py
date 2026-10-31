#!/usr/bin/env python3
"""Inspect a stopped E027 return without running science or changing cloud state.

Whole-archive verification is separate from workflow success. Completed stage
seals are checked against the complete member/alias/omission inventory, including
failed attempts. A closed independent reference can be admitted separately; this
never turns a failed three-mode workflow into a successful comparison.
"""
import argparse
from datetime import datetime
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tarfile

ROOT = Path(__file__).absolute().parents[1]
sys.path.insert(0, str(ROOT/'scripts'))
from e024_coverage import binding, write
from e014_collect import member_path
from e027_collect import verify

UNITS = ['E009-noGLM', 'E009-GLM', 'oral-noGLM']
STAGES = ['admit', 'teacher', 'teacher-embed', 'teacher-graph', 'pairs', 'student',
          'student-embed', 'student-graph', 'group', 'export', 'audit']


def require(condition, message):
    """Refuse a missing contract without synthesizing successful provenance."""
    if not condition:
        raise ValueError(message)


def read(path):
    """Read a retained regular JSON file without following artifact links."""
    path = Path(path)
    require(path.is_file() and not path.is_symlink(), 'Missing/linked JSON: '+str(path))
    return json.loads(path.read_text())


def archive_contract(archive, expected, output):
    """Verify every byte/member before exposing a compact inventory for readers."""
    proof = verify(archive, expected)
    with tarfile.open(archive, 'r:gz') as stream:
        inventory = json.load(stream.extractfile('inventory.json'))
    require(inventory['kind'] == 'E027 exact-byte calibrated grouping return', 'Wrong E027 archive kind')
    out = Path(output); out.mkdir(exist_ok=False)
    write(out/'inventory.json', inventory)
    write(out/'archive-verified.json', dict(proof, workflow_success_not_implied=True))
    return proof


def selection(inventory, scope):
    """Select closed controls or one arm; keep native reference DNA in the archive."""
    names = set(inventory['members']) | set(inventory['aliases'])
    if scope == 'controls':
        chosen = {n for n in names if n.startswith('evidence/controls/') or n.startswith('evidence/source/')
            or n.startswith('evidence/phase-logs/') or n.startswith('work/logs/')
            or n.startswith('work/benchmarks/') or n in ['evidence/science-result.json',
            'evidence/plan.json', 'evidence/config.json', 'evidence/external-data.json',
            'evidence/gates/completion.json', 'evidence/gates/source.json', 'evidence/gates/data.json',
            'evidence/gates/runtime.json', 'evidence/gates/schedule.json']
            or n.startswith('work/units/') and Path(n).name in ['done.json', 'checkpoint.json',
            'embeddings.json', 'graph.json', 'verified-reuse.json', 'information-contract.json',
            'admission.json', 'audit.json', 'completed.json', 'proof.json']}
    elif scope in UNITS:
        chosen = {n for n in names if n.startswith('work/units/'+scope+'/')}
    elif scope == 'reference':
        chosen = {n for n in names if n.startswith('work/reference/') and
                  not (n.startswith('work/reference/native/') and n.endswith('.fa'))}
    else:
        raise ValueError('One explicit inspection scope required')
    aliases = {n: inventory['aliases'][n] for n in chosen if n in inventory['aliases']}
    physical = {n for n in chosen if n in inventory['members']}
    physical.update(v['canonical'] for v in aliases.values())
    return physical, aliases


def stage(archive, verified, scope, output, cap=3*1024**3, reserve=6*1024**3):
    """Materialize one declared scope from the already whole-verified archive.

    Canonical members of cross-arm aliases are included by exact byte identity.
    Originals and native absolute locators remain unchanged. Failed directories
    are retained; no overwrite, repair, data regeneration or scientific replay.
    """
    proof = read(Path(verified)/'archive-verified.json'); inv = read(Path(verified)/'inventory.json')
    require(binding(Path(archive)) == proof['archive'], 'Verified archive drifted')
    selected, aliases = selection(inv, scope)
    size = sum(inv['members'][n]['bytes'] for n in selected)
    out = Path(output)
    require(size+1024**2 <= cap and shutil.disk_usage(out.parent).free >= size+reserve+1024**2,
            'Actual one-scope footprint/reserve unavailable')
    out.mkdir(exist_ok=False)
    with tarfile.open(archive, 'r:gz') as stream:
        for member in stream:
            if member.name not in selected:
                continue
            target = member_path(out, member.name); target.parent.mkdir(parents=True, exist_ok=True)
            require(member.isfile(), 'Scientific member is not regular')
            with target.open('xb') as dest:
                shutil.copyfileobj(stream.extractfile(member), dest, 1024**2)
            require(binding(target) == inv['members'][member.name], 'Staged member differs')
    for name, alias in aliases.items():
        target = member_path(out, name); target.parent.mkdir(parents=True, exist_ok=True)
        os.link(member_path(out, alias['canonical']), target)
        require(binding(target) == {k: alias[k] for k in ['bytes', 'sha256']}, 'Alias differs')
    result = dict(status='PASS', scope=scope, physical_bytes=size, physical_members=len(selected),
        aliases=len(aliases), original_receipts_rewritten=False, full_archive=proof['archive'])
    write(out/'staging.json', result)
    return result


def seal_from_inventory(seal, prefix, inventory):
    """Verify a completed stage even when its accepted linked arrays are omitted."""
    require(seal.get('status') == 'PASS' and isinstance(seal.get('files'), dict), 'Unpassed stage seal')
    for name, expected in seal['files'].items():
        p = Path(name)
        require(not p.is_absolute() and '..' not in p.parts, 'Unsafe stage member')
        require(inventory['all_work_members'].get(prefix+'/'+name) == expected,
                'Stage seal/member inventory differs: '+prefix+'/'+name)
    actual = {n.removeprefix(prefix+'/') for n in inventory['all_work_members']
              if n.startswith(prefix+'/') and n != prefix+'/done.json'}
    require(actual == set(seal['files']), 'Unsealed extra/missing stage member')
    return dict(status='PASS', members=len(seal['files']))


def summarize_stages(controls, inventory):
    """Report sealed versus partial stages; driver counters are not fit evidence."""
    root = Path(controls)/'work/units'; result = {}
    for unit in UNITS:
        stages = {}
        for name in STAGES:
            p = root/unit/name/'done.json'; prefix = 'units/'+unit+'/'+name
            members = [n for n in inventory['all_work_members'] if n.startswith(prefix+'/')]
            stages[name] = (seal_from_inventory(read(p), prefix, inventory) if p.is_file() else
                dict(status='PARTIAL_UNSEALED' if members else 'NOT_RUN', retained_members=len(members)))
        result[unit] = stages
    return result


def shutdown_contract(provider, guest, completion, completion_binding, watchdog, started, live, finance):
    """Cross-check stopped control-plane, private exit and the intended process.

    These are independent retained observations. A clean stop or successful
    collection never promotes an unsuccessful scientific workflow. Allocation
    duration must agree with the independently priced start/stop interval.
    """
    require(provider['status'] == 'TERMINATED', 'Provider has not independently stopped')
    values = [json.loads(x['value']) for x in guest
              if x['namespace'] == 'e027-candidate' and x['key'] == 'status']
    require(len(values) == 1, 'Missing/duplicated E027 guest completion')
    value = values[0]
    require(value['completion'] == completion_binding and value['status'] == completion['status']
            and value['science_completed'] == completion['science_completed'],
            'Guest/private completion binding differs')
    require(watchdog['shutdown'] is True and watchdog['decision'] == 'workflow exited'
            and watchdog['boot_id'] == live['boot_id']
            and watchdog['expected_process'] == started['identity'] == live['expected_process']
            and live['observed_process'] == started['identity'] and live['decision'] == 'workflow alive'
            and live['shutdown'] is False,
            'Exit watcher is not bound to the intended boot/process')
    elapsed = (datetime.fromisoformat(provider['lastStopTimestamp']) -
               datetime.fromisoformat(provider['lastStartTimestamp'])).total_seconds()
    require(elapsed > 0 and abs(elapsed-finance['measured_allocation_seconds']) < .001
            and finance['cost_and_retention_admitted'] is True,
            'Measured allocation/cost admission differs')
    stages = completion['stages']; names = [s['name'] for s in stages]
    expected = ['workflow', 'collect']+[prefix+n for n in ['e027-evidence.tar.gz',
        'e027-evidence.tar.gz.sha256', 'collection.json', 'collection-disk.jsonl',
        'terminal-disk.json'] for prefix in ['upload-', 'readback-']]
    require(names == expected and completion['collection_readback_verified'] is True
            and all(s['resources']['exit_code'] == 0 for s in stages[1:]),
            'Collection/upload/readback exit missing')
    success = stages[0]['resources']['exit_code'] == 0
    require(completion['science_completed'] == success and
            completion['status'] == ('SUCCESS' if success else 'FAILED'),
            'Workflow exit and scientific completion disagree')
    return dict(provider_status='TERMINATED', workflow_completed=success,
        science_status=completion['status'], collection_completed=True,
        measured_allocation_seconds=elapsed, intended_watchdog_process_verified=True,
        guest_private_completion_verified=True,
        stage_exits={s['name']: s['resources']['exit_code'] for s in stages},
        driver_fit_counter_not_a_scientific_stage_receipt=True)


def source_contract(controls, commit='243b8ac'):
    """Bind returned frozen source to Git objects and every release gate control."""
    root = Path(controls)/'evidence'; lock = read(ROOT/'experiments/E027-common-information-binner/source-lock.json')
    for name, expected in lock['files'].items():
        p = root/'source'/name
        require(binding(p) == expected, 'Returned frozen source differs: '+name)
        data = subprocess.check_output(['git', 'show', commit+':'+name], cwd=ROOT)
        require(dict(bytes=len(data), sha256=hashlib.sha256(data).hexdigest()) == expected,
                'Executed Git object differs: '+name)
    control = root/'controls'; receipt = read(control/'control-inventory.json')
    require(not receipt['missing'], 'Native release controls are missing')
    for name, expected in receipt['copied'].items():
        require(binding(control/name) == expected, 'Closed control bytes differ: '+name)
    release = read(control/'release.json'); phase = read(control/'config.json')
    for name, expected in release['gate_files'].items():
        relative = str(Path(name).relative_to(phase['root']))
        require(binding(control/relative) == expected, 'Delivered release gate differs: '+name)
    native = read(root/'gates/completion.json')
    require(native['status'] == 'PASS' and len(native['stages']) == 10 and
            all(s['resources']['exit_code'] == 0 for s in native['stages']), 'Native admission failed')
    require(release['config'] == binding(control/'config.json') and
            release['plan'] == binding(control/'science-plan.json'), 'Released native plan/config differs')
    return dict(status='PASS', source_files=len(lock['files']), commit=commit,
        native_gates=10, delivered_release_gates=len(release['gate_files']),
        full_workflow_success_not_implied=True)


def scoped_admission(scope, status, finance, archive_proof, source, stage_proof):
    """Admit only an independently complete target, keeping failed-run status false."""
    require(scope in ['reference']+UNITS and status['provider_status'] == 'TERMINATED'
            and finance['cost_and_retention_admitted'] is True
            and archive_proof['every_member_verified'] is True and source['status'] == 'PASS'
            and stage_proof['status'] == 'PASS' and stage_proof.get('target') == scope
            and stage_proof.get('native_exit') == 0
            and all(stage_proof.get(k) is True for k in ['all_dependency_seals_checked',
                'independent_retained_inputs_verified', 'complete_DNA_accounting_verified',
                'frozen_rule_verified']), 'Incomplete scoped target admission')
    return dict(status='PASS_INDEPENDENT_COMPLETED_TARGET', target=scope,
        global_workflow_completed=status['workflow_completed'], scoped_target_completed=True,
        provider_status='TERMINATED', archive_and_every_member_verified=True,
        cost_and_retention_admitted=True, global_failed_gate_not_waived=True)


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--archive', type=Path, required=True); p.add_argument('--output', type=Path, required=True)
    p.add_argument('--expected', type=Path); p.add_argument('--verified', type=Path)
    p.add_argument('--scope', choices=['controls', 'reference']+UNITS); a = p.parse_args()
    if a.expected and not a.scope:
        result = archive_contract(a.archive, read(a.expected)['archive'], a.output)
    elif a.scope and a.verified:
        result = stage(a.archive, a.verified, a.scope, a.output)
    else:
        p.error('Select whole archive verification or one already verified scope')
    print(json.dumps({k: v for k, v in result.items() if k not in ['aliases', 'omitted_retained_on_disk']}), flush=True)
