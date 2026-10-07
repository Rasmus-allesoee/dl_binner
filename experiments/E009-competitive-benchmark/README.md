# E009: first competitive human-gut assembly benchmark

Opened: 2026-10-08. Execution: **planned**, not launched. Scientific outcome:
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
  our product. Absent depth is not fabricated zeros. This second pair addresses
  the still-unresolved coverage question; no new architecture is involved.

All four partitions retain the same complete input DNA, exclusions/masks and
unassigned outcomes. Raw versus learned isolates the learning pipeline under
fixed inputs/geometry/clustering, including its saved transforms; it is not a
controlled comparison of every embedding normalization decision. Depth versus
sequence changes the declared information contract, keeping scientific defaults.

External shortlist: **SemiBin2 short-read self-supervised, MetaCAT core CPU,
SCGBinner native**; **CompleteBin conditional fourth** if its full current native
CPU recipe and payload fit the pre-scoring resource check. One configuration and
one attempt per tool; native data-dependent schedule/eligibility/selection retained.
No reduction of SCGBinner's 200-epoch maximum or CompleteBin's resolved schedule
to rescue a failing budget and label it native parity. Early stops already built
into a pinned tool are legitimate and recorded. CompleteBin pretraining may
automatically switch off: report that outcome rather than forcing a desired label.

SCGBinner is prioritized as a biological-constraint challenger despite long-read
emphasis; SemiBin2 is a mature short-read reference; MetaCAT adds a distinct
CPU-oriented grouping route. CompleteBin retains the thesis's strongest tool and
context/pretraining comparison without presuming affordable CPU execution.
COMEBin is studied/reused as measured E001 evidence but deferred from this larger
first execution because of its full CPU/grid cost and overlapping contrastive/
marker role. DCVBin's unresolved payload/continued-pretraining parity and LorBin's
long-read/model/thread contracts defer execution, not their relevant mechanisms.
Do not automatically replace unavailable tools or add VAMB/MetaBAT2. This is a
focused competitive baseline, not coverage of every current SOTA method.

## Data and immutable axes

Choose **CAMI III Toy Longitudinal Human Gut, short-read sample 0** as the single
assembly target. **Sample 1** is its second-time-point depth source from subject S1.
The downloaded corrected subject table verifies this pairing. Subject selection
uses the first listed subject, not genome abundance, quality or anticipated rank.
Use full published reads, no truth-selected read subset, genome filtering or
artificial fragmentation. Each short-read sample is advertised as about 5 Gbp;
two compressed archives total 9.732 GB. Keep other subjects outside this milestone;
they are not certified unseen-genome holdouts because source overlap is unresolved.

Build **one MEGAHIT read-derived sample-0 assembly**, default metagenome recipe
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
all IDs/lengths/strata, ordered BAM/depth manifest and native eligibility. Current
HEAD receipts do not verify payload integrity. Source taxonomy is the toy dataset's
2025-08-01 snapshot, not the active challenge's 2026 taxonomy.

Inspect source-genome accession aliases, per-replicon canonical DNA hashes and
near-genome overlap against retained E001/E002/E003/E004/E005 and real software
smoke sources. Record matches at exact sequence/accession and species/strain
levels; do not remove them after scores. The preliminary source filenames already
show S. mutans species overlap with E003, but exact overlap is **unresolved**.
Record source assembly completeness/isolate/MAG status and chromosome/plasmid
membership. Public-genome pretraining/database overlap is possible/unknown for
reference-informed tools. This is new-sample/assembly evidence; no unseen-species
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

Use established **MetaQUAST reference alignments/misassembly evidence** with
explicit supplied source references (disable automatic reference discovery), and
the retained pinned **AMBER** API/options (`filter_tail_percentage=0`). The next
adapter milestone must pin/version-test the actual alignment outputs, retain
all competing hits, test orientation/coordinates, and validate a narrow interval
adapter before scientific execution. Do not apply GSA mappings to assembler IDs,
force a dominant label on a chimera, or import MAG-E's isolate-only defaults into
this source population without an audit. The unresolved adapter is an execution
dependency, not a completed evaluator/runtime claim.

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
  duplicates cannot inflate completeness. Best-bin ties use opaque bin IDs,
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
Linux tool feasibility from it. No integration was needed in this planning task.

**Owner UCloud:** first a separate 8-vCPU/24-GB setup/asset/runtime preflight,
then a recommended 16-vCPU/48-GB scientific job or resumable serial jobs following
returned preflight review. Working RSS ceilings are 20/40 GB respectively, with
parent/setup/native children inside the overall clock. CPU-only; no GPU presumed.
Protocol ceilings are safety/budget choices, not ordinary product maxima or runtime
forecasts. More CPUs may help some stages; no linear speedup claim is made.

The [budget](protocol.json) reserves at most **500 allocated vCPU-hours**, including
failed attempts, downloads/setup, collector time and idle driver time. Stage caps
sum to 472; 28 are a reserve, not permission for automatic retries. The dated 2,100
core-hour access record is not today's balance; confirm available owner budget
when preparing a job. Measured full-stage projections must fit before admitting
SCGBinner/CompleteBin. If not, report them resource-deferred before scoring; do not
shorten native science or spend beyond the cap to make the shortlist look complete.

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

Prospective new disk allowance: 200 GB including compressed reads/source (~13 GB),
decompressed reads, alignments, environments/payloads, failures and retained exports;
largest uncertainty is BAM/native temporary data. Inspect actual members/sizes first.
Do not delete old E001–E008 data or migrate colleagues' files. If reviewed size exceeds
allowance, stop before the heavy step and request a specific expansion decision.
No reference-population or read-subset change to satisfy storage silently.

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

## Exact next milestone and acceptance boundary

Implement/test the E009 **acquisition, source-overlap, assembly/depth/truth and
native runtime adapters** on tiny actual contracts; pin recipes/payloads and the
real alignment/evaluator semantics. Prepare a checksum-bound 8-vCPU/24-GB owner
preflight (≤5 hours including setup/collection) to inventory new assets and test
isolated Linux native paths. It must not fit full-community binners, rerun accepted
science or execute the GLM study. Review its return before preparing the 16-vCPU
assembly/scientific command and freezing actual manifests/projections. A healthy
prefix alone is insufficient full-schedule feasibility; admission also uses the
planned assembly's actual length/contig distribution and representative native timing.
No owner command is runnable yet: adapters, payload hashes, actual inputs and native
limits are not resolved by this planning commit.

Planning checks: maintained links/context hashes, recorded source-byte verification,
subject pairing, coverage schema/counts, budget arithmetic and unchanged product/source
tree. No product/scientific regression or inference is repeated solely for a prose plan.
Update this record with actual attempts and results only after evidence exists.

2026-10-08 planning verification: `python3 scripts/check_docs.py --check-context`
passes (54 maintained documents / 657 local links / 85 present fingerprints;
ten unavailable historical optional caches explicitly unverified). An independent
read-only audit verifies 79 recorded source/metadata/training-file byte bindings,
S1 pairing, 311/332/355 source-name counts, object-size arithmetic and the
472+28=500 core-hour ceiling. `git diff --check` passes; product/scientific code,
defaults, tests, workflows, environments and PROJECT_INTENT are unchanged.
These are planning checks, **not native adapter tests or Linux/scientific validation**.
