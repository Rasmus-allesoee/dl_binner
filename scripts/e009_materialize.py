"""Progress-reporting, resumable E009 numerical runtime materialization.

Select runtime Python/packages/shared libraries from the unchanged Conda prefix.
Omit explicit development/test payloads, retaining metadata, licences and all
other package resources. Copy/hash at most 128 members per chunk; persist sealed
uncompressed chunks immediately. A subsequent job verifies and restores sealed
chunks, never recopies their source contents. Unsealed partials remain evidence.
The caller supplies the overall allocation clock and a progress-aware stall guard;
this worker has no arbitrary copy/verification/packing stage timeout.
"""
import argparse
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import tarfile
import threading
import time
import uuid
import sys
sys.path.insert(0,str(Path(__file__).absolute().parent))

from e009_snapshot import entries, verify

POLICY='e009-numerical-runtime-v8'


class Progress:
    """Emit monotonic work units from completed metadata/byte/file operations.

    Work units are activity evidence, not CPU, throughput or scientific success.
    No timer thread manufactures progress while actual I/O is stalled.
    """
    def __init__(self, interval=5):
        self.interval=interval;self.units=0;self.last=0;self.lock=threading.Lock()

    def advance(self, phase, amount=1, force=False, **details):
        """Report real increasing work; phase text alone never extends the clock."""
        with self.lock:
            self.units+=amount;now=time.monotonic()
            if force or now-self.last>=self.interval:
                print('DLBINNER SNAPSHOT_PROGRESS_JSON='+json.dumps(dict(
                    work_units=self.units,phase=phase,**details)),flush=True)
                self.last=now


def exclusion(rel):
    """Return a precise omission reason, or None for retained runtime payload.

    Public testing helpers (_testing, testing, unittest itself) remain. No model,
    database, data, licence, metadata, .pth or ordinary package source is removed
    from an included package. This is a numerical runtime, not a compiler/tool
    distribution; later utility executables have their separate pinned prefix.
    """
    p=Path(rel);parts=p.parts
    if parts[0]=='bin':
        return None if len(parts)==2 and re.fullmatch(r'python(?:\d+(?:\.\d+)?)?',parts[1]) else 'non-Python executable'
    if parts[0] not in ('lib','conda-meta'):return 'non-numerical top-level payload'
    if p.suffix in ('.a','.la'):return 'static build library'
    if len(parts)>1 and parts[1] in ('gcc','cmake','pkgconfig'):return 'compiler/build metadata'
    if parts[0]=='lib' and any(x in ('test','tests') for x in parts[2:]):return 'bundled test suite'
    text='/'.join(parts)
    if any('/site-packages/'+path+'/' in text for path in (
        'torch/include','numpy/_core/include','numpy/core/include','pysam/include')):
        return 'package compiler headers/sources'
    return None


def plan(source, progress=None):
    """Record selected identities, omissions and required internal-link closure."""
    source=Path(source).absolute();raw=entries(source,progress=progress)
    # Device/inode IDs can legitimately differ on a new job's Home mount. Keep
    # portable stat identities in the persistent plan; copy checks also compare
    # the within-job device/inode before and after each original read.
    raw={n:dict(r,identity=r['identity'][2:]) if r['type']=='file' else r for n,r in raw.items()}
    selected={n:r for n,r in raw.items() if exclusion(n) is None}
    omissions={n:exclusion(n) for n in raw if n not in selected}
    while True:
        added={}
        for rel,r in selected.items():
            if r['type']!='link':continue
            target=(source/rel).resolve();target_rel=str(target.relative_to(source.resolve()))
            needed=[target_rel] if target_rel in raw else [n for n in raw if n.startswith(target_rel+'/')]
            for n in needed:
                if n not in selected:added[n]=raw[n]
        if not added:break
        selected.update(added)
        for n in added:omissions.pop(n,None)
    if not selected:raise ValueError('No numerical runtime files selected')
    return dict(policy=POLICY,source_prefix=str(source),files=dict(sorted(selected.items())),
        omitted=dict(sorted(omissions.items())),original_non_bytecode_entries=len(raw),
        selected_entries=len(selected),logical_bytes=sum(r.get('bytes',0) for r in selected.values()),
        omitted_counts=dict(Counter(omissions.values())),
        omitted_bytes=sum(raw[n].get('bytes',0) for n in omissions),
        bytecode_omission='__pycache__, .pyc, .pyo',chunk_members=128,chunk_target_bytes=128_000_000)


