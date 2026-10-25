#!/usr/bin/env python3
"""Restore-only E021 CPU recovery from the existing, checksum-bound handoff.

Never starts a VM, installs software, recopies missing data, extracts DNA or
repeats a completed fit. The retained receiver records remain unchanged. Fresh
transport evidence is distinct from the subsequent actual consumer admission.
All ten control files exist completely before the native parent is armed.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import sys
import time
sys.path.insert(0,str(Path(__file__).absolute().parent))
from e021_control_json import publish
from e021_portable_handoff import bound
from e021_portable_transport import names,paired

STAGES=['train','embed','group','refine','export','graph-proof']


def admit_transport(manifest,ledger,receiver,directory):
    """Verify the three historical stream hashes and actual retained member bytes."""
    names(manifest)
    if ledger['status']!='PASS'or receiver!=ledger['receiver']:
        raise ValueError('Retained receiver/ledger differs')
    digest=hashlib.sha256(json.dumps(manifest,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    result=paired(ledger['sender'],receiver,ledger['stream'])
    if result['manifest_sha256']!=digest or result['members']!=len(manifest['files']):
        raise ValueError('Closed transport manifest differs')
    directory=Path(directory)
    for rel,b in manifest['files'].items():
        if bound(directory/rel)!={k:b[k]for k in ['bytes','sha256']}:
            raise ValueError('Retained transported member differs: '+rel)
    return dict(status='PASS_PAIRED_TRANSPORT_AND_RETAINED_BYTES',pairing=result,
        consumer_admitted=False,
        scope='Legacy pairing.consumer_admitted names transport only; actual native reader still required',
        directory=str(directory),members={k:{n:b[n]for n in ['bytes','sha256']}for k,b in manifest['files'].items()})


def restore_links(source,destination,expected):
    """Hardlink exact verified bank members into a fresh work root; no copy fallback."""
    source=Path(source);destination=Path(destination)
    actual={str(p.relative_to(source))for p in source.rglob('*')if p.is_file()}
    if actual!=set(expected):raise ValueError('Unexpected old work: refuse possible completed science')
    for rel,b in expected.items():
        if bound(source/rel)!=b:raise ValueError('Original bank changed before restore')
    destination.mkdir(parents=True,exist_ok=False)
    for rel,b in expected.items():
        p=destination/rel;p.parent.mkdir(parents=True,exist_ok=True);os.link(source/rel,p)
        if bound(p)!=b:raise ValueError('Hardlink restore differs')
    return {k:bound(destination/k)for k in expected}


def tasks(cfg):
    """Freeze three admission gates, six sole consumers and an automatic final target."""
    r=Path(cfg['root']);repo=Path(cfg['repo']);py=cfg['runtime_prefix']+'/bin/python';plan=str(r/'science-plan.json')
    rows=[]
    for op in ['verify-retained','bank','admit']:
        if op=='bank':
            argv=[py,'-I','-B',str(repo/'scripts/e021_portable_handoff.py'),'bank','--context','--plan',plan,'--output',str(r/'gates/E009-restored-bank.json')]
        else:argv=['/usr/bin/python3','-I','-B',str(repo/'scripts/e021_restore_cpu.py'),op,'--config',str(r/'config.json')]
        rows.append(dict(name='restore-only-'+op,kind='gate',seconds=1200,argv=argv))
    for stage in STAGES:
        rows.append(dict(name='E009-'+stage,kind='science',unit='E009-hybrid',stage=stage,seconds=6000,
            argv=[py,'-I','-B',str(repo/'scripts/e021_control.py'),'--plan',plan,'--unit','E009-hybrid','--stage',stage]))
    rows.append(dict(name='complete-E009-target-and-close',kind='gate',seconds=240,
        argv=[py,'-I','-B',str(repo/'scripts/e021_portable_handoff.py'),'cpu-target','--root',str(r),'--plan',plan]))
    return rows


def prepare(config):
    """Reuse passed setup, validate old handoff, and arm a completely preloaded queue."""
    cfg=json.loads(Path(config).read_text());r=Path(cfg['root']);old=Path(cfg['retained_consumer_root'])
    prior=json.loads((old/'completion.json').read_text())
    if any(x['kind']=='science'for x in prior['stages']):raise ValueError('Prior scientific attempt exists; explicit stage resume required')
    inventory=json.loads((old/'tasks/0001.result.json').read_text())
    if inventory['status']!='SUCCESS'or inventory['name']!='fresh-owned-CPU-inventory':
        raise ValueError('Passed inventory stage not retained')
    from e021_portable_reuse_node import start
    # Prepare the same verified source/runtime/host layout, but do not arm early.
    setup=dict(cfg,prepare_only=True)
    p=Path(config).with_name('prepared-config.json');publish(setup,p);start(p)
    # Final config removes the preparation flag; its bytes are frozen before arm.
    (r/'config.json').rename(r/'preparation-config.json');publish(cfg,r/'config.json')
    packet=Path(config).parent/'handoff';dest=r/'payload/handoff';shutil.copytree(packet,dest)
    proofs={}
    for label,folder in [('bank',old/'work/units/E009-hybrid'),('runtime',old/'preserved-GPU-runtime')]:
        manifest=json.loads((dest/(label+'-manifest.json')).read_text());ledger=json.loads((dest/(label+'-ledger.json')).read_text())
        receiver=json.loads((old/('transport-E009-'+label+'-v1-received.json')).read_text())
        proofs[label]=admit_transport(manifest,ledger,receiver,folder)
    restore_links(old/'work/units/E009-hybrid',r/'work/units/E009-hybrid',proofs['bank']['members'])
    publish(dict(status='PASS',transports=proofs,old_receivers_unchanged=True),r/'gates/transport-pairs.json')
    publish(dict(status='PASS',prior_stage=bound(old/'tasks/0001.result.json'),runtime_inventory=bound(old/'gates/runtime-native.json'),original=json.loads((old/'gates/runtime-native.json').read_text())),r/'gates/reused-inventory.json')
    # Retain malformed-publication evidence without executing any old command.
    old_tasks={p.name:dict(binding=bound(p),valid_JSON=json.loads(p.read_text()))for p in sorted((old/'tasks').glob('*.json'))}
    publish(old_tasks,r/'gates/prior-task-journals.json')
    (r/'tasks').mkdir()
    for i,task in enumerate(tasks(cfg),1):publish(task,r/'tasks'/(str(i).zfill(4)+'.json'))
    import subprocess
    subprocess.run(['sudo','-n','/usr/bin/python3','-I','-B',str(Path(cfg['repo'])/'scripts/e021_portable_arm.py'),'--config',str(r/'config.json')],check=True)
    print('RESTORE_ONLY_E009_QUEUE_ARMED_NO_MAC_DEPENDENCY',flush=True)


def verify_retained(cfg):
    """Verify inert runtime archive members, accepted tiny exits and reused sources."""
    r=Path(cfg['root']);old=Path(cfg['retained_consumer_root']);d=old/'preserved-GPU-runtime'
    from e021_portable_runtime_archive import verify
    m=json.loads((d/'runtime-preservation.json').read_text());verify(d/'native-runtime.tar.gz',m['members'])
    tiny=Path(cfg['reuse_root']).with_name('cpu-staging-v3')/'gates/tiny-cached-native.json';t=json.loads(tiny.read_text())
    if(t['status']!='PASS_REAL_NATIVE_CACHED_TINY_BOTH_MODES'or len(t['records'])!=12
        or any(x['exit']!=0 for x in t['records'])):raise ValueError('Passed real tiny contracts missing')
    inventory=json.loads((old/'gates/runtime-native.json').read_text())
    if inventory['status']!='PASS'or inventory['prefix']!=cfg['runtime_prefix']:raise ValueError('Accepted owned runtime differs')
    for alias,v in inventory['loaded_library_aliases'].items():
        p=Path(alias).resolve(strict=True)
        if str(p)!=v['resolved']or bound(p)!=v['binding']:raise ValueError('Reused native library identity differs')
    package=Path(cfg['runtime_prefix'])/'lib/python3.10/site-packages/dl_binner'
    lock=json.loads((Path(cfg['repo'])/'experiments/E021-frozen-sequence-hybrid/candidate-lock.json').read_text())
    if {str(p.relative_to(package)):bound(p)for p in package.rglob('*')if p.is_file()and p.suffix in ['.py','.json']}!=lock['package_files']:
        raise ValueError('Installed frozen scientific package differs')
    publish(dict(status='PASS_RETAINED_RUNTIME_AND_TINY',runtime_archive=bound(d/'native-runtime.tar.gz'),runtime_manifest=bound(d/'runtime-preservation.json'),passed_tiny=bound(tiny),passed_runtime=bound(old/'gates/runtime-native.json'),no_reinstallation=True,no_tiny_fit_replay=True),r/'gates/retained-runtime-and-tiny.json')


def admit(cfg):
    """Admit only verified restore gates under the original budget and current watcher."""
    r=Path(cfg['root'])
    for i in [1,2]:
        if json.loads((r/'tasks'/(str(i).zfill(4)+'.result.json')).read_text())['status']!='SUCCESS':
            publish(dict(reason='Prior restore gate failed'),r/'abort.json');raise ValueError('Restore gate failed; no scientific release')
    bank=json.loads((r/'gates/E009-restored-bank.json').read_text())
    if bank['status']!='PASS_ACTUAL_E009_BANK_READER'or bank['context_arrays_read']is not True:
        raise ValueError('Full frozen bank and context reader not admitted')
    finance=json.loads((r/'payload/handoff/recovery-assessment.json').read_text())
    if(finance['status']!='APPROVED_WITHIN_ORIGINAL_ALLOWANCE'or finance['real_money_authorized']is not False
        or time.time()>finance['gate_valid_until_epoch']):
        raise ValueError('Original credit-only recovery gate missing')
    publish(dict(status='PASS_ACTUAL_E009_CONSUMER',transport=bound(r/'gates/transport-pairs.json'),runtime=bound(r/'gates/retained-runtime-and-tiny.json'),bank=bound(r/'gates/E009-restored-bank.json'),consumer_admitted=True,old_receivers_unchanged=True),r/'gates/consumer-admission.json')
    files=[r/'gates/consumer-admission.json',r/'gates/transport-pairs.json',r/'gates/retained-runtime-and-tiny.json',r/'gates/reused-inventory.json',r/'gates/E009-restored-bank.json',r/'logs/maintenance-restart-refused.json']
    publish(dict(all_native_gates_passed=True,watchdog_current=True,config=bound(r/'config.json'),gate_files={str(p):bound(p)for p in files},science_plan=str(r/'science-plan.json'),science_plan_binding=bound(r/'science-plan.json'),gross_upper_USD=finance['whole_phase_gross_upper_USD'],covered_by_welcome_credit=True,scope='E009-only restore; original joint criterion remains unmet'),r/'release.json')


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('operation',choices=['prepare','verify-retained','admit']);p.add_argument('--config',type=Path,required=True);a=p.parse_args()
    if a.operation=='prepare':prepare(a.config)
    else:
        cfg=json.loads(a.config.read_text())
        verify_retained(cfg)if a.operation=='verify-retained'else admit(cfg)
