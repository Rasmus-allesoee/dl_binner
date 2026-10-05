#!/usr/bin/env python3
"""Frozen E005 GI pilot rule adapters: sample, map, depth, verify and evaluate.

Operate on byte-bound explicit manifests, not inferred filenames or truth-based
choices. Heavy commands are supervised by e005_rule.py in a serial Snakemake DAG.
Only evaluate() reads origins. No E001 result, encoder setting or clustering rule
is changed; all short, zero, excluded and unassigned rows remain accounted for.
"""
import argparse
from collections import Counter, defaultdict
from fractions import Fraction
import gzip
import hashlib
import heapq
import json
import math
from pathlib import Path
import re
import subprocess
import sys
import time

sys.path.insert(0, str(Path(__file__).resolve().parent))
from e005_smoke import progress, sha, write


def read(path):
    """Read a retained JSON contract or receipt."""
    return json.loads(Path(path).read_text())


def axis(fasta):
    """Read strict FASTA IDs/lengths without loading the whole reference in memory."""
    result, ident, bp = [], None, 0
    seen = set()
    with Path(fasta).open() as stream:
        for line in stream:
            line = line.strip()
            if line.startswith('>'):
                if ident is not None:
                    if not bp:
                        raise ValueError('Empty reference sequence')
                    result.append((ident, bp))
                ident = line[1:].split()[0] if line[1:].strip() else ''
                if not ident or ident in seen:
                    raise ValueError('Empty/duplicate reference ID')
                seen.add(ident)
                bp = 0
            elif line:
                if ident is None or set(line.upper())-set('ACGTRYSWKMBDHVN'):
                    raise ValueError('Invalid FASTA DNA')
                bp += len(line)
    if ident is None or not bp:
        raise ValueError('Empty FASTA/sequence')
    return result+[(ident, bp)]


def pairs(stream, sample, digest):
    """Yield complete anonymous 150-bp pairs and offsets, hashing every source byte.

    The accepted E001 anonymous source numbers increase strictly. Enforce this
    source-specific invariant to detect duplicate/reordered names in constant RAM.
    No filtering by mapping, genome, sequence or a biological label occurs.
    """
    previous, ordinal = -1, 0
    pattern = re.compile(rb'@S'+str(sample).encode()+rb'R(0|[1-9][0-9]*)/1\n')
    dna_pattern = re.compile(rb'[ACGTRYSWKMBDHVNacgtryswkmbdhvn]{150}')
    quality_pattern = re.compile(rb'[!-~]{150}')
    while True:
        offset = stream.tell()
        first = stream.readline(1024)
        if not first:
            return
        lines = [first]+[stream.readline(1024) for _ in range(7)]
        if any(not line.endswith(b'\n') for line in lines):
            raise ValueError('Broken/odd/overlong FASTQ pair')
        match = pattern.fullmatch(first)
        if not match or int(match[1]) <= previous:
            raise ValueError('Wrong/duplicate/non-increasing anonymous pair ID')
        ident = first[1:-3]
        if lines[4] != b'@'+ident+b'/2\n':
            raise ValueError('Mismatched mate ID')
        for start in (0, 4):
            dna, qual = lines[start+1][:-1], lines[start+3][:-1]
            if len(dna) != 150 or len(qual) != 150 or lines[start+2] != b'+\n':
                raise ValueError('FASTQ must have 150 bases/qualities and bare +')
            if not dna_pattern.fullmatch(dna) or not quality_pattern.fullmatch(qual):
                raise ValueError('Invalid FASTQ DNA/quality')
        raw = b''.join(lines)
        digest.update(raw)
        previous = int(match[1])
        ordinal += 1
        yield ordinal, ident.decode('ascii'), offset, raw


class Rank:
    """Reverse digest/ID comparison gives heapq an exact maximum-rank root."""
    __slots__ = ('digest', 'ident', 'offset', 'ordinal')

    def __init__(self, digest, ident, offset, ordinal):
        self.digest, self.ident, self.offset, self.ordinal = digest, ident, offset, ordinal

    def __lt__(self, other):
        return (self.digest, self.ident) > (other.digest, other.ident)


