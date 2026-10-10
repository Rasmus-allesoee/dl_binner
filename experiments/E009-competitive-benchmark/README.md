# E009: first competitive human-gut assembly benchmark

Opened: 2026-10-08; amended 2026-10-09. Owner preflight: **v3 failed at initial runtime startup; v4 recovery prepared**, not executed. Scientific outcome:
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
  separately and capped at 24 allocated core-hours within the 48-core-hour product budget.

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
