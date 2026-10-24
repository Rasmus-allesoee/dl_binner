#!/usr/bin/env python3
"""Select and verify a distro-signed precompiled driver for the actual boot kernel.

No DKMS, unsigned module, security bypass, CUDA toolkit or reboot fallback. The
proposed exact top-level apt versions and signed archive identities are retained
before the controller separately schedules installation within the same clock.
"""
import argparse,json,os,re,subprocess,sys,time
from pathlib import Path


def query(root,output=None):
    """Inventory matching current-kernel packages; never install from this reader."""
    root=Path(root);kernel=os.uname().release
    def call(argv):return subprocess.run(argv,check=True,text=True,capture_output=True,timeout=90).stdout
    result=call(['apt-cache','search','--names-only','^linux-modules-nvidia-.*'+re.escape(kernel)+'$']);choices=[]
    for line in result.splitlines():
        name=line.split()[0];m=re.fullmatch(r'linux-modules-nvidia-(\d+)-server(-open)?-'+re.escape(kernel),name)
        if not m or int(m[1])<535:continue
        driver='nvidia-headless-no-dkms-'+m[1]+'-server'+(m[2]or'');packages={}
        for p in [name,driver,'nvidia-utils-'+m[1]+'-server','nvidia-compute-utils-'+m[1]+'-server']:
            policy=call(['apt-cache','policy',p]);candidate=next((l.split(':',1)[1].strip()for l in policy.splitlines()if l.strip().startswith('Candidate:')),None)
            if candidate in [None,'(none)']:break
            info=call(['apt-cache','show',p+'='+candidate])
            if re.search('Description[^\n]*transitional',info,re.I):break
            packages[p]=dict(version=candidate,policy=policy,archive_metadata=info)
        if len(packages)==4:
            install=['/usr/bin/sudo','-n','/usr/bin/apt-get','install','-y','--no-install-recommends']+[p+'='+x['version']for p,x in packages.items()]
            preview=call(['apt-get','--simulate','install','--no-install-recommends']+install[6:])
            if re.search(r'^Inst (?:dkms|nvidia-dkms)',preview,re.M):continue
            choices.append(dict(branch=int(m[1]),open=bool(m[2]),packages=packages,install_argv=install,solver_preview=preview))
    out=dict(status='PROPOSED_NOT_INSTALLED'if choices else'NO_CURRENT_KERNEL_SIGNED_MODULE',kernel=kernel,search=result,choices=choices)
    if choices:
        choice=sorted(choices,key=lambda x:(x['branch'],x['open']),reverse=True)[0];out['selected']=choice;out['install_argv']=choice['install_argv'];out['solver_preview']=choice['solver_preview']
    target=Path(output)if output else root/'gates/driver-proposal.json'
    with target.open('x')as f:f.write(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2),flush=True)
    if not choices:raise ValueError('No precompiled signed current-kernel driver; no fallback')


def verify(root,gpu):
    """Load only a signed current-kernel module and activate same-boot telemetry."""
    root=Path(root)
    def call(argv):
        p=subprocess.run(argv,text=True,capture_output=True,timeout=60)
        if p.returncode:raise RuntimeError('Native driver command failed '+repr(argv)+' exit='+str(p.returncode)+' stdout='+p.stdout+' stderr='+p.stderr)
        return p.stdout
    secure=call(['mokutil','--sb-state'])
    if 'SecureBoot enabled'not in secure:raise ValueError('Secure Boot must stay enabled')
    signer=call(['modinfo','-F','signer','nvidia']).strip();module=call(['modinfo','-n','nvidia']).strip()
    if not signer or'Canonical'not in signer or os.uname().release not in module:raise ValueError('Canonical current-kernel signed module required')
    call(['sudo','-n','modprobe','nvidia']);attempts=[];text=None
    for attempt in range(15):
        q=subprocess.run(['/usr/bin/nvidia-smi','--query-gpu=uuid,name,driver_version,memory.total,memory.used','--format=csv,noheader,nounits'],text=True,capture_output=True,timeout=8);attempts.append(dict(epoch=time.time(),exit=q.returncode,stdout=q.stdout,stderr=q.stderr))
        if q.returncode==0:text=q.stdout;break
        time.sleep(2)
    (root/'gates/driver-readiness-attempts.json').write_text(json.dumps(attempts,indent=2)+'\n')
    if text is None:raise RuntimeError('GPU readiness unavailable after bounded 30-second native probe: '+json.dumps(attempts))
    rows=[x.strip()for x in text.strip().split(',')]
    if len(rows)!=5 or not rows[1].endswith(gpu):raise ValueError('Actual approved GPU differs')
    result=dict(status='PASS',kernel=os.uname().release,secure_boot=secure,signer=signer,module=module,nvidia_smi=text,dpkg=call(['dpkg-query','-W','-f','${Package}\t${Version}\n','*nvidia*']),epoch=time.time())
    (root/'gates/driver-verified.json').write_text(json.dumps(result,indent=2)+'\n');(root/'gpu-ready.json').write_text(json.dumps(dict(boot_id=Path('/proc/sys/kernel/random/boot_id').read_text().strip(),gpu_uuid=rows[0]))+'\n');print(json.dumps(result,indent=2),flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('operation',choices=['query','verify']);p.add_argument('--root',type=Path,required=True);p.add_argument('--gpu',choices=['L4','T4']);p.add_argument('--output',type=Path);a=p.parse_args();(query(a.root,a.output)if a.operation=='query'else verify(a.root,a.gpu))
