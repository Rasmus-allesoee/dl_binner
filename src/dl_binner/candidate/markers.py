"""Native, checksum-bound SCG evidence without an external binner or taxonomy.

Call genes on complete DNA with Pyrodigal; search a supplied pinned profile with
PyHMMER's per-model trusted cutoffs. Retain all genes/domains and explicitly mark
ambiguous or multicopy evidence. This cache does not estimate genome quality.
"""
from collections import Counter, defaultdict
import importlib.metadata
import json
from pathlib import Path

from ..contracts import check_files, digest, file_record, write_json
from ..io import read_fasta, emit, id_digest

POLICY = dict(version=1, gene_mode='pyrodigal-meta', min_gene_contig_bp=90,
    bit_cutoffs='trusted', min_hmm_coverage=0.5,
    ambiguity='any multi-family protein loses constraint support; overlapping same-family domains deduplicated; distinct same-contig copies unreliable',
    coordinates='zero-based half-open genomic; one-based inclusive native protein/HMM columns retained')


def runtime():
    """Bind executable library versions and this evidence-reduction implementation."""
    return dict(versions={k: importlib.metadata.version(k) for k in ('pyrodigal', 'pyhmmer', 'archspec')},
                implementation=file_record(__file__))


def read_asset(hmm, manifest):
    """Require explicit profile bytes, unique canonical families, provenance/license."""
    asset = json.loads(Path(manifest).read_text())
    if (asset.get('version') != 1 or asset.get('kind') != 'scg_profile_asset'
            or asset.get('hmm') != file_record(hmm) or not asset.get('source')
            or not asset.get('license') or not isinstance(asset.get('families'), dict)
            or not asset['families'] or any(not k or not isinstance(v, str) or not v
                for k, v in asset['families'].items())):
        raise ValueError('Invalid/missing marker asset bytes, families, license or provenance')
    return asset


def reduce_hits(genes, domains, families):
    """Deduplicate same-gene/overlapping hits and quarantine ambiguous/multicopy calls.

    Different HMM bit scores are not comparable probabilities: any credible
    multi-family protein is ambiguous. A contig with distinct copies of one
    canonical SCG supplies no constraint for that family. All raw rows survive.
    """
    by_gene = defaultdict(list)
    for d in domains:
        if (d['gene'] not in genes or d['marker'] not in families or
                not 1 <= d['hmm_from'] <= d['hmm_to'] <= d['hmm_length'] or
                not 1 <= d['protein_from'] <= d['protein_to'] <= genes[d['gene']]['protein_length']):
            raise ValueError('Malformed marker gene/domain coordinates')
        d = dict(d, family=families[d['marker']])
        by_gene[d['gene']].append(d)
    calls, ambiguous = [], []
    for gene, items in sorted(by_gene.items()):
        if len({d['family'] for d in items}) != 1:
            ambiguous.append(dict(gene=gene, reason='multi_family_protein', families=sorted({d['family'] for d in items})))
            continue
        accepted = []
        for d in sorted(items, key=lambda x: (-x['score'], x['protein_from'], x['marker'])):
            start, end = d['protein_from']-1, d['protein_to']
            if any(max(0, min(end, b)-max(start, a)) >= .5*min(end-start, b-a) for a, b in accepted):
                continue
            accepted.append((start, end))
        for start, end in accepted:
            g = genes[gene]
            left, right = ((g['start']+3*start, g['start']+3*end) if g['strand'] == 1
                           else (g['end']-3*end, g['end']-3*start))
            if not g['start'] <= left < right <= g['end']:
                raise ValueError('Marker genomic normalization escaped gene')
            calls.append(dict(contig=g['contig'], gene=gene, family=items[0]['family'], start=left, end=right))
    grouped = defaultdict(list)
    for d in calls:
        grouped[d['contig'], d['family']].append(d)
    clean, multicopy = defaultdict(list), []
    for (contig, family), values in sorted(grouped.items()):
        # Predictions overlapping on opposite strands can be the same physical
        # locus. Deduplicate by genomic overlap before counting distinct copies.
        loci = []
        for d in sorted(values, key=lambda x: (x['start'], x['end'], x['gene'])):
            if not any(max(0, min(d['end'], b)-max(d['start'], a)) >=
                       .5*min(d['end']-d['start'], b-a) for a, b in loci):
                loci.append((d['start'], d['end']))
        if len(loci) == 1:
            clean[contig].append(family)
        else:
            multicopy.append(dict(contig=contig, family=family, loci=[list(v) for v in loci],
                                  reason='distinct_same_contig_copies_unreliable'))
    return dict(clean={k: sorted(v) for k, v in clean.items()}, calls=calls,
                ambiguous=ambiguous, multicopy=multicopy)


