#!/usr/bin/env python3
"""Serial E024 acquisition/coverage and fixed-learning comparison workers.

This script cannot start a VM, change resources or authorize its own execution.
Native plans require an external held-parent release and source/runtime/credit/
storage gates. Engineering plans only accept local fixture URLs and explicit
small byte caps. Failed stages are never overwritten or automatically retried.
Sealed summaries are reused byte-for-byte; removal of newly acquired raw FASTQ
is explicit, bound and allowed only after full summary admission.
"""
import argparse
import gzip
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time

ROOT = Path(__file__).absolute().parents[1]
sys.path[:0] = [str(ROOT/'scripts'), str(ROOT/'src')]
from e024_coverage import SAMPLES, binding, write, acquire, axis, map_summary, read_profile, combine


def read_plan(path, engineering=False):
    """Refuse expanded science, truth paths and changes to the frozen sample rule."""
    p = json.loads(Path(path).read_text())
    fields = {'kind','work','python','workflow_python','mapper','samtools','reference','inputs',
              'read_manifest','policy','worker','snakefile','limits','engineering'}
    if set(p) != fields or p['kind'] != 'E024 oral measured-depth information' or p['engineering'] is not engineering:
        raise ValueError('Unexpected E024 plan/schema/scope')
    m = json.loads(Path(p['read_manifest']).read_text())
    if (m['ordered_samples'] != SAMPLES or [r['sample'] for r in m['reads']] != SAMPLES
            or sum(r['bytes'] for r in m['reads']) != m['total_read_bytes']):
        raise ValueError('Frozen sample axis/total differs')
    if set(p['inputs']) != {'features','views','embeddings','graph','marker_evidence'}:
        raise ValueError('Unexpected truth/training input')
    if not engineering:
        expected = json.loads((ROOT/'experiments/E024-oral-measured-coverage/runtime-plan.json').read_text())
        if p['limits'] != expected['limits'] or m['total_read_bytes'] > 52_000_000_000:
            raise ValueError('Frozen native limits/read payload differs')
        release_path=os.environ.get('E024_RELEASE_FILE')
        if not release_path or not Path(release_path).is_file():
            raise ValueError('Native held-parent release required before worker')
        release=json.loads(Path(release_path).read_text())
        if release.get('plan')!=binding(path):
            raise ValueError('Active held-parent release/plan binding differs')
        for k in ['mapper','samtools','reference','inputs','python','workflow_python','worker','snakefile','policy','read_manifest']:
            if p[k] != expected[k]:
                raise ValueError('Native existing runtime/reference differs')
        work=Path(p['work'])
        if not work.is_absolute() or not work.is_relative_to('/srv/dl_binner/experiments/e024') or work.is_symlink():
            raise ValueError('Fresh E024-owned native working directory required')
    else:
        if m['total_read_bytes'] > 10*1024**2 or any(not r['url'].startswith('http://127.0.0.1:') for r in m['reads']):
            raise ValueError('Engineering permits only bounded loopback fixture reads')
    return p, m


def fresh(root, name):
    """Allocate an exclusive stage while tolerating only an empty scheduler parent."""
    p = Path(root)/name
    if p.is_dir() and not any(p.iterdir()):
        p.rmdir()
    p.mkdir(parents=True, exist_ok=False)
    write(p/'started.json', dict(stage=name, epoch=time.time()))
    return p


def seal(path, extra=None):
    """Bind closed stage files; the completion marker is published last."""
    path = Path(path)
    files = {str(p.relative_to(path)):binding(p) for p in sorted(path.rglob('*'))
             if p.is_file() and p != path/'done.json'}
    result = dict(status='PASS', files=files, **(extra or {}))
    write(path/'done.json', result)
    return result


def verify_seal(path):
    """Refuse missing/corrupt completed outputs, without copy/install fallback."""
    path = Path(path)
    r = json.loads((path/'done.json').read_text())
    if r.get('status') != 'PASS':
        raise ValueError('Unaccepted stage seal')
    for name, expected in r['files'].items():
        q = Path(name)
        if q.is_absolute() or '..' in q.parts or binding(path/q) != expected:
            raise ValueError('Changed/missing completed stage member: ' + name)
    return r


