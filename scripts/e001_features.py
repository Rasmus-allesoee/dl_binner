"""Grouped owner-run native E001 feature extraction from accepted UCloud BAMs.

The stdlib driver reuses isolated tool prefixes and the reviewed workflow copy.
Snakemake verifies inputs, schedules three independent tool branches, and gates
an aggregate review receipt. C0/CT and CS remain within each native branch so a
failure cannot publish that tool as complete. No acquisition, mapping or fits.
"""
import argparse
from contextlib import contextmanager
import errno
import json
import logging
import os
from pathlib import Path
import shutil
import sys
import tarfile
import tempfile
import threading
import time
import traceback

sys.path.insert(0, str(Path(__file__).resolve().parent))
from e001_vamb_cpu import invoke, require, sha
from e001_multisample import stage_runtime, workflow_command, workflow_preflight

CODE = Path(__file__).resolve().parents[1]
EXP = CODE / 'experiments/E001-coverage-thinning'
TOOLS = ('metabat', 'vamb', 'comebin')


def read(path):
    """Read a JSON record; malformed/missing records are failures."""
    return json.loads(Path(path).read_text())


def write(path, value):
    """Publish one JSON receipt; parents must already exist."""
    Path(path).write_text(json.dumps(value, indent=2) + '\n')


def isolated_env(prefix=None, threads=1):
    """Remove user Python/profile leakage and bound native thread pools."""
    env = {k:v for k,v in os.environ.items() if k not in
           ('PYTHONPATH','PYTHONHOME','PYTHONUSERBASE','SNAKEMAKE_PROFILE','SNAKEMAKE_WORKFLOW_PROFILE')}
    env.update(PYTHONNOUSERSITE='1', PYTHONDONTWRITEBYTECODE='1', PYTHONUNBUFFERED='1',
               OMP_NUM_THREADS=str(threads), OPENBLAS_NUM_THREADS='1', MKL_NUM_THREADS='1', NUMEXPR_NUM_THREADS='1')
    if prefix:
        env['PATH'] = str(Path(prefix)/'bin') + os.pathsep + env.get('PATH','')
    return env


def resource_plan(cpus, ram):
    """Reserve coordinator headroom and one native branch at a time."""
    require(cpus >= 4 and ram >= 12, 'Feature extraction needs at least 4 vCPU / 12 GB')
    # More allocation is charged but does not silently increase native concurrency.
    return {'vcpus':cpus, 'ram_gb':ram, 'worker_vcpus':3, 'worker_mem_mb':10000,
            'memory_budget_mb':int((ram-1)*1000), 'tool_slots':1}


def validate_manifest(manifest, frozen):
    """Check ordered sample/reference/replicate contracts without remote access."""
    require([e['sample'] for e in manifest['samples']] == frozen['samples'], 'Wrong sample order')
    require(manifest['reference_sha256'] == frozen['outputs']['canonical.fna'], 'Wrong reference')
    paths = set()
    for i,e in enumerate(manifest['samples']):
        s = e['summary']
        require(s['sample'] == e['sample'] and s['thinning_seed'] == 1000+i and s['thinning_fraction'] == .1, 'Wrong replicate/seed')
        require(0 < s['CT']['records'] < s['C0']['records'], 'Invalid BAM counts')
        for c in ('C0','CT'):
            p = Path(e['directory'])/c/'mapped.bam'
            require(p.is_absolute() and str(p) not in paths, 'Duplicate/nonabsolute BAM path')
            paths.add(str(p))
            require(s[c]['bytes'] > 0 and len(s[c]['sha256']) == 64, 'Missing BAM receipt')


