#!/usr/bin/env python3
"""Bounded control-plane helpers for the explicitly approved portable E021 scope.

No IAM/service changes, alternate providers, old-disk mutation or scientific retry.
Every SDK call is captured privately. The common clock begins on the first real
original-node start; failed allocations never reuse stale start/stop subtraction.
"""
import datetime,json,os,subprocess,time
from pathlib import Path
PROJECT='project-d17bd588-df31-488f-b16';CPU='dl-binner-cpu';CPU_ZONE='us-central1-a';RETENTION=1793142000
PLACEMENTS=[('us-central1-b','g2-standard-8','L4','pd-balanced'),('us-central1-c','g2-standard-8','L4','pd-balanced'),('us-central1-f','n1-standard-8','T4','pd-standard')]


def worker_commands(name,placement,baseline,image):
    """Return only the approved one-worker/40+64GiB create sequence."""
    if placement not in PLACEMENTS or not name.startswith('e021-'):raise ValueError('Unapproved worker/placement')
    zone,machine,gpu,disk=placement;boot=name+'-boot';work=name+'-work'
    network=baseline['networkInterfaces'][0];sa=baseline['serviceAccounts'][0]
    commands=[['compute','disks','create',boot,'--size=40GB','--type='+disk,'--image='+image,'--labels=experiment=e021'],['compute','disks','create',work,'--size=64GB','--type='+disk,'--labels=experiment=e021']]
    args=['compute','instances','create',name,'--machine-type='+machine,'--disk=name='+boot+',boot=yes,auto-delete=no','--disk=name='+work+',boot=no,auto-delete=no','--subnet='+network['subnetwork'],'--network-tier=STANDARD','--tags=dl-binner-iap','--service-account='+sa['email'],'--scopes='+','.join(sa['scopes']),'--metadata=enable-oslogin=TRUE,enable-guest-attributes=TRUE','--shielded-secure-boot','--shielded-vtpm','--shielded-integrity-monitoring','--maintenance-policy=TERMINATE','--no-restart-on-failure','--max-run-duration=137700s','--instance-termination-action=STOP','--labels=experiment=e021']
    if gpu=='T4':args+=['--accelerator=count=1,type=nvidia-tesla-t4']
    commands.append(args);return commands


