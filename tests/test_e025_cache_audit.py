"""Equivalent complete reader/refinement checks after hoisting a repeated set."""
import json
from pathlib import Path
import tempfile
import unittest

from e024_information import audit as original
from e025_cache_audit import audit as faster
from e025_information import run
from e024_coverage import binding
from test_e025_retrieval import retained,CFG


class CacheAudit(unittest.TestCase):
    def test_identical_actual_reader_proof_and_malformed_choices_refusal(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);u,receipt=retained(root)
            out=root/'group';run(receipt,u['graph'],u['marker_evidence'],out,CFG)
            paths=[p for p in root.rglob('*') if p.is_file()]
            before={str(p):binding(p) for p in paths}
            self.assertEqual(original(receipt,u['graph'],u['marker_evidence'],out,CFG),
                             faster(receipt,u['graph'],u['marker_evidence'],out,CFG))
            self.assertEqual(before,{str(p):binding(p) for p in paths})
            choices=out/'selected-choices.json';choices.write_text('[{"forged":true}]')
            for checker in [original,faster]:
                with self.assertRaisesRegex(ValueError,'Cached marker choices differ'):
                    checker(receipt,u['graph'],u['marker_evidence'],out,CFG)


if __name__=='__main__':unittest.main()