def cleanup_read(path, receipt, summary_receipt):
    """Delete only a newly owned regenerable FASTQ after admitted measured summary.

    No accepted input, BAM, old experiment, environment or source is a target.
    The caller retains download+mapper+summary bindings before deletion. This
    policy is only proposed now; tiny generated fixtures exercise it locally.
    """
    path = Path(path)
    if path.name != 'raw.fq.gz' or path.is_symlink():
        raise ValueError('Only this stage-owned raw.fq.gz may be released')
    r = json.loads(Path(receipt).read_text())
    s = json.loads(Path(summary_receipt).read_text())
    if (s.get('status') != 'PASS' or s.get('mapper_exit') != 0
            or s['reads'] != binding(path) or s['depth'] != binding(Path(summary_receipt).parent/'depth.tsv')
            or {k:r[k] for k in ['bytes','sha256']} != binding(path)):
        raise ValueError('Input/summary must be byte-verified before temporary release')
    removed = dict(path=str(path), identity=binding(path), regeneration=r['manifest'],
                   summary=binding(summary_receipt), backup=False,
                   reason='New public raw FASTQ regenerable by publisher segment MD5; complete measured summary retained')
    write(path.parent/'released-raw.json', removed)
    path.unlink()
    return removed


def acquire_one(root, record):
    """Acquire once, or verify a passed download without recopy/reinstall fallback."""
    folder = Path(root)/'downloads'/str(record['sample'])
    if folder.exists():
        receipt=folder/'raw.fq.gz.acquired.json'
        if not receipt.is_file():
            raise ValueError('Unsealed acquisition preserved; assess a fresh attempt, no fallback download')
        r=json.loads(receipt.read_text())
        if (r.get('manifest') != record or r.get('publisher_segment_MD5_passed') != len(record['segments'])
                or {k:r[k] for k in ['bytes','sha256']} != binding(folder/'raw.fq.gz')):
            raise ValueError('Passed acquisition bytes/manifest differ; no fallback download')
        return dict(r,reused_without_download=True)
    folder.mkdir(parents=True, exist_ok=False)
    return acquire(record, folder/'raw.fq.gz')


