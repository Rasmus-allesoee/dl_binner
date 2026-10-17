"""Real tiny reader/refiner/export/reload contracts; no community outcomes or fits."""
import copy
import io
import json
import math
from pathlib import Path
import sys
import tarfile
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).absolute().parents[1]/'scripts'))
from e009_common import binding, write_json
from e013_refinement import marker_evidence, quality, seed_proposal, contexts, centroid_context, assess
from e013_control import run

CONFIG = dict(seed=11, physical_overlap_fraction=.5, seed_reliability=.5,
              min_seed_families=2, excess_penalty=5., lloyd_iterations=10,
              context_epsilon=64*sys.float_info.epsilon)


def fixture(root):
    """Build fresh sealed FASTA/cache/graphs and native HMMs with hand-authored calls.

    No reader/refiner/exporter is mocked. Tiny domain/gene annotations and fixed
    vectors/partitions are explicit engineering fixtures, not detector/fit claims.
    PyHMMER writes and reads genuine own synthetic profiles with trusted cutoffs.
    """
    import numpy as np
    import pyhmmer
    from dl_binner.candidate.views import prepare, config, load
    from dl_binner.candidate.markers import POLICY, runtime, reduce_hits
    from dl_binner.io import save_arrays, id_digest, digest
    p = Path(root); cache = p/'restore'; c = cache/'candidate'
    for folder in ['features', 'embed', 'group', 'refine', 'markers']:
        (c/folder).mkdir(parents=True)
    ids = ['z', 'a', 'y', 'b', 'x', 'c', 'old_noise', 'short', 'unknown']
    fasta, depth = p/'all.fa', p/'depth.tsv'; rows = []
    for i, q in enumerate(ids):
        dna = 'GCT'*10+'GGT'*10+('A' if i in [0, 1, 4, 6] else 'C')*3140
        rows.append((q, 'ACGT' if q == 'short' else 'N'*3200 if q == 'unknown' else dna))
    fasta.write_text(''.join('>'+q+'\n'+dna+'\n' for q, dna in rows))
    depth.write_text('contig_id\tZ\tA\n'+''.join(q+('\t0\t0\n' if i == 6 else '\t10\t1\n' if i in [0, 1, 4] else '\t1\t10\n') for i, q in enumerate(ids)))
    cfg = config(); cfg.update(output=2, neighbors=5, min_bin_bp=1)
    prepare(fasta, depth, c/'features', cfg); data, _ = load(c/'features/features.npz'); valid = data['eligible']
    x = np.zeros((len(ids), 2), np.float32)
    for i in np.flatnonzero(valid):
        angle = 0 if i in [0, 1, 4, 6] else .3; x[i] = [np.cos(angle), np.sin(angle)]
    save_arrays(c/'embed/embeddings.npz', dict(ids=data['ids'], features=x, evidence=valid),
                dict(kind='embeddings', features_sha256=digest(c/'features/features.npz'), metric='unit cosine'))
    pairs = sorted([tuple(sorted(pair, key=lambda i: ids[i])) for pair in [(0, 1), (2, 3), (0, 2), (4, 5)]],
                   key=lambda pair: (ids[pair[0]], ids[pair[1]]))
    edges = np.array(pairs, np.int64); weights = np.array([.9 if set(pair) == {0, 2} else 1. for pair in pairs])
    neighbors = np.full((len(ids), 5), -1, np.int64)
    for i in np.flatnonzero(valid):
        neighbors[i] = sorted([int(j) for j in np.flatnonzero(valid) if j != i], key=lambda j: ids[j])[:5]
    save_arrays(c/'group/graph.npz', dict(ids=data['ids'], edges=edges, weights=weights, neighbors=neighbors),
                dict(kind='candidate_sparse_graph', embedding_sha256=digest(c/'embed/embeddings.npz')))
    pre = dict(ids=ids, assignment=[0]*6+[-1]*3, valid=valid.tolist(), clusters=1, unassigned=3,
        reason=['']*6+['old_noise', 'below_min_length', 'no_valid_fourmers'],
        neighbors=[[ids[j] for j in row] if valid[i] else [] for i, row in enumerate(neighbors)],
        config=cfg, parent_features_sha256=digest(c/'features/features.npz'),
        graph_sha256=digest(c/'group/graph.npz'), embedding_sha256=digest(c/'embed/embeddings.npz'),
        objective=dict(gamma=float(np.median(weights))/5))
    hmm = p/'profiles.hmm'; alphabet = pyhmmer.easel.Alphabet.amino()
    with hmm.open('xb') as out:
        for name, sequence in [('F', 'A'*10), ('G', 'G'*10)]:
            digital = pyhmmer.easel.TextSequence(name=name.encode(), sequence=sequence).digitize(alphabet)
            model, _, _ = pyhmmer.plan7.Builder(alphabet).build(digital, pyhmmer.plan7.Background(alphabet))
            model.name = name.encode(); model.cutoffs.trusted = (20., 20.); model.write(out)
    with pyhmmer.plan7.HMMFile(hmm) as stream:
        assert [m.M for m in stream] == [10, 10]
    genes, domains = {}, []
    for j, i in enumerate([0, 2]):
        for k, name in enumerate(['F', 'G']):
            gene = f'g{2*j+k}'; genes[gene] = dict(contig=ids[i], start=k*30, end=(k+1)*30,
                strand=1, protein_length=10, partial_begin=False, partial_end=False)
            domains.append(dict(gene=gene, marker=name, score=60., hmm_from=1, hmm_to=10, hmm_length=10,
                                protein_from=1, protein_to=10, hmm_coverage=1.))
    markers = c/'markers'; families = {'F': 'F', 'G': 'G'}
    evidence = reduce_hits(genes, domains, families); evidence.update(ids=ids, ids_sha256=id_digest(ids))
    (markers/'genes.jsonl').write_text(''.join(json.dumps(dict(gene=g, **v))+'\n' for g, v in genes.items()))
    (markers/'proteins.faa').write_text(''.join('>'+g+'\n'+('A' if int(g[1:]) % 2 == 0 else 'G')*10+'\n' for g in genes))
    write_json(markers/'asset.json', dict(families=families, hmm=binding(hmm), source='own synthetic HMM fixtures', license='own'))
    write_json(markers/'domains.json', domains); write_json(markers/'evidence.json', evidence)
    write_json(markers/'cache.json', dict(kind='candidate_marker_cache', version=1, fasta=binding(fasta), hmm=binding(hmm),
        policy=POLICY, runtime=runtime(), genes=len(genes), domains=len(domains),
        files={q.name: binding(q) for q in markers.iterdir()}))
    write_json(c/'group/partition.json', pre)
    post = copy.deepcopy(pre); post.pop('config'); post.update(assignment=[0, 0, 1, 1, -1, -1, -1, -1, -1],
        reason=['']*4+['refinement_ambiguous_affinity']*2+pre['reason'][6:], clusters=2, unassigned=5,
        pre_partition_sha256=digest(c/'group/partition.json'), marker_cache_sha256=digest(markers/'cache.json'),
        attempts=[dict(pre_bin=0, adopted=True, before={'F': 2, 'G': 2}, k=2, seed_family='F',
                       seed_ids=['z', 'y'], proposed_bp=[6400, 6400], unassigned_proposal=2)])
    write_json(c/'refine/partition.json', post); write_json(c/'candidate.json', cfg); write_json(cache/'runtime.json', {})
    original = dict(bytes=1, sha256='own engineering archive identity')
    write_json(cache/'restore.json', dict(archive=original, restored_files={q.relative_to(cache).as_posix(): binding(q) for q in cache.rglob('*') if q.is_file()}))
    native = p/'native'; (native/'cpm').mkdir(parents=True)
    write_json(native/'cpm/pre.json', pre); write_json(native/'cpm/post.json', post)
    members = {q.relative_to(native).as_posix(): q.read_bytes() for q in native.rglob('*') if q.is_file()}
    write_json(native/'collection-inventory.json', dict(files={name: binding(native/name) for name in members}))
    members['collection-inventory.json'] = (native/'collection-inventory.json').read_bytes()
    archive = p/'native.tar.gz'
    with tarfile.open(archive, 'w:gz') as tar:
        for name, raw in members.items():
            info = tarfile.TarInfo(name); info.size = len(raw); tar.addfile(info, io.BytesIO(raw))
    lock = dict(cache='restore', restore_manifest=binding(cache/'restore.json'), e010_archive=original,
        native_return='native', native_members=['cpm/pre.json', 'cpm/post.json'], e011_inventory=binding(native/'collection-inventory.json'),
        e011_archive_path='native.tar.gz', e011_archive=binding(archive), fasta='all.fa', depth='depth.tsv', hmm_path='profiles.hmm',
        files={q.name: binding(q) for q in [fasta, depth, hmm]}, contexts={'CPM': ['native/cpm/pre.json', 'native/cpm/post.json']})
    protocol = dict(candidate_config=cfg, refinement=CONFIG, samples=['Z', 'A'])
    write_json(p/'lock.json', lock); write_json(p/'protocol.json', protocol)
    return data, x, genes, domains, families, cfg


