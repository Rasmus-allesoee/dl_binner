#!/usr/bin/env python3
"""Finish only the failed-to-complete Mac bridge diagnostics on the existing VM.

This read-only gate never fits or reconstructs community science. It consumes
the independently admitted original bridge, exact original features, and the
already retained E030 truth payload. Truth stays in a separate lexical review
view, absent from the learning plan and all training inputs. Original Mac
storage/portability failures remain failures. Resources retain the eight-GB
review cap and original one-hour review deadline.
"""
import argparse
import hashlib
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tarfile
import time

ROOT = Path(__file__).absolute().parents[1]
sys.path.insert(0, str(ROOT/'scripts'))
from e024_coverage import binding, write
from e009_owner import supervisor
from e009_controls import PhaseGuard
from e031_phase import readback


def prepare_view(repo, view, prior, wanted_payload):
    """Reuse exact old truth files read-only, with no bulk copy or source mutation."""
    source = Path(prior); proof = json.loads((source/'inputs.json').read_text())['payload']
    if proof != wanted_payload:
        raise ValueError('Accepted existing truth payload proof differs')
    files = proof['files']
    for name, expected in files.items():
        member=Path(name)
        if (member.is_absolute() or '..' in member.parts or not name.startswith('artifacts/')
                or (source/'view'/name).is_symlink() or binding(source/'view'/name) != expected):
            raise ValueError('Retained truth/source payload bytes differ: '+name)
    view.mkdir(exist_ok=False); (view/'scripts').mkdir()
    for script in (repo/'scripts').glob('*.py'):
        (view/'scripts'/script.name).symlink_to(script)
    (view/'experiments').symlink_to(repo/'experiments', target_is_directory=True)
    # Directory aliases keep each final artifact a regular, SHA-bound file.
    # They are an explicit read-only review view, never a portable environment.
    for relative in ['artifacts/e009-truth-v2/20261015/attempt-local-v2/truth-v2',
                     'artifacts/e014-multiview-reconstruction/oral-truth-origin-v1']:
        target = view/relative; target.parent.mkdir(parents=True, exist_ok=True)
        target.symlink_to(source/'view'/relative, target_is_directory=True)
    for clean in ['artifacts/e014-multiview-reconstruction/inspection-20261019/oral-marker-review.json',
                  'artifacts/e011-cached-grouping-reference/restore-local/candidate/markers/evidence.json']:
        target = view/clean; target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source/'view'/clean, target)
    return dict(status='PASS', consumed_existing_payload=proof,
                truth_is_separate_from_training=True, original_truth_not_rewritten=True)


def run(config):
    """Complete the two Oral reviews and return every compact diagnostic member."""
    cfg = json.loads(Path(config).read_text()); root = Path(cfg['root']); repo = Path(cfg['repo'])
    control = json.loads((root/'payload/bridge-review-control.json').read_text())
    if (control['RSS_bytes'] != 8_000_000_000 or control['threads'] != 4
            or time.time() >= control['deadline_epoch']
            or control['science_source'] != '31962f85af266801687885a41fbf6e933cabc33b'):
        raise ValueError('Original read-only review scope/deadline differs')
    original = Path(control['original_bridge'])
    for name, expected in control['original_control_bindings'].items():
        if binding(original/name) != expected:
            raise ValueError('Independently admitted bridge byte differs: '+name)
    folder = root/'bridge-review'; folder.mkdir(exist_ok=False); view = folder/'view'
    payload = prepare_view(repo, view, control['truth_payload_root'], control['truth_payload'])
    base = folder/'admission'; base.mkdir()
    for name in ['admission.json','inventory.json']:
        shutil.copyfile(root/'payload'/('bridge-'+name),base/name)
    p = json.loads(Path(cfg['plan']).read_text())
    outputs = folder/'outputs'; outputs.mkdir(); sup = supervisor(); env = sup.isolated_env(4)
    env.update(NUMBA_NUM_THREADS='4', NUMBA_CACHE_DIR=str(folder/'native-cache'))
    stages = []
    with PhaseGuard(root, control['deadline_epoch']-time.time(), growth_bytes=4*1024**3) as disk_guard:
        for role in ['teacher','student']:
            label = 'review-oral-noGLM-'+role
            remaining = control['deadline_epoch']-time.time()-180
            if remaining < 30:
                raise TimeoutError('Original cumulative one-hour diagnostic clock exhausted')
            argv = [p['python'],'-I','-B',str(view/'scripts/e031_review.py'),
                '--base',str(base),'--staged',str(original),'--unit','oral-noGLM','--role',role,
                '--features',p['units']['oral-noGLM']['features'],'--comparison','bridge',
                '--marker-clean',str(view/'artifacts/e014-multiview-reconstruction/inspection-20261019/oral-marker-review.json'),
                '--truth-root',str(view/'artifacts/e014-multiview-reconstruction/oral-truth-origin-v1'),
                '--output',str(outputs/label)]
            resources = sup.supervise(argv, folder/(label+'.log'), remaining, 8_000_000_000, env)
            stages.append(dict(stage=label,resources=resources))
        argv=[p['python'],'-I','-B',str(view/'scripts/e031_neighbors.py'),'--bridge',str(original),
            '--plan',cfg['plan'],'--truth-root',str(view/'artifacts/e014-multiview-reconstruction/oral-truth-origin-v1'),
            '--output',str(outputs/'matched-neighbors.json')]
        resources=sup.supervise(argv,folder/'matched-neighbors.log',control['deadline_epoch']-time.time()-180,8_000_000_000,env)
        stages.append(dict(stage='matched-neighbors',resources=resources))
    write(folder/'result.json',dict(status='PASS',stages=stages,original_one_hour_deadline=control['deadline_epoch'],
        payload=payload,original_bridge_source=control['science_source'],diagnostic_operations_source=cfg['source_commit'],
        no_science_replayed=True,Mac_storage_failure_not_erased=True,truth_in_learning=False,
        disk_samples=disk_guard.observations))
    files = [x for x in outputs.rglob('*') if x.is_file()]
    files += [x for x in folder.iterdir() if x.is_file()]
    inventory = {str(x.relative_to(folder)):binding(x) for x in files}
    if sum(v['bytes'] for v in inventory.values()) > 128*1024**2:
        raise ValueError('Compact diagnostic logical return cap exceeded')
    archive = folder/'bridge-review.tar.gz'
    with tarfile.open(archive,'x:gz') as out:
        raw = (json.dumps(inventory,sort_keys=True)+'\n').encode(); item=tarfile.TarInfo('inventory.json');item.size=len(raw)
        out.addfile(item,io.BytesIO(raw))
        for name in sorted(inventory):out.add(folder/name,arcname=name,recursive=False)
    if archive.stat().st_size > 32*1024**2:
        raise ValueError('Compact diagnostic compressed return cap exceeded')
    url = cfg['archive_prefix']+'bridge-review.tar.gz'; b = binding(archive)
    subprocess.run([cfg['gcloud'],'storage','cp','--if-generation-match=0',str(archive),url],check=True,env=env,timeout=90)
    readback(cfg['gcloud'],url,b['bytes'],b['sha256'])
    result = dict(status='PASS',archive=b,archive_url=url,members=len(files),every_member_manifest=inventory,
                  collection_readback_verified=True,stages=stages,finished_epoch=time.time())
    write(root/'gates/bridge-review.json',result)
    return result


if __name__ == '__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--config',type=Path,required=True)
    a=p.parse_args();run(a.config)
