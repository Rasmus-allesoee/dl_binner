#!/usr/bin/env python3
"""Inspect retained E006 software evidence and dependency bytes, never rerun science."""
import hashlib
import json
from pathlib import Path
import zipfile

ROOT=Path(__file__).resolve().parents[2]
ART=ROOT/'artifacts/e006-cli-usability'


def record(path):
    """Bind one retained regular file incrementally, with a repository-relative locator."""
    h=hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda:stream.read(1024*1024),b''):h.update(chunk)
    return dict(path=str(path.relative_to(ROOT)),bytes=path.stat().st_size,sha256=h.hexdigest())


def main():
    """Publish compact acceptance/cost records after all intended native checks pass."""
    final=ART/'integration-005';observed=json.loads((final/'observed.json').read_text())
    assert observed['status']=='passed' and len(observed['cases'])==14
    wheel=ART/'setup/dist-v7/dl_binner-0.1.0.dev1-py3-none-any.whl'
    with zipfile.ZipFile(wheel) as archive:
        for p in (ROOT/'src/dl_binner').rglob('*'):
            if p.is_file() and p.suffix in ('.py','.json','.smk'):
                assert archive.read('dl_binner/'+str(p.relative_to(ROOT/'src/dl_binner')))==p.read_bytes()
    reuse=json.loads((ART/'setup/dependency-reuse-v6.json').read_text())
    for name,entry in reuse['entries'].items():
        if name=='.DS_Store':continue  # Finder metadata is not a dependency/input.
        path=Path(entry['target']);h=hashlib.sha256();total=count=0
        link=ART/'env-local-v7/lib/python3.10/site-packages'/name
        assert link.is_symlink() and link.resolve()==path.resolve()
        for p in sorted(path.rglob('*')) if path.is_dir() else [path]:
            if not p.is_file() or '__pycache__' in p.parts or p.suffix=='.pyc':continue
            file=record(p)
            h.update((str(p.relative_to(path)) if path.is_dir() else path.name).encode()+b'\0'+file['sha256'].encode()+b'\n')
            total+=file['bytes'];count+=1
        assert h.hexdigest()==entry['tree_sha256'] and total==entry['bytes'] and count==entry['files']
    runtime=json.loads((ART/'setup/runtime-v7.json').read_text())
    assert runtime['torch_threads']==4 and runtime['torch_interop']==1 and runtime['cuda'] is None
    run=final/'tiny depth run';summary=json.loads((run/'run-summary.json').read_text())
    checkpoint=json.loads((run/'training/checkpoint.json').read_text())
    assert summary['checkpoint_reload_exact'] and checkpoint['loader_workers']==0
    assert checkpoint['config']==json.loads((ROOT/'experiments/E004-first-binner/training.json').read_text())
    assert len(checkpoint['epochs'])==20 and all(e['contigs_seen']==2 for e in checkpoint['epochs'])
    assert all(pool['num_threads']<=4 for pool in checkpoint['library_pools'])
    cases={name:dict(exit_code=value['exit_code'],wall_seconds=value['wall_seconds'],log=value['log_bytes'])
           for name,value in observed['cases'].items()}
    resources={name:dict(record(ART/name/'integration.exit.json'),
        **json.loads((ART/name/'integration.exit.json').read_text())) for name in
        ('integration-002','integration-003','integration-004','integration-005')}
    seconds=sum(value['wall_seconds'] for value in resources.values())
    e005=json.loads((ART/'integration-002/e005-accounting.json').read_text())
    own=lambda folder:sum(p.stat().st_size for p in folder.rglob('*') if p.is_file() and not p.is_symlink())
    receipt=dict(status='accepted',date='2026-10-06',role='Software contracts only, no new bin-quality result',
        initial_contract_commit='e93132b',accepted_source_commit=observed['source_commit'],
        final_wheel=record(wheel),native_observation=record(final/'observed.json'),
        protocol=record(ROOT/'experiments/E006-cli-usability/protocol.json'),
        review_source=record(Path(__file__)),
        runtime=record(ART/'setup/runtime-v7.json'),dependency_reuse=record(ART/'setup/dependency-reuse-v6.json'),
        dependency_origins=runtime['origins'],read_only_dependency_trees_unchanged=True,
        dependency_binding_exclusions=['.DS_Store: volatile Finder metadata; no numerical/source/input bytes excluded'],
        package_prefix=str((ART/'env-local-v7').relative_to(ROOT)),workflow_prefix='artifacts/e005-linux-pilot/env-workflow-local',
        fixture=dict(baseline_contigs=13,baseline_bp=42311,final_contigs=4,final_bp=2048),
        tested_contracts=cases,reused_passed_contracts=observed['reused_passed_cases'],
        retained_scientific_modules_unchanged=['io.py','model.py','clustering.py'],
        final_masks_and_counts={name:value for name,value in summary['arms'].items()},
        retained_e005_summary=dict(record=record(ART/'integration-002/e005-accounting.json'),arms={
            name:dict(bins=value['accounting']['bin_count'],statuses=value['accounting']['statuses'],
                      all_zero_depth_contigs=value['accounting']['masks']['all_zero_depth_contigs']) for name,value in e005.items()}),
        driver_resources=resources,known_supervised_seconds=seconds,known_thread_wall_hours=4*seconds/3600,
        cost_scope='Known supervised local QA drivers, failures included. Initial unsupervised ps prerequisite failure, setup/build, review, debugging/idle time excluded; not provider charges or complete task cost.',
        retained_storage=dict(attempts_regular_bytes=sum(own(ART/name) for name in ('integration-001','integration-002','integration-003','integration-004','integration-005')),
            final_prefix_owned_regular_bytes=own(ART/'env-local-v7'),
            prior_environment_logical_bytes={p.name:own(p) for p in sorted(ART.glob('env-local-v*')) if p.name!='env-local-v7'},
            scope='Logical regular-file bytes; symlinked dependency payload belongs to retained v4. Existing wheel caches/other experiments and filesystem billing are separate.'),
        failed_attempts=dict(initial_ps_prerequisite='integration-001: no scientific stage, originally no exit receipt; repaired regression passes',
            scheduler_trailer='integration-002: successful scientific fixtures reused, native input error stopped correctly but hidden from console',
            unreaped_probe='integration-003/004: strict timeout check failed; final reaping/status checks pass',
            local_disk='v5 setup/build hit ENOSPC; preserve failed prefix/logs. v6/v7 reuse explicit verified numerical dependencies read-only instead of another copy.'),
        limitations=['Native Mac, not final generic Linux execution','No biological utility/whole-MAG/generalization assessment',
            'Sampled CPU/RSS are approximate; shared pages may be counted twice','No compatibility commitment for prototype journals/CLI'],
        next_step='Prepare one tiny checksum-bound owner-controlled CPU/Linux generic-command smoke; do not run it or repeat E005 science')
    target=ROOT/'experiments/E006-cli-usability/observed.json'
    with target.open('x') as stream:json.dump(receipt,stream,sort_keys=True,indent=2);stream.write('\n')
    print(json.dumps(dict(status='accepted',known_seconds=seconds,thread_wall_hours=4*seconds/3600,wheel=record(wheel),receipt=str(target))))


if __name__=='__main__':main()
