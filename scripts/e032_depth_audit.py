#!/usr/bin/env python3
"""Audit retained BAM availability and tiny JGI semantics without community depth.

Uses only existing utilities, one generated SAM/BAM and existing BAM headers or
quick checks. No reads are mapped, no community coverage is recomputed and no
candidate feature cache is changed. Missing optional utilities are explicit.
"""
import argparse
import json
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).absolute().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from e024_coverage import binding,write


def run(output):
    """Record current existing BAM/utility identity and real default tiny outputs."""
    out=Path(output);out.mkdir(parents=True,exist_ok=False)
    reuse=json.loads((ROOT/'experiments/E011-cached-grouping-reference/reuse-lock.json').read_text())
    jgi=Path(reuse['metabat_prefix'])/'bin/jgi_summarize_bam_contig_depths'
    plan=json.loads((ROOT/'experiments/E024-oral-measured-coverage/runtime-plan.json').read_text())
    samtools=Path(plan['samtools'])
    result=dict(status='READ_ONLY_INVENTORY',community_depth_recomputed=False,features_changed=False,
        within_contig_variance_used_by_E032=False,paired_links_used_by_E032=False)
    assembly=Path('/srv/dl_binner/experiments/e009/data-stage-v1')
    bams=sorted(assembly.rglob('*.bam')) if assembly.exists() else []
    result['E009_existing_BAMs']=[dict(path=str(p),bytes=p.stat().st_size,index_exists=p.with_suffix('.bam.bai').exists()) for p in bams]
    result['samtools_available']=samtools.is_file();result['jgi_available']=jgi.is_file()
    if not samtools.is_file() or not jgi.is_file():
        result['tiny_JGI']='UNAVAILABLE_NO_INSTALL_FALLBACK';write(out/'audit.json',result);return result
    result['samtools_binding']=binding(samtools);result['jgi_binding']=binding(jgi)
    def command(label,argv):
        p=subprocess.run(list(map(str,argv)),capture_output=True,text=True,timeout=180)
        (out/(label+'.stdout')).write_text(p.stdout);(out/(label+'.stderr')).write_text(p.stderr)
        write(out/(label+'.exit.json'),dict(argv=list(map(str,argv)),exit_code=p.returncode))
        return p
    command('samtools-version',[samtools,'--version']);command('jgi-help',[jgi])
    if bams:
        p=command('E009-quickcheck',[samtools,'quickcheck','-v',*bams])
        if p.returncode:raise ValueError('Existing E009 BAM quickcheck failed')
        # Header only: no bulk decode/re-hash or mapping is claimed here.
        command('E009-header',[samtools,'view','-H',bams[0]])
    header='@HD\tVN:1.6\tSO:coordinate\n@SQ\tSN:opaque-A\tLN:500\n@SQ\tSN:opaque-Z\tLN:500\n'
    rows=[]
    for name,flag,pos,mq,nm in [('perfect',0,101,60,0),('mapq0',0,101,0,0),
            ('duplicate',1024,101,60,0),('qcfail',512,101,60,0),('secondary',256,101,60,0),('supplementary',2048,101,60,0),
            ('identity96',0,101,60,6),('identity98',0,101,60,3)]:
        rows.append('\t'.join(map(str,[name,flag,'opaque-A',pos,mq,'150M','*',0,0,'A'*150,'I'*150,'NM:i:'+str(nm)])))
    sam=out/'tiny.sam';sam.write_text(header+'\n'.join(rows)+'\n');bam=out/'tiny.bam'
    p=command('tiny-encode',[samtools,'view','-b','-o',bam,sam]);p.check_returncode()
    p=command('tiny-sort',[samtools,'sort','-@','0','-m','16M','-o',out/'tiny-sorted.bam',bam]);p.check_returncode()
    matrices={}
    for label,flags in [('default',[]),('MAPQ20',['--minMapQual','20']),('all-edges',['--includeEdgeBases']),('no-variance',['--noIntraDepthVariance'])]:
        target=out/(label+'.tsv');p=command('jgi-'+label,[jgi,'--outputDepth',target,*flags,out/'tiny-sorted.bam']);p.check_returncode()
        matrices[label]=target.read_text()
    expected={'default':1.5,'MAPQ20':1.125,'all-edges':1.2,'no-variance':1.4925}
    observations={}
    for label,text in matrices.items():
        row=next(line.split('\t') for line in text.splitlines() if line.startswith('opaque-A\t'))
        mean=float(row[3]);observations[label]=dict(mean=mean,source_prediction=expected[label],
            matches_source_prediction=abs(mean-expected[label])<=1e-5)
    result.update(status='PASS_READ_ONLY_INVENTORY_AND_REAL_TINY_JGI',tiny_tables=matrices,
        tiny_semantic_observations=observations,
        original_BAM_quickcheck=bool(bams),only_first_existing_BAM_header_read=bool(bams),
        source_review_tag='v2.18 a51200652a8907629b83d63fa5fa6c2f6612d105',
        full_BAM_integrity_not_rehashed=True,Oral_private_BAM_metadata_audited_separately=True)
    write(out/'audit.json',result);return result


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();run(a.output)
