"""Refuse false native exits, generation substitutions and unsealed members."""
import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT=Path(__file__).absolute().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from e033_completed_inspection import exits,archive
from e027_inspection import seal_from_inventory

PRIVATE=ROOT/'artifacts/e033-multiscale-bam/completed-inspection-20261105'

@unittest.skipUnless((PRIVATE/'native-admission.json').is_file(),
    'Requires the checksum-verified private E033 return; never acquire it in CI')
class CompletedInspection(unittest.TestCase):
    def test_actual_native_sequence_and_failed_or_missing_exit_refusal(self):
        path=ROOT/'artifacts/e033-multiscale-bam/completed-inspection-20261105/receipts/completion.json'
        record=json.loads(path.read_text());self.assertEqual(len(exits(record)),11)
        bad=copy.deepcopy(record);bad['stages'][6]['resources']['exit_code']=1
        with self.assertRaisesRegex(ValueError,'exit failed'):exits(bad)
        bad=copy.deepcopy(record);bad['stages'].pop()
        with self.assertRaisesRegex(ValueError,'sequence'):exits(bad)

    def test_actual_verified_archive_generation_and_alias_count_are_bound(self):
        source=ROOT/'artifacts/e033-multiscale-bam/completed-inspection-20261105'
        record=json.loads((source/'receipts/completion.json').read_text())
        expected=next(x for x in record['collections'] if x['label']=='E009-noGLM')['delivered']['e033-evidence.tar.gz']
        proof,inv=archive(source,'E009-noGLM',expected)
        self.assertTrue(proof['every_member_verified'])
        with self.assertRaisesRegex(ValueError,'generation'):archive(source,'E009-noGLM',dict(expected,generation='1'))
        with tempfile.TemporaryDirectory() as folder:
            base=Path(folder);(base/'receipts/E009-noGLM').mkdir(parents=True)
            (base/'receipts/E009-noGLM/inventory.json').write_text(json.dumps(inv))
            bad=copy.deepcopy(proof);bad['aliases']+=1
            (base/'E009-noGLM-verification.json').write_text(json.dumps(bad))
            with self.assertRaisesRegex(ValueError,'alias'):archive(base,'E009-noGLM',expected)

    def test_real_inventory_seal_closes_and_refuses_omitted_or_extra_bytes(self):
        source=ROOT/'artifacts/e033-multiscale-bam/completed-inspection-20261105'
        inv=json.loads((source/'receipts/E009-noGLM/inventory.json').read_text())
        seal=json.loads((source/'verified-E009-noGLM/work/student/done.json').read_text())
        self.assertEqual(seal_from_inventory(seal,'student',inv)['status'],'PASS')
        bad=copy.deepcopy(inv);bad['all_work_members'].pop('student/result/checkpoint.pt')
        with self.assertRaisesRegex(ValueError,'inventory differs'):seal_from_inventory(seal,'student',bad)
        bad=copy.deepcopy(inv);bad['all_work_members']['student/UNSEALED']={'bytes':0,'sha256':'0'*64}
        with self.assertRaisesRegex(ValueError,'extra/missing'):seal_from_inventory(seal,'student',bad)


class PortableExitContract(unittest.TestCase):
    def test_complete_delivery_sequence_and_missing_collection_refusal(self):
        """A successful science exit cannot substitute for closed collection exits."""
        stages=['original-inputs-before','repaired-package-install','repaired-complete-runtime',
            'repaired-plan','actual-progress-64-and-learning','actual-repaired-serial-tiny',
            'serial-six-fit-three-mode','original-inputs-after','collect-E009-noGLM',
            'collect-E009-GLM','collect-oral-noGLM']
        receipt=dict(stages=[dict(stage=s,resources=dict(exit_code=0,stop_reason=None)) for s in stages])
        self.assertEqual(set(exits(receipt)),set(stages))
        receipt['stages'].pop()
        with self.assertRaisesRegex(ValueError,'sequence'):exits(receipt)


if __name__=='__main__':unittest.main()