def stage(plan, name, sample=None, engineering=False):
    """Execute one admitted serial rule and seal the exact outputs it produced."""
    p, m = read_plan(plan, engineering)
    work = Path(p['work'])
    if hasattr(os,'sched_setaffinity'):
        budget=8 if name in ['acquire-first','index','sample'] else 4
        os.sched_setaffinity(0,sorted(os.sched_getaffinity(0))[:budget])
    if name == 'verify':
        out = fresh(work, 'verified')
        inputs = dict(p['inputs'], reference=p['reference'], mapper=p['mapper'], samtools=p['samtools'])
        files = {k:binding(v) for k,v in inputs.items()}
        if not engineering:
            lock = json.loads((ROOT/'experiments/E024-oral-measured-coverage/reuse-lock.json').read_text())
            for name_, expected in lock['files'].items():
                if binding(name_) != expected:
                    raise ValueError('Native retained bytes differ; no fallback: ' + name_)
        version = subprocess.check_output([p['mapper'],'--version'],text=True).strip()
        if version != '0.17.0':
            raise ValueError('Frozen strobealign 0.17.0 required')
        ids, sizes = axis(p['reference'])
        return seal(out, dict(inputs=files, contigs=len(ids), bp=sum(sizes), mapper_version=version,
                              plan=binding(plan), source=source_identity()))
    if name == 'acquire-first':
        acquire_one(work, m['reads'][0])
        out = fresh(work, 'first-acquired')
        return seal(out, dict(input=binding(work/'downloads/6/raw.fq.gz'),
                              acquisition=binding(work/'downloads/6/raw.fq.gz.acquired.json')))
    if name == 'index':
        out = fresh(work, 'index')
        reference = out/'reference.fna'
        # A new regular copy allows the mapper to write only its own adjacent STI.
        shutil.copyfile(p['reference'], reference)
        if binding(reference) != binding(p['reference']):
            raise ValueError('Index reference copy differs')
        profile = read_profile(work/'downloads/6/raw.fq.gz')
        argv = [p['mapper'],'--create-index','-t',str(p['limits']['index_threads']),'-r',str(profile),str(reference)]
        with (out/'index.log').open('x') as log:
            subprocess.run(argv,stdout=log,stderr=subprocess.STDOUT,check=True)
        indexes = list(out.glob('reference.fna*.sti'))
        if len(indexes) != 1 or indexes[0].stat().st_size > p['limits']['index_bytes']:
            raise ValueError('Index size/profile exceeds admitted limit')
        return seal(out, dict(profile=profile, index=binding(indexes[0]), reference=binding(reference), argv=argv))
    if name == 'sample':
        if sample not in SAMPLES:
            raise ValueError('Unknown oral sample')
        if sample != 6:
            verify_seal(work/'samples/6')
            gate = json.loads((work/'pilot/done.json').read_text())
            if gate['status'] != 'PASS':
                raise ValueError('Measured first-sample pilot not admitted')
            acquire_one(work, next(r for r in m['reads'] if r['sample'] == sample))
        out = fresh(work, 'samples/'+str(sample))
        index = verify_seal(work/'index')
        raw = work/'downloads'/str(sample)/'raw.fq.gz'
        if read_profile(raw) != index['profile']:
            raise ValueError('Sample index profile differs; do not silently rebuild')
        started = time.time()
        result = map_summary(p['mapper'],work/'index/reference.fna',raw,out/'mapped',
                             expected_read_length=index['profile'],sample=sample,
                             mapper_threads=p['limits']['mapper_threads'])
        # Reference bytes are exactly identical to the original, not its location.
        if result['reference'] != binding(p['reference']):
            raise ValueError('Summary mapped to a different reference')
        # Read the entire writer output once before deleting the regenerable raw.
        count = 0
        with (out/'mapped/depth.tsv').open() as f:
            if f.readline() != 'contig_id\taligned_read_bases\tlength\tmean\n':
                raise ValueError('Native summary schema differs')
            for ident, length in zip(*axis(p['reference'])):
                row = f.readline().rstrip('\n').split('\t')
                if (len(row) != 4 or row[0] != ident or int(row[2]) != length
                        or int(row[1]) < 0 or row[3] != f'{int(row[1])/length:.17g}'):
                    raise ValueError('Native summary full-axis/denominator differs')
                count += 1
            if f.read(1) or count != result['rows']:
                raise ValueError('Native summary truncated/extra rows')
        download = raw.with_name('raw.fq.gz.acquired.json')
        shutil.copyfile(download, out/'acquisition.json')
        removed = cleanup_read(raw, download, out/'mapped/done.json')
        return seal(out, dict(sample=sample, mapping_seconds=time.time()-started, removed=removed,
                              completed_science='one measured sample; no bins or quality scores'))
    if name == 'pilot':
        first = verify_seal(work/'samples/6')
        out = fresh(work, 'pilot')
        measured=json.loads((work/'samples/6/mapped/done.json').read_text())
        if measured['counters'].get('accepted_alignments',0) <= 0:
            raise ValueError('No positive measured pilot support; do not acquire remaining nine')
        if not engineering:
            clock = json.loads(Path(os.environ['E024_RELEASE_FILE']).read_text())
            original_deadline = clock['vm_start_epoch']+p['limits']['seconds']
            # Full sample 6 is accepted and never rerun; extrapolate its complete
            # acquire/map/summary duration to the remaining nine similar objects.
            sample_seconds = first['mapping_seconds']
            download_seconds = json.loads((work/'samples/6/acquisition.json').read_text())['elapsed_seconds']
            remaining_ratio = sum(r['bytes'] for r in m['reads'][1:])/m['reads'][0]['bytes']
            forecast = 1.5*(sample_seconds+download_seconds)*remaining_ratio + 3*3600
            if forecast > original_deadline-time.time():
                raise TimeoutError('Measured full-sample acquisition/mapping forecast does not fit original clock; no full release')
        else:
            forecast = 0
        return seal(out, dict(status_scope='Accepted full sample6 reused; remaining nine may run once',
                              first_sample=binding(work/'samples/6/done.json'), forecast_remaining_seconds=forecast))
    if name == 'combine':
        out = fresh(work, 'combined')
        combine(p['reference'],[work/'samples'/str(s)/'mapped/depth.tsv' for s in SAMPLES],SAMPLES,out/'depth.tsv')
        return seal(out)
    from e024_information import rebind, run, audit
    u = p['inputs']
    if name == 'rebind':
        if (work/'rebound').is_dir() and not any((work/'rebound').iterdir()):
            (work/'rebound').rmdir()
        rebind(u['features'],u['views'],u['embeddings'],work/'combined/depth.tsv',p['reference'],work/'rebound')
        return
    cfg = json.loads(Path(p['policy']).read_text())
    if name == 'group':
        if (work/'group').is_dir() and not any((work/'group').iterdir()):
            (work/'group').rmdir()
        run(work/'rebound/rebind.json',u['graph'],u['marker_evidence'],work/'group',cfg,4)
        return
    if name == 'export':
        from dl_binner.information.export import export
        out = fresh(work, 'export')
        account = {}
        for arm in ['density','selected']:
            account[arm] = export(work/'rebound/features.npz',work/'group'/(arm+'-partition.json'),
                                  p['reference'],out/arm,include_dna=arm == 'selected')
        write(out/'accounting.json',account)
        return seal(out)
    if name == 'audit':
        out = fresh(work, 'audited')
        value = audit(work/'rebound/rebind.json',u['graph'],u['marker_evidence'],work/'group',cfg)
        before = verify_seal(work/'verified')['inputs']
        for key, source in dict(u, reference=p['reference'], mapper=p['mapper'], samtools=p['samtools']).items():
            if binding(source) != before[key]:
                raise ValueError('Retained input changed after workflow')
        return seal(out, dict(proof=value))
    raise ValueError('Unknown stage')


