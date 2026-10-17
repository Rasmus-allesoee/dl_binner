"""Actual cached readers/selection/export on hand-authored tiny evidence; no fits."""
import copy
import io
import json
from pathlib import Path
import sys
import tarfile
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).absolute().parents[1]/'scripts'))
from e009_common import binding, write_json
from e012_acceptance import gains, run, select, validate_proposals, verify_inputs


def fixture(root):
    """Write real FASTA/NPZ/cache/partitions with opaque-ID endpoints and old noise.

    Marker domains and child memberships are explicit engineering inputs, not
    detected genes or regenerated scientific splits. No reader is mocked.
    """
    import numpy as np
    from dl_binner.candidate.views import prepare, config, load
    from dl_binner.candidate.markers import POLICY, runtime, reduce_hits
    from dl_binner.io import save_arrays, id_digest, digest
    p = Path(root); cache = p/'restore'; c = cache/'candidate'
    for name in ['features', 'embed', 'group', 'refine', 'markers']:
        (c/name).mkdir(parents=True)
    fasta, depth = p/'all.fa', p/'depth.tsv'
    ids = ['z', 'a', 'y', 'b', 'x', 'c', 'old_noise', 'short', 'unknown']
    fasta.write_text(''.join('>'+q+'\n'+('ACGT' if q == 'short' else 'N'*3200 if q == 'unknown' else 'ACGT'*800)+'\n' for q in ids))
    depth.write_text('contig_id\tZ\tA\n'+''.join(q+'\t5\t9\n' for q in reversed(ids)))
    cfg = config(); cfg.update(output=2, neighbors=5, min_bin_bp=1)
    prepare(fasta, depth, c/'features', cfg)
    data, _ = load(c/'features/features.npz'); valid = data['eligible']
    vectors = np.zeros((len(ids), 2), np.float32); vectors[valid, 0] = 1
    save_arrays(c/'embed/embeddings.npz', dict(ids=data['ids'], features=vectors, evidence=valid),
                dict(kind='embeddings', features_sha256=digest(c/'features/features.npz'), metric='unit cosine'))
    pairs = [(0, 1), (2, 3), (0, 2), (4, 5)]
    pairs = sorted([tuple(sorted(pair, key=lambda i: ids[i])) for pair in pairs], key=lambda pair: (ids[pair[0]], ids[pair[1]]))
    edges = np.array(pairs, np.int64); weights = np.array([.01 if set(v) == {0, 2} else 1 for v in pairs])
    neighbors = np.full((len(ids), 5), -1, np.int64)
    for i in np.flatnonzero(valid):
        neighbors[i] = sorted([int(j) for j in np.flatnonzero(valid) if j != i], key=lambda j: ids[j])[:5]
    graph = dict(ids=data['ids'], edges=edges, weights=weights, neighbors=neighbors)
    save_arrays(c/'group/graph.npz', graph, dict(kind='candidate_sparse_graph', embedding_sha256=digest(c/'embed/embeddings.npz')))
    pre = dict(ids=ids, valid=valid.tolist(), assignment=[0]*6+[-1]*3,
               reason=['']*6+['old_noise', 'below_min_length', 'no_valid_fourmers'],
               clusters=1, unassigned=3,
               neighbors=[[ids[j] for j in row] if valid[i] else [] for i, row in enumerate(neighbors)],
               config=cfg, parent_features_sha256=digest(c/'features/features.npz'),
               graph_sha256=digest(c/'group/graph.npz'), embedding_sha256=digest(c/'embed/embeddings.npz'))
    genes = {f'g{n}': dict(contig=ids[i], start=n*30, end=n*30+30, strand=1,
                          protein_length=10, partial_begin=False, partial_end=False)
             for n, i in enumerate([0, 0, 2, 2])}
    domains = [dict(gene=g, marker='F' if n % 2 == 0 else 'G', score=40.,
                    hmm_from=1, hmm_to=10, hmm_length=10, protein_from=1, protein_to=10,
                    hmm_coverage=1.) for n, g in enumerate(genes)]
    families = {'F': 'F', 'G': 'G'}; evidence = reduce_hits(genes, domains, families)
    evidence.update(ids=ids, ids_sha256=id_digest(ids), gene_count=4)
    markers = c/'markers'
    (markers/'genes.jsonl').write_text(''.join(json.dumps(dict(gene=g, **v))+'\n' for g, v in genes.items()))
    (markers/'proteins.faa').write_text(''.join('>'+g+'\n'+'A'*10+'\n' for g in genes))
    write_json(markers/'domains.json', domains); write_json(markers/'evidence.json', evidence)
    hmm_binding = dict(bytes=0, sha256='synthetic engineering metadata; never searched')
    write_json(markers/'asset.json', dict(families=families, hmm=hmm_binding))
    write_json(markers/'cache.json', dict(kind='candidate_marker_cache', version=1,
        fasta=binding(fasta), hmm=hmm_binding, policy=POLICY, runtime=runtime(), genes=4, domains=4,
        files={f.name: binding(f) for f in markers.iterdir()}))
    write_json(c/'group/partition.json', pre)
    post = copy.deepcopy(pre); post.pop('config')
    post.update(assignment=[0, 0, 1, 1, -1, -1, -1, -1, -1], clusters=2, unassigned=5,
                reason=['']*4+['refinement_ambiguous_affinity']*2+pre['reason'][6:],
                pre_partition_sha256=digest(c/'group/partition.json'), marker_cache_sha256=digest(markers/'cache.json'),
                attempts=[dict(pre_bin=0, adopted=True, before={'F': 2, 'G': 2}, k=2,
                               seed_family='F', seed_ids=['z', 'y'], proposed_bp=[6400, 6400], unassigned_proposal=2)])
    write_json(c/'refine/partition.json', post); write_json(c/'candidate.json', cfg)
    write_json(cache/'runtime.json', {})
    restored = {f.relative_to(cache).as_posix(): binding(f) for f in cache.rglob('*') if f.is_file()}
    original = dict(bytes=3, sha256='engineering archive identity')
    write_json(cache/'restore.json', dict(archive=original, restored_files=restored))
    native = p/'native'; (native/'cpm').mkdir(parents=True)
    write_json(native/'cpm/pre.json', pre); write_json(native/'cpm/post.json', post)
    payload = {f.relative_to(native).as_posix(): f.read_bytes() for f in native.rglob('*') if f.is_file()}
    write_json(native/'collection-inventory.json', dict(files={n: binding(native/n) for n in payload}))
    payload['collection-inventory.json'] = (native/'collection-inventory.json').read_bytes()
    archive = p/'native.tar.gz'
    with tarfile.open(archive, 'w:gz') as tar:
        for name, content in payload.items():
            item = tarfile.TarInfo(name); item.size = len(content); tar.addfile(item, io.BytesIO(content))
    lock = dict(files={'all.fa': binding(fasta), 'depth.tsv': binding(depth)}, cache='restore',
                restore_manifest=binding(cache/'restore.json'), e010_archive=original,
                native_return='native', e011_inventory=binding(native/'collection-inventory.json'),
                native_members=['cpm/pre.json', 'cpm/post.json'], e011_archive_path='native.tar.gz',
                e011_archive=binding(archive), fasta='all.fa', depth='depth.tsv',
                contexts={'RB': ['restore/candidate/group/partition.json', 'restore/candidate/refine/partition.json'],
                          'CPM': ['native/cpm/pre.json', 'native/cpm/post.json']})
    protocol = dict(config=cfg, samples=['Z', 'A'], rule=dict(gamma=float(np.median(weights))/5))
    write_json(p/'lock.json', lock); write_json(p/'protocol.json', protocol)
    return data, graph, pre, post, evidence['clean'], cfg, lock


