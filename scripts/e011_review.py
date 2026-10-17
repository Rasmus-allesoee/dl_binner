#!/usr/bin/env python3
"""Verify sealed E011 returns and diagnose frozen partitions locally, without fits.

Archive/member verification precedes scientific reading. The caller independently
verifies provider shutdown and export cost. No cloud API, training, marker search,
neighbor index, partition optimization or inference is reachable from this module.
"""
import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path, PurePosixPath
import resource
import signal
import sys
import tarfile
import time
sys.path.insert(0, str(Path(__file__).absolute().parent))
from e009_common import binding, write_json
from e009_evaluate import read_partition
from e009_truth import recovery
from e009_controls_review import diagnostics, BOUNDS
from e010_review import require, refinement_membership

REPO = Path(__file__).absolute().parents[1]
EXP = REPO/'experiments/E011-cached-grouping-reference'


def verify_return(archive, checksum, completion, output):
    """Verify the archive and every regular member before exposing a fresh return."""
    archive, checksum, output = map(Path, [archive, checksum, output])
    record = completion['control_archive']; collection = record['collection']
    expected = {k: record[k] for k in ['bytes', 'sha256']}
    require(binding(archive) == expected == collection['archive'], 'Return archive differs')
    require(checksum.read_text().split() == [expected['sha256'], archive.name], 'Checksum sidecar differs')
    require(not output.exists(), 'Fresh verified return directory required')
    with tarfile.open(archive) as tar:
        raw = tar.extractfile('collection-inventory.json').read()
    inventory_binding = dict(bytes=len(raw), sha256=hashlib.sha256(raw).hexdigest())
    require(inventory_binding == collection['inventory'], 'Sealed inventory differs')
    inventory = json.loads(raw)['files']; seen = set(); logical = 0; output.mkdir(parents=True)
    with tarfile.open(archive, 'r|gz') as tar:
        for member in tar:
            pure = PurePosixPath(member.name)
            require(member.isfile() and not pure.is_absolute() and '..' not in pure.parts
                    and member.name not in seen, 'Unsafe or duplicate return member')
            seen.add(member.name); digest = hashlib.sha256(); count = 0
            target = output.joinpath(*pure.parts); target.parent.mkdir(parents=True, exist_ok=True)
            with tar.extractfile(member) as src, target.open('xb') as dst:
                for block in iter(lambda: src.read(1024**2), b''):
                    digest.update(block); count += len(block); dst.write(block)
            actual = dict(bytes=count, sha256=digest.hexdigest()); logical += count
            require(actual == (inventory_binding if member.name == 'collection-inventory.json'
                               else inventory.get(member.name)), 'Return member differs: '+member.name)
    require(seen == set(inventory) | {'collection-inventory.json'}, 'Return member set differs')
    require(len(seen) == collection['members'] and logical == collection['logical_member_bytes'],
            'Return archive accounting differs')
    return dict(archive=expected, inventory=inventory_binding, regular_members=len(seen),
                logical_member_bytes=logical, every_member_verified=True)


def verify_native_members(before, after):
    """Compare stable executed identities, excluding per-process ldd ASLR addresses.

    The native probe binds every reported absolute file/alias and resolved target.
    Its full execution-member map must remain exact. Raw ldd text is retained as
    evidence but its randomized hexadecimal load addresses are not file identity.
    """
    fields = {'version', 'system', 'binary', 'help', 'execution_members', 'member_scope'}
    require(set(before) == set(after) == fields | {'library_report'}, 'Native probe schema changed')
    require(all(before[k] == after[k] for k in fields)
            and before['system'] == 'Linux' and before['version'] == '2.18', 'Native loaded members changed')


def verify_refinement_inputs(pre, post, pre_sha, features_sha, cache_sha):
    """Validate the actual frozen writer's input references and unchanged neighbors."""
    require(post['pre_partition_sha256'] == pre_sha and post['marker_cache_sha256'] == cache_sha
            and post['parent_features_sha256'] == features_sha == pre['parent_features_sha256']
            and post['neighbors'] == pre['neighbors'], 'Frozen refinement inputs differ')