def source_identity():
    """Bind executed helpers to a commit and local diff without treating dirty as native."""
    return dict(commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
                dirty=bool(subprocess.check_output(['git','status','--porcelain'],cwd=ROOT,text=True).strip()))


def resume_gate(plan, engineering=False):
    """Verify all completed outputs before scheduling; partial stages require review."""
    p, _ = read_plan(plan, engineering)
    work = Path(p['work'])
    for name in ['verified','first-acquired','index','pilot','combined','export','audited']+['samples/'+str(s) for s in SAMPLES]:
        stage_root = work/name
        if (stage_root/'done.json').exists():
            verify_seal(stage_root)
        elif (stage_root/'started.json').exists():
            raise ValueError('Unsealed failed stage preserved; fresh assessed attempt required: ' + name)
    if (work/'verified/done.json').exists():
        before=verify_seal(work/'verified')
        if before['plan'] != binding(plan):raise ValueError('Completed input plan changed')
        for key,source in dict(p['inputs'],reference=p['reference'],mapper=p['mapper'],samtools=p['samtools']).items():
            if binding(source)!=before['inputs'][key]:raise ValueError('Completed original input changed')
    if (work/'rebound/rebind.json').exists():
        from e024_information import load_rebound
        load_rebound(work/'rebound/rebind.json')
    elif (work/'rebound').exists():
        raise ValueError('Unsealed rebind preserved; fresh assessed attempt required')
    if (work/'group/completed.json').exists():
        from e024_information import audit
        audit(work/'rebound/rebind.json',p['inputs']['graph'],p['inputs']['marker_evidence'],work/'group',
              json.loads(Path(p['policy']).read_text()))
    elif (work/'group').exists() and any((work/'group').iterdir()):
        raise ValueError('Unsealed grouping preserved; fresh assessed attempt required')
    return p


def workflow(plan, engineering=False, dry_run=False, until_pilot=False):
    """Run the serial DAG with eight node CPUs, four-thread grouping, no jobs/retry."""
    p = resume_gate(plan, engineering)
    argv = [p['workflow_python'],'-I','-B','-m','snakemake','--snakefile',p['snakefile'],
            '--directory',p['work'],'--cores','8','--resources','mem_mb=26000',
            '--runtime-source-cache-path',str(Path(p['work']).parent/'workflow-source-cache'),
            '--benchmark-extended','--config','plan='+str(Path(plan).absolute()),
            'engineering='+str(engineering).lower(), '--rerun-triggers','mtime']
    if dry_run:
        argv.append('--dry-run')
    if until_pilot:
        argv+=['--until','pilot']
    subprocess.run(argv,check=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--plan',type=Path,required=True)
    parser.add_argument('--engineering',action='store_true')
    parser.add_argument('--stage')
    parser.add_argument('--sample',type=int)
    parser.add_argument('--workflow',action='store_true')
    parser.add_argument('--dry-run',action='store_true')
    parser.add_argument('--until-pilot',action='store_true')
    args = parser.parse_args()
    if args.workflow:
        workflow(args.plan,args.engineering,args.dry_run,args.until_pilot)
    elif args.stage:
        stage(args.plan,args.stage,args.sample,args.engineering)
    else:
        parser.error('Select workflow or one stage')
