#!/usr/bin/env python3
"""Held E034 template pilot and conditional graph comparison on existing CPU.

No provisioning, mapping, detector, old-model fit or truth input exists. Fresh
financial/source/schema/runtime/tiny/watchdog gates precede the two pilots. Both
pilots finish even when useful support is insufficient. Every accepted sample
and stage is reused by verified bytes only; there is no automatic science retry.
"""
import argparse,json,os
from pathlib import Path
import shutil,subprocess,sys,time,traceback,urllib.request
ROOT=Path(__file__).absolute().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from e024_coverage import binding,write
from e021_control_json import publish
from e009_owner import supervisor
from e009_exit_watchdog import identity
from e033_phase import validate_config as common_configuration
from e033_recovery import DiskHistory
from e021_portable_node import storage_upload

EXP=ROOT/'experiments/E034-genome-graph';UNITS=['E009-noGLM','E009-GLM','oral-noGLM']


def validate_config(c,now=None):
    """Reuse the tested full clock/credit schema, then restrict E034 scope."""
    common_configuration(c,now)
    if (not c['root'].startswith('/srv/dl_binner/experiments/e034/') or not c['service_name'].startswith('e034-')
        or c['limits']!=json.loads((EXP/'limits.json').read_text()) or c['financial']['ceiling_USD']!=15):
        raise ValueError('E034 resource/phase/credit scope differs')
    return True


def status(c,value):
    """Publish a compact progress pointer, never a substitute for terminal exits."""
    q=urllib.request.Request('http://metadata.google.internal/computeMetadata/v1/instance/guest-attributes/e034-candidate/status',data=json.dumps(dict(value,root=c['root'],source=c['source_commit'],epoch=time.time())).encode(),method='PUT',headers={'Metadata-Flavor':'Google','Content-Type':'application/json'})
    try:
        with urllib.request.urlopen(q,timeout=3) as f:f.read(1024)
    except Exception as error:print('E034_GUEST_STATUS_UNAVAILABLE',repr(error),flush=True)


def evidence(root):
    """Snapshot only closed phase records and worker logs; never live terminal/SDK auth."""
    root=Path(root);out=root/('evidence-'+str(time.time_ns()));out.mkdir()
    for n in ['config.json','science-plan.json','host.json','release.json','started.json']:
        shutil.copyfile(root/n,out/n)
    terminal=root/'terminal.log'
    if terminal.is_file():
        if terminal.stat().st_size>64*1024**2:raise ValueError('Phase terminal snapshot exceeds bounded evidence scope')
        shutil.copyfile(terminal,out/'terminal-at-snapshot.log')
    for name in ['logs','gates']:
        (out/name).mkdir()
        for p in (root/name).rglob('*'):
            if p.is_file() and p.name!='filesystem.jsonl':
                target=out/name/p.relative_to(root/name);target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,target)
    return out


def collect(c,result,units):
    """Preserve closed scientific caches plus small failure evidence within 4 GiB."""
    from e034_collect import pack
    root=Path(c['root']);task=Path(c['task_filesystem']);e=evidence(root);returned=[];total=0
    # Original source BAM copies/collator scratch/runtime caches are disposable,
    # not scientific output members. Preserve their explicit failure inventories.
    links=task/'link-return';links.mkdir()
    for p in (task/'links').rglob('*'):
        if p.is_file() and (p.name in ['completed.json','source-restore.json','CRC32C.stdout','CRC32C.stderr'] or 'links' in p.parts[len((task/'links').parts):] and p.name not in ['observations.bin'] and not (p.name.startswith('collate.') and p.suffix=='.bam')):
            if 'hash-cli-config' in p.parts:continue
            target=links/p.relative_to(task/'links');target.parent.mkdir(parents=True,exist_ok=True);os.link(p,target)
    for label,work in [('links',links)]+[(u,task/'science'/u) for u in units if (task/'science'/u).exists()]:
        # Sealed completed scientific work is complete. An incomplete failed
        # target is retained with its actual outputs, never assigned a score.
        out=task/('return-'+label);proof=pack(work,e,out);total+=proof['archive']['bytes']
        if total>c['limits']['aggregate_compressed_bytes']:raise ValueError('Frozen aggregate return cap exceeded')
        delivered={n:storage_upload(out/n,c['archive_prefix']+label+'/'+n) for n in ['e033-evidence.tar.gz','inventory.json','collection.json','e033-evidence.tar.gz.sha256']}
        returned.append(dict(label=label,archive=proof['archive'],inventory=binding(out/'inventory.json'),delivered=delivered))
    result.update(collections=returned,collection_readback_verified=True,aggregate_compressed_bytes=total)


