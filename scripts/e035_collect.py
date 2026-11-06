#!/usr/bin/env python3
"""Complete cross-slice exact-byte collection, with explicit alias closure.

Group identical bytes before deterministic bounded slicing. Every work member
belongs to exactly one slice. Large regenerable database/query intermediates are
external inputs, inventoried separately; unique compact classifier evidence must
already be staged in work. There is no oversized or omission fallback.
"""
import json
import os
from pathlib import Path
import sys
import tarfile

sys.path.insert(0,str(Path(__file__).absolute().parent))
from e024_coverage import binding,write
import e033_collect as closed

CAP=2*1024**3;LOGICAL=8*1024**3;AGGREGATE=12*1024**3;PHYSICAL=int(1.5*1024**3)


def pack(work,evidence,output,physical_limit=PHYSICAL):
    """Pack all closed files and aliases, then independently verify every slice."""
    work,evidence,out=map(lambda p:Path(p).absolute(),[work,evidence,output])
    if work in out.parents or evidence in out.parents or out==work or out==evidence:raise ValueError('Return destination overlaps inputs')
    out.mkdir(parents=True,exist_ok=False);groups={};all_members={}
    for p in sorted(work.rglob('*')):
        if p.is_symlink():raise ValueError('Scientific return symlinks refused')
        if not p.is_file():continue
        name=str(p.relative_to(work));b=binding(p);all_members[name]=b
        groups.setdefault((b['bytes'],b['sha256']),[]).append(name)
    if not all_members:raise ValueError('Empty scientific return')
    bins=[];current=[];size=0
    for key,names in groups.items():
        if key[0]>physical_limit:raise ValueError('Individual member exceeds prepared physical slice; retain it, no fallback')
        if current and size+key[0]>physical_limit:bins.append(current);current=[];size=0
        current.append(names);size+=key[0]
    if current:bins.append(current)
    results=[];compressed=0
    old=closed.CAP,closed.LOGICAL;closed.CAP,closed.LOGICAL=CAP,LOGICAL
    try:
        for i,groups_in_bin in enumerate(bins):
            staging=out/('stage-%03d'%i);staging.mkdir()
            for names in groups_in_bin:
                for name in names:
                    target=staging/name;target.parent.mkdir(parents=True,exist_ok=True);os.link(work/name,target)
            destination=out/('slice-%03d'%i);r=closed.pack(staging,evidence,destination)
            compressed+=r['archive']['bytes']
            if compressed>AGGREGATE:raise ValueError('Aggregate return limit exceeded; no omission fallback')
            results.append(dict(folder=destination.name,archive=r['archive'],inventory=binding(destination/'inventory.json')))
        write(out/'collection.json',dict(kind='E035 complete scientific slices',version=1,slices=results,
            all_work_members=all_members,omitted_work_members={},aggregate_compressed_bytes=compressed,
            limits=dict(slice_compressed=CAP,slice_logical=LOGICAL,aggregate_compressed=AGGREGATE,physical_per_slice=physical_limit)))
        verify(out)
    finally:closed.CAP,closed.LOGICAL=old
    return json.loads((out/'collection.json').read_text())


def verify(root):
    """Recheck all archived regular bytes/aliases and their complete global union."""
    root=Path(root);m=json.loads((root/'collection.json').read_text());merged={};members={};aliases={};total=0
    old=closed.CAP,closed.LOGICAL;closed.CAP,closed.LOGICAL=CAP,LOGICAL
    try:
        for record in m['slices']:
            name=Path(record['folder'])
            if name.is_absolute()or len(name.parts)!=1:raise ValueError('Unsafe return slice name')
            at=root/name
            if binding(at/'inventory.json')!=record['inventory']:raise ValueError('Return inventory bytes differ')
            closed.verify(at/'e033-evidence.tar.gz',record['archive']);total+=record['archive']['bytes']
            inv=json.loads((at/'inventory.json').read_text())
            for n,b in inv['all_work_members'].items():
                if n in merged:raise ValueError('Scientific member appears in multiple slices')
                merged[n]=b
            for key,target in [('members',members),('aliases',aliases)]:
                for n,b in inv[key].items():
                    if n in target and target[n]!=b:raise ValueError('Cross-slice member evidence differs')
                    target[n]=b
        if merged!=m['all_work_members']or m['omitted_work_members'] or total!=m['aggregate_compressed_bytes']or total>AGGREGATE:raise ValueError('Incomplete global return closure')
    finally:closed.CAP,closed.LOGICAL=old
    global_inventory=dict(kind='E035 verified global slice union',members=members,aliases=aliases,all_work_members=merged,omitted_retained_on_disk={})
    for name in ['global-inventory.json','inventory.json']:
        target=root/name
        if target.exists():
            if json.loads(target.read_text())!=global_inventory:raise ValueError('Existing verified global inventory differs')
        else:write(target,global_inventory)
    return dict(status='PASS',members=len(merged),slices=len(m['slices']),compressed_bytes=total,all_aliases_verified=True)


