#!/usr/bin/env python3
"""Restore-only fixed-learning E023 grouping consumer and serial workflow entry.

No detector, encoder, baseline evaluator, install/copy fallback or cloud API is
reachable. New source is an explicitly frozen research overlay on the accepted
numerical prefix, not a mutation of that installed comparator or its wheel.
"""
import argparse
import json
import os
from pathlib import Path
import sys

ROOT = Path(__file__).absolute().parents[1]
sys.path[:0] = [str(ROOT/'src'), str(ROOT/'scripts')]
from e014_collect import binding, member_path

UNITS = ['E009-E022', 'oral-E019']
STAGES = ['verify', 'group', 'export', 'audit']


def verify_source(path=None,base=ROOT):
    """Verify frozen research source/default/helper bytes without modifying them."""
    path=Path(path)if path else ROOT/'experiments/E023-adaptive-density-bins/source-lock.json'
    record=json.loads(path.read_text())
    if record.get('kind')!='E023 exact prospective research overlay and execution source':
        raise ValueError('Wrong E023 source freeze')
    for name,expected in record['files'].items():
        if binding(member_path(Path(base),name))!=expected:
            raise ValueError('Frozen research source/default/helper bytes differ: '+name)
    return dict(status='PASS_FROZEN_RESEARCH_OVERLAY',lock=binding(path),members=len(record['files']))


def validate_plan(p, engineering=False):
    """Refuse expanded science/inputs and preserve the two named frozen anchors."""
    allowed={'kind','work','units','threads','python','worker','workflow_python','snakefile','config','reuse_lock'}
    fields={'features','embeddings','graph','marker_evidence','fasta','baseline_partition'}
    if (set(p)!=allowed or p['kind']!='E023 fixed-learning density hierarchy' or p['threads']!=4
            or list(p['units'])!=UNITS or any(set(u)!=fields for u in p['units'].values())):
        raise ValueError('Unfrozen E023 plan or unexpected truth/training path')
    from dl_binner.density.grouping import policy
    cfg=policy(p['config'])
    if not engineering:
        lock=json.loads(Path(p['reuse_lock']).read_text())
        if p['units']!=lock['units'] or p['python']!=lock['numerical_python']:
            raise ValueError('Native retained unit/runtime identities differ')
    return cfg


def verify_reuse(path, output=None):
    """Hash only admitted retained consumers; never recopy/reinstall on a mismatch."""
    value=json.loads(Path(path).read_text())
    if value.get('kind')!='E023 restore-only dual-anchor reuse': raise ValueError('Wrong retained-cache lock')
    total=0
    for name, expected in value['files'].items():
        p=member_path(Path('/'),name.removeprefix('/'))
        if binding(p)!=expected: raise ValueError('Missing/corrupt retained input; no fallback: '+name)
        total+=expected['bytes']
    result=dict(status='PASS',lock=binding(path),files=len(value['files']),bytes=total,read_only=True)
    if output:
        with Path(output).open('x')as f:json.dump(result,f,indent=2);f.write('\n')
    return result


def stage(plan, unit, name, engineering=False):
    """Verify once, construct one hierarchy, export both choices and audit reload."""
    p=json.loads(Path(plan).read_text());cfg=validate_plan(p,engineering)
    if unit not in UNITS or name not in STAGES:raise ValueError('Unknown E023 unit/stage')
    if not os.environ.get('NUMBA_CACHE_DIR'):raise ValueError('Fresh owned JIT cache required')
    u=p['units'][unit];root=Path(p['work'])/'units'/unit;root.mkdir(parents=True,exist_ok=True)
    if name=='verify':
        from dl_binner.density.grouping import load_inputs,sparse_input
        if not engineering:verify_source();verify_reuse(p['reuse_lock'])
        data,x,valid,meta=load_inputs(u['features'],u['embeddings'])
        sparse_input(u['graph'],data['ids'].tolist(),valid,u['embeddings'])
        before={n:binding(f)for n,f in u.items()}
        with (root/'verified.json').open('x')as f:json.dump(dict(inputs=before,contigs=len(data['ids']),samples=meta['samples']),f,indent=2)
    elif name=='group':
        from dl_binner.density.grouping import run
        target=root/'group'
        if target.is_dir()and not any(target.iterdir()):target.rmdir()
        run(u['features'],u['embeddings'],u['graph'],u['marker_evidence'],target,cfg,4)
    elif name=='export':
        from dl_binner.information.export import export
        target=root/'export';target.mkdir(exist_ok=True);account={}
        for arm in ['density','selected']:
            account[arm]=export(u['features'],root/'group'/(arm+'-partition.json'),u['fasta'],target/arm,include_dna=arm=='selected')
        with (target/'accounting.json').open('x')as f:json.dump(account,f,indent=2)
    else:
        from dl_binner.density.grouping import audit_cache
        from dl_binner.information.export import validate_partition
        from dl_binner.multiview.views import load
        proof=audit_cache(u['features'],u['embeddings'],u['graph'],u['marker_evidence'],root/'group',cfg)
        data,meta=load(u['features'])
        for arm in ['density','selected']:validate_partition(data,root/'group'/(arm+'-partition.json'),u['features'])
        old=json.loads((root/'verified.json').read_text())['inputs']
        if old!={n:binding(f)for n,f in u.items()}:raise ValueError('Retained input bytes changed')
        with (root/'audited.json').open('x')as f:json.dump(dict(proof,inputs_unchanged=True,truth_accessed=False),f)


def workflow(plan,dry_run=False,engineering=False):
    """Invoke the pinned local Snakemake executor with four cores and serial barriers."""
    p=json.loads(Path(plan).read_text());validate_plan(p,engineering)
    argv=[p['workflow_python'],'-I','-B','-m','snakemake','--snakefile',p['snakefile'],'--directory',p['work'],
          '--cores','4','--runtime-source-cache-path',str(Path(p['work']).parent/'workflow-source-cache'),
          '--config','plan='+str(Path(plan).absolute()),'engineering='+str(engineering).lower(),
          '--printshellcmds','--benchmark-extended']
    if dry_run:argv+=['--dry-run']
    os.execv(argv[0],argv)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--plan',required=True,type=Path)
    p.add_argument('--workflow',action='store_true');p.add_argument('--dry-run',action='store_true')
    p.add_argument('--verify-inputs',action='store_true')
    p.add_argument('--engineering',action='store_true');p.add_argument('--unit',choices=UNITS);p.add_argument('--stage',choices=STAGES)
    a=p.parse_args()
    if a.verify_inputs:
        plan=json.loads(a.plan.read_text());validate_plan(plan,a.engineering)
        if not a.engineering:verify_source()
        print(verify_reuse(plan['reuse_lock']),flush=True)
    elif a.workflow:workflow(a.plan,a.dry_run,a.engineering)
    elif a.unit and a.stage and not a.dry_run:stage(a.plan,a.unit,a.stage,a.engineering)
    else:p.error('Choose workflow, or one complete unit/stage')
