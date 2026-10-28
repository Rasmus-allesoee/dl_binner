"""Real archived-schema checks for the E024 failure/data inspection consumer."""
import copy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from e024_inspect_data import Retained, acquired_contract, binding


class Inspection(unittest.TestCase):
    def test_streamed_binding_on_retained_runtime(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'bytes';p.write_bytes(b'actual fixture')
            self.assertEqual(binding(p),dict(bytes=14,sha256=hashlib.sha256(b'actual fixture').hexdigest()))

    def test_actual_exact_byte_alias_resolution_and_bad_binding_refusal(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);(root/'canonical.json').write_text('{"status":"PASS"}')
            b=dict(bytes=17,sha256='fixture')
            inv=dict(members={'canonical.json':b},aliases={'logical.json':dict(b,canonical='canonical.json')})
            self.assertEqual(Retained(root,inv).read('logical.json'),{'status':'PASS'})
            inv['aliases']['logical.json']['bytes']=18
            with self.assertRaisesRegex(ValueError,'Alias content binding'):
                Retained(root,inv).path('logical.json')
            with self.assertRaisesRegex(ValueError,'Missing retained'):
                Retained(root,inv).path('absent')

    def test_segment_aggregate_is_distinct_from_full_file_MD5(self):
        segments=[dict(bytes=2,md5=hashlib.md5(b'ab').hexdigest()),dict(bytes=1,md5=hashlib.md5(b'c').hexdigest())]
        expected=dict(sample=6,bytes=3,segments=segments,DLO_aggregate_md5=hashlib.md5(''.join(s['md5'] for s in segments).encode()).hexdigest())
        record=dict(sample=6,bytes=3,manifest=expected,publisher_segment_MD5_passed=2,sha256=hashlib.sha256(b'abc').hexdigest(),calculated_whole_MD5=hashlib.md5(b'abc').hexdigest())
        acquired_contract(record,expected)
        self.assertNotEqual(record['calculated_whole_MD5'],expected['DLO_aggregate_md5'])
        bad=copy.deepcopy(record);bad['publisher_segment_MD5_passed']=1
        with self.assertRaisesRegex(ValueError,'Acquisition receipt'):
            acquired_contract(bad,expected)

    def test_success_seal_must_account_for_every_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);p=root/'work/stage';p.mkdir(parents=True)
            expected=dict(bytes=2,sha256='fixture')
            (p/'done.json').write_text(json.dumps(dict(status='PASS',files={'a':expected})))
            inv=dict(members={'work/stage/done.json':{}},aliases={},all_work_members={'stage/a':expected})
            self.assertEqual(Retained(root,inv).seal('stage')['status'],'PASS')
            inv['all_work_members']['stage/a']=dict(bytes=3,sha256='fixture')
            with self.assertRaisesRegex(ValueError,'Sealed output binding'):
                Retained(root,inv).seal('stage')
