#!/usr/bin/env python3
"""Own one independent, held E029 GPU qualification and bounded private return.

Provider creation/deletion is outside this worker. It reuses an inert hash-bound
CUDA prefix, installs only the current product into an owned linked prefix, and
compares 128 original views. No fit or full community feature extraction exists.
"""
import argparse,hashlib,json,os,shutil,subprocess,sys,tarfile,time,urllib.parse,urllib.request
from pathlib import Path
sys.path.insert(0,str(Path(__file__).absolute().parent))
from e024_coverage import binding,write
from e021_control_json import publish
from e009_owner import supervisor
from e009_controls import PhaseGuard
from e009_exit_watchdog import identity
from e021_portable_node import storage_upload


def progress(root,stage):
    """Atomically replace disposable progress and publish a best-effort guest attribute."""
    data=json.dumps(dict(stage=stage,epoch=time.time())).encode();root=Path(root)
    private=root/('.status-'+str(time.time_ns()))
    with private.open('xb')as f:f.write(data);f.flush();os.fsync(f.fileno())
    os.replace(private,root/'status.json')
    req=urllib.request.Request('http://metadata.google.internal/computeMetadata/v1/instance/guest-attributes/e029-gpu/status',data=data,method='PUT',headers={'Metadata-Flavor':'Google','Content-Type':'application/json'})
    try:
        with urllib.request.urlopen(req,timeout=3)as f:f.read(1024)
    except Exception as exc:print('GPU_PROGRESS_UPLOAD_UNAVAILABLE',repr(exc),flush=True)


def token():
    """Read ephemeral attached-service auth in memory without credential copies."""
    req=urllib.request.Request('http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/token',headers={'Metadata-Flavor':'Google'})
    with urllib.request.urlopen(req,timeout=10)as f:return json.load(f)['access_token']


def download(asset,destination):
    """Download only a generation-bound admitted private object and verify its SHA256."""
    u=urllib.parse.urlsplit(asset['uri']);p=Path(destination)
    if u.scheme!='gs'or u.netloc!='dl-binner-archive-167650584170'or p.exists():raise ValueError('Fresh approved private asset required')
    url='https://storage.googleapis.com/storage/v1/b/'+u.netloc+'/o/'+urllib.parse.quote(u.path.lstrip('/'),safe='')+'?alt=media&generation='+asset['generation']
    req=urllib.request.Request(url,headers={'Authorization':'Bearer '+token()});h=hashlib.sha256();size=0
    with urllib.request.urlopen(req,timeout=120)as f,p.open('xb')as out:
        for b in iter(lambda:f.read(1024**2),b''):
            size+=len(b)
            if size>asset['binding']['bytes']:raise ValueError('Oversized private asset')
            out.write(b);h.update(b)
    if dict(bytes=size,sha256=h.hexdigest())!=asset['binding']:raise ValueError('Private asset checksum differs')
    return dict(status='PASS',**asset)


def unpack_runtime(archive,manifest,engineering=False):
    """Restore every original runtime member at its exact original absolute prefix."""
    from e021_portable_runtime_archive import verify,inventory
    m=json.loads(Path(manifest).read_text());prefix=Path(m['source_prefix'])
    if (not prefix.is_relative_to('/srv/dl_binner/experiments/e021/')and not(engineering and prefix.is_relative_to(Path(__import__('tempfile').gettempdir()))))or prefix.exists()or m['archive']!=binding(archive):raise ValueError('Original fresh runtime prefix/bytes required')
    verify(archive,m['members']);prefix.mkdir(parents=True)
    links=[]
    with tarfile.open(archive,'r:gz')as a:
        for member in a:
            path=Path(member.name)
            if path.is_absolute()or'..'in path.parts:raise ValueError('Unsafe runtime member')
            target=prefix/path;target.parent.mkdir(parents=True,exist_ok=True)
            if member.isfile():
                with a.extractfile(member)as src,target.open('xb')as dst:shutil.copyfileobj(src,dst)
                target.chmod(member.mode&0o777)
            elif member.issym():links.append((target,member.linkname))
            else:raise ValueError('Unexpected runtime type')
    for target,value in links:
        resolved=(target.parent/value).resolve()if not Path(value).is_absolute()else Path(value).resolve()
        if not resolved.is_relative_to(prefix):raise ValueError('Restored alias escapes original prefix')
        target.symlink_to(value)
    actual,total=inventory(prefix)
    if actual!=m['members']or total!=m['logical_regular_bytes']:raise ValueError('Restored runtime bytes/aliases differ')
    return dict(status='PASS_ALL_RESTORED_RUNTIME_BYTES_NOT_YET_NATIVE',prefix=str(prefix),regular_bytes=total,members=len(actual))


