"""Exact streamed BAM moments for full parents and retained DNA-window intervals.

The coordinate sweep stores only active alignment events, not a per-base assembly
matrix. Outputs are exclusive, checksum-bound sample directories; partial failures
are not consumable. No read mapping, quality estimation or label join occurs.
"""
from collections import Counter
import hashlib
import heapq
import json
from pathlib import Path
import time

import numpy as np

from ..context.tokens import binding
from ..io import digest, write_json, emit
from ..multiview.views import load

POLICY = dict(version=1, reader='pysam==0.23.3', min_identity=.97,
    exclude_flags=0xF04, min_mapq=0, reject_mapq255=True, high_mapq=20,
    min_base_quality=0, missing_base_qualities='included_at_BQ0_and_audited',
    identity='(M+EQ+X-(NM-I-D))/(M+EQ+X+I+D)',
    reference_skips='refuse', edge_bases=0, overlapping_mates='count_each_alignment',
    coverage='aligned_M_EQ_X_including_substitutions', denominator='full_interval_including_zeros',
    variance='population_E_depth_squared_minus_mean_squared', coordinates='zero_based_half_open')


def policy(value=None):
    """Require the one common prospective procedure, including exact field types."""
    value = POLICY if value is None else value
    if value != POLICY or any(type(value[k]) is not type(v) for k,v in POLICY.items()):
        raise ValueError('Unfrozen BAM measurement policy')
    return dict(value)


def intervals(data, views):
    """Return exact parent/crop coordinates; -1 distinguishes an absent DNA view."""
    n=len(data['ids']); result=np.full((n,5,2),-1,np.int64)
    result[:,0,0]=0; result[:,0,1]=data['lengths']
    result[:,1:]=views['coordinates']
    good=result[:,:,0]>=0
    if np.any(good & ((result[:,:,1]<=result[:,:,0]) | (result[:,:,1]>data['lengths'][:,None]))):
        raise ValueError('Invalid retained DNA-window interval')
    return result


def aligned_blocks(read, length, counters):
    """Validate one kept primary alignment and return exact covered half-open spans.

    NM counts substitutions plus I/D. Explicit =/X bounds must agree even for
    mixed M/=/X. Malformed kept reads fail rather than becoming missing support.
    Filtered records need no invented NM. BQ is exactly zero for this protocol.
    """
    if read.flag & POLICY['exclude_flags']:
        counters['excluded_flags']+=1; return []
    if read.mapping_quality==255:
        counters['excluded_MAPQ255']+=1; return []
    cigar=read.cigartuples
    if not cigar or read.query_sequence is None or read.reference_start<0:
        raise ValueError('Mapped primary is missing CIGAR/sequence/position')
    if any(type(n) is not int or n<=0 or op not in range(9) for op,n in cigar):
        raise ValueError('Malformed CIGAR operation/length')
    if any(op==3 for op,_ in cigar):raise ValueError('Reference-skip CIGAR is outside pinned short-read policy')
    consumed=sum(n for op,n in cigar if op in (0,1,4,7,8))
    if consumed!=len(read.query_sequence):raise ValueError('CIGAR/query sequence length differs')
    if not read.has_tag('NM'):raise ValueError('Kept primary alignment missing NM')
    nm=read.get_tag('NM')
    if type(nm) is not int or nm<0:raise ValueError('Malformed NM edit count')
    total=sum(n for op,n in cigar if op in (0,7,8))
    ins=sum(n for op,n in cigar if op==1); delete=sum(n for op,n in cigar if op==2)
    eq=sum(n for op,n in cigar if op==7); diff=sum(n for op,n in cigar if op==8)
    substitutions=nm-ins-delete
    if not total or not diff<=substitutions<=total-eq:
        raise ValueError('NM/CIGAR substitution accounting differs')
    if read.reference_start+total+delete>length:
        raise ValueError('CIGAR escapes reference interval')
    if (total-substitutions)/(total+ins+delete)<POLICY['min_identity']:
        counters['excluded_identity']+=1; return []
    if read.query_qualities is None:counters['included_missing_BQ']+=1
    counters['accepted_reads']+=1; counters['accepted_aligned_bases']+=total
    if read.mapping_quality>=POLICY['high_mapq']:counters['high_MAPQ_aligned_bases']+=total
    position=read.reference_start; blocks=[]
    for op,n in cigar:
        if op in (0,7,8):
            blocks.append((position,position+n));position+=n
        elif op==2:position+=n
    return blocks


