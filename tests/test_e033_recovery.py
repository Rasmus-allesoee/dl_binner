"""Actual logging-only AST, long-report, source/plan and failed-worker return contracts."""
import contextlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time
import unittest
from unittest.mock import patch
ROOT=Path(__file__).absolute().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from e033_recovery import logging_only,DiskHistory,admit,upload,PRODUCT
from e033_resume import validate_config,seal_evidence,FIELDS
from e033_resume_launch import configuration,plan_value,render_setup,start_with_common_stop
from e021_control_json import publish,MAX_BYTES
from e024_coverage import binding


class Recovery(unittest.TestCase):
    def test_actual_provider_adapter_sets_duration_only_while_stopped(self):
        import datetime
        class Provider:
            """Model only the observed external GCP scheduling restriction."""
            def __init__(self,delay):self.delay=delay;self.phase='TERMINATED';self.schedule={};self.calls=[]
            def call(self,argv,zone):
                self.calls.append(argv[2])
                if argv[2]=='set-scheduling':
                    if self.phase!='TERMINATED':raise RuntimeError('Max run duration cannot be changed while running')
                    seconds=int(next(a for a in argv if a.startswith('--max-run-duration=')).split('=')[1][:-1])
                    self.schedule=dict(maxRunDuration=dict(seconds=str(seconds)),instanceTerminationAction='STOP',automaticRestart=False)
                elif argv[2]=='start':self.phase='RUNNING'
                else:raise AssertionError('Unexpected provider mutation')
            def state(self):
                return dict(status=self.phase,scheduling=self.schedule,lastStartTimestamp=datetime.datetime.fromtimestamp(1000+self.delay,datetime.timezone.utc).isoformat())
        clock=dict(deadline_epoch=100000,provider_deadline_epoch=100900)
        p=Provider(80);live,start,stop=start_with_common_stop(p,clock,now=1000)
        self.assertEqual(p.calls,['set-scheduling','start']);self.assertEqual(start,1080)
        self.assertLessEqual(stop,clock['provider_deadline_epoch']);self.assertGreater(stop,clock['deadline_epoch'])
        with self.assertRaisesRegex(ValueError,'STOP window'):start_with_common_stop(Provider(350),clock,now=1000)

    def test_actual_fixed_product_AST_preserves_every_nonlogging_statement(self):
        before=subprocess.check_output(['git','show','c812eb8:'+PRODUCT],cwd=ROOT,text=True)
        after=(ROOT/PRODUCT).read_text();self.assertTrue(logging_only(before,after))
        with self.assertRaisesRegex(ValueError,'more than'):
            logging_only(before,after.replace('torch.manual_seed(11)','torch.manual_seed(12)',1))
        lock,files,candidate=admit();self.assertEqual(len(files),122)
        self.assertEqual(json.loads(candidate.read_text())['learning_policy'],json.loads((ROOT/'experiments/E033-multiscale-bam/candidate-lock.json').read_text())['learning_policy'])

    def test_actual_large_history_writer_small_immutable_completion_and_failure_close(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);(root/'logs').mkdir()
            c=dict(root=str(root),initial_filesystem_used_bytes=24576,initial_filesystem_device=root.stat().st_dev,
                   source_filesystem=str(root),task_filesystem=str(root))
            h=DiskHistory(c);h.file=h.path.open('x')
            row=dict(epoch=1793840000.123,task_used=2000000000,task_free=90000000000,source_free=28000000000)
            # More than the full 30-hour recovery at one sample per two seconds.
            for i in range(55000):h.record(dict(row,epoch=row['epoch']+i*2))
            # Mock only external device counters; serialization/closure/publication are real.
            usage=shutil._ntuple_diskusage(100*1024**3,2*1024**3,98*1024**3)
            with patch('shutil.disk_usage',return_value=usage):summary=h.close()
            self.assertGreater(h.path.stat().st_size,MAX_BYTES);self.assertIsNone(summary['monitor_error'])
            target=root/'completion.json';publish(dict(status='SUCCESS',filesystem=summary),target)
            self.assertLess(target.stat().st_size,MAX_BYTES)
            self.assertEqual(len(h.path.read_text().splitlines()),55001)
            self.assertEqual(summary['history'],binding(h.path))
            self.assertFalse(hasattr(h,'samples'))
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);(root/'logs').mkdir();c.update(root=str(root),source_filesystem=str(root),task_filesystem=str(root),initial_filesystem_device=root.stat().st_dev)
            h=DiskHistory(c);h.file=h.path.open('x')
            with patch('shutil.disk_usage',return_value=shutil._ntuple_diskusage(100,99,1)):summary=h.close()
            self.assertIn('reserve failed',summary['monitor_error']);self.assertTrue(h.path.is_file());self.assertIsNone(h.file)

    def test_complete_actual_config_plan_readback_and_rendered_consumers(self):
        b=ROOT/'artifacts/e033-multiscale-bam/recovery-20261105';f=json.loads((b/'financial-gate.json').read_text());clock=json.loads((b/'common-clock.json').read_text());now=time.time()
        ident=dict(root='/srv/dl_binner/experiments/e033/resume-tiny',source='a'*40,start=now,
            provider_deadline=clock['provider_deadline_epoch']-.5,service_name='e033-resume-tiny',archive_prefix='gs://dl-binner-archive-167650584170/e033/resume-tiny/')
        c=configuration(ident,f,clock);self.assertEqual(set(c),FIELDS);validate_config(c)
        for name in FIELDS:
            bad=dict(c);bad.pop(name)
            with self.assertRaises(ValueError):validate_config(bad)
        code=render_setup(c,next((b/'build-r2/dist').glob('*.whl')));compile(code,'actual-native-setup','exec')
        self.assertIn("write_metadata(root/'config.json',c)",code)
        self.assertNotIn('mkfs',code)
        plan=plan_value(c);self.assertEqual(plan['measurements']['E009']['bank'],c['task_filesystem']+'/measurements/E009')
        self.assertEqual(plan['limits']['threads'],4)
        # Localize only the external repository mount; native producer paths
        # remain checked in the rendered Linux consumer above.
        plan['recovery']['lock']=str(ROOT/'experiments/E033-multiscale-bam/repair-lock.json')
        with tempfile.TemporaryDirectory() as folder:
            at=Path(folder);p=at/'plan.json';p.write_text(json.dumps(plan));release=at/'release.json';release.write_text(json.dumps(dict(plan=binding(p))))
            from e033_control import read_plan
            with patch.dict(os.environ,{'E033_RELEASE_FILE':str(release)}):self.assertEqual(read_plan(p),plan)
            plan['limits']['threads']=1;p.write_text(json.dumps(plan));release.write_text(json.dumps(dict(plan=binding(p))))
            with patch.dict(os.environ,{'E033_RELEASE_FILE':str(release)}),self.assertRaisesRegex(ValueError,'limits'):read_plan(p)
        p=subprocess.run([sys.executable,'-I','-B',str(ROOT/'scripts/e033_resume_arm.py'),'--help'],cwd='/private/tmp',capture_output=True,text=True)
        self.assertEqual(p.returncode,0,p.stderr)

    def test_actual_first_worker_failure_and_live_history_return_selection(self):
        with tempfile.TemporaryDirectory() as folder:
            at=Path(folder);root=at/'phase';work=at/'work';(root/'logs').mkdir(parents=True);(root/'gates').mkdir();(work/'logs').mkdir(parents=True)
            (root/'logs/closed-science.log').write_text('scheduler failure')
            (root/'logs/filesystem.jsonl').write_text('LIVE_MUST_NOT_COPY')
            (work/'logs/teacher.log').write_text('ACTUAL_WORKER_CAUSE')
            out=seal_evidence(root,dict(work=str(work)))
            self.assertEqual((out/'workflow-logs/teacher.log').read_text(),'ACTUAL_WORKER_CAUSE')
            self.assertFalse((out/'logs/filesystem.jsonl').exists())

    def test_oversized_upload_is_refused_before_network_or_whole_hash(self):
        with tempfile.TemporaryDirectory() as folder:
            p=Path(folder)/'oversized'
            with p.open('wb') as f:f.truncate(3*1024**3+1)
            with self.assertRaisesRegex(ValueError,'Bounded new private'):upload(p,'gs://dl-binner-archive-167650584170/e033/test/oversized')


if __name__=='__main__':unittest.main()
