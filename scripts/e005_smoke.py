#!/usr/bin/env python3
"""E005 portable supervision and native smoke verification, never biological scoring.

The owner wrapper uses only the standard library before environment setup. Native
verification imports the installed binner in its isolated prefix. Linux /proc and
portable ps samples are planning receipts, not exact peaks or provider billing.
"""
import argparse
import csv
import hashlib
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time


def sha(path):
    """Hash file bytes without loading a payload into RAM."""
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def write(path, data):
    """Exclusively retain a small JSON receipt; refuse prior-output replacement."""
    with Path(path).open('x') as stream:
        json.dump(data, stream, indent=2, sort_keys=True, allow_nan=False)
        stream.write('\n')


def progress(stage, **values):
    """Emit timestamped progress to the automatically captured owner terminal."""
    print(json.dumps(dict(stage=stage, utc=time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
                          **values)), flush=True)


def process_sample(root_pid, known):
    """Sample descendants and retain PID/start identities for safe orphan cleanup.

    Return (summed RSS, cumulative CPU maxima). Linux reads /proc without an
    extra package; Mac harness checks use ps and do not validate Linux sampling.
    """
    rows = {}
    if sys.platform.startswith('linux'):
        ticks = os.sysconf('SC_CLK_TCK')
        for folder in Path('/proc').iterdir():
            if not folder.name.isdigit():
                continue
            try:
                raw = (folder/'stat').read_text()
                fields = raw[raw.rfind(')')+2:].split()
                # fields begin at field 3 (state); starttime is field 22.
                rows[int(folder.name)] = (int(fields[1]), fields[19],
                    int(fields[21])*os.sysconf('SC_PAGE_SIZE'),
                    (int(fields[11])+int(fields[12]))/ticks)
            except (OSError, ValueError, IndexError):
                continue
    else:
        raw = subprocess.check_output(['ps', '-axo', 'pid=,ppid=,lstart=,rss=,time='], text=True)
        for line in raw.splitlines():
            fields = line.split()
            if len(fields) != 9:
                continue
            minutes, seconds = fields[8].split(':')
            rows[int(fields[0])] = (int(fields[1]), ' '.join(fields[2:7]),
                                   int(fields[7])*1024, int(minutes)*60+float(seconds))
    selected = {pid for pid, start in known if pid in rows and rows[pid][1] == start}
    if root_pid in rows:
        selected.add(root_pid)
    while True:
        expanded = selected | {pid for pid, row in rows.items() if row[0] in selected}
        if expanded == selected:
            break
        selected = expanded
    rss = 0
    for pid in selected:
        parent, start, memory, cpu = rows[pid]
        known[(pid, start)] = max(known.get((pid, start), 0), cpu)
        rss += memory
    return rss, sum(known.values())


