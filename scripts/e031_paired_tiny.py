#!/usr/bin/env python3
"""Exercise actual paired readers, serial DAG, export and unchanged resume on tiny DNA.

Reuses the native/local tiny gate's generated input banks and bootstrap fixtures.
The three engineering fits are small numerical contracts, never community fits.
Both constructors consume the same fresh engineering outputs. No detector, real
GLM inference, truth, cloud action or accepted community output is reachable.
"""
import argparse
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).absolute().parents[1]
sys.path.insert(0, str(ROOT/'scripts'))
from e024_coverage import binding, write


def run(source, workflow_python):
    """Run the full real paired DAG, then require an exact no-work verified resume."""
    from e031_control import product_scope, UNITS
    from e031_review import contract
    from e031_collect import collect_controls, CONTROLS
    from e031_paired_collect import pack, verify
    product_scope()
    source = Path(source).absolute(); root = source/'paired-contract'
    root.mkdir(exist_ok=False)
    old = json.loads((source/'plan.json').read_text())
    plan = json.loads((ROOT/'experiments/E031-bootstrap-preserving-learning/paired-plan.json').read_text())
    plan.update(work=str(root/'work'), units=old['units'], python=sys.executable,
                workflow_python=str(Path(workflow_python).absolute()), worker=str(ROOT/'scripts/e031_paired.py'),
                snakefile=str(ROOT/'experiments/E031-bootstrap-preserving-learning/paired.smk'), engineering=True)
    write(root/'plan.json', plan)
    argv = [sys.executable, '-I', '-B', str(ROOT/'scripts/e031_paired.py'),
            '--plan', str(root/'plan.json'), '--engineering', '--workflow']
    def call(label):
        with (root/(label+'.log')).open('x') as log:
            result = subprocess.run(argv, stdout=log, stderr=subprocess.STDOUT)
        write(root/(label+'.exit.json'), dict(argv=argv, exit_code=result.returncode))
        if result.returncode:
            raise RuntimeError('Actual paired tiny DAG failed: '+str(root/(label+'.log')))
    call('first')
    active, events = None, []
    for line in (root/'first.log').read_text().splitlines():
        if line.startswith('localrule ') and not line.startswith('localrule all:'):
            if active is not None:
                raise ValueError('Independent paired stages overlapped')
            active = line.split()[1].rstrip(':'); events.append(active)
        if 'Finished jobid:' in line:
            active = None
    if len(events) != 34 or events[0] != 'barrier':
        raise ValueError('Complete 34-stage paired DAG not exercised')
    before = {str(p): binding(p) for p in (root/'work').rglob('*')
              if p.is_file() and '.snakemake' not in p.parts}
    call('verified-resume')
    if 'Nothing to be done' not in (root/'verified-resume.log').read_text() or any(binding(p) != b for p, b in before.items()):
        raise ValueError('Paired resume repeated or changed accepted engineering science')
    phase = root/'phase'; phase.mkdir(); evidence = root/'evidence'; evidence.mkdir()
    for name in CONTROLS+['config.json','science-plan.json','started.json','release.json',
                          'science-result.json','science-disk.jsonl','external-data.json']:
        path = phase/name; path.parent.mkdir(parents=True, exist_ok=True)
        write(path, dict(data_copied=False, fixture=True) if name == 'external-data.json' else dict(fixture=True))
    collect_controls(phase, evidence/'controls'); write(evidence/'external-data.json', dict(data_copied=False))
    packed = pack(root/'work', evidence, root/'return')
    verify(root/'return/e031-evidence.tar.gz', packed['archive'])
    base = root/'review'; base.mkdir()
    import shutil
    shutil.copyfile(root/'return/inventory.json', base/'inventory.json')
    write(base/'admission.json', dict(provider_status='TERMINATED', archive_and_every_member_verified=True,
        cost_and_retention_admitted=True, workflow_completed=True, exact_source_schedule_axes_verified=True,
        fixture_only=True, live_provider_or_billing_observed=False))
    readers = {}
    for unit in UNITS:
        for comparison in ['learning', 'learning-E023']:
            readers[unit+'/'+comparison] = contract(base, root, unit, 'student', plan['units'][unit]['features'],
                                                   comparison, engineering=True)[-1]
    write(root/'completed.json', dict(status='PASS', actual_ready_events=events, no_overlap=True,
        verified_resume_noop=True, actual_fits=3, same_output_both_constructors=True,
        archive=packed, reader_contracts=readers, truth_scored=False,
        actual=['real generated DNA/retained input-bank readers', 'full paired serial DAG',
                'strict native reload', 'both sparse constructors and audits', 'six reader/export contracts',
                'complete exact-byte member/alias collector'],
        synthetic=['tiny marker calls', 'GLM fixture vectors; no DNABERT inference'],
        community_or_cloud_admission=False))


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__); p.add_argument('--root', type=Path, required=True)
    p.add_argument('--workflow-python', type=Path, required=True); a = p.parse_args()
    run(a.root, a.workflow_python)
