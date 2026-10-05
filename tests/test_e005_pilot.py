"""Meaningful new pilot failures, deterministic pair selection and recovery boundaries."""
import hashlib
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'scripts'))
from e005_pilot import confirmed_recovery, parse_depth, sample_reads
from e005_smoke import sha
import e005_pilot_owner


def fastq(number, sample=1):
    """A complete anonymous pair with a valid 150-base DNA/quality contract."""
    return ''.join(f'@S{sample}R{number}/{mate}\n'+('ACGT'*38)[:150]+'\n+\n'+150*'I'+'\n' for mate in (1, 2))


class PilotTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(); self.root = Path(self.temp.name)

    def tearDown(self):
        self.temp.cleanup()

    def test_bottom_hash_exact_order_and_repeated_new_output(self):
        source = self.root/'source.fq'; source.write_text(''.join(fastq(n) for n in range(1, 30)))
        expected = sorted(range(1, 30), key=lambda n: (hashlib.sha256(f'E005-S1-pairs-v1:S1R{n}'.encode()).digest(), f'S1R{n}'))[:5]
        for name in ('first.fq', 'second.fq'):
            out = self.root/name; sample_reads(source, 1, sha(source), 5, 100, out)
            self.assertEqual(out.read_text(), ''.join(fastq(n) for n in sorted(expected)))
            self.assertEqual(json.loads(out.with_suffix('.sample.json').read_text())['selected_pairs'], 5)
        with self.assertRaises(FileExistsError):
            sample_reads(source, 1, sha(source), 5, 100, self.root/'first.fq')

    def test_invalid_fastq_sources_stop_before_success_receipt(self):
        for index, text in enumerate((fastq(1)+fastq(1), fastq(1)[:-5], fastq(1).replace('/2', '/1'),
                                      fastq(1).replace('I'*150, 'I'*149), fastq(1, sample=4))):
            source = self.root/f'in-{index}'; source.write_text(text)
            output = self.root/f'out-{index}.fq'
            with self.assertRaises(ValueError):
                sample_reads(source, 1, sha(source), 1, 100, output)
            self.assertFalse(output.with_suffix('.sample.json').exists())
        source = self.root/'valid'; source.write_text(fastq(1))
        for count, cap, digest in ((1,100,'0'*64), (2,100,sha(source)), (1,0,sha(source))):
            with self.assertRaises(ValueError):
                sample_reads(source, 1, digest, count, cap, self.root/f'bad-{count}-{cap}.fq')

    def test_shuffled_zero_padded_names_and_optional_plus_ids(self):
        source=self.root/'shuffled.fq'
        records=[fastq(n).replace(f'S1R{n}',f'S1R{n:03d}') for n in (5,2,9,1)]
        records=[text.replace('\n+\n','\n+'+text.splitlines()[0][1:]+'\n',1) for text in records]
        source.write_text(''.join(records))
        names=[text.splitlines()[0][1:-2] for text in records]
        chosen=set(sorted(names,key=lambda n:(hashlib.sha256(('E005-S1-pairs-v1:'+n).encode()).digest(),n))[:2])
        output=self.root/'selected.fq'; sample_reads(source,1,sha(source),2,100,output)
        self.assertEqual(output.read_text(),''.join(text for name,text in zip(names,records) if name in chosen))

    def test_native_stream_missing_duplicate_reordered_negative_extra_rejected(self):
        rows = [('a', 2), ('short_zero', 1)]
        good = b'a\t1\t3\na\t2\t0\nshort_zero\t1\t0\n'
        self.assertEqual(parse_depth(io.BytesIO(good), rows, hashlib.sha256()), [3, 0])
        for data in (good[:-5], good.replace(b'a\t2', b'a\t1'), good.replace(b'\t3\n', b'\t-1\n'),
                     good+b'unknown\t1\t0\n', good.replace(b'short_zero', b'unknown')):
            with self.assertRaises(ValueError):
                parse_depth(io.BytesIO(data), rows, hashlib.sha256())

    def test_r95_complete_short_denominator_purity_boundary_tie_empty_unknown(self):
        records = [dict(contig_id=i, bp=str(n), genome_id=g, confirmed_origin=c) for i,n,g,c in (
            ('a1',200000,'A','1'), ('a2',200000,'A','1'), ('short',199,'A','1'),
            ('b',200000,'B','1'), ('amb',10526,'A','0'))]
        x = confirmed_recovery(records, {'a1':'z', 'a2':'a', 'amb':'z'})
        self.assertEqual(x['per_genome']['A']['bin'], 'a')
        self.assertEqual(x['per_genome']['A']['total_bp'], 400199)
        self.assertEqual(x['per_genome']['A']['recovered_bp'], 200000)
        self.assertEqual(x['ambiguous_or_unscored_assigned_bp'], 10526)
        records[1]['confirmed_origin'] = '0'
        x = confirmed_recovery(records, {'a1':'z', 'amb':'z'})
        self.assertGreaterEqual(x['per_genome']['A']['confirmed_purity'], .95)
        records[-1]['bp'] = '10527'
        self.assertEqual(confirmed_recovery(records, {'a1':'z', 'amb':'z'})['r95'], 0)
        self.assertEqual(confirmed_recovery(records, {})['r95'], 0)
        with self.assertRaisesRegex(ValueError, 'unknown'):
            confirmed_recovery(records, {'not-in-reference':'x'})
        from e001lib.metrics import score as old_score
        population = dict(lengths={r['contig_id']:int(r['bp']) for r in records},
                          unique_origins={r['contig_id']:r['genome_id'] for r in records if r['confirmed_origin']=='1'}, genomes=['A','B'])
        assignments = {'a1':'z', 'amb':'z'}
        reference = old_score(population, assignments)
        actual = confirmed_recovery(records, assignments)
        for key in ('r95','r95_base_weighted','inclusive_recovered_counts','assigned_bp','unassigned_bp','ambiguous_or_unscored_assigned_bp'):
            self.assertEqual(actual[key], reference[key])

    def test_changed_rule_guard_really_fails_and_records_time_limit(self):
        cfg = self.root/'cfg.json'; cfg.write_text(json.dumps(dict(threads=4, rss_bytes=8_000_000_000, rule_receipts=str(self.root/'rules'))))
        base = [sys.executable, ROOT/'scripts/e005_rule.py', '--config', cfg]
        for name, ceiling, code in (('fatal',10,'raise OSError("fatal native contract")'), ('timeout',.3,'import time; time.sleep(30)')):
            result = subprocess.run([str(v) for v in base+['--name',name,'--seconds',ceiling,'--',sys.executable,'-c',code]], capture_output=True, text=True, timeout=10)
            self.assertNotEqual(result.returncode, 0)
            receipt = json.loads((self.root/'rules'/(name+'.json')).read_text())
            self.assertLess(receipt['wall_seconds'], 5)
            self.assertEqual(receipt['allocated_vcpus'], 4)
            if name == 'fatal':
                self.assertIsNone(receipt['stop_reason'])
                self.assertIn('fatal native contract', (self.root/'rules/fatal.log').read_text())
            else:
                self.assertIn('Stage time ceiling exceeded', receipt['stop_reason'])

    def test_owner_prerequisite_failure_keeps_manifest_and_transfer_return(self):
        bundle=self.root/'bundle'; (bundle/'experiments/E005-linux-pilot').mkdir(parents=True)
        (bundle/'experiments/E005-linux-pilot/pilot.json').write_text(json.dumps(dict(resources=dict(total_driver_seconds_ceiling=5))))
        (bundle/'bundle-manifest.json').write_text(json.dumps(dict(source_commit='0'*40,files={})))
        root=self.root/'owner'
        argv=['owner','--root',str(root),'--allocated-vcpus','5','--allocated-ram-gb','12']
        with patch.object(e005_pilot_owner,'BUNDLE',bundle), patch.object(sys,'argv',argv):
            self.assertEqual(e005_pilot_owner.main(),1)
        attempt=next(root.glob('gi-pilot-*'))
        status=json.loads((attempt/'status.json').read_text())
        self.assertIn('4-vCPU',status['error'])
        self.assertTrue((attempt/'bundle-manifest.json').is_file())
        self.assertEqual(len(list((root/'transfer').glob('*-return.tar.gz'))),1)
        self.assertFalse((attempt/'pilot/checkpoint.pt').exists())


if __name__ == '__main__':
    unittest.main()
