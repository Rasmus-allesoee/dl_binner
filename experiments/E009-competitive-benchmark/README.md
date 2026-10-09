# E009: first competitive human-gut assembly benchmark

Opened: 2026-10-08; amended 2026-10-09. Owner preflight: **prepared locally**, not launched. Scientific outcome:
**not assessed**. [D013](../../docs/decisions/D013-first-comparative-benchmark.md)
and the [focused study](../../docs/evidence/2026-10-08-competitive-binner-study.md)
own the rationale; [protocol.json](protocol.json) owns numerical scope/budgets.
The source/metadata [provenance](../../docs/evidence/2026-10-08-competitive-study-provenance.json)
is a reviewed planning snapshot, not an input/environment lock.

## Question and informative comparisons

How useful are our accepted raw and learned bins on a real read-derived
human-associated assembly, compared with a small native-tool shortlist, and
does the main deficit concern information, learned geometry or grouping?
No prior result establishes a globally poor or strong binner. Measure the gap.

Freeze our stable main source at `5e54538d1799e8d2538621729400f33fbaf017b9`
(dev3; normal prototype merge `5bc824a9bf4b1ca4562acda10735a3fc6b54dc3d`).
No model, fitted-transform procedure, training default or clusterer changes.
Run one seed-11 target-specific fit with its matched raw control for each of:

- TNF plus the same two explicitly observed mean-depth columns: primary product pair.
- TNF alone: matched secondary pair, isolating the value of added depth within
  our product. Absent depth is not fabricated zeros. These are diagnostic controls,
  not product alternatives or a gate on learning/depth. Their cost is reported
  separately and capped at 16 allocated core-hours within the 48-core-hour product budget.

All four partitions retain the same complete input DNA, exclusions/masks and
unassigned outcomes. Raw versus learned isolates the learning pipeline under
fixed inputs/geometry/clustering, including its saved transforms; it is not a
controlled comparison of every embedding normalization decision. Depth versus
sequence changes the declared information contract, keeping scientific defaults.

External shortlist: **SemiBin2 short-read self-supervised, MetaCAT core CPU,
SCGBinner, COMEBin native full 120-candidate grid** and **CompleteBin modified
max-50**, subject to Linux and actual-scale affordability admission before fits.
One configuration/attempt per tool. Preserve native schedules/eligibility/selection
except the explicitly named CompleteBin cap. No replacement list or automatic retry.

COMEBin's successful E001 stages cost 39.6462 allocated core-hours (known recovery
sequence lower bound 58.1075), with high seed-11 R95; a whole-tool comparison on
this same new assembly is valuable despite mechanism overlap. Those results and
failed attempts remain accepted, with no replay. Reserve 192 hours for its new
native run/grid; this is a conservative cap, not a size-scaled runtime forecast.

CompleteBin's current data-dependent schedule uses a 115,000 effective-contig
threshold, base 35 epochs (39 at N50 ≥1536), and can otherwise reach 200 epochs.
The isolated E009 source changes only that maximum to **50**. Training loops over
resolved epochs; it does not stop on validation-loss stabilization. The separate
150-epoch extreme-overfit safety valve cannot increase our 50 cap. Automatic
pretraining decisions use the capped epoch count, so this modification can also
change that decision; retain the outcome. Leiden's adaptive convergence is a
separate stop. This is a modified configuration, **not upstream parity**.

DCVBin's official 1.657-GB continued-pretraining payload is available. Its actual
basic wrapper selects one BAM, constructs `VAE(nsamples=1)` with unconditional
CUDA and 200 epochs; the encoder alone has a CPU fallback and a 5,000-token cap,
with ≥2-kb eligibility. The enhanced source also calls CUDA directly. A tested
CPU/two-depth/continued-pretraining adaptation would be substantial extra tool
implementation, so **DCVBin is excluded from E009**, rather than treating coverage
as a disadvantage or claiming its weights are missing. LorBin remains deferred
for long-read/model contracts. See the [targeted reconciliation](../../docs/evidence/2026-10-09-e009-contract-reconciliation.md)
and [asset inspection](../../docs/evidence/2026-10-09-e009-asset-inspection.json).

