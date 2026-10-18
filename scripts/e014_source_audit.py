#!/usr/bin/env python3
"""Stream the approved source archive and independently check corrected GSA loci.

Never extract a reference collection or alter the first provisional SQLite audit.
Only one FASTA member is resident. Full record inventories, raw/deduplicated
denominators and exact competitors are retained; these do not assert unique near-
homology truth, biological plasmid hosts or admission of an evaluation adapter.
"""
import argparse
from collections import Counter, defaultdict
import hashlib
import io
import json
from pathlib import Path, PurePosixPath
import sqlite3
import sys
import tarfile
import time

sys.path.insert(0, str(Path(__file__).absolute().parent))
from e014_acquire import ROOT, guard, hashes
from e014_oral_audit import DNA


def records(raw):
    """Parse full headers and exact uppercase source DNA, refusing malformed input."""
    name = None
    chunks = []
    for line in io.StringIO(raw.decode('ascii')):
        line = line.strip()
        if not line:
            continue
        if line.startswith('>'):
            if name is not None:
                yield name, ''.join(chunks)
            if not line[1:].split():
                raise ValueError('Missing source FASTA identifier')
            name, chunks = line[1:], []
        else:
            if name is None or set(line.upper()) - DNA:
                raise ValueError('Invalid source DNA/header')
            chunks.append(line.upper())
    if name is None:
        raise ValueError('Empty source FASTA')
    yield name, ''.join(chunks)


def verify_locus(dna, start, end, expected):
    """Require exact one-based inclusive sequence identity; no clipped coordinates."""
    if not 1 <= start <= end <= len(dna):
        raise ValueError('Provided source coordinate outside complete record')
    actual = hashlib.sha256(dna[start-1:end].encode()).hexdigest()
    if actual != expected:
        raise ValueError('Provided GSA/source substring DNA differs')


def read_member(archive, member, in_memory, maximum=256*1024**2):
    """Hash every regular member; only needed small source/metadata bytes enter RAM.

    Setup also contains an unrelated 924-MB compressed pooled GSA. It is hashed
    as opaque archive content, never decompressed, extracted or used as truth.
    Source FASTAs still have an explicit in-memory size refusal.
    """
    if not member.isfile():raise ValueError('Unsupported nonregular source member: '+member.name)
    if in_memory and member.size>maximum:raise ValueError('Oversized in-memory source member: '+member.name)
    stream=archive.extractfile(member);sha=hashlib.sha256();n=0;chunks=[]
    for block in iter(lambda:stream.read(1024**2),b''):
        sha.update(block);n+=len(block)
        if in_memory:chunks.append(block)
    if n!=member.size:raise ValueError('Truncated source member')
    return (b''.join(chunks) if in_memory else None),dict(member=member.name,bytes=n,sha256=sha.hexdigest())


