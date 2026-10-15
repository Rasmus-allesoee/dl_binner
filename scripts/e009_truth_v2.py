#!/usr/bin/env python3
"""Fresh E009 truth from retained PAFs and accepted population; never run an aligner.

Validate minimap2 2.30 =XID/nn/NM contracts before filtering. Quarantine ambiguous
alignment spans globally; normalize verified circular aliases before reconciling
all competitors. Keep originals read-only, write a fresh output, and never admit
truth automatically or open bin predictions. Stdlib only; usable on the Mac.
"""
import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import re
import sys
import time
sys.path.insert(0, str(Path(__file__).absolute().parent))
from e009_common import binding, fasta, write_json
from e009_truth import union


def reference_axes(axis, catalog, audit, population, circular_dir):
    """Bind provided files to observed genomes and canonical molecule coordinates.

    Unobserved replicons of observed genomes remain in their full denominators.
    Two zero-origin files remain separate competitive identities. Circular aliases
    need actual DNA, exact catalog hashes and unambiguous forward offsets.
    """
    if not audit['all_origin_source_taxonomy_joins_resolved'] or not audit['sets_equal']:
        raise ValueError('Unresolved origin/source/taxonomy review')
    if audit['multiple_genome_source_records'] or audit['multiple_genome_source_files']:
        raise ValueError('Ambiguous source/genome grouping')
    if set(audit['positive_genomes']) != set(population['genomes']):
        raise ValueError('Population/origin genome axis mismatch')
    sources = {v['name']: v for v in catalog['files']}
    groups = defaultdict(list)
    for rid, item in axis['reference_axis'].items():
        groups[item['genome']].append((rid, item))
    canonical = {}; aliases = {}; genomes = {}; circular = []
    assigned = set()
    for name, records in sorted(groups.items()):
        source = sources[name]
        source_records = {v['replicon_id']: v for v in source['replicons']}
        if {v['original_replicon_id'] for _, v in records} != set(source_records):
            raise ValueError('Selected source does not retain every provided record')
        gids = audit['source_file_to_observed_genomes'].get(name, [])
        if len(gids) > 1: raise ValueError('Multiple genomes in source file')
        gid = gids[0] if gids else 'zero_origin::' + name
        if gid in genomes: raise ValueError('Genome spans multiple source files; needs review')
        if gids:
            assigned.add(gid); p = population['genomes'][gid]; a = audit['positive_genomes'][gid]
            if p['source_files'] != [name] or p['lineage_class'] != a['lineage_class'] or p['HOST'] != a['HOST']:
                raise ValueError('Population grouping/taxonomy/HOST drift')
            if p['positive_read_records'] != a['read_records'] or a['read_records'] <= 0:
                raise ValueError('Positive origin count mismatch')
            metadata = dict(p)
        else:
            metadata = {'source_files': [name], 'lineage_class': 'zero_origin_competitor',
                        'positive_read_records': 0, 'HOST': '', 'primary_candidate': False}
        offsets = {}; canonical_id = None
        if name.endswith('.permuted.fna'):
            path = Path(circular_dir) / name
            if binding(path) != source['file']: raise ValueError('Circular source bytes drift')
            dna = list(fasta(path)); base_id, base = dna[0]; length = len(base)
            if len(dna) != len(records) or {k for k,_ in dna} != set(source_records):
                raise ValueError('Circular source record axis mismatch')
            for ident, seq in dna:
                record = source_records[ident]
                if len(seq) != record['length'] or hashlib.sha256(seq.encode()).hexdigest() != record['DNA_sha256']:
                    raise ValueError('Circular record DNA drift')
                offset = (base + base).find(seq)
                if len(seq) != length or not 0 <= offset < length or (base + base).find(seq, offset+1, 2*length-1) >= 0:
                    raise ValueError('Circular alias is not a unique exact forward rotation')
                offsets[ident] = offset
            canonical_id = next(rid for rid,v in records if v['original_replicon_id'] == base_id)
            circular.append({'file': name, 'genome': gid, 'HOST': metadata['HOST'],
                             'canonical_id': canonical_id, 'length': length, 'offsets': offsets})
        literal = sum(v['length'] for _,v in records)
        for rid, record in records:
            original = source_records[record['original_replicon_id']]
            if original['length'] != record['length']: raise ValueError('Source axis length drift')
            target = canonical_id or rid
            aliases[rid] = dict(record, genome=gid, canonical_id=target,
                                offset=offsets.get(record['original_replicon_id'], 0))
            canonical[target] = {'genome': gid, 'length': record['length'], 'source_file': name,
                                 'original_replicon_id': source_records[record['original_replicon_id']]['replicon_id'] if not canonical_id else base_id}
        length = sum(v['length'] for v in canonical.values() if v['genome'] == gid)
        if gids and (metadata['literal_provided_bp'] != literal or metadata['one_copy_provided_bp'] != length):
            raise ValueError('Reviewed full-reference denominator drift')
        genomes[gid] = dict(metadata, literal_provided_bp=literal, one_copy_provided_bp=length)
    if assigned != set(audit['positive_genomes']): raise ValueError('Positive genome missing from universe')
    absent = sorted(n for n in groups if n not in audit['source_file_to_observed_genomes'])
    if absent != sorted(population['selected_source_files_without_positive_origins']):
        raise ValueError('Zero-origin competitor universe drift')
    return aliases, canonical, genomes, circular


