#!/usr/bin/env python3
"""One restore-only E022 pair cache and one fit with unchanged CPM/E013 downstream.

All scientific inputs are explicit and checksum-bound. Missing/corrupt retained
payloads fail; there is no acquisition, model extraction, marker detection,
baseline fit, scoring, dependency install or copy fallback in this worker.
"""
import argparse
import json
import os
from pathlib import Path
import sys
import tarfile

sys.path.insert(0,str(Path(__file__).absolute().parent))
from e014_collect import binding, member_path

STAGES=('restore','train','embed','group','refine','export','graph-proof')
UNIT='E009-relational'


def validate(plan, engineering=False):
    """Admit only the one declared cached treatment and complete fixed schedule."""
    keys={'kind','work','unit','threads','python','worker','workflow_python','snakefile',
          'config','base_config','input_lock','pair_archive'}
    if set(plan)!=keys or plan['kind']!='E022 cached marker-informed learning' or plan['threads']!=4:
        raise ValueError('Unexpected E022 plan keys/thread/scope; no truth path supported')
    expected={'fasta','features','views','tokens','frozen','marker_cache','hmm','anchor_embeddings','anchor_graph'}
    if set(plan['unit'])!=expected:raise ValueError('Complete explicit retained inputs required')
    cfg=json.loads(Path(plan['config']).read_text());base=json.loads(Path(plan['base_config']).read_text())
    repo=Path(__file__).absolute().parents[1]
    prospective=json.loads((repo/'experiments/E021-frozen-sequence-hybrid/config.json').read_text())
    relation=json.loads((repo/'src/dl_binner/resources/relational.json').read_text())
    if not engineering and (cfg!=dict(prospective,relational=relation) or base!=json.loads((repo/'src/dl_binner/resources/multiview.json').read_text())):
        raise ValueError('Frozen E009 source/default/seed/schedule differs')
    if engineering:
        # Engineering is a real own-DNA fixture contract, never native admission.
        from dl_binner.multiview.views import load
        data,_=load(plan['unit']['features'])
        if len(data['ids'])>128 or int(data['lengths'].sum())>1_000_000:raise ValueError('Engineering fixture too large')
    return cfg,base


def verify_inputs(lock_path):
    """Read only the named used inputs, preserving the original restore-only boundary."""
    lock=json.loads(Path(lock_path).read_text())
    if lock['kind']!='E022 exact used-input and pair-cache lock':raise ValueError('Wrong input-lock kind')
    for name,wanted in lock['files'].items():
        p=Path(name)
        if p.is_symlink() or binding(p)!=wanted:raise ValueError('Missing/corrupt retained input; no fallback: '+name)
    return lock


def restore_pairs(archive, output, lock):
    """Extract only an exact bounded flat pair inventory; never regenerate its science."""
    output=Path(output)
    if output.exists():raise FileExistsError('Fresh restored pair directory required')
    if Path(archive).is_symlink() or binding(archive)!=lock['pair_archive'] or Path(archive).stat().st_size>64*1024**2:
        raise ValueError('Missing/corrupt compact pair archive; no regeneration fallback')
    expected=lock['pair_members'];observed={};total=0
    with tarfile.open(archive)as stream:
        for m in stream:
            member_path(output,m.name)
            if not m.isfile() or Path(m.name).name!=m.name or m.name in observed or m.size>64*1024**2:
                raise ValueError('Unexpected pair archive member')
            import hashlib
            sha=hashlib.sha256();count=0
            f=stream.extractfile(m)
            for value in iter(lambda:f.read(1024**2),b''):sha.update(value);count+=len(value)
            total+=count
            if total>64*1024**2:raise ValueError('Pair archive logical limit exceeded')
            observed[m.name]=dict(bytes=count,sha256=sha.hexdigest())
    if observed!=expected:raise ValueError('Pair archive inventory/member bytes differ')
    output.mkdir(parents=True,exist_ok=False)
    with tarfile.open(archive)as stream:
        for m in stream:
            with (output/m.name).open('xb')as f:f.write(stream.extractfile(m).read())


