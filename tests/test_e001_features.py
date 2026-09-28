"""Portable integrity/driver tests and real Snakemake wiring, not native Linux evidence."""
import contextlib
import copy
import errno
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tarfile
import tempfile
import time
from types import SimpleNamespace
import unittest
from unittest.mock import patch

REPO=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(REPO/'scripts'))
import e001_features as f
import e001_review_multisample as review


class FeaturesTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name)

    def tearDown(self):
        self.temp.cleanup()

    def manifest(self):
        return f.read(f.EXP/'multisample-bam-manifest.json')

    def test_manifest_axes_and_seed_not_literal_sample_number(self):
        m=self.manifest();frozen=f.read(f.EXP/'frozen-inputs.json')
        f.validate_manifest(m,frozen)
        for mutate in (lambda x:x['samples'].reverse(),
                       lambda x:x['samples'][6]['summary'].update(thinning_seed=1009),
                       lambda x:x.update(reference_sha256='bad'),
                       lambda x:x['samples'][1].update(directory=x['samples'][0]['directory'])):
            changed=copy.deepcopy(m);mutate(changed)
            with self.assertRaises(ValueError):f.validate_manifest(changed,frozen)

    def test_resource_and_environment_limits(self):
        self.assertEqual(f.resource_plan(4,12)['worker_vcpus'],3)
        for args in ((3,12),(4,10)):
            with self.assertRaises(ValueError):f.resource_plan(*args)
        with patch.dict(os.environ,{'PYTHONPATH':'wrong','PYTHONHOME':'wrong','PYTHONUSERBASE':'wrong','SNAKEMAKE_PROFILE':'wrong'}):
            env=f.isolated_env(self.root,3)
        self.assertNotIn('PYTHONPATH',env);self.assertEqual(env['OMP_NUM_THREADS'],'3')
        self.assertTrue(env['PATH'].startswith(str(self.root/'bin')))

    def test_hardlinks_preserve_order_after_native_resolve_sort(self):
        # Opposite lexical source order is deliberate; native resolves paths.
        sources=[]
        for i in range(3):
            p=self.root/f'sample_{12-i}'/'mapped.bam';p.parent.mkdir();p.write_bytes(bytes([i])*12)
            Path(str(p)+'.bai').write_bytes(b'index');sources.append(p)
        dest=self.root/'aliases';dest.mkdir()
        for i,p in enumerate(sources):
            receipt=f.stage_bam(p,dest/f'{i:02d}-sample.bam',{'bytes':12,'sha256':f.sha(p)})
            self.assertEqual(receipt['mode'],'hardlink')
        ordered=sorted(p.resolve() for p in dest.glob('*.bam'))
        self.assertEqual([p.read_bytes()[0] for p in ordered],[0,1,2])
        with self.assertRaises(FileExistsError):f.stage_bam(sources[0],ordered[0],{'bytes':12,'sha256':f.sha(sources[0])})
        with self.assertRaisesRegex(ValueError,'BAM changed'):f.stage_bam(sources[0],dest/'bad',{'bytes':12,'sha256':'wrong'})

    def test_cross_filesystem_copy_and_unrelated_error(self):
        p=self.root/'mapped.bam';p.write_bytes(b'data');Path(str(p)+'.bai').write_bytes(b'index')
        receipt={'bytes':4,'sha256':f.sha(p)}
        with patch.object(f.os,'link',side_effect=OSError(errno.EXDEV,'cross device')):
            r=f.stage_bam(p,self.root/'copy.bam',receipt)
        self.assertEqual(r['mode'],'copy-cross-filesystem');self.assertEqual(p.read_bytes(),b'data')
        with patch.object(f.os,'link',side_effect=PermissionError(errno.EACCES,'denied')):
            with self.assertRaises(PermissionError):f.stage_bam(p,self.root/'denied',receipt)
        self.assertFalse((self.root/'denied').exists())

    def test_input_gate_real_tiny_bams_and_corruption(self):
        import pysam
        fasta=self.root/'canonical.fna';fasta.write_text('>a\n'+'A'*2500+'\n')
        samples=[]
        for i,s in enumerate((0,9)):
            folder=self.root/f'original_{s}';summary={'sample':s,'thinning_seed':1000+i,'thinning_fraction':.1}
            for c,n in (('C0',2),('CT',1)):
                p=folder/c/'mapped.bam';p.parent.mkdir(parents=True)
                with pysam.AlignmentFile(str(p),'wb',header={'HD':{'VN':'1.6','SO':'coordinate'},'SQ':[{'SN':'a','LN':2500}]}) as bam:
                    for j in range(n):
                        r=pysam.AlignedSegment();r.query_name=f'r{j}';r.query_sequence='A'*50;r.flag=0;r.reference_id=0;r.reference_start=j*100;r.mapping_quality=60;r.cigarstring='50M';bam.write(r)
                pysam.index(str(p));summary[c]={'records':n,'bytes':p.stat().st_size,'sha256':f.sha(p)}
            samples.append({'sample':s,'directory':str(folder),'summary':summary})
        m={'reference':str(fasta),'reference_sha256':f.sha(fasta),'samples':samples}
        manifest=self.root/'manifest.json';f.write(manifest,m)
        exp=self.root/'exp';exp.mkdir();f.write(exp/'frozen-inputs.json',{'samples':[0,9],'outputs':{'canonical.fna':f.sha(fasta)},'retained_contigs':1,'retained_bp':2500})
        stage=self.root/'run';stage.mkdir();cfg={'stage':str(stage),'manifest':str(manifest),'manifest_sha256':f.sha(manifest)}
        with patch.object(f,'EXP',exp):f.verify_inputs(cfg)
        r=f.read(stage/'inputs.json');self.assertEqual(r['samples'],[0,9]);self.assertEqual([Path(e['path']).name for e in r['bams']['C0']],['00-sample-0.bam','01-sample-9.bam'])
        bad=self.root/'bad';bad.mkdir();cfg['stage']=str(bad)
        # Alter the source; its accepted hash must stop the new attempt.
        p=Path(samples[0]['directory'])/'C0/mapped.bam';p.write_bytes(b'corrupt')
        with patch.object(f,'EXP',exp),self.assertRaisesRegex(ValueError,'BAM changed'):f.verify_inputs(cfg)
        self.assertFalse((bad/'inputs.json').exists())

    def test_native_depth_contract_and_scale(self):
        from e001lib.native import scale_metabat_depth
        p=self.root/'depth.tsv';p.write_text('contigName\tcontigLen\ttotalAvgDepth\t00\t00-var\t01\t01-var\na\t2500\t5\t10\t4\t0\t0\n')
        self.assertEqual(f.depth_report(p,{'a':2500},['00.bam','01.bam'])['zero_means_per_sample'],[0,1])
        scale_metabat_depth(p,self.root/'scaled.tsv',{'a':2500})
        self.assertIn('\t0.040000000000000008\t', (self.root/'scaled.tsv').read_text())
        with self.assertRaisesRegex(ValueError,'sample order'):f.depth_report(p,{'a':2500},['01.bam','00.bam'])
        p.write_text(p.read_text().replace('\t10\t4\t','\tnan\t4\t'))
        with self.assertRaisesRegex(ValueError,'Invalid depth'):f.depth_report(p,{'a':2500},['00.bam','01.bam'])

    def test_failed_prerequisite_repeated_driver_preserves_evidence(self):
        with patch.object(f.shutil,'disk_usage',return_value=SimpleNamespace(free=0)),contextlib.redirect_stdout(io.StringIO()),contextlib.redirect_stderr(io.StringIO()):
            for _ in range(2):self.assertEqual(f.run(self.root,self.root,self.root/'missing',4,12,self.root/'snapshot'),1)
        archives=list(self.root.glob('*-return.tar.gz'));self.assertEqual(len(archives),2)
        for p in archives:
            self.assertTrue(Path(str(p)+'.sha256').exists())
            with tarfile.open(p) as tar:self.assertTrue(any(m.name.endswith('failure.json') for m in tar))
        self.assertEqual(len(list(self.root.glob('multisample-features-*/status.json'))),2)

    def test_packaging_excludes_bams_and_large_arrays(self):
        stage=self.root/'attempt';stage.mkdir();(stage/'bams').mkdir();(stage/'bams/input.bam').write_bytes(b'bulk')
        (stage/'values.npy').write_bytes(b'bulk');f.write(stage/'result.json',{'pass':True})
        (stage/'escape.json').symlink_to(stage/'values.npy')
        with contextlib.redirect_stdout(io.StringIO()):f.package(stage)
        with tarfile.open(self.root/'attempt-return.tar.gz') as tar:self.assertEqual(tar.getnames(),['attempt/result.json'])
        checksum=Path(str(self.root/'attempt-return.tar.gz')+'.sha256')
        self.assertIn(f.sha(self.root/'attempt-return.tar.gz'),checksum.read_text())
        with self.assertRaisesRegex(ValueError,'overwrite'):
            with contextlib.redirect_stdout(io.StringIO()):f.package(stage)
        self.assertFalse(list(self.root.glob('*.partial')))

    def test_progress(self):
        log=self.root/'native.stdout';log.write_text('native stage\n');out=io.StringIO()
        with contextlib.redirect_stdout(out),f.progress(self.root,interval=.01,heartbeat=.02):time.sleep(.06)
        self.assertIn('native stage',out.getvalue());self.assertIn('RUNNING',out.getvalue())

    def test_actual_return_review_and_bad_checksum(self):
        p=REPO/'agent_context/multisample-preprocess-rau3rfod-return.tar.gz'
        if not p.exists():self.skipTest('Owner return not available')
        manifest,record=review.review(p,Path(str(p)+'.sha256'),REPO/'agent_context/e001-multisample.MrU4F7.log')
        self.assertEqual(record['manifest_sha256'],f.sha(f.EXP/'multisample-bam-manifest.json'))
        self.assertEqual(json.loads(manifest)['samples'][6]['sample'],9)
        bad=self.root/'checksum';bad.write_text('bad '+p.name)
        with self.assertRaisesRegex(ValueError,'checksum'):review.review(p,bad,REPO/'agent_context/e001-multisample.MrU4F7.log')

    def fixture_dag(self,fail=''):
        helper=self.root/'helper.py'
        helper.write_text('''import argparse,json,time
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--worker');p.add_argument('--config');a=p.parse_args()
c=json.loads(Path(a.config).read_text()); root=Path(c['stage']); mode=a.worker
with (root/'events.txt').open('a') as f:f.write(mode+'\\n')
if mode==c.get('fail'):raise RuntimeError('fixture native failure')
paths={'verify':'inputs.json','aggregate':'feature-summary.json'}
if mode not in paths: time.sleep(.05)
dest=root/paths.get(mode,mode+'/result.json');dest.parent.mkdir(exist_ok=True);dest.write_text('{}')
''')
        stage=self.root/'dag';stage.mkdir();reference=self.root/'ref';reference.write_text('fixture');manifest=self.root/'manifest';manifest.write_text('{}')
        cfg={'driver_python':sys.executable,'helper':str(helper),'runtime_config':str(stage/'runtime.json'),'stage':str(stage),
             'manifest':str(manifest),'reference':str(reference),'worker_vcpus':3,'worker_mem_mb':10000,'fail':fail}
        f.write(stage/'runtime.json',cfg)
        executable=REPO/'artifacts/e001-snakemake-test-env/bin/snakemake'
        if not executable.exists():self.skipTest('Pinned engine unavailable')
        cmd=f.workflow_command(executable,'snakemake',['--snakefile',REPO/'workflows/e001-preprocess/features.smk','--directory',stage,'--configfile',stage/'runtime.json','--cores',4,'--resources','mem_mb=11000','tool_slots=1','--keep-going','--benchmark-extended'],0)
        return stage,[str(a) for a in cmd]

    def test_real_dag_calls_actual_worker_with_engine_created_directories(self):
        stage,cmd=self.fixture_dag()
        cfg=f.read(stage/'runtime.json');cfg['root']=str(self.root);f.write(stage/'runtime.json',cfg)
        bedtools=self.root/'envs/comebin/bin/bedtools';bedtools.parent.mkdir(parents=True);bedtools.write_text('fixture')
        (self.root/'helper.py').write_text("""import argparse,json,sys
from pathlib import Path
sys.path.insert(0, SCRIPT_DIR)
import e001_features as f
p=argparse.ArgumentParser();p.add_argument('--worker');p.add_argument('--config');a=p.parse_args()
c=f.read(a.config);stage=Path(c['stage'])
def command(argv,env,out,label,timeout=None):
    if label=='bedtools-version':(out/'bedtools-version.stdout').write_text('bedtools v2.31.1')
    if label=='native':f.write(out/'result.json',{'fixture':True})
if a.worker in f.TOOLS:
    assert (stage/a.worker).is_dir(), 'engine should create output parent'
    f.rule_command=command
    f.worker(a.worker,c)
else:
    f.write(stage/('inputs.json' if a.worker=='verify' else 'feature-summary.json'),{})
""".replace('SCRIPT_DIR',repr(str(REPO/'scripts'))))
        result=subprocess.run(cmd,capture_output=True,text=True,timeout=120)
        self.assertEqual(result.returncode,0,result.stdout+result.stderr)
        for tool in f.TOOLS:self.assertTrue((stage/tool/'worker-started.json').is_file())

    def test_worker_rejects_previous_outputs_and_symlink(self):
        cfg={'stage':str(self.root),'root':str(self.root),'worker_vcpus':3,'runtime_config':'fixture'}
        (self.root/'vamb').mkdir();(self.root/'vamb/partial.npy').write_bytes(b'preserve')
        with patch.object(f,'rule_command') as command:
            with self.assertRaisesRegex(ValueError,'previous worker outputs'):f.worker('vamb',cfg)
            command.assert_not_called()
        (self.root/'metabat').symlink_to(self.root/'vamb',target_is_directory=True)
        with self.assertRaisesRegex(ValueError,'symlinked'):f.worker('metabat',cfg)
        self.assertEqual((self.root/'vamb/partial.npy').read_bytes(),b'preserve')

    def test_reuse_checks_hashes_and_real_dag_skips_accepted_work(self):
        stage,cmd=self.fixture_dag()
        previous=self.root/'previous';previous.mkdir();(previous/'vamb').mkdir();(previous/'metabat/C0').mkdir(parents=True)
        reference=self.root/'ref'
        bam=previous/'sample.bam';bam.write_bytes(b'bam');index=Path(str(bam)+'.bai');index.write_bytes(b'index')
        inputs={'manifest_sha256':'manifest','reference':str(reference),'reference_sha256':f.sha(reference),
                'bams':{'C0':[{'path':str(bam),'bytes':3,'sha256':f.sha(bam),'index_sha256':f.sha(index)}]}}
        f.write(previous/'inputs.json',inputs);f.write(previous/'status.json',{'exit_code':1})
        (previous/'vamb/feature.npy').write_bytes(b'feature')
        f.write(previous/'vamb/result.json',{'artifacts':{'feature.npy':{'sha256':f.sha(previous/'vamb/feature.npy')}}})
        (previous/'metabat/C0/depth.tsv').write_text('accepted table')
        record={'directory':str(previous),'reuse_sha256':{n:f.sha(previous/n) for n in ('inputs.json','status.json','vamb/result.json','metabat/C0/depth.tsv')}}
        exp=self.root/'exp';exp.mkdir();f.write(exp/'feature-partial-observed.json',record)
        cfg=f.read(stage/'runtime.json');cfg['manifest_sha256']='manifest'
        with patch.object(f,'EXP',exp):f.reuse_reviewed(stage,previous,cfg)
        f.write(stage/'runtime.json',cfg)
        result=subprocess.run(cmd,capture_output=True,text=True,timeout=120)
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertEqual(set((stage/'events.txt').read_text().splitlines()),{'metabat','comebin','aggregate'})
        self.assertEqual((previous/'vamb/feature.npy').read_bytes(),b'feature')
        (previous/'vamb/feature.npy').write_bytes(b'changed')
        new=self.root/'new';new.mkdir()
        with patch.object(f,'EXP',exp),self.assertRaisesRegex(ValueError,'VAMB artifact changed'):f.reuse_reviewed(new,previous,cfg)
        self.assertFalse((new/'inputs.json').exists())

    def test_completed_tools_are_not_rescheduled_after_recovery(self):
        stage,cmd=self.fixture_dag()
        previous=self.root/'completed';previous.mkdir()
        reference=self.root/'ref';f.write(previous/'inputs.json',{'manifest_sha256':'manifest','reference':str(reference),'reference_sha256':f.sha(reference),'bams':{}})
        f.write(previous/'status.json',{'exit_code':1})
        for tool in ('vamb','metabat'):
            (previous/tool).mkdir();(previous/tool/'features.tsv').write_text(tool)
            f.write(previous/tool/'result.json',{'artifacts':{'features.tsv':{'sha256':f.sha(previous/tool/'features.tsv')}}})
        record={'directory':str(previous),'completed_tools':['vamb','metabat'],
                'reuse_sha256':{n:f.sha(previous/n) for n in ('inputs.json','status.json','vamb/result.json','metabat/result.json')}}
        exp=self.root/'exp';exp.mkdir();f.write(exp/'feature-recovery-observed.json',record)
        cfg=f.read(stage/'runtime.json');cfg['manifest_sha256']='manifest'
        with patch.object(f,'EXP',exp):f.reuse_reviewed(stage,previous,cfg)
        f.write(stage/'runtime.json',cfg)
        result=subprocess.run(cmd,capture_output=True,text=True,timeout=120)
        self.assertEqual(result.returncode,0,result.stdout+result.stderr)
        self.assertEqual((stage/'events.txt').read_text().splitlines(),['comebin','aggregate'])
        self.assertFalse((stage/'bams').exists())

    def test_native_probe_emits_pre_site_and_import_diagnostics(self):
        result=subprocess.run([sys.executable,'-I','-S',str(REPO/'scripts/e001_native_probe.py'),sys.prefix,'numpy'],capture_output=True,text=True,timeout=30)
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertIn('PROBE: before site',result.stderr)
        self.assertIn('PROBE: ready numpy',result.stderr)

    def test_complete_owner_driver_with_real_engine_and_fixture_workers(self):
        # Only native/runtime probes are replaced; both dry-run and actual DAG execute.
        fixture,unused=self.fixture_dag()
        code=self.root/'code';(code/'scripts').mkdir(parents=True);(code/'workflows/e001-preprocess').mkdir(parents=True)
        (code/'scripts/e001_features.py').write_text((self.root/'helper.py').read_text())
        (code/'workflows/e001-preprocess/features.smk').write_text((REPO/'workflows/e001-preprocess/features.smk').read_text())
        (code/'SOURCE_COMMIT').write_text('fixture-source\n')
        exp=self.root/'exp';exp.mkdir()
        for name in ('feature-plan.json','config.json','frozen-inputs.json'):
            (exp/name).write_bytes((f.EXP/name).read_bytes())
        m=self.manifest();m['reference']=str(self.root/'ref')
        manifest=self.root/'accepted.json';f.write(manifest,m)
        f.write(exp/'multisample-preprocess-observed.json',{'manifest_sha256':f.sha(manifest)})
        inventory=self.root/'inventory';inventory.write_text('fixture inventory\n')
        f.write(exp/'sample0-preprocess-observed.json',{'member_sha256':{'workflow-lock.stdout':f.sha(inventory)}})
        def preflight(workflow,env,stage):
            (stage/'workflow-lock.stdout').write_bytes(inventory.read_bytes())
        original_invoke=f.invoke
        def invoke(command,env,stage,label,limit):
            if label=='workflow-prefix':
                (stage/'workflow-prefix.stdout').write_text('fixture prefix probe\n')
            else:original_invoke(command,env,stage,label,limit)
        with patch.object(f,'CODE',code),patch.object(f,'EXP',exp),patch.object(f,'ensure_git'), \
             patch.object(f,'stage_runtime',return_value=REPO/'artifacts/e001-snakemake-test-env'), \
             patch.object(f,'workflow_preflight',side_effect=preflight),patch.object(f,'invoke',side_effect=invoke), \
             contextlib.redirect_stdout(io.StringIO()),contextlib.redirect_stderr(io.StringIO()):
            for _ in range(2):self.assertEqual(f.run(self.root,self.root,manifest,4,12,self.root/'snapshot'),0)
        runs=list(self.root.glob('multisample-features-*/status.json'));self.assertEqual(len(runs),2)
        for p in runs:
            status=f.read(p);self.assertEqual(status['exit_code'],0)
            self.assertAlmostEqual(status['allocated_core_hours'],status['elapsed_seconds']*4/3600)
            self.assertTrue((p.parent/'feature-summary.json').exists())
            self.assertTrue((self.root/(p.parent.name+'-return.tar.gz.sha256')).exists())

    def test_rule_command_failure_and_timeout_records(self):
        with self.assertRaisesRegex(ValueError,'Native bad failed'):
            f.rule_command([sys.executable,'-c','raise SystemExit(7)'],f.isolated_env(),self.root,'bad',5)
        self.assertEqual(f.read(self.root/'bad.command.json')['returncode'],7)
        with self.assertRaises(subprocess.TimeoutExpired):
            f.rule_command([sys.executable,'-c','import time; time.sleep(10)'],f.isolated_env(),self.root,'timeout',.05)
        self.assertIn('error',f.read(self.root/'timeout.command.json'))
        self.assertIn('process_at_failure',f.read(self.root/'timeout.command.json'))

    def test_container_git_check_and_failure_stop(self):
        with patch.object(f.shutil,'which',return_value='/usr/bin/git'),patch.object(f,'invoke') as invoke:
            f.ensure_git({},self.root);invoke.assert_not_called()
        with patch.object(f.shutil,'which',return_value=None),patch.object(f.Path,'is_file',return_value=False):
            with self.assertRaisesRegex(ValueError,'no supported Ubuntu'):f.ensure_git({},self.root)

    def test_shell_wrapper_logs_success_and_failure(self):
        code=self.root/'shell-code';(code/'scripts').mkdir(parents=True)
        (code/'SOURCE_COMMIT').write_text('fixture\n')
        script=code/'scripts/e001_features_run.sh';script.write_text((REPO/'scripts/e001_features_run.sh').read_text())
        work=self.root/'work';(work/'transfer').mkdir(parents=True)
        bindir=self.root/'bin';bindir.mkdir()
        for name,body in (('uname','echo Linux'),('python3','echo "fixture owner call: $*"; exit "${FIXTURE_EXIT:-0}"')):
            p=bindir/name;p.write_text('#!/bin/sh\n'+body+'\n');p.chmod(0o755)
        # UCloud is GNU/Linux; BSD mktemp does not support GNU suffix templates.
        mktemp=bindir/'mktemp'
        mktemp.write_text('#!'+sys.executable+'\nimport os,sys,tempfile\nfrom pathlib import Path\np=Path(sys.argv[1]); fd,name=tempfile.mkstemp(prefix=p.name.split("XXXXXX")[0],suffix=".log",dir=p.parent);os.close(fd);print(name)\n')
        mktemp.chmod(0o755)
        env=dict(os.environ,PATH=str(bindir)+os.pathsep+os.environ['PATH'])
        cmd=['bash',str(script),str(work),str(self.root),'4','12']
        for status in (0,7):
            result=subprocess.run(cmd,env=dict(env,FIXTURE_EXIT=str(status)),text=True,capture_output=True)
            self.assertEqual(result.returncode,status,result.stderr)
        logs=list((work/'transfer').glob('*.log'));self.assertEqual(len(logs),2)
        self.assertTrue(all('fixture owner call' in p.read_text() and '--vcpus 4 --ram-gb 12' in p.read_text() for p in logs))

    def test_real_dag_success_rerun_no_work_and_extended_benchmarks(self):
        stage,cmd=self.fixture_dag()
        result=subprocess.run(cmd,capture_output=True,text=True,timeout=120)
        self.assertEqual(result.returncode,0,result.stdout+result.stderr)
        self.assertTrue((stage/'feature-summary.json').exists());events=(stage/'events.txt').read_text().splitlines()
        self.assertEqual(events[0],'verify');self.assertEqual(events[-1],'aggregate');self.assertEqual(set(events[1:-1]),set(f.TOOLS))
        self.assertEqual(len(list((stage/'benchmarks').glob('*.tsv'))),4)
        self.assertIn('cpu_time',(stage/'benchmarks/comebin.tsv').read_text())
        result=subprocess.run(cmd,capture_output=True,text=True,timeout=120)
        self.assertEqual(result.returncode,0,result.stderr);self.assertEqual((stage/'events.txt').read_text().splitlines(),events)

    def test_real_dag_tool_failure_keeps_other_tools_blocks_aggregate(self):
        stage,cmd=self.fixture_dag('vamb')
        result=subprocess.run(cmd,capture_output=True,text=True,timeout=120)
        self.assertNotEqual(result.returncode,0)
        self.assertTrue((stage/'metabat/result.json').exists());self.assertTrue((stage/'comebin/result.json').exists())
        self.assertFalse((stage/'feature-summary.json').exists())

    def test_real_dag_shared_input_failure_blocks_all_tools(self):
        stage,cmd=self.fixture_dag('verify')
        result=subprocess.run(cmd,capture_output=True,text=True,timeout=120)
        self.assertNotEqual(result.returncode,0);self.assertEqual((stage/'events.txt').read_text(),'verify\n')


if __name__=='__main__':unittest.main()
