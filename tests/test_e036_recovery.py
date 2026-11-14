"""Exercise actual recovery parent source guard and snapshot filesystem contract."""
import json,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).absolute().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from e036_resume import prepare_layout
from e034_phase import evidence
from e024_coverage import binding

class Recovery(unittest.TestCase):
    def test_actual_parent_invokes_admitted_overlay(self):
        import e036_resume_phase as p
        from e036_control import freeze
        self.assertIs(p.freeze_sources,freeze)
        self.assertEqual(p.freeze_sources(),binding(ROOT/'experiments/E036-optional-pooled-links/source-lock.json'))

    def test_actual_layout_producer_and_snapshot_reader_agree(self):
        with tempfile.TemporaryDirectory()as folder:
            base=Path(folder);plan=base/'immutable-plan.json';plan.write_text('{"retained":true}\n');cfg=dict(root=str(base/'fresh'),plan=str(plan))
            root=prepare_layout(cfg)
            for n in ['config.json','host.json','release.json','started.json']:(root/n).write_text(json.dumps(cfg))
            out=evidence(root)
            self.assertEqual(binding(out/'science-plan.json'),binding(plan))
            with self.assertRaises(FileExistsError):prepare_layout(cfg)
            self.assertEqual(plan.read_text(),'{"retained":true}\n')

if __name__=='__main__':unittest.main()
