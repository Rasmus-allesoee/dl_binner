"""Independently verify both mates and retain a sparse physical-template graph.

A pinned external collator bounds the QNAME join. Only coordinate observations
are spooled; names/read DNA never become features. Biological thresholds are
explicit; malformed retained alignments fail rather than becoming zero support.
"""
from collections import Counter
import json
import math
from pathlib import Path
import struct
import sys
import subprocess
import time

import numpy as np

from ..context.tokens import binding
from ..io import emit, id_digest, load_arrays, save_arrays, write_json
from ..multiscale.measurement import aligned_blocks

DEFAULT = dict(version=1, min_mapq=20, min_identity=.97, min_query_fraction=.90,
    min_calibration=1000, insert_quantile=.995, min_two_record_fraction=.95,
    max_insert=2000, min_support=3, min_distinct_starts=2,
    orientation_fraction=.90, maximum_degree=64, maximum_observations=20000000,
    identity='(M+EQ+X-(NM-I-D))/(M+EQ+X+I+D)', calibration='all_qualified_inward_FR_histogram',
    collator='pysam_0233_samtools_121_full_collate', qnames='opaque_per_sample_only')
OBS = np.dtype([('i','<u4'),('j','<u4'),('a','<u4'),('b','<u4'),('distance','<u4'),('orientation','<u4')])


def policy(value=None):
    """Validate explicit product settings; the experiment freezes one exact value."""
    value=dict(DEFAULT if value is None else value)
    if set(value)!=set(DEFAULT) or any(type(value[k]) is not type(v) for k,v in DEFAULT.items()):
        raise ValueError('Unknown/malformed physical-link policy')
    if any(value[k]!=DEFAULT[k] for k in ['version','min_identity','identity','calibration','collator','qnames']):
        raise ValueError('Unsupported physical identity/join semantics')
    if not (0<=value['min_two_record_fraction']<=1 and 0<=value['min_mapq']<255 and 0<value['min_query_fraction']<=1 and
        1<=value['min_calibration'] and 0<value['insert_quantile']<1 and
        value['max_insert']>0 and value['min_support']>=2 and value['min_distinct_starts']>=2 and
        .5<value['orientation_fraction']<=1 and value['maximum_degree']>=2 and value['maximum_observations']>0):
        raise ValueError('Invalid physical-link bounds')
    return value


def axes(ids,lengths,eligible):
    """Validate full FASTA axes, including excluded and original zero-bp records."""
    ids=list(ids);lengths=np.asarray(lengths);eligible=np.asarray(eligible)
    if (not ids or len(ids)!=len(set(ids)) or any(not isinstance(s,str) or not s for s in ids)
        or lengths.shape!=(len(ids),) or lengths.dtype.kind not in 'iu' or (lengths<0).any()
        or eligible.shape!=(len(ids),) or eligible.dtype!=bool or len(ids)>=2**32 or (lengths>=2**32).any()):
        raise ValueError('Malformed full contig/length/eligibility axes')
    return ids,lengths,eligible


def dictionary(header,ids,lengths):
    """Map arbitrary BAM dictionary order to the exact complete opaque FASTA axis."""
    sq=header.to_dict().get('SQ',[]);names=[x['SN'] for x in sq]
    lookup={s:i for i,s in enumerate(ids)}
    if len(names)!=len(set(names)) or set(names)!=set(ids):
        raise ValueError('BAM dictionary has missing/extra/duplicate contigs')
    if any(type(x['LN']) is not int or x['LN']!=int(lengths[lookup[x['SN']]]) for x in sq):
        raise ValueError('BAM dictionary lengths differ from full FASTA')
    return np.array([lookup[n] for n in names],np.int64)


