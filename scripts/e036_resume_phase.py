#!/usr/bin/env python3
"""Resume E036 with preserved caches, fresh supervision and the original deadline."""
import argparse,json,os,shutil,subprocess,sys,time,traceback
from pathlib import Path
ROOT=Path(__file__).absolute().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from e036_phase import validate_config,status,freeze_sources,collect
from e024_coverage import binding,write
from e021_control_json import publish
from e021_portable_node import storage_upload
from e009_owner import supervisor
from e009_exit_watchdog import identity
from e033_recovery import DiskHistory


def repaired_evidence(root):
    """Archive the effective source overlay and original lock without falsifying either."""
    from e034_phase import evidence as snapshot
    from e036_repair import admit
    admit();root=Path(root);c=json.loads((root/'config.json').read_text());repo=Path(c['repo']);out=snapshot(root)
    original=repo/'experiments/E036-optional-pooled-links/source-lock.json';repair=repo/'experiments/E036-optional-pooled-links/repair-lock.json';r=json.loads(repair.read_text());names=dict(json.loads(original.read_text())['files'])
    for n,b in r['overrides'].items():names[n]=b['after']
    names.update(r['extra_files']);names[str(original.relative_to(repo))]=binding(original);names[str(repair.relative_to(repo))]=binding(repair)
    for n,b in names.items():
        if binding(repo/n)!=b:raise ValueError('Effective collection source differs: '+n)
        p=out/'effective-source-repository'/n;p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(repo/n,p)
    packet=repo.parent/'experiments/e036/source-transports'/('source-'+c['source_commit']+'.bundle')
    if binding(packet)!=c['financial']['source_transport']['bundle']:raise ValueError('Repaired exact source packet differs')
    shutil.copyfile(packet,out/'source.bundle');shutil.copyfile(c['wheel'],out/Path(c['wheel']).name)
    old=Path(c['financial']['recovery']['original_root']);(out/'original-failed-attempt').mkdir()
    for n in ['completion.json','closed-delivery-tail.json','config.json']:
        shutil.copyfile(old/n,out/'original-failed-attempt'/n)
    return out


