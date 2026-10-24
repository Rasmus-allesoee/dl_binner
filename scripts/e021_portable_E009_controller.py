#!/usr/bin/env python3
"""One bounded E009 bank handoff and release of six unchanged CPU consumers.

The owner-approved phase retains its original $45/48-hour and per-node limits.
This controller never retries science, installs software or provisions resources.
Native parents own collection and shutdown independently of this Mac process.
"""
import argparse,datetime,hashlib,json,os,shlex,subprocess,sys,time
from pathlib import Path
sys.path.insert(0,str(Path(__file__).absolute().parent))
from e021_portable_cloud import Cloud,CPU,CPU_ZONE
from e021_portable_relay import transfer

def binding(p):
    """Bind a small immutable control file."""
    b=Path(p).read_bytes();return dict(bytes=len(b),sha256=hashlib.sha256(b).hexdigest())

def call(r,argv,seconds=180,input=None):
    """Capture each actual command and surface its native cause."""
    tag=str(time.time_ns());p=subprocess.run(argv,capture_output=True,text=True,input=input,timeout=seconds)
    (r/(tag+'-handoff-command.log')).write_text(json.dumps(argv)+chr(10)+p.stdout+p.stderr)
    if p.returncode:raise RuntimeError('Handoff command failed '+tag+': '+p.stderr[-1000:])
    return p.stdout

def remote(r,n,code,value=None,seconds=180):
    """Use the pinned nonmultiplexed IAP path; never transfer credentials."""
    return call(r,n.get('bulk_ssh',n['ssh'])+['/usr/bin/python3 -I -B -c '+shlex.quote(code)],seconds,None if value is None else json.dumps(value))

def read(r,n,p):return json.loads(remote(r,n,'from pathlib import Path;print(Path('+repr(p)+').read_text())'))

def put(r,n,p,v):
    remote(r,n,"import json,sys;from pathlib import Path;f=Path("+repr(p)+").open('x');json.dump(json.load(sys.stdin),f);f.write(chr(10));f.close()",v)

def queue(r,n,i,v):put(r,n,n['root']+'/tasks/'+str(i).zfill(4)+'.json',v)

def wait(r,n,i,deadline):
    """Observe an existing task; failure cannot schedule a replacement."""
    p=n['root']+'/tasks/'+str(i).zfill(4)+'.result.json'
    while time.time()<deadline:
        v=json.loads(remote(r,n,'from pathlib import Path;p=Path('+repr(p)+");print(p.read_text()if p.exists()else'null')"))
        if v:
            if v['status']!='SUCCESS':raise RuntimeError('Native task failed '+json.dumps(v))
            return v
        time.sleep(30)
    raise TimeoutError('Original handoff/phase clock exhausted')

def validate_lease(v,c,now):
    """Reserve this whole preapproved phase against the observed available credit."""
    if(v['gross_upper_USD']>45 or v['real_money']is not False or v['available_USD_after_pending_reserve']<45
       or v['credit_expiry_epoch']<=c['provider_deadline_epoch']or now>=c['deadline_epoch']-7200
       or v['scope']!='SAME_PREAPPROVED_E009_PHASE_ONLY'):raise ValueError('Phase credit/clock reservation failed')

