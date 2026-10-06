"""Bounded CPU process supervision, adapted from accepted E005 smoke helpers.

Native /proc (Linux) or ps (Mac) samples are approximate process-tree CPU/RSS,
not provider billing or exact peaks. Each launched group is stopped on failure,
cancellation, monitoring error or wall/RSS limit, including observed orphans.
"""
import json
import os
from pathlib import Path
import signal
import subprocess
import time


def isolated_env(threads):
    """Return an import-isolated CPU environment without mutating any prefix."""
    env = os.environ.copy()
    for key in ('PYTHONPATH', 'PYTHONHOME', 'PYTHONUSERBASE'):
        env.pop(key, None)
    env.update(PYTHONNOUSERSITE='1', PYTHONUNBUFFERED='1')
    for key in ('OMP_NUM_THREADS', 'MKL_NUM_THREADS', 'OPENBLAS_NUM_THREADS',
                'VECLIB_MAXIMUM_THREADS', 'NUMEXPR_NUM_THREADS'):
        env[key] = str(threads)
    return env


def local_scheduler_options(threads, mem_mb):
    """Cap local cores and aggregate RAM, never combine --cores with --jobs."""
    if not 1 <= threads <= 4 or not 0 < mem_mb <= 8000:
        raise ValueError('CPU budget must be 1–4 threads; RAM budget must be 1–8000 MB')
    return ['--cores', str(threads), '--executor', 'local', '--resources',
            f'mem_mb={mem_mb}', '--set-resource-scopes', 'mem_mb=global',
            '--scheduler', 'greedy']


def process_sample(root_pid, known):
    """Sample descendants by PID/start identity, retaining cumulative CPU maxima."""
    rows = {}
    if Path('/proc/self/stat').exists():
        ticks, page = os.sysconf('SC_CLK_TCK'), os.sysconf('SC_PAGE_SIZE')
        for folder in Path('/proc').iterdir():
            if not folder.name.isdigit():
                continue
            try:
                raw = (folder/'stat').read_text()
                fields = raw[raw.rfind(')')+2:].split()
                rows[int(folder.name)] = (int(fields[1]), fields[19], int(fields[21])*page,
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
    memory = 0
    for pid in selected:
        _, start, rss, cpu = rows[pid]
        known[(pid, start)] = max(known.get((pid, start), 0), cpu)
        memory += rss
    return memory, sum(known.values())


def terminate(process, members):
    """Terminate only the launched group and observed descendants with matching IDs."""
    if process is None:
        return
    live = {}
    try:
        process_sample(process.pid, members)
        for key in members:
            check = {}
            process_sample(key[0], check)
            if key in check:
                live[key] = True
    except (OSError, subprocess.SubprocessError):
        pass
    for sig in (signal.SIGTERM, signal.SIGKILL):
        for pid, start in live:
            check = {}
            process_sample(pid, check)
            if (pid, start) in check:
                try:
                    os.kill(pid, sig)
                except ProcessLookupError:
                    pass
        try:
            os.killpg(process.pid, sig)
        except ProcessLookupError:
            pass
        try:
            process.wait(timeout=1)
        except subprocess.TimeoutExpired:
            pass
    process.wait(timeout=2)


def progress(message):
    """Emit a readable timestamped line, also forwarded from workers to the parent."""
    print('DLBINNER '+time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime())+' | '+message,
          flush=True)


def supervise(command, log_path, seconds, ram_bytes, env, sample_root=None):
    """Run an argv, retain log/samples/exit receipt and stop promptly on real failure.

Only DLBINNER progress lines are echoed; verbose native output stays in the log.
When sample_root is the calling driver, aggregate RSS includes its coordinator.
The receipt is always written, including cancellation/failed prerequisites.
"""
    log_path = Path(log_path)
    started, known, members, peak, reason, process = time.monotonic(), {}, {}, 0, None, None
    baseline = process_sample(sample_root, known)[1] if sample_root else 0
    offset, heartbeat = 0, started
    interrupted = None
    with log_path.open('x') as log, log_path.with_suffix('.samples.jsonl').open('x') as samples:
        try:
            process = subprocess.Popen([str(c) for c in command], stdout=log,
                                       stderr=subprocess.STDOUT, env=env, start_new_session=True)
            while True:
                now = time.monotonic()
                memory, cpu = process_sample(sample_root or process.pid, known)
                if sample_root:
                    process_sample(process.pid, members)
                else:
                    members = known
                peak = max(peak, memory)
                samples.write(json.dumps(dict(seconds=now-started, rss_bytes=memory,
                                               sampled_cpu_seconds=max(0, cpu-baseline)))+'\n')
                samples.flush()
                with log_path.open() as reader:
                    reader.seek(offset)
                    for line in reader:
                        if line.startswith('DLBINNER '):
                            print(line.rstrip(), flush=True)
                    offset = reader.tell()
                if memory > ram_bytes:
                    raise MemoryError('Sampled working RSS exceeded the configured limit')
                if now-started >= seconds:
                    raise TimeoutError('Configured wall-time limit reached')
                if process.poll() is not None:
                    break
                if now-heartbeat >= 10:
                    progress(f'Still running ({now-started:.0f}s, sampled RSS {memory/1e9:.2f} GB); log: {log_path}')
                    heartbeat = now
                time.sleep(.2)
        except BaseException as error:
            reason = f'{type(error).__name__}: {error}'
            interrupted = error if isinstance(error, (KeyboardInterrupt, SystemExit)) else None
        finally:
            terminate(process, members)
    elapsed = time.monotonic()-started
    receipt = dict(command=[str(c) for c in command], exit_code=process.returncode if process else None,
                   stop_reason=reason, wall_seconds=elapsed, peak_sampled_rss_bytes=peak,
                   sampled_cpu_seconds=max(0, sum(known.values())-baseline),
                   sampled_average_cpus=max(0, sum(known.values())-baseline)/elapsed,
                   scope='sampled process tree; shared pages may be counted twice; short CPU work may be missed',
                   sample_includes_coordinator=sample_root is not None)
    log_path.with_suffix('.exit.json').write_text(json.dumps(receipt, indent=2, sort_keys=True)+'\n')
    with log_path.open('a') as log:
        log.write(f'\nDLBINNER exit_code={receipt["exit_code"]} stop_reason={reason!r}\n')
    if interrupted:
        raise interrupted
    if receipt['exit_code'] != 0 or reason:
        tail = log_path.read_text()[-2500:]
        raise RuntimeError(f'Command failed; see {log_path}\n{reason or tail}')
    return receipt