def sample_reads(source, sample, expected_sha, count, max_pairs, output):
    """Two-pass exact bottom-hash sampling; retain ranks/offsets, never a DNA heap.

    Pass one validates and hashes the complete source, retaining at most count
    ranks. Pass two validates/hashes it again and emits chosen pairs in source
    order. A changed/short/malformed source never gets a successful receipt.
    Retain partial files on error; callers use unique attempts and fail fast.
    """
    source, output = Path(source), Path(output)
    if count < 1 or max_pairs < count:
        raise ValueError('Invalid sampling cap')
    output.parent.mkdir(parents=True, exist_ok=True)
    digest, ranks, total = hashlib.sha256(), [], 0
    salt = ('E005-S'+str(sample)+'-pairs-v1:').encode()
    with source.open('rb') as stream:
        for total, ident, offset, raw in pairs(stream, sample, digest):
            if total > max_pairs:
                raise ValueError('Source pair ceiling exceeded')
            rank = Rank(hashlib.sha256(salt+ident.encode()).digest(), ident, offset, total)
            if len(ranks) < count:
                heapq.heappush(ranks, rank)
            elif rank < ranks[0]:
                pass  # worse than the current largest retained digest
            else:
                heapq.heapreplace(ranks, rank)
            if total % 1_000_000 == 0:
                progress('sampling_pass_1', sample=sample, source_pairs=total, retained=len(ranks))
    if digest.hexdigest() != expected_sha:
        raise ValueError('Source FASTQ checksum mismatch')
    if total < count:
        raise ValueError('Too few complete source pairs; no silent smaller sample')
    selected = {r.ordinal: r for r in ranks}
    largest = max((r.digest.hex(), r.ident) for r in ranks)
    digest2, emitted, final_total = hashlib.sha256(), 0, 0
    selection = output.with_suffix('.selection.tsv.gz')
    with source.open('rb') as stream, output.open('xb') as out, selection.open('xb') as sf:
        with gzip.GzipFile(fileobj=sf, mode='wb', mtime=0) as report:
            report.write(b'pair_id\tsource_pair_ordinal\tsource_byte_offset\n')
            for final_total, ident, offset, raw in pairs(stream, sample, digest2):
                if final_total in selected:
                    rank = selected[final_total]
                    if (ident, offset) != (rank.ident, rank.offset):
                        raise ValueError('Source changed between sampling passes')
                    out.write(raw)
                    report.write(f'{ident}\t{final_total}\t{offset}\n'.encode())
                    emitted += 1
                if final_total % 1_000_000 == 0:
                    progress('sampling_pass_2', sample=sample, source_pairs=final_total, emitted=emitted)
    if digest2.hexdigest() != expected_sha or final_total != total or emitted != count:
        raise ValueError('Source changed or emitted sample incomplete')
    write(output.with_suffix('.sample.json'), dict(status='completed', sample=sample, source=str(source),
        source_sha256=expected_sha, source_bytes=source.stat().st_size, source_pairs=total, selected_pairs=emitted,
        salt=salt.decode(), rank_threshold=largest, sampled_sha256=sha(output), sampled_bytes=output.stat().st_size,
        selection_sha256=sha(selection), selection_bytes=selection.stat().st_size,
        policy='full SHA256 then pair ID; original order; two complete validation/hash passes; no truth access'))


def native(command, prefix, stdout=None):
    """Run a real native command, retaining stderr, argv and exit/time provenance.

    The rule supervisor covers this worker and descendants. The fallback timeout
    bounds direct tiny-fixture calls; an error raises and stops subsequent calls.
    """
    prefix = Path(prefix)
    command = [str(c) for c in command]
    started = time.monotonic()
    result, error = None, None
    try:
        with Path(str(prefix)+'.stderr').open('x') as err, Path(stdout or str(prefix)+'.stdout').open('xb') as out:
            result = subprocess.run(command, stdout=out, stderr=err, timeout=1800)
    except BaseException as exc:
        error = repr(exc)
        raise
    finally:
        write(str(prefix)+'.command.json', dict(argv=command, exit_code=result.returncode if result else None,
              error=error, wall_seconds=time.monotonic()-started))
    if result.returncode:
        raise RuntimeError('Native worker failed: '+str(prefix))


