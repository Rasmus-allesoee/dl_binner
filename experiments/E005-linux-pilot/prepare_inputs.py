#!/usr/bin/env python3
"""Freeze smoke inputs and one capped GI pilot from accepted, unchanged assets.

No embeddings, training, partitions or biological scores are computed. Smoke
TNF rows reuse E003 cache bytes; synthetic sentinels/depth test contracts only.
Pilot genomes are hash-ranked after prospective fragmentation/size criteria,
then all their GSA contigs (including below 500 bp) are retained. Truth is used
only for controlled dataset construction, not model inputs or bin selection.
"""
import argparse
from collections import Counter, defaultdict
import csv
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'scripts'))
from e005_smoke import sha, write


def freeze_smoke(output):
    """Reuse twelve cached real rows and add two explicit exclusion sentinels."""
    import numpy as np
    from dl_binner.io import read_fasta, tnf
    output = Path(output)
    output.mkdir(parents=True, exist_ok=False)
    e003 = json.loads((ROOT/'experiments/E003-representation-screen/panel.json').read_text())
    fasta = ROOT/'artifacts/e003-representation-screen/input/fragments.fna'
    cache = ROOT/'artifacts/e003-representation-screen/run-001/tnf.features.npz'
    receipt = ROOT/'artifacts/e003-representation-screen/run-001/tnf.features.json'
    old = json.loads(receipt.read_text())
    if sha(fasta) != e003['fna_sha256'] or sha(cache) != old['sha256']:
        raise ValueError('Accepted E003 source changed')
    real = read_fasta(fasta)[:12]
    sentinel = [('SENTINEL_short_199', 'ACGT'*49+'ACG'), ('SENTINEL_ambiguous_768', 'N'*768)]
    rows = real+sentinel
    assembled = output/'assembly.fna'
    assembled.write_text(''.join(f'>{i}\n{s}\n' for i, s in rows))
    (output/'fresh.fna').write_text(''.join(f'>{i}\n{s}\n' for i, s in real[:2]))
    with np.load(cache, allow_pickle=False) as source:
        if source['ids'].tolist()[:12] != [i for i, s in real]:
            raise ValueError('Accepted cache axis changed')
        counts = old['detail']['valid_fourmers'][:12]
        added, added_counts = tnf(sentinel)
        values = np.vstack([source['features'][:12], added])
    np.savez_compressed(output/'tnf.npz', ids=np.array([i for i, s in rows]), features=values)
    panel = dict(fna_sha256=sha(assembled), rows=[dict(id=i, bp=len(s),
                 sequence_sha256=hashlib.sha256(s.encode()).hexdigest()) for i, s in rows])
    write(output/'panel.json', panel)
    write(output/'tnf.json', dict(sha256=sha(output/'tnf.npz'),
          panel_manifest_sha256=sha(output/'panel.json'),
          detail=dict(valid_fourmers=counts+added_counts.tolist())))
    depths = [[0, 0] if j == 0 else [0 if j % 3 == 0 else j, 0 if j % 2 == 0 else j*2] for j in range(len(rows))]
    # Deliberately reversed rows exercise contig matching; sample columns fixed.
    with (output/'mean-depth.tsv').open('x') as stream:
        stream.write('contig_id\tsmoke_A\tsmoke_B\n')
        for (ident, _), d in reversed(list(zip(rows, depths))):
            stream.write(ident+'\t'+'\t'.join(map(str, d))+'\n')
    expectations = dict(ids=[i for i, s in rows], samples=['smoke_A', 'smoke_B'], depth=depths,
                        eligible=[True]*12+[False, False],
                        exclusion_reason=['']*12+['below_min_length', 'no_valid_fourmers'])
    write(output/'provenance.json', dict(role='software smoke; real DNA + synthetic depths/sentinels, not biological evaluation',
          parent_fasta_sha256=sha(fasta), parent_tnf_sha256=sha(cache), parent_receipt_sha256=sha(receipt),
          parent_panel_sha256=sha(ROOT/'experiments/E003-representation-screen/panel.json'),
          reused_real_rows=12, extracted_synthetic_rows=2, expectations=expectations,
          files={p.name: dict(sha256=sha(p), bytes=p.stat().st_size) for p in sorted(output.iterdir())}))
    return expectations


