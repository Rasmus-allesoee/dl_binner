"""E009 acquisition-derived axes, source overlap, assembly/mapping and depth.

No truth enters feature construction. Native subprocesses inherit their monitored
worker's process group. Receipts bind actual files and sample order; source names
and simulator coverages never substitute for observed mean-depth values.
"""
import csv
import gzip
import hashlib
import json
import math
from pathlib import Path
import re
import subprocess
import time
import sys
sys.path.insert(0, str(Path(__file__).absolute().parent))

from e009_common import binding, fasta, write_json
from e009_startup import source_cache_argv

STRATA = (1,500,768,1000,2500,10000)


def run_native(argv, log, stdout=None, timeout=None, cwd=None):
    """Run one native child, surface fatal Python worker traces promptly and retain exits.

    Parent owner supervision enforces the whole clock/RSS and cleans the inherited
    process group. This inner watcher detects a traceback even if the tool hangs.
    """
    argv=source_cache_argv(argv)
    log = Path(log); log.parent.mkdir(parents=True, exist_ok=True)
    process = None; started = time.monotonic(); error = None
    output = Path(stdout).open('xb') if stdout else None
    try:
        with log.open('xb') as stream:
            process = subprocess.Popen([str(a) for a in argv], stdout=output or stream,
                                       stderr=stream, cwd=cwd)
            offset, tail = 0, b''
            while True:
                with log.open('rb') as reader:
                    reader.seek(offset); chunk = reader.read(); offset = reader.tell()
                current=tail+chunk
                if any(marker in current for marker in (b'Traceback (most recent call last):',b'Fatal Python error:',
                       b'Error: Failed to run hmmsearch.',b'Error: Failed to run FragGeneScan.')):
                    raise RuntimeError('Native worker emitted a fatal Python traceback')
                tail=current[-65536:]
                if timeout is not None and time.monotonic()-started >= timeout:
                    raise TimeoutError('Native contract clock exceeded')
                if process.poll() is not None:
                    if process.returncode: raise RuntimeError(f'Native exit {process.returncode}: {log}')
                    break
                time.sleep(.1)
    except BaseException as exc:
        error = repr(exc); raise
    finally:
        if process and process.poll() is None:
            process.terminate()
            try: process.wait(timeout=2)
            except subprocess.TimeoutExpired: process.kill(); process.wait(timeout=2)
        if output: output.close()
        write_json(log.with_name(log.name+'.exit.json'), {'argv':[str(a) for a in argv],
                   'exit_code':process.returncode if process else None, 'error':error,
                   'seconds':time.monotonic()-started,'cwd':str(cwd) if cwd else None})


def assembly_axis(path):
    """Inventory all emitted DNA and six strata without applying binner cutoffs."""
    rows = []; counts = {str(x):{'contigs':0,'bp':0} for x in STRATA}
    for ident,seq in fasta(path):
        stratum = max(x for x in STRATA if len(seq)>=x)
        counts[str(stratum)]['contigs'] += 1; counts[str(stratum)]['bp'] += len(seq)
        rows.append({'contig_id':ident,'length':len(seq),'DNA_sha256':hashlib.sha256(seq.encode()).hexdigest(),
                     'stratum_lower_bp':stratum})
    return {'fasta':binding(path),'rows':rows,'strata':counts,
            'contigs':len(rows),'bp':sum(x['length'] for x in rows),
            'eligible_500':sum(x['length']>=500 for x in rows)}


