#!/usr/bin/env python3
"""Measure E024 aligned read-base means without storing a community SAM/BAM.

Inputs are a checksum-admitted interleaved FASTQ and the complete opaque-ID
reference. The streaming primary-alignment counter has O(contigs) memory and
never allocates per-base tracks. Means count overlapping mates twice, M/= /X
only, MAPQ >= 20, BQ >= 0, excluding unmapped/secondary/supplementary/QCFAIL/DUP.
It is deliberately not a fragment-coverage, breadth or variance estimator.
Every producer exit and full FASTQ/SAM axis/count contract must pass before seal.
"""
from array import array
from collections import Counter
import gzip
import hashlib
import io
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import threading
import time
import urllib.request

SAMPLES = [6, 7, 8, 13, 14, 15, 16, 17, 18, 19]
EXCLUDE = 0xF04
CIGAR = re.compile(r'([1-9][0-9]*)([MIDNSHP=X])')


def binding(path):
    """Hash a regular owned/input file without following an artifact symlink."""
    p = Path(path)
    if p.is_symlink() or not p.is_file():
        raise ValueError('Regular artifact required: ' + str(p))
    h = hashlib.sha256();done=0;last=time.monotonic();total=p.stat().st_size
    with p.open('rb') as f:
        for b in iter(lambda: f.read(1024**2), b''):
            h.update(b)
            done+=len(b)
            if time.monotonic()-last>=5:
                print('E024_VERIFY_BYTES',str(p),done,total,'epoch',time.time(),flush=True)
                last=time.monotonic()
    return dict(bytes=p.stat().st_size, sha256=h.hexdigest())


def write(path, value):
    """Write a closed exclusive JSON record; no accepted record is overwritten."""
    with Path(path).open('x') as f:
        json.dump(value, f, indent=2, allow_nan=False)
        f.write('\n')


def axis(reference):
    """Return the full ordered ID/length axis, refusing empty/duplicate/invalid DNA."""
    ids, lengths, seen = [], array('Q'), set()
    ident, size = None, 0
    with Path(reference).open() as f:
        for raw in f:
            line = raw.strip()
            if not line:
                continue
            if line.startswith('>'):
                if ident is not None:
                    if not size:
                        raise ValueError('Empty reference DNA')
                    lengths.append(size)
                parts = line[1:].split()
                if not parts or parts[0] in seen:
                    raise ValueError('Duplicate/missing reference ID')
                ident, size = parts[0], 0
                seen.add(ident)
                ids.append(ident)
            else:
                if ident is None or set(line.upper()) - set('ACGTRYSWKMBDHVN'):
                    raise ValueError('Invalid reference DNA')
                size += len(line)
    if ident is None or not size:
        raise ValueError('Empty reference')
    lengths.append(size)
    return ids, lengths


def verify_segments(stream, segments, destination, progress=None):
    """Copy one object once, checking each publisher segment MD5 and new full hashes.

    Swift DLO ETag is MD5(concatenated segment-MD5 hex strings), not the MD5 of
    the FASTQ. The independently calculated whole MD5 is recorded as new only.
    This function also tests the exact production copier with tiny real bytes.
    """
    total, sha, whole_md5 = 0, hashlib.sha256(), hashlib.md5()
    for i, part in enumerate(segments):
        if type(part['bytes']) is not int or part['bytes'] <= 0 or not re.fullmatch('[0-9a-f]{32}', part['md5']):
            raise ValueError('Malformed publisher segment manifest')
        remaining, md5 = part['bytes'], hashlib.md5()
        while remaining:
            b = stream.read(min(1024**2, remaining))
            if not b:
                raise ValueError('Truncated publisher read object')
            destination.write(b)
            remaining -= len(b)
            total += len(b)
            md5.update(b)
            sha.update(b)
            whole_md5.update(b)
            if progress:
                progress(total)
        if md5.hexdigest() != part['md5']:
            raise ValueError('Publisher segment MD5 differs: ' + str(i))
    if stream.read(1):
        raise ValueError('Publisher object larger than admitted segments')
    return dict(bytes=total, sha256=sha.hexdigest(), calculated_whole_MD5=whole_md5.hexdigest(),
                publisher_segment_MD5_passed=len(segments))