def atomic_json(path, data):
    """Commit a complete JSON receipt atomically; preserve interrupted temporaries."""
    path=Path(path);tmp=path.with_name(path.name+'.'+uuid.uuid4().hex+'.partial')
    with tmp.open('x') as f:
        json.dump(data,f,sort_keys=True);f.write('\n');f.flush();os.fsync(f.fileno())
    tmp.replace(path)


def digest_json(data):
    """Bind the deterministic plan/receipts without reading source contents."""
    return hashlib.sha256(json.dumps(data,sort_keys=True).encode()).hexdigest()


def groups(files):
    """Deterministic small chunks; a single large library is streamed on its own."""
    batch=[];size=0
    for name,r in files.items():
        if batch and (len(batch)>=128 or size+r.get('bytes',0)>128_000_000):
            yield batch;batch=[];size=0
        batch.append(name);size+=r.get('bytes',0)
    if batch:yield batch


class DigestStream:
    """Hash streamed tar reads/writes and report actual byte progress."""
    def __init__(self, stream, progress, phase):
        self.stream,self.progress,self.phase=stream,progress,phase
        self.digest=hashlib.sha256();self.size=0

    def read(self, n=-1):
        data=self.stream.read(n);self.digest.update(data);self.size+=len(data)
        if data:self.progress.advance(self.phase,len(data))
        return data

    def write(self, data):
        n=self.stream.write(data)
        if n!=len(data):raise OSError('Short snapshot archive write')
        self.digest.update(data);self.size+=n;self.progress.advance(self.phase,n)
        return n


def restore_chunk(state, sealed, names, destination, progress):
    """Stream-check archive and every member before counting a chunk as restored."""
    if set(sealed['files'])!=set(names):raise ValueError('Sealed chunk member set changed')
    archive=state/sealed['archive']['name']
    if Path(sealed['archive']['name']).name!=sealed['archive']['name']:raise ValueError('Unsafe chunk archive locator')
    seen=set()
    with archive.open('rb') as f:
        stream=DigestStream(f,progress,'restore/hash')
        with tarfile.open(fileobj=stream,mode='r|') as tar:
            for m in tar:
                rel=str(Path(m.name).relative_to('prefix'))
                if rel not in sealed['files'] or rel in seen or '..' in Path(rel).parts:raise ValueError('Unexpected chunk member')
                seen.add(rel);r=sealed['files'][rel];q=destination/rel;q.parent.mkdir(parents=True,exist_ok=True)
                if r['type']=='link':
                    if not m.issym() or m.linkname!=r['target']:raise ValueError('Chunk link differs')
                    if not (q.parent/r['target']).resolve().is_relative_to(destination.resolve()):raise ValueError('Escaping chunk link')
                    q.symlink_to(r['target'])
                else:
                    if not m.isfile() or m.size!=r['bytes']:raise ValueError('Chunk file differs')
                    h=hashlib.sha256()
                    with tar.extractfile(m) as src,q.open('xb') as out:
                        for block in iter(lambda:src.read(1024*1024),b''):
                            h.update(block);out.write(block)
                    q.chmod(r['mode'])
                    if h.hexdigest()!=r['sha256']:raise ValueError('Chunk member bytes changed')
        while stream.read(1024*1024):pass
    if seen!=set(names) or stream.size!=sealed['archive']['bytes'] or stream.digest.hexdigest()!=sealed['archive']['sha256']:
        raise ValueError('Chunk archive bytes changed')


