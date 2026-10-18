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
from e014_inspect_phase import admission,reuse_graph_proofs


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

    def test_identical_reference_is_losslessly_bound_not_duplicated(self):
        with tempfile.TemporaryDirectory()as t:
            root=Path(t);work,inventory,phase,proofs=self.fixture(root)
            ref=work/'units/E009-dev5/train/reference.npz';ref.parent.mkdir(parents=True);ref.write_bytes(b'actual identical payload')
            em=ref.parents[1]/'embeddings.npz';em.write_bytes(ref.read_bytes())
            r=json.loads(inventory.read_text())
            for p in [ref,em]:
                key=str(p.relative_to(work));r['all_result_members'][key]=binding(p);r['retained'].append(key)
            inventory.write_text(json.dumps(r))
            result=pack(work,inventory,phase,proofs,root/'return')
            alias='work/'+str(ref.relative_to(work));canonical='work/'+str(em.relative_to(work))
            self.assertEqual(result['identical_duplicate_members'][alias],dict(canonical=canonical,**binding(ref)))
            with tarfile.open(root/'return/e014-review.tar.gz')as a:
                self.assertNotIn(alias,a.getnames());self.assertEqual(a.extractfile(canonical).read(),ref.read_bytes())
            ref.write_bytes(b'nonidentical')
            r['all_result_members'][str(ref.relative_to(work))]=binding(ref);inventory.write_text(json.dumps(r))
            with self.assertRaisesRegex(ValueError,'not an identical'):selection(work,inventory)

    def test_reuses_passed_readers_and_preserves_failed_collection_without_invocation(self):
        with tempfile.TemporaryDirectory()as t:
            root=Path(t);prior=root/'prior';(prior/'proofs').mkdir(parents=True);(prior/'logs').mkdir();(prior/'helpers').mkdir()
            for u in ['E009-dev5','oral-dev4','oral-dev5']:(prior/'proofs'/('graph-'+u+'.json')).write_text(json.dumps(dict(status='PASS',unit=u)))
            stages=[dict(name='graph-'+u,resources=dict(exit_code=0,stop_reason=None))for u in ['E009-dev5','oral-dev4','oral-dev5']]
            (prior/'completion.json').write_text(json.dumps(dict(status='FAILED',stages=stages)))
            for n in ['host.json','config.json','started.json','release.json']:(prior/n).write_text('{}')
            for n in ['parent-terminal.log','collect.log','supervision.json','watchdog-live-before-release.json']:(prior/'logs'/n).write_text('retained evidence')
            reader=prior/'helpers/e014_graph_review.py';reader.write_text('raise RuntimeError("must never execute")')
            proof=root/'fresh';proof.mkdir();expected=binding(prior/'completion.json')
            r=reuse_graph_proofs(prior,proof,expected,binding(reader))
            self.assertEqual(r['passed_readers_reused'],3)
            self.assertEqual(binding(proof/'previous-collection-failure/completion.json'),expected)
            stages[0]['resources']['exit_code']=1;(prior/'completion.json').write_text(json.dumps(dict(status='FAILED',stages=stages)))
            with self.assertRaisesRegex(ValueError,'journal differs'):reuse_graph_proofs(prior,proof,expected,binding(reader))
            with self.assertRaisesRegex(ValueError,'did not pass'):reuse_graph_proofs(prior,proof,binding(prior/'completion.json'),binding(reader))


if __name__=='__main__':unittest.main()
