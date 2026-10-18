"""Real tiny archive inventory/collection and corruption/link refusal contracts."""
import json
from pathlib import Path
import sys
import tarfile
import tempfile
import time
import unittest

sys.path.insert(0,str(Path(__file__).absolute().parents[1]/'scripts'))
from e014_collect import binding,pack,selection,verify_work
from e014_inspect_phase import admission


class CollectionContracts(unittest.TestCase):
    def test_held_release_refuses_uncovered_or_changed_original_limits(self):
        with tempfile.TemporaryDirectory()as t:
            p=Path(t)/'config.json';p.write_text('{}');now=time.time()
            cfg=dict(_path=str(p),vm_start_epoch=now,original_VM_uptime_seconds=9347.13)
            release=dict(credit_gate_passed=True,existing_VM_only=True,source_bytes_verified=True,
                no_scientific_replay=True,watchdog_verified=True,config=binding(p),provider_STOP_seconds=2700,
                storage_valid_until_epoch=now+9000,estimated_total_original_phase_gross_USD=1.6)
            admission(cfg,release,now)
            for changes in [dict(no_scientific_replay=False),dict(provider_STOP_seconds=3600),
                            dict(estimated_total_original_phase_gross_USD=11),dict(storage_valid_until_epoch=now)]:
                with self.assertRaises(ValueError):admission(cfg,release|changes,now)

    def fixture(self,root):
        """Construct original scientific bytes with an authentic inventory structure."""
        work=root/'work';work.mkdir();(work/'result.json').write_text('{"status":"SUCCESS"}')
        graphs=[]
        for unit in ['E009-dev5','oral-dev4','oral-dev5']:
            p=work/'units'/unit/'group/graph.npz';p.parent.mkdir(parents=True);p.write_bytes(unit.encode());graphs.append(p)
        (work/'DNA.fna').write_text('>x\nACGT\n')
        inventory=root/'original.json';inventory.write_text(json.dumps(dict(
            all_result_members={str(p.relative_to(work)):binding(p)for p in work.rglob('*')if p.is_file()},
            retained=['result.json']+[str(p.relative_to(work))for p in graphs])))
        phase=root/'phase';(phase/'logs').mkdir(parents=True);(phase/'completion.json').write_text('{"status":"FAILED","community_completed":true}')
        proofs=root/'proofs';proofs.mkdir()
        for i,p in enumerate(graphs):(proofs/('graph-'+str(i)+'.json')).write_text(json.dumps(dict(status='PASS',unit=p.parents[1].name,graph=binding(p))))
        return work,inventory,phase,proofs

    def test_real_smaller_archive_preserves_failed_parent_and_omitted_members(self):
        with tempfile.TemporaryDirectory()as t:
            root=Path(t);work,inventory,phase,proofs=self.fixture(root)
            before={str(p.relative_to(work)):binding(p)for p in work.rglob('*')if p.is_file()};r=pack(work,inventory,phase,proofs,root/'return')
            self.assertTrue(r['every_return_member_verified']);self.assertEqual(r['all_original_work']['members'],5)
            with tarfile.open(root/'return/e014-review.tar.gz')as a:
                self.assertNotIn('work/graph.npz',a.getnames());self.assertIn('phase/completion.json',a.getnames())
                self.assertEqual(json.load(a.extractfile('phase/completion.json'))['status'],'FAILED')
            self.assertEqual(before,{str(p.relative_to(work)):binding(p)for p in work.rglob('*')if p.is_file()})

    def test_corruption_extra_member_and_link_refusal(self):
        for mode in ['corrupt','extra','link']:
            with self.subTest(mode=mode),tempfile.TemporaryDirectory()as t:
                root=Path(t);work,inventory,phase,proofs=self.fixture(root)
                if mode=='corrupt':(work/'result.json').write_text('{}')
                elif mode=='extra':(work/'new.json').write_text('{}')
                else:(work/'result.json').unlink();(work/'result.json').symlink_to(phase/'completion.json')
                with self.assertRaises(ValueError):verify_work(work,inventory)

    def test_no_graph_proof_or_low_cap_cannot_pass(self):
        with tempfile.TemporaryDirectory()as t:
            root=Path(t);work,inventory,phase,proofs=self.fixture(root)
            with self.assertRaisesRegex(ValueError,'cap'):pack(work,inventory,phase,proofs,root/'too-small',ceiling=1)
            (proofs/'graph-0.json').unlink()
            with self.assertRaisesRegex(ValueError,'Three'):pack(work,inventory,phase,proofs,root/'missing')


if __name__=='__main__':unittest.main()
