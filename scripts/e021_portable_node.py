#!/usr/bin/env python3
"""Own one portable E021 node's bounded tasks, supervision and compact return.

All tasks are recorded; scientific argv must match the frozen stage interface.
The Mac controller may disappear: absolute clocks, stale-live-peer detection,
idle limits, native exit watcher and provider STOP still bound charges. No retry,
cloud lifecycle mutation, feature fallback or scientific tuning occurs here.
"""
import argparse,csv,hashlib,json,os,shutil,signal,subprocess,sys,threading,time,urllib.parse,urllib.request
from pathlib import Path
sys.path.insert(0,str(Path(__file__).absolute().parent))
from e009_common import binding,write_json
from e009_owner import supervisor,Tee
from e009_controls import PhaseGuard
from e021_gpu_guard import GPUPhaseGuard
from e009_exit_watchdog import identity


def sample_gpu(model):
    """Read one actual approved GPU without loading a numerical library."""
    p=subprocess.run(['/usr/bin/nvidia-smi','--query-gpu=uuid,name,memory.total,memory.used','--format=csv,noheader,nounits'],check=True,capture_output=True,text=True,timeout=8);rows=list(csv.reader(p.stdout.strip().splitlines()))
    if len(rows)!=1 or len(rows[0])!=4:raise ValueError('Exactly one GPU required')
    uuid,name,total,used=[x.strip()for x in rows[0]]
    if model not in ['L4','T4']or not name.endswith(model)or not uuid.startswith('GPU-')or not total.isdigit()or not used.isdigit():raise ValueError('Approved GPU identity/counters differ')
    total,used=int(total)*1024**2,int(used)*1024**2
    if total<14*1024**3 or used>total:raise ValueError('GPU physical-memory contract failed')
    return dict(uuid=uuid,name=name,total_bytes=total,used_bytes=used)


def usage(cfg):
    """Count new work and boot filesystem use; do not hide setup/staging growth."""
    host=json.loads((Path(cfg['root'])/'host.json').read_text());work=shutil.disk_usage('/srv/dl_binner');boot=shutil.disk_usage('/')
    return dict(epoch=time.time(),boot_id=host['boot_id'],growth_bytes=max(0,work.used-host['work_used_bytes'])+max(0,boot.used-host['boot_used_bytes']),work_free_bytes=work.free,boot_free_bytes=boot.free,role=cfg['role'])


def peer_check(cfg,local,peer,now):
    """Refuse stale live-peer accounting or aggregate extra work above 32 GiB."""
    if peer.get('live')and now-peer['epoch']>180:raise TimeoutError('Live-peer accounting stale; stop rather than hide aggregate space')
    if local['growth_bytes']+peer.get('growth_bytes',0)>32*1024**3:raise MemoryError('Aggregate 32 GiB extra-work ceiling exceeded')
    if local['work_free_bytes']<25*1024**3 or local['boot_free_bytes']<1024**3:raise MemoryError('Node work/boot free-space reserve failed')


def write_status(root,value):
    """Expose atomic local progress and a compact best-effort guest attribute."""
    root=Path(root);v=dict(value,epoch=time.time());temp=root/'status.pending';temp.write_text(json.dumps(v)+'\n');temp.replace(root/'status.json')
    data=json.dumps(v).encode();req=urllib.request.Request('http://metadata.google.internal/computeMetadata/v1/instance/guest-attributes/e021-portable/status',data=data,method='PUT',headers={'Metadata-Flavor':'Google','Content-Type':'application/json'})
    try:
        with urllib.request.urlopen(req,timeout=3)as f:f.read(1024)
    except Exception as e:print('GUEST_ATTRIBUTE_UNAVAILABLE',str(e),flush=True)