def collect(root,cfg,result):
    """Seal only compact closed evidence, verify every member, upload/read back privately."""
    ev=root/'sealed-evidence';ev.mkdir(exist_ok=False)
    for folder in ['logs','gates','probe','gpu-monitor']:
        if(root/folder).exists():shutil.copytree(root/folder,ev/folder)
    for n in ['config.json','host.json','started.json','release.json','cohort-manifest.json','runtime-native.json','node-result.json']:
        if(root/n).exists():shutil.copyfile(root/n,ev/n)
    members={str(p.relative_to(ev)):binding(p)for p in ev.rglob('*')if p.is_file()}
    if sum(x['bytes']for x in members.values())>256*1024**2 or len(members)>2000:raise ValueError('Compact qualification evidence exceeds cap')
    write(ev/'inventory.json',dict(members=members,large_model_runtime_not_in_return=True));archive=root/'e029-gpu-evidence.tar.gz'
    with tarfile.open(archive,'w:gz')as a:
        for p in sorted(ev.rglob('*')):
            if p.is_symlink():raise ValueError('Evidence links refused')
            if p.is_file():a.add(p,arcname=str(p.relative_to(ev)),recursive=False)
    if archive.stat().st_size>256*1024**2:raise ValueError('Compressed qualification cap exceeded')
    seen=set()
    with tarfile.open(archive)as a:
        for member in a:
            if not member.isfile()or member.name in seen:raise ValueError('Malformed compact return')
            seen.add(member.name)
            if member.name=='inventory.json':continue
            h=hashlib.sha256();size=0
            with a.extractfile(member)as f:
                for b in iter(lambda:f.read(1024**2),b''):size+=len(b);h.update(b)
            if members[member.name]!=dict(bytes=size,sha256=h.hexdigest()):raise ValueError('Compact member checksum differs')
    if seen!=set(members)|{'inventory.json'}:raise ValueError('Compact member inventory incomplete')
    return dict(status='PASS',archive=binding(archive),regular_members=len(seen),every_member_verified=True,private_readback=storage_upload(archive,cfg['archive_prefix']+'/e029-gpu-evidence.tar.gz'))