def restore(root,output):
    """Exercise the actual archive-to-reader path with regular bytes and hardlinks.

    Full restoration is for tiny fixtures or an admitted native disk. A later
    compact desktop reviewer can stream-verify the same slices and materialize
    only required members under the separately checked local-space envelope.
    """
    root=Path(root);out=Path(output);out.mkdir(parents=True,exist_ok=False);verify(root)
    collection=json.loads((root/'collection.json').read_text())
    for record in collection['slices']:
        at=root/record['folder'];inv=json.loads((at/'inventory.json').read_text())
        with tarfile.open(at/'e033-evidence.tar.gz','r:gz')as archive:
            for member in archive:
                if member.name=='inventory.json':continue
                p=Path(member.name)
                if p.is_absolute()or '..'in p.parts or not member.isfile()or member.name not in inv['members']:raise ValueError('Unexpected restored member')
                target=out/p;target.parent.mkdir(parents=True,exist_ok=True)
                if target.exists():
                    if binding(target)!=inv['members'][member.name]:raise ValueError('Restored duplicate evidence differs')
                    continue
                with archive.extractfile(member)as source,target.open('xb')as dest:
                    for b in iter(lambda:source.read(1024**2),b''):dest.write(b)
                if binding(target)!=inv['members'][member.name]:raise ValueError('Restored member checksum differs')
        for n,b in inv['aliases'].items():
            target=out/n;canonical=out/b['canonical'];target.parent.mkdir(parents=True,exist_ok=True)
            if target.exists()or not canonical.is_file():raise ValueError('Restored alias contract differs')
            os.link(canonical,target)
            if binding(target)!={k:b[k]for k in ['bytes','sha256']}:raise ValueError('Restored alias bytes differ')
    actual={str(p.relative_to(out/'work')):binding(p)for p in (out/'work').rglob('*')if p.is_file()}
    if actual!=collection['all_work_members']:raise ValueError('Restored full scientific axis differs')
    return out


def compact_classification(source,destination,allow_failure=False):
    """Stage actual aggregate/per-ORF evidence, declaring regenerable exclusions.

    Preserve the query index, raw/complete parent calls, normalized annotations,
    native reducer/ORF headers and per-ORF taxonomy/alignment weight records. Query
    DNA/sequence DB/search intermediates are regenerable original-input derivatives;
    their closed inventory remains. Failures keep the entire original source too.
    """
    source=Path(source).absolute();out=Path(destination).absolute();out.mkdir(parents=True,exist_ok=False);omitted={};kept={}
    for p in sorted(source.rglob('*')):
        if p.is_symlink():
            # MMseqs2 creates tmp/latest and internal header aliases. The actual
            # regular target is inventoried under its real relative name.
            if not p.resolve().is_relative_to(source):raise ValueError('Classifier alias escapes original work')
            if p.is_dir():continue
        if not p.is_file():continue
        n=str(p.relative_to(source));b=binding(p.resolve())
        select=(n.startswith('annotations/')or n=='query/index.json'or p.suffix in ['.log']or n.endswith('.exit.json')
                or n in ['provenance.json','completed.json','taxonomy.tsv','complete.tsv','complete.completion.json','queryDB.lookup','queryDB.index','queryDB.dbtype']
                or p.name.startswith(('orfs_h_swapped','orfs_tax','orfs_aa_h'))or p.suffix=='.sh')
        if select:
            target=out/n;target.parent.mkdir(parents=True,exist_ok=True);os.link(p.resolve(),target);kept[n]=b
        else:omitted[n]=dict(b,reason='Regenerable native input/search intermediate; original DNA/reference bytes and exact producer remain bound')
    complete={'completed.json','taxonomy.tsv','complete.completion.json','annotations/completed.json'}.issubset(kept)
    if not complete and not allow_failure:raise ValueError('Incomplete native classifier result')
    write(out/'compact-stage.json',dict(status='PASS'if complete else'FAILED_INPUT_PRESERVED',kept=kept,regenerable_excluded=omitted,
        native_scientific_completion=complete,
        raw_annotations_and_per_ORF_context_retained=True,symlinks_not_substituted_for_missing_regular_bytes=True))
    return kept
