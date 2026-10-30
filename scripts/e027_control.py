#!/usr/bin/env python3
"""Frozen common-version three-arm worker; truth and cloud mutation are absent.

Snakemake owns stage dependencies and the four-core/26-GB aggregate cap. Every
completed stage is sealed, and verified resume refuses incomplete or drifted
artifacts. Operational recovery cannot silently replay a successfully sealed fit.
"""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).absolute().parents[1]
sys.path[:0] = [str(ROOT/'scripts'), str(ROOT/'src')]
from e024_coverage import binding, write
from e024_control import fresh, seal, verify_seal

EXP = ROOT/'experiments/E027-common-information-binner'
UNITS = ['E009-noGLM', 'E009-GLM', 'oral-noGLM']
STAGES = ['admit', 'teacher', 'teacher-embed', 'teacher-graph', 'pairs',
          'student', 'student-embed', 'student-graph', 'group', 'export', 'audit']


def freeze():
    """Bind the new implementation and preserve all inherited accepted source locks."""
    from e026_gates import freeze as previous
    inherited = previous()
    lock = json.loads((EXP/'source-lock.json').read_text())
    for name, wanted in lock['files'].items():
        if binding(ROOT/name) != wanted: raise ValueError('Frozen E027 source differs: '+name)
    return dict(status='PASS', inherited=inherited, current=binding(EXP/'source-lock.json'))


def read_plan(path, engineering=False):
    """Require declared common source/modes and external held-parent release."""
    p = json.loads(Path(path).read_text())
    fields = {'kind', 'work', 'units', 'reference', 'python', 'workflow_python', 'worker',
              'snakefile', 'policy', 'limits', 'engineering', 'reuse_lock', 'learning_reuse_lock', 'wheel'}
    if (set(p) != fields or p['kind'] != 'E027 common full-version information binner'
            or p['engineering'] is not engineering or set(p['units']) != set(UNITS)):
        raise ValueError('Unexpected common-version plan/scope')
    unit_fields = {'fasta', 'original_features', 'features', 'views', 'tokens', 'frozen',
                   'marker_cache', 'hmm', 'marker_evidence', 'measured_receipt'}
    if any(set(u) != unit_fields for u in p['units'].values()):
        raise ValueError('Unknown training/truth path or incomplete availability contract')
    if any((p['units'][u]['frozen'] is not None) != (u == 'E009-GLM') for u in UNITS):
        raise ValueError('GLM teacher/proposal/student availability differs')
    if not engineering:
        expected = json.loads((EXP/'runtime-plan.json').read_text())
        if any(p[k] != expected[k] for k in fields-{'work', 'python', 'wheel'}):
            raise ValueError('Frozen common version/runtime/input policy differs')
        if not Path(p['work']).is_relative_to('/srv/dl_binner/experiments/e027'):
            raise ValueError('Fresh E027 work root required')
        release = os.environ.get('E027_RELEASE_FILE')
        if not release or json.loads(Path(release).read_text()).get('plan') != binding(path):
            raise ValueError('Externally supervised native release required')
        freeze()
        reuse = json.loads(Path(p['learning_reuse_lock']).read_text())['models']
        if {k: set(v) for k, v in reuse.items()} != {'E009-noGLM': {'teacher'}, 'E009-GLM': {'teacher', 'student'}}:
            raise ValueError('Declared identical-learning reuse changed; no fitting fallback')
    return p


def verify_inputs(p, engineering=False):
    """Verify named source bytes and all complete axes, not a repeated old science DAG."""
    from dl_binner.multiview.views import load
    result = {}
    if not engineering:
        lock = json.loads(Path(p['reuse_lock']).read_text())
        for name, wanted in lock['files'].items():
            if binding(name) != wanted: raise ValueError('Missing/corrupt retained input; no fallback: '+name)
    for name, u in p['units'].items():
        old, _, _, _ = load(u['original_features'], u['views'])
        data, meta = load(u['features'])
        actual = dict(rows=len(data['ids']), bp=int(data['lengths'].sum()), eligible=int(data['eligible'].sum()),
                      samples=meta['samples'])
        if not engineering:
            expected = json.loads((EXP/'protocol.json').read_text())['axes'][name]
            if actual != {k: expected[k] for k in actual}: raise ValueError('Full contig/ordered sample axes differ: '+name)
        if engineering and (actual['rows'] > 128 or actual['bp'] > 1_000_000):
            raise ValueError('Engineering fixture exceeds declared tiny scope')
        result[name] = actual
    return dict(status='PASS', units=result, copied_or_regenerated_science=False,
        verified_reuse_lock=binding(p['reuse_lock']) if not engineering else None,
        verified_learning_reuse_lock=binding(p['learning_reuse_lock']) if not engineering else None)


