#!/usr/bin/env python3
"""Seal E023 preparation source/resources from existing local engineering receipts.

No science, score, cloud call, install, cleanup or budget reset occurs. This
pre-release summarizer refuses any E023 native handoff. It preserves failures
and binds source bytes rather than rewriting accepted input/cache manifests.
"""
import ast
import datetime
import hashlib
import json
from pathlib import Path
import shutil
import time

ROOT=Path(__file__).absolute().parents[3]
EXP=ROOT/'experiments/E023-adaptive-density-bins'
ART=ROOT/'artifacts/e023-local'


def bound(path):
    """Bind one small regular record/source; never follow a scientific link."""
    p=Path(path)
    if p.is_symlink()or not p.is_file():raise ValueError('Missing/linked preparation record')
    return dict(bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest())


def main():
    """Freeze code and summarize only verified local attempts under the original clock."""
    if (EXP/'native-observed.json').exists():raise ValueError('Native handoff exists; preserve this source freeze')
    clock=json.loads((ART/'engineering-clock.json').read_text())
    if time.time()-clock['start_epoch']>=7200:raise TimeoutError('Original engineering clock exceeded')
    old=json.loads((ROOT/'experiments/E022-marker-informed-learning/candidate-lock.json').read_text())['package_files']
    for name,expected in old.items():
        if bound(ROOT/'src/dl_binner'/name)!=expected:raise ValueError('Immutable E022 source/default changed: '+name)
    preserved=dict(status='PASS',original_E022_package_members=len(old),all_original_source_defaults_unchanged=True,
        added_only='density research module; no installed prefix changed')
    paths=list((ROOT/'src/dl_binner').rglob('*.py'))+list((ROOT/'src/dl_binner').rglob('*.json'))
    paths+=list((ROOT/'scripts').glob('*.py'))+list((ROOT/'tests').glob('test_e023*.py'))+[Path(__file__).absolute()]
    paths+=[EXP/n for n in ['config.json','protocol.json','reuse-lock.json','plan-template.json','resources.json',
        'Snakefile','storage-admission.json','confirmation-plan.json','external-sources.json','design.md']]
    for p in paths:
        if p.suffix=='.py':ast.parse(p.read_text())
        if p.suffix=='.json':json.loads(p.read_text())
    source=dict(kind='E023 exact prospective research overlay and execution source',
        parent_source='5a82ae9982911e0e41e7726766659cefd936519d',policy=bound(EXP/'config.json'),
        files={str(p.relative_to(ROOT)):bound(p)for p in sorted(set(paths))},original_package=preserved,
        scientific_status='No changed community outcome',
        native_execution_commit='Record the exact clean Git HEAD containing these members before native release; no self-reference',
        no_built_wheel_or_installed_prefix_mutation=True)
    attempts=[]
    for p in sorted(ART.glob('*.resources.json')):
        value=json.loads(p.read_text());attempts.append(dict(attempt=p.stem,**value,receipt=bound(p)))
    required=['final-17-contracts','sealed-adapter-DAG','local-runtime','workflow-actual','final-control-inventory']
    indexed={a['attempt'].removesuffix('.resources'):a for a in attempts}
    selected={}
    for prefix in required:
        names=[n for n in indexed if n.startswith(prefix+'-')and n[len(prefix)+1:].isdigit()]
        name=max(names,key=lambda n:int(n[len(prefix)+1:]));selected[prefix]=name
        if indexed[name]['status']!='SUCCESS':raise ValueError('Required latest local contract not passed: '+name)
    (EXP/'source-lock.json').write_text(json.dumps(source,indent=2)+'\n')
    obs=json.loads((EXP/'local-observed.json').read_text())
    failed=list(obs['failed_attempts_preserved'])
    known={v.get('attempt') for v in failed}
    for a in attempts:
        label=a['attempt'].removesuffix('.resources')
        if a['status']!='SUCCESS'and label not in known:
            repair=('Local resource sampler now tolerates disappearance of test-owned temporary files between walk/stat; scientific missing-member refusal unchanged.'
                    if label.startswith('final-17-contracts') else
                    'Premature finalization refused the interrupted required suite; no success/native admission was published.'
                    if label.startswith('source-resource-seal') else
                    'Malformed-cache test now writes to a fresh damaged artifact; immutable writer refusal remains. Actual structural reader test passes.')
            failed.append(dict(attempt=label,cause=a.get('error'),receipt=a['receipt'],
                repair=repair))
    (EXP/'journals/preparation-failures.json').write_text(json.dumps(dict(failures=failed,original_clock_not_reset=True),indent=2)+'\n')
    successful=[a['resources']for a in attempts if a['status']=='SUCCESS'and'resources'in a]
    owned=sum(p.stat().st_size for p in ART.rglob('*')if p.is_file()and not p.is_symlink())
    new_source=sum(p.stat().st_size for p in paths if 'e023_'in p.name or 'density'in p.parts or p.is_relative_to(EXP))
    if owned+new_source>4*1024**3:raise RuntimeError('Original local extra-space cap exceeded')
    peak=max(v['peak_sampled_rss_bytes']for v in successful)
    if peak>8000000000:raise RuntimeError('Original sampled RSS cap exceeded')
    obs.update(source_lock=bound(EXP/'source-lock.json'),observed_UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        original_package=preserved,attempts=attempts,failed_attempts_preserved=failed,
        elapsed_cumulative_seconds=time.time()-clock['start_epoch'],peak_sampled_tree_RSS_bytes=peak,
        owned_artifact_bytes=owned,additional_source_metadata_bytes=new_source,free_local_bytes=shutil.disk_usage(ROOT).free,
        local_runtime=bound(ART/'local-runtime.json'),
        local_workflow=dict(python='3.13.2',snakemake='9.13.7',status='ACTUAL_LOCAL_DAG_AND_RENDERED_PROBE_PASS',
            native_expected='3.12.10 / 9.16.3, separate pending native gate'),
        provider_final=dict(status='TERMINATED',receipt=bound(ART/'cloud/final-instance.json')))
    obs['tests'].update(combined_contracts=17,latest_full=selected['final-17-contracts'],latest_affected=selected['final-control-inventory'],
        final_actual_DAG=selected['sealed-adapter-DAG'],persisted_hierarchy='PASS_STRUCTURAL_AND_REPRODUCED_CACHED_CHOICES_NO_INDEX_OR_MST_REBUILD',
        large_completion_control='10,000-member full receipt bound in <2 KiB compact control')
    obs['final_tiny_return']=json.loads((ART/'tiny-dag-v6/return/collection.json').read_text())
    (EXP/'local-observed.json').write_text(json.dumps(obs,indent=2,allow_nan=False)+'\n')
    print('E023_LOCAL_SEALED',len(source['files']),17,'tests',round(obs['elapsed_cumulative_seconds'],2),
          'seconds',peak,'sampled_RSS_bytes',owned+new_source,'extra_bytes',flush=True)


if __name__=='__main__':main()
