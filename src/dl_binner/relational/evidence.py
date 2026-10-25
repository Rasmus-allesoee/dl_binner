"""Restore reliable marker loci from byte-bound cached genes/domains/proteins.

No gene caller, HMM search, reference taxonomy or original DNA read is reachable.
Retained detection/runtime receipts describe the original detector, not this
reader's platform. Stricter training eligibility never rewrites that evidence.
"""
from collections import defaultdict
import hashlib
import json
import math
from pathlib import Path

from ..candidate.markers import reduce_hits, POLICY
from ..context.tokens import binding
from ..io import id_digest


def require(condition, message):
    """Refuse a violated artifact contract without assertion-dependent behavior."""
    if not condition:
        raise ValueError(message)


def proteins(path):
    """Read complete cached proteins with duplicate, alphabet and empty refusal."""
    result = {}; key = None; chunks = []
    def finish():
        if key is not None:
            value = ''.join(chunks)
            require(value and not set(value)-set('ACDEFGHIKLMNPQRSTVWYBXZJUO'),
                    'Malformed cached protein sequence')
            result[key] = value
    with Path(path).open() as stream:
        for line in stream:
            line = line.strip()
            if not line:
                continue
            if line.startswith('>'):
                finish(); fields = line[1:].split()
                require(len(fields) == 1 and fields[0] not in result,
                        'Missing/duplicate cached protein ID')
                key = fields[0]; chunks = []
            else:
                require(key is not None, 'Protein sequence before header')
                chunks.append(line)
        finish()
    return result


