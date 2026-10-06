#!/usr/bin/env python3
"""Bounded installed-wheel integration from outside the checkout; no science rerun.

New real-DNA software windows, synthetic depth/ambiguity and retained E005 outputs
test native contracts. The outer installed supervisor caps the full suite at
four threads, 8 GB sampled process-tree RSS and two hours. Setup is separate.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time

from dl_binner.contracts import file_record, write_json
from dl_binner.runner import STAGES, receipt_name, validate_completed
from dl_binner.supervision import isolated_env, local_scheduler_options, progress, supervise

ROOT = Path(__file__).resolve().parents[2]


def fixture(folder):
    """Publish new deterministic windows plus named synthetic mask/depth fixtures."""
    from dl_binner.io import read_fasta
    source = ROOT/'artifacts/e005-linux-pilot/input/pilot/assembly.fna'
    original = read_fasta(source)
    candidates = sorted([(i,s) for i,s in original if len(s)>=14000])
    lengths = [180,499,500,767,768,999,1000,2499,2500,9999,10000,12000]
    rows, provenance = [], []
    for at, bp in enumerate(lengths):
        ident, dna = candidates[at]
        offset = 113+at*7
        new = f'e006_real_{at:02d}_{bp}'
        rows.append((new,dna[offset:offset+bp]))
        provenance.append(dict(id=new,source_id=ident,offset_zero_based=offset,bp=bp,
                               sequence_sha256=hashlib.sha256(rows[-1][1].encode()).hexdigest()))
    rows.append(('e006_ambiguity_mask','N'*600))
    path = folder/'assembly.fna'
    path.write_text(''.join(f'>{i}\n{s}\n' for i,s in rows))
    depth = folder/'mean-depth.tsv'
    depth.write_text('contig_id\tsoftware_S1\tsoftware_S2\n'+''.join(
        f'{ident}\t{0 if at%3==0 else at/2}\t{0 if at%2==0 else at+1}\n'
        for at,(ident,_) in reversed(list(enumerate(rows)))))
    write_json(folder/'inputs.json',dict(source=str(source),source_bytes=file_record(source),
        fasta=file_record(path),depth=file_record(depth),rows=provenance,
        contigs=len(rows),bp=sum(len(s) for _,s in rows),synthetic=['mean depths','N-only ambiguity mask'],
        role='Software fixtures only; not a new biological benchmark or independent data'))
    assert len(rows)<=32 and sum(len(s) for _,s in rows)<=600000
    return path,depth,rows


def execute(command, folder, name, expected=0, contains=None):
    """Run installed native argv from unrelated cwd; retain both terminal and result."""
    started=time.monotonic(); log=folder/(name+'.log')
    env=isolated_env(4); env['PYTHONDONTWRITEBYTECODE']='1'
    with log.open('x') as stream:
        result=subprocess.run([str(c) for c in command],cwd=folder,env=env,stdout=stream,
                              stderr=subprocess.STDOUT,timeout=180)
    text=log.read_text()
    if result.returncode!=expected or (contains and contains not in text):
        raise RuntimeError(f'Contract {name}: exit {result.returncode}, expected {expected}; {log}\n{text[-5000:]}')
    progress(f'Integration contract passed: {name}')
    return dict(command=[str(c) for c in command],exit_code=result.returncode,
                wall_seconds=time.monotonic()-started,log=str(log),log_bytes=file_record(log))


def frozen(root):
    """Return completed scientific bytes and mtimes, excluding append-only logs."""
    paths=[root/receipt_name(s) for s in STAGES if (root/receipt_name(s)).exists()]
    for s in validate_completed(root):
        from dl_binner.runner import FOLDERS
        folder=root/FOLDERS[STAGES.index(s['stage'])]
        paths += [folder/name for name in s['files']]
    return {str(p.relative_to(root)):dict(file_record(p),mtime_ns=p.stat().st_mtime_ns) for p in paths}


def suite(folder, workflow):
    """Exercise actual packaged DAG, recovery, accounting and meaningful failures."""
    from dl_binner.accounting import summarize_arm
    folder=Path(folder).absolute(); workflow=Path(workflow).absolute()
    inputs=folder/'input';inputs.mkdir()
    fasta,depth,rows=fixture(inputs)
    python=Path(sys.executable).absolute()
    console=python.parent/'dl-binner'
    cases={}
    base=[python,'-I','-B','-m','dl_binner','run','--threads','4','--fasta',fasta,'--workflow-python',workflow]
    def command(output,with_depth=False):
        return base+['--output',output]+(['--depth',depth] if with_depth else [])
    seq=folder/'sequence'; dep=folder/'depth'; partial=folder/'partial'
    cases['console-help']=execute([console,'run','--help'],folder,'console-help',contains='learned/bins/')
    cases['sequence']=execute([console,*command(seq)[5:]],folder,'sequence')
    seq_summary=json.loads((seq/'run-summary.json').read_text())
    assert seq_summary['checkpoint_reload_exact'] and len(validate_completed(seq))==8
    assert seq_summary['arms']['raw']['masks']['all_zero_depth_contigs'] is None
    assert seq_summary['arms']['learned']['reasons']['excluded']['no_valid_fourmers']==1
    before=frozen(seq)
    cases['fresh-refusal']=execute(command(seq),folder,'fresh-refusal',1,'populated')
    assert before==frozen(seq)
    cases['completed-resume']=execute(command(seq)+['--resume'],folder,'completed-resume',contains='No feature extraction')
    assert before==frozen(seq)
    cases['depth']=execute(command(dep,True),folder,'depth')
    depth_summary=json.loads((dep/'run-summary.json').read_text())
    assert depth_summary['arms']['raw']['samples']==['software_S1','software_S2']
    assert depth_summary['arms']['learned']['masks']['all_zero_depth_contigs']==3
    cases['partial']=execute(command(partial)+['--stop-after','train'],folder,'partial',contains='Paused after 2/8')
    saved=frozen(partial)
    cases['partial-resume']=execute(command(partial)+['--resume'],folder,'partial-resume',contains='Verified 2/8')
    assert all(frozen(partial)[k]==v for k,v in saved.items())
    latest=max((partial/'logs').glob('invocation-*'),key=lambda p:p.stat().st_mtime_ns)
    assert not (latest/'01-features.native.log').exists() and not (latest/'02-train.native.log').exists()
    # Retained E005 outputs are only read, never extracted/inferred/clustered/evaluated.
    returned=ROOT/'artifacts/e005-linux-pilot/returned/gi-pilot-b9k3j2r3/gi-pilot-b9k3j2r3/pilot'
    reused={}
    for arm, assigned in (('raw',798),('learned',3891)):
        account,sources=summarize_arm(returned/'features.npz',returned/f'{arm}.export')
        assert account['statuses']['assigned']['contigs']==assigned
        assert account['masks']['all_zero_depth_contigs']==1353
        reused[arm]=dict(accounting=account,source_files=sources)
    write_json(folder/'e005-accounting.json',reused)
    # Mutation cases affect only new E006 fixtures/prefixes and are restored byte for byte.
    for name,path,change,cmd in (
        ('changed-fasta',fasta,lambda b:b+b'\n',command(seq)),
        ('changed-sample-order',depth,lambda b:b.replace(b'software_S1\tsoftware_S2',b'software_S2\tsoftware_S1'),command(dep,True)),
        ('corrupt-checkpoint',seq/'training/checkpoint.pt',lambda b:b+b'corrupt',command(seq)),
        ('corrupt-export',seq/'learned/bins/assignments.tsv',lambda b:b+b'corrupt',command(seq)),
        ('corrupt-snapshot',seq/'.workflow/run.smk',lambda b:b+b'\n',command(seq))):
        original=path.read_bytes()
        try:
            path.write_bytes(change(original))
            cases[name]=execute(cmd+['--resume'],folder,name,1,contains='changed' if name.startswith('changed') else 'bytes changed')
        finally: path.write_bytes(original)
    config=inputs/'changed-training.json'
    settings=json.loads((seq/'.workflow/training.json').read_text());settings['epochs']=19
    config.write_text(json.dumps(settings))
    cases['changed-config']=execute(command(seq)+['--resume','--training-config',config],folder,'changed-config',1,'changed')
    extra=seq/'raw/bins/unexpected.txt';extra.write_text('unexpected')
    try: cases['extra-output']=execute(command(seq)+['--resume'],folder,'extra-output',1,'Unexpected published')
    finally: extra.unlink()
    missing=seq/'features/features.npz'; original=missing.read_bytes();missing.unlink()
    try: cases['missing-output']=execute(command(seq)+['--resume'],folder,'missing-output',1,'Missing or linked')
    finally: missing.write_bytes(original)
    from dl_binner.runner import PACKAGE
    source=PACKAGE/'cli.py'; original=source.read_bytes()
    try:
        source.write_bytes(original+b'\n')
        cases['changed-package']=execute(command(seq)+['--resume'],folder,'changed-package',1,'changed')
    finally: source.write_bytes(original)
    # Native malformed reader and insufficient training evidence must fail in the intended adapter.
    for name,content,needle in (
        ('invalid-fasta','>broken\nACGTZ\n','invalid IUPAC'),
        ('insufficient-evidence','>one\n'+rows[2][1]+'\n>short\nACGT\n','at least two eligible')):
        bad=inputs/(name+'.fna');bad.write_text(content)
        args=[python,'-I','-B','-m','dl_binner','run','--fasta',bad,'--workflow-python',workflow,'--output',folder/name]
        cases[name]=execute(args,folder,name,1,needle)
        assert not (folder/name/'raw').exists() and not (folder/name/'learned').exists()
    empty=inputs/'two.fna';empty.write_text(''.join(f'>{i}\n{s}\n' for i,s in (rows[2],rows[4])))
    args=[python,'-I','-B','-m','dl_binner','run','--fasta',empty,'--workflow-python',workflow,'--output',folder/'empty-partition']
    cases['empty-partition']=execute(args,folder,'empty-partition')
    empty_summary=json.loads((folder/'empty-partition/run-summary.json').read_text())
    assert all(v['bin_count']==0 and v['statuses']['unassigned']['contigs']==2 for v in empty_summary['arms'].values())
    cases['overall-timeout']=execute(command(folder/'overall-timeout')+['--timeout','.3'],folder,'overall-timeout',1,'wall-time limit')
    # Test this packaged production helper on independent ready native rules.
    for name,threads in (('cpu',4),('memory',1)):
        schedule=folder/('scheduler-'+name);schedule.mkdir()
        worker=schedule/'worker.py'
        worker.write_text('import json,time,sys\nfrom pathlib import Path\ns=time.monotonic_ns()\ntime.sleep(.6)\nPath(sys.argv[1]).write_text(json.dumps(dict(start=s,end=time.monotonic_ns())))\n')
        snake=schedule/'Snakefile'
        snake.write_text("rule all:\n    input: 'a.json','b.json'\nrule worker:\n    output: '{name}.json'\n    threads: "+str(threads)+"\n    resources: mem_mb=8000\n    shell: "+repr(f'{python} -I -B {worker} '+'{output:q}')+'\n')
        cmd=[workflow,'-I','-B','-m','snakemake','--snakefile',snake,'--directory',schedule,
             *local_scheduler_options(4,8000),'--runtime-source-cache-path',schedule/'source-cache']
        cases['scheduler-'+name]=execute(cmd,folder,'scheduler-'+name)
        timings=[json.loads((schedule/f'{v}.json').read_text()) for v in ('a','b')]
        assert min(t['end'] for t in timings)<=max(t['start'] for t in timings)
        cases['scheduler-'+name]['nonoverlapping_intervals']=timings
    # Run the new focused tests against this installed wheel, without adding src to sys.path.
    cases['contracts']=execute([python,'-I','-B',ROOT/'tests/test_generic_run.py','-v'],folder,'contracts')
    config_files=list((dep/'logs').glob('invocation-*/config.json'))
    cmd=[workflow,'-I','-B','-m','snakemake','--snakefile',dep/'.workflow/run.smk','--configfile',config_files[0],
        '--directory',dep,'--cores','4','--executor','local','--resources','mem_mb=8000',
        '--set-resource-scopes','mem_mb=global','--rerun-triggers','mtime','--ignore-incomplete','--dry-run',
        '--runtime-source-cache-path',dep/'.workflow/source-cache']
    cases['native-completed-dag']=execute(cmd,folder,'native-completed-dag',contains='Nothing to be done')
    result=dict(status='passed',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        installed_version=__import__('dl_binner').__version__,python=str(python),workflow_python=str(workflow),
        native_workers_mocked=[],scope='Native Mac installed-wheel software contracts, not new biological utility or generic Linux validation',
        cases=cases,fixture_manifest=file_record(inputs/'inputs.json'),reused_e005_accounting=file_record(folder/'e005-accounting.json'),
        summaries={name:dict(path=str(path),files={p.name:file_record(p) for p in (path/'run-summary.json',path/'run-summary.tsv')})
            for name,path in (('sequence',seq),('depth',dep),('partial',partial),('empty',folder/'empty-partition'))})
    write_json(folder/'observed.json',result)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output',type=Path,required=True);p.add_argument('--workflow-python',type=Path,required=True)
    p.add_argument('--child',action='store_true');a=p.parse_args()
    if a.child:
        suite(a.output,a.workflow_python)
    else:
        a.output=a.output.absolute();a.output.mkdir(parents=True,exist_ok=False)
        supervise([Path(sys.executable).absolute(),'-I','-B',Path(__file__).absolute(),'--child',
                   '--output',a.output,'--workflow-python',a.workflow_python.absolute()],a.output/'integration.log',
                   7200,8000000000,isolated_env(4),sample_root=os.getpid())
