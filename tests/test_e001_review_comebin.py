"""Real returned-evidence audit plus schedule/selection corruption checks."""
from pathlib import Path
import sys
import tempfile
import unittest

REPO=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(REPO/'scripts'))
import e001_review_comebin as review


class ComebinReviewTests(unittest.TestCase):
    def test_real_return(self):
        archive=REPO/'agent_context/paired-pilot-comebin-istuh_2t-resume-fe7ig32w-return.tar.gz'
        pop=REPO/'artifacts/e001-population-reviewed'
        if not archive.exists() or not pop.exists(): self.skipTest('Optional owner evidence absent')
        observed=review.review(archive,Path(str(archive)+'.sha256'),REPO/'agent_context/e001-pilot-resume.K9rPwO.log',pop)
        self.assertEqual(observed,review.read(review.EXP/'comebin-paired-observed.json'))

    def test_schedule_rejects_missing_epoch_and_premature_stop(self):
        suffix='Final inference: published complete binary embedding bundle; contigs=22594.\nFinish training.'
        lines=[f'NN training: epoch={n}/200, batches=22, loss=0.3, top1={100 if n>=11 else 90}, elapsed=1.0s\n' for n in range(1,14)]
        self.assertEqual(review.native_schedule(''.join(lines)+suffix)['epochs'],13)
        with self.assertRaisesRegex(ValueError,'Noncontiguous'): review.native_schedule(''.join(lines[1:])+suffix)
        with self.assertRaisesRegex(ValueError,'early-stop'): review.native_schedule(''.join(lines[:-1])+suffix)

    def test_marker_grid_ties_and_corruption(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'estimate.tsv'; names=sorted(review.candidate_names())
            text='Binning_method\tnum_5010\tnum_7010\tnum_9010\tnum_505\tnum_705\tnum_905\tsum\tsum_cont5\n'+''.join(n+'\t1\t1\t1\t1\t1\t1\t6\t3\n' for n in names)
            p.write_text(text); self.assertEqual(review.marker_selection(p,names[0])['candidate_rows'],120)
            with self.assertRaisesRegex(ValueError,'winner'): review.marker_selection(p,names[-1])
            p.write_text(text.replace('\t6\t3','\t7\t3',1))
            with self.assertRaisesRegex(ValueError,'sum mismatch'): review.marker_selection(p,names[0])
            p.write_text('\n'.join(text.splitlines()[:-1]))
            with self.assertRaisesRegex(ValueError,'Incomplete'): review.marker_selection(p,names[0])