def acquire_segments(record, output, opener=urllib.request.urlopen):
    """Acquire the publisher's exact public segments once in frozen byte order.

    This explicit transport avoids an inaccessible DLO aggregate GET. It does
    not weaken byte admission: validate each segment's length/ETag/MD5, the DLO
    aggregate and whole byte count, and calculate new whole MD5/SHA256 while
    concatenating. Preserve partial output on any error; never retry/fallback.
    """
    output=Path(output);started=time.time();parts=record['segments']
    aggregate=hashlib.md5(''.join(x['md5'] for x in parts).encode()).hexdigest()
    if (sum(x['bytes'] for x in parts)!=record['bytes'] or
            aggregate!=record.get('DLO_aggregate_md5',aggregate)):
        raise ValueError('Frozen segment aggregate/whole length differs')
    total=0;sha=hashlib.sha256();md5=hashlib.md5();last=time.monotonic()
    with output.open('xb') as destination:
        class WholeWriter:
            def write(self, b):
                nonlocal total
                total+=len(b);sha.update(b);md5.update(b);return destination.write(b)
        def progress(n):
            nonlocal last
            if time.monotonic()-last>5:
                print('E024_DOWNLOAD_BYTES',record['sample'],total,flush=True);last=time.monotonic()
        for index,part in enumerate(parts):
            request=urllib.request.Request(part['url'],headers={'Accept-Encoding':'identity'})
            with opener(request,timeout=60) as source:
                if (source.status!=200 or int(source.headers['Content-Length'])!=part['bytes']
                        or source.headers.get('ETag','').strip('"')!=part['md5']):
                    raise ValueError('Publisher segment HEAD/GET identity differs')
                verify_segments(source,[part],WholeWriter(),progress)
            print('E024_PUBLISHER_SEGMENT_PASS',record['sample'],index,total,flush=True)
    if total!=record['bytes']:raise ValueError('Concatenated publisher object differs')
    result=dict(bytes=total,sha256=sha.hexdigest(),calculated_whole_MD5=md5.hexdigest(),
                publisher_segment_MD5_passed=len(parts),sample=record['sample'],manifest=record,
                elapsed_seconds=time.time()-started,transport='Frozen public segment GETs in order; no DLO GET/fallback/retry')
    write(str(output)+'.acquired.json',result)
    return result


def acquire(record, output, opener=urllib.request.urlopen):
    """Acquire exact admitted bytes by frozen segments or the tiny whole-object fixture."""
    if record['segments'] and all(p.get('url') for p in record['segments']):
        return acquire_segments(record,output,opener)
    output = Path(output)
    started = time.time()
    if sum(p['bytes'] for p in record['segments']) != record['bytes']:
        raise ValueError('Publisher segment/whole sizes differ')
    request = urllib.request.Request(record['url'], headers={'Accept-Encoding': 'identity'})
    last = time.monotonic()
    def progress(n):
        nonlocal last
        if time.monotonic() - last > 5:
            print('E024_DOWNLOAD_BYTES', record['sample'], n, flush=True)
            last = time.monotonic()
    with opener(request, timeout=60) as source, output.open('xb') as sink:
        if source.status != 200 or int(source.headers['Content-Length']) != record['bytes']:
            raise ValueError('Full publisher object/HEAD differs')
        result = verify_segments(source, record['segments'], sink, progress)
    result['elapsed_seconds'] = time.time()-started
    write(str(output) + '.acquired.json', dict(result, sample=record['sample'], manifest=record))
    return result


def mate_identity(header):
    """Parse /1,/2 or CASAVA mate suffixes; never repair ambiguous/swapped mates."""
    fields = header.rstrip().split()
    if not fields or not fields[0].startswith(b'@'):
        raise ValueError('Malformed FASTQ read ID')
    name, mate = fields[0][1:], None
    if name.endswith((b'/1', b'/2')):
        mate, name = int(name[-1:]), name[:-2]
    if len(fields) > 1 and fields[1][:2] in (b'1:', b'2:'):
        comment_mate = int(fields[1][:1])
        if mate is not None and mate != comment_mate:
            raise ValueError('Conflicting FASTQ mate annotations')
        mate = comment_mate
    if not name:
        raise ValueError('Empty FASTQ read ID')
    return name, mate


