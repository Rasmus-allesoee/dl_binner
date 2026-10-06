#!/usr/bin/env python3
"""Test the changed production scheduler options with a data-free native DAG.

Two independent four-thread/eight-GB rules only sleep and write monotonic timing
receipts. Compare old simultaneous --cores/--jobs options, test the actual
owner option helper, partial/completed resume and a memory-bound pair. No binner,
mapping, evaluation, scientific data or accepted demonstration is executed.
"""
import argparse
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'scripts'))
from e005_owner import isolated_env, local_scheduler_options
from e005_smoke import sha


def execute(python, folder, options, target=None, dry=False):
    """Run actual Snakemake with bounded startup and retain its command/whole log."""
    command = [str(python), '-I', '-B', '-m', 'snakemake', '--snakefile', str(folder/'Snakefile'),
               '--directory', str(folder), '--configfile', str(folder/'config.json'),
               *options, '--runtime-source-cache-path', str(folder/'source-cache')]
    if target: command.append(target)
    if dry: command.append('--dry-run')
    log = folder/('completed.log' if dry else 'partial.log' if target else 'native.log')
    with log.open('x') as stream:
        result = subprocess.run(command, stdout=stream, stderr=subprocess.STDOUT,
                                env=isolated_env(4), timeout=60)
    if result.returncode:
        raise RuntimeError(log.read_text()[-3000:])
    return dict(command=command, exit_code=result.returncode, log=str(log.relative_to(ROOT)), sha256=sha(log))


def main(python, output):
    """Publish fresh synthetic scheduler evidence; preserve all native workdirs."""
    output = output.resolve(); output.mkdir(parents=True, exist_ok=False)
    version = subprocess.check_output([str(python),'-I','-B','-c',
        'import importlib.metadata; print(importlib.metadata.version("snakemake"))'],
        env=isolated_env(4), timeout=30, text=True).strip()
    if version != '9.16.3':
        raise ValueError('Unexpected scheduler version: '+version)
    # No worker mock: Snakemake invokes these actual tiny rule bodies in its executor.
    worker = output/'worker.py'
    worker.write_text('import json,time,sys\nfrom pathlib import Path\nstart=time.monotonic_ns()\ntime.sleep(.6)\nPath(sys.argv[1]).write_text(json.dumps(dict(start=start,end=time.monotonic_ns(),threads=int(sys.argv[2]))))\n')
    snake = '''PYTHON=config['python']
WORKER=config['worker']
rule all:
    input: 'a.json','b.json'
rule timed:
    output: '{name}.json'
    wildcard_constraints: name='a|b'
    threads: THREADS
    resources: mem_mb=8000
    shell: '{PYTHON:q} -I -B {WORKER:q} {output:q} {threads}'
'''
    receipts = {}
    for name, options, threads in (
        ('legacy', ['--cores','4','--jobs','1','--resources','mem_mb=8000','--scheduler','greedy'],4),
        ('corrected', local_scheduler_options(4),4),
        ('memory', local_scheduler_options(4),1)):
        folder = output/name; folder.mkdir(); (folder/'Snakefile').write_text(snake.replace('THREADS',str(threads)))
        (folder/'config.json').write_text(json.dumps(dict(python=str(python),worker=str(worker))))
        receipt = execute(python,folder,options)
        intervals = [json.loads((folder/f'{v}.json').read_text()) for v in ('a','b')]
        overlap = min(r['end'] for r in intervals) > max(r['start'] for r in intervals)
        if overlap and name != 'legacy':
            raise RuntimeError('Unexpected native concurrency for '+name)
        receipts[name] = dict(receipt, intervals=intervals, overlap=overlap)
    folder = output/'resume'; folder.mkdir(); (folder/'Snakefile').write_text(snake.replace('THREADS','4'))
    (folder/'config.json').write_text(json.dumps(dict(python=str(python),worker=str(worker))))
    partial = execute(python,folder,local_scheduler_options(4),'a.json')
    before = dict(sha256=sha(folder/'a.json'), mtime_ns=(folder/'a.json').stat().st_mtime_ns)
    complete = execute(python,folder,local_scheduler_options(4))
    if before != dict(sha256=sha(folder/'a.json'),mtime_ns=(folder/'a.json').stat().st_mtime_ns):
        raise RuntimeError('Partial completed rule repeated')
    dry = execute(python,folder,local_scheduler_options(4),dry=True)
    if 'Nothing to be done' not in (folder/'completed.log').read_text():
        raise RuntimeError('Completed scheduler fixture schedules work')
    result = dict(date='2026-10-06', status='passed', scope='native Mac Snakemake 9.16.3 scheduling only; no scientific workers or new Linux launcher execution',
                  legacy_limitation='returned Linux GI DAG overlaps; tiny Mac legacy fixture does not necessarily reproduce that context',
                  workflow_python=str(python.absolute()), snakemake_version=version,
                  check_source_sha256=sha(Path(__file__)), production_helper_sha256=sha(ROOT/'scripts/e005_owner.py'),
                  cases=receipts, partial_resume=dict(partial=partial, complete=complete, completed_dry_run=dry,
                                                      reused=before),
                  remedy='local --cores cap without --jobs; explicit local executor and global mem_mb')
    (output/'observed.json').write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')
    print(json.dumps(dict(status='passed', receipt=str(output/'observed.json'))))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workflow-python', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    # Resolving a venv's interpreter symlink bypasses pyvenv.cfg and its packages.
    args = parser.parse_args(); main(args.workflow_python.absolute(),args.output)
