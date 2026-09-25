"""Seed-11 paired native pilot on accepted features; no preprocessing or downloads.

The driver owns allocation accounting and a process-group deadline. Snakemake
serializes complete tool/condition jobs; isolated native workers retain models,
partitions and selection candidates, then AMBER evaluates in its own prefix.
"""
import argparse
import json
import logging
import os
from pathlib import Path
import runpy
import shutil
import signal
import subprocess
import sys
import tempfile
import time
import traceback
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parent))
from e001_features import (CODE, EXP, read, write, isolated_env, progress, package,
                           ensure_git, stage_runtime, workflow_command, workflow_preflight)
from e001_vamb_cpu import invoke, require, sha


def resources(group, cpus, ram):
    """Use measured allocations; reject accidental host-sized resource requests."""
    expected = 2 if group == 'comebin' else 4
    require(cpus == expected and ram >= expected * 3,
            f'{group} requires explicit {expected} allocated vCPUs and >= {expected*3} GB RAM')
    return dict(vcpus=cpus, ram_gb=ram, threads=2 if group=='comebin' else 3,
                worker_mem_mb=int((ram-.75)*1000), group_core_hours=200 if group=='comebin' else 20,
                tools=['comebin'] if group=='comebin' else ['metabat','vamb'])


def verify_features(cfg):
    """Rehash retained features and frozen inputs before any scientific fit."""
    accepted=read(EXP/'features-observed.json'); frozen=read(EXP/'frozen-inputs.json')
    require(accepted['status']=='accepted','Features not reviewed')
    require(sha(EXP/'config.json')==frozen['config_sha256'],'Changed scientific configuration')
    feature=Path(accepted['directory']); inp=Path(frozen['owner_input_directory'])
    for name, digest in frozen['outputs'].items():
        require(sha(inp/name)==digest,'Changed frozen input: '+name)
    for tool in cfg['tools']:
        for name, record in accepted['results'][tool]['artifacts'].items():
            path=feature/tool/name
            require(path.is_file() and sha(path)==record['sha256'],'Changed accepted feature: '+str(path))
    write(Path(cfg['stage'])/'verified.json',dict(feature_record_sha256=sha(EXP/'features-observed.json'),
          frozen_record_sha256=sha(EXP/'frozen-inputs.json'), feature_directory=str(feature)))


def fit_arguments(tool, feature, out, threads):
    """Construct native scientific schedules, with no tuning or truth inputs."""
    if tool=='vamb':
        return ['bin','default','--outdir',str(out),'--composition',str(feature/'composition.npz'),
                '--abundance',str(feature/'abundance.npz'),'-m','2500','-p',str(threads),
                '--seed','11','-e','300','-o','']
    require(tool=='comebin','No Python training CLI for this tool')
    return ['train','--data',str(feature),'--output_path',str(out),'--epochs','200',
            '--batch_size','1024','--earlystop','--addvars','--vars_sqrt','--n_views','6',
            '--num_threads',str(threads),'--seed','11','--device','cpu']


