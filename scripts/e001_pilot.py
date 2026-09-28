"""Seed-11 paired native pilot on accepted features; no preprocessing or downloads.

The driver owns allocation accounting and a process-group deadline. Snakemake
serializes complete tool/condition jobs; isolated native workers retain models,
partitions and selection candidates, then AMBER evaluates in its own prefix.
"""
import argparse
from datetime import datetime, timezone
import json
import logging
import os
from pathlib import Path
import re
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


def worker_environment(prefix, tool, cfg):
    """Set native thread-pool limits to the actual serial tool allocation."""
    omp_threads = cfg['metabat_threads'] if tool == 'metabat' else 1
    env = isolated_env(prefix, omp_threads)
    env.update(TMPDIR=str(Path(cfg['stage'])/'tmp'),
               CHECKM_DATA_PATH=str(Path(prefix)/'checkm_data'))
    return env


def resources(group, cpus, ram):
    """Use reviewed allocations and include native loader workers in CPU budgets."""
    require(group in ('metabat-vamb', 'comebin'), 'Unknown pilot resource group')
    expected = 8 if group == 'comebin' else 4
    require(cpus == expected and ram >= expected * 3,
            f'{group} requires explicit {expected} allocated vCPUs and >= {expected*3} GB RAM')
    return dict(vcpus=cpus, ram_gb=ram,
                threads=cpus,
                comebin_threads=7 if group=='comebin' else 0,
                comebin_loader_workers=1 if group=='comebin' else 0,
                leiden_workers=8 if group=='comebin' else 0,
                metabat_threads=4 if group=='metabat-vamb' else 0,
                vamb_threads=3 if group=='metabat-vamb' else 0,
                vamb_loader_workers=1 if group=='metabat-vamb' else 0,
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


def metabat_command(executable, fasta, depth, prefix, threads):
    """Build the pinned MetaBAT2 command with its actual OpenMP CPU budget."""
    return [str(executable), '-i', str(fasta), '-a', str(depth), '-o', str(prefix),
            '-t', str(threads), '--seed', '11', '--saveCls', '--unbinned']


def short_local_tmpdir():
    """Create a private short path on node-local /tmp for Unix-socket IPC."""
    root = Path('/tmp')
    require(root.is_dir(), 'Node-local /tmp is required for native IPC')
    path = Path(tempfile.mkdtemp(prefix='e1p-', dir=root))
    require(len(os.fsencode(str(path))) <= 40,
            'Short native IPC path exceeds the Unix-socket safety limit')
    return path


def native_vamb_ipc_smoke(cfg):
    """Exercise pinned VAMB's actual one-worker CPU DataLoader before fitting.

    Synthetic tensors pass through VAMB's normalization and PyTorch shared
    tensor queue, the same multiprocessing resource-sharer path that failed in
    the returned run. This is a software/IPC check, not a fit or data result.
    """
    import numpy as np
    import torch
    from e001lib.native import require_packages, verify_source

    root = Path(cfg['root'])
    source=root/'sources/vamb'
    provenance = verify_source('vamb', source)
    import vamb
    module_path=Path(vamb.__file__).resolve()
    require(module_path.is_relative_to(source.resolve()) or
            module_path.is_relative_to((root/'envs/vamb').resolve()),
            'VAMB import is outside its pinned source and experiment prefix')
    require_packages({'numpy':'1.26.4', 'torch':'2.6.0+cpu', 'pycoverm':'0.6.2'})
    scratch = Path(os.environ['TMPDIR']).resolve()
    require(scratch.is_dir() and scratch == Path(tempfile.gettempdir()).resolve(),
            'Python is not using the short private VAMB TMPDIR')
    torch.set_num_threads(cfg['vamb_threads'])
    torch.set_num_interop_threads(1)
    rng = np.random.default_rng(11)
    nseq, nsamples = 32, 10
    abundance = rng.random((nseq, nsamples), dtype=np.float32) + np.float32(.01)
    tnf = rng.normal(size=(nseq, 103)).astype(np.float32)
    lengths = np.full(nseq, 10_000, dtype=np.int64)
    loader = vamb.encode.make_dataloader(abundance, tnf, lengths,
                                         batchsize=8, destroy=False, cuda=False)
    require(loader.num_workers == cfg['vamb_loader_workers'] == 1,
            'Pinned VAMB CPU DataLoader worker count changed')
    batches = list(loader)
    rows = sum(int(batch[0].shape[0]) for batch in batches)
    require(rows == nseq and batches, 'Pinned VAMB DataLoader returned incomplete batches')
    report = dict(status='passed', source=provenance, import_path=str(module_path),python=sys.version.split()[0],
                  torch=torch.__version__, tmpdir=str(scratch), tmpdir_bytes=len(os.fsencode(str(scratch))),
                  dataloader_workers=loader.num_workers, torch_threads=torch.get_num_threads(),
                  torch_interop_threads=torch.get_num_interop_threads(),
                  synthetic_contigs=nseq, batches=len(batches), rows=rows,
                  scope='Pinned VAMB CPU DataLoader IPC only; no scientific inputs or training')
    write(Path(cfg['stage'])/'vamb-ipc-smoke.json', report)
    print('PASS: pinned VAMB CPU DataLoader IPC', flush=True)


def preflight_vamb_ipc(root, stage, cfg):
    """Run the pinned VAMB/PyTorch CPU IPC check before any full pilot rule."""
    prefix = Path(root)/'envs/vamb'
    local_tmp = short_local_tmpdir()
    env = isolated_env(prefix, 1)
    env['TMPDIR'] = str(local_tmp)
    write(Path(stage)/'vamb-ipc-smoke-attempt.json', dict(
        tmpdir=str(local_tmp), tmpdir_bytes=len(os.fsencode(str(local_tmp))),
        vamb_threads=cfg['vamb_threads'], dataloader_workers=cfg['vamb_loader_workers'],
        order='before MetaBAT2 or VAMB full fit'))
    try:
        invoke([prefix/'bin/python','-I','-S',CODE/'scripts/e001_native_probe.py',prefix,
                'numpy','torch'],env,stage,'vamb-ipc-prefix',60)
        smoke=[prefix/'bin/python','-I',CODE/'scripts/e001_pilot.py','--config',
               Path(cfg['runtime_config']),'--native','vamb-ipc-smoke']
        checked(smoke,env,Path(stage),'vamb-ipc-smoke',120,3000,
                fatal_markers=('OSError: AF_UNIX path too long',),stall_seconds=60)
    finally:
        shutil.rmtree(local_tmp,ignore_errors=True)


def native_comebin_ipc_smoke(cfg):
    """Drain COMEBin's production TensorDataset loader at the retry worker budget.

    The pinned implementation hard-codes four workers. The E001 adapter reduces
    that queue to one worker so its native --num_threads=7 fits an eight-vCPU
    allocation. TensorDataset returns precomputed tensors without random
    augmentation, and the seeded main-process sampler preserves input ordering.
    This bounded check exercises the same PyTorch multiprocessing queue first.
    """
    import numpy as np
    import torch
    from e001lib.native import require_packages, verify_source
    root=Path(cfg['root']); source=root/'sources/COMEBin'
    provenance=verify_source('COMEBin',source)
    require_packages({'numpy':'2.4.6','torch':'2.13.0+cpu'})
    sys.path.insert(0,str(source/'COMEBin'))
    import train_CLmodel
    require(train_CLmodel.DATALOADER_WORKERS==4,'Pinned COMEBin loader source changed')
    require(cfg['comebin_threads']==7 and cfg['comebin_loader_workers']==1 and
            cfg['comebin_threads']+cfg['comebin_loader_workers']==cfg['vcpus'],
            'COMEBin CPU allocation does not fit this job')
    scratch=Path(os.environ['TMPDIR']).resolve()
    require(scratch.is_dir() and scratch==Path(tempfile.gettempdir()).resolve() and
            len(os.fsencode(str(scratch)))<=40,'COMEBin IPC must use its short private /tmp')
    torch.set_num_threads(cfg['comebin_threads']); torch.set_num_interop_threads(1)
    views=tuple(torch.from_numpy(np.random.default_rng(11+i).normal(size=(32,156)).astype('float32'))
                for i in range(6))
    dataset=torch.utils.data.TensorDataset(*views)
    generator=torch.Generator().manual_seed(11)
    from utils import seed_data_loader_worker
    loader=torch.utils.data.DataLoader(dataset,batch_size=8,shuffle=True,
        num_workers=cfg['comebin_loader_workers'],drop_last=True,
        worker_init_fn=seed_data_loader_worker,generator=generator)
    batches=list(loader); rows=sum(int(batch[0].shape[0]) for batch in batches)
    require(loader.num_workers==1 and len(batches)==4 and rows==32,
            'COMEBin CPU loader IPC smoke returned incomplete batches')
    report=dict(status='passed',source=provenance,torch=torch.__version__,tmpdir=str(scratch),
        pytorch_threads=torch.get_num_threads(),native_loader_workers=train_CLmodel.DATALOADER_WORKERS,
        adapter_loader_workers=loader.num_workers,synthetic_views=6,rows=rows,batches=len(batches),
        scope='Pinned PyTorch CPU queue and production TensorDataset; no research features or training')
    write(Path(cfg['stage'])/'comebin-ipc-smoke.json',report)
    print('PASS: pinned COMEBin CPU DataLoader IPC',flush=True)


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
        command=metabat_command(root/'envs/metabat/bin/metabat2',fasta,
                                feature/'depth.tsv',native/'bins',cfg['metabat_threads'])
        write(out/'native-command.json',list(map(str,command)))
        subprocess.run(list(map(str,command)),check=True)
        predictions=partition(native/'bins.MemberMatrix.txt',lengths,'metabat')
    else:
        import torch
        torch.set_num_interop_threads(1)
        threads=cfg['vamb_threads'] if tool=='vamb' else cfg['comebin_threads']
        args=fit_arguments(tool,feature,native,threads); write(out/'native-command.json',args)
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
            import train_CLmodel
            require(train_CLmodel.DATALOADER_WORKERS==4, 'Pinned COMEBin loader source changed')
            require(threads+cfg['comebin_loader_workers']==cfg['vcpus'], 'COMEBin CPU budget mismatch')
            # The pinned source fixes four queue workers. Use a one-worker runtime
            # override; TensorDataset is deterministic and training order is
            # controlled by its seeded sampler in the parent process.
            train_CLmodel.DATALOADER_WORKERS=cfg['comebin_loader_workers']
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
         not_l2normaize=False,num_threads=threads,leiden_workers=cfg['leiden_workers'],max_edges=100,seed=11,bac_mg_table=None,ar_mg_table=None)
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
        query.precision_df.to_csv(out/'amber-per-bin.tsv',sep='\t',index=True,index_label='BINID')
        query.recall_df.to_csv(out/'amber-per-genome.tsv',sep='\t',index=True,index_label='BINID')
    write(out/'evaluation.json',dict(status='completed',tool=tool,condition=condition,seed=11,
          r95=result['r95'],assigned_bp=result['assigned_bp'],amber='filter=0' if assignments else 'empty partition; no AMBER rows',
          assignment_sha256=sha(predictions),source_commit=cfg['source_commit']))