class Sweep:
    """Integrate coverage runs and prefix moments at a few exact interval endpoints.

    Active start/end events are O(overlapping aligned blocks), independent of
    assembly length or read count. Integrals include zeros between alignments.
    """
    def __init__(self, length, coordinates):
        self.length=int(length);self.coordinates=np.asarray(coordinates,np.int64)
        if self.coordinates.shape!=(5,2):raise ValueError('Expected parent and four retained views')
        self.bounds=sorted(set([0,self.length]+[int(x) for row in self.coordinates if row[0]>=0 for x in row]))
        if self.bounds[0]!=0 or self.bounds[-1]!=self.length:raise ValueError('Sweep interval escapes reference')
        self.at=0;self.depth=0;self.high=0;self.events=[];self.totals=[0,0,0,0]
        self.prefix={0:tuple(self.totals)};self.bound_at=1;self.peak_events=0

    def _run(self,end):
        """Integrate a constant-depth segment, splitting only requested endpoints."""
        if not self.at<=end<=self.length:raise ValueError('Nonmonotone depth sweep')
        if end==self.at:return
        rate=(self.depth,self.depth*self.depth,int(self.depth>0),self.high)
        while self.bound_at<len(self.bounds) and self.bounds[self.bound_at]<=end:
            p=self.bounds[self.bound_at];width=p-self.at
            for j in range(4):self.totals[j]+=width*rate[j]
            self.at=p;self.prefix[p]=tuple(self.totals);self.bound_at+=1
        width=end-self.at
        for j in range(4):self.totals[j]+=width*rate[j]
        self.at=end

    def advance(self,position):
        """Commit all events through the next alignment start or final contig end."""
        while self.events and self.events[0][0]<=position:
            p=self.events[0][0];self._run(p)
            while self.events and self.events[0][0]==p:
                _,d,h=heapq.heappop(self.events);self.depth+=d;self.high+=h
            if not 0<=self.high<=self.depth:raise ValueError('Invalid active coverage counters')
        self._run(position)

    def add(self,blocks,high):
        """Queue an alignment's CIGAR-exact spans after advancing to its start."""
        for a,b in blocks:
            if not self.at<=a<b<=self.length:raise ValueError('Late/invalid aligned interval')
            heapq.heappush(self.events,(a,1,int(high)))
            heapq.heappush(self.events,(b,-1,-int(high)))
        self.peak_events=max(self.peak_events,len(self.events))

    def finish(self):
        """Return sum, sum-square, breadth numerator and high-MAPQ aligned mass."""
        self.advance(self.length)
        if self.events or self.depth or self.high:raise ValueError('Unclosed alignment events')
        if max(self.totals)>2**53:raise ValueError('Depth moment exceeds exact float64 integer range')
        result=np.zeros((5,4),np.float64)
        for j,(a,b) in enumerate(self.coordinates):
            if a>=0:result[j]=[x-y for x,y in zip(self.prefix[int(b)],self.prefix[int(a)])]
        return result


