"""Real native parser contracts and executable orchestration tests, not Linux fits."""
import argparse
import ast
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from types import SimpleNamespace
from unittest.mock import patch

REPO=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(REPO/'scripts'))
import e001_pilot as p


class PilotTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(); self.root=Path(self.temp.name)
    def tearDown(self): self.temp.cleanup()

    def test_allocation_and_native_schedules(self):
        self.assertEqual(p.resources('comebin',2,6)['threads'],2)
        for group,cpu,ram in [('comebin',4,12),('metabat-vamb',2,6),('comebin',2,4)]:
            with self.assertRaises(ValueError): p.resources(group,cpu,ram)
        self.assertNotIn('--epochs',p.fit_arguments('vamb',self.root,self.root/'out',3))

    def test_actual_comebin_argument_parser(self):
        source=REPO/'agent_context/tools_repo/COMEBin/COMEBin/main.py'
        if not source.exists(): self.skipTest('Optional pinned source cache absent')
        tree=ast.parse(source.read_text()); fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='arguments')
        ns=dict(argparse=argparse,Path=Path,ver='pinned',DEFAULT_HMM_EVALUE=1e-5,DEFAULT_RANDOM_SEED=11)
        exec(compile(ast.Module(body=[fn],type_ignores=[]),str(source),'exec'),ns)
        with patch.object(sys,'argv',['comebin',*p.fit_arguments('comebin',self.root,self.root/'out',2)]):
            args=ns['arguments']()
        self.assertEqual((args.epochs,args.batch_size,args.n_views,args.num_threads),(200,1024,6,2))
        self.assertTrue(args.earlystop and args.addvars and args.vars_sqrt)
        self.assertEqual(args.device,'cpu')

    def test_actual_vamb_argument_parser(self):
        source=REPO/'agent_context/tools_repo/vamb/vamb/__main__.py'
        if not source.exists(): self.skipTest('Optional pinned source cache absent')
        tree=ast.parse(source.read_text())
        funcs=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in
               ['add_help_arguments','add_general_arguments','add_composition_arguments','add_abundance_arguments','add_bin_output_arguments','add_vae_arguments','add_clustering_arguments']]
        ns=dict(argparse=argparse,Path=Path,os=os,DEFAULT_THREADS=3,vamb=SimpleNamespace(__version_str__="pinned"))
        exec(compile(ast.Module(body=funcs,type_ignores=[]),str(source),'exec'),ns)
        parser=argparse.ArgumentParser(add_help=False)
        for fn in funcs:
            if fn.name!='add_help_arguments': ns[fn.name](parser)
        args=parser.parse_args(p.fit_arguments('vamb',self.root,self.root/'out',3)[2:])
        self.assertEqual(args.nepochs,300)
        self.assertEqual(args.binsplit_separator,'')

    def test_real_child_success_failure_timeout_and_repeat(self):
        env=p.isolated_env()
        p.checked([sys.executable,'-c','print("native stream")'],env,self.root,'ok',5)
        self.assertIn('native stream',(self.root/'ok.stdout').read_text())
        with self.assertRaises(FileExistsError): p.checked([sys.executable,'-c','pass'],env,self.root,'ok',5)
        with self.assertRaisesRegex(ValueError,'failed'): p.checked([sys.executable,'-c','raise SystemExit(3)'],env,self.root,'fail',5)
        with self.assertRaisesRegex(ValueError,'ceiling'): p.checked([sys.executable,'-c','import time;time.sleep(20)'],env,self.root,'timeout',.1)
        self.assertIn('failure',p.read(self.root/'timeout.command.json'))

    def test_memory_ceiling_and_descendant_cleanup(self):
        code="import subprocess,sys,time; c=subprocess.Popen([sys.executable,'-c','import time;time.sleep(30)']); print(c.pid,flush=True); time.sleep(30)"
        with self.assertRaisesRegex(ValueError,'ceiling'):
            p.checked([sys.executable,'-c',code],p.isolated_env(),self.root,'tree',1)
        child=int((self.root/'tree.stdout').read_text())
        state=subprocess.run(['ps','-o','stat=','-p',str(child)],capture_output=True,text=True).stdout.strip()
        self.assertTrue(not state or state.startswith('Z'),state)
        with self.assertRaisesRegex(ValueError,'RAM ceiling'):
            p.checked([sys.executable,'-c','import time; time.sleep(30)'],p.isolated_env(),self.root,'memory',5,.001)

    def test_uploaded_feature_acceptance_and_bad_checksum(self):
        import e001_review_features as review
        archive=REPO/'agent_context/multisample-features-69_32jz9-return.tar.gz'
        if not archive.exists(): self.skipTest('Reviewed inbox archive not present')
        checksum=Path(str(archive)+'.sha256'); terminal=REPO/'agent_context/e001-features.3qiYVJ.log'
        observed=review.review(archive,checksum,terminal)
        self.assertEqual(observed,p.read(p.EXP/'features-observed.json'))
        wrong=self.root/'bad.sha256';wrong.write_text('0'*64+'  '+archive.name)
        with self.assertRaisesRegex(ValueError,'checksum mismatch'):review.review(archive,wrong,terminal)

    def test_corrupted_feature_stops_before_fit(self):
        exp=self.root/'exp'; exp.mkdir(); inp=self.root/'input'; inp.mkdir(); features=self.root/'features/metabat';features.mkdir(parents=True)
        (exp/'config.json').write_text('{}'); (inp/'canonical.fna').write_text('frozen')
        (features/'depth.tsv').write_text('original')
        p.write(exp/'frozen-inputs.json',dict(config_sha256=p.sha(exp/'config.json'),owner_input_directory=str(inp),outputs={'canonical.fna':p.sha(inp/'canonical.fna')}))
        p.write(exp/'features-observed.json',dict(status='accepted',directory=str(features.parent),results={'metabat':{'artifacts':{'depth.tsv':{'sha256':p.sha(features/'depth.tsv')}}}}))
        cfg=dict(tools=['metabat'],stage=str(self.root))
        with patch.object(p,'EXP',exp):
            p.verify_features(cfg)
            (features/'depth.tsv').write_text('corruption')
            with self.assertRaisesRegex(ValueError,'Changed accepted feature'):p.verify_features(cfg)

    def test_real_snakemake_dag_execution_and_resume(self):
        executable=REPO/'artifacts/e001-snakemake-test-env/bin/snakemake'
        if not executable.exists():self.skipTest('Local Snakemake not installed')
        # A stand-in isolates orchestration only; native CLI contracts above use
        # actual pinned parser code and are explicitly separate evidence.
        helper=self.root/'worker.py'
        helper.write_text('''import argparse,json,pathlib
p=argparse.ArgumentParser();p.add_argument('--config');p.add_argument('--tool');p.add_argument('--condition');p.add_argument('--worker',action='store_true');p.add_argument('--aggregate',action='store_true');a=p.parse_args()
c=json.load(open(a.config));root=pathlib.Path(c['stage'])
if a.aggregate:(root/'paired-summary.json').write_text('{}')
else:
 out=root/a.tool/a.condition/'retained.json';out.parent.mkdir(parents=True,exist_ok=True);out.write_text('{}')
 with (root/'order.txt').open('a') as f:f.write(a.tool+' '+a.condition+'\\n')
''')
        cfg=dict(stage=str(self.root),driver_python=sys.executable,helper=str(helper),runtime_config=str(self.root/'runtime.json'),**p.resources('metabat-vamb',4,12))
        p.write(self.root/'runtime.json',cfg);p.write(self.root/'verified.json',{})
        args=['--snakefile',REPO/'workflows/e001-preprocess/pilot.smk','--directory',self.root,'--configfile',self.root/'runtime.json',
              '--cores',4,'--resources','mem_mb=11500','tool_slots=1','--benchmark-extended']
        command=p.workflow_command(executable,'snakemake',args,0)
        for _ in range(2):
            r=subprocess.run(list(map(str,command)),capture_output=True,text=True,env=p.isolated_env())
            self.assertEqual(r.returncode,0,r.stdout+r.stderr)
        self.assertEqual((self.root/'order.txt').read_text().splitlines(),['metabat C0','metabat CT','vamb C0','vamb CT'])
        self.assertEqual(len(list((self.root/'benchmarks').glob('*.tsv'))),4)

    def test_complete_driver_packages_success_repeat_and_failed_prerequisite(self):
        import shutil
        executable=REPO/'artifacts/e001-snakemake-test-env/bin/snakemake'
        if not executable.exists():self.skipTest('Local Snakemake not installed')
        code=self.root/'code'; (code/'workflows/e001-preprocess').mkdir(parents=True)
        (code/'SOURCE_COMMIT').write_text('1'*40)
        (code/'scripts').mkdir()
        shutil.copyfile(REPO/'scripts/e001_native_probe.py',code/'scripts/e001_native_probe.py')
        shutil.copyfile(REPO/'workflows/e001-preprocess/pilot.smk',code/'workflows/e001-preprocess/pilot.smk')
        helper=code/'worker.py'
        helper.write_text("""import argparse,json,pathlib
p=argparse.ArgumentParser();p.add_argument('--config');p.add_argument('--tool');p.add_argument('--condition');p.add_argument('--worker',action='store_true');p.add_argument('--aggregate',action='store_true');a=p.parse_args();c=json.load(open(a.config));r=pathlib.Path(c['stage'])
if a.aggregate:(r/'paired-summary.json').write_text('{}')
else:
 o=r/a.tool/a.condition/'retained.json';o.parent.mkdir(parents=True,exist_ok=True);o.write_text('{}')
""")
        exp=self.root/'exp';exp.mkdir(); inv=self.root/'inventory';inv.write_text('test inventory')
        p.write(exp/'sample0-preprocess-observed.json',{'member_sha256':{'workflow-lock.stdout':p.sha(inv)}})
        def preflight(workflow,env,stage):shutil.copyfile(inv,stage/'workflow-lock.stdout')
        def verify(cfg):p.write(Path(cfg['stage'])/'verified.json',{})
        with patch.object(p,'CODE',code),patch.object(p,'EXP',exp),patch.object(p,'__file__',str(helper)), \
             patch.object(p,'stage_runtime',return_value=executable.parent.parent),patch.object(p,'workflow_preflight',side_effect=preflight), \
             patch.object(p,'verify_features',side_effect=verify),patch.object(p.shutil,'disk_usage',return_value=SimpleNamespace(free=40_000_000_000)):
            for _ in range(2):self.assertEqual(p.run(self.root,self.root,'metabat-vamb',4,12,self.root/'snapshot'),0)
            with patch.object(p,'verify_features',side_effect=ValueError('changed input')):
                self.assertEqual(p.run(self.root,self.root,'metabat-vamb',4,12,self.root/'snapshot'),1)
        attempts=[x for x in self.root.glob('paired-pilot-*') if x.is_dir()]
        self.assertEqual(len(attempts),3)
        self.assertEqual(sorted(p.read(x/'status.json')['exit_code'] for x in attempts),[0,0,1])
        self.assertEqual(len(list(self.root.glob('*-return.tar.gz.sha256'))),3)


if __name__=='__main__':unittest.main()
