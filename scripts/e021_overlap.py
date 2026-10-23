#!/usr/bin/env python3
"""Bounded shared-sequence warning screen against retained oral reference DNA.

No ANI, alignment, source acquisition, feature use or uniqueness/absence claim.
The content-anchored sketch is intentionally a cheap positive screen only.
"""
import argparse
from collections import Counter,defaultdict
import json,sys,tarfile
from pathlib import Path
sys.path.insert(0,str(Path(__file__).absolute().parent))
from e021_skin import HashReader,sketch,write
from e021_acquire import guard,hashes
from e014_source_audit import records,read_member


def run(root,repo):
    """Read each old source record once, verify its accepted DNA, screen all new refs."""
    root,repo=Path(root),Path(repo);clock=json.loads((root/'acquisition-clock.json').read_text());guard(root,clock)
    oldroot=repo/'artifacts/e014-multiview-reconstruction';acq=json.loads((oldroot/'source-acquisition.json').read_text());item=acq['files'][0]
    if not Path(item['path']).is_file():raise ValueError('Retained source archive missing; no acquisition fallback')
    old=json.loads((oldroot/'source-validation-v2/references.json').read_text());wanted=defaultdict(dict)
    for row in old:wanted[row['source']][row['record']]=row
    new=json.loads((root/'admission-v2/references.json').read_text());oldsk=[];seen=set()
    with open(item['path'],'rb')as f:
        reader=HashReader(f)
        with tarfile.open(fileobj=reader,mode='r|gz')as t:
            for m in t:
                if m.isdir():continue
                name=Path(m.name).name;raw,b=read_member(t,m,name in wanted)
                if name not in wanted:continue
                for header,dna in records(raw):
                    import hashlib
                    ident=header.split()[0];record=wanted[name].get(ident)
                    if record is None or hashlib.sha256(dna.encode()).hexdigest()!=record['sha256']:raise ValueError('Retained oral source bytes/record differ')
                    if(name,ident)in seen:raise ValueError('Duplicate retained source record')
                    seen.add((name,ident));oldsk.append(dict(source=name,record=ident,canonical_sha256=record['canonical_sha256'],genomes=record['genomes'],sketch=sketch(dna)))
                if len(seen)%50==0:guard(root,clock);print('OLD_ORAL_SCREEN_RECORDS',len(seen),flush=True)
        while reader.read(1024**2):pass
        if reader.result()!=item['hashes']:raise ValueError('Complete old reference archive hash differs')
    if len(seen)!=len(old):raise ValueError('Incomplete old reference axis')
    inverted=defaultdict(list)
    for j,row in enumerate(oldsk):
        for h in row['sketch']:inverted[h].append(j)
    hits=[]
    for row in new:
        common=Counter(j for h in row['anchored32_sketch']for j in inverted.get(h,[]))
        ranked=[]
        for j,n in common.items():
            oldrow=oldsk[j];den=len(row['anchored32_sketch'])+len(oldrow['sketch'])-n
            ranked.append(dict(source=oldrow['source'],record=oldrow['record'],genomes=oldrow['genomes'],shared_anchor_hashes=n,sketch_Jaccard=n/den if den else 0,exact_canonical_DNA=row['canonical_sha256']==oldrow['canonical_sha256']))
        ranked.sort(key=lambda z:(-z['sketch_Jaccard'],-z['shared_anchor_hashes'],z['source'],z['record']))
        if ranked:hits.append(dict(source=row['source'],record=row['record'],genomes=row['genomes'],top3=ranked[:3]))
    result=dict(status='BOUNDED_POSITIVE_SHARED_SEQUENCE_SCREEN_ONLY',skin_source_records=len(new),oral_source_records=len(oldsk),skin_records_with_anchor_match=len(hits),skin_records_with_nonexact_anchor_match=sum(any(not h['exact_canonical_DNA']for h in z['top3'])for z in hits),algorithm='Bottom 128 SHA256-64 hashes of canonical 32-mers around palindromic ACGCGT anchors; fixed before screen, motif biased, no ANI/absence/unique-support claim.',top_matches=hits,source_archive=item['hashes'],unresolved=['No exhaustive near-homology localization or calibrated ANI.','E009 complete source DNA is not present in this local audit; exact source hashes/accessions do not exclude near overlap.','Complete historical GLM pretraining inventory unavailable; no unseen-genome claim.'],scope='Admission/audit only; no training, K, threshold, bin or candidate choice uses these labels/hits.')
    write(root/'overlap-screen.json',result);guard(root,clock);print('SHARED_SEQUENCE_SCREEN_COMPLETE',len(oldsk),len(hits),flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--root',type=Path,required=True);p.add_argument('--repo',type=Path,default=Path(__file__).absolute().parents[1]);a=p.parse_args();run(a.root,a.repo)
