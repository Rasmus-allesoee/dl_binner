#!/usr/bin/env python3
"""Create, strictly pin and supervise one approved E029 GPU qualification worker.

Only explicitly priced capacity fallbacks are tried once. Original CPU/disks,
quotas/IAM and scientific inputs are untouched. Deletion needs verified private
collection; a failed delivery retains stopped temporary disks before November 4.
"""
import argparse,datetime,json,os,shlex,subprocess,sys,time
from pathlib import Path
ROOT=Path(__file__).absolute().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from e021_portable_cloud import Cloud,PROJECT
from e024_coverage import binding,write


def commands(name,zone,baseline,image,gpu='L4'):
    """Render only one ordinary 8-vCPU GPU/40+64 GiB worker with 105-minute STOP."""
    if not name.startswith('e029-batching-')or zone not in ['us-central1-b','us-central1-c','us-central1-f']:raise ValueError('Unapproved worker')
    disk='pd-balanced'if gpu=='L4'else'pd-standard';sa=baseline['serviceAccounts'][0];network=baseline['networkInterfaces'][0]
    result=[['compute','disks','create',name+'-boot','--size=40GB','--type='+disk,'--image='+image,'--labels=experiment=e029'],['compute','disks','create',name+'-work','--size=64GB','--type='+disk,'--labels=experiment=e029']]
    args=['compute','instances','create',name,'--machine-type='+('g2-standard-8'if gpu=='L4'else'n1-standard-8'),'--disk=name='+name+'-boot,boot=yes,auto-delete=no','--disk=name='+name+'-work,boot=no,auto-delete=no','--subnet='+network['subnetwork'],'--network-tier=STANDARD','--tags=dl-binner-iap','--service-account='+sa['email'],'--scopes='+','.join(sa['scopes']),'--metadata=enable-oslogin=TRUE,enable-guest-attributes=TRUE','--shielded-secure-boot','--shielded-vtpm','--shielded-integrity-monitoring','--maintenance-policy=TERMINATE','--no-restart-on-failure','--max-run-duration=6300s','--instance-termination-action=STOP','--labels=experiment=e029']
    if gpu=='T4':args+=['--accelerator=count=1,type=nvidia-tesla-t4']
    result.append(args);return result


def unused_owned_disks(disks,name,zone):
    """Select exact fresh temporary disks from actual inventory; refuse users/shape drift."""
    expected={name+'-boot':40,name+'-work':64};selected=[]
    if not name.startswith('e029-batching-')or zone not in ['us-central1-b','us-central1-c','us-central1-f']:raise ValueError('Unapproved empty-resource scope')
    for disk in disks:
        if disk['name']not in expected or not disk['zone'].endswith('/'+zone):continue
        if disk.get('users')or int(disk['sizeGb'])!=expected[disk['name']]or disk.get('labels',{}).get('experiment')!='e029':raise ValueError('Temporary disk ownership/shape differs')
        selected.append(disk)
    return selected