def pair(records,mapping,lengths,counters,cfg):
    """Return two independently admitted mates; count one reason per refused group."""
    counters['templates']+=1
    if len(records)!=2:
        counters['template_record_count_not_two']+=1;return None
    if any(r.is_secondary or r.is_supplementary or r.has_tag('SA') for r in records):
        counters['alternative_or_chimeric_template']+=1;return None
    by_role={}
    for r in records:
        if not r.is_paired or r.is_read1==r.is_read2:
            counters['invalid_or_missing_mate_role']+=1;return None
        role=1 if r.is_read1 else 2
        if role in by_role:counters['duplicate_mate_role']+=1;return None
        by_role[role]=r
    if set(by_role)!={1,2}:raise ValueError('Internal actual-mate accounting differs')
    left,right=by_role[1],by_role[2]
    if any(r.flag&0xF04 for r in (left,right)):
        counters['template_flag_exclusion']+=1;return None
    if any(r.mapping_quality==255 or r.mapping_quality<cfg['min_mapq'] for r in (left,right)):
        counters['low_or_unknown_template_MAPQ']+=1;return None
    admitted=[]
    for r in (left,right):
        if not 0<=r.reference_id<len(mapping):raise ValueError('Mapped mate reference index escapes dictionary')
        i=int(mapping[r.reference_id]);blocks=aligned_blocks(r,int(lengths[i]),counters)
        if not blocks:
            counters['template_identity_exclusion']+=1;return None
        if any(op==5 for op,_ in r.cigartuples) or r.query_alignment_length/len(r.query_sequence)<cfg['min_query_fraction']:
            counters['partial_template_alignment']+=1;return None
        admitted.append(i)
    if any(r.mate_is_unmapped or r.next_reference_id!=other.reference_id or r.next_reference_start!=other.reference_start
        or r.mate_is_reverse!=other.is_reverse for r,other in [(left,right),(right,left)]):
        counters['inconsistent_actual_mate_metadata']+=1;return None
    counters['qualified_both_mates']+=1
    return left,right,*admitted


def aggregate(observations,insert_limit,lengths,eligible,cfg):
    """Deduplicate physical coordinates, require oriented support and suppress hubs."""
    count=len(observations)
    if not count:return np.empty((0,2),np.int64),np.empty(0,np.int64),np.empty(0,np.uint8),dict(observations=0)
    kept=observations[observations['distance']<=insert_limit]
    order=np.lexsort((kept['b'],kept['a'],kept['orientation'],kept['j'],kept['i']))
    kept=kept[order]
    different=np.ones(len(kept),bool)
    if len(kept)>1:
        different[1:]=np.logical_or.reduce([kept[n][1:]!=kept[n][:-1] for n in ['i','j','orientation','a','b']])
    unique=kept[different];edges=[];support=[];directions=[];rejected=Counter()
    if len(unique):
        starts=np.r_[0,np.flatnonzero((unique['i'][1:]!=unique['i'][:-1])|(unique['j'][1:]!=unique['j'][:-1]))+1,len(unique)]
        for lo,hi in zip(starts[:-1],starts[1:]):
            group=unique[lo:hi];bins=np.bincount(group['orientation'].astype(int),minlength=4)
            sig=int(np.argmax(bins));chosen=group[group['orientation']==sig]
            if len(chosen)<cfg['min_support']:rejected['below_unique_support']+=1;continue
            if len(chosen)/len(group)<cfg['orientation_fraction']:rejected['orientation_conflict']+=1;continue
            if min(len(np.unique(chosen['a'])),len(np.unique(chosen['b'])))<cfg['min_distinct_starts']:
                rejected['insufficient_distinct_starts']+=1;continue
            edges.append((int(group['i'][0]),int(group['j'][0])));support.append(len(chosen));directions.append(sig)
    e=np.array(edges,np.int64).reshape(-1,2);support=np.asarray(support,np.int64);directions=np.asarray(directions,np.uint8)
    degree=np.bincount(e.ravel(),minlength=len(lengths));hub=degree>cfg['maximum_degree']
    good=~hub[e].any(1);removed=int((~good).sum());e,support,directions=e[good],support[good],directions[good]
    return e,support,directions,dict(observations=count,end_supported_observations=len(kept),unique_coordinate_observations=len(unique),
        duplicate_coordinate_observations=len(kept)-len(unique),edge_exclusions=dict(rejected),hub_nodes=int(hub.sum()),hub_edges_removed=removed)