def verify_after(p, engineering=False):
    """Retain the final used-input proof in the collected work, without overwriting."""
    result = verify_inputs(p, engineering); target = Path(p['work'])/'used-inputs-after.json'
    if target.is_file():
        if json.loads(target.read_text()) != result: raise ValueError('Accepted final input proof differs')
    else: write(target, result)
    return result


def input_bindings(u):
    """Bind only actual stage inputs; runtime/cache arrays are admitted separately."""
    result = {}
    for k in ['fasta', 'original_features', 'features', 'views', 'hmm', 'marker_evidence']:
        result[k] = binding(u[k])
    for k, manifest in [('tokens', 'tokens.json'), ('marker_cache', 'cache.json'), ('frozen', 'bank.json')]:
        result[k] = binding(Path(u[k])/manifest) if u[k] is not None else None
    if u['measured_receipt']: result['measured_receipt'] = binding(u['measured_receipt'])
    return result


def stage(path, unit, name, engineering=False):
    """Run one exclusive new stage; no accepted teacher/student output is repeated."""
    from dl_binner.unified import training
    from dl_binner.multiview.views import load
    p = read_plan(path, engineering)
    if unit not in UNITS or name not in STAGES: raise ValueError('Unknown arm/stage')
    u = p['units'][unit]; root = Path(p['work'])/'units'/unit; root.mkdir(parents=True, exist_ok=True)
    cfg = training.configuration(u['frozen'] is not None)
    learning = {} if engineering else json.loads(Path(p['learning_reuse_lock']).read_text())['models'].get(unit, {})
    if engineering:
        _, _, _, vm = load(u['original_features'], u['views'])
        cfg.update(vm['policy'])
    target = root/name
    if (target/'done.json').exists():
        raise FileExistsError('Completed stage must be resumed through verified DAG, never replayed')
    if target.is_dir() and not any(target.iterdir()): target.rmdir()
    views = root/'admit/views.npz'; tokens = root/'admit/tokens'
    if name != 'admit':
        r = verify_seal(root/'admit')
        if r['inputs'] != input_bindings(u): raise ValueError('Accepted inputs drifted since training admission')
    if name == 'admit':
        from dl_binner.unified import cache
        cache.admit(u['original_features'], u['features'], u['views'], u['tokens'], target, u['measured_receipt'])
        write(target/'information-contract.json', training.information_contract(u['frozen'] is not None, bool(learning)))
        return seal(target, dict(inputs=input_bindings(u)))
    role = name.split('-')[0]
    if role in learning or name == 'pairs' and 'student' in learning:
        from e027_learning_reuse import restore
        entry = learning[role] if role in learning else learning['student']
        kind = 'pairs' if name == 'pairs' else 'embed' if name.endswith('-embed') else 'graph' if name.endswith('-graph') else 'fit'
        restore(entry, u, cfg, views, tokens, target, kind)
        return seal(target, dict(identical_learning_reused=True))
    if name == 'teacher':
        training.bootstrap(u['features'], views, tokens, u['frozen'], target, cfg)
    elif name == 'teacher-embed':
        target = fresh(root, name)
        training.reload_bootstrap(u['features'], views, tokens, u['frozen'], root/'teacher/checkpoint.pt', target/'embeddings.npz')
    elif name == 'teacher-graph':
        from dl_binner.unified import graph
        graph.prepare(u['features'], root/'teacher-embed/embeddings.npz', target, cfg)
    elif name == 'pairs':
        from dl_binner.relational.pairs import prepare, load_pairs
        target = fresh(root, name)
        prepare(u['features'], root/'teacher-embed/embeddings.npz', root/'teacher-graph/graph.npz',
                u['marker_cache'], u['hmm'], target/'cache')
        pairs, receipt = load_pairs(target/'cache', u['features'])
        if not engineering and min(int((pairs['sign'] == s).sum()) for s in [-1, 1]) < 20:
            raise ValueError('Too few reliable own-teacher signed pairs; evidence kept, no substitute')
    elif name == 'student':
        training.student(u['features'], views, tokens, u['frozen'], root/'pairs/cache', target, cfg)
    elif name == 'student-embed':
        from dl_binner.relational.model import embed
        target = fresh(root, name)
        embed(u['features'], views, tokens, u['frozen'], root/'pairs/cache', root/'student/checkpoint.pt', target/'embeddings.npz', 4)
    elif name == 'student-graph':
        from dl_binner.unified import graph
        graph.prepare(u['features'], root/'student-embed/embeddings.npz', target, cfg)
    elif name == 'group':
        from dl_binner.unified import grouping
        target = fresh(root, name)
        for learner in ['teacher', 'student']:
            grouping.run(u['features'], root/(learner+'-embed/embeddings.npz'), root/(learner+'-graph/graph.npz'),
                         u['marker_evidence'], target/learner)
    elif name == 'export':
        from dl_binner.information.export import export
        target = fresh(root, name); accounting = {}
        for learner in ['teacher', 'student']:
            for arm in ['parent', 'post']:
                key = learner+'-'+arm
                accounting[key] = export(u['features'], root/'group'/learner/(arm+'-partition.json'),
                    u['fasta'], target/key, include_dna=False)
        write(target/'accounting.json', accounting)
        write(target/'DNA-reuse.json', dict(status='PASS', full_input_fasta=binding(u['fasta']),
            path=u['fasta'], complete_assignments=True, physical_DNA_emission=False,
            reason='Avoid copying identical accepted DNA four times; exact assignment plus protected source reconstructs every bin'))
    elif name == 'audit':
        from dl_binner.unified import grouping
        target = fresh(root, name); proofs = {}
        for learner in ['teacher', 'student']:
            proofs[learner] = grouping.audit(u['features'], root/(learner+'-embed/embeddings.npz'),
                root/(learner+'-graph/graph.npz'), u['marker_evidence'], root/'group'/learner)
        write(target/'proof.json', dict(status='PASS', learners=proofs, inputs_unchanged=True))
    return seal(target)


