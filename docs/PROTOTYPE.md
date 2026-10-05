# First binner prototype

This experimental package implements our own composition-based contrastive
encoder, checkpoint inference, fixed clustering and complete FASTA/assignment
export. It is development software, not validated whole-MAG recovery or a
published release. [D011](decisions/D011-first-binner-prototype.md) owns the design;
[E004](../experiments/E004-first-binner/README.md) owns integration evidence.

Install into a separate Python 3.10 environment with the pinned local requirements,
then `python -m pip install --no-deps --no-build-isolation .`. The executable is
`dl-binner`; `python -m dl_binner` provides the same CLI. Keep numerical stages
serial within four CPU threads. A Linux recipe must select CPU PyTorch wheels
explicitly and pass native checks before owner execution; local installation
does not validate that recipe. [E005](../experiments/E005-linux-pilot/OPERATIONS.md)
has accepted the checksum-bound native CPU/Linux smoke and prepares one bounded
GI pilot. Its protocol preserves shorter
contigs and requires depth from that exact reference, never fabricated missing rows.

The first actual local integration is accepted in E004: a frozen installed wheel
trained and exported bins, checkpoint reload matched exactly, and the raw control
matched E003. Grouping improved while short-neighbor purity/precision declined.
This is working experimental software, not an established improvement in MAG
recovery. The measured demo used sequence only; optional depth has native contract
tests but no biological coverage result yet.

Commands are `prepare`, `train`, `embed`, `cluster`, and `export`, with `--help`
on each. `prepare` reads assembly FASTA and optional mean-depth TSV. Its header is
`contig_id` followed by unique ordered sample names. Every FASTA ID needs one
nonnegative finite depth row; row order may vary, but extra/missing IDs fail.
Absent depth is explicit sequence-only mode. Zero depth remains an observation,
with original masks retained. Sample-column order must match the checkpoint at
inference. Full IUPAC DNA is accepted; ambiguous fourmers do not supply TNF counts.
Matching table IDs verifies the input axis, not read-mapping provenance: depth
must originate from this assembly, with reference/alignment hashes recorded in
the pilot. Coverage's biological value has not been established here.

The default length cutoff is configurable 500 bp. Every original ID remains in
the outputs, including excluded short/zero-evidence contigs and cluster noise.
Training uses only eligible data, without labels. It fits and saves transforms;
inference reuses them without refitting. Different contigs are in-batch negatives
and may be co-genomic: this false-negative assumption is explicit and unproven.

Export writes `assignments.tsv`, bin FASTAs, `unassigned.fna`, `excluded.fna` and
a byte-bound manifest. Each input contig appears in exactly one exported FASTA.
Output paths must be fresh; no command silently overwrites an accepted artifact.
Feature/cache/embedding manifests bind ordered IDs, DNA, arrays and parents.
Checkpoints contain tensor state and fitted transforms and use restricted
`weights_only=True` loading. They must still come from a trusted provenance.

Fixed clustering uses exact cosine neighbors, positive mutual five-neighbor
edges, NetworkX greedy weighted modularity at resolution one, and minimum
community size three. It never receives a genome count or truth. Exact neighbor
queries are blocked to bound matrix memory, but greedy modularity is not yet
benchmarked at assembly scale. Retain the raw-feature control; declining training
loss alone does not establish useful bins.
