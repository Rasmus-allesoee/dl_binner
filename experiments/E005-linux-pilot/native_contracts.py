#!/usr/bin/env python3
"""Tiny native mapper/depth/AMBER contract checks for the changed pilot adapters.

Use byte-bound real smoke DNA for new mapping reads; a handcrafted real SAM/BAM
tests flags/CIGAR/zeros, and synthetic CAMI truth tests evaluation boundaries.
No model training or accepted inference benchmark is repeated. Fixture scores
are software expectations, never scientific pilot utility measurements.
"""
import argparse
import csv
import json
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'scripts'))
from e005_pilot import axis, confirmed_recovery, map_reads, mean_depth, native, sample_reads
from e005_smoke import sha, write
from dl_binner.io import read_fasta


def contracts(mapping_prefix, amber_python, amber_source, root):
    """Exercise real commands/readers and assert predetermined non-biological outcomes."""
    root = Path(root).absolute(); root.mkdir(exist_ok=False)
    real = read_fasta(ROOT/'input/smoke/fresh.fna') if (ROOT/'input/smoke/fresh.fna').is_file() else read_fasta(ROOT/'artifacts/e005-linux-pilot/input/smoke/fresh.fna')
    fasta = root/'reference.fna'
    with fasta.open('x') as stream:
        for ident, dna in real:
            stream.write('>'+ident+'\n'+dna+'\n')
        stream.write('>fixture_short_zero\n'+real[0][1][:199]+'\n')
    source = root/'source.fq'
    dna = real[0][1]
    complement = str.maketrans('ACGT', 'TGCA')
    with source.open('x') as stream:
        for index in range(1, 25):
            start = 3*index
            a, b = dna[start:start+150], dna[start+150:start+300].translate(complement)[::-1]
            for mate, seq in ((1, a), (2, b)):
                stream.write(f'@S1R{index}/{mate}\n{seq}\n+\n'+150*'I'+'\n')
    chosen = root/'chosen.fq'
    sample_reads(source, 1, sha(source), 8, 100, chosen)
    sampler = json.loads(chosen.with_suffix('.sample.json').read_text())
    if sampler['selected_pairs'] != 8 or sampler['source_pairs'] != 24:
        raise AssertionError('Sampler lost pairs')
    strobealign, samtools = Path(mapping_prefix)/'bin/strobealign', Path(mapping_prefix)/'bin/samtools'
    bam = root/'mapped.bam'
    map_reads(fasta, chosen, 1, 'GI_sample_1', strobealign, samtools, 4, bam)
    mapped_depth = root/'mapped-depth.tsv'
    mean_depth(fasta, bam, 'GI_sample_1', samtools, 4, mapped_depth)
    if json.loads(mapped_depth.with_suffix('.depth.json').read_text())['aligned_base_observations'] == 0:
        raise AssertionError('Real perfect reads did not map')
    # Native BAM covers primary/DUP/QCFAIL, secondary/supplementary, MAPQ/BQ0,
    # overlapping mates, softclip/insertion/deletion/=/X and unused short references.
    flags = root/'flags.sam'
    with flags.open('x') as stream:
        stream.write('@HD\tVN:1.6\tSO:unsorted\n')
        for ident, length in axis(fasta):
            stream.write(f'@SQ\tSN:{ident}\tLN:{length}\n')
        ident = real[0][0]
        for index, flag in enumerate((0, 1024, 512, 1536, 256, 2048)):
            stream.write(f'flag{index}\t{flag}\t{ident}\t1\t0\t10M\t*\t0\t0\t{dna[:10]}\t'+10*'!'+'\n')
        for flag, pos in ((99, 1), (147, 5)):
            stream.write(f'overlap\t{flag}\t{ident}\t{pos}\t0\t10M\t=\t1\t14\t{dna[:10]}\t'+10*'!'+'\n')
        stream.write(f'complex\t0\t{ident}\t30\t0\t2S5M2I3M2D2=1X\t*\t0\t0\t{dna[:15]}\t'+15*'!'+'\n')
        stream.write('unmapped\t4\t*\t0\t0\t*\t*\t0\t0\t'+dna[:10]+'\t'+10*'!'+'\n')
    flag_bam = root/'flags.bam'
    native([samtools, 'sort', '-@', '3', '-o', flag_bam, flags], root/'flag-sort')
    write(flag_bam.with_suffix('.mapped.json'), dict(reference_sha256=sha(fasta), bam_sha256=sha(flag_bam), column='flags'))
    depth = root/'flags-depth.tsv'
    mean_depth(fasta, flag_bam, 'flags', samtools, 4, depth)
    report = json.loads(depth.with_suffix('.depth.json').read_text())
    if report['aligned_base_observations'] != 71 or report['zero_contigs'] != len(axis(fasta))-1:
        raise AssertionError('Native flag/CIGAR/zero contract changed')
    evaluate = root/'evaluation'; evaluate.mkdir()
    records = [dict(contig_id=i, bp=str(n), genome_id=g, confirmed_origin=c) for i, n, g, c in (
        ('a', 200000, 'A', '1'), ('short', 199, 'A', '1'), ('b', 200000, 'B', '1'), ('uncertain', 10526, 'A', '0'))]
    contigs = evaluate/'contigs.tsv'
    with contigs.open('x') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(records[0]), delimiter='\t', lineterminator='\n')
        writer.writeheader(); writer.writerows(records)
    export = evaluate/'raw.export'; export.mkdir()
    with (export/'assignments.tsv').open('x') as stream:
        writer = csv.writer(stream, delimiter='\t', lineterminator='\n')
        writer.writerow(['contig_id', 'length', 'bin_id', 'status', 'reason'])
        writer.writerows([['a',200000,'bin','assigned',''], ['short',199,'','excluded','below_min_length'],
                         ['b',200000,'','unassigned','noise'], ['uncertain',10526,'bin','assigned','']])
    write(evaluate/'verified.json', dict(status='completed', role='evaluation-only synthetic contract'))
    cfg = evaluate/'config.json'
    write(cfg, dict(contigs=str(contigs), amber_source=str(Path(amber_source).absolute())))
    saved = Path.cwd()
    try:
        os.chdir(evaluate)
        native([amber_python, '-I', '-u', ROOT/'scripts/e005_pilot.py', '--config', cfg, 'evaluate', '--mode', 'raw'], root/'amber')
    finally:
        os.chdir(saved)
    score = json.loads((evaluate/'raw.evaluation/r95.json').read_text())
    if abs(score['r95']-0.5*200000/200199) > 1e-12 or score['ambiguous_or_unscored_assigned_bp'] != 10526:
        raise AssertionError('Confirmed R95 denominator/purity changed')
    with (evaluate/'raw.evaluation/amber-per-bin.tsv').open() as stream:
        bins = list(csv.DictReader(stream, delimiter='\t'))
    if sum(float(r['total_length']) for r in bins) != 210526:
        raise AssertionError('Real AMBER did not retain all assigned bp')
    records[-1]['bp'] = '10527'
    if confirmed_recovery(records, {'a':'bin','uncertain':'bin'})['r95'] != 0:
        raise AssertionError('Confirmed purity boundary is not inclusive/exact')
    write(root/'verified.json', dict(status='completed', real_DNA=True, sampled_pairs=8,
        actual_mapping=True, native_depth_base_observations=71, zero_unused_short_reference=True,
        flags='exclude0x904; keepDUP/QCFAIL; overlap/BQ0/MAPQ0; no deletion/insert/softclip counting',
        native_AMBER=True, confirmed_R95_boundary=True, source_commit='f8b3a601043d13fc4227d5691c13561eb4490e50',
        scope='tiny real/native adapters and synthetic truth; no inference repeat or scientific utility claim'))


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    for name in ('mapping-prefix', 'amber-python', 'amber-source', 'root'):
        p.add_argument('--'+name, type=Path, required=True)
    a = p.parse_args()
    contracts(a.mapping_prefix, a.amber_python, a.amber_source, a.root)