def create(out):
    """Check fresh complete cost/quota/source/assets before a bounded capacity sequence."""
    out=Path(out).absolute();c=Cloud(out/'control-plane');f=json.loads((out/'financial-gate.json').read_text())
    if time.time()-f['checked_epoch']>7200 or time.time()-f['credit_checked_epoch']>7200 or f['coverage_status']!='PASS_FOR_SPECIFIED_ORDINARY_FIRST_PARTY_PRODUCTS_ONLY'or f['real_money_authorized']is not False or f['estimated_complete_gross_USD']>f['ceiling_USD']or f['ceiling_USD']>3:raise ValueError('Fresh complete GPU credit gate required')
    if time.time()+6300>=1793746800:raise ValueError('GPU clock crosses original retention')
    assets=json.loads((out/'assets.json').read_text());source=json.loads((out/'source.json').read_text())
    if subprocess.check_output(['git','status','--porcelain'],cwd=ROOT,text=True).strip():raise ValueError('Exact clean pushed GPU source required')
    head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    if head!=source['commit']or subprocess.check_output(['git','ls-remote','origin','refs/heads/certifiable-joint-retrieval'],cwd=ROOT,text=True).split()[0]!=head:raise ValueError('GPU source packet is not the exact pushed commit')
    for n,a in assets.items():
        if not a['generation'].isdigit()or a['binding']['bytes']<=0:raise ValueError('Generation-bound complete asset required')
    before=c.state();q=c.call(['compute','regions','describe','us-central1']);c.put('quota-before.json',q)
    quota={v['metric']:v for v in q['quotas']}
    if quota['SSD_TOTAL_GB']['limit']<404 or quota['SSD_TOTAL_GB']['limit']-quota['SSD_TOTAL_GB']['usage']<104 or quota['NVIDIA_L4_GPUS']['limit']-quota['NVIDIA_L4_GPUS']['usage']<1:raise ValueError('Approved existing quota unavailable')
    existing=c.call(['compute','instances','list'])
    if any(x['name'].startswith('e029-batching-')for x in existing):raise ValueError('Existing temporary qualification worker requires inspection')
    image=c.call(['compute','disks','describe',before['disks'][0]['source'].split('/')[-1]],'us-central1-a')['sourceImage']
    for zone,gpu in [('us-central1-b','L4'),('us-central1-c','L4'),('us-central1-f','T4')]:
        prior=f.get('prior_capacity_refusals',{}).get(zone)
        if prior:
            if binding(prior['path'])!=prior['binding']:raise ValueError('Prior capacity receipt changed')
            refused=json.loads(Path(prior['path']).read_text())
            if refused.get('capacity')is not True or 'ZONE_RESOURCE_POOL_EXHAUSTED'not in refused.get('error',''):raise ValueError('Only verified capacity refusal can skip a placement')
            c.put('reused-capacity-'+zone+'.json',prior);continue
        if gpu=='T4'and f.get('T4_complete_current_pricing_passed')is not True:raise ValueError('T4 requires explicit current complete pricing; no unpriced fallback')
        if gpu=='T4'and quota['NVIDIA_T4_GPUS']['limit']-quota['NVIDIA_T4_GPUS']['usage']<1:raise ValueError('Existing T4 quota unavailable')
        name='e029-batching-'+datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%d')+'-'+zone[-1]
        cmds=commands(name,zone,before,image,gpu)
        try:
            for a in cmds:c.call(a,zone)
            state=c.state(name,zone);c.put('worker-'+zone+'.json',state)
            if state['status']!='RUNNING'or str(state['scheduling']['maxRunDuration']['seconds'])!='6300'or state['scheduling']['instanceTerminationAction']!='STOP'or not state['shieldedInstanceConfig']['enableSecureBoot']or state['serviceAccounts']!=before['serviceAccounts']:raise ValueError('Actual worker security/STOP/service scope differs')
            if [int(d['diskSizeGb'])for d in state['disks']]!=[40,64]or any(d['autoDelete']for d in state['disks'])or not state['disks'][0]['source'].endswith('/'+name+'-boot')or not state['disks'][1]['source'].endswith('/'+name+'-work'):raise ValueError('Worker disks differ')
            if len(state.get('guestAccelerators',[]))!=1 or state['guestAccelerators'][0]['acceleratorCount']!=1:raise ValueError('Exactly one native GPU required')
            start=datetime.datetime.fromisoformat(state['lastStartTimestamp']).timestamp()
            ident=dict(name=name,zone=zone,GPU=gpu,state=state,start_epoch=start,node_deadline_epoch=start+5400,provider_deadline_epoch=start+6300,source=source['commit'],source_asset=source['asset'],assets=assets,archive_prefix='gs://dl-binner-archive-167650584170/e029/'+name+'-'+str(int(start)))
            write(out/'identity.json',ident);return ident
        except BaseException as exc:
            capacity='ZONE_RESOURCE_POOL_EXHAUSTED'in str(exc);c.put('attempt-'+zone+'.json',dict(error=repr(exc),capacity=capacity,commands=cmds))
            instances=[x for x in c.call(['compute','instances','list'])if x['name']==name and x['zone'].endswith('/'+zone)]
            if instances:
                if instances[0]['status']!='TERMINATED':c.stop(name,zone)
                c.call(['compute','instances','delete',name,'--keep-disks=all'],zone)
            disks=unused_owned_disks(c.call(['compute','disks','list']),name,zone)
            for d in disks:
                if d.get('users')or d['name']not in [name+'-boot',name+'-work']:raise ValueError('Temporary empty disk ownership differs')
                c.call(['compute','disks','delete',d['name']],zone)
            if not capacity:raise
    raise RuntimeError('Approved capacity attempts exhausted; no loop')


