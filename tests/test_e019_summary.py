"""Exact frozen E019 decision boundary, independent of any community outcome."""
from pathlib import Path
import sys
import unittest
import tempfile
import json
sys.path.insert(0,str(Path(__file__).absolute().parents[1]/'scripts'))
from e019_summarize import disposition,compact_verification,binding

class FrozenRule(unittest.TestCase):
    def row(self,delta,count=0):
        return dict(candidate_bp=100+delta,baseline_bp=100,reference_bp=1000,candidate_90=4+count,baseline_90=4)
    def test_exact_half_percentage_point_both_and_counts(self):
        self.assertEqual(disposition([self.row(5),self.row(5)]),'KEEP')
        self.assertEqual(disposition([self.row(5),self.row(4)]),'MODIFY')
        self.assertEqual(disposition([self.row(5),self.row(5,-1)]),'MODIFY')
    def test_abandon_or_count_only_modify_without_grid(self):
        self.assertEqual(disposition([self.row(0),self.row(-1)]),'ABANDON')
        self.assertEqual(disposition([self.row(-1,1),self.row(-1)]),'MODIFY')
        self.assertEqual(disposition([self.row(0),self.row(1)]),'MODIFY')
    def test_compact_inventory_binds_all_omissions_without_repeating_hash_rows(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'proof.json'
            value=dict(status='SUCCESS',every_member_verified=True,archive={'bytes':1},
                regular_members=3,logical_member_bytes=9,aliases={},
                omitted_retained_on_disk={'DNA':{'bytes':7,'sha256':'x','reason':'on VM'}})
            p.write_text(json.dumps(value));out=compact_verification(p)
            self.assertEqual(out['omitted_member_count'],1)
            self.assertEqual(out['omitted_bytes'],7)
            self.assertEqual(out['full_verification'],binding(p))
            self.assertNotIn('omitted_retained_on_disk',out)
            value['every_member_verified']=False;p.write_text(json.dumps(value))
            with self.assertRaises(ValueError):compact_verification(p)
    def test_malformed_axes_and_denominators_refused(self):
        for rows in [[],[self.row(5)], [self.row(5)|{'reference_bp':0},self.row(5)], [self.row(5)|{'candidate_bp':1001},self.row(5)]]:
            with self.assertRaises(ValueError):disposition(rows)

if __name__=='__main__':unittest.main()