def bam_axis(samtools, bam, fasta, log):
    """Require coordinate-sort status and the exact ordered reference ID/length axis."""
    header = Path(str(log)+'.header.sam')
    native([samtools, 'view', '-H', bam], str(log)+'.header', stdout=header)
    rows, sorted_header = [], False
    for line in header.read_text().splitlines():
        fields = line.split('\t')
        if fields[0] == '@HD':
            sorted_header = 'SO:coordinate' in fields
        if fields[0] == '@SQ':
            value = dict(f.split(':', 1) for f in fields[1:])
            rows.append((value['SN'], int(value['LN'])))
    if not sorted_header or rows != axis(fasta):
        raise ValueError('BAM reference/sort axis differs from exact pilot FASTA')
    return rows


def map_reads(fasta, reads, sample, column, strobealign, samtools, threads, output):
    """Serial full-budget mapping then sort/index, with a verified sampled-read receipt."""
    fasta, reads, output = Path(fasta), Path(reads), Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    receipt = read(reads.with_suffix('.sample.json'))
    if receipt['sample'] != sample or sha(reads) != receipt['sampled_sha256']:
        raise ValueError('Wrong sampled reads/receipt')
    if not 1 <= threads <= 4:
        raise ValueError('Invalid native CPU budget')
    sam = output.with_suffix('.sam')
    native([strobealign, '-t', threads, '-r', '150', '--rg-id', column, '--rg', 'SM:'+column,
            fasta, '--interleaved', reads], output.with_suffix('.map'), stdout=sam)
    native([samtools, 'sort', '-@', threads-1, '-m', '512M', '-T', output.with_suffix('.sort-tmp'),
            '-o', output, sam], output.with_suffix('.sort'))
    native([samtools, 'index', '-@', threads-1, output], output.with_suffix('.index'))
    native([samtools, 'quickcheck', '-v', output], output.with_suffix('.quickcheck'))
    rows = bam_axis(samtools, output, fasta, output.with_suffix('.axis'))
    native([samtools, 'flagstat', '-@', threads-1, output], output.with_suffix('.flagstat'))
    write(output.with_suffix('.mapped.json'), dict(status='completed', sample=sample, column=column,
          reference_sha256=sha(fasta), reads_sha256=sha(reads), sample_receipt_sha256=sha(reads.with_suffix('.sample.json')),
          bam_sha256=sha(output), bam_bytes=output.stat().st_size, index_sha256=sha(output.with_suffix('.bam.bai')),
          sam_sha256=sha(sam), sam_bytes=sam.stat().st_size, reference_axis=rows,
          allocated_threads=threads, mapper_threads=threads, sort_extra_threads=threads-1,
          policy='serial SAM then coordinate BAM; no pre-filter; depth excludes 0x904'))


def parse_depth(stream, rows, digest):
    """Sum a native -aa stream; reject missing/duplicate/reordered positions or IDs."""
    sums = []
    for ident, length in rows:
        total = 0
        for pos in range(1, length+1):
            raw = stream.readline()
            digest.update(raw)
            fields = raw.decode('ascii').rstrip('\n').split('\t')
            if len(fields) != 3 or fields[0] != ident or int(fields[1]) != pos:
                raise ValueError('Native depth has missing/reordered/duplicate reference positions')
            value = int(fields[2])
            if value < 0:
                raise ValueError('Negative native depth')
            total += value
        sums.append(total)
    if stream.readline():
        raise ValueError('Unexpected additional depth/reference row')
    return sums


