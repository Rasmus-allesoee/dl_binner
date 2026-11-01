#!/usr/bin/env python3
"""Release only verified redundant native transport archives for E030 headroom.

All extracted science, original inputs, private generations, environments and
journals remain. No recursive cleanup, GCS mutation or accepted evidence deletion
exists. The caller runs before the new work baseline, within the same VM clock.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time


def release(plan,output,gcloud='/snap/bin/gcloud',engineering=False):
    """Require current private generation/whole-object identity, SHA and no users."""
    if not engineering and os.geteuid()!=0:raise ValueError('Root read access to all process descriptors required')
    cfg=json.loads(Path(plan).read_text());result=[]
    for item in cfg['archives']:
        if shutil.disk_usage('/srv/dl_binner' if not engineering else Path(output).parent).free>=cfg['target_free_bytes']:break
        p=Path(item['path'])
        if not p.exists():result.append(dict(path=str(p),status='already_absent_no_action'));continue
        if p.is_symlink() or not p.is_file() or not (engineering or p.is_relative_to('/srv/dl_binner/experiments')):raise ValueError('Unapproved transport path/type')
        v=p.stat();identity=(v.st_dev,v.st_ino)
        if not engineering:
            for process in Path('/proc').iterdir():
                if not process.name.isdigit():continue
                try:
                    for fd in (process/'fd').iterdir():
                        try:st=fd.stat()
                        except FileNotFoundError:continue
                        if (st.st_dev,st.st_ino)==identity:raise ValueError('Transport archive has a current open user')
                except FileNotFoundError:continue
        h=hashlib.sha256();md5=hashlib.md5();size=0
        with p.open('rb') as f:
            for b in iter(lambda:f.read(4*1024**2),b''):h.update(b);md5.update(b);size+=len(b)
        if dict(bytes=size,sha256=h.hexdigest())!=item['binding']:raise ValueError('Accepted transport archive checksum differs')
        argv=[gcloud,'storage','objects','describe',item['uri']+'#'+item['generation'],'--format=json']
        m=json.loads(subprocess.check_output(argv,text=True,timeout=60))
        if str(m['generation'])!=item['generation'] or int(m['size'])!=size or m.get('crc32c_hash')!=item['crc32c']:raise ValueError('Private whole-object identity differs')
        import base64
        if m.get('md5_hash') and base64.b64encode(md5.digest()).decode()!=m['md5_hash']:raise ValueError('Private whole-object MD5 differs')
        if (p.stat().st_dev,p.stat().st_ino,p.stat().st_mtime_ns,p.stat().st_size)!=(v.st_dev,v.st_ino,v.st_mtime_ns,v.st_size):raise ValueError('Transport changed during verification')
        receipt=dict(path=str(p),status='verified_redundant_transport_released',binding=item['binding'],private_object=item['uri'],generation=item['generation'],server_crc32c=item['crc32c'],retained_extracted_inputs_and_journals=True,epoch=time.time())
        p.unlink();result.append(receipt);print('E030_RELEASED_REDUNDANT_TRANSPORT',str(p),size,flush=True)
    target=Path(output);target.parent.mkdir(parents=True,exist_ok=True)
    if target.exists():raise ValueError('Fresh cleanup receipt required')
    with target.open('x') as f:json.dump(dict(status='PASS',records=result,unique_science_deleted=False,GCS_mutated=False,free_bytes=shutil.disk_usage('/srv/dl_binner' if not engineering else target.parent).free),f,indent=2);f.write('\n')
    return result


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--plan',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();release(a.plan,a.output)