def storage_upload(path,uri):
    """Upload one new compact object and stream readback with ephemeral metadata auth."""
    path=Path(path);b=binding(path);u=urllib.parse.urlsplit(uri)
    if u.scheme!='gs'or u.netloc!='dl-binner-archive-167650584170'or b['bytes']>2*1024**3:raise ValueError('Bounded private object required')
    def token():
        q=urllib.request.Request('http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/token',headers={'Metadata-Flavor':'Google'})
        with urllib.request.urlopen(q,timeout=8)as f:return json.load(f)['access_token']
    auth=token();query=urllib.parse.urlencode(dict(uploadType='resumable',name=u.path.lstrip('/'),ifGenerationMatch=0));url='https://storage.googleapis.com/upload/storage/v1/b/'+u.netloc+'/o?'+query
    q=urllib.request.Request(url,data=b'{}',method='POST',headers={'Authorization':'Bearer '+auth,'Content-Type':'application/json','X-Upload-Content-Length':str(b['bytes'])})
    with urllib.request.urlopen(q,timeout=15)as f:upload=f.headers['Location']
    with path.open('rb')as stream:
        q=urllib.request.Request(upload,data=stream,method='PUT',headers={'Authorization':'Bearer '+auth,'Content-Length':str(b['bytes']),'Content-Type':'application/octet-stream'})
        with urllib.request.urlopen(q,timeout=180)as f:obj=json.load(f)
    read='https://storage.googleapis.com/storage/v1/b/'+u.netloc+'/o/'+urllib.parse.quote(u.path.lstrip('/'),safe='')+'?alt=media&generation='+obj['generation'];q=urllib.request.Request(read,headers={'Authorization':'Bearer '+token()});h=hashlib.sha256();n=0
    with urllib.request.urlopen(q,timeout=180)as f:
        for chunk in iter(lambda:f.read(1024**2),b''):n+=len(chunk);h.update(chunk)
    if dict(bytes=n,sha256=h.hexdigest())!=b:raise ValueError('Private object readback differs')
    return dict(uri=uri,generation=obj['generation'],binding=b,readback_verified=True)


def scientific_argv(cfg,release,stage,unit):
    """Return the sole unchanged stage interface; no new schedule/model can enter."""
    if unit not in ['E009-hybrid','oral-hybrid']:raise ValueError('Unfrozen scientific unit')
    allowed=['extract']if cfg['role']=='gpu'else['train','embed','group','refine','export','graph-proof']
    if stage not in allowed:raise ValueError('Unapproved scientific stage for node role')
    plan=Path(release['science_plan']);p=json.loads(plan.read_text())
    if binding(plan)!=release['science_plan_binding']:raise ValueError('Frozen admitted plan differs')
    if cfg['role']=='gpu'and p['extract_device']!='cuda':raise ValueError('GPU extraction must be explicit')
    return [p['python'],'-I','-B',str(Path(cfg['repo'])/'scripts'/('e021_gpu_worker.py'if cfg['role']=='gpu'else'e021_control.py')),'--plan',str(plan),'--unit',unit,'--stage',stage]


def admission(cfg,release):
    """Verify actual source, current held watcher and all recorded native gate bytes."""
    root=Path(cfg['root']);watch=json.loads((root/'logs/watchdog-live-before-release.json').read_text())
    if release.get('all_native_gates_passed')is not True or release.get('watchdog_current')is not True or release.get('config')!=binding(root/'config.json'):raise ValueError('Native gates/config missing')
    if watch['decision']!='workflow alive'or watch['boot_id']!=Path('/proc/sys/kernel/random/boot_id').read_text().strip()or watch['expected_process']!=identity(os.getpid()):raise ValueError('Current boot/process watcher differs')
    head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=cfg['repo'],text=True).strip();dirty=subprocess.check_output(['git','status','--porcelain'],cwd=cfg['repo'],text=True).strip()
    if head!=cfg['source']or dirty:raise ValueError('Exact clean source differs')
    if len(release.get('gate_files',{}))<5:raise ValueError('Complete native gate receipt set required')
    for p,b in release['gate_files'].items():
        if binding(p)!=b:raise ValueError('Native gate evidence differs: '+p)
    if time.time()>cfg['node_deadline_epoch']-600 or release.get('gross_upper_USD',46)>45 or release.get('covered_by_welcome_credit')is not True:raise ValueError('Clock/cost/coverage admission differs')
    if cfg['role']=='gpu':
        gpu=sample_gpu(cfg['GPU']);live=json.loads((root/'logs/gpu-guard-live.json').read_text())
        if live['gpu_uuid']!=gpu['uuid']or live['guard_pid']!=os.getpid():raise ValueError('Live native GPU guard differs')
    return True


