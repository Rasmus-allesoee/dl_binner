#!/usr/bin/env python3
"""Read only new E031 outputs on the existing CPU, then collect compact evidence.

This explicit post-shutdown recovery preserves the first learner clock and fixed
truth readers. It has no fit, grouping, marker, acquisition or VM-start entry
point. The controller must arm a fresh held-parent exit watcher and provider
STOP before release. Accepted dependency/source/truth files are verified/reused.
"""
import argparse
from collections import Counter
import hashlib
import io
import json
import math
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tarfile
import time

START = 1793649752.426
DEADLINE = START + 57600
SOURCE = 'ba659119c3ec86edc83e27bad95939326fbaa2b8'
UNITS = ['E009-noGLM', 'E009-GLM', 'oral-noGLM']


def check_config(cfg, now):
    """Require the original clock, already admitted science and read-only bounds."""
    if (cfg['original_start_epoch'] != START or cfg['science_source'] != SOURCE
            or not now < cfg['review_deadline_epoch'] <= min(DEADLINE, cfg['review_started_epoch'] + 3600)
            or cfg['provider_deadline_epoch'] > START + 58500
            or cfg['review_deadline_epoch'] >= 1793746800 or cfg['review_RSS_bytes'] != 8_000_000_000
            or cfg['numerical_threads'] != 4 or not cfg['credit_only_admitted']
            or cfg['incremental_ceiling_USD'] != 8 or cfg['complete_cost_USD_upper'] > 8):
        raise ValueError('Original source/clock/credit/resource scope differs')


def counter_audit(before, after, updates):
    """Check genuine lazy Adam counters without inventing one common step value."""
    if type(updates) is not int or updates < 1 or not set(before) <= set(after):
        raise ValueError('Optimizer state/counter population differs')
    rows = []
    for key, final in after.items():
        old = before.get(key)
        a = float(old['step']) if old is not None else 0.0
        b = float(final['step'])
        if not all(math.isfinite(v) and v.is_integer() for v in [a, b]) or not 0 <= b - a <= updates:
            raise ValueError('Optimizer counter exceeds actual update exposure')
        rows.append(dict(parameter_id=int(key), inherited_step=int(a), final_step=int(b),
                         updates=int(b-a), originally_lazy=old is None))
    return dict(parameters=rows, delta_histogram=dict(Counter(r['updates'] for r in rows)),
                distinct_inherited_steps=sorted({r['inherited_step'] for r in rows}),
                distinct_final_steps=sorted({r['final_step'] for r in rows}))


def configure(cfg):
    """Import only the exact retained scientific source and accepted runtime."""
    sys.path.insert(0, str(Path(cfg['scientific_repo']) / 'scripts'))


def tensor_audit(cfg):
    """Inspect retained checkpoint states and Adam counters, with no model forward."""
    configure(cfg)
    import torch
    from e024_coverage import binding, write
    torch.set_num_threads(4)
    plan = json.loads(Path(cfg['science_plan']).read_text())
    inv = json.loads((Path(cfg['admission_root']) / 'inventory.json').read_text())['all_work_members']
    original = json.loads((Path(cfg['science_root']) / 'gates/data.json').read_text())['hashed_inputs']
    def digest(state):
        h = hashlib.sha256()
        for name, value in state.items():
            x = value.detach().cpu().contiguous()
            h.update(json.dumps([name, str(x.dtype), list(x.shape)]).encode()); h.update(x.numpy().tobytes())
        return h.hexdigest()
    result = {}
    for unit in UNITS:
        folder = Path(cfg['science_root']) / 'work' / unit / 'train/result'
        old = Path(plan['units'][unit]['bootstrap']); new = folder / 'checkpoint.pt'
        meta = json.loads((folder / 'checkpoint.json').read_text())
        if binding(old) != original[str(old)] or binding(new) != inv[unit + '/train/result/checkpoint.pt']:
            raise ValueError('Bound native checkpoint bytes differ')
        a = torch.load(old, map_location='cpu', weights_only=True)
        b = torch.load(new, map_location='cpu', weights_only=True)
        states = [('online', 'model_state'), ('target', 'target_state'), ('predictor', 'predictor_state')]
        for label, key in states:
            if digest(a[key]) != meta['initial_state'][label] or digest(b[key]) != meta['final_state'][label]:
                raise ValueError('Original/final named state or buffers differ')
        if digest(a['model_state']) != digest(b['anchor_state']) or digest(b['anchor_state']) != meta['final_state']['anchor']:
            raise ValueError('Fixed bootstrap anchor changed')
        if b['inherited_updates'] != a['ema_updates'] or b['added_updates'] != meta['added_updates']:
            raise ValueError('Inherited/added EMA exposure differs')
        for state in b['optimizer_state']['state'].values():
            for name, tensor in state.items():
                if not torch.isfinite(tensor).all():
                    raise ValueError('Nonfinite retained optimizer state: ' + name)
        groups = b['optimizer_state']['param_groups']
        if len(groups) != 1 or groups[0]['lr'] != .0002:
            raise ValueError('Actual continuation optimizer rate differs')
        result[unit] = dict(status='PASS', bootstrap=binding(old), checkpoint=binding(new),
            optimizer=counter_audit(a['optimizer_state']['state'], b['optimizer_state']['state'], b['added_updates']),
            inherited_updates=b['inherited_updates'], added_updates=b['added_updates'],
            complete_modules_and_buffers_restored=True, fixed_anchor_exact=True, model_forward_performed=False)
        del a, b
    write(Path(cfg['root']) / 'outputs/tensor-audit.json', dict(status='PASS', units=result, inference=False))