class AcceptanceTests(unittest.TestCase):
    def test_actual_production_consumer_full_export_and_refuse_corrupt_or_existing(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d); data, graph, pre, post, clean, cfg, lock = fixture(p)
            result = run(p/'lock.json', p/'protocol.json', p/'run', base=p)
            self.assertEqual(result['status'], 'SUCCESS')
            for context in ['RB', 'CPM']:
                self.assertEqual(result['contexts'][context]['accepted'], 1)
                self.assertEqual(result['contexts'][context]['accounting']['contigs'], 9)
                self.assertEqual(result['contexts'][context]['accounting']['bp'], 25604)
                import csv
                with (p/'run'/context/'export/assignments.tsv').open() as stream:
                    rows = list(csv.DictReader(stream, delimiter='\t'))
                self.assertEqual([r['status'] for r in rows], ['assigned']*4+['unassigned']*3+['excluded']*2)
            with self.assertRaises(FileExistsError):
                run(p/'lock.json', p/'protocol.json', p/'run', base=p)
            (p/'native/cpm/post.json').write_text('corrupt')
            with self.assertRaisesRegex(ValueError, 'Sealed native member differs'):
                verify_inputs(lock, p)
            (p/'restore/candidate/group/graph.npz').unlink()
            with self.assertRaisesRegex(ValueError, 'member set differs'):
                verify_inputs(lock, p)

    def test_delta_matches_real_native_fixed_membership_CPM_quality_without_optimizer(self):
        import numpy as np
        import igraph as ig
        import leidenalg as la
        from e011_cached import cached_graph
        with tempfile.TemporaryDirectory() as d:
            data, graph, pre, post, clean, cfg, _ = fixture(d)
            parents, proposals = validate_proposals(pre, post, data['lengths'], clean, cfg)
            selected, edges = cached_graph(graph, pre['ids'], np.array(pre['valid']))
            self.assertTrue(any(i > j for i, j in graph['edges']))
            native = ig.Graph(n=len(selected), edges=edges.tolist())
            def quality(labels):
                membership = []; next_noise = 1+max(labels)
                for i in selected:
                    if labels[i] < 0:
                        membership.append(next_noise); next_noise += 1
                    else: membership.append(labels[i])
                # Normalize gaps; quality of a fixed partition only, never optimize.
                remap = {x: i for i, x in enumerate(sorted(set(membership)))}
                return la.CPMVertexPartition(native, initial_membership=[remap[x] for x in membership],
                    weights=graph['weights'].tolist(), node_sizes=[1]*len(selected), resolution_parameter=.1).quality()/2
            actual = gains(graph['edges'], graph['weights'], pre, post, proposals, .1)[0]
            self.assertAlmostEqual(actual['delta_half_quality'], quality(post['assignment'])-quality(pre['assignment']))
            # The edge between the two noise vertices must be lost, not omitted.
            self.assertAlmostEqual(actual['cut_weight'], 1.01)
            self.assertEqual(actual['separated_pairs'], 13)

    def test_accept_veto_tie_noise_and_unchanged_parent(self):
        import numpy as np
        with tempfile.TemporaryDirectory() as d:
            data, graph, pre, post, clean, cfg, _ = fixture(d)
            a, decisions = select(data, graph, pre, post, clean, cfg, .2)
            self.assertTrue(decisions[0]['accepted']); self.assertEqual(a['assignment'][4:7], [-1]*3)
            b, decisions = select(data, graph, pre, post, clean, cfg, .001)
            self.assertFalse(decisions[0]['accepted']); self.assertEqual(b['assignment'], pre['assignment'])
            _, proposals = validate_proposals(pre, post, data['lengths'], clean, cfg)
            # Exact binary tie and one-ULP gain both retain the parent.
            proposals = {0: dict(members=[0, 1], groups=[[0], [1]], noise=[])}
            tiny_pre = dict(assignment=[0, 0]); tiny_post = dict(assignment=[0, 1])
            for weight in [.5, np.nextafter(.5, 0)]:
                self.assertFalse(gains([[0, 1]], [weight], tiny_pre, tiny_post, proposals, .5)[0]['accepted'])

    def test_refuse_unrecorded_split_changed_cache_axis_merge_and_duplicate_edge(self):
        import numpy as np
        with tempfile.TemporaryDirectory() as d:
            data, graph, pre, post, clean, cfg, _ = fixture(d)
            for change in ['unrecorded', 'cache', 'axis', 'new_assignment', 'count']:
                bad = copy.deepcopy(post)
                if change == 'unrecorded': bad['attempts'] = []
                elif change == 'cache': bad['attempts'][0]['before']['F'] = 3
                elif change == 'axis': bad['ids'][0] = 'wrong'
                elif change == 'new_assignment': bad['assignment'][6] = 0
                else: bad['attempts'][0]['unassigned_proposal'] = 3
                with self.subTest(change=change), self.assertRaises(ValueError):
                    select(data, graph, pre, bad, clean, cfg, .2)
            graph['edges'] = np.vstack([graph['edges'], graph['edges'][0]])
            graph['weights'] = np.append(graph['weights'], graph['weights'][0])
            with self.assertRaisesRegex(ValueError, 'Duplicate'):
                select(data, graph, pre, post, clean, cfg, .2)