def native_fit(cfg, tool, condition):
    """Run the pinned training entry point and export full native assignments."""
    from e001lib.native import verify_source, require_packages
    from e001lib.records import sequences, partition, write_cami
    root=Path(cfg['root']); out=Path(cfg['stage'])/tool/condition; native=out/'native'
    source=root/'sources'/('COMEBin' if tool=='comebin' else tool)
    provenance=verify_source('COMEBin' if tool=='comebin' else tool,source)
    versions={'metabat':{'numpy':'2.2.6','biopython':'1.85','pysam':'0.23.3'},
              'vamb':{'numpy':'1.26.4','torch':'2.6.0+cpu','pycoverm':'0.6.2'},
              'comebin':{'numpy':'2.4.6','torch':'2.13.0+cpu','biopython':'1.87'}}
    require_packages(versions[tool])
    if tool=='metabat':
        for line in (root/'locks/metabat/binaries.sha256').read_text().splitlines():
            digest,filename=line.split(maxsplit=1)
            require(sha(filename.strip())==digest,'MetaBAT binary changed')
    accepted=read(EXP/'features-observed.json'); feature=Path(accepted['directory'])/tool/condition
    fasta=Path(read(EXP/'frozen-inputs.json')['owner_input_directory'])/'canonical.fna'
    lengths={name:len(seq) for name,seq in sequences(fasta)}
    require(len(lengths)==22594,'Wrong frozen contig axis')
    report={'source':provenance,'seed':11,'condition':condition,'feature_record_sha256':sha(EXP/'features-observed.json')}
    if tool=='metabat':
        native.mkdir()
        command=[root/'envs/metabat/bin/metabat2','-i',fasta,'-a',feature/'depth.tsv',
                 '-o',native/'bins','-t',str(cfg['threads']),'--seed','11','--saveCls','--unbinned']
        write(out/'native-command.json',list(map(str,command)))
        subprocess.run(list(map(str,command)),check=True)
        predictions=partition(native/'bins.MemberMatrix.txt',lengths,'metabat')
    else:
        import torch
        torch.set_num_interop_threads(1)
        args=fit_arguments(tool,feature,native,cfg['threads']); write(out/'native-command.json',args)
        if tool=='vamb':
            sys.path.insert(0,str(source)); sys.argv=['vamb',*args]
            from vamb.__main__ import main
            # The native module resets pool environment variables at import.
            for key in ('OMP_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'): os.environ[key]='1'
            from threadpoolctl import threadpool_limits
            with threadpool_limits(limits=1,user_api='blas'):
                main()
            predictions=partition(native/'vae_clusters_unsplit.tsv',lengths,'vamb')
            import numpy as np
            from vamb.parsecontigs import Composition
            comp=Composition.load(feature/'composition.npz')
            embedding=np.load(native/'latent.npz')['arr_0']
            require(embedding.shape[0]==len(comp.metadata.identifiers) and np.isfinite(embedding).all(),'Invalid VAMB embedding')
            write(native/'embedding-ids.json',list(comp.metadata.identifiers))
            require((native/'model.pt').is_file(),'VAMB model missing')
        else:
            sys.path.insert(0,str(source/'COMEBin')); sys.argv=['comebin',*args]
            runpy.run_path(str(source/'COMEBin/main.py'),run_name='__main__')
            from embedding_bundle import load_embedding_bundle
            bundle=load_embedding_bundle(native/'embeddings.npy')
            require(set(bundle.contig_ids)==set(lengths),'COMEBin embedding axis changed')
            require(any(native.glob('checkpoint*.pth.tar')),'COMEBin checkpoint missing')
            # Clustering is a separate bounded process; its imports cannot affect training.
            write(out/'trained.json',report); return
    write_cami(out/'predictions.tsv',lengths,assignments=predictions)
    report.update(assigned_contigs=len(predictions),assignment_sha256=sha(out/'predictions.tsv'))
    write(out/'fit.json',report)


def comebin_cluster(cfg, condition):
    """Use the accepted native grid/marker selector; retain all 120 candidates."""
    import numpy as np
    from e001lib.native import verify_source
    from e001lib.records import sequences, write_cami
    root=Path(cfg['root']); source=root/'sources/COMEBin'
    verify_source('COMEBin',source); sys.path.insert(0,str(source/'COMEBin'))
    from embedding_bundle import load_embedding_bundle
    from utils import gen_seed, configure_reproducibility
    from cluster import cluster
    from leiden_grid import validate_leiden_output_set
    from get_final_result import run_get_final_result, _profile_marker_tables, Markers, select_best_result
    from checkm.defaultValues import DefaultValues
    out=Path(cfg['stage'])/'comebin'/condition; native=out/'native'
    bundle=load_embedding_bundle(native/'embeddings.npy'); ids=list(bundle.contig_ids)
    fasta=native/'canonical.fna'
    shutil.copyfile(Path(read(EXP/'frozen-inputs.json')['owner_input_directory'])/'canonical.fna',fasta)
    lengths={name:len(seq) for name,seq in sequences(fasta)}
    data=Path(DefaultValues.CHECKM_DATA_DIR)
    require(data.resolve()==(root/'envs/comebin/checkm_data').resolve(),'Wrong CheckM data root')
    write(out/'checkm-payloads.json',{str(p.relative_to(data)):sha(p) for p in
          (data/'hmms/checkm.hmm',data/'pfam/Pfam-A.hmm.dat',data/'pfam/tigrfam2pfam.tsv')})
    configure_reproducibility(11); logger=logging.getLogger('E001-pilot'); threads=cfg['threads']
    count=gen_seed(logger,str(fasta),threads,1001,marker_name='bacar_marker',quarter='2quarter')
    args=SimpleNamespace(contig_file=str(fasta),output_path=str(native),emb_file=str(native/'embeddings.npy'),
         seed_file=str(fasta)+'.bacar_marker.2quarter_lencutoff_1001.seed',contig_len=1001,cluster_num=0,
         not_l2normaize=False,num_threads=threads,leiden_workers=1,max_edges=100,seed=11,bac_mg_table=None,ar_mg_table=None)
    cluster(logger,args)
    names,rows=validate_leiden_output_set(native/'cluster_res',100,expected_rows=len(ids))
    require(len(names)==120,'Incomplete native candidate grid')
    bac,ar=_profile_marker_tables(logger,args,count,threads,'binary-labels',None)
    args.bac_mg_table,args.ar_mg_table=str(bac),str(ar)
    run_get_final_result(logger,args,count,num_threads=threads)
    markers=Markers(); markers.marker_gene_tables(str(bac),str(ar))
    _,best,_=select_best_result(native/'cluster_res',names,'binary-labels',ids,markers)
    labels=np.load(native/'cluster_res'/best,allow_pickle=False)
    require(len(labels)==len(ids) and (labels>=0).all(),'Invalid selected labels')
    write_cami(out/'predictions.tsv',lengths,assignments={n:str(int(v)) for n,v in zip(ids,labels)})
    report=read(out/'trained.json'); report.update(winning_candidate=best,candidate_count=len(names),rows=rows,
        candidate_sha256={n:sha(native/'cluster_res'/n) for n in names},assignment_sha256=sha(out/'predictions.tsv'),
        scope='Full selected labels are primary; native filtered bins and comebin_res.tsv retained separately')
    write(out/'fit.json',report)


