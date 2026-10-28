#!/usr/bin/env python3
"""Audit retained E024 data after a failed grouping gate, without running science.

Inputs are a member-verified return, its inventory, current BAM object metadata
and retained original features. Stream all ten coverage summaries against the
matrix and rebound array. Do not open truth, rebuild neighbors or contact cloud.
Write a fresh compact data-admission record; omitted raw/index bytes are not
independently reread by this consumer.
"""
import argparse
from contextlib import ExitStack
import hashlib
import json
from pathlib import Path
import re
import time

SAMPLES = [6, 7, 8, 13, 14, 15, 16, 17, 18, 19]


def require(ok, message):
    """Refuse incomplete or contradictory evidence with a concrete cause."""
    if not ok:
        raise ValueError(message)


def binding(path):
    """Hash a regular local input incrementally, including on retained Python 3.10."""
    path = Path(path)
    sha = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1024**2), b''):
            sha.update(chunk)
    return dict(bytes=path.stat().st_size, sha256=sha.hexdigest())


def acquired_contract(record, expected):
    """Check recorded full-object identities and the exact publisher segment plan.

    This verifies the retained native checksum receipts, not deleted FASTQ bytes.
    Swift's aggregate digest remains distinct from the calculated whole-file MD5.
    """
    require(record['manifest'] == expected and record['sample'] == expected['sample']
            and record['bytes'] == expected['bytes']
            and record['publisher_segment_MD5_passed'] == len(expected['segments'])
            and re.fullmatch('[0-9a-f]{64}', record['sha256'])
            and re.fullmatch('[0-9a-f]{32}', record['calculated_whole_MD5']),
            'Acquisition receipt differs from frozen publisher plan')
    segments = expected['segments']
    require(sum(s['bytes'] for s in segments) == expected['bytes']
            and hashlib.md5(''.join(s['md5'] for s in segments).encode()).hexdigest()
            == expected['DLO_aggregate_md5'], 'Publisher DLO segment accounting differs')


class Retained:
    """Resolve exact-byte aliases through a verified inventory, without copying."""
    def __init__(self, root, inventory):
        self.root, self.inventory = Path(root), inventory

    def path(self, key):
        alias = self.inventory['aliases'].get(key)
        if alias:
            wanted = {k: alias[k] for k in ['bytes', 'sha256']}
            require(self.inventory['members'].get(alias['canonical']) == wanted,
                    'Alias content binding differs')
            key = alias['canonical']
        require(key in self.inventory['members'], 'Missing retained member: ' + key)
        require(not Path(key).is_absolute() and '..' not in Path(key).parts,
                'Unsafe inventory member')
        return self.root/key

    def read(self, key):
        return json.loads(self.path(key).read_text())

    def seal(self, folder):
        """Check every sealed output binding against archived/explicit omitted bytes."""
        receipt = self.read('work/'+folder+'/done.json')
        require(receipt['status'] == 'PASS', 'Stage not accepted: ' + folder)
        for name, expected in receipt['files'].items():
            key = folder+'/'+name
            require(self.inventory['all_work_members'].get(key) == expected,
                    'Sealed output binding differs: ' + key)
        return receipt


