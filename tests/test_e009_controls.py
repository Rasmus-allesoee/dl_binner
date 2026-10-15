"""Launcher contracts with native inert children; no binner fits or scientific replay."""
from collections import namedtuple
import json
import os
from pathlib import Path
import subprocess
import shutil
import sys
import tarfile
import tempfile
import time
import unittest
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).absolute().parents[1]/'scripts'))
from e009_controls import PhaseGuard, collect_complete, paired_command, run_serial, verify_wheel


class ControlLauncher(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup);self.root=Path(self.temp.name)
        if os.environ.get('E009_CONTROL_TEST_EVIDENCE'):
            destination=Path(os.environ['E009_CONTROL_TEST_EVIDENCE'])/self._testMethodName
            self.addCleanup(lambda:shutil.copytree(self.root,destination))

    def test_exact_scientific_command_and_no_truth_input(self):
        command=paired_command('/env/bin/python','assembly.fa','ten-depth.tsv','fresh',800)
        self.assertEqual(command[:7],['/env/bin/python','-I','-B','-m','dl_binner','run','--fasta'])
        self.assertIn('ten-depth.tsv',command);self.assertNotIn('--depth',paired_command('/p','a',None,'b',1))
        self.assertFalse(any('truth'in x or 'config'in x or 'seed'in x for x in command))
        for v in [0,-1,float('nan'),float('inf')]:
            with self.assertRaises(TimeoutError):paired_command('/p','a',None,'b',v)

    def test_read_only_default_and_execute_without_approval_refused(self):
        script=Path(__file__).parents[1]/'scripts/e009_controls.py'
        p=subprocess.run([sys.executable,'-I','-B',script],cwd=self.root,capture_output=True,text=True,check=True)
        self.assertFalse(json.loads(p.stdout)['execution']);self.assertEqual(list(self.root.iterdir()),[])
        p=subprocess.run([sys.executable,'-I','-B',script,'--execute'],cwd=self.root,capture_output=True,text=True)
        self.assertNotEqual(p.returncode,0);self.assertIn('--approval is required',p.stderr)
        self.assertEqual(list(self.root.iterdir()),[])

    def test_serial_native_children_and_shared_setup_clock(self):
        events=self.root/'events'
        def stage(label):
            def argv(remaining):
                return [sys.executable,'-I','-B','-c',
                        'from pathlib import Path;import time;'+
                        f'p=Path({str(events)!r});f=p.open("a");f.write({label!r}+" start\\n");f.flush();time.sleep(.15);f.write({label!r}+" end\\n");f.close()']
            return label,argv
        result=run_serial([stage('setup'),stage('first'),stage('second')],self.root,time.monotonic()+8,collect_reserve=.1)
        self.assertEqual(events.read_text().splitlines(),[f'{s} {e}'for s in ['setup','first','second']for e in ['start','end']])
        self.assertEqual(len(result),3)
        self.assertGreater(result[0]['receipt']['seconds_ceiling'],result[2]['receipt']['seconds_ceiling'])

    def test_worker_failure_and_deadline_do_not_schedule_successor(self):
        successor=self.root/'forbidden'
        for label,code,seconds,reason in [('fatal','raise ValueError("intended inert worker failure")',5,'intended inert worker failure'),
                                           ('time','import time;time.sleep(60)',.5,'wall-time limit')]:
            stages=[(label,lambda t,c=code:[sys.executable,'-I','-B','-c',c]),
                    ('successor',lambda t:[sys.executable,'-c',f'open({str(successor)!r},"w").close()'])]
            with self.assertRaisesRegex(RuntimeError,reason):run_serial(stages,self.root,time.monotonic()+seconds,collect_reserve=.01)
            self.assertFalse(successor.exists())
            receipt=json.loads((self.root/(label+'.exit.json')).read_text())
            self.assertNotEqual(receipt['exit_code'],0)

    def test_parent_prerequisite_clock_and_disk_guards(self):
        with self.assertRaisesRegex(RuntimeError,'reserve unavailable'):
            with PhaseGuard(self.root,5,reserve_bytes=10**30):pass
        with self.assertRaisesRegex(TimeoutError,'Whole control-phase clock'):
            with PhaseGuard(self.root,.1,reserve_bytes=0):time.sleep(2)
        usage=namedtuple('usage','total used free')
        # Substitute only the filesystem sensor; alarm delivery and child cleanup are real.
        with patch('e009_controls.shutil.disk_usage',side_effect=[usage(100,10,90),usage(100,30,70)]):
            with self.assertRaisesRegex(TimeoutError,'growth allowance'):
                with PhaseGuard(self.root,5,reserve_bytes=0,growth_bytes=1):time.sleep(2)

    def test_changed_wheel_fails_before_install(self):
        fake=self.root/'changed.whl';fake.write_bytes(b'changed')
        with self.assertRaisesRegex(ValueError,'wheel bytes changed'):
            verify_wheel(fake,{'wheel':{'bytes':1,'sha256':'not-a-hash'}})

    def test_collection_exact_members_inventory_and_closed_terminal_snapshot(self):
        (self.root/'env').mkdir();(self.root/'env/ignored').write_text('environment')
        (self.root/'cache').mkdir();(self.root/'cache/ignored').write_text('payload cache')
        (self.root/'ten-depth/features').mkdir(parents=True)
        (self.root/'ten-depth/features/features.npz').write_bytes(b'fixture representation')
        (self.root/'stage.log').write_text('closed stage\n')
        terminal=self.root.parent/(self.root.name+'-terminal.log');terminal.write_text('before snapshot\n')
        self.addCleanup(terminal.unlink)
        result=collect_complete(self.root,terminal);terminal.write_text('after snapshot\n')
        with tarfile.open(self.root/result['filename'])as tar:
            members=tar.getmembers();self.assertEqual(sum(m.size for m in members),result['logical_member_bytes'])
            self.assertEqual(len(members),result['regular_members'])
            self.assertEqual(tar.extractfile('terminal.snapshot.log').read(),b'before snapshot\n')
            self.assertEqual(set(m.name for m in members),{'terminal.snapshot.log','stage.log','collection-inventory.json','ten-depth/features/features.npz'})
            self.assertEqual(len(json.load(tar.extractfile('collection-inventory.json'))['files']),3)

    def test_parent_alarm_stops_child_and_running_orphan(self):
        pidfile=self.root/'orphan.pid'
        code=('import subprocess,sys,time;from pathlib import Path;'
              'p=subprocess.Popen([sys.executable,"-c","import time;time.sleep(60)"]);'
              f'Path({str(pidfile)!r}).write_text(str(p.pid));time.sleep(60)')
        with self.assertRaisesRegex(RuntimeError,'Whole control-phase clock'):
            with PhaseGuard(self.root,.7,reserve_bytes=0):
                run_serial([('alarm',lambda t:[sys.executable,'-I','-B','-c',code])],
                           self.root,time.monotonic()+10,collect_reserve=.01)
        self.assertTrue(pidfile.exists())
        for pid in [int(pidfile.read_text()),json.loads((self.root/'alarm.exit.json').read_text())['launched_pid']]:
            check=subprocess.run(['ps','-p',str(pid),'-o','stat='],text=True,capture_output=True)
            self.assertTrue(not check.stdout.strip()or check.stdout.strip().startswith('Z'),check.stdout)


if __name__=='__main__':unittest.main()
