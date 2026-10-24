#!/usr/bin/env python3
"""Prepare one exact clean source and held queue on an approved mounted node.

Original-node access uses its existing read-only Git key. The temporary node
consumes a hash-verified shallow source packet without any copied credentials.
No dependency installation, acquisition or scientific job is released here.
"""
import argparse,getpass,hashlib,json,os,shutil,subprocess,sys,tarfile,time
from pathlib import Path


def run(config,archive=None,archive_sha=None):
    """Bind current host/source/payloads and arm its process-specific exit watcher."""
    cfg=json.loads(Path(config).read_text());root=Path(cfg['root']);repo=Path(cfg['repo']);role=cfg['role']
    if root.exists()or not os.path.ismount('/srv/dl_binner'):raise ValueError('Fresh mounted phase root required')
    root.mkdir(parents=True,exist_ok=False)
    for n in ['payload','logs','gates','tmp','work']:(root/n).mkdir()
    def command(argv,cwd=None):
        p=subprocess.run(list(map(str,argv)),cwd=cwd,text=True,capture_output=True,timeout=180)
        with(root/'logs/prepare.log').open('a')as f:f.write(json.dumps(list(map(str,argv)))+'\n'+p.stdout+p.stderr)
        print(p.stdout+p.stderr,flush=True);p.check_returncode();return p.stdout
    if role=='gpu':
        if archive is None or hashlib.sha256(Path(archive).read_bytes()).hexdigest()!=archive_sha:raise ValueError('Exact source packet required')
        repo.mkdir(parents=True,exist_ok=False)
        with tarfile.open(archive)as a:
            for m in a:
                p=Path(m.name)
                if p.is_absolute()or'..'in p.parts or not(m.isfile()or m.isdir()):raise ValueError('Source packet path/member refused')
            a.extractall(repo,filter='data')
        host=json.loads(Path('/srv/dl_binner/initial-host.json').read_text());payload=Path('/srv/dl_binner')
    else:
        original=Path('/srv/dl_binner/repo');head=command(['git','rev-parse','HEAD'],original).strip()
        if command(['git','status','--porcelain'],original).strip():raise ValueError('Primary checkout dirty; never reset')
        command(['git','fetch','origin','e021-frozen-sequence-hybrid'],original)
        if command(['git','rev-parse','FETCH_HEAD'],original).strip()!=cfg['source']:raise ValueError('Exact prepared branch differs')
        repo.parent.mkdir(exist_ok=True);command(['git','worktree','add','--detach',repo,cfg['source']],original)
        if command(['git','rev-parse','HEAD'],original).strip()!=head or command(['git','status','--porcelain'],original).strip():raise ValueError('Primary checkout changed')
        mount=json.loads(command(['findmnt','-J','-T','/srv/dl_binner','-o','TARGET,SOURCE,FSTYPE,UUID,OPTIONS']))
        if mount['filesystems'][0]['uuid']!='f76283ed-60c4-4060-bd22-84c95f38d3fb':raise ValueError('Original work UUID differs')
        host=json.loads(Path('/tmp/cpu-baseline.json').read_text());host.update(boot_id=Path('/proc/sys/kernel/random/boot_id').read_text().strip(),user=getpass.getuser(),cpus=os.cpu_count(),kernel=os.uname().release,mount=mount,epoch=time.time(),primary_source=head);payload=Path('/tmp')
    if command(['git','rev-parse','HEAD'],repo).strip()!=cfg['source']or command(['git','status','--porcelain'],repo).strip():raise ValueError('Exact clean native source differs')
    if os.cpu_count()!=8 or shutil.disk_usage('/srv/dl_binner').free<57*1024**3 or shutil.disk_usage('/').free<5*1024**3:raise ValueError('Actual CPU/work/boot inventory failed')
    for name in ['candidate-lock.json','gpu-launch-lock.json','portable-launch-lock.json']:
        lock=json.loads((repo/'experiments/E021-frozen-sequence-hybrid'/name).read_text())
        for key,b in lock['files'].items():
            p=repo/key;data=p.read_bytes()
            if p.is_symlink()or dict(bytes=len(data),sha256=hashlib.sha256(data).hexdigest())!=b:raise ValueError('Frozen source differs: '+key)
    recipe=json.loads(Path('/tmp/'+role+'-recipe.json').read_text())
    for key in ['micromamba','project_wheel']:
        item=recipe[key];p=payload/Path(item['path']).name;data=p.read_bytes()
        if dict(bytes=len(data),sha256=hashlib.sha256(data).hexdigest())!={k:item[k]for k in ['bytes','sha256']}:raise ValueError('Payload byte mismatch')
        shutil.copyfile(p,root/'payload'/p.name)
    for name,v in [('config.json',cfg),('host.json',host),('runtime-recipe.json',recipe),('peer-usage.json',dict(live=False,epoch=time.time(),growth_bytes=0,reason='Both queues held; peer measurement required before setup jobs'))]:(root/name).write_text(json.dumps(v,indent=2)+'\n')
    command(['sudo','-n','/usr/bin/python3','-I','-B',repo/'scripts/e021_portable_arm.py','--config',root/'config.json'],repo)
    print('E021_PORTABLE_HELD_NODE_READY',role,str(root),flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--config',type=Path,required=True);p.add_argument('--archive',type=Path);p.add_argument('--archive-sha');a=p.parse_args();run(a.config,a.archive,a.archive_sha)