def audit(root=ROOT, e009_catalog=None, clock_path=None, output_name='source-validation-v1'):
    """Bind the complete archive, metadata and all indexed GSA intervals without fits."""
    root = Path(root)
    clock = json.loads(Path(clock_path or root/'acquisition-clock.json').read_text())
    guard(root, clock)
    receipt = json.loads((root/'source-acquisition.json').read_text())
    item = receipt['files'][0]
    if receipt['status'] != 'SUCCESS' or hashes(item['path']) != item['hashes']:
        raise ValueError('Full source acquisition bytes/receipt differ')
    prior = root/'admission-v1'
    review = json.loads((prior/'review.json').read_text())
    if review['fixed_unmatched'] or review['supplied_GSA'].get('unresolved_source_join_contigs', 0):
        raise ValueError('Prior sequence joins are unresolved')
    db = sqlite3.connect((prior/'joins.sqlite').absolute().as_uri()+'?mode=ro', uri=True)
    db.execute('PRAGMA cache_size=-32768')
    sources = dict(line.split('\t', 1) for line in (root/'metadata/setup-genome_to_id.tsv').read_text().splitlines())
    by_name = defaultdict(list)
    for genome, path in sources.items():
        by_name[Path(path).name].append(genome)
    if Path(output_name).name!=output_name:raise ValueError('Source audit output must be a fresh local basename')
    out = root/output_name
    out.mkdir(exist_ok=False)
    inventory, refs, totals, members = [], [], {}, set()
    checked, metadata_checked = Counter(), []
    records_seen = set()
    started = time.monotonic()
    complete_sources = set()
    complement = str.maketrans('ACGTRYSWKMBDHVN', 'TGCAYRSWMKVHDBN')
    with tarfile.open(item['path'], 'r|gz') as archive:
        for member in archive:
            name = PurePosixPath(member.name)
            if name.is_absolute() or '..' in name.parts or member.name in members or member.issym() or member.islnk():
                raise ValueError('Unsafe/duplicate source archive member')
            members.add(member.name)
            if member.isdir():
                continue
            metadata_path = root/'metadata'/('setup-'+member.name)
            raw,bound=read_member(archive,member,name.name in by_name or metadata_path.is_file())
            inventory.append(bound)
            if metadata_path.is_file():
                if metadata_path.read_bytes() != raw:
                    raise ValueError('Complete source metadata differs from earlier bounded prefix')
                metadata_checked.append(member.name)
            if name.name not in by_name:
                continue
            if name.name in complete_sources:
                raise ValueError('Duplicate provided source basename')
            complete_sources.add(name.name)
            genomes = by_name[name.name]
            local = []
            for header, dna in records(raw):
                record = header.split()[0]
                if not dna or (name.name, record) in records_seen:
                    raise ValueError('Empty/duplicate source record ID')
                records_seen.add((name.name, record))
                sha = hashlib.sha256(dna.encode()).hexdigest()
                # Match E009's frozen canonical_dna writer: choose the lexical
                # sequence first, then hash, rather than taking a minimum hash.
                reverse = dna.translate(complement)[::-1]
                canonical = hashlib.sha256(min(dna, reverse).encode()).hexdigest()
                lower = header.lower()
                molecule = ('plasmid' if 'plasmid' in lower else 'chromosome' if 'chromosome' in lower else 'unannotated')
                refs.append(dict(genomes=genomes, source=name.name, record=record, header=header,
                    bp=len(dna), sha256=sha, canonical_sha256=canonical,
                    ambiguous_bp=sum(dna.count(c) for c in DNA-set('ACGT')),
                    molecule_header_evidence=molecule, host='not inferred'))
                local.append((canonical, len(dna)))
                for anon, genome, start, end, expected in db.execute(
                    'SELECT anon,genome,start,end,sha FROM fixed WHERE record=?', (record,)):
                    if genome not in genomes:
                        continue
                    verify_locus(dna, start, end, expected)
                    checked[genome] += 1
            unique = dict(local)
            for genome in genomes:
                totals[genome] = dict(raw_bp=sum(n for _, n in local), records=len(local),
                    exact_DNA_deduplicated_bp=sum(unique.values()), exact_DNA_records=len(unique),
                    source=name.name, duplicate_policy='both lengths retained; biological equivalence not inferred')
            if len(complete_sources) % 20 == 0:
                guard(root, clock)
                print('SOURCE_FILES', len(complete_sources), 'VERIFIED_GSA_LOCI', sum(checked.values()), flush=True)
    if complete_sources != set(by_name) or set(totals) != set(sources):
        raise ValueError('Complete archive does not cover the provided source axis')
    expected = dict(db.execute('SELECT genome,count(*) FROM fixed GROUP BY genome'))
    if dict(checked) != expected or sum(checked.values()) != review['fixed_rows']:
        raise ValueError('Not every corrected GSA locus has exactly one source-sequence verification')
    db.close()
    by_dna, by_record = defaultdict(list), defaultdict(list)
    for r in refs:
        by_dna[r['canonical_sha256']].append(dict(genomes=r['genomes'], record=r['record'], bp=r['bp']))
        by_record[r['record']].append(dict(genomes=r['genomes'], sha256=r['sha256']))
    e009_path = Path(e009_catalog) if e009_catalog else Path(__file__).absolute().parents[1]/'artifacts/e009-gcp-data/20261014/preflight/source-catalog.json'
    e009 = json.loads(e009_path.read_text())
    e009_hashes = {r['canonical_sha256'] for f in e009['files'] for r in f['replicons']}
    e009_accessions = {a for f in e009['files'] for r in f['replicons'] for a in r['accessions']}
    overlaps = [dict(genomes=r['genomes'], record=r['record'], bp=r['bp'],
                     exact_canonical_DNA=r['canonical_sha256'] in e009_hashes,
                     accession=r['record'] in e009_accessions)
                for r in refs if r['canonical_sha256'] in e009_hashes or r['record'] in e009_accessions]
    duplicates = [rows for rows in by_dna.values() if len(rows)>1]
    conflicts = [dict(record=k, rows=v) for k,v in by_record.items() if len({r['sha256'] for r in v})>1]
    result = dict(status='SOURCE_VALIDATED_TRUTH_STILL_PROVISIONAL',
        archive=item, archive_members=len(inventory), provided_genomes=len(totals),
        source_records=len(refs), provided_reference_raw_bp=sum(v['raw_bp'] for v in totals.values()),
        verified_GSA_loci=sum(checked.values()), verified_GSA_bp=review['supplied_GSA']['bp'],
        metadata_prefix_members_exact=metadata_checked, exact_duplicate_record_groups=duplicates,
        conflicting_record_IDs=conflicts, E009_overlap_catalog=dict(path=str(e009_path),hashes=hashes(e009_path)),
        exact_DNA_or_accession_overlap_with_E009=overlaps,
        molecule_header_counts=dict(Counter(r['molecule_header_evidence'] for r in refs)),
        unresolved=['Near homology/competitive-origin ambiguity has not been exhaustively localized; exact hashes/accessions are not a near-overlap proof.',
                    'Source FASTA headers do not provide a complete molecule/host annotation inventory; retain provided assembly grouping and unknown annotations.',
                    'A source-blind model-input derivative, duplicate-safe union evaluator and independently reviewed truth admission are still required.'],
        seconds=time.monotonic()-started, validation_clock=clock,
        original_acquisition_clock=json.loads((root/'acquisition-clock.json').read_text()),
        scope='Exact publisher origin and full reference inventory, not admitted unique-alignment truth or a changed community score.')
    for name, value in [('members.json',inventory),('references.json',refs),('denominators.json',totals),('review.json',result)]:
        (out/name).write_text(json.dumps(value,indent=2,sort_keys=True)+'\n')
    guard(root,clock)
    print('SOURCE_VALIDATED', len(totals), len(refs), sum(checked.values()), flush=True)
    return result


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root', type=Path, default=ROOT)
    p.add_argument('--clock',type=Path,help='Explicit recorded repair clock; original attempt is preserved')
    p.add_argument('--output-name',default='source-validation-v1')
    a=p.parse_args();audit(a.root,clock_path=a.clock,output_name=a.output_name)
