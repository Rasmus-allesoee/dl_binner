"""Independent return-review failures and conservative recovery boundaries."""
import csv
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('pilot_review', ROOT/'experiments/E005-linux-pilot/review_pilot.py')
review = importlib.util.module_from_spec(spec)
spec.loader.exec_module(review)


class PilotReviewTests(unittest.TestCase):
    def test_production_scheduler_options_reject_invalid_allocations(self):
        import sys
        sys.path.insert(0, str(ROOT/'scripts'))
        from e005_owner import local_scheduler_options
        for threads, ram in ((0,8000),(5,8000),(4,0)):
            with self.assertRaisesRegex(ValueError, 'budget'):
                local_scheduler_options(threads,ram)

    def test_return_inventory_detects_corruption_unknown_files_and_unsafe_omission(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder); artifact = root/'data.tsv'; artifact.write_text('data\n')
            (root/'terminal.log').write_text('completed\n')
            entry = dict(path='data.tsv', bytes=artifact.stat().st_size, sha256=review.digest(artifact), in_return=True)
            (root/'retained-files.json').write_text(json.dumps(dict(files=[entry])))
            self.assertEqual(review.inventory(root)['verified_returned_files'], 1)
            artifact.write_text('oops\n')
            with self.assertRaisesRegex(ValueError, 'bytes mismatch'):
                review.inventory(root)
            artifact.write_text('data\n'); (root/'surprise').write_text('unreviewed')
            with self.assertRaisesRegex(ValueError, 'Uninventoried'):
                review.inventory(root)
            (root/'surprise').unlink()
            (root/'retained-files.json').write_text(json.dumps(dict(files=[entry, dict(path='../escaped.bam', in_return=False)])))
            with self.assertRaisesRegex(ValueError, 'escapes'):
                review.inventory(root)

    def test_confirmed_purity_boundary_and_short_full_denominator(self):
        records = [dict(contig_id=i, bp=str(n), genome_id=g, confirmed_origin=c) for i,n,g,c in (
            ('a',200000,'A','1'), ('short',199,'A','1'),
            ('b',200000,'B','1'), ('amb',10526,'A','0'))]
        result = review.count_quality(records, {'a':'x','amb':'x'})
        self.assertEqual(result['per_genome']['A']['total_bp'], 200199)
        self.assertEqual(result['per_genome']['A']['recovered_bp'], 200000)
        self.assertEqual(result['ambiguous_or_unscored_assigned_bp'], 10526)
        self.assertEqual(result['inclusive_recovered_counts'], {'0.5':1,'0.9':1})
        records[-1]['bp'] = '10527'
        self.assertEqual(review.count_quality(records, {'a':'x','amb':'x'})['r95'], 0)
        self.assertEqual(review.count_quality(records, {})['r95'], 0)
        with self.assertRaisesRegex(ValueError, 'unknown'):
            review.count_quality(records, {'unknown':'x'})

    def test_fragmented_recovery_selects_one_bin_with_deterministic_tie(self):
        records = [dict(contig_id=i, bp=str(n), genome_id='A', confirmed_origin='1')
                   for i,n in [('a',200000),('b',200000),('short',199)]]
        result = review.count_quality(records, {'a':'z','b':'a'})['per_genome']['A']
        self.assertEqual(result['qualifying_bins'], 2)
        self.assertEqual(result['bin'], 'a')
        self.assertEqual(result['recovered_bp'], 200000)
        self.assertLess(result['r95'], .5)

    def test_amber_tables_are_recounted_and_corruption_is_rejected(self):
        records = [dict(contig_id=i, bp=str(n), genome_id=g, confirmed_origin='1')
                   for i,n,g in [('a',200000,'A'),('b',200000,'A'),('short',199,'A'),('c',300000,'B')]]
        assignments = {'a':'x','b':'y','c':'x'}
        bins = []
        for group, genome, total, count, tp, tp_count, gs, gs_count in (
            ('x','B',500000,2,300000,1,300000,1), ('y','A',200000,1,200000,1,400199,3)):
            bins.append(dict(BINID=group,genome_id=genome,total_length=total,total_seq_counts=count,
                tp_length=tp,tp_seq_counts=tp_count,length_gs=gs,seq_counts_gs=gs_count,
                precision_bp=tp/total,precision_seq=tp_count/count,recall_bp=tp/gs,
                recall_seq=tp_count/gs_count,seq_length_mean=total/count))
        recalls = [dict(BINID=group,genome_id=genome,genome_length=bp,genome_seq_counts=1,
                        length_gs=gs,seq_counts_gs=count,recall_bp=bp/gs,recall_seq=1/count,total_length=total)
                   for group,genome,bp,gs,count,total in [('x','A',200000,400199,3,500000),('x','B',300000,300000,1,500000)]]
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            def publish(name, rows):
                with (root/name).open('w') as stream:
                    writer = csv.DictWriter(stream, fieldnames=list(rows[0]), delimiter='\t')
                    writer.writeheader(); writer.writerows(rows)
            publish('amber-per-bin.tsv', bins); publish('amber-per-genome.tsv', recalls)
            result = review.inspect_amber(root, records, assignments)
            self.assertEqual(result['bins'], 2); self.assertEqual(result['genomes'], 2)
            bins[0]['precision_bp'] = .99
            publish('amber-per-bin.tsv', bins)
            with self.assertRaises(AssertionError):
                review.inspect_amber(root, records, assignments)


if __name__ == '__main__':
    unittest.main()