class MarkerProjectionTests(unittest.TestCase):
    def test_reverse_circular_normalization_and_gene_domain_clipping(self):
        from e009_truth_v2 import parse_paf
        from e012_marker_audit import clip_span, classify_pair
        refs = {'alias': dict(length=100, offset=95, canonical_id='r', genome='G')}
        with tempfile.TemporaryDirectory() as d:
            p = Path(d)/'existing.paf'
            p.write_text('q\t10\t0\t10\t-\talias\t100\t0\t10\t10\t10\t60\tcg:Z:10=\tnn:i:0\tNM:i:0\n')
            blocks, vetoes, _ = parse_paf(p, {'q': 10}, refs, dict(aligned_query_bp_min=4, identity_min=.99))
            gene = clip_span(2, 8, blocks['q'], vetoes['q'])
            self.assertEqual(gene['source_intervals'], {'r': [[0, 3], [97, 100]]})
            self.assertEqual(gene['confirmed_query_bp'], {'G': 6})
            distinct = dict(gene, source_intervals={'r': [[30, 36]]})
            self.assertEqual(classify_pair(gene, distinct)['classification'], 'same_genome_distinct_loci_same_provided_replicon')
            replicon = dict(gene, source_intervals={'r2': [[30, 36]]})
            self.assertEqual(classify_pair(gene, replicon)['classification'], 'same_genome_distinct_provided_replicons')
            self.assertIn('duplication_candidate', classify_pair(gene, gene)['classification'])

    def test_global_N_veto_competition_gaps_and_malformed_input_refusal(self):
        from e009_truth_v2 import parse_paf
        from e012_marker_audit import clip_span
        refs = {'r': dict(length=100, offset=0, canonical_id='r', genome='G'),
                'other': dict(length=100, offset=0, canonical_id='other', genome='H')}
        policy = dict(aligned_query_bp_min=4, identity_min=.5)
        with tempfile.TemporaryDirectory() as d:
            p = Path(d)/'retained.paf'
            clean = 'q\t12\t0\t12\t+\tr\t100\t10\t22\t10\t14\t60\tcg:Z:4=2I3=2D3=\tnn:i:0\tNM:i:4\n'
            p.write_text(clean)
            b, v, _ = parse_paf(p, {'q': 12}, refs, policy)
            item = clip_span(2, 10, b['q'], v['q'])
            self.assertEqual(item['source_intervals'], {'r': [[12, 17], [19, 20]]})
            self.assertEqual(item['unsupported_query_bp'], 2)
            # A qualifying N-bearing competitor vetoes all its query span.
            n = 'q\t12\t0\t12\t+\tother\t100\t0\t12\t11\t11\t60\tcg:Z:12=\tnn:i:1\tNM:i:1\n'
            p.write_text(clean+n)
            b, v, _ = parse_paf(p, {'q': 12}, refs, policy)
            item = clip_span(2, 10, b['q'], v['q'])
            self.assertEqual(item['nn_quarantined_query_bp'], 8)
            self.assertEqual(item['confirmed_query_bp'], {})
            # Two clean genomes compete; clipping cannot manufacture uniqueness.
            other = 'q\t12\t0\t12\t+\tother\t100\t0\t12\t12\t12\t60\tcg:Z:12=\tnn:i:0\tNM:i:0\n'
            p.write_text(clean+other)
            b, v, _ = parse_paf(p, {'q': 12}, refs, policy)
            self.assertEqual(clip_span(2, 10, b['q'], v['q'])['ambiguous_query_bp'], 6)
            p.write_text(clean.replace('cg:Z:4=2I3=2D3=', 'cg:Z:12M'))
            with self.assertRaisesRegex(ValueError, 'Unsupported'):
                parse_paf(p, {'q': 12}, refs, policy)
            p.write_text(clean.replace('nn:i:0', 'nn:i:1'))
            with self.assertRaisesRegex(ValueError, 'ambiguous-base counts'):
                parse_paf(p, {'q': 12}, refs, policy)


