"""Prospective E010 launcher contracts; no GCP calls, community fit or scoring."""
import json
from pathlib import Path
import subprocess
import sys
import tarfile
import tempfile
import time
import unittest
from unittest.mock import patch
from collections import namedtuple
sys.path.insert(0,str(Path(__file__).absolute().parents[1]/'scripts'))
from e010_candidate import candidate_command,collect,verify_approval,verify_wheel


class CandidateLaunchContracts(unittest.TestCase):
    def test_default_read_only_and_explicit_approval_required(self):
        script=Path(__file__).parents[1]/'scripts/e010_candidate.py'
        with tempfile.TemporaryDirectory()as folder:
            result=subprocess.run([sys.executable,'-I','-B',script],cwd=folder,text=True,capture_output=True,check=True)
            self.assertFalse(json.loads(result.stdout)['execution'])
            self.assertEqual(list(Path(folder).iterdir()),[])
            result=subprocess.run([sys.executable,'-I','-B',script,'--execute'],cwd=folder,text=True,capture_output=True)
            self.assertNotEqual(result.returncode,0);self.assertIn('explicit execution paths',result.stderr)
            self.assertEqual(list(Path(folder).iterdir()),[])

    def test_exact_single_candidate_command_has_no_truth_baseline_or_schedule_override(self):
        command=candidate_command('/env/bin/python','assembly','depth','markers','asset','fresh',100)
        self.assertEqual(command[:6],['/env/bin/python','-I','-B','-m','dl_binner','candidate'])
        self.assertNotIn('--config',command);self.assertNotIn('--resume',command)
        self.assertNotIn('--seed',command);self.assertNotIn('truth',' '.join(command))
        self.assertIn('--marker-hmm',command)
        for seconds in [-1,0,14401,float('nan')]:
            with self.assertRaises(TimeoutError):candidate_command('p','a','d','m','b','o',seconds)

    def test_new_coverage_storage_watchdog_and_cumulative_clock_gates(self):
        now=time.time()
        a=dict(experiment='E010',incremental_gross_ceiling_usd=2,credit_gate_passed=True,
            pending_usage_accounted=True,provider_stop_seconds=15300,watchdog_release_verified=True,
            no_resource_change=True,storage_retention_extended=False,
            credit_valid_until_epoch=now+99999,storage_valid_until_epoch=now+99999,
            covered_costs=['compute','disk','storage','network','operations'],vm_start_epoch=now-300)
        self.assertEqual(verify_approval(a,now),14100)
        for key,value in [('credit_gate_passed',False),('pending_usage_accounted',False),
                          ('watchdog_release_verified',False),('incremental_gross_ceiling_usd',20),
                          ('covered_costs',['compute']),('storage_valid_until_epoch',now-1)]:
            with self.subTest(key=key):
                with self.assertRaises(ValueError):verify_approval(dict(a,**{key:value}),now)
        with self.assertRaises(TimeoutError):verify_approval(dict(a,vm_start_epoch=now-14400),now)

    def test_archive_every_member_inventory_and_closed_terminal_not_later_live_bytes(self):
        with tempfile.TemporaryDirectory()as folder:
            root=Path(folder)/'retained';root.mkdir()
            (root/'terminal.log').write_text('live and growing')
            (root/'terminal.snapshot.log').write_text('closed')
            (root/'candidate').mkdir();(root/'candidate'/'features').write_text('real retained fixture')
            (root/'candidate'/'native-cache').mkdir();(root/'candidate'/'native-cache'/'jit').write_text('not portable')
            result=collect(root)
            with tarfile.open(result['path'])as tar:
                members=tar.getmembers();self.assertEqual(result['members'],len(members))
                self.assertEqual(result['logical_member_bytes'],sum(m.size for m in members))
                self.assertNotIn('terminal.log',tar.getnames())
                self.assertFalse(any('native-cache'in n for n in tar.getnames()))
                self.assertEqual(tar.extractfile('terminal.snapshot.log').read(),b'closed')
                inventory=json.load(tar.extractfile('collection-inventory.json'))
                self.assertEqual(set(tar.getnames()),set(inventory['files'])|{'collection-inventory.json'})
            (root/'terminal.log').write_text('later, larger live bytes are not archived')
            self.assertEqual(result['logical_member_bytes'],sum(m.size for m in members))

    def test_changed_wheel_refused_without_install_or_fit(self):
        with tempfile.TemporaryDirectory()as folder:
            p=Path(folder)/'changed.whl';p.write_bytes(b'changed')
            with self.assertRaisesRegex(ValueError,'wheel bytes changed'):verify_wheel(p,{'wheel':{'bytes':1,'sha256':'bad'}})

    def test_real_held_phase_adapter_native_inert_launcher_and_external_only_transfer_substitute(self):
        import e010_phase
        from e009_owner import supervisor
        from e009_common import binding
        # Real parent, alarm, process supervision, file/closure hashing and
        # readback paths run here. Only GCS transport and filesystem capacity
        # sensor are substituted; the launcher is explicitly inert, never a fit.
        native=supervisor()
        with tempfile.TemporaryDirectory()as folder:
            root=Path(folder);storage=root/'fake-external-store';storage.mkdir()
            transport=root/'external.py';transport.write_text('''import pathlib,shutil,sys
args=[a for a in sys.argv[1:]if not a.startswith('--')]
src,dst=args[args.index('cp')+1:]
def local(p):return pathlib.Path(sys.argv[0]).parent/'fake-external-store'/pathlib.Path(p).name if p.startswith('gs://')else pathlib.Path(p)
source,destination=local(src),local(dst)
if dst.startswith('gs://')and destination.exists():raise ValueError('immutable remote object exists')
shutil.copyfile(source,destination)
''')
            class ExternalAdapter:
                isolated_env=staticmethod(native.isolated_env)
                def supervise(self,argv,*args,**kwargs):
                    if argv[0]=='/snap/bin/gcloud':argv=[sys.executable,'-I','-B',str(transport),*map(str,argv[1:])]
                    return native.supervise(argv,*args,**kwargs)
            for failing in [False,True]:
                with self.subTest(failing=failing):
                    # Each attempt has a fresh remote prefix/store; no retry.
                    for p in storage.iterdir():p.unlink()
                    phase=root/('failed'if failing else'passed');phase.mkdir()
                    launcher=phase/'launcher';archive=phase/'launcher-evidence.tar.gz'
                    child=phase/'inert.py';child.write_text('''import hashlib,json,pathlib,sys
p=pathlib.Path(sys.argv[1]);p.mkdir()
if sys.argv[2]=='True':raise ValueError('intended inert launcher failure')
a=p.parent/'launcher-evidence.tar.gz';a.write_bytes(b'inert transfer fixture, not science')
r=dict(bytes=a.stat().st_size,sha256=hashlib.sha256(a.read_bytes()).hexdigest())
(a.parent/(a.name+'.sha256')).write_text(r['sha256']+'  '+a.name+'\\n')
(p/'phase-result.json').write_text(json.dumps(dict(status='SUCCESS',fit_completed=True,collection=dict(path=str(a),archive=r))))
''')
                    cfg=dict(phase_root=str(phase),launcher_root=str(launcher),vm_start_epoch=time.time(),
                        initial_filesystem_used_bytes=0,phase_id='inert-native-test',source_commit='fixture',
                        release_file=str(phase/'release.json'),archive_prefix='gs://fake-prefix',
                        launcher_argv=[sys.executable,'-I','-B',str(child),str(launcher),str(failing)])
                    path=phase/'config.json';path.write_text(json.dumps(cfg))
                    (phase/'release.json').write_text(json.dumps(dict(phase_config=binding(path))))
                    disk=namedtuple('disk','total used free')(200*1024**3,0,200*1024**3)
                    with patch.object(e010_phase,'supervisor',return_value=ExternalAdapter()),patch.object(e010_phase,'publish_status'),patch('e009_controls.shutil.disk_usage',return_value=disk):
                        code=e010_phase.run(path)
                    outcome=json.loads((phase/'completion.json').read_text())
                    self.assertEqual(code,1 if failing else 0)
                    self.assertEqual(outcome['status'],'FAILED'if failing else'SUCCESS')
                    if failing:self.assertIn('intended inert launcher failure',outcome['error'])
                    else:self.assertTrue(outcome['cloud_collection_verified'])
                    self.assertTrue(outcome['closure_archive']['readback_verified'])
                    with self.assertRaisesRegex(ValueError,'no retry or resume'):e010_phase.run(path)


if __name__=='__main__':unittest.main()