## Data and immutable axes

Choose **CAMI III Toy Longitudinal Human Gut, short-read sample 0** as the single
assembly target. **Sample 1** is its second-time-point depth source from subject S1.
The downloaded corrected subject table verifies this pairing. Subject selection
uses the first listed subject, not genome abundance, quality or anticipated rank.
Use full published reads, no truth-selected read subset, genome filtering or
artificial fragmentation. Each short-read sample is advertised as about 5 Gbp;
two compressed archives total 9.732 GB. Keep other subjects outside this milestone;
they are not certified unseen-genome holdouts because source overlap is unresolved.

The complete official sample-0 `contigs` and `gsa` archives were inspected:
`contigs` holds anonymous/named GSA plus the simulator origin map; `gsa` holds
per-source reference-coordinate fragments. All three DNA collections have the
**same 665,738-record / 422,673,293-bp DNA multiset**, including 544,093 below-500
records. CAMISIM GSA/anonymization code produces that layout; no assembler
provenance is supplied. These are gold-standard reconstructions, not suitable
read-derived assembly inputs for E009. The exact provider producer commit is unknown.

Build **one MEGAHIT 1.2.9 read-derived sample-0 assembly**, default metagenome recipe
with an explicit 200-bp output cutoff, pinned source/binary and native arguments.
Keep every emitted contig and graph if readily emitted; no second assembler,
coassembly, long-read branch or GSA accuracy arm. The GSA is not a substitute if
this contract fails. This is a documented derivative of public toy data, not an
official 20-sample CAMI score or human-donor generalization study.

Map full sample 0 and sample 1 competitively to this exact assembly with the
reviewed strobealign/samtools contract where it fits. Serial mapper then sorter;
no three full-thread commands in a pipe. Both sorted BAM reference-name/length
axes must exactly match the FASTA. Simulator BAMs mapped to original genomes are
truth assets, never the depth input. Mean-depth header order:
`contig_id`, `cami3_toy_human_gut_short_read_sample_0`,
`cami3_toy_human_gut_short_read_sample_1`. Retain all rows and true zero masks;
no inferred filename ordering, synthetic missing depths or GSA depth joins.

Use E005's tested mean-depth definition: aligned M/= /X observations divided by
full contig length; MAPQ/baseQ minima zero; exclude unmapped, secondary and
supplementary, retain DUP/QCFAIL and both overlapping mates; no deletion/edge trim.
This policy has mapping-ambiguity limitations. Native external tools receive the
**same BAMs/assembly**, extracting their own mean/variance/fragment statistics as
documented. Native statistics need not be numerically equal to our explicit mean
depth, and that difference belongs in the comparison's input accounting.

Before fitting: verify downloaded archive SHA256s, member inventory/path safety,
read pair/quality structure and exact source-reference/taxonomy identities.
Freeze the unmodified reads, reference genome inventory, one assembly hash and
all IDs/lengths/strata, ordered BAM/depth manifest and native eligibility. The [native locks](native-lock.json) bind acquired code/model/HMM payloads.
Bulk reads and source DNA remain provisional until their actual SHA256s and
member inventories are reviewed; no HEAD receipt verifies payload integrity. Source taxonomy is the toy dataset's
2025-08-01 snapshot, not the active challenge's 2026 taxonomy.

Inspect source-genome accession aliases, per-replicon canonical DNA hashes and
near-genome overlap against retained E001/E002/E003/E004/E005 and real software
smoke sources. Record matches at exact sequence/accession and species/strain
levels; do not remove them after scores. The preliminary source filenames already
show S. mutans species overlap with E003, but exact overlap is **unresolved**.
Record source assembly completeness/isolate/MAG status and chromosome/plasmid
membership. Public-genome pretraining/database overlap is possible/unknown for
reference-informed tools. Historical training inventories are not always complete;
this limits unseen-genome claims and is not evaluation-pipeline label leakage or
a blocker merely because a full inventory cannot be recovered. This is new-sample/assembly evidence; no unseen-species
claim follows. After error inspection it is development data for improvements.