def evaluate(cfg, tool, condition):
    """Evaluate full assignments with frozen truth, conservative R95 and native AMBER."""
    from e001lib.native import verify_source
    from e001lib.records import partition
    from e001lib.metrics import score
    root=Path(cfg['root']); source=root/'sources/AMBER_evaluation'; verify_source('AMBER_evaluation',source)
    sys.path.insert(0,str(source))
    from cami_amber.binning_classes import GenomeQuery, Options
    from cami_amber.utils.load_data import read_metadata
    out=Path(cfg['stage'])/tool/condition; inp=Path(read(EXP/'frozen-inputs.json')['owner_input_directory'])
    population=read(inp/'population.json'); predictions=out/'predictions.tsv'
    assignments=partition(predictions,population['lengths']); result=score(population,assignments)
    write(out/'r95.json',result)
    # Empty assignments are a valid failed biological outcome. AMBER cannot load
    # header-only predictions; record that contract explicitly instead of dropping it.
    if assignments:
        options=Options(filter_tail_percentage=0,skip_heatmap=True)
        gold=GenomeQuery('gold','E001',options,read_metadata((str(inp/'truth.tsv'),'gold'))[0],is_gs=True)
        query=GenomeQuery(tool+'-'+condition,'E001',options,read_metadata((str(predictions),tool))[0])
        query.gold_standard=gold; query.compute_metrics()
        require(int(query.precision_df['total_length'].sum())==result['assigned_bp'],'AMBER assigned base mismatch')
        query.precision_df.to_csv(out/'amber-per-bin.tsv',sep='\t',index=False)
        query.recall_df.to_csv(out/'amber-per-genome.tsv',sep='\t',index=False)
    write(out/'evaluation.json',dict(status='completed',tool=tool,condition=condition,seed=11,
          r95=result['r95'],assigned_bp=result['assigned_bp'],amber='filter=0' if assignments else 'empty partition; no AMBER rows',
          assignment_sha256=sha(predictions),source_commit=cfg['source_commit']))


def descendants(pid):
    """Snapshot only this child's process tree, with sampled RSS in KiB."""
    rows=[list(map(int,line.split())) for line in subprocess.check_output(
        ['ps','-axo','pid=,ppid=,rss='],text=True).splitlines() if line.strip()]
    selected={pid}
    while True:
        expanded=selected | {p for p,parent,rss in rows if parent in selected}
        if expanded==selected: break
        selected=expanded
    result=[]
    for p,parent,rss in rows:
        if p not in selected: continue
        if sys.platform.startswith('linux'):
            try:
                lines=Path(f'/proc/{p}/smaps_rollup').read_text().splitlines()
                rss=next(int(line.split()[1]) for line in lines if line.startswith('Pss:'))
            except (OSError,StopIteration): pass
        result.append((p,rss))
    return result


