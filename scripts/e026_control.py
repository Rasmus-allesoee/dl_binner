#!/usr/bin/env python3
"""Serial restore-only E026 workers; no training/acquisition/cloud operation.

The actual dispatcher admits only a frozen two-unit plan, byte-verified reuse,
fresh source and external held-parent release. Partial scientific output is
preserved/refused; completed stages resume only through their exact seals.
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
from e026_information import inputs, source_bindings, run, audit
from dl_binner.calibrated.fusion import policy

EXPERIMENT = ROOT/'experiments/E026-calibrated-evidence-fusion'
UNITS = ['E009-E022', 'oral-E019']


def freeze():
    """Verify every old scientific lock and the new research overlay independently."""
    from e025_gates import freeze as previous
    inherited = previous()
    lock = json.loads((EXPERIMENT/'source-lock.json').read_text())
    for name, wanted in lock['files'].items():
        if binding(ROOT/name) != wanted:
            raise ValueError('Frozen E026 source differs: '+name)
    return dict(status='PASS', inherited=inherited, new=binding(EXPERIMENT/'source-lock.json'))


def read_plan(path, engineering=False):
    """Reject extra science/paths; local engineering must be explicitly declared."""
    p = json.loads(Path(path).read_text())
    fields = {'kind', 'work', 'units', 'python', 'workflow_python', 'worker', 'snakefile',
              'policy', 'limits', 'engineering', 'reuse_lock'}
    unit_fields = {'features', 'embeddings', 'graph', 'marker_evidence', 'fasta', 'receipt'}
    if (set(p) != fields or p['kind'] != 'E026 calibrated fixed-learning biological grouping'
            or p['engineering'] is not engineering or list(p['units']) != UNITS
            or any(set(u) != unit_fields for u in p['units'].values())):
        raise ValueError('Unexpected cached-only E026 plan/schema')
    policy(p['policy'])
    if not engineering:
        expected = json.loads((EXPERIMENT/'runtime-plan.json').read_text())
        # Standing cost/time flexibility uses recorded consistent source/ledger
        # revisions; it is not permission for an unbound plan to drift silently.
        if any(p[k] != expected[k] for k in fields-{'work'}):
            raise ValueError('Frozen E026 source/input/runtime differs')
        if not Path(p['work']).is_relative_to('/srv/dl_binner/experiments/e026'):
            raise ValueError('Fresh E026 work directory required')
        release = os.environ.get('E026_RELEASE_FILE')
        if not release or json.loads(Path(release).read_text()).get('plan') != binding(path):
            raise ValueError('External supervised release required; preparation cannot run community work')
        freeze()
    return p


def verify_inputs(p, engineering=False):
    """Restore in place, with no missing/corrupt-byte reinstall or recopy fallback."""
    if not engineering:
        lock = json.loads(Path(p['reuse_lock']).read_text())
        for name, wanted in lock['files'].items():
            if binding(name) != wanted:
                raise ValueError('Missing/corrupt retained member; no fallback: '+name)
        # Read every retained archive member once; do not silently trust a locator.
        from e024_reuse_gates import archive_inventory
        for a in lock['archives']:
            if binding(a['path']) != {k: a[k] for k in ['bytes', 'sha256']}:
                raise ValueError('Retained archive bytes differ')
            archive_inventory(a['path'])
        # The faster E025 validator is source/reuse-bound and its actual tiny
        # equivalence contract is a gate. Old hierarchy/choices are not inputs
        # to this new core search, so do not replay their accepted decisions.
    result = {}
    for name, unit in p['units'].items():
        data, _, valid, meta, _, _ = inputs(unit)
        if not engineering:
            expected = json.loads((EXPERIMENT/'protocol.json').read_text())['axes'][name]
            actual = dict(rows=len(data['ids']), bp=int(data['lengths'].sum()),
                          eligible=int(valid.sum()), samples=meta['samples'],
                          core_rows=int((valid & (data['lengths'] >= 2500)).sum()))
            if actual != expected:
                raise ValueError('Complete retained contig/sample axes differ: '+name)
        result[name] = dict(inputs=source_bindings(unit), rows=len(data['ids']),
            bp=int(data['lengths'].sum()), samples=meta['samples'], eligible=int(valid.sum()))
    return dict(status='PASS', units=result, no_copy_install_or_science_fallback=True,
                prior_selection_replayed=False, old_native_index_rebuilt=False)


def stage(path, unit, name, engineering=False):
    """Run one new rule, retaining complete partitions and before/after input bytes."""
    p = read_plan(path, engineering); cfg = policy(p['policy'])
    if unit not in UNITS or name not in ['verify', 'group', 'export', 'audit']:
        raise ValueError('Unknown cached unit/stage')
    if not os.environ.get('NUMBA_CACHE_DIR'):
        raise ValueError('Fresh owned JIT cache required')
    u = p['units'][unit]; work = Path(p['work'])/'units'/unit
    work.mkdir(parents=True, exist_ok=True)
    if name == 'verify':
        out = fresh(work, 'verified')
        data, _, valid, meta, _, _ = inputs(u)
        return seal(out, dict(inputs=source_bindings(u), rows=len(valid), samples=meta['samples']))
    if name == 'group':
        if source_bindings(u) != verify_seal(work/'verified')['inputs']:
            raise ValueError('Retained bytes changed before new grouping; no fallback')
        out = work/'group'
        if out.is_dir() and not any(out.iterdir()): out.rmdir()
        return run(u, out, cfg)
    if name == 'export':
        from dl_binner.information.export import export
        out = fresh(work, 'export'); account = {}
        for arm in ['core', 'recruited']:
            account[arm] = export(u['features'], work/'group'/(arm+'-partition.json'),
                                  u['fasta'], out/arm, include_dna=arm == 'recruited')
        write(out/'accounting.json', account)
        return seal(out)
    out = fresh(work, 'audited'); proof = audit(u, work/'group', cfg)
    if source_bindings(u) != verify_seal(work/'verified')['inputs']:
        raise ValueError('Accepted input bytes changed after grouping')
    return seal(out, dict(proof=proof, inputs_unchanged=True))


def resume_gate(path, engineering=False):
    """Verify completed stage bytes; preserve and refuse incomplete science."""
    p = read_plan(path, engineering)
    for unit, u in p['units'].items():
        work = Path(p['work'])/'units'/unit
        for name in ['verified', 'export', 'audited']:
            folder = work/name
            if (folder/'done.json').is_file(): verify_seal(folder)
            elif folder.is_dir() and any(folder.iterdir()):
                raise ValueError('Partial stage preserved; fresh assessed attempt required: '+str(folder))
        if (work/'group/completed.json').is_file(): audit(u, work/'group', policy(p['policy']))
        elif (work/'group').is_dir() and any((work/'group').iterdir()):
            raise ValueError('Partial grouping preserved; no automatic scientific replay')
        if (work/'verified/done.json').is_file() and verify_seal(work/'verified')['inputs'] != source_bindings(u):
            raise ValueError('Reuse inputs drifted')
    return p


def workflow(path, engineering=False, dry=False):
    """Dispatch the serial local Snakemake DAG; no --jobs/core-cap conflict."""
    p = resume_gate(path, engineering); Path(p['work']).mkdir(parents=True, exist_ok=True)
    argv = [p['workflow_python'], '-I', '-B', '-m', 'snakemake', '--snakefile', p['snakefile'],
        '--directory', p['work'], '--cores', '4', '--resources', 'mem_mb=26000',
        '--runtime-source-cache-path', str(Path(p['work']).parent/'workflow-source-cache'),
        '--benchmark-extended', '--rerun-triggers', 'mtime', '--config',
        'plan='+str(Path(path).absolute()), 'engineering='+str(engineering).lower()]
    if dry: argv.append('--dry-run')
    return subprocess.run(argv, check=True).returncode


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__); p.add_argument('--plan', type=Path, required=True)
    p.add_argument('--unit', choices=UNITS); p.add_argument('--stage', choices=['verify', 'group', 'export', 'audit'])
    p.add_argument('--workflow', action='store_true'); p.add_argument('--engineering', action='store_true')
    p.add_argument('--dry-run', action='store_true'); p.add_argument('--verify-inputs', action='store_true')
    p.add_argument('--output', type=Path); a = p.parse_args()
    if a.workflow: workflow(a.plan, a.engineering, a.dry_run)
    elif a.verify_inputs: write(a.output, verify_inputs(read_plan(a.plan, a.engineering), a.engineering))
    elif a.unit and a.stage: stage(a.plan, a.unit, a.stage, a.engineering)
    else: p.error('Choose verification, one complete stage, or workflow')
