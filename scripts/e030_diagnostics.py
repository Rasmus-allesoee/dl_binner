#!/usr/bin/env python3
"""Run only frozen E030 diagnostics on the existing VM under its original clock.

A checksum-bound private evidence payload supplies truth and accepted summaries.
The scientific source, installed package and completed construction stay fixed.
A lexical read-only source view maps existing native feature/marker files without
copying or rewriting accepted caches. No fitting, grouping or cloud creation API
is available here. A separate controller owns the provider STOP and fresh watcher.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tarfile
import time

ROOT=Path(__file__).absolute().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from e024_coverage import binding
from e021_control_json import publish
from e009_exit_watchdog import identity
from e009_owner import supervisor
from e009_controls import PhaseGuard
from e030_phase import service_content,status,readback

SCIENCE='638084d05b257deeb221cade33042e3459025e2d'
START=1793549447.991
DEADLINE=START+21600
RETENTION=1793746800


def check_config(cfg,now):
    """Refuse a new clock, unsupported allocation or mutable scientific consumer."""
    if (cfg['original_start_epoch']!=START or cfg['science_source']!=SCIENCE
        or not now<cfg['review_deadline_epoch']<=DEADLINE<RETENTION
        or cfg['provider_deadline_epoch']>START+22500
        or cfg['incremental_ceiling_USD']!=3 or cfg['numerical_threads']!=4
        or cfg['review_RSS_bytes']!=8_000_000_000):
        raise ValueError('Original credit/clock/source/resource scope differs')
    if cfg['complete_cost_USD_upper']>3 or cfg['credit_only_admitted']is not True:
        raise ValueError('Complete covered cost not admitted')
    return True


def extract_payload(archive,expected,destination):
    """Verify safe, exact members before exposing a new job-private evidence view."""
    from e014_collect import member_path
    if binding(archive)!=expected or expected['bytes']>128*2**20:
        raise ValueError('Bounded evidence payload bytes differ')
    destination=Path(destination);destination.mkdir(exist_ok=False);seen=set();total=0
    with tarfile.open(archive,'r:gz')as a:
        for m in a:
            p=member_path(destination,m.name)
            if not m.isfile()or m.name in seen or m.size<0 or total+m.size>256*2**20:
                raise ValueError('Malformed evidence payload member')
            if not seen and m.name!='payload-inventory.json':raise ValueError('Inventory first required')
            seen.add(m.name);total+=m.size;data=a.extractfile(m).read()
            if m.name=='payload-inventory.json':
                if m.size>2**20:raise ValueError('Evidence inventory too large')
                inventory=json.loads(data);continue
            actual=dict(bytes=len(data),sha256=hashlib.sha256(data).hexdigest())
            if inventory.get(m.name)!=actual:raise ValueError('Evidence payload member differs')
            p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
    if seen!=set(inventory)|{'payload-inventory.json'}:raise ValueError('Missing evidence member')
    return dict(status='PASS_EXACT_EVIDENCE_PAYLOAD',members=len(inventory),logical_bytes=total,files=inventory)


def make_view(repo,view,mappings):
    """Bind exact native files into a fresh lexical source view without science copy."""
    repo=Path(repo);view=Path(view)
    if not view.is_dir()or (view/'scripts').exists():raise ValueError('Fresh evidence view required')
    (view/'scripts').mkdir()
    for p in sorted((repo/'scripts').iterdir()):
        if p.is_file()and p.suffix=='.py':(view/'scripts'/p.name).symlink_to(p)
    (view/'experiments').symlink_to(repo/'experiments',target_is_directory=True)
    proof={}
    for name,v in mappings.items():
        target=view/name;source=Path(v['path'])
        if not name.startswith('artifacts/')or '..'in Path(name).parts or target.exists()or source.is_symlink()or binding(source)!=v['binding']:
            raise ValueError('Native read-only evidence mapping differs')
        target.parent.mkdir(parents=True,exist_ok=True);os.link(source,target)
        proof[name]=dict(source=str(source),binding=binding(target),hardlink=True)
    return proof


def record_progress(root,name,result):
    """Keep one immutable receipt per distinct completed stage, never overwrite."""
    if not name or any(not(c.isalnum()or c=='-')for c in name):
        raise ValueError('Unsafe diagnostic stage label')
    publish(result,Path(root)/('progress-'+name+'.json'))


def reuse_payload_view(prior,proof,destination):
    """Reuse every admitted read-only payload member with verified hardlinks."""
    from e014_collect import member_path
    destination=Path(destination);destination.mkdir(exist_ok=False)
    if proof['status']!='PASS_EXACT_EVIDENCE_PAYLOAD':raise ValueError('Passed payload proof required')
    for name,wanted in proof['files'].items():
        source=member_path(Path(prior),name);target=member_path(destination,name)
        if source.is_symlink()or binding(source)!=wanted:raise ValueError('Passed payload member changed')
        target.parent.mkdir(parents=True,exist_ok=True);os.link(source,target)
    return dict(proof,reused_from=str(prior),no_new_payload_materialization=True)


def prepare(config):
    """Restore small truth/summaries only, verify full bytes, and pin native runtime."""
    cfg=json.loads(Path(config).read_text());check_config(cfg,time.time());root=Path(cfg['root']);repo=Path(cfg['repo'])
    if not os.path.ismount('/srv/dl_binner')or os.cpu_count()!=8:raise ValueError('Existing mounted E2 required')
    if subprocess.check_output(['git','rev-parse','HEAD'],cwd=repo,text=True).strip()!=cfg['operations_source']or subprocess.check_output(['git','status','--porcelain'],cwd=repo,text=True).strip():raise ValueError('Exact clean operations source required')
    frozen=json.loads((repo/'experiments/E030-supported-biological-bins/source-lock.json').read_text())
    for name,wanted in frozen['files'].items():
        if binding(repo/name)!=wanted:raise ValueError('Frozen scientific source altered')
    u=shutil.disk_usage(root)
    if u.free<25*2**30+256*2**20 or u.used-cfg['initial_filesystem_used_bytes']+256*2**20>4*2**30:
        raise ValueError('Original disk growth/reserve cannot admit diagnostics')
    if 'reuse_payload' in cfg:
        old=cfg['reuse_payload'];record=Path(old['root'])/'inputs.json'
        if binding(record)!=old['inputs_binding']:raise ValueError('Passed evidence restoration proof differs')
        payload=reuse_payload_view(Path(old['root'])/'view',json.loads(record.read_text())['payload'],root/'view')
    else:
        payload=extract_payload(root/'payload.tar.gz',cfg['payload'],root/'view')
    mapped=make_view(repo,root/'view',cfg['mappings'])
    base=root/'view/artifacts/e030-supported-biological-bins/inspection'
    admission=json.loads((base/'admission.json').read_text())
    if not all(admission[k]for k in ['archive_and_every_member_verified','workflow_completed','cost_and_retention_admitted'])or admission['provider_status']!='TERMINATED':raise ValueError('Original science not independently admitted')
    host=dict(user=cfg['user'],boot_id=Path('/proc/sys/kernel/random/boot_id').read_text().strip(),filesystem=u._asdict(),epoch=time.time())
    publish(host,root/'host.json');publish(dict(payload=payload,native_mappings=mapped,frozen_science_source=SCIENCE,no_science_repeated=True),root/'inputs.json')
    print('E030_REVIEW_INPUTS_VERIFIED',flush=True)


def run(config):
    """Hold for current-boot supervision, then run six unchanged diagnostic readers."""
    cfg=json.loads(Path(config).read_text());root=Path(cfg['root']);check_config(cfg,time.time())
    logs=root/'logs';sup=supervisor();env=sup.isolated_env(4);env.update(NUMBA_NUM_THREADS='4',PYTHONDONTWRITEBYTECODE='1',HF_HUB_OFFLINE='1',CLOUDSDK_STORAGE_PARALLEL_COMPOSITE_UPLOAD_ENABLED='false',CLOUDSDK_STORAGE_PROCESS_COUNT='1',CLOUDSDK_STORAGE_THREAD_COUNT='2')
    publish(dict(pid=os.getpid(),identity=identity(os.getpid()),epoch=time.time()),root/'started.json')
    result=dict(status='HELD',science_source=SCIENCE,operations_source=cfg['operations_source'],original_start_epoch=START,new_scientific_work=False,stages=[])
    try:
        with PhaseGuard(root,cfg['review_deadline_epoch']-time.time(),growth_bytes=max(0,4*2**30-(shutil.disk_usage(root).used-cfg['initial_filesystem_used_bytes'])))as guard:
            while not(root/'release.json').exists():
                if time.time()>cfg['setup_deadline_epoch']or(root/'abort.json').exists():raise TimeoutError('Read-only review setup expired/refused')
                time.sleep(.2)
            release=json.loads((root/'release.json').read_text())
            watch=json.loads((root/'logs/watchdog-live-before-release.json').read_text())
            if release['config']!=binding(config)or release['provider_STOP_verified']is not True or watch['expected_process']!=identity(os.getpid())or watch['boot_id']!=Path('/proc/sys/kernel/random/boot_id').read_text().strip():raise ValueError('Fresh diagnostic release/watcher differs')
            def command(name,argv,reserve=300):
                left=cfg['review_deadline_epoch']-time.time()-reserve
                if left<10:raise TimeoutError('Original review clock exhausted')
                print('E030_READONLY_STAGE',name,flush=True)
                resources=sup.supervise(argv,logs/(name+'.log'),left,cfg['review_RSS_bytes'],env,sample_root=os.getpid())
                result['stages'].append(dict(name=name,resources=resources));record_progress(root,name,dict(result,status='RUNNING',stage=name))
            view=root/'view';base=view/'artifacts/e030-supported-biological-bins/inspection'
            if 'reuse_review_gates' in cfg:
                old=cfg['reuse_review_gates'];prior=Path(old['root'])
                for name,wanted in old['files'].items():
                    if binding(prior/name)!=wanted:raise ValueError('Passed diagnostic gate bytes differ')
                passed=json.loads((prior/'completion.json').read_text())
                if [v['name']for v in passed['stages']]!=['runtime','frozen-tiny-review-contracts']or any(v['resources']['exit_code']!=0 for v in passed['stages']):raise ValueError('Passed diagnostic gate receipt differs')
                shutil.copyfile(prior/'runtime.json',root/'runtime.json')
                result['reused_gate_proof']=old
                result['stages'].extend(dict(v,reused=True)for v in passed['stages'])
            else:
                command('runtime',[cfg['python'],'-I','-B',str(Path(cfg['repo'])/'scripts/e027_runtime.py'),'--base',cfg['base_python_root'],'--reference',cfg['runtime_reference'],'--candidate-lock',str(Path(cfg['repo'])/'experiments/E030-supported-biological-bins/candidate-lock.json'),'--output',str(root/'runtime.json')])
                command('frozen-tiny-review-contracts',[cfg['python'],'-I','-B','-c',"import sys,unittest;sys.path.insert(0,"+repr(str(Path(cfg['repo'])/'tests'))+");r=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromName('test_e030_review'));sys.exit(not r.wasSuccessful())"])
            for unit in ['E009-noGLM','E009-GLM','oral-noGLM']:
                for role in ['teacher','student']:
                    name='review-'+unit+'-'+role
                    command(name,[cfg['python'],'-I','-B',str(view/'scripts/e030_review.py'),'--base',str(base),'--staged',cfg['science_root'],'--unit',unit,'--role',role,'--output',str(base/name)])
            result['status']='SUCCESS';result['diagnostics_completed']=True
    except BaseException as exc:
        result['status']='FAILED';result['error']=repr(exc)
    publish(result,root/'result.json')
    try:
        sources=[root/'config.json',root/'host.json',root/'inputs.json',root/'runtime.json',root/'result.json',root/'release.json']
        sources += [p for folder in [root/'logs',root/'view/artifacts/e030-supported-biological-bins/inspection']if folder.is_dir()for p in sorted(folder.rglob('*'))if p.is_file()]
        members={str(p.relative_to(root)):binding(p)for p in sources if p.is_file()}
        if len(members)>10000 or sum(v['bytes']for v in members.values())>256*2**20:raise ValueError('Bounded diagnostic collection inventory exceeds cap')
        archive=root/'review-evidence.tar.gz'
        import io
        with tarfile.open(archive,'x:gz')as t:
            data=(json.dumps(members,sort_keys=True)+'\n').encode();m=tarfile.TarInfo('inventory.json');m.size=len(data);t.addfile(m,io.BytesIO(data))
            for n in sorted(members):t.add(root/n,arcname=n,recursive=False)
        if archive.stat().st_size>128*2**20:raise ValueError('Diagnostic compressed return exceeds cap')
        result['archive']=binding(archive);result['members']=len(members)
        g=cfg['gcloud'];uri=cfg['archive_prefix']+'review-evidence.tar.gz'
        subprocess.run([g,'storage','cp','--if-generation-match=0',str(archive),uri],check=True,env=env,timeout=180,capture_output=True)
        readback(g,uri,result['archive']['bytes'],result['archive']['sha256'])
        result['collection_readback_verified']=True
    except BaseException as exc:
        result['status']='FAILED';result['collection_error']=repr(exc)
    result['finished_epoch']=time.time();result['disk']=shutil.disk_usage(root)._asdict();result['config']=binding(config)
    publish(result,root/'completion.json')
    subprocess.run([cfg['gcloud'],'storage','cp','--if-generation-match=0',str(root/'completion.json'),cfg['archive_prefix']+'completion.json'],check=True,env=env,timeout=90,capture_output=True)
    print('E030_READONLY_FINISHED',json.dumps(result),flush=True)
    return 0 if result['status']=='SUCCESS'else 1


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--config',type=Path,required=True);p.add_argument('--prepare',action='store_true');a=p.parse_args()
    if a.prepare:prepare(a.config)
    else:sys.exit(run(a.config))
