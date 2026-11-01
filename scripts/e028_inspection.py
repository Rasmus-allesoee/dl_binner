#!/usr/bin/env python3
"""Independently inspect a stopped E028 return, without rerunning its science.

Reads already byte-verified controls and the complete archive inventory. Checks
stage seals, frozen source/runtime/input admission and the intended shutdown.
Failed retrievals never become bin scores or a biological ABANDON disposition.
"""
import argparse
from datetime import datetime
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).absolute().parents[1]
sys.path.insert(0, str(ROOT/'scripts'))
from e024_coverage import binding, write
from e027_inspection import read, require, seal_from_inventory

EXP = ROOT/'experiments/E028-global-discovery-repair'
UNITS = ['E009-noGLM', 'E009-GLM', 'oral-noGLM']
SOURCE = '45a759051f91ee42f08f4bd0557bb9c68a7455bc'


def recall_contract(audit, threshold=.9):
    """Recompute sampled overall/stratum recall, including an unchanged refusal."""
    queries = audit['queries']
    require(queries and all(0 <= q['recall'] <= 1 for q in queries), 'Invalid query recall')
    require(len({q['id'] for q in queries}) == len(queries), 'Duplicate audit query')
    overall = sum(q['recall'] for q in queries)/len(queries)
    strata = {}
    for name in ['positive_depth', 'measured_zero_depth', 'short', 'long']:
        values = [q['recall'] for q in queries if name in q['strata']]
        if values:
            strata[name] = sum(values)/len(values)
    require(abs(overall-audit['overall']) < 1e-12 and set(strata) == set(audit['strata'])
            and all(abs(v-audit['strata'][k]) < 1e-12 for k, v in strata.items()),
            'Retained recall summary differs from actual queries')
    passed = min([overall]+list(strata.values())) >= threshold
    require(audit['status'] == ('PASS' if passed else 'FAILED_RECALL_GATE'),
            'Recall status contradicts unchanged threshold')
    return dict(status=audit['status'], overall=overall, strata=strata,
        query_count=len(queries), min_query_recall=min(q['recall'] for q in queries),
        threshold=threshold, biological_quality_assessed=False)


def matched_queries(before, after):
    """Compare existing search audits only; never recompute an older science score."""
    a={q['id']:q for q in before['queries']};b={q['id']:q for q in after['queries']}
    require(a.keys()==b.keys() and all(a[k]['row']==b[k]['row'] and
        set(a[k]['strata'])==set(b[k]['strata'])for k in a), 'Unmatched search-audit population')
    rows=[dict(id=k,before=a[k]['recall'],after=b[k]['recall'],
        delta=b[k]['recall']-a[k]['recall'],kth_exact_before=a[k]['kth_exact'],
        kth_exact_after=b[k]['kth_exact'])for k in sorted(a)]
    return dict(queries=len(rows),calibration_identical=before['calibration']==after['calibration'],
        exact_kth_identical=all(r['kth_exact_before']==r['kth_exact_after']for r in rows),
        max_abs_exact_kth_difference=max(abs(r['kth_exact_before']-r['kth_exact_after'])for r in rows),
        improved=sum(r['delta']>0 for r in rows),worse=sum(r['delta']<0 for r in rows),
        unchanged=sum(r['delta']==0 for r in rows),before=recall_contract(before),after=recall_contract(after),
        rows=rows,no_old_outputs_rescored=True)


def feature_metadata_contract(features, wanted, ids_digest, samples):
    """Cross-check retained feature bytes, independent full-ID digest and sample order."""
    features=Path(features);meta=read(features.with_suffix('.json'))
    require(binding(features)==wanted and meta['kind']=='features' and meta['version']==1
            and meta['sha256']==wanted['sha256'] and meta['ids_sha256']==ids_digest
            and meta['samples']==samples and len(samples)==len(set(samples))==10,
            'Local feature metadata/full axis/ordered ten samples differ')
    return dict(status='PASS_INDEPENDENT_LOCAL_SAMPLE_AND_ID_AXIS',metadata=binding(features.with_suffix('.json')),
        features=wanted,full_ids_sha256=ids_digest,ordered_samples=samples)


def summarize_stages(controls, inventory):
    """Distinguish sealed outputs, retained failures and commands never reached."""
    root = Path(controls)/'work'; stages = {}
    paths = [f'retrieval/{u}/{role}' for u in UNITS for role in ['teacher', 'student']]
    paths += ['barrier']+[f'groups/{u}/{role}' for u in UNITS for role in ['teacher', 'student']]
    paths += [f'{u}/{kind}' for kind in ['export', 'audit'] for u in UNITS]
    for prefix in paths:
        done = root/prefix/'done.json'
        members = [p for p in inventory['all_work_members'] if p.startswith(prefix+'/')]
        result = (seal_from_inventory(read(done), prefix, inventory) if done.exists()
            else dict(status='PARTIAL_UNSEALED' if members else 'NOT_RUN', retained_members=len(members)))
        if prefix.startswith('retrieval/') and members:
            for name in ['packing', 'initialization', 'proposal-audit']:
                path = root/prefix/'cache'/(name+'.json')
                if path.exists():
                    result[name] = read(path)
            audit = root/prefix/'cache/audit.json'
            if audit.exists():
                result['recall'] = recall_contract(read(audit))
            if result['status'] == 'PASS':
                require(result['recall']['status'] == 'PASS', 'Sealed failed retrieval')
        stages[prefix] = result
    return stages