def mean_depth(fasta, bam, column, samtools, threads, output):
    """Stream exact M/= /X depth means, including actual native zeros and short rows.

    Native depth main+extra workers plus this Python stream aggregator fit the
    allocation: at four CPUs use two extra BGZF workers, one native main and one
    aggregator. No deletion/overlap trimming; -g clears DUP/QCFAIL defaults and
    -G adds SUPPLEMENTARY, yielding the frozen 0x904 exclusion mask.
    """
    if threads < 2 or threads > 4:
        raise ValueError('Streaming depth needs 2–4 allocated CPUs, including aggregator')
    fasta, bam, output = Path(fasta), Path(bam), Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    mapped = read(bam.with_suffix('.mapped.json'))
    if mapped['reference_sha256'] != sha(fasta) or mapped['bam_sha256'] != sha(bam) or mapped['column'] != column:
        raise ValueError('BAM/reference/sample receipt mismatch')
    rows = bam_axis(samtools, bam, fasta, output.with_suffix('.axis'))
    command = [str(samtools), 'depth', '-aa', '-q', '0', '-Q', '0', '-g', '0x600', '-G', '0x800',
               '-@', str(threads-2), str(bam)]
    digest, process, started = hashlib.sha256(), None, time.monotonic()
    with output.with_suffix('.stderr').open('x') as error:
        try:
            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=error)
            sums = parse_depth(process.stdout, rows, digest)
            process.stdout.close()
            if process.wait(timeout=10):
                raise RuntimeError('Native depth failed')
        finally:
            if process and process.poll() is None:
                process.terminate()
                try:
                    process.wait(timeout=2)
                except subprocess.TimeoutExpired:
                    process.kill(); process.wait(timeout=2)
    with output.open('x') as stream:
        stream.write('contig_id\t'+column+'\n')
        for (ident, length), total in zip(rows, sums):
            stream.write(ident+'\t'+format(total/length, '.17g')+'\n')
    write(output.with_suffix('.depth.json'), dict(status='completed', column=column, command=command,
        wall_seconds=time.monotonic()-started, reference_sha256=sha(fasta), bam_sha256=mapped['bam_sha256'],
        mapped_receipt_sha256=sha(bam.with_suffix('.mapped.json')), native_stream_sha256=digest.hexdigest(),
        native_positions=sum(n for i, n in rows), contigs=len(rows), aligned_base_observations=sum(sums),
        zero_contigs=sum(v == 0 for v in sums), native_extra_workers=threads-2, python_aggregator_workers=1,
        table_sha256=sha(output), table_bytes=output.stat().st_size,
        policy='M/= /X over full lengths; MAPQ/BQ0; exclude0x904; keepDUP/QCFAIL/overlap; no invented rows'))


def combine_depth(fasta, tables, columns, output):
    """Merge only exact validated axes into the frozen ordered explicit depth columns."""
    rows, matrices, receipts = axis(fasta), [], []
    if len(tables) != len(columns) or len(set(columns)) != len(columns):
        raise ValueError('Depth sample axis is empty/duplicate/missing')
    for table, column in zip(map(Path, tables), columns):
        report = read(table.with_suffix('.depth.json'))
        if report['reference_sha256'] != sha(fasta) or report['column'] != column or report['table_sha256'] != sha(table):
            raise ValueError('Mean-depth receipt/reference/sample mismatch')
        with table.open() as stream:
            if stream.readline().rstrip('\n') != 'contig_id\t'+column:
                raise ValueError('Wrong depth header')
            values = []
            for ident, length in rows:
                fields = stream.readline().rstrip('\n').split('\t')
                if len(fields) != 2 or fields[0] != ident:
                    raise ValueError('Depth row axis mismatch')
                value = float(fields[1])
                if not math.isfinite(value) or value < 0:
                    raise ValueError('Nonfinite/negative depth')
                values.append(fields[1])
            if stream.readline():
                raise ValueError('Extra depth ID')
        matrices.append(values)
        receipts.append(dict(table=str(table), sha256=sha(table), receipt_sha256=sha(table.with_suffix('.depth.json'))))
    with Path(output).open('x') as stream:
        stream.write('contig_id\t'+'\t'.join(columns)+'\n')
        for index, (ident, length) in enumerate(rows):
            stream.write(ident+'\t'+'\t'.join(m[index] for m in matrices)+'\n')
    write(Path(output).with_suffix('.depth.json'), dict(status='completed', samples=columns,
          reference_sha256=sha(fasta), reference_contigs=len(rows), tables=receipts, table_sha256=sha(output)))