def stage_bam(source, destination, expected):
    """Verify a retained BAM, hardlink it or copy only across filesystem devices.

    Symlinks are unsuitable: native COMEBin resolves then sorts targets, losing
    both manifest ordering and the unique names when all targets are mapped.bam.
    Original BAMs are read-only inputs; neither links nor copies are modified.
    """
    require(source.stat().st_size == expected['bytes'] and sha(source) == expected['sha256'], 'BAM changed: '+str(source))
    mode = 'hardlink'
    try:
        os.link(source, destination)
    except OSError as e:
        if e.errno != errno.EXDEV:
            raise
        shutil.copyfile(source, destination)
        require(sha(destination) == expected['sha256'], 'Copied BAM checksum mismatch')
        mode = 'copy-cross-filesystem'
    index = Path(str(source)+'.bai')
    require(index.is_file() and index.stat().st_size > 0, 'Missing BAM index')
    target = Path(str(destination)+'.bai')
    try:
        os.link(index, target)
    except OSError as e:
        if e.errno != errno.EXDEV:
            raise
        shutil.copyfile(index, target)
    return {'path':str(destination), 'source':str(source), 'mode':mode, **expected, 'index_sha256':sha(target)}


def verify_inputs(cfg):
    """Hash all accepted inputs once; check BAM headers/index counts and stage axes."""
    import pysam
    from e001lib.records import sequences
    stage = Path(cfg['stage'])
    manifest = read(cfg['manifest'])
    require(sha(cfg['manifest']) == cfg['manifest_sha256'], 'Accepted manifest changed')
    frozen = read(EXP/'frozen-inputs.json')
    validate_manifest(manifest, frozen)
    reference = Path(manifest['reference'])
    require(sha(reference) == manifest['reference_sha256'], 'Frozen reference changed')
    lengths = dict((name,len(seq)) for name,seq in sequences(reference))
    require(len(lengths) == frozen['retained_contigs'] and sum(lengths.values()) == frozen['retained_bp'], 'Canonical population mismatch')
    axes = {c:[] for c in ('C0','CT')}
    for c in axes:
        (stage/'bams'/c).mkdir(parents=True)
        for i,e in enumerate(manifest['samples']):
            print(f"VERIFY {c} sample {e['sample']}", flush=True)
            source = Path(e['directory'])/c/'mapped.bam'
            target = stage/'bams'/c/f'{i:02d}-sample-{e["sample"]}.bam'
            receipt = stage_bam(source, target, e['summary'][c])
            with pysam.AlignmentFile(str(target),'rb') as bam:
                require(list(zip(bam.references,bam.lengths)) == list(lengths.items()), 'BAM reference mismatch')
                require(bam.header.to_dict().get('HD',{}).get('SO') == 'coordinate', 'BAM not coordinate sorted')
                require(bam.check_index() and bam.mapped == e['summary'][c]['records'], 'BAM index/count mismatch')
            axes[c].append({'sample':e['sample'], **receipt})
    write(stage/'inputs.json', {'reference':str(reference), 'reference_sha256':manifest['reference_sha256'],
                              'manifest_sha256':cfg['manifest_sha256'], 'samples':frozen['samples'], 'bams':axes})


def depth_report(path, lengths, names):
    """Validate the native MetaBAT table and summarize zero-depth evidence."""
    import csv
    import numpy as np
    with Path(path).open() as handle:
        rows = list(csv.reader(handle, delimiter='\t'))
    header = rows.pop(0)
    require(header[:3] == ['contigName','contigLen','totalAvgDepth'], 'Wrong depth header')
    require(header[3::2] == [Path(x).stem for x in names], 'Depth sample order mismatch')
    require(all(header[i+1] == header[i]+'-var' for i in range(3,len(header),2)), 'Missing variance columns')
    require([r[0] for r in rows] == list(lengths), 'Depth contig order mismatch')
    require(all(len(r)==3+2*len(names) and int(r[1])==lengths[r[0]] for r in rows), 'Invalid depth rows')
    values = np.array([[float(x) for x in r[2:]] for r in rows])
    require(np.isfinite(values).all() and (values>=0).all(), 'Invalid depth values')
    return {'contigs':len(rows), 'samples':names, 'zero_means_per_sample':(values[:,1::2]==0).sum(axis=0).tolist(), 'sha256':sha(path)}


