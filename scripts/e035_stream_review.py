#!/usr/bin/env python3
"""Verify a generation-bound return stream without storing a second archive.

Materialize regular members and exact aliases for bounded local inspection.
The caller supplies authenticated transport and independently bound metadata;
this helper cannot launch compute, upload, or change scientific artifacts.
"""
import base64
import hashlib
import json
from pathlib import Path
import shutil
import struct
import subprocess
import tarfile


def verify_stream(raw, metadata, expected, inventory, output, crc_binary,
                  reserve=8*1024**3):
    """Check whole SHA/MD5/CRC32C, every member and explicit alias before admission.

    Consume the full compressed stream, including tar padding. Failed staging is
    retained for diagnosis and never accepted. The destination must be fresh.
    """
    out=Path(output);out.mkdir(parents=True,exist_ok=False)
    if expected['bytes']!=int(metadata['size']):raise ValueError('Object size binding differs')
    sha=hashlib.sha256();md5=hashlib.md5();count=0
    crc=subprocess.Popen([str(crc_binary),'-'],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    class HashingReader:
        def read(self,size=-1):
            nonlocal count
            value=raw.read(size);count+=len(value)
            if count>expected['bytes']:raise ValueError('Compressed object exceeds binding')
            sha.update(value);md5.update(value);crc.stdin.write(value)
            return value
    reader=HashingReader();seen=set();logical=0
    try:
        with tarfile.open(fileobj=reader,mode='r|gz',bufsize=1024**2)as archive:
            for member in archive:
                p=Path(member.name)
                if p.is_absolute()or '..'in p.parts or not member.isfile()or member.name in seen:
                    raise ValueError('Unsafe/duplicate/nonregular return member')
                if not seen and member.name!='inventory.json':raise ValueError('Inventory must be first')
                if member.name!='inventory.json'and member.name not in inventory['members']:
                    raise ValueError('Unlisted return member')
                logical+=member.size
                if logical>8*1024**3 or shutil.disk_usage(out).free-member.size<reserve:
                    raise ValueError('Local review space/logical limit exceeded')
                target=out/p;target.parent.mkdir(parents=True,exist_ok=True)
                h=hashlib.sha256();n=0
                with archive.extractfile(member)as source,target.open('xb')as dest:
                    for block in iter(lambda:source.read(1024**2),b''):
                        h.update(block);n+=len(block);dest.write(block)
                b=dict(bytes=n,sha256=h.hexdigest())
                if member.name=='inventory.json':
                    if json.loads(target.read_text())!=inventory:raise ValueError('Embedded inventory differs')
                elif b!=inventory['members'][member.name]:raise ValueError('Return member bytes differ')
                seen.add(member.name)
        while reader.read(1024**2):pass
        crc.stdin.close();crc.stdin=None
        stdout,stderr=crc.communicate(timeout=30)
        if crc.returncode:raise ValueError('SDK CRC32C failed: '+stderr.decode()[-1000:])
        digest=base64.b64encode(struct.pack('>I',int(stdout.strip()))).decode()
        if dict(bytes=count,sha256=sha.hexdigest())!=expected:raise ValueError('Whole archive SHA256 differs')
        if digest!=metadata['crc32c']:raise ValueError('Whole archive CRC32C differs')
        if metadata.get('md5Hash')and base64.b64encode(md5.digest()).decode()!=metadata['md5Hash']:
            raise ValueError('Whole archive MD5 differs')
        if seen!=set(inventory['members'])|{'inventory.json'}:raise ValueError('Missing archive member')
        work={n.removeprefix('work/'):b for n,b in inventory['members'].items()if n.startswith('work/')}
        for name,b in inventory['aliases'].items():
            p=Path(name);canonical=Path(b['canonical']);wanted={k:b[k]for k in ['bytes','sha256']}
            if (p.is_absolute()or canonical.is_absolute()or '..'in p.parts or '..'in canonical.parts
                or name in seen or inventory['members'].get(str(canonical))!=wanted
                or not name.startswith('work/')):raise ValueError('Invalid exact-byte alias')
            target=out/p;target.parent.mkdir(parents=True,exist_ok=True)
            target.hardlink_to(out/canonical);work[name.removeprefix('work/')]=wanted
        if inventory['omitted_retained_on_disk']or work!=inventory['all_work_members']:
            raise ValueError('Complete work/alias union differs')
        return dict(status='PASS',archive=expected,generation=metadata['generation'],
            physical_members=len(seen)-1,aliases=len(inventory['aliases']),logical_bytes=logical,
            every_member_and_alias_verified=True,whole_SHA256_MD5_CRC32C_verified=True,
            local_free_after=shutil.disk_usage(out).free)
    finally:
        if crc.poll()is None:
            crc.kill();crc.communicate()
