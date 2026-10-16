"""Check full-axis feature review refuses reordered, missing and altered data."""
import importlib.util
from pathlib import Path
import tempfile
import unittest

spec=importlib.util.spec_from_file_location('e009_data_acceptance',Path(__file__).resolve().parents[1]/'scripts/e009_data_acceptance.py')
mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)


class AcceptanceTests(unittest.TestCase):
    def test_full_fasta_axis_and_duplicate_refusal(self):
        with tempfile.TemporaryDirectory()as tmp:
            path=Path(tmp)/'dna.fa';path.write_text('>short\nAC\n>long\nACGT\nACGT\n')
            self.assertEqual(mod.fasta_axis(path),[('short',2),('long',8)])
            path.write_text('>short\nAC\n>short\nAC\n')
            with self.assertRaisesRegex(ValueError,'Duplicate'):mod.fasta_axis(path)

    def test_depth_and_matrix_exact_axes_and_values(self):
        with tempfile.TemporaryDirectory()as tmp:
            path=Path(tmp)/'depth.tsv';axis=[('short',2),('long',8)]
            path.write_text('contig_id\tS0\nshort\t0\nlong\t1.25\n')
            values=mod.depth_values(path,axis,'S0');self.assertEqual(values,[0,1.25])
            path.write_text('contig_id\tS0\nlong\t0\nshort\t1.25\n')
            with self.assertRaisesRegex(ValueError,'contig axis'):mod.depth_values(path,axis,'S0')
            path.write_text('contig_id\tS0\nshort\tnan\nlong\t1.25\n')
            with self.assertRaisesRegex(ValueError,'Invalid depth'):mod.depth_values(path,axis,'S0')
            path.write_text('contig_id\tS0\tS2\nshort\t0\t2\nlong\t1.25\t0\n')
            mod.check_matrix(path,axis,['S0','S2'],[values,[2,0]])
            with self.assertRaisesRegex(ValueError,'sample axis'):mod.check_matrix(path,axis,['S2','S0'],[values,[2,0]])
            with self.assertRaisesRegex(ValueError,'measured depths'):mod.check_matrix(path,axis,['S0','S2'],[values,[3,0]])


if __name__=='__main__':unittest.main()
