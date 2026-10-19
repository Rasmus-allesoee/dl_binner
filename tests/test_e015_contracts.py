"""Actual E015 policy/source/collection refusal tests, independent of cloud state."""
import ast
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

REPO=Path(__file__).absolute().parents[1];sys.path.insert(0,str(REPO/'scripts'))
from e015_policy import validate_control
from e015_collect import pack,verify


class ControlContracts(unittest.TestCase):
    def test_only_two_weights_change_and_training_loop_AST_is_frozen(self):
        base=json.loads((REPO/'src/dl_binner/resources/multiview.json').read_text())
        cfg=json.loads((REPO/'experiments/E015-zero-reconstruction/config.json').read_text());validate_control(cfg,base)
        for changed in [dict(seed=12),dict(depth_dropout=.4),dict(composition_reconstruction_weight=.1)]:
            with self.assertRaises(ValueError):validate_control(cfg|changed,base)
        with self.assertRaises(ValueError):validate_control(cfg,cfg)
        old=next(n for n in ast.parse((REPO/'src/dl_binner/multiview/model.py').read_text()).body if isinstance(n,ast.FunctionDef)and n.name=='train')
        new=next(n for n in ast.parse((REPO/'scripts/e015_training.py').read_text()).body if isinstance(n,ast.FunctionDef)and n.name=='train')
        # The sole change is explicit admission of the original bank policy.
        self.assertEqual(ast.unparse(old.body[3]),"if vm['policy'] != cfg:\n    raise ValueError('Multiview bank/config differs')")
        self.assertEqual(ast.unparse(new.body[3]),"validate_control(cfg, vm['policy'])")
        new.body[3]=old.body[3]
        self.assertEqual(ast.dump(old),ast.dump(new))

    def test_actual_controller_to_native_configuration_schema_in_fresh_directory(self):
        from e015_phase import configuration
        from e014_collect import binding
        with tempfile.TemporaryDirectory() as t:
            root=Path(t);plan=root/'science-plan.json';plan.write_text('{}')
            ident=dict(root=str(root),service_name='fresh-test',source='a'*40,vm_start_epoch=12345,
                       archive_prefix='gs://private-existing/fresh')
            value=configuration(ident,root/'repo',100,{str(plan):binding(plan)})
            path=root/'config.json';path.write_text(json.dumps(value));read=json.loads(path.read_text())
            self.assertEqual(read['source_commit'],ident['source']);self.assertEqual(read['science_plan'],str(plan))
            self.assertEqual(read['bindings'][str(plan)],binding(plan))
            self.assertEqual(read['reuse_lock'],str(root/'repo/experiments/E015-zero-reconstruction/reuse-lock.json'))
            with self.assertRaises(ValueError):configuration(ident|dict(source='short'),root,100,{})

    def test_release_needs_current_credit_retention_clock_and_exact_config(self):
        import time
        from e015_phase import admission,STOP_SECONDS,SECONDS
        from e014_collect import binding
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)/'config.json';p.write_text('{}');now=time.time()
            cfg=dict(_path=str(p),vm_start_epoch=now)
            r={k:True for k in ['credit_gate_passed','pending_usage_accounted','native_gates_passed','watchdog_verified','existing_VM_only','full_axes_verified']}
            r.update(config=binding(p),provider_STOP_seconds=STOP_SECONDS,ceiling_USD=2,estimated_incremental_gross_USD=1.1,
                storage_retention_extended=False,covered_costs=['compute','disk','storage','network','operations'],
                credit_valid_until_epoch=now+100000,storage_valid_until_epoch=now+100000)
            admission(cfg,r,now)
            for changed in [dict(credit_gate_passed=False),dict(provider_STOP_seconds=9000),dict(ceiling_USD=10),
                            dict(estimated_incremental_gross_USD=2.1),dict(storage_retention_extended=True),
                            dict(storage_valid_until_epoch=now+8100),dict(covered_costs=['compute'])]:
                with self.assertRaises(ValueError):admission(cfg,r|changed,now)
            with self.assertRaises(TimeoutError):admission(cfg,r,now+SECONDS)

    def fixture(self,p):
        work=p/'work';(work/'units/x/train').mkdir(parents=True);evidence=p/'evidence';evidence.mkdir()
        (work/'units/x/train/reference.npz').write_bytes(b'identical native reload bytes')
        (work/'units/x/embeddings.npz').write_bytes(b'identical native reload bytes')
        (work/'units/x/graph.npz').write_bytes(b'tiny real graph transport')
        (work/'units/x/partition.json').write_text('{"assignment":[0,-1]}')
        (work/'units/x/full.fna').write_text('>opaque\nACGTNN\n')
        (evidence/'passed.json').write_text('{"status":"PASS"}')
        return work,evidence

    def test_actual_archive_member_alias_and_DNA_accounting(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t);work,evidence=self.fixture(p);r=pack(work,evidence,p/'return')
            self.assertTrue(r['every_member_verified']);self.assertEqual(len(r['aliases']),1)
            v=verify(p/'return/e015-evidence.tar.gz',r['archive'],p/'verified')
            self.assertEqual(v['regular_members'],r['regular_members'])
            inv=json.loads((p/'verified/inventory.json').read_text());self.assertIn('units/x/full.fna',inv['omitted_DNA_retained_on_disk'])
            (p/'return/e015-evidence.tar.gz').write_bytes(b'corruption')
            with self.assertRaisesRegex(ValueError,'bytes/cap'):verify(p/'return/e015-evidence.tar.gz',r['archive'])

    def test_exact_isolated_collector_CLI_and_transferred_sibling_layout(self):
        """Run the production -I/-B child from another cwd, not an in-process import.

        Exercise both checkout and explicit two-helper transfer layouts, including
        fresh output, exact archive verification and intended scientific-link
        refusal. The ignored inherited Python environment must supply no imports.
        """
        for transferred in [False,True]:
            with self.subTest(transferred=transferred),tempfile.TemporaryDirectory() as t:
                p=Path(t);work,evidence=self.fixture(p);cwd=p/'unrelated';cwd.mkdir()
                script=REPO/'scripts/e015_collect.py'
                if transferred:
                    helpers=p/'transferred-helpers';helpers.mkdir()
                    for name in ['e015_collect.py','e014_collect.py']:
                        shutil.copyfile(REPO/'scripts'/name,helpers/name)
                    script=helpers/'e015_collect.py'
                env=os.environ|{'PYTHONPATH':str(p/'untrusted-imports'),
                    'PYTHONHOME':str(p/'nonexistent-home'),'PYTHONUSERBASE':str(p/'untrusted-site')}
                def child(args):
                    return subprocess.run([sys.executable,'-I','-B',str(script),*map(str,args)],
                        cwd=cwd,env=env,capture_output=True,text=True,timeout=30)
                result=child(['--work',work,'--evidence',evidence,'--output',p/'return'])
                self.assertEqual(result.returncode,0,result.stdout+result.stderr)
                receipt=json.loads(result.stdout);self.assertTrue(receipt['every_member_verified'])
                result=child(['--verify',p/'return/e015-evidence.tar.gz','--output',p/'verified'])
                self.assertEqual(result.returncode,0,result.stdout+result.stderr)
                self.assertEqual(json.loads(result.stdout)['archive'],receipt['archive'])
                (work/'bad-link.json').symlink_to(evidence/'passed.json')
                result=child(['--work',work,'--evidence',evidence,'--output',p/'refused'])
                self.assertNotEqual(result.returncode,0)
                self.assertIn('Scientific result link refused',result.stderr)
                self.assertNotIn('ModuleNotFoundError',result.stderr)

    def test_collection_refuses_nonidentical_alias_link_unknown_or_impossible_bound(self):
        for mode in ['nonidentical','link','unknown','cap']:
            with self.subTest(mode=mode),tempfile.TemporaryDirectory() as t:
                p=Path(t);work,evidence=self.fixture(p)
                if mode=='nonidentical':(work/'units/x/train/reference.npz').write_bytes(b'different')
                if mode=='link':(work/'link.json').symlink_to(evidence/'passed.json')
                if mode=='unknown':(work/'unsupported.bin').write_bytes(b'unknown')
                with self.assertRaisesRegex(ValueError,{'nonidentical':'not exact','link':'link refused','unknown':'Unexpected','cap':'bound exceeds'}[mode]):
                    pack(work,evidence,p/'return',ceiling=1 if mode=='cap' else 2*1024**3)


if __name__=='__main__':unittest.main()