def checked(command, env, out, label, seconds, memory_mb=None):
    """Capture a bounded child in the workflow group; kill its tree on failure.

    Linux uses summed PSS to avoid counting shared DataLoader pages repeatedly;
    unavailable PSS falls back to conservative RSS.
    The outer workflow deadline also kills these children because they never
    create a new session. No process outside the verified child tree is killed.
    """
    start=time.monotonic(); record=dict(argv=list(map(str,command)),timeout_seconds=seconds,
                                      memory_limit_mb=memory_mb,peak_tree_memory_mb=0,memory_metric='sum PSS on Linux; RSS fallback')
    process=None
    print('START: '+label,flush=True)
    try:
        with (out/(label+'.stdout')).open('x') as stdout, (out/(label+'.stderr')).open('x') as stderr:
            process=subprocess.Popen(record['argv'],env=env,stdout=stdout,stderr=stderr)
            record['pid']=process.pid
            write(out/(label+'.command.json'),record)
            while process.poll() is None:
                rss=sum(r for _,r in descendants(process.pid))/1024
                record['peak_tree_memory_mb']=max(record['peak_tree_memory_mb'],rss)
                require(memory_mb is None or rss<=memory_mb,'Process tree exceeded RAM ceiling')
                require(time.monotonic()-start<seconds,'Native command exceeded time/cost ceiling')
                time.sleep(.5)
            record['returncode']=process.returncode
            require(process.returncode==0,f'{label} failed; inspect captured stderr')
    except BaseException:
        record['failure']=traceback.format_exc()
        if process is not None and process.poll() is None:
            for pid,_ in reversed(descendants(process.pid)):
                try: os.kill(pid,signal.SIGKILL)
                except ProcessLookupError: pass
            process.wait()
        raise
    finally:
        record['elapsed_seconds']=time.monotonic()-start
        write(out/(label+'.command.json'),record)
    print('PASS: '+label,flush=True)


def worker(cfg, tool, condition):
    """Run one complete condition in isolated tool/evaluator runtimes."""
    out=Path(cfg['stage'])/tool/condition; out.mkdir(parents=True,exist_ok=True)
    require(not any(out.iterdir()),'Refusing to overwrite pilot outputs')
    root=Path(cfg['root']); prefix=root/'envs'/tool; env=isolated_env(prefix,1)
    env.update(TMPDIR=str(Path(cfg['stage'])/'tmp'),CHECKM_DATA_PATH=str(prefix/'checkm_data'))
    helper=CODE/'scripts/e001_pilot.py'
    try:
        checked([prefix/'bin/python','-I','-S',CODE/'scripts/e001_native_probe.py',prefix,*(['numpy'] if tool=='metabat' else ['numpy','torch'])],env,out,'probe',60)
        checked([prefix/'bin/python','-I','-m','pip','freeze','--all'],env,out,'inventory',60)
        base=[prefix/'bin/python','-I',helper,'--config',cfg['runtime_config'],'--tool',tool,'--condition',condition]
        checked([*base,'--native','fit'],env,out,'fit',min(80,cfg['group_core_hours'])*3600/cfg['vcpus'],cfg['worker_mem_mb'])
        if tool=='comebin':
            checked([*base,'--native','cluster'],env,out,'cluster',15*3600/cfg['vcpus'],cfg['worker_mem_mb'])
        amber=root/'envs/amber'; amber_env=isolated_env(amber,1); amber_env['TMPDIR']=env['TMPDIR']
        checked([amber/'bin/python','-I','-S',CODE/'scripts/e001_native_probe.py',amber,'numpy'],amber_env,out,'amber-probe',60)
        checked([amber/'bin/python','-I',*base[2:],'--native','evaluate'],amber_env,out,'evaluate',3600)
        write(out/'complete.json',read(out/'evaluation.json'))
        write(out/'retained.json',{str(p.relative_to(out)):dict(bytes=p.stat().st_size,sha256=sha(p))
              for p in sorted(out.rglob('*')) if p.is_file()})
    except BaseException:
        write(out/'failure.json',{'traceback':traceback.format_exc()}); raise


