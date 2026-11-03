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

    def test_rendered_service_targets_separate_readonly_consumer(self):
        import shlex
        import sys
        sys.path.insert(0, str(SCRIPT.parent))
        from e031_phase import service_content
        root=Path('/retained/review with spaces')
        consumer=root/'operations/e031_learning_diagnostics.py'
        cfg=root/'config.json'
        unit=service_content(root,'/usr/bin/python3',consumer,cfg,'owner')
        command=next(line.removeprefix('ExecStart=') for line in unit.splitlines()
                     if line.startswith('ExecStart='))
        self.assertEqual(shlex.split(command),
            ['/usr/bin/python3','-I','-B',str(consumer),'--config',str(cfg)])
        with self.assertRaises(ValueError):
            service_content(root,'/usr/bin/python3',consumer,'/bad\nExecStart=other','owner')

    def test_missing_operations_provenance_refused_before_service_start(self):
        import sys
        sys.path.insert(0, str(SCRIPT.parent))
        from e031_learning_review_arm import validate_config
        cfg = dict(root='/retained/review', repo='/retained/science', setup_deadline_epoch=100,
            service_name='e031-test', review_deadline_epoch=200, source_commit='a'*40,
            operations_source='a'*40, vm_start_epoch=1, provider_deadline_epoch=250)
        validate_config(cfg)
        del cfg['source_commit']
        with self.assertRaises(ValueError): validate_config(cfg)

    def test_full_reference_integer_summary_and_missing_target_refusal(self):
        import sys
        sys.path.insert(0, str(SCRIPT.parent))
        from e031_learning_summary import integer_metrics
        rows=[dict(genome=str(i),reference_bp=1,recovered_bp=1) for i in range(156)]
        rows[-1]['reference_bp']+=554661890-156
        value=integer_metrics(rows,'E009-GLM')
        self.assertEqual(value,dict(recovered_bp=156,reference_bp=554661890,target_90=155))
        with self.assertRaises(ValueError): integer_metrics(rows[:-1],'E009-GLM')
        rows[-1]['genome']='0'
        with self.assertRaises(ValueError): integer_metrics(rows,'E009-GLM')


if __name__ == '__main__':
    unittest.main()
