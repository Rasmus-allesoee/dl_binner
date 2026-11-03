"""Read-only E031 counter/clock contracts; no community model is executed."""
import importlib.util
from pathlib import Path
import unittest

SCRIPT = Path(__file__).absolute().parents[1] / 'scripts/e031_learning_diagnostics.py'
spec = importlib.util.spec_from_file_location('e031_readonly_contract', SCRIPT)
module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)


class ReadonlyContracts(unittest.TestCase):
    def test_actual_lazy_and_unequal_counter_semantics(self):
        before = {0: {'step': 7}, 1: {'step': 19}}
        after = {0: {'step': 27}, 1: {'step': 19}, 2: {'step': 3}}
        result = module.counter_audit(before, after, 20)
        self.assertEqual(result['distinct_inherited_steps'], [0, 7, 19])
        self.assertEqual(result['delta_histogram'], {20: 1, 0: 1, 3: 1})
        self.assertEqual(before[1]['step'], 19)

    def test_missing_rewound_nonfinite_and_excessive_counters_refused(self):
        for after in [{}, {0: {'step': 6}}, {0: {'step': 28}}, {0: {'step': float('nan')}}]:
            with self.subTest(after=after), self.assertRaises(ValueError):
                module.counter_audit({0: {'step': 7}}, after, 20)

    def test_original_cumulative_clock_and_bound_review(self):
        start = module.START + 50000
        cfg = dict(original_start_epoch=module.START, science_source=module.SOURCE,
            review_deadline_epoch=start+3600, review_started_epoch=start,
            provider_deadline_epoch=module.START+58500, review_RSS_bytes=8_000_000_000,
            numerical_threads=4, credit_only_admitted=True, incremental_ceiling_USD=8,
            complete_cost_USD_upper=7.2)
        module.check_config(cfg, start+10)
        for key, value in [('original_start_epoch', start), ('review_RSS_bytes', 9_000_000_000),
                           ('review_deadline_epoch', start+3601), ('credit_only_admitted', False)]:
            with self.subTest(key=key), self.assertRaises(ValueError):
                module.check_config(dict(cfg, **{key:value}), start+10)

    def test_actual_held_armer_uses_separate_readonly_consumer(self):
        text=(SCRIPT.parent/'e031_learning_review_arm.py').read_text()
        compile(text, 'actual E031 read-only armer', 'exec')
        self.assertIn("root/'operations/e031_learning_diagnostics.py'", text)
        self.assertIn("unit.startswith('e031-')", text)
        self.assertIn('try-restart', text)
        self.assertNotIn('instances start', text)


if __name__ == '__main__':
    unittest.main()
