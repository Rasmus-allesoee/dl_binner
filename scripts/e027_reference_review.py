#!/usr/bin/env python3
"""Independently admit and diagnose only the completed E027 Oral MetaBAT target.

The surrounding candidate workflow failed. No false whole-workflow admission,
new bins, fit, mapping, native-path rewrite or threshold selection is performed.
Every retained native FASTA is streamed against accepted parent DNA hashes. The
unchanged provided-origin evaluator keeps all 799 full-reference denominators;
known-shared sensitivity and secondary numerical tiers remain separate.
"""
import argparse
from collections import Counter
import csv
import hashlib
import io
import json
from pathlib import Path
import re
import sys
import tarfile

ROOT = Path(__file__).absolute().parents[1]
sys.path.insert(0, str(ROOT/'scripts'))
from e027_inspection import read, require, seal_from_inventory, scoped_admission
from e024_coverage import binding, write


def fasta_stream(stream):
    """Parse regular DNA FASTA from the already checksum-verified tar stream."""
    name = None; chunks = []
    for line in io.TextIOWrapper(stream, encoding='ascii'):
        line = line.strip()
        if not line: continue
        if line.startswith('>'):
            if name is not None: yield name, ''.join(chunks).upper()
            name = line[1:].split()[0]; chunks = []
        else:
            require(name is not None, 'Native FASTA has DNA before an identifier')
            chunks.append(line)
    if name is not None: yield name, ''.join(chunks).upper()


def dna_contract(archive, inventory, data, reference):
    """Match all native bin sequences and complete assignments to the parent axis."""
    import numpy as np
    r = Path(reference)/'work/reference'; manifest = read(r/'export/manifest.json')
    seal = read(r/'done.json'); seal_from_inventory(seal, 'reference', inventory)
    ids = data['ids'].tolist(); index = {q: i for i, q in enumerate(ids)}
    labels = np.full(len(ids), -1, np.int32); seen = set(); bins = Counter(); native_names = {}
    with tarfile.open(archive, 'r:gz') as stream:
        for member in stream:
            match = re.fullmatch(r'work/reference/native/bin\.(\d+)\.fa', member.name)
            if not match: continue
            label = int(match[1])-1; require(label >= 0, 'Invalid native bin index')
            native_names[label] = 'bin_'+str(label+1)
            for q, dna in fasta_stream(stream.extractfile(member)):
                require(q in index and q not in seen, 'Unknown/duplicated native bin DNA')
                i = index[q]
                require(len(dna) == int(data['lengths'][i]) and len(dna) >= 1000 and
                        hashlib.sha256(dna.encode()).hexdigest() == str(data['sequence_sha256'][i]),
                        'Native bin DNA differs from the accepted parent')
                seen.add(q); labels[i] = label; bins[label] += len(dna)
    require(len(native_names) == manifest['bins'] == len(bins) and all(n >= 200000 for n in bins.values()),
            'Native default bin count/size differs')
    statuses = {s: dict(contigs=0, bp=0) for s in ['assigned', 'unassigned', 'excluded']}
    count = 0
    with (r/'export/assignments.tsv').open() as stream:
        rows = csv.DictReader(stream, delimiter='\t')
        require(rows.fieldnames == ['contig_id', 'length', 'bin_id', 'status', 'reason'], 'Reference table schema differs')
        for i, row in enumerate(rows):
            require(i < len(ids) and row['contig_id'] == ids[i] and int(row['length']) == int(data['lengths'][i]),
                    'Reference full ordered DNA axis differs')
            label = int(labels[i]); n = int(data['lengths'][i])
            status = 'assigned' if label >= 0 else 'excluded' if n < 1000 else 'unassigned'
            reason = '' if label >= 0 else 'native_below_small_contig_minimum' if n < 1000 else 'native_not_assigned'
            require(row['bin_id'] == (native_names[label] if label >= 0 else '') and
                    row['status'] == status and row['reason'] == reason, 'Reference status/bin/reason differs')
            statuses[status]['contigs'] += 1; statuses[status]['bp'] += n; count += 1
    require(count == manifest['contigs'] == len(ids) and manifest['bp'] == int(data['lengths'].sum()) and
            statuses == manifest['statuses'] and binding(r/'export/assignments.tsv') == manifest['assignments'],
            'Complete native DNA accounting differs')
    return labels, dict(status='PASS', bins=len(bins), rows=count, bp=int(data['lengths'].sum()),
        statuses=statuses, native_DNA_reverified=True, no_NEW_DNA_or_partition_produced=True,
        length_eligibility='>=2500 bp main; >=1000 bp recruitment; per-row coverage eligibility not invented')