def utility(edges,ids,lengths,eligible,pilot=False):
    """Apply a prospective assembly-specific practical support floor without truth."""
    e=edges[eligible[edges].all(1)];linked=np.zeros(len(ids),bool);linked[e.ravel()]=True
    bp=int(lengths[linked].sum());den=int(lengths[eligible].sum());fraction=bp/den if den else 0.
    minimum_edges=20 if pilot else 100;minimum_fraction=.001 if pilot else .01
    return dict(status='PASS' if len(e)>=minimum_edges and fraction>=minimum_fraction else 'INSUFFICIENT_ASSEMBLY_LINK_SUPPORT',
        scope='This assembly/library/mapping and frozen filters only; not general paired-link usefulness',
        eligible_edges=len(e),linked_eligible_contigs=int(linked.sum()),linked_eligible_bp=bp,eligible_bp=den,
        linked_eligible_bp_fraction=fraction,minimum_edges=minimum_edges,minimum_bp_fraction=minimum_fraction,pilot=pilot)


def extract(bam,ids,lengths,eligible,sample,output,threads=4,cfg=None):
    """Collate one verified regular BAM, audit both mates and seal its exact graph.

    Owns a fresh output/scratch directory and captures collator stderr/exit. Failed
    attempts remain unsealed. Complete source/samtools hashes and every counter
    are retained. No cloud, mapping, read-name parsing or truth interface exists.
    """
    import pysam
    cfg=policy(cfg);ids,lengths,eligible=axes(ids,lengths,eligible)
    if pysam.__version__!='0.23.3':raise ValueError('Pinned pysam 0.23.3 required')
    bam,output=map(Path,[bam,output]);output.mkdir(parents=True,exist_ok=False)
    if bam.is_symlink() or not bam.is_file():raise ValueError('Regular BAM required')
    if type(threads) is not int or threads<2 or not isinstance(sample,str) or not sample:raise ValueError('Invalid sample/thread budget')
    started=time.monotonic();source=binding(bam);binary=binding(Path(pysam.libcsamtools.__file__).resolve());counts=Counter();calibration=np.zeros(cfg['max_insert']+1,np.int64);spooled=0;buffer=bytearray()
    version=pysam.__samtools_version__
    if version!='1.21':raise ValueError('Pinned bundled samtools 1.21 required')
    program='import pysam,sys; pysam.collate(*sys.argv[1:],catch_stdout=False)'
    command=[sys.executable,'-I','-B','-c',program,'-u','-O','-@',str(threads-2),'-n','64',str(bam),str(output/'collate')]
    stderr=(output/'collate.stderr').open('wb');process=subprocess.Popen(command,stdout=subprocess.PIPE,stderr=stderr)
    raw=output/'observations.bin'
    try:
        with pysam.AlignmentFile(process.stdout,'rb',threads=1) as stream,raw.open('xb') as observations:
            mapping=dictionary(stream.header,ids,lengths)
            group=[];previous=None;overflow=False
            def consume(records,overflowed):
                nonlocal spooled
                if overflowed:counts['templates']+=1;counts['excessive_template_records']+=1;return
                result=pair(records,mapping,lengths,counts,cfg)
                if result is None:return
                left,right,i,j=result
                if i==j:
                    forward,reverse=(left,right) if not left.is_reverse else (right,left)
                    span=max(left.reference_end,right.reference_end)-min(left.reference_start,right.reference_start)
                    if not forward.is_reverse and reverse.is_reverse and forward.reference_start<=reverse.reference_start and span<=cfg['max_insert']:
                        counts['calibration_eligible_templates']+=1
                        calibration[span]+=1
                    return
                counts['cross_contig_qualified_templates']+=1
                d1=left.reference_end if left.is_reverse else int(lengths[i])-left.reference_start
                d2=right.reference_end if right.is_reverse else int(lengths[j])-right.reference_start
                if d1+d2>cfg['max_insert']:counts['cross_outside_max_insert_scope']+=1;return
                if i>j:i,j,left,right=j,i,right,left
                signature=int(left.is_reverse)*2+int(right.is_reverse)
                buffer.extend(struct.pack('<6I',i,j,left.reference_start,right.reference_start,d1+d2,signature));spooled+=1
                if spooled>cfg['maximum_observations']:raise ValueError('Physical observations exceed prospective bounded spool')
                if len(buffer)>=1024**2:observations.write(buffer);buffer.clear()
            for r in stream:
                counts['alignment_records']+=1
                name=r.query_name
                if name is None or not name or len(name)>254:raise ValueError('Invalid opaque template identity')
                if previous is not None and name!=previous:
                    consume(group,overflow);group=[];overflow=False
                previous=name
                if len(group)<64:group.append(r)
                else:overflow=True
                if counts['alignment_records']%2000000==0:emit('physical_links_progress',sample=sample,alignment_records=counts['alignment_records'],templates=counts['templates'],cross_observations=spooled)
            if previous is not None:consume(group,overflow)
            if buffer:observations.write(buffer)
        process.stdout.close();code=process.wait(timeout=60)
        if code:raise RuntimeError('Pinned collator failed; inspect retained stderr')
        two_fraction=1-(counts['template_record_count_not_two']+counts['excessive_template_records'])/max(counts['templates'],1)
        if two_fraction<cfg['min_two_record_fraction']:raise ValueError('Actual QNAME/mate join contract failed; not an assembly link-utility result')
        if binding(bam)!=source:raise ValueError('Source BAM changed during physical-template reader')
        calibration_count=int(calibration.sum())
        if calibration_count<cfg['min_calibration']:raise ValueError('Too few qualified same-contig insert calibration pairs')
        def quantile(q):return int(np.searchsorted(np.cumsum(calibration),math.ceil((calibration_count-1)*q)+1))
        insert_limit=quantile(cfg['insert_quantile'])
        a=np.memmap(raw,dtype=OBS,mode='r') if spooled else np.empty(0,OBS)
        edges,support,orient,audit=aggregate(a,insert_limit,lengths,eligible,cfg)
        degree=np.bincount(edges.ravel(),minlength=len(ids))
        weights=np.log1p(support)/np.sqrt(np.maximum(degree[edges[:,0]],1)*np.maximum(degree[edges[:,1]],1))
        meta=dict(kind='physical_template_graph',version=1,sample=sample,policy=cfg,source=source,samtools=binary,samtools_version=version,
            collator_command=command,collator_exit=code,pipeline_workers=threads,ids_sha256=id_digest(ids),rows=len(ids),bp=int(lengths.sum()),
            counters=dict(counts),calibration=dict(observations=calibration_count,total_eligible=counts['calibration_eligible_templates'],
                insert_limit=insert_limit,minimum=int(np.flatnonzero(calibration)[0]),median=quantile(.5),maximum=int(np.flatnonzero(calibration)[-1]),histogram=calibration.tolist(),order_independent=True),
            aggregation=audit,utility=utility(edges,ids,lengths,eligible,True),wall_seconds=time.monotonic()-started,
            truth_accessed=False,read_names_or_DNA_retained=False)
        save_arrays(output/'graph.npz',dict(ids=np.array(ids),lengths=lengths,eligible=eligible,edges=edges,support=support,orientations=orient,weights=weights),meta)
        write_json(output/'completed.json',dict(status='PASS',graph=binding(output/'graph.npz'),receipt=binding(output/'graph.json')))
        del a;raw.unlink();return meta
    except BaseException as error:
        if process.poll() is None:process.terminate()
        try:process.wait(timeout=15)
        except subprocess.TimeoutExpired:process.kill();process.wait()
        write_json(output/'failure.json',dict(error=repr(error),collator_exit=process.returncode,counters=dict(counts),source=source,policy=cfg))
        raise
    finally:
        stderr.close()
        if process.stdout is not None:process.stdout.close()


