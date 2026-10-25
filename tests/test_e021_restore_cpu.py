"""Real tiny transport/hardlink contracts for restore-only CPU recovery."""
import hashlib
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT=Path(__file__).absolute().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from e021_portable_transport import send,receive,binding,paired
from e021_restore_cpu import admit_transport,restore_links,tasks,STAGES
from e021_portable_node import completed_E009


class RestoreOnlyContracts(unittest.TestCase):
    def test_real_receiver_pairing_hardlinks_and_unchanged_old_receipt(self):
        with tempfile.TemporaryDirectory()as d:
            r=Path(d);original=r/'original';original.write_bytes(b'actual native-style bank fixture'*171)
            manifest=dict(kind='E021 verified transport v1',files={'frozen/vectors.npy':dict(source=str(original),**binding(original))})
            stream=io.BytesIO();sender=send(manifest,stream);receiver=receive(manifest,io.BytesIO(stream.getvalue()),r/'retained')
            raw=json.dumps(receiver);wire=dict(bytes=len(stream.getvalue()),sha256=hashlib.sha256(stream.getvalue()).hexdigest())
            ledger=dict(status='PASS',sender=sender,receiver=receiver,stream=wire,pairing=paired(sender,receiver,wire))
            proof=admit_transport(manifest,ledger,receiver,r/'retained')
            self.assertFalse(proof['consumer_admitted']);self.assertEqual(json.dumps(receiver),raw)
            result=restore_links(r/'retained',r/'new-work',proof['members'])
            self.assertEqual(result['frozen/vectors.npy'],binding(original))
            self.assertEqual((r/'retained/frozen/vectors.npy').stat().st_ino,(r/'new-work/frozen/vectors.npy').stat().st_ino)
            with self.assertRaises(FileExistsError):restore_links(r/'retained',r/'new-work',proof['members'])
            (r/'retained/frozen/vectors.npy').write_bytes(b'corrupt')
            with self.assertRaisesRegex(ValueError,'member differs'):admit_transport(manifest,ledger,receiver,r/'retained')
            self.assertEqual(original.read_bytes(),b'actual native-style bank fixture'*171)

    def test_unexpected_scientific_output_refuses_fresh_fit(self):
        with tempfile.TemporaryDirectory()as d:
            r=Path(d);s=r/'old';s.mkdir();(s/'bank').write_bytes(b'accepted bank');b=binding(s/'bank');(s/'checkpoint.pt').write_bytes(b'possible completed fit')
            with self.assertRaisesRegex(ValueError,'possible completed science'):restore_links(s,r/'new',{'bank':b})
            self.assertFalse((r/'new').exists())

    def test_closed_queue_has_no_extraction_install_or_old_baseline_stage(self):
        cfg=dict(root='/fresh',repo='/exact-source',runtime_prefix='/accepted-prefix')
        rows=tasks(cfg);self.assertEqual(len(rows),10)
        science=[x for x in rows if x['kind']=='science']
        self.assertEqual([x['stage']for x in science],STAGES)
        self.assertTrue(all(x['unit']=='E009-hybrid'for x in science))
        self.assertTrue(all('--engineering'not in x['argv']for x in rows))
        self.assertNotIn('extract',[x.get('stage')for x in rows])
        self.assertIn('cpu-target',rows[-1]['argv'])

    def test_scope_boolean_requires_all_six_exits_and_the_actual_target(self):
        with tempfile.TemporaryDirectory()as d:
            r=Path(d);(r/'gates').mkdir();(r/'gates/E009-scoped-target.json').write_text(json.dumps(dict(status='PASS_E009_ONLY_COMPLETE')))
            cfg=dict(root=str(r),role='cpu',scope='E009-only')
            rows=[dict(kind='science',unit='E009-hybrid',stage=s,status='SUCCESS')for s in STAGES]
            self.assertTrue(completed_E009(cfg,dict(stages=rows)))
            for bad in [rows[:-1],rows+[rows[0]],rows+[dict(kind='science',unit='oral-hybrid',stage='train',status='SUCCESS')]]:
                with self.assertRaisesRegex(ValueError,'not proved'):completed_E009(cfg,dict(stages=bad))


if __name__=='__main__':unittest.main()