def inspect(root, original_features, bam_metadata, output):
    """Audit all recorded stages and read every coverage cell without any scoring."""
    import numpy as np
    started = time.monotonic()
    root = Path(root)
    inv = json.loads((root/'inventory.json').read_text())
    retained = Retained(root/'verified', inv)
    plan = retained.read('evidence/plan.json')
    config = retained.read('evidence/config.json')
    source = retained.read('evidence/source/experiments/E024-oral-measured-coverage/source-lock.json') if 'evidence/source/experiments/E024-oral-measured-coverage/source-lock.json' in inv['members'] else None
    require(config['source_commit'] == '2e34d648a7db6e84aa0720a23453ad30124571d5',
            'Executed scientific source differs')
    manifest = retained.read('evidence/source/experiments/E024-oral-measured-coverage/read-manifest.json')
    for folder in ['verified', 'first-acquired', 'index', 'pilot', 'combined']:
        retained.seal(folder)
    metadata = json.loads(Path(bam_metadata).read_text())
    samples = []
    for s, expected in zip(SAMPLES, manifest['reads']):
        acquired = retained.read(f'work/samples/{s}/acquisition.json')
        acquired_contract(acquired, expected)
        done = retained.seal(f'samples/{s}')
        mapped = retained.read(f'work/samples/{s}/mapped/done.json')
        bam = retained.read(f'work/samples/{s}/mapped/alignment-retained.json')
        require(mapped['mapper_exit'] == 0 and mapped['retained_alignment'] == bam
                and bam['status'] == 'PASS' and bam['full_readback_verified']
                and bam['native_encoder_exit'] == bam['native_decoder_exit'] == 0
                and bam['sorted'] is False and bam['indexed'] is False
                and int(metadata[bam['uri']]['size']) == bam['bytes'],
                'Native BAM producer/readback/decode/current-size contract differs')
        feeder, counters = mapped['feeder'], mapped['counters']
        require(feeder['reads'] == 2*feeder['pairs'] == counters['primary_reads']
                == counters['SAM_records'] == bam['native_full_decode_records']
                and feeder['primary_identity_sum'] == counters['primary_identity_sum']
                and mapped['reference'] == rebound_reference(retained)
                and mapped['reads'] == dict(bytes=acquired['bytes'], sha256=acquired['sha256'])
                and done['removed']['identity'] == mapped['reads'], 'Read identity/raw release differs')
        samples.append(dict(sample=s, read_bytes=acquired['bytes'], read_sha256=acquired['sha256'],
                            whole_MD5=acquired['calculated_whole_MD5'], segment_MD5s=[x['md5'] for x in expected['segments']],
                            download_seconds=acquired['elapsed_seconds'], mapping_seconds=done['mapping_seconds'],
                            bam=bam, object_generation=metadata[bam['uri']].get('generation'),
                            mapped=mapped))
    rebound = retained.read('work/rebound/rebind.json')
    require(rebound['status'] == 'PASS' and rebound['rows'] == 1286547,
            'Native depth rebind not accepted')
    old = Path(original_features)
    require(binding(old) == rebound['files']['original_features'], 'Retained original feature bytes differ')
    with np.load(old, allow_pickle=False) as before, np.load(retained.path('work/rebound/features.npz'), allow_pickle=False) as after:
        for key in rebound['invariant_arrays']:
            require(np.array_equal(before[key], after[key]), 'Depth rebind changed '+key)
        ids, lengths, depth, eligible = after['ids'], after['lengths'], after['depth'], after['eligible']
        require(depth.shape == (len(ids),10) and np.isfinite(depth).all() and (depth >= 0).all(),
                'Rebound coverage array malformed')
        require(np.array_equal(after['zero_depth'],depth == 0)
                and np.array_equal(after['depth_evidence'],(depth > 0).any(1)), 'Depth masks differ')
    totals, zero_rows = [0]*10, [0]*10
    with ExitStack() as stack:
        matrix = stack.enter_context(retained.path('work/combined/depth.tsv').open())
        tables = [stack.enter_context(retained.path(f'work/samples/{s}/mapped/depth.tsv').open()) for s in SAMPLES]
        require(matrix.readline().rstrip('\n').split('\t') == ['contig_id']+[f'oral_sample_{s}' for s in SAMPLES], 'Sample columns reordered')
        require(all(f.readline().strip() == 'contig_id\taligned_read_bases\tlength\tmean' for f in tables), 'Summary schema differs')
        for i, ident in enumerate(ids):
            row = matrix.readline().rstrip('\n').split('\t')
            require(len(row) == 11 and row[0] == ident, 'Matrix contig axis differs')
            for j, table in enumerate(tables):
                fields = table.readline().rstrip('\n').split('\t')
                require(len(fields) == 4 and fields[0] == ident and int(fields[2]) == lengths[i], 'Sample contig axis differs')
                bases, mean = int(fields[1]), float(fields[3])
                require(bases >= 0 and mean == bases/int(lengths[i]) == float(row[j+1])
                        and np.float32(mean) == depth[i,j], 'Aligned-base/mean/matrix/rebound cell differs')
                totals[j] += bases
                zero_rows[j] += bases == 0
            if i % 250000 == 0:
                print('E024_DATA_AUDIT_ROWS',i,flush=True)
        require(not matrix.read(1) and all(not f.read(1) for f in tables), 'Extra coverage rows')
    for j, s in enumerate(samples):
        require(s['mapped']['counters']['aligned_read_bases'] == totals[j]
                and s['mapped']['zero_rows'] == zero_rows[j], 'Whole-sample counters differ')
    zero = (depth == 0).all(1)
    require(int(zero.sum()) == rebound['all_zero_rows'], 'Measured zero population differs')
    result = dict(status='PASS_DATA_ONLY_GROUPING_FAILED',scientific_source=config['source_commit'],
                  rows=len(ids),bp=int(lengths.sum()),ordered_samples=SAMPLES,samples=samples,
                  publisher_segments_verified_in_native_receipts=50,whole_compressed_read_bytes=sum(x['read_bytes'] for x in samples),
                  full_matrix_cells_independently_read=int(depth.size),missing_cells=0,
                  all_zero_rows=int(zero.sum()),all_zero_bp=int(lengths[zero].sum()),
                  eligible_rows=int(eligible.sum()),eligible_positive_depth_rows=int((eligible & ~zero).sum()),
                  zero_cells_per_sample=zero_rows,native_rebind_invariants_independently_equal=True,
                  group_completed=False,export_completed=False,final_audit_completed=False,
                  quality_evaluation_admitted=False,truth_opened=False,
                  BAMs_not_downloaded_or_redecoded_locally=True,
                  raw_reads_deleted_verified_by_native_receipts_not_reread=True,
                  no_after_failure_whole_input_mutation_proof=True,
                  source_lock_in_archive=source is not None,wall_seconds=time.monotonic()-started)
    Path(output).write_text(json.dumps(result,indent=2)+'\n')
    return result


def rebound_reference(retained):
    """Use the combined writer's bound reference; never infer it from a directory."""
    return retained.read('work/combined/depth.tsv.receipt.json')['reference']


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    for name in ['root','original-features','bam-metadata','output']:
        p.add_argument('--'+name,type=Path,required=True)
    args = p.parse_args()
    require(not args.output.exists(), 'Fresh inspection result required')
    inspect(args.root,args.original_features,args.bam_metadata,args.output)
