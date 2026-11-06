"""Streaming independent GTDB protein-reference construction; no acquisition.

Input is a separately admitted whole archive and release-specific taxonomy TSVs.
Reference genome/accession joins belong to the classifier database, never to the
query feature pipeline. All archive members receive a compact checksum record.
"""
import gzip
import hashlib
import io
from pathlib import Path
import re
import tarfile

from ..context.tokens import binding
from ..io import write_json
from .tree import from_gtdb
from .classifier import command, VERSION

GTDB_PROTEINS_BYTES=71_733_563_809
GTDB_PROTEINS_MD5='49fffb75d1d142ec669d964690c2ab6b'
TAXONOMY_MEMBERS=[dict(bytes=83820569,sha256='03dd92ecf0d5ee24d79df2cb913439b99a69f7ffb5a7785947b4a6f8c4b07652'),
                  dict(bytes=1776985,sha256='8f824c59973a0655ab979f4496833be4aef28ee1fe55ab7bf311dc4180f726ce')]


def build(binary, archive, taxonomy_files, output, engineering=False):
    """Verify and stream proteins into a fresh native protein/taxonomy database.

    Keep the archive, source-member inventory, source accession map, converted
    FASTA and native DB until independent verification/collection admits cleanup.
    No missing/corrupt member triggers an alternate database or a download.
    A prospective 250 GiB converted-FASTA cap is a resource refusal, not permission
    to truncate proteins. Real release/index/scratch throughput remains a native gate.
    """
    archive=Path(archive);root=Path(output);root.mkdir(parents=True,exist_ok=False)
    command(binary,['version'],root,'version')
    if (root/'version.log').read_text().strip()!=VERSION:raise ValueError('Unsupported reference-builder binary')
    if archive.is_symlink() or not archive.is_file():raise ValueError('Regular admitted protein archive required')
    md5=hashlib.md5()
    with archive.open('rb')as stream:
        for b in iter(lambda:stream.read(1024**2),b''):md5.update(b)
    if not engineering and (archive.stat().st_size!=GTDB_PROTEINS_BYTES or md5.hexdigest()!=GTDB_PROTEINS_MD5):
        raise ValueError('GTDB R220 whole protein payload differs')
    if not engineering and sorted([binding(p)for p in taxonomy_files],key=lambda b:b['sha256'])!=sorted(TAXONOMY_MEMBERS,key=lambda b:b['sha256']):
        raise ValueError('GTDB R220 taxonomy metadata bytes differ')
    if engineering and archive.stat().st_size>2*1024**2:raise ValueError('Synthetic reference archive is not tiny')
    tree,accessions=from_gtdb(taxonomy_files);tree.save(root/'tree.json')
    dump=root/'dump';dump.mkdir()
    with (dump/'nodes.dmp').open('x')as nodes,(dump/'names.dmp').open('x')as names:
        for row in tree.nodes[1:]:
            nodes.write(f"{row['id']}\t|\t{row['parent']}\t|\t{row['rank']}\t|\t\t|\t0\t|\t0\t|\t11\t|\t0\t|\t0\t|\t0\t|\t0\t|\t0\t|\t\t|\n")
            names.write(f"{row['id']}\t|\t{row['name']}\t|\t\t|\tscientific name\t|\n")
    (dump/'merged.dmp').write_text('');(dump/'delnodes.dmp').write_text('')
    count=residues=converted=0;genomes=set();member_names=set()
    with (root/'proteins.faa').open('x')as fasta,(root/'mapping.tsv').open('x')as mapping,(root/'reference-sources.tsv').open('x')as sources,(root/'members.jsonl').open('x')as inventory:
        import json
        sources.write('protein_id\treference_accession\tprotein_aa_length\tsha256\n')
        with tarfile.open(archive,mode='r|gz')as tar:
            for member in tar:
                name=Path(member.name)
                if name.is_absolute()or '..'in name.parts or member.name in member_names or not (member.isfile()or member.isdir()):raise ValueError('Unsafe/duplicate protein archive member')
                member_names.add(member.name)
                if member.isdir():continue
                raw=tar.extractfile(member);h=hashlib.sha256();protein=member.name.endswith(('.faa','.faa.gz'))
                # tarfile streams one member. Hash its compressed member bytes,
                # then decode through a bounded spool, never an entire collection.
                import tempfile
                with tempfile.SpooledTemporaryFile(max_size=1024**2,dir=root)as temporary:
                    seen=0
                    for b in iter(lambda:raw.read(1024**2),b''):
                        h.update(b);temporary.write(b);seen+=len(b)
                    if seen!=member.size:raise ValueError('Truncated protein archive member')
                    record=dict(name=member.name,bytes=seen,sha256=h.hexdigest(),protein=protein)
                    if protein:
                        hit=re.search(r'GC[AF]_[0-9]+\.[0-9]+',member.name)
                        if not hit:raise ValueError('No independent reference accession in protein member')
                        accession=('RS_'if hit.group().startswith('GCF')else 'GB_')+hit.group()
                        if accession not in accessions or accession in genomes:raise ValueError('Missing/duplicate reference taxonomy accession')
                        genomes.add(accession);temporary.seek(0);decoded=gzip.GzipFile(fileobj=temporary,mode='rb')if member.name.endswith('.gz')else temporary
                        text=io.TextIOWrapper(decoded,encoding='ascii');chunks=[];header=False;member_proteins=0
                        def finish():
                            """Validate and emit one reference protein under an opaque ID."""
                            nonlocal count,residues,converted,member_proteins
                            if not header:return
                            sequence=''.join(chunks).upper().rstrip('*')
                            if not sequence or set(sequence)-set('ACDEFGHIKLMNPQRSTVWYBXZJUO'):raise ValueError('Malformed reference protein sequence')
                            q='r%010d'%count;line='>'+q+'\n'+sequence+'\n';converted+=len(line)
                            if converted>250*1024**3 or (engineering and count>=1000):raise ValueError('Prospective protein-conversion bound exceeded')
                            fasta.write(line);mapping.write(q+'\t'+str(accessions[accession])+'\n');sources.write(q+'\t'+accession+'\t'+str(len(sequence))+'\t'+hashlib.sha256(sequence.encode()).hexdigest()+'\n')
                            count+=1;residues+=len(sequence);member_proteins+=1
                        for line in text:
                            line=line.strip()
                            if not line:continue
                            if line.startswith('>'):finish();chunks=[];header=True
                            else:
                                if not header:raise ValueError('Protein sequence before header')
                                chunks.append(line)
                        finish();text.detach()
                        if member.name.endswith('.gz'):decoded.close()
                        record.update(accession=accession,proteins=member_proteins)
                        if not member_proteins:raise ValueError('Empty reference protein member')
                    inventory.write(json.dumps(record,sort_keys=True)+'\n')
    if not count:raise ValueError('Reference archive has no searchable proteins')
    if not engineering and len(genomes)!=113104:raise ValueError('GTDB R220 representative-genome population differs')
    command(binary,['createdb',root/'proteins.faa',root/'target','--dbtype','1','--shuffle','0','--compressed','1','--threads','4'],root,'createdb')
    command(binary,['createtaxdb',root/'target',root/'tmp','--ncbi-tax-dump',dump,'--tax-mapping-file',root/'mapping.tsv','--threads','4'],root,'createtaxdb')
    files={str(p.relative_to(root)):binding(p)for p in root.iterdir()if p.is_file()and (p.name.startswith('target')or p.name=='tree.json')}
    manifest=dict(kind='independent_taxonomy_database',version=1,binary=binding(binary),release='own_synthetic_reference'if engineering else 'GTDB_R220_220.0_species_representative_proteins',
        synthetic_reference=engineering,target='target',tree='tree.json',files=files)
    write_json(root/'database.json',manifest)
    write_json(root/'completed.json',dict(status='PASS',archive=binding(archive),archive_md5=md5.hexdigest(),
        taxonomy=[binding(p)for p in taxonomy_files],member_inventory=binding(root/'members.jsonl'),proteins=count,
        reference_genomes=len(genomes),amino_acids=residues,converted_FASTA_bytes=converted,database=binding(root/'database.json'),
        source_map=binding(root/'reference-sources.tsv'),engineering=engineering,community_or_truth_accessed=False))
    return manifest