class RefinementTests(unittest.TestCase):
    def test_actual_cached_consumer_new_refinement_reload_all_DNA_and_negative_graph_gain(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d); fixture(p)
            result = run(p/'lock.json', p/'protocol.json', p/'run', base=p)
            self.assertEqual(result['selection'], {'median_seeded': 1})
            self.assertEqual(result['contigs'], 9); self.assertEqual(result['bp'], 25604)
            self.assertEqual(result['accounting']['statuses']['assigned']['contigs'], 6)
            self.assertEqual(result['accounting']['statuses']['unassigned']['contigs'], 1)
            self.assertEqual(result['accounting']['statuses']['excluded']['contigs'], 2)
            audit = json.loads((p/'run/selected-graph-audit.json').read_text())
            self.assertLess(audit['0']['delta_half_quality'], 0)
            from e013_review import verify_choices
            pre = json.loads((p/'native/cpm/pre.json').read_text()); old = json.loads((p/'native/cpm/post.json').read_text())
            part = json.loads((p/'run/partition.json').read_text()); decisions = json.loads((p/'run/decisions.json').read_text())
            alternatives = json.loads((p/'run/alternatives.json').read_text())
            self.assertTrue(verify_choices(pre, old, part, decisions, alternatives)['no_merge_or_new_assignment'])
            malformed = copy.deepcopy(part); malformed['assignment'][0] = -1
            with self.assertRaisesRegex(ValueError, 'whole alternative'):
                verify_choices(pre, old, malformed, decisions, alternatives)
            self.assertTrue(result['encoder_graph_seed_unchanged']); self.assertFalse(result['truth_accessed'])
            with self.assertRaises(FileExistsError): run(p/'lock.json', p/'protocol.json', p/'run', base=p)
            (p/'restore/candidate/markers/domains.json').write_text('corrupt')
            with self.assertRaisesRegex(ValueError, 'bytes differ'):
                run(p/'lock.json', p/'protocol.json', p/'corrupt', base=p)

    def test_weighted_call_context_partial_marginal_overlap_and_ambiguity(self):
        from e012_marker_audit import profile_headers
        with tempfile.TemporaryDirectory() as d:
            data, vectors, genes, domains, families, cfg = fixture(d)
            headers = profile_headers(Path(d)/'profiles.hmm'); ids = data['ids'].tolist()
            good = marker_evidence(genes, domains, families, headers, ids, data['lengths'], CONFIG)
            self.assertEqual(len(good['loci']), 4)
            changed = copy.deepcopy(domains); changed[0]['score'] = 20.01
            altered = marker_evidence(genes, changed, families, headers, ids, data['lengths'], CONFIG)
            self.assertLess(altered['calls']['z']['F'][0], .01)
            g = copy.deepcopy(genes); g['g0']['partial_begin'] = True
            changed[0].update(score=60., hmm_to=5, protein_to=5, hmm_coverage=.5)
            partial = marker_evidence(g, changed, families, headers, ids, data['lengths'], CONFIG)
            self.assertAlmostEqual(partial['calls']['z']['F'][0], .25, places=9)
            duplicate = marker_evidence(genes, domains+[domains[0]], families, headers, ids, data['lengths'], CONFIG)
            self.assertEqual(len(duplicate['loci']), 4); self.assertEqual(len(duplicate['consolidated']), 1)
            ambiguous = marker_evidence(genes, domains+[dict(domains[0], marker='G')], families, headers, ids, data['lengths'], CONFIG)
            self.assertIn('g0', ambiguous['ambiguous_genes']); self.assertNotIn('F', ambiguous['calls']['z'])
            with self.assertRaisesRegex(ValueError, 'Malformed cached HMM'):
                marker_evidence(genes, [dict(domains[0], protein_to=11)], families, headers, ids, data['lengths'], CONFIG)

    def test_median_singletons_same_contig_copies_and_collapse_have_no_forced_split(self):
        import numpy as np
        ids = ['a', 'b', 'c', 'd']; lengths = np.full(4, 6000); x = np.array([[1., 0], [1., 0], [0., 1], [0., 1]])
        evidence = dict(panel_size=4, calls={'a': {'F': [1.], 'G': [1.], 'single1': [1.]},
                                           'c': {'F': [1.], 'G': [1.], 'single2': [1.]}})
        groups, trace = seed_proposal(list(range(4)), evidence, ids, lengths, x, CONFIG, dict(min_bin_contigs=2, min_bin_bp=10000))
        self.assertIsNotNone(groups)  # Upper median of [1,1,2,2] is two.
        evidence['calls']['a']['single3'] = [1.]
        groups, trace = seed_proposal(list(range(4)), evidence, ids, lengths, x, CONFIG, dict(min_bin_contigs=2, min_bin_bp=10000))
        self.assertIsNone(groups); self.assertEqual(trace['k'], 1)
        evidence['calls'] = {'a': {'F': [1., 1.], 'G': [1.]}, 'c': {'F': [1.], 'G': [1.]}}
        groups, _ = seed_proposal(list(range(4)), evidence, ids, lengths, x, CONFIG, dict(min_bin_contigs=2, min_bin_bp=10000))
        self.assertIsNone(groups)  # Only one family supports K after same-contig copies are refused as seeds.
        evidence['calls'] = {q: {'F': [1.], 'G': [1.]} for q in ['a', 'c']}
        groups, trace = seed_proposal(list(range(4)), evidence, ids, lengths, np.tile([1., 0], (4, 1)), CONFIG, dict(min_bin_contigs=2, min_bin_bp=10000))
        self.assertIsNone(groups); self.assertEqual(trace['reason'], 'collapsed_child')

    def test_contexts_missing_depth_no_invented_variance_and_full_noise_penalty(self):
        import numpy as np
        x = np.array([[0.], [0.], [1.], [1.]]); lengths = np.full(4, 1000)
        score = centroid_context([0, 1, 2, 3], [[0, 1], [2, 3]], [], x, lengths)
        self.assertEqual(score['score'], 1)
        score = centroid_context([0, 1, 2, 3], [[0, 2], [1, 3]], [], x, lengths)
        self.assertLess(score['score'], 0)
        missing = centroid_context([0, 1, 2, 3], [[0, 1], [2, 3]], [], np.empty((4, 0)), lengths)
        self.assertFalse(missing['available']); self.assertEqual(missing['score'], 0)
        identical = centroid_context([0, 1, 2, 3], [[0, 1], [2, 3]], [], np.ones((4, 2)), lengths)
        self.assertEqual(identical['score'], 0)
        with tempfile.TemporaryDirectory() as d:
            data, vectors, genes, domains, families, cfg = fixture(d)
            data['depth'][:] = 0; comp, dep, meta = contexts(data)
            self.assertEqual(dep.shape[1], 0)
            self.assertIn('no window/per-base variance', meta['depth'])

    def test_weighted_quality_and_discarding_DNA_cannot_manufacture_gain(self):
        import numpy as np
        ids = ['a', 'b', 'c', 'd']; lens = np.full(4, 1000)
        e = dict(panel_size=2, calls={'a': {'F': [1.], 'G': [1.]}, 'c': {'F': [1.], 'G': [1.]}})
        self.assertEqual(quality([0, 1, 2, 3], e, ids, CONFIG)['score'], -400)
        self.assertEqual(quality([0, 1], e, ids, CONFIG)['score'], 100)
        # Full-parent weighting assigns noise its old quality, not a free zero.
        x = np.array([[1., 0], [1., 0], [0., 1], [0., 1]])
        data = dict(valid_fourmers=np.ones(4), depth_evidence=np.ones(4, bool))
        with self.assertRaisesRegex(ValueError, 'Malformed whole-parent'):
            assess([0, 1, 2, 3], [[], []], [0, 1, 2, 3], e, ids, lens, x, x, x, data, CONFIG)
        result = assess([0, 1, 2, 3], [[0], [2]], [1, 3], e, ids, lens, x, x, x, data, CONFIG)
        self.assertEqual(result['weighted_quality'], -150)  # .5*100 + .5*(-400)
        self.assertFalse(result['eligible'])  # Singleton context has no support.