def native_features(tool, cfg):
    """Extract one complete paired native feature bundle, preserving CS diagnostics."""
    import numpy as np
    from e001lib import native
    from e001lib.records import sequences
    stage = Path(cfg['stage']); out = stage/tool
    inputs = read(stage/'inputs.json'); fasta = Path(inputs['reference'])
    bams = {c:[Path(e['path']) for e in inputs['bams'][c]] for c in ('C0','CT')}
    names = [p.name for p in bams['C0']]
    source = Path(cfg['root'])/'sources'/('COMEBin' if tool=='comebin' else tool)
    native.verify_source('COMEBin' if tool=='comebin' else tool, source)
    lengths = {n:len(s) for n,s in sequences(fasta)}
    report = {'tool':tool, 'samples':inputs['samples'], 'input_manifest_sha256':cfg['manifest_sha256'], 'training':'not run'}
    if tool == 'metabat':
        native.require_packages({'numpy':'2.2.6','biopython':'1.85','pysam':'0.23.3'})
        # The accepted binaries are a reviewed build with a retained build-only patch.
        lock = Path(cfg['root'])/'locks/metabat/binaries.sha256'
        for line in lock.read_text().splitlines():
            digest, filename = line.split(maxsplit=1)
            require(sha(filename.strip()) == digest, 'MetaBAT binary changed')
        report['conditions'] = {}
        for c in ('C0','CT'):
            print('START MetaBAT depth '+c, flush=True)
            (out/c).mkdir()
            command = native.metabat_commands(fasta,bams[c],out/c,threads=cfg['worker_vcpus'])[0]
            if c=='C0' and cfg.get('reused_metabat_depth'):
                shutil.copyfile(cfg['reused_metabat_depth'],out/c/'depth.tsv')
            else:
                native.run_checked(command,out/'logs', 'depth-'+c)
            report['conditions'][c] = depth_report(out/c/'depth.tsv',lengths,names)
        (out/'CS').mkdir()
        native.scale_metabat_depth(out/'C0/depth.tsv',out/'CS/depth.tsv',lengths)
        report['conditions']['CS'] = depth_report(out/'CS/depth.tsv',lengths,names)
        report['CS_interpretation'] = 'Means x0.1, variances x0.01; native absolute-depth filters need not be invariant. No binning executed.'
    elif tool == 'vamb':
        report['conditions'] = {}
        import torch
        torch.set_num_threads(cfg['worker_vcpus']); torch.set_num_interop_threads(1)
        for c in ('C0','CT'):
            print('START VAMB features '+c, flush=True)
            native.vamb_features(source,fasta,bams[c],out/c,threads=cfg['worker_vcpus'])
            import vamb
            composition = vamb.parsecontigs.Composition.load(out/c/'composition.npz')
            abundance = vamb.parsebam.Abundance.load(out/c/'abundance.npz',composition.metadata.refhash)
            ids = (out/c/'ids.txt').read_text().splitlines()
            require(ids == list(lengths), 'VAMB contig axis changed')
            require([Path(str(n)).name for n in abundance.samplenames] == names, 'VAMB sample order mismatch')
            require(abundance.matrix.shape == (len(lengths),len(names)) and np.isfinite(abundance.matrix).all() and (abundance.matrix>=0).all(), 'Invalid VAMB abundance')
            report['conditions'][c] = {'contigs':len(ids), 'zero_means_per_sample':(abundance.matrix==0).sum(axis=0).tolist(), **read(out/c/'native-features.json')}
        require(sha(out/'C0/ids.txt') == sha(out/'CT/ids.txt') and sha(out/'C0/input-mask.npy') == sha(out/'CT/input-mask.npy'), 'VAMB paired masks differ')
        report['CS_location'] = 'C0/normalized-CS.npz; CT/normalized-CS.npz is only an additional adapter diagnostic, not protocol CS'
    else:
        import torch
        torch.set_num_threads(1); torch.set_num_interop_threads(1)
        # A coverage worker also runs bedtools; one worker avoids hidden 2x CPU use.
        for c in ('C0','CT'):
            print('START COMEBin six-view features '+c, flush=True)
            native.comebin_features(source,fasta,stage/'bams'/c,out/c,
                                    fixed=out/'C0' if c=='CT' else None,threads=1)
            require((out/c/'bam_ids.txt').read_text().splitlines() == names, 'COMEBin sample order mismatch')
        report['paired'] = native.validate_comebin_pair(out/'C0',out/'CT')
        native.scale_comebin(out/'C0',out/'CS')
        from get_augfeature import get_kmer_coverage
        views,ids,_,_ = get_kmer_coverage(out/'CS',n_views=6,addvars=True,vars_sqrt=True)
        scaled = np.stack([v.numpy() for v in views])
        np.save(out/'CS/normalized-views.npy',scaled,allow_pickle=False)
        require(list(ids) == list(lengths), 'CS contig axis mismatch')
        full = np.load(out/'C0/normalized-views.npy',allow_pickle=False)
        report['CS_max_abs_difference_per_view'] = np.max(np.abs(full-scaled),axis=(1,2)).tolist()
        report['CS_changed_entries_per_view'] = np.count_nonzero(full!=scaled,axis=(1,2)).tolist()
        report['zero_means_per_sample_view'] = {c:(np.load(out/c/'coverage_mean.npy',allow_pickle=False)==0).sum(axis=2).tolist() for c in ('C0','CT')}
        report['augmentation_sha256'] = sha(out/'C0/augmentation_intervals.npy')
    report['artifacts'] = {str(p.relative_to(out)):{'sha256':sha(p),'bytes':p.stat().st_size}
                           for p in out.rglob('*') if p.is_file() and p.suffix in ('.npy','.npz','.tsv','.txt','.json')}
    write(out/'result.json',report)


