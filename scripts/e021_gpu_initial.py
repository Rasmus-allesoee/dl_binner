#!/usr/bin/env python3
"""Inspect the existing GPU admission host, sync exact source and arm its held parent.

No package install, feature acquisition, science, cloud mutation or disk cleanup.
All old checkouts and inputs stay in place. The driver refuses insufficient actual
root/work space before setup, and retains commands/host identity in a fresh root.
"""
import argparse,datetime,getpass,hashlib,json,os,shutil,subprocess,sys,time
from pathlib import Path


def populate_plan(template,repo,root):
    """Bind the frozen science to explicit CUDA extraction and bounded worker only."""
    text=Path(template).read_text().replace('@REPO@',str(repo)).replace('@RUN_ROOT@',str(root));plan=json.loads(text)
    plan['extract_device']='cuda';plan['worker']=str(Path(repo)/'scripts/e021_gpu_worker.py')
    return plan


def main():
    """Run one fresh source/space/host bootstrap and test current-boot exit supervision."""
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--identity',type=Path,required=True);p.add_argument('--financial',type=Path,required=True);a=p.parse_args();ID=json.loads(a.identity.read_text());F=json.loads(a.financial.read_text());root=Path(ID['root']);repo=Path(ID['repo']);original=Path('/srv/dl_binner/repo')
    if sys.platform!='linux'or os.cpu_count()!=8 or not os.path.ismount('/srv/dl_binner'):raise ValueError('Existing Linux eight-CPU work mount required')
    usage=shutil.disk_usage('/srv/dl_binner');boot=shutil.disk_usage('/')
    if usage.free<57*1024**3 or boot.free<5*1024**3:raise ValueError('Measured root/work headroom insufficient; review cleanup before any storage request')
    root.mkdir(parents=True,exist_ok=False)
    for n in ['logs','gates','tmp','native-cache','work','payload']:(root/n).mkdir()
    (root/'identity.json').write_text(json.dumps(ID,indent=2)+'\n');(root/'financial-gate.json').write_text(json.dumps(F,indent=2)+'\n')
    def run(argv,cwd=original):
        p=subprocess.run([str(x)for x in argv],cwd=cwd,capture_output=True,text=True,timeout=180)
        with(root/'logs/initial.log').open('a')as f:f.write(json.dumps([str(x)for x in argv])+'\n'+p.stdout+p.stderr)
        print(p.stdout+p.stderr,flush=True);p.check_returncode();return p.stdout
    initial_source=run(['git','rev-parse','HEAD']).strip()
    if run(['git','status','--porcelain']).strip():raise ValueError('Primary checkout has local changes; never reset')
    run(['git','fetch','origin','e021-frozen-sequence-hybrid'])
    if run(['git','rev-parse','FETCH_HEAD']).strip()!=ID['source']:raise ValueError('Remote branch is not exact prepared source')
    repo.parent.mkdir(exist_ok=True);run(['git','worktree','add','--detach',repo,ID['source']])
    if run(['git','rev-parse','HEAD'],repo).strip()!=ID['source']or run(['git','status','--porcelain'],repo).strip():raise ValueError('Exact clean research checkout differs')
    if run(['git','rev-parse','HEAD']).strip()!=initial_source or run(['git','status','--porcelain']).strip():raise ValueError('Primary checkout changed')
    def bind(path):
        data=Path(path).read_bytes();return dict(bytes=len(data),sha256=hashlib.sha256(data).hexdigest())
    for name in ['candidate-lock.json','gpu-launch-lock.json']:
        lock=json.loads((repo/'experiments/E021-frozen-sequence-hybrid'/name).read_text())
        for key,v in lock['files'].items():
            if bind(repo/key)!=v:raise ValueError('Frozen source differs: '+key)
    mount=json.loads(run(['findmnt','-J','-T','/srv/dl_binner','-o','TARGET,SOURCE,FSTYPE,UUID,SIZE,OPTIONS']))
    uuid=mount['filesystems'][0]['uuid']
    if uuid!='f76283ed-60c4-4060-bd22-84c95f38d3fb':raise ValueError('Original work filesystem identity differs')
    pci=[]
    for v in Path('/sys/bus/pci/devices').glob('*/vendor'):
        if v.read_text().strip()=='0x10de':pci.append(dict(device=v.parent.name,vendor=v.read_text().strip()))
    mem=int(next(l.split()[1]for l in Path('/proc/meminfo').read_text().splitlines()if l.startswith('MemTotal:')))*1024
    if mem<29_000_000_000 or not pci:raise ValueError('N1 memory/NVIDIA device inventory unavailable')
    host=dict(user=getpass.getuser(),uid=os.getuid(),gid=os.getgid(),boot_id=Path('/proc/sys/kernel/random/boot_id').read_text().strip(),cpus=os.cpu_count(),physical_memory_bytes=mem,used_bytes=usage.used,free_bytes=usage.free,boot_free_bytes=boot.free,mount='/srv/dl_binner',mount_identity=mount,source=ID['source'],original_checkout_source=initial_source,new_research_checkout=str(repo),kernel=os.uname().release,NVIDIA_PCI=pci,checked_UTC=datetime.datetime.now(datetime.timezone.utc).isoformat())
    (root/'host.json').write_text(json.dumps(host,indent=2)+'\n')
    run(['du','-x','-k','--max-depth=2','/srv/dl_binner/experiments'])
    plan=populate_plan(repo/'experiments/E021-frozen-sequence-hybrid/native-plan-template.json',repo,root);(root/'science-plan.json').write_text(json.dumps(plan,indent=2)+'\n')
    sys.path.insert(0,str(repo/'scripts'));from e021_gpu_phase import configuration
    storage=repo/'experiments/E017-information-aware-grouping/storage-admission.json';bindings={str(q):bind(q)for q in [root/'science-plan.json',root/'financial-gate.json',repo/'experiments/E021-frozen-sequence-hybrid/reuse-lock.json',repo/'experiments/E021-frozen-sequence-hybrid/candidate-lock.json',repo/'experiments/E021-frozen-sequence-hybrid/gpu-launch-lock.json',repo/'experiments/E021-frozen-sequence-hybrid/protocol.json',storage]}
    cfg=configuration(ID,repo,usage.used,bindings);cfg['storage_authorization_sha256']=bind(storage)['sha256'];(root/'config.json').write_text(json.dumps(cfg,indent=2)+'\n')
    run(['sudo','-n','/usr/bin/python3','-I','-B',repo/'scripts/e021_gpu_arm.py','--config',root/'config.json'],repo)
    print('E021_GPU_HOST_SOURCE_AND_FRESH_SUPERVISION_READY',json.dumps(host),flush=True)

if __name__=='__main__':main()