def review(args):
    """Verify independent target scope before opening truth; evaluate frozen rules."""
    import numpy as np
    from threadpoolctl import threadpool_limits
    from dl_binner.multiview.views import load
    from dl_binner.density.bin_quality import summarize
    from e027_reference import validate_means
    from e014_review import oral_labels, oral_population
    from e014_oral_truth import evaluate
    from e023_review import oral_secondary_rows
    threadpool_limits(4)
    out = Path(args.output); out.mkdir(exist_ok=False)
    inv = read(Path(args.verified)/'inventory.json'); archive = read(Path(args.verified)/'archive-verified.json')
    require(binding(Path(args.archive)) == archive['archive'], 'Verified reference archive drifted')
    controls = Path(args.controls)/'evidence'; plan = read(controls/'plan.json')
    global_status = read(args.status); finance = read(args.finance); source = read(args.source)['source']
    data, meta = load(args.features)
    expected = read(ROOT/'experiments/E027-common-information-binner/reuse-lock.json')['files']
    for native, local in [(plan['units']['oral-noGLM']['features'], args.features),
                          (plan['reference']['fasta'], args.fasta),
                          (plan['reference']['matrix'], args.matrix),
                          (plan['reference']['matrix_receipt'], args.matrix_receipt)]:
        require(binding(Path(local)) == expected[native], 'Retained reference input differs: '+native)
    measured = validate_means(args.matrix, args.matrix_receipt, args.fasta)
    require(meta['samples'] == measured['samples'] and len(data['ids']) == measured['rows'] == 1286547
            and meta['fasta_sha256'] == binding(Path(args.fasta))['sha256'], 'Reference data/depth axis differs')
    native = read(Path(args.reference)/'work/reference/native-exit.json'); argv = native['argv']
    require(native['exit_code'] == 0 and argv == [plan['reference']['binary'], '-i', plan['reference']['fasta'],
        '-a', plan['reference']['matrix'], '--cvExt', '-o', plan['work']+'/reference/native/bin',
        '-t', '4', '--seed', '11', '-v'], 'Frozen single native reference command differs')
    assignments, DNA = dna_contract(args.archive, inv, data, args.reference)
    target_proof = dict(status='PASS', target='reference', native_exit=0, all_dependency_seals_checked=True,
        independent_retained_inputs_verified=True, complete_DNA_accounting_verified=True, frozen_rule_verified=True)
    admission = scoped_admission('reference', global_status, finance, archive, source, target_proof)
    write(out/'admission.json', dict(admission, DNA=DNA, measured=measured,
        note='Global input-after target was not run. This independent closed target verifies its own retained input bytes and every emitted DNA record. No candidate grouping/export/audit gate is waived.'))
    # Only now may the independently admitted target open its separately named oracle.
    ids = data['ids'].tolist(); part = dict(ids=ids, assignment=assignments.tolist())
    write(out/'native-assignment-adapter.json', part)
    result = evaluate(args.truth_root, out/'native-assignment-adapter.json', out/'truth')
    lab, quarantine, shared, genomes, truth = oral_labels(args.truth_root, ids, data['lengths'])
    require(len(truth['targets']) == 799 and sum(truth['targets'].values()) == 2083072211 and
            truth['model_input']['sha256'] == meta['fasta_sha256'], 'Frozen Oral full reference denominator differs')
    refs = truth['references']; lengths = Counter()
    for r in refs.values(): lengths[r['genome']] += r['length']
    assignment_map = {q: int(b) if b >= 0 else None for q, b in zip(ids, assignments)}
    secondary = {mode: summarize(oral_secondary_rows(Path(args.truth_root)/'rows.jsonl.gz', refs, masked),
        assignment_map, refs, lengths, truth['targets']) for mode, masked in
        [('provided_origin', False), ('known_shared_sensitivity', True)]}
    marker_clean = set(read(args.marker_clean)['clean'])
    method_data = dict(data, eligible=data['lengths'] >= 1000)
    display = dict(part, neighbors=[[] for _ in ids])
    population = oral_population(display, method_data, lab, quarantine, shared, genomes, truth['targets'], marker_clean)
    population['eligibility_scope'] = 'Native length eligibility; further coverage filters unresolved per row, retained in native log. No learned-neighbor geometry exists for this external tool.'
    strata = Counter()
    for i, n in enumerate(data['lengths']):
        key = ('assigned' if assignments[i] >= 0 else 'excluded' if n < 1000 else 'unassigned')+'|'+('measured_positive' if data['depth_evidence'][i] else 'measured_all_zero')
        strata[key] += int(n)
    for mode, table in secondary.items():
        with (out/('bin-quality-'+mode+'.tsv')).open('x') as stream:
            fields = list(table['bins'][0]) if table['bins'] else ['bin_id']
            writer = csv.DictWriter(stream, fieldnames=fields, delimiter='\t', lineterminator='\n')
            writer.writeheader(); writer.writerows(table['bins'])
    value = dict(status='PASS_INDEPENDENT_REFERENCE_REVIEW', admission=admission, DNA=DNA,
        primary=result, secondary=secondary, population=population, measured_depth_status_bp=dict(strata),
        full_reference_targets=799, full_reference_bp=2083072211,
        global_candidate_comparison_available=False, candidate_failure_not_a_zero_score=True,
        secondary_tiers_not_formal_MIMAG=True, primary_rule_changed=False,
        source_truth='Admitted Oral provided-origin oracle; known-shared masking is not exhaustive unique-source truth')
    write(out/'review.json', value)
    print(json.dumps({mode: row['recovery_summary'] for mode, row in result.items()}), flush=True)
    return value


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    for name in ['archive', 'verified', 'controls', 'reference', 'features', 'fasta', 'matrix',
                 'matrix-receipt', 'status', 'finance', 'source', 'truth-root', 'marker-clean', 'output']:
        p.add_argument('--'+name, type=Path, required=True)
    review(p.parse_args())
