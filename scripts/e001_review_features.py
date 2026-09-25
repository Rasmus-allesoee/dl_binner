"""Verify a compact native feature return against E001's frozen input contracts.

Binaries remain on UCloud: acceptance distinguishes returned native validation
and hash receipts from arrays independently inspected locally. No extraction is
rerun. The output pins completed artifacts for the paired-pilot input gate.
"""
import argparse
import csv
import hashlib
import io
import json
from pathlib import Path
import sys
import tarfile

sys.path.insert(0,str(Path(__file__).resolve().parent))
from e001_features import EXP, read, write, require, sha, depth_report


def review(archive, checksum, terminal):
    """Audit all returned axes/receipts, scale tables, statuses and accounting."""
    require(checksum.read_text().split()==[sha(archive),archive.name],'Return checksum mismatch')
    with tarfile.open(archive) as tar:
        members=[m for m in tar if m.isfile()]
        require(len({m.name for m in members})==len(members),'Duplicate return members')
        data={m.name.split('/',1)[1]:tar.extractfile(m).read() for m in members}
    get=lambda n:json.loads(data[n])
    digest=lambda b:hashlib.sha256(b).hexdigest()
    frozen=read(EXP/'frozen-inputs.json');manifest=read(EXP/'multisample-bam-manifest.json')
    status=get('status.json');summary=get('feature-summary.json');runtime=get('runtime.json')
    require(status['exit_code']==0 and get('workflow.command.json')['returncode']==0,'Incomplete feature run')
    require('PASS: workflow' in terminal.read_text(),'No terminal workflow completion')
    require(abs(status['allocated_core_hours']-status['elapsed_seconds']*status['vcpus']/3600)<1e-9,'Cost mismatch')
    inputs=get('inputs.json');require(inputs['manifest_sha256']==sha(EXP/'multisample-bam-manifest.json'),'Changed BAM manifest')
    require(inputs['reference_sha256']==frozen['outputs']['canonical.fna'],'Changed reference')
    ids=data['comebin/C0/contig_ids.txt'].decode().splitlines()
    require(len(ids)==len(set(ids))==frozen['retained_contigs'],'Invalid contig IDs')
    names=[f'{i:02d}-sample-{s}.bam' for i,s in enumerate(frozen['samples'])]
    results={tool:get(tool+'/result.json') for tool in ('metabat','vamb','comebin')}
    for tool,result in results.items():
        require(result==summary['tools'][tool] and result['samples']==frozen['samples'],'Summary/sample mismatch')
        require(result['input_manifest_sha256']==inputs['manifest_sha256'],'Tool input mismatch')
        for name,receipt in result['artifacts'].items():
            if tool+'/'+name in data:
                require(digest(data[tool+'/'+name])==receipt['sha256'],'Returned artifact changed: '+name)
    for c in ('C0','CT'):
        require([e['sample'] for e in inputs['bams'][c]]==frozen['samples'],'Input order mismatch')
        for e,m in zip(inputs['bams'][c],manifest['samples']):
            require(e['sha256']==m['summary'][c]['sha256'],'BAM hash mismatch')
        require(data[f'vamb/{c}/ids.txt'].decode().splitlines()==ids,'VAMB axis mismatch')
        require(data[f'comebin/{c}/contig_ids.txt'].decode().splitlines()==ids,'COMEBin axis mismatch')
        require(data[f'comebin/{c}/bam_ids.txt'].decode().splitlines()==names,'COMEBin column mismatch')
        cov=get(f'comebin/{c}/coverage_manifest.json')
        require(cov['complete'] and cov['coverage_mean']['shape']==[10,6,len(ids)] and cov['coverage_var']['shape']==[10,6,len(ids)],'Coverage tensor shape mismatch')
        for tool in ('vamb','comebin'):
            native=get(f'{tool}/{c}/native-features.json')
            require(list(native['bam_sha256'].values())==[m['summary'][c]['sha256'] for m in manifest['samples']],'Native BAM ordering/hash mismatch')
            require(native['fasta_sha256']==frozen['outputs']['canonical.fna'],'Native reference mismatch')
        require(max(results['vamb']['conditions'][c]['scale_max_abs_difference'].values())<1e-5,'VAMB scale discrepancy')
    for name in ('input-mask.npy','composition.npz','ids.txt'):
        r=results['vamb']['artifacts'];require(r['C0/'+name]['sha256']==r['CT/'+name]['sha256'],'VAMB paired identity mismatch')
    for name in ('augmentation_intervals.npy','kmer_counts.npy','contig_lengths.npy','contig_ids.txt','bam_ids.txt'):
        r=results['comebin']['artifacts'];require(len({r[c+'/'+name]['sha256'] for c in ('C0','CT','CS')})==1,'COMEBin fixed identity mismatch')
    require(data['comebin/CS/bam_ids.txt'].decode().splitlines()==names,'CS sample mismatch')
    require(results['comebin']['paired']['status']=='paired_provenance_valid','No paired coverage validation')
    import numpy as np
    tables={}
    for c in ('C0','CT','CS'):
        rows=list(csv.reader(io.StringIO(data[f'metabat/{c}/depth.tsv'].decode()),delimiter='\t'))
        require(rows[0][3::2]==[Path(n).stem for n in names],'MetaBAT column mismatch')
        require([r[0] for r in rows[1:]]==ids,'MetaBAT row mismatch')
        require(sum(int(r[1]) for r in rows[1:])==frozen['retained_bp'],'MetaBAT lengths mismatch')
        tables[c]=np.array([[float(x) for x in r[2:]] for r in rows[1:]])
        require(np.isfinite(tables[c]).all() and (tables[c]>=0).all(),'Invalid depth values')
    expected=tables['C0'].copy();expected[:,0]*=.1;expected[:,1::2]*=.1;expected[:,2::2]*=.01
    require(np.allclose(expected,tables['CS'],rtol=1e-12,atol=1e-12),'MetaBAT CS transform mismatch')
    cb=results['comebin'];require(max(cb['CS_max_abs_difference_per_view'])<1e-5,'Material COMEBin scale discrepancy needs review')
    for full,thin in zip(cb['zero_means_per_sample_view']['C0'],cb['zero_means_per_sample_view']['CT']):
        require(all(0<=a<=b<=len(ids) for a,b in zip(full,thin)),'Invalid thinning zero counts')
    benchmarks={n:list(csv.DictReader(io.StringIO(b.decode()),delimiter='\t')) for n,b in data.items() if n.startswith('benchmarks/') and n.endswith('.tsv')}
    return {'status':'accepted','reviewed':'2026-09-25','directory':runtime['stage'],
            'archive_sha256':sha(archive),'terminal_sha256':sha(terminal),'source_commit':runtime['source_commit'],
            'run_status':status,'samples':frozen['samples'],'contigs':len(ids),'results':results,
            'summary_sha256':digest(data['feature-summary.json']),
            'receipt_sha256':{n:digest(data[n]) for n in ('status.json','inputs.json','feature-summary.json','metabat/result.json','vamb/result.json','comebin/result.json')},
            'benchmarks':benchmarks,'scope':'Returned native QC, identities, hashes and MetaBAT tables accepted. Bulk arrays remain on UCloud and must match hashes before fits; no biological scores.'}


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for n in ('archive','checksum','terminal'):p.add_argument(n,type=Path)
    p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    require(not a.out.exists(),'Preserve existing assessment');write(a.out,review(a.archive,a.checksum,a.terminal))
    print('PASS: feature integrity, axes, scale controls and run accounting')
