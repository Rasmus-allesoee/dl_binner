#!/usr/bin/env python3
"""Admit a stopped E029 return from independent control, source and stage proofs.

Reads verified compact controls only. Does not start cloud work, reconstruct
science, modify native receipts or calculate recovery scores.
"""
import argparse
from datetime import datetime
import hashlib
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).absolute().parents[1]
sys.path.insert(0, str(ROOT/'scripts'))
from e024_coverage import binding, write
from e027_inspection import read, require, seal_from_inventory
from e028_inspection import recall_contract

EXP = ROOT/'experiments/E029-certifiable-joint-retrieval'
SOURCE = '31fb9c788e3903f10eb8beb012ca44a36fa74400'
UNITS = ['E009-noGLM', 'E009-GLM', 'oral-noGLM']


def inspect(base, guest_path, output):
    """Refuse incomplete provenance before exposing a separate evaluator admission."""
    base = Path(base); controls = base/'controls'; evidence = controls/'evidence'
    inv = read(base/'inventory.json'); proof = read(base/'archive-verified.json')
    finance = read(base/'finance-admission.json'); completion = read(base/'completion.json')
    provider = read(base/'control/provider.json'); guest = read(guest_path)
    require(proof['every_member_verified'] and proof['archive'] == finance['archive']
            == read(base/'collection.json')['archive'], 'Archive not independently admitted')
    require(provider['status'] == 'TERMINATED' and not provider.get('guestAccelerators')
            and provider['machineType'].endswith('/e2-standard-8')
            and sorted(int(x['diskSizeGb']) for x in provider['disks']) == [30, 300],
            'Original VM/disks are not independently stopped')
    values = [read_value(x['value']) for x in guest
              if x['namespace'] == 'e029-candidate' and x['key'] == 'status']
    require(len(values) == 1 and values[0]['completion'] == binding(base/'completion.json')
            and values[0]['status'] == completion['status'] == 'SUCCESS'
            and values[0]['science_completed'] is completion['science_completed'] is True,
            'Guest/private completion differs')
    started = read(evidence/'controls/started.json')
    live = read(evidence/'controls/logs/watchdog-live-before-release.json')
    exited = read(base/'watchdog-exit.json')
    require(exited['shutdown'] is True and exited['decision'] == 'workflow exited'
            and exited['boot_id'] == live['boot_id']
            and exited['expected_process'] == started['identity'] == live['expected_process']
            == live['observed_process'] and live['decision'] == 'workflow alive'
            and live['shutdown'] is False, 'Intended boot/process shutdown proof differs')
    seconds = (datetime.fromisoformat(provider['lastStopTimestamp'])-
               datetime.fromisoformat(provider['lastStartTimestamp'])).total_seconds()
    require(abs(seconds-finance['measured_allocation_seconds']) < .001
            and finance['cost_and_retention_admitted'] is True, 'Allocation/cost not admitted')
    names = ['workflow', 'used-inputs-after', 'collect'] + [prefix+name
        for name in ['e029-evidence.tar.gz', 'e029-evidence.tar.gz.sha256', 'collection.json',
                     'collection-disk.jsonl', 'terminal-disk.json']
        for prefix in ['upload-', 'readback-']]
    # The final terminal disk upload is deliberately collected outside the command sampler.
    actual = [s['name'] for s in completion['stages']]
    require(actual == names and all(s['resources']['exit_code'] == 0
            for s in completion['stages']) and completion['collection_readback_verified'] is True
            and completion['source_commit'] == SOURCE, 'Actual phase/delivery exits differ')
    lock = read(EXP/'source-lock.json')
    for name, wanted in lock['files'].items():
        require(binding(evidence/'source'/name) == wanted, 'Returned source differs: '+name)
        raw = subprocess.check_output(['git', 'show', SOURCE+':'+name], cwd=ROOT)
        require(dict(bytes=len(raw), sha256=hashlib.sha256(raw).hexdigest()) == wanted,
                'Executed Git source differs: '+name)
    control = evidence/'controls'; delivery = read(control/'control-inventory.json')
    require(not delivery['missing'], 'Missing release control')
    for name, wanted in delivery['copied'].items():
        require(binding(control/name) == wanted, 'Delivered control differs: '+name)
    release = read(control/'release.json'); cfg = read(control/'config.json')
    released_provider = read(control/'logs/provider-before-release.json')
    scheduling = released_provider['scheduling']
    provider_deadline = datetime.fromisoformat(released_provider['lastStartTimestamp']).timestamp()+int(scheduling['maxRunDuration']['seconds'])
    require(scheduling['automaticRestart'] is False and scheduling['instanceTerminationAction']=='STOP'
            and provider_deadline <= cfg['vm_start_epoch']+60.25*3600+1
            and completion['finished_epoch'] <= cfg['vm_start_epoch']+60*3600
            and completion['finished_epoch'] < 1793746800, 'Original cumulative clock/STOP/retention differs')
    for name, wanted in release['gate_files'].items():
        path = Path(name); require(path.is_relative_to(cfg['root']), 'Gate outside phase')
        require(binding(control/path.relative_to(cfg['root'])) == wanted, 'Released gate differs')
    require(release['config'] == binding(control/'config.json')
            and release['plan'] == binding(control/'science-plan.json'), 'Release plan/config differs')
    gates = read(evidence/'gates/completion.json'); runtime = read(evidence/'gates/runtime.json')
    require(gates['status'] == 'PASS' and len(gates['stages']) == 10
            and all(s['resources']['exit_code'] == 0 for s in gates['stages']), 'Native gate failed')
    require(runtime['status'] == 'PASS_COMPLETE_READONLY_BASE_AND_NEW_OWNED_PACKAGE'
            and runtime['package_files'] == read(EXP/'candidate-lock.json')['package_files']
            and len(runtime['distributions']) == 41, 'Native owned runtime differs')
    for name, wanted in runtime['package_files'].items():
        raw = subprocess.check_output(['git', 'show', SOURCE+':src/dl_binner/'+name], cwd=ROOT)
        require(dict(bytes=len(raw), sha256=hashlib.sha256(raw).hexdigest()) == wanted,
                'Installed product member differs from executed Git source: '+name)
    require(read(evidence/'gates/ann-source.json')['source'] ==
            read(ROOT/'experiments/E028-global-discovery-repair/ann-source-lock.json')['binding'],
            'Inherited ANN source differs')
    before = read(evidence/'gates/data.json'); after = read(controls/'work/used-inputs-after.json')
    require(before == after and before['status'] == 'PASS', 'Used inputs changed after consumption')
    reuse = read(EXP/'reuse-lock.json'); expected = {
        str(Path(reuse['source_work'])/k): v for k, v in reuse['all_closed_stage_members'].items()}
    expected.update(reuse['external_files'])
    require(expected == dict(before['hashed'], **before['unused_admitted_arrays_stat_only']),
            'Used-member/stat-only inventory differs')
    require(before['scientific_fits_run'] == before['learning_graphs_rebuilt'] ==
            before['markers_redetected'] == 0, 'Unexpected scientific replay')
    for unit, axis in read(EXP/'protocol.json')['axes'].items():
        require(before['axes'][unit] == dict(axis, GLM_in_teacher_proposals_student=unit=='E009-GLM'),
                'Full contig/sample/information axis differs')
    stages = {}; recalls = {}
    paths = [f'retrieval/{u}/{r}' for u in UNITS for r in ['teacher', 'student']]
    paths += ['barrier']+[f'groups/{u}/{r}' for u in UNITS for r in ['teacher', 'student']]
    paths += [f'{u}/{kind}' for kind in ['export', 'audit'] for u in UNITS]
    for prefix in paths:
        stages[prefix] = seal_from_inventory(read(controls/'work'/prefix/'done.json'), prefix, inv)
    for u in UNITS:
        for r in ['teacher', 'student']:
            result = controls/'work/groups'/u/r/'result'
            audit = read(result/'retrieval/audit.json'); recalls[u+'/'+r] = recall_contract(audit)
            require(recalls[u+'/'+r]['status'] == 'PASS', 'Sealed recall gate failed')
            done = read(result/'completed.json')
            require(done['status'] == 'SUCCESS' and done['truth_accessed'] is False
                    and done['full_DNA_preserved'] is True
                    and done['rows'] == before['axes'][u]['rows']
                    and done['bp'] == before['axes'][u]['bp']
                    and done['samples'] == before['axes'][u]['samples'], 'Grouping/full DNA differs')
            if u.startswith('oral'):
                require(audit['overall'] == 1 and all(v == 1 for v in audit['strata'].values()),
                        'Exact backend failed unchanged additional 1.0 contract')
            else:
                require(read(result/'retrieval/completed.json') == before['retained_four_retrievals'][u+'-'+r],
                        'Passed retained E009 cache identity differs')
    disk = read(base/'terminal-disk.json')
    require(binding(base/'terminal-disk.json') == completion['terminal_disk']
            and disk['summary']['minimum_free_bytes'] >= 25*2**30
            and disk['summary']['maximum_sampled_global_growth_bytes'] <= 4*2**30,
            'Native total filesystem bounds failed')
    commands = re.findall(r'^Execute (\d+) jobs', (evidence/'phase-logs/workflow.log').read_text(),re.M)
    require(len(commands)>=19 and all(int(n)==1 for n in commands), 'Actual native scheduling was not serial')
    result = dict(status='PASS_INDEPENDENT_STOP_SOURCE_STAGES_INPUTS_DELIVERY',
        phase='discovery-20261101T015844Z-31fb9c7', source=SOURCE,
        provider_status='TERMINATED', archive_and_every_member_verified=True,
        cost_and_retention_admitted=True, workflow_completed=True, archive=proof['archive'],
        regular_members=proof['regular_members'], aliases=len(inv['aliases']),
        source_files=len(lock['files']), owned_package_files=len(runtime['package_files']),
        numerical_distributions=41, native_gate_exits={s['stage']:s['resources']['exit_code'] for s in gates['stages']},
        phase_exits={s['name']:s['resources']['exit_code'] for s in completion['stages']},
        stages=stages, recall=recalls, axes=before['axes'], used_inputs_after_verified=True,
        hashed_files=len(before['hashed']), unused_stat_only=len(before['unused_admitted_arrays_stat_only']),
        watchdog_boot_process_verified=True, measured_allocation_seconds=seconds,
        actual_serial_dispatches=len(commands), original_cumulative_start_epoch=cfg['vm_start_epoch'],
        provider_absolute_STOP_epoch=provider_deadline,
        native_disk=disk['summary'], no_truth_scores_computed=True,
        scope='Exact used-input before/after and retained cache proofs; no claim about every unrelated VM file')
    write(output, result); print('PASS independent E029 admission', flush=True)
    return result


def read_value(raw):
    """Decode a guest-attribute value without changing its namespace or contents."""
    import json
    return json.loads(raw)


if __name__ == '__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for name in ['base', 'guest', 'output']:p.add_argument('--'+name, type=Path, required=True)
    a=p.parse_args();inspect(a.base,a.guest,a.output)