def split_circular(q0, q1, r0, rid, strand, alias):
    """Map one paired CIGAR span to canonical coordinates, splitting circular wraps.

    Reference traversal always ascends. On a reverse query the first reference
    piece consumes the high query coordinates, including across a circular wrap.
    """
    length = alias['length']; span = q1-q0
    if span <= 0 or r0 < 0 or r0+span > length: raise ValueError('Invalid paired CIGAR span')
    start = (r0 + alias['offset']) % length; first = min(span, length-start)
    chunks = [(start, first)]
    if first < span: chunks.append((0, span-first))
    used = 0; result = []
    for left, size in chunks:
        qa, qb = (q0+used, q0+used+size) if strand == '+' else (q1-used-size, q1-used)
        result.append({'q0': qa, 'q1': qb, 'r0': left, 'r1': left+size,
                       'rid': alias['canonical_id'], 'genome': alias['genome'], 'strand': strand})
        used += size
    return result


def paf_row(raw, query_lengths, references):
    """Validate even low-quality rows against native 2.30 accounting, without filtering.

    = can include N:N while mlen excludes it. Therefore equal-mlen must be between
    zero and nn, not necessarily zero. Require typed nn/NM and cg from this writer;
    reject M, clipping, skips, bad endpoints/counts/tags and zero-sized operations.
    """
    fields = raw.rstrip('\n').split('\t')
    if len(fields) < 15: raise ValueError('Malformed PAF row / missing native tags')
    qid, strand, rid = fields[0], fields[4], fields[5]
    qlen, qs, qe, rlen, rs, re_, matches, block, mapq = [int(fields[i]) for i in (1,2,3,6,7,8,9,10,11)]
    if qid not in query_lengths or rid not in references: raise ValueError('Unknown PAF axis')
    if qlen != query_lengths[qid] or rlen != references[rid]['length']: raise ValueError('PAF axis length mismatch')
    if strand not in ('+', '-') or not (0 <= qs < qe <= qlen and 0 <= rs < re_ <= rlen):
        raise ValueError('PAF coordinate/orientation mismatch')
    if not (0 <= matches <= block and block > 0 and 0 <= mapq <= 255): raise ValueError('Invalid PAF counts')
    tags = {}
    for value in fields[12:]:
        parts = value.split(':', 2)
        if len(parts) != 3 or not re.fullmatch(r'[A-Za-z][A-Za-z0-9]', parts[0]) or parts[0] in tags:
            raise ValueError('Invalid/duplicate PAF tag')
        tags[parts[0]] = parts[1:]
    if any(k not in tags or tags[k][0] != typ for k,typ in [('cg','Z'),('nn','i'),('NM','i')]):
        raise ValueError('Missing/wrong native cg/nn/NM tag type')
    cigar = tags['cg'][1]; ops = [(int(n),op) for n,op in re.findall(r'(\d+)([=XID])', cigar)]
    if ''.join(str(n)+op for n,op in ops) != cigar or not ops or any(n <= 0 for n,_ in ops):
        raise ValueError('Unsupported =XID CIGAR')
    counts = Counter()
    for n,op in ops: counts[op] += n
    nn, nm = int(tags['nn'][1]), int(tags['NM'][1]); columns = sum(counts.values())
    eq_ambiguous = counts['=']-matches
    if counts['=']+counts['X']+counts['I'] != qe-qs or counts['=']+counts['X']+counts['D'] != re_-rs:
        raise ValueError('CIGAR/endpoints disagree')
    if columns != block+nn or nn < 0 or not 0 <= eq_ambiguous <= nn or nn-eq_ambiguous > counts['X']+counts['I']+counts['D'] or nm != columns-matches:
        raise ValueError('CIGAR/native ambiguous-base counts disagree')
    return qid, qs, qe, strand, rid, rs, matches, block, nn, ops