def copy_chunk(source, destination, records, names, progress, readers):
    """Read/hash selected original contents once, checking immutable stat identities."""
    def copy(rel):
        r=records[rel];p=source/rel;q=destination/rel;q.parent.mkdir(parents=True,exist_ok=True)
        if r['type']=='link':q.symlink_to(r['target']);result=dict(r)
        else:
            h=hashlib.sha256();before=p.stat()
            if [before.st_mtime_ns,before.st_size]!=r['identity']:raise ValueError('Original source changed before read: '+rel)
            with p.open('rb') as f,q.open('xb') as out:
                for block in iter(lambda:f.read(1024*1024),b''):
                    h.update(block);out.write(block);progress.advance('source copy/hash',len(block))
            q.chmod(r['mode']);info=p.stat()
            if [info.st_mtime_ns,info.st_size]!=r['identity'] or (info.st_dev,info.st_ino)!=(before.st_dev,before.st_ino):
                raise ValueError('Original source changed during read: '+rel)
            result={k:v for k,v in r.items() if k!='identity'};result['sha256']=h.hexdigest()
        progress.advance('source copy/hash',force=False,latest=rel)
        return rel,result
    pool=ThreadPoolExecutor(max_workers=readers)
    try:
        result=dict(f.result() for f in as_completed([pool.submit(copy,n) for n in names]))
    except BaseException:
        pool.shutdown(wait=False,cancel_futures=True);raise
    else:pool.shutdown(wait=True)
    return dict(sorted(result.items()))