def ssh_entry(out,ident):
    """Pin authenticated provider host keys and use the owner's existing OS Login key."""
    c=Cloud(out/'ssh-control');host=None
    for attempt in range(12):
        try:
            v=c.call(['compute','instances','get-guest-attributes',ident['name'],'--query-path=hostkeys/'],ident['zone'])
            rows=v if isinstance(v,list)else v.get('queryValue',{}).get('items',[])
            host=next(x['value']for x in rows if x['key']=='ssh-ed25519');break
        except (KeyError,StopIteration,RuntimeError):time.sleep(2)
    if not host:raise ValueError('Authenticated provider host key unavailable; no TOFU')
    if host.startswith('ssh-ed25519 '):host=host.split()[1]
    if len(host.split())!=1:raise ValueError('Malformed provider Ed25519 key')
    alias=ident['name']+'-'+ident['state']['id'];known=out/'known-hosts';known.write_text(alias+' ssh-ed25519 '+host+'\n');known.chmod(0o600)
    effective=subprocess.check_output(['ssh','-G','dl-binner-gcp'],text=True)
    key=next(x.split(' ',1)[1]for x in effective.splitlines()if x.startswith('identityfile '));user='rasmus_allesoee_gmail_com'
    proxy=shlex.join(['/usr/bin/env','CLOUDSDK_PYTHON=/opt/miniconda3/bin/python3','CLOUDSDK_CONFIG='+c.env['CLOUDSDK_CONFIG'],'CLOUDSDK_CORE_DISABLE_USAGE_REPORTING=true',str(c.sdk),'compute','start-iap-tunnel',ident['name'],'%p','--listen-on-stdin','--project='+PROJECT,'--zone='+ident['zone'],'--verbosity=warning','--quiet'])
    cfg=out/'ssh.conf';cfg.write_text('Host '+ident['name']+'\n HostName '+ident['name']+'\n User '+user+'\n IdentityFile '+key+'\n IdentitiesOnly yes\n StrictHostKeyChecking yes\n UserKnownHostsFile '+str(known)+'\n HostKeyAlias '+alias+'\n BatchMode yes\n ForwardAgent no\n PasswordAuthentication no\n ServerAliveInterval 20\n ServerAliveCountMax 3\n ProxyCommand '+proxy+'\n');cfg.chmod(0o600)
    return ['ssh','-F',str(cfg),'-o','ControlMaster=no','-o','ControlPath=none','-o','ConnectTimeout=15',ident['name']]


def remote(out,argv,code,seconds=240):
    """Compile and persist actual non-shell SSH source and its captured terminal log."""
    compile(code,'E029 GPU remote','exec');stamp=str(time.time_ns());(out/(stamp+'.py')).write_text(code)
    p=subprocess.run(argv+['/usr/bin/python3 -I -B -'],input=code,text=True,capture_output=True,timeout=seconds);(out/(stamp+'.log')).write_text(p.stdout+p.stderr);print(p.stdout+p.stderr,flush=True);p.check_returncode();return p.stdout


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--root',type=Path,required=True);a=p.parse_args();print(json.dumps(create(a.root)),flush=True)


