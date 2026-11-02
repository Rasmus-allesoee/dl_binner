#!/usr/bin/env python3
"""Independently admit the stopped E031 bridge before frozen truth diagnostics.

Consumes only checksum-verified compact return controls and provider/financial
readbacks. Driver counters cannot replace real gate exits and complete stage
seals. No cloud wake, scientific replay, score, or resource mutation occurs.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).absolute().parents[1]
sys.path.insert(0, str(ROOT/'scripts'))
from e024_coverage import binding, write
from e027_inspection import seal_from_inventory

EXP = ROOT/'experiments/E031-bootstrap-preserving-learning'
SOURCE = '31962f85af266801687885a41fbf6e933cabc33b'
PHASE = 'bridge-20261102T130813Z-31962f8'
UNITS = ['E009-noGLM', 'E009-GLM', 'oral-noGLM']


def read(path):
    """Read an existing closed JSON receipt."""
    return json.loads(Path(path).read_text())


def require(value, message):
    """Refuse an unmet admission rather than deriving a partial quality result."""
    if not value:
        raise ValueError(message)


def inspect(base):
    """Verify source, original inputs, supervision, actual exits and full DNA axes."""
    base = Path(base); staged = base/'verified'; evidence = staged/'evidence'
    inventory = read(staged/'inventory.json'); stream = read(base/'download-verification.json')
    completion = read(base/'completion.json'); collection = read(base/'collection.json')
    provider = read(base/'control/provider.json'); finance = read(base/'finance/inspection-download-admission.json')
    require(stream['every_member_verified'] and stream['archive'] == collection['archive']
            and stream['regular_members'] == collection['regular_members']
            and stream['logical_member_bytes'] == collection['logical_member_bytes'], 'Complete archive not admitted')
    require(provider['status'] == 'TERMINATED' and not provider.get('guestAccelerators')
            and provider['machineType'].endswith('/e2-standard-8')
            and sorted(int(d['diskSizeGb']) for d in provider['disks']) == [30, 40, 300], 'Stopped resource scope differs')
    guest = [json.loads(v['value']) for v in read(base/'control/guest.json')
             if v['namespace'] == 'e031-candidate' and v['key'] == 'status']
    require(len(guest) == 1 and guest[0]['completion'] == binding(base/'completion.json')
            and guest[0]['status'] == completion['status'] == 'SUCCESS'
            and completion['science_completed'] and completion['collection_readback_verified'], 'Completion/guest mismatch')
    seconds = (datetime.fromisoformat(provider['lastStopTimestamp'])
               - datetime.fromisoformat(provider['lastStartTimestamp'])).total_seconds()
    require(abs(seconds-finance['allocation_seconds']) < .001 and finance['export_admitted']
            and finance['coverage_status'] == 'PASS_FOR_SPECIFIED_ORDINARY_FIRST_PARTY_PRODUCTS_ONLY'
            and finance['complete_bridge_upper_USD'] < 4, 'Original cost admission differs')
    controls = evidence/'controls'; delivery = read(controls/'control-inventory.json')
    require(not delivery['missing'], 'Release controls missing')
    for name, wanted in delivery['copied'].items():
        require(binding(controls/name) == wanted, 'Delivered control bytes differ: '+name)
    cfg = read(controls/'config.json'); release = read(controls/'release.json')
    live = read(controls/'logs/watchdog-live-before-release.json'); exited = read(base/'watchdog-exit.json')
    started = read(controls/'started.json')
    require(exited['shutdown'] and exited['decision'] == 'workflow exited'
            and exited['boot_id'] == live['boot_id']
            and exited['expected_process'] == live['expected_process'] == live['observed_process'] == started['identity']
            and live['decision'] == 'workflow alive' and not live['shutdown'], 'Boot/process shutdown evidence differs')
    require(cfg['source_commit'] == completion['source_commit'] == SOURCE
            and cfg['root'].endswith('/'+PHASE) and cfg['limits']['seconds'] == 21600
            and cfg['limits']['provider_STOP_seconds'] == 22500
            and completion['finished_epoch'] < cfg['vm_start_epoch']+21600
            and cfg['vm_start_epoch']+22500 < 1793746800, 'Source/clock/retention differs')
    names = ['workflow', 'used-inputs-after', 'collect'] + [p+n for n in
        ['e031-evidence.tar.gz', 'e031-evidence.tar.gz.sha256', 'collection.json', 'collection-disk.jsonl', 'terminal-disk.json']
        for p in ['upload-', 'readback-']]
    require([s['name'] for s in completion['stages']] == names
            and all(s['resources']['exit_code'] == 0 and s['resources']['stop_reason'] is None for s in completion['stages']),
            'Actual driver/delivery exit missing')
    require(release['config'] == binding(controls/'config.json')
            and release['plan'] == binding(controls/'science-plan.json'), 'Released config/plan bytes differ')
    for native, wanted in release['gate_files'].items():
        path = Path(native)
        require(path.is_relative_to(cfg['root']) and binding(controls/path.relative_to(cfg['root'])) == wanted,
                'Bound native release gate differs: '+native)
    lock = read(EXP/'source-lock.json')
    for name, wanted in lock['files'].items():
        require(binding(evidence/'source'/name) == wanted, 'Returned prepared source differs: '+name)
        raw = subprocess.check_output(['git', 'show', SOURCE+':'+name], cwd=ROOT)
        require(dict(bytes=len(raw), sha256=hashlib.sha256(raw).hexdigest()) == wanted, 'Executed Git source differs: '+name)
    gates = read(evidence/'gates/completion.json'); runtime = read(evidence/'gates/runtime.json')
    require(gates['status'] == 'PASS' and len(gates['stages']) == 7
            and gates['config'] == binding(controls/'config.json')
            and all(s['resources']['exit_code'] == 0 for s in gates['stages']), 'Native gate exit differs')
    require(runtime['status'] == 'PASS_COMPLETE_READONLY_BASE_AND_NEW_OWNED_PACKAGE'
            and runtime['package_files'] == read(EXP/'candidate-lock.json')['package_files']
            and len(runtime['distributions']) == 41, 'Complete installed runtime differs')
    before = read(evidence/'gates/data.json'); after = read(staged/'work/used-inputs-after.json')
    reuse = read(EXP/'reuse-lock.json')
    require(before == after and before['hashed_inputs'] == reuse['bridge_files']
            and before['verified_original_files'] == 40 and before['truth_accessed'] is False, 'Original science input-after differs')
    paths = ['barrier'] + ['actors/'+u+'/'+r for u in UNITS for r in ['teacher', 'student']] + [u+'/audit' for u in UNITS]
    seals = {p: seal_from_inventory(read(staged/'work'/p/'done.json'), p, inventory) for p in paths}
    plan = read(controls/'science-plan.json'); queries = read(EXP/'query-axes.json'); actors = {}
    for u in UNITS:
        for role in ['teacher', 'student']:
            actor = staged/'work/actors'/u/role; proof = read(actor/'science/bridge.json')
            axis = reuse['axes'][u]; entry = plan['units'][u]; original = entry[role]
            require(before['axes'][u+'-'+role] == axis and proof['status'] == 'PASS'
                    and proof['truth_accessed'] is False and proof['audit']['status'] == 'PASS'
                    and proof['native_learned_geometry_fixed'] and proof['DNA_reuse']['full_DNA_preserved'], 'Actor/input axis audit differs')
            require(proof['accepted_science_reused'] is (u == 'E009-GLM' and role == 'student'), 'Accepted/new actor distinction differs')
            for name, b in proof['inputs'].items():
                require(before['hashed_inputs'][name] == b, 'Native actor did not use exact original bytes')
            for arm, account in proof['accounts'].items():
                require(account['status'] == 'SUCCESS' and account['contigs'] == axis['rows'] and account['bp'] == axis['bp']
                        and sum(p['bp'] for p in account['populations'].values()) == axis['bp']
                        and sum(p['contigs'] for p in account['populations'].values()) == axis['rows'], 'Incomplete DNA export accounting')
            query = read(actor/'query-neighbors.json')
            require(query['status'] == 'PASS' and query['features'] == reuse['bridge_files'][entry['features']]
                    and query['graph'] == reuse['bridge_files'][original['graph']]
                    and query['samples'] == axis['samples']
                    and [dict(id=q['id'], strata=q['strata']) for q in query['queries']] == queries[u][role]['queries'],
                    'Frozen source-blind neighbor query population differs')
            actors[u+'/'+role] = dict(accounts=proof['accounts'], audit=proof['audit'], query_count=len(query['queries']),
                                     accepted_reuse=proof['accepted_science_reused'])
    commands = re.findall(r'^Execute (\d+) jobs', (evidence/'phase-logs/workflow.log').read_text(), re.M)
    require(len(commands) >= 10 and all(int(n) == 1 for n in commands), 'Actual scheduling is not serial')
    disk = read(base/'terminal-disk.json')
    require(binding(base/'terminal-disk.json') == completion['terminal_disk']
            and disk['summary']['minimum_free_bytes'] >= 25*1024**3
            and disk['summary']['maximum_sampled_global_growth_bytes'] <= 7*1024**3
            and disk['source_filesystem_terminal']['free'] >= 25*1024**3, 'Source/task reserve or total growth failed')
    admission = dict(phase=PHASE, source=SOURCE, checked_UTC=datetime.now(timezone.utc).isoformat(),
        provider_status='TERMINATED', archive_and_every_member_verified=True, cost_and_retention_admitted=True,
        workflow_completed=True, exact_source_schedule_axes_verified=True, science_fits=0,
        native_gate_exits=7, actual_phase_delivery_exits=len(names), stage_seals=seals, actors=actors,
        allocation_seconds=seconds, original_Mac_portability_tolerance_unchanged=True,
        criteria_or_scientific_gate_changed=False, diagnostic_scores_not_yet_admitted=True)
    write(base/'admission.json', admission)
    write(base/'inventory.json', inventory)
    return admission


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__); parser.add_argument('--base', type=Path, required=True)
    args = parser.parse_args(); result = inspect(args.base)
    print(json.dumps(dict(status='PASS', phase=result['phase'], gates=result['native_gate_exits'], seals=len(result['stage_seals']))))
