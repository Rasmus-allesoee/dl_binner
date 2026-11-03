#!/usr/bin/env python3
"""Admit the stopped paired E031 learner from verified bytes, never from scores.

Inputs are the exact private return, its complete stream verification, control
plane and fresh financial receipts. This reader does not run a model, alter a
partition, select a scientific treatment or wake a VM. Tensor-level inspection
can subsequently use the retained native checkpoints without model inference.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).absolute().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from e024_coverage import binding, write
from e027_inspection import seal_from_inventory

EXP = ROOT / 'experiments/E031-bootstrap-preserving-learning'
SOURCE = 'ba659119c3ec86edc83e27bad95939326fbaa2b8'
PHASE = 'learning-20261102T200852Z-ba65911-r2'
UNITS = ['E009-noGLM', 'E009-GLM', 'oral-noGLM']
STAGES = ['confidence', 'train', 'embed', 'graph', 'e023', 'retrieve',
          'forest', 'construct', 'export', 'audit', 'paired']


def read(path):
    """Read a closed retained JSON record."""
    return json.loads(Path(path).read_text())


def require(value, message):
    """Refuse incomplete evidence before any biological diagnostic."""
    if not value:
        raise ValueError(message)


def inspect(base):
    """Verify real exits, immutable stage contents, complete axes and delivery."""
    base = Path(base); staged = base / 'verified'; evidence = staged / 'evidence'
    inv = read(staged / 'inventory.json'); stream = read(base / 'download-verification.json')
    completion = read(base / 'completion.json'); collection = read(base / 'collection.json')
    provider = read(base / 'control/provider.json')
    finance = read(base / 'finance/inspection-download-admission.json')
    require(provider['status'] == 'TERMINATED' and not provider.get('guestAccelerators')
            and provider['machineType'].endswith('/e2-standard-8')
            and sorted(int(d['diskSizeGb']) for d in provider['disks']) == [30, 40, 300], 'Stopped allocation differs')
    require(stream['every_member_verified'] and stream['archive'] == collection['archive']
            and stream['regular_members'] == collection['regular_members']
            and stream['logical_member_bytes'] == collection['logical_member_bytes'], 'Full member verification missing')
    guest = [json.loads(v['value']) for v in read(base / 'control/guest.json')
             if v['namespace'] == 'e031-candidate' and v['key'] == 'status']
    require(len(guest) == 1 and guest[0]['root'].endswith('/' + PHASE)
            and guest[0]['completion'] == binding(base / 'completion.json')
            and guest[0]['status'] == completion['status'] == 'SUCCESS'
            and completion['science_completed'] and completion['collection_readback_verified'], 'Completion/root mismatch')
    require(finance['coverage_status'] == 'PASS_FOR_SPECIFIED_ORDINARY_FIRST_PARTY_PRODUCTS_ONLY'
            and finance['download_and_full_stream_admitted'] and finance['credit_only']
            and finance['original_learner_ceiling_USD'] == 8, 'Cost/credit admission differs')
    controls = evidence / 'controls'; delivery = read(controls / 'control-inventory.json')
    require(not delivery['missing'], 'Native controls missing')
    for name, wanted in delivery['copied'].items():
        require(binding(controls / name) == wanted, 'Control bytes differ: ' + name)
    cfg = read(controls / 'config.json'); release = read(controls / 'release.json')
    live = read(controls / 'logs/watchdog-live-before-release.json')
    exited = read(base / 'watchdog-exit.json'); started = read(controls / 'started.json')
    require(exited['shutdown'] and exited['decision'] == 'workflow exited'
            and exited['boot_id'] == live['boot_id']
            and exited['expected_process'] == live['expected_process'] == live['observed_process'] == started['identity']
            and live['decision'] == 'workflow alive' and not live['shutdown'], 'Boot/process exit proof differs')
    require(cfg['source_commit'] == completion['source_commit'] == SOURCE
            and cfg['root'].endswith('/' + PHASE) and cfg['vm_start_epoch'] == 1793649752.426
            and cfg['limits']['seconds'] == 57600 and cfg['limits']['provider_STOP_seconds'] == 58500
            and cfg['limits']['extra_bytes'] == 9 * 1024**3
            and completion['finished_epoch'] < cfg['vm_start_epoch'] + 57600 < 1793746800,
            'Original source/clock/retention changed')
    names = ['workflow', 'used-inputs-after', 'collect'] + [prefix + name for name in
        ['e031-evidence.tar.gz', 'e031-evidence.tar.gz.sha256', 'collection.json', 'collection-disk.jsonl', 'terminal-disk.json']
        for prefix in ['upload-', 'readback-']]
    require([s['name'] for s in completion['stages']] == names
            and all(s['resources']['exit_code'] == 0 and s['resources']['stop_reason'] is None
                    for s in completion['stages']), 'Actual workflow/delivery exit missing')
    require(release['config'] == binding(controls / 'config.json')
            and release['plan'] == binding(controls / 'science-plan.json'), 'Release bytes differ')
    for native, wanted in release['gate_files'].items():
        path = Path(native)
        require(path.is_relative_to(cfg['root']) and binding(controls / path.relative_to(cfg['root'])) == wanted,
                'Released gate differs: ' + native)
    old = read(EXP / 'source-lock.json'); paired = read(EXP / 'paired-source-lock.json')
    effective = dict(old['files']); effective.update(paired['files'])
    for name, wanted in effective.items():
        require(binding(evidence / 'source' / name) == wanted, 'Returned executed source differs: ' + name)
        raw = subprocess.check_output(['git', 'show', SOURCE + ':' + name], cwd=ROOT)
        require(dict(bytes=len(raw), sha256=hashlib.sha256(raw).hexdigest()) == wanted,
                'Executed Git source differs: ' + name)
    gates = read(evidence / 'gates/completion.json'); runtime = read(evidence / 'gates/runtime.json')
    require(gates['status'] == 'PASS' and len(gates['stages']) == 9
            and gates['config'] == binding(controls / 'config.json')
            and all(s['resources']['exit_code'] == 0 for s in gates['stages']), 'Native gate exit differs')
    require(runtime['status'] == 'PASS_COMPLETE_READONLY_BASE_AND_NEW_OWNED_PACKAGE'
            and runtime['package_files'] == read(EXP / 'candidate-lock.json')['package_files']
            and len(runtime['distributions']) == 41, 'Complete runtime differs')
    before = read(evidence / 'gates/data.json'); after = read(staged / 'work/used-inputs-after.json')
    reuse = read(EXP / 'reuse-lock.json'); plan = read(controls / 'science-plan.json')
    require(before == after and before['hashed_inputs'] == reuse['learning_files']
            and before['verified_original_files'] == 125 and before['truth_accessed'] is False,
            'Original inputs-after differs')
    prefixes = ['barrier'] + [u + '/' + s for u in UNITS for s in STAGES]
    for path in (staged / 'work').rglob('*.json'):
        name = str(path.relative_to(staged / 'work'))
        require(binding(path) == inv['all_work_members'].get(name), 'Restored work JSON drift: ' + name)
    seals = {p: seal_from_inventory(read(staged / 'work' / p / 'done.json'), p, inv) for p in prefixes}
    units = {}
    for unit in UNITS:
        at = staged / 'work' / unit; axis = reuse['axes'][unit]
        checkpoint = read(at / 'train/result/checkpoint.json'); init = read(at / 'train/result/initial-state.json')
        embedding = read(at / 'embed/embeddings.json'); graph = read(at / 'graph/result/completed.json')
        paired_proof = read(at / 'paired/proof.json'); bridge = read(at / 'e023/science/bridge.json')
        done = read(at / 'construct/result/completed.json'); history = checkpoint['history']
        require(checkpoint['config']['seed'] == 11 and checkpoint['config']['batch_size'] == 256
                and checkpoint['config']['epochs'] == 20 and checkpoint['training_parents'] == axis['eligible']
                and checkpoint['original_optimizer_steps_restored'] and not checkpoint['truth_accessed']
                and checkpoint['threads'] == 4 and checkpoint['loader_workers'] == 0, 'Learning schedule differs')
        require(checkpoint['samples'] == embedding['samples'] == done['samples'] == axis['samples']
                and len(history) == 20 and [h['epoch'] for h in history] == list(range(1, 21))
                and all(h['parents_seen'] == axis['eligible'] and math.isfinite(h['loss']) for h in history),
                'Parent/sample/exposure history incomplete')
        require(init['continuation'] == checkpoint['continuation']
                and checkpoint['continuation']['learning_rate'] == .0002
                and checkpoint['continuation']['anchor_weight'] == .1
                and init['state']['anchor'] == init['state']['online']
                and checkpoint['initial_state'] == init['state'], 'Preserved initialization/anchor differs')
        require(all(not v['catastrophic_collapse'] for h in history for branch in h['geometry'].values()
                    for v in branch.values()) and embedding['reload_exact'], 'Collapse/native reload failed')
        require(graph['status'] == 'PASS' and done['status'] == 'SUCCESS' and not graph['truth_accessed']
                and not done['truth_accessed'] and done['full_DNA_preserved']
                and done['rows'] == axis['rows'] and done['bp'] == axis['bp'], 'Complete DNA/graph contract failed')
        require(paired_proof['status'] == 'PASS' and paired_proof['one_fit_per_mode']
                and paired_proof['no_teacher_refit'] and paired_proof['no_truth_selection']
                and bridge['status'] == bridge['audit']['status'] == 'PASS'
                and not bridge['accepted_science_reused'] and bridge['DNA_reuse']['full_DNA_preserved'],
                'Matched constructor audit failed')
        for key, path in dict(features=Path(plan['units'][unit]['features']), embeddings=Path(cfg['work']) / unit / 'embed/embeddings.npz',
                              graph=Path(cfg['work']) / unit / 'graph/result/graph.npz',
                              evidence=Path(plan['units'][unit]['marker_evidence'])).items():
            wanted = before['hashed_inputs'].get(str(path)) or inv['all_work_members'][str(path.relative_to(cfg['work']))]
            require(bridge['inputs'][str(path)] == wanted and done['input_sha256'][key] == wanted['sha256'],
                    'Constructors consumed different ' + key)
        for arm, account in bridge['accounts'].items():
            require(account['status'] == 'SUCCESS' and account['contigs'] == axis['rows'] and account['bp'] == axis['bp']
                    and sum(v['bp'] for v in account['populations'].values()) == axis['bp'], 'E023 DNA accounting incomplete')
        require(binding(at / 'audit/proof.json') == paired_proof['native_reload_and_E030_audit']
                and binding(at / 'e023/science/bridge.json') == paired_proof['E023_audit'], 'Paired independent audit differs')
        units[unit] = dict(axis=axis, train_seconds=checkpoint['wall_seconds'], checkpoint=binding(at / 'train/result/checkpoint.json'),
                           continuation=checkpoint['continuation'], initial_state=init['state'],
                           initial_geometry=init['geometry'], final_history=history[-1],
                           no_collapse=True, strict_native_reload=True, full_DNA_preserved=True,
                           same_new_vectors_and_graph=paired_proof['same_new_vectors_and_graph'])
    jobs = re.findall(r'^Execute (\d+) jobs', (evidence / 'phase-logs/workflow.log').read_text(), re.M)
    require(len(jobs) >= 34 and all(int(n) == 1 for n in jobs), 'Actual serial scheduling incomplete')
    disk = read(base / 'terminal-disk.json')
    require(binding(base / 'terminal-disk.json') == completion['terminal_disk']
            and disk['summary']['minimum_free_bytes'] >= 25 * 1024**3
            and disk['summary']['maximum_sampled_global_growth_bytes'] <= 9 * 1024**3
            and disk['source_filesystem_terminal']['free'] >= 25 * 1024**3, 'Source/task reserve failed')
    admission = dict(phase=PHASE, source=SOURCE, checked_UTC=datetime.now(timezone.utc).isoformat(),
        provider_status='TERMINATED', archive_and_every_member_verified=True, cost_and_retention_admitted=True,
        workflow_completed=True, exact_source_schedule_axes_verified=True,
        native_gate_exits=9, actual_phase_delivery_exits=len(names), stage_seals=seals, units=units,
        scientific_fits=3, new_model_outputs=3, constructors_each=2,
        original_Mac_portability_tolerance_unchanged=True, criteria_or_scientific_gate_changed=False,
        diagnostic_scores_not_yet_admitted=True)
    write(base / 'admission.json', admission); write(base / 'inventory.json', inv)
    return admission


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__); parser.add_argument('--base', type=Path, required=True)
    value = inspect(parser.parse_args().base)
    print(json.dumps(dict(status='PASS', phase=value['phase'], seals=len(value['stage_seals']), fits=value['scientific_fits'])))
