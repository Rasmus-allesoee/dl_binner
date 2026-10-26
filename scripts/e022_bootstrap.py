#!/usr/bin/env python3
"""Prepare E022's held native parent and run its existing gates inside one clock.

This operational adapter changes no candidate/default/input science. It installs
only the locked wheel against the accepted complete read-only CPU base, arms the
existing watcher and invokes prepared gates. It neither releases community science
nor starts/provisions a VM. A disconnected controller leaves the held parent with
its original setup timeout and provider STOP. Failures publish an abort, never retry.
"""
import argparse
from datetime import datetime
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time
sys.path.insert(0,str(Path(__file__).absolute().parent))
from e009_owner import supervisor,Tee
from e009_controls import PhaseGuard
from e014_collect import binding
from e021_control_json import publish
from e022_phase import configuration


def plan_for(identity,repo):
    """Instantiate only declared paths; preserve all fixed E009 native input locators."""
    repo=Path(repo);root=Path(identity['root'])
    plan=json.loads((repo/'experiments/E022-marker-informed-learning/plan-template.json').read_text().replace('{REPO}',str(repo)).replace('{PHASE}',str(root)))
    reuse=json.loads((repo/'experiments/E022-marker-informed-learning/reuse-lock.json').read_text())
    if plan['unit']!=reuse['units']['E009-relational'] or plan['threads']!=4:raise ValueError('Frozen E009 plan differs')
    return plan,reuse


def admit(identity,finance,now):
    """Refuse stale finance, another scope or a reset/expired original setup clock."""
    if identity['ceiling_USD']!=2 or identity['provider_STOP_seconds']!=8100 or identity['storage_retention_extended']is not False:
        raise ValueError('Frozen cost/STOP/retention differs')
    if finance['coverage_status']!='PASS_FOR_SPECIFIED_ORDINARY_FIRST_PARTY_PRODUCTS_ONLY' or finance['real_money_authorized']is not False or finance['new_incremental_gross_ceiling_USD']!=2:
        raise ValueError('Strict current credit-only gate missing')
    observed=datetime.fromisoformat(finance['UTC']).timestamp()
    if not 0<=now-observed<7200 or not 0<=now-identity['vm_start_epoch']<1800:raise TimeoutError('Original finance/setup clock expired')
    if identity['vm_start_epoch']+8100>=min(finance['credit_valid_until_epoch'],finance['storage_valid_until_epoch']):raise ValueError('Credit/storage boundary exceeded')
    if not identity['archive_prefix'].startswith('gs://dl-binner-archive-167650584170/e022/') or len(identity['source'])!=40:
        raise ValueError('Unexpected archive/source identity')