def grouping_diagnostics(truth, rows, population, targets, clean_markers=()):
    """Independent grouping/length/origin summaries; no invented external geometry.

    Restricted B3 includes all attributable contigs, counting unassigned/excluded
    as zero. Full-bin purity instead includes every assigned base. R95 delegates
    to the previously tested evaluator and its full provided-reference denominator.
    """
    ids = truth['ordered_contig_ids']; contigs = truth['contigs']; clean_markers = set(clean_markers)
    require([r['contig_id'] for r in rows] == ids, 'Grouping row axis differs')
    known = Counter(); cells = Counter(); known_bins = Counter(); all_bins = Counter()
    confirmed_bins = defaultdict(Counter); statuses = defaultdict(Counter)
    for row in rows:
        q = row['contig_id']; item = contigs[q]; bp = item['length']; genome = item['AMBER_label']; b = row['bin_id']
        require(int(row['length']) == bp, 'Grouping length differs')
        if genome is not None:
            known[genome] += bp
            if b: cells[b, genome] += bp; known_bins[b] += bp
        if b:
            all_bins[b] += bp
            confirmed_bins[b].update(item['confirmed_query_bp'])
    strata = defaultdict(Counter); origins = defaultdict(Counter); markers = defaultdict(Counter)
    numerators = Counter(); total_attributable = sum(known.values())
    for row in rows:
        q = row['contig_id']; item = contigs[q]; bp = item['length']; genome = item['AMBER_label']; b = row['bin_id']; status = row['status']
        low = max(x for x in BOUNDS if bp >= x); st = strata[str(low)]; st['contigs'] += 1; st['bp'] += bp
        st[status+'_contigs'] += 1; st[status+'_bp'] += bp
        statuses[status]['contigs'] += 1; statuses[status]['all_bp'] += bp
        mk = markers['clean_marker' if q in clean_markers else 'no_clean_marker']; mk[status+'_contigs'] += 1; mk[status+'_bp'] += bp
        origins[status]['all_bp'] += bp
        for g, n in item['confirmed_query_bp'].items():
            origins[status][population['genomes'][g]['lineage_class']+'_confirmed_bp'] += n
        for field in ['ambiguous_query_bp', 'nn_quarantined_query_bp', 'unsupported_query_bp']:
            origins[status][field] += item[field]
        if genome is not None:
            st['attributable_bp'] += bp
            if b:
                precision = bp*cells[b, genome]/known_bins[b]; recall = bp*cells[b, genome]/known[genome]
                st['b3_precision_sum'] += precision; st['b3_recall_sum'] += recall
                numerators['precision'] += precision; numerators['recall'] += recall
    for st in strata.values():
        for metric in ['precision', 'recall']:
            st['b3_'+metric] = st['b3_'+metric+'_sum']/st['attributable_bp'] if st['attributable_bp'] else None
    p = numerators['precision']/total_attributable if total_attributable else 0
    r = numerators['recall']/total_attributable if total_attributable else 0
    assignments = {row['contig_id']: row['bin_id'] or None for row in rows}
    metrics = recovery(contigs, assignments, truth['reference_axis'], targets['genome_lengths'], targets['targets'])
    bin_rows = []
    for b, bp in sorted(all_bins.items(), key=lambda x: (-x[1], x[0])):
        g, supported = sorted(confirmed_bins[b].items(), key=lambda x: (-x[1], x[0]))[0] if confirmed_bins[b] else (None, 0)
        bin_rows.append(dict(bin_id=b, all_bp=bp, dominant_genome=g, dominant_confirmed_bp=supported,
                             all_DNA_confirmed_purity=supported/bp, supported_genomes=len(confirmed_bins[b])))
    return dict(statuses=dict(statuses), length_strata=dict(strata), origin_by_status=dict(origins),
                clean_marker_by_status=dict(markers), bins=bin_rows,
                restricted_B3=dict(attributable_bp=total_attributable, precision=p, recall=r,
                                   f1=2*p*r/(p+r) if p+r else 0), recovery=metrics,
                recovery_summary=dict(targets=len(metrics), reference_bp=sum(x['reference_bp'] for x in metrics),
                    bp_weighted_R95=sum(x['recovered_bp'] for x in metrics)/sum(x['reference_bp'] for x in metrics),
                    macro_R95=sum(x['whole_reference_R95'] for x in metrics)/len(metrics),
                    at_least_50_percent=sum(x['whole_reference_R95'] >= .5 for x in metrics),
                    at_least_90_percent=sum(x['whole_reference_R95'] >= .9 for x in metrics)),
                geometry='not inferred from partitions; external reference has no comparable learned vectors')


