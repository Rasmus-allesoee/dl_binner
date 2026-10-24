#!/usr/bin/env python3
"""Inventory a new approved worker and mount only its verified empty 64 GiB disk.

Never formats, resizes or detaches an original disk. The host baseline is captured
before source/runtime staging so all subsequent boot/work growth remains counted.
"""
import argparse,getpass,json,os,pwd,shutil,subprocess,time
from pathlib import Path


def mount(name,user,device_name):
    """Refuse existing signatures and initialize the sole new experiment disk."""
    if os.geteuid()!=0 or not name.startswith('e021-portable-20261024-')or name[-1]not in 'bcf':raise ValueError('Approved new worker root bootstrap only')
    if device_name not in [name+'-work','persistent-disk-1']:raise ValueError('Explicit control-plane work-device alias required')
    account=pwd.getpwnam(user);disk=Path('/dev/disk/by-id/google-'+device_name)
    def call(argv,check=True):return subprocess.run(argv,check=check,text=True,capture_output=True,timeout=90)
    if not disk.exists()or os.path.ismount('/srv/dl_binner'):raise ValueError('Fresh named work device required')
    ls=json.loads(call(['lsblk','-J','-b','-o','NAME,SIZE,TYPE,FSTYPE,MOUNTPOINT',str(disk)]).stdout)['blockdevices']
    if len(ls)!=1 or ls[0]['size']!=64*1024**3 or ls[0]['type']!='disk'or ls[0].get('fstype')or ls[0].get('children')or ls[0].get('mountpoint'):raise ValueError('Empty exact new 64 GiB disk required')
    probe=call(['blkid',str(disk)],check=False)
    if probe.returncode!=2:raise ValueError('Existing/unknown filesystem signature refused')
    call(['mkfs.ext4','-m','0','-L','e021-work',str(disk)]);Path('/srv/dl_binner').mkdir(exist_ok=True);call(['mount','-o','nosuid,nodev',str(disk),'/srv/dl_binner']);os.chown('/srv/dl_binner',account.pw_uid,account.pw_gid)
    work=shutil.disk_usage('/srv/dl_binner');boot=shutil.disk_usage('/');mem=int(next(l.split()[1]for l in Path('/proc/meminfo').read_text().splitlines()if l.startswith('MemTotal:')))*1024
    if os.cpu_count()!=8 or mem<29_000_000_000 or work.free<57*1024**3:raise ValueError('Worker CPU/RAM/free-space inventory failed')
    host=dict(user=user,uid=account.pw_uid,gid=account.pw_gid,boot_id=Path('/proc/sys/kernel/random/boot_id').read_text().strip(),cpus=os.cpu_count(),physical_memory_bytes=mem,kernel=os.uname().release,work_used_bytes=work.used,work_free_bytes=work.free,boot_used_bytes=boot.used,boot_free_bytes=boot.free,epoch=time.time(),new_device=str(disk),control_plane_resource=name+'-work',control_plane_device_name=device_name,mount=json.loads(call(['findmnt','-J','-T','/srv/dl_binner','-o','TARGET,SOURCE,FSTYPE,UUID,OPTIONS']).stdout))
    if host['mount']['filesystems'][0]['uuid']=='f76283ed-60c4-4060-bd22-84c95f38d3fb':raise ValueError('Original disk refused')
    p=Path('/srv/dl_binner/initial-host.json');p.write_text(json.dumps(host,indent=2)+'\n');os.chown(p,account.pw_uid,account.pw_gid);print(json.dumps(host,indent=2),flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--name',required=True);p.add_argument('--user',required=True);p.add_argument('--device-name',required=True);a=p.parse_args();mount(a.name,a.user,a.device_name)
