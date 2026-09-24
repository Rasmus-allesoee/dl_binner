"""Audit a compact E001 preprocessing return without extracting or reading BAMs.

Inputs are the return tar, its SHA256 sidecar and terminal log. Output is an
acceptance record and byte-identical ordered BAM manifest in a new directory.
This verifies returned QC/command consistency, not a new local BAM inspection.
"""
import argparse
import hashlib
import json
from pathlib import Path
import sys
import tarfile

sys.path.insert(0, str(Path(__file__).resolve().parent))
from e001_vamb_cpu import require, sha

EXPERIMENT = Path(__file__).resolve().parents[1] / 'experiments/E001-coverage-thinning'


def review(archive, checksum, terminal):
    """Return verified raw manifest bytes and the compact, source-bound assessment."""
    digest = sha(archive)
    require(checksum.read_text().split() == [digest, archive.name], 'Archive checksum mismatch')
    with tarfile.open(archive) as tar:
        members = [m for m in tar.getmembers() if m.isfile()]
        require(len({m.name for m in members}) == len(members), 'Duplicate archive members')
        prefix = archive.name.removesuffix('-return.tar.gz') + '/'
        data = {m.name.removeprefix(prefix): tar.extractfile(m).read() for m in members}
    def read(name):
        return json.loads(data[name])
    status, runtime, manifest = [read(n) for n in ('status.json', 'runtime.json', 'bam-manifest.json')]
    frozen = json.loads((EXPERIMENT / 'frozen-inputs.json').read_text())
    sample0 = json.loads((EXPERIMENT / 'sample0-preprocess-observed.json').read_text())
    sources = {s['sample']: s for s in json.loads((EXPERIMENT / 'acquisition.json').read_text())['read_archives_not_authorized_by_inventory']}
    require(status['exit_code'] == 0 and not status['startup_only'], 'Incomplete preprocessing')
    require([s['sample'] for s in manifest['samples']] == frozen['samples'], 'Wrong sample order')
    require(manifest['reference_sha256'] == frozen['outputs']['canonical.fna'] == runtime['reference_sha256'], 'Wrong reference')
    require(manifest['source_commit'] == runtime['source_commit'], 'Source mismatch')
    require(manifest['samples'][0]['summary'] == sample0['records']['preprocessing-summary.json'], 'Sample 0 differs')
    require(abs(status['allocated_core_hours'] - status['elapsed_seconds'] * status['actual_vcpus'] / 3600) < 1e-9, 'Cost mismatch')
    evidence = {}
    for index, entry in enumerate(manifest['samples']):
        s = entry['sample']; summary = entry['summary']
        require(summary['sample'] == s and summary['thinning_seed'] == 1000 + index and summary['thinning_fraction'] == .1, 'Seed/sample/fraction mismatch')
        require(0 < summary['CT']['records'] < summary['C0']['records'], 'Invalid counts')
        require(abs(summary['observed_record_fraction'] - summary['CT']['records'] / summary['C0']['records']) < 1e-12, 'Fraction mismatch')
        if s == 0:
            continue
        p = f'sample_{s}/'
        require(read(p+'preprocessing-summary.json') == summary, 'Summary mismatch')
        require(read(p+'reads.json') == entry['reads'], 'Reads mismatch')
        acquisition = read(p+'acquisition.json')
        require(acquisition['publisher_md5_verified'] and acquisition['md5'] == sources[s]['md5'], 'Publisher checksum mismatch')
        require(acquisition['sha256'] == entry['reads']['archive_sha256'], 'Archive/read provenance mismatch')
        require(summary['C0']['records'] <= 2 * entry['reads']['pairs'], 'Read count mismatch')
        pipeline = read(p+'C0/pipeline/pipeline.json')
        require(pipeline['returncodes'] == [0,0,0], 'Mapping failure')
        mapper, filt, sort = pipeline['commands']
        require(mapper[mapper.index('-t')+1] == '2' and manifest['reference'] in mapper and '--interleaved' in mapper, 'Unexpected mapping settings')
        require(filt == ['samtools','view','-u','-F','2308','-'], 'Changed filtering')
        require(sort[sort.index('-@')+1] == '0', 'Changed sort threads')
        thin = read(p+'CT/thin.command.json')
        argv = thin['argv']
        require(thin['returncode'] == 0 and argv[argv.index('--subsample-seed')+1] == str(1000+index) and argv[argv.index('--subsample')+1] == '0.1', 'Thinning mismatch')
        require(argv[-1] == entry['directory'] + '/C0/mapped.bam', 'Thinning input mismatch')
        for condition in ('C0','CT'):
            require(read(p+condition+'/qc.json') == summary[condition], 'QC mismatch')
            require(read(p+condition+'/index.command.json')['returncode'] == 0, 'Index failed')
            require(summary[condition]['bytes'] > 0 and len(summary[condition]['sha256']) == 64, 'Missing BAM receipt')
        for stage in (('extract','map','thin') if s in {r['sample'] for r in status['reused_archives']} else ('download','extract','map','thin')):
            require(p+f'benchmarks/{stage}.tsv' in data, 'Missing rule benchmark')
        evidence[str(s)] = {'acquisition': acquisition, 'mapping': pipeline, 'thinning': thin}
    for name in ('workflow', 'dag', 'snakemake-startup', 'workflow-prefix', 'workflow-stage', 'workflow-lock', 'mapping-environment', 'samtools-version', 'strobealign-version'):
        require(read(name+'.command.json')['returncode'] == 0, 'Failed '+name)
    log = terminal.read_text()
    require('35 of 35 steps (100%) done' in log and 'PASS: workflow' in log, 'No terminal completion')
    result = {'status':'accepted', 'reviewed':'2026-09-24', 'archive':archive.name, 'archive_sha256':digest,
              'terminal_log_sha256':sha(terminal), 'manifest_sha256':hashlib.sha256(data['bam-manifest.json']).hexdigest(),
              'scope':'Ten ordered samples, C0 and CT replicate 0. Returned QC accepted; no BAM upload, remapping, fitting or scores.',
              'run_status':status, 'runtime':runtime, 'per_sample_commands':evidence,
              'all_bam_bytes':sum(e['summary'][c]['bytes'] for e in manifest['samples'] for c in ('C0','CT')),
              'retention_note':'attempt_bytes is logical retained size including hardlinked reused archives; excludes earlier attempts, sample 0, environments and outside-driver idle time. Not incremental physical storage or total job billing.',
              'member_sha256':{n:hashlib.sha256(b).hexdigest() for n,b in sorted(data.items())}}
    return data['bam-manifest.json'], result


if __name__ == '__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('archive',type=Path);p.add_argument('checksum',type=Path);p.add_argument('terminal',type=Path);p.add_argument('--out',type=Path,required=True)
    a=p.parse_args(); manifest,record=review(a.archive,a.checksum,a.terminal)
    a.out.mkdir(parents=True,exist_ok=False)
    (a.out/'bam-manifest.json').write_bytes(manifest)
    (a.out/'multisample-preprocess-observed.json').write_text(json.dumps(record,indent=2)+'\n')
    print('PASS: checksum, all sample receipts/commands, reference, ordered manifest, terminal completion')
