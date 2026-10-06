"""Meaningful installed-command accounting, scheduler and supervisor contracts."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from dl_binner.accounting import check_files, file_record, summarize_arm
from dl_binner import clustering, io
from dl_binner.runner import source_records
from dl_binner.supervision import isolated_env, local_scheduler_options, supervise

ROOT = Path(__file__).resolve().parents[1]


class GenericContracts(unittest.TestCase):
    def test_packaged_defaults_and_scheduler_contract(self):
        from dl_binner.runner import PACKAGE
        self.assertEqual((PACKAGE/'resources/training.json').read_bytes(),
                         (ROOT/'experiments/E004-first-binner/training.json').read_bytes())
        self.assertIn('resources/run.smk', source_records())
        options = local_scheduler_options(4, 8000)
        self.assertNotIn('--jobs', options)
        self.assertIn('mem_mb=global', options)
        for threads, memory in ((0,8000), (5,8000), (4,0), (4,8001)):
            with self.assertRaises(ValueError): local_scheduler_options(threads, memory)

    def test_inventory_detects_bytes_links_and_escape(self):
        with tempfile.TemporaryDirectory() as name:
            folder = Path(name); path = folder/'valid'; path.write_text('one')
            entry = file_record(path)
            check_files(folder, {'valid':entry})
            path.write_text('two')
            with self.assertRaisesRegex(ValueError, 'bytes changed'): check_files(folder, {'valid':entry})
            path.unlink(); path.symlink_to(folder/'elsewhere')
            with self.assertRaises(ValueError): check_files(folder, {'valid':entry})
            with self.assertRaises(ValueError): check_files(folder, {'../outside':entry})

    def test_real_e005_retained_accounting_without_science(self):
        root = ROOT/'artifacts/e005-linux-pilot/returned/gi-pilot-b9k3j2r3/gi-pilot-b9k3j2r3/pilot'
        for arm, expected in (('raw',(113,798,3414,1097,4837013)), ('learned',(51,3891,321,1097,11831674))):
            summary, sources = summarize_arm(root/'features.npz', root/f'{arm}.export')
            actual = (summary['bin_count'], *(summary['statuses'][s]['contigs'] for s in ('assigned','unassigned','excluded')),
                      summary['statuses']['assigned']['bp'])
            self.assertEqual(actual, expected)
            self.assertEqual(len(summary['length_strata']),6)
            self.assertEqual(summary['masks']['all_zero_depth_contigs'],1353)
            self.assertEqual(sum(s['bp'] for s in summary['length_strata']),12924259)
            self.assertTrue(sources)
            self.assertNotIn('r95',summary)

    def test_empty_partition_strata_reasons_and_semantic_corruption(self):
        with tempfile.TemporaryDirectory() as name:
            root = Path(name); fasta = root/'tiny.fna'
            fasta.write_text('>short\nACGT\n>ambiguous\nNNNNNNNN\n>eligible\nACGTACGT\n')
            features = root/'features.npz'; io.prepare(fasta, features, min_length=5)
            partition = root/'partition.json'
            labels = dict(ids=['short','ambiguous','eligible'],parent_features_sha256=io.digest(features),
                          assignment=[-1,-1,-1],valid=[False,False,True],reason=['zero_geometry_evidence','zero_geometry_evidence','isolated_graph'],clusters=0,unassigned=3)
            partition.write_text(json.dumps(labels))
            clustering.export(features,partition,fasta,root/'bins')
            summary, _ = summarize_arm(features,root/'bins')
            self.assertEqual(summary['bin_count'],0)
            self.assertIsNone(summary['bin_size_bp']['median'])
            self.assertIsNone(summary['masks']['all_zero_depth_contigs'])
            self.assertEqual(summary['reasons']['excluded'],{'below_min_length':1,'no_valid_fourmers':1})
            table = root/'bins/assignments.tsv'
            table.write_text(table.read_text().replace('no_valid_fourmers','false_reason'))
            manifest = root/'bins/manifest.json'; value = json.loads(manifest.read_text())
            value['files']['assignments.tsv']=file_record(table); manifest.write_text(json.dumps(value))
            with self.assertRaisesRegex(ValueError,'Exclusion reason'): summarize_arm(features,root/'bins')

    def test_cli_actionable_help_and_resource_limits(self):
        env = isolated_env(4)
        result = subprocess.run([sys.executable,'-I','-B','-m','dl_binner','run','--help'],
                                env=env,capture_output=True,text=True,timeout=10)
        self.assertEqual(result.returncode,0)
        for term in ('--resume','--workflow-python','learned/bins','--timeout','--threads'):
            self.assertIn(term,result.stdout)
        for flag, value in (('--threads','5'),('--timeout','nan'),('--timeout','7201'),('--memory-gb','9')):
            result = subprocess.run([sys.executable,'-I','-B','-m','dl_binner','run','--fasta','unused',
                '--output','unused','--workflow-python',sys.executable,flag,value],env=env,capture_output=True,text=True,timeout=10)
            self.assertEqual(result.returncode,2)
            self.assertIn(flag,result.stderr)

    def test_actual_supervisor_timeout_and_fatal_orphan_cleanup(self):
        with tempfile.TemporaryDirectory() as name:
            root=Path(name)
            for mode in ('timeout','fatal'):
                pidfile=root/(mode+'.pid')
                child='import time; time.sleep(60)'
                code=f'import subprocess,sys,time,os; p=subprocess.Popen([sys.executable,"-I","-B","-c",{child!r}]); open({str(pidfile)!r},"w").write(str(p.pid)); '+('time.sleep(60)' if mode=='timeout' else 'print("intended fatal worker",flush=True); os._exit(7)')
                log=root/(mode+'.log')
                with self.assertRaises(RuntimeError): supervise([sys.executable,'-I','-B','-c',code],log,
                    .8 if mode=='timeout' else 10,8000000000,isolated_env(4))
                receipt=json.loads(log.with_suffix('.exit.json').read_text())
                if mode=='timeout': self.assertIn('wall-time',receipt['stop_reason'])
                else:
                    self.assertEqual(receipt['exit_code'],7)
                    self.assertIn('intended fatal worker',log.read_text())
                self.assertLess(receipt['wall_seconds'],5)
                pid=int(pidfile.read_text())
                result=subprocess.run(['ps','-p',str(pid),'-o','stat='],capture_output=True,text=True)
                self.assertTrue(not result.stdout.strip() or result.stdout.strip().startswith('Z'))


if __name__=='__main__': unittest.main()