def fastq_pairs(first, second=None):
    """Stream strict paired/interleaved FASTQ, including complete gzip CRC validation.

    Unannotated repeated pair IDs are accepted only as two adjacent equal names;
    explicit annotations must be 1 then 2. No whole-dataset ID set is retained.
    """
    def open_read(p):
        return gzip.open(p, 'rb') if str(p).endswith('.gz') else open(p, 'rb')
    def one(f):
        h = f.readline()
        if not h:
            return None
        s, plus, quality = f.readline(), f.readline(), f.readline()
        sequence = s.removesuffix(b'\n').removesuffix(b'\r')
        qualities = quality.removesuffix(b'\n').removesuffix(b'\r')
        if (not s.endswith(b'\n') or not plus.startswith(b'+') or not quality.endswith(b'\n')
                or len(sequence) != len(qualities) or not sequence
                or set(sequence.upper()) - set(b'ACGTRYSWKMBDHVN')
                or any(c < 33 or c > 126 for c in qualities)):
            raise ValueError('Malformed FASTQ sequence/quality')
        mate_identity(h)
        return h, s, plus, quality
    with open_read(first) as a:
        b = open_read(second) if second else a
        try:
            while True:
                left, right = one(a), one(b)
                if left is None and right is None:
                    break
                if left is None or right is None:
                    raise ValueError('Unpaired/truncated FASTQ')
                x, y = mate_identity(left[0]), mate_identity(right[0])
                if x[0] != y[0] or (x[1], y[1]) not in [(1, 2), (None, None)]:
                    raise ValueError('Mismatched/swapped FASTQ mates')
                yield left, right
        finally:
            if second:
                b.close()


def identity_hash(name, mate):
    """Hash source-blind read identity for order-independent full-stream accounting."""
    return int.from_bytes(hashlib.sha256(name+b'\0'+str(mate).encode()).digest(),'big')


def sum_sam(stream, ids, lengths, min_mapq=20, paired=False):
    """Sum aligned M/= /X bases in O(contigs) memory; refuse malformed SAM.

    The full SQ axis must equal the reference in order and length. All primary
    mapped and unmapped reads are counted, enabling comparison with feeder reads.
    Coordinates/CIGAR/SEQ are validated before filtering; missing rows are not
    converted to zero. Zero means a complete measured stream with zero support.
    """
    lookup = {q: i for i, q in enumerate(ids)}
    if len(lookup) != len(ids) or len(lengths) != len(ids):
        raise ValueError('Invalid reference axis')
    totals, counts, header, started = array('Q', [0]) * len(ids), Counter(), [], False
    qhist = Counter()
    for raw in stream:
        line = raw.rstrip('\n')
        if not line:
            raise ValueError('Blank SAM row')
        f = line.split('\t')
        if line.startswith('@'):
            if started:
                raise ValueError('SAM header after alignments')
            if f[0] == '@SQ':
                tags = dict(x.split(':', 1) for x in f[1:])
                header.append((tags['SN'], int(tags['LN'])))
            continue
        if not started:
            if header != list(zip(ids, lengths)):
                raise ValueError('SAM full reference axis differs')
            started = True
        if len(f) < 11 or not f[0] or f[0] == '*':
            raise ValueError('Malformed SAM fields')
        flag, pos, mq = int(f[1]), int(f[3]), int(f[4])
        if not 0 <= flag <= 65535 or not 0 <= mq <= 255 or pos < 0:
            raise ValueError('Invalid SAM flags/quality/position')
        counts['SAM_records'] += 1
        if not flag & (0x100 | 0x800):
            counts['primary_reads'] += 1
            if paired:
                if not flag & 1 or bool(flag & 64) == bool(flag & 128):
                    raise ValueError('Primary paired SAM mate flag differs')
                qname = f[0].encode()
                if qname.endswith((b'/1',b'/2')):qname=qname[:-2]
                counts['primary_identity_sum'] = (counts['primary_identity_sum']+identity_hash(qname,1 if flag & 64 else 2)) % (1<<256)
        if flag & 4:
            counts['unmapped'] += 1
            continue
        if f[2] not in lookup or pos < 1 or f[5] == '*':
            raise ValueError('Mapped SAM reference/coordinate absent')
        operations = CIGAR.findall(f[5])
        if ''.join(n + op for n, op in operations) != f[5]:
            raise ValueError('Malformed SAM CIGAR')
        ref_span = sum(int(n) for n, op in operations if op in 'MDN=X')
        query_span = sum(int(n) for n, op in operations if op in 'MIS=X')
        row = lookup[f[2]]
        if not ref_span or pos - 1 + ref_span > lengths[row]:
            raise ValueError('Alignment outside reference')
        if f[9] != '*' and (query_span != len(f[9]) or (f[10] != '*' and len(f[10]) != len(f[9]))):
            raise ValueError('CIGAR/SEQ/QUAL length differs')
        if (f[9] == '*' and not flag & (0x100 | 0x800)) or (f[9] != '*' and set(f[9].upper())-set('ACGTRYSWKMBDHVN')):
            raise ValueError('Primary/mapped SAM sequence missing or invalid')
        if f[10] != '*' and any(ord(c)<33 or ord(c)>126 for c in f[10]):
            raise ValueError('Invalid SAM quality byte')
        if not flag & (0x100 | 0x800):
            qhist[mq] += 1
        if flag & EXCLUDE:
            counts['excluded_flag'] += 1
        elif mq == 255 or mq < min_mapq:
            counts['excluded_MAPQ'] += 1
        else:
            size = sum(int(n) for n, op in operations if op in 'M=X')
            totals[row] += size
            counts['accepted_alignments'] += 1
            counts['aligned_read_bases'] += size
    if header != list(zip(ids, lengths)):
        raise ValueError('Missing/truncated SAM header')
    return totals, dict(counts), dict(sorted(qhist.items()))