def run(path):
    """Verify exact read-only runtime/cache reuse, run remaining stages and deliver."""
    c=json.loads(Path(path).read_text());validate_config(c);root=Path(c['root']);task=Path(c['task_filesystem']);r=c['financial']['recovery'];old=Path(r['original_root']);attempt=task/root.name;attempt.mkdir(exist_ok=False)
    p=json.loads(Path(c['plan']).read_text());sup=supervisor();env=sup.isolated_env(4);env.update(NUMBA_NUM_THREADS='4',NUMBA_CACHE_DIR=str(attempt/'numba'),TMPDIR=str(attempt/'tmp'),E036_RELEASE_FILE=str(root/'release.json'));(attempt/'tmp').mkdir()
    publish(dict(pid=os.getpid(),identity=identity(os.getpid()),epoch=time.time()),root/'started.json');result=dict(status='FAILED',science_completed=False,stages=[],root=str(root),source=c['source_commit'],original_root=str(old),original_clock_retained=True,original_science_source=r['original_source']);disk=None
    def command(label,args,reserve=1200):
        remaining=c['review_deadline_epoch']-time.time()-reserve
        if remaining<=10:raise TimeoutError('Original common E036 deadline exhausted')
        status(c,dict(status='RUNNING',stage=label));q=sup.supervise(list(map(str,args)),root/'logs'/(label+'.log'),remaining,26_000_000_000,env,sample_root=os.getpid());result['stages'].append(dict(stage=label,resources=q));return q
    def py(*args):return [c['python'],'-I','-B',*args]
    try:
        while not(root/'release.json').exists():
            if time.time()>c['setup_deadline_epoch']:raise TimeoutError('Held repair setup expired')
            time.sleep(.2)
        release=json.loads((root/'release.json').read_text())
        if release['config']!=binding(path)or release['plan']!=binding(c['plan'])or not release['watchdog_verified']or not release['provider_STOP_verified']:raise ValueError('Fresh recovery release differs')
        freeze_sources()
        if subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()!=c['source_commit']or subprocess.check_output(['git','status','--porcelain'],cwd=ROOT,text=True).strip():raise ValueError('Exact clean repaired source required')
        disk=DiskHistory(c);disk.start()
        command('runtime-readonly-reuse',py(ROOT/'scripts/e035_pool_runtime.py','--base',c['base'],'--reference',c['reference'],'--candidate-lock',ROOT/'experiments/E036-optional-pooled-links/candidate-lock.json','--pysam-wheel',c['pysam_wheel'],'--output',root/'gates/runtime.json'))
        command('repaired-production-layout-tiny',py(ROOT/'scripts/e036_tiny.py','--root',attempt/'tiny','--workflow-python',c['workflow_python']))
        command('original-inputs-before',py(ROOT/'scripts/e036_native.py','--plan',c['plan'],'--action','inputs','--output',root/'gates/inputs-before.json'))
        for kind in ['pooled','baseline','bootstrap','measurements']:command('verify-reused-'+kind,py(ROOT/'scripts/e036_restore.py','--kind',kind,'--output',task/('original-'+kind)))
        command('verify-original-gates-and-preserve-partial',py(ROOT/'scripts/e036_resume.py','--config',path))
        command('serial-remaining-optional-graph',py(ROOT/'scripts/e036_control.py','--plan',c['plan'],'--workflow'))
        command('native-result-contracts',py(ROOT/'scripts/e036_native.py','--plan',c['plan'],'--action','final'))
        result.update(status='SUCCESS',science_completed=True)
    except BaseException as e:
        result.update(error=repr(e),traceback=traceback.format_exc());print(result['traceback'],flush=True)
        known={q['stage']for q in result['stages']}
        for f in (root/'logs').glob('*.exit.json'):
            n=f.name.removesuffix('.exit.json')
            if n not in known:result['stages'].append(dict(stage=n,resources=json.loads(f.read_text())))
    try:
        command('original-inputs-after',py(ROOT/'scripts/e036_native.py','--plan',c['plan'],'--action','inputs','--output',root/'gates/inputs-after.json'),reserve=600)
        if json.loads((root/'gates/inputs-before.json').read_text())!=json.loads((root/'gates/inputs-after.json').read_text()):raise ValueError('Protected original inputs changed')
        for kind in ['pooled','baseline','bootstrap','measurements']:command('after-reused-'+kind,py(ROOT/'scripts/e036_restore.py','--kind',kind,'--output',task/('original-'+kind)),reserve=600)
    except BaseException as e:result.update(status='FAILED',after_error=repr(e))
    try:
        # Regular hardlinks give the existing collector a fresh private namespace;
        # accepted caches/science never move or acquire receiver metadata.
        science=attempt/'science';science.mkdir()
        for f in Path(p['work']).rglob('*'):
            if '.snakemake'in f.parts:continue
            if f.is_symlink():raise ValueError('Science symlink refused')
            if f.is_file():
                q=science/f.relative_to(p['work']);q.parent.mkdir(parents=True,exist_ok=True);os.link(f,q)
        # Preserve original failed-stage bytes in the new complete delivery too.
        failed=task/('failed-stage-'+r['original_source'][:7])
        if failed.exists():
            for f in failed.rglob('*'):
                if f.is_file():
                    q=science/'failed-r1'/f.relative_to(failed);q.parent.mkdir(parents=True,exist_ok=True);os.link(f,q)
        cc=dict(c,task_filesystem=str(attempt),limits=dict(c['limits'],aggregate_compressed_bytes=c['limits']['aggregate_compressed_bytes']-r['original_aggregate_export_bytes']))
        import e036_phase
        e036_phase.evidence=repaired_evidence
        collect(cc,result)
        if disk is not None:
            result['filesystem']=disk.close();result['filesystem_delivery']=storage_upload(root/'logs/filesystem.jsonl',c['archive_prefix']+'filesystem.jsonl')
            if result['filesystem']['monitor_error']is not None:result['status']='FAILED'
        result['finished_epoch']=time.time();publish(result,root/'completion.json');proof=storage_upload(root/'completion.json',c['archive_prefix']+'completion.json');publish(dict(status='PASS',completion=proof,science_completed=result['science_completed']),root/'closed-delivery-tail.json');storage_upload(root/'closed-delivery-tail.json',c['archive_prefix']+'closed-delivery-tail.json');status(c,dict(status=result['status'],science_completed=result['science_completed'],completion_delivery_verified=True))
        return 0 if result['status']=='SUCCESS'else 1
    except BaseException as e:
        print('E036_RECOVERY_DELIVERY_FAILED',traceback.format_exc(),flush=True);q=root/('completion-failure-'+str(time.time_ns())+'.json');publish(dict(status='FAILED_DELIVERY',science_completed=result['science_completed'],error=repr(e),evidence_retained_on_disk=True),q)
        try:storage_upload(q,c['archive_prefix']+q.name)
        except Exception:pass
        return 1

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--config',type=Path,required=True);a=p.parse_args();raise SystemExit(run(a.config))
