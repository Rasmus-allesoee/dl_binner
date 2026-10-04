"""Native package contracts, actual tiny training, cache and failure accounting."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

import numpy as np
import torch

from dl_binner import io, model, clustering

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'scripts'))
from e003_representation_screen import geometry as reference_geometry
from e004_integration import supervise, review


def dna_fixture(folder, number=9):
    """Write deterministic diverse DNA for native contracts, not biological claims."""
    rng = np.random.default_rng(11)
    rows = [(f'contig_{i}', ''.join(rng.choice(list('ACGT'), size=120))) for i in range(number)]
    path = folder/'assembly.fna'
    path.write_text(''.join(f'>{ident}\n{dna}\n' for ident, dna in rows))
    return path


class NativeBinnerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.folder = Path(self.temp.name)

    def tearDown(self):
        self.temp.cleanup()

    def test_fasta_iupac_strand_counts_and_invalid_inputs(self):
        sequence = 'AAAACGTACGTRYSWKMBDHVNAAAA'
        rc = sequence.translate(str.maketrans('ACGTRYSWKMBDHVN', 'TGCAYRSWMKVHDBN'))[::-1]
        values, counts = io.tnf([('a', sequence), ('b', rc), ('n', 'NNNN'), ('tiny', 'A')])
        np.testing.assert_array_equal(values[0], values[1])
        self.assertEqual(counts[0], sum(set(sequence[i:i+4]) <= set('ACGT') for i in range(len(sequence)-3)))
        self.assertEqual(counts[-2:].tolist(), [0, 0])
        for content in ('>x\nACGT\n>x\nACGT\n', '>x\nACGZ\n', '>x\n', 'ACGT\n', '>\nACGT\n'):
            path = self.folder/'bad.fna'; path.write_text(content)
            with self.assertRaises(ValueError): io.read_fasta(path)

    def test_fresh_real_reader_matches_two_retained_tnf_rows(self):
        source = ROOT/'artifacts/e003-representation-screen/input/fragments.fna'
        rows = io.read_fasta(source)[:2]
        path = self.folder/'real.fna'
        path.write_text(''.join(f'>{i}\n{s}\n' for i, s in rows))
        output = self.folder/'real.npz'
        io.prepare(path, output, min_length=4)
        prepared, _ = io.load_arrays(output, 'features')
        with np.load(ROOT/'artifacts/e003-representation-screen/run-001/tnf.features.npz') as cached:
            np.testing.assert_array_equal(prepared['tnf'], cached['features'][:2])
        self.assertEqual(prepared['tnf'].shape, (2, 136))

    def test_depth_axes_masks_zero_blocks_and_failures(self):
        fasta = dna_fixture(self.folder, 3)
        ids = [i for i, _ in io.read_fasta(fasta)]
        depth = self.folder/'depth.tsv'
        depth.write_text('contig_id\tS1\tS2\ncontig_2\t3\t0\ncontig_0\t0\t0\ncontig_1\t0\t4\n')
        output = self.folder/'features.npz'
        io.prepare(fasta, output, depth, min_length=4)
        data, meta = io.load_arrays(output, 'features')
        np.testing.assert_array_equal(data['depth'], [[0, 0], [0, 4], [3, 0]])
        np.testing.assert_array_equal(data['zero_depth'], data['depth'] == 0)
        fitted = model.fit_transform(data)
        transformed, valid = model.transform(data, fitted)
        np.testing.assert_array_equal(transformed[0, 136:], [0, 0])
        self.assertTrue(valid.all())
        for content in ('contig_id\tS1\tS1\n', 'contig_id\tS1\nx\t1\n',
                        'contig_id\tS1\ncontig_0\t-1\n', 'contig_id\tS1\ncontig_0\tnan\n',
                        'contig_id\tS1\ncontig_0\tinf\n', 'contig_id\tS1\ncontig_0\t1\ncontig_0\t2\n'):
            depth.write_text(content)
            with self.assertRaises(ValueError): io.read_depth(depth, ids)
        samples, absent = io.read_depth(None, ids)
        self.assertEqual(samples, [])
        self.assertEqual(absent.shape, (3, 0))

    def test_byte_and_order_bound_cache_rejections(self):
        fasta = dna_fixture(self.folder, 3)
        path = self.folder/'data.npz'
        io.prepare(fasta, path, min_length=4)
        arrays, meta = io.load_arrays(path, 'features')
        arrays['ids'] = arrays['ids'][::-1]
        with path.open('wb') as f: np.savez(f, **arrays)
        meta['sha256'] = io.digest(path)
        path.with_suffix('.json').write_text(json.dumps(meta))
        with self.assertRaisesRegex(ValueError, 'ordered-ID'): io.load_arrays(path, 'features')
        with path.open('ab') as f: f.write(b'corruption')
        with self.assertRaisesRegex(ValueError, 'byte hash'): io.load_arrays(path, 'features')

    def test_single_sample_transform_retains_depth_magnitude(self):
        fasta = dna_fixture(self.folder, 4)
        depth = self.folder/'depth.tsv'
        depth.write_text('contig_id\tS1\ncontig_0\t0\ncontig_1\t1\ncontig_2\t10\ncontig_3\t100\n')
        output = self.folder/'features.npz'; io.prepare(fasta, output, depth, min_length=4)
        data, _ = io.load_arrays(output, 'features')
        transformed, _ = model.transform(data, model.fit_transform(data))
        self.assertEqual(transformed[0, 136], 0)
        self.assertEqual(len(set(transformed[1:, 136].tolist())), 3)
        self.assertGreater(transformed[3, 136], transformed[2, 136])

    def test_legacy_cache_rejects_changed_dna_and_array_order(self):
        fasta = dna_fixture(self.folder, 3)
        rows = io.read_fasta(fasta)
        values, counts = io.tnf(rows)
        cache = self.folder/'cached.npz'
        np.savez(cache, ids=[r[0] for r in rows], features=values)
        panel = self.folder/'panel.json'
        panel.write_text(json.dumps(dict(fna_sha256=io.digest(fasta), rows=[dict(id=i, bp=len(dna), sequence_sha256=hashlib.sha256(dna.encode()).hexdigest()) for i, dna in rows])))
        receipt = self.folder/'receipt.json'
        data = dict(sha256=io.digest(cache), panel_manifest_sha256=io.digest(panel), detail=dict(valid_fourmers=counts.tolist()))
        receipt.write_text(json.dumps(data))
        actual, _ = io.import_tnf(cache, receipt, panel, fasta, rows)
        np.testing.assert_array_equal(actual, values)
        np.savez(cache, ids=[r[0] for r in rows][::-1], features=values[::-1])
        data['sha256'] = io.digest(cache); receipt.write_text(json.dumps(data))
        with self.assertRaisesRegex(ValueError, 'ordered-ID'): io.import_tnf(cache, receipt, panel, fasta, rows)
        fasta.write_text(fasta.read_text().replace('A', 'C', 1))
        with self.assertRaisesRegex(ValueError, 'DNA file'): io.import_tnf(cache, receipt, panel, fasta, io.read_fasta(fasta))

    def test_nt_xent_independent_formula_and_tail_coverage(self):
        a = torch.tensor([[1., 0.], [0., 1.]])
        b = torch.tensor([[.8, .6], [.6, .8]])
        z = np.concatenate([a.numpy(), b.numpy()])
        sim = z@z.T/.2
        expected = np.mean([-sim[i, (i+2)%4]+np.log(np.exp(np.delete(sim[i], i)).sum()) for i in range(4)])
        self.assertAlmostEqual(float(model.nt_xent(a, b, .2)), expected, places=6)
        parts = model.batches(np.arange(65), 64)
        np.testing.assert_array_equal(np.concatenate(parts), np.arange(65))
        self.assertTrue(all(len(p) >= 2 for p in parts))

    def test_native_training_checkpoint_reload_and_new_input_schema(self):
        fasta = dna_fixture(self.folder)
        features = self.folder/'features.npz'
        io.prepare(fasta, features, min_length=4)
        config = json.loads((ROOT/'experiments/E004-first-binner/training.json').read_text())
        config.update(hidden=8, output=4, epochs=2, batch_size=4)
        cfg = self.folder/'training.json'; cfg.write_text(json.dumps(config))
        checkpoint = self.folder/'checkpoint.pt'
        model.train(features, cfg, checkpoint, 4)
        output = self.folder/'reloaded.npz'
        model.embed(features, output, checkpoint, 4)
        observed, _ = io.load_arrays(output, 'embeddings')
        reference, _ = io.load_arrays(checkpoint.with_suffix('.reference.npz'), 'embeddings')
        np.testing.assert_allclose(observed['features'], reference['features'], rtol=0, atol=1e-7)
        report = json.loads(checkpoint.with_suffix('.json').read_text())
        self.assertEqual([r['contigs_seen'] for r in report['epochs']], [9, 9])
        with self.assertRaisesRegex(ValueError, 'schema'): model.load_checkpoint(checkpoint, ['unexpected_sample'])
        with self.assertRaises(FileExistsError): model.train(features, cfg, checkpoint, 4)
        before = json.dumps(report['transform'], sort_keys=True)
        newdir = self.folder/'new'; newdir.mkdir()
        new_fasta = dna_fixture(newdir, 3)
        new_features = newdir/'features.npz'
        io.prepare(new_fasta, new_features, min_length=4)
        model.embed(new_features, newdir/'embeddings.npz', checkpoint, 4)
        after, _ = model.load_checkpoint(checkpoint, [])
        self.assertEqual(before, json.dumps(after['transform'], sort_keys=True))
        with checkpoint.open('ab') as f: f.write(b'bad')
        with self.assertRaisesRegex(ValueError, 'byte/receipt'): model.load_checkpoint(checkpoint, [])

    def test_no_valid_training_signal_fails_and_preserves_exclusions(self):
        path = self.folder/'none.fna'; path.write_text('>short\nACGT\n>ambiguous\nNNNNNNNN\n')
        out = self.folder/'data.npz'
        io.prepare(path, out, min_length=5)
        data, meta = io.load_arrays(out, 'features')
        self.assertEqual(data['exclusion_reason'].tolist(), ['below_min_length', 'no_valid_fourmers'])
        with self.assertRaisesRegex(ValueError, 'two eligible'): model.fit_transform(data)
        data['tnf'][0, 0] = np.nan
        with self.assertRaises(ValueError): io.validate_features(data, meta)

    def test_blocked_fixed_geometry_matches_native_e003_and_noise(self):
        ids = ['b', 'a', 'c', 'd', 'e', 'f', 'z']
        values = np.array([[2, 1], [2, 1], [2, 1], [1, 2], [1, 2], [1, 2], [0, 0]])
        expected = reference_geometry(values, ids)
        for block in (1, 3, 128):
            actual = clustering.geometry(values, ids, query_block=block)
            for key in ('assignment', 'neighbors', 'valid', 'edges', 'clusters', 'unassigned'):
                self.assertEqual(actual[key], expected[key])
        self.assertEqual(actual['assignment'][-1], -1)
        self.assertEqual(actual['clusters'], 2)

    def test_actual_cluster_export_complete_accounting_and_rejections(self):
        fasta = self.folder/'assembly.fna'
        rows = [(f'A{i}', 'A'*60) for i in range(3)]+[(f'C{i}', 'C'*60) for i in range(3)]+[('short', 'ACGT'), ('none', 'N'*60)]
        fasta.write_text(''.join(f'>{i}\n{s}\n' for i, s in rows))
        features = self.folder/'features.npz'; io.prepare(fasta, features, min_length=20)
        embeddings = self.folder/'raw.npz'; model.embed(features, embeddings)
        partition = self.folder/'raw.partition.json'; clustering.cluster(embeddings, partition)
        folder = self.folder/'export'; clustering.export(features, partition, fasta, folder)
        exported = []
        for path in folder.glob('*.fna'):
            if path.stat().st_size: exported.extend(io.read_fasta(path))
        self.assertEqual(dict(exported), dict(rows))
        self.assertEqual(len(exported), len(rows))
        manifest = json.loads((folder/'manifest.json').read_text())
        self.assertEqual(manifest['excluded'], 2)
        self.assertEqual(manifest['assigned']+manifest['unassigned']+manifest['excluded'], 8)
        malformed = json.loads(partition.read_text()); malformed['assignment'].pop()
        partition.write_text(json.dumps(malformed))
        with self.assertRaisesRegex(ValueError, 'incomplete'): clustering.export(features, partition, fasta, self.folder/'bad')

    def test_fatal_cli_error_exits_promptly_and_guard_stops_timeout_children(self):
        path = self.folder/'invalid.fna'; path.write_text('>x\nINVALID\n')
        result = subprocess.run([sys.executable, '-m', 'dl_binner', 'prepare', '--fasta', str(path), '--output', str(self.folder/'bad.npz')], capture_output=True, text=True, timeout=10)
        self.assertEqual(result.returncode, 1)
        self.assertIn('invalid IUPAC', result.stderr)
        command = [sys.executable, '-c', 'import subprocess,sys,time;subprocess.Popen([sys.executable,"-c","import time;time.sleep(60)"]);time.sleep(60)']
        report = supervise(command, self.folder/'guard', seconds=.4, ram_bytes=8000000000)
        self.assertEqual(report['stop_reason'], 'Time ceiling')
        self.assertLess(report['wall_seconds'], 5)

    def test_receipt_writer_accepts_relative_retained_paths(self):
        with tempfile.TemporaryDirectory(dir=ROOT/'artifacts/e004-first-binner/setup') as name:
            folder = Path(name)
            metrics = dict(fragments=2, bp=1000, neighbor_purity=0., b3_precision=0., b3_recall=0., b3_f1=0., assigned_fraction=0.)
            score = {k:metrics for k in ('all','base_weighted','short','long')};score['by_length']={'500':metrics}
            commit = subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
            (folder/'evaluation.json').write_text(json.dumps(dict(source_commit=commit,scores=dict(raw=score,learned=score),checks={},reload_max_abs=0,limits='software fixture')))
            (folder/'supervisor.json').write_text(json.dumps(dict(exit_code=0,stop_reason=None,wall_seconds=1,peak_sampled_rss_bytes=1)))
            (folder/'checkpoint.json').write_text('{}')
            output = self.folder/'receipt.json'
            review(dict(limits=dict(seconds=7200,ram_bytes=8000000000)),folder.relative_to(ROOT),output)
            observed = json.loads(output.read_text())
            self.assertEqual(observed['run_locator'],str(folder.relative_to(ROOT)))
            self.assertEqual(len(observed['retained_files']),3)


if __name__ == '__main__':
    unittest.main()