def read(path):
    """Refuse partial/corrupt caches and validate all edge/population coordinates."""
    path=Path(path);done=json.loads((path/'completed.json').read_text())
    if done!=dict(status='PASS',graph=binding(path/'graph.npz'),receipt=binding(path/'graph.json')):raise ValueError('Physical graph seal differs')
    a,m=load_arrays(path/'graph.npz','physical_template_graph');policy(m['policy']);ids,lengths,eligible=axes(a['ids'].tolist(),a['lengths'],a['eligible'])
    e=a['edges']
    if e.ndim!=2 or e.shape[1]!=2 or e.dtype.kind not in 'iu' or (e<0).any() or (e>=len(ids)).any() or (e[:,0]>=e[:,1]).any():raise ValueError('Malformed physical edge axis')
    if (len({tuple(v) for v in e})!=len(e) or a['support'].shape!=(len(e),) or a['support'].dtype.kind not in 'iu'
        or (a['support']<m['policy']['min_support']).any() or a['weights'].shape!=(len(e),) or not np.isfinite(a['weights']).all()
        or (a['weights']<=0).any() or a['orientations'].shape!=(len(e),) or (a['orientations']>3).any()):
        raise ValueError('Malformed physical edge support/weights')
    degree=np.bincount(e.ravel(),minlength=len(ids));expected=np.log1p(a['support'])/np.sqrt(np.maximum(degree[e[:,0]],1)*np.maximum(degree[e[:,1]],1))
    if not np.allclose(a['weights'],expected,rtol=1e-12,atol=0):raise ValueError('Physical weight expression differs')
    if 'sample_support' in a:
        support=a['sample_support']
        if support.shape!=(len(e),len(m['samples'])) or support.dtype.kind not in 'iu' or (support<0).any() or not np.array_equal(support.sum(1),a['support']):raise ValueError('Pooled sample support differs')
    if id_digest(ids)!=m['ids_sha256'] or len(ids)!=m['rows'] or int(lengths.sum())!=m['bp'] or m['truth_accessed'] is not False:
        raise ValueError('Physical graph full population differs')
    return a,m


