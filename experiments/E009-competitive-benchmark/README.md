# E009: first competitive human-gut assembly benchmark

Opened 2026-10-08; updated 2026-10-16. **Four unchanged controls completed and reviewed;
VM stopped.** [The result](controls-review.json) owns acceptance, bounded development
diagnostics, costs and limitations; [operations](OPERATIONS.md) owns the current
next preparation boundary. No external binner ran. All five tiny UCloud contracts
remain accepted through v10/v14 without replay; [v14](linux-preflight-v14.json)
remains distinct from these native GCP prototype controls.

The current design uses **one full sample-0 assembly and ten full coverage sources**,
first listed sample of every corrected subject: 0,2,3,4,6,9,10,11,14,17.
[GCP operations](OPERATIONS.md) owns the prepared data-only DAG, cost/retention
records, truth-v2 admission, separate control approval and exact following prompt.
The later owner message authorizes the data-only phase at `5fec4e1`, subject to
verified credits/prices and effective quota. [The phase receipt](gcp-data-observed.json)
owns the earlier data phase. The later separate $2 authorization executed only
the four unchanged prototype controls; no further fit is authorized.
[D014](../../docs/decisions/D014-google-cloud-workspace.md) supersedes UCloud
operating paths/budgets; the [old handoff](../../docs/history/E009_UCLOUD_OPERATIONS.md)
retains their history. Old attempt records are provenance, not current commands.

**Verified data outcome, 2026-10-15:** the DAG failed in the final alignment-truth
parser. Sources, full sample-0 assembly and all ten BAM/depth stages are sealed;
independent critical-byte/native-header/axis review accepts those outputs and the
closed combined matrix separately, without sealing the failed final stage.
The full assembly is **145,702 contigs /231,678,157 bp**; the ten-column matrix
has **1,457,020 checked cells** and preserves 13 all-zero rows. All ten minimap2
batches exited 0 and their PAFs are retained. The first parser failure is reproduced
in [the exact example](truth-failure-example.json); ambiguous-base accounting
explains it. No data/alignment stage was replayed and no binner ran.

