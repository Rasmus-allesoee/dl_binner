"""Actual failed-child/terminal-status, isolated CLI and capped archive contracts."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest
from unittest.mock import patch

from e024_coverage import write,binding
from e025_phase import phase_exit,deliver_completion,service_content,admission,STOP_SECONDS,SECONDS
from e025_collect import pack
from e025_gates import unit_command
from e009_owner import supervisor

ROOT=Path(__file__).absolute().parents[1]


class Operations(unittest.TestCase):
    def test_new_credit_clock_retention_and_file_gates_refuse_expansion(self):
        import copy
        with tempfile.TemporaryDirectory() as tmp:
            r=Path(tmp);write(r/'plan.json',{});write(r/'gate.json',{});write(r/'config.json',{})
            cfg=dict(vm_start_epoch=1000,_path=str(r/'config.json'),plan=str(r/'plan.json'))
            release=dict(config=binding(r/'config.json'),plan=binding(r/'plan.json'),vm_start_epoch=1000,
                credit_gate_passed=True,pending_usage_accounted=True,native_gates_passed=True,
                watchdog_verified=True,provider_STOP_verified=True,existing_VM_only=True,full_axes_verified=True,
                headroom_measured=True,retention_passed=True,real_money_authorized=False,
                estimated_incremental_gross_USD=4.9,ceiling_USD=5,provider_STOP_seconds=STOP_SECONDS,
                storage_retention_extended=False,credit_valid_until_epoch=1799740800,
                storage_valid_until_epoch=1793746800,covered_costs=['compute','disk','storage','network','operations'],
                gate_files={str(r/'gate.json'):binding(r/'gate.json')})
            admission(cfg,release,1100)
            for k,v in [('estimated_incremental_gross_USD',5.01),('estimated_incremental_gross_USD',float('nan')),
                        ('real_money_authorized',True),('ceiling_USD',6),('provider_STOP_seconds',130500),
                        ('storage_valid_until_epoch',1793746801),('credit_gate_passed',False)]:
                bad=copy.deepcopy(release);bad[k]=v
                with self.assertRaises(ValueError,msg=k):admission(cfg,bad,1100)
            with self.assertRaises(ValueError):admission(cfg,release,1000+SECONDS)
            (r/'gate.json').write_text('corrupt')
            with self.assertRaisesRegex(ValueError,'bytes differ'):admission(cfg,release,1100)

    def test_failed_real_child_is_not_hidden_by_successful_collection_parent(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);log=root/'failed.log';s=supervisor()
            with self.assertRaises(RuntimeError):
                s.supervise([sys.executable,'-I','-B','-c','print("intended-scientific-failure",flush=True);raise SystemExit(7)'],
                    log,10,8_000_000_000,s.isolated_env(4))
            receipt=json.loads(log.with_suffix('.exit.json').read_text())
            self.assertEqual(receipt['exit_code'],7);self.assertIn('intended-scientific-failure',log.read_text())
            result=dict(status='FAILED',science_completed=False,collection_readback_verified=True)
            write(root/'result.json',result)
            code='import sys,json;sys.path.insert(0,'+repr(str(ROOT/'scripts'))+');from e025_phase import phase_exit;sys.exit(phase_exit(json.load(open(sys.argv[1]))))'
            actual=subprocess.run([sys.executable,'-I','-B','-c',code,str(root/'result.json')],cwd=root)
            self.assertEqual(actual.returncode,1)

    def test_terminal_status_follows_upload_and_delivery_failure_stays_failed(self):
        for transport_fails in [False,True]:
            with tempfile.TemporaryDirectory() as tmp:
                root=Path(tmp);events=[]
                def upload(path):
                    self.assertTrue(path.is_file());events.append('upload')
                    if transport_fails:raise RuntimeError('external cloud transport unavailable')
                result=dict(status='SUCCESS',science_completed=True,collection_readback_verified=True)
                with patch('e025_phase.status',lambda r:events.append(r['status'])):
                    deliver_completion(result,root,time.time()+60,upload)
                self.assertEqual(events,['upload','FAILED' if transport_fails else 'SUCCESS'])
                self.assertEqual(phase_exit(result),1 if transport_fails else 0)

    def test_actual_isolated_rendered_consumers_import_outside_checkout(self):
        compile(unit_command('/srv/dl_binner/repo'),'native-unit-command','exec')
        from e025_launch import render_host,render_release
        for code in [render_host(dict(root='/srv/dl_binner/experiments/e025/tiny',repo='/srv/dl_binner/repo'),{}),
                     render_release(dict(root='/srv/dl_binner/experiments/e025/tiny'),{})]:
            compile(code,'actual-rendered-native-controller','exec')
            self.assertNotIn('IDENTITY',code)
        with tempfile.TemporaryDirectory() as tmp:
            for name in ['e025_control.py','e025_phase.py','e025_arm.py','e025_gates.py','e025_collect.py','e025_launch.py']:
                value=subprocess.run([sys.executable,'-I','-B',str(ROOT/'scripts'/name),'--help'],cwd=tmp,capture_output=True,text=True,timeout=20)
                self.assertEqual(value.returncode,0,value.stderr)
            text=service_content('/tmp/fixture','/usr/bin/python3','/tmp/repo/scripts/e025_phase.py','/tmp/config.json','researcher')
            self.assertIn('Restart=no',text);self.assertIn('-I -B',text)

    def test_real_archive_binds_external_inputs_without_recopy_and_enforces_cap(self):
        from e023_collect import verify
        with tempfile.TemporaryDirectory() as tmp:
            r=Path(tmp);work=r/'work';work.mkdir();evidence=r/'evidence';evidence.mkdir()
            (work/'numeric.json').write_text('{"recall":0.4}')
            (work/'same.json').write_bytes((work/'numeric.json').read_bytes())
            (work/'DNA.fna').write_text('>opaque\nACGT\n')
            ext=dict(data_copied=False,archive=dict(bytes=42,sha256='fixture-only'),fixture=True)
            write(evidence/'external-data.json',ext)
            result=pack(work,evidence,r/'return',allow_incomplete=True)
            self.assertTrue(result['every_member_verified']);self.assertEqual(len(result['aliases']),1)
            inv=json.loads((r/'return/inventory.json').read_text());self.assertEqual(inv['external_data'],ext)
            self.assertIn('DNA.fna',inv['omitted_retained_on_disk'])
            with self.assertRaisesRegex(ValueError,'Compressed return cap'):pack(work,evidence,r/'capped',ceiling=1,allow_incomplete=True)
            archive=r/'return/e025-evidence.tar.gz';archive.write_bytes(archive.read_bytes()[:30])
            with self.assertRaises(Exception):verify(archive)


if __name__=='__main__':unittest.main()