def pool(folders,samples,output):
    """Pool fixed ordered admitted samples, refusing conflicting endpoint evidence."""
    if not folders or len(folders)!=len(samples) or len(samples)!=len(set(samples)):
        raise ValueError('Explicit unique ordered sample graphs required')
    first,meta=read(folders[0]);n=len(first['ids']);cfg=meta['policy'];combined={};proof=[]
    for at,(folder,sample) in enumerate(zip(folders,samples)):
        a,m=(first,meta) if at==0 else read(folder)
        if (m['sample']!=sample or m['policy']!=cfg or any(not np.array_equal(a[k],first[k]) for k in ['ids','lengths','eligible'])):
            raise ValueError('Pooled graph sample/policy/full axes differ')
        proof.append(dict(sample=sample,completed=binding(Path(folder)/'completed.json')))
        for edge,count,sig in zip(a['edges'],a['support'],a['orientations']):
            key=tuple(map(int,edge));entry=combined.setdefault(key,dict(signature=int(sig),conflict=False,counts=np.zeros(len(samples),np.int64)))
            entry['conflict']|=entry['signature']!=int(sig);entry['counts'][at]=int(count)
    keys=sorted(k for k,v in combined.items() if not v['conflict']);e=np.array(keys,np.int64).reshape(-1,2)
    counts=np.array([combined[k]['counts'] for k in keys],np.int64).reshape(-1,len(samples));direction=np.array([combined[k]['signature'] for k in keys],np.uint8)
    degree=np.bincount(e.ravel(),minlength=n);good=(degree[e]<=cfg['maximum_degree']).all(1)
    e,counts,direction=e[good],counts[good],direction[good];support=counts.sum(1)
    degree=np.bincount(e.ravel(),minlength=n);weights=np.log1p(support)/np.sqrt(np.maximum(degree[e[:,0]],1)*np.maximum(degree[e[:,1]],1))
    output=Path(output);output.mkdir(parents=True,exist_ok=False)
    arrays={k:first[k] for k in ['ids','lengths','eligible']};arrays.update(edges=e,support=support,orientations=direction,weights=weights,sample_support=counts)
    receipt=dict(kind='physical_template_graph',version=1,sample='pooled',samples=list(samples),policy=cfg,
        ids_sha256=id_digest(first['ids'].tolist()),rows=n,bp=int(first['lengths'].sum()),sources=proof,
        orientation_conflicts=sum(v['conflict'] for v in combined.values()),hub_edges_removed=int((~good).sum()),
        utility=utility(e,first['ids'],first['lengths'],first['eligible']),truth_accessed=False,
        semantics='Log template support with symmetric degree normalization; not calibrated genome probability')
    save_arrays(output/'graph.npz',arrays,receipt)
    write_json(output/'completed.json',dict(status='PASS',graph=binding(output/'graph.npz'),receipt=binding(output/'graph.json')))
    return receipt
