#!/usr/bin/env python3
"""Bound the exact new cross-contig learning return, explicitly omitting only identified bulk.

All counts/coordinates remain on the VM with their manifests, not backed up by
inventory hashes. Every checkpoint/embedding/graph/partition/decision/history and
full-axis assignment is returned. DNA is emitted once and retained in place.
"""
import argparse
import hashlib
import json
from pathlib import Path
import sys
import tarfile

sys.path.insert(0, str(Path(__file__).absolute().parent))
from e014_collect import binding, member_path

CAP = 2*1024**3
LOGICAL_CAP = 6*1024**3
MANIFEST_CAP = 64*1024**2


def select(work, allow_incomplete=False):
    """Inventory every fresh member; retain evidence or explicitly name omitted bulk."""
    work = Path(work)
    all_files, files, aliases, omitted = {}, {}, {}, {}
    for p in sorted(work.rglob('*')):
        if p.is_symlink():
            raise ValueError('Scientific result link refused')
        if not p.is_file():
            continue
        k = str(p.relative_to(work))
        b = binding(p)
        all_files[k] = b
        if '/frozen/' in '/'+k and p.suffix=='.npy':
            if p.name=='vectors.npy':
                omitted[k]=dict(**b,reason='Original immutable full GLM view vectors hardlinked natively; complete bank manifest and view provenance returned, not backed up by this hash')
            elif p.name in ['rows.npy','ids.npy','quality.npy','usable.npy']:files['work/'+k]=p
            else:raise ValueError('Unknown frozen view-bank member')
        elif '/tokens/'  in '/'+k and p.suffix == '.npy':
            if p.name not in ['counts.npy', 'coordinates.npy', 'flipped.npy', 'rows.npy']:
                raise ValueError('Unknown context bulk member')
            omitted[k] = dict(**b, reason='Indexed context counts/coordinates retained on disk; manifest returned')
        elif p.suffix in ['.fa', '.fna', '.fasta']:
            omitted[k] = dict(**b, reason='Full accounted DNA retained on disk')
        elif (k.startswith('.snakemake/') or p.suffix in ['.json', '.tsv', '.log', '.jsonl']
                or p.name in ['embeddings.npz', 'graph.npz', 'reference.npz', 'checkpoint.pt', 'pairs.npz', 'calibration.npz']):
            files['work/'+k] = p
        else:
            raise ValueError('Unexpected unaccounted result: '+k)
    for key in list(files):
        if key.endswith('/train/reference.npz'):
            canonical = key.removesuffix('/train/reference.npz')+'/embeddings.npz'
            if canonical not in files or binding(files[key]) != binding(files[canonical]):
                if allow_incomplete:
                    # A failed/missing reload is evidence, never a byte-identical
                    # alias. Preserve whichever physical files exist separately.
                    continue
                raise ValueError('Reference alias is not exact bytes')
            aliases[key] = dict(canonical=canonical, **binding(files[key]))
            del files[key]
    return files, all_files, aliases, omitted


def verify(archive, expected_archive=None):
    """Stream-check every physical member/alias and all inventory/omission relations."""
    archive = Path(archive)
    if archive.stat().st_size > CAP or (expected_archive and binding(archive) != expected_archive):
        raise ValueError('Return archive bytes/cap differ')
    seen, inventory, logical = set(), None, 0
    with tarfile.open(archive, 'r:gz') as a:
        for m in a:
            member_path(Path('/verification-only'), m.name)
            if m.size>LOGICAL_CAP or logical+m.size>LOGICAL_CAP or not m.isfile() or m.name in seen:
                raise ValueError('Duplicate/nonregular archive member')
            if not seen and m.name != 'inventory.json':
                raise ValueError('Inventory must be first')
            if m.name=='inventory.json'and m.size>MANIFEST_CAP:
                raise ValueError('Return inventory exceeds bounded manifest cap')
            seen.add(m.name)
            f = a.extractfile(m)
            sha, count, chunks = hashlib.sha256(), 0, []
            for value in iter(lambda: f.read(1024**2), b''):
                sha.update(value)
                count += len(value)
                if m.name == 'inventory.json':
                    chunks.append(value)
            logical += count
            if m.name == 'inventory.json':
                inventory = json.loads(b''.join(chunks))
            elif inventory['members'].get(m.name) != dict(bytes=count, sha256=sha.hexdigest()):
                raise ValueError('Return member bytes differ')
    if seen != set(inventory['members']) | {'inventory.json'}:
        raise ValueError('Incomplete archive inventory')
    retained = {k.removeprefix('work/') for k in inventory['members'] if k.startswith('work/')}
    aliases = {k.removeprefix('work/') for k in inventory['aliases']}
    omitted = set(inventory['omitted_retained_on_disk'])
    if (retained & aliases or retained & omitted or aliases & omitted
            or set(inventory['all_work_members']) != retained | aliases | omitted):
        raise ValueError('Complete work accounting differs')
    for key in retained:
        if inventory['members']['work/'+key] != inventory['all_work_members'][key]:
            raise ValueError('Work member binding differs')
    for key, value in inventory['aliases'].items():
        b = {k: value[k] for k in ['bytes', 'sha256']}
        if key in inventory['members'] or inventory['members'].get(value['canonical']) != b or inventory['all_work_members'].get(key.removeprefix('work/')) != b:
            raise ValueError('Invalid exact-byte alias')
    for key, value in inventory['omitted_retained_on_disk'].items():
        if {k: value[k] for k in ['bytes', 'sha256']} != inventory['all_work_members'][key] or not value['reason']:
            raise ValueError('Invalid omission binding/reason')
    return dict(status='SUCCESS', archive=binding(archive), regular_members=len(seen),
        logical_member_bytes=logical, every_member_verified=True, aliases=inventory['aliases'],
        omitted_retained_on_disk=inventory['omitted_retained_on_disk'])


