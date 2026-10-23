"""Exact prospective E020 criterion and malformed full-denominator refusal."""
from pathlib import Path
import sys
import unittest
sys.path.insert(0, str(Path(__file__).absolute().parents[1]/'scripts'))
from e020_summarize import disposition


def row(delta=0, count=0):
    """Return integer base totals with a 0.005 boundary at exactly 500 bp."""
    return dict(candidate_bp=1000+delta, baseline_bp=1000, reference_bp=100000,
                candidate_90=3+count, baseline_90=3)


class Summary(unittest.TestCase):
    def test_exact_one_material_gain_and_no_loss(self):
        self.assertEqual(disposition([row(500), row()]), 'KEEP')
        self.assertEqual(disposition([row(499), row()]), 'MODIFY')
        self.assertEqual(disposition([row(500), row(-1)]), 'MODIFY')
        self.assertEqual(disposition([row(500, -1), row()]), 'MODIFY')

    def test_abandon_and_count_only_modify(self):
        self.assertEqual(disposition([row(), row()]), 'ABANDON')
        self.assertEqual(disposition([row(-1), row(-1)]), 'ABANDON')
        self.assertEqual(disposition([row(-1, 1), row(-1)]), 'MODIFY')

    def test_refuse_malformed_scope_and_denominators(self):
        for rows in [[row()], [row()|dict(reference_bp=0), row()],
                     [row()|dict(candidate_bp=100001), row()], [row()|dict(candidate_90=True), row()]]:
            with self.subTest(rows=rows), self.assertRaises(ValueError):
                disposition(rows)


if __name__ == '__main__':
    unittest.main()