def run(path):
    """Hold until supervision, then gate/pilot/conditionally compare and close delivery."""
    c=json.loads(Path(path).read_text());validate_config(c);root=Path(c['root']);task=Path(c['task_filesystem']);p=json.loads(Path(c['plan']).read_text());deadline=c['review_deadline_epoch']
    sup=supervisor();env=sup.isolated_env(4);env.update(NUMBA_NUM_THREADS='4',NUMBA_CACHE_DIR=str(task/'numba-cache'),TMPDIR=str(task/'tmp'),E034_HASH_CONFIG=str(root/'tmp/hash-cli'),E034_RELEASE_FILE=str(root/'release.json'),HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1',TOKENIZERS_PARALLELISM='false')
    publish(dict(pid=os.getpid(),identity=identity(os.getpid()),epoch=time.time()),root/'started.json')
    result=dict(status='FAILED',science_completed=False,pilot_completed=False,comparison_admitted=False,stages=[],source=c['source_commit'],root=str(root));disk=None
    def command(label,argv,reserve=1800):
        remaining=deadline-time.time()-reserve
        if remaining<10:raise TimeoutError('Original E034 common clock exhausted')
        status(c,dict(status='RUNNING',stage=label));r=sup.supervise(list(map(str,argv)),root/'logs'/(label+'.log'),remaining,26_000_000_000,env,sample_root=os.getpid());result['stages'].append(dict(stage=label,resources=r));return r
    def scientific(args):return [c['python'],'-I','-B',*args]
    try:
        while not(root/'release.json').exists():
            if time.time()>=c['setup_deadline_epoch']:raise TimeoutError('Held setup deadline exhausted')
            time.sleep(.2)
        release=json.loads((root/'release.json').read_text());watch=json.loads((root/'logs/watchdog-live-before-release.json').read_text())
        if release['config']!=binding(path) or release['plan']!=binding(c['plan']) or not release['watchdog_verified'] or not release['provider_STOP_verified'] or watch['decision']!='workflow alive':raise ValueError('Fresh held supervision/source release missing')
        from e034_control import freeze
        freeze()
        if subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()!=c['source_commit'] or subprocess.check_output(['git','status','--porcelain'],cwd=ROOT,text=True).strip():raise ValueError('Exact clean frozen source required')
        disk=DiskHistory(c);disk.start();(task/'tmp').mkdir()
        from e023_gates import workflow_probe
        command('workflow-origin',[c['workflow_python'],'-I','-B','-c',workflow_probe('3.12.10','9.16.3')])
        command('owned-package-install',[str(Path(c['base'])/'bin/python'),'-I','-B',ROOT/'scripts/e033_install.py','--base',c['base'],'--destination',str(Path(c['python']).parent.parent),'--wheel',c['wheel'],'--pysam-wheel',c['pysam_wheel'],'--lock',EXP/'candidate-lock.json','--output',root/'gates/install.json'])
        command('complete-native-runtime',scientific([ROOT/'scripts/e034_runtime.py','--base',c['base'],'--reference',c['reference'],'--candidate-lock',EXP/'candidate-lock.json','--pysam-wheel',c['pysam_wheel'],'--output',root/'gates/runtime.json']))
        command('original-inputs-before',scientific([ROOT/'scripts/e034_native.py','--plan',c['plan'],'--action','inputs','--output',root/'gates/inputs-before.json']))
        command('actual-native-tiny',scientific([ROOT/'scripts/e034_tiny.py','--root',root/'gates/tiny','--workflow-python',c['workflow_python']]))
        pilots={}
        for community,index in [('E009',0),('oral',8)]:
            unit='oral-noGLM' if community=='oral' else 'E009-noGLM';at=task/'links'/community/('sample-%02d'%index)
            command('pilot-'+community,scientific([ROOT/'scripts/e034_pilot.py','--community',community,'--index',index,'--features',p['units'][unit]['features'],'--output',at]))
            pilots[community]=json.loads((at/'completed.json').read_text())
        result.update(pilot_completed=True,pilot_utilities={k:v['utility'] for k,v in pilots.items()})
        if any(v['utility']['status']!='PASS' for v in pilots.values()):
            result.update(status='INSUFFICIENT_ASSEMBLY_LINK_SUPPORT',disposition='NOT_ASSESSED',reason='Frozen pilot utility gate failed for these assemblies/library/mapping inputs; not a paired-link method-family verdict')
        else:
            # A measured full-cache projection precedes eighteen more samples.
            projected=sum((v['reader_wall_seconds']+v['restore'].get('wall_seconds',0))*10*1.5 for v in pilots.values())+8*3600
            # Conservative Python pooling overhead plus full node/context
            # caches, and serial source/collator/return coexistence. These are
            # forecasts, in addition to live hard RSS/disk enforcement.
            pool_RSS=6*1024**3+sum(v['physical_edges']*10*1.5*800 for v in pilots.values())
            peak_disk=18*1024**3+max(v['source']['bytes'] for v in pilots.values())*3
            if pool_RSS>c['limits']['RSS_bytes'] or peak_disk>c['limits']['extra_bytes']:raise MemoryError('Measured full-cache memory/disk projection refused')
            if projected>deadline-time.time()-1800:raise TimeoutError('Measured complete serial schedule cannot fit original clock')
            write(root/'gates/pilot-schedule.json',dict(status='PASS',remaining_seconds=deadline-time.time(),forecast_seconds=projected,forecast_pool_RSS_bytes=pool_RSS,forecast_peak_disk_bytes=peak_disk,source='Measured two retained-BAM readers/restores plus eight-hour graph/construction/collection reserve; later full-shape fit probe still required'))
            for community in ['E009','oral']:
                for index in range(10):
                    if index==(0 if community=='E009' else 8):continue
                    unit='E009-noGLM' if community=='E009' else 'oral-noGLM';at=task/'links'/community/('sample-%02d'%index)
                    command('links-'+community+'-%02d'%index,scientific([ROOT/'scripts/e034_pilot.py','--community',community,'--index',index,'--features',p['units'][unit]['features'],'--output',at]))
            command('pool-admit-graphs',scientific([ROOT/'scripts/e034_native.py','--plan',c['plan'],'--action','pool']))
            pooled=json.loads((root/'gates/pooled.json').read_text())
            if any(v['status']!='PASS' for v in pooled['utility'].values()):
                result.update(status='INSUFFICIENT_ASSEMBLY_LINK_SUPPORT',disposition='NOT_ASSESSED',pooled=pooled)
            else:
                for kind in ['bootstrap','measurements']:
                    where=Path(p['source_cache']) if kind=='bootstrap' else task/'original-measurements'
                    command('restore-'+kind,scientific([ROOT/'scripts/e034_restore.py','--kind',kind,'--output',where]))
                command('full-native-admission',scientific([ROOT/'scripts/e034_native.py','--plan',c['plan'],'--action','probe']))
                gate=json.loads((root/'gates/full-schedule.json').read_text())
                if gate['status']!='PASS' or gate['forecast_seconds']>deadline-time.time()-1800:raise ValueError('Full native comparison schedule refused')
                result['comparison_admitted']=True
                command('serial-three-mode-graph-comparison',scientific([ROOT/'scripts/e034_control.py','--plan',c['plan'],'--workflow']))
                result.update(status='SUCCESS',science_completed=True)
    except BaseException as error:
        result.update(status='FAILED',error=repr(error),traceback=traceback.format_exc());print(result['traceback'],flush=True)
        # The supervisor's actual exit survives even when it raises on failure.
        known={x['stage'] for x in result['stages']}
        for exitpath in (root/'logs').glob('*.exit.json'):
            label=exitpath.name.removesuffix('.exit.json')
            if label not in known:result['stages'].append(dict(stage=label,resources=json.loads(exitpath.read_text())))
    # A failed integrity/audit check must not prevent evidence collection. It
    # disqualifies the result and remains an explicit failed terminal contract.
    try:
        if (root/'gates/inputs-before.json').exists():
            command('original-inputs-after',scientific([ROOT/'scripts/e034_native.py','--plan',c['plan'],'--action','inputs','--output',root/'gates/inputs-after.json']),reserve=900)
            if json.loads((root/'gates/inputs-before.json').read_text())!=json.loads((root/'gates/inputs-after.json').read_text()):raise ValueError('Accepted original inputs changed')
        for kind,where in [('bootstrap',Path(p['source_cache'])),('measurements',task/'original-measurements')]:
            if (where/'stream-admission.json').exists():command('verify-reused-'+kind,scientific([ROOT/'scripts/e034_restore.py','--kind',kind,'--output',where]),reserve=900)
    except BaseException as error:
        result.update(status='FAILED',integrity_after_error=repr(error),integrity_after_traceback=traceback.format_exc())
        print('E034_AFTER_CHECK_FAILED',traceback.format_exc(),flush=True)
    try:
        collect(c,result,UNITS if (task/'science').exists() else [])
        closed=evidence(root);empty=root/'closed-empty';empty.mkdir();from e034_collect import pack
        close=task/'closed-return';proof=pack(closed,empty,close)
        total=result['aggregate_compressed_bytes']+proof['archive']['bytes']
        if total>c['limits']['aggregate_compressed_bytes']:raise ValueError('Closed delivery exceeds aggregate return cap')
        result['aggregate_compressed_bytes']=total
        result['closed_delivery_archive']=storage_upload(close/'e033-evidence.tar.gz',c['archive_prefix']+'closed-delivery/e033-evidence.tar.gz');result['closed_delivery_inventory']=storage_upload(close/'inventory.json',c['archive_prefix']+'closed-delivery/inventory.json')
        if disk is not None:
            result['filesystem']=disk.close();result['filesystem_delivery']=storage_upload(root/'logs/filesystem.jsonl',c['archive_prefix']+'filesystem.jsonl')
            if result['filesystem']['monitor_error']is not None:result['status']='FAILED'
        result['finished_epoch']=time.time();publish(result,root/'completion.json');delivered=storage_upload(root/'completion.json',c['archive_prefix']+'completion.json')
        tail=dict(status='PASS',completion=delivered,science_completed=result['science_completed'],epoch=time.time());publish(tail,root/'closed-delivery-tail.json');storage_upload(root/'closed-delivery-tail.json',c['archive_prefix']+'closed-delivery-tail.json')
        status(c,dict(status=result['status'],science_completed=result['science_completed'],pilot_completed=result['pilot_completed'],completion_delivery_verified=True));return 0 if result['status']!='FAILED' else 1
    except BaseException as error:
        print('E034_FINAL_DELIVERY_FAILED',repr(error),traceback.format_exc(),flush=True);status(c,dict(status='FAILED_FINAL_DELIVERY',error=repr(error)));return 1


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--config',required=True,type=Path);raise SystemExit(run(p.parse_args().config))
