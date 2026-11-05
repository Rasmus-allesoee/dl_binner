# E033: recovery evidence and the genome-graph priority

Reviewed November 5, 2026. Scope: interpret the completed frozen E033 bundle,
then choose one consequential next block. This is targeted primary-source review,
not execution of another tool or a claim that the proposed method will win.
[Completed review](../../experiments/E033-multiscale-bam/completed-review.md) owns
actual results; [source identities](../../experiments/E033-multiscale-bam/next-source-audit.json)
binds the newly inspected upstream files. Earlier completed reviews are reused,
particularly [standalone candidate/depth methods](2026-11-03-depth-and-standalone-candidate-audit.md)
and [multiscale measurement design](2026-11-04-multiscale-coverage-and-storage.md).

## What the completed evidence changes

E033 completes all six fits and delivery contracts. Its common newly measured
parent/crop information, reliability residual and learning adaptation loses
weighted R95 in all three modes against E032. Frozen disposition is ABANDON this
bundle; it is not an integrity refusal. Positive new pre/post recruitment effects
cannot rescue the between-bundle regressions. New measurements remain valuable
engineering assets and do not need to be repeated.

Oral loses 12 multi-contig T90 recoveries and one singleton T90, despite a slightly
larger singleton bp contribution. Saved unit embeddings are noncollapsed, and
sampled search recall is excellent. Yet Oral's full attributable same-origin 5NN
agreement remains about 26%; raw input on the fixed 128 queries is stronger than
learned input. Approximately 14.78% of resolved positive proposals cross provided
origins. E009 bacterial queries are much more homogeneous and do not support a
global rejection of learning. These distinguish meaningful information/
representation/global-construction uncertainty from a broken ANN or collapsed fit.

Interpretation: improving how fragments exchange genome-scale evidence is a
stronger next hypothesis than another coefficient sweep. It does not follow that
our global constructor is already correct. The E023/E030 exact-vector bridge and
E031 paired evidence already show that construction matters. Keep E032 provisional,
stronger E031 constructor contexts and E023 10.4163% visible; do not truth-route
one constructor per dataset. E032 exceeds the retained native MetaBAT2 reference
on both development communities, so “we trail all SOTA tools” is not an established
quantitative conclusion. We still lack a current stronger matched external panel
and independent confirmation. MAG recovery, not implementation complexity, is the
decision target.

## Primary method and source observations