def aggregate(cfg):
    """Publish a review gate only when every native paired branch completed."""
    stage = Path(cfg['stage'])
    results = {t:read(stage/t/'result.json') for t in TOOLS}
    require(all(r['input_manifest_sha256']==cfg['manifest_sha256'] and r['samples']==cfg['samples'] for r in results.values()), 'Feature provenance mismatch')
    write(stage/'feature-summary.json',{'status':'features complete; owner return review required before fits',
          'source_commit':cfg['source_commit'], 'manifest_sha256':cfg['manifest_sha256'], 'tools':results,
          'next_pilot':{'replicate':0,'seed':11,'conditions':['C0','CT'],'tools':list(TOOLS),
          'authorized':False,'boundary':'Review actual features/CS differences, costs and remaining 800-core-hour budget first; no score-based scope decisions.'}})


def rule_command(command, env, out, label, timeout=None):
    """Capture native rule commands in the workflow's process group.

    Short import/inventory probes have individual timeouts. Extraction inherits
    the driver's group deadline. No detached grandchildren survive group abort.
    """
    import subprocess
    started=time.monotonic()
    record={'argv':[str(x) for x in command], 'timeout_seconds':timeout,
            'prefix_path':env.get('PATH'), 'threads_env':{k:v for k,v in env.items() if k.endswith('NUM_THREADS')}}
    try:
        with (out/(label+'.stdout')).open('x') as stdout, (out/(label+'.stderr')).open('x') as stderr:
            process=subprocess.Popen(record['argv'],env=env,stdout=stdout,stderr=stderr)
            try:
                record['returncode']=process.wait(timeout=timeout)
            except BaseException:
                record['process_at_failure']={}
                for name in ('status','wchan','syscall'):
                    try:
                        record['process_at_failure'][name]=(Path('/proc')/str(process.pid)/name).read_text()[:8192]
                    except OSError as error:
                        record['process_at_failure'][name]=str(error)
                process.kill();record['returncode']=process.wait();raise
        require(record['returncode']==0, 'Native '+label+' failed; inspect '+str(out))
    except BaseException as error:
        record['error']=repr(error);raise
    finally:
        record['elapsed_seconds']=time.monotonic()-started
        write(out/(label+'.command.json'),record)