## Truth and evaluation contracts

Truth lives in a separate evaluator path. Features/train/cluster/native selection
must never open source origin tables, read-origin mappings or evaluator metrics.
Freeze truth construction before any scores; evaluate all finalized partitions
together only after their hashes and admitted tool list are committed.
Resource eligibility decisions are made without rank/quality access.

The evaluation reference universe contains all source genomes/replicons that
generated sample-0 reads, including non-target biology; reference selection uses
the simulator origin inventory, never a binning result. Retain the full released
source catalog for provenance/overlap checks. If alignment indexing needs batches,
merge competing hits globally before declaring unique origin; independent
per-batch winners are not competitive truth. Resource-check this path before fits.

Use pinned **minimap2 2.30** all-chain PAF/CIGAR (`-x asm5 -P -c --eqx -m
100 -s 100 -n 2 -t N-1`) and the retained **AMBER** API/options
(`filter_tail_percentage=0`). `-P` retains all emitted chains without primary/
secondary pruning; this is still a heuristic aligner, not exhaustive homology.
Convert nothing silently: PAF coordinates are zero-based half-open, reverse query
coordinates descend while reference coordinates ascend. I/D columns are not
aligned support. The tested adapter reconciles all competing hits globally.
MetaQUAST can provide supplemental misassembly evidence later; its filtered
internal matches are not our narrow truth contract. Native small DNA validates
coordinates, orientation, gaps, competing genomes and repeats locally; native
Linux and full-reference scale remain owner-preflight/later admission dependencies.

Prospective scoring rules:

- Source-reference local alignments need ≥99% identity and ≥200 aligned bp.
  Reference/query intervals are zero-based half-open in our adapter; native
  conventions are converted explicitly. Retain secondary/equal alternatives,
  strand, edits and assembly duplication; no MAPQ-only shortcut for near strains.
  A query segment compatible with multiple source genomes is ambiguous. Count
  confirmed query intervals once and reference-coordinate union once; alignment
  caps or unresolved ties are unknown, not unique truth. Test this on exact,
  edited, duplicated, shared and chimeric software sequences before freezing the
  resolved native command. These are conservative alignment-support criteria,
  not proof of biological uniqueness beyond the supplied references.
- **AMBER contig view:** label a contig only if ≥95% of its whole query length is
  uniquely attributable to a single source genome. Use original full lengths.
  Report this restricted truth population and ambiguous/chimeric/unmapped counts;
  do not call its eligible-view completeness whole-genome completeness. Keep
  all missing/noise/excluded truth IDs in denominators, including below 500 bp.
- **Primary conservative reference R95:** for each source bacterial/archaeal
  cellular genome present in sample-0 read-origin truth and with ≥200-kb reference length,
  choose its best single bin with ≥200-kb exported DNA and ≥95% confirmed-query
  purity. Purity numerator is query bp uniquely supported for that genome;
  denominator is **all exported bin bp**, including ambiguous, chimeric,
  unmatched and non-target DNA. Completeness is the union of that genome's
  reference coordinates supported in that bin divided by its entire supplied
  reference length. Missing/unassembled/excluded/noise regions remain failures;
  duplicates cannot inflate completeness. Repeated loci within one source genome
  can establish genome purity while remaining unusable for unique-coordinate
  completeness; cross-genome shared segments support neither. Best-bin ties use opaque bin IDs,
  not a candidate search or truth-driven export choice. Include genomes with
  no recovered bin as zero. Report macro and reference-bp-weighted values and
  counts at ≥50% and ≥90% reference completeness at ≥95% purity. Separately
  simulated plasmids, viruses, eukaryotes and host are outside this primary
  cellular-genome denominator even if a plasmid shares its host's taxonomy.
  Retain their assignments as non-target/contaminant diagnostics, including
  their bp contribution to every bin's purity denominator.
