#!/usr/bin/env python3
"""Gate one cache-only integration using the already accepted E019 environment.

All verification and tiny consumers count from the original VM start. There is
no installer, source recopy, inference, detector or scientific retry path here.
"""
import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time
sys.path.insert(0, str(Path(__file__).absolute().parent))
from e014_collect import binding
from e009_common import write_json
from e009_owner import supervisor, Tee
from e009_controls import PhaseGuard
from e019_bootstrap import require_headroom


def context_input(features, embeddings):
    """Validate original context metadata and full opaque unit-sphere axes, read-only."""
    from dl_binner.information.grouping import load_inputs
    from dl_binner.multiview.arrays import load_arrays
    data, vectors, valid, meta = load_inputs(features, embeddings)
    em = json.loads(Path(embeddings).with_suffix('.json').read_text())
    if (em.get('mode') != 'context_online_unit_sphere' or em.get('reload_exact') is not True
            or em.get('samples') != meta['samples']
            or em.get('metric') != 'unit-sphere cosine/equivalent Euclidean; no post-learning transform'
            or any(len(em.get(k, '')) != 64 for k in ['checkpoint_sha256', 'tokens_manifest_sha256'])):
        raise ValueError('Exact retained E019 context metadata required')
    return data, vectors, valid, meta, em


def inputs(plan, output):
    """Require complete original community populations and ten-depth or absent axes."""
    from e020_control import validate_plan
    p = json.loads(Path(plan).read_text()); validate_plan(p); units = {}
    for unit, u in p['units'].items():
        data, vectors, valid, meta, em = context_input(u['features'], u['embeddings'])
        samples = ['cami3_toy_human_gut_short_read_sample_'+str(i)
                   for i in [0, 2, 3, 4, 6, 9, 10, 11, 14, 17]] if unit == 'E009-context' else []
        n, bp, eligible = (145702, 231678157, 89041) if unit == 'E009-context' else (1286547, 1669981123, 508763)
        if (len(data['ids']) != n or int(data['lengths'].sum()) != bp or int(valid.sum()) != eligible
                or meta['samples'] != samples or data['depth'].shape != (n, len(samples))):
            raise ValueError('Complete DNA/depth/eligible axes differ')
        units[unit] = dict(rows=n, bp=bp, eligible=eligible, samples=samples,
            features=binding(u['features']), embeddings=binding(u['embeddings']),
            context_metadata=em, measured_parent_depth=meta['depth_semantics'])
        del data, vectors
    write_json(output, dict(status='PASS', units=units, inference=False, truth_used=False))


def run(path):
    """Run only new reader/launcher gates and reuse accepted runtime/setup unchanged."""
    path = Path(path); cfg = json.loads(path.read_text()); root = Path(cfg['root']); repo = Path(cfg['repo'])
    gates = root/'gates'; gates.mkdir(exist_ok=False)
    plan = json.loads(Path(cfg['science_plan']).read_text()); py = plan['python']
    deadline = cfg['vm_start_epoch']+900
    result = dict(status='FAILED', config=binding(path), stages=[], accepted_setup_reinstalled=False)
    sup = supervisor(); env = sup.isolated_env(4)
    env.update(NUMBA_NUM_THREADS='4', NUMBA_CACHE_DIR=str(root/'native-cache'), TMPDIR=str(root/'tmp'))
    def command(name, argv):
        """Retain exit and sampled process usage within the same original clock."""
        left = deadline-time.time()-10
        if left < 15:
            raise TimeoutError('Original 15-minute native gate allowance exhausted')
        print('E020_NATIVE_GATE', name, flush=True)
        r = sup.supervise(argv, gates/(name+'.log'), min(600, left), 26_000_000_000, env, sample_root=os.getpid())
        result['stages'].append(dict(name=name, resources=r))
    try:
        usage = shutil.disk_usage(root)
        require_headroom(usage.free, usage.used, cfg['initial_filesystem_used_bytes'])
        with PhaseGuard(root, deadline-time.time()-10,
                growth_bytes=20*1024**3-max(0, usage.used-cfg['initial_filesystem_used_bytes'])) as guard:
            if sys.platform != 'linux' or os.cpu_count() != 8 or not os.path.ismount('/srv/dl_binner'):
                raise ValueError('Existing Linux allocation/mount required')
            if (subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=repo, text=True).strip() != cfg['source_commit']
                    or subprocess.check_output(['git', 'status', '--porcelain'], cwd=repo, text=True).strip()):
                raise ValueError('Exact clean source required')
            lock = json.loads(Path(cfg['reuse_lock']).read_text())
            frozen = json.loads((repo/'experiments/E020-context-information-integration/candidate-lock.json').read_text())
            for key, expected in frozen['files'].items():
                if binding(repo/key) != expected:
                    raise ValueError('Frozen new consumer/source differs: '+key)
            command('retained-byte-reuse', [sys.executable, '-I', '-B', str(repo/'scripts/e020_reuse.py'),
                '--lock', cfg['reuse_lock'], '--output', str(gates/'reuse-before.json')])
            command('complete-existing-runtime-source-library', [py, '-I', '-B', str(repo/'scripts/e019_runtime.py'),
                'probe', '--base', lock['runtime']['prefix'], '--lock', cfg['reuse_lock'], '--output', str(gates/'runtime.json')])
            command('full-context-axes', [py, '-I', '-B', str(repo/'scripts/e020_bootstrap.py'),
                '--inputs', cfg['science_plan'], '--output', str(gates/'inputs.json')])
            command('context-metadata-sparse-opaque-reader-refusal', [py, '-I', '-B', str(repo/'tests/test_e020_integration.py'),
                '--context-root', lock['native_context_tiny'], '--output', str(gates/'tiny-context.json')])
            command('cached-marker-worker-refiner-four-export', [py, '-I', '-B',
                str(repo/'experiments/E020-context-information-integration/engineering_fixture.py'),
                '--cached', lock['native_marker_tiny'], '--layout', 'marker', '--output', str(gates/'tiny-cached')])
            command('launcher-collector-contracts', [sys.executable, '-I', '-B', str(repo/'tests/test_e020_operations.py')])
            command('serial-DAG-dryrun', [py, '-I', '-B', str(repo/'scripts/e020_control.py'),
                '--plan', cfg['science_plan'], '--workflow', '--dry-run'])
            result.update(status='SUCCESS', disk_observations=guard.observations)
    except BaseException as exc:
        result['error'] = f'{type(exc).__name__}: {exc}'
    write_json(gates/'completion.json', result)
    print('E020_NATIVE_GATES_EXIT', result['status'], result.get('error'), flush=True)
    return 0 if result['status'] == 'SUCCESS' else 1


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--config', type=Path); p.add_argument('--inputs', type=Path); p.add_argument('--output', type=Path)
    a = p.parse_args()
    if a.inputs:
        inputs(a.inputs, a.output)
    else:
        cfg = json.loads(a.config.read_text())
        with (Path(cfg['root'])/'logs/bootstrap-terminal.log').open('x') as f:
            old = sys.stdout, sys.stderr; sys.stdout = Tee(sys.stdout, f); sys.stderr = Tee(sys.stderr, f)
            try:
                code = run(a.config)
            finally:
                sys.stdout, sys.stderr = old
        raise SystemExit(code)
