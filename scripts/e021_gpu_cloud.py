#!/usr/bin/env python3
"""Apply only the owner-approved existing-VM E021 GPU allocation or its rollback.

No new VM, disk, service, permission, reservation, or billing change. Credit and
quota gates precede all mutations. SDK responses and every command are retained;
there is no automatic start retry or alternative resource. Stop/restore is an
explicit action, with independent TERMINATED readback before E2 restoration.
"""
import argparse,datetime,json,os,subprocess,time,urllib.request
from pathlib import Path

PROJECT='project-d17bd588-df31-488f-b16';ZONE='us-central1-a';VM='dl-binner-cpu';RETENTION=1793142000;STOP=173700


def configuration_commands():
    """Return the sole prospective resource/STOP mutation sequence, without executing."""
    return [
        ['compute','instances','set-machine-type',VM,'--machine-type=n1-standard-8'],
        ['compute','instances','set-scheduling',VM,'--maintenance-policy=TERMINATE','--no-restart-on-failure','--max-run-duration='+str(STOP)+'s','--instance-termination-action=STOP'],
        ['compute','instances','set-machine-resources',VM,'--accelerator-count=1','--accelerator-type=nvidia-tesla-t4']]


def await_operation(operation,describe,timeout=180):
    """Read a submitted zonal operation to completion; never resubmit a mutation."""
    deadline=time.monotonic()+timeout
    while operation.get('status')!='DONE':
        if time.monotonic()>=deadline:raise TimeoutError('Existing restoration operation did not complete within readback window')
        time.sleep(1)
        operation=describe(operation['name'])
    if operation.get('error'):raise RuntimeError('Provider restoration operation failed: '+json.dumps(operation['error']))
    return operation


