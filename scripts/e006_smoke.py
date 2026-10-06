#!/usr/bin/env python3
"""Actual installed E006 driver contracts on tiny retained real DNA, no scoring.

Invoked with the new package Python outside the checkout. Both native scientific
arms run; no workers are mocked. Process fixtures exercise only the production
supervisor/scheduler. Mutation checks restore E006-only files and their mtimes.
"""
import argparse
import json
import os
from pathlib import Path
from shlex import quote
import subprocess
import sys

from dl_binner.contracts import file_record, write_json
from dl_binner.runner import FOLDERS, STAGES, receipt_name, validate_completed
from dl_binner.supervision import isolated_env, local_scheduler_options, progress, supervise


def frozen(root):
    """Snapshot completed scientific files and receipts, excluding append-only logs."""
    files = {}
    for data in validate_completed(root):
        stage = data['stage']; folder = root/FOLDERS[STAGES.index(stage)]
        for path in [root/receipt_name(stage), *[folder/name for name in data['files']]]:
            files[str(path.relative_to(root))] = dict(file_record(path), mtime_ns=path.stat().st_mtime_ns)
    return files


def suite(folder, workflow, bundle):
    """Run finite fresh/resume/tamper/native failure/resource/serial checks."""
    from dl_binner.io import read_fasta, load_arrays, read_depth
    folder.mkdir(parents=True, exist_ok=False)
    inputs = folder/'fixture inputs'; inputs.mkdir()
    for name in ('assembly.fna','mean-depth.tsv'):
        (inputs/name).write_bytes((bundle/'input'/name).read_bytes())
    fasta, depth = inputs/'assembly.fna', inputs/'mean-depth.tsv'
    rows = read_fasta(fasta); ids = [i for i,s in rows]
    assert len(rows)==13 and sum(len(s) for i,s in rows)==42311
    assert len(rows)<=32 and sum(len(s) for i,s in rows)<=600000
    cases = {}
    python = Path(sys.executable).absolute(); console = python.parent/'dl-binner'
    base = [python,'-I','-B','-m','dl_binner','run','--threads','4','--fasta',fasta,
            '--workflow-python',workflow,'--timeout','300','--memory-gb','8']
    def command(output, with_depth=False):
        return base+['--output',output]+(['--depth',depth] if with_depth else [])
    def check(argv, name, expected=0, needle=None):
        log = folder/(name+'.log')
        try:
            supervise(argv, log, 320, 8000000000, isolated_env(4))
        except RuntimeError:
            if expected==0: raise
        receipt = json.loads(log.with_suffix('.exit.json').read_text())
        text = log.read_text()
        assert receipt['exit_code']==expected and receipt['stop_reason'] is None, (name,receipt,text[-2000:])
        assert not needle or needle in text, (name,needle,text[-2000:])
        cases[name] = dict(receipt=receipt, log=file_record(log), intended_message=needle)
        progress('Contract passed: '+name)
    check([console,'run','--help'],'installed-console-help',needle='learned/bins/')
    seq, dep = folder/'sequence run', folder/'depth run'
    check([console,*command(seq)[5:]],'sequence-fresh')
    check(command(dep,True)+['--stop-after','train'],'depth-partial',needle='Paused after 2/8')
    partial = frozen(dep)
    check(command(dep,True)+['--resume'],'depth-partial-resume',needle='Verified 2/8')
    assert all(frozen(dep)[k]==v for k,v in partial.items())
    newest = max((dep/'logs').glob('invocation-*'), key=lambda p:p.stat().st_mtime_ns)
    assert not (newest/'01-features.native.log').exists() and not (newest/'02-train.native.log').exists()
    final = frozen(dep)
    check(command(dep,True)+['--resume'],'depth-completed-resume',needle='No feature extraction')
    assert final==frozen(dep)
    newest = max((dep/'logs').glob('invocation-*'), key=lambda p:p.stat().st_mtime_ns)
    assert not list(newest.glob('*.native.log'))
    check(command(dep,True),'fresh-populated-refusal',1,'populated')
    assert final==frozen(dep)
    summaries = {}
    for name, root in (('sequence',seq),('depth',dep)):
        stages = validate_completed(root); assert len(stages)==8
        assert all(a['end_monotonic_ns']<=b['start_monotonic_ns'] for a,b in zip(stages,stages[1:]))
        summary = json.loads((root/'run-summary.json').read_text()); assert summary['checkpoint_reload_exact']
        assert summary['scientific_quality_assessed'] is False
        data,_ = load_arrays(root/'features/features.npz','features')
        assert data['ids'].tolist()==ids
        if name=='depth':
            import numpy as np
            samples, expected = read_depth(depth,ids)
            assert samples==['software_S1','software_S2']
            assert np.array_equal(data['depth'],expected)
        training = json.loads((root/'training/checkpoint.json').read_text())
        assert training['config']['seed']==11 and training['config']['epochs']==20
        assert len(training['epochs'])==20 and all(v['contigs_seen']==10 for v in training['epochs'])
        assert training['numerical_threads']==4 and training['loader_workers']==0
        assert all(v['num_threads']<=4 for v in training['library_pools'])
        for arm in summary['arms'].values():
            assert sum(v['contigs'] for v in arm['statuses'].values())==13
            assert sum(v['bp'] for v in arm['statuses'].values())==42311
            assert len(arm['length_strata'])==6 and all(v['contigs']>0 for v in arm['length_strata'])
            assert arm['reasons']['excluded']=={'below_min_length':2,'no_valid_fourmers':1}
            assert arm['masks']['all_zero_depth_contigs']==(None if name=='sequence' else 3)
        summaries[name] = dict(summary=file_record(root/'run-summary.json'), arms=summary['arms'])
    # The same retained DNA subset exercises valid empty partitions explicitly.
    empty_fasta=inputs/'empty-partition.fna'
    empty_fasta.write_text(''.join(f'>{i}\n{s}\n' for i,s in (rows[0],rows[2],rows[4],rows[12])))
    empty_root=folder/'empty partition'
    check([python,'-I','-B','-m','dl_binner','run','--fasta',empty_fasta,'--workflow-python',workflow,
           '--output',empty_root,'--threads','4','--timeout','300'],'empty-partition')
    empty_summary=json.loads((empty_root/'run-summary.json').read_text())
    assert all(v['bin_count']==0 and v['statuses']['unassigned']['contigs']==2 and
               v['statuses']['excluded']['contigs']==2 for v in empty_summary['arms'].values())
    summaries['empty']=dict(summary=file_record(empty_root/'run-summary.json'),arms=empty_summary['arms'])
    for name, path, change, argv, needle in (
        ('changed-input',fasta,lambda b:b+b'\n',command(dep,True),'changed'),
        ('changed-sample-axis',depth,lambda b:b.replace(b'software_S1\tsoftware_S2',b'software_S2\tsoftware_S1'),command(dep,True),'changed'),
        ('corrupt-checkpoint',dep/'training/checkpoint.pt',lambda b:b+b'corrupt',command(dep,True),'bytes changed'),
        ('corrupt-export',dep/'raw/bins/assignments.tsv',lambda b:b+b'corrupt',command(dep,True),'bytes changed')):
        original, stat = path.read_bytes(), path.stat()
        try:
            path.write_bytes(change(original)); check(argv+['--resume'],name,1,needle)
        finally:
            path.write_bytes(original); os.utime(path,ns=(stat.st_atime_ns,stat.st_mtime_ns))
    for name, contents, needle in (
        ('invalid-fasta','>broken\nACGTZ\n','Empty/invalid IUPAC sequence: broken'),
        ('insufficient-evidence','>one\n'+rows[2][1]+'\n>short\nACGT\n','at least two eligible')):
        bad=inputs/(name+'.fna'); bad.write_text(contents)
        argv=[python,'-I','-B','-m','dl_binner','run','--fasta',bad,'--workflow-python',workflow,'--output',folder/name,'--timeout','300']
        check(argv,name,1,needle)
        assert not (folder/name/'raw').exists() and not (folder/name/'learned').exists()
        native = list((folder/name/'logs').glob('invocation-*/*.native.exit.json'))
        assert native and any(json.loads(p.read_text())['exit_code']==1 for p in native)
        assert cases[name]['receipt']['wall_seconds']<30, 'Fatal native failure did not stop promptly'
    incomplete_depth=inputs/'missing-depth.tsv'
    incomplete_depth.write_text('\n'.join(depth.read_text().splitlines()[:-1])+'\n')
    check([python,'-I','-B','-m','dl_binner','run','--fasta',fasta,'--depth',incomplete_depth,
           '--workflow-python',workflow,'--output',folder/'missing-depth','--threads','4','--timeout','300'],
          'missing-depth-axis',1,'Missing/extra depth IDs relative to assembly')
    assert not (folder/'missing-depth/training').exists()
    # A real CLI-wide timeout, not a generic nonzero exit or monitoring failure.
    check([python,'-I','-B','-m','dl_binner','run','--fasta',fasta,'--workflow-python',workflow,
           '--output',folder/'overall-timeout','--timeout','.3'],'overall-timeout',1,'wall-time limit')
    stops = [json.loads(p.read_text()) for p in (folder/'overall-timeout/logs').glob('invocation-*/*.exit.json')]
    assert any('wall-time limit' in (v['stop_reason'] or '') for v in stops)
    assert all('Cleanup failed' not in (v['stop_reason'] or '') for v in stops)
    # Native production process supervision: fatal orphan, heartbeat and RSS limit.
    for mode in ('fatal','memory','heartbeat'):
        log=folder/(mode+'-supervisor.log'); pidfile=folder/(mode+'.pid')
        code = 'import subprocess,sys,time,os; '
        if mode=='fatal':
            code += f'p=subprocess.Popen([sys.executable,"-I","-B","-c","import time; time.sleep(60)"]); open({str(pidfile)!r},"w").write(str(p.pid)); time.sleep(.4); print("intended fatal worker",flush=True); os._exit(7)'
        else: code += 'time.sleep('+('10.3' if mode=='heartbeat' else '60')+')'
        try:
            supervise([python,'-I','-B','-c',code],log,15,1 if mode=='memory' else 8000000000,isolated_env(4))
        except RuntimeError:
            assert mode!='heartbeat'
        value=json.loads(log.with_suffix('.exit.json').read_text())
        assert 'Cleanup failed' not in (value['stop_reason'] or '')
        if mode=='fatal':
            assert value['exit_code']==7 and value['stop_reason'] is None
            assert 'intended fatal worker' in log.read_text()
            result=subprocess.run(['ps','-p',pidfile.read_text(),'-o','stat='],capture_output=True,text=True)
            assert not result.stdout.strip() or result.stdout.strip().startswith('Z')
            assert value['wall_seconds']<5
        elif mode=='memory':
            assert 'MemoryError: Sampled working RSS' in value['stop_reason']
            assert value['peak_sampled_rss_bytes']>1 and value['wall_seconds']<5
        else: assert value['exit_code']==0 and value['stop_reason'] is None
        cases['supervisor-'+mode]=value
    # Ready independent rules verify actual CPU and global-memory placement.
    for name, threads in (('cpu',4),('memory',1)):
        schedule=folder/('scheduler-'+name); schedule.mkdir()
        worker=schedule/'worker.py'
        worker.write_text('import json,time,sys\nfrom pathlib import Path\ns=time.monotonic_ns()\ntime.sleep(.6)\nPath(sys.argv[1]).write_text(json.dumps(dict(start=s,end=time.monotonic_ns())))\n')
        snake=schedule/'Snakefile'
        shell=quote(str(python))+' -I -B '+quote(str(worker))+' {output:q}'
        snake.write_text("rule all:\n    input: 'a.json','b.json'\nrule worker:\n    output: '{name}.json'\n    threads: "+str(threads)+"\n    resources: mem_mb=8000\n    shell: "+repr(shell)+'\n')
        argv=[workflow,'-I','-B','-m','snakemake','--snakefile',snake,'--directory',schedule,
              *local_scheduler_options(4,8000),'--runtime-source-cache-path',schedule/'source-cache']
        check(argv,'scheduler-'+name)
        intervals=[json.loads((schedule/(v+'.json')).read_text()) for v in ('a','b')]
        assert min(v['end'] for v in intervals)<=max(v['start'] for v in intervals)
        cases['scheduler-'+name]['nonoverlapping_intervals']=intervals
    config=next((dep/'logs').glob('invocation-*/config.json'))
    check([workflow,'-I','-B','-m','snakemake','--snakefile',dep/'.workflow/run.smk','--configfile',config,
           '--directory',dep,*local_scheduler_options(4,8000),'--rerun-triggers','mtime','--ignore-incomplete',
           '--dry-run','--runtime-source-cache-path',dep/'.workflow/source-cache'],'completed-native-dag',needle='Nothing to be done')
    assert final==frozen(dep)
    write_json(folder/'observed.json',dict(status='passed',cases=cases,summary=summaries,
        fixture=dict(contigs=13,bp=42311,fasta=file_record(fasta),depth=file_record(depth)),
        workers_mocked=[],scope='Software contracts only; no MAG/quality or independent-generalization claim'))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output',type=Path,required=True); p.add_argument('--workflow-python',type=Path,required=True)
    p.add_argument('--bundle',type=Path,required=True); a=p.parse_args()
    suite(a.output.absolute(),a.workflow_python.absolute(),a.bundle.absolute())