def neighbors(cfg):
    """Review only the three new frozen query caches; no neighbor index is built."""
    configure(cfg)
    from e024_coverage import write
    from e031_neighbors import evaluate_queries
    from e014_review import oral_labels
    from dl_binner.multiview.views import load
    repo = Path(cfg['review_view']); plan = json.loads(Path(cfg['science_plan']).read_text())
    lock = json.loads((repo / 'experiments/E013-marker-quality/review-lock.json').read_text())
    truth = json.loads((repo / lock['truth_root'] / 'truth.json').read_text())
    targets = json.loads((repo / lock['truth_root'] / 'targets.json').read_text())
    pop = json.loads((repo / lock['population_path']).read_text())
    labels = {q: c['AMBER_label'] for q, c in truth['contigs'].items()}
    lineages = {g: v['lineage_class'] for g, v in pop['genomes'].items()}
    actors = {}
    for unit in UNITS[:2]:
        q = json.loads((Path(cfg['science_root']) / 'work' / unit / 'e023/query-neighbors.json').read_text())
        actors[unit] = evaluate_queries(q['queries'], labels, lineages, targets['targets'])
    del truth, labels
    data, _ = load(plan['units']['oral-noGLM']['features'])
    lab, _, _, genomes, truth = oral_labels(Path(cfg['review_view']) / 'artifacts/e014-multiview-reconstruction/oral-truth-origin-v1', data['ids'].tolist(), data['lengths'])
    labels = {q: genomes[int(g)] if g >= 0 else None for q, g in zip(data['ids'].tolist(), lab)}
    q = json.loads((Path(cfg['science_root']) / 'work/oral-noGLM/e023/query-neighbors.json').read_text())
    actors['oral-noGLM'] = evaluate_queries(q['queries'], labels, {}, truth['targets'])
    write(Path(cfg['root']) / 'outputs/matched-neighbors.json', dict(status='PASS', actors=actors,
        old_scores_recomputed=False, search_or_inference_performed=False, technical_query_population_only=True))