def run(root):
    """Restore one exact bank, verify native consumers and release each stage once."""
    r=Path(root).absolute();repo=Path(__file__).absolute().parents[1];cloud=Cloud(r,repo)
    nodes=json.loads((r/'active-nodes.json').read_text());g=nodes['nodes']['gpu'];clock=json.loads((r/'common-clock.json').read_text());lease=json.loads((r/'E009-phase-credit-reservation.json').read_text())
    validate_lease(lease,clock,time.time())
    if binding(lease['financial_receipt'])!=lease['financial_binding']:raise ValueError('Admitted financial bytes differ')
    with(r/'E009-controller-started.json').open('x')as f:json.dump(dict(pid=os.getpid(),epoch=time.time(),scope=binding(r/'E009-only-scope.json')),f)
    wait(r,g,6,min(clock['deadline_epoch']-7200,time.time()+12*3600))
    bank=read(r,g,g['root']+'/gates/E009-bank-reader.json')
    if bank['status']!='PASS_ACTUAL_E009_BANK_READER':raise ValueError('Full native GPU bank not proved')
    validate_lease(lease,clock,time.time())
    for rel,b in lease['operational_files'].items():
        if binding(repo/rel)!=b:raise ValueError('Frozen handoff helper changed: '+rel)
    billing=cloud.call(['billing','projects','describe','project-d17bd588-df31-488f-b16'])
    if billing.get('billingEnabled')is not True:raise ValueError('Original billing project inactive')
    before=cloud.state();original=json.loads((r/'original-CPU.json').read_text())
    if before['status']!='TERMINATED'or any(before[k]!=original[k]for k in ['machineType','disks','shieldedInstanceConfig','serviceAccounts','metadata']):raise ValueError('Original stopped E2 resources differ')
    last=json.loads((r/'cpu-evidence-v4-start.json').read_text());used=last['prior_cumulative_CPU_seconds']+datetime.datetime.fromisoformat(before['lastStopTimestamp']).timestamp()-last['start_epoch']
    if used+15300>20.25*3600 or time.time()+15300>clock['provider_deadline_epoch']:raise TimeoutError('Remaining cumulative CPU/common cap insufficient')
    cloud.call(['compute','instances','set-scheduling',CPU,'--no-restart-on-failure','--max-run-duration=15300s','--instance-termination-action=STOP'],CPU_ZONE)
    cloud.call(['compute','instances','start',CPU],CPU_ZONE);state=cloud.state()
    if state['status']!='RUNNING'or str(state['scheduling']['maxRunDuration']['seconds'])!='15300':raise ValueError('CPU provider STOP readback failed')
    start=datetime.datetime.fromisoformat(state['lastStartTimestamp']).timestamp();cloud.put('cpu-E009-consumer-start.json',dict(state=state,prior_cumulative_CPU_seconds=used,start_epoch=start))
    n=nodes['nodes']['cpu'];n['root']=str(Path(g['root']).with_name('cpu-E009-consumer-v5'));n['ssh']=n['bulk_ssh'];(r/'E009-consumer-nodes.json').write_text(json.dumps(nodes,indent=2)+chr(10))
    for _ in range(12):
        try:remote(r,n,'print("PINNED_CPU_SSH_READY")',seconds=15);break
        except(RuntimeError,subprocess.TimeoutExpired):time.sleep(3)
    else:raise RuntimeError('Pinned CPU SSH unavailable')
    remote(r,n,"import os,subprocess;subprocess.run(['sudo','-n','mount','-U','f76283ed-60c4-4060-bd22-84c95f38d3fb','/srv/dl_binner'],check=True)if not os.path.ismount('/srv/dl_binner')else None")
    cc=json.loads((r/'cpu-resume-config.json').read_text());cc.update(root=n['root'],service_name='e021-portable-cpu-E009-5',node_deadline_epoch=start+14400,provider_deadline_epoch=start+15300,peer_reservation_bytes=16*1024**3,archive_prefix=clock['archive_prefix']+'/cpu-E009-consumer-v5',return_cap_bytes=2*1024**3)
    packet=r/'E009-consumer-packet';packet.mkdir();(packet/'cpu-config.json').write_text(json.dumps(cc,indent=2)+chr(10))
    p=json.loads((repo/'experiments/E021-frozen-sequence-hybrid/native-plan-template.json').read_text().replace('@REPO@',cc['repo']).replace('@RUN_ROOT@',cc['root']));p.update(python=cc['runtime_prefix']+'/bin/python',extract_device='cuda');(packet/'cpu-science-plan.json').write_text(json.dumps(p,indent=2)+chr(10));(packet/'cpu-allocation-approval.json').write_bytes((r/'E009-only-scope.json').read_bytes())
    remote(r,n,"from pathlib import Path;Path('/tmp/e021-E009-consumer-v5').mkdir()")
    scp=['scp','-F',str(r/'bulk-ssh.conf')]
    for source,name in [(packet/x,x)for x in ['cpu-config.json','cpu-science-plan.json','cpu-allocation-approval.json']]+[(repo/'scripts/e021_portable_reuse_node.py','reuse.py')]:call(r,scp+[str(source),'e021-bulk-cpu:/tmp/e021-E009-consumer-v5/'+name])
    call(r,n['ssh']+['/usr/bin/python3 -u -I -B /tmp/e021-E009-consumer-v5/reuse.py --config /tmp/e021-E009-consumer-v5/cpu-config.json'],300)
    remote(r,n,'from pathlib import Path;Path('+repr(n['root']+'/helpers')+').mkdir()')
    for name in ['e021_portable_handoff.py','e021_portable_runtime_archive.py','e021_portable_gates.py','e009_common.py']:call(r,scp+[str(repo/'scripts'/name),'e021-bulk-cpu:'+n['root']+'/helpers/'+name])
    call(r,scp+[str(r/'cpu-recipe.json'),'e021-bulk-cpu:'+n['root']+'/cpu-recipe.json'])
    py=cc['runtime_prefix']+'/bin/python';helper=n['root']+'/helpers/e021_portable_handoff.py'
    queue(r,n,1,dict(name='fresh-owned-CPU-inventory',kind='gate',seconds=240,argv=[py,'-I','-B',n['root']+'/helpers/e021_portable_gates.py','inventory','--config',n['root']+'/config.json','--recipe',n['root']+'/cpu-recipe.json','--output',n['root']+'/gates/runtime-native.json']))
    wait(r,n,1,min(start+900,clock['deadline_epoch']))
    meta=read(r,g,g['root']+'/gates/runtime-preservation-file-bindings.json')
    for label,m,dest in [('bank',dict(kind='E021 verified transport v1',files=bank['files']),n['root']+'/work/units/E009-hybrid'),('runtime',dict(kind='E021 verified transport v1',files=meta['files']),n['root']+'/preserved-GPU-runtime')]:
        mp=r/('E009-handoff-'+label+'-manifest.json');mp.write_text(json.dumps(m,indent=2)+chr(10));transfer(r/'E009-consumer-nodes.json','gpu','cpu',mp,dest,'E009-'+label+'-v1',1800)
    code="import sys,json;from pathlib import Path;sys.path.insert(0,"+repr(n['root']+'/helpers')+");from e021_portable_runtime_archive import verify,binding as rb;r=Path("+repr(n['root'])+");d=r/'preserved-GPU-runtime';v=json.loads((d/'runtime-preservation.json').read_text());verify(d/'native-runtime.tar.gz',v['members']);t=Path('/srv/dl_binner/experiments/e021/portable-20261024T190419Z/cpu-staging-v3/gates/tiny-cached-native.json');z=json.loads(t.read_text());assert z['status']=='PASS_REAL_NATIVE_CACHED_TINY_BOTH_MODES'and len(z['records'])==12 and all(x['exit']==0 for x in z['records']);(r/'gates/verified-runtime-and-tiny.json').write_text(json.dumps({'status':'PASS','runtime_not_executed_on_CPU':True,'retained_archive':str(d/'native-runtime.tar.gz'),'archive_binding':rb(d/'native-runtime.tar.gz'),'manifest_binding':rb(d/'runtime-preservation.json'),'tiny':z})+chr(10))"
    queue(r,n,2,dict(name='verify-relocated-runtime-and-passed-tiny',kind='gate',seconds=600,argv=['/usr/bin/python3','-I','-B','-c',code]))
    queue(r,n,3,dict(name='actual-full-E009-bank-and-context-reader',kind='gate',seconds=600,argv=[py,'-I','-B',helper,'bank','--context','--plan',n['root']+'/science-plan.json','--output',n['root']+'/gates/E009-restored-bank.json']))
    wait(r,n,2,min(start+6000,clock['deadline_epoch']));wait(r,n,3,min(start+6600,clock['deadline_epoch']))
    proof=read(r,n,n['root']+'/gates/E009-restored-bank.json')
    if proof['status']!='PASS_ACTUAL_E009_BANK_READER'or not proof['context_arrays_read']:raise ValueError('Full native restored bank/context gate failed')
    put(r,g,g['root']+'/handoff-done.json',dict(CPU_bank_reader=proof['status'],paired_transport=True,CPU_root=n['root']))
    code="import json,hashlib;from pathlib import Path;r=Path("+repr(n['root'])+");files=[r/'gates/runtime-native.json',r/'gates/verified-runtime-and-tiny.json',r/'gates/E009-restored-bank.json',r/'reused-runtime-receipts.json',r/'logs/maintenance-restart-refused.json'];b=lambda p:dict(bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest());v=dict(all_native_gates_passed=True,watchdog_current=True,config=b(r/'config.json'),gate_files={str(p):b(p)for p in files},science_plan=str(r/'science-plan.json'),science_plan_binding=b(r/'science-plan.json'),gross_upper_USD=39.107882420652246,covered_by_welcome_credit=True,scope='Full E009 only; original joint criterion unmet');(r/'release.json').write_text(json.dumps(v,indent=2)+chr(10))"
    remote(r,n,code)
    for i,stage in enumerate(['train','embed','group','refine','export','graph-proof'],4):queue(r,n,i,dict(name='E009-'+stage,kind='science',unit='E009-hybrid',stage=stage,seconds=6000,argv=[py,'-I','-B',cc['repo']+'/scripts/e021_control.py','--plan',n['root']+'/science-plan.json','--unit','E009-hybrid','--stage',stage]))
    queue(r,n,10,dict(name='complete-E009-target-and-close',kind='gate',seconds=240,argv=[py,'-I','-B',helper,'cpu-target','--root',n['root'],'--plan',n['root']+'/science-plan.json']))
    cloud.put('E009-CPU-science-released.json',dict(epoch=time.time(),root=n['root'],archive_prefix=cc['archive_prefix'],scope='E009 only',six_stages_once=True,Mac_no_longer_required_for_fit_collection_shutdown=True))
    print('E009_CPU_SCIENCE_RELEASED_UNDER_NATIVE_SUPERVISION',flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--root',type=Path,required=True);a=p.parse_args()
    try:run(a.root)
    except BaseException as e:
        r=Path(a.root);(r/'E009-controller-failed.json').write_text(json.dumps(dict(epoch=time.time(),error=repr(e),no_retry=True))+chr(10));print('E009_HANDOFF_FAILED_NO_RETRY',repr(e),flush=True)
        if(r/'cpu-E009-consumer-start.json').exists()and not(r/'E009-CPU-science-released.json').exists():
            try:Cloud(r).stop()
            except Exception as stop_error:print('STOP_CONFIRMATION_REQUIRED',repr(stop_error),flush=True)
        raise
