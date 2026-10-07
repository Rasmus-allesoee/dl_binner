#!/usr/bin/env python3
"""Build an immutable small E005 owner packet, reusing accepted Linux/E001 runtimes.

Commit source first. Include the exact prepared short-inclusive reference and tiny
real mapper-contract input, not whole sources, reads/BAMs, runtimes or GLM payloads.
Bind every file and source commit; refuse overwriting any earlier transfer.
"""
import argparse
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tarfile

sys.path.insert(0, str(Path(__file__).resolve().parent))
from e005_smoke import sha, write

ROOT = Path(__file__).resolve().parents[1]
SOURCES = [
    'scripts/e005_pilot.py', 'scripts/e005_pilot_owner.py', 'scripts/e005_pilot_bundle.py',
    'scripts/e005_external_probe.py', 'scripts/e005_rule.py', 'scripts/e005_owner.py',
    'scripts/e005_probe.py', 'scripts/e005_smoke.py', 'workflows/first-binner/gi_pilot.smk',
    'experiments/E004-first-binner/training.json',
    *['experiments/E005-linux-pilot/'+n for n in ('pilot.json','pilot-inputs.json','pilot-contigs.tsv',
        'smoke.json','external-runtime.json','linux-observed.json','native_contracts.py','OPERATIONS.md')]]


def build(destination):
    """Verify committed source/reference bytes and emit archive, checksum and manifest."""
    destination = Path(destination).resolve(); destination.mkdir(parents=True, exist_ok=False)
    folder = destination/'e005-gi-pilot'; folder.mkdir()
    commit = subprocess.check_output(['git','rev-parse','HEAD'], cwd=ROOT, text=True).strip()
    for name in SOURCES:
        original = ROOT/name
        committed = subprocess.check_output(['git','show',commit+':'+name], cwd=ROOT)
        if original.read_bytes() != committed:
            raise ValueError('Uncommitted transfer source: '+name)
        target = folder/name; target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(original, target)
    for name, source in [('pilot/assembly.fna',ROOT/'artifacts/e005-linux-pilot/input/pilot/assembly.fna'),
                         ('smoke/fresh.fna',ROOT/'artifacts/e005-linux-pilot/input/smoke/fresh.fna')]:
        target = folder/'input'/name; target.parent.mkdir(parents=True, exist_ok=True); shutil.copyfile(source, target)
    expected = json.loads((ROOT/'experiments/E005-linux-pilot/pilot-inputs.json').read_text())
    if sha(folder/'input/pilot/assembly.fna') != expected['fasta_sha256']:
        raise ValueError('Frozen pilot DNA changed')
    files = {str(p.relative_to(folder)):dict(sha256=sha(p),bytes=p.stat().st_size) for p in sorted(folder.rglob('*')) if p.is_file()}
    write(folder/'bundle-manifest.json',dict(record='E005',kind='frozen GI pilot v5',source_commit=commit,files=files,
        runtime_policy='read-only healthy E005 CPU/workflow and E001 mapping/AMBER; exact AMBER inventory reconciliation; no install or accepted smoke rerun'))
    archive = destination/'e005-gi-pilot-v5.tar.gz'
    with archive.open('xb') as stream, tarfile.open(fileobj=stream,mode='w:gz') as tar:
        for path in sorted(folder.rglob('*')):
            if path.is_file():
                tar.add(path,arcname='e005-gi-pilot/'+str(path.relative_to(folder)),recursive=False)
    checksum = archive.with_name(archive.name+'.sha256')
    checksum.write_text(sha(archive)+'  '+archive.name+'\n')
    print(json.dumps(dict(archive=str(archive),checksum=str(checksum),bytes=archive.stat().st_size,
                         sha256=sha(archive),source_commit=commit)))


if __name__ == '__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True)
    build(p.parse_args().output)