- Also report **assembled-confirmed recovery** using the unique reference union
  represented anywhere in this assembly as denominator; show the assembly
  ceiling beside whole-reference recovery. This exposes binning loss separately
  from assembly loss. E005's exact-GSA R95 is related but different: label the
  new alignment-based metric explicitly, never append it as directly comparable
  E005 values. If sources are draft MAGs, full-reference recovery still is not
  completeness of an unknown finished biological genome or a MIMAG HQ count.
- Report genome-level mixing/splitting, bp- and contig-weighted precision/recall,
  AMBER summaries, and assignment fractions. Retain all assembly strata
  [1,500), [500,768), [768,1000), [1000,2500), [2500,10000), ≥10000 bp;
  state that MEGAHIT's 200-bp emission floor cannot evaluate shorter sequence.
  Cross-tool native ranges and a secondary intersection-of-native-eligibility
  contig view are both reported; the latter is a restriction of outputs, not a
  rerun or a pure architecture comparison. Whole-reference denominators stay fixed.
- Every original ID/DNA is assigned once, unassigned/noise, outside native range,
  or explicitly excluded. Native absent exports are never removed from recall.
  Unknown IDs, altered DNA or duplicate native bin claims fail the adapter with
  retained evidence; no silent largest-bin repair. A valid empty partition is a
  biological outcome; timeout/crash is operational failure, not a zero-quality run.

Reference truth is the primary independent quality measure. Marker selection
scores are retained for diagnosis, not reused as the sole validation metric.
CheckM2/GUNC may be a later secondary reality/proxy check; they are not required
downloads or a reason to grow this first benchmark. Truth-based ≥90/95 recovery
must not be labelled validated real-sample MAG quality or formal HQ MIMAG status.

## Focused diagnostics and decisions

Retain our raw/learned embeddings, checkpoints, reload comparison, complete
partitions and native intermediate/final partitions/marker decisions where emitted.
Select at most 128 query IDs per length stratum by fixed hash before scores; inspect
1/5/10-neighbor truth purity against the full eligible embedding population.
Use only shared eligible query IDs for cross-embedding comparisons, with exclusions
reported. Native geometries/preprocessing differ: diagnose, do not rank architectures
from this convenience view. Recount co-genomic negatives from our deterministic
batch indices after training without gradients/retraining; retain expected versus
observed rate and ambiguous-pair status. Do not interpret correlation as causation.

| Observation | Next bounded improvement it could justify | What would weaken that explanation |
| --- | --- | --- |
| Learning loses to matched raw, with lower neighbor quality | Actual sequence-view positives or one false-negative treatment, keeping grouping fixed | Native grouping rescues both equally; apparent gain only increases contamination |
| Good same-origin neighborhoods, mixed/fragmented native bins or large assembly-conditional loss | One marker-guided grouping/refinement ablation on retained embeddings | Source ambiguity/assembly loss dominates; no truth-free selector can recover the gap |
| Sequence-only poor, both depth arms materially better | Retain/develop explicit abundance integration and assess its cost | Depth zeros/ambiguity explain effects; two time points do not supply useful separation |
| Short-contig sequence gap persists while long contigs work | Planned frozen GLM/head versus TNF/head versus hybrid comparison on matched inputs/objective | Gains disappear under common grouping or come only from reference overlap |
| CompleteBin/SCGBinner succeeds while matched controls fail | Inspect its actual pretraining/marker/view/selection behavior, then isolate one plausible component | Native recipe changed inputs, eligibility or refinement; a tool win alone does not identify its cause |

Rank candidate changes by confirmed recovery at fixed purity, harm to other length
strata, avoidable error coverage and measured resource cost. Do not tune to E009
and call it final validation. Any architecture/head/grouping ablation is a later
separately frozen task; the three-way GLM study remains planned, not run here.

## CPU, storage, execution and stopping

**Local Mac:** documentation, source review, ≤32-contig/0.6-Mb real-DNA native
adapter tests, output/evaluator failure tests and returned-record analysis. Use
≤4 threads, loader zero, 8-GB RSS, ≤2-hour local integration. The accepted E002
machine had 4 physical cores/16 GiB RAM; do not bulk download reads or infer full
Linux tool feasibility from it. Local contracts are reported separately from pending native Linux validation.

