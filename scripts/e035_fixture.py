#!/usr/bin/env python3
"""Own synthetic reference engineering for actual native taxonomy classification.

Proteins are translations of the fixture DNA. Synthetic taxa deliberately have
no connection to CAMI/source genomes. This establishes parser/command mechanics,
not reference coverage, taxonomic accuracy or a community result.
"""
import hashlib
import json
from pathlib import Path


def tree():
    """Return two synthetic genera with two species each under a full rank path."""
    from dl_binner.taxonomy.tree import Tree, RANKS
    nodes=[dict(id=0,parent=0,rank='no rank',name='unclassified'),dict(id=1,parent=1,rank='no rank',name='root')]
    parent=1
    for rank in RANKS[:5]:
        i=len(nodes);nodes.append(dict(id=i,parent=parent,rank=rank,name='Fixture_'+rank));parent=i
    leaves=[]
    for g in range(2):
        i=len(nodes);nodes.append(dict(id=i,parent=parent,rank='genus',name='Fixture_genus_'+str(g)))
        for s in range(2):
            j=len(nodes);nodes.append(dict(id=j,parent=i,rank='species',name='Fixture_species_%s_%s'%(g,s)));leaves.append(j)
    return Tree(nodes),leaves


def reference(binary, fasta, output):
    """Create an actual native protein/taxonomy DB from a small generated FASTA."""
    from dl_binner.io import read_fasta, write_json
    from dl_binner.context.tokens import binding
    from dl_binner.taxonomy.classifier import command
    root=Path(output);root.mkdir(parents=True,exist_ok=False);t,leaves=tree();t.save(root/'tree.json')
    dump=root/'dump';dump.mkdir()
    (dump/'nodes.dmp').write_text(''.join(f"{r['id']}\t|\t{r['parent']}\t|\t{r['rank']}\t|\t\t|\t0\t|\t0\t|\t11\t|\t0\t|\t0\t|\t0\t|\t0\t|\t0\t|\t\t|\n" for r in t.nodes[1:]))
    (dump/'names.dmp').write_text(''.join(f"{r['id']}\t|\t{r['name']}\t|\t\t|\tscientific name\t|\n" for r in t.nodes[1:]));(dump/'merged.dmp').write_text('');(dump/'delnodes.dmp').write_text('')
    alphabet='TCAG';aas='FFLLSSSSYY**CC*WLLLLPPPPHHQQRRRRIIIMTTTTNNKKSSRRVVVVAAAADDEEGGGG'
    codons={a+b+c:v for v,(a,b,c) in zip(aas,((a,b,c)for a in alphabet for b in alphabet for c in alphabet))}
    seen=set();count=0
    with (root/'proteins.faa').open('x')as out,(root/'mapping.tsv').open('x')as mapping:
        for ident,dna in read_fasta(fasta):
            if dna in seen:continue
            seen.add(dna);taxid=leaves[int(hashlib.sha256(dna.encode()).hexdigest()[:8],16)%4]
            reverse=dna.translate(str.maketrans('ACGT','TGCA'))[::-1]
            for sequence in [dna,reverse]:
                for frame in range(3):
                    aa=''.join(codons.get(sequence[i:i+3],'*')for i in range(frame,len(sequence)-2,3))
                    for fragment in aa.split('*'):
                        if len(fragment)<30:continue
                        q='r%08d'%count;count+=1;out.write('>'+q+'\n'+fragment+'\n');mapping.write(q+'\t'+str(taxid)+'\n')
    if not count:raise ValueError('Fixture lacks native searchable ORFs')
    command(binary,['createdb',root/'proteins.faa',root/'target','--dbtype','1','--shuffle','0','--threads','4'],root,'createdb')
    command(binary,['createtaxdb',root/'target',root/'tmp','--ncbi-tax-dump',dump,'--tax-mapping-file',root/'mapping.tsv','--threads','4'],root,'createtaxdb')
    members={str(p.relative_to(root)):binding(p)for p in root.iterdir()if p.is_file()and (p.name.startswith('target')or p.name=='tree.json')}
    manifest=dict(kind='independent_taxonomy_database',version=1,binary=binding(binary),release='own_synthetic_reference',synthetic_reference=True,target='target',tree='tree.json',files=members)
    write_json(root/'database.json',manifest);return root/'database.json'
