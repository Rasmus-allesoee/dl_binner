"""Generated DNA/HMM engineering fixtures; no research assets or biological claims."""
import hashlib
import json
from pathlib import Path

import numpy as np


def fixture(root):
    """Write six length strata, coding DNA, IUPAC/zero evidence and ordered depths."""
    rng = np.random.default_rng(71)
    codons = ['GCT','GAT','GAA','GGT','ATT','CTG','AAA','TTC','TAT','GTT','CCT','CAA','AGC','ACT']
    rows = []
    for i, n in enumerate([31, 499, 500, 767, 768, 999, 1000, 1999, 2000, 2499, 2500, 8000, 11000]):
        coding = 'AGGAGGAAAAAAATG'+''.join(rng.choice(codons, size=(n+2)//3))+'TAA'
        rows.append(('contig_opaque_'+str(i), (coding*3)[:n]))
    rows += [('no_composition', 'N'*2500), ('partial_ambiguity', 'ACGTRYSWKMBDHVN'*150)]
    fasta, depth = root/'assembly.fna', root/'depth.tsv'
    fasta.write_text(''.join('>'+i+'\n'+s+'\n' for i, s in rows))
    depth.write_text('contig_id\tZ-last\tA-first\n'+''.join(f'{ident}\t{i%3}\t{0 if i%4==0 else 8-i%3}\n' for i,(ident,_) in enumerate(reversed(rows))))
    return fasta, depth, rows


def asset(root, fasta):
    """Build a real HMM from one native called synthetic protein, with trusted scores."""
    import pyhmmer
    import pyrodigal
    from dl_binner.io import read_fasta
    from dl_binner.contracts import file_record
    caller = pyrodigal.GeneFinder(meta=True)
    proteins = [g.translate().rstrip('*') for _, dna in read_fasta(fasta)
                if len(dna) >= 90 for g in caller.find_genes(dna.encode())]
    sequence = max(proteins, key=len)
    alphabet = pyhmmer.easel.Alphabet.amino()
    digital = pyhmmer.easel.TextSequence(name=b'own_synthetic_marker', sequence=sequence).digitize(alphabet)
    hmm, _, _ = pyhmmer.plan7.Builder(alphabet).build(digital, pyhmmer.plan7.Background(alphabet))
    hmm.name = b'engineering_marker'
    hmm.cutoffs.trusted = (20., 20.)
    profile = root/'engineering-marker.hmm'
    with profile.open('xb') as stream:
        hmm.write(stream)
    manifest = root/'asset.json'
    manifest.write_text(json.dumps(dict(version=1, kind='scg_profile_asset', hmm=file_record(profile),
        families={'engineering_marker':'engineering_marker'},
        source='Generated synthetic coding DNA / native Pyrodigal / PyHMMER single-sequence builder',
        license='Own generated engineering fixture, not a biological SCG panel')))
    return profile, manifest


def tiny_config(path):
    """Reduce only engineering workload, never use this as the community schedule."""
    from dl_binner.candidate.views import config
    cfg = config()
    cfg.update(epochs=2, batch_size=4, window_min=128, window_max=512,
               min_bin_bp=1, sequence_hidden=32, sequence_output=16,
               depth_hidden=8, fusion_hidden=16, output=8)
    path.write_text(json.dumps(cfg))
    return cfg
