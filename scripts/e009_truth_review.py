#!/usr/bin/env python3
"""Independently review a fresh E009 truth artifact without running its derivation.

Use a separate PAF reader and direct interval clipping, not the production parser,
canonical splitter or sweep. Check every serialized contig and full target axis;
recount all ambiguous/circular queries and a deterministic SHA256 query sample
against raw PAFs. Admission is a separate maintained research decision.
"""
import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import re
import sys
sys.path.insert(0,str(Path(__file__).absolute().parent))
from e009_common import binding, fasta, write_json


def merged(spans):
    """Independently merge bounded source intervals for the review oracle."""
    result=[]
    for a,b in sorted(spans):
        if result and a <= result[-1][1]:result[-1][1]=max(b,result[-1][1])
        else:result.append([a,b])
    return result


def oracle(length, rows, aliases, identity, min_bp, attribution):
    """Resolve raw-chain overlaps by direct clipping, independent of canonical splitting.

    Keep alias coordinates until each overlap is clipped. Split at every physical
    circular-origin crossing using query coordinates, then compare one-base locus
    maps and emit their interval union. Opposite orientation remains unresolved.
    """
    pieces=[];vetoes=[];bounds={0,length}
    for f,ops,nn in rows:
        qs,qe=int(f[2]),int(f[3]);rid=f[5];r=int(f[7]);strand=f[4]
        if sum(n for n,o in ops if o in '=X') < min_bp or int(f[9])/int(f[10]) < identity:continue
        if nn:
            vetoes.append((qs,qe));bounds.update((qs,qe));continue
        q=qs if strand=='+'else qe
        for n,o in ops:
            if o in '=X':
                a,b=(q,q+n)if strand=='+'else(q-n,q);alias=aliases[rid]
                pieces.append((a,b,r,rid,strand));bounds.update((a,b))
                wrap=alias['length']-((r+alias['offset'])%alias['length'])
                if wrap<n:bounds.add(a+wrap if strand=='+'else b-wrap)
                q+=n if strand=='+'else -n;r+=n
            elif o=='I':q+=n if strand=='+'else -n
            else:r+=n
    support=Counter();loci=defaultdict(list);ambiguous=repeat=quarantine=0
    points=sorted(bounds)
    for a,b in zip(points,points[1:]):
        if any(x<=a and b<=y for x,y in vetoes):quarantine+=b-a;continue
        active=[p for p in pieces if p[0]<=a and b<=p[1]]
        gs={aliases[p[3]]['genome']for p in active}
        if len(gs)>1:ambiguous+=b-a;continue
        if not gs:continue
        support[next(iter(gs))]+=b-a;locations=set()
        for x,y,r,rid,strand in active:
            alias=aliases[rid];size=alias['length']
            # Compare the mapping of the first query base plus orientation.
            local=r+a-x if strand=='+'else r+y-1-a
            pos=(local+alias['offset'])%size
            locations.add((alias['canonical_id'],pos,strand))
        if len(locations)>1:repeat+=b-a;continue
        rid,pos,strand=next(iter(locations))
        left,right=(pos,pos+b-a)if strand=='+'else(pos-(b-a)+1,pos+1)
        assert 0 <= left < right <= aliases[active[0][3]]['length']
        loci[rid].append([left,right])
    best=sorted(support,key=lambda g:(-support[g],g))
    return {'length':length,'confirmed_query_bp':dict(support),'ambiguous_query_bp':ambiguous,
            'nn_quarantined_query_bp':quarantine,'repeat_locus_query_bp':repeat,
            'unsupported_query_bp':length-sum(support.values())-ambiguous-quarantine,
            'source_intervals':{r:merged(v)for r,v in loci.items()},
            'AMBER_label':best[0]if best and support[best[0]]/length>=attribution else None,
            'multiple_confirmed_genomes':len(support)>1}