def cache(fasta, hmm, asset_manifest, output, threads):
    """Create fresh native gene/HMM evidence and hash every retained cache member."""
    import pyrodigal
    import pyhmmer
    out = Path(output)
    asset = read_asset(hmm, asset_manifest)
    rows = read_fasta(fasta)
    with pyhmmer.plan7.HMMFile(hmm) as stream:
        models = list(stream)
    if ({m.name.decode() for m in models} != set(asset['families']) or len(models) != len(asset['families'])
            or any(not m.cutoffs.trusted_available() for m in models)):
        raise ValueError('Profile family inventory/trusted cutoffs mismatch')
    caller = pyrodigal.GeneFinder(meta=True)
    genes, skipped = {}, []
    with (out/'proteins.faa').open('x') as proteins, (out/'genes.jsonl').open('x') as records:
        for i, (ident, dna) in enumerate(rows):
            if len(dna) < POLICY['min_gene_contig_bp']:
                skipped.append(dict(contig=ident, reason='below_gene_call_length'))
                continue
            for gene in caller.find_genes(dna.encode()):
                sequence = gene.translate().rstrip('*')
                key = 'g'+str(len(genes)).zfill(9)
                record = dict(contig=ident, start=gene.begin-1, end=gene.end, strand=gene.strand,
                              protein_length=len(sequence), partial_begin=gene.partial_begin,
                              partial_end=gene.partial_end)
                if not 0 <= record['start'] < record['end'] <= len(dna):
                    raise ValueError('Native gene coordinates outside parent')
                genes[key] = record
                proteins.write('>'+key+'\n'+sequence+'\n')
                records.write(json.dumps(dict(gene=key, **record), sort_keys=True)+'\n')
            if i % 2000 == 0:
                emit('candidate_gene_calls', completed_contigs=i, genes=len(genes), total_contigs=len(rows))
    domains = []
    if genes:
        with pyhmmer.easel.SequenceFile(out/'proteins.faa', digital=True, alphabet=pyhmmer.easel.Alphabet.amino()) as stream:
            proteins = stream.read_block()
        for i, hits in enumerate(pyhmmer.hmmsearch(models, proteins, cpus=threads, bit_cutoffs='trusted')):
            marker = hits.query.name.decode()
            for hit in hits:
                if not hit.included:
                    continue
                for domain in hit.domains:
                    a = domain.alignment
                    coverage = (a.hmm_to-a.hmm_from+1)/hits.query.M
                    if domain.included and coverage >= POLICY['min_hmm_coverage']:
                        domains.append(dict(gene=hit.name.decode(), marker=marker, score=float(domain.score),
                            hmm_from=a.hmm_from, hmm_to=a.hmm_to, hmm_length=hits.query.M,
                            protein_from=a.target_from, protein_to=a.target_to, hmm_coverage=coverage))
            emit('candidate_marker_search', profiles_complete=i+1, profiles=len(models), retained_domains=len(domains))
    reduced = reduce_hits(genes, domains, asset['families'])
    write_json(out/'domains.json', domains)
    write_json(out/'evidence.json', dict(version=1, ids=[i for i, _ in rows],
        ids_sha256=id_digest(i for i, _ in rows), skipped=skipped, gene_count=len(genes),
        profile_count=len(models), canonical_families=len(set(asset['families'].values())), **reduced))
    write_json(out/'asset.json', asset)
    write_json(out/'cache.json', dict(version=1, kind='candidate_marker_cache',
        fasta=file_record(fasta), hmm=file_record(hmm), asset_manifest=file_record(asset_manifest),
        policy=POLICY, runtime=runtime(), genes=len(genes), domains=len(domains),
        files={p.name: file_record(p) for p in sorted(out.iterdir()) if p.is_file()}))
    emit('candidate_marker_cache_complete', genes=len(genes), domains=len(domains),
         clean_contigs=len(reduced['clean']), ambiguous=len(reduced['ambiguous']), multicopy=len(reduced['multicopy']))


def load_cache(path, fasta, ids=None):
    """Restore-only consumer: verify retained bytes/policy/runtime; never rescan DNA."""
    path = Path(path)
    receipt = json.loads((path/'cache.json').read_text())
    if (receipt.get('kind') != 'candidate_marker_cache' or receipt.get('version') != 1
            or receipt['fasta'] != file_record(fasta) or receipt['policy'] != POLICY
            or receipt['runtime'] != runtime()):
        raise ValueError('Marker cache input/policy/runtime mismatch; no automatic fresh scan')
    check_files(path, receipt['files'])
    if {p.name for p in path.iterdir()} != set(receipt['files']) | {'cache.json'}:
        raise ValueError('Unexpected marker cache files')
    evidence = json.loads((path/'evidence.json').read_text())
    asset = json.loads((path/'asset.json').read_text())
    axis = evidence['ids']
    axis_set = set(axis)
    if (len(set(axis)) != len(axis) or id_digest(axis) != evidence['ids_sha256']
            or (ids is not None and axis != list(ids)) or not set(evidence['clean']) <= set(axis)
            or any(len(v) != len(set(v)) for v in evidence['clean'].values())):
        raise ValueError('Marker cache complete ID/family axis mismatch')
    canonical = set(asset['families'].values())
    if asset['hmm'] != receipt['hmm'] or any(not set(v) <= canonical for v in evidence['clean'].values()):
        raise ValueError('Unknown canonical marker family/asset in cache')
    genes = {}
    with (path/'genes.jsonl').open() as stream:
        for line in stream:
            gene = json.loads(line)
            key = gene.pop('gene')
            if (key in genes or gene['contig'] not in axis_set or gene['strand'] not in (-1, 1)
                    or not 0 <= gene['start'] < gene['end'] or gene['protein_length'] < 1
                    or 3*gene['protein_length'] > gene['end']-gene['start']):
                raise ValueError('Malformed cached gene metadata')
            genes[key] = gene
    domains = json.loads((path/'domains.json').read_text())
    if len(genes) != receipt['genes'] or len(domains) != receipt['domains']:
        raise ValueError('Cached gene/domain count mismatch')
    reduced = reduce_hits(genes, domains, asset['families'])
    if any(evidence[k] != value for k, value in reduced.items()):
        raise ValueError('Retained marker evidence reduction differs; no fresh scan permitted')
    return evidence
