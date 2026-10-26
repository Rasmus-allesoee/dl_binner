"""Actual retained-FASTA contract refusals; no binner, RNA or community fixture."""
from pathlib import Path
import hashlib
import tempfile
import unittest
import sys
sys.path.insert(0,str(Path(__file__).absolute().parents[1]/'scripts'))
from e023_metabat_secondary import fasta_contract

class FASTAContract(unittest.TestCase):
    def test_real_reader_membership_original_bytes_and_duplicate_refusal(self):
        with tempfile.TemporaryDirectory()as d:
            p=Path(d)/'bin.fna';p.write_text('>opaque comment\nACGT\n')
            source={'opaque':(4,hashlib.sha256(b'ACGT').hexdigest())};seen=set()
            self.assertEqual(fasta_contract(p,{'opaque'},source,seen)['bp'],4)
            with self.assertRaisesRegex(ValueError,'duplicate'):fasta_contract(p,{'opaque'},source,seen)
            with self.assertRaisesRegex(ValueError,'omitted'):fasta_contract(p,{'opaque','missing'},source,set())
            p.write_text('>opaque\nAGGT\n')
            with self.assertRaisesRegex(ValueError,'original DNA'):fasta_contract(p,{'opaque'},source,set())

if __name__=='__main__':unittest.main()