def review(root, artifact, population_path, expected_path, output):
    """Review manifest bytes, exact axes, whole-population invariants and raw-chain oracle."""
    root,artifact=Path(root),Path(artifact)
    load=lambda p:json.loads(Path(p).read_text())
    manifest=load(artifact/'manifest.json')
    if set(p.name for p in artifact.iterdir()) != {*manifest['files'],'manifest.json'}:raise ValueError('Truth artifact file set drift')
    for name,expected in manifest['files'].items():
        if Path(name).name!=name or binding(artifact/name)!=expected:raise ValueError('Truth artifact bytes drift')
    expected=load(expected_path)['files']
    if manifest['inputs']!=expected:raise ValueError('Frozen truth inputs drift')
    for name,expected_record in expected.items():
        if name.startswith('$'):continue
        if binding(root/name)!=expected_record:raise ValueError('Retained input bytes drift')
    if binding(population_path)!=expected['$population']:raise ValueError('Population drift')
    truth=load(artifact/'truth.json');mapping=load(artifact/'reference-map.json');targets=load(artifact/'targets.json')
    policy_path=Path(expected_path).with_name('truth-v2-policy.json')
    if binding(policy_path)!=expected['$policy']or truth['policy']!=load(policy_path):
        raise ValueError('Predeclared truth policy differs')
    pop=load(population_path);aliases=mapping['aliases'];refs=truth['reference_axis'];genomes=mapping['genomes']
    if refs!=mapping['canonical_references']:raise ValueError('Two canonical reference axes disagree')
    original=load(root/'data-stage-v1/parts/sources/reference.fna.axis.json')['reference_axis']
    catalog={v['name']:v for v in load(root/'data-stage-v1/parts/sources/catalog.json')['files']}
    if set(aliases)!=set(original):raise ValueError('Missing competitive alias')
    files_to_gid={n:g for g,v in pop['genomes'].items()for n in v['source_files']}
    expected_ref={};circular_records=0
    circular={v['file']:v for v in mapping['circular']}
    for name,item in circular.items():
        dna=list(fasta(root/'data-stage-v1/parts/sources/unpacked/source_genomes'/name))
        base=dna[0][1]
        if binding(root/'data-stage-v1/parts/sources/unpacked/source_genomes'/name)!=catalog[name]['file']:raise ValueError('Circular bytes differ')
        for ident,seq in dna:
            off=item['offsets'][ident]
            if seq!=base[off:]+base[:off] or len(seq)!=len(base):raise ValueError('Bad circular offset')
    for rid,old in original.items():
        new=aliases[rid];name=old['genome'];gid=files_to_gid.get(name,'zero_origin::'+name)
        if new['genome']!=gid or new['length']!=old['length'] or new['original_replicon_id']!=old['original_replicon_id']:
            raise ValueError('Simulator genome/alias relation differs')
        cid=new['canonical_id']
        if name in circular:
            c=circular[name];circular_records+=1
            if cid!=c['canonical_id']or new['offset']!=c['offsets'][old['original_replicon_id']]:raise ValueError('Circular alias drift')
            expected_ref[cid]=(gid,old['length'])
        else:
            if cid!=rid or new['offset']!=0:raise ValueError('Unexpected alias collapse')
            expected_ref[rid]=(gid,old['length'])
    if {r:(v['genome'],v['length'])for r,v in refs.items()}!=expected_ref:raise ValueError('Canonical reference universe mismatch')
    lengths=Counter()
    for v in refs.values():lengths[v['genome']]+=v['length']
    if dict(lengths)!=targets['genome_lengths']:raise ValueError('Incomplete provided denominators')
    eligible=[]
    for gid,p in pop['genomes'].items():
        if lengths[gid]!=p['one_copy_provided_bp'] or genomes[gid]['HOST']!=p['HOST']:raise ValueError('Population denominator/HOST mismatch')
        if p['lineage_class']in('bacterial','archaeal')and p['positive_read_records']>0 and lengths[gid]>=200000:eligible.append(gid)
    if targets['targets']!=sorted(eligible) or set(targets['non_targets'])!=set(lengths)-set(eligible):raise ValueError('Primary target eligibility differs')
    query={q:len(s)for q,s in fasta(root/'data-stage-v1/parts/assembly/megahit/final.contigs.fa')}
    if truth['ordered_contig_ids']!=list(query)or set(truth['contigs'])!=set(query):raise ValueError('Full assembly axis mismatch')
    totals=Counter();labels={}
    for q,n in query.items():
        v=truth['contigs'][q];support=v['confirmed_query_bp']
        parts=[sum(support.values()),v['ambiguous_query_bp'],v['nn_quarantined_query_bp'],v['unsupported_query_bp']]
        if v['length']!=n or sum(parts)!=n or min(parts)<0 or any(b<=0 for b in support.values()):raise ValueError('Query DNA accounting differs')
        if set(support)-set(lengths)or v['repeat_locus_query_bp']>sum(support.values()):raise ValueError('Invalid genome support')
        expected_label=next((g for g,b in support.items()if b/n>=.95),None)
        if v['AMBER_label']!=expected_label:raise ValueError('Contig attribution differs')
        if expected_label:labels[q]=(expected_label,n)
        locus_bp=0
        for r,spans in v['source_intervals'].items():
            if r not in refs or spans!=merged(spans):raise ValueError('Invalid source interval union')
            if any(not 0<=a<b<=refs[r]['length']for a,b in spans):raise ValueError('Source interval out of bounds')
            if refs[r]['genome']not in support:raise ValueError('Locus lacks genome support')
            locus_bp+=sum(b-a for a,b in spans)
        if locus_bp>sum(support.values())-v['repeat_locus_query_bp']:raise ValueError('Locus support exceeds unique query support')
        totals.update(dict(zip(['confirmed','ambiguous','nn_quarantined','unsupported'],parts)))
    amber={}
    for line in (artifact/'AMBER-truth.tsv').read_text().splitlines():
        if line.startswith('@'):continue
        q,g,n=line.split('\t')
        if q in amber:raise ValueError('Duplicate AMBER label')
        amber[q]=(g,int(n))
    if amber!=labels:raise ValueError('AMBER view differs')
    chosen=set(sorted(query,key=lambda q:hashlib.sha256(q.encode()).digest())[:128]);raw_rows=defaultdict(list)
    flagged=set();counts=Counter()
    with (root/'data-stage-v1/parts/final/all_competing_chains.paf').open()as stream:
        for raw in stream:
            f=raw.rstrip('\n').split('\t');tags={t.split(':',2)[0]:t.split(':',2)[2]for t in f[12:]}
            ops=[(int(n),o)for n,o in re.findall(r'(\d+)([=XID])',tags['cg'])];nn=int(tags['nn'])
            # Independently recount native columns/matches, without production helpers.
            op_counts=Counter()
            for n,o in ops:op_counts[o]+=n
            if sum(op_counts.values())!=int(f[10])+nn or not 0<=op_counts['=']-int(f[9])<=nn:raise ValueError('Native count recount differs')
            counts['rows']+=1;counts['nn_rows']+=bool(nn)
            qualifies=sum(n for n,o in ops if o in '=X')>=200 and int(f[9])/int(f[10])>=.99
            if qualifies:counts['qualifying_rows']+=1
            if nn or original[f[5]]['genome']in circular:flagged.add(f[0])
            # Store all rows once; flagged queries are discovered throughout the file.
            raw_rows[f[0]].append((f,ops,nn))
    chosen.update(flagged)
    for i,q in enumerate(sorted(chosen),1):
        result=oracle(query[q],raw_rows[q],aliases,.99,200,.95)
        if result!=truth['contigs'][q]:raise ValueError('Independent raw-chain oracle differs: '+q)
        if i%100==0:print('REVIEW_ORACLE_QUERIES',i,flush=True)
    result={'status':'PASS','artifact_manifest':binding(artifact/'manifest.json'),'full_assembly_axis':len(query),
            'full_query_bp':sum(query.values()),'query_bp':dict(totals),'primary_targets':len(eligible),
            'full_primary_provided_bp':sum(lengths[g]for g in eligible),'positive_genomes':len(pop['genomes']),
            'zero_origin_competitors':sum(g.startswith('zero_origin::')for g in lengths),
            'canonical_references':len(refs),'competitive_alias_records':len(aliases),'circular_alias_records':circular_records,
            'native_row_recount':dict(counts),'independent_oracle_queries':len(chosen),
            'all_nn_or_circular_queries_reviewed':len(flagged),'deterministic_SHA256_sample_queries':128,
            'AMBER_labelled_contigs':len(labels),'AMBER_labelled_bp':sum(n for _,n in labels.values()),
            'no_binner_fits_scores_or_alignment':True,'admission_is_separate_owner_record':True}
    write_json(output,result);return result


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for n in ['root','artifact','population','input_manifest','output']:p.add_argument('--'+n.replace('_','-'),required=True,type=Path)
    a=p.parse_args();print(json.dumps(review(a.root,a.artifact,a.population,a.input_manifest,a.output),sort_keys=True))