def worker(mode, cfg):
    """Run a rule in its persistent isolated runtime, capturing bounded probes."""
    stage=Path(cfg['stage'])
    if mode=='aggregate':
        aggregate(cfg); return
    tool = 'mapping' if mode=='verify' else mode
    out = stage/('verify' if mode=='verify' else mode)
    # Snakemake pre-creates parents of declared output files. Accept only empty
    # directories, and claim the worker exclusively before writing any logs.
    require(not out.is_symlink(), 'Refusing symlinked worker directory')
    out.mkdir(exist_ok=True)
    require(not any(out.iterdir()), 'Refusing previous worker outputs: '+str(out))
    with (out/'worker-started.json').open('x') as handle:
        json.dump({'mode':mode,'pid':os.getpid()},handle)
    prefix = Path(cfg['root'])/'envs'/tool
    env = isolated_env(prefix, cfg['worker_vcpus'] if tool=='metabat' else 1)
    env['TMPDIR'] = str(stage/'tmp')
    python=prefix/'bin/python'
    modules = ['Bio','pysam'] if tool in ('mapping','metabat') else ['numpy','torch','Bio']
    rule_command([python,'-I','-S',CODE/'scripts/e001_native_probe.py',prefix,*modules],env,out,'environment',60)
    if tool=='comebin':
        require((prefix/'bin/bedtools').is_file(), 'Missing persistent bedtools; no automatic install')
        rule_command([prefix/'bin/bedtools','--version'],env,out,'bedtools-version',30)
        require((out/'bedtools-version.stdout').read_text().strip()=='bedtools v2.31.1','bedtools version changed')
        write(out/'bedtools-binary.json',{'sha256':sha(prefix/'bin/bedtools')})
    rule_command([python,'-I','-m','pip','freeze','--all'],env,out,'inventory',60)
    command=[str(python),'-I',str(CODE/'scripts/e001_features.py'),'--native',mode,'--config',cfg['runtime_config']]
    rule_command(command,env,out,'native')


@contextmanager
def progress(stage, interval=1, heartbeat=60):
    """Mirror tool logs and timestamped heartbeats without replacing originals."""
    stop=threading.Event(); positions={}; started=time.monotonic()
    with (stage/'progress.log').open('x') as log:
        def emit(text):
            line=time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime())+' '+text
            print(line,flush=True); log.write(line+'\n'); log.flush()
        def watch():
            last=0
            while not stop.wait(interval):
                paths=[p for p in stage.rglob('*') if p.is_file() and p.suffix in ('.stdout','.stderr','.log') and p.name!='progress.log']
                for p in paths:
                    with p.open(errors='replace') as f:
                        f.seek(positions.get(p,0)); text=f.read(65536);positions[p]=f.tell()
                    for line in text.splitlines(): emit(f'[{p.relative_to(stage)}] {line}')
                elapsed=time.monotonic()-started
                if elapsed-last>=heartbeat:
                    emit(f'RUNNING {elapsed/60:.1f} min; completed tools: '+','.join(t for t in TOOLS if (stage/t/'result.json').exists()));last=elapsed
        thread=threading.Thread(target=watch,daemon=True);thread.start()
        try: yield
        finally: stop.set();thread.join()


def package(stage, root):
    """Return small records/logs only; never follow BAM links into the archive."""
    archive=root/(stage.name+'-return.tar.gz')
    with tarfile.open(archive,'x:gz') as tar:
        for p in sorted(stage.rglob('*')):
            if p.is_file() and not p.is_symlink() and 'bams' not in p.relative_to(stage).parts and p.suffix in ('.json','.log','.stdout','.stderr','.tsv','.txt'):
                tar.add(p,arcname=stage.name+'/'+str(p.relative_to(stage)),recursive=False)
    Path(str(archive)+'.sha256').write_text(sha(archive)+'  '+archive.name+'\n')
    print('RETURN:',archive,'and .sha256',flush=True)


def ensure_git(env, stage):
    """Recheck the disposable container; bootstrap only Git if absent.

    Uses Python's existing timed command runner, so no missing timeout utility
    is needed. Installs no tool packages and never changes experiment prefixes.
    """
    if shutil.which('git',path=env.get('PATH')):
        return
    require(Path('/usr/bin/apt-get').is_file(), 'Git missing and no supported Ubuntu apt-get')
    command=[] if os.geteuid()==0 else ['sudo','-n']
    require(not command or shutil.which('sudo',path=env.get('PATH')), 'Git bootstrap needs root or noninteractive sudo')
    invoke([*command,'/usr/bin/apt-get','update'],env,stage,'container-apt-update',600)
    invoke([*command,'/usr/bin/apt-get','install','-y','--no-install-recommends','git'],
           dict(env,DEBIAN_FRONTEND=noninteractive),stage,'container-git-install',600)
    require(shutil.which('git',path=env.get('PATH')), 'Git still unavailable after container bootstrap')