class LocalBoundaryTests(unittest.TestCase):
    def test_actual_output_cap_and_original_clock_leave_failure_evidence(self):
        import time
        from e013_local import OutputGuard
        with tempfile.TemporaryDirectory() as d:
            p = Path(d)
            with self.assertRaisesRegex(TimeoutError, 'working-space cap'):
                with OutputGuard(p, 5, 128):
                    (p/'retained-failure.bin').write_bytes(b'x'*256)
                    time.sleep(2)
            self.assertEqual((p/'retained-failure.bin').stat().st_size, 256)
            with self.assertRaisesRegex(TimeoutError, 'cumulative E013 clock'):
                with OutputGuard(p, .05, 1024): time.sleep(1)

    def test_restore_only_completed_control_and_compact_archive_readback(self):
        from e013_local import verify_reuse, collect
        with tempfile.TemporaryDirectory() as d:
            p = Path(d); root = p/'closed'; root.mkdir()
            members = [('partition', 'partition.json'), ('decisions', 'decisions.json'), ('alternatives', 'alternatives.json'),
                       ('quality_evidence', 'quality-evidence.json'), ('context_transforms', 'context-transforms.json'),
                       ('graph_audit', 'selected-graph-audit.json')]
            done = dict(status='SUCCESS', protocol=dict(bytes=1, sha256='frozen'), input_lock=dict(bytes=2, sha256='locked'))
            for key, name in members:
                write_json(root/name, {'data': name}); done[key] = binding(root/name)
            write_json(root/'completed.json', done)
            self.assertTrue(verify_reuse(root, done['protocol'], done['input_lock'])['no_refinement_repeat'])
            (root/'unassigned.fna').write_text('>retained\nACGT\n')
            record = collect(root, p/'evidence.tar.gz')
            self.assertTrue(record['every_member_readback'])
            with tarfile.open(p/'evidence.tar.gz') as archive:
                self.assertNotIn('unassigned.fna', archive.getnames())
                self.assertIn('partition.json', archive.getnames())
            (root/'decisions.json').write_text('corrupt')
            with self.assertRaisesRegex(ValueError, 'Reused E013 member differs'):
                verify_reuse(root, done['protocol'], done['input_lock'])


if __name__ == '__main__':
    unittest.main()
