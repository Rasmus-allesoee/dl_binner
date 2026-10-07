#!/usr/bin/env python3
"""Bounded D011 CPU inference probe, not a binner or an accuracy benchmark.

Prepare deterministic real-DNA windows, run the unmodified pinned author model,
check extraction contracts, retain incremental timing/provenance and supervise
one worker with a RAM/time ceiling. Model assets and bulk results stay ignored.
"""
import argparse
import gc
import hashlib
import importlib
import json
import math
import os
from pathlib import Path
import platform
import signal
import subprocess
import sys
import time
import traceback

ROOT = Path(__file__).resolve().parents[1]
LENGTHS = (500, 768, 1000, 2500, 10000)


def digest(path):
    """Stream a file's SHA256 without loading model or assembly bytes into RAM."""
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for b in iter(lambda: f.read(1024 * 1024), b''):
            h.update(b)
    return h.hexdigest()


def write_json(path, value):
    """Atomically replace a small JSON receipt, preserving the previous on failure."""
    path = Path(path)
    tmp = path.with_suffix(path.suffix + '.tmp')
    tmp.write_text(json.dumps(value, indent=2, sort_keys=True) + '\n')
    tmp.replace(path)


def fasta(path):
    """Yield ordered (unique ID, uppercase sequence) records; reject bad DNA/IDs."""
    seen, name, parts = set(), None, []
    with Path(path).open() as f:
        for line in f:
            if line.startswith('>'):
                if name is not None:
                    yield name, validate_dna(''.join(parts))
                name = line[1:].split()[0]
                if name in seen:
                    raise ValueError('Duplicate FASTA ID: ' + name)
                seen.add(name)
                parts = []
            elif line.strip():
                if name is None:
                    raise ValueError('Sequence before FASTA header')
                parts.append(line.strip())
        if name is not None:
            yield name, validate_dna(''.join(parts))


def validate_dna(seq):
    """Accept nonempty IUPAC DNA; preserve ambiguity rather than replacing bases."""
    seq = seq.upper()
    if not seq or set(seq) - set('ACGTRYSWKMBDHVN'):
        raise ValueError('Empty sequence or unsupported DNA alphabet')
    return seq


def reverse_complement(seq):
    """Return the IUPAC reverse complement without converting unknown evidence."""
    return validate_dna(seq).translate(str.maketrans('ACGTRYSWKMBDHVN', 'TGCAYRSWMKVHDBN'))[::-1]


def bounded_chunks(seq, tokenizer, max_bp, max_tokens):
    """Cover canonical-strand DNA exactly once with bounded, untruncated chunks.

    Split over-budget chunks in base coordinates, rather than truncating tokens.
    Return (start, end, DNA, total_tokens_including_specials) records. Canonicalizing
    the whole sequence makes chunk boundaries invariant under strand reversal.
    """
    if max_bp < 1 or max_tokens < 3:
        raise ValueError('Invalid chunk limits')
    seq = validate_dna(seq)
    seq = min(seq, reverse_complement(seq))
    result = []

    def split(start, end):
        piece = seq[start:end]
        count = max(len(tokenizer(strand, truncation=False)['input_ids'])
                    for strand in (piece, reverse_complement(piece)))
        if count <= max_tokens:
            result.append((start, end, piece, count))
        elif end - start > 1:
            mid = (start + end) // 2
            split(start, mid)
            split(mid, end)
        else:
            raise ValueError('One base exceeds token budget')

    for start in range(0, len(seq), max_bp):
        split(start, min(start + max_bp, len(seq)))
    assert ''.join(x[2] for x in result) == seq
    assert sum(x[1] - x[0] for x in result) == len(seq)
    return result