def parse_paf(path, query_lengths, references, policy):
    """Validate all chains, retain clean paired blocks and global ambiguous-span vetoes."""
    blocks = defaultdict(list); vetoes = defaultdict(list); counts = Counter()
    with Path(path).open() as stream:
        for i, raw in enumerate(stream, 1):
            try: qid, qs, qe, strand, rid, rs, matches, block, nn, ops = paf_row(raw, query_lengths, references)
            except ValueError as exc: raise ValueError(f'PAF line {i}: {exc}') from exc
            counts['paf_rows'] += 1; counts['nn_positive_rows'] += bool(nn)
            aligned = sum(n for n,op in ops if op in ('=','X'))
            if aligned < policy['aligned_query_bp_min'] or matches/block < policy['identity_min']: continue
            counts['qualifying_rows'] += 1
            if nn:
                vetoes[qid].append([qs,qe]); counts['quarantined_rows'] += 1; continue
            counts['clean_qualifying_rows'] += 1
            q = qs if strand == '+' else qe; r = rs
            for n,op in ops:
                if op in ('=','X'):
                    qa,qb = (q,q+n) if strand == '+' else (q-n,q)
                    blocks[qid].extend(split_circular(qa,qb,r,rid,strand,references[rid]))
                    q += n if strand == '+' else -n; r += n
                elif op == 'I': q += n if strand == '+' else -n
                else: r += n
            if i % 25000 == 0: print(f'TRUTH_PAF_ROWS {i}', flush=True)
    return blocks, vetoes, dict(counts)


def reconcile_one(length, values, vetoes, attributable=.95):
    """Sweep all clean competitors and vetoes before granting any genome/locus support."""
    events = defaultdict(list)
    for i,v in enumerate(values):
        events[v['q0']].append((1,i)); events[v['q1']].append((-1,i))
    for i,(a,b) in enumerate(union(vetoes)):
        events[a].append((1,-i-1)); events[b].append((-1,-i-1))
    positions = sorted(events); active = set(); confirmed = Counter(); loci = defaultdict(list)
    ambiguous = repeated = quarantined = 0
    for a,b in zip(positions, positions[1:]):
        for mode,i in events[a]:
            if mode == 1: active.add(i)
            else: active.remove(i)
        if any(i < 0 for i in active): quarantined += b-a; continue
        current = [values[i] for i in active]; genomes = {v['genome'] for v in current}
        if not genomes: continue
        if len(genomes) > 1: ambiguous += b-a; continue
        genome = next(iter(genomes)); confirmed[genome] += b-a; locations = set()
        for v in current:
            left,right = ((v['r0']+a-v['q0'],v['r0']+b-v['q0']) if v['strand'] == '+' else
                          (v['r0']+v['q1']-b,v['r0']+v['q1']-a))
            locations.add((v['rid'],left,right,v['strand']))
        if len(locations) == 1:
            rid,left,right,_ = next(iter(locations)); loci[rid].append([left,right])
        else: repeated += b-a
    best = sorted(confirmed, key=lambda g:(-confirmed[g],g))
    label = best[0] if best and confirmed[best[0]]/length >= attributable else None
    return {'length': length, 'confirmed_query_bp': dict(confirmed), 'ambiguous_query_bp': ambiguous,
            'nn_quarantined_query_bp': quarantined, 'repeat_locus_query_bp': repeated,
            'unsupported_query_bp': length-sum(confirmed.values())-ambiguous-quarantined,
            'source_intervals': {rid: union(items) for rid,items in loci.items()},
            'AMBER_label': label, 'multiple_confirmed_genomes': len(confirmed)>1}


