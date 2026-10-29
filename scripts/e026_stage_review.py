#!/usr/bin/env python3
"""Verify every compact return byte, then stage only one unit's needed evidence.

No download/cloud call, truth or scientific execution occurs. Raw recruitment
journals remain in the verified archive for streaming inspection; omitted FASTAs
are only native locators, not a backup. External accepted inputs use separate
byte-bound review mappings, never rewritten native receipts.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import sys
import tarfile

sys.path.insert(0, str(Path(__file__).absolute().parent))
from e024_coverage import binding, write
from e023_collect import verify
from e014_collect import member_path
from e022_review import admission_contract


def selected_members(inv, unit):
    """Select one complete unit plus compact source/control proofs and exact aliases."""
    prefix = 'work/units/'+unit+'/'
    needed = {prefix+k for k in ['group/completed.json', 'group/forest.npz', 'group/forest.json',
        'group/retrieval/neighbors.npz', 'group/retrieval/neighbors.json', 'group/core-partition.json',
        'group/recruited-partition.json', 'audited/done.json', 'export/core/assignments.tsv',
        'export/recruited/assignments.tsv', 'export/core/manifest.json', 'export/recruited/manifest.json']}
    if inv['kind'] != 'E026 exact-byte calibrated grouping return' or not needed <= set(inv['members']) | set(inv['aliases']):
        raise ValueError('Missing completed unit review members or wrong archive kind')
    selected = {k for k in inv['members'] if (k.startswith(prefix) and not k.endswith('/recruitment.jsonl'))
                or k.startswith('evidence/controls/') or k.startswith('evidence/source/')
                or k in ['evidence/science-result.json', 'evidence/plan.json', 'evidence/config.json',
                         'evidence/gates/completion.json', 'evidence/gates/runtime.json']}
    aliases = {k: v for k, v in inv['aliases'].items() if k.startswith(prefix)}
    selected.update(v['canonical'] for v in aliases.values())
    return selected, aliases


def inventory_relations(inv, seen):
    """Check the same whole-work/alias/omission relations as the frozen verifier."""
    if seen != set(inv['members']) | {'inventory.json'}:
        raise ValueError('Incomplete streaming inventory')
    retained = {k.removeprefix('work/') for k in inv['members'] if k.startswith('work/')}
    aliases = {k.removeprefix('work/') for k in inv['aliases']}
    omitted = set(inv['omitted_retained_on_disk'])
    if (retained & aliases or retained & omitted or aliases & omitted
            or set(inv['all_work_members']) != retained | aliases | omitted):
        raise ValueError('Streaming whole-work accounting differs')
    for key in retained:
        if inv['members']['work/'+key] != inv['all_work_members'][key]:
            raise ValueError('Streaming work member binding differs')
    for key, value in inv['aliases'].items():
        b = {k: value[k] for k in ['bytes', 'sha256']}
        if key in inv['members'] or inv['members'].get(value['canonical']) != b or inv['all_work_members'].get(key.removeprefix('work/')) != b:
            raise ValueError('Streaming alias binding differs')
    for key, value in inv['omitted_retained_on_disk'].items():
        if {k: value[k] for k in ['bytes', 'sha256']} != inv['all_work_members'][key] or not value['reason']:
            raise ValueError('Streaming omission binding differs')


def compact_proof(expected, regular, logical, selected, aliases, member_bytes, unit, kept):
    """Keep the polled receipt bounded; full member/alias tables stay in inventory."""
    return dict(status='PASS', unit=unit, archive=dict(status='SUCCESS', archive=expected,
        regular_members=regular, logical_member_bytes=logical, every_member_verified=True),
        verified_materialized_member_bytes=member_bytes, materialization_upper_bytes=member_bytes+1024**2,
        materialized_member_count=len(selected), materialized_alias_count=len(aliases),
        full_tables='inventory.json; exact deterministic unit selection in frozen stager',
        all_other_members_verified_but_not_materialized=True,
        compressed_archive_kept_locally=kept, original_absolute_paths_or_receipts_rewritten=False,
        raw_recruitment_journal='Retained in checksum-bound private archive; no materialized-journal claim')


class BoundReader:
    """Hash/count the actual compressed input, refusing an overrun before admission."""
    def __init__(self, stream, expected):
        if not 0 < expected['bytes'] <= 2*1024**3 or len(expected['sha256']) != 64:
            raise ValueError('Bounded expected compressed bytes/SHA256 required')
        self.stream, self.expected = stream, expected
        self.count = 0; self.hash = hashlib.sha256()

    def read(self, size=-1):
        """Serve a bounded chunk to the streaming tar parser and accumulate all bytes."""
        data = self.stream.read(1024**2 if size < 0 else size)
        self.count += len(data)
        if self.count > self.expected['bytes']:
            raise ValueError('Streaming compressed bytes exceed expected return')
        self.hash.update(data)
        return data

    def finish(self):
        """Include gzip/tar trailers and refuse truncated/altered/extra input bytes."""
        while self.read(1024**2): pass
        if dict(bytes=self.count, sha256=self.hash.hexdigest()) != self.expected:
            raise ValueError('Streaming archive checksum/bytes differ; partial stage not admitted')


def stream_stage(stream, expected, unit, output, admission, cap=2*1024**3, reserve=6*1024**3):
    """Verify/stage in one pass without a compressed local copy or native-path reads.

    `staging.json` appears only after all compressed/member/alias/inventory checks
    pass. A failed partial directory is preserved and never admitted or replaced.
    The immutable original remains in private storage, not invented as a local copy.
    """
    if unit not in ['E009-E022', 'oral-E019'] or not 0 < cap <= 2*1024**3:
        raise ValueError('One frozen unit and bounded local materialization required')
    admission_contract(admission); reader = BoundReader(stream, expected)
    output = Path(output); seen = set(); inv = None; logical = 0
    with tarfile.open(fileobj=reader, mode='r|gz') as a:
        for m in a:
            member_path(output, m.name)
            if not m.isfile() or m.name in seen or m.size < 0 or m.size+logical > 6*1024**3:
                raise ValueError('Nonregular/duplicate/oversized streaming member')
            if not seen and m.name != 'inventory.json': raise ValueError('Streaming inventory must be first')
            seen.add(m.name); f = a.extractfile(m)
            if m.name == 'inventory.json':
                if m.size > 64*1024**2: raise ValueError('Streaming manifest cap exceeded')
                payload = f.read(); inv = json.loads(payload)
                selected, aliases = selected_members(inv, unit)
                member_bytes = sum(inv['members'][k]['bytes'] for k in selected)+m.size
                if len(inv['members']) > 20000 or member_bytes+1024**2 > cap or shutil.disk_usage(output.parent).free < member_bytes+1024**2+reserve:
                    raise ValueError('Actual return review footprint/free reserve does not fit; no oversized fallback')
                output.mkdir(parents=True, exist_ok=False)
                (output/'inventory.json').write_bytes(payload)
                logical += len(payload); continue
            h = hashlib.sha256(); count = 0; target = None
            if m.name in selected:
                p = member_path(output, m.name); p.parent.mkdir(parents=True, exist_ok=True); target = p.open('xb')
            try:
                for chunk in iter(lambda: f.read(1024**2), b''):
                    count += len(chunk); h.update(chunk)
                    if target:
                        if shutil.disk_usage(output).free < len(chunk)+reserve:
                            raise ValueError('Local free reserve changed during streaming stage')
                        target.write(chunk)
            finally:
                if target: target.close()
            logical += count
            if count != m.size or inv['members'].get(m.name) != dict(bytes=count, sha256=h.hexdigest()):
                raise ValueError('Streaming member checksum/bytes differ')
    reader.finish(); inventory_relations(inv, seen)
    for name, wanted in aliases.items():
        target = member_path(output, name); target.parent.mkdir(parents=True, exist_ok=True)
        os.link(member_path(output, wanted['canonical']), target)
        if binding(target) != {k: wanted[k] for k in ['bytes', 'sha256']}:
            raise ValueError('Streaming materialized alias differs')
    result = compact_proof(expected, len(seen), logical, selected, aliases, member_bytes, unit, False)
    from e021_control_json import publish
    publish(result, output/'staging.json')
    return result


def stage(archive, expected, unit, output, admission, cap=2*1024**3, reserve=6*1024**3):
    """Refuse oversized selected members before writing; verify materialized aliases."""
    if unit not in ['E009-E022', 'oral-E019'] or not 0 < cap <= 2*1024**3:
        raise ValueError('One frozen unit and bounded local materialization required')
    admission_contract(admission)
    proof = verify(archive, expected)
    with tarfile.open(archive, 'r:gz') as a:
        inventory_bytes = a.getmember('inventory.json').size
        inv = json.load(a.extractfile('inventory.json'))
    selected, aliases = selected_members(inv, unit)
    member_bytes = sum(inv['members'][k]['bytes'] for k in selected)+inventory_bytes
    physical = member_bytes+1024**2  # Closed staging receipt/metadata headroom.
    output = Path(output)
    if physical > cap or shutil.disk_usage(output.parent).free < physical+reserve:
        raise ValueError('Actual return review footprint/free reserve does not fit; no oversized fallback')
    output.mkdir(parents=True, exist_ok=False)
    with tarfile.open(archive, 'r:gz') as a:
        for m in a:
            if m.name != 'inventory.json' and m.name not in selected: continue
            path = member_path(output, m.name); path.parent.mkdir(parents=True, exist_ok=True)
            with path.open('xb') as f:
                shutil.copyfileobj(a.extractfile(m), f, length=1024**2)
            if m.name != 'inventory.json' and binding(path) != inv['members'][m.name]:
                raise ValueError('Materialized return bytes differ')
    for name, wanted in aliases.items():
        target = member_path(output, name); target.parent.mkdir(parents=True, exist_ok=True)
        os.link(member_path(output, wanted['canonical']), target)
        if binding(target) != {k: wanted[k] for k in ['bytes', 'sha256']}:
            raise ValueError('Materialized exact alias differs')
    result = compact_proof(expected, proof['regular_members'], proof['logical_member_bytes'],
                           selected, aliases, member_bytes, unit, True)
    from e021_control_json import publish
    publish(result, output/'staging.json'); return result


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--archive', type=Path); p.add_argument('--stdin', action='store_true')
    p.add_argument('--bytes', type=int, required=True)
    p.add_argument('--sha256', required=True); p.add_argument('--unit', required=True)
    p.add_argument('--output', type=Path, required=True); p.add_argument('--admission', type=Path, required=True)
    a = p.parse_args(); expected = dict(bytes=a.bytes, sha256=a.sha256)
    if bool(a.archive) == a.stdin: p.error('Choose exactly archive or stdin')
    value = stream_stage(sys.stdin.buffer, expected, a.unit, a.output, a.admission) if a.stdin else stage(a.archive, expected, a.unit, a.output, a.admission)
    print(json.dumps(value), flush=True)
