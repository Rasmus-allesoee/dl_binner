"""Real tiny ten-sample banks, partial-comparison refusal and long-journal boundary."""
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).absolute().parents[1]
sys.path[:0] = [str(ROOT / 'scripts'), str(ROOT / 'tests/product')]
from e033_measurement_inspection import audit, validate_counters
from e024_coverage import binding
from e021_control_json import publish, MAX_BYTES


class Inspection(unittest.TestCase):
    def test_real_twenty_sample_banks_features_reader_and_zero_population(self):
        from test_multiscale_measurement import fixture
        from dl_binner.multiview.views import prepare, config
        from dl_binner.multiscale.measurement import summarize
        from dl_binner.multiscale.cache import seal, rebind
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            _, _, bam = fixture(root / 'input')
            names = ['sample-%02d' % i for i in range(10)]
            depth = root / 'depth.tsv'
            depth.write_text('contig_id\t' + '\t'.join(names) + '\nopaque-A\t'
                             + '\t'.join(['1'] * 10) + '\nopaque-Z\t' + '\t'.join(['0'] * 10) + '\n')
            prepare(root / 'input/assembly.fna', depth, root / 'old', config())
            features = root / 'old/features.npz'
            views = root / 'old/views.npz'
            members = {}
            for community in ['E009', 'oral']:
                bank = root / 'measurement-detail/work' / community
                paths = []
                for i, name in enumerate(names):
                    path = bank / ('sample-%02d' % i)
                    summarize(bam, features, views, path, name)
                    paths.append(path)
                    members[community + '/' + path.name + '/moments.npy'] = binding(path / 'moments.npy')
                seal(bank, features, views, paths)
                rebind(bank, features, views, bank / 'features.npz')
            control = root / 'control/measurements'
            control.mkdir(parents=True)
            (control / 'inventory.json').write_text(json.dumps(dict(all_work_members=members)))
            # External stream admission is a synthetic envelope here; complete
            # native archive streams are independently verified by the controller.
            proof = dict(every_member_verified=True, archive=dict(bytes=123, sha256='fixture'), generation='123')
            for name in ['measurement-detail-stream-proof.json', 'measurements-stream-proof.json']:
                (root / name).write_text(json.dumps(proof))
            result = audit(root, dict(E009=features, oral=features), root / 'review.json')
            self.assertFalse(result['scientific_comparison_admitted'])
            self.assertFalse(result['new_quality_scores'])
            for community in result['communities'].values():
                self.assertEqual(community['ordered_samples'], names)
                self.assertEqual(community['strata']['all']['new_measured_all_zero'], 1)
                self.assertEqual(community['counters']['accepted_reads'], 30)
            bank = root / 'measurement-detail/work/E009/bank.json'
            bad = json.loads(bank.read_text())
            bad['samples'].reverse()
            bank.write_text(json.dumps(bad))
            with self.assertRaisesRegex(ValueError, 'sample/bank binding'):
                audit(root, dict(E009=features, oral=features), root / 'bad-review.json')
            self.assertFalse((root / 'bad-review.json').exists())

    def test_filter_ledger_refuses_double_count_negative_and_impossible_HQ(self):
        good = dict(records=8, accepted_reads=3, excluded_flags=4, excluded_identity=1,
                    accepted_aligned_bases=450, high_MAPQ_aligned_bases=300)
        validate_counters(good)
        for key, value in [('records', 9), ('excluded_flags', -1), ('high_MAPQ_aligned_bases', 451)]:
            bad = dict(good, **{key: value})
            with self.assertRaises(ValueError):
                validate_counters(bad)

    def test_stopped_partial_return_cannot_enter_quality_review(self):
        from e022_review import admission_contract
        with tempfile.TemporaryDirectory() as folder:
            p = Path(folder) / 'admission.json'
            p.write_text(json.dumps(dict(provider_status='TERMINATED', archive_and_every_member_verified=True,
                                        cost_and_retention_admitted=True, workflow_completed=False)))
            with self.assertRaises(ValueError):
                admission_contract(p)

    def test_actual_immutable_publisher_refuses_long_disk_sample_history(self):
        # This demonstrates a source-bound failure mechanism, not the missing
        # native terminal exception. Preserve the actual 1 MiB publisher bound.
        sample = dict(monotonic=17000.123456789, epoch=1793822800.123456,
                      task_used=28000000000, task_free=77000000000, source_free=29453312000)
        completion = dict(status='FAILED', filesystem_samples=[sample] * 8300)
        self.assertGreater(len(json.dumps(completion, separators=(',', ':')).encode()), MAX_BYTES)
        with tempfile.TemporaryDirectory() as folder:
            p = Path(folder) / 'completion.json'
            with self.assertRaisesRegex(ValueError, 'bounded size'):
                publish(completion, p)
            self.assertEqual(list(p.parent.iterdir()), [])


if __name__ == '__main__':
    unittest.main()
