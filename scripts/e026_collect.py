#!/usr/bin/env python3
"""Compact E026 return with exact deduplication and complete explicit controls.

Every new non-DNA artifact and closed supervision/release gate must be delivered.
Accepted inputs and emitted FASTAs stay in place under their byte locators; an
inventory is not their backup. No upload, VM operation or science is performed.
"""
import argparse
import json
from pathlib import Path
import shutil
import sys
import tarfile

sys.path.insert(0, str(Path(__file__).absolute().parent))
from e024_coverage import binding, write
from e023_collect import verify, CappedWriter

CAP = 2*1024**3
LOGICAL_CAP = 6*1024**3
CONTROLS = ['logs/supervision.json', 'logs/provider-before-release.json',
    'logs/watchdog-native-tests.log', 'logs/maintenance-restart-refused.json',
    'logs/watchdog-live-before-release.json', 'payload/financial-gate.json']


def collect_controls(root, destination, allow_incomplete=False):
    """Copy exact allowed release controls, including the previously omitted stderr.

    Only files inside the phase root may be selected by release manifests.
    Missing controls are refused on success and explicitly enumerated on failure.
    Credentials, unrelated private files and unclosed changing logs are excluded.
    """
    root = Path(root).absolute(); destination = Path(destination)
    destination.mkdir(parents=True, exist_ok=False)
    required = set(CONTROLS)
    release = json.loads((root/'release.json').read_text()) if (root/'release.json').is_file() else {}
    for path, wanted in release.get('gate_files', {}).items():
        p = Path(path).absolute()
        if not p.is_relative_to(root) or p.is_symlink():
            raise ValueError('Release control outside current phase refused')
        if binding(p) != wanted:
            raise ValueError('Release control bytes changed: '+path)
        required.add(str(p.relative_to(root)))
    for name in ['config.json', 'science-plan.json', 'started.json', 'release.json',
                 'science-result.json', 'science-disk.jsonl', 'external-data.json']:
        required.add(name)
    missing = []; copied = {}
    for name in sorted(required):
        source = root/name
        if not source.is_file() or source.is_symlink():
            missing.append(name); continue
        target = destination/name; target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
        if binding(target) != binding(source):
            raise ValueError('Closed control copy bytes differ')
        copied[name] = binding(target)
    if missing and not allow_incomplete:
        raise ValueError('Missing completed-phase controls: '+','.join(missing))
    write(destination/'control-inventory.json', dict(copied=copied, missing=missing,
        failure_only=allow_incomplete, original_open_terminal_log_copied=False))
    return copied


def pack(work, evidence, output, ceiling=CAP, allow_incomplete=False):
    """Seal manifest-inclusive bounded bytes; refuse links, overflow and absent controls."""
    work, evidence, output = map(Path, [work, evidence, output])
    if not 0 < ceiling <= CAP or output == work or work in output.parents:
        raise ValueError('Separate return directory and capped compressed bytes required')
    control = evidence/'controls/control-inventory.json'
    if not control.is_file() or (json.loads(control.read_text())['missing'] and not allow_incomplete):
        raise ValueError('Explicit control delivery inventory required')
    output.mkdir(parents=True, exist_ok=False)
    files = {}; aliases = {}; omitted = {}; all_work = {}; seen = {}
    for folder, prefix in [(work, 'work'), (evidence, 'evidence')]:
        for p in sorted(folder.rglob('*')):
            if p.is_symlink(): raise ValueError('Artifact links refused')
            if not p.is_file(): continue
            name = str(p.relative_to(folder)); b = binding(p); key = prefix+'/'+name
            if prefix == 'work':
                all_work[name] = b
                if p.suffix in ['.fa', '.fna', '.fasta']:
                    omitted[name] = dict(**b, reason='Full accounted DNA retained on original disk; inventory is not backup')
                    continue
            content = b['bytes'], b['sha256']
            # Verifier's historical alias schema covers work members only.
            if prefix == 'work' and content in seen:
                aliases[key] = dict(**b, canonical=seen[content])
            else:
                files[key] = p; seen.setdefault(content, key)
    members = {k: binding(p) for k, p in files.items()}
    logical = sum(v['bytes'] for v in members.values())
    if logical > LOGICAL_CAP or len(members) > 20000:
        raise ValueError('Logical/member return cap exceeded; no oversized fallback')
    external = json.loads((evidence/'external-data.json').read_text())
    if external.get('data_copied') is not False:
        raise ValueError('Restore-only external input manifest required')
    inventory = dict(kind='E026 exact-byte calibrated grouping return', members=members,
        all_work_members=all_work, aliases=aliases, omitted_retained_on_disk=omitted,
        external_data=external, incomplete_failure_evidence=allow_incomplete,
        compressed_hard_ceiling_bytes=ceiling, logical_cap_bytes=LOGICAL_CAP)
    write(output/'inventory.json', inventory)
    if (output/'inventory.json').stat().st_size > 64*1024**2 or logical+(output/'inventory.json').stat().st_size > LOGICAL_CAP:
        raise ValueError('Manifest-inclusive return cap exceeded')
    partial = output/'e026-evidence.tar.gz.partial'
    with partial.open('xb') as raw:
        with tarfile.open(fileobj=CappedWriter(raw, ceiling), mode='w:gz') as a:
            a.add(output/'inventory.json', arcname='inventory.json', recursive=False)
            for key, p in sorted(files.items()): a.add(p, arcname=key, recursive=False)
    archive = output/'e026-evidence.tar.gz'; partial.rename(archive)
    result = verify(archive)
    result.update(control_inventory=binding(control), omitted_inventory_is_not_backup=True)
    write(output/'collection.json', result)
    (output/'e026-evidence.tar.gz.sha256').write_text(result['archive']['sha256']+'  e026-evidence.tar.gz\n')
    return result


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    for name in ['work', 'evidence', 'output']: p.add_argument('--'+name, type=Path, required=True)
    p.add_argument('--allow-incomplete', action='store_true'); a = p.parse_args()
    print(json.dumps(pack(a.work, a.evidence, a.output, allow_incomplete=a.allow_incomplete)), flush=True)