def materialize(source, destination, state, summary, readers=8, progress=None):
    """Resume sealed chunks, copy only missing chunks, then verify a complete runtime.

    State is experiment-owned persistent storage; destination is fresh job-local
    storage. A killed job loses at most its current unsealed chunk, not all work.
    Native import/ABI acceptance is deliberately separate. Original files remain
    untouched; source plan identities must match across jobs and after copying.
    """
    source=Path(source).absolute();destination=Path(destination).absolute();state=Path(state).absolute()
    if destination.exists() or state.is_symlink() or destination.resolve().is_relative_to(source.resolve()) or state.resolve().is_relative_to(source.resolve()):
        raise ValueError('Fresh destination and unlinked state outside source required')
    if not 1<=readers<=8:raise ValueError('Use one to eight bounded I/O readers')
    state.mkdir(parents=True,exist_ok=True);progress=progress or Progress()
    with (state/'writer.lock').open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        progress.advance('enumerate source plan',force=True)
        current=plan(source,progress=lambda n:progress.advance('enumerate source plan',n));plan_path=state/'plan.json';anchor=digest_json(current)
        if plan_path.exists():
            if json.loads(plan_path.read_text())!=current:raise ValueError('Source/selection plan changed; preserve state, use a new versioned state')
        else:
            if list(state.glob('chunk-*.json')):raise ValueError('Chunk receipts without a source plan')
            atomic_json(plan_path,current)
        batches=list(groups(current['files']))
        missing=[names for i,names in enumerate(batches) if not (state/f'chunk-{i:05}.json').exists()]
        missing_entries=sum(len(x) for x in missing)
        brief={k:v for k,v in current.items() if k not in ('files','omitted')}
        brief.update(plan_sha256=anchor,state=str(state),
            measured_v7_entries_per_second=17989/1200.067715,
            rough_copy_seconds_at_v7_rate=current['selected_entries']/(17989/1200.067715),
            candidate_sealed_entries=current['selected_entries']-missing_entries,
            missing_entries=missing_entries,
            rough_remaining_copy_seconds_at_v7_rate=missing_entries/(17989/1200.067715),
            forecast_scope='rough entry-count projection only; large-file throughput, exclusions and chunk persistence change costs')
        atomic_json(summary,brief);print('DLBINNER SNAPSHOT_PLAN_JSON='+json.dumps(brief),flush=True)
        missing_bytes=sum(current['files'][n].get('bytes',0) for names in missing for n in names)
        # Restore needs local space for the complete runtime; persistent storage
        # needs only missing chunks, tar headers and new manifests, not a second
        # complete archive on every resume.
        requirements=[(destination.parent,current['logical_bytes']+500_000_000),
                      (state,missing_bytes+sum(len(x) for x in missing)*4096+64_000_000)]
        for parent,required in requirements:
            if shutil.disk_usage(parent).free<required:
                raise ValueError('Provision '+str(required)+' free bytes at '+str(parent))
        destination.mkdir();all_files={};shards=[];copied=restored=0
        for index,names in enumerate(batches):
            seal=state/f'chunk-{index:05}.json'
            if seal.exists():
                sealed=json.loads(seal.read_text())
                if sealed['plan_sha256']!=anchor or sealed['index']!=index:raise ValueError('Chunk plan/index changed')
                restore_chunk(state,sealed,names,destination,progress);restored+=len(names)
            else:
                files=copy_chunk(source,destination,current['files'],names,progress,readers)
                name=f'chunk-{index:05}-{uuid.uuid4().hex}.tar';archive=state/name
                # Unsealed archives are retained on interruption, never reused.
                with archive.open('xb') as out:
                    stream=DigestStream(out,progress,'pack/persist')
                    with tarfile.open(fileobj=stream,mode='w|') as tar:
                        for rel in files:tar.add(destination/rel,arcname='prefix/'+rel,recursive=False)
                    out.flush();os.fsync(out.fileno())
                sealed=dict(plan_sha256=anchor,index=index,files=files,
                            archive=dict(name=name,bytes=stream.size,sha256=stream.digest.hexdigest()))
                atomic_json(seal,sealed);copied+=len(names)
            all_files.update(sealed['files']);shards.append({'receipt':seal.name,'receipt_sha256':digest_json(sealed),'archive':sealed['archive']})
            progress.advance('chunk sealed/restored',force=True,selected_total=current['selected_entries'],
                             source_copied=copied,restored=restored,sealed_chunks=len(shards))
        if plan(source,progress=lambda n:progress.advance('recheck source identities',n))!=current:raise ValueError('Original source/selection plan changed during materialization')
        manifest=dict(format='e009-runtime-chunks-v8',source_prefix=str(source),plan_sha256=anchor,
            state=str(state),files=dict(sorted(all_files.items())),shards=shards,
            logical_bytes=current['logical_bytes'],excluded=current['omitted_counts'],
            scientific_execution_admitted=False)
        verify(destination,manifest,progress=lambda n:progress.advance('verify local bytes',n))
        final=state/'snapshot.json'
        if final.exists():
            if json.loads(final.read_text())!=manifest:raise ValueError('Existing final snapshot receipt changed')
        else:atomic_json(final,manifest)
        brief.update(source_copied_entries=copied,restored_entries=restored,sealed_chunks=len(shards),complete=True)
        atomic_json(summary,brief)
        print('DLBINNER SNAPSHOT_READY_JSON='+json.dumps(dict(receipt=str(state/'snapshot.json'),
              copied=copied,restored=restored,chunks=len(shards))),flush=True)
        return dict(manifest,source_copied_entries=copied,restored_entries=restored)


