"""Small byte-bound E009 helpers; no scientific work occurs on import.

Paths and receipts are explicit. Existing files are never silently repaired or
overwritten; cache reuse needs an intact receipt and a caller's resume request.
"""
import gzip
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import shutil
import tarfile
import time
import urllib.request
import zipfile


def binding(path):
    """Return size/SHA256 of one regular file, streaming its original bytes."""
    path = Path(path)
    if path.is_symlink() or not path.is_file():
        raise ValueError(f'Missing or linked regular file: {path}')
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(chunk)
    return {'bytes': path.stat().st_size, 'sha256': digest.hexdigest()}


def write_json(path, data):
    """Exclusively write finite JSON; refuse an existing record."""
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x') as out:
        json.dump(data, out, indent=2, sort_keys=True, allow_nan=False)
        out.write('\n')


def fasta(path):
    """Stream nonempty unique-ID IUPAC FASTA records, preserving DNA/ID order."""
    path = Path(path)
    opener = gzip.open if path.suffix == '.gz' else open
    seen, ident, pieces = set(), None, []
    with opener(path, 'rt', encoding='ascii') as stream:
        for line in stream:
            line = line.strip()
            if not line: continue
            if line.startswith('>'):
                if ident is not None:
                    if not pieces: raise ValueError(f'Empty FASTA record: {ident}')
                    yield ident, ''.join(pieces)
                fields = line[1:].split()
                if not fields or fields[0] in seen: raise ValueError('Empty/duplicate FASTA ID')
                ident = fields[0]; seen.add(ident); pieces = []
            else:
                if ident is None or set(line.upper()) - set('ACGTRYSWKMBDHVN'):
                    raise ValueError('Invalid FASTA DNA or sequence before header')
                pieces.append(line.upper())
    if ident is not None:
        if not pieces: raise ValueError(f'Empty FASTA record: {ident}')
        yield ident, ''.join(pieces)
    if not seen: raise ValueError('Empty FASTA')


def safe_name(name):
    """Reject traversal, absolute paths, backslashes and empty archive names."""
    path = PurePosixPath(name)
    if not path.parts or path.is_absolute() or '..' in path.parts or '\\' in name:
        raise ValueError(f'Unsafe archive member: {name}')
    return path


def extract(archive, destination, strip_root=False, max_bytes=50_000_000_000):
    """Extract regular tar/zip members only into a fresh directory and record bytes.

    Reject links/devices, duplicates and traversal before writing any member.
    Never call a downloaded installer or Python source here.
    """
    archive, destination = Path(archive), Path(destination)
    if destination.exists(): raise ValueError('Extraction destination must be fresh')
    zipped = zipfile.is_zipfile(archive)
    container = zipfile.ZipFile(archive) if zipped else tarfile.open(archive)
    planned, names, roots, total = [], set(), set(), 0
    with container:
        for member in container.infolist() if zipped else container.getmembers():
            name = member.filename if zipped else member.name
            rel = safe_name(name)
            roots.add(rel.parts[0])
            if zipped:
                mode = member.external_attr >> 16
                if (mode & 0o170000) not in (0,0o100000,0o040000):raise ValueError('Nonregular ZIP member')
                directory, size = member.is_dir(), member.file_size
            else:
                if not (member.isfile() or member.isdir()): raise ValueError('Nonregular tar member')
                directory, size = member.isdir(), member.size
            if strip_root: rel = PurePosixPath(*rel.parts[1:])
            if directory: continue
            if not rel.parts or str(rel) in names: raise ValueError('Duplicate/empty archive file')
            names.add(str(rel)); total += size
            if total > max_bytes: raise ValueError('Archive expands beyond declared space')
            planned.append((member, rel, size))
        if strip_root and len(roots) != 1: raise ValueError('Source archive lacks a single root')
        for name in names:
            if any(str(p) in names for p in PurePosixPath(name).parents):
                raise ValueError('Archive file/directory path collision')
        parent=destination.parent
        while not parent.exists():parent=parent.parent
        if total>shutil.disk_usage(parent).free:raise ValueError('Archive requires more free space; provision storage first')
        destination.mkdir(parents=True)
        for member, rel, size in planned:
            target = destination / str(rel); target.parent.mkdir(parents=True, exist_ok=True)
            source = container.open(member) if zipped else container.extractfile(member)
            with source, target.open('xb') as out: shutil.copyfileobj(source, out)
            if target.stat().st_size != size: raise ValueError('Truncated archive member')
            if not zipped: target.chmod(member.mode & 0o777)
    return {'archive': binding(archive), 'files': len(planned), 'logical_bytes': total}


