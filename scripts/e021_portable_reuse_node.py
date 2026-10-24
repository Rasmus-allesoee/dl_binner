#!/usr/bin/env python3
"""Start a fresh supervised node while reusing verified complete owned setup.

Never installs, recopies an environment, formats a disk, regenerates inputs or
replays science. Each boot gets new config/source/runtime identity and watcher.
Fixed peer reservations divide the unchanged 32 GiB aggregate budget explicitly;
they are upper bounds, not a claim that the other node is stopped or measured live.
"""
import argparse,csv,hashlib,json,os,shutil,subprocess,sys,tarfile,time
from pathlib import Path


def readiness(text,model,boot):
    """Bind one actual current-boot GPU before the waiting device guard is armed."""
    rows=list(csv.reader(text.strip().splitlines()))
    if len(rows)!=1 or len(rows[0])!=4:raise ValueError('Exactly one GPU required')
    uuid,name,total,used=[x.strip()for x in rows[0]]
    if (model not in ['L4','T4']or not name.endswith(model)or not uuid.startswith('GPU-')
        or not total.isdigit()or not used.isdigit()or int(total)<14*1024
        or int(used)>14*1024):raise ValueError('Fresh GPU identity/memory differs')
    return dict(boot_id=boot,gpu_uuid=uuid)


def start(config):
    """Verify frozen source and prior setup receipts, then arm a fresh held parent."""
    cfg=json.loads(Path(config).read_text());root=Path(cfg['root']);repo=Path(cfg['repo']);old=Path(cfg['reuse_root']);root.mkdir(parents=True,exist_ok=False)
    for n in ['logs','gates','tmp','work','payload']:(root/n).mkdir()
    def call(argv,cwd=None):
        p=subprocess.run(list(map(str,argv)),cwd=cwd,capture_output=True,text=True,timeout=180)
        with(root/'logs/reuse-prepare.log').open('a')as f:f.write(json.dumps(list(map(str,argv)))+'\n'+p.stdout+p.stderr)
        print(p.stdout+p.stderr,flush=True);p.check_returncode();return p.stdout
    if not repo.exists():
        if cfg['role']!='gpu':raise ValueError('Passed exact CPU source worktree missing; no fetch fallback')
        archive=Path(cfg['source_archive']);data=archive.read_bytes()
        if hashlib.sha256(data).hexdigest()!=cfg['source_archive_sha256']:raise ValueError('New clean source packet differs')
        repo.mkdir(parents=True,exist_ok=False)
        with tarfile.open(archive)as a:
            for m in a:
                p=Path(m.name)
                if p.is_absolute()or'..'in p.parts or not m.isfile():raise ValueError('Only regular source packet members allowed')
            a.extractall(repo,filter='data')
    if call(['git','rev-parse','HEAD'],repo).strip()!=cfg['source']or call(['git','status','--porcelain'],repo).strip():raise ValueError('Exact clean research source differs')
    for name in ['candidate-lock.json','gpu-launch-lock.json','portable-launch-lock.json']:
        lock=json.loads((repo/'experiments/E021-frozen-sequence-hybrid'/name).read_text())
        for key,b in lock['files'].items():
            p=repo/key;data=p.read_bytes()
            if p.is_symlink()or dict(bytes=len(data),sha256=hashlib.sha256(data).hexdigest())!=b:raise ValueError('Frozen source differs: '+key)
    prior=json.loads((old/'runtime-installed.json').read_text());inventory=json.loads((old/'gates/runtime-native.json').read_text())
    if prior['status']!='INSTALLED_NOT_NATIVE_GATE_ADMITTED'or inventory['status']!='PASS'or prior['prefix']!=cfg['runtime_prefix']or inventory['prefix']!=cfg['runtime_prefix']:raise ValueError('Passed complete exact runtime missing; no fallback')
    py=Path(cfg['runtime_prefix'])/'bin/python';call([py,'-I','-B','-c','import sys,torch;assert sys.version_info[:3]==(3,10,15);print(sys.executable,sys.prefix,torch.__version__)'])
    host=json.loads((old/'host.json').read_text());host.update(boot_id=Path('/proc/sys/kernel/random/boot_id').read_text().strip(),kernel=os.uname().release,epoch=time.time());mount=json.loads(call(['findmnt','-J','-T','/srv/dl_binner','-o','TARGET,SOURCE,FSTYPE,UUID,OPTIONS']))
    expected='f76283ed-60c4-4060-bd22-84c95f38d3fb'if cfg['role']=='cpu'else'e2a3d7a2-268b-4059-a57e-7f73484c2656'
    if not os.path.ismount('/srv/dl_binner')or mount['filesystems'][0]['uuid']!=expected:raise ValueError('Existing mounted filesystem differs')
    host['mount']=mount
    bindings={str(p):dict(bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest())for p in [old/'runtime-installed.json',old/'gates/runtime-native.json',old/'wheel-native-metadata.json']}
    peer=dict(kind='FIXED_PEER_RESERVATION',live=False,growth_bytes=cfg['peer_reservation_bytes'],epoch=time.time(),meaning='Conservative peer hard-cap allocation, not live telemetry or stopped-state assertion; both own caps sum to 32 GiB')
    for name,value in [('config.json',cfg),('host.json',host),('peer-usage.json',peer),('reused-runtime-receipts.json',dict(status='PASS',files=bindings,old_prefix=cfg['runtime_prefix'],no_reinstall=True,no_recopy=True))]:(root/name).write_text(json.dumps(value,indent=2)+'\n')
    if cfg['role']=='gpu':
        value=call(['/usr/bin/nvidia-smi','--query-gpu=uuid,name,memory.total,memory.used','--format=csv,noheader,nounits'])
        ready=readiness(value,cfg['GPU'],host['boot_id'])
        (root/'gpu-ready.json').write_text(json.dumps(ready)+'\n')
        (root/'gates/fresh-native-GPU-readiness.json').write_text(json.dumps(dict(status='PASS',native_query=value,**ready))+'\n')
    # Stage all predeclared JSON controls before arming; source/clock fields stay explicit.
    for name in ['science-plan.json','allocation-approval.json']:
        src=Path(config).parent/(cfg['role']+'-'+name)
        if src.exists():shutil.copyfile(src,root/name)
    call(['sudo','-n','/usr/bin/python3','-I','-B',repo/'scripts/e021_portable_arm.py','--config',root/'config.json'])
    if cfg['role']=='gpu':
        live=json.loads((root/'logs/gpu-guard-live.json').read_text())
        watch=json.loads((root/'logs/supervision.json').read_text())
        if live['gpu_uuid']!=ready['gpu_uuid']or live['guard_pid']!=watch['process']['pid']:
            raise ValueError('Fresh parent device guard is not live on the admitted GPU')
        (root/'gates/current-boot-device-guard.json').write_text(json.dumps(dict(status='PASS',telemetry=live,watchdog=watch))+'\n')
    print('E021_REUSED_HELD_NODE_READY',json.dumps(cfg),flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--config',type=Path,required=True);a=p.parse_args();start(a.config)