**Owner UCloud:** first a separate 8-vCPU/24-GB setup/asset/runtime preflight,
then a recommended 16-vCPU/48-GB scientific job or resumable serial jobs following
returned preflight review. Working RSS ceilings are 20/40 GB respectively, with
parent/setup/native children inside the overall clock. CPU-only; no GPU presumed.
Protocol ceilings are safety/budget choices, not ordinary product maxima or runtime
forecasts. More CPUs may help some stages; no linear speedup claim is made.

The [budget](protocol.json) reserves at most **700 allocated core-hours**, including
failed attempts, downloads/setup, collector time and idle driver time. Stage caps
sum to **664**, with **36** reserved, not automatic retry permission. The owner's
2026-10-09 approximate balance is **1,980**: **1,280** remain outside this ceiling.
This adds COMEBin's 192-hour slot to the prior 472-hour stage plan. No UCloud spend
is measured in this preparation task. Native-scale projections must fit before
admitting full fits; resource deferral is an operational outcome, not zero quality.

Tools run serially, using the full allocation **including** coordinator/loader/
child budgets. Numerical phases may use all 16 threads with loader zero; process
pools need per-worker BLAS=1 and explicit aggregate placement. Audit native flags,
OMP/BLAS/PyTorch/Infomap/HMM/child limits and actual CPU reports per phase. MetaCAT
has affinity/label-propagation pools plus five score workers; CompleteBin's API
defaults to 32 loader workers and its CLI does not expose that setting; SCGBinner's
train parser defaults to five. A top-level `-t 16` alone is insufficient. Use a
tested operational adapter for loader zero/pool budgets without changing scientific
defaults; source patches/unsupported changes require named identities and review.
Serial/I/O/graph stages may use less CPU; record that rather than fabricate full use.

The former **200 GB is a provisioning estimate**, not a hard experiment cap.
Home is approximately 50–100 GB; shared storage approximately 8–10 TB. Keep code,
new environments, transfers/logs and compact evidence in Home. Bulk sources,
reads, BAM/SAM and heavy temporaries belong in the project's own quoted
`/work/RasmusAllesøeNielsen#2936/dl_binner/e009/` subtree. The preflight checks
≥6-GB free Home / ≥30-GB free shared space before creating new payloads/prefixes;
extraction checks declared member sizes against actual free space. Inspect actual
sizes before the heavy run; provision more owned shared storage when needed,
without changing science, deleting old attempts or touching colleagues' files.

Research DAG should use pinned Snakemake local executor `--cores` without `--jobs`,
aggregate RAM and explicit serial barriers. Installed `dl-binner run` remains its
built-in dispatcher. Use new version-qualified E009 prefixes where needed; healthy
accepted UCloud dependencies may be borrowed read-only after full inventory/import/
byte validation, never upgraded/relocated. Keep lexical venv Python and isolated
`-B` children. Transfers/logs/returns belong under
`/work/Home/dl_binner/e009/transfer/`; unique attempts under E009's persistent root.

Retain terminal/per-tool logs, timestamps, heartbeats, native schedules, sampled
tree CPU/RSS, exit status, source/config/runtime hashes and collection inventory.
Report allocated vCPUs × total driver wall time separately from CPU seconds;
charge setup and failed attempts, distinguish resumable reused stages from new work.
No expected cost is a measured cost. On fatal workers/time/RSS stop promptly and
verify no running orphans; return checksum-bound evidence even on early failure.

Stop before fits if assembly exceeds 100,000 ≥500-bp eligible contigs or 600 Mb
total emitted DNA, source/truth axes are unresolved, or projected native work
exceeds caps. Those caps protect this first exact-neighbor baseline; they do not
filter the assembly or constrain the product. Retain preparation and amend the
prospective scale/resource plan before scores; never secretly subsample a failing
input. Do not automatically start another community, seed or architecture gate.

## Current prepared milestone and acceptance boundary

