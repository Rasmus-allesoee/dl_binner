"""Label-independent alignment truth construction and conservative recovery.

Consumes all emitted minimap2 all-chain PAF/CIGAR matches, never feature inputs.
Coordinates are zero-based half-open. Competing genomes stay ambiguous; repeated
locations within one genome support genome purity but not unique locus recovery.
These are supplied-reference alignment diagnostics, not finished-MAG certification.
"""
from collections import defaultdict
import csv
import json
from pathlib import Path
import re
import sys
sys.path.insert(0, str(Path(__file__).absolute().parent))

from e009_common import binding, fasta, write_json


def union(intervals):
    """Return a merged half-open interval union; duplicates cannot inflate recovery."""
    result = []
    for left, right in sorted(intervals):
        if left < 0 or right <= left: raise ValueError('Invalid half-open interval')
        if result and left <= result[-1][1]: result[-1][1] = max(right, result[-1][1])
        else: result.append([left, right])
    return result


def parse_paf(path, query_lengths, references, identity=.99, min_bp=200):
    """Validate every PAF row and expand qualifying cg CIGAR into query/locus blocks.

    Require exact axes, endpoints and full CIGAR consumption. No MAPQ or dominant
    alignment filtering. PAF target coordinates ascend on both strands; reverse
    query coordinates descend. Insertions/deletions are never counted as aligned
    support. Malformed low-quality rows still fail instead of hiding a bad writer.
    """
    blocks = defaultdict(list); rows = accepted = 0
    with Path(path).open() as stream:
        for raw in stream:
            rows += 1; fields = raw.rstrip('\n').split('\t')
            if len(fields) < 12: raise ValueError('Malformed PAF row')
            qid, strand, rid = fields[0], fields[4], fields[5]
            qlen, qstart, qend, rlen, rstart, rend, matches, aln, mapq = map(int, [fields[i] for i in (1,2,3,6,7,8,9,10,11)])
            if qid not in query_lengths or rid not in references: raise ValueError('Unknown PAF axis ID')
            if qlen != query_lengths[qid] or rlen != references[rid]['length']:
                raise ValueError('PAF axis length mismatch')
            if strand not in ('+', '-') or not (0 <= qstart < qend <= qlen and 0 <= rstart < rend <= rlen):
                raise ValueError('PAF coordinate/orientation mismatch')
            if not (0 <= matches <= aln and aln > 0 and 0 <= mapq <= 255): raise ValueError('Invalid PAF counts')
            tags = {}
            for tag in fields[12:]:
                value = tag.split(':', 2)
                if len(value) != 3 or value[0] in tags: raise ValueError('Invalid/duplicate PAF tag')
                tags[value[0]] = value[1:]
            if 'cg' not in tags or tags['cg'][0] != 'Z': raise ValueError('Required cg CIGAR missing')
            cigar = tags['cg'][1]; ops = re.findall(r'(\d+)([MID=X])', cigar)
            if ''.join(n+op for n,op in ops) != cigar or any(int(n) <= 0 for n,_ in ops):
                raise ValueError('Unsupported CIGAR')
            q = qstart if strand == '+' else qend; r = rstart; pieces = []; aligned = 0; columns = 0
            for size, op in ops:
                size = int(size); columns += size
                if op in ('M', '=', 'X'):
                    qa, qb = (q, q+size) if strand == '+' else (q-size, q)
                    pieces.append({'q0': qa, 'q1': qb, 'r0': r, 'r1': r+size,
                                   'rid': rid, 'genome': references[rid]['genome'], 'strand': strand})
                    q += size if strand == '+' else -size; r += size; aligned += size
                elif op == 'I': q += size if strand == '+' else -size
                else: r += size
            if q != (qend if strand == '+' else qstart) or r != rend or columns != aln:
                raise ValueError('CIGAR/endpoints/block length disagree')
            if not any(op=='M' for _,op in ops) and sum(int(n) for n,op in ops if op=='=')!=matches:
                raise ValueError('eqx CIGAR/match count disagree')
            if aligned >= min_bp and matches / aln >= identity:
                accepted += 1; blocks[qid].extend(pieces)
    return blocks, {'paf_rows': rows, 'accepted_alignments': accepted, 'paf': binding(path)}