def run(cfg, config_path):
    """Hold for supervision, run six frozen readers, and return bounded evidence."""
    configure(cfg); check_config(cfg, time.time())
    from e021_control_json import publish
    from e024_coverage import binding
    from e009_exit_watchdog import identity
    from e009_owner import supervisor
    from e009_controls import PhaseGuard
    from e031_phase import readback
    root = Path(cfg['root']); logs = root / 'logs'; outputs = root / 'outputs'
    outputs.mkdir(); sup = supervisor(); env = sup.isolated_env(4)
    env.update(NUMBA_NUM_THREADS='4', PYTHONDONTWRITEBYTECODE='1', HF_HUB_OFFLINE='1',
               CLOUDSDK_STORAGE_PARALLEL_COMPOSITE_UPLOAD_ENABLED='false',
               CLOUDSDK_STORAGE_PROCESS_COUNT='1', CLOUDSDK_STORAGE_THREAD_COUNT='2')
    publish(dict(pid=os.getpid(), identity=identity(os.getpid()), epoch=time.time()), root / 'started.json')
    result = dict(status='HELD', scientific_source=SOURCE, operations_source=cfg['operations_source'],
                  no_science_replayed=True, old_baselines_rescored=False, stages=[])
    try:
        with PhaseGuard(root, cfg['review_deadline_epoch']-time.time(), growth_bytes=4*1024**3) as guard:
            while not (root / 'release.json').exists():
                if time.time() > cfg['setup_deadline_epoch'] or (root / 'abort.json').exists():
                    raise TimeoutError('Held read-only setup expired')
                time.sleep(.2)
            release = json.loads((root / 'release.json').read_text())
            watch = json.loads((logs / 'watchdog-live-before-release.json').read_text())
            if release['config'] != binding(config_path) or not release['provider_STOP_verified'] or watch['expected_process'] != identity(os.getpid()):
                raise ValueError('Read-only supervision release differs')
            def command(name, argv):
                left = cfg['review_deadline_epoch'] - time.time() - 180
                if left < 10:
                    raise TimeoutError('Original cumulative review clock exhausted')
                print('E031_READONLY_STAGE', name, flush=True)
                resources = sup.supervise(argv, logs / (name+'.log'), left, 8_000_000_000, env)
                result['stages'].append(dict(name=name, resources=resources))
                publish(dict(stage=name, resources=resources), root / ('progress-'+name+'.json'))
            py = cfg['python']; own = root / 'operations/e031_learning_diagnostics.py'
            command('retained-tensor-audit', [py, '-I', '-B', own, '--config', config_path, '--tensor'])
            view = Path(cfg['review_view'])
            for unit in UNITS:
                for comparison in ['learning', 'learning-E023']:
                    name = 'review-' + unit + '-' + comparison
                    marker = ('artifacts/e011-cached-grouping-reference/restore-local/candidate/markers/evidence.json'
                              if unit.startswith('E009') else 'artifacts/e014-multiview-reconstruction/inspection-20261019/oral-marker-review.json')
                    command(name, [py, '-I', '-B', view / 'scripts/e031_review.py', '--base', cfg['admission_root'],
                        '--staged', cfg['science_root'], '--unit', unit, '--role', 'student',
                        '--comparison', comparison, '--features', cfg['units'][unit]['features'],
                        '--marker-clean', view / marker, '--truth-root', view / 'artifacts/e014-multiview-reconstruction/oral-truth-origin-v1',
                        '--output', outputs / name])
            command('matched-new-queries', [py, '-I', '-B', own, '--config', config_path, '--neighbors'])
            result.update(status='SUCCESS', diagnostics_completed=True, disk_samples=guard.observations)
    except BaseException as exc:
        result.update(status='FAILED', error=repr(exc))
    publish(result, root / 'result.json')
    try:
        files = [p for folder in [outputs, logs, root/'operations'] for p in sorted(folder.rglob('*')) if p.is_file()]
        files += [root/n for n in ['config.json', 'host.json', 'inputs.json', 'release.json', 'result.json'] if (root/n).is_file()]
        members = {str(p.relative_to(root)): binding(p) for p in files}
        if len(members)>2000 or sum(v['bytes'] for v in members.values())>128*1024**2:
            raise ValueError('Compact diagnostic inventory exceeds limit')
        archive = root/'learning-review.tar.gz'
        with tarfile.open(archive, 'x:gz') as a:
            raw=(json.dumps(members, sort_keys=True)+'\n').encode(); item=tarfile.TarInfo('inventory.json'); item.size=len(raw)
            a.addfile(item, io.BytesIO(raw))
            for name in sorted(members): a.add(root/name, arcname=name, recursive=False)
        if archive.stat().st_size>32*1024**2:
            raise ValueError('Compact diagnostic compressed cap exceeded')
        url=cfg['archive_prefix']+'learning-review.tar.gz'; b=binding(archive)
        subprocess.run([cfg['gcloud'], 'storage', 'cp', '--if-generation-match=0', str(archive), url], env=env, check=True, capture_output=True, timeout=120)
        readback(cfg['gcloud'], url, b['bytes'], b['sha256'])
        result.update(archive=b, members=len(members), archive_url=url, collection_readback_verified=True)
    except BaseException as exc:
        result.update(status='FAILED', collection_error=repr(exc))
    result.update(finished_epoch=time.time(), config=binding(config_path), disk=shutil.disk_usage(root)._asdict())
    publish(result, root/'completion.json')
    subprocess.run([cfg['gcloud'], 'storage', 'cp', '--if-generation-match=0', str(root/'completion.json'), cfg['archive_prefix']+'completion.json'], env=env, check=True, capture_output=True, timeout=90)
    print('E031_READONLY_COMPLETE', json.dumps({k:v for k,v in result.items() if k not in ['stages','disk_samples']}), flush=True)
    return 0 if result['status']=='SUCCESS' else 1


if __name__ == '__main__':
    p=argparse.ArgumentParser(description=__doc__); p.add_argument('--config', type=Path, required=True)
    p.add_argument('--tensor', action='store_true'); p.add_argument('--neighbors', action='store_true'); a=p.parse_args()
    cfg=json.loads(a.config.read_text())
    if a.tensor: tensor_audit(cfg)
    elif a.neighbors: neighbors(cfg)
    else: sys.exit(run(cfg, a.config))