def verify_outputs(cfg, output):
    """Independently validate real pilot arrays, masks, saved inference and all exports."""
    import csv
    import numpy as np
    from dl_binner.io import load_arrays, read_fasta, validate_features
    source = dict(read_fasta(cfg['fasta']))
    features, meta = load_arrays('features.npz', 'features')
    validate_features(features, meta)
    if features['ids'].tolist() != list(source) or meta['samples'] != cfg['columns']:
        raise ValueError('Pilot feature/sample axis mismatch')
    with Path('mean-depth.tsv').open() as stream:
        depth = list(csv.reader(stream, delimiter='\t'))
    if depth[0] != ['contig_id']+cfg['columns'] or [r[0] for r in depth[1:]] != list(source):
        raise ValueError('Explicit measured depth axis mismatch')
    np.testing.assert_array_equal(features['depth'], np.asarray([r[1:] for r in depth[1:]], dtype=np.float32))
    np.testing.assert_array_equal(features['zero_depth'], features['depth'] == 0)
    np.testing.assert_array_equal(features['depth_evidence'], (features['depth'] > 0).any(1))
    np.testing.assert_array_equal(features['eligible'], (features['lengths'] >= 500) & (features['valid_fourmers'] > 0))
    learned, _ = load_arrays('learned.embeddings.npz', 'embeddings')
    reference, _ = load_arrays('checkpoint.reference.npz', 'embeddings')
    for key in ('ids', 'evidence'):
        np.testing.assert_array_equal(learned[key], reference[key])
    np.testing.assert_allclose(learned['features'], reference['features'], atol=1e-7, rtol=0)
    training = read('checkpoint.json')
    if training['config'] != read(cfg['training']) or training['numerical_threads'] != cfg['threads'] or training['loader_workers'] != 0:
        raise ValueError('Training schedule/CPU budget changed')
    if any(e['contigs_seen'] != int(features['eligible'].sum()) for e in training['epochs']):
        raise ValueError('Training dropped eligible IDs')
    accounting = {}
    for mode in ('raw', 'learned'):
        found, folder = {}, Path(mode+'.export')
        for path in folder.glob('*.fna'):
            for ident, dna in read_fasta(path) if path.stat().st_size else []:
                if ident in found:
                    raise ValueError('Duplicate exported contig')
                found[ident] = dna
        if found != source:
            raise ValueError('Export omitted or changed DNA')
        export = read(folder/'manifest.json')
        for name, entry in export['files'].items():
            if sha(folder/name) != entry['sha256']:
                raise ValueError('Export receipt differs')
        with (folder/'assignments.tsv').open() as stream:
            rows = list(csv.DictReader(stream, delimiter='\t'))
        if [r['contig_id'] for r in rows] != list(source):
            raise ValueError('Assignment row lost')
        for row, eligible, reason in zip(rows, features['eligible'], features['exclusion_reason']):
            if not eligible and (row['status'] != 'excluded' or row['reason'] != reason):
                raise ValueError('Exclusion reason lost')
        accounting[mode] = {k: sum(r['status'] == k for r in rows) for k in ('assigned', 'unassigned', 'excluded')}
    write(output, dict(status='completed', rows=len(source), bp=sum(map(len, source.values())), samples=meta['samples'],
        eligible=int(features['eligible'].sum()), below_500=int((features['lengths'] < 500).sum()),
        zero_depth_rows=int((~features['depth_evidence']).sum()), accounting=accounting,
        reload_max_abs=float(np.max(np.abs(learned['features']-reference['features']))),
        scope='software/output accounting; biological metrics run only afterward'))