def terminate(process, members):
    """Stop this launched process group and observed descendants, including orphans."""
    if process is None:
        return
    # Refresh creation identities before signalling; never signal a reused PID.
    live = {}
    try:
        process_sample(process.pid, live)
        process_sample(process.pid, members)
        for key in list(members):
            check = {}
            process_sample(key[0], check)
            if key in check:
                live[key] = True
    except (OSError, subprocess.SubprocessError):
        pass
    for pid, start in live:
        try:
            os.kill(pid, signal.SIGTERM)
        except ProcessLookupError:
            pass
    try:
        os.killpg(process.pid, signal.SIGTERM)
    except ProcessLookupError:
        pass
    try:
        process.wait(timeout=2)
    except subprocess.TimeoutExpired:
        pass
    # A failing parent may exit while a child stays alive; kill that child too.
    for pid, start in live:
        current = {}
        process_sample(pid, current)
        if (pid, start) in current:
            try:
                os.kill(pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
    try:
        os.killpg(process.pid, signal.SIGKILL)
    except ProcessLookupError:
        pass
    process.wait(timeout=2)


def run(command, directory, name, seconds, ram_bytes, allocation, env=None):
    """Run one bounded stage, retain log/samples/exit receipt and kill on failure.

    No shell interpolation. Nonzero exits, cancellations, time/RSS ceilings and
    monitor failures stop dependent work. CPU sampling can miss short processes;
    summed RSS can double-count shared pages. Allocation is explicit owner input.
    """
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    started, peak, known, reason, process = time.monotonic(), 0, {}, None, None
    progress('stage_start', name=name, command=[str(c) for c in command], seconds_ceiling=seconds)
    log_path = directory/(name+'.log')
    with log_path.open('x') as log, (directory/(name+'.resources.jsonl')).open('x') as samples:
        try:
            process = subprocess.Popen([str(c) for c in command], stdout=log,
                                       stderr=subprocess.STDOUT, env=env, start_new_session=True)
            heartbeat, sampled = started, 0
            while True:
                now = time.monotonic()
                rss, cpu = process_sample(process.pid, known)
                peak = max(peak, rss)
                if now-sampled >= 1:
                    samples.write(json.dumps(dict(seconds=now-started, rss_bytes=rss,
                                                   sampled_cpu_seconds=cpu))+'\n')
                    samples.flush()
                    sampled = now
                if process.poll() is not None:
                    break
                if rss > ram_bytes:
                    raise RuntimeError('RSS ceiling exceeded')
                if now-started > seconds:
                    raise TimeoutError('Stage time ceiling exceeded')
                if now-heartbeat >= 20:
                    progress('heartbeat', name=name, seconds=now-started, rss_bytes=rss, log=str(log_path))
                    heartbeat = now
                time.sleep(.2)
        except BaseException as error:
            reason = repr(error)
        finally:
            terminate(process, known)
    elapsed = time.monotonic()-started
    if reason is None and peak > ram_bytes:
        reason = 'RSS ceiling exceeded'
    if reason is None and elapsed > seconds:
        reason = 'Stage time ceiling exceeded including cleanup'
    receipt = dict(command=[str(c) for c in command], exit_code=process.returncode if process else None,
                   stop_reason=reason, wall_seconds=elapsed, peak_sampled_rss_bytes=peak,
                   sampled_cpu_seconds=sum(known.values()), sampled_average_cpus=sum(known.values())/elapsed,
                   allocated_vcpus=allocation, allocated_vcpu_hours=allocation*elapsed/3600,
                   resource_scope='sampled descendants; excludes outer driver; not provider invoice')
    write(directory/(name+'.json'), receipt)
    progress('stage_end', name=name, **{k: receipt[k] for k in ('exit_code', 'stop_reason', 'wall_seconds')})
    if receipt['exit_code'] != 0 or reason:
        print(log_path.read_text()[-8000:], flush=True)
        raise RuntimeError('Stage failed: '+name+'; see '+str(log_path))
    return receipt


def verify(config, output):
    """Inspect real installed-package caches, checkpoint reload and every export.

    Compare cached and freshly read tiny real DNA, ordered sample axes, exact zero
    masks, excluded short/no-fourmer rows and complete DNA accounting. No labels,
    biological metric or acceptance requirement for superior utility is used.
    """
    import numpy as np
    from dl_binner.io import load_arrays, read_fasta, validate_features
    cfg = json.loads(Path(config).read_text())
    data, meta = load_arrays('features.npz', 'features')
    validate_features(data, meta)
    expected = cfg['expectations']
    if data['ids'].tolist() != expected['ids'] or meta['samples'] != expected['samples']:
        raise ValueError('Smoke contig/sample axis mismatch')
    if data['depth'].tolist() != expected['depth']:
        raise ValueError('Depth row alignment mismatch')
    np.testing.assert_array_equal(data['zero_depth'], data['depth'] == 0)
    np.testing.assert_array_equal(data['depth_evidence'], (data['depth'] > 0).any(1))
    if data['eligible'].tolist() != expected['eligible']:
        raise ValueError('Eligibility/exclusion mismatch')
    fresh, _ = load_arrays('fresh.npz', 'features')
    at = [expected['ids'].index(i) for i in fresh['ids'].tolist()]
    np.testing.assert_array_equal(fresh['tnf'], data['tnf'][at])
    np.testing.assert_array_equal(fresh['valid_fourmers'], data['valid_fourmers'][at])
    learned, _ = load_arrays('learned.embeddings.npz', 'embeddings')
    reference, _ = load_arrays('checkpoint.reference.npz', 'embeddings')
    np.testing.assert_array_equal(learned['ids'], reference['ids'])
    np.testing.assert_allclose(learned['features'], reference['features'], rtol=0, atol=1e-7)
    np.testing.assert_array_equal(learned['evidence'], reference['evidence'])
    source = dict(read_fasta(cfg['fasta']))
    for mode in ('raw', 'learned'):
        folder = Path(mode+'.export')
        exported = {}
        for path in folder.glob('*.fna'):
            for ident, dna in read_fasta(path) if path.stat().st_size else []:
                if ident in exported:
                    raise ValueError('Duplicate export')
                exported[ident] = dna
        if exported != source:
            raise ValueError('Export DNA/ID loss')
        manifest = json.loads((folder/'manifest.json').read_text())
        for name, entry in manifest['files'].items():
            if sha(folder/name) != entry['sha256'] or (folder/name).stat().st_size != entry['bytes']:
                raise ValueError('Export hash mismatch')
        with (folder/'assignments.tsv').open() as stream:
            rows = list(csv.DictReader(stream, delimiter='\t'))
        if [r['contig_id'] for r in rows] != expected['ids']:
            raise ValueError('Assignment axis mismatch')
        for row, eligible, reason in zip(rows, expected['eligible'], expected['exclusion_reason']):
            if not eligible and (row['status'] != 'excluded' or row['reason'] != reason):
                raise ValueError('Exclusion reason lost')
        write(mode+'.accounting.json', dict(contigs=len(rows), bp=sum(len(s) for s in source.values()),
              assigned=manifest['assigned'], unassigned=manifest['unassigned'], excluded=manifest['excluded']))
    write(output, dict(status='passed', cached_tnf_reused=True, native_fresh_tiny_reader=True,
          contig_sample_axes=True, depth_masks=True, complete_exports=True, checkpoint_reload=True,
          reload_max_abs=float(np.max(np.abs(learned['features']-reference['features']))),
          scope='native software smoke on retained real DNA plus synthetic sentinel/depth; no biological result'))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', required=True)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    verify(args.config, args.output)