def stage(path,name,engineering=False):
    """Run a single new stage; passed outputs are exclusive, never silently retried."""
    from dl_binner.io import digest,write_json
    plan=json.loads(Path(path).read_text());cfg,base=validate(plan,engineering)
    lock=verify_inputs(plan['input_lock']);u=plan['unit'];root=Path(plan['work'])/'units'/UNIT
    root.mkdir(parents=True,exist_ok=True)
    # Snakemake may create only the declared empty output parent.
    leaf={'restore':'pairs','train':'train','group':'group','refine':'refine','export':'export'}.get(name)
    if leaf and (root/leaf).is_dir() and not any((root/leaf).iterdir()):(root/leaf).rmdir()
    if name=='restore':
        restore_pairs(plan['pair_archive'],root/'pairs',lock)
        from dl_binner.relational.pairs import load_pairs
        pairs,receipt=load_pairs(root/'pairs',u['features'])
        if not engineering and (receipt['full_contigs']!=145702 or receipt['full_bp']!=231678157
                or sum(pairs['sign']==1)<20 or sum(pairs['sign']==-1)<20):
            raise ValueError('Full E009 pair availability gate failed; no fit')
        if (receipt['inputs']['embeddings']!=binding(u['anchor_embeddings']) or receipt['inputs']['graph']!=binding(u['anchor_graph'])
                or receipt['inputs']['marker_cache']!=binding(Path(u['marker_cache'])/'cache.json') or receipt['inputs']['hmm']!=binding(u['hmm'])):
            raise ValueError('Pair anchor vectors/graph differ')
        # Preserve complete original bank bytes via hardlinks, with no recopy or
        # missing-member fallback. They count once in filesystem growth.
        source=Path(u['frozen']);bank=json.loads((source/'bank.json').read_text())
        expected={**bank['members'],'bank.json':binding(source/'bank.json')}
        (root/'frozen').mkdir(exist_ok=False)
        for rel,wanted in expected.items():
            p=source/rel
            if p.is_symlink() or Path(rel).name!=rel or binding(p)!=wanted:raise ValueError('Original frozen bank differs')
            os.link(p,root/'frozen'/rel)
        context=Path(u['tokens'])/'tokens.json'
        with (root/'accepted-context.json').open('xb')as f:f.write(context.read_bytes())
        write_json(root/'restore.json',dict(status='PASS_RESTORED_EXACT_PAIRS_AND_BANK',pairs=binding(root/'pairs/cache.json'),
            pair_counts=receipt['summary']['sign_counts'],no_pair_reselection_or_extraction=True))
    elif name=='train':
        from dl_binner.relational.model import train
        train(u['features'],u['views'],u['tokens'],root/'frozen',root/'pairs',root/'train',cfg,4)
    elif name=='embed':
        from dl_binner.relational.model import embed
        embed(u['features'],u['views'],u['tokens'],root/'frozen',root/'pairs',root/'train/checkpoint.pt',root/'embeddings.npz',4)
    elif name=='group':
        from dl_binner.multiview.downstream import group
        group(root/'embeddings.npz',u['features'],root/'group',base,4)
    elif name=='refine':
        from dl_binner.multiview.downstream import refine
        refine(u['features'],root/'embeddings.npz',root/'group/partition.json',u['marker_cache'],u['fasta'],u['hmm'],root/'refine',base)
    elif name=='export':
        from dl_binner.information.export import export
        target=root/'export';target.mkdir(exist_ok=False);account={}
        for arm,part in [('pre',root/'group/partition.json'),('old',root/'refine/old-partition.json'),('post',root/'refine/partition.json')]:
            account[arm]=export(u['features'],part,u['fasta'],target/arm,include_dna=arm=='post')
        write_json(target/'accounting.json',account)
    elif name=='graph-proof':
        from e014_graph_review import review
        review(root,root/'graph-proof.json')
    else:raise ValueError('Unknown E022 stage')


def workflow(path,dry_run=False,engineering=False):
    """Run the pinned serial local executor with one four-core cap and benchmarks."""
    plan=json.loads(Path(path).read_text());validate(plan,engineering)
    argv=[plan['workflow_python'],'-I','-B','-m','snakemake','--snakefile',plan['snakefile'],
        '--directory',plan['work'],'--cores','4','--runtime-source-cache-path',str(Path(plan['work']).parent/'workflow-source-cache'),
        '--config','plan='+str(Path(path).absolute()),'engineering='+str(engineering).lower(),'--printshellcmds','--benchmark-extended']
    if dry_run:argv.append('--dry-run')
    os.execv(argv[0],argv)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--plan',type=Path,required=True)
    p.add_argument('--workflow',action='store_true');p.add_argument('--dry-run',action='store_true')
    p.add_argument('--verify-inputs',action='store_true');p.add_argument('--engineering',action='store_true')
    p.add_argument('--stage',choices=STAGES);a=p.parse_args()
    if a.verify_inputs:verify_inputs(json.loads(a.plan.read_text())['input_lock'])
    elif a.workflow:workflow(a.plan,a.dry_run,a.engineering)
    elif a.stage:stage(a.plan,a.stage,a.engineering)
    else:p.error('Select --workflow, --verify-inputs or --stage')