def confirmed_recovery(records, assignments):
    """Frozen conservative assembled-sequence R95, independent of AMBER majority ties.

    Match E001's unique-origin purity numerator and full assigned-bin denominator.
    Keep below-500/noise in full confirmed genome denominators, inclusive purity
    and recovery boundaries, 200-kb minimum genome/bin and deterministic bin ties.
    """
    lengths = {r['contig_id']: int(r['bp']) for r in records}
    confirmed = {r['contig_id']: r['genome_id'] for r in records if r['confirmed_origin'] == '1'}
    genomes = sorted({r['genome_id'] for r in records})
    if len(lengths) != len(records) or set(assignments)-lengths.keys():
        raise ValueError('Duplicate/unknown evaluation IDs')
    totals, bin_bp, overlap = Counter(), Counter(), Counter()
    for ident, genome in confirmed.items():
        totals[genome] += lengths[ident]
    if not genomes or any(totals[g] < 200_000 for g in genomes):
        raise ValueError('Frozen genome lacks minimum confirmed assembled denominator')
    for ident, group in assignments.items():
        bin_bp[group] += lengths[ident]
        if ident in confirmed:
            overlap[group, confirmed[ident]] += lengths[ident]
    result = {}
    for genome in genomes:
        candidates = [(bp, group) for (group, g), bp in overlap.items()
                      if g == genome and bin_bp[group] >= 200_000 and 100*bp >= 95*bin_bp[group]]
        bp, group = sorted(candidates, key=lambda v: (-v[0], v[1]))[0] if candidates else (0, None)
        result[genome] = dict(total_bp=totals[genome], recovered_bp=bp, bin=group, r95=bp/totals[genome],
                             bin_bp=bin_bp[group] if group is not None else None,
                             confirmed_purity=bp/bin_bp[group] if group is not None else None)
        strata, bounds = [], [1, 500, 768, 1000, 2500, 10000]
        for index, lower in enumerate(bounds):
            upper = bounds[index+1] if index+1 < len(bounds) else None
            ids = [i for i, g in confirmed.items() if g == genome and lengths[i] >= lower
                   and (upper is None or lengths[i] < upper)]
            total = sum(lengths[i] for i in ids)
            recovered = sum(lengths[i] for i in ids if group is not None and assignments.get(i) == group)
            strata.append(dict(lower_bp=lower, upper_bp=upper, total_bp=total, recovered_bp=recovered,
                               recovery=recovered/total if total else None))
        result[genome]['length_strata'] = strata
    return dict(r95=sum(v['r95'] for v in result.values())/len(genomes),
        r95_base_weighted=sum(v['recovered_bp'] for v in result.values())/sum(totals.values()),
        inclusive_recovered_counts={str(t): sum(Fraction(v['recovered_bp'], v['total_bp']) >= Fraction(str(t))
            for v in result.values()) for t in (0.5, 0.9)}, per_genome=result,
        assigned_bp=sum(bin_bp.values()), unassigned_bp=sum(lengths.values())-sum(bin_bp.values()),
        ambiguous_or_unscored_assigned_bp=sum(lengths[i] for i in assignments if i not in confirmed))