def shutdown_contract(provider, guest, completion, completion_bytes, watchdog, started, live, finance):
    """Bind independent provider, guest, completion, process and actual child exits."""
    require(provider['status'] == 'TERMINATED' and not provider.get('guestAccelerators')
            and provider['machineType'].endswith('/e2-standard-8'), 'Original VM is not stopped')
    require(sorted(int(x['diskSizeGb']) for x in provider['disks']) == [30, 300],
            'Original disks differ')
    values = [json.loads(x['value']) for x in guest
              if x['namespace'] == 'e028-candidate' and x['key'] == 'status']
    require(len(values) == 1 and values[0]['completion'] == completion_bytes
            and values[0]['status'] == completion['status']
            and values[0]['science_completed'] == completion['science_completed'],
            'Guest/private final bytes/status differ')
    require(watchdog['shutdown'] is True and watchdog['decision'] == 'workflow exited'
            and watchdog['boot_id'] == live['boot_id']
            and watchdog['expected_process'] == started['identity'] == live['expected_process']
            and live['observed_process'] == started['identity']
            and live['decision'] == 'workflow alive' and live['shutdown'] is False,
            'Exit is not bound to the intended boot/process')
    seconds = (datetime.fromisoformat(provider['lastStopTimestamp'])-
               datetime.fromisoformat(provider['lastStartTimestamp'])).total_seconds()
    require(abs(seconds-finance['measured_allocation_seconds']) < .001
            and finance['cost_and_retention_admitted'] is True, 'Allocation/finance differ')
    names = [s['name'] for s in completion['stages']]
    expected = ['workflow']+(['used-inputs-after'] if completion['science_completed'] else [])+['collect']
    expected += [prefix+name for name in ['e028-evidence.tar.gz',
        'e028-evidence.tar.gz.sha256', 'collection.json', 'collection-disk.jsonl',
        'terminal-disk.json'] for prefix in ['upload-', 'readback-']]
    require(names == expected, 'Missing/extra actual phase command')
    success = completion['stages'][0]['resources']['exit_code'] == 0
    require(success == completion['science_completed']
            and completion['status'] == ('SUCCESS' if success else 'FAILED')
            and completion['collection_readback_verified'] is True
            and all(s['resources']['exit_code'] == 0 for s in completion['stages'][1:]),
            'Workflow/collection exits contradict final status')
    require(completion['source_commit'] == SOURCE, 'Different science source')
    return dict(status='PASS_INDEPENDENT_STOP_AND_DELIVERY', provider='TERMINATED',
        science_status=completion['status'], science_completed=success,
        stage_exits={s['name']:s['resources']['exit_code'] for s in completion['stages']},
        intended_watchdog_process_verified=True, measured_allocation_seconds=seconds,
        guest_private_completion_verified=True)


def source_contract(controls):
    """Verify returned executed Git bytes, all release gates and full native axes."""
    root = Path(controls)/'evidence'; lock = read(EXP/'source-lock.json')
    for name, wanted in lock['files'].items():
        require(binding(root/'source'/name) == wanted, 'Returned source differs: '+name)
        value = subprocess.check_output(['git','show',SOURCE+':'+name],cwd=ROOT)
        require(dict(bytes=len(value),sha256=hashlib.sha256(value).hexdigest()) == wanted,
                'Executed Git source differs: '+name)
    control = root/'controls'; delivery = read(control/'control-inventory.json')
    require(not delivery['missing'], 'Release control is missing')
    for name, wanted in delivery['copied'].items():
        require(binding(control/name) == wanted, 'Delivered control differs: '+name)
    release = read(control/'release.json'); cfg = read(control/'config.json')
    for name, wanted in release['gate_files'].items():
        path = Path(name)
        require(path.is_relative_to(cfg['root']), 'Release gate outside phase')
        require(binding(control/path.relative_to(cfg['root'])) == wanted,
                'Released gate differs: '+name)
    require(release['config'] == binding(control/'config.json')
            and release['plan'] == binding(control/'science-plan.json'), 'Released plan/config differs')
    gates = read(root/'gates/completion.json')
    require(gates['status'] == 'PASS' and len(gates['stages']) == 10
            and all(s['resources']['exit_code'] == 0 for s in gates['stages']), 'Native gate failed')
    runtime = read(root/'gates/runtime.json'); candidate = read(EXP/'candidate-lock.json')
    require(runtime['status'] == 'PASS_COMPLETE_READONLY_BASE_AND_NEW_OWNED_PACKAGE'
            and runtime['package_files'] == candidate['package_files']
            and len(runtime['distributions']) == 41, 'Owned installed runtime differs')
    require(read(root/'gates/ann-source.json')['source'] == read(EXP/'ann-source-lock.json')['binding'],
            'Actual native ANN source differs')
    data = read(root/'gates/data.json'); protocol = read(EXP/'protocol.json')
    require(data['status'] == 'PASS', 'Native before-input verification failed')
    for unit, axis in protocol['axes'].items():
        expected = dict(axis, GLM_in_teacher_proposals_student=unit=='E009-GLM')
        require(data['axes'][unit] == expected, 'Full axis or information availability differs')
    reuse = read(EXP/'reuse-lock.json')
    expected = {str(Path(reuse['source_work'])/k):v for k,v in reuse['all_closed_stage_members'].items()}
    expected.update(reuse['external_files'])
    observed = dict(data['hashed'], **data['unused_admitted_arrays_stat_only'])
    require(expected == observed, 'Native used-member/stat-only inventory differs')
    return dict(status='PASS_EXECUTED_SOURCE_NATIVE_BEFORE_INPUTS', commit=SOURCE,
        source_files=len(lock['files']), native_gates=10,
        native_gates_exits={s['stage']:s['resources']['exit_code'] for s in gates['stages']},
        owned_package_files=len(runtime['package_files']), numerical_distributions=41,
        axes=data['axes'], hash_verified_files=len(data['hashed']),
        unused_admitted_arrays_stat_only=len(data['unused_admitted_arrays_stat_only']),
        used_input_after_present=False, scope='Before-use native contracts; no claim of whole-VM after-state')


