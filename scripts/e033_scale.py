#!/usr/bin/env python3
"""Bounded actual BAM interval-sweep throughput/memory fixture, not a native forecast."""
import argparse
import json
from pathlib import Path
import time


def run(root):
    """Encode 100,000 reads on 524,288 bp and measure exact parent/window moments."""
    import numpy as np
    import pysam
    from dl_binner.multiview.views import prepare,config
    from dl_binner.multiscale.measurement import summarize
    from dl_binner.io import write_json
    import platform
    root=Path(root);root.mkdir(parents=True,exist_ok=False);n=8;length=65536
    fasta=root/'DNA.fna';fasta.write_text(''.join('>opaque-'+str(i)+'\n'+'ACGT'*(length//4)+'\n' for i in range(n)))
    table=root/'old.tsv';table.write_text('contig_id\tsample\n'+''.join('opaque-'+str(i)+'\t1\n' for i in range(n)))
    prepare(fasta,table,root/'old',config());rng=np.random.default_rng(11);bam=root/'tiny-scale.bam'
    header=dict(HD=dict(VN='1.6',SO='coordinate'),SQ=[dict(SN='opaque-'+str(i),LN=length) for i in range(n)])
    with pysam.AlignmentFile(bam,'wb',header=header) as stream:
        for tid in range(n):
            starts=np.sort(rng.integers(0,length-150,size=12500))
            for at,pos in enumerate(starts):
                r=pysam.AlignedSegment(stream.header);r.query_name='r-'+str(tid)+'-'+str(at);r.reference_id=tid;r.reference_start=int(pos)
                r.mapping_quality=60 if at%3 else 0;r.cigarstring='150M';r.query_sequence='A'*150;r.query_qualities=pysam.qualitystring_to_array('I'*150);r.set_tag('NM',1)
                stream.write(r)
    r=summarize(bam,root/'old/features.npz',root/'old/views.npz',root/'measured','sample')
    rate=r['counters']['records']/r['wall_seconds']
    write_json(root/'completed.json',dict(status='PASS_SYNTHETIC_SCALE_ONLY',system=platform.system(),records=r['counters']['records'],
        wall_seconds=r['wall_seconds'],reads_per_second=rate,peak_active_events=r['peak_active_events'],
        BAM_bytes=bam.stat().st_size,parents=n,bp=n*length,full_native_BAM_sort_and_complexity_not_measured=True))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--root',required=True,type=Path);run(p.parse_args().root)