def descendants(pid):
    """Snapshot only this child's process tree and summed PSS in KiB."""
    proc=Path('/proc')
    if sys.platform.startswith('linux') and proc.is_dir():
        parents={}
        for entry in proc.iterdir():
            if not entry.name.isdigit(): continue
            try:
                stat=(entry/'stat').read_text(); fields=stat[stat.rfind(')')+2:].split()
                parents[int(entry.name)]=int(fields[1])
            except (OSError,ValueError,IndexError): continue
        selected={pid}
        while True:
            expanded=selected | {child for child,parent in parents.items() if parent in selected}
            if expanded==selected: break
            selected=expanded
        page_kb=os.sysconf('SC_PAGE_SIZE')/1024
        result=[]
        for child in selected:
            try:
                lines=(proc/str(child)/'smaps_rollup').read_text().splitlines()
                memory_kb=next(int(line.split()[1]) for line in lines if line.startswith('Pss:'))
            except (OSError,StopIteration,ValueError):
                try: memory_kb=int((proc/str(child)/'statm').read_text().split()[1])*page_kb
                except (OSError,IndexError,ValueError): memory_kb=0
            result.append((child,memory_kb))
        return result

    rows=[list(map(int,line.split())) for line in subprocess.check_output(
        ['ps','-axo','pid=,ppid=,rss='],text=True).splitlines() if line.strip()]
    selected={pid}
    while True:
        expanded=selected | {p for p,parent,rss in rows if parent in selected}
        if expanded==selected: break
        selected=expanded
    return [(p,rss) for p,parent,rss in rows if p in selected]


