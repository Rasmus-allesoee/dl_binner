"""Collect a hash-bound allowlist of retained E001 diagnostic files, read-only.

Uses only Python's standard library: no tool imports, installs, fitting, feature
extraction or clustering. A fresh output directory preserves earlier collections.
The manifest binds every source path, byte count and SHA256. Source roots can be
relocated explicitly for portable tests; the owner uses the recorded roots.
"""
import argparse
import hashlib
import io
import json
from pathlib import Path, PurePosixPath
import signal
import tarfile
import tempfile
import time


def digest(path):
    """Stream a regular file's SHA256 without loading it into memory."""
    h=hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda:f.read(1024*1024),b''): h.update(chunk)
    return h.hexdigest()


def relative(name):
    """Reject unsafe or ambiguous names before opening source files or tar members."""
    p=PurePosixPath(name)
    if p.is_absolute() or '..' in p.parts or str(p)!=name or not p.parts:
        raise ValueError('Unsafe relative path: '+name)
    return p


def collect(manifest_path, output, vcpus, ram_gb, roots=None):
    """Verify and archive existing bytes; return paths and charged driver metrics.

    Failures retain an incomplete archive and status without publishing a success
    checksum. Inputs are never modified. The caller bounds runtime to 20 minutes.
    """
    if vcpus<1 or ram_gb<=0: raise ValueError('Record actual positive allocation')
    manifest=json.loads(manifest_path.read_text()); roots=roots or manifest['roots']
    members=manifest['files']; seen=set(); total=0
    for item in members:
        relative(item['path']); relative(item['member'])
        if item['member'] in seen: raise ValueError('Duplicate member')
        seen.add(item['member']); total+=item['bytes']
    if total>1024**3: raise ValueError('Collection exceeds the 1 GiB scope ceiling')
    output.mkdir(parents=True,exist_ok=True)
    stage=Path(tempfile.mkdtemp(prefix='e001-diagnostics-',dir=output)); started=time.monotonic()
    archive=stage/'e001-diagnostics.tar.gz'; partial=stage/'e001-diagnostics.partial.tar.gz'
    status={'status':'failed','allocated_vcpus':vcpus,'allocated_ram_gb':ram_gb,
            'manifest_sha256':digest(manifest_path),'requested_files':len(members),'source_bytes':total}
    try:
        with tarfile.open(partial,'w:gz',compresslevel=1) as tar:
            raw=manifest_path.read_bytes(); info=tarfile.TarInfo('manifest.json'); info.size=len(raw); tar.addfile(info,io.BytesIO(raw))
            for index,item in enumerate(members,1):
                root=Path(roots[item['root']]).resolve(); path=root/item['path']
                resolved=path.resolve(strict=True)
                if not resolved.is_relative_to(root) or not resolved.is_file(): raise ValueError('Source escapes recorded root: '+str(path))
                if path.stat().st_size!=item['bytes'] or digest(path)!=item['sha256']: raise ValueError('Source checksum mismatch: '+str(path))
                # Stream exactly the checked bytes and verify again after copying.
                info=tar.gettarinfo(str(resolved),arcname=item['member'])
                with resolved.open('rb') as handle: tar.addfile(info,handle)
                if digest(resolved)!=item['sha256']: raise ValueError('Source changed during collection: '+str(path))
                if index==1 or index%20==0 or index==len(members):
                    print(time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),f'PACKED {index}/{len(members)}',flush=True)
        partial.rename(archive)
        status.update(status='completed',archive_bytes=archive.stat().st_size,archive_sha256=digest(archive))
        (stage/'e001-diagnostics.tar.gz.sha256').write_text(status['archive_sha256']+'  '+archive.name+'\n')
    except BaseException as error:
        status['error']=repr(error); raise
    finally:
        status['elapsed_seconds']=time.monotonic()-started
        status['allocated_core_hours']=vcpus*status['elapsed_seconds']/3600
        (stage/'collection-status.json').write_text(json.dumps(status,indent=2)+'\n')
        print('STATUS:',stage/'collection-status.json',flush=True)
    print('RETURN:',archive,stage/'e001-diagnostics.tar.gz.sha256',flush=True)
    return stage,status


def timeout(signum,frame):
    """Stop a stalled collection without touching source artifacts."""
    raise TimeoutError('20-minute collection limit reached; preserve partial output')


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('manifest',type=Path); p.add_argument('output',type=Path)
    p.add_argument('--vcpus',type=int,required=True); p.add_argument('--ram-gb',type=float,required=True)
    a=p.parse_args(); signal.signal(signal.SIGALRM,timeout); signal.alarm(1200)
    collect(a.manifest,a.output,a.vcpus,a.ram_gb)