class ReviewAndReuseTests(unittest.TestCase):
    def test_paired_reference_denominators_and_unknown_DNA_cells(self):
        from e012_review import paired_targets, population_cells
        old = [dict(genome='G', reference_bp=1000000, recovered_bp={'cpm-pre': 200000, 'cpm-post': 0})]
        selected = [dict(genome='G', reference_bp=1000000, recovered_bp=200000)]
        pair = paired_targets(selected, old, 'CPM')[0]
        self.assertEqual(pair['selected_minus_parent_bp'], 0)
        self.assertEqual(pair['selected_minus_old_children_bp'], 200000)
        self.assertEqual(pair['reference_bp'], 1000000)
        with self.assertRaisesRegex(ValueError, 'reference length'):
            paired_targets([dict(selected[0], reference_bp=300000)], old, 'CPM')
        def item(length, g, nn=0):
            return dict(length=length, AMBER_label=g, confirmed_query_bp={g: length} if g else {},
                        nn_quarantined_query_bp=nn, ambiguous_query_bp=0, unsupported_query_bp=0)
        truth = dict(contigs={'short': item(31, None, 31), 'other': item(800, 'V'), 'b': item(10000, 'G')})
        rows = [dict(contig_id='short', status='excluded'), dict(contig_id='other', status='unassigned'),
                dict(contig_id='b', status='assigned')]
        cells = population_cells(rows, truth, {'genomes': {'G': {'lineage_class': 'bacterial'}, 'V': {'lineage_class': 'viral'}}}, {'b'})['cells']
        self.assertEqual(sum(v['all_bp'] for v in cells.values()), 10831)
        self.assertEqual(sum(v['nn_quarantined_query_bp'] for v in cells.values()), 31)
        self.assertEqual(cells['768|viral|candidate_eligible|unassigned|no_clean_marker']['confirmed_viral_bp'], 800)

    def test_reuse_refuses_failed_or_corrupt_selection_without_fallback(self):
        from e012_acceptance import EXP
        from e012_local import verify_selection_reuse
        with tempfile.TemporaryDirectory() as d:
            p = Path(d); (p/'CPM').mkdir()
            write_json(p/'CPM/partition.json', dict(assignment=[0, -1]))
            write_json(p/'CPM/decisions.json', [])
            done = dict(status='SUCCESS', protocol=binding(EXP/'protocol.json'), contexts={'CPM': dict(
                partition=binding(p/'CPM/partition.json'), decisions=binding(p/'CPM/decisions.json'))})
            (p/'completed.json').write_text(json.dumps(done))
            self.assertTrue(verify_selection_reuse(p)['no_reselection'])
            (p/'CPM/decisions.json').write_text('corrupt')
            with self.assertRaisesRegex(ValueError, 'member differs'):
                verify_selection_reuse(p)
            done['status'] = 'FAILED'; (p/'completed.json').write_text(json.dumps(done))
            with self.assertRaisesRegex(ValueError, 'Only successful'):
                verify_selection_reuse(p)


if __name__ == '__main__':
    unittest.main()
