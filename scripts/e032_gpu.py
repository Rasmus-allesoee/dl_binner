#!/usr/bin/env python3
"""Make one authorized T4 qualification attempt, never an L4/capacity loop.

Uses the unchanged ec7ff25 source/model/runtime/128-view assets and tested held
parent. It cannot extract the full Oral bank or mutate the original CPU/disks.
Only verified empty capacity-failed resources are removed automatically.
"""
import argparse
import datetime
import json
from pathlib import Path
import sys
import time

ROOT=Path(__file__).absolute().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from e021_portable_cloud import Cloud,CPU_ZONE
from e024_coverage import binding,write
from e029_gpu_launch import commands,unused_owned_disks,ssh_entry,remote,render_bootstrap,render_release

SOURCE='ec7ff25b24f3db428429d5b861e7a06c4d223ca8'
ZONE='us-central1-f'
RETENTION=1794351600


def gate(f,now):
    """Require fresh exact T4 credit-only complete costs, including disk lifetime."""
    if (f['coverage_status']!='PASS_FOR_SPECIFIED_ORDINARY_FIRST_PARTY_PRODUCTS_ONLY'
        or f['real_money_authorized'] is not False or f['ceiling_USD']!=3
        or not 0<=f['estimated_complete_gross_USD']<=3
        or not 0<=now-f['checked_epoch']<7200 or not 0<=now-f['credit_checked_epoch']<7200
        or now+6300>=min(f['storage_valid_until_epoch'],f['credit_valid_until_epoch'],RETENTION)
        or f.get('T4_complete_current_pricing_passed') is not True):
        raise ValueError('Fresh complete single-T4 financial/retention gate required')


def start(out):
    """Try precisely one existing-quota Iowa-f T4, then supervise or close stockout."""
    out=Path(out).absolute();f=json.loads((out/'financial-gate.json').read_text());gate(f,time.time())
    assets=json.loads((out/'assets.json').read_text());source=json.loads((out/'source.json').read_text())
    if source['commit']!=SOURCE:raise ValueError('Unchanged qualification source required')
    c=Cloud(out/'control');before=c.state();c.put('original-CPU-before.json',before)
    q=c.call(['compute','regions','describe','us-central1']);c.put('quota-before.json',q);quotas={v['metric']:v for v in q['quotas']}
    if (quotas['NVIDIA_T4_GPUS']['limit']-quotas['NVIDIA_T4_GPUS']['usage']<1
        or quotas['DISKS_TOTAL_GB']['limit']-quotas['DISKS_TOTAL_GB']['usage']<104):
        raise ValueError('Existing T4/standard-disk quota unavailable')
    instances=c.call(['compute','instances','list'])
    if any(v.get('guestAccelerators') for v in instances):raise ValueError('Another GPU worker already exists')
    for name,a in dict(assets,source=source['asset']).items():
        m=c.call(['storage','objects','describe',a['uri']+'#'+a['generation']])
        if str(m['generation'])!=a['generation'] or int(m['size'])!=a['binding']['bytes']:
            raise ValueError('Frozen GPU asset metadata differs: '+name)
        c.put('asset-'+name.replace('.','-')+'.json',m)
    image=c.call(['compute','disks','describe',before['disks'][0]['source'].split('/')[-1]],CPU_ZONE)['sourceImage']
    name='e029-batching-'+datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%d')+'-e032-f'
    cmds=commands(name,ZONE,before,image,'T4');c.put('single-prospective-attempt.json',dict(commands=cmds,financial=f,source=source))
    preview=dict(name=name,zone=ZONE,GPU='T4',state=dict(disks=[{},dict(deviceName=name+'-work')]),
        start_epoch=time.time(),node_deadline_epoch=time.time()+5400,provider_deadline_epoch=time.time()+6300,
        source=SOURCE,source_asset=source['asset'],assets=assets,
        archive_prefix='gs://dl-binner-archive-167650584170/e032/'+name+'-preview')
    compile(render_bootstrap(preview,f),'T4 fully rendered bootstrap before creation','exec')
    compile(render_release(preview,dict(root='/srv/fixture',repo='/srv/fixture'),{}),'T4 release before creation','exec')
    try:
        for argv in cmds:c.call(argv,ZONE)
        state=c.state(name,ZONE);c.put('worker-start.json',state)
        if (state['status']!='RUNNING' or not state['machineType'].endswith('/n1-standard-8')
            or str(state['scheduling']['maxRunDuration']['seconds'])!='6300'
            or state['scheduling']['instanceTerminationAction']!='STOP' or state['scheduling']['automaticRestart']
            or state['serviceAccounts']!=before['serviceAccounts'] or not state['shieldedInstanceConfig']['enableSecureBoot']
            or len(state.get('guestAccelerators',[]))!=1 or state['guestAccelerators'][0]['acceleratorCount']!=1
            or not state['guestAccelerators'][0]['acceleratorType'].endswith('/nvidia-tesla-t4')
            or [int(v['diskSizeGb']) for v in state['disks']]!=[40,64]):
            raise ValueError('Actual single T4 scope/STOP/security differs')
        start=datetime.datetime.fromisoformat(state['lastStartTimestamp']).timestamp()
        ident=dict(name=name,zone=ZONE,GPU='T4',state=state,start_epoch=start,node_deadline_epoch=start+5400,
            provider_deadline_epoch=start+6300,source=SOURCE,source_asset=source['asset'],assets=assets,
            archive_prefix='gs://dl-binner-archive-167650584170/e032/'+name+'-'+str(int(start)))
        write(out/'identity.json',ident);ssh=ssh_entry(out,ident)
        code=render_bootstrap(ident,f);text=remote(out,ssh,code,300)
        held=json.loads(next(v.removeprefix('GPU_HELD_IDENTITY ') for v in text.splitlines() if v.startswith('GPU_HELD_IDENTITY ')))
        write(out/'held.json',held);provider=c.state(name,ZONE);c.put('provider-before-release.json',provider)
        remote(out,ssh,render_release(ident,held,provider),90)
        write(out/'released.json',dict(status='SUPERVISED_T4_QUALIFICATION_RUNNING',identity=ident,held=held,epoch=time.time()))
        return ident
    except BaseException as e:
        capacity='ZONE_RESOURCE_POOL_EXHAUSTED' in str(e)
        c.put('attempt.json',dict(error=repr(e),capacity=capacity,commands=cmds,attempts=1))
        matches=[v for v in c.call(['compute','instances','list']) if v['name']==name]
        if matches:
            c.stop(name,ZONE)
            # Any worker that booted can contain unique evidence: retain stopped
            # disks until collection has been independently verified.
            raise
        disks=unused_owned_disks(c.call(['compute','disks','list']),name,ZONE)
        for d in disks:c.call(['compute','disks','delete',d['name']],ZONE)
        write(out/'closed.json',dict(status='NOT_RUN_CAPACITY_BLOCKED' if capacity else 'FAILED_BEFORE_BOOT',
            attempts=1,compute_USD=0,temporary_empty_disks_deleted=True,no_fallback=True,error=repr(e)))
        if not capacity:raise
        return None


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--root',type=Path,required=True)
    a=p.parse_args();print(json.dumps(start(a.root)),flush=True)