def read_profile(first, second=None):
    """Measure the first 500 pairs' uniform ART length before choosing index profile.

    This is an input-format gate, not an outcome-selected treatment. Subsequent
    full-stream validation must match that measured length for every read.
    """
    sizes = set()
    pairs = fastq_pairs(first, second)
    try:
        for i, pair in enumerate(pairs):
            sizes.update(len(r[1].rstrip()) for r in pair)
            if i == 499:
                break
    finally:
        pairs.close()
    if len(sizes) != 1 or not 100 <= next(iter(sizes)) <= 500:
        raise ValueError('Uniform 100–500 bp ART read profile required; no implicit repair')
    return next(iter(sizes))


def map_summary(mapper, reference, reads, output, second=None, use_index=True,
                expected_read_length=150, mapper_threads=2, sample=None, bam_retention=None):
    """Feed validated pairs to the real mapper and summarize stdout, with both exits.

    Native use assigns four mapper workers + one validation/decompression thread
    + one summary process + up to two mapper I/O helpers inside eight CPUs. The
    production worker enforces Linux affinity; tiny tests may use fewer workers.
    No shell pipe can conceal a producer failure.
    The original FASTQ stays until the sealed summary explicitly permits cleanup.
    """
    out = Path(output)
    out.mkdir(parents=True, exist_ok=False)
    ids, lengths = axis(reference)
    argv = [str(mapper), '-t', str(mapper_threads), '-r', str(expected_read_length), '-N', '0', '--interleaved']
    if use_index:
        argv.append('--use-index')
    argv += [str(reference), '-']
    write(out/'started.json', dict(argv=argv, reference=binding(reference), reads=binding(reads),
                                  second=binding(second) if second else None))
    retained = None
    if bam_retention:
        from e024_alignment import BamRetention
        retained = BamRetention(log_root=out, **bam_retention)
    fed, errors = dict(pairs=0, reads=0, bases=0, primary_identity_sum=0), []
    with (out/'mapper.stderr.log').open('x') as log:
        process = subprocess.Popen(argv, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=log)
        def feed():
            try:
                for pair in fastq_pairs(reads, second):
                    for mate, read in enumerate(pair,1):
                        size = len(read[1].rstrip())
                        if size != expected_read_length:
                            raise ValueError('Frozen read length/profile differs')
                        process.stdin.write(b''.join(read))
                        fed['reads'] += 1
                        fed['bases'] += size
                        fed['primary_identity_sum'] = (fed['primary_identity_sum']+identity_hash(mate_identity(read[0])[0],mate)) % (1<<256)
                    fed['pairs'] += 1
                    if fed['pairs'] % 100000 == 0:
                        print('E024_VALIDATED_PAIRS', fed['pairs'], flush=True)
            except BaseException as exc:
                errors.append(repr(exc))
            finally:
                try:
                    process.stdin.close()
                except BrokenPipeError:
                    pass
        worker = threading.Thread(target=feed, daemon=True)
        worker.start()
        try:
            with io.TextIOWrapper(process.stdout, encoding='ascii') as stream:
                totals, counts, histogram = sum_sam(retained.lines(stream) if retained else stream, ids, lengths, paired=True)
            exit_code = process.wait(timeout=60)
            worker.join(60)
            if (worker.is_alive() or errors or exit_code or counts.get('primary_reads', 0) != fed['reads']
                    or counts.get('primary_identity_sum',0) != fed['primary_identity_sum']):
                raise RuntimeError('Mapper/FASTQ/count contract failed: ' + str((exit_code, errors, fed, counts)))
            retention = retained.finish(counts['SAM_records']) if retained else None
            if retention:write(out/'alignment-retained.json', retention)
            target = out/'depth.tsv'
            with target.open('x') as f:
                f.write('contig_id\taligned_read_bases\tlength\tmean\n')
                for ident, length, total in zip(ids, lengths, totals):
                    f.write(f'{ident}\t{total}\t{length}\t{total/length:.17g}\n')
            result = dict(status='PASS', sample=sample, reference=binding(reference), reads=binding(reads),
                          second=binding(second) if second else None, rows=len(ids), bp=sum(lengths),
                          depth=binding(target), feeder=fed, counters=counts, MAPQ_histogram=histogram,
                          zero_rows=sum(v == 0 for v in totals), mapper_exit=exit_code,
                          retained_alignment=retention,
                          policy='M/= /X; MAPQ >=20 except unknown255; BQ0; exclude0xF04; overlapping mates twice; full contig denominator; no variance; unfiltered primary BAM retained separately when admitted')
            write(out/'done.json', result)
            return result
        except BaseException as exc:
            write(out/'failed.json', dict(error=repr(exc), feeder=fed, input_errors=errors))
            raise
        finally:
            if retained:retained.close()
            if process.poll() is None:
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait(timeout=5)
            worker.join(5)