def run(config):
    """Hold for current watcher/credit release, then serially setup, qualify and collect."""
    cfg=json.loads(Path(config).read_text());root=Path(cfg['root']);repo=Path(cfg['repo']);deadline=cfg['node_deadline_epoch'];sup=supervisor();env=sup.isolated_env(4)
    env.update(TMPDIR=str(root/'tmp'),NUMBA_NUM_THREADS='4',NVIDIA_TF32_OVERRIDE='0',CUBLAS_WORKSPACE_CONFIG=':4096:8',HF_MODULES_CACHE=str(root/'model-module-cache'),HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1',TOKENIZERS_PARALLELISM='false')
    write(root/'started.json',dict(pid=os.getpid(),identity=identity(os.getpid()),epoch=time.time()))
    progress(root,'HELD')
    result=dict(status='FAILED',stage='HELD',stages=[],source=cfg['source'],full_community_extraction=False,scientific_fits=0)
    def command(label,argv):
        left=deadline-time.time()-300
        if left<30:raise TimeoutError('Original GPU clock cannot admit another stage')
        progress(root,label)
        try:v=sup.supervise(list(map(str,argv)),root/'logs'/(label+'.log'),left,26000000000,env,sample_root=os.getpid())
        except BaseException:
            p=root/'logs'/(label+'.exit.json');result['stages'].append(dict(stage=label,result=json.loads(p.read_text())if p.exists()else dict(exit_code=None)));raise
        result['stages'].append(dict(stage=label,result=v))
    try:
        with PhaseGuard(root,deadline-time.time()-300,reserve_bytes=10*1024**3,growth_bytes=20*1024**3)as guard:
            while not(root/'release.json').exists():
                if time.time()>cfg['start_epoch']+900:raise TimeoutError('GPU held release unavailable')
                time.sleep(.2)
            release=json.loads((root/'release.json').read_text());watch=json.loads((root/'logs/watchdog-live-before-release.json').read_text())
            if release['config']!=binding(config)or not release['credit_covered']or not release['provider_STOP_verified']or watch['expected_process']!=identity(os.getpid())or watch['boot_id']!=Path('/proc/sys/kernel/random/boot_id').read_text().strip():raise ValueError('Fresh current-boot GPU admission differs')
            f=cfg['financial_gate']
            if f['real_money_authorized']is not False or f['coverage_status']!='PASS_FOR_SPECIFIED_ORDINARY_FIRST_PARTY_PRODUCTS_ONLY'or time.time()-f['checked_epoch']>7200 or time.time()-f['credit_checked_epoch']>7200 or f['estimated_complete_gross_USD']>f['ceiling_USD']or cfg['provider_deadline_epoch']>=min(f['credit_valid_until_epoch'],f['storage_valid_until_epoch']):raise ValueError('Original fresh credit/scope/retention gate differs')
            progress(root,'restoring-verified-assets')
            assets=cfg['assets'];receipts={}
            for key,asset in assets.items():receipts[key]=download(asset,root/key)
            write(root/'gates/transports.json',receipts)
            write(root/'cohort-manifest.json',json.loads((root/'manifest.json').read_text()))
            m=json.loads((root/'cohort-manifest.json').read_text())
            if m['cohort']!=binding(root/'cohort.json'):raise ValueError('Frozen cohort differs')
            restored=unpack_runtime(root/'native-runtime.tar.gz',root/'runtime-preservation.json');write(root/'gates/runtime-restored.json',restored);base=restored['prefix']
            model=root/'model';model.mkdir()
            with tarfile.open(root/'model.tar.gz')as a:
                for member in a:
                    if not member.isfile()or Path(member.name).name!=member.name:raise ValueError('Only declared regular model files allowed')
                    a.extract(member,model,filter='data')
            command('driver-refresh',['sudo','-n','apt-get','update'])
            command('driver-query',['/usr/bin/python3','-I','-B',repo/'scripts/e021_portable_driver.py','query','--root',root])
            proposal=json.loads((root/'gates/driver-proposal.json').read_text());command('driver-install',proposal['install_argv'])
            command('driver-native',['/usr/bin/python3','-I','-B',repo/'scripts/e021_portable_driver.py','verify','--root',root,'--gpu',cfg['GPU']])
            command('install-own-package',[Path(base)/'bin/python','-I','-B',repo/'scripts/e019_runtime.py','create','--base',base,'--destination',root/'env','--wheel',root/'dl_binner-0.1.0.dev9-py3-none-any.whl','--output',root/'gates/package-install.json'])
            py=root/'env/bin/python'
            command('native-runtime',[py,'-I','-B',repo/'scripts/e029_gpu_runtime.py','--base',base,'--recipe',root/'gpu-recipe.json','--candidate-lock',repo/'experiments/E029-certifiable-joint-retrieval/candidate-lock.json','--runtime-manifest',root/'runtime-preservation.json','--output',root/'runtime-native.json'])
            command('native-128-view-qualification',[py,'-I','-B',repo/'scripts/e029_gpu_probe.py','--model',model,'--cohort',root/'cohort.json','--manifest',root/'cohort-manifest.json','--output',root/'probe','--gpu',cfg['GPU'],'--deadline',deadline-300])
            result.update(status='SUCCESS',probe_admitted=True,admission=binding(root/'probe/admission.json'))
            with (root/'logs/disk-samples.jsonl').open('x')as stream:
                for z in guard.observations:stream.write(json.dumps(z)+'\n')
            result['disk_samples']=binding(root/'logs/disk-samples.jsonl')
    except BaseException as exc:result['error']=repr(exc)
    result['elapsed_from_VM_start_seconds']=time.time()-cfg['start_epoch'];write(root/'node-result.json',result)
    try:
        with PhaseGuard(root,max(.001,deadline-time.time()),reserve_bytes=10*1024**3,growth_bytes=20*1024**3):result['collection']=collect(root,cfg,result)
    except BaseException as exc:result.update(status='FAILED',collection_error=repr(exc))
    result['finished_epoch']=time.time();progress(root,result['status']);publish(result,root/'completion.json')
    try:storage_upload(root/'completion.json',cfg['archive_prefix']+'/completion.json')
    except BaseException as exc:print('GPU_COMPLETION_DELIVERY_FAILED',repr(exc),flush=True);return 1
    return 0 if result['status']=='SUCCESS'else 1


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--config',type=Path,required=True);a=p.parse_args();sys.exit(run(a.config))