def render_bootstrap(ident,financial):
    """Render the exact empty-disk/source/held-watchdog bootstrap before release."""
    code=r'''import os,subprocess,pathlib,json,pwd,time,tarfile,urllib.request,urllib.parse,hashlib
ident=@@IDENT@@
financial=@@FINANCE@@
name=ident['name'];device=ident['state']['disks'][1]['deviceName'];user='rasmus_allesoee_gmail_com'
mount=r"""import os,json,subprocess,pathlib,pwd
name=@@NAME@@;device=@@DEVICE@@;user=@@USER@@
if not name.startswith('e029-batching-')or device not in ['persistent-disk-1',name+'-work']:raise ValueError('Exact new device required')
disk=pathlib.Path('/dev/disk/by-id/google-'+device)
def call(a):return subprocess.run(a,check=True,text=True,capture_output=True)
if os.path.ismount('/srv/dl_binner'):raise ValueError('Fresh GPU mount required')
x=json.loads(call(['lsblk','-J','-b','-o','NAME,SIZE,TYPE,FSTYPE,MOUNTPOINT',str(disk)]).stdout)['blockdevices']
if len(x)!=1 or x[0]['size']!=64*1024**3 or x[0].get('fstype')or x[0].get('children')or x[0].get('mountpoint'):raise ValueError('Only empty newly created 64 GiB disk can be formatted')
if subprocess.run(['blkid',str(disk)],capture_output=True).returncode!=2:raise ValueError('Existing disk signature refused')
call(['mkfs.ext4','-m','0','-L','e029-work',str(disk)]);pathlib.Path('/srv/dl_binner').mkdir(exist_ok=True);call(['mount','-o','nosuid,nodev',str(disk),'/srv/dl_binner']);a=pwd.getpwnam(user);os.chown('/srv/dl_binner',a.pw_uid,a.pw_gid)
print('NEW_GPU_WORK_MOUNTED')
""".replace('@@NAME@@',repr(name)).replace('@@DEVICE@@',repr(device)).replace('@@USER@@',repr(user))
subprocess.run(['sudo','-n','/usr/bin/python3','-I','-B','-'],input=mount,text=True,check=True)
root=pathlib.Path('/srv/dl_binner/experiments/e029')/('gpu-qualification-'+str(int(ident['start_epoch'])));root.mkdir(parents=True)
for n in ['logs','gates','tmp']:(root/n).mkdir()
repo=pathlib.Path('/srv/dl_binner/e029-source-'+ident['source'][:7]);repo.mkdir()
a=ident['source_asset'];u=urllib.parse.urlsplit(a['uri']);request=urllib.request.Request('http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/token',headers={'Metadata-Flavor':'Google'})
with urllib.request.urlopen(request,timeout=10)as f:token=json.load(f)['access_token']
url='https://storage.googleapis.com/storage/v1/b/'+u.netloc+'/o/'+urllib.parse.quote(u.path.lstrip('/'),safe='')+'?alt=media&generation='+a['generation']
req=urllib.request.Request(url,headers={'Authorization':'Bearer '+token});packet=root/'source.tar.gz';h=hashlib.sha256();size=0
with urllib.request.urlopen(req,timeout=60)as f,packet.open('xb')as out:
 for b in iter(lambda:f.read(1024**2),b''):
  size+=len(b)
  if size>50*1024**2:raise ValueError('Source packet cap exceeded')
  out.write(b);h.update(b)
if dict(bytes=size,sha256=h.hexdigest())!=a['binding']:raise ValueError('Exact source packet differs')
logical=0;seen=set()
with tarfile.open(packet)as archive:
 for m in archive:
  p=pathlib.Path(m.name);logical+=m.size
  if p.is_absolute()or'..'in p.parts or m.name in seen or not(m.isfile()or m.isdir())or logical>150*1024**2 or len(seen)>20000:raise ValueError('Unsafe/oversized source packet')
  seen.add(m.name);archive.extract(m,repo,filter='data')
import sys,shutil
sys.path.insert(0,str(repo/'scripts'))
from e024_coverage import binding
from e021_control_json import publish
lock=json.loads((repo/'experiments/E029-certifiable-joint-retrieval/gpu-source-lock.json').read_text())
for n,b in lock['files'].items():
 if binding(repo/n)!=b:raise ValueError('Frozen GPU/source member differs')
u=shutil.disk_usage('/srv/dl_binner');boot=shutil.disk_usage('/')
if os.cpu_count()!=8 or u.free<50*1024**3 or boot.free<5*1024**3:raise ValueError('Fresh GPU resources/headroom differ')
memory=int(next(x.split()[1]for x in pathlib.Path('/proc/meminfo').read_text().splitlines()if x.startswith('MemTotal:')))*1024
if memory<29000000000:raise ValueError('Native GPU host RAM below declared tree/OS headroom')
h=dict(physical_memory_bytes=memory,user=user,boot_id=pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip(),work_used_bytes=u.used,work_free_bytes=u.free,boot_used_bytes=boot.used,boot_free_bytes=boot.free,cpus=os.cpu_count(),kernel=os.uname().release,source_packet=binding(packet))
cfg=dict(root=str(root),repo=str(repo),source=ident['source'],start_epoch=ident['start_epoch'],node_deadline_epoch=ident['node_deadline_epoch'],provider_deadline_epoch=ident['provider_deadline_epoch'],service_name='e029-batching-'+str(int(ident['start_epoch'])),GPU=ident['GPU'],assets=ident['assets'],archive_prefix=ident['archive_prefix'],financial_gate=financial)
publish(h,root/'host.json');publish(cfg,root/'config.json')
p=subprocess.run(['sudo','-n','/usr/bin/python3','-I','-B',str(repo/'scripts/e029_gpu_arm.py'),'--config',str(root/'config.json')],capture_output=True,text=True)
(root/'logs/arm.log').write_text(p.stdout+p.stderr);print(p.stdout+p.stderr,flush=True);p.check_returncode()
print('GPU_HELD_IDENTITY',json.dumps(dict(root=str(root),repo=str(repo),config=binding(root/'config.json'),service_name=cfg['service_name'])),flush=True)
'''
    code=code.replace('@@IDENT@@',repr(ident)).replace('@@FINANCE@@',repr(financial))
    compile(code,'actual-E029-GPU-bootstrap','exec');return code


