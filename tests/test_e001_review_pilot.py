"""Returned native-evidence audit and tamper rejection; no HPC fits are repeated."""
import csv
import json
from pathlib import Path
import sys
import tempfile
import unittest

REPO=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(REPO/'scripts'))
import e001_review_pilot as review


class ReviewPilotTests(unittest.TestCase):
    def test_return_and_corrupt_checksum(self):
        archive=REPO/'agent_context/paired-pilot-metabat-vamb-kru6t8dq-return.tar.gz'
        population=REPO/'artifacts/e001-population-reviewed'
        if not archive.exists() or not population.exists(): self.skipTest('Optional retained evidence missing')
        terminal=REPO/'agent_context/e001-pilot.PkrRsg.log'
        observed=review.review(archive,Path(str(archive)+'.sha256'),terminal,population)
        self.assertEqual(observed,review.read(review.EXP/'paired-pilot-observed.json'))
        with tempfile.TemporaryDirectory() as tmp:
            bad=Path(tmp)/'bad.sha256';bad.write_text('0'*64+'  '+archive.name)
            with self.assertRaisesRegex(ValueError,'checksum mismatch'): review.review(archive,bad,terminal,population)

    def test_amber_rejects_changed_winning_origin_and_missing_genome(self):
        with tempfile.TemporaryDirectory() as tmp:
            d=Path(tmp)
            (d/'amber-per-bin.tsv').write_text('total_length\ttotal_seq_counts\ttp_length\tgenome_id\tlength_gs\tprecision_bp\trecall_bp\n10\t1\t10\tg\t10\t1\t1\n')
            (d/'amber-per-genome.tsv').write_text('genome_id\tgenome_length\tlength_gs\trecall_bp\ng\t10\t10\t1\nh\t0\t20\t0\n')
            args=(d,{'a':'b'},{'a':10,'c':20},{'a':['g'],'c':['h']})
            self.assertEqual(review.check_amber(*args)['assigned_bp'],10)
            f=d/'amber-per-bin.tsv';original=f.read_text();f.write_text(original.replace('\tg\t','\th\t'))
            with self.assertRaisesRegex(ValueError,'dominant origin'): review.check_amber(*args)
            f.write_text(original)
            f=d/'amber-per-genome.tsv';f.write_text(f.read_text().replace('h\t0\t20\t0\n',''))
            with self.assertRaisesRegex(ValueError,'genome axis'):review.check_amber(*args)

if __name__=='__main__':unittest.main()