def run(path):
    """Install once, arm/test the real watcher and gate; leave science explicitly held."""
    identity=json.loads(Path(path).read_text());root=Path(identity['root']);repo=Path(identity['repo']);exp=repo/'experiments/E022-marker-informed-learning'
    finance=json.loads((root/'payload/financial-gate.json').read_text());admit(identity,finance,time.time())
    if not os.path.ismount('/srv/dl_binner') or os.cpu_count()!=8:raise ValueError('Original allocation/mount differs')
    if subprocess.check_output(['git','rev-parse','HEAD'],cwd=repo,text=True).strip()!=identity['source'] or subprocess.check_output(['git','status','--porcelain'],cwd=repo,text=True).strip():raise ValueError('Exact clean source required')
    freeze=json.loads((exp/'source-lock.json').read_text())
    for name,wanted in freeze['files'].items():
        if binding(repo/name)!=wanted:raise ValueError('Original frozen candidate/policy source differs: '+name)
    candidate=json.loads((exp/'candidate-lock.json').read_text());inputs=json.loads((exp/'input-lock.json').read_text())
    wheel=root/'payload/dl_binner-0.1.0.dev9-py3-none-any.whl'
    if binding(wheel)!=candidate['wheel'] or binding(root/'payload/E009-pairs.tar.gz')!=inputs['pair_archive']:raise ValueError('Locked payload bytes differ')
    plan,reuse=plan_for(identity,repo);publish(plan,root/'science-plan.json')
    bindfiles=[exp/'source-lock.json',exp/'candidate-lock.json',exp/'input-lock.json',exp/'config.json',exp/'protocol.json',exp/'plan-template.json',repo/'scripts/e022_bootstrap.py',root/'science-plan.json',root/'payload/financial-gate.json',wheel]
    binds={str(p):binding(p)for p in bindfiles}
    cfg=configuration(identity,repo,identity['initial_filesystem_used_bytes'],binds);publish(cfg,root/'config.json')
    publish(dict(boot_id=Path('/proc/sys/kernel/random/boot_id').read_text().strip(),user=identity['user'],cpus=os.cpu_count(),filesystem=shutil.disk_usage(root)._asdict()),root/'host.json')
    sup=supervisor();env=sup.isolated_env(4);env.update(NUMBA_NUM_THREADS='4',NUMBA_CACHE_DIR=str(root/'native-cache'),TMPDIR=str(root/'tmp'),HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1')
    deadline=identity['vm_start_epoch']+1800;results=[]
    def cmd(name,argv):
        left=deadline-time.time()
        if left<5:raise TimeoutError('Original setup clock exhausted')
        print('E022_BOOTSTRAP_STAGE',name,flush=True)
        v=sup.supervise(argv,root/'logs'/('bootstrap-'+name+'.log'),left,26_000_000_000,env,sample_root=os.getpid());results.append(dict(name=name,resources=v))
    growth=max(0,shutil.disk_usage(root).used-identity['initial_filesystem_used_bytes'])
    with PhaseGuard(root,deadline-time.time(),growth_bytes=20*1024**3-growth)as guard:
        base=Path(reuse['native_dependency_base'])
        cmd('package-install',[str(base/'bin/python'),'-I','-B',str(repo/'scripts/e019_runtime.py'),'create','--base',str(base),'--destination',str(root/'env'),'--wheel',str(wheel),'--output',str(root/'package-install.json')])
        cmd('arm',['sudo','-n','/usr/bin/python3','-I','-B',str(repo/'scripts/e022_arm.py'),'--config',str(root/'config.json')])
        cmd('native-gates',['/usr/bin/python3','-I','-B',str(repo/'scripts/e022_gates.py'),'--config',str(root/'config.json')])
        complete=json.loads((root/'gates/completion.json').read_text());watch=json.loads((root/'logs/supervision.json').read_text())
        if complete['status']!='SUCCESS' or watch['source_commit']!=identity['source']:raise ValueError('Gate/watcher source contract differs')
        publish(dict(status='READY_FOR_INDEPENDENT_RELEASE',config=binding(root/'config.json'),gates=binding(root/'gates/completion.json'),supervision=binding(root/'logs/supervision.json'),stages=results,disk_observations=guard.observations,elapsed_since_VM_start_seconds=time.time()-identity['vm_start_epoch'],science_released=False),root/'bootstrap-ready.json')
    print('E022_HELD_READY_NO_SCIENCE_RELEASED',root,flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--identity',type=Path,required=True);a=p.parse_args();i=json.loads(a.identity.read_text());root=Path(i['root'])
    with (root/'logs/bootstrap-terminal.log').open('x')as log:
        old=sys.stdout,sys.stderr;sys.stdout=Tee(sys.stdout,log);sys.stderr=Tee(sys.stderr,log)
        try:run(a.identity)
        except BaseException as e:
            failure=dict(error=type(e).__name__+': '+str(e),epoch=time.time(),science_released=False)
            publish(failure,root/'bootstrap-failure.json')
            if (root/'started.json').exists():publish(failure,root/'abort.json')
            if not(root/'logs/supervision.json').exists():subprocess.run(['sudo','-n','/sbin/shutdown','-h','now'],check=False)
            raise
        finally:sys.stdout,sys.stderr=old