def review(base, output):
    """Create one compact failed-or-complete outcome without scoring old/new bins."""
    base = Path(base); controls = base/'controls'; ctl = base/'control-r3'
    finance = read(base/'finance/transfer-admission.json'); inventory = read(base/'inventory.json')
    proof = read(base/'archive-verified.json')
    require(proof['every_member_verified'] and proof['archive'] == finance['archive'], 'Archive not admitted')
    source = source_contract(controls)
    shutdown = shutdown_contract(read(ctl/'provider.json'), read(ctl/'guest.json'),
        read(ctl/'completion.json'),binding(ctl/'completion.json'),read(ctl/'watchdog-exit.json'),
        read(controls/'evidence/controls/started.json'),
        read(controls/'evidence/controls/logs/watchdog-live-before-release.json'),finance)
    stages = summarize_stages(controls, inventory)
    passed = [p for p,s in stages.items() if s['status'] == 'PASS']
    complete = all(s['status'] == 'PASS' for s in stages.values())
    require(complete == shutdown['science_completed'], 'Actual science stages contradict driver')
    after = 'used-inputs-after.json' in inventory['all_work_members']
    source['used_input_after_present'] = after
    if complete:
        require(after, 'Completed workflow lacks final input verification')
    old=ROOT/'artifacts/e027-common-information-binner/inspection-20261031'
    old_path=old/'controls/work/units/oral-noGLM/group/teacher/retrieval/audit.json'
    query_comparison=None
    if old_path.exists():
        old_inventory=read(old/'verified/inventory.json')
        require(binding(old_path)==old_inventory['members']['work/units/oral-noGLM/group/teacher/retrieval/audit.json'],
                'Prior accepted search receipt differs')
        query_comparison=matched_queries(read(old_path),read(controls/'work/retrieval/oral-noGLM/teacher/cache/audit.json'))
        query_comparison['before_binding']=binding(old_path)
    axes={}
    numeric=read(base/'numeric-audit.json')if(base/'numeric-audit.json').exists()else None
    if numeric:
        require(numeric['status']=='PASS_ACTUAL_READER_AND_AXES','Local sparse reader failed')
        paths={'E009-noGLM':ROOT/'artifacts/e011-cached-grouping-reference/restore-local/candidate/features/features.npz',
            'oral-noGLM':ROOT/'artifacts/e024-inspection/20261028T193107Z/verified/work/rebound/features.npz'}
        for unit,path in paths.items():
            proof=numeric['caches'][unit+'/teacher']
            axes[unit]=feature_metadata_contract(path,proof['features'],proof['full_axis_sha256'],source['axes'][unit]['samples'])
    result = dict(kind='E028 independent stopped-return inspection',phase='discovery-20261031T204532Z-45a7590',
        source=source,shutdown=shutdown,stages=stages,completed_stages=passed,
        final_target_complete=complete,used_inputs_after_present=after,archive=proof,
        candidate_quality_status='READY_FOR_SEPARATE_FROZEN_DIAGNOSTICS' if complete else 'NOT_ASSESSABLE',
        biological_KEEP_MODIFY_ABANDON='NOT_ASSESSABLE' if not complete else 'PENDING_FROZEN_DIAGNOSTICS',
        matched_Oral_search_receipts=query_comparison,
        independent_local_feature_metadata=axes,
        no_truth_scores_computed=True,no_VM_wake_or_science_replay=True)
    write(output,result)
    print(json.dumps(dict(shutdown=shutdown,completed_stages=passed,candidate_quality_status=result['candidate_quality_status'])),flush=True)
    return result


if __name__ == '__main__':
    a=argparse.ArgumentParser(description=__doc__);a.add_argument('--base',type=Path,required=True);a.add_argument('--output',type=Path,required=True)
    v=a.parse_args();review(v.base,v.output)
