#!/usr/bin/env python3
"""Verify a full E033 archive while staging a bounded diagnostics-only subset.

Requires a separately bound exact inventory from completion delivery. Full archive
SHA/MD5 and every physical member/alias still pass the accepted strict reader;
unselected bytes are hashed, never claimed as local backups. No cloud or download
entry point exists here: the authorized controller supplies the priced raw stream.
"""
from contextlib import contextmanager
import json
from pathlib import Path
import sys

sys.path.insert(0,str(Path(__file__).absolute().parent))
import e032_restore as accepted
from e024_coverage import binding


def selected(name,kind):
    """Choose complete new outputs/learning receipts or only new parent features."""
    if kind=='measurements':return name.startswith('work/') and name.endswith(('features.npz','features.json'))
    if kind!='mode':raise ValueError('One explicit collection kind required')
    return (name.startswith('work/select/result/') or name=='work/audit/proof.json'
        or name in {'work/'+stage+'/result/checkpoint.json' for stage in ['teacher','student']}
        or name in {'work/'+stage+'-embed/'+member for stage in ['teacher','student'] for member in ['embeddings.json']}
        or name in ['work/student-embed/embeddings.npz','work/student-graph/result/graph.npz',
                    'work/student-graph/result/graph.json','work/student-graph/result/completed.json',
                    'work/pairs/result/cache/cache.json'])


@contextmanager
def scope(predicate):
    """Scope only selection and the prospectively enlarged logical bound."""
    old=accepted.needed,accepted.LOGICAL
    accepted.needed=predicate;accepted.LOGICAL=8*1024**3
    try:yield
    finally:accepted.needed,accepted.LOGICAL=old


def restore(stream,metadata,expected,inventory,root,kind,reserve=8*1024**3,cap=3*1024**3):
    """Bound staged byte exposure before reading, retaining full stream verification."""
    inventory=Path(inventory);inv=json.loads(inventory.read_text());root=Path(root)
    wanted={n for n in inv['members'] if selected(n,kind)}
    for n,v in inv['aliases'].items():
        if selected(n,kind):wanted.add(v['canonical'])
    staged=sum(inv['members'][n]['bytes'] for n in wanted)+inventory.stat().st_size
    if staged>cap:raise ValueError('Prospective compact staging cap exceeded; no fallback')
    with scope(lambda n:selected(n,kind)):
        result=accepted.stream_restore(stream,metadata,expected,root,binding(inventory),reserve)
    proof=root/'work/restore-admission.json'
    proof.rename(root/'stream-admission.json')
    result.update(compact_staging_predeclared_bytes=staged,local_backup_of_unselected_members=False,
        full_archive_every_member_verified=True)
    return result
