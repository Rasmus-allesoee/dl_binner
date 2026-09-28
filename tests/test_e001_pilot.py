"""Real native parser contracts and executable orchestration tests, not Linux fits."""
import argparse
import ast
import json
import os
from pathlib import Path
import subprocess
import sys
import tarfile
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
        comebin=p.resources('comebin',8,24)
        self.assertEqual(comebin['threads'],8)
        self.assertEqual(comebin['comebin_threads']+comebin['comebin_loader_workers'],8)
        self.assertEqual(comebin['leiden_workers'],8)
        allocation=p.resources('metabat-vamb',4,12)
        self.assertEqual(allocation['threads'],4)
        self.assertEqual(allocation['metabat_threads'],4)
        self.assertEqual(allocation['vamb_threads']+allocation['vamb_loader_workers'],4)
        allocation['stage']=str(self.root)
        env=p.worker_environment(self.root,'metabat',allocation)
        self.assertEqual(env['OMP_NUM_THREADS'],'4')
        self.assertEqual(p.worker_environment(self.root,'vamb',allocation)['OMP_NUM_THREADS'],'1')
        metabat=p.metabat_command('/prefix/metabat2','ref.fa','depth.tsv','bins',allocation['metabat_threads'])
        self.assertEqual(metabat[metabat.index('-t')+1],'4')
        for group,cpu,ram in [('comebin',4,12),('metabat-vamb',2,6),('comebin',8,12)]:
            with self.assertRaises(ValueError): p.resources(group,cpu,ram)
        args=p.fit_arguments('vamb',self.root,self.root/'out',allocation['vamb_threads'])
        self.assertEqual(args[args.index('-p')+1],'3')
        self.assertEqual(args[args.index('-e')+1],'300')

    def test_actual_comebin_argument_parser(self):
        source=REPO/'agent_context/tools_repo/COMEBin/COMEBin/main.py'
        if not source.exists(): self.skipTest('Optional pinned source cache absent')
        tree=ast.parse(source.read_text()); fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='arguments')
        ns=dict(argparse=argparse,Path=Path,ver='pinned',DEFAULT_HMM_EVALUE=1e-5,DEFAULT_RANDOM_SEED=11)
        exec(compile(ast.Module(body=[fn],type_ignores=[]),str(source),'exec'),ns)
        with patch.object(sys,'argv',['comebin',*p.fit_arguments('comebin',self.root,self.root/'out',p.resources('comebin',8,24)['comebin_threads'])]):
            args=ns['arguments']()
        self.assertEqual((args.epochs,args.batch_size,args.n_views,args.num_threads),(200,1024,6,7))
        self.assertTrue(args.earlystop and args.addvars and args.vars_sqrt)
        self.assertEqual(args.device,'cpu')

    def test_pinned_comebin_loader_count_and_budget(self):
        source=REPO/'agent_context/tools_repo/COMEBin/COMEBin/train_CLmodel.py'
        if not source.exists(): self.skipTest('Optional native cache missing')
        tree=ast.parse(source.read_text())
        count=next(n.value.value for n in tree.body if isinstance(n,ast.Assign)
                   and any(isinstance(t,ast.Name) and t.id=='DATALOADER_WORKERS' for t in n.targets))
        cfg=p.resources('comebin',8,24)
        self.assertEqual(count,4)
        self.assertEqual(cfg['comebin_loader_workers'],1)
        self.assertEqual(cfg['comebin_threads']+cfg['comebin_loader_workers'],cfg['threads'])
        helper=ast.parse((REPO/'scripts/e001_pilot.py').read_text())
        fit=next(n for n in helper.body if isinstance(n,ast.FunctionDef) and n.name=='native_fit')
        self.assertIn('train_CLmodel.DATALOADER_WORKERS=cfg',ast.unparse(fit))
        smoke=next(n for n in helper.body if isinstance(n,ast.FunctionDef) and n.name=='native_comebin_ipc_smoke')
        self.assertIn('torch.utils.data.DataLoader',ast.unparse(smoke))

    def test_comebin_worker_temp_guards_and_failed_fit_stops_cluster(self):
        # Native executables are external here; this runs the production worker
        # that owns IPC paths, resource budgets, guards and downstream dispatch.
        cfg=dict(root=str(self.root),stage=str(self.root/'attempt'),runtime_config='runtime.json',
                 **p.resources('comebin',8,24))
        calls=[]
        def external(argv,env,out,label,seconds,*args,**kwargs):
            calls.append((label,env['TMPDIR'],seconds,kwargs))
            if label=='evaluate':p.write(out/'evaluation.json',{'status':'completed'})
        with patch.object(p,'checked',side_effect=external):p.worker(cfg,'comebin','C0')
        fit=next(x for x in calls if x[0]=='fit'); cluster=next(x for x in calls if x[0]=='cluster')
        self.assertEqual(fit[1],cluster[1]); self.assertEqual(Path(fit[1]).parent,Path('/tmp'))
        self.assertFalse(Path(fit[1]).exists()); self.assertEqual(fit[2],80*3600/8)
        self.assertEqual(fit[3]['projected_steps'],200)
        self.assertEqual(fit[3]['projection_vcpus'],8)
        self.assertEqual(cluster[2],15*3600/8)
        self.assertIn('comebin-ipc-smoke',[x[0] for x in calls])
        calls.clear()
        def failure(argv,env,out,label,seconds,*args,**kwargs):
            external(argv,env,out,label,seconds,*args,**kwargs)
            if label=='fit':raise RuntimeError('native worker failure')
        with patch.object(p,'checked',side_effect=failure),self.assertRaisesRegex(RuntimeError,'native worker failure'):
            p.worker(cfg,'comebin','CT')
        self.assertNotIn('cluster',[x[0] for x in calls])
        self.assertFalse(Path(calls[-1][1]).exists())

    def test_full_schedule_projection_counts_startup_once(self):
        code='import sys,time; time.sleep(.4); [print(f"NN training: epoch={i}/200 elapsed=0.010s",file=sys.stderr,flush=True) for i in (1,2,3)];time.sleep(.1)'
        with patch.object(p,'descendants',side_effect=lambda pid:[(pid,0)]):
            p.checked([sys.executable,'-c',code],p.isolated_env(),self.root,'project',5,
                      progress_pattern=r'NN training: epoch=(\d+)/.*?elapsed=(\d+(?:\.\d+)?)s',
                      projected_steps=200,projection_vcpus=8)
        rec=p.read(self.root/'project.command.json')
        self.assertGreater(rec['projected_full_schedule_seconds'],.4)
        self.assertLess(rec['projected_full_schedule_seconds'],5)
        self.assertLess(rec['projected_full_schedule_core_hours'],80)

    def test_package_failed_comebin_attempt_without_rerunning_or_mutating_it(self):
        stage=self.root/'paired-pilot-comebin-retained';stage.mkdir()
        (stage/'comebin/CT').mkdir(parents=True)
        p.write(stage/'runtime.json',{'stage':str(stage),'tools':['comebin']})
        p.write(stage/'status.json',{'exit_code':1,'packaging_failed':True})
        p.write(stage/'failure.json',{'traceback':'workflow failed'})
        (stage/'workflow.stderr').write_text('worker failed\n')
        p.write(stage/'comebin/CT/fit.command.json',{'returncode':1})
        (stage/'comebin/CT/fit.stderr').write_text('last retained epoch\n')
        before={x.relative_to(stage):x.read_bytes() for x in stage.rglob('*') if x.is_file()}
        result=subprocess.run([sys.executable,'-I',str(REPO/'scripts/e001_pilot.py'),
                               '--data-root',str(self.root),'--package-existing',str(stage)],
                              capture_output=True,text=True)
        self.assertEqual(result.returncode,0,result.stdout+result.stderr)
        archive=self.root/(stage.name+'-return.tar.gz')
        checksum=Path(str(archive)+'.sha256')
        self.assertTrue(archive.is_file());self.assertTrue(checksum.is_file())
        self.assertIn(str(archive),result.stdout)
        self.assertIn(p.sha(archive),checksum.read_text())
        with tarfile.open(archive) as tar:
            self.assertIn(stage.name+'/comebin/CT/fit.stderr',tar.getnames())
            self.assertIn(stage.name+'/workflow.stderr',tar.getnames())
        after={x.relative_to(stage):x.read_bytes() for x in stage.rglob('*') if x.is_file()}
        self.assertEqual(before,after)
        with self.assertRaisesRegex(ValueError,'direct child'):
            p.package_failed_attempt(stage,self.root/'elsewhere')

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

    def test_actual_pinned_vamb_loader_worker_budget(self):
        source=REPO/'agent_context/tools_repo/vamb/vamb/encode.py'
        if not source.exists(): self.skipTest('Optional pinned source cache absent')
        tree=ast.parse(source.read_text())
        loader=next(node for node in tree.body if isinstance(node,ast.FunctionDef) and node.name=='make_dataloader')
        assignments=[node for node in ast.walk(loader) if isinstance(node,ast.Assign)
                     and any(isinstance(target,ast.Name) and target.id=='n_workers' for target in node.targets)]
        self.assertEqual(len(assignments),1)
        self.assertEqual(ast.unparse(assignments[0].value),'4 if cuda else 1')
        self.assertTrue(any(isinstance(node,ast.keyword) and node.arg=='num_workers'
                            and isinstance(node.value,ast.Name) and node.value.id=='n_workers'
                            for node in ast.walk(loader)))

    def test_real_child_success_failure_timeout_and_repeat(self):
        env=p.isolated_env()
        with patch.object(p,'descendants',side_effect=lambda pid:[(pid,0)]):
            p.checked([sys.executable,'-c','print("native stream")'],env,self.root,'ok',5)
            self.assertIn('native stream',(self.root/'ok.stdout').read_text())
            with self.assertRaises(FileExistsError): p.checked([sys.executable,'-c','pass'],env,self.root,'ok',5)
            with self.assertRaisesRegex(ValueError,'failed'): p.checked([sys.executable,'-c','raise SystemExit(3)'],env,self.root,'fail',5)
            with self.assertRaisesRegex(ValueError,'ceiling'): p.checked([sys.executable,'-c','import time;time.sleep(20)'],env,self.root,'timeout',.1)
        self.assertIn('failure',p.read(self.root/'timeout.command.json'))

    def test_async_multiprocessing_traceback_stops_and_kills_child(self):
        child="import sys,threading,time; threading.Thread(target=lambda: (sys.stderr.write('Traceback (most recent call last):\\nOSError: AF_UNIX path too long\\n'),sys.stderr.flush()),daemon=True).start(); time.sleep(30)"
        start=__import__('time').monotonic()
        with patch.object(p,'descendants',side_effect=lambda pid:[(pid,0)]), \
             self.assertRaisesRegex(RuntimeError,'fatal stderr marker'):
            p.checked([sys.executable,'-c',child],p.isolated_env(),self.root,'feeder-failure',30,
                      fatal_markers=('OSError: AF_UNIX path too long',))
        self.assertLess(__import__('time').monotonic()-start,5)
        rec=p.read(self.root/'feeder-failure.command.json')
        self.assertIn('OSError: AF_UNIX path too long',rec['fatal_stderr_tail'])
        self.assertIsNotNone(rec['returncode'])

    def test_native_epoch_progress_and_stall_guard(self):
        env=p.isolated_env()
        code="import sys,time; print('Epoch: 1',file=sys.stderr,flush=True); time.sleep(.1); print('Epoch: 2',file=sys.stderr,flush=True)"
        with patch.object(p,'descendants',side_effect=lambda pid:[(pid,0)]):
            p.checked([sys.executable,'-c',code],env,self.root,'epochs',5,
                      progress_pattern=r'Epoch:\s*(\d+)',stall_seconds=2)
        progress=(self.root/'epochs.progress.log').read_text().splitlines()
        self.assertEqual([json.loads(x)['progress'] for x in progress],['1','2'])
        with patch.object(p,'descendants',side_effect=lambda pid:[(pid,0)]):
            with self.assertRaisesRegex(ValueError,'no native progress'):
                p.checked([sys.executable,'-c','import time;time.sleep(30)'],env,self.root,'stalled',5,
                          progress_pattern=r'Epoch:\s*(\d+)',stall_seconds=.1)

    def test_vamb_prefit_ipc_smoke_uses_unique_short_temp_and_runs_before_fits(self):
        root=self.root/'work'; stage=self.root/'attempt'; stage.mkdir()
        (stage/'runtime.json').write_text('{}')
        cfg={'stage':str(stage),'runtime_config':str(stage/'runtime.json'),
             'vamb_threads':3,'vamb_loader_workers':1}
        calls=[]
        def fake_invoke(argv,env,out,label,seconds):
            calls.append((label,list(map(str,argv)),env['TMPDIR']))
        def fake_checked(argv,env,out,label,seconds,memory_mb,**kwargs):
            calls.append((label,list(map(str,argv)),env['TMPDIR'],kwargs))
        with patch.object(p,'CODE',self.root/'code'),patch.object(p,'invoke',side_effect=fake_invoke), \
             patch.object(p,'checked',side_effect=fake_checked):
            p.preflight_vamb_ipc(root,stage,cfg)
            p.preflight_vamb_ipc(root,stage,cfg)
        self.assertEqual([x[0] for x in calls],['vamb-ipc-prefix','vamb-ipc-smoke']*2)
        paths=[calls[i][2] for i in (0,2)]
        self.assertNotEqual(paths[0],paths[1])
        self.assertTrue(all(Path(x).parent==Path('/tmp') and len(os.fsencode(x))<=40 for x in paths))
        smoke=calls[1]
        self.assertEqual(smoke[1][-2:],['--native','vamb-ipc-smoke'])
        self.assertEqual(smoke[3]['fatal_markers'],('OSError: AF_UNIX path too long',))
        self.assertTrue(all(not Path(x).exists() for x in paths))

    def test_native_ipc_smoke_uses_pinned_data_loader_not_training(self):
        source=REPO/'agent_context/tools_repo/vamb/vamb/encode.py'
        if not source.exists(): self.skipTest('Optional pinned source cache absent')
        src=ast.parse(source.read_text())
        loader=next(n for n in src.body if isinstance(n,ast.FunctionDef) and n.name=='make_dataloader')
        worker_assignment=next(n for n in ast.walk(loader) if isinstance(n,ast.Assign)
                               and any(isinstance(t,ast.Name) and t.id=='n_workers' for t in n.targets))
        self.assertEqual(ast.unparse(worker_assignment.value),'4 if cuda else 1')
        helper=ast.parse((REPO/'scripts/e001_pilot.py').read_text())
        smoke=next(n for n in helper.body if isinstance(n,ast.FunctionDef) and n.name=='native_vamb_ipc_smoke')
        source_text=ast.unparse(smoke)
        self.assertIn('make_dataloader',source_text)
        self.assertIn('list(loader)',source_text)
        self.assertNotIn('trainvae(',source_text)

    def test_short_private_ipc_directory(self):
        a=p.short_local_tmpdir();b=p.short_local_tmpdir()
        try:
            self.assertNotEqual(a,b)
            self.assertEqual(a.parent,Path('/tmp'))
            self.assertLessEqual(len(os.fsencode(str(a))),40)
            self.assertEqual(a.stat().st_mode & 0o777,0o700)
        finally:
            import shutil
            shutil.rmtree(a);shutil.rmtree(b)

    def test_memory_ceiling_and_descendant_cleanup(self):
        with patch.object(p,'descendants',side_effect=lambda pid:[(pid,1024)]):
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
              '--cores',4,'--runtime-source-cache-path',self.root/'.snakemake-source-cache',
              '--resources','mem_mb=11500','tool_slots=1','--benchmark-extended']
        command=p.workflow_command(executable,'snakemake',args,0)
        for _ in range(2):
            testenv=p.isolated_env(); testenv['TMPDIR']=str(self.root/'tmp');testenv['XDG_CACHE_HOME']=str(self.root/'cache')
            (self.root/'tmp').mkdir(exist_ok=True);(self.root/'cache').mkdir(exist_ok=True)
            r=subprocess.run(list(map(str,command)),capture_output=True,text=True,env=testenv)
            self.assertEqual(r.returncode,0,r.stdout+r.stderr)
        self.assertEqual((self.root/'order.txt').read_text().splitlines(),['metabat C0','metabat CT','vamb C0','vamb CT'])
        self.assertEqual(len(list((self.root/'benchmarks').glob('*.tsv'))),4)
        import csv
        for benchmark in (self.root/'benchmarks').glob('*.tsv'):
            with benchmark.open() as handle:
                self.assertEqual(next(csv.DictReader(handle,delimiter='\t'))['threads'],'4')

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
             patch.object(p,'verify_features',side_effect=verify),patch.object(p,'preflight_vamb_ipc'), \
             patch.object(p.shutil,'disk_usage',return_value=SimpleNamespace(free=40_000_000_000)):
            for _ in range(2):self.assertEqual(p.run(self.root,self.root,'metabat-vamb',4,12,self.root/'snapshot'),0)
            with patch.object(p,'verify_features',side_effect=ValueError('changed input')):
                self.assertEqual(p.run(self.root,self.root,'metabat-vamb',4,12,self.root/'snapshot'),1)
        attempts=[x for x in self.root.glob('paired-pilot-*') if x.is_dir()]
        self.assertEqual(len(attempts),3)
        self.assertEqual(sorted(p.read(x/'status.json')['exit_code'] for x in attempts),[0,0,1])
        self.assertEqual(len(list(self.root.glob('*-return.tar.gz.sha256'))),3)


if __name__=='__main__':unittest.main()
