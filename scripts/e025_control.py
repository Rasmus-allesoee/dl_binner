#!/usr/bin/env python3
"""Restore-only E025 serial workers and verified partial reuse.

The plan permits only input verification, one new retrieval/hierarchy, export and
cache audit. It cannot acquire, map, train, infer GLM, redetect markers or change
cloud resources. Complete stages are byte-verified before scheduler reuse;
partial science is refused, never overwritten or automatically rerun.
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
from e024_information import load_rebound


def read_plan(path, engineering=False):
    """Admit a fixed cached-only plan; reject truth, acquisitions or old work reuse."""
    p = json.loads(Path(path).read_text())
    required = {'kind','work','python','workflow_python','worker','snakefile','policy',
                'reference','graph','marker_evidence','receipt','limits','engineering','data_archive'}
    if set(p) != required or p['kind'] != 'E025 cached joint-distance retrieval' or p['engineering'] is not engineering:
        raise ValueError('Unexpected cached-only plan/schema')
    if not engineering:
        expected = json.loads((ROOT/'experiments/E025-joint-distance-retrieval/runtime-plan.json').read_text())
        if any(p[k] != expected[k] for k in required-{'work'}):
            raise ValueError('Frozen E025 source/input/runtime/limits differ')
        work = Path(p['work'])
        if not work.is_relative_to('/srv/dl_binner/experiments/e025') or work.is_symlink():
            raise ValueError('Fresh E025 work required')
        release = os.environ.get('E025_RELEASE_FILE')
        if not release or json.loads(Path(release).read_text()).get('plan') != binding(path):
            raise ValueError('External held-parent release required')
    return p


def input_bindings(p):
    """Bind admitted external rebind members without copying or changing them."""
    r = json.loads(Path(p['receipt']).read_text())
    paths = dict(r['paths'], receipt=p['receipt'], graph=p['graph'], marker_evidence=p['marker_evidence'])
    return {k:dict(path=str(v), **binding(v)) for k,v in paths.items()}


def verify_inputs(p, engineering=False):
    """Verify the prior archive and actual retained consumer bytes, without recopy."""
    from e024_reuse_gates import archive_inventory
    proof = {}
    if not engineering:
        a = p['data_archive']
        if binding(a['path']) != {k:a[k] for k in ['bytes','sha256']}:
            raise ValueError('Missing/corrupt accepted data archive; no fallback')
        inventory = archive_inventory(a['path'])
        prior = Path(a['actual_work'])
        for name in ['rebound/rebind.json','rebound/features.npz','rebound/features.json',
                     'combined/depth.tsv','combined/depth.tsv.receipt.json']:
            if binding(prior/name) != inventory['members']['work/'+name]:
                raise ValueError('Accepted E024 data member differs: '+name)
        if Path(p['receipt']) != prior/'rebound/rebind.json':
            raise ValueError('Actual retained rebind location differs')
        proof = dict(archive={k:a[k] for k in ['bytes','sha256']}, every_prior_member_verified=True,
                     in_place_only=True, previous_science_repeated=False)
    data, _, valid, meta, _ = load_rebound(p['receipt'])
    if not engineering and (len(data['ids']) != 1286547 or int(data['lengths'].sum()) != 1669981123
                            or int(valid.sum()) != 508763 or data['depth'].shape != (1286547,10)):
        raise ValueError('Full retained Oral axes differ')
    return dict(inputs=input_bindings(p), accepted_data=proof, rows=len(data['ids']),
                bp=int(data['lengths'].sum()), samples=meta['samples'], truth_accessed=False)


def stage(path, name, engineering=False):
    """Execute only the requested new stage; all failure directories remain intact."""
    p = read_plan(path, engineering); work = Path(p['work'])
    if hasattr(os,'sched_setaffinity'):
        os.sched_setaffinity(0, sorted(os.sched_getaffinity(0))[:4])
    if name == 'verify':
        out = fresh(work,'verified')
        return seal(out, verify_inputs(p,engineering))
    from dl_binner.density.grouping import policy
    from e025_information import run, audit
    cfg = policy(p['policy'])
    if name == 'group':
        out = work/'group'
        if out.is_dir() and not any(out.iterdir()): out.rmdir()
        return run(p['receipt'], p['graph'], p['marker_evidence'], out, cfg, 4)
    if name == 'export':
        from dl_binner.information.export import export
        out = fresh(work,'export'); account = {}
        r = json.loads(Path(p['receipt']).read_text())
        for arm in ['density','selected']:
            account[arm] = export(r['paths']['rebound_features'],work/'group'/(arm+'-partition.json'),
                p['reference'],out/arm,include_dna=arm == 'selected')
        write(out/'accounting.json',account)
        return seal(out)
    if name == 'audit':
        out = fresh(work,'audited')
        value = audit(p['receipt'],p['graph'],p['marker_evidence'],work/'group',cfg)
        if input_bindings(p) != verify_seal(work/'verified')['inputs']:
            raise ValueError('Retained input changed after cached comparison')
        return seal(out,dict(proof=value))
    raise ValueError('No such cached-only stage')


def resume_gate(path, engineering=False):
    """Validate completed directories; never reschedule accepted retrieval science."""
    p=read_plan(path,engineering); work=Path(p['work'])
    for name in ['verified','export','audited']:
        folder=work/name
        if (folder/'done.json').is_file(): verify_seal(folder)
        elif folder.exists() and any(folder.iterdir()): raise ValueError('Partial stage preserved; fresh assessed attempt required: '+name)
    if (work/'group/completed.json').is_file():
        from e025_information import audit
        from dl_binner.density.grouping import policy
        audit(p['receipt'],p['graph'],p['marker_evidence'],work/'group',policy(p['policy']))
    elif (work/'group').exists() and any((work/'group').iterdir()):
        raise ValueError('Partial grouping preserved; no automatic retrieval rerun')
    if (work/'verified/done.json').is_file() and input_bindings(p) != verify_seal(work/'verified')['inputs']:
        raise ValueError('Accepted reuse inputs differ')
    return p


def workflow(path, engineering=False, dry=False):
    """Run the four-stage serial Snakemake DAG under externally bounded clocks."""
    p=resume_gate(path,engineering); work=Path(p['work']);work.mkdir(parents=True,exist_ok=True)
    argv=[p['workflow_python'],'-I','-B','-m','snakemake','--snakefile',p['snakefile'],
          '--directory',str(work),'--cores','4','--resources','mem_mb=26000',
          '--benchmark-extended','--rerun-triggers','mtime','--config','plan='+str(Path(path).absolute()),
          'engineering='+str(engineering).lower()]
    if dry:argv.append('--dry-run')
    return subprocess.run(argv,check=True).returncode


if __name__ == '__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--plan',type=Path,required=True)
    p.add_argument('--stage',choices=['verify','group','export','audit']);p.add_argument('--workflow',action='store_true')
    p.add_argument('--dry-run',action='store_true');p.add_argument('--engineering',action='store_true');a=p.parse_args()
    if a.workflow: workflow(a.plan,a.engineering,a.dry_run)
    elif a.stage: stage(a.plan,a.stage,a.engineering)
    else:p.error('Choose a stage or workflow')
