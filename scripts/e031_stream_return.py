#!/usr/bin/env python3
"""Verify an E031 private return once while retaining compact review members.

The caller provides a generation-bound byte stream, independently read metadata,
and the native SHA256 receipt. Every physical member and exact-byte alias is
verified. Large native arrays remain in the private archive; this is selective
restoration, not a claim that omitted members have local copies. No cloud write,
science, extraction fallback, or numerical tolerance change is performed.
"""
import base64
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import shutil
import tarfile


class BoundReader:
    """Hash/count the exact compressed stream and refuse bytes beyond admission."""
    def __init__(self, stream, maximum):
        self.stream, self.maximum, self.count = stream, maximum, 0
        self.sha, self.md5 = hashlib.sha256(), hashlib.md5()

    def read(self, size=-1):
        value = self.stream.read(size)
        self.count += len(value)
        if self.count > self.maximum:
            raise ValueError('Compressed stream exceeds admitted bytes')
        self.sha.update(value)
        self.md5.update(value)
        return value


def compact(name):
    """Select closed controls and new-output review data, never large native banks."""
    if name.startswith('evidence/'):
        return True
    if not name.startswith('work/'):
        return False
    tail = name.rsplit('/', 1)[-1]
    return (name in ['work/used-inputs-after.json', 'work/barrier/proof.json']
            or tail in ['done.json', 'proof.json', 'query-neighbors.json', 'bridge.json',
                        'verified-reuse.json', 'completed.json', 'accounting.json']
            or '/export/' in name
            or tail.endswith('-partition.json') or tail.endswith('-choices.json')
            or tail in ['alternatives.json', 'hierarchy.json'])


def stream_restore(stream, metadata, expected, destination, reserve=6*1024**3, existing=None):
    """Check complete transport/member bytes, then expose compact exact aliases.

    Partial staging is preserved on failure and never receives an admission.
    Storage is checked during member writes and restoration is refused if a
    planned compact member would consume the filesystem reserve.
    """
    root = Path(destination)
    root.mkdir(parents=True, exist_ok=False)
    if int(metadata['size']) != expected['bytes'] or expected['bytes'] > 2*1024**3:
        raise ValueError('Object/native archive size differs')
    raw = BoundReader(stream, expected['bytes'])
    seen, bindings, inventory, logical, local = set(), {}, None, 0, 0
    wanted = set()
    with tarfile.open(fileobj=raw, mode='r|gz') as archive:
        for member in archive:
            path = PurePosixPath(member.name)
            if (path.is_absolute() or '..' in path.parts or str(path) != member.name
                    or not member.isfile() or member.name in seen):
                raise ValueError('Unsafe/nonregular/duplicate return member')
            if not seen and member.name != 'inventory.json':
                raise ValueError('Inventory must be first')
            if member.size < 0 or logical + member.size > 4*1024**3:
                raise ValueError('Logical return cap exceeded')
            if member.name == 'inventory.json' and member.size > 64*1024**2:
                raise ValueError('Inventory cap exceeded')
            seen.add(member.name)
            handle = archive.extractfile(member)
            h, count, chunks = hashlib.sha256(), 0, []
            keep = member.name == 'inventory.json' or member.name in wanted
            target = root/member.name
            writer = None
            if keep:
                target.parent.mkdir(parents=True, exist_ok=True)
                old = Path(existing)/member.name if existing is not None else None
                prior = None
                if old is not None and old.is_file() and not old.is_symlink() and old.stat().st_size == member.size:
                    check = hashlib.sha256()
                    with old.open('rb') as handle_old:
                        for block in iter(lambda: handle_old.read(1024**2), b''):
                            check.update(block)
                    prior = dict(bytes=member.size, sha256=check.hexdigest())
                wanted_binding = inventory['members'].get(member.name) if inventory else None
                if prior is not None and prior == wanted_binding:
                    os.link(old, target)
                else:
                    if shutil.disk_usage(root).free - member.size < reserve:
                        raise RuntimeError('Local reserve cannot admit compact member')
                    writer = target.open('xb')
            try:
                for value in iter(lambda: handle.read(1024**2), b''):
                    h.update(value); count += len(value)
                    if writer:
                        if shutil.disk_usage(root).free - len(value) < reserve:
                            raise RuntimeError('Local free-space reserve reached')
                        writer.write(value)
                    if member.name == 'inventory.json':
                        chunks.append(value)
            finally:
                if writer:
                    writer.close()
            logical += count
            if count != member.size:
                raise ValueError('Truncated member')
            measured = dict(bytes=count, sha256=h.hexdigest())
            bindings[member.name] = measured
            if member.name == 'inventory.json':
                inventory = json.loads(b''.join(chunks))
                wanted = {n for n in inventory['members'] if compact(n)}
                wanted.update(v['canonical'] for n, v in inventory['aliases'].items() if compact(n))
            elif inventory['members'].get(member.name) != measured:
                raise ValueError('Return member bytes differ: '+member.name)
            if keep:
                local += count
    for _ in iter(lambda: raw.read(1024**2), b''):
        pass
    measured = dict(bytes=raw.count, sha256=raw.sha.hexdigest())
    if measured != expected or (metadata.get('md5_hash') and
            base64.b64encode(raw.md5.digest()).decode() != metadata['md5_hash']):
        raise ValueError('Whole archive/object digest differs')
    if seen != set(inventory['members']) | {'inventory.json'}:
        raise ValueError('Incomplete member set')
    retained = {n.removeprefix('work/') for n in inventory['members'] if n.startswith('work/')}
    aliases = {n.removeprefix('work/') for n in inventory['aliases']}
    omitted = set(inventory['omitted_retained_on_disk'])
    if (retained & aliases or retained & omitted or aliases & omitted
            or set(inventory['all_work_members']) != retained | aliases | omitted):
        raise ValueError('Full work inventory does not close')
    for name in retained:
        if inventory['members']['work/'+name] != inventory['all_work_members'][name]:
            raise ValueError('Work binding differs')
    for name, value in inventory['aliases'].items():
        for candidate in [name, value['canonical']]:
            path=PurePosixPath(candidate)
            if path.is_absolute() or '..' in path.parts or str(path)!=candidate:
                raise ValueError('Unsafe exact-byte alias path')
        b = {k: value[k] for k in ['bytes', 'sha256']}
        if (name in inventory['members'] or inventory['members'].get(value['canonical']) != b
                or inventory['all_work_members'].get(name.removeprefix('work/')) != b):
            raise ValueError('Invalid exact-byte alias')
        if compact(name):
            target = root/name; target.parent.mkdir(parents=True, exist_ok=True)
            os.link(root/value['canonical'], target)
    for name, value in inventory['omitted_retained_on_disk'].items():
        if ({k: value[k] for k in ['bytes', 'sha256']} != inventory['all_work_members'][name]
                or not value['reason']):
            raise ValueError('Invalid original on-disk omission')
    proof = dict(status='PASS', archive=measured, generation=metadata['generation'],
                 every_member_verified=True, regular_members=len(seen), aliases=len(aliases),
                 logical_member_bytes=logical, selectively_restored_physical_bytes=local,
                 local_free_after_bytes=shutil.disk_usage(root).free,
                 no_complete_local_compressed_copy=True, new_science=False,
                 omitted_private_members_not_local_backups=True)
    (root/'stream-verification.json').write_text(json.dumps(proof, indent=2)+'\n')
    return proof
