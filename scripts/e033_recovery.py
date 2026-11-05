#!/usr/bin/env python3
"""Admit the explicit E033 logging repair without rewriting its frozen source lock.

Only the progress keyword changes in product code. The remaining overrides are
operations/readers needed for verified reuse, compact long-run delivery and the
newly authorized clock. All inputs, policy/defaults, encoders, losses and RNG
statements remain the original E033 treatment.
"""
import ast
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).absolute().parents[1]
EXP=ROOT/'experiments/E033-multiscale-bam'
ORIGINAL='/srv/dl_binner/experiments/e033/multiscale-20261104T152005Z-a940769-r2'
PRODUCT='src/dl_binner/multiscale/model.py'
OVERRIDES={PRODUCT,'scripts/e033_control.py','scripts/e033_review.py'}


def binding(path):
    """Bind one regular source or metadata artifact."""
    path=Path(path)
    if path.is_symlink() or not path.is_file():raise ValueError('Regular repair artifact required')
    digest=hashlib.sha256();size=0
    with path.open('rb') as stream:
        for block in iter(lambda:stream.read(1024**2),b''):
            size+=len(block);digest.update(block)
    return dict(bytes=size,sha256=digest.hexdigest())


def logging_only(before,after):
    """Prove AST equality after the sole invalid stage keyword becomes role."""
    old=ast.parse(before);new=ast.parse(after);changed=0
    for n in ast.walk(old):
        if (isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id=='emit'
            and n.args and isinstance(n.args[0],ast.Constant) and n.args[0].value=='multiscale_training_progress'):
            for kw in n.keywords:
                if kw.arg=='stage':kw.arg='role';changed+=1
    if changed!=1 or ast.dump(old,include_attributes=False)!=ast.dump(new,include_attributes=False):
        raise ValueError('Repair changes more than the actual failing progress keyword')
    return True


def admit(path=None):
    """Verify the unchanged parent freezes and the exact prospective effective source."""
    path=Path(path or EXP/'repair-lock.json')
    if path.absolute()!=EXP/'repair-lock.json':raise ValueError('Canonical E033 repair lock required')
    lock=json.loads(path.read_text())
    fields={'kind','parent_source_lock','parent_candidate_lock','candidate','source_overrides','extra_files','original_phase','limits'}
    if set(lock)!=fields or lock['kind']!='E033 logging-only verified-reuse repair' or lock['original_phase']!=ORIGINAL:
        raise ValueError('Unknown repair scope or schema')
    source=EXP/'source-lock.json';candidate=EXP/'candidate-lock.json'
    if binding(source)!=lock['parent_source_lock'] or binding(candidate)!=lock['parent_candidate_lock']:
        raise ValueError('Original freeze was rewritten')
    old=json.loads(source.read_text());effective=dict(old['files'])
    if set(lock['source_overrides'])!=OVERRIDES:raise ValueError('Unapproved E033 source override')
    for name,pair in lock['source_overrides'].items():
        if set(pair)!={'before','after'} or old['files'][name]!=pair['before']:
            raise ValueError('Repair predecessor differs')
        effective[name]=pair['after']
    for name,wanted in effective.items():
        if binding(ROOT/name)!=wanted:raise ValueError('Effective E033 source differs: '+name)
    for name,wanted in lock['extra_files'].items():
        if Path(name).is_absolute() or '..' in Path(name).parts or binding(ROOT/name)!=wanted:
            raise ValueError('Repair helper differs: '+name)
    raw=subprocess.check_output(['git','show','c812eb8:'+PRODUCT],cwd=ROOT)
    if dict(bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest())!=old['files'][PRODUCT]:
        raise ValueError('Immutable scientific source snapshot differs')
    logging_only(raw.decode(),(ROOT/PRODUCT).read_text())
    newpath=EXP/'repair-candidate-lock.json'
    if binding(newpath)!=lock['candidate']:raise ValueError('Effective candidate artifact lock differs')
    previous=json.loads(candidate.read_text());current=json.loads(newpath.read_text())
    oldpackage=previous.pop('package_files');newpackage=current.pop('package_files')
    previous.pop('wheel');current.pop('wheel')
    if previous!=current or set(oldpackage)!=set(newpackage):raise ValueError('Scientific policy/defaults changed')
    if {n for n in oldpackage if oldpackage[n]!=newpackage[n]}!={'multiscale/model.py'}:
        raise ValueError('More than the logging-only installed module changed')
    if newpackage['multiscale/model.py']!=binding(ROOT/PRODUCT):raise ValueError('Repaired installed module differs')
    expected=json.loads((EXP/'runtime-plan.json').read_text())['limits']
    expected.update(seconds=108000,provider_STOP_seconds=108900)
    if lock['limits']!=expected:raise ValueError('Prospective operational limits differ')
    return lock,effective,newpath


def sources(plan):
    """Admit the explicit plan pointer and source overlay, with no hidden treatment."""
    r=plan['recovery']
    if set(r)!={'lock','binding'} or Path(r['lock']).absolute()!=EXP/'repair-lock.json' or binding(r['lock'])!=r['binding']:
        raise ValueError('Unbound repair plan')
    return admit(r['lock'])


