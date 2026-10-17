"""Real inert held-phase commands/collection; only cloud/host identity boundaries mocked."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest
from unittest.mock import patch
from collections import namedtuple
sys.path.insert(0,str(Path(__file__).absolute().parents[1]/'scripts'))
import e011_phase
import e009_exit_watchdog
from e009_common import binding
from e009_owner import supervisor


class HeldPhaseTests(unittest.TestCase):
    def test_actual_inert_children_seal_readback_and_failure_skips_successor(self):
        native=supervisor();real_read=Path.read_text;real_check=subprocess.check_output
        def read(path,*args,**kwargs):
            if str(path)=='/proc/sys/kernel/random/boot_id':return 'fixture-boot'
            if str(path)=='/proc/meminfo':return 'MemTotal: 33554432 kB\n'
            return real_read(path,*args,**kwargs)
        def check(argv,*args,**kwargs):
            if argv[:2]==['git','rev-parse']:return 'frozen-source\n'
            if argv[:2]==['git','status']:return ''
            return real_check(argv,*args,**kwargs)
        Usage=namedtuple('usage','total used free')
        for failure in [False,True]:
            with self.subTest(failure=failure),tempfile.TemporaryDirectory()as directory:
                p=Path(directory);phase=p/'phase';phase.mkdir();logs=phase/'logs';logs.mkdir();store=p/'store';store.mkdir()
                transport=p/'cloud-boundary.py';transport.write_text('''from pathlib import Path
import shutil,sys
a=[x for x in sys.argv[1:]if not x.startswith('--')];src,dst=a[a.index('cp')+1:]
def local(s):return Path(sys.argv[0]).parent/'store'/Path(s).name if s.startswith('gs://')else Path(s)
if dst.startswith('gs://')and local(dst).exists():raise ValueError('Remote overwrite refused')
shutil.copyfile(local(src),local(dst))
''')
                worker=p/'inert.py';worker.write_text('''from pathlib import Path
import sys
Path(sys.argv[1]).write_text('real inert child ran')
sys.exit(int(sys.argv[2]))
''')
                class ExternalTransport:
                    isolated_env=staticmethod(native.isolated_env)
                    def supervise(self,argv,*args,**kwargs):
                        if argv[0]=='/snap/bin/gcloud':argv=[sys.executable,'-I','-B',str(transport),*map(str,argv[1:])]
                        return native.supervise(argv,*args,**kwargs)
                identity=dict(pid=__import__('os').getpid(),start_ticks=17,command_sha256='fixture-command')
                (logs/'watchdog-live-before-release.json').write_text(json.dumps(dict(decision='workflow alive',expected_process=identity,boot_id='fixture-boot')))
                cfg=dict(phase_root=str(phase),phase_id='tiny-phase',source_commit='frozen-source',repo=str(p),
                    vm_start_epoch=time.time()-2,initial_filesystem_used_bytes=100,
                    archive_prefix='gs://inert-private/phase',release_file=str(phase/'release.json'),
                    stages=[dict(name='cpm',argv=[sys.executable,'-I','-B',str(worker),str(phase/'run/first'),str(7 if failure else 0)]),
                            dict(name='metabat-export',argv=[sys.executable,'-I','-B',str(worker),str(phase/'run/second'),'0'])])
                path=phase/'config.json';path.write_text(json.dumps(cfg))
                release=dict(phase_config=binding(path),credit_gate_passed=True,pending_usage_accounted=True,
                    watchdog_release_verified=True,provider_stop_seconds=2700,incremental_gross_ceiling_usd=1,
                    no_resource_change=True,storage_retention_extended=False,credit_valid_until_epoch=time.time()+9999,
                    storage_valid_until_epoch=time.time()+9999,covered_costs=['compute','disk','storage','network','operations'])
                (phase/'release.json').write_text(json.dumps(release))
                with patch.object(e011_phase,'supervisor',return_value=ExternalTransport()),patch.object(e011_phase,'publish'), \
                     patch.object(e011_phase.shutil,'disk_usage',return_value=Usage(80*1024**3,100,79*1024**3)), \
                     patch.object(e011_phase.os.path,'ismount',return_value=True),patch.object(e011_phase.os,'cpu_count',return_value=8), \
                     patch.object(e009_exit_watchdog,'identity',return_value=identity),patch.object(Path,'read_text',read), \
                     patch.object(subprocess,'check_output',check):
                    result=e011_phase.run(path)
                outcome=json.loads((phase/'completion.json').read_text())
                self.assertEqual(result,1 if failure else 0)
                self.assertTrue(outcome['cloud_collection_verified'])
                self.assertEqual((phase/'run/second').exists(),not failure)
                self.assertTrue((store/'completion.json').exists())
                receipt=json.loads((logs/'cpm.exit.json').read_text())
                self.assertEqual(receipt['exit_code'],7 if failure else 0)
                self.assertIsNone(receipt['stop_reason'])
                self.assertEqual(outcome['status'],'FAILED'if failure else'SUCCESS')
                self.assertLess(outcome['elapsed_since_VM_start_seconds'],1800)


if __name__=='__main__':unittest.main()
