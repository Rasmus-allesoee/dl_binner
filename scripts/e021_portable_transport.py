#!/usr/bin/env python3
"""Stream only explicitly hash-bound E021 files into fresh destinations.

No extraction, learning, source repair, credentials or cloud access. The sender
and receiver both retain complete byte/stream digests; the controller must pair
those receipts before admitting a consumer. Incomplete destinations and failures
are retained, never overwritten or silently refetched.
"""
import argparse,hashlib,io,json,os,sys,tarfile,time
from pathlib import Path,PurePosixPath

CAP=20*1024**3
MANIFEST_CAP=1024**2


def binding(path):
    """Hash a regular immutable file without following a final symlink."""
    p=Path(path)
    if p.is_symlink()or not p.is_file():raise ValueError('Regular source required: '+str(p))
    h=hashlib.sha256();n=0
    with p.open('rb')as f:
        for b in iter(lambda:f.read(1024**2),b''):n+=len(b);h.update(b)
    return dict(bytes=n,sha256=h.hexdigest())


def binding_bytes(data):
    """Hash a bounded in-memory test/control stream; never used for bulk buffering."""
    if len(data)>MANIFEST_CAP:raise ValueError('Only small control bytes may be buffered')
    return dict(bytes=len(data),sha256=hashlib.sha256(data).hexdigest())


def names(manifest):
    """Refuse arbitrary archive paths, invalid counters and expanded schemas."""
    if set(manifest)!={'kind','files'}or manifest['kind']!='E021 verified transport v1':raise ValueError('Unexpected transport manifest')
    files=manifest['files']
    if not isinstance(files,dict)or not 1<=len(files)<=4096:raise ValueError('Bounded explicit file set required')
    for name,v in files.items():
        p=PurePosixPath(name)
        if not name or name!=str(p)or p.is_absolute()or'..'in p.parts or'\\'in name or name=='inventory.json':raise ValueError('Unsafe transport member')
        if set(v)!={'source','bytes','sha256'}or type(v['bytes'])is not int or not 0<=v['bytes']<=CAP or len(v['sha256'])!=64 or set(v['sha256'])-set('0123456789abcdef'):raise ValueError('Invalid member binding')
    if sum(v['bytes']for v in files.values())>CAP:raise ValueError('Transport bytes exceed cap')
    return files


class Meter:
    """Bound and hash actual stream bytes, including tar headers and footer."""
    def __init__(self,stream,cap):
        if not 0<cap<=CAP:raise ValueError('Transport ceiling exceeds scope')
        self.stream=stream;self.cap=cap;self.count=0;self.sha=hashlib.sha256()
    def write(self,data):
        if self.count+len(data)>self.cap:raise ValueError('Transport byte cap exceeded')
        n=self.stream.write(data)
        if n is None:n=len(data)
        if n!=len(data):raise OSError('Short transport write')
        self.count+=n;self.sha.update(data);return n
    def read(self,size=-1):
        if size<0:size=min(1024**2,self.cap-self.count+1)
        data=self.stream.read(size)
        if self.count+len(data)>self.cap:raise ValueError('Transport byte cap exceeded')
        self.count+=len(data);self.sha.update(data);return data
    def flush(self):return self.stream.flush()
    def record(self):return dict(bytes=self.count,sha256=self.sha.hexdigest())


def send(manifest,stream,cap=CAP):
    """Verify declared source bytes and stream a reproducible, regular-file tar."""
    files=names(manifest);raw=json.dumps(manifest,sort_keys=True,separators=(',',':')).encode()
    if len(raw)>MANIFEST_CAP:raise ValueError('Manifest exceeds cap')
    for k,v in files.items():
        if binding(v['source'])!={n:v[n]for n in ['bytes','sha256']}:raise ValueError('Source bytes differ: '+k)
    meter=Meter(stream,cap)
    def entry(a,name,data=None,path=None,size=None):
        t=tarfile.TarInfo(name);t.size=len(data)if data is not None else size;t.mtime=0;t.mode=0o600;t.uid=t.gid=0
        if data is not None:a.addfile(t,io.BytesIO(data))
        else:
            with Path(path).open('rb')as f:a.addfile(t,f)
    with tarfile.open(fileobj=meter,mode='w|',format=tarfile.GNU_FORMAT)as a:
        entry(a,'inventory.json',raw)
        for k,v in sorted(files.items()):entry(a,k,path=v['source'],size=v['bytes'])
    meter.flush()
    for k,v in files.items():
        if binding(v['source'])!={n:v[n]for n in ['bytes','sha256']}:raise ValueError('Source changed during transfer: '+k)
    return dict(status='SENT_VERIFIED',stream=meter.record(),manifest_sha256=hashlib.sha256(raw).hexdigest(),members=len(files))