def restore(cache, hmm, data, metadata, policy):
    """Verify cached inventory/axes and retain full single-locus training support.

    Returns JSON-ready quality/abstention evidence and the original protein
    strings for conservative pair vetoes. This is not a calibrated SCG test.
    """
    import pyhmmer
    cache = Path(cache); receipt = json.loads((cache/'cache.json').read_text())
    require(receipt.get('kind') == 'candidate_marker_cache' and receipt.get('version') == 1
            and receipt['policy'] == POLICY, 'Unsupported retained marker cache policy')
    required = {'asset.json', 'proteins.faa', 'genes.jsonl', 'domains.json', 'evidence.json'}
    require(set(receipt['files']) == required and
            {p.name for p in cache.iterdir()} == required | {'cache.json'},
            'Missing/unexpected retained marker members; no scan fallback')
    for name, wanted in receipt['files'].items():
        require(binding(cache/name) == wanted, 'Corrupt retained marker member: '+name)
    asset = json.loads((cache/'asset.json').read_text())
    require(binding(hmm) == asset['hmm'] == receipt['hmm'], 'Pinned marker HMM differs')
    require(receipt['fasta']['sha256'] == metadata['fasta_sha256'],
            'Marker/feature assembly identity differs')
    ids = data['ids'].tolist(); axis = dict(zip(ids, map(int, data['lengths'])))
    old = json.loads((cache/'evidence.json').read_text())
    require(old['ids'] == ids and old['ids_sha256'] == id_digest(ids),
            'Full marker/feature opaque-ID axis differs')
    genes = {}
    with (cache/'genes.jsonl').open() as stream:
        for line in stream:
            g = json.loads(line); name = g.pop('gene')
            require(name not in genes and g['contig'] in axis and g['strand'] in (-1, 1)
                    and type(g['partial_begin']) is bool and type(g['partial_end']) is bool
                    and 0 <= g['start'] < g['end'] <= axis[g['contig']]
                    and type(g['protein_length']) is int and g['protein_length'] > 0
                    and 3*g['protein_length'] <= g['end']-g['start'],
                    'Malformed cached gene coordinates/partial flags')
            genes[name] = g
    sequences = proteins(cache/'proteins.faa')
    require(sequences.keys() == genes.keys() and
            all(len(sequences[k]) == g['protein_length'] for k, g in genes.items()),
            'Cached protein/gene inventory or lengths differ')
    domains = json.loads((cache/'domains.json').read_text())
    require(len(genes) == receipt['genes'] and len(domains) == receipt['domains'],
            'Retained marker gene/domain count differs')
    reduced = reduce_hits(genes, domains, asset['families'])
    require(all(old[k] == v for k, v in reduced.items()),
            'Retained marker reduction differs; do not silently repair evidence')
    profiles = {}
    with pyhmmer.plan7.HMMFile(hmm) as stream:
        for model in stream:
            name = model.name.decode()
            require(name not in profiles and model.cutoffs.trusted_available(),
                    'Duplicate profile/missing trusted cutoff')
            profiles[name] = (model.M, float(model.cutoffs.trusted[1]))
    require(profiles.keys() == asset['families'].keys(), 'Native HMM/asset family axis differs')
    grouped = defaultdict(list); credible = defaultdict(set)
    ambiguous = {g['gene'] for g in reduced['ambiguous']}
    for d in domains:
        g = genes[d['gene']]; family = asset['families'][d['marker']]
        credible[g['contig']].add(family)
        length, cutoff = profiles[d['marker']]
        require(d['hmm_length'] == length and math.isfinite(d['score']),
                'Malformed cached HMM length/score')
        coverage = (d['hmm_to']-d['hmm_from']+1)/length
        require(math.isfinite(d['hmm_coverage']) and abs(coverage-d['hmm_coverage']) < 1e-12,
                'Cached HMM coverage counter differs')
        margin = d['score']-cutoff
        partial = g['partial_begin'] or g['partial_end']
        start, end = ((g['start']+3*(d['protein_from']-1), g['start']+3*d['protein_to'])
                      if g['strand'] == 1 else
                      (g['end']-3*d['protein_to'], g['end']-3*(d['protein_from']-1)))
        require(g['start'] <= start < end <= g['end'], 'Cached domain escaped gene')
        reasons = []
        if d['gene'] in ambiguous: reasons.append('multi_family_protein')
        if partial: reasons.append('partial_gene')
        if coverage < policy['hmm_coverage']: reasons.append('insufficient_HMM_coverage')
        if margin < policy['margin_bits']: reasons.append('near_trusted_cutoff')
        if set(sequences[d['gene']])-set('ACDEFGHIKLMNPQRSTVWY'): reasons.append('uncertain_protein_residues')
        reliability = coverage*(-math.expm1(-math.log(2)*max(0., margin)))
        grouped[g['contig'], family].append(dict(gene=d['gene'], contig=g['contig'],
            family=family, start=start, end=end, coverage=coverage, margin_bits=margin,
            reliability=reliability, reasons=reasons,
            protein_sha256=hashlib.sha256(sequences[d['gene']].encode()).hexdigest()))
    calls = defaultdict(dict); retained = []; consolidated = []; withheld = []
    for (contig, family), values in sorted(grouped.items()):
        loci = []
        for value in sorted(values, key=lambda x: (-x['reliability'], x['start'], x['gene'])):
            if any(max(0, min(value['end'], x['end'])-max(value['start'], x['start'])) >=
                   policy['physical_overlap_fraction']*min(value['end']-value['start'], x['end']-x['start']) for x in loci):
                consolidated.append(value)
            else:
                loci.append(value)
        for value in loci:
            if len(loci) > 1:
                value['reasons'] = value['reasons']+['distinct_same_contig_loci']
            if value['reasons']:
                withheld.append(value)
            else:
                calls[contig][family] = value; retained.append(value)
    return dict(calls=dict(calls), credible={k: sorted(v) for k, v in credible.items()},
                retained=retained, withheld=withheld, consolidated=consolidated,
                detection_runtime=receipt['runtime'], cache=binding(cache/'cache.json'),
                hmm=binding(hmm), original_counts=dict(genes=len(genes), domains=len(domains)),
                semantics='Training-quality proxy; partial/multicopy/near-cutoff withheld; no lineage calibration'), sequences