def derive(root, audit_path, population_path, policy_path, output, expected_inputs):
    """Derive one fresh byte-bound artifact; verification/serialization are part of its clock.

    Expected input paths are relative to retained root, or explicit reviewed
    records under the named $audit/$population/$policy keys. Never discover bulk
    paths from old absolute receipt locators. A failed output is never resumed.
    """
    started = time.monotonic(); root, output = Path(root), Path(output)
    if output.exists(): raise ValueError('Fresh truth directory required')
    paths = {k: root/k for k in expected_inputs if not k.startswith('$')}
    paths.update({'$audit': Path(audit_path), '$population': Path(population_path), '$policy': Path(policy_path)})
    checked = {}
    for name,path in paths.items():
        actual = binding(path)
        if actual != expected_inputs[name]: raise ValueError('Truth input bytes drift: '+name)
        checked[name] = actual
    load = lambda name: json.loads(paths[name].read_text())
    source = 'data-stage-v1/parts/sources/'
    aliases, references, genomes, circular = reference_axes(load(source+'reference.fna.axis.json'),
        load(source+'catalog.json'), load('$audit'), load('$population'), root/source/'unpacked/source_genomes')
    policy = load('$policy')
    query_path = paths['data-stage-v1/parts/assembly/megahit/final.contigs.fa']
    queries = {qid: len(seq) for qid,seq in fasta(query_path)}
    blocks,vetoes,counts = parse_paf(paths['data-stage-v1/parts/final/all_competing_chains.paf'], queries, aliases, policy)
    contigs = {}
    for i,(qid,length) in enumerate(queries.items(),1):
        contigs[qid] = reconcile_one(length, blocks.pop(qid,[]), vetoes.pop(qid,[]), policy['contig_attribution_min'])
        if i % 25000 == 0: print(f'TRUTH_CONTIGS {i}', flush=True)
    lengths = {g: v['one_copy_provided_bp'] for g,v in genomes.items()}
    targets = sorted(g for g,v in genomes.items() if v['positive_read_records'] > 0 and
                     v['lineage_class'] in ('bacterial','archaeal') and lengths[g] >= policy['primary_reference_bp_min'])
    if any(genomes[g].get('primary_candidate',False) != (g in targets) for g in genomes):
        raise ValueError('Target population differs from reviewed candidates')
    output.mkdir(parents=True)
    write_json(output/'reference-map.json', {'aliases': aliases, 'canonical_references': references,
                                           'genomes': genomes, 'circular': circular})
    write_json(output/'targets.json', {'targets': targets, 'genome_lengths': lengths,
                                      'non_targets': sorted(set(genomes)-set(targets))})
    write_json(output/'truth.json', {'version': policy['version'], 'reference': binding(query_path),
        'policy': policy, 'inputs': checked, 'alignments': counts, 'reference_axis': references,
        'ordered_contig_ids': list(queries), 'contigs': contigs, 'scientific_truth_admitted': False})
    with (output/'AMBER-truth.tsv').open('x') as f:
        f.write('@Version:0.9.0\n@SampleID:E009\n@@SEQUENCEID\tBINID\t_LENGTH\n')
        for qid,item in contigs.items():
            if item['AMBER_label'] is not None: f.write(f"{qid}\t{item['AMBER_label']}\t{item['length']}\n")
    summary = {'contigs': len(queries), 'assembly_bp': sum(queries.values()), 'alignment_rows': counts,
               'positive_genomes': sum(v['positive_read_records']>0 for v in genomes.values()),
               'primary_targets': len(targets), 'alias_records': len(aliases), 'canonical_references': len(references),
               'full_provided_primary_bp': sum(lengths[g] for g in targets),
               'AMBER_labelled_contigs': sum(v['AMBER_label'] is not None for v in contigs.values()),
               'AMBER_labelled_bp': sum(v['length'] for v in contigs.values() if v['AMBER_label'] is not None),
               'query_bp': {k: sum(v[k] for v in contigs.values()) for k in
                 ['ambiguous_query_bp','nn_quarantined_query_bp','repeat_locus_query_bp','unsupported_query_bp']},
               'confirmed_query_bp': sum(sum(v['confirmed_query_bp'].values()) for v in contigs.values()),
               'wall_seconds': time.monotonic()-started, 'no_fits_or_scores': True, 'scientific_truth_admitted': False}
    write_json(output/'derivation.json', summary)
    write_json(output/'manifest.json', {'files': {p.name: binding(p) for p in sorted(output.iterdir())},
        'inputs': checked, 'policy': binding(policy_path), 'code': binding(__file__), 'independent_review_required': True})
    return summary


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    for name in ['root','audit','population','policy','output','input_manifest']: p.add_argument('--'+name.replace('_','-'), required=True, type=Path)
    args = p.parse_args()
    print(json.dumps(derive(args.root,args.audit,args.population,args.policy,args.output,
                            json.loads(args.input_manifest.read_text())['files']), sort_keys=True))