def receive(manifest,stream,destination,cap=CAP,before_write=None):
    """Restore every byte to a fresh directory and retain failure partials."""
    files=names(manifest);dest=Path(destination);incoming=dest.with_name(dest.name+'.incoming')
    if dest.exists()or incoming.exists():raise FileExistsError('Fresh destination/partial required')
    incoming.mkdir(parents=True,exist_ok=False);meter=Meter(stream,cap);seen=set();inventory=None
    with tarfile.open(fileobj=meter,mode='r|')as a:
        for m in a:
            if not m.isfile()or m.name in seen:raise ValueError('Nonregular/duplicate transport member')
            if inventory is None:
                if m.name!='inventory.json'or not 0<m.size<=MANIFEST_CAP:raise ValueError('Bounded first manifest required')
                f=a.extractfile(m);raw=f.read(MANIFEST_CAP+1)
                if len(raw)!=m.size:raise ValueError('Truncated transport manifest')
                inventory=json.loads(raw)
                if inventory!=manifest:raise ValueError('Expected manifest differs')
                seen.add(m.name);continue
            if m.name not in files or m.size!=files[m.name]['bytes']:raise ValueError('Unexpected member/size')
            p=incoming/m.name;p.parent.mkdir(parents=True,exist_ok=True);h=hashlib.sha256();n=0
            with p.open('xb')as out:
                f=a.extractfile(m)
                for b in iter(lambda:f.read(1024**2),b''):
                    if before_write is not None:before_write(len(b))
                    out.write(b);h.update(b);n+=len(b)
            if dict(bytes=n,sha256=h.hexdigest())!={k:files[m.name][k]for k in ['bytes','sha256']}:raise ValueError('Member bytes differ: '+m.name)
            seen.add(m.name)
    for _ in iter(lambda:meter.read(1024**2),b''):pass
    if seen!=set(files)|{'inventory.json'}:raise ValueError('Incomplete transport file set')
    if dest.exists():raise FileExistsError('Destination appeared during transfer')
    incoming.rename(dest)
    return dict(status='RECEIVED_MEMBERS_VERIFIED_PENDING_PAIRED_STREAM',stream=meter.record(),manifest_sha256=hashlib.sha256(json.dumps(manifest,sort_keys=True,separators=(',',':')).encode()).hexdigest(),members=len(files),destination=str(dest),consumer_admitted=False)


def paired(sender,receiver,relay):
    """Admit a transport only after all three full stream bindings agree."""
    if sender['status']!='SENT_VERIFIED'or receiver['status']!='RECEIVED_MEMBERS_VERIFIED_PENDING_PAIRED_STREAM':raise ValueError('Transport terminal status differs')
    if sender['manifest_sha256']!=receiver['manifest_sha256']or sender['stream']!=receiver['stream']or sender['stream']!=relay:raise ValueError('Independent stream digests differ')
    return dict(status='PAIRED_STREAM_AND_MEMBERS_PASS',stream=relay,manifest_sha256=sender['manifest_sha256'],members=sender['members'],consumer_admitted=True)


def native_budget(config):
    """Refuse each write before aggregate space/reserve or current clock can be lost."""
    import shutil
    cfg=json.loads(Path(config).read_text());root=Path(cfg['root']);host=json.loads((root/'host.json').read_text())
    def check(n):
        if time.time()>=cfg['node_deadline_epoch']-120:raise TimeoutError('Original node/common transport clock exhausted')
        peer=json.loads((root/'peer-usage.json').read_text());w=shutil.disk_usage('/srv/dl_binner');b=shutil.disk_usage('/')
        if peer.get('live')and time.time()-peer['epoch']>180:raise TimeoutError('Live peer accounting stale')
        growth=max(0,w.used-host['work_used_bytes'])+max(0,b.used-host['boot_used_bytes'])
        if growth+peer.get('growth_bytes',0)+n+256*1024>32*1024**3 or w.free-n-1024**2<25*1024**3 or b.free<1024**3:raise MemoryError('Before-write aggregate/reserve transport guard failed')
    return check


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('action',choices=['send','receive']);p.add_argument('--manifest',type=Path,required=True);p.add_argument('--receipt',type=Path,required=True);p.add_argument('--destination',type=Path);p.add_argument('--cap',type=int,default=CAP);p.add_argument('--budget-config',type=Path);a=p.parse_args()
    try:
        m=json.loads(a.manifest.read_text());value=send(m,sys.stdout.buffer,a.cap)if a.action=='send'else receive(m,sys.stdin.buffer,a.destination,a.cap,native_budget(a.budget_config)if a.budget_config else None)
    except BaseException as e:
        with a.receipt.open('x')as f:json.dump(dict(status='FAILED',error=repr(e),epoch=time.time()),f)
        raise
    with a.receipt.open('x')as f:json.dump(value,f,indent=2);f.write('\n')

if __name__=='__main__':main()