class DiskHistory:
    """Stream whole-recovery filesystem observations outside compact control JSON."""
    def __init__(self,c):
        import threading
        self.c=c;self.done=threading.Event();self.reason=None;self.count=0
        self.minimum_free=None;self.minimum_source_free=None;self.minimum_task_free=None
        self.maximum_growth=0;self.maximum_task_used=0
        self.path=Path(c['root'])/'logs/filesystem.jsonl';self.file=None

    def record(self,row):
        """Append a complete row and update bounded counters; retain no growing list."""
        self.file.write(json.dumps(row,separators=(',',':'),allow_nan=False)+'\n');self.file.flush()
        self.count+=1;free=min(row['source_free'],row['task_free'])
        self.minimum_free=free if self.minimum_free is None else min(self.minimum_free,free)
        self.minimum_source_free=row['source_free'] if self.minimum_source_free is None else min(self.minimum_source_free,row['source_free'])
        self.minimum_task_free=row['task_free'] if self.minimum_task_free is None else min(self.minimum_task_free,row['task_free'])
        self.maximum_task_used=max(self.maximum_task_used,row['task_used'])
        self.maximum_growth=max(self.maximum_growth,row['task_used']-self.c['initial_filesystem_used_bytes'])

    def sample(self):
        """Read the positively identified source/task devices and enforce old baseline."""
        import os,shutil,time
        c=self.c;task=shutil.disk_usage(c['task_filesystem']);source=shutil.disk_usage(c['source_filesystem'])
        if os.stat(c['task_filesystem']).st_dev!=c['initial_filesystem_device']:
            raise ValueError('Recovery task device changed')
        row=dict(epoch=time.time(),task_used=task.used,task_free=task.free,source_free=source.free)
        self.record(row)
        if min(task.free,source.free)<25*1024**3:raise ValueError('Recovery source/task reserve failed')
        if task.used-c['initial_filesystem_used_bytes']>60*1024**3:raise ValueError('Original cumulative 60 GiB task growth failed')
        return row

    def start(self):
        """Start independent sampling and the original replacement-clock alarm."""
        import os,signal,threading,time
        self.file=self.path.open('x');self.previous=signal.getsignal(signal.SIGALRM)
        def alarm(*_):raise TimeoutError(self.reason or 'Common E033 recovery clock exhausted')
        signal.signal(signal.SIGALRM,alarm);signal.setitimer(signal.ITIMER_REAL,max(.001,self.c['review_deadline_epoch']-time.time()))
        self.sample()
        def loop():
            while not self.done.wait(2):
                try:self.sample()
                except BaseException as error:
                    self.reason=repr(error);os.kill(os.getpid(),signal.SIGALRM);return
        self.thread=threading.Thread(target=loop,daemon=True);self.thread.start()

    def close(self):
        """Seal the full history after collection and return only a compact binding."""
        import os,signal
        self.done.set()
        if hasattr(self,'thread'):self.thread.join(timeout=3)
        if self.file is not None:
            try:self.sample()
            except BaseException as error:self.reason=self.reason or repr(error)
            self.file.flush();os.fsync(self.file.fileno());self.file.close()
            self.file=None
        if hasattr(self,'previous'):
            signal.setitimer(signal.ITIMER_REAL,0);signal.signal(signal.SIGALRM,self.previous)
        return dict(history=binding(self.path),samples=self.count,minimum_free_bytes=self.minimum_free,
            minimum_source_free_bytes=self.minimum_source_free,minimum_task_free_bytes=self.minimum_task_free,
            maximum_original_baseline_growth_bytes=self.maximum_growth,maximum_task_used_bytes=self.maximum_task_used,
            original_task_baseline_bytes=self.c['initial_filesystem_used_bytes'],monitor_error=self.reason,
            scope='Current recovery science/collection sampled devices; original task baseline retained; earlier missing sort peak not reconstructed')


def upload(path,uri):
    """Upload/read back one new E033 object under its actual 3 GiB slice limit.

    Uses the accepted resumable/private/ephemeral-token transport, with E033's
    prospective cap rather than the older E021 helper's unrelated 2 GiB cap.
    There is no overwrite, composite-object fallback or credential persistence.
    """
    import urllib.parse,urllib.request
    path=Path(path);u=urllib.parse.urlsplit(uri)
    if (u.scheme!='gs' or u.netloc!='dl-binner-archive-167650584170' or not u.path.startswith('/e033/')
        or not path.is_file() or not 0<path.stat().st_size<=3*1024**3):
        raise ValueError('Bounded new private E033 object required')
    expected=binding(path)
    def token():
        q=urllib.request.Request('http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/token',headers={'Metadata-Flavor':'Google'})
        with urllib.request.urlopen(q,timeout=8) as f:return json.load(f)['access_token']
    auth=token();query=urllib.parse.urlencode(dict(uploadType='resumable',name=u.path.lstrip('/'),ifGenerationMatch=0))
    q=urllib.request.Request('https://storage.googleapis.com/upload/storage/v1/b/'+u.netloc+'/o?'+query,data=b'{}',method='POST',headers={'Authorization':'Bearer '+auth,'Content-Type':'application/json','X-Upload-Content-Length':str(expected['bytes'])})
    with urllib.request.urlopen(q,timeout=15) as f:location=f.headers['Location']
    with path.open('rb') as stream:
        q=urllib.request.Request(location,data=stream,method='PUT',headers={'Authorization':'Bearer '+auth,'Content-Length':str(expected['bytes']),'Content-Type':'application/octet-stream'})
        with urllib.request.urlopen(q,timeout=180) as f:obj=json.load(f)
    url='https://storage.googleapis.com/storage/v1/b/'+u.netloc+'/o/'+urllib.parse.quote(u.path.lstrip('/'),safe='')+'?alt=media&generation='+obj['generation']
    q=urllib.request.Request(url,headers={'Authorization':'Bearer '+token()});h=hashlib.sha256();size=0
    with urllib.request.urlopen(q,timeout=180) as f:
        for block in iter(lambda:f.read(1024**2),b''):size+=len(block);h.update(block)
    if dict(bytes=size,sha256=h.hexdigest())!=expected:raise ValueError('New E033 private readback differs')
    return dict(uri=uri,generation=obj['generation'],binding=expected,readback_verified=True)