def validate_fastq_pair(first, second=None):
    """Validate the complete mate axis, sequence/quality and pair count; allow interleaving.

    No sampling. Opposite /1,/2 (or CASAVA mate fields) are checked when emitted.
    Generic identical names may supply positional mates; that limitation is recorded.
    """
    def reads(path):
        opener = gzip.open if str(path).endswith('.gz') else open
        with opener(path,'rt',encoding='ascii') as stream:
            while True:
                lines = [stream.readline() for _ in range(4)]
                if not lines[0]:
                    if any(lines[1:]): raise ValueError('Malformed FASTQ trailing record')
                    return
                head,seq,plus,qual = [v.rstrip('\r\n') for v in lines]
                if not head.startswith('@') or not plus.startswith('+') or not seq or len(seq)!=len(qual):
                    raise ValueError('Malformed/truncated FASTQ record')
                if set(seq.upper())-set('ACGTRYSWKMBDHVN') or any(not 33<=ord(c)<=126 for c in qual):
                    raise ValueError('Invalid FASTQ DNA/quality')
                parts=head[1:].split()
                if not parts:raise ValueError('Empty FASTQ read name')
                raw=parts[0];mate=None
                if raw.endswith(('/1','/2')): mate=raw[-1];raw=raw[:-2]
                elif len(parts)>1 and parts[1].startswith(('1:','2:')): mate=parts[1][0]
                yield raw,mate,len(seq)
    left=iter(reads(first));right=iter(reads(second)) if second else left
    pairs=bp=generic=0
    while True:
        a=next(left,None);b=next(right,None)
        if a is None and b is None: break
        if a is None or b is None or a[0]!=b[0] or (a[1] is not None and a[1]!='1') or (b[1] is not None and b[1]!='2'):
            raise ValueError('FASTQ mate names/order/count differ')
        pairs+=1;bp+=a[2]+b[2];generic += a[1] is None and b[1] is None
    if not pairs: raise ValueError('Empty paired reads')
    return {'pairs':pairs,'bp':bp,'mate_identity_unspecified_pairs':generic,
            'files':[binding(p) for p in ([first,second] if second else [first])]}


def canonical_dna(seq):
    """Hash strand-canonical IUPAC DNA while retaining unmodified sequence elsewhere."""
    complement = str.maketrans('ACGTRYSWKMBDHVN','TGCAYRSWMKVHDBN')
    reverse=seq.translate(complement)[::-1]
    return hashlib.sha256(min(seq,reverse).encode()).hexdigest()


def source_catalog(root, development, output):
    """Inventory full source FASTAs, matching accession and canonical replicon bytes.

    Unknown historical/pretraining inventories are reported, not declared clean or
    used to drop data. Near-genome/species evidence remains a separate annotation.
    """
    accession_set=set(development['accessions']);hash_set=set(development['canonical_replicon_sha256s'])
    files=[];replicons=[]
    for path in sorted(Path(root).rglob('*')):
        if not path.is_file() or not any(str(path).endswith(s) for s in ('.fa','.fna','.fasta','.fa.gz','.fna.gz','.fasta.gz')):continue
        genome=path.name.removesuffix('.gz');records=[]
        for ident,seq in fasta(path):
            accessions=re.findall(r'(?:NZ_)?(?:[A-Z]{1,4}_?\d{5,})(?:\.\d+)?',ident)
            digest=canonical_dna(seq)
            item={'genome_file':genome,'replicon_id':ident,'length':len(seq),
                  'DNA_sha256':hashlib.sha256(seq.encode()).hexdigest(),'canonical_sha256':digest,
                  'accessions':accessions,'development_accession_match':sorted(set(accessions)&accession_set),
                  'development_exact_replicon_match':digest in hash_set}
            records.append(item);replicons.append(item)
        files.append({'path':str(path),'name':genome,'file':binding(path),'replicons':records})
    if not files:raise ValueError('No source genome FASTAs found')
    value={'files':files,'replicon_count':len(replicons),'bp':sum(x['length'] for x in replicons),
           'scope':'exact accession/full-replicon bytes; partial contig and ANI overlap not excluded',
           'pretraining_overlap':'unknown inventories are a generalization limitation, not evaluator label leakage'}
    write_json(output,value);return value


def competitive_reference(catalog, selected_genome_names, output):
    """Emit opaque unique replicon IDs for all simulator-selected genomes/replicons.

    Identical accession headers in separate sources remain distinct competitors.
    Selection comes from frozen simulator origin records, never predicted bins.
    Taxonomy/target membership must be frozen separately; names are not domain truth.
    """
    output=Path(output);axis={};genome_lengths={};found=set()
    with output.open('x') as out:
        for gi,item in enumerate(catalog['files']):
            if item['name'] not in selected_genome_names:continue
            if item['name'] in found:raise ValueError('Duplicate source genome file name')
            if binding(item['path'])!=item['file']:raise ValueError('Source catalog DNA bytes changed')
            found.add(item['name']);genome_lengths[item['name']]=0
            for ri,(ident,seq) in enumerate(fasta(item['path'])):
                alias=f'G{gi:06d}R{ri:06d}'
                axis[alias]={'genome':item['name'],'original_replicon_id':ident,'length':len(seq)}
                genome_lengths[item['name']]+=len(seq);out.write(f'>{alias}\n{seq}\n')
    if found!=set(selected_genome_names):raise ValueError('Simulator-selected source genome names missing')
    write_json(str(output)+'.axis.json',{'reference':binding(output),'reference_axis':axis,
                 'genome_lengths':genome_lengths,'selection_role':'simulator origins only; features do not consume this path'})
    return axis