def completed(cfg,outcome):
    """Refuse a controller success claim without every exact scientific exit/artifact."""
    stages=['extract']if cfg['role']=='gpu'else['train','embed','group','refine','export','graph-proof']
    expected={(u,s)for u in ['E009-hybrid','oral-hybrid']for s in stages}
    got={(x.get('unit'),x.get('stage'))for x in outcome['stages']if x['kind']=='science'and x['status']=='SUCCESS'}
    if got!=expected:raise ValueError('Scientific completion exits incomplete')
    root=Path(cfg['root'])/'work/units'
    for u in ['E009-hybrid','oral-hybrid']:
        if cfg['role']=='gpu':
            m=json.loads((root/u/'frozen/bank.json').read_text())
            if m['status']!='COMPLETE'or m['kind']!='hybrid_bank':raise ValueError('Native bank incomplete')
            for name,b in m['members'].items():
                if binding(root/u/'frozen'/name)!=b:raise ValueError('Completed bank member differs')
        else:
            a=json.loads((root/u/'export/accounting.json').read_text());g=json.loads((root/u/'graph-proof.json').read_text())
            if set(a)!={'pre','old','post'}or g['status']!='PASS':raise ValueError('DNA/graph target missing')
    return True


def collect(cfg,outcome):
    """Seal native journals before exit; raw banks/runtime are explicitly retained."""
    root=Path(cfg['root']);ev=root/'sealed-evidence';ev.mkdir(exist_ok=False)
    for folder in ['logs','gates']:shutil.copytree(root/folder,ev/folder)
    for p in root.iterdir():
        if p.is_file()and p.suffix in ['.json','.py']:shutil.copyfile(p,ev/p.name)
    from e021_collect import pack
    work=root/'work'if cfg['role']=='cpu'else root/'empty-return-work';work.mkdir(exist_ok=True)
    result=pack(work,ev,root/'return',ceiling=cfg.get('return_cap_bytes',2*1024**3),allow_incomplete=not outcome.get('science_completed',False));uploads=[]
    for n in ['e021-evidence.tar.gz','e021-evidence.tar.gz.sha256','collection.json']:uploads.append(storage_upload(root/'return'/n,cfg['archive_prefix']+'/'+n))
    return dict(collection=result,uploads=uploads,raw_bank_runtime_not_backed_up_by_hash=True)


