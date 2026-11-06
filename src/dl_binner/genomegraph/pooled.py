"""Prospective pooled-before-support ledgers, separate from frozen E034 graphs.

Keep calibrated coordinates before the support/orientation/hub filter. Samples
remain independent libraries; deduplicate within sample, then apply one pooled
support policy. No read names, DNA, source labels or truth enter graph features.
"""
from collections import Counter
import json
import math
from pathlib import Path
import struct
import subprocess
import sys
import time

import numpy as np

from ..context.tokens import binding
from ..io import emit, id_digest, save_arrays, write_json
from . import links

LEDGER = np.dtype(links.OBS.descr+[('a_end','<u4'),('b_end','<u4')])


def screening(records,counters):
    """Count joint MAPQ/identity strata without admitting filtered templates.

    This descriptive table includes only two primary mapped, nonduplicate/QC-fail
    mates with distinct roles. Missing/invalid edit counters stay unknown here;
    the actual retained reader still refuses malformed *kept* alignments.
    """
    if len(records)!=2 or any(r.flag&0xF04 or not r.is_paired or r.reference_id<0 for r in records):return
    if {bool(r.is_read1)for r in records}!={False,True} or any(r.is_read1==r.is_read2 for r in records):return
    qs=[r.mapping_quality for r in records]
    q='unknown255'if 255 in qs else ('0'if min(qs)==0 else '1-9'if min(qs)<10 else '10-19'if min(qs)<20 else '20-59'if min(qs)<60 else '60+')
    values=[]
    for r in records:
        if not r.cigartuples or not r.has_tag('NM'):break
        nm=r.get_tag('NM');total=sum(n for op,n in r.cigartuples if op in (0,7,8));ins=sum(n for op,n in r.cigartuples if op==1);delete=sum(n for op,n in r.cigartuples if op==2)
        if type(nm)is not int or total<=0 or not 0<=nm-ins-delete<=total:break
        values.append((total-(nm-ins-delete))/(total+ins+delete))
    identity='unknown'if len(values)!=2 else ('<.90'if min(values)<.9 else '.90-.95'if min(values)<.95 else '.95-.97'if min(values)<.97 else '.97-.99'if min(values)<.99 else '.99-1')
    scope='same'if records[0].reference_id==records[1].reference_id else 'cross'
    counters['screen_'+scope+'_MAPQ_'+q+'_identity_'+identity]+=1

def unique(observations, insert_limit):
    """Retain all deduplicated calibrated starts before any pair support floor."""
    if observations.dtype != LEDGER or insert_limit < 1: raise ValueError('Malformed coordinate ledger')
    a = observations[observations['distance'] <= insert_limit]
    a = a[np.lexsort((a['b_end'],a['a_end'],a['b'], a['a'], a['orientation'], a['j'], a['i']))]
    keep = np.ones(len(a), bool)
    if len(a) > 1: keep[1:] = np.logical_or.reduce([a[k][1:] != a[k][:-1] for k in ['i','j','orientation','a','b']])
    positions=np.flatnonzero(keep); result=a[positions].copy()
    # Same coordinate/direction is one within-library molecule. Preserve the
    # conservative full span envelope when alignments with that start differ.
    for k in ['a_end','b_end']:
        if len(a):result[k]=np.maximum.reduceat(a[k],positions)
    return result