def assemble(megahit, first, second, threads, mem_bytes, output, log):
    """One pinned MEGAHIT default assembly; 200-bp emission is separate from eligibility."""
    if threads<1 or mem_bytes<=0:raise ValueError('Invalid assembly allocation')
    validate_fastq_pair(first,second)
    command=[megahit,'-1',first,'-2',second,'-t',threads,'-m',mem_bytes,'--min-contig-len','200','-o',output]
    run_native(command,log)
    value=assembly_axis(Path(output)/'final.contigs.fa')
    if any(x['length']<200 for x in value['rows']):raise ValueError('Assembler emitted DNA below configured floor')
    write_json(Path(output)/'e009-assembly.json',value);return value


def bam_axis(samtools, bam, reference, log):
    """Require coordinate sort and the exact ordered FASTA SQ name/length axis."""
    header=Path(str(log)+'.header.sam');run_native([samtools,'view','-H',bam],log,stdout=header)
    rows=[];coordinate=False
    for line in header.read_text().splitlines():
        fields=line.split('\t')
        if fields[0]=='@HD':coordinate='SO:coordinate' in fields
        if fields[0]=='@SQ':
            tags=dict(v.split(':',1) for v in fields[1:]);rows.append((tags['SN'],int(tags['LN'])))
    expected=[(ident,len(seq)) for ident,seq in fasta(reference)]
    if not coordinate or rows!=expected:raise ValueError('BAM/reference sort/axis differs')
    return rows


def map_sample(strobealign, samtools, reference, first, second, sample, column, threads, output):
    """Map then sort/index serially, binding sample and reference rather than basename guesses."""
    output=Path(output);output.mkdir(parents=True,exist_ok=False)
    reads=validate_fastq_pair(first,second)
    sam=output/'alignment.sam';bam=output/f'sample_{sample}.sorted.bam'
    command=[strobealign,'-t',threads]
    if second is None:command+=['--interleaved']
    command+=[reference,first]+([second] if second else [])
    run_native(command,output/'map.log',stdout=sam)
    # samtools -@ is EXTRA threads; include its main thread in the allocation.
    run_native([samtools,'sort','-@',threads-1,'-m','256M','-o',bam,sam],output/'sort.log')
    run_native([samtools,'index','-@',threads-1,bam],output/'index.log')
    bam_axis(samtools,bam,reference,output/'axis.log')
    receipt={'sample':sample,'column':column,'reference':binding(reference),'reads':reads,'bam':binding(bam)}
    write_json(bam.with_suffix('.mapped.json'),receipt);return bam


