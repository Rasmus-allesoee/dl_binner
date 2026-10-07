"""Deterministic synthetic software inputs; no genomes, labels or quality scores."""
from pathlib import Path
import os
import random

LENGTHS = (180, 499, 500, 767, 768, 999, 1000, 2499, 2500, 9999, 10000, 12000)
THREADS = int(os.environ.get('DL_BINNER_TEST_THREADS', '4'))
if not 1 <= THREADS <= 4:
    raise ValueError('DL_BINNER_TEST_THREADS must be between one and four')


def write_fixture(folder):
    """Write 13 bounded contigs and reverse-row synthetic depth with zero masks."""
    folder = Path(folder); folder.mkdir(parents=True, exist_ok=True)
    rng = random.Random(107)
    rows = [(f'software_{i:02d}_{bp}', ''.join(rng.choice('ACGT') for _ in range(bp)))
            for i, bp in enumerate(LENGTHS)]
    # Reader accepts the full IUPAC alphabet; ambiguity does not supply fourmers.
    ident, dna = rows[4]; rows[4] = (ident, 'RYSWKMBDHVN'+dna[11:])
    rows.append(('ambiguity_mask', 'N'*600))
    assert len(rows) <= 32 and sum(len(s) for _,s in rows) <= 600000
    fasta = folder/'assembly.fna'
    fasta.write_text(''.join(f'>{i}\n{s}\n' for i,s in rows))
    depth = folder/'mean-depth.tsv'
    values = {i: (0,0) if j in (0,6,12) else (j%4, (j*3)%5) for j,(i,_) in enumerate(rows)}
    depth.write_text('contig_id\tsoftware_S1\tsoftware_S2\n'+''.join(
        f'{i}\t{values[i][0]}\t{values[i][1]}\n' for i,_ in reversed(rows)))
    return fasta, depth, rows