def run(root, data, group, cpus, ram, snapshot):
    """Create a unique grouped attempt, execute the DAG and always package evidence."""
    res=resources(group,cpus,ram)
    require(root.is_absolute() and root.is_dir() and data.is_absolute() and data.is_dir(),'Existing absolute roots required')
    stage=Path(tempfile.mkdtemp(prefix='paired-pilot-'+group+'-',dir=data)); start=time.monotonic(); status=1
    cfg=dict(**res,root=str(root),stage=str(stage),runtime_config=str(stage/'runtime.json'),
             helper=str(Path(__file__).resolve()),driver_python=sys.executable,
             source_commit=(CODE/'SOURCE_COMMIT').read_text().strip())
    write(stage/'runtime.json',cfg); env=isolated_env()
    try:
        with progress(stage):
            for name in ('logs','benchmarks','tmp'): (stage/name).mkdir()
            require(shutil.disk_usage(stage).free>=30_000_000_000,'Need 30 GB free; retain existing work')
            ensure_git(env,stage); verify_features(cfg)
            prefix=stage_runtime(root,snapshot,env,stage); workflow=prefix/'bin/snakemake'
            env['PATH']=str(prefix/'bin')+os.pathsep+env.get('PATH',''); env['TMPDIR']=str(stage/'tmp')
            invoke([prefix/'bin/python','-I','-S',CODE/'scripts/e001_native_probe.py',prefix,'snakemake'],env,stage,'workflow-prefix',60)
            workflow_preflight(workflow,env,stage)
            require(sha(stage/'workflow-lock.stdout')==read(EXP/'sample0-preprocess-observed.json')['member_sha256']['workflow-lock.stdout'],'Workflow inventory changed')
            cmd=['--snakefile',CODE/'workflows/e001-preprocess/pilot.smk','--directory',stage,'--configfile',stage/'runtime.json',
                 '--cores',cpus,'--executor','local','--resources',f"mem_mb={int((ram-.5)*1000)}",'tool_slots=1',
                 '--keep-incomplete','--printshellcmds','--benchmark-extended']
            invoke(workflow_command(workflow,'snakemake',cmd+['--dry-run']),env,stage,'dag',120)
            remaining=res['group_core_hours']*3600/cpus-(time.monotonic()-start)
            require(remaining>0,'Group budget exhausted')
            invoke(workflow_command(workflow,'snakemake',cmd,0),env,stage,'workflow',remaining)
            require((stage/'paired-summary.json').is_file(),'Missing completed paired receipt'); status=0
    except BaseException:
        write(stage/'failure.json',{'traceback':traceback.format_exc()}); print(traceback.format_exc(),file=sys.stderr)
    finally:
        elapsed=time.monotonic()-start
        write(stage/'status.json',dict(exit_code=status,**res,elapsed_seconds=elapsed,allocated_core_hours=elapsed*cpus/3600,
              retained_bytes=sum(p.stat().st_size for p in stage.rglob('*') if p.is_file()),
              cost_scope='Driver wall time including setup; excludes packaging and outside-driver idle time'))
        try: package(stage,root)
        except Exception:
            status=1; record=read(stage/'status.json'); record.update(exit_code=1,packaging_failed=True); write(stage/'status.json',record)
            print('Packaging failed; preserve',stage,traceback.format_exc(),file=sys.stderr)
    return status


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('root',type=Path,nargs='?'); p.add_argument('--data-root',type=Path)
    p.add_argument('--group',choices=('metabat-vamb','comebin')); p.add_argument('--vcpus',type=int); p.add_argument('--ram-gb',type=float)
    p.add_argument('--workflow-snapshot',type=Path); p.add_argument('--config',type=Path)
    p.add_argument('--tool',choices=('metabat','vamb','comebin')); p.add_argument('--condition',choices=('C0','CT'))
    p.add_argument('--native',choices=('fit','cluster','evaluate')); p.add_argument('--worker',action='store_true'); p.add_argument('--aggregate',action='store_true')
    a=p.parse_args(); logging.basicConfig(level=logging.INFO,format='%(asctime)s %(message)s')
    if a.config:
        cfg=read(a.config)
        if a.aggregate:
            results={t:{c:read(Path(cfg['stage'])/t/c/'complete.json') for c in ('C0','CT')} for t in cfg['tools']}
            write(Path(cfg['stage'])/'paired-summary.json',dict(results=results,delta_r95={t:r['CT']['r95']-r['C0']['r95'] for t,r in results.items()},
                  scope='Seed-11 development diagnostic; review before additional seeds; does not establish H001'))
        elif a.worker: worker(cfg,a.tool,a.condition)
        elif a.native=='fit': native_fit(cfg,a.tool,a.condition)
        elif a.native=='cluster': comebin_cluster(cfg,a.condition)
        elif a.native=='evaluate': evaluate(cfg,a.tool,a.condition)
        else: p.error('Worker mode required')
    else:
        if any(x is None for x in (a.root,a.data_root,a.group,a.vcpus,a.ram_gb,a.workflow_snapshot)): p.error('All allocation and root arguments required')
        raise SystemExit(run(a.root,a.data_root,a.group,a.vcpus,a.ram_gb,a.workflow_snapshot))