def mean_depth(samtools, reference, bam, column, threads, output):
    """Stream native all-position depth and exact zeros under the E005 flag definition.

    Depth subprocess uses one main plus N-2 BGZF threads, plus one Python reducer.
    Nonzero native failures or wrong position/contig/sample axes fail immediately.
    """
    if threads<2:raise ValueError('Depth requires reducer plus native main CPU')
    output=Path(output);rows=bam_axis(samtools,bam,reference,output.with_suffix('.axis.log'))
    receipt=json.loads(Path(bam).with_suffix('.mapped.json').read_text())
    if receipt['column']!=column or receipt['reference']!=binding(reference) or receipt['bam']!=binding(bam):
        raise ValueError('BAM/source/column receipt changed')
    command=[str(samtools),'depth','-aa','-q','0','-Q','0','-g','0x600','-G','0x800','-@',str(threads-2),str(bam)]
    values=[];process=None
    with output.with_suffix('.stderr').open('xb') as log:
        try:
            process=subprocess.Popen(command,stdout=subprocess.PIPE,stderr=log)
            for ident,length in rows:
                total=0
                for pos in range(1,length+1):
                    fields=process.stdout.readline().decode().rstrip('\n').split('\t')
                    if len(fields)!=3 or fields[0]!=ident or int(fields[1])!=pos or int(fields[2])<0:
                        raise ValueError('Native depth position/reference axis mismatch')
                    total+=int(fields[2])
                values.append(total/length)
            if process.stdout.readline():raise ValueError('Extra native depth rows')
            process.stdout.close()
            if process.wait(timeout=10):raise RuntimeError('Native depth failed')
        finally:
            if process and process.poll() is None:
                process.terminate()
                try:process.wait(timeout=2)
                except subprocess.TimeoutExpired:process.kill();process.wait(timeout=2)
    with output.open('x') as out:
        out.write('contig_id\t'+column+'\n')
        for (ident,length),value in zip(rows,values):out.write(f'{ident}\t{value:.17g}\n')
    write_json(output.with_suffix('.receipt.json'),{'reference':binding(reference),'bam':binding(bam),
                'column':column,'output':binding(output),'zero_rows':sum(v==0 for v in values),
                'policy':'M/= /X; exclude 0x904; MAPQ/baseQ0; no deletion/edge/overlap trimming',
                'command':command})
    return values


def combine_depth(reference, columns, paths, output):
    """Join exact ordered depth axes and verify file receipts; never impute missing rows."""
    if len(columns)!=len(set(columns)) or len(columns)!=len(paths):raise ValueError('Duplicate/missing depth columns')
    axis=[ident for ident,seq in fasta(reference)];values=[]
    for column,path in zip(columns,paths):
        receipt=json.loads(Path(path).with_suffix('.receipt.json').read_text())
        if receipt['column']!=column or receipt['reference']!=binding(reference) or receipt['output']!=binding(path):
            raise ValueError('Depth receipt/bytes/column mismatch')
        with Path(path).open() as stream:rows=list(csv.reader(stream,delimiter='\t'))
        if not rows or rows[0]!=['contig_id',column] or [r[0] for r in rows[1:]]!=axis:
            raise ValueError('Depth axes/header mismatch')
        data=[float(r[1]) for r in rows[1:]]
        if any(not math.isfinite(v) or v<0 for v in data):raise ValueError('Nonfinite/negative depth')
        values.append(data)
    with Path(output).open('x') as out:
        out.write('\t'.join(['contig_id',*columns])+'\n')
        for i,ident in enumerate(axis):out.write('\t'.join([ident,*[f'{v[i]:.17g}' for v in values]])+'\n')
    write_json(str(output)+'.manifest.json',{'reference':binding(reference),'ordered_columns':columns,
                 'depth_files':[binding(p) for p in paths],'matrix':binding(output)})


def partition(reference, bin_files, eligible, output):
    """Normalize native bin FASTAs into a complete assignment axis, refusing corruption.

    Missing eligible DNA is unassigned; native-range exclusions retain explicit
    reasons. No largest-bin or dominant-duplicate repair is permitted.
    """
    sequences=dict(fasta(reference));assigned={};bin_names=set();eligible=set(eligible)
    if not eligible<=set(sequences):raise ValueError('Eligibility includes unknown contigs')
    for path in bin_files:
        label=Path(path).name
        if label in bin_names:raise ValueError('Duplicate native bin name')
        bin_names.add(label)
        for ident,seq in fasta(path):
            if ident not in sequences or sequences[ident]!=seq:raise ValueError('Native unknown ID or altered DNA')
            if ident in assigned:raise ValueError('Duplicate native bin claim')
            if ident not in eligible:raise ValueError('Assigned DNA outside recorded native eligibility')
            assigned[ident]=label
    with Path(output).open('x') as out:
        out.write('contig_id\tbin_id\tstatus\texclusion_reason\tlength\n')
        for ident,seq in sequences.items():
            status='assigned' if ident in assigned else 'unassigned' if ident in eligible else 'excluded'
            reason='' if ident in eligible else 'outside_recorded_native_eligibility'
            out.write(f"{ident}\t{assigned.get(ident,'')}\t{status}\t{reason}\t{len(seq)}\n")
    return {'assigned':len(assigned),'unassigned':len(eligible-set(assigned)),'excluded':len(sequences)-len(eligible)}