def extract(bam, ids, lengths, eligible, sample, output, threads=4, engineering=False):
    """Read one whole BAM through the pinned real collator and retain its ledger.

    Same MAPQ/identity/mate/insert rules as E034; only the support aggregation order
    changes. Successful ledgers retain endpoint starts/distance/orientation for
    localized later evaluation. Failed reads keep spool/logs and an exit receipt.
    """
    import pysam
    cfg = links.policy(); ids, lengths, eligible = links.axes(ids,lengths,eligible)
    if engineering:
        if len(ids) > 128: raise ValueError('Tiny BAM ledger scope exceeded')
        cfg['min_calibration'] = 2
    if pysam.__version__ != '0.23.3' or pysam.__samtools_version__ != '1.21': raise ValueError('Pinned BAM runtime required')
    bam = Path(bam); out = Path(output); out.mkdir(parents=True,exist_ok=False)
    if bam.is_symlink() or not bam.is_file() or threads < 2: raise ValueError('Regular BAM and collator budget required')
    source = binding(bam); counters = Counter(); histogram = np.zeros(cfg['max_insert']+1,np.int64); count = 0; start = time.monotonic()
    argv = [sys.executable,'-I','-B','-c','import pysam,sys;pysam.collate(*sys.argv[1:],catch_stdout=False)',
            '-u','-O','-@',str(threads-2),'-n','64',str(bam),str(out/'collate')]
    stderr = (out/'collate.stderr').open('xb'); process = subprocess.Popen(argv,stdout=subprocess.PIPE,stderr=stderr)
    raw = out/'coordinates.bin'
    try:
        with raw.open('xb') as spool, pysam.AlignmentFile(process.stdout,'rb',threads=1) as stream:
            mapping = links.dictionary(stream.header,ids,lengths); previous = None; records = []; overflow = False
            def consume():
                nonlocal count
                if overflow: counters['templates'] += 1; counters['excessive_template_records'] += 1; return
                screening(records,counters)
                result = links.pair(records,mapping,lengths,counters,cfg)
                if result is None: return
                left,right,i,j = result
                counters['qualified_read_length_'+str(len(left.query_sequence))]+=1
                counters['qualified_read_length_'+str(len(right.query_sequence))]+=1
                if i == j:
                    f,r = (left,right) if not left.is_reverse else (right,left)
                    span = max(left.reference_end,right.reference_end)-min(left.reference_start,right.reference_start)
                    if not f.is_reverse and r.is_reverse and f.reference_start <= r.reference_start and span <= cfg['max_insert']:
                        histogram[span] += 1
                        overlap=max(0,min(left.reference_end,right.reference_end)-max(left.reference_start,right.reference_start))
                        counters['calibration_reference_span_overlap_templates']+=int(overlap>0)
                        counters['calibration_reference_span_overlap_bp']+=overlap
                    return
                counters['cross_contig_qualified_templates'] += 1
                distance = (left.reference_end if left.is_reverse else int(lengths[i])-left.reference_start)+(right.reference_end if right.is_reverse else int(lengths[j])-right.reference_start)
                if distance > cfg['max_insert']: counters['cross_outside_max_insert_scope'] += 1; return
                if i > j: i,j,left,right = j,i,right,left
                spool.write(struct.pack('<8I',i,j,left.reference_start,right.reference_start,distance,int(left.is_reverse)*2+int(right.is_reverse),left.reference_end,right.reference_end))
                count += 1
                if count > cfg['maximum_observations']: raise ValueError('Bounded coordinate ledger exceeded')
            for r in stream:
                counters['alignment_records'] += 1; name = r.query_name
                if not name or len(name) > 254: raise ValueError('Invalid opaque template identity')
                if previous is not None and name != previous: consume(); records = []; overflow = False
                previous = name
                if len(records) < 64: records.append(r)
                else: overflow = True
                if counters['alignment_records'] % 2000000 == 0: emit('pooled_support_reader', sample=sample, **dict(counters))
            if previous is not None: consume()
        process.stdout.close(); code = process.wait(timeout=60)
        if code: raise RuntimeError('Whole-QNAME collator failed')
        if 1-(counters['template_record_count_not_two']+counters['excessive_template_records'])/max(counters['templates'],1) < cfg['min_two_record_fraction']:
            raise ValueError('Actual mate join failed')
        if histogram.sum() < cfg['min_calibration']: raise ValueError('Insert calibration missing')
        limit = int(np.searchsorted(np.cumsum(histogram),math.ceil((int(histogram.sum())-1)*cfg['insert_quantile'])+1))
        raw_array = np.memmap(raw,dtype=LEDGER,mode='r') if count else np.empty(0,LEDGER)
        kept = unique(raw_array,limit)
        if binding(bam) != source: raise ValueError('Original BAM changed')
        meta = dict(kind='pooled_support_ledger',version=1,sample=sample,policy=cfg,source=source,
            ids_sha256=id_digest(ids),counters=dict(counters),insert_limit=limit,histogram=histogram.tolist(),
            pre_support_observations=count,calibrated_unique_observations=len(kept),samtools_version=pysam.__samtools_version__,
            collator_exit=code,collator_argv=argv,wall_seconds=time.monotonic()-start,
            sample_scoped_coordinate_dedup=True,retained_loci='start/end reference span envelopes, not gap-free CIGAR base support; original calibrated distance is not recomputed from a potentially wider duplicate envelope',
            raw_read_names_retained=False,truth_accessed=False,engineering=engineering)
        save_arrays(out/'ledger.npz',dict(ids=np.asarray(ids),lengths=lengths,eligible=eligible,observations=kept),meta)
        write_json(out/'completed.json',dict(status='PASS',arrays=binding(out/'ledger.npz'),metadata=binding(out/'ledger.json')))
        del raw_array; raw.unlink(); return meta
    except BaseException as error:
        if process.poll() is None: process.terminate()
        try: process.wait(timeout=15)
        except subprocess.TimeoutExpired: process.kill(); process.wait()
        write_json(out/'failure.json',dict(error=repr(error),collator_exit=process.returncode,counters=dict(counters),source=source))
        raise
    finally:
        stderr.close()
        if process.stdout is not None: process.stdout.close()


