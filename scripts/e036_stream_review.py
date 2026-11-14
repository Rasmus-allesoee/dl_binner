#!/usr/bin/env python3
"""Verify complete E036 slices while staging only frozen diagnostic consumers.

The caller admits authenticated generations and export cost first. Every byte,
physical member and exact alias is verified, including unmaterialized Oral
fallback payloads. This module cannot start compute or change science.
"""
import base64
import json
from pathlib import Path
import shutil
import struct
import subprocess
import sys

sys.path.insert(0, str(Path(__file__).absolute().parent))
import e032_restore as accepted
from e024_coverage import binding


def selected(name):
    """Retain new E009 outputs and compact closure; Oral is never rescored."""
    if name.startswith('evidence/'):
        return True
    if not name.startswith('work/'):
        return False
    tail = name.removeprefix('work/')
    if not tail.startswith(('E009-noGLM/', 'E009-GLM/', 'oral-noGLM/')):
        return True
    if tail.startswith('oral-noGLM/'):
        return tail.endswith(('.json', '.tsv')) and not tail.endswith(
            ('pre-partition.json', 'post-partition.json', 'updates.json',
             'assignments.tsv'))
    stage = tail.split('/')[1]
    if stage in {'node-features', 'student', 'student-embed', 'student-graph',
                 'select', 'audit'}:
        return True
    return tail.endswith(('.json', '.tsv')) and not tail.endswith(
        ('partition.json', 'updates.json', 'candidates.json', 'decisions.json'))


def staged_bytes(inventory):
    """Count canonical selected bytes; exact aliases need no second copy."""
    wanted = {n for n in inventory['members'] if selected(n)}
    wanted.update(v['canonical'] for n, v in inventory['aliases'].items()
                  if selected(n))
    return sum(inventory['members'][n]['bytes'] for n in wanted)


def restore(raw, metadata, expected, inventory_path, output, crc_binary,
            reserve=8 * 1024**3, cap=3 * 1024**3):
    """Stream SHA/MD5/CRC32C and all members with strict bounded selection.

    Failed partial staging is preserved without admission. Transport receipts
    live outside the immutable work namespace. No unchecked fallback exists.
    """
    inv = json.loads(Path(inventory_path).read_text())
    count = staged_bytes(inv) + Path(inventory_path).stat().st_size
    if count > cap or shutil.disk_usage(Path(output).parent).free - count < reserve:
        raise ValueError('Prospective local staging/reserve refused')
    crc = subprocess.Popen([str(crc_binary), '-'], stdin=subprocess.PIPE,
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    class Reader:
        def read(self, size=-1):
            block = raw.read(size)
            crc.stdin.write(block)
            return block

    old = accepted.needed, accepted.LOGICAL
    accepted.needed, accepted.LOGICAL = selected, 8 * 1024**3
    try:
        proof = accepted.stream_restore(Reader(), metadata, expected, output,
                                        binding(inventory_path), reserve)
        receipt = Path(output) / 'work/restore-admission.json'
        receipt.rename(Path(output) / 'stream-admission.json')
        crc.stdin.close()
        crc.stdin = None
        stdout, stderr = crc.communicate(timeout=30)
        if crc.returncode:
            raise ValueError('CRC32C worker failed: ' + stderr.decode()[-1000:])
        actual = base64.b64encode(struct.pack('>I', int(stdout.strip()))).decode()
        if actual != metadata['crc32c']:
            raise ValueError('Whole archive CRC32C differs')
        proof.update(whole_SHA256_MD5_CRC32C_verified=True,
                     full_archive_every_member_and_alias_verified=True,
                     compact_staging_predeclared_bytes=count,
                     unselected_members_backed_up_locally=False,
                     baseline_rescored=False)
        return proof
    finally:
        accepted.needed, accepted.LOGICAL = old
        if crc.poll() is None:
            crc.kill()
            crc.communicate()
