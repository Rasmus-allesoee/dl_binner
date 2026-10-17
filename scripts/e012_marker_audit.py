#!/usr/bin/env python3
"""Diagnose retained marker copies using existing PAFs, never select partitions.

    Gene/domain projections reuse admitted v2 alignment/competition/circular/N
    semantics. The output is separate diagnostic evidence, not a replacement
    truth, a marker whitelist, a new detection pass or an acceptance-rule input.
"""
import argparse
from collections import Counter, defaultdict
import hashlib
from itertools import combinations
import json
from pathlib import Path
import sys
import time

sys.path.insert(0, str(Path(__file__).absolute().parent))
from e009_common import binding, write_json
from e009_truth import union
from e009_truth_v2 import parse_paf, reconcile_one
from e010_review import require
from e012_acceptance import REPO, EXP, verify_inputs


def clip_span(left, right, blocks, vetoes):
    """Clip paired plus/minus canonical pieces and vetoes to one half-open query span."""
    require(type(left) is int and type(right) is int and 0 <= left < right, 'Malformed audit span')
    values = []
    for piece in blocks:
        a, b = max(left, piece['q0']), min(right, piece['q1'])
        if a >= b:
            continue
        r0, r1 = ((piece['r0']+a-piece['q0'], piece['r0']+b-piece['q0']) if piece['strand'] == '+'
                  else (piece['r0']+piece['q1']-b, piece['r0']+piece['q1']-a))
        values.append(dict(piece, q0=a-left, q1=b-left, r0=r0, r1=r1))
    clipped_vetoes = [[max(left, a)-left, min(right, b)-left] for a, b in vetoes
                      if max(left, a) < min(right, b)]
    return reconcile_one(right-left, values, clipped_vetoes, .95)


def classify_pair(left, right):
    """Describe source-locus evidence without claiming biological copy universality."""
    l, r = left['source_intervals'], right['source_intervals']
    overlap = sum(max(0, min(b, d)-max(a, c)) for ref in set(l)&set(r)
                  for a, b in union(l[ref]) for c, d in union(r[ref]))
    unique = [sum(b-a for spans in x['source_intervals'].values() for a, b in union(spans))
              for x in [left, right]]
    same = left['AMBER_label'] is not None and left['AMBER_label'] == right['AMBER_label']
    localized = all(n >= .95*x['length'] for n, x in zip(unique, [left, right]))
    if not localized or left['AMBER_label'] is None or right['AMBER_label'] is None:
        state = 'unresolved_competition_N_or_locus_support'
    elif same and overlap:
        state = 'same_genome_overlapping_locus_duplication_candidate'
    elif same and set(l)&set(r):
        state = 'same_genome_distinct_loci_same_provided_replicon'
    elif same:
        state = 'same_genome_distinct_provided_replicons'
    else:
        state = 'different_provided_genomes'
    return dict(classification=state, same_genome_label=same, source_overlap_bp=overlap,
                unique_source_bp=unique, gene_localization_at_least_95_percent=localized)


def verify_truth(lock, base=REPO):
    """Read only the separately admitted manifest/files/policy and frozen population."""
    root = Path(base)/lock['truth_root']
    require(binding(root/'manifest.json') == lock['manifest'], 'Admitted truth manifest differs')
    manifest = json.loads((root/'manifest.json').read_text())
    require(manifest['files'] == lock['truth_files'], 'Admitted truth file set differs')
    for name, record in lock['truth_files'].items():
        require(binding(root/name) == record, 'Admitted truth bytes differ: '+name)
    require(binding(Path(base)/lock['population_path']) == lock['population']
            and binding(Path(base)/lock['policy_path']) == lock['policy'], 'Population/policy differs')
    return root


def profile_headers(path):
    """Read pinned profile names/accessions/descriptions/trusted cutoffs, without search."""
    records = {}; current = {}
    with Path(path).open() as stream:
        for raw in stream:
            key, _, value = raw.strip().partition(' ')
            if key in ['NAME', 'ACC', 'DESC', 'LENG', 'TC']:
                current[key] = value.strip()
            if raw.strip() == '//':
                require(current.get('NAME') not in records and 'TC' in current, 'Malformed HMM header')
                records[current['NAME']] = current; current = {}
    require(not current, 'Truncated HMM headers')
    return records