def reuse_reviewed(stage, previous, cfg):
    """Reuse only checksum-bound outputs from the reviewed t8lpankx return.

    Rehash retained BAMs/indexes and accepted VAMB artifacts, copy small features
    and the valid MetaBAT C0 table; never modify the previous attempt or recopy
    BAMs. Existing outputs satisfy the DAG, leaving only missing work scheduled.
    """
    accepted=read(EXP/'feature-partial-observed.json')
    require(str(previous)==accepted['directory'], 'Unreviewed reuse attempt')
    for name,digest in accepted['reuse_sha256'].items():
        require(sha(previous/name)==digest, 'Changed reuse record: '+name)
    inputs=read(previous/'inputs.json')
    require(inputs['manifest_sha256']==cfg['manifest_sha256'],'Reuse manifest mismatch')
    require(sha(inputs['reference'])==inputs['reference_sha256'],'Reference changed')
    for entries in inputs['bams'].values():
        for entry in entries:
            p=Path(entry['path'])
            require(p.stat().st_size==entry['bytes'] and sha(p)==entry['sha256'],'Reused BAM changed')
            require(sha(Path(str(p)+'.bai'))==entry['index_sha256'],'Reused index changed')
    result=read(previous/'vamb/result.json')
    for name,receipt in result['artifacts'].items():
        require(sha(previous/'vamb'/name)==receipt['sha256'],'VAMB artifact changed: '+name)
    shutil.copyfile(previous/'inputs.json',stage/'inputs.json')
    (stage/'vamb').mkdir()
    for name in [*result['artifacts'],'result.json']:
        dest=stage/'vamb'/name;dest.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(previous/'vamb'/name,dest)
    shutil.copyfile(previous/'metabat/C0/depth.tsv',stage/'reused-metabat-depth.tsv')
    cfg['reused_metabat_depth']=str(stage/'reused-metabat-depth.tsv')
    write(stage/'reuse.json',{'previous':str(previous),'review_sha256':sha(EXP/'feature-partial-observed.json'),
                            'reused':['input aliases','VAMB C0/CT/CS','MetaBAT C0 depth']})