def panel(source, expected_sha, count):
    """Hash-select disjoint real parents, then center one timing window per parent.

    Forty parents (eight per length) are selected independent of truth or model
    output. Return windows, source provenance and the full assembly length list.
    The long-parent short windows measure speed, not short-contig biology.
    """
    if digest(source) != expected_sha:
        raise ValueError('Timing-source checksum mismatch')
    lengths, candidates = [], []
    for name, seq in fasta(source):
        lengths.append(len(seq))
        if len(seq) >= max(LENGTHS):
            key = hashlib.sha256(('D011-timing-v1:' + name).encode()).hexdigest()
            candidates.append((key, name))
    chosen = [name for _, name in sorted(candidates)[:len(LENGTHS) * count]]
    if len(chosen) != len(LENGTHS) * count:
        raise ValueError('Insufficient independent long parents')
    selected = {}
    for name, seq in fasta(source):
        if name in chosen:
            selected[name] = seq
    rows, provenance = [], []
    for index, name in enumerate(chosen):
        length = LENGTHS[index // count]
        start = (len(selected[name]) - length) // 2
        seq = selected[name][start:start + length]
        window_id = f'{name}:{start}:{start + length}'
        rows.append((window_id, seq))
        provenance.append(dict(id=window_id, source_contig=name, start=start,
                               end=start + length, bp=length,
                               sequence_sha256=hashlib.sha256(seq.encode()).hexdigest()))
    return rows, provenance, lengths


def bind_cache(rows, pin, settings):
    """Bind a feature cache to ordered IDs, DNA bytes, model bytes and transforms."""
    return dict(model_files=pin['files'], revision=pin['revision'], settings=settings,
                rows=[dict(id=name, sequence_sha256=hashlib.sha256(seq.encode()).hexdigest())
                      for name, seq in rows])


def load_cache(path, binding):
    """Load a hash-verified finite float32 cache; reject reordered/stale provenance."""
    import numpy as np
    path = Path(path)
    receipt = json.loads(path.with_suffix('.json').read_text())
    if receipt['binding'] != binding or receipt['sha256'] != digest(path):
        raise ValueError('Cache binding or bytes mismatch')
    with np.load(path, allow_pickle=False) as z:
        x, ids = z['features'].copy(), z['ids'].tolist()
    if ids != [r['id'] for r in binding['rows']] or x.shape != (len(ids), 768):
        raise ValueError('Cache axes mismatch')
    if x.dtype != np.float32 or not np.isfinite(x).all():
        raise ValueError('Invalid cached features')
    return x


def save_cache(path, features, binding):
    """Save features and a content-bound receipt; never store pickle objects."""
    import numpy as np
    path = Path(path)
    np.savez(path, features=features, ids=[r['id'] for r in binding['rows']])
    write_json(path.with_suffix('.json'), dict(binding=binding, sha256=digest(path)))


class Extractor:
    """Frozen CPU mean-pooling adapter with an explicit strand/chunk contract."""
    def __init__(self, model_dir, settings):
        import torch
        from transformers import AutoModel, AutoTokenizer
        self.torch, self.settings = torch, settings
        self.tokenizer = AutoTokenizer.from_pretrained(model_dir, trust_remote_code=True,
                                                       local_files_only=True)
        self.model = AutoModel.from_pretrained(model_dir, trust_remote_code=True,
                                               local_files_only=True).to('cpu').eval()
        self.model.requires_grad_(False)
        assert not self.model.training
        assert all(not p.requires_grad and p.device.type == 'cpu' for p in self.model.parameters())

    def pool(self, sequences):
        """Mean over attended tokens including specials, excluding padding, on CPU."""
        torch = self.torch
        tokens = self.tokenizer(sequences, return_tensors='pt', padding=True, truncation=False)
        if tokens['input_ids'].shape[1] > self.settings['max_tokens']:
            raise ValueError('Unchunked call exceeds explicit token limit')
        with torch.inference_mode():
            hidden = self.model(**tokens)[0]
            mask = tokens['attention_mask'].unsqueeze(-1)
            result = (hidden * mask).sum(1) / mask.sum(1)
        assert not result.requires_grad and torch.isfinite(result).all()
        return result.numpy()

    def extract(self, rows):
        """Return features in input order, averaging both strands and bp-weighted chunks."""
        import numpy as np
        if len({name for name, _ in rows}) != len(rows):
            raise ValueError('Duplicate extraction IDs')
        result, detail = [], []
        for name, seq in rows:
            chunks = bounded_chunks(seq, self.tokenizer, self.settings['chunk_bp'],
                                    self.settings['max_tokens'])
            pieces = [strand for _, _, piece, _ in chunks
                      for strand in (piece, reverse_complement(piece))]
            encoded = [self.tokenizer(p, truncation=False)['input_ids'] for p in pieces]
            # Reverse tokens can compress differently; split if either strand exceeds budget.
            if any(len(ids) > self.settings['max_tokens'] for ids in encoded):
                raise ValueError('Reverse-strand token budget exceeded; no truncation allowed')
            batch = self.settings['batch_size']
            embeds = np.concatenate([self.pool(pieces[i:i + batch])
                                     for i in range(0, len(pieces), batch)])
            weights = np.array([end - start for start, end, _, _ in chunks], dtype=np.float64)
            vector = np.average(embeds.reshape(len(chunks), 2, 768).mean(1), axis=0, weights=weights)
            result.append(vector.astype(np.float32))
            detail.append(dict(id=name, bp=len(seq), chunks=len(chunks),
                               tokens=[len(ids) for ids in encoded],
                               unknown_tokens=sum(ids.count(self.tokenizer.unk_token_id) for ids in encoded),
                               intervals=[[a, b] for a, b, _, _ in chunks]))
        return np.stack(result), detail


def supervise(command, directory, seconds, max_rss):
    """Run one isolated worker; kill its group on failure/time/RAM, retain measurements.

    Sampling uses psutil and includes descendants. A dead parent never leaves a
    sleeping child to hold a log pipe open. No timeout increase or worker retry.
    """
    import psutil
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=False)
    start, peak, cpu, reason = time.monotonic(), 0, 0.0, None
    with (directory / 'terminal.log').open('w') as log, (directory / 'resources.jsonl').open('w') as metrics:
        process = subprocess.Popen(command, stdout=log, stderr=subprocess.STDOUT,
                                   start_new_session=True)
        live = psutil.Process(process.pid)
        sampled = 0
        try:
            while process.poll() is None:
                now = time.monotonic()
                try:
                    members = [live] + live.children(recursive=True)
                except psutil.NoSuchProcess:
                    break
                rss, total_cpu = 0, 0.0
                for member in members:
                    try:
                        rss += member.memory_info().rss
                        times = member.cpu_times()
                        total_cpu += times.user + times.system
                    except psutil.NoSuchProcess:
                        pass
                peak, cpu = max(peak, rss), max(cpu, total_cpu)
                if now - sampled >= 5:
                    metrics.write(json.dumps(dict(seconds=now-start, rss_bytes=rss,
                                                  cpu_seconds=total_cpu)) + '\n')
                    metrics.flush()
                    sampled = now
                if rss > max_rss:
                    reason = 'RAM ceiling'
                    break
                if now - start > seconds:
                    reason = 'Time ceiling'
                    break
                time.sleep(.2)
        except Exception as error:
            reason = 'Monitor failure: ' + repr(error)
            traceback.print_exc(file=log)
        finally:
            # Always clean this worker's group, including orphan descendants on fatal exit.
            try:
                os.killpg(process.pid, signal.SIGTERM)
            except ProcessLookupError:
                pass
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                os.killpg(process.pid, signal.SIGKILL)
                process.wait()
    wall = time.monotonic() - start
    status = dict(exit_code=process.returncode, stop_reason=reason, wall_seconds=wall,
                  peak_sampled_rss_bytes=peak, sampled_process_cpu_seconds=cpu,
                  sampled_average_cpus=cpu / wall, thread_budget=4,
                  thread_budget_wall_hours=4 * wall / 3600,
                  scope='local process accounting, not UCloud billing', command=command)
    write_json(directory / 'supervisor.json', status)
    return status