def freeze_pilot(output, manifest_dir):
    """Select complete fragmented-genome GSA input, verify source/DNA and cap it.

    Reuse accepted E001's all-length coordinate/hash/domain records, not its
    length-filtered scientific matrix. No new exception to the D005 source policy.
    Full-source duplicate-strand groups inform conservative truth; ambiguous
    bases stay in bin-purity denominators, not confirmed-recovery numerators.
    """
    records_path = ROOT/'artifacts/e001-population-reviewed/contigs.jsonl'
    frozen = json.loads((ROOT/'experiments/E001-coverage-thinning/frozen-inputs.json').read_text())
    if sha(records_path) != frozen['outputs']['contigs.jsonl']:
        raise ValueError('Accepted all-length coordinate manifest changed')
    stats, records, cross = {}, [], defaultdict(set)
    with records_path.open() as stream:
        for line in stream:
            r = json.loads(line)
            records.append(r)
            cross[r['strand_invariant_sha256']].update(r['origins'])
            if r['domains'] == ['bacteria'] and len(r['origins']) == 1:
                v = stats.setdefault(r['origins'][0], Counter())
                v['bp'] += r['length']; v['contigs'] += 1
                v['eligible'] += r['length'] >= 500
                v['short'] += 500 <= r['length'] < 2500
                v['below_500'] += r['length'] < 500
    eligible = [g for g, v in stats.items() if v['bp'] >= 200000 and v['contigs'] <= 2500
                and v['eligible'] >= 10 and v['short'] > 0 and v['below_500'] > 0]
    ranking = sorted(eligible, key=lambda g: (hashlib.sha256(('E005-pilot:'+g).encode()).hexdigest(), g))
    genomes = ranking[:4]
    selected = [r for r in records if set(r['origins']) & set(genomes)]
    if len(genomes) != 4 or len(selected) > 6000 or sum(r['length'] for r in selected) > 20000000:
        raise ValueError('Frozen pilot exceeds cap; do not truncate genomes or enlarge automatically')
    original = {r['original_id']: r for r in selected}
    fasta = ROOT/'agent_context/inventory/per_bodysite/gastro_bam/gsa.fa'
    if sha(fasta) != frozen['source_sha256']['fasta']:
        raise ValueError('Cached GI full-source byte mismatch')
    output = Path(output)
    output.mkdir(parents=True, exist_ok=False)
    found = {}
    # Streaming parser permits the two known empty orphans in the full source;
    # selected records are required nonempty and individually hash-bound.
    def consume(ident, chunks):
        if ident not in original:
            return
        dna = ''.join(chunks)
        r = original[ident]
        if ident in found or len(dna) != r['length'] or hashlib.sha256(dna.encode()).hexdigest() != r['sha256']:
            raise ValueError('Pilot original-coordinate/DNA mismatch')
        found[ident] = dna
    ident, chunks = None, []
    with fasta.open() as stream:
        for line in stream:
            if line.startswith('>'):
                consume(ident, chunks)
                ident, chunks = line[1:].split()[0], []
            elif ident in original:
                chunks.append(line.strip())
        consume(ident, chunks)
    if set(found) != set(original):
        raise ValueError('Missing selected GI contigs')
    with (output/'assembly.fna').open('x') as stream:
        for r in selected:
            dna = found[r['original_id']].upper()
            stream.write('>'+r['id']+'\n')
            stream.write('\n'.join(dna[i:i+80] for i in range(0, len(dna), 80))+'\n')
    manifest_dir = Path(manifest_dir)
    manifest_dir.mkdir(parents=True, exist_ok=True)
    with (manifest_dir/'pilot-contigs.tsv').open('x') as stream:
        fields = ['contig_id', 'bp', 'genome_id', 'original_id', 'sequence_sha256', 'confirmed_origin', 'truth_reason']
        writer = csv.writer(stream, delimiter='\t', lineterminator='\n'); writer.writerow(fields)
        for r in selected:
            confirmed = (len(r['origins']) == 1 and r['domains'] == ['bacteria']
                         and len(cross[r['strand_invariant_sha256']]) == 1)
            writer.writerow([r['id'], r['length'], ';'.join(r['origins']), r['original_id'],
                             r['sha256'], int(confirmed), 'unique_origin' if confirmed else 'cross_origin_or_ambiguous'])
    boundaries = [1, 500, 768, 1000, 2500, 10000]
    strata = {}
    for lo, hi in zip(boundaries, boundaries[1:]+[None]):
        points = [r for r in selected if r['length'] >= lo and (hi is None or r['length'] < hi)]
        strata[str(lo)] = dict(upper_bp=hi, contigs=len(points), bp=sum(r['length'] for r in points))
    e003 = json.loads((ROOT/'experiments/E003-representation-screen/sources.json').read_text())
    e003_accessions = {s[k] for s in e003['sources'] for k in ('accession_version', 'genbank_equivalent') if s.get(k)}
    accessions = sorted({r['original_id'].split('_from_')[0] for r in selected})
    write(manifest_dir/'pilot-inputs.json', dict(record='E005', role='transductive GI development GSA derivative; not independent/real assembler MAG test',
          parent_all_length_records_sha256=sha(records_path), parent_fasta_sha256=sha(fasta),
          original_dataset_doi='10.4126/FRL01-006425518', policy='accepted D005 coordinate/quarantine identities, retained unchanged',
          selection=dict(salt='E005-pilot:', genomes=4, per_genome_max_contigs=2500,
                         min_genome_bp=200000, min_eligible_contigs=10, require_below_500=True,
                         require_500_to_2499=True, eligible_genomes=len(eligible), hash_ranked=ranking),
          genomes={g: dict(stats[g]) for g in genomes}, input_contigs=len(selected),
          input_bp=sum(r['length'] for r in selected), length_strata=strata,
          fasta_sha256=sha(output/'assembly.fna'), fasta_bytes=(output/'assembly.fna').stat().st_size,
          contig_manifest_sha256=sha(manifest_dir/'pilot-contigs.tsv'),
          e001_retained_id_overlap=sum(r['retained'] for r in selected),
          e003_exact_accession_overlap=sorted(set(accessions)&e003_accessions),
          accession_versions=accessions, overlap_limit='same GI community as E001; accession inequality does not exclude homolog/strain/sequence overlap; no GLM used'))
    return genomes


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=('smoke', 'pilot'))
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--manifest-dir', type=Path)
    args = parser.parse_args()
    if args.mode == 'pilot':
        if args.manifest_dir is None:
            parser.error('--manifest-dir required for pilot')
        print(freeze_pilot(args.output, args.manifest_dir))
    else:
        print(json.dumps(freeze_smoke(args.output)))
