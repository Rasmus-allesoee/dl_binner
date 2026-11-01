"""Real private-evidence restoration and refusal contracts for read-only review."""
from pathlib import Path
import io,json,sys,tarfile,tempfile,unittest
ROOT=Path(__file__).absolute().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import e030_diagnostics as d
from e024_coverage import binding

class DiagnosticsContracts(unittest.TestCase):
    def test_original_clock_not_reset(self):
        c=dict(original_start_epoch=d.START,science_source=d.SCIENCE,review_deadline_epoch=d.START+10000,provider_deadline_epoch=d.START+11000,incremental_ceiling_USD=3,numerical_threads=4,review_RSS_bytes=8_000_000_000,complete_cost_USD_upper=2.52,credit_only_admitted=True)
        self.assertTrue(d.check_config(c,d.START+9000))
        for change in [dict(original_start_epoch=d.START+1),dict(review_deadline_epoch=d.DEADLINE+1),dict(complete_cost_USD_upper=3.01),dict(credit_only_admitted=False)]:
            with self.assertRaises(ValueError):d.check_config(dict(c,**change),d.START+9000)

    def packet(self,root,name='artifacts/truth.json',bad=False):
        source=root/'truth';source.write_text('{"truth_only":true}\n');inv={name:binding(source)};packet=root/'input.tar.gz'
        with tarfile.open(packet,'w:gz')as t:
            for n,b in [('payload-inventory.json',json.dumps(inv).encode()),(name,b'changed'if bad else source.read_bytes())]:
                m=tarfile.TarInfo(n);m.size=len(b);t.addfile(m,io.BytesIO(b))
        return packet

    def test_exact_payload_and_lexical_native_mapping(self):
        with tempfile.TemporaryDirectory()as td:
            r=Path(td);p=self.packet(r);view=r/'view';proof=d.extract_payload(p,binding(p),view);self.assertEqual(proof['members'],1)
            repo=r/'repo';(repo/'scripts').mkdir(parents=True);(repo/'experiments').mkdir();(repo/'scripts/read.py').write_text('from pathlib import Path\nROOT=Path(__file__).absolute().parents[1]\n')
            native=r/'native';native.write_bytes(b'native feature unchanged');before=binding(native)
            m=d.make_view(repo,view,{'artifacts/features.npz':dict(path=str(native),binding=before)})
            self.assertEqual(binding(view/'artifacts/features.npz'),before);self.assertEqual(native.stat().st_ino,(view/'artifacts/features.npz').stat().st_ino)
            self.assertEqual(binding(native),before);self.assertTrue((view/'scripts/read.py').is_symlink())
            with self.assertRaises(ValueError):d.make_view(repo,view,{})

    def test_corrupt_and_traversal_payload_refused(self):
        for name,bad in [('artifacts/truth.json',True),('../escaped',False)]:
            with tempfile.TemporaryDirectory()as td:
                r=Path(td);p=self.packet(r,name,bad)
                with self.assertRaises(ValueError):d.extract_payload(p,binding(p),r/'view')

    def test_rendered_arm_cannot_dispatch_science(self):
        text=(ROOT/'scripts/e030_review_arm.py').read_text()
        self.assertIn("repo/'scripts/e030_diagnostics.py'",text)
        self.assertNotIn("repo/'scripts/e030_phase.py'",text)
        self.assertIn("cfg['review_deadline_epoch']-time.time()",text)
        self.assertIn('native_normal_exit_and_crash_tests_passed=True',text)

if __name__=='__main__':unittest.main()