def worker(config_path, output):
    """Execute native contracts and timing once, with incremental stage receipts."""
    print(json.dumps(dict(stage='worker_entered_before_numerical_imports', pid=os.getpid())), flush=True)
    import numpy as np
    import psutil
    import torch
    from threadpoolctl import threadpool_info
    output = Path(output)
    config = json.loads(Path(config_path).read_text())
    settings = config['settings']
    torch.set_num_threads(4)
    torch.set_num_interop_threads(1)
    torch.manual_seed(11)
    pin = json.loads((ROOT / config['model_pin']).read_text())
    model_dir = ROOT / config['model_directory']
    for name, info in pin['files'].items():
        if digest(model_dir / name) != info['sha256']:
            raise ValueError('Model asset hash mismatch: ' + name)
    result = dict(status='running', config=config, source_commit=subprocess.check_output(
        ['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(), stages=[], timings=[])

    def stage(name, **values):
        event = dict(stage=name, utc=time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()), **values)
        print(json.dumps(event), flush=True)
        result['stages'].append(event)
        write_json(output / 'result.json', result)

    stage('prepare_real_panel')
    rows, provenance, lengths = panel(ROOT / config['source_fasta'], config['source_sha256'],
                                      config['windows_per_length'])
    write_json(output / 'panel.json', dict(source_sha256=config['source_sha256'], rows=provenance))
    result['panel_ambiguity_bases'] = sum(sum(base not in 'ACGT' for base in seq) for _,seq in rows)
    with (output / 'windows.fna').open('w') as f:
        for name, seq in rows:
            f.write(f'>{name}\n{seq}\n')
    start = time.monotonic()
    extractor = Extractor(str(model_dir), settings)
    load_seconds = time.monotonic() - start
    module = importlib.import_module(type(extractor.model).__module__)
    assert module.flash_attn_qkvpacked_func is None  # Native author's PyTorch fallback.
    result['runtime'] = dict(python=sys.version, executable=sys.executable, platform=platform.platform(),
                             torch=torch.__version__, numpy=np.__version__,
                             torch_intraop=torch.get_num_threads(), torch_interop=torch.get_num_interop_threads(),
                             loader_workers=0, training=False, library_pools=threadpool_info(),
                             imports={name:importlib.import_module(name).__file__ for name in
                                      ('torch','transformers','numpy','einops','tokenizers')},
                             model_class_module=module.__file__, model_module_sha256=digest(module.__file__),
                             parameter_count=sum(p.numel() for p in extractor.model.parameters()),
                             model_load_seconds=load_seconds)
    if platform.system() == 'Darwin':
        result['runtime']['hardware'] = dict(zip(
            ('cpu', 'host_ram_bytes', 'physical_cores', 'logical_cpus'),
            subprocess.check_output(['sysctl', '-n', 'machdep.cpu.brand_string', 'hw.memsize',
                                     'hw.physicalcpu', 'hw.logicalcpu'], text=True).splitlines()))
    assert result['runtime']['model_module_sha256'] == pin['files']['bert_layers.py']['sha256']
    prefix = Path(sys.executable).parent.parent.resolve()
    assert all(Path(p).resolve().is_relative_to(prefix)
               for p in result['runtime']['imports'].values())
    assert all(p['num_threads'] <= 4 for p in result['runtime']['library_pools'])
    stage('model_loaded', seconds=load_seconds)

    first = rows[0][1]
    t0 = time.monotonic()
    cold, _ = extractor.extract(rows[:1])
    result['first_extraction_seconds'] = time.monotonic() - t0
    stage('cold_forward_complete', seconds=result['first_extraction_seconds'])
    # Direct author example uses unpadded single-sequence mean including special tokens.
    tokens = extractor.tokenizer(first, return_tensors='pt')['input_ids']
    with torch.inference_mode():
        author = extractor.model(tokens)[0][0].mean(0).numpy()
    np.testing.assert_allclose(extractor.pool([first])[0], author, rtol=2e-5, atol=2e-5)
    two = [rows[0][1], rows[2 * config['windows_per_length']][1]]
    singles = np.concatenate([extractor.pool([seq]) for seq in two])
    batched = extractor.pool(two)
    np.testing.assert_allclose(batched, singles, rtol=2e-5, atol=2e-5)
    np.testing.assert_allclose(extractor.pool(list(reversed(two)))[::-1], singles,
                               rtol=2e-5, atol=2e-5)
    with torch.inference_mode():
        padded = extractor.tokenizer(two, padding=True, return_tensors='pt')
        hidden = extractor.model(**padded)[0]
        naive = hidden.mean(1).numpy()
    assert np.max(np.abs(naive[0] - batched[0])) > 1e-4
    for name, seq in (rows[0], rows[-1]):
        a, _ = extractor.extract([(name, seq)])
        b, _ = extractor.extract([(name, reverse_complement(seq))])
        np.testing.assert_array_equal(a, b)
    # ALiBi source can expand beyond the config's 512; prove it on real DNA.
    medium = rows[-1][1][:settings['chunk_bp']]
    n_tokens = len(extractor.tokenizer(medium, truncation=False)['input_ids'])
    assert 512 < n_tokens <= settings['max_tokens']
    extractor.pool([medium])
    stage('native_contracts_passed', padded_batch_max_abs=float(np.max(np.abs(batched-singles))),
          padding_contamination_if_naive=float(np.max(np.abs(naive[0]-batched[0]))),
          tested_tokens_beyond_512=n_tokens, author_pool_max_abs=float(np.max(np.abs(extractor.pool([first])[0]-author))))

    all_features, details = [], []
    process = psutil.Process()
    for length in LENGTHS:
        group = [(name, seq) for name, seq in rows if len(seq) == length]
        extractor.extract(group[:1])  # Length-specific warmup; excluded from timing.
        cpu0 = sum(process.cpu_times()[:2])
        start = time.monotonic()
        features, records = extractor.extract(group)
        elapsed = time.monotonic() - start
        cpu = sum(process.cpu_times()[:2]) - cpu0
        tok = sum(sum(r['tokens']) for r in records)
        result['timings'].append(dict(bp=length, windows=len(group), seconds=elapsed,
                                      seconds_per_window=elapsed/len(group), process_cpu_seconds=cpu,
                                      average_cpus=cpu/elapsed, both_strands_tokens=tok,
                                      tokens_per_bp_including_specials=tok/(2*len(group)*length),
                                      chunks=sum(r['chunks'] for r in records)))
        all_features.append(features)
        details += records
        stage('length_timed', **result['timings'][-1])
    features = np.concatenate(all_features)
    assert np.isfinite(features).all() and not np.any(np.all(features == 0, axis=1))
    binding = bind_cache(rows, pin, settings)
    save_cache(output / 'features.npz', features, binding)
    np.testing.assert_array_equal(features, load_cache(output / 'features.npz', binding))
    reversed_binding = bind_cache(list(reversed(rows)), pin, settings)
    try:
        load_cache(output / 'features.npz', reversed_binding)
    except ValueError:
        pass
    else:
        raise AssertionError('Stale ordered-ID cache accepted')
    reference, _ = extractor.extract(rows[:1])
    np.testing.assert_array_equal(features[:1], reference)
    del extractor
    gc.collect()
    extractor = Extractor(str(model_dir), settings)
    reloaded, _ = extractor.extract(rows[:1])
    np.testing.assert_array_equal(reference, reloaded)
    assert all(p.grad is None for p in extractor.model.parameters())
    stage('cache_and_checkpoint_reload_passed')
    result['chunk_records'] = details
    rates = {r['bp']:r['seconds_per_window'] for r in result['timings']}

    def projection(population):
        # Apply the observed rate for the nearest tested length on a per-base basis.
        # This is deliberately labelled a rough length-stratified projection, not a run.
        groups = {str(k):dict(contigs=0, bp=0, projected_seconds=0.0) for k in LENGTHS}
        for length in population:
            nearest = min(LENGTHS, key=lambda k:abs(math.log(length/k)))
            g = groups[str(nearest)]
            g['contigs'] += 1
            g['bp'] += length
            g['projected_seconds'] += rates[nearest] * length / nearest
        total = sum(g['projected_seconds'] for g in groups.values())
        return dict(contigs=len(population), bp=sum(population), groups=groups,
                    projected_wall_hours=total/3600, four_thread_budget_hours=4*total/3600)

    result['projections'] = dict(
        method='Nearest tested log-length per-base rate; both strands/chunks included; no speedup assumed',
        limitations='Eight windows per length, local thermal/cache state, long-contig tails and sequence compression unmodelled; excludes setup/I/O/learning/clustering; not Linux measurements',
        synthetic_length_distribution=projection([k for k in LENGTHS for _ in range(2000)]),
        accepted_E001_fasta_timing_only=projection(lengths))
    result['status'] = 'completed'
    stage('complete', feature_shape=list(features.shape), feature_sha256=digest(output/'features.npz'))


def main():
    """Dispatch the one supervised run or its internal worker; never auto-retry."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--worker', action='store_true', help=argparse.SUPPRESS)
    args = parser.parse_args()
    if args.worker:
        try:
            worker(args.config, args.output)
        except BaseException:
            traceback.print_exc()
            sys.stdout.flush()
            sys.stderr.flush()
            os._exit(1)  # No background library teardown can keep a fatal worker alive.
        return 0
    config = json.loads(args.config.read_text())
    env_root = Path(sys.executable).parent.parent
    for key in ('PYTHONPATH', 'PYTHONHOME', 'PYTHONUSERBASE'):
        os.environ.pop(key, None)
    os.environ.update(PYTHONNOUSERSITE='1', TOKENIZERS_PARALLELISM='false', HF_HUB_OFFLINE='1',
                      TRANSFORMERS_OFFLINE='1', HF_HOME=str(args.output.resolve()/'hf-cache'),
                      OMP_NUM_THREADS='4', MKL_NUM_THREADS='4', OPENBLAS_NUM_THREADS='4',
                      VECLIB_MAXIMUM_THREADS='4', NUMEXPR_NUM_THREADS='4')
    if not str(env_root.resolve()).startswith(str((ROOT/'artifacts/d011-dnabert-s-spike/env').resolve())):
        raise ValueError('Use the separate pinned spike environment')
    command = [sys.executable, '-u', str(Path(__file__).resolve()), '--worker',
               '--config', str(args.config.resolve()), '--output', str(args.output.resolve())]
    status = supervise(command, args.output, config['limits']['seconds'], config['limits']['rss_bytes'])
    print(json.dumps(status, indent=2))
    return 0 if status['exit_code'] == 0 and not status['stop_reason'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
