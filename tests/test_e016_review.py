"""Full-axis/denominator refusals and the unchanged two-community keep boundary."""
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).absolute().parents[1] / 'scripts'))
from e016_summarize import numerical_keep, paired


class SummaryContracts(unittest.TestCase):
    def test_complete_target_pairing_and_denominator_refusal(self):
        before = [dict(genome='A', reference_bp=100, recovered_bp=50),
                  dict(genome='zero-origin', reference_bp=1000, recovered_bp=0)]
        after = [dict(genome='zero-origin', reference_bp=1000, recovered_bp=0),
                 dict(genome='A', reference_bp=100, recovered_bp=60)]
        summary, rows = paired(after, before)
        self.assertEqual(summary, dict(gained=1, lost=0, unchanged=1, delta_bp=10))
        self.assertEqual(sum(r['reference_bp'] for r in rows), 1100)
        for bad in [after[:1], after + [after[0]],
                    [after[0], dict(after[1], reference_bp=90)]]:
            with self.assertRaises(ValueError):
                paired(bad, before)

    def test_keep_requires_both_scopes_effect_size_and_no_90percent_count_loss(self):
        baseline = [dict(bp_weighted_R95=.05, at_least_90_percent=4),
                    dict(bp_weighted_R95=.06, at_least_90_percent=30)]
        good = [dict(bp_weighted_R95=.053, at_least_90_percent=4),
                dict(bp_weighted_R95=.066, at_least_90_percent=34)]
        self.assertTrue(numerical_keep(good, baseline))
        self.assertFalse(numerical_keep([dict(good[0], bp_weighted_R95=.049), good[1]], baseline))
        self.assertFalse(numerical_keep([good[0], dict(good[1], at_least_90_percent=29)], baseline))
        self.assertFalse(numerical_keep([good[0], dict(good[1], bp_weighted_R95=.064)], baseline))
        self.assertFalse(numerical_keep(good[:1], baseline))


if __name__ == '__main__':
    unittest.main()
