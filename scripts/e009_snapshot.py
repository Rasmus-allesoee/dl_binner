"""Create and verify an immutable E009 job-local Conda execution snapshot.

Read the authoritative prefix once, with eight bounded I/O readers, hashing each
file while copying. Skip regenerable bytecode; preserve all other regular bytes
and modes. Normalize internal symlinks, reject external links/devices/venvs, and
retain a self-contained uncompressed archive for later explicit reuse. No installs,
prefix rewriting, activation or copied console-script execution is performed.
Native imports, inventory, loaded-library origins and numerical work must pass
separately: a copy is not proof that a Conda environment is relocatable.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib
import json
import os
from pathlib import Path
import shutil
import stat
import tarfile
import time


def entries(prefix, progress=None):
    """Inventory lstat identities without following directories through symlinks."""
    prefix=Path(prefix).absolute()
    if prefix.is_symlink() or not prefix.is_dir() or (prefix/'pyvenv.cfg').exists():
        raise ValueError('Snapshot requires an unlinked standalone Conda prefix, not a venv')
    prefix=prefix.resolve()  # Normalize parent aliases such as macOS /var -> /private/var.
    result={}
    for root, dirs, files in os.walk(prefix,followlinks=False):
        dirs[:]=sorted(d for d in dirs if d!='__pycache__')
        for name in sorted(dirs+files):
            p=Path(root)/name
            if p.suffix in ('.pyc','.pyo'):continue
            info=p.lstat();mode=stat.S_IMODE(info.st_mode);rel=str(p.relative_to(prefix))
            if stat.S_ISLNK(info.st_mode):
                target=p.resolve(strict=True)
                if not target.is_relative_to(prefix):raise ValueError('External prefix link refused: '+rel)
                result[rel]={'type':'link','target':os.path.relpath(target,p.parent),'mode':mode}
            elif stat.S_ISREG(info.st_mode):
                result[rel]={'type':'file','mode':mode,'bytes':info.st_size,
                             'identity':[info.st_dev,info.st_ino,info.st_mtime_ns,info.st_size]}
            elif not stat.S_ISDIR(info.st_mode):raise ValueError('Nonregular prefix member: '+rel)
            if progress:progress(1)
    return result


def verify(prefix, manifest, progress=None):
    """Check exact local file/link set, modes and content hashes against the copy."""
    actual=entries(prefix,progress=progress);expected=manifest['files']
    if set(actual)!=set(expected):raise ValueError('Snapshot file set changed')
    for rel,record in expected.items():
        a=actual[rel]
        if a['type']!=record['type'] or a['mode']!=record['mode']:raise ValueError('Snapshot member type/mode changed: '+rel)
        if a['type']=='link':
            if a['target']!=record['target']:raise ValueError('Snapshot link changed: '+rel)
        else:
            h=hashlib.sha256()
            with (Path(prefix)/rel).open('rb') as f:
                for block in iter(lambda:f.read(1024*1024),b''):
                    h.update(block)
                    if progress:progress(len(block))
            if a['bytes']!=record['bytes'] or h.hexdigest()!=record['sha256']:
                raise ValueError('Snapshot bytes changed: '+rel)
        if progress:progress(1)


def create(source, destination, archive, receipt):
    """Copy unchanged original bytes, verify locally, then persist a reusable tar.

    Eight readers overlap storage latency; affinity/native thread caps still bound
    CPU use. The caller supervises the entire worker, including enumeration/pack.
    Partial copies/archives are never admitted. All original file identities and
    the complete non-bytecode file set must remain unchanged during the copy.
    """
    source=Path(source).absolute();destination=Path(destination).absolute()
    archive=Path(archive);receipt=Path(receipt)
    if destination.exists() or archive.exists() or receipt.exists():raise ValueError('Use fresh snapshot destinations')
    if destination.is_relative_to(source):raise ValueError('Snapshot cannot be inside source prefix')
    print('DLBINNER SNAPSHOT enumerate '+str(source),flush=True)
    before=entries(source);total=sum(r.get('bytes',0) for r in before.values())
    for parent in (destination.parent,archive.parent):
        if shutil.disk_usage(parent).free<total+500_000_000:raise ValueError('Provision snapshot space: '+str(total)+' bytes plus 500 MB reserve at '+str(parent))
    destination.mkdir();records={};done=0;last=time.monotonic()
    def copy(rel,record):
        p=source/rel;q=destination/rel;q.parent.mkdir(parents=True,exist_ok=True)
        if record['type']=='link':q.symlink_to(record['target']);return rel,record
        digest=hashlib.sha256()
        with p.open('rb') as f,q.open('xb') as out:
            for block in iter(lambda:f.read(1024*1024),b''):
                digest.update(block);out.write(block)
        q.chmod(record['mode'])
        r={k:v for k,v in record.items() if k!='identity'};r['sha256']=digest.hexdigest()
        return rel,r
    pool=ThreadPoolExecutor(max_workers=8)
    try:
        futures=[pool.submit(copy,rel,r) for rel,r in before.items()]
        for future in as_completed(futures):
            rel,r=future.result();records[rel]=r;done+=1
            if time.monotonic()-last>=5:
                print(f'DLBINNER SNAPSHOT copied {done}/{len(before)} members; latest={rel}',flush=True);last=time.monotonic()
    except BaseException:
        pool.shutdown(wait=False,cancel_futures=True)
        raise
    else:pool.shutdown(wait=True)
    if entries(source)!=before:raise ValueError('Original prefix changed during copy')
    manifest={'source_prefix':str(source),'files':dict(sorted(records.items())),
              'logical_bytes':total,'excluded':'__pycache__, .pyc and .pyo only',
              'identity_scope':'copied source bytes, not equality to historical full-prefix hash',
              'io_readers':8,'scientific_execution_admitted':False}
    print('DLBINNER SNAPSHOT verify local bytes',flush=True);verify(destination,manifest)
    print('DLBINNER SNAPSHOT pack immutable archive',flush=True)
    partial=archive.with_name(archive.name+'.partial')
    with tarfile.open(partial,'x') as tar:
        for rel in manifest['files']:tar.add(destination/rel,arcname='prefix/'+rel,recursive=False)
    digest=hashlib.sha256()
    with partial.open('rb') as f:
        for block in iter(lambda:f.read(1024*1024),b''):digest.update(block)
    partial.rename(archive)
    manifest['archive']={'path':str(archive),'bytes':archive.stat().st_size,'sha256':digest.hexdigest()}
    receipt.write_text(json.dumps(manifest,sort_keys=True,indent=2)+'\n')
    print('SNAPSHOT_READY='+json.dumps({'receipt':str(receipt),'archive':manifest['archive'],
                                     'files':len(records),'logical_bytes':total}),flush=True)
    return manifest


def restore(receipt, destination):
    """Verify a retained archive and restore exact safe files/links, never Home paths."""
    manifest=json.loads(Path(receipt).read_text());archive=Path(manifest['archive']['path'])
    destination=Path(destination)
    if destination.exists():raise ValueError('Restore needs fresh destination')
    h=hashlib.sha256()
    with archive.open('rb') as f:
        for block in iter(lambda:f.read(1024*1024),b''):h.update(block)
    if archive.stat().st_size!=manifest['archive']['bytes'] or h.hexdigest()!=manifest['archive']['sha256']:
        raise ValueError('Snapshot archive bytes changed')
    destination.mkdir()
    with tarfile.open(archive) as tar:
        seen=set()
        for m in tar:
            rel=str(Path(m.name).relative_to('prefix'))
            if rel not in manifest['files'] or rel in seen or '..' in Path(rel).parts:raise ValueError('Unexpected snapshot archive member')
            seen.add(rel);r=manifest['files'][rel];q=destination/rel;q.parent.mkdir(parents=True,exist_ok=True)
            if r['type']=='link':
                if not m.issym() or m.linkname!=r['target']:raise ValueError('Snapshot archive link differs')
                if not (q.parent/r['target']).resolve().is_relative_to(destination.resolve()):raise ValueError('Escaping snapshot link')
                q.symlink_to(r['target'])
            else:
                if not m.isfile() or m.size!=r['bytes']:raise ValueError('Snapshot archive file differs')
                with tar.extractfile(m) as f,q.open('xb') as out:shutil.copyfileobj(f,out)
                q.chmod(r['mode'])
    verify(destination,manifest);return manifest


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source',type=Path);p.add_argument('--destination',type=Path,required=True)
    p.add_argument('--archive',type=Path);p.add_argument('--receipt',type=Path,required=True)
    p.add_argument('--restore',action='store_true');a=p.parse_args()
    try:
        if a.restore:restore(a.receipt,a.destination)
        else:
            if not a.source or not a.archive:p.error('Creation needs --source and --archive')
            create(a.source,a.destination,a.archive,a.receipt)
    except BaseException:
        # Do not let a fatal copy error wait for other readers blocked in kernel I/O
        # during ThreadPoolExecutor's interpreter-exit join. No child processes here.
        import sys, traceback
        traceback.print_exc();sys.stdout.flush();sys.stderr.flush();os._exit(1)