The completed [origin/population review](truth-population-review.json) verifies
all 33,267,026 sample-0 mate IDs and 309 positive simulator genomes: 156 bacterial,
133 viral, 11 eukaryotic and nine separately simulated plasmids. All nine permuted
files are exact circular rotations; host-like filenames do **not** make them host
genomes. Fresh [truth v2 is admitted](truth-v2-admission.json) after local derivation
and independent raw-chain review, preserving all 7,688 competitive aliases as
7,607 canonical records, actual simulator genome IDs and full provided-reference
denominators. Its fixed conservative N policy leaves 7,653,205 bp /3.3034% unknown.
The old failed DAG/journals are unchanged. No new aligner or VM wake was needed.
[Operations](OPERATIONS.md#earlier-data-review-and-failed-dag-evidence-2026-10-15)
owns actual cost/storage/shutdown evidence and the exact next prompt. The next
step is a coherent next-prototype recommendation in
[D015](../../docs/decisions/D015-coherent-prototype-upgrade.md), with local implementation
only after the next owner prompt. The prior standalone marker split is optional.
[The unchanged controls](diagnostic-controls-plan.json) are now
complete under their separate $2 approval. Actual runtime, outputs and costs are
reviewed; original failure/truth histories remain unchanged.

## Question and informative comparisons

What does a full read-derived human-gut assembly reveal about actionable failures
in our simple prototype, and which bounded change could improve our own method?
E009 is development evidence and reusable data, not final product evaluation.
[D013](../../docs/decisions/D013-first-comparative-benchmark.md) records the owner's
performance/cost concern, prior evidence, serious alternatives and the revised
value-of-information decisions. Expensive confirmation of an expected mature-tool
advantage is insufficient justification for a campaign.

Freeze our stable main source at `5e54538d1799e8d2538621729400f33fbaf017b9`
(dev3; normal prototype merge `5bc824a9bf4b1ca4562acda10735a3fc6b54dc3d`).
This phase changes no model, transforms, training defaults, clusterer or seed.
After admitted data/truth and separate cost approval, unchanged seed-11 learned/raw
TNF+ten-depth and TNF-only pairs are useful diagnostic controls. Retain complete
DNA, short/excluded/noise outcomes and stage intermediates. Their results apply
to these representations/objective/grouping/data, not every possible use of depth,
sequence or future taxonomy. A whole-tool result cannot isolate its causal component.

Recommend at most **SemiBin2** as the first later external native reference, after
cost admission, with useful intermediate evidence. **MetaCAT core CPU** is a
conditional second reference if marker-seeded grouping is the concrete unresolved
decision; a matched own-method grouping test may be more informative. **Defer full
SCGBinner, COMEBin's 120-candidate grid and CompleteBin**, retaining their accepted
tiny contracts, code/architecture evidence and payload locks. CompleteBin's max-50
configuration remains stored provenance; its full run needs a specific future
question and separate CPU/RAM/storage/spending approval. No binner run is authorized
by this data phase, and no entire shortlist must finish before improvements.

The older mandatory shortlist, two-depth wording and allocation-hour reservations
are [historical](../../docs/history/E009_UCLOUD_OPERATIONS.md#superseded-mandatory-comparison-planning-2026-10-14).
Keep source/payload/runtime receipts unchanged; accepting a contract is not an
entitlement to fit that tool on this assembly. D015 supersedes a mandatory single-
mechanism-first workflow; use selective matched tests with prospective
keep/modify/abandon criteria, preserve the immutable control, and confirm promising
changes on prospectively chosen additional data before broad/SOTA claims.

## Data and immutable axes

Use **CAMI III Toy Longitudinal Human Gut short-read sample 0**, subject S1,
as the only assembly target. Ten selected full depth samples cover all ten
subjects, using the first listed ID from each corrected subject table group:
**0,2,3,4,6,9,10,11,14,17**. This includes cross-subject coverage and sacrifices
paired temporal depth relative to all twenty; its optimality is unmeasured.
The selection is label/score-blind and the first-ten numeric IDs would cover only
six subjects. All selected samples are development coverage after inspection;
none supplies a certified unseen-genome/donor holdout. Full reads, no truth-selected
subsets, source filtering or artificial fragmentation. About 5 Gbp/sample;
current HEAD archive sum is 48.63 decimal GB (45.29 GiB), versus 97.28 GB for all
20. Actual SHA256/member identities remain acquisition dependencies.

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

Map all ten full selected samples competitively to that same exact assembly
with the reviewed strobealign/samtools definition, serial mapper then sorter.
Every BAM reference-name/length axis matches the FASTA. Simulator source BAMs
are evaluator assets, never observed depth. The immutable
[ordered axes](depth-samples.tsv) and [data plan](gcp-data-plan.json) define
`contig_id` followed by columns for 0,2,3,4,6,9,10,11,14,17 in that order.
Padded *actual* BAM paths, not aliases alone, preserve native resolved-path order.
Retain all rows, true zeros/masks and short DNA. No filename-order guesses,
synthetic missing depths or GSA depth joins.

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

The table retains the earlier experiment-specific options.
[D015](../../docs/decisions/D015-coherent-prototype-upgrade.md) now recommends a
coherent prototype upgrade; these are diagnostic/ablation choices, not a mandatory
sequence of isolated experiments before implementation. Scientific measurements
and dev3 source remain unchanged.


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
| Sequence-only poor, both depth arms materially better | Investigate this representation's use of the ten cross-subject coverage columns; preserve other depth designs as alternatives | Depth zeros/mapping ambiguity or prototype transforms explain effects; these columns may not provide separation |
| Short-contig sequence gap persists while long contigs work | Planned frozen GLM/head versus TNF/head versus hybrid comparison on matched inputs/objective | Gains disappear under common grouping or come only from reference overlap |
| A later, separately justified native tool succeeds where matched controls fail | Inspect retained input/embedding/marker/selection evidence, then isolate one plausible component | Native recipe changed inputs, eligibility or refinement; a tool win alone does not identify its cause |

Rank candidate changes by confirmed recovery at fixed purity, harm to other length
strata, avoidable error coverage and measured resource cost. Do not tune to E009
and call it final validation. Any architecture/head/grouping ablation is a later
separately frozen task; the three-way GLM study remains planned, not run here.

## CPU, storage, execution and stopping

Current resources/costs/credit checks and commands live in [Operations](OPERATIONS.md)
and [CLOUD](../../docs/CLOUD.md), with owner-authorized 8-vCPU/32-GiB, 300-GiB disk,
24-hour cumulative data-stage clock subject to credit/quota admission. The retired 700-hour
UCloud plan, 1,980 old balance, Home/shared quota and 16/48 allocation are
[historical](../../docs/history/E009_UCLOUD_OPERATIONS.md#superseded-two-depth-resource-protocol),
not GCP funding or authorization. No full-fit monetary schedule is approved.

Use cheap <=4-thread, <=8-GB, tiny real-DNA local checks; the Mac assembler path
remains one thread. Local timings are not Linux/scale projections. Data/native
phases run serially with explicit child/loader/OpenMP/BLAS/BGZF/I/O accounting,
actual native reports and extended rule benchmarks. No `--cores` plus `--jobs`.
CompleteBin starts **two** coverage processes for >2 BAMs; the expanded prepared
plan divides their BGZF budgets rather than give each the old N-2 allowance.
This new multi-BAM plan is locally checked, not full-fit admission.

Keep persistent closed logs/manifests, checksums, failure causes, timing/allocation
and monetary/provider uptime separately. Byte-bound explicit resume must preserve
completed stages and fail on drift/unsealed outputs. Keep native exclusions/noise
and all emitted DNA. Stop before fits if the real assembly exceeds 100,000 >=500-bp
eligible contigs or 600 Mb, or on resource/native/axis failures; prospectively
reassess rather than filter/subsample or shorten schedules. CompleteBin's separate
[storage audit](../../docs/evidence/2026-10-14-completebin-storage.md) requires actual
eligibility, candidate/checkpoint coexistence and RAM review after the data stage.

The dated attempt sections below preserve their original preparation/failure
state. They are superseded by the accepted v14/current GCP section at the end;
only OPERATIONS supplies current commands. No historical imperative authorizes replay.

## Initial prepared milestone and acceptance boundary (superseded by v8 recovery)

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

V3 local preparation source `a12c962a85946167bcc2441597b30fcca85b209c` is bound to the immutable
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

## Native v3 startup failure and v4 recovery — 2026-10-10

[Verified failure receipt](linux-startup-failure-v3.json) retains archive checksum,
all seven inventory-file hashes / nine members and **54,039 immutable retained
bytes**, including inventory and terminal snapshot. Declared 8-vCPU /24-GB driver:
**91.129350 seconds /0.202510 allocated core-hours** through collection, not exact
provider billing. The first COMEBin read-only inventory/import probe exhausted its
unchanged 90-second cap; only 1.31 sampled CPU seconds and 0.059-GB aggregate RSS
were recorded. Its log is silent before the supervisor trailer. No downloads,
new tool environments, native data paths, fits or scores started. Packet verification
passed; current runtime health and unchanged dependency bytes were not established.

The retained return does **not identify the blocking module or root cause**. Do
not call this repaired by raising the timeout, skipping the probe, reinstalling or
relocating the accepted prefix. V4 uses an instrumented startup under `-I -B -S`,
executes normal `site.main()`, and preserves all prefix/origin/inventory/freeze
checks. Parent-requested stacks begin before site initialization and use separate
per-PID files, avoiding a child timer thread and contamination of inventory JSON.
Metadata/import/pip progress and bounded Linux owned-PID wait/syscall/fd observations
are retained before termination; denied kernel views remain explicitly unavailable.
Each metadata object is read once instead of twice, without changing its values.
The first gate still has 90 seconds. If the stall persists, return evidence and
stop before dependent work. An underlying Linux runtime repair remains **unconfirmed**.

Both the bootstrap log and live `<attempt>-terminal.log` now have explicit `.log`
names directly in `transfer/`. An exclusive immutable snapshot is copied into the
attempt/return during collection. Preserve v3 and its original receipts; upload
only the newly bound v4 pair from Operations. No accepted science is repeated.

Recovery checks: **25 self-contained tests pass**, including a real fresh venv,
normal site processing, intentionally stalled `.pth` hook with retained stacks,
strict lexical interpreter/origins, module stdout, PID reuse and immutable terminal
snapshots. Actual retained Mac NumPy/Torch imports and complete instrumented vs
ordinary `pip freeze --all` agree; all 20,132 numerical-prefix files /774,207,552
bytes remain unchanged. This is no model inference or Linux compatibility claim.
A local child-timer shutdown hang was retained and avoided with parent-triggered
separate stack files. Linux `/proc` decoding uses a fixture locally; actual kernel
wait capture and the original startup stall require the owner return.

The exact v4 packet/bootstrap passes an out-of-checkout Mac harness: two fresh
attempts, intended inner/outer checksum corruption, missing native executable and
overall timeout, with all returned file hashes and storage totals checked. Both
bootstrap and driver live `.log` files reside in transfer/; immutable snapshots
exclude later return-print output. Source `2027436c54b6ff016a5ed4e75232f0256bc7e568`,
30 payload files plus manifest, 6,659,467-byte archive. This is locally tested
recovery preparation, not repaired Linux startup or admitted scientific execution.


## V4 Linux cold-import timeout diagnosed, 2026-10-10

[The verified v4 receipt](linux-startup-failure-v4.json) binds all 11 members,
9 inventory files and 177,168 immutable uncompressed bytes. The first COMEBin
probe again stopped at 90 seconds, but its new traces establish progress:
NumPy imports finish around 60 seconds, then Torch advances through libraries and
Python modules. Seventeen `/proc` observations show `read(2)` waiting in
`folio_wait_bit_common` on changing bytecode/shared-library paths under Home.
Sampled CPU is 1.89 seconds over 90.044 seconds, consistent with storage waits.
This is a prematurely terminated cold import, not an established Python deadlock
or evidence of a corrupt package. The storage/provider reason remains unknown.
See the [Linux page-cache documentation](https://docs.kernel.org/filesystems/vfs.html)
for the kernel mechanism; the diagnosis itself follows retained local evidence.

All 73 explicitly versioned metadata entries match the accepted freeze; the 13
direct-reference entries and full pip freeze remain unvalidated. No downloads,
new prefixes, tiny native contracts, fitting or scoring started. Reported driver
clock before collection: 91.233606 seconds /0.202741 allocated core-hours at the
declared 8-vCPU/24-GB allocation. Provider idle/billing and collection are separate.
The command correctly saved bootstrap and driver logs under transfer/.

**V5 corrects the cold-start budget:** every complete inventory probe allows at
most 900 seconds, while 90 seconds without observed child phase, latest stack or
open-file movement stops it. Repeated identical stack dumps, sampled CPU and
parent heartbeats do not count as progress. Fatal tracebacks stop promptly; the
absolute stage/overall/RSS limits remain enforced. No originals are copied,
relocated, reinstalled or altered, and all normal site/import/origin/freeze checks
remain mandatory. This repairs premature wrapper termination; native runtime
health and storage throughput still need the owner's return. It does not claim
that a longer budget fixes filesystem latency. All other preflight scope/settings
and the five-hour/40-core-hour ceiling remain unchanged.

Local v5 source checks pass 28 tests, including the actual owner `run_stage` and
inventory adapter with eight delayed module imports, idle/fatal-descendant cleanup
and absolute timeout despite progress. The unchanged native Mac numeric prefix
passes full freeze/origin checks with identical before/after bytes: 3.715 seconds,
0.242-GB sampled process-tree peak. Native Linux recovery remains unexecuted.

The exact immutable v5 packet and documented bootstrap pass the outside-checkout
Mac harness: two fresh attempts, intended inner/outer checksum corruption, missing
native executable and overall timeout, with return hashes/storage snapshots and
transfer log placement checked. All 30 packet payload hashes verify. Retained
Linux trace replay keeps all 18 moving-file snapshots alive under the idle policy,
then rejects an unchanged final signature; this is analysis, not native execution.
V5 source `01837619230458e830fba7f54755c04d6c8c7604`; see [transfer receipt](transfer.json)
for byte identities. The owner must return Linux evidence before admission.


## V5 storage failure and targeted source-cache recovery, 2026-10-10

[Verified v5 evidence](linux-startup-failure-v5.json) binds all 11 members, nine
inventory files and 1,544,852 immutable retained bytes. The initial inventory
again reached its absolute cap: 900.223 seconds, 10.51 sampled CPU seconds,
0.288-GB sampled peak, 901.425973 driver seconds before collection /2.003169
allocated core-hours at declared 8/24. NumPy/Torch/Pandas/SciPy imported; sklearn
and complete pip freeze did not finish. No payload/native/scientific work began.
V3/v4/v5 failure costs are retained separately; provider idle/billing are unknown.

All 177 wait snapshots were inspected. There are 175 `folio_wait_bit_common`
read waits: **162 existing `.pyc`**, eight libraries, two `.py` and three metadata
files. The earlier excerpt-based chat estimate of 176 cache waits was incorrect;
the complete recount here supersedes it. The dominant read path is bytecode, but
other file types also wait. Therefore cache bypass alone is **not yet a proven
Linux repair**. The exact filesystem/provider cause remains unknown.

The old read-only `-B` policy stops writes but continues reading caches. Explicit
`-X pycache_prefix=<empty job-local namespace>` with `-B` makes CPython ignore
old cache trees and compile unchanged original sources in memory. It preserves
interpreter/prefix, versions, imports and scientific configuration. The same
explicit policy reaches pip/native Python children; `-I` would ignore the usual
PYTHONPYCACHEPREFIX environment variable. These semantics are documented by
[Python](https://docs.python.org/3.13/library/sys.html#sys.pycache_prefix).

**V6 suspends the full preflight.** Its next owner job is **one vCPU /4 GB, five
minutes work plus 30 seconds normal collection**: actual source/cache read pairs,
all ten prefix imports/full inventory/freeze/origins, audit of zero old cache
access, sampled source rehash and safe cleanup. It has no downloads, installations,
new environments, tool fixtures, science or inferred native-scale readiness.
This is an inexpensive test of a concrete workaround, not another timeout increase.
The code repairs an actual locally reproduced import blocked reading cache bytes:
a real cache FIFO stalls CPython `get_data`, while isolated cache lookup imports
that same source successfully without writes. Native Linux effectiveness remains
pending; source/library waits may still require a packed execution snapshot or
separately pinned runtime. No shortlist/dataset/scientific setting is discarded.

Review v6 before restoring the original resource-aware full preflight. Its
whole-prefix byte checks must explicitly distinguish original source/binaries
from ignored regenerable caches, and every Python/shell child needs the policy.
Those subsequent admission changes are not claimed completed by this recovery.

Thirty local checks pass, including blocked-cache reproduction and zero old-cache
access without writes. The finalized real Mac recovery worker reads both source/
cache pairs, loads NumPy/Torch, matches full normal pip freeze and leaves the entire
20,132-file /774,207,552-byte prefix binding unchanged. Its inventory is 8.974
seconds /0.288-GB sampled peak, with 474/923 source-open audit events in pip/parent
and zero persistent-cache attempts. This is a Mac path/contract check, not timing
for Linux's ten-module probe or proof of repaired storage.

The immutable v6 packet is 51,348 bytes, 16 payload files plus manifest, with all
archive member hashes verified. Source `76c5012e9f9981d89a3ac3c4d6773205cf1dee2b`. The exact
owner bootstrap passes outside-checkout Mac recovery: two fresh attempts, intended
inner/outer corruption, unavailable source, changed full inventory and overall
timeout, immutable return hashes/storage/log placement and unchanged retained
prefix bytes. This is genuine local worker execution with explicit Mac
platform/root/numerical-prefix/module-list and shortened test-clock overrides.
Review the cheap owner return before any full allocation; [transfer.json](transfer.json)
owns final identities and observed scope.

## V6 source-read failure and v7 local snapshot, 2026-10-10

[Verified return](linux-startup-failure-v6.json): checksum and all 22 inventory
files pass; 24 regular archive members /326,016 logical bytes including immutable
terminal and inventory. Full inventory stopped at 180.170 seconds /2.94 sampled
CPU seconds /203,976,704-byte sampled peak RSS during Torch import. All 34 captured
`folio_wait_bit_common` samples have original `.py` files open. The two sampled
source reads took 0.567/0.638 seconds versus 0.000632/0.000530 seconds for their
bytecode. Cache bypass did not repair slow Home reads. The kernel/provider cause
is unidentified; no Bash syntax failure, scientific stage or new installation.
Declared 1-vCPU /4-GB driver cost: 183.213927 seconds /0.050893 allocated core-hours
before collection, not exact provider billing.

[D006](../../docs/decisions/D006-environment-ownership.md) now permits this narrow
byte-verified job-local numerical snapshot. V7 replaces direct Home imports with
one-time parallel I/O copy and immutable archive retention, preserving original
bytes/versions and recording internal-link normalization. Full native preflight
remains disabled; a native numerical compatibility pass is still required.
Thirty minutes work, 30 seconds normal collection, one CPU /4 GB, sampled RSS
3 GB. The copy/pack cap is 20 minutes; the import cap stays 180 seconds. No larger
import timeout, dependency gate bypass, package installation or changed science.
See [Operations](OPERATIONS.md) for the next owner command and exact acceptance
boundary. Local tests and native Linux validation remain separate.

V7 final packet is bound to committed source `4068297c2ec18d941b56c463abcc31aad61f6d8b`:
54,472 bytes /17 payload files plus manifest. Thirty-three local checks pass. The
exact Bash bootstrap/driver ran outside the checkout on a real standalone Mac
Conda Python 3.13.12 runtime, full freeze matched, NumPy/Pandas imported, and
NumPy arithmetic passed. Original complete prefix binding stayed unchanged.
Copy/verify/pack: 16.144 seconds; first inventory: 57.722 seconds /7.46 sampled
CPU seconds /185,303,040-byte peak RSS. Snapshot: 13,829 file/link entries,
276,167,151 regular bytes, 300,646,400-byte archive. Fresh and explicit reuse
passed; reuse scheduled restore, never a new source copy. Actual outer/inner
packet corruption, missing-prefix failure, wrong freeze, runtime archive corruption
and overall timeout produced their intended retained causes. A production reader
permission error exited promptly without receipt/archive acceptance.

These are software/portability contract checks, not UCloud cost or Linux validation.
Mac lacks the `/proc` mapped-library check; its fixture checks NumPy/Pandas, not
all ten Linux modules or a Torch snapshot. Local copy CPU averaged 1.54 because
Mac has no Linux affinity binding; native recovery binds the whole process tree
to one CPU. No proportional runtime prediction follows.
[transfer.json](transfer.json) binds logs, full compact metrics and return evidence;
failed sandbox `ps` checks and the corrected macOS parent-path alias regression
remain retained locally. All old packets/environments and scientific settings
are preserved. The provider storage cause remains unidentified.

## V7 measured workload correction and resumable v8, 2026-10-10

[Verified v7 return](linux-startup-failure-v7.json) has nine members/seven verified
inventory files and 602,809 immutable logical bytes. The 1,200-second copy cap
terminated steady progress at 17,989/44,770 entries; overall 1,800 seconds had not
expired. Copy: 1,200.067715 seconds /22.53 CPU seconds /193,208,320-byte sampled peak
RSS. Declared 1/4 driver: 1,200.179870 seconds /0.333383 core-hours before collection.
No runtime import or native/scientific work started. Preserve the failed attempt,
original prefix and unjournaled v7 /tmp partial if the job remains live.

V8 selects a conservative numerical runtime, omitting compiler/static/test payloads
and retaining package metadata/resources/public testing helpers and link closure.
Persist small verified chunks, then resume by restoring seals and copying only
missing original contents. No final monolithic packing step is needed. Failed/
partial chunks are not admitted. The old source bytes/versions and benchmark
settings stay unchanged. [D006](../../docs/decisions/D006-environment-ownership.md)
and [Operations](OPERATIONS.md) own the changed contract and limits.

Measured v7 rate (~15 entries/sec) projects full 44,770-entry copy to ~49.8 minutes
before other work. Proposed owner-selected ceiling: 90 minutes work +120 seconds
normal collection at 1 CPU /4 GB. Copy/hash/restore/pack/import stages have no
independent wall caps; a five-minute no-work guard watches advancing byte/entry
counters. Initial selection reports native counts/bytes and a rough measured-rate
projection. Local timing/cardinality is not UCloud performance or compatibility.
Full native preflight remains disabled. No accepted science is repeated.

V8 final source is `bd7addb6e3e646a80bab57deadf9e847e3f02858`; upload only the
61,445-byte final pair under `artifacts/e009-preparation/transfer-v8-final/`.
The provisional locally executed v8 packet remains retained, with its source and
negative/positive tests, but is not the owner transfer. Final byte/command/log
identities and detailed checks are in [transfer.json](transfer.json).

Thirty-nine E009 regressions pass. Real permission failure stops the chunk reader
with its cause after preserving two earlier seals; source drift, conflicting writers,
archive corruption and stalls refuse admission. A moving worker runs beyond the
former short substage window; repeated identical counters/heartbeats cannot keep
it alive. An actual interrupted worker resumes previously sealed chunks. No mocks
replace the materializer, tar writers/readers, hashing or numerical imports.

Final-scale fixture: 44,770 actual regular files /24,770 selected /20,000 explicit
header/test omissions, 194 sealed chunks. Fresh: 40.953 s /56.66 sampled CPU s /
147,496,960-byte peak RSS; complete restore: 39.777 s /35.97 CPU s /159,289,344-byte
peak. Both keep the original hashes, and the completed 4,589,013-byte inventory
receipt has exactly the same SHA on reuse. Tiny software file contents and local
filesystem performance are **not** native package sizes or UCloud throughput.

The exact final Bash/packet/driver also runs outside the checkout on the unchanged
standalone Mac Conda Python 3.13.12 runtime. Its selection is 9,509 of 13,829 entries,
with full accepted freeze/NumPy/Pandas and compatibility arithmetic passing. An
intentional overall 12-second stop retains 47 chunks /6,016 entries; the next attempt
restores those and copies only 3,493 missing entries. Completed resume copies zero
source contents; its final inventory receipt stays unchanged. Outer/inner checksum,
missing prefix, wrong freeze and corrupted chunk failures preserve intended causes,
logs/returns/resource receipts. Original full prefix tree binding remains unchanged.
Native Linux mapping/locking, all ten modules/Torch and actual filtered workload/
throughput are still unverified. Native affinity is not available on Mac; local
copy CPU can exceed one while remaining a small software check. No UCloud cost
or proportional CPU speedup claim follows from these timings.


## Accepted v8 numerical runtime and restored native consumers, 2026-10-10

[Return review](linux-runtime-recovery-v8.json) verifies the successful Linux gate,
not a scientific result. All 86 accepted distributions, ten imports, local stdlib/
shared libraries, NumPy matmul and Torch backward pass; no original-prefix binary
was mapped, and no persistent bytecode was accessed/written. All 24 return members
/22 inventory hashes pass (1,036,210 immutable logical bytes /88,477 compressed).
The fresh numerical selection contains 18,977 of 44,770 entries /1,682,401,752 bytes;
25,793 entries /2,826,138,072 bytes were explicitly omitted. 151 retained chunks
contain 1,716,981,760 tar bytes plus final receipt/plan/member seals. Exact total
persistent storage was not returned. The original prefix was not edited.

Driver before collection: 161.307 s at declared 1 vCPU /4 GB /0.0448074 allocated
core-hours; /proc CPU affinity 0, sampled peak 460,787,712 bytes. Copy 143.613 s /
24.07 sampled CPU s; imports 13.670 s /7.95 CPU s; final byte verification 3.867 s /
3.61 CPU s. These are observed phase timings, not community affordability or linear
CPU scaling. After-collection/provider/idle costs are unknown; collection receipt
was not uploaded. V9 prints through-collection accounting in the live terminal.

The native attempt created all chunks; it did **not** test native restored resume.
Bulk chunks/final file inventory were not attached, so independent local review
verifies returned seals/receipts and executed worker checks, not remote content.
V9 must verify their exact final receipt, every seal/archive/member and complete
population while restoring, with no fallback to original source reads/copies.
The accepted inventory is reused; only per-job lexical identity and each tool's
new dependencies/origins are checked. Original scientific stages remain unrun.

The prepared v9 native preflight preserves the original eight-CPU /24-GB /
17,400-second work +600-second collection ceiling. It removes old arbitrary
substage caps for imports/features/install/help; real CPU/I-O or completed-byte/
entry activity guards coexist with the one overall clock. Quiet compute stays
active; parent heartbeats do not constitute progress. All children and parent
setup remain bounded. Original AMBER/mapping are still direct read-only bindings;
no portability/health credit follows from the numerical snapshot. New tool
execution venvs explicitly bind the job-local runtime and require new bindings
following job reset. Tiny CheckM console source is separately bound and invoked
through lexical Python; no old shebang/console PATH is used. Sources, modified
CompleteBin max-50, operational SCGBinner dtype and scientific defaults stay frozen.
Native assembly/mapping/evaluator and native five-tool feature/checkpoint contracts,
source-acquisition overlap, utility identity/health and full-scale affordability
remain unresolved until returned evidence. See [Operations](OPERATIONS.md).


Final v9 source `d57536746e47d2b3e82d5190ef90d0ae4c3308cc`, 6,698,794-byte
packet under `artifacts/e009-preparation/transfer-v9-reviewed/`. Forty-six checks
pass (45-suite plus actual local HTTP acquisition). The final exact packet/Bash/
driver outside checkout restores 9,509 retained Mac entries /75 chunks /zero
original source copies, creates its own venv/full inventory/origin probe and
executes tiny real native mapping/assembly/depth/competitive truth contracts.
Final driver 63.622 s, outer sampled peak 158,851,072 bytes. Persistent state is
unchanged. This is not native Linux throughput or eight-thread assembly evidence.

Earlier source `ff213c0` passed two identical consumer launches (65.723 /55.270 s,
<=319,401,984-byte sampled peak), actual own-wheel install/wrapper, post-install
numerical hash checks and retained failure/return contracts. Only acquisition
byte reports and their activity consumer changed in the final packet; all owner,
materializer, native and input bytes are identical. The new actual HTTP transfer
and advancing/repeated counter tests cover those changes; repeated driver/native
checks were limited to the changed final packet. The harness JSON-trailer parsing
error was corrected from retained successful stages. Initial sandbox ps failures
have no validation credit. Full logs/scopes/hashes are in [transfer.json](transfer.json).
Linux utility/tool/AMBER paths were not mocked and called passed; they remain
pending in the owner v9 preflight. No accepted science was repeated.


## Cancelled v9 and focused v10 repair, 2026-10-10

The [cancellation receipt](linux-cancellation-v9.json) binds the only uploaded
terminal log. All 151 chunks /18,977 entries were restored with zero original
source access, approximately nine seconds between stage announcements. AMBER's
four imports and inventory target reached `target ready` /`finished pid=644`;
the next code path silently hashes numerical/mapping/AMBER/source/marker directory
trees. The terminal alone does not prove which file was being hashed, supervisor
exit status, exact cancellation time or total cost. Timestamp span is at least
349 seconds /0.77556 allocated core-hours at 8 vCPU; the owner reports about five
additional silent minutes. No scientific work began. The working tree was clean
at inspection; no in-progress changes were lost. Original attempt/log/v9 packet,
E001 environment and accepted v8 chunks stay intact.

V10 removes those blanket before/after scans, retaining accepted member checks,
full inventory/origin probes and only 26 explicit external file bindings with
visible start/end and advancing byte reports. Successful child stages now announce
exit status before the next stage. Collection enumerates only this attempt rather
than all prior environments/chunks/shared sources. It honestly reports the narrower
assurance scope. [D006](../../docs/decisions/D006-environment-ownership.md) explains
why simplified reuse is the bounded choice over five new numerical Conda builds.
Scientific design and all accepted science remain unchanged. The corrected packet
and exact command are owned by [Operations](OPERATIONS.md) and
[transfer.json](transfer.json). Linux continuation beyond AMBER remains unverified.

Final v10 packet binds source `5a780e411f0b4c1b78409db7270338b45ac80039`,
6,699,717 bytes, SHA256 `25b9a12492329041fca6bd126fe2daf3e45b079c6b6963aaac8390c76663103c`.
All 49 regressions pass (40.197 s). Exact packet/Bash/driver restores 9,509
real Mac entries /75 retained chunks, creates its own bound venv, verifies complete
inventories/origins and passes real tiny native mapping/one-thread assembly/depth/
truth contracts; 69.395 s through collection, outer sampled peak 366,776,320 bytes.
The actual transferred scoped-binding helper reads all 26 declared inputs in
0.633 s, real mapping binaries/pinned AMBER sources plus synthetic CheckM hashing
inputs. Before/after file/path identities pass; original Mac state is unchanged.
Fixture/hash contracts do not establish native CheckM or full Linux execution.
No accepted science repeated. [transfer.json](transfer.json) binds complete logs,
command/archive/source and explicit Linux omissions; previous packets stay intact.


## Accepted v10 stages and two-path v14 recovery, 2026-10-10

[Independent return review](linux-preflight-v10.json) verifies SHA256/all 340
archive members and 338 retained hashes /39,835,306 immutable logical bytes.
SemiBin, MetaCAT and CompleteBin contracts pass; eight-thread Linux MEGAHIT,
ordered mapping/depth, competitive truth and AMBER/confirmed R95 software tests
pass. Runtime restores all accepted v8 chunks; numerical/per-tool inventories
and 26 explicit external before/after identities pass. CompleteBin remains max-50;
SCGBinner's accepted dtype patch remains. **No community fit or E009 score ran.**

SCGBinner fails at shared sklearn1.9.0's missing private stable_cumsum import;
COMEBin's own full help passes, but CheckM lacks pruned checkm.test. Preserve both
failures and all passed stages. New independent SCGBinner/CheckM Conda recipes
are selected for only those failed paths, with actual compatibility probes rather
than assuming environment creation fixes them. [D006](../../docs/decisions/D006-environment-ownership.md)
records requirements/alternatives and [failed-paths-lock.json](failed-paths-lock.json)
binds 118 SCGBinner/98 CheckM Linux packages including all-Conda CPU Torch (577.1 MB
compressed before deduplication). COMEBin's main numerical recipe stays unchanged;
complete CheckM runs under its own interpreter/libraries. No E001/v8/v10 mutation.

Actual cost through collection: **456.278 s /1.01395 allocated core-hours at 8 vCPU
/24 GB**, peak stage sampled RSS **1,363,578,880 bytes**. Provider billing/idle is
unknown. Attempt precollection files are 381.482 MB, return compressed 5.415 MB;
separate prefixes/caches/source data are outside that attempt storage scope.
Source genome acquisition SHA is 9a0373b6a42f7322583b1c091059b513d8d62bd5be2e57244ac19b50b1f4f69a,
3,202,310,417 bytes, catalog 2,078 source files /65,571 records /10,251,869,096 bp.
Returned canonical/accession comparisons find zero exact development matches;
this does not establish unseen-pretraining or near-genome independence. Heavy
source bytes remain remotely receipt-bound and are not redownloaded/rehashed.

V14 schedules only SCGBinner/COMEBin native contracts, reusing exact tiny ordered
BAMs, pinned source archives and the accepted utility prefix. The other three tools,
assembly/mapping/truth/evaluator/source download/catalog are not scheduled. New
uniquely named corrected prefixes and attempts preserve old outputs. Proposed
8-vCPU/24-GB three-hour allocation, 10,200 seconds work +600 collection, sampled
20-GB RSS, no lower stage caps; cold Linux timing remains unknown. Local tests
and transfer identities belong to [transfer.json](transfer.json); exact owner
command and Linux limitations belong to [Operations](OPERATIONS.md).

### Local recipe correction before transfer

Preserve source a6e88c3 and the rejected v11 packet/local attempt. The first mixed
Conda/pip Torch2.0 Mac recipe imported but crashed during native thread setup;
this does not establish the lower-level cause or Linux failure. The corrected
all-Conda CPU Torch2.0 build104 stack successfully sets four threads, with CUDA
absent. Exact Conda identities and executed distribution versions are both bound
(the Torch Python distribution is 2.0.0.post104). COMEBin's old Mac Torch2.2 cannot
import its modern training AMP entry point; reuse accepted v10 full Linux help and
execute the identical augmentation API/default parser rather than patch training.
A local observer test also found a queued shutdown SIGUSR1 race; retain its failed
log and fix the signal restoration, with active hang dumps still required.
Final local native results and unchanged-receipt checks belong in transfer.json;
new Linux installs/native dependencies remain pending owner evidence.

The v12 local packet passed SCGBinner's actual full help, augmentation writer and
reader, finite features, seeded initializer and HNSW limit. Its COMEBin path then
exposed CheckM1.2.3's unsupported top-level --help (exit2); this was caught locally
and never handed to the owner. V14 probes lineage_wf -h instead, with the complete
owned package. The Linux retry also checks owned HMMER/Prodigal/pplacer entry
points without a fit; those platform-specific checks remain pending locally.

The v13 exact packet/owner command passed both corrected native contracts locally
(137.380 s through collection, outer harness157.293 s /642.630 MB sampled peak;
Mac platform/install substitutions remain explicit). Preserve that positive packet.
Final v14 increases only the cold-install allocation to three hours and free Home
floor to10 GB after inspecting actual Linux payloads: 94,327 cache/prefix payload
paths, 497.171 MB deduplicated download and >=7.45 GB cache/prefix/compressed bytes.
The old filesystem copy-rate comparison alone is ~105 min, with Conda throughput
unmeasured. [linux-package-inventory-v14.json](linux-package-inventory-v14.json)
owns that provisioning evidence; there is no new stage timeout or native/scientific
algorithm change. Final packet/harness provenance belongs in transfer.json.

### Final v14 local acceptance

[Local evidence](local-failed-paths-v14.json) binds the exact final archive and
Bash command, real tiny FASTA/BAM contracts, own-prefix inventories, native writer/
reader outputs and all 122 immutable return members. Both corrected contracts
pass; prior accepted receipts are byte-identical, and all three passed tools plus
assembly/mapping/truth/AMBER/source catalog remain unscheduled. Actual Mac driver
through collection128.946 s, outer harness145.042 s, outer sampled peak665,939,968
bytes; sampled CPU146.11 s. These are local warm-runtime measurements, not Linux
cold-install forecasts or UCloud spend. All53 E009 regression tests and documentation
checks pass. The final Linux install/new binding/native entry/eight-CPU checks still
require the owner return. No full community fits, E009 scores or scientific changes.

## Accepted v14 return and current GCP preparation — 2026-10-14

[V14 independent receipt](linux-preflight-v14.json) verifies SHA256
`c6f2c4df856c7e80031cb84b47e7f82297f0d56c924d57b86d53d9696c673ff3`,
all 174 regular archive members, 172 retained hashes, source freeze/locked recipes,
terminal status/collection and zero exits for all 16 actual stages. The terminal
snapshot and inventory are bound separately; archived payload is 8,352,269 bytes,
not the growing external log. Actual finite COMEBin arrays/contig/sample axes were
read independently; original v10 reference/BAM identities match exactly.

SCGBinner's complete owned Python3.10/NumPy1.26.4/pandas1.5.3/sklearn1.6.1/CPU
Torch2.0.0.post104 imports, full help, actual augmentation/reader/initializer/HNSW
pass. Complete owned CheckM1.2.3 imports `checkm.test.test_ecoli`; lineage help and
HMMER/Prodigal/pplacer entry points pass. COMEBin's real augmentation and feature
reader pass on the unchanged bound numerical recipe; full help is reused.
All three formerly passed tools and utility/assembly/depth/truth/AMBER/source
contracts stay unscheduled/accepted. Restore uses 151 sealed chunks, zero original
recopy/access. Eight CPUs, loader zero and isolated actual import origins remain
explicit. These are tiny software contracts, not training, grid, lineage placement,
GCP runtime health or scientific results.

Actual cost through collection: 211.421995 s /0.469826655 allocated vCPU-hours,
8-vCPU/24-GB allocation, peak sampled stage RSS 3,724,357,632 bytes. Precollection
attempt snapshot: 62,276,326 logical file bytes. Separate prefixes/caches/source
DNA/provider idle are outside that scope; no GCP bill is inferred.

The ten-source protocol, serial real-worker DAG and complete independent data
recipe are now prepared for separately approved direct GCP execution. Local
[validation](gcp-local-validation.json) owns native fixture paths, preserved
failures, resume/axis contracts and precise omissions. Reconcile positive read
origins, genome/replicon grouping and cellular target taxonomy before final truth
admission; provisional alignment truth is not a frozen scoring denominator.
No VM start, provision, scientific acquisition/assembly/mapping/truth, binner fit,
quality score, architecture change or accepted science replay ran in this task.