def run(config):
    """Run explicit ordered jobs; retain failure and stop on idle/deadline loss."""
    cfg=json.loads(Path(config).read_text());root=Path(cfg['root']);logs=root/'logs';jobs=root/'tasks';jobs.mkdir(exist_ok=True);sup=supervisor();env=sup.isolated_env(4)
    env.update(NUMBA_NUM_THREADS='4',NUMBA_CACHE_DIR=str(root/'numba-cache'),TMPDIR=str(root/'tmp'),NVIDIA_TF32_OVERRIDE='0',CUBLAS_WORKSPACE_CONFIG=':4096:8',HF_MODULES_CACHE=str(root/'model-module-cache'),HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1',TOKENIZERS_PARALLELISM='false')
    outcome=dict(status='FAILED',role=cfg['role'],source=cfg['source'],stages=[],science_completed=False);write_json(root/'started.json',dict(pid=os.getpid(),epoch=time.time()));deadline=cfg['node_deadline_epoch'];last=time.time();next_job=1;failed_since=None;done=threading.Event();error=[]
    def disk_watch():
        while not done.wait(5):
            try:
                u=usage(cfg);tmp=root/'usage.pending';tmp.write_text(json.dumps(u)+'\n');tmp.replace(root/'usage.json');peer=json.loads((root/'peer-usage.json').read_text());peer_check(cfg,u,peer,time.time())
            except BaseException as e:error.append(str(e));os.kill(os.getpid(),signal.SIGALRM);return
    guard=None
    try:
        host=json.loads((root/'host.json').read_text())
        if host['boot_id']!=Path('/proc/sys/kernel/random/boot_id').read_text().strip():raise ValueError('Current-boot host identity differs')
        seconds=deadline-time.time()
        guard=GPUPhaseGuard(root,seconds,sampler=lambda:sample_gpu(cfg['GPU']),wait_for_ready=True)if cfg['role']=='gpu'else PhaseGuard(root,seconds,growth_bytes=32*1024**3)
        with guard:
            threading.Thread(target=disk_watch,daemon=True).start();write_status(root,dict(status='HELD',role=cfg['role']))
            while True:
                if error:raise RuntimeError(error[-1])
                if(root/'abort.json').exists():raise RuntimeError('Controller abort; inspect retained failure')
                if(root/'finish.json').exists():
                    finish=json.loads((root/'finish.json').read_text());outcome['science_completed']=finish.get('science_completed')is True
                    if outcome['science_completed']:completed(cfg,outcome)
                    outcome['status']=finish['status'];break
                p=jobs/(str(next_job).zfill(4)+'.json')
                if not p.exists():
                    if time.time()-last>(900 if failed_since else 7200):raise TimeoutError('Native task queue idle/setup ceiling exhausted')
                    time.sleep(.2);continue
                task=json.loads(p.read_text());name=task['name'];kind=task['kind'];argv=task['argv']
                if Path(name).name!=name or not name or any(c not in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_'for c in name):raise ValueError('Unsafe task name')
                if kind=='science':
                    release=json.loads((root/'release.json').read_text())
                    admission(cfg,release)
                    if argv!=scientific_argv(cfg,release,task['stage'],task['unit']):raise ValueError('Scientific argv differs from fixed stage')
                elif kind not in ['setup','gate','transport','cleanup']:raise ValueError('Unknown task scope')
                write_status(root,dict(status='RUNNING',role=cfg['role'],stage=name,task=next_job));left=min(task.get('seconds',deadline-time.time()),deadline-time.time()-(600 if kind=='science'else 120))
                if left<1:raise TimeoutError('Original common/node clock unavailable')
                try:
                    result=sup.supervise(argv,logs/(name+'.log'),left,26_000_000_000,env,sample_root=os.getpid());record=dict(name=name,kind=kind,status='SUCCESS',resources=result)
                except BaseException as e:
                    record=dict(name=name,kind=kind,status='FAILED',error=repr(e));failed_since=time.time()
                if kind=='science':record.update(stage=task['stage'],unit=task['unit'])
                outcome['stages'].append(record);write_json(jobs/(str(next_job).zfill(4)+'.result.json'),record);next_job+=1;last=time.time()
                if record['status']=='FAILED':
                    write_status(root,dict(status='FAILED_HELD_FOR_RECORDED_RECOVERY',role=cfg['role'],stage=name))
                    if kind=='science':raise RuntimeError('Scientific stage failed; no automatic retry')
                else:failed_since=None;write_status(root,dict(status='HELD',role=cfg['role'],completed_stage=name))
    except BaseException as e:outcome['error']=repr(e)
    finally:done.set()
    outcome['guard_errors']=error;outcome['elapsed_since_first_VM_start']=time.time()-cfg['first_VM_start_epoch'];write_json(root/'node-result.json',outcome)
    try:
        with PhaseGuard(root,max(.001,deadline-time.time()),growth_bytes=32*1024**3):outcome['return']=collect(cfg,outcome)
    except BaseException as e:outcome['collection_error']=repr(e)
    write_json(root/'completion.json',outcome)
    try:storage_upload(root/'completion.json',cfg['archive_prefix']+'/completion.json')
    except BaseException as e:print('COMPLETION_UPLOAD_FAILED',repr(e),flush=True)
    write_status(root,dict(status=outcome['status'],role=cfg['role'],science_completed=outcome['science_completed'],collection_error=outcome.get('collection_error'),completion=binding(root/'completion.json')))
    return 0 if outcome['status'].startswith('SUCCESS')else 1

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--config',type=Path,required=True);a=p.parse_args();cfg=json.loads(a.config.read_text());root=Path(cfg['root'])
    with(root/'logs/parent-terminal.log').open('x')as f:
        old=sys.stdout,sys.stderr;sys.stdout=Tee(sys.stdout,f);sys.stderr=Tee(sys.stderr,f)
        try:code=run(a.config)
        finally:sys.stdout,sys.stderr=old
    raise SystemExit(code)