def restore_accepted(accepted, destination, summary, progress=None):
    """Restore an accepted complete runtime read-only, with no original-source access.

    The reviewed record binds the final receipt and every sealed chunk. Verify
    seals, archive and member bytes before use; missing/corrupt state fails rather
    than triggering a new copy. A fresh job-local destination is mandatory.
    """
    from e009_common import binding
    anchor=accepted['snapshot'];state=Path(anchor['state']);destination=Path(destination).absolute()
    if state.is_symlink() or destination.exists() or destination.is_symlink():
        raise ValueError('Unlinked retained state and fresh restore destination required')
    progress=progress or Progress();progress.advance('bind accepted snapshot',force=True)
    receipt=state/'snapshot.json'
    if binding(receipt)!=anchor['receipt_file']:raise ValueError('Accepted snapshot receipt bytes changed')
    manifest=json.loads(receipt.read_text())
    if manifest['format']!='e009-runtime-chunks-v8' or manifest['source_prefix']!=anchor['source_prefix'] or manifest['state']!=str(state) or manifest['shards']!=anchor['shards']:
        raise ValueError('Accepted snapshot identity changed')
    if len(manifest['files'])!=anchor['files'] or manifest['logical_bytes']!=anchor['logical_bytes']:
        raise ValueError('Accepted snapshot population changed')
    if shutil.disk_usage(destination.parent).free<manifest['logical_bytes']+500_000_000:
        raise ValueError('Provision local temporary space for retained runtime')
    # Lock an already existing inode read-only; do not create/change persistent state.
    with (state/'writer.lock').open('r') as lock:
        fcntl.flock(lock,fcntl.LOCK_SH|fcntl.LOCK_NB)
        destination.mkdir();seen={}
        for index,shard in enumerate(manifest['shards']):
            if shard['receipt']!=f'chunk-{index:05}.json':raise ValueError('Accepted chunk locator changed')
            seal=state/shard['receipt']
            if seal.is_symlink():raise ValueError('Linked chunk receipt refused')
            sealed=json.loads(seal.read_text())
            if digest_json(sealed)!=shard['receipt_sha256'] or sealed['index']!=index or sealed['plan_sha256']!=manifest['plan_sha256'] or sealed['archive']!=shard['archive']:
                raise ValueError('Accepted chunk seal changed')
            if (state/sealed['archive']['name']).is_symlink():raise ValueError('Linked chunk archive refused')
            for name,record in sealed['files'].items():
                if name in seen or manifest['files'].get(name)!=record:raise ValueError('Accepted chunk member population changed')
                seen[name]=record
            restore_chunk(state,sealed,list(sealed['files']),destination,progress)
            progress.advance('accepted chunk restored',force=True,restored=len(seen),sealed_chunks=index+1)
        if seen!=manifest['files']:raise ValueError('Incomplete accepted chunk population')
        verify(destination,manifest,progress=lambda n:progress.advance('verify restored bytes',n))
    write=dict(state=str(state),receipt_file=anchor['receipt_file'],local_prefix=str(destination),
        source_copied_entries=0,restored_entries=len(seen),sealed_chunks=len(manifest['shards']),
        logical_bytes=manifest['logical_bytes'],complete=True,original_source_accessed=False)
    atomic_json(summary,write);print('DLBINNER SNAPSHOT_READY_JSON='+json.dumps(write),flush=True)
    return manifest


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source',type=Path);p.add_argument('--destination',type=Path,required=True)
    p.add_argument('--state',type=Path);p.add_argument('--summary',type=Path,required=True)
    p.add_argument('--accepted-record',type=Path,help='Restore-only reviewed snapshot; never copies original contents')
    p.add_argument('--verify-receipt',type=Path);a=p.parse_args()
    try:
        if a.accepted_record:
            if a.source or a.state or a.verify_receipt:raise ValueError('Accepted restore cannot also copy or select another state')
            restore_accepted(json.loads(a.accepted_record.read_text()),a.destination,a.summary)
        elif a.verify_receipt:
            progress=Progress();verify(a.destination,json.loads(a.verify_receipt.read_text()),
                progress=lambda n:progress.advance('verify local bytes',n))
        else:
            if not a.source or not a.state:raise ValueError('Materialization needs source and state')
            materialize(a.source,a.destination,a.state,a.summary)
    except BaseException:
        import sys,traceback
        traceback.print_exc();sys.stdout.flush();sys.stderr.flush();os._exit(1)