def summarize(bam,features,views,output,sample,expected_dictionary=None):
    """Read one sorted BAM once into an exclusive all-contig moment cache.

    SHA verification is a separate sequential file pass. The BAM and original
    feature/view artifacts remain untouched. A missing footer/refusal leaves no
    admissible sample.json. Only explicit source-blind dictionary IDs are accepted.
    """
    import pysam
    if pysam.__version__!='0.23.3':raise ValueError('Pinned pysam 0.23.3 required')
    bam=Path(bam);out=Path(output);out.mkdir(parents=True,exist_ok=False)
    data,meta,v,vm=load(features,views);coords=intervals(data,v)
    if not isinstance(sample,str) or sample not in meta['samples']:raise ValueError('Unknown ordered sample ID')
    ids=data['ids'].tolist();lookup={ident:i for i,ident in enumerate(ids)}
    original=binding(bam);signature=(bam.stat().st_size,bam.stat().st_mtime_ns)
    shape=(len(ids),5,4);mom=np.lib.format.open_memmap(out/'moments.npy',mode='w+',dtype=np.float64,shape=shape);mom[:]=0
    counters=Counter();peak=0;start=time.monotonic();current=-1;sweep=None;last=(-1,-1);unplaced=False
    with pysam.AlignmentFile(str(bam),'rb',threads=1,ignore_truncation=False) as stream:
        dictionary=list(zip(stream.references,stream.lengths))
        if (stream.header.to_dict().get('HD',{}).get('SO')!='coordinate' or
                len(dictionary)!=len(ids) or set(stream.references)!=set(ids) or
                any(int(data['lengths'][lookup[x]])!=n for x,n in dictionary)):
            raise ValueError('BAM coordinate header/full source-blind dictionary differs')
        dictionary_hash=hashlib.sha256(json.dumps(dictionary,separators=(',',':')).encode()).hexdigest()
        if expected_dictionary is not None and dictionary_hash!=expected_dictionary:
            raise ValueError('Ordered BAM dictionary differs between samples')
        for read in stream.fetch(until_eof=True):
            counters['records']+=1;tid,pos=read.reference_id,read.reference_start
            if counters['records']%1_000_000==0:
                emit('multiscale_BAM_progress',sample=sample,records=counters['records'],accepted_reads=counters['accepted_reads'],
                    accepted_aligned_bases=counters['accepted_aligned_bases'],reference_index=tid,position=pos)
            if tid<0 or pos<0:
                if not read.is_unmapped:raise ValueError('Mapped record has no coordinate')
                unplaced=True;counters['unplaced_unmapped']+=1;continue
            if unplaced or (tid,pos)<last:raise ValueError('Actual BAM coordinate order differs')
            last=(tid,pos)
            if tid!=current:
                if sweep is not None:
                    mom[lookup[dictionary[current][0]]]=sweep.finish();peak=max(peak,sweep.peak_events)
                current=tid;row=lookup[dictionary[tid][0]]
                sweep=Sweep(dictionary[tid][1],coords[row])
            sweep.advance(pos)
            blocks=aligned_blocks(read,dictionary[tid][1],counters)
            if blocks:sweep.add(blocks,read.mapping_quality>=POLICY['high_mapq'])
        if sweep is not None:
            mom[lookup[dictionary[current][0]]]=sweep.finish();peak=max(peak,sweep.peak_events)
    mom.flush();del mom
    if (bam.stat().st_size,bam.stat().st_mtime_ns)!=signature:raise ValueError('BAM changed during measurement')
    # BAM dictionaries with no alignments still produce measured zero rows.
    receipt=dict(kind='multiscale_BAM_sample',version=1,policy=policy(),sample=sample,
        features=binding(features),views=binding(views),BAM=original,dictionary_sha256=dictionary_hash,
        ids_sha256=meta['ids_sha256'],rows=len(ids),bp=int(data['lengths'].sum()),shape=list(shape),
        moments=binding(out/'moments.npy'),counters=dict(counters),peak_active_events=peak,
        wall_seconds=time.monotonic()-start,pysam=pysam.__version__,samtools_htslib=pysam.__samtools_version__,
        zeros='all dictionary rows/valid intervals fully observed including absent records',truth_accessed=False)
    write_json(out/'sample.json',receipt);return receipt