**METAMVGL, Zhang and Zhang, 2021.** Its [paper, Methods → Construct PE graph](https://pmc.ncbi.nlm.nih.gov/articles/PMC8296540/)
uses aligned mate names to link distinct contigs, estimates insert size from
uniquely placed within-contig pairs, and requires concentration of paired support
to reduce chimeric links. Its graph is combined with assembly connectivity for
label propagation. This is precedent for physical evidence between fragments;
its reported gains are not our reproduced MAG results, and its species/contig
metrics differ from full-reference R95.

Inspected source is commit `14e513f0222745619894347565995b8ab13d4d6c`, not asserted
to be the paper's release. In
[`graph.cpp`](https://github.com/ZhangZhenmiao/METAMVGL/blob/14e513f0222745619894347565995b8ab13d4d6c/graph.cpp),
`load_ngs_alignment_megahit` indexes mate roles by QNAME and rejects secondary/
supplementary alignments. `construct_PE_overlap_athena` joins opposing mate roles
on different contigs and counts spatially concentrated support on both sides.
`main.cpp` defaults are MAPQ 10, identity 0.95, insert 270, minimum support 3.
The parser counts M/I/D, defaults missing NM to zero, and lacks our explicit
MAPQ-255/duplicate/QCFAIL policy in that function. Do not copy it as a safe
identity/uniqueness implementation. Its nested per-link support loops and in-memory
QNAME maps are also unsuitable defaults for an unbounded 20-BAM pipeline.

**GraphMB, Lamurias et al., 2022.** The [primary paper](https://academic.oup.com/bioinformatics/article/38/19/4481/6668279)
([PubMed abstract](https://pubmed.ncbi.nlm.nih.gov/35972375/)) learns contig features
with graph neural networks and assembly-edge coverage. Its evidence is primarily
long-read assemblies; it does not validate a paired-short-read graph on our Oral
GSA. We cannot manufacture an assembly GFA from simulator coordinates or assume a
GSA comes with the graph GraphMB needs.

Source commit `30cb2ded07531135a92ef0890cf1bf06fd28717e` is independently bound.
[`contigsdataset.py:read_gfa`](https://github.com/MicrobialDarkMatter/GraphMB/blob/30cb2ded07531135a92ef0890cf1bf06fd28717e/src/graphmb/contigsdataset.py)
maps GFA links to contig indices, symmetrizes edges, reads a link count when
available and otherwise uses unit weight. The sparse GCN/SAGE implementations in
[`gnn_models.py`](https://github.com/MicrobialDarkMatter/GraphMB/blob/30cb2ded07531135a92ef0890cf1bf06fd28717e/src/graphmb/gnn_models.py)
combine node features with graph aggregation. This supports a compact graph
representation as a coherent architecture option. Optional label/evaluation code
is not evidence that every path trains with taxonomy; our implementation must
exclude benchmark truth from every feature, edge, proposal and model input.
No upstream model, dependency or binner was installed or executed.

**Standalone construction alternatives remain serious.** Reuse the existing
source-bound COMEBin/SemiBin2/CompleteBin/SCGBinner/DCVBin/TaxVAMB audits rather
than restarting the landscape review. COMEBin's inspected final selector ranks
multiple clustering candidates using marker-quality counts and emits size-filtered
bins. SemiBin2's inspected `run_embed_infomap` uses contig-length vertex weights,
and its marker-seeded reclustering is a different candidate policy. These are
concrete alternatives to E032's proxy, not evidence that an ensemble-like count
rule or length weighting will necessarily improve our results. Q006 remains open.
A future direct selector comparison needs prospective common candidates and all
DNA/singleton/fragmented strata; it is not the default next serial tweak.

## Chosen next block and why

Choose **a BAM-supported genome-graph representation with frozen per-contig
bootstrap features**, conditional on actual reliable-link admission. Begin from
the preserved E031 common three-mode learning and provisional E032 constructor;
do not promote the weaker E033 learner. Reuse the admitted E033 measurement bank
as explicitly new measured context and keep the differently filtered inherited
E031 priors visible. Link evidence, available raw features and optional GLM are
separate channels with explicit absence/reliability. Freeze the graph policy,
compact encoder, objective and defaults before new community results.

The useful information is: two fragments can be physically adjacent even when
short-contig composition and relative abundance are inconclusive. An embedding
trained solely to agree with augmented versions of one contig or noisy marker
proposals does not observe that relationship. Confidence-gated message passing
can integrate it without hard-merging an entire connected component or changing
one dataset's defaults. It can also propagate a false edge, oversmooth strains or
have no effect when links are sparse; retain the unlinked fallback and all DNA.

This is **not** a presumption that retained BAMs contain enough informative links.
Short insert sizes, repeats, multi-mapping and GSA breaks can make support sparse
or misleading. Oral has only 31.78% high-MAPQ mass among accepted aligned bases;
a measured positive signal is not a unique physical link. The first native pilot
must measure useful support/connectivity, ambiguous-template rates, repeat hubs,
end/orientation evidence and full resource needs under a rule frozen without truth.
If the scientific/engineering gate fails, retain that result and revise the
information hypothesis before a community fit; never invent edges, parse simulator
IDs or lower a frozen quality gate. The pilot is not a cutoff grid or permission
to tune labels. Independent truth can later diagnose the fixed links/outputs.

Serious alternatives weighed:

- **Parent-mean-only E033 ablation:** cheaper causal localization of the regression,
  but by itself supplies no new genome-scale information or clear recovery route.
  Retain it for a decision that specifically needs that attribution.
- **Another global selector or density adjustment:** plausible, with prior exact-
  vector evidence, but E032 already protects many intact genomes and the strongest
  remaining Oral loss is fragmented. Keep Q006 and cheap paired partitions, rather
  than optimize several proxies against these same two communities by default.
- **A larger Transformer or another loss:** could improve representation, but
  model size alone does not add relationships between contigs; E033's noncollapsed
  representation and false proposals argue for better evidence first. The proposed
  compact graph model is itself a core representation upgrade, not cosmetic tuning.
- **Full Oral GLM:** high priority and complementary. It may improve sequence
  evidence, but the admitted E009 GLM path does not yet guarantee an R95 advantage,
  and capacity/throughput plus the missing explicit hybrid-state transition remain
  concrete blockers. Resolve that milestone in parallel preparation, without
  claiming it already passed or silently expanding the graph task to full extraction.
- **More data or an external-tool campaign:** needed for generalization/relative
  performance claims, but not a substitute for this diagnosed recovery block.
  Skin is already source/origin-admitted and unscored, with material source overlap;
  it is not automatically untouched unseen-genome confirmation.

Keep a common frozen version across E009 no-GLM, E009 GLM (including upstream
teacher/proposals where used), and Oral ten-depth no-GLM. Require full-reference
R95/T90 and multi-contig improvement against strong preserved comparators, with
purity, unassigned and non-target trade-offs exposed. One links-off matched control
is justified only if it can change whether physical links belong in the design;
no factorial campaign. Any future guarantee of better MAG recovery would outrun
current evidence: the rule is to implement a well-supported candidate and accept
it only if the prespecified recovery contracts pass.