def run(root, data_root, manifest, cpus, ram, snapshot, reuse_attempt=None):
    """Create a unique attempt, run the real DAG, and always package failure evidence."""
    resources=resource_plan(cpus,ram)
    require(all(p.is_absolute() and p.is_dir() for p in (root,data_root)), 'Existing absolute roots required')
    stage=Path(tempfile.mkdtemp(prefix='multisample-features-',dir=data_root))
    start=time.monotonic();status=1
    env=isolated_env(); plan=read(EXP/'feature-plan.json')
    try:
        with progress(stage):
            (stage/'tmp').mkdir(); (stage/'logs').mkdir(); (stage/'benchmarks').mkdir()
            require(shutil.disk_usage(stage).free>=plan['minimum_free_bytes'],'Need 15 GB free for copied sample 0/features; preserve data')
            ensure_git(env,stage)
            require(sha(EXP/'config.json')==read(EXP/'frozen-inputs.json')['config_sha256'],'Frozen config changed')
            accepted=read(EXP/'multisample-preprocess-observed.json')
            require(sha(manifest)==accepted['manifest_sha256'],'Use the accepted BAM manifest')
            m=read(manifest); validate_manifest(m,read(EXP/'frozen-inputs.json'))
            shutil.copyfile(manifest,stage/'bam-manifest.json')
            cfg={**resources,'feature_plan':plan,'stage':str(stage),'root':str(root),'manifest':str(stage/'bam-manifest.json'),
                 'manifest_sha256':sha(manifest),'samples':[e['sample'] for e in m['samples']],
                 'reference':m['reference'],'source_commit':(CODE/'SOURCE_COMMIT').read_text().strip(),
                 'helper':str(CODE/'scripts/e001_features.py'),'driver_python':sys.executable,
                 'runtime_config':str(stage/'runtime.json')}
            if reuse_attempt is not None:
                reuse_reviewed(stage,reuse_attempt,cfg)
            write(stage/'runtime.json',cfg)
            prefix=stage_runtime(root,snapshot,env,stage)
            workflow=prefix/'bin/snakemake'
            env['PATH']=str(prefix/'bin')+os.pathsep+env.get('PATH','');env['TMPDIR']=str(stage/'tmp')
            probe="import sys,site,sysconfig,importlib.metadata as m; from pathlib import Path; p=Path(sys.argv[1]).resolve(); assert Path(sys.prefix).resolve()==p and not site.ENABLE_USER_SITE; assert Path(sysconfig.get_path('stdlib')).resolve().is_relative_to(p); assert all(Path(d.locate_file('')).resolve().is_relative_to(p) for d in m.distributions()); print(p)"
            invoke([prefix/'bin/python','-I','-c',probe,prefix],env,stage,'workflow-prefix',60)
            workflow_preflight(workflow,env,stage)
            require(sha(stage/'workflow-lock.stdout')==read(EXP/'sample0-preprocess-observed.json')['member_sha256']['workflow-lock.stdout'],'Workflow inventory differs')
            cmd=['--snakefile',CODE/'workflows/e001-preprocess/features.smk','--directory',stage,
                 '--configfile',stage/'runtime.json','--cores',cpus,'--executor','local','--resources',
                 f"mem_mb={resources['memory_budget_mb']}",'tool_slots=1','--keep-going','--keep-incomplete','--printshellcmds','--benchmark-extended']
            invoke(workflow_command(workflow,'snakemake',cmd+['--dry-run']),env,stage,'dag',120)
            remaining=plan['group_core_hour_limit']*3600/cpus-(time.monotonic()-start)
            require(remaining>0,'Feature group budget exhausted')
            invoke(workflow_command(workflow,'snakemake',cmd,0),env,stage,'workflow',remaining)
            require((stage/'feature-summary.json').is_file(),'No complete feature receipt')
            status=0
    except Exception:
        write(stage/'failure.json',{'traceback':traceback.format_exc()});print(traceback.format_exc(),file=sys.stderr)
    finally:
        elapsed=time.monotonic()-start
        write(stage/'status.json',{'exit_code':status,**resources,'elapsed_seconds':elapsed,
              'allocated_core_hours':elapsed*cpus/3600,'group_core_hour_limit':plan['group_core_hour_limit'],
              'feature_bytes':sum(p.stat().st_size for p in stage.rglob('*') if p.is_file() and 'bams' not in p.relative_to(stage).parts),
              'note':'Excludes external BAMs, outside-driver idle/setup and return packaging; linked/copied BAM receipts are in inputs.json. No fitting.'})
        try: package(stage,root)
        except Exception:
            status=1;record=read(stage/'status.json');record.update(exit_code=1,packaging_failed=True);write(stage/'status.json',record)
            print('Packaging failed; preserve attempt:',stage,traceback.format_exc(),file=sys.stderr)
    return status


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('root',type=Path,nargs='?');p.add_argument('--data-root',type=Path);p.add_argument('--manifest',type=Path)
    p.add_argument('--vcpus',type=int);p.add_argument('--ram-gb',type=float);p.add_argument('--workflow-snapshot',type=Path);p.add_argument('--reuse-attempt',type=Path)
    p.add_argument('--worker',choices=('verify',*TOOLS,'aggregate'));p.add_argument('--native',choices=('verify',*TOOLS));p.add_argument('--config',type=Path)
    a=p.parse_args()
    if a.native or a.worker:
        require(a.config is not None,'Worker config required');cfg=read(a.config)
        logging.basicConfig(level=logging.INFO,format='%(asctime)s %(message)s')
        if a.native=='verify': verify_inputs(cfg)
        elif a.native: native_features(a.native,cfg)
        else: worker(a.worker,cfg)
    else:
        if any(v is None for v in (a.root,a.data_root,a.manifest,a.vcpus,a.ram_gb,a.workflow_snapshot)):
            p.error('root, --data-root, --manifest, --vcpus, --ram-gb and --workflow-snapshot required')
        raise SystemExit(run(a.root,a.data_root,a.manifest,a.vcpus,a.ram_gb,a.workflow_snapshot,a.reuse_attempt))
