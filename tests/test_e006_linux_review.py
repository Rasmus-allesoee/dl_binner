"""Retained-evidence regressions; no training, extraction or binner imports."""
import importlib.util
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).absolute().parents[1]
spec = importlib.util.spec_from_file_location('review_linux', ROOT/'experiments/E006-cli-usability/review_linux.py')
review = importlib.util.module_from_spec(spec); spec.loader.exec_module(review)


class LinuxEvidenceChecks(unittest.TestCase):
    def test_inventory_rejects_byte_changes_and_unsafe_paths(self):
        with tempfile.TemporaryDirectory() as name:
            root = Path(name); path = root/'record'; path.write_text('original')
            binding = review.record(path)
            review.check_files(root, {'record': binding})
            path.write_text('changed')
            with self.assertRaises(AssertionError): review.check_files(root, {'record': binding})
            with self.assertRaises(AssertionError): review.check_files(root, {'../outside': binding})
            path.unlink(); path.symlink_to(root/'elsewhere')
            with self.assertRaises(AssertionError): review.check_files(root, {'record': binding})

    def test_independent_fasta_preserves_order_and_rejects_duplicate_ids(self):
        with tempfile.TemporaryDirectory() as name:
            path = Path(name)/'reads.fna'
            path.write_text('>b description\nacgt\nNN\n>a\nTGCA\n')
            self.assertEqual(list(review.fasta(path)), ['b', 'a'])
            self.assertEqual(review.fasta(path)['b'], 'ACGTNN')
            path.write_text('>same\nACGT\n>same\nTGCA\n')
            with self.assertRaises(AssertionError): review.fasta(path)

    def test_inventory_normalization_cannot_hide_duplicate_distribution(self):
        self.assertEqual(review.normalized({'Jinja2':'3','typing_extensions':'4'}), {'jinja2':'3','typing-extensions':'4'})
        with self.assertRaises(AssertionError): review.normalized({'dl_binner':'1','dl-binner':'2'})

    def test_retained_export_recount_rejects_false_status_totals(self):
        root = ROOT/'artifacts/e006-cli-usability/linux-return-review/generic-linux-smoke-y9xix7p9/smoke/depth run'
        source = review.fasta(root.parent/'fixture inputs/assembly.fna')
        feature, _ = review.arrays(root/'features/features.npz')
        partition = review.load(root/'raw/clustering/partition.json')
        summary = review.load(root/'run-summary.json')['arms']['raw']
        summary['statuses']['assigned']['contigs'] += 1
        with self.assertRaises(AssertionError): review.recount_export(root/'raw/bins', source, feature, summary, partition)
        summary = review.load(root/'run-summary.json')['arms']['raw']
        source[next(iter(source))] = 'N'*180
        with self.assertRaisesRegex(AssertionError, 'DNA'): review.recount_export(root/'raw/bins', source, feature, summary, partition)


if __name__ == '__main__': unittest.main()
