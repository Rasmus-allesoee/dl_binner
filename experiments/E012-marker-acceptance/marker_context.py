#!/usr/bin/env python3
"""Extend the diagnostic audit to every conflict family in four E011 loss cases.

Cases were identified in accepted E011, before E012 selection. Reuse E012's
already projected seed calls and project only missing cached calls through
existing competing PAFs. No selection, thresholds, fits or aligners change.
Also compare retained source-record hashes; a FASTA record is not automatically
a biological replicon, and different hashes cannot exclude partial redundancy.
"""
from collections import Counter
import hashlib
from itertools import combinations
import json
from pathlib import Path
import sys
import time

ROOT = Path(__file__).absolute().parents[2]
sys.path.insert(0, str(ROOT/'scripts'))
from e009_common import binding, write_json
from e009_truth_v2 import parse_paf
from e010_review import require
from e012_marker_audit import clip_span, classify_pair, profile_headers, verify_truth


def run(primary, output):
    """Retain the full repeated-family call context and explicit unresolved biology."""
    started = time.monotonic(); primary, output = Path(primary), Path(output)
    output.mkdir(parents=True, exist_ok=False)
    exp = ROOT/'experiments/E012-marker-acceptance'
    inputs = json.loads((exp/'input-lock.json').read_text()); lock = json.loads((exp/'review-lock.json').read_text())
    truth_root = verify_truth(lock, ROOT)
    manifest = json.loads((truth_root/'manifest.json').read_text())
    catalog_path = ROOT/'artifacts/e009-gcp-review/20261015/returned/data-stage-v1/parts/sources/catalog.json'
    require(binding(catalog_path) == manifest['inputs']['data-stage-v1/parts/sources/catalog.json'], 'Retained source catalog differs')
    require(binding(ROOT/lock['paf_path']) == lock['paf'], 'Retained PAF differs')
    cache = ROOT/inputs['cache']/'candidate/markers'
    restored = json.loads((ROOT/inputs['cache']/'restore.json').read_text())
    require(binding(ROOT/inputs['cache']/'restore.json') == inputs['restore_manifest'], 'Restore receipt differs')
    consumed = ['evidence.json', 'genes.jsonl', 'domains.json', 'proteins.faa', 'asset.json']
    for name in consumed:
        require(binding(cache/name) == restored['restored_files']['candidate/markers/'+name], 'Cached call bytes differ')
    prior = json.loads(primary.read_text())
    require(prior['input_lock'] == binding(exp/'input-lock.json') and prior['status'] == 'SUCCESS', 'Primary audit contract differs')
    old_path = ROOT/lock['baseline_root']/'grouping-diagnostics-v2.json'
    require(binding(old_path) == lock['baseline_files']['grouping-diagnostics-v2.json'], 'E011 cases differ')
    old = json.loads(old_path.read_text()); cases = old['marker_seed_audit']['lost_passing_bins']
    require(len(cases) == 4, 'Expected four previously recorded loss cases')
    pre, post = [json.loads((ROOT/p).read_text()) for p in inputs['contexts']['CPM']]
    evidence = json.loads((cache/'evidence.json').read_text()); wanted_calls = []
    attempts = {a['pre_bin']: a for a in post['attempts']}
    for case in cases:
        # E011 records the parent through its retained paired target proposal.
        parent = case['pre_bin']; attempt = attempts[parent]
        members = {q for q, b in zip(pre['ids'], pre['assignment']) if b == parent}
        calls = [c for c in evidence['calls'] if c['contig'] in members and c['family'] in attempt['before']]
        wanted_calls.extend(calls)
        case.update(parent=parent, before=attempt['before'], all_conflict_calls=calls)
    key = lambda c: (c['gene'], c['family'], c['start'], c['end'])
    existing = {key(c['call']): c for p in prior['proposals'] for c in p['calls']}
    missing = {key(c): c for c in wanted_calls if key(c) not in existing}
    genes = {}; wanted_genes = {c['gene'] for c in missing.values()}
    with (cache/'genes.jsonl').open() as stream:
        for raw in stream:
            g = json.loads(raw)
            if g['gene'] in wanted_genes:
                genes[g['gene']] = g
    require(set(genes) == wanted_genes, 'Missing additional gene metadata')
    truth = json.loads((truth_root/'truth.json').read_text())
    refs = json.loads((truth_root/'reference-map.json').read_text())
    qids = {g['contig'] for g in genes.values()}; subset = output/'additional-competitors.paf'
    with (ROOT/lock['paf_path']).open() as src, subset.open('x') as dst:
        for raw in src:
            if raw.split('\t', 1)[0] in qids:
                dst.write(raw)
    policy = json.loads((ROOT/lock['policy_path']).read_text())
    blocks, vetoes, counts = parse_paf(subset, {q: truth['contigs'][q]['length'] for q in qids}, refs['aliases'], policy)
    for k, call in missing.items():
        g = genes[call['gene']]; q = g['contig']
        existing[k] = dict(call=call, gene=g,
            gene_projection=clip_span(g['start'], g['end'], blocks[q], vetoes[q]),
            domain_projection=clip_span(call['start'], call['end'], blocks[q], vetoes[q]))
    catalog = json.loads(catalog_path.read_text())
    source_records = {(f['name'], r['replicon_id']): r for f in catalog['files'] for r in f['replicons']}
    asset = json.loads((cache/'asset.json').read_text()); hmm = ROOT/lock['hmm_path']
    require(binding(hmm) == asset['hmm'], 'Pinned profile differs')
    headers = profile_headers(hmm); domains = json.loads((cache/'domains.json').read_text())
    summaries = Counter(); results = []
    for case in cases:
        families = []
        for family in sorted(case['before']):
            calls = [existing[key(c)] for c in case['all_conflict_calls'] if c['family'] == family]
            pairs = []
            for left, right in combinations(calls, 2):
                if left['gene']['contig'] == right['gene']['contig']:
                    continue
                result = classify_pair(left['gene_projection'], right['gene_projection'])
                domain = classify_pair(left['domain_projection'], right['domain_projection'])
                records = []
                for call in [left, right]:
                    values = []
                    for rid, spans in call['gene_projection']['source_intervals'].items():
                        meta = refs['canonical_references'][rid]
                        raw = source_records[meta['source_file'], meta['original_replicon_id']]
                        values.append(dict(reference_id=rid, spans=spans, **meta,
                            DNA_sha256=raw['DNA_sha256'], canonical_sha256=raw['canonical_sha256']))
                    records.append(values)
                canonical_sets = [{r['canonical_sha256'] for r in items} for items in records]
                result.update(domain=domain, genes=[left['gene'], right['gene']], source_records=records,
                              exact_whole_source_record_hash_overlap=bool(canonical_sets[0]&canonical_sets[1]))
                pairs.append(result); summaries[result['classification']] += 1
            families.append(dict(family=family, profiles=[headers[m] for m, f in asset['families'].items() if f == family],
                calls=[dict(call=c['call'], gene=c['gene'], gene_projection=c['gene_projection'], domain_projection=c['domain_projection'],
                            native_domains=[d for d in domains if d['gene'] == c['call']['gene'] and asset['families'][d['marker']] == family]) for c in calls], pairs=pairs))
        results.append(dict(genome=case['genome'], parent=case['parent'], seed_family=case['seed_family'], families=families))
    for name in consumed:
        require(binding(cache/name) == restored['restored_files']['candidate/markers/'+name], 'Cache changed during context audit')
    write_json(output/'context.json', dict(status='SUCCESS', primary_audit=binding(primary), source=binding(__file__),
        catalog=binding(catalog_path), old_cases=binding(old_path), projections_reused=len({key(c) for c in wanted_calls if key(c) not in missing}),
        new_projections=len(missing), additional_PAF_rows=counts, cases=results, pair_classifications=dict(summaries),
        semantics='provided_replicon means a supplied FASTA sequence record; WGS records need not be separate biological replicons',
        limitations=['No functional reannotation or proof of biological paralogy; HMM specificity and source-assembly redundancy remain uncertain.',
                     'No shared provided locus/whole-record hash rules out those simple duplication explanations only; partial/ancient source redundancy is not excluded.',
                     'This is the diagnostic expansion of four E011-preidentified cases, after E012 scores; it does not select thresholds/bins or alter the rule.'],
        wall_seconds=time.monotonic()-started))


if __name__ == '__main__':
    import argparse
    p = argparse.ArgumentParser(description=__doc__); p.add_argument('--primary', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True); a = p.parse_args(); run(a.primary, a.output)