class Cloud:
    """Capture live operations and exact allocation clock without storing tokens."""
    def __init__(self,root,repo=None):
        self.root=Path(root).absolute();self.root.mkdir(parents=True,exist_ok=True);self.repo=Path(repo or Path(__file__).absolute().parents[1]);self.sdk=self.repo/'artifacts/gcp-workspace/tools/google-cloud-sdk/bin/gcloud';self.env=os.environ.copy();self.env['CLOUDSDK_CONFIG']=str(self.repo/'artifacts/gcp-workspace/private-gcloud-config')
    def put(self,name,value):
        with (self.root/name).open('x')as f:json.dump(value,f,indent=2,allow_nan=False);f.write('\n')
    def call(self,args,zone=None,timeout=240):
        argv=[str(self.sdk),*map(str,args),'--project='+PROJECT]+(['--zone='+zone]if zone else[])+['--quiet','--format=json'];tag=str(time.time_ns())
        with(self.root/'cloud-actions.jsonl').open('a')as f:f.write(json.dumps(dict(epoch=time.time(),argv=argv))+'\n')
        p=subprocess.run(argv,capture_output=True,text=True,env=self.env,timeout=timeout)
        (self.root/(tag+'.stdout')).write_text(p.stdout);(self.root/(tag+'.stderr')).write_text(p.stderr)
        print('E021_PORTABLE_CLOUD',args[:4],p.returncode,flush=True)
        if p.returncode:raise RuntimeError(p.stderr[-9000:])
        return json.loads(p.stdout)if p.stdout.strip()else None
    def state(self,name=CPU,zone=CPU_ZONE):return self.call(['compute','instances','describe',name],zone)
    def financial(self):
        g=json.loads((self.root/'financial-gate.json').read_text())
        if g['coverage_status']!='PASS_FOR_SPECIFIED_ORDINARY_FIRST_PARTY_PRODUCTS_ONLY'or g['real_money_authorized']is not False or g['new_incremental_gross_ceiling_USD']!=45:raise ValueError('Strict credit-only financial gate missing')
        if time.time()-datetime.datetime.fromisoformat(g['UTC']).timestamp()>7200:raise ValueError('Credit observation expired; refresh, never bypass')
        if time.time()+1800>=RETENTION:raise ValueError('Original storage interval unavailable')
        return g
    def start_inventory(self):
        """One short original-E2 inventory wake; no hardware or disk mutation."""
        self.financial();before=self.state()
        if before['status']!='TERMINATED'or not before['machineType'].endswith('/e2-standard-8')or before.get('guestAccelerators'):raise ValueError('Original stopped E2 required')
        if not before['shieldedInstanceConfig']['enableSecureBoot']:raise ValueError('Original Secure Boot must remain')
        self.put('original-CPU.json',before)
        self.call(['compute','instances','set-scheduling',CPU,'--no-restart-on-failure','--max-run-duration=1800s','--instance-termination-action=STOP'],CPU_ZONE)
        setstate=self.state();duration=setstate['scheduling']['maxRunDuration']
        if str(duration['seconds'])!='1800'or duration.get('nanos',0)!=0 or setstate['disks']!=before['disks']or setstate['shieldedInstanceConfig']!=before['shieldedInstanceConfig']:raise ValueError('Inventory STOP/disk/security readback differs')
        self.call(['compute','instances','start',CPU],CPU_ZONE)
        live=self.state();self.put('inventory-start-state.json',live)
        if live['status']!='RUNNING':raise ValueError('Original E2 did not start')
        start=datetime.datetime.fromisoformat(live['lastStartTimestamp']).timestamp()
        if live['lastStartTimestamp']==before['lastStartTimestamp']:raise ValueError('No fresh successful start')
        clock=dict(first_VM_start_epoch=start,deadline_epoch=min(start+48*3600,RETENTION-900),provider_deadline_epoch=min(start+48.25*3600,RETENTION),retention_epoch=RETENTION,archive_prefix='gs://dl-binner-archive-167650584170/e021/portable-'+datetime.datetime.fromtimestamp(start,datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ'),original_CPU_running_seconds=0)
        self.put('common-clock.json',clock);return clock
    def stop(self,name=CPU,zone=CPU_ZONE):
        """Independently confirm TERMINATED after any native or controller exit."""
        state=self.state(name,zone)
        if state['status']!='TERMINATED':self.call(['compute','instances','stop',name],zone)
        final=self.state(name,zone)
        if final['status']!='TERMINATED':raise ValueError('Independent stop unconfirmed')
        self.put('stop-'+name+'-'+str(time.time_ns())+'.json',final);return final
    def restore_original_schedule(self):
        """Restore only original scheduling on an independently stopped original E2."""
        current=self.state();original=json.loads((self.root/'original-CPU.json').read_text())
        if current['status']!='TERMINATED'or current['machineType']!=original['machineType']or current['disks']!=original['disks']:raise ValueError('Original stopped resources differ')
        s=original['scheduling'];seconds=s['maxRunDuration']['seconds'];self.call(['compute','instances','set-scheduling',CPU,'--maintenance-policy='+s['onHostMaintenance'],'--no-restart-on-failure','--max-run-duration='+seconds+'s','--instance-termination-action=STOP'],CPU_ZONE)
        final=self.state();self.put('original-schedule-restored-'+str(time.time_ns())+'.json',final)
        if final['scheduling']!=original['scheduling']or any(final[k]!=original[k]for k in ['disks','shieldedInstanceConfig','metadata','serviceAccounts']):raise ValueError('Original configuration restoration differs')
        return final