def audit(input_lock_path, review_lock_path, output, base=REPO):
    """Project all adopted seed calls in both contexts, retaining all PAF competitors."""
    started = time.monotonic(); base, output = Path(base), Path(output)
    output.mkdir(parents=True, exist_ok=False)
    inputs, lock = [json.loads(Path(p).read_text()) for p in [input_lock_path, review_lock_path]]
    verify_inputs(inputs, base); truth_root = verify_truth(lock, base)
    require(binding(base/lock['paf_path']) == lock['paf'], 'Retained PAF differs; no aligner fallback')
    truth = json.loads((truth_root/'truth.json').read_text())
    refs = json.loads((truth_root/'reference-map.json').read_text())
    policy = json.loads((base/lock['policy_path']).read_text())
    cache = base/inputs['cache']/'candidate/markers'
    evidence = json.loads((cache/'evidence.json').read_text()); asset = json.loads((cache/'asset.json').read_text())
    proposals, wanted = [], set()
    for context, (_, post_path) in inputs['contexts'].items():
        post = json.loads((base/post_path).read_text())
        for attempt in post['attempts']:
            if not attempt['adopted']:
                continue
            calls = [c for c in evidence['calls'] if c['contig'] in attempt['seed_ids'] and c['family'] == attempt['seed_family']]
            require(set(c['contig'] for c in calls) == set(attempt['seed_ids']), 'Missing retained seed call')
            proposals.append(dict(context=context, pre_bin=attempt['pre_bin'], seed_family=attempt['seed_family'],
                                  seed_ids=attempt['seed_ids'], calls=calls))
            wanted.update(c['gene'] for c in calls)
    genes = {}
    with (cache/'genes.jsonl').open() as stream:
        for line in stream:
            g = json.loads(line)
            if g['gene'] in wanted:
                genes[g['gene']] = g
    require(set(genes) == wanted, 'Missing seed gene metadata')
    proteins = {}; key = None; parts = []
    def finish():
        """Bind only requested retained amino-acid sequences, without realignment."""
        if key in wanted:
            proteins[key] = hashlib.sha256(''.join(parts).encode()).hexdigest()
    with (cache/'proteins.faa').open() as stream:
        for line in stream:
            if line.startswith('>'):
                finish(); key = line[1:].strip(); parts = []
            elif key in wanted:
                parts.append(line.strip())
        finish()
    require(set(proteins) == wanted, 'Missing seed protein bytes')
    selected_ids = {g['contig'] for g in genes.values()}; subset = output/'all-seed-competitors.paf'
    with (base/lock['paf_path']).open() as src, subset.open('x') as dst:
        for raw in src:
            if raw.split('\t', 1)[0] in selected_ids:
                dst.write(raw)
    lengths = {q: truth['contigs'][q]['length'] for q in selected_ids}
    blocks, vetoes, row_counts = parse_paf(subset, lengths, refs['aliases'], policy)
    hmm = base/lock['hmm_path']
    require(binding(hmm) == asset['hmm'], 'Pinned marker profile differs')
    headers = profile_headers(hmm)
    profiles = {family: [headers[m] for m, f in asset['families'].items() if f == family]
                for family in {r['seed_family'] for r in proposals}}
    domains = json.loads((cache/'domains.json').read_text())
    summaries = defaultdict(Counter)
    for proposal in proposals:
        call_records = []
        for call in proposal.pop('calls'):
            gene = genes[call['gene']]; q = gene['contig']
            gene_projection = clip_span(gene['start'], gene['end'], blocks[q], vetoes[q])
            domain_projection = clip_span(call['start'], call['end'], blocks[q], vetoes[q])
            reference_metadata = {rid: refs['canonical_references'][rid] for projection in [gene_projection, domain_projection]
                                  for rid in projection['source_intervals']}
            genome_metadata = {g: refs['genomes'][g] for projection in [gene_projection, domain_projection]
                               for g in projection['confirmed_query_bp']}
            call_records.append(dict(call=call, gene=gene, protein_sha256=proteins[call['gene']],
                whole_contig_label=truth['contigs'][q]['AMBER_label'], gene_projection=gene_projection,
                domain_projection=domain_projection, canonical_reference_metadata=reference_metadata,
                genome_metadata=genome_metadata,
                native_domains=[d for d in domains if d['gene'] == call['gene'] and asset['families'][d['marker']] == call['family']]))
        pairs = []
        for left, right in combinations(call_records, 2):
            if left['gene']['contig'] == right['gene']['contig']:
                continue
            pair = dict(genes=[left['gene']['gene'], right['gene']['gene']],
                        contigs=[left['gene']['contig'], right['gene']['contig']],
                        identical_retained_protein=left['protein_sha256'] == right['protein_sha256'],
                        gene=classify_pair(left['gene_projection'], right['gene_projection']),
                        domain=classify_pair(left['domain_projection'], right['domain_projection']))
            pairs.append(pair); summaries[proposal['context']][pair['gene']['classification']] += 1
        proposal.update(calls=call_records, pairs=pairs)
    result = dict(status='SUCCESS', input_lock=binding(input_lock_path), review_lock=binding(review_lock_path),
                  scope='all retained adopted seed proposals; diagnostic only, never selector input',
                  full_paf=lock['paf'], subset=binding(subset), selected_contigs=len(selected_ids),
                  selected_genes=len(genes), row_counts=row_counts, profile_headers=profiles,
                  pair_classifications={k: dict(v) for k, v in summaries.items()}, proposals=proposals,
                  limits=['Provided reference loci establish distinct sequence locations, not functional annotation or universal single-copy biology.',
                          'Trusted HMM family membership can include true paralogs or family cross-reactivity; no reference reannotation/search was run.',
                          'Whole-chain identity is inherited; gene-specific nucleotide identity was not independently measured.',
                          'Same-genome repeated-locus ambiguity and all nn competitors remain unresolved; no unsupported unique support is granted.',
                          'Different source replicons are reported literally; chromosome/plasmid identity is not invented from an accession.'],
                  no_new_alignment_detection_or_truth_admission=True, wall_seconds=time.monotonic()-started)
    write_json(output/'audit.json', result)
    return result


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--lock', type=Path, default=EXP/'input-lock.json')
    p.add_argument('--review-lock', type=Path, default=EXP/'review-lock.json')
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args(); audit(a.lock, a.review_lock, a.output)