def render_release(ident,held,provider):
    """Bind actual current watcher/process and provider STOP to the one setup/probe release."""
    code=r'''import pathlib,json,sys,time,subprocess
ident=@@IDENT@@;held=@@HELD@@;provider=@@PROVIDER@@
root=pathlib.Path(held['root']);sys.path.insert(0,str(pathlib.Path(held['repo'])/'scripts'))
from e021_control_json import publish
from e024_coverage import binding
from e009_exit_watchdog import identity
cfg=json.loads((root/'config.json').read_text());w=json.loads((pathlib.Path('/var/lib')/(cfg['service_name']+'-exit')/'status.json').read_text());started=json.loads((root/'started.json').read_text())
if w['decision']!='workflow alive'or w['expected_process']!=identity(started['pid'])or w['observed_process']!=w['expected_process']or w['boot_id']!=pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip():raise ValueError('Current held GPU watcher differs')
if subprocess.check_output(['systemctl','is-active',cfg['service_name']+'-exit.timer'],text=True).strip()!='active':raise ValueError('GPU timer inactive')
if provider['status']!='RUNNING'or str(provider['scheduling']['maxRunDuration']['seconds'])!='6300'or provider['scheduling']['instanceTerminationAction']!='STOP':raise ValueError('Independent GPU provider STOP differs')
if time.time()>cfg['node_deadline_epoch']-1800:raise TimeoutError('GPU setup clock unavailable')
f=cfg['financial_gate']
if time.time()-f['checked_epoch']>7200 or f['real_money_authorized']is not False or f['estimated_complete_gross_USD']>f['ceiling_USD']:raise ValueError('GPU finance stale/unclear')
publish(provider,root/'logs/provider-before-release.json')
publish(dict(config=binding(root/'config.json'),credit_covered=True,provider_STOP_verified=True,watchdog=w,source=ident['source'],epoch=time.time(),full_community_work_authorized=False),root/'release.json')
print('GPU_QUALIFICATION_RELEASED',str(root),flush=True)
'''
    code=code.replace('@@IDENT@@',repr(ident)).replace('@@HELD@@',repr(held)).replace('@@PROVIDER@@',repr(provider));compile(code,'actual-E029-GPU-release','exec');return code
