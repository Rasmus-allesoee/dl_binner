#!/usr/bin/env python3
"""Actual serial two-unit DAG, verified partial/full resume and compact return.

Only synthetic fixtures are generated. The production isolated dispatcher,
Snakemake barriers, cached reload, full FASTA export, collector and review
entrypoints run. No community grouping/score, cloud transport or native detector.
"""
import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).absolute().parents[1]
sys.path[:0] = [str(ROOT/'scripts'), str(ROOT/'src'), str(ROOT/'tests')]
from e024_coverage import binding, write
from e026_collect import pack, collect_controls, CONTROLS
from test_e026_fusion import fixture
from test_e025_retrieval import retained
from e026_stage_review import stage as stage_review, stream_stage


def tiny(root, workflow_python):
    """Run the exact isolated production argv with no replay of completed rules."""
    root = Path(root).absolute(); root.mkdir(parents=True, exist_ok=False)
    inp = root/'inputs'; inp.mkdir(); unit = fixture(inp)
    oral = root/'rebound-inputs'; oral.mkdir(); u, receipt = retained(oral)
    oral_unit = dict(features=str(receipt.parent/'features.npz'), embeddings=str(u['embeddings']),
        graph=str(u['graph']), marker_evidence=str(u['marker_evidence']), fasta=str(u['reference']), receipt=str(receipt))
    plan = json.loads((ROOT/'experiments/E026-calibrated-evidence-fusion/runtime-plan.json').read_text())
    plan.update(work=str(root/'work'), python=sys.executable, workflow_python=str(Path(workflow_python).absolute()),
        worker=str(ROOT/'scripts/e026_control.py'), snakefile=str(ROOT/'experiments/E026-calibrated-evidence-fusion/Snakefile'),
        policy=str(ROOT/'experiments/E026-calibrated-evidence-fusion/policy.json'),
        units={'E009-E022': unit, 'oral-E019': oral_unit}, engineering=True)
    write(root/'plan.json', plan)
    argv = [sys.executable, '-I', '-B', str(ROOT/'scripts/e026_control.py'), '--plan', str(root/'plan.json'), '--engineering']
    env = dict(os.environ, NUMBA_NUM_THREADS='4', NUMBA_CACHE_DIR=str(root/'jit'))
    def call(label, arguments):
        with (root/(label+'.log')).open('x') as f:
            value = subprocess.run(argv+arguments, cwd=root, env=env, stdout=f, stderr=subprocess.STDOUT)
        write(root/(label+'.exit.json'), dict(exit_code=value.returncode, argv=argv+arguments))
        if value.returncode: raise RuntimeError('Actual tiny DAG failure: '+str(root/(label+'.log')))
    call('first-verify', ['--unit', 'E009-E022', '--stage', 'verify'])
    call('first-group', ['--unit', 'E009-E022', '--stage', 'group'])
    work = root/'work'; before = {str(p.relative_to(work)): binding(p)
        for name in ['verified', 'group'] for p in (work/'units/E009-E022'/name).rglob('*') if p.is_file()}
    call('partial-resume', ['--workflow'])
    text = (root/'partial-resume.log').read_text()
    if any(binding(work/k) != v for k, v in before.items()): raise ValueError('Accepted new stage was changed')
    # Six rules remain, with all E009 rules before any Oral rule.
    events = []; active = None
    for line in text.splitlines():
        if line.startswith('localrule '): active = line.split()[1].rstrip(':')
        if active and 'wildcards: unit=' in line:
            events.append(dict(rule=active, unit=line.split('wildcards: unit=')[1].strip()))
            active = None
    expected = [dict(rule=s, unit=u) for u, stages in [('E009-E022', ['export', 'audit']),
                ('oral-E019', ['verify', 'group', 'export', 'audit'])] for s in stages]
    if events != expected: raise ValueError('Actual scheduler ordering/reuse differs: '+repr(events))
    call('completed-resume', ['--workflow'])
    if 'Nothing to be done' not in (root/'completed-resume.log').read_text():
        raise ValueError('Completed DAG was not a verified no-op')
    phase = root/'phase'; phase.mkdir(); evidence = root/'evidence'; evidence.mkdir()
    for name in CONTROLS+['config.json', 'science-plan.json', 'started.json', 'release.json',
                         'science-result.json', 'science-disk.jsonl', 'external-data.json']:
        path = phase/name; path.parent.mkdir(parents=True, exist_ok=True)
        write(path, {'fixture': True} if name != 'external-data.json' else dict(data_copied=False, fixture=True))
    collect_controls(phase, evidence/'controls')
    write(evidence/'external-data.json', dict(data_copied=False, units=plan['units'], fixture=True))
    returned = pack(work, evidence, root/'return')
    admit = root/'admission.json'
    write(admit, dict(provider_status='TERMINATED', archive_and_every_member_verified=True,
                      cost_and_retention_admitted=True, workflow_completed=True, fixture=True))
    # Native absolute paths deliberately become unavailable. Preserve the exact
    # receipt/cache bytes and admit explicit external review copies instead.
    mapped = {}
    for name, u in plan['units'].items():
        mapped[name] = {}; directory = root/'review-inputs'/name; directory.mkdir(parents=True)
        for key in ['features', 'graph', 'marker_evidence']+(['receipt'] if u['receipt'] else []):
            source = Path(u[key]); target = directory/(key+source.suffix)
            shutil.copyfile(source, target); mapped[name][key] = str(target)
            if key in ['features', 'graph']: shutil.copyfile(source.with_suffix('.json'), target.with_suffix('.json'))
        write(root/(name+'-review-paths.json'), mapped[name])
    inp.rename(root/'preserved-original-inputs'); oral.rename(root/'preserved-original-rebound-inputs')
    for name in plan['units']:
        write(root/(name+'-unit.json'), plan['units'][name])
        staged = root/('staged-'+name)
        try:
            stage_review(root/'return/e026-evidence.tar.gz', returned['archive'], name,
                         root/('refused-stage-'+name), admit, cap=1)
        except ValueError as error:
            if 'review footprint/free reserve does not fit' not in str(error): raise
        else:
            raise ValueError('Oversized local stage was not refused')
        stage_review(root/'return/e026-evidence.tar.gz', returned['archive'], name, staged, admit)
        streamed = root/('streamed-'+name)
        # Exercise the actual isolated stdin producer/consumer layout. Only a
        # local tiny fixture is read; no gcloud transport or internet is used.
        streaming_command = [sys.executable, '-I', '-B', str(ROOT/'scripts/e026_stage_review.py'),
            '--stdin', '--bytes', str(returned['archive']['bytes']), '--sha256', returned['archive']['sha256'],
            '--unit', name, '--output', str(streamed), '--admission', str(admit)]
        with (root/'return/e026-evidence.tar.gz').open('rb') as source:
            value = subprocess.run(streaming_command, stdin=source, capture_output=True, text=True, cwd=root, env=env)
        (root/(name+'-streamed-stage.log')).write_text(value.stdout+value.stderr); value.check_returncode()
        proof = json.loads((streamed/'staging.json').read_text())
        if proof['archive']['regular_members'] != returned['regular_members'] or proof['compressed_archive_kept_locally']:
            raise ValueError('Streaming verification differs from frozen whole-archive verifier')
        # A corrupt expected digest cannot publish ready after partial staging.
        bad = dict(returned['archive'], sha256='0'*64); failed = root/('bad-stream-'+name)
        with (root/'return/e026-evidence.tar.gz').open('rb') as source:
            try: stream_stage(source, bad, name, failed, admit)
            except ValueError as error:
                if 'Streaming archive checksum/bytes differ' not in str(error): raise
            else: raise ValueError('Corrupt streaming bytes were admitted')
        if (failed/'staging.json').exists(): raise ValueError('Corrupt stream exposed a ready name')
        staged = streamed
        command = [sys.executable, '-I', '-B', str(ROOT/'scripts/e026_review.py'), '--contracts-only',
            '--unit', str(root/(name+'-unit.json')), '--unit-root', str(staged/'work/units'/name),
            '--inventory', str(staged/'inventory.json'), '--admission', str(admit),
            '--review-paths', str(root/(name+'-review-paths.json')),
            '--output', str(root/(name+'-review-contract.json'))]
        result = subprocess.run(command, cwd=root, env=env, capture_output=True, text=True)
        (root/(name+'-review-contract.log')).write_text(result.stdout+result.stderr)
        result.check_returncode()
    write(root/'completed.json', dict(status='PASS', actual_two_unit_serial_DAG=True, scheduler_events=events,
        actual_partial_reuse=True, actual_completed_noop=True, actual_full_DNA_exports=True,
        actual_review_isolated_argv=True, actual_native_absolute_paths_unavailable=True,
        actual_selective_staging_member_aliases=True, actual_oversized_local_stage_refused=True, actual_collection=returned,
        actual_isolated_streaming_stage=True, actual_streaming_bad_checksum_no_ready=True,
        community_science_or_truth=False, synthetic='DNA/vectors/marker evidence; VM/billing/transport absent'))


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__); p.add_argument('--root', type=Path, required=True)
    p.add_argument('--workflow-python', required=True); a = p.parse_args(); tiny(a.root, a.workflow_python)
