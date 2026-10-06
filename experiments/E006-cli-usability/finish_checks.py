#!/usr/bin/env python3
"""Finish E006 from retained successes; test the corrected wheel, never rerun E005.

Integration-002 already passed the 13-contig native paths/resume/tamper checks.
Its malformed-input error was hidden by the scheduler trailer. Reuse all that
evidence; test the final error handler and resume on a new four-contig fixture.
"""
import argparse
import importlib.util
import json
from pathlib import Path
import subprocess
import sys

from dl_binner.contracts import file_record, write_json
from dl_binner.runner import PACKAGE, validate_completed
from dl_binner.supervision import isolated_env, local_scheduler_options, supervise

ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('e006_integrate',Path(__file__).with_name('integrate.py'))
helpers=importlib.util.module_from_spec(spec);spec.loader.exec_module(helpers)


def finish(folder, baseline, workflow):
    """Verify retained successful cases and run only remaining/final-wheel contracts."""
    folder,baseline,workflow=Path(folder).absolute(),Path(baseline).absolute(),Path(workflow).absolute()
    python=Path(sys.executable).absolute();cases={}
    reused={}
    for name in ('sequence','depth','partial'):
        path=baseline/name;data=json.loads((path/'run-manifest.json').read_text())
        for module in ('io.py','model.py','clustering.py'):
            assert data['source_files'][module]==file_record(PACKAGE/module)
        assert len(validate_completed(path))==8
        reused[name]=dict(locator=str(path),summary=file_record(path/'run-summary.json'),
                          stages=helpers.frozen(path),scientific_code_unchanged=True)
    passed=[line.split('Integration contract passed: ')[1] for line in (baseline/'integration.log').read_text().splitlines()
            if 'Integration contract passed: ' in line]
    assert len(passed)==16
    reused_logs={name:file_record(baseline/(name+'.log')) for name in passed}
    fasta0=baseline/'input/assembly.fna'
    from dl_binner.io import read_fasta
    rows=read_fasta(fasta0);chosen=[rows[i] for i in (0,2,4,12)]
    inputs=folder/'fixture inputs';inputs.mkdir()
    fasta=inputs/'tiny real.fna';fasta.write_text(''.join(f'>{i}\n{s}\n' for i,s in chosen))
    depth=inputs/'depth table.tsv'
    depth.write_text('contig_id\tsoftware_S1\tsoftware_S2\n'+''.join(f'{i}\t{v[0]}\t{v[1]}\n' for (i,_),v in zip(chosen,[(0,0),(1,0),(0,4),(0,0)])))
    run=folder/'tiny depth run'
    cmd=[python,'-I','-B','-m','dl_binner','run','--fasta',fasta,'--depth',depth,'--workflow-python',workflow,'--output',run]
    cases['final-console-help']=helpers.execute([python.parent/'dl-binner','run','--help'],folder,'final-console-help',contains='learned/bins/')
    cases['final-partial']=helpers.execute([python.parent/'dl-binner',*cmd[5:],'--stop-after','train'],folder,'final-partial',contains='Paused after 2/8')
    old=helpers.frozen(run)
    cases['final-partial-resume']=helpers.execute(cmd+['--resume'],folder,'final-partial-resume',contains='Verified 2/8')
    assert all(helpers.frozen(run)[k]==v for k,v in old.items())
    final=helpers.frozen(run)
    cases['final-completed-resume']=helpers.execute(cmd+['--resume'],folder,'final-completed-resume',contains='No feature extraction')
    assert helpers.frozen(run)==final
    cases['final-fresh-refusal']=helpers.execute(cmd,folder,'final-fresh-refusal',1,'populated')
    summary=json.loads((run/'run-summary.json').read_text())
    assert summary['checkpoint_reload_exact']
    assert all(v['bin_count']==0 and v['statuses']['unassigned']['contigs']==2 and
        v['statuses']['excluded']['contigs']==2 and v['masks']['all_zero_depth_contigs']==2 for v in summary['arms'].values())
    for name,path,change in (
        ('final-changed-depth',depth,lambda b:b.replace(b'software_S1\tsoftware_S2',b'software_S2\tsoftware_S1')),
        ('final-corrupt-output',run/'training/checkpoint.pt',lambda b:b+b'changed')):
        original=path.read_bytes()
        try:
            path.write_bytes(change(original))
            cases[name]=helpers.execute(cmd+['--resume'],folder,name,1,'changed')
        finally: path.write_bytes(original)
    for name,content,needle in (
        ('invalid-fasta','>broken\nACGTZ\n','Empty/invalid IUPAC sequence: broken'),
        ('insufficient-evidence','>one\n'+rows[2][1]+'\n>short\nACGT\n','at least two eligible')):
        bad=inputs/(name+'.fna');bad.write_text(content)
        args=[python,'-I','-B','-m','dl_binner','run','--fasta',bad,'--workflow-python',workflow,'--output',folder/name]
        cases[name]=helpers.execute(args,folder,name,1,needle)
        assert not (folder/name/'raw').exists() and not (folder/name/'learned').exists()
    cases['overall-timeout']=helpers.execute([python,'-I','-B','-m','dl_binner','run','--fasta',fasta,
        '--workflow-python',workflow,'--output',folder/'overall-timeout','--timeout','.3'],folder,'overall-timeout',1,'wall-time limit')
    for name,threads in (('cpu',4),('memory',1)):
        schedule=folder/('scheduler-'+name);schedule.mkdir()
        worker=schedule/'worker.py'
        worker.write_text('import json,time,sys\nfrom pathlib import Path\ns=time.monotonic_ns()\ntime.sleep(.6)\nPath(sys.argv[1]).write_text(json.dumps(dict(start=s,end=time.monotonic_ns())))\n')
        snake=schedule/'Snakefile'
        from shlex import quote
        shell=quote(str(python))+' -I -B '+quote(str(worker))+' {output:q}'
        snake.write_text("rule all:\n    input: 'a.json','b.json'\nrule worker:\n    output: '{name}.json'\n    threads: "+str(threads)+"\n    resources: mem_mb=8000\n    shell: "+repr(shell)+'\n')
        args=[workflow,'-I','-B','-m','snakemake','--snakefile',snake,'--directory',schedule,
            *local_scheduler_options(4,8000),'--runtime-source-cache-path',schedule/'source-cache']
        cases['scheduler-'+name]=helpers.execute(args,folder,'scheduler-'+name)
        timings=[json.loads((schedule/f'{v}.json').read_text()) for v in ('a','b')]
        assert min(t['end'] for t in timings)<=max(t['start'] for t in timings)
        cases['scheduler-'+name]['nonoverlapping_intervals']=timings
    cases['contracts']=helpers.execute([python,'-I','-B',ROOT/'tests/test_generic_run.py','-v'],folder,'contracts')
    config=next((run/'logs').glob('invocation-*/config.json'))
    args=[workflow,'-I','-B','-m','snakemake','--snakefile',run/'.workflow/run.smk','--configfile',config,
        '--directory',run,*local_scheduler_options(4,8000),'--rerun-triggers','mtime','--ignore-incomplete','--dry-run',
        '--runtime-source-cache-path',run/'.workflow/source-cache']
    cases['native-completed-dag']=helpers.execute(args,folder,'native-completed-dag',contains='Nothing to be done')
    write_json(folder/'observed.json',dict(status='passed',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        final_package_source={str(p.relative_to(PACKAGE)):file_record(p) for p in PACKAGE.rglob('*.py')},
        final_python=str(python),workflow_python=str(workflow),reused_baseline=reused,reused_passed_cases=passed,
        reused_case_log_hashes=reused_logs,cases=cases,fixture=dict(contigs=len(chosen),bp=sum(len(s) for _,s in chosen),
        fasta=file_record(fasta),depth=file_record(depth),source=file_record(fasta0)),
        scope='Native Mac wheel software contracts only; no E005 science rerun or generic Linux execution',
        native_workers_mocked=[],external_prerequisite_mock='One focused unavailable-ps regression; all scientific adapters execute natively',
        summary=file_record(run/'run-summary.json')))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output',type=Path,required=True);p.add_argument('--baseline',type=Path,required=True)
    p.add_argument('--workflow-python',type=Path,required=True);p.add_argument('--child',action='store_true');a=p.parse_args()
    if a.child: finish(a.output,a.baseline,a.workflow_python)
    else:
        a.output=a.output.absolute();a.output.mkdir(parents=True,exist_ok=False)
        supervise([Path(sys.executable).absolute(),'-I','-B',Path(__file__).absolute(),'--child',
            '--output',a.output,'--baseline',a.baseline.absolute(),'--workflow-python',a.workflow_python.absolute()],
            a.output/'integration.log',7200,8000000000,isolated_env(4),sample_root=__import__('os').getpid())