def main():
    """Run one explicit live action and seal current state/clock or preserved failure."""
    a=argparse.ArgumentParser(description=__doc__);a.add_argument('action',choices=['start','stop','restore','describe']);a.add_argument('--root',type=Path,required=True);p=a.parse_args();repo=Path(__file__).absolute().parents[1];root=p.root.absolute();root.mkdir(parents=True,exist_ok=True)
    env=os.environ.copy();env['CLOUDSDK_CONFIG']=str(repo/'artifacts/gcp-workspace/private-gcloud-config');g=repo/'artifacts/gcp-workspace/tools/google-cloud-sdk/bin/gcloud';stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ');counter=0
    def run(args,zone=True):
        nonlocal counter
        counter+=1;argv=[str(g),*args,'--project='+PROJECT]+(['--zone='+ZONE]if zone else[])+['--quiet','--format=json'];prefix=root/(stamp+'-'+str(counter))
        with (root/'cloud-actions.jsonl').open('a')as f:f.write(json.dumps(dict(epoch=time.time(),argv=argv))+'\n')
        q=subprocess.run(argv,capture_output=True,text=True,env=env,timeout=240);prefix.with_suffix('.stdout').write_text(q.stdout);prefix.with_suffix('.stderr').write_text(q.stderr)
        print('E021_CLOUD',args[:4],q.returncode,flush=True)
        if q.returncode:raise RuntimeError(q.stderr[-8000:])
        return json.loads(q.stdout)if q.stdout.strip()else None
    def state():return run(['compute','instances','describe',VM])
    def put(name,x):(root/name).write_text(json.dumps(x,indent=2)+'\n')
    before=state();put('state-before-'+stamp+'.json',before)
    if p.action=='describe':return
    if p.action=='start':
        gate=json.loads((root/'credit-gate.json').read_text())
        if gate['coverage_status']!='PASS_FOR_SPECIFIED_ORDINARY_FIRST_PARTY_PRODUCTS_ONLY'or gate['real_money_authorized']is not False or gate['new_incremental_gross_ceiling_USD']!=45:raise ValueError('Strict credit-only gate missing')
        if time.time()-datetime.datetime.fromisoformat(gate['UTC']).timestamp()>7200:raise ValueError('Live credit snapshot older than two hours')
        if time.time()+STOP+900>=RETENTION:raise ValueError('Complete provider STOP window cannot fit original retention')
        if before['status']!='TERMINATED'or not before['machineType'].endswith('/e2-standard-8')or before.get('guestAccelerators'):raise ValueError('Original stopped E2 state required')
        if not before['shieldedInstanceConfig']['enableSecureBoot']:raise ValueError('Original Secure Boot protection differs')
        global_q=run(['compute','project-info','describe'],False);regional=run(['compute','regions','describe','us-central1'],False)
        if next(x['limit']-x['usage']for x in global_q['quotas']if x['metric']=='GPUS_ALL_REGIONS')<1 or next(x['limit']-x['usage']for x in regional['quotas']if x['metric']=='NVIDIA_T4_GPUS')<1:raise ValueError('Live GPU quota not available')
        if (root/'cloud-original.json').exists():raise FileExistsError('A prior allocation attempt must be reviewed explicitly')
        put('cloud-original.json',before)
        try:
            for command in configuration_commands():run(command)
            configured=state()
            if configured['disks']!=before['disks']or configured['shieldedInstanceConfig']!=before['shieldedInstanceConfig']:raise ValueError('Disk/security mutation refused')
            if not configured['machineType'].endswith('/n1-standard-8')or len(configured.get('guestAccelerators',[]))!=1 or not configured['guestAccelerators'][0]['acceleratorType'].endswith('/nvidia-tesla-t4')or configured['guestAccelerators'][0]['acceleratorCount']!=1:raise ValueError('Exact N1/T4 resources differ')
            duration=configured['scheduling'].get('maxRunDuration',{})
            if (str(duration.get('seconds'))!=str(STOP) or duration.get('nanos',0)!=0
                    or configured['scheduling']['instanceTerminationAction']!='STOP'
                    or configured['scheduling'].get('automaticRestart',True)):
                raise ValueError('Independent provider STOP differs')
            put('configured-before-start.json',configured);run(['compute','instances','start',VM]);after=state();put('state-after-start.json',after)
            if after['status']!='RUNNING':raise ValueError('VM did not reach RUNNING')
            started=datetime.datetime.fromisoformat(after['lastStartTimestamp']).timestamp();put('allocation-clock.json',dict(original_vm_start_epoch=started,execution_deadline=started+172800,provider_STOP_deadline=started+STOP,retention_deadline=RETENTION,machine='n1-standard-8',T4=1,attempts=1))
        except BaseException as exc:
            put('cloud-failure.json',dict(error=repr(exc),epoch=time.time(),automatic_retry=False));raise
    elif p.action=='stop':
        if before['status']!='TERMINATED':run(['compute','instances','stop',VM])
        after=state();put('independent-stop.json',after)
        if after['status']!='TERMINATED':raise ValueError('Independent stop unconfirmed')
    else:
        if before['status']!='TERMINATED':raise ValueError('Stop independently before restoring E2')
        original=json.loads((root/'cloud-original.json').read_text())
        if before.get('guestAccelerators'):
            # The inspected SDK always constructs one accelerator entry, even
            # for count zero. Use the documented replacement-list REST method.
            token=subprocess.check_output([str(g),'auth','print-access-token'],env=env,text=True).strip()
            body={'guestAccelerators':[]};put('restore-accelerator-request.json',body)
            url='https://compute.googleapis.com/compute/v1/projects/'+PROJECT+'/zones/'+ZONE+'/instances/'+VM+'/setMachineResources'
            request=urllib.request.Request(url,data=json.dumps(body).encode(),method='POST',headers={'Authorization':'Bearer '+token,'Content-Type':'application/json'})
            with urllib.request.urlopen(request,timeout=45)as response:operation=json.load(response)
            put('restore-accelerator-operation.json',operation)
            completed=await_operation(operation,lambda name:run(['compute','operations','describe',name]))
            put('restore-accelerator-completed.json',completed)
            if state().get('guestAccelerators'):raise ValueError('GPU removal did not pass readback')
        old_schedule=original['scheduling'];duration=old_schedule.get('maxRunDuration',{}).get('seconds')
        args=['compute','instances','set-scheduling',VM,'--maintenance-policy='+old_schedule['onHostMaintenance'],'--no-restart-on-failure','--instance-termination-action=STOP','--clear-termination-time']
        args+=['--max-run-duration='+duration+'s']if duration else['--clear-max-run-duration']
        # Restore MIGRATE while still N1; ordinary E2 refuses TERMINATE.
        run(args)
        if not state()['machineType'].endswith('/e2-standard-8'):run(['compute','instances','set-machine-type',VM,'--machine-type=e2-standard-8'])
        restored=state();put('restored-E2.json',restored)
        if (restored['status']!='TERMINATED' or restored.get('guestAccelerators')
                or not restored['machineType'].endswith('/e2-standard-8')
                or any(restored[k]!=original[k]for k in ['disks','shieldedInstanceConfig','scheduling','serviceAccounts','metadata'])):
            raise ValueError('Independent E2/disk/security/scheduling restoration differs')

if __name__=='__main__':main()
