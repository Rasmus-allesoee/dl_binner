"""Real native-format FASTA/assignment fixtures for isolated reference admission."""
import hashlib
import json
from pathlib import Path
import sys
import tarfile
import tempfile
import unittest

import numpy as np

sys.path.insert(0, str(Path(__file__).absolute().parents[1]/'scripts'))
from e027_reference import export
from e024_control import seal
from e024_coverage import binding
from e027_reference_review import dna_contract, fasta_stream


class NativeReferenceReview(unittest.TestCase):
    """Do not trust an exit code without every contig's DNA and assignment axis."""

    def fixture(self, root):
        """Create real DNA and native-format outputs, without another tool fit."""
        seq = ['ACGT'*50003, 'A'*1100, 'C'*500]
        ids = ['opaque-A', 'opaque-B', 'opaque-C']
        fasta = root/'original.fna'
        fasta.write_text(''.join('>'+q+'\n'+s+'\n' for q, s in zip(ids, seq)))
        ref = root/'staged/work/reference'; native = ref/'native'; native.mkdir(parents=True)
        (native/'bin.1.fa').write_text('>'+ids[0]+'\n'+seq[0]+'\n')
        export(fasta, native, ref/'export'); seal(ref)
        inventory = dict(all_work_members={'reference/'+str(p.relative_to(ref)): binding(p)
                                          for p in ref.rglob('*') if p.is_file()})
        archive = root/'actual.tar.gz'
        with tarfile.open(archive, 'w:gz') as out:
            for p in ref.rglob('*'):
                if p.is_file(): out.add(p, arcname='work/reference/'+str(p.relative_to(ref)), recursive=False)
        data = dict(ids=np.asarray(ids), lengths=np.asarray(list(map(len, seq))),
                    sequence_sha256=np.asarray([hashlib.sha256(s.encode()).hexdigest() for s in seq]))
        return archive, inventory, data, root/'staged'

    def test_actual_native_DNA_all_statuses_and_source_blind_IDs(self):
        with tempfile.TemporaryDirectory() as t:
            archive, inv, data, staged = self.fixture(Path(t))
            labels, proof = dna_contract(archive, inv, data, staged)
            self.assertEqual(labels.tolist(), [0, -1, -1])
            self.assertEqual(proof['statuses']['assigned']['bp'], 200012)
            self.assertEqual(proof['statuses']['unassigned']['bp'], 1100)
            self.assertEqual(proof['statuses']['excluded']['bp'], 500)
            self.assertTrue(proof['native_DNA_reverified'])

    def test_changed_parent_DNA_refused(self):
        with tempfile.TemporaryDirectory() as t:
            archive, inv, data, staged = self.fixture(Path(t))
            data['sequence_sha256'][0] = '0'*64
            with self.assertRaises(ValueError): dna_contract(archive, inv, data, staged)

    def test_reordered_or_extra_assignment_refused(self):
        with tempfile.TemporaryDirectory() as t:
            archive, inv, data, staged = self.fixture(Path(t))
            table = staged/'work/reference/export/assignments.tsv'
            rows = table.read_text().splitlines(); rows[1], rows[2] = rows[2], rows[1]
            table.write_text('\n'.join(rows)+'\n')
            with self.assertRaises(ValueError): dna_contract(archive, inv, data, staged)


if __name__ == '__main__':
    unittest.main()