The acquisition, exact-accession/canonical-sequence overlap, read-pair, assembly,
ordered BAM/depth, competitive truth, complete partition and narrow AMBER/R95
adapters are implemented. [Operations](OPERATIONS.md) owns the immutable packet,
exact command and return review. [Local validation](local-validation.json) keeps
actual native paths, failed attempts, resource receipts and unexecuted paths
separate. The driver accepts exactly 8 vCPU / 24 GB on Linux, one tool at a time,
20-GB sampled working RSS, 17,400 work seconds plus 600 collection seconds.
Parent verification/setup and native children share the clock; evidence-only
collection after a timeout is labelled and charged separately. No community fit
or E009 score is part of the packet.

It borrows clean E001 numerical/mapping/AMBER/CheckM assets read-only after complete
inventory/import and byte checks, creates five distinct E009 tool prefixes, and
owns missing wheel additions. The Linux utility solve pins all 59 package URLs,
SHA256/MD5 identities; solve success is not Linux execution. Native HMMER worker
counts include the master; owned wrappers retain actual argv. SCGBinner's otherwise
host-wide marker/selection pools and HNSW defaults are capped explicitly; its two
removed NumPy aliases are fixed in the isolated source copy. COMEBin receives a
native BAM directory and its resolved emitted axes are checked, not guessed from
aliases. Local Mac MEGAHIT four-thread crashes are preserved; one-thread software
assembly validates its writer, while Linux must pass the full eight-thread path.

**Next: owner runs the prepared preflight and returns its archive, checksum and
terminal log.** Review source catalog/overlap, all native contracts, actual limits,
read-only bytes, payload identities and costs before preparing the bounded
16-vCPU/48-GB acquisition/assembly/mapping/truth job. Actual read payload hashes,
source biological classification/targets, near-overlap annotation, assembly scale
and representative full-native-schedule costs are unresolved before science.
Unknown historical pretrained overlap is a claim limitation, not an automatic
execution rejection. Scientific execution remains **not admitted**. No baseline,
accepted science, architecture or marker-follow-up study changes here.

Final source `a12c962a85946167bcc2441597b30fcca85b209c` is bound to the immutable
v3 packet: **6,656,591 bytes**, **29 payload files plus the manifest**. The actual
documented bootstrap ran outside the checkout with explicit Mac-only runtime/
allocation overrides: two distinct fresh attempts pass; inner/outer corruption,
missing MEGAHIT and the overall timeout fail for their intended causes. Every
returned member hash, closed terminal snapshot and collection-size total passes
independent inspection. Collection after work timeout is labelled explicitly.
Linux setup/imports and five full native tool contracts remain **unexecuted**, not
mocked as passed. Earlier packets and failed local checks are preserved.

The final self-contained suite passes **21 checks**. A final production COMEBin
reader accepts retained real native arrays using its exact **>1000-bp** eligibility,
resolved BAM basenames, intervals/lengths and zero masks; no feature regeneration.
Known supervised stage and outer owner-harness clocks, including retained failures,
sum to **176.009 s / 0.195566 four-thread wall-budget hours**; sampled successful
peak **0.501 GB**. Nested stage clocks are not added twice. Unit/build/retained-
reader work, source review/acquisition/setup/read-only hashing/debugging/idle are
outside this partial accounting; none are UCloud spend or scientific performance.
See [local-validation.json](local-validation.json) and [transfer.json](transfer.json)
for byte-bound evidence and unresolved Linux/science boundaries.

2026-10-08 planning verification: `python3 scripts/check_docs.py --check-context`
passes (54 maintained documents / 657 local links / 85 present fingerprints;
ten unavailable historical optional caches explicitly unverified). An independent
read-only audit verifies 79 recorded source/metadata/training-file byte bindings,
S1 pairing, 311/332/355 source-name counts, object-size arithmetic and the
472+28=500 core-hour ceiling. `git diff --check` passes; product/scientific code,
defaults, tests, workflows, environments and PROJECT_INTENT are unchanged.
These are planning checks, **not native adapter tests or Linux/scientific validation**.