def reconcile(query_lengths, blocks, attributable=.95):
    """Globally reconcile all competing intervals before any label or reference union.

    Repeated same-locus matches are deduplicated. Same-genome multiple-locus matches
    are explicitly unresolved for completeness, while cross-genome segments are
    ambiguous for both purity and completeness. Unmapped/gap DNA remains unknown.
    """
    result = {}
    for qid, length in query_lengths.items():
        values = blocks.get(qid, []); boundaries = sorted({x for b in values for x in (b['q0'], b['q1'])})
        confirmed = defaultdict(int); loci = defaultdict(list); ambiguous = repeated = 0
        for a,b in zip(boundaries, boundaries[1:]):
            active = [v for v in values if v['q0'] <= a and v['q1'] >= b]
            genomes = {v['genome'] for v in active}
            if not genomes: continue
            if len(genomes) > 1: ambiguous += b-a; continue
            genome = next(iter(genomes)); confirmed[genome] += b-a
            locations = set()
            for v in active:
                if v['strand'] == '+': left, right = v['r0']+a-v['q0'], v['r0']+b-v['q0']
                else: left, right = v['r0']+v['q1']-b, v['r0']+v['q1']-a
                locations.add((v['rid'],left,right,v['strand']))
            if len(locations) == 1:
                rid,left,right,strand = next(iter(locations)); loci[rid].append([left,right])
            else: repeated += b-a
        best = sorted(confirmed, key=lambda g:(-confirmed[g],g))
        label = best[0] if best and confirmed[best[0]] / length >= attributable else None
        result[qid] = {'length': length, 'confirmed_query_bp': dict(confirmed),
                       'ambiguous_query_bp': ambiguous, 'repeat_locus_query_bp': repeated,
                       'unsupported_query_bp': length-sum(confirmed.values())-ambiguous,
                       'source_intervals': {rid:union(items) for rid,items in loci.items()},
                       'AMBER_label': label, 'multiple_confirmed_genomes': len(confirmed)>1}
    return result


def construct(fasta_path, paf_path, references, output):
    """Build byte-bound truth and AMBER view without loading any bins or scores."""
    query_lengths = {qid:len(seq) for qid,seq in fasta(fasta_path)}
    blocks, receipt = parse_paf(paf_path, query_lengths, references)
    contigs = reconcile(query_lengths, blocks)
    output = Path(output); output.mkdir(parents=True, exist_ok=False)
    write_json(output/'truth.json', {'reference': binding(fasta_path), 'alignments':receipt,
                'reference_axis':references, 'contigs':contigs,'ordered_contig_ids':list(query_lengths),
                'claim_limit':'all emitted qualifying all-chain alignments; heuristic aligner sensitivity; supplied references only'})
    with (output/'AMBER-truth.tsv').open('x') as out:
        out.write('@Version:0.9.0\n@SampleID:E009\n@@SEQUENCEID\tBINID\t_LENGTH\n')
        for qid,item in contigs.items():
            if item['AMBER_label'] is not None: out.write(f"{qid}\t{item['AMBER_label']}\t{item['length']}\n")
    return contigs


def recovery(contigs, assignments, references, genome_lengths, targets, min_bin=200000, purity=.95):
    """Count conservative whole-reference and assembly-conditional best-bin recovery.

    Includes every bin base in purity and every target genome in recovery; no
    missing/noise/excluded locus is removed from a full-reference denominator.
    This diagnostic is separate from AMBER's restricted contig population.
    """
    if set(assignments) != set(contigs): raise ValueError('Incomplete/extra assignment axis')
    expected_lengths=defaultdict(int)
    for item in references.values():expected_lengths[item['genome']]+=item['length']
    if any(genome not in expected_lengths or genome_lengths.get(genome)!=expected_lengths[genome] for genome in targets):
        raise ValueError('Target denominator differs from the full competitive reference axis')
    bin_bp = defaultdict(int); bin_confirmed = defaultdict(lambda:defaultdict(int))
    bin_loci = defaultdict(lambda:defaultdict(list)); assembly_loci = defaultdict(list)
    for qid,item in contigs.items():
        label = assignments[qid]
        for rid,items in item['source_intervals'].items(): assembly_loci[rid].extend(items)
        if label is None: continue
        bin_bp[label] += item['length']
        for genome,bp in item['confirmed_query_bp'].items(): bin_confirmed[label][genome] += bp
        for rid,items in item['source_intervals'].items(): bin_loci[label][rid].extend(items)
    union_bp = lambda vals:sum(b-a for a,b in union(vals))
    represented = defaultdict(int)
    for rid,items in assembly_loci.items(): represented[references[rid]['genome']] += union_bp(items)
    rows = []
    for genome in sorted(targets):
        length = genome_lengths[genome]
        if length <= 0: raise ValueError('Nonpositive genome denominator')
        candidates = []
        for label,bp in bin_bp.items():
            confirmed_purity = bin_confirmed[label][genome]/bp
            if bp < min_bin or confirmed_purity < purity: continue
            recovered = sum(union_bp(items) for rid,items in bin_loci[label].items() if references[rid]['genome']==genome)
            if recovered > length: raise ValueError('Reference union exceeds source length')
            candidates.append((recovered,label,confirmed_purity))
        best = sorted(candidates,key=lambda x:(-x[0],x[1]))[0] if candidates else (0,None,None)
        rows.append({'genome':genome,'reference_bp':length,'assembly_confirmed_bp':represented[genome],
                     'best_bin':best[1],'confirmed_purity':best[2],'recovered_bp':best[0],
                     'whole_reference_R95':best[0]/length,
                     'assembly_conditional_R95':best[0]/represented[genome] if represented[genome] else 0.0})
    return rows