def read(folder):
    """Refuse corrupt, foreign-coordinate or mismatched-sample support ledgers."""
    from ..multiview.arrays import load_arrays
    root = Path(folder); seal = json.loads((root/'completed.json').read_text())
    if seal != dict(status='PASS',arrays=binding(root/'ledger.npz'),metadata=binding(root/'ledger.json')):
        raise ValueError('Pooled support ledger bytes differ')
    a,m = load_arrays(root/'ledger.npz','pooled_support_ledger'); ids,lengths,eligible = links.axes(a['ids'].tolist(),a['lengths'],a['eligible'])
    links.policy(m['policy']); o = a['observations']
    if o.dtype != LEDGER or (o['i'] >= len(ids)).any() or (o['j'] >= len(ids)).any() or (o['i'] >= o['j']).any() or (o['orientation'] > 3).any():
        raise ValueError('Malformed pooled support coordinates')
    if len(o) and ((o['a'] >= lengths[o['i']]).any() or (o['b'] >= lengths[o['j']]).any()): raise ValueError('Pooled coordinates outside contigs')
    if len(o) and ((o['a_end']>lengths[o['i']]).any() or (o['b_end']>lengths[o['j']]).any() or (o['a_end']<=o['a']).any() or (o['b_end']<=o['b']).any()):raise ValueError('Pooled endpoint spans outside contigs')
    if not np.array_equal(unique(o,m['insert_limit']),o): raise ValueError('Ledger is not calibrated/sorted/deduplicated')
    if (len(o)!=m['calibrated_unique_observations'] or m['ids_sha256']!=id_digest(ids)
            or m['truth_accessed']is not False or not isinstance(m['sample'],str) or not m['sample']):
        raise ValueError('Pooled ledger counter/source schema differs')
    return a,m


