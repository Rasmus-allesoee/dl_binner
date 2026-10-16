"""Exercise the held parent and real archive readers; substitute child/cloud boundaries.

No fit executes. Existing launcher and current-boot watchdog have separate native
contracts. The filesystem-capacity sensor is substituted for a tiny local fixture.
"""
from collections import namedtuple
import json
from pathlib import Path
import sys
import tarfile
import tempfile
import time
import unittest
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).absolute().parents[1]/'scripts'))
import e009_controls_phase as phase
from e009_common import binding


class HeldPhase(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.root=Path(self.tmp.name)
        self.work=self.root/'phase';self.work.mkdir();self.result=self.root/'controls'
        self.cfg={'phase_root':str(self.work),'controls_root':str(self.result),'vm_start_epoch':time.time(),
                  'initial_filesystem_used_bytes':100,'release_file':str(self.work/'release.json'),
                  'phase_id':'inert-test','source_commit':'fixture','launcher_argv':['inert-fixture'],
                  'archive_prefix':'gs://fixture/private-phase'}
        self.config=self.work/'config.json';self.objects={};self.launches=0;self.fail=False

    def write_config(self):
        self.config.write_text(json.dumps(self.cfg));Path(self.cfg['release_file']).write_text(json.dumps({'phase_config':binding(self.config)}))

    def supervise(self,argv,log,*args,**kwargs):
        Path(log).write_text('closed inert command\n')
        if argv==['inert-fixture']:
            self.launches+=1
            if self.fail:raise RuntimeError('intended inert launcher failure')
            self.result.mkdir();(self.result/'controls-evidence.tar.gz').write_bytes(b'closed fixture')
            (self.result/'controls-evidence.tar.gz.sha256').write_text(binding(self.result/'controls-evidence.tar.gz')['sha256'])
            (self.result/'phase-result.json').write_text(json.dumps({'status':'SUCCESS','four_arms_completed':True}))
        else:
            source,destination=map(str,argv[-3:-1])
            if source.startswith('gs://'):Path(destination).write_bytes(self.objects[source])
            else:self.objects[destination]=Path(source).read_bytes()
        return {'exit_code':0}

    def run_fixture(self):
        usage=namedtuple('Usage','total used free')(200*1024**3,100,100*1024**3)
        with patch.object(phase,'supervisor',return_value=self),patch.object(phase,'publish_status'),\
             patch('e009_controls_phase.shutil.disk_usage',return_value=usage):
            return phase.run(self.config)

    def isolated_env(self,threads):return {'FIXTURE':'no scientific child'}

    def test_one_release_success_closed_archive_and_private_readback(self):
        self.write_config();self.assertEqual(self.run_fixture(),0);self.assertEqual(self.launches,1)
        completed=json.loads(self.objects[self.cfg['archive_prefix']+'/completion.json'])
        self.assertTrue(completed['four_arms_completed']);self.assertTrue(completed['cloud_collection_verified'])
        with tarfile.open(self.work/'closure.tar.gz')as t:
            self.assertIn('attempt-controls.json',t.getnames());self.assertTrue(all(m.isfile()for m in t))
        with self.assertRaisesRegex(ValueError,'no retry'):self.run_fixture()
        self.assertEqual(self.launches,1)

    def test_failure_preserves_reason_without_successor_or_retry(self):
        self.fail=True;self.write_config();self.assertEqual(self.run_fixture(),1);self.assertEqual(self.launches,1)
        completed=json.loads(self.objects[self.cfg['archive_prefix']+'/completion.json'])
        self.assertEqual(completed['status'],'FAILED');self.assertIn('intended inert launcher failure',completed['error'])
        self.assertNotIn(self.cfg['archive_prefix']+'/controls-evidence.tar.gz',self.objects)

    def test_expired_boot_clock_and_wrong_release_never_launch(self):
        self.cfg['vm_start_epoch']=time.time()-14401;self.write_config()
        with self.assertRaisesRegex(ValueError,'phase clock'):self.run_fixture()
        self.assertEqual(self.launches,0)
        self.cfg['vm_start_epoch']=time.time();self.write_config()
        Path(self.cfg['release_file']).write_text(json.dumps({'phase_config':{}}))
        self.assertEqual(self.run_fixture(),1);self.assertEqual(self.launches,0)


if __name__=='__main__':unittest.main()
