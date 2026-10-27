#!/usr/bin/env python3
"""Seal E024 compact evidence with exact-byte aliases and explicit bulk omissions.

No upload occurs here. Index/reference/exported DNA stay on the work disk and
are not backed up by this inventory. Newly acquired raw reads must already have
verified removal receipts, or remain explicitly omitted in a failure return.
The existing independently tested E023 verifier checks every archived member,
alias, omission and full-work inventory relationship under the same 2/6 GiB caps.
"""
import json
from pathlib import Path
import sys
import tarfile

sys.path.insert(0,str(Path(__file__).absolute().parent))
from e024_coverage import binding, write
from e023_collect import verify, CAP, LOGICAL_CAP, CappedWriter


def pack(work, evidence, output, ceiling=CAP, allow_incomplete=False):
    """Inventory all regular fresh files and verify the complete bounded archive."""
    work, evidence, output = map(Path,(work,evidence,output))
    if not 0 < ceiling <= CAP or output == work or work in output.parents:
        raise ValueError('Separate collection destination and frozen compressed cap required')
    output.mkdir(parents=True,exist_ok=False)
    files, all_work, omitted, aliases, seen = {}, {}, {}, {}, {}
    for p in sorted(work.rglob('*')):
        if p.is_symlink():
            raise ValueError('Result artifact links refused')
        if not p.is_file():
            continue
        name, b = str(p.relative_to(work)), binding(p)
        all_work[name] = b
        bulk = (p.suffix in ['.fa','.fna','.fasta','.sti'] or p.name == 'raw.fq.gz'
                or 'native-cache' in p.parts or 'workflow-source-cache' in p.parts)
        if bulk:
            if p.name == 'raw.fq.gz' and not allow_incomplete:
                raise ValueError('Completed collection requires explicit verified raw release')
            omitted[name] = dict(**b,reason='Retained regenerable index/reference/DNA/cache or failed raw; inventory is not a backup')
            continue
        key = 'work/'+name
        content = (b['bytes'],b['sha256'])
        if content in seen:
            aliases[key] = dict(**b,canonical=seen[content])
        else:
            seen[content] = key
            files[key] = p
    for p in sorted(evidence.rglob('*')):
        if p.is_symlink():
            raise ValueError('Evidence links refused')
        if p.is_file():
            files['evidence/'+str(p.relative_to(evidence))] = p
    members = {k:binding(p) for k,p in files.items()}
    logical = sum(v['bytes'] for v in members.values())
    if logical > LOGICAL_CAP or len(members) > 20000:
        raise ValueError('Bounded logical/member inventory exceeded; no fallback')
    inv = dict(kind='E024 measured-depth information exact-byte return',members=members,
               all_work_members=all_work,aliases=aliases,omitted_retained_on_disk=omitted,
               incomplete_failure_evidence=allow_incomplete,
               shared_inputs='Original E014/E019/E023 data/vector/marker caches are not recopied or backed up here',
               compressed_hard_ceiling_bytes=ceiling,logical_cap_bytes=LOGICAL_CAP)
    write(output/'inventory.json',inv)
    if (output/'inventory.json').stat().st_size > 64*1024**2 or logical+(output/'inventory.json').stat().st_size > LOGICAL_CAP:
        raise ValueError('Manifest-inclusive logical cap exceeded')
    archive = output/'e024-evidence.tar.gz'
    partial = output/'e024-evidence.tar.gz.partial'
    with partial.open('xb') as f:
        wrapped = CappedWriter(f,ceiling)
        with tarfile.open(fileobj=wrapped,mode='w:gz') as tar:
            tar.add(output/'inventory.json',arcname='inventory.json',recursive=False)
            for name,p in sorted(files.items()):
                tar.add(p,arcname=name,recursive=False)
    partial.rename(archive)
    result = verify(archive)
    result.update(scope='E024 compact new evidence; omitted byte inventories are not backups',
                  raw_BAM_in_compact_archive=False,
                  remote_primary_BAM_receipts=len(list((work/'samples').glob('*/mapped/alignment-retained.json'))),
                  remote_primary_BAM_scope='Separately retained exact GCS objects, full byte/readback/decode in archived receipts; no BAM internet export',
                  compressed_cap_bytes=ceiling)
    write(output/'collection.json',result)
    (output/'e024-evidence.tar.gz.sha256').write_text(binding(archive)['sha256']+'  e024-evidence.tar.gz\n')
    return result


if __name__ == '__main__':
    import argparse
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--work',type=Path,required=True)
    parser.add_argument('--evidence',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--allow-incomplete',action='store_true')
    a=parser.parse_args()
    print(json.dumps(pack(a.work,a.evidence,a.output,allow_incomplete=a.allow_incomplete)),flush=True)