def evaluate(cfg, mode, output):
    """Score completed exports using the pinned native AMBER API plus confirmed R95.

    This is the sole truth-consuming path. All exports must already pass software
    verification. Empty assignments are a valid zero-recovery outcome, not a
    reason to force a bin or discard short/noise/excluded rows.
    """
    import csv
    if read('verified.json')['status'] != 'completed' or mode not in ('raw', 'learned'):
        raise ValueError('Evaluation prerequisite missing')
    output = Path(output); output.mkdir(exist_ok=False)
    with Path(cfg['contigs']).open() as stream:
        records = list(csv.DictReader(stream, delimiter='\t'))
    with Path(mode+'.export/assignments.tsv').open() as stream:
        rows = list(csv.DictReader(stream, delimiter='\t'))
    if [r['contig_id'] for r in rows] != [r['contig_id'] for r in records]:
        raise ValueError('Truth/assignment axes differ')
    assignments = {}
    for row in rows:
        if row['status'] not in ('assigned', 'unassigned', 'excluded'):
            raise ValueError('Unknown assignment state')
        if row['status'] == 'assigned':
            if not row['bin_id']:
                raise ValueError('Assigned ID has no bin')
            assignments[row['contig_id']] = row['bin_id']
    result = confirmed_recovery(records, assignments)
    write(output/'r95.json', result)
    for name, truth in (('truth.tsv', True), ('predictions.tsv', False)):
        with (output/name).open('x') as stream:
            stream.write('@Version:0.9.0\n@SampleID:E005\n@@SEQUENCEID\tBINID'+('\t_LENGTH' if truth else '')+'\n')
            for row in records:
                ident = row['contig_id']
                if truth:
                    stream.write(ident+'\t'+row['genome_id']+'\t'+row['bp']+'\n')
                elif ident in assignments:
                    stream.write(ident+'\t'+assignments[ident]+'\n')
    if assignments:
        sys.path.insert(0, cfg['amber_source'])
        from cami_amber.binning_classes import GenomeQuery, Options
        from cami_amber.utils.load_data import read_metadata
        options = Options(filter_tail_percentage=0, skip_heatmap=True)
        gold = GenomeQuery('gold', 'E005', options, read_metadata((str(output/'truth.tsv'), 'gold'))[0], is_gs=True)
        query = GenomeQuery(mode, 'E005', options, read_metadata((str(output/'predictions.tsv'), mode))[0])
        query.gold_standard = gold
        query.compute_metrics()
        if int(query.precision_df['total_length'].sum()) != result['assigned_bp']:
            raise ValueError('Native AMBER assigned bp differ')
        query.precision_df.to_csv(output/'amber-per-bin.tsv', sep='\t', index=True, index_label='BINID')
        query.recall_df.to_csv(output/'amber-per-genome.tsv', sep='\t', index=True, index_label='BINID')
    else:
        for name in ('amber-per-bin.tsv', 'amber-per-genome.tsv'):
            (output/name).write_text('BINID\n')
    strata, boundaries = [], [1, 500, 768, 1000, 2500, 10000]
    for index, lower in enumerate(boundaries):
        upper = boundaries[index+1] if index+1 < len(boundaries) else None
        subset = [(r, a) for r, a in zip(records, rows) if int(r['bp']) >= lower and (upper is None or int(r['bp']) < upper)]
        value = dict(lower_bp=lower, upper_bp=upper, contigs=len(subset), bp=sum(int(r['bp']) for r, a in subset))
        for status in ('assigned', 'unassigned', 'excluded'):
            value[status+'_contigs'] = sum(a['status'] == status for r, a in subset)
            value[status+'_bp'] = sum(int(r['bp']) for r, a in subset if a['status'] == status)
        value['reasons'] = dict(Counter(a['reason'] for r, a in subset if a['status'] != 'assigned'))
        value['confirmed_total_bp'] = sum(int(r['bp']) for r, a in subset if r['confirmed_origin'] == '1')
        value['confirmed_recovered_bp'] = sum(int(r['bp']) for r, a in subset if r['confirmed_origin'] == '1'
            and result['per_genome'][r['genome_id']]['bin'] is not None
            and assignments.get(r['contig_id']) == result['per_genome'][r['genome_id']]['bin'])
        strata.append(value)
    write(output/'evaluation.json', dict(status='completed', mode=mode, seed=11,
        r95=result['r95'], assigned_bp=result['assigned_bp'], strata=strata,
        assignment_sha256=sha(mode+'.export/assignments.tsv'), truth_manifest_sha256=sha(cfg['contigs']),
        amber_source_commit='f8b3a601043d13fc4227d5691c13561eb4490e50',
        amber='native filter_tail_percentage=0' if assignments else 'empty valid partition; no AMBER prediction rows',
        scope='four-genome GI development GSA derivative; assembled recovery, not whole-MAG/generalization'))


def main():
    """Dispatch one frozen rule from its resolved explicit input/runtime configuration."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', required=True, type=Path)
    parser.add_argument('action', choices=('sample', 'map', 'depth', 'combine', 'verify', 'evaluate'))
    parser.add_argument('--sample', type=int)
    parser.add_argument('--mode', choices=('raw', 'learned'))
    args = parser.parse_args(); cfg = read(args.config)
    if args.action in ('sample', 'map', 'depth'):
        by_sample = {s['sample']: s for s in cfg['samples']}
        sample = by_sample[args.sample]; stem = Path('reads')/('sample_'+str(args.sample))
        fastq, bam = stem.with_suffix('.fq'), Path('mapping')/('sample_'+str(args.sample)+'.bam')
        if args.action == 'sample':
            sample_reads(sample['reads'], args.sample, sample['sha256'], cfg['sampled_pairs'], cfg['max_source_pairs'], fastq)
        elif args.action == 'map':
            map_reads(cfg['fasta'], fastq, args.sample, sample['column'], cfg['strobealign'], cfg['samtools'], cfg['threads'], bam)
        else:
            mean_depth(cfg['fasta'], bam, sample['column'], cfg['samtools'], cfg['threads'], Path('depth')/('sample_'+str(args.sample)+'.tsv'))
    elif args.action == 'combine':
        combine_depth(cfg['fasta'], [Path('depth')/('sample_'+str(s['sample'])+'.tsv') for s in cfg['samples']], cfg['columns'], 'mean-depth.tsv')
    elif args.action == 'verify':
        verify_outputs(cfg, 'verified.json')
    else:
        evaluate(cfg, args.mode, args.mode+'.evaluation')


if __name__ == '__main__':
    main()