def acquire(spec, destination, resume=False):
    """Download one pinned object atomically or verify explicitly requested reuse.

    A publisher lacking SHA256 is a *provisional acquisition*, never an admitted
    scientific input. Returned receipts bind actual bytes for later review/freeze.
    Size and object ETag can constrain transport, but an ETag is not a checksum.
    """
    destination = Path(destination); receipt = destination.with_name(destination.name + '.receipt.json')
    if destination.exists() or receipt.exists():
        if not resume or not destination.is_file() or not receipt.is_file():
            raise ValueError('Existing/partial acquisition needs intact receipt and explicit resume')
        old = json.loads(receipt.read_text())
        if old['spec'] != spec or old['file'] != binding(destination):
            raise ValueError('Acquisition bytes/spec changed; preserve and inspect')
        return old
    destination.parent.mkdir(parents=True, exist_ok=True)
    partial = destination.with_name(destination.name + '.partial')
    if partial.exists(): raise ValueError('Preserve partial download; choose a fresh destination')
    headers = {}
    if spec.get('etag'): headers['If-Match'] = '"'+spec['etag'].strip('"')+'"'
    request = urllib.request.Request(spec['url'], headers=headers)
    with urllib.request.urlopen(request, timeout=60) as response, partial.open('xb') as out:
        if getattr(response, 'status', None) not in (None, 200): raise ValueError('Not a complete object response')
        observed_headers = dict(response.headers)
        if spec.get('etag') and response.headers.get('ETag', '').strip('"') != spec['etag'].strip('"'):
            raise ValueError('Remote object identity changed')
        size = 0; last_report = time.monotonic()
        print('DLBINNER WORK_PROGRESS_JSON='+json.dumps({'work_key':str(destination),'completed_bytes':0}),flush=True)
        for chunk in iter(lambda: response.read(1024 * 1024), b''):
            size += len(chunk)
            if size > spec.get('max_bytes', spec.get('bytes') or 10_000_000_000):
                raise ValueError('Download exceeds declared provisioning allowance')
            out.write(chunk)
            if time.monotonic()-last_report>=5:
                print('DLBINNER WORK_PROGRESS_JSON='+json.dumps({'work_key':str(destination),'completed_bytes':size}),flush=True)
                last_report=time.monotonic()
        print('DLBINNER WORK_PROGRESS_JSON='+json.dumps({'work_key':str(destination),'completed_bytes':size}),flush=True)
    actual = binding(partial)
    if spec.get('bytes') is not None and actual['bytes'] != spec['bytes']:
        raise ValueError('Downloaded size differs')
    if spec.get('sha256') and actual['sha256'] != spec['sha256']:
        raise ValueError('Downloaded SHA256 differs')
    partial.rename(destination)
    value = {'spec': spec, 'file': actual, 'headers': observed_headers,
             'admitted_scientific_input': False, 'publisher_checksum_verified': bool(spec.get('sha256'))}
    write_json(receipt, value)
    return value


def tree_binding(root):
    """Bind all regular dependency files and link targets without modifying a prefix."""
    root = Path(root); files = {}
    for path in sorted(root.rglob('*')):
        if path.is_file():
            value = binding(path.resolve() if path.is_symlink() else path)
            if path.is_symlink(): value['link'] = os.readlink(path)
            files[str(path.relative_to(root))] = value
    return {'files': len(files), 'bytes': sum(x['bytes'] for x in files.values()),
            'tree_sha256': hashlib.sha256(json.dumps(files, sort_keys=True).encode()).hexdigest()}