def reference(path, engineering=False):
    """Run only the one declared native cvExt reference; no unsupported table substitution."""
    p = read_plan(path, engineering); u = p['reference']; out = Path(p['work'])/'reference'
    if out.is_dir() and not any(out.iterdir()): out.rmdir()
    out.mkdir(parents=True, exist_ok=False)
    from e027_reference import validate_means, export
    write(out/'input-proof.json', validate_means(u['matrix'], u['matrix_receipt'], u['fasta']))
    native = out/'native'; native.mkdir()
    argv = [u['binary'], '-i', u['fasta'], '-a', u['matrix'], '--cvExt', '-o', str(native/'bin'),
            '-t', '4', '--seed', '11', '-v']
    with (out/'native.log').open('x') as log:
        value = subprocess.run(argv, stdout=log, stderr=subprocess.STDOUT)
    write(out/'native-exit.json', dict(argv=argv, exit_code=value.returncode, means_only_native_assumption=True))
    if value.returncode: raise RuntimeError('Native Oral reference failed; preserve journal')
    export(u['fasta'], native, out/'export')
    return seal(out)


def resume(path, engineering=False):
    """Require every completed stage's exact member seal; refuse partial fits."""
    p = read_plan(path, engineering)
    for name in UNITS:
        root = Path(p['work'])/'units'/name
        for step in STAGES:
            out = root/step
            if (out/'done.json').is_file(): verify_seal(out)
            elif out.is_dir() and any(out.iterdir()): raise ValueError('Incomplete stage preserved; assessed operational repair required: '+str(out))
        if (root/'admit/done.json').is_file() and verify_seal(root/'admit')['inputs'] != input_bindings(p['units'][name]):
            raise ValueError('Completed admission input drift')
    if (Path(p['work'])/'reference/done.json').is_file(): verify_seal(Path(p['work'])/'reference')
    return p


def workflow(path, engineering=False, dry=False):
    """Run real Snakemake with independent arms, serial resource cap and keep-going.

    A technical blocker in one arm does not cancel another ready independent arm.
    All rules request four threads/26 GB under aggregate four threads/26 GB, so no
    community processes overlap. No --jobs is combined with --cores.
    """
    p = resume(path, engineering); Path(p['work']).mkdir(parents=True, exist_ok=True)
    argv = [p['workflow_python'], '-I', '-B', '-m', 'snakemake', '--snakefile', p['snakefile'],
        '--directory', p['work'], '--cores', '4', '--resources', 'mem_mb=26000', '--keep-going',
        '--runtime-source-cache-path', str(Path(p['work']).parent/'workflow-source-cache'),
        '--benchmark-extended', '--rerun-triggers', 'mtime', '--config',
        'plan='+str(Path(path).absolute()), 'engineering='+str(engineering).lower()]
    if dry: argv.append('--dry-run')
    return subprocess.run(argv, check=True).returncode


if __name__ == '__main__':
    a = argparse.ArgumentParser(description=__doc__); a.add_argument('--plan', type=Path, required=True)
    a.add_argument('--unit', choices=UNITS); a.add_argument('--stage', choices=STAGES)
    for key in ['workflow', 'dry-run', 'engineering', 'verify-inputs', 'reference']:
        a.add_argument('--'+key, action='store_true')
    v = a.parse_args()
    if v.verify_inputs: verify_after(read_plan(v.plan, v.engineering), v.engineering)
    elif v.reference: reference(v.plan, v.engineering)
    elif v.workflow: workflow(v.plan, v.engineering, v.dry_run)
    elif v.unit and v.stage: stage(v.plan, v.unit, v.stage, v.engineering)
    else: a.error('Select one explicit action')
