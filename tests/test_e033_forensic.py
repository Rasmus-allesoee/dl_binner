"""Actual forensic schema/writer and closed failed-worker copy/pack contracts."""
import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest
ROOT=Path(__file__).absolute().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from e033_forensic import binding,collect,validate_config,write_metadata,FIELDS
from e033_forensic_launch import configuration,render_setup


def config():
    """Use the actual producer, with synthetic external financial admission only."""
    now=time.time();f=dict(coverage_status='PASS_FOR_SPECIFIED_ORDINARY_FIRST_PARTY_PRODUCTS_ONLY',real_money_authorized=False,checked_epoch=now,credit_checked_epoch=now,estimated_complete_gross_USD=15.65,ceiling_USD=20,collection_ceiling_USD=.25,storage_valid_until_epoch=1794351600,credit_valid_until_epoch=1799712000)
    return configuration(dict(root='/srv/dl_binner/experiments/e033/forensic-tiny',source='a'*40,start=now,service_name='e033-forensic-tiny',archive_prefix='gs://dl-binner-archive-167650584170/e033/forensic-tiny'),f)


class Forensic(unittest.TestCase):
    def test_complete_real_producer_consumer_and_exclusive_JSON_writer(self):
        c=config();self.assertEqual(set(c),FIELDS);validate_config(c);code=render_setup(c);compile(code,'actual-setup','exec')
        self.assertIn("write_metadata(root/'config.json',c)",code)
        for name in FIELDS:
            bad=dict(c);bad.pop(name)
            with self.assertRaises(ValueError):validate_config(bad)
        bad=dict(c,common_deadline_epoch=c['common_deadline_epoch']+1)
        with self.assertRaises(ValueError):validate_config(bad)
        bad=copy.deepcopy(c);bad['financial']['real_money_authorized']=True
        with self.assertRaises(ValueError):validate_config(bad)
        with tempfile.TemporaryDirectory() as folder:
            p=Path(folder)/'config.json';write_metadata(p,c);self.assertEqual(json.loads(p.read_text()),c);validate_config(json.loads(p.read_text()))
            self.assertTrue(p.read_bytes().endswith(b'\n'))
            with self.assertRaises(FileExistsError):write_metadata(p,c)

    def test_actual_closed_root_worker_barrier_copy_pack_and_no_science_inputs(self):
        from e033_collect import pack,verify
        with tempfile.TemporaryDirectory() as folder:
            at=Path(folder);original=at/'original';root=at/'new';root.mkdir();original.mkdir()
            for name,value in [('terminal.log','CONTROL_JSON_FAILURE'),('science-result.json','{"status":"FAILED"}'),('config.json','{}'),('task/work/logs/E009_noGLM_teacher.log','ACTUAL_NATIVE_TRACEBACK'),('task/work/barrier/done.json','{}'),('logs/last-upload.exit.json','{"exit_code":0}'),('task/work/benchmarks/teacher.tsv','s\tmax_rss\n1\t2\n'),('task/work/E009-noGLM/teacher/result/initial-state.json','{}'),('task/work/E009-noGLM/teacher/result/large-model.pt','NEVER_COPY'),('task/measurements/raw-moments.npy','NEVER_READ')]:
                p=original/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(value)
            before={str(p):binding(p) for p in original.rglob('*') if p.is_file()}
            result=collect(dict(root=str(root),original=str(original)),engineering=True)
            self.assertFalse(result['science_executed']);self.assertFalse(result['original_completion_present'])
            self.assertEqual((root/'closed/workflow/logs/E009_noGLM_teacher.log').read_text(),'ACTUAL_NATIVE_TRACEBACK')
            self.assertFalse(any(p.suffix in ['.pt','.npy'] for p in (root/'closed').rglob('*')))
            self.assertTrue(all(binding(p)==v for p,v in before.items()))
            evidence=root/'evidence';evidence.mkdir();(evidence/'fixture.json').write_text('{"engineering":true}')
            receipt=pack(root/'closed',evidence,root/'return');verify(root/'return/e033-evidence.tar.gz',receipt['archive'])
            inv=json.loads((root/'return/inventory.json').read_text());self.assertIn('workflow/logs/E009_noGLM_teacher.log',inv['all_work_members'])

    def test_missing_worker_oversize_and_symlink_refuse_without_proof(self):
        for case in ['missing','symlink','cap']:
            with self.subTest(case=case),tempfile.TemporaryDirectory() as folder:
                at=Path(folder);original=at/'original';root=at/'new';root.mkdir();original.mkdir()
                for n in ['terminal.log','science-result.json','config.json']:(original/n).write_text('{}')
                p=original/'task/work/logs/E009_noGLM_teacher.log';p.parent.mkdir(parents=True)
                if case=='symlink':p.symlink_to(original/'terminal.log')
                elif case=='cap':
                    with p.open('wb') as f:f.truncate(91*1024**2)
                with self.assertRaises(ValueError):collect(dict(root=str(root),original=str(original)),engineering=True)
                self.assertFalse((root/'closed/copy-proof.json').exists())

    def test_actual_transferred_armer_isolated_outside_checkout(self):
        with tempfile.TemporaryDirectory() as folder:
            at=Path(folder)
            for n in ['e033_forensic.py','e033_forensic_arm.py']:(at/n).write_bytes((ROOT/'scripts'/n).read_bytes())
            p=subprocess.run([sys.executable,'-I','-B',str(at/'e033_forensic_arm.py'),'--help'],cwd=at,capture_output=True,text=True)
            self.assertEqual(p.returncode,0,p.stderr);self.assertIn('--config',p.stdout)


if __name__=='__main__':unittest.main()