def combine(reference, summaries, samples, output):
    """Stream a strict full-axis ordered ten-column matrix from verified summaries."""
    import contextlib
    if samples != SAMPLES or len(summaries) != len(SAMPLES):
        raise ValueError('Frozen ordered ten sample axis required')
    ids, lengths = axis(reference)
    reference_hash = binding(reference)
    with contextlib.ExitStack() as stack:
        readers, receipts = [], []
        for p, sample in zip(map(Path, summaries), samples):
            receipt = json.loads((p.parent/'done.json').read_text())
            if (receipt['status'] != 'PASS' or receipt['reference'] != reference_hash
                    or receipt['depth'] != binding(p) or receipt.get('sample') != sample):
                raise ValueError('Summary provenance/sample bytes differ')
            f = stack.enter_context(p.open())
            if f.readline() != 'contig_id\taligned_read_bases\tlength\tmean\n':
                raise ValueError('Summary header differs')
            readers.append(f)
            receipts.append(binding(p.parent/'done.json'))
        with Path(output).open('x') as sink:
            sink.write('\t'.join(['contig_id'] + [f'oral_sample_{s}' for s in samples]) + '\n')
            for ident, length in zip(ids, lengths):
                values = []
                for f in readers:
                    row = f.readline().rstrip('\n').split('\t')
                    if len(row) != 4 or row[0] != ident or int(row[2]) != length or int(row[1]) < 0:
                        raise ValueError('Missing/malformed full summary axis')
                    value = int(row[1])/length
                    if row[3] != f'{value:.17g}':
                        raise ValueError('Summary full-length mean differs')
                    values.append(row[3])
                sink.write('\t'.join([ident] + values) + '\n')
            if any(f.read(1) for f in readers):
                raise ValueError('Extra summary rows')
    result = dict(status='PASS', reference=reference_hash, summaries=receipts,
                  samples=[f'oral_sample_{s}' for s in samples], rows=len(ids), bp=sum(lengths),
                  matrix=binding(output), all_cells_measured=True, missing_cells=0,
                  semantics='Measured aligned read-base parent means; all-zero rows retained; no per-base/window variance')
    write(str(output)+'.receipt.json', result)
    return result