def review(a):
    """Check actual native exits, unchanged caches/axes and complete DNA before scoring."""
    import numpy as np
    from dl_binner.io import load_arrays, read_fasta, read_depth, digest
    from dl_binner.runner import source_records
    from dl_binner.candidate.markers import load_cache
    from dl_binner.accounting import summarize_arm
    from e011_cached import verify_restored
    started = time.perf_counter(); cpu = time.process_time(); a.output.mkdir(parents=True, exist_ok=False)
    protocol = json.loads((EXP/'protocol.json').read_text()); lock = json.loads((REPO/'experiments/E010-coherent-prototype/candidate-lock.json').read_text())
    reuse = json.loads((EXP/'reuse-lock.json').read_text()); completion = json.loads(a.completion.read_text()); root = a.root
    require(completion['status'] == 'SUCCESS' and completion['cpm_completed'] and completion['metabat_completed']
            and completion['cloud_collection_verified'], 'Native phase did not complete')
    cfg = json.loads((root/'phase-config.json').read_text()); release = json.loads((root/'release.json').read_text())
    require(binding(root/'phase-config.json') == release['phase_config'] and cfg['source_commit'] == completion['source_commit'], 'Native source/release differs')
    require([s['name'] for s in completion['stages']] == [s['name'] for s in cfg['stages']], 'Native stage chain differs')
    for step in cfg['stages']:
        receipt = json.loads((root/('log-'+step['name']+'.exit.json')).read_text())
        require(receipt['exit_code'] == 0 and receipt['stop_reason'] is None and receipt['command'] == step['argv'], 'Failed or changed native command: '+step['name'])
    require(source_records() == lock['package_files'], 'Local retained dev4 source differs')
    reused = verify_restored(a.cache, reuse['restore_manifest'], protocol['archive']['archive'])
    require(json.loads((root/'reused-cache.json').read_text()) == reused, 'Native/cache reuse differs')
    require(json.loads((root/'reused-install.json').read_text())['installation_reused'], 'Native installation reuse absent')
    before = json.loads((root/'metabat-before.json').read_text()); after = json.loads((root/'metabat-after.json').read_text())
    verify_native_members(before, after)
    for stage in ['runtime-before', 'runtime-after']:
        native = json.loads((root/(stage+'.json')).read_text())
        require(native['native'] and native['source'] == lock['package_files'], 'Native runtime source differs')
    require(binding(a.fasta) == protocol['inputs']['fasta'] and binding(a.depth) == protocol['inputs']['depth'], 'Full accepted input differs')
    cached = a.cache/'candidate'; features = cached/'features/features.npz'; data, meta = load_arrays(features, 'features')
    fasta = read_fasta(a.fasta); ids = [q for q, _ in fasta]
    require(ids == data['ids'].tolist() and [len(s) for _, s in fasta] == data['lengths'].tolist()
            and [hashlib.sha256(s.encode()).hexdigest() for _, s in fasta] == data['sequence_sha256'].tolist(), 'Full assembly DNA axis differs')
    originals = dict(fasta); samples, depths = read_depth(a.depth, ids)
    require(samples == meta['samples'] == lock['ordered_depth_columns'] and np.array_equal(depths, data['depth']), 'Ordered ten-depth axes differ')
    marker = load_cache(cached/'markers', a.fasta, ids)
    admission = json.loads((REPO/'experiments/E009-competitive-benchmark/truth-v2-admission.json').read_text())
    require(admission['admitted'] and binding(a.truth/'manifest.json') == admission['artifact_manifest'], 'Truth admission differs')
    for name, expected in json.loads((a.truth/'manifest.json').read_text())['files'].items():
        require(binding(a.truth/name) == expected, 'Admitted truth member differs: '+name)
    truth = json.loads((a.truth/'truth.json').read_text()); targets = json.loads((a.truth/'targets.json').read_text())
    require(truth['ordered_contig_ids'] == ids, 'Truth/complete assembly axis differs')
    population = json.loads((REPO/'experiments/E009-competitive-benchmark/truth-population-review.json').read_text())
    done = json.loads((root/'cpm/completed.json').read_text())
    for key, path in [('protocol', EXP/'protocol.json'), ('original_graph', cached/'group/graph.npz'),
                      ('original_embeddings', cached/'embed/embeddings.npz'), ('original_marker_cache', cached/'markers/cache.json')]:
        require(done[key] == binding(path), 'CPM consumed cache differs: '+key)
    old = json.loads((cached/'group/partition.json').read_text()); pre = json.loads((root/'cpm/pre.json').read_text()); post = json.loads((root/'cpm/post.json').read_text())
    require(pre['config'] == protocol['config'] and pre['ids'] == ids and pre['valid'] == old['valid']
            and pre['neighbors'] == old['neighbors'] and pre['graph_sha256'] == old['graph_sha256']
            and pre['embedding_sha256'] == old['embedding_sha256'], 'CPM axes/geometry changed')
    graph, _ = load_arrays(cached/'group/graph.npz', 'candidate_sparse_graph')
    expected_gamma = float(np.median(graph['weights']))/protocol['cpm']['neighbors']
    objective = pre['objective']
    require(objective['gamma'] == expected_gamma and objective['node_sizes'] == 1
            and objective['seed'] == protocol['cpm']['seed']
            and objective['n_iterations'] == protocol['cpm']['leiden_iterations']
            and objective['vertices'] == int(np.count_nonzero(pre['valid']))
            and objective['edges'] == len(graph['weights']), 'Frozen sole CPM density/schedule differs')
    # The frozen refinement writer emits input bindings, not a copied config.
    # Its cfg comes directly from the bound pre/driver protocol; do not require
    # a field absent from the executed native schema or alter that old output.
    verify_refinement_inputs(pre, post, digest(root/'cpm/pre.json'),
                             digest(features), digest(cached/'markers/cache.json'))
    refinement = refinement_membership(pre, post); require(refinement == done['refinement'], 'Paired refinement differs')
    result = dict(source_commit=completion['source_commit'], phase_id=completion['phase_id'], protocol=binding(EXP/'protocol.json'),
        source_lock=protocol['candidate_lock'], full_contigs=len(ids), full_bp=sum(map(len, originals.values())),
        depth_columns=samples, depth_cells=int(depths.size), zero_depth_rows=int((depths == 0).all(1).sum()),
        objective=pre['objective'], actual_refinement=refinement, arms={}, native_science_reused=True,
        preserved_Mac_portability_failure='E010 strict rtol1e-5/atol2e-6 failed at four coordinates; no new inference, tolerance change or vector substitution')
    for name, part in [('cpm-pre', pre), ('cpm-post', post), ('metabat', None)]:
        directory = root/'cpm'/name.split('-')[-1] if part is not None else root/'metabat-export'
        rows, assignments = read_partition(directory/'assignments.tsv', truth)
        if part is not None:
            accounting, _ = summarize_arm(features, directory)
            require(accounting == done['accounting'][name.split('-')[-1]], 'Independent CPM DNA accounting differs')
            require([assignments[q] for q in ids] == [f'bin_{v+1:06d}' if v >= 0 else None for v in part['assignment']], 'CPM partition/export differs')
        else:
            manifest = json.loads((directory/'manifest.json').read_text())
            for file, expected in manifest['files'].items(): require(binding(directory/file) == expected, 'External export member differs')
            observed = {}
            for file in sorted(directory.glob('*.fna')):
                for q, dna in read_fasta(file):
                    require(q not in observed and originals.get(q) == dna, 'External export DNA lost/changed/duplicated')
                    observed[q] = dna
            require(observed == originals, 'External export does not retain complete DNA')
            accounting = manifest
        grouped = grouping_diagnostics(truth, rows, population, targets, marker['clean'])
        result['arms'][name] = dict(assignments=binding(directory/'assignments.tsv'), accounting=accounting, diagnostics=grouped)
        if part is not None:
            checked = diagnostics(truth, rows, part, population, targets)
            require(checked['recovery'] == grouped['recovery'], 'Independent full-denominator recovery differs')
            for metric in ['precision', 'recall', 'f1']:
                require(abs(checked['restricted_B3'][metric]-grouped['restricted_B3'][metric]) < 1e-12, 'Independent B3 differs')
            result['arms'][name]['retained_geometry'] = checked['geometry']
        # Reuse accepted source-union/mixing diagnostics without changing its code.
        import importlib.util
        diagnostic_source = REPO/'experiments/E010-coherent-prototype/review_diagnostics.py'
        spec = importlib.util.spec_from_file_location('accepted_e010_bin_diagnostics', diagnostic_source)
        diagnostic = importlib.util.module_from_spec(spec); spec.loader.exec_module(diagnostic)
        result['arms'][name]['source_bin_diagnostics'] = diagnostic.bin_sources(rows, truth, population, targets['targets'])
        result['arms'][name]['bin_diagnostic_source'] = binding(diagnostic_source)
        print('E011_REVIEW_ARM', name, grouped['recovery_summary'], flush=True)
    result['local_resources'] = dict(wall_seconds=time.perf_counter()-started, process_CPU_seconds=time.process_time()-cpu,
        peak_own_RSS_native_units=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss, platform=sys.platform,
        scope='retained bytes/partitions and admitted truth only; no fit or new geometry')
    result['limits'] = ['development assembly, no generalization or product-feature conclusion', '3.3034% N-quarantine',
        'R95 all-bin purity and full provided-reference denominators; not MAG quality', 'MetaBAT native cvExt assumes variance=mean; different eligibility',
        'restricted B3 excludes unattributable bin DNA; full-bin R95 does not', 'original Mac portability failure remains unresolved']
    write_json(a.output/'review.json', result)


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__); p.add_argument('action', choices=['verify', 'review'])
    for name in ['archive', 'checksum', 'completion', 'output', 'root', 'cache', 'fasta', 'depth', 'truth']: p.add_argument('--'+name, type=Path)
    a = p.parse_args()
    def timeout(*_): raise TimeoutError('Bounded local review exceeded 15 minutes')
    signal.signal(signal.SIGALRM, timeout); signal.alarm(900)
    if a.action == 'verify': write_json(a.output.parent/'member-verification.json', verify_return(a.archive, a.checksum, json.loads(a.completion.read_text()), a.output))
    else: review(a)
