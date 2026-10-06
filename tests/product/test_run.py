"""Native installed CLI, strict resume and real scheduler/supervisor contracts.

Uses only generated software DNA and the separate workflow interpreter supplied
by DL_BINNER_WORKFLOW_PYTHON. Required paths are never skipped or mocked. Set
DL_BINNER_TEST_OUTPUT to retain every command's logs/receipts and fixture outputs.
"""
import json
import os
from pathlib import Path
from shlex import quote
import subprocess
import sys
import tempfile
import unittest

import numpy as np
from dl_binner import io
from dl_binner.contracts import file_record, write_json
from dl_binner.runner import FOLDERS, STAGES, receipt_name, validate_completed
from dl_binner.supervision import isolated_env, local_scheduler_options, supervise
from fixtures import THREADS, write_fixture


def snapshot(root):
    """Bind completed files and mtimes; append-only invocation logs are separate."""
    values = {}
    for data in validate_completed(root):
        folder = root/FOLDERS[STAGES.index(data['stage'])]
        for path in [root/receipt_name(data['stage']), *[folder/n for n in data['files']]]:
            values[str(path.relative_to(root))] = dict(file_record(path), mtime_ns=path.stat().st_mtime_ns)
    return values


class NativeRunContracts(unittest.TestCase):
    def test_installed_run_resume_accounting_failures_and_resource_placement(self):
        workflow = os.environ.get('DL_BINNER_WORKFLOW_PYTHON')
        self.assertTrue(workflow, 'Supply the separate workflow interpreter; see scripts/test_product.py --help')
        workflow = Path(workflow).absolute()  # preserve lexical venv path
        self.assertTrue(workflow.is_file(), str(workflow))
        retained = os.environ.get('DL_BINNER_TEST_OUTPUT')
        if retained:
            root = Path(retained)/'native-run';root.mkdir(parents=True,exist_ok=False)
        else:
            temp = tempfile.TemporaryDirectory(prefix='dl-binner-native-')
            self.addCleanup(temp.cleanup);root=Path(temp.name)
        fasta,depth,rows=write_fixture(root/'fixture inputs')
        cases={};console=Path(sys.executable).parent/'dl-binner'
        base=[sys.executable,'-I','-B','-m','dl_binner','run','--fasta',fasta,'--workflow-python',workflow,
              '--threads',str(THREADS),'--memory-gb','8','--timeout','300']
        def command(output, coverage=False):
            return base+['--output',output]+(['--depth',depth] if coverage else [])
        def check(argv,name,expected=0,needle=None):
            log=root/(name+'.log')
            try:supervise(argv,log,320,8000000000,isolated_env(THREADS))
            except RuntimeError:
                if expected==0:raise
            value=json.loads(log.with_suffix('.exit.json').read_text())
            self.assertEqual(value['exit_code'],expected,(name,log.read_text()[-2500:]))
            self.assertIsNone(value['stop_reason'])
            if needle:self.assertIn(needle,log.read_text())
            cases[name]=dict(resources=value,log=file_record(log),intended_message=needle)
            print('PRODUCT contract passed: '+name,flush=True)
        check([console,'run','--help'],'console-help',needle='learned/bins/')
        seq,dep=root/'sequence run',root/'depth run'
        check([console,*command(seq)[5:]],'sequence-fresh')
        check(command(dep,True)+['--stop-after','train'],'depth-partial',needle='Paused after 2/8')
        partial=snapshot(dep)
        check(command(dep,True)+['--resume'],'depth-resume',needle='Verified 2/8')
        self.assertTrue(all(snapshot(dep)[k]==v for k,v in partial.items()))
        newest=max((dep/'logs').glob('invocation-*'),key=lambda p:p.stat().st_mtime_ns)
        self.assertEqual(sorted(p.name for p in newest.glob('*.native.log')),
                         [f'{i+1:02d}-{s}.native.log' for i,s in enumerate(STAGES) if i>=2])
        frozen=snapshot(dep)
        check(command(dep,True)+['--resume'],'completed-resume',needle='No feature extraction')
        self.assertEqual(frozen,snapshot(dep))
        newest=max((dep/'logs').glob('invocation-*'),key=lambda p:p.stat().st_mtime_ns)
        self.assertFalse(list(newest.glob('*.native.log')))
        check(command(dep,True),'fresh-refusal',1,'populated')
        summaries={}
        for name,directory in [('sequence',seq),('depth',dep)]:
            stages=validate_completed(directory)
            self.assertEqual(len(stages),8)
            self.assertTrue(all(a['end_monotonic_ns']<=b['start_monotonic_ns'] for a,b in zip(stages,stages[1:])))
            summary=json.loads((directory/'run-summary.json').read_text())
            self.assertTrue(summary['checkpoint_reload_exact']);self.assertFalse(summary['scientific_quality_assessed'])
            feature,meta=io.load_arrays(directory/'features/features.npz','features')
            self.assertEqual(feature['ids'].tolist(),[i for i,_ in rows])
            if name=='depth':
                samples,expected=io.read_depth(depth,feature['ids'].tolist())
                self.assertEqual(meta['samples'],samples);np.testing.assert_array_equal(feature['depth'],expected)
            for arm in ('raw','learned'):
                value=summary['arms'][arm]
                self.assertEqual(sum(v['contigs'] for v in value['statuses'].values()),13)
                self.assertEqual(sum(v['bp'] for v in value['statuses'].values()),42311)
                self.assertEqual(value['reasons']['excluded'],{'below_min_length':2,'no_valid_fourmers':1})
                self.assertEqual(value['masks']['all_zero_depth_contigs'],3 if name=='depth' else None)
                self.assertEqual(len(value['length_strata']),6)
                self.assertTrue(all(s['contigs']>0 for s in value['length_strata']))
                exported=[]
                for p in (directory/arm/'bins').glob('*.fna'):
                    if p.stat().st_size:exported.extend(io.read_fasta(p))
                self.assertEqual(len(exported),len(rows));self.assertEqual(dict(exported),dict(rows))
            summaries[name]=summary['arms']
        for name,path,alter,needle in (
            ('changed-fasta',fasta,lambda b:b+b'\n','changed'),
            ('changed-sample-order',depth,lambda b:b.replace(b'software_S1\tsoftware_S2',b'software_S2\tsoftware_S1'),'changed'),
            ('corrupt-checkpoint',dep/'training/checkpoint.pt',lambda b:b+b'bad','bytes changed'),
            ('corrupt-export',dep/'raw/bins/assignments.tsv',lambda b:b+b'bad','bytes changed')):
            original,stat=path.read_bytes(),path.stat()
            try:
                path.write_bytes(alter(original));check(command(dep,True)+['--resume'],name,1,needle)
            finally:path.write_bytes(original);os.utime(path,ns=(stat.st_atime_ns,stat.st_mtime_ns))
        extra=dep/'raw/bins/unexpected.txt'
        try:
            extra.write_text('unbound');check(command(dep,True)+['--resume'],'extra-output',1,'Unexpected published files')
        finally:extra.unlink()
        self.assertEqual(frozen,snapshot(dep))
        bad=root/'invalid.fna';bad.write_text('>broken\nACGTZ\n')
        check([*base[:5],'run','--fasta',bad,'--workflow-python',workflow,'--threads',str(THREADS),'--output',root/'invalid','--timeout','60'],
              'invalid-native',1,'Empty/invalid IUPAC sequence: broken')
        self.assertFalse((root/'invalid/training').exists())
        self.assertLess(cases['invalid-native']['resources']['wall_seconds'],30)
        check([*base[:5],'run','--fasta',fasta,'--workflow-python',workflow,'--threads',str(THREADS),'--output',root/'timeout','--timeout','.3'],
              'overall-timeout',1,'wall-time limit')
        stops=[json.loads(p.read_text()) for p in (root/'timeout/logs').glob('invocation-*/*.exit.json')]
        self.assertTrue(any('wall-time limit' in (v['stop_reason'] or '') for v in stops))
        self.assertTrue(all('Cleanup failed' not in (v['stop_reason'] or '') for v in stops))
        for flag,value in [('--threads','5'),('--memory-gb','9'),('--timeout','nan')]:
            result=subprocess.run([console,'run','--fasta','unused','--output','unused','--workflow-python',workflow,flag,value],
                                  env=isolated_env(THREADS),capture_output=True,text=True,timeout=15)
            self.assertEqual(result.returncode,2);self.assertIn(flag,result.stderr)
        for mode in ('fatal','memory','heartbeat'):
            log=root/(mode+'-supervisor.log');pidfile=root/(mode+'.pid')
            code='import subprocess,sys,time,os; '
            if mode=='fatal':
                code+=f'p=subprocess.Popen([sys.executable,"-I","-B","-c","import time; time.sleep(60)"]); open({str(pidfile)!r},"w").write(str(p.pid)); time.sleep(.4); print("intended fatal worker",flush=True); os._exit(7)'
            else:code+='time.sleep('+('10.3' if mode=='heartbeat' else '60')+')'
            try:supervise([sys.executable,'-I','-B','-c',code],log,15,1 if mode=='memory' else 8000000000,isolated_env(THREADS))
            except RuntimeError:
                if mode=='heartbeat':raise
            value=json.loads(log.with_suffix('.exit.json').read_text());cases['supervisor-'+mode]=value
            self.assertNotIn('Cleanup failed',value['stop_reason'] or '')
            if mode=='fatal':
                self.assertEqual(value['exit_code'],7);self.assertIsNone(value['stop_reason'])
                self.assertIn('intended fatal worker',log.read_text());self.assertLess(value['wall_seconds'],5)
                result=subprocess.run(['ps','-p',pidfile.read_text(),'-o','stat='],capture_output=True,text=True)
                state=result.stdout.strip();write_json(root/'orphan-status.json',dict(pid=int(pidfile.read_text()),state=state,returncode=result.returncode))
                self.assertTrue(not state or state.startswith('Z'))
            elif mode=='memory':
                self.assertIn('MemoryError: Sampled working RSS',value['stop_reason']);self.assertLess(value['wall_seconds'],5)
            else:self.assertEqual(value['exit_code'],0);self.assertGreater(value['wall_seconds'],10)
        for name,threads in [('cpu',THREADS),('memory',1)]:
            folder=root/('scheduler-'+name);folder.mkdir()
            worker=folder/'worker.py';worker.write_text('import json,time,sys\nfrom pathlib import Path\ns=time.monotonic_ns()\ntime.sleep(.6)\nPath(sys.argv[1]).write_text(json.dumps(dict(start=s,end=time.monotonic_ns())))\n')
            shell=quote(sys.executable)+' -I -B '+quote(str(worker))+' {output:q}'
            snake=folder/'Snakefile';snake.write_text("rule all:\n    input: 'a.json','b.json'\nrule worker:\n    output: '{name}.json'\n    threads: "+str(threads)+"\n    resources: mem_mb=8000\n    shell: "+repr(shell)+'\n')
            check([workflow,'-I','-B','-m','snakemake','--snakefile',snake,'--directory',folder,
                   *local_scheduler_options(THREADS,8000),'--runtime-source-cache-path',folder/'source-cache'],'scheduler-'+name)
            times=[json.loads((folder/(n+'.json')).read_text()) for n in ('a','b')]
            self.assertLessEqual(min(t['end'] for t in times),max(t['start'] for t in times))
            cases['scheduler-'+name]['intervals']=times
        write_json(root/'observed.json',dict(status='passed',scope='Synthetic software contracts only; no bin-quality result',
            fixture=dict(contigs=len(rows),bp=sum(len(s) for _,s in rows),fasta=file_record(fasta),depth=file_record(depth)),
            cases=cases,summary=summaries,completed_snapshot=frozen,workers_mocked=[]))


if __name__=='__main__':unittest.main()