def checked(command, env, out, label, seconds, memory_mb=None, *,
            fatal_markers=(), progress_pattern=None, stall_seconds=None, projected_steps=None, projection_margin=1.25, projection_vcpus=1):
    """Capture a bounded child in the workflow group; kill its tree on failure.

    Linux uses summed PSS to avoid counting shared DataLoader pages repeatedly;
    unavailable PSS falls back to conservative RSS. Optional projected_steps
    stops a full native schedule whose measured epoch rate exceeds its budget,
    starting after three completed epochs without assuming early-stop savings.
    The outer workflow deadline also kills these children because they never
    create a new session. No process outside the verified child tree is killed.
    """
    start=time.monotonic(); last_progress=start; fatal_tail=b''; progress_partial=b''; stderr_position=0
    record=dict(argv=list(map(str,command)),timeout_seconds=seconds,
                memory_limit_mb=memory_mb,peak_tree_memory_mb=0,
                memory_metric='sum PSS on Linux; RSS fallback',
                fatal_stderr_markers=list(fatal_markers),progress_pattern=progress_pattern,
                stall_seconds=stall_seconds)
    process=None
    print('START: '+label,flush=True)
    try:
        stderr_path=out/(label+'.stderr')
        with (out/(label+'.stdout')).open('x') as stdout, stderr_path.open('x') as stderr:
            process=subprocess.Popen(record['argv'],env=env,stdout=stdout,stderr=stderr)
            record['pid']=process.pid
            write(out/(label+'.command.json'),record)
            progress_log=(out/(label+'.progress.log')).open('x') if progress_pattern else None
            try:
                while True:
                    current_size=stderr_path.stat().st_size
                    if current_size>stderr_position:
                        with stderr_path.open('rb') as monitor:
                            monitor.seek(stderr_position)
                            chunk=monitor.read(current_size-stderr_position)
                        stderr_position += len(chunk)
                        if chunk:
                            fatal_bytes=fatal_tail+chunk
                            decoded=fatal_bytes.decode('utf-8',errors='replace')
                            for marker in fatal_markers:
                                if marker in decoded:
                                    record['fatal_stderr']=marker
                                    record['fatal_stderr_tail']=decoded[-2000:]
                                    raise RuntimeError(f'{label} emitted fatal stderr marker: {marker}')
                            fatal_tail=fatal_bytes[-4096:]
                            if progress_pattern:
                                progress_bytes=progress_partial+chunk
                                lines=progress_bytes.splitlines(keepends=True)
                                progress_partial=b''
                                if lines and not lines[-1].endswith((b'\n',b'\r')):
                                    progress_partial=lines.pop()
                                for line in lines:
                                    for match in re.finditer(progress_pattern,line.decode('utf-8',errors='replace')):
                                        value=match.group(1) if match.groups() else match.group(0)
                                        if value != record.get('last_native_progress'):
                                            last_progress=time.monotonic()
                                            record['last_native_progress']=value
                                            if projected_steps and int(value)>=3:
                                                require(len(match.groups())>=2,
                                                        'Schedule projection needs a native epoch-duration measurement')
                                                samples=record.setdefault('native_epoch_seconds',[])
                                                samples.append(float(match.group(2)))
                                                recent=samples[-3:]
                                                mean_epoch=sum(recent)/len(recent)
                                                projected=(last_progress-start +
                                                    (projected_steps-int(value))*mean_epoch*projection_margin)
                                                record['projected_full_schedule_seconds']=projected
                                                record['projected_full_schedule_core_hours']=projected*projection_vcpus/3600
                                                record['projection_method']='elapsed fit startup once plus remaining epochs at mean of latest three native epoch times with 25% margin; no early-stop savings'
                                                require(projected<=seconds, 'Measured full-schedule projection exceeds fit cost ceiling')
                                            progress_log.write(json.dumps(dict(
                                                utc=datetime.now(timezone.utc).isoformat(),
                                                elapsed_seconds=last_progress-start,progress=value))+'\n')
                                            progress_log.flush()
                                            print(f'PROGRESS: {label} {value}',flush=True)
                    if process.poll() is not None:
                        if stderr_path.stat().st_size<=stderr_position:
                            break
                        continue
                    rss=sum(r for _,r in descendants(process.pid))/1024
                    record['peak_tree_memory_mb']=max(record['peak_tree_memory_mb'],rss)
                    require(memory_mb is None or rss<=memory_mb,'Process tree exceeded RAM ceiling')
                    require(time.monotonic()-start<seconds,'Native command exceeded time/cost ceiling')
                    require(stall_seconds is None or time.monotonic()-last_progress<=stall_seconds,
                            f'{label} made no native progress for {stall_seconds} seconds')
                    time.sleep(.5)
            finally:
                if progress_log and not progress_log.closed:
                    progress_log.close()
            record['returncode']=process.returncode
            require(process.returncode==0,f'{label} failed; inspect captured stderr')
    except BaseException:
        record['failure']=traceback.format_exc()
        if process is not None and process.poll() is None:
            for pid,_ in reversed(descendants(process.pid)):
                try: os.kill(pid,signal.SIGKILL)
                except ProcessLookupError: pass
            process.wait()
            record['returncode']=process.returncode
        raise
    finally:
        record['elapsed_seconds']=time.monotonic()-start
        write(out/(label+'.command.json'),record)
    print('PASS: '+label,flush=True)


