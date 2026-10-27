"""Bounded operational E024 gates; cloud delivery and live Linux watcher are pending."""
import copy
import json
from pathlib import Path
import shlex
import subprocess
import sys
import tempfile
import time
import unittest

from e024_coverage import binding,write
from e024_phase import admission,service_content,STOP_SECONDS,disk_summary,upload_command
from e024_control import read_plan

ROOT=Path(__file__).absolute().parents[1]


class Operations(unittest.TestCase):
    def test_actual_isolated_arm_cli_imports_from_outside_checkout(self):
        with tempfile.TemporaryDirectory() as tmp:
            value=subprocess.run([sys.executable,'-I','-B',str(ROOT/'scripts/e024_arm.py'),'--help'],
                                 cwd=tmp,capture_output=True,text=True,timeout=20)
            self.assertEqual(value.returncode,0,value.stderr)
            self.assertIn('--config',value.stdout)

    def test_actual_verified_archive_inventory_reader_not_summary_schema(self):
        from e024_reuse_gates import archive_inventory
        from e024_collect import pack
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);work=root/'work';work.mkdir();evidence=root/'evidence';evidence.mkdir()
            (evidence/'gate.json').write_text('{"fixture":true}')
            pack(work,evidence,root/'return',allow_incomplete=True)
            path=root/'return/e024-evidence.tar.gz';inv=archive_inventory(path)
            self.assertEqual(inv['members']['evidence/gate.json'],binding(evidence/'gate.json'))
            bad=root/'bad.tar.gz';bad.write_bytes(path.read_bytes()[:30])
            with self.assertRaises(Exception):archive_inventory(bad)

    def test_private_delivery_refuses_overwriting_an_accepted_generation(self):
        self.assertEqual(upload_command('gcloud','/tmp/a','gs://private/new'),
                         ['gcloud','storage','cp','--if-generation-match=0','/tmp/a','gs://private/new'])

    def test_36hour_disk_history_does_not_overflow_atomic_control(self):
        rows=[dict(used=10000+i,free=1000000-i,growth=i) for i in range(70000)]
        summary=disk_summary(rows,9000)
        self.assertEqual(summary['maximum_sampled_global_growth_bytes'],70999)
        self.assertEqual(summary['samples'],70000)
        self.assertLess(len(json.dumps(dict(disk_summary=summary))),1024)

    def test_exact_rendered_Linux_unit_consumer_compiles_before_spending(self):
        from e024_gates import unit_command
        code=unit_command('/srv/dl_binner/repo')
        compile(code,'exact-Linux-consumer','exec')
        self.assertIn('test_e024_operations',code)

    def test_review_cached_numeric_neighbor_axes_and_frozen_disposition(self):
        import numpy as np
        from e024_review import neighbor_summary,disposition,coverage_populations
        h=dict(selected=np.array([2,0,1]),neighbors=np.array([[1,2],[0,2],[0,1]]))
        value=neighbor_summary(h,np.array([0,-1,0]),np.array([10,20,30]))
        self.assertEqual(value['queries'],2)
        self.assertEqual(value['bp'],40)
        self.assertEqual(value['same_origin_bp_weighted'],.5)
        self.assertEqual(disposition(.071,43,33,.1),'KEEP')
        self.assertEqual(disposition(.04,29,9,-.01),'ABANDON_THIS_FROZEN_RETRIEVAL_POLICY')
        self.assertEqual(disposition(.068,42,32,.1),'MODIFY')
        population=coverage_populations(dict(depth=np.array([[0,0],[1,0],[0,0]]),lengths=np.array([10,20,30]),eligible=np.array([True,True,False])),
            dict(ids=['a','b','c'],assignment=[0,-1,-1]),np.array([0,1,-1]),['A','B'],{'A':100},set())
        self.assertEqual(population['all_zero_bp'],40)
        self.assertEqual(population['missing_cells'],0)
        self.assertEqual(sum(x['bp'] for x in population['cells'].values()),60)

    def test_credit_clock_storage_complete_cost_and_gate_bindings(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);(root/'gate.json').write_text('{"tiny":true}')
            (root/'plan.json').write_text('{"tiny":true}')
            cfg=dict(vm_start_epoch=1000,_path=str(root/'config.json'),plan=str(root/'plan.json'))
            write(root/'config.json',cfg)
            release=dict(config=binding(root/'config.json'),credit_gate_passed=True,pending_usage_accounted=True,
                native_gates_passed=True,watchdog_verified=True,provider_STOP_verified=True,existing_VM_only=True,
                full_axes_verified=True,headroom_measured=True,retention_passed=True,real_money_authorized=False,
                estimated_incremental_gross_USD=14.75,ceiling_USD=16,provider_STOP_seconds=STOP_SECONDS,
                storage_retention_extended=False,credit_valid_until_epoch=1799740800,
                storage_valid_until_epoch=1793746800,covered_costs=['compute','disk','storage','network','operations'],
                gate_files={str(root/'gate.json'):binding(root/'gate.json')},plan=binding(root/'plan.json'),vm_start_epoch=1000)
            admission(cfg,release,1100)
            for field,value in [('estimated_incremental_gross_USD',16.01),('estimated_incremental_gross_USD',float('nan')),
                                ('real_money_authorized',True),('provider_STOP_seconds',36*3600),
                                ('covered_costs',['compute']),('credit_gate_passed',False),
                                ('vm_start_epoch',1001),
                                ('storage_valid_until_epoch',1793746801)]:
                r=copy.deepcopy(release);r[field]=value
                with self.assertRaises(ValueError,msg=field):admission(cfg,r,1100)
            with self.assertRaises(ValueError):admission(cfg,release,1000+36*3600)
            (root/'gate.json').write_text('corrupt')
            with self.assertRaisesRegex(ValueError,'bytes differ'):admission(cfg,release,1100)

    def test_rendered_service_exact_isolated_argv_and_no_restart(self):
        text=service_content('/tmp/fresh phase','/usr/bin/python','/tmp/repo/scripts/e024_phase.py','/tmp/config.json','researcher')
        self.assertIn('Restart=no',text)
        line=next(x for x in text.splitlines() if x.startswith('ExecStart='))
        argv=shlex.split(line.removeprefix('ExecStart='))
        self.assertEqual(argv[1:3],['-I','-B'])
        self.assertEqual(argv[-2:],['--config','/tmp/config.json'])
        with self.assertRaises(ValueError):service_content('/tmp/%n','p','s','c','u')

    def test_actual_isolated_readback_consumer_success_corruption_and_producer_failure(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);payload=root/'payload';payload.write_bytes(b'compact immutable fixture\n')
            external=root/'external-cli'
            # Only the external cloud transport is replaced; actual isolated
            # streaming hash/exit/cap consumer is tested from outside checkout.
            external.write_text('#!'+sys.executable+'\nimport sys\nfrom pathlib import Path\nsys.stdout.buffer.write(Path('+repr(str(payload))+').read_bytes())\n')
            external.chmod(0o700)
            argv=[sys.executable,'-I','-B',str(ROOT/'scripts/e024_phase.py'),'--readback','external-fixture',
                  '--gcloud',str(external),'--bytes',str(payload.stat().st_size),'--sha256',binding(payload)['sha256']]
            self.assertEqual(subprocess.run(argv,cwd=root,capture_output=True).returncode,0)
            payload.write_bytes(b'corrupt')
            self.assertNotEqual(subprocess.run(argv,cwd=root,capture_output=True).returncode,0)
            external.write_text('#!'+sys.executable+'\nraise SystemExit(7)\n')
            self.assertNotEqual(subprocess.run(argv,cwd=root,capture_output=True).returncode,0)

    def test_actual_timeout_receipt_records_intended_limit(self):
        from e009_owner import supervisor
        with tempfile.TemporaryDirectory() as tmp:
            log=Path(tmp)/'timeout.log';s=supervisor()
            with self.assertRaises(RuntimeError):
                s.supervise([sys.executable,'-I','-B','-c','import time;print("fixture-started",flush=True);time.sleep(5)'],
                            log,.3,8_000_000_000,s.isolated_env(4))
            receipt=json.loads(log.with_suffix('.exit.json').read_text())
            self.assertIn('TimeoutError',receipt['stop_reason'])
            self.assertIn('fixture-started',log.read_text())
            self.assertIsNotNone(receipt['exit_code'])

    def test_engineering_cannot_acquire_a_public_bulk_object(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            p=json.loads((ROOT/'experiments/E024-oral-measured-coverage/runtime-plan.json').read_text())
            p['engineering']=True;p['read_manifest']=str(root/'reads.json')
            m=json.loads((ROOT/'experiments/E024-oral-measured-coverage/read-manifest.json').read_text())
            write(root/'reads.json',m);write(root/'plan.json',p)
            with self.assertRaisesRegex(ValueError,'loopback'):read_plan(root/'plan.json',True)


if __name__=='__main__':unittest.main()