class CappedWriter:
    """Enforce exact compressed bytes including gzip footer before any overshoot."""
    def __init__(self,raw,ceiling):self.raw=raw;self.ceiling=ceiling;self.count=0
    def write(self,data):
        if self.count+len(data)>self.ceiling:raise ValueError('Compressed return cap exceeded')
        n=self.raw.write(data);self.count+=n;return n
    def __getattr__(self,name):return getattr(self.raw,name)


def pack(work, evidence, output, ceiling=CAP, allow_incomplete=False):
    """Refuse an impossible manifest-inclusive return before writing its archive."""
    work, evidence, output = map(Path, [work, evidence, output])
    output.mkdir(exist_ok=False)
    files, all_files, aliases, omitted = select(work, allow_incomplete)
    for p in sorted(evidence.rglob('*')):
        if p.is_symlink():
            raise ValueError('Evidence link refused')
        if p.is_file():
            files['evidence/'+str(p.relative_to(evidence))] = p
    members = {k: binding(p) for k, p in files.items()}
    logical = sum(b['bytes'] for b in members.values())
    inv = dict(kind='E022 exact-byte new-result return', members=members, all_work_members=all_files,
        aliases=aliases, omitted_retained_on_disk=omitted,
        incomplete_failure_evidence=allow_incomplete,
        shared_inputs='Original E014/E011/E019/E021 inputs plus accepted runtime, named in input/reuse locks; not backed up here')
    # Reserve a full MiB for manifest expansion in addition to actual inventory,
    # pessimistic DEFLATE overhead and conservative per-member tar headers.
    manifest_size = len(json.dumps(inv, indent=2, sort_keys=True).encode())+1024**2
    upper = logical+logical//1000+2048*len(members)+manifest_size+manifest_size//1000+4096
    if logical>LOGICAL_CAP or ceiling>CAP or ceiling<=0:
        raise ValueError('Logical inventory or compressed ceiling exceeds frozen scope')
    inv['logical_member_bytes_before_inventory']=logical
    inv['compressed_hard_ceiling_bytes']=ceiling
    inv['uncompressed_plus_overhead_bound_bytes']=upper
    manifest = output/'inventory.json'
    manifest.write_text(json.dumps(inv, indent=2, sort_keys=True)+'\n')
    if manifest.stat().st_size>MANIFEST_CAP or logical+manifest.stat().st_size>LOGICAL_CAP:
        raise ValueError('Manifest-inclusive logical inventory cap exceeded')
    archive = output/'e022-evidence.tar.gz';partial=archive.with_suffix('.gz.partial')
    with partial.open('xb')as raw:
        wrapped=CappedWriter(raw,ceiling)
        with tarfile.open(fileobj=wrapped,mode='w:gz')as a:
            a.add(manifest,arcname='inventory.json',recursive=False)
            for key,p in sorted(files.items()):a.add(p,arcname=key,recursive=False)
    partial.rename(archive)
    result = verify(archive)
    result.update(uncompressed_plus_overhead_bound_bytes=upper, compressed_hard_ceiling_bytes=ceiling, planned_science_fits=1,
        incomplete_failure_evidence=allow_incomplete,
        omitted_bytes_not_backed_up=True)
    (output/'collection.json').write_text(json.dumps(result, indent=2)+'\n')
    (output/'e022-evidence.tar.gz.sha256').write_text(result['archive']['sha256']+'  e022-evidence.tar.gz\n')
    return result


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--work', type=Path, required=True)
    p.add_argument('--evidence', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--allow-incomplete', action='store_true', help='Failed-stage evidence only; keep nonidentical/missing reload counterparts physical, without aliases')
    a = p.parse_args()
    print(json.dumps(pack(a.work, a.evidence, a.output, allow_incomplete=a.allow_incomplete)), flush=True)
