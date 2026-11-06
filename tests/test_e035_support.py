"""Refuse source/axis/envelope drift before a retained-BAM consumer can run."""
import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

ROOT=Path(__file__).absolute().parents[1]
spec=importlib.util.spec_from_file_location('e035_support',ROOT/'scripts/e035_support.py')
support=importlib.util.module_from_spec(spec);spec.loader.exec_module(support)


class PooledPlan(unittest.TestCase):
    def setUp(self):
        self.original=json.loads((ROOT/'experiments/E035-confidence-taxonomy/pooled-audit-plan.json').read_text())

    def read(self,value):
        """Exercise the real consumer parser through an independent JSON file."""
        with tempfile.TemporaryDirectory()as folder:
            p=Path(folder)/'plan.json';p.write_text(json.dumps(value));return support.plan(p)

    def test_only_restore_location_and_new_work_directory_may_change(self):
        p=copy.deepcopy(self.original);p['work']='/new/task/support'
        p['BAMs']['oral'][0]['local']='/new/verified/one-BAM.bam'
        self.assertEqual(self.read(p),p)

    def test_valid_but_different_BAM_bytes_or_sample_order_are_refused(self):
        for mutation in ['bytes','order','generation']:
            p=copy.deepcopy(self.original)
            if mutation=='bytes':p['BAMs']['oral'][0]['sha256']='0'*64
            elif mutation=='order':p['BAMs']['oral'][0],p['BAMs']['oral'][1]=p['BAMs']['oral'][1],p['BAMs']['oral'][0]
            else:p['BAMs']['oral'][0]['generation']='unadmitted'
            with self.assertRaisesRegex(ValueError,'Frozen ordered'):self.read(p)

    def test_feature_or_envelope_drift_is_refused_before_any_BAM_open(self):
        for field in ['features','limits']:
            p=copy.deepcopy(self.original)
            if field=='features':p['features']['oral']='/another/community/features.npz'
            else:p['limits']['seconds']+=1
            with self.assertRaisesRegex(ValueError,'Frozen feature'):self.read(p)


if __name__=='__main__':unittest.main()