def pool(folders, samples, output):
    """Apply the three-template floor after independent sample ledgers are pooled.

    Identical coordinates in different libraries are separate evidence, but two
    distinct physical starts are still required at both endpoints overall. Keep
    all sample counts and coordinates, including refused pairs, for later audit.
    """
    if len(folders) != len(samples) or not samples or len(set(samples)) != len(samples): raise ValueError('Explicit unique sample axis required')
    total=sum(json.loads((Path(folder)/'ledger.json').read_text())['calibrated_unique_observations']for folder in folders)
    if total>5_000_000:raise ValueError('Prospective pooled in-memory observation limit exceeded; resource refusal, not link utility')
    first, fm = read(folders[0]); cfg = fm['policy']; groups = {}; proof = []
    for at,(folder,sample) in enumerate(zip(folders,samples)):
        a,m = read(folder)
        if m['sample'] != sample or m['policy'] != cfg or any(not np.array_equal(a[k],first[k]) for k in ['ids','lengths','eligible']): raise ValueError('Pooled sample/policy/full axes differ')
        proof.append(dict(sample=sample,seal=binding(Path(folder)/'completed.json')))
        for o in a['observations']: groups.setdefault((int(o['i']),int(o['j'])),[]).append((at,int(o['a']),int(o['b']),int(o['orientation'])))
    edges=[]; supports=[]; directions=[]; trace=[]
    for pair, observations in sorted(groups.items()):
        x=np.asarray(observations,np.int64); votes=np.bincount(x[:,3],minlength=4); direction=int(votes.argmax()); keep=x[x[:,3]==direction]
        reason='supported'
        if len(keep)<cfg['min_support']: reason='below_pooled_unique_support'
        elif len(keep)/len(x)<cfg['orientation_fraction']: reason='pooled_orientation_conflict'
        elif min(len(np.unique(keep[:,1])),len(np.unique(keep[:,2])))<cfg['min_distinct_starts']: reason='pooled_distinct_starts'
        trace.append(dict(edge=list(pair),counts=np.bincount(keep[:,0],minlength=len(samples)).tolist(),orientation=direction,reason=reason,observations=len(x)))
        if reason=='supported': edges.append(pair); supports.append(trace[-1]['counts']); directions.append(direction)
    e=np.asarray(edges,np.int64).reshape(-1,2); counts=np.asarray(supports,np.int64).reshape(-1,len(samples)); direction=np.asarray(directions,np.uint8)
    degree=np.bincount(e.ravel(),minlength=len(first['ids'])); good=(degree[e]<=cfg['maximum_degree']).all(1)
    removed={tuple(map(int,pair))for pair in e[~good]};hub_nodes=int((degree>cfg['maximum_degree']).sum())
    for row in trace:
        if tuple(row['edge'])in removed:row['reason']='pooled_repeat_hub_guard'
    e,counts,direction=e[good],counts[good],direction[good]
    support=counts.sum(1);degree=np.bincount(e.ravel(),minlength=len(first['ids']));weights=np.log1p(support)/np.sqrt(np.maximum(degree[e[:,0]],1)*np.maximum(degree[e[:,1]],1))
    out=Path(output);out.mkdir(parents=True,exist_ok=False)
    arrays={k:first[k] for k in ['ids','lengths','eligible']};arrays.update(edges=e,support=support,orientations=direction,weights=weights,sample_support=counts)
    write_json(out/'decisions.json',trace)
    meta=dict(kind='physical_template_graph',version=1,sample='pooled',samples=samples,policy=cfg,threshold_order='pool_before_support',sources=proof,
              pair_filter_order='sample calibration/dedup first; pooled support/orientation/distinct-start/hub decisions',
              ids_sha256=id_digest(first['ids'].tolist()),rows=len(first['ids']),bp=int(first['lengths'].sum()),decisions=binding(out/'decisions.json'),
              calibrated_unique_observations=total,candidate_contig_pairs=len(groups),decision_counts=dict(Counter(row['reason']for row in trace)),hub_nodes=hub_nodes,hub_edges_removed=len(removed),
              utility=links.utility(e,first['ids'],first['lengths'],first['eligible']),truth_accessed=False,
              assembly_scope='all-ten pooled under frozen mapping filters; not all future libraries')
    save_arrays(out/'graph.npz',arrays,meta)
    write_json(out/'completed.json',dict(status='PASS',graph=binding(out/'graph.npz'),receipt=binding(out/'graph.json')))
    return meta
