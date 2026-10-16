"""Protect a live experiment from shutdown and prove both exit paths select STOP."""
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

spec=importlib.util.spec_from_file_location('e009_exit_watchdog',Path(__file__).resolve().parents[1]/'scripts/e009_exit_watchdog.py')
mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)


class WatchdogTests(unittest.TestCase):
    def test_live_exit_grace_pid_reuse_zombie_and_boot(self):
        process={'pid':42,'start_ticks':123,'command_sha256':'abc'}
        cfg={'process':process,'boot_id':'this-boot','exit_grace_seconds':60}
        self.assertFalse(mod.decide(cfg,{},process,'this-boot',1)['shutdown'])
        first=mod.decide(cfg,{},None,'this-boot',10)
        self.assertFalse(mod.decide(cfg,first,None,'this-boot',69)['shutdown'])
        self.assertTrue(mod.decide(cfg,first,None,'this-boot',70)['shutdown'])
        self.assertFalse(mod.decide(cfg,first,None,'later-boot',70)['shutdown'])
        self.assertTrue(mod.decide(cfg,first,{**process,'start_ticks':124},'this-boot',70)['shutdown'])
        self.assertNotIn('first_missing_monotonic',mod.decide(cfg,first,process,'this-boot',70))
        with tempfile.TemporaryDirectory()as tmp:
            proc=Path(tmp);folder=proc/'42';folder.mkdir()
            # State Z must be treated as exited even if the proc directory still exists.
            (folder/'stat').write_text('42 (a name with ) brackets) Z '+' '.join(['0']*30))
            self.assertIsNone(mod.identity(42,proc))

    @unittest.skipUnless(sys.platform=='linux','actual Linux /proc contract')
    def test_real_native_success_and_crash_without_powering_off_host(self):
        for exit_code in (0,7):
            with self.subTest(exit_code=exit_code),tempfile.TemporaryDirectory()as tmp:
                root=Path(tmp);work=root/'work';(work/'parts').mkdir(parents=True);(work/'logs').mkdir()
                child=subprocess.Popen([sys.executable,'-I','-B','-c',f'import sys; sys.stdin.readline(); sys.exit({exit_code})'],stdin=subprocess.PIPE)
                stopped=[]
                try:
                    cfg={'process':mod.identity(child.pid),'boot_id':Path('/proc/sys/kernel/random/boot_id').read_text().strip(),
                         'workflow_root':str(work),'exit_grace_seconds':1}
                    self.assertIsNotNone(cfg['process'])
                    state=root/'state';evidence=root/'evidence'
                    mod.tick(cfg,state,evidence,now=0,shutdown=lambda:stopped.append('STOP'))
                    self.assertFalse(stopped)
                    child.communicate(b'finish\n',timeout=10);self.assertEqual(child.returncode,exit_code)
                    mod.tick(cfg,state,evidence,now=1,shutdown=lambda:stopped.append('STOP'))
                    self.assertFalse(stopped)
                    mod.tick(cfg,state,evidence,now=2,shutdown=lambda:stopped.append('STOP'))
                    self.assertEqual(stopped,['STOP'])
                    snapshot=json.loads((evidence/'exit-snapshot.json').read_text())
                    self.assertEqual(snapshot['decision'],'workflow exited')
                finally:
                    if child.poll()is None:child.kill();child.wait()


if __name__=='__main__':unittest.main()