def worker(cfg, tool, condition):
    """Run one complete condition in isolated tool/evaluator runtimes."""
    out=Path(cfg['stage'])/tool/condition; out.mkdir(parents=True,exist_ok=True)
    require(not any(out.iterdir()),'Refusing to overwrite pilot outputs')
    root=Path(cfg['root']); prefix=root/'envs'/tool
    env=worker_environment(prefix,tool,cfg)
    helper=CODE/'scripts/e001_pilot.py'
    local_tmp=None
    try:
        checked([prefix/'bin/python','-I','-S',CODE/'scripts/e001_native_probe.py',prefix,*(['numpy'] if tool=='metabat' else ['numpy','torch'])],env,out,'probe',60)
        checked([prefix/'bin/python','-I','-m','pip','freeze','--all'],env,out,'inventory',60)
        base=[prefix/'bin/python','-I',helper,'--config',cfg['runtime_config'],'--tool',tool,'--condition',condition]
        if tool in ('vamb','comebin'):
            local_tmp=short_local_tmpdir(); env['TMPDIR']=str(local_tmp)
        if tool=='comebin':
            ipc=[prefix/'bin/python','-I',helper,'--config',cfg['runtime_config'],
                 '--native','comebin-ipc-smoke']
            checked(ipc,env,out,'comebin-ipc-smoke',120,3000,
                    fatal_markers=('OSError: AF_UNIX path too long','RuntimeError: DataLoader worker'),
                    stall_seconds=60)
        checked([*base,'--native','fit'],env,out,'fit',
                min(80,cfg['group_core_hours'])*3600/cfg['vcpus'],cfg['worker_mem_mb'],
                fatal_markers=('OSError: AF_UNIX path too long','RuntimeError: DataLoader worker','Training failed.') if tool in ('vamb','comebin') else (),
                progress_pattern=r'Epoch:\s*(\d+)' if tool=='vamb' else r'NN training: epoch=(\d+)/.*?elapsed=(\d+(?:\.\d+)?)s' if tool=='comebin' else None,
                stall_seconds=600 if tool=='vamb' else 1800 if tool=='comebin' else None,
                projected_steps=200 if tool=='comebin' else None,
                projection_vcpus=cfg['vcpus'])
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
    finally:
        if local_tmp is not None:
            shutil.rmtree(local_tmp,ignore_errors=True)


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
            if group=='metabat-vamb':
                preflight_vamb_ipc(root,stage,cfg)
            cmd=['--snakefile',CODE/'workflows/e001-preprocess/pilot.smk','--directory',stage,'--configfile',stage/'runtime.json',
                 '--cores',cpus,'--executor','local','--runtime-source-cache-path',stage/'.snakemake-source-cache',
                 '--resources',f"mem_mb={int((ram-.5)*1000)}",'tool_slots=1',
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
        try: package(stage)
        except Exception:
            status=1; record=read(stage/'status.json'); record.update(exit_code=1,packaging_failed=True); write(stage/'status.json',record)
            print('Packaging failed; preserve',stage,traceback.format_exc(),file=sys.stderr)
    return status


def package_failed_attempt(stage, data_root):
    """Package retained COMEBin failure receipts without rerunning its DAG.

    The target must be the recorded failed attempt as a direct child of the
    persistent data root. This reads the attempt and writes a compact return
    archive beside it; it does not clean or modify the retained attempt.
    """
    stage=Path(stage)
    data_root=Path(data_root)
    require(not stage.is_symlink() and stage.is_dir(), 'Attempt must be an existing real directory')
    require(data_root.is_dir() and stage.parent.resolve()==data_root.resolve(),
            'Attempt must be a direct child of the supplied persistent data root')
    require(stage.name.startswith('paired-pilot-comebin-'), 'Not a COMEBin paired-pilot attempt')
    runtime=read(stage/'runtime.json')
    require(Path(runtime['stage']).resolve()==stage.resolve() and runtime['tools']==['comebin'],
            'Attempt runtime does not match the COMEBin pilot')
    expected=('status.json','failure.json','workflow.stderr',
              'comebin/CT/fit.command.json','comebin/CT/fit.stderr')
    missing=[name for name in expected if not (stage/name).is_file()]
    if missing:
        print('NOTICE: retained attempt is missing optional recovery records: '+', '.join(missing),
              file=sys.stderr,flush=True)
    # This is a salvage path: missing receipts are themselves evidence and
    # must not prevent returning the logs that did survive.
    return package(stage)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('root',type=Path,nargs='?'); p.add_argument('--data-root',type=Path)
    p.add_argument('--group',choices=('metabat-vamb','comebin')); p.add_argument('--vcpus',type=int); p.add_argument('--ram-gb',type=float)
    p.add_argument('--workflow-snapshot',type=Path); p.add_argument('--config',type=Path)
    p.add_argument('--package-existing',type=Path,
                    help='package the retained failed COMEBin attempt without rerunning it')
    p.add_argument('--tool',choices=('metabat','vamb','comebin')); p.add_argument('--condition',choices=('C0','CT'))
    p.add_argument('--native',choices=('fit','cluster','evaluate','vamb-ipc-smoke','comebin-ipc-smoke')); p.add_argument('--worker',action='store_true'); p.add_argument('--aggregate',action='store_true')
    a=p.parse_args(); logging.basicConfig(level=logging.INFO,format='%(asctime)s %(message)s')
    if a.package_existing is not None:
        if a.data_root is None: p.error('--package-existing also requires --data-root')
        package_failed_attempt(a.package_existing,a.data_root)
    elif a.config:
        cfg=read(a.config)
        if a.aggregate:
            results={t:{c:read(Path(cfg['stage'])/t/c/'complete.json') for c in ('C0','CT')} for t in cfg['tools']}
            write(Path(cfg['stage'])/'paired-summary.json',dict(results=results,delta_r95={t:r['CT']['r95']-r['C0']['r95'] for t,r in results.items()},
                  scope='Seed-11 development diagnostic; review before additional seeds; does not establish H001'))
        elif a.worker: worker(cfg,a.tool,a.condition)
        elif a.native=='fit': native_fit(cfg,a.tool,a.condition)
        elif a.native=='cluster': comebin_cluster(cfg,a.condition)
        elif a.native=='evaluate': evaluate(cfg,a.tool,a.condition)
        elif a.native=='vamb-ipc-smoke': native_vamb_ipc_smoke(cfg)
        elif a.native=='comebin-ipc-smoke': native_comebin_ipc_smoke(cfg)
        else: p.error('Worker mode required')
    else:
        if any(x is None for x in (a.root,a.data_root,a.group,a.vcpus,a.ram_gb,a.workflow_snapshot)): p.error('All allocation and root arguments required')
        raise SystemExit(run(a.root,a.data_root,a.group,a.vcpus,a.ram_gb,a.workflow_snapshot))
