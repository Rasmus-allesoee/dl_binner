"""Portable D011 guard/cache/chunk tests; native model contracts run in the spike."""
import json
from pathlib import Path
import sys
import tempfile
import time
import unittest

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import dnabert_s_cpu_spike as spike


class SpikeTests(unittest.TestCase):
    def test_chunk_coverage_strand_and_asymmetric_token_limits(self):
        def tokenizer(seq, **kwargs):
            # Stand-in tests this splitting algorithm, not the native extractor.
            return {'input_ids': list(range(2 + len(seq) * (2 if 'T' in seq else 1)))}
        seq = 'AACGACGAACA'
        chunks = spike.bounded_chunks(seq, tokenizer, 6, 7)
        reverse = spike.bounded_chunks(spike.reverse_complement(seq), tokenizer, 6, 7)
        self.assertEqual(chunks, reverse)
        self.assertEqual(''.join(r[2] for r in chunks), min(seq, spike.reverse_complement(seq)))
        self.assertEqual(sum(b-a for a,b,_,_ in chunks), len(seq))
        self.assertTrue(all(n <= 7 for _,_,_,n in chunks))
        self.assertEqual(chunks[-1][1], len(seq))

    def test_invalid_dna_and_limits(self):
        for seq in ['', 'ACGX']:
            with self.assertRaises(ValueError):
                spike.validate_dna(seq)
        self.assertEqual(spike.reverse_complement('acgtn'), 'NACGT')
        with self.assertRaises(ValueError):
            spike.bounded_chunks('A', lambda x:None, 0, 4)

    def test_fasta_duplicate_and_missing_header(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp)/'input.fa'
            for content in ['>a\nACG\n>a\nAAA\n', 'AAA\n']:
                path.write_text(content)
                with self.assertRaises(ValueError):
                    list(spike.fasta(path))

    def test_cache_order_dna_model_and_bytes(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp)/'features.npz'
            rows = [('a','ACG'),('b','ACT')]
            pin = {'files':{'weights':'hash'}, 'revision':'revision'}
            binding = spike.bind_cache(rows,pin,{'pool':'masked'})
            x = np.ones((2,768),dtype=np.float32)
            spike.save_cache(path,x,binding)
            np.testing.assert_array_equal(spike.load_cache(path,binding),x)
            for changed in [list(reversed(rows)), [('a','AAA'),rows[1]]]:
                with self.assertRaises(ValueError):
                    spike.load_cache(path,spike.bind_cache(changed,pin,{'pool':'masked'}))
            changed_pin = {**pin,'revision':'other'}
            with self.assertRaises(ValueError):
                spike.load_cache(path,spike.bind_cache(rows,changed_pin,{'pool':'masked'}))
            with path.open('ab') as f:
                f.write(b'corrupt')
            with self.assertRaises(ValueError):
                spike.load_cache(path,binding)

    def test_supervisor_fatal_exit_and_orphan_cleanup(self):
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)/'run'
            child_file = Path(tmp)/'child.pid'
            code = ('import subprocess,sys; p=subprocess.Popen([sys.executable,"-c",'
                    '"import time; time.sleep(120)"]); '
                    f'open({str(child_file)!r},"w").write(str(p.pid)); '
                    'raise RuntimeError("intentional guard test")')
            start = time.monotonic()
            status = spike.supervise([sys.executable,'-c',code],directory,10,500_000_000)
            self.assertNotEqual(status['exit_code'],0)
            self.assertLess(time.monotonic()-start,6)
            import psutil
            pid = int(child_file.read_text())
            self.assertTrue(not psutil.pid_exists(pid) or psutil.Process(pid).status()==psutil.STATUS_ZOMBIE)
            self.assertIn('intentional guard test',(directory/'terminal.log').read_text())

    def test_supervisor_time_and_ram_ceilings(self):
        with tempfile.TemporaryDirectory() as tmp:
            for name,seconds,rss in [('time',.3,500_000_000),('ram',5,1)]:
                status = spike.supervise([sys.executable,'-c','import time; time.sleep(120)'],
                                         Path(tmp)/name,seconds,rss)
                self.assertEqual(status['stop_reason'], 'Time ceiling' if name=='time' else 'RAM ceiling')
                self.assertNotEqual(status['exit_code'],0)


if __name__ == '__main__':
    unittest.main()
