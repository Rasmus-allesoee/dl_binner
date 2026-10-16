# E010: an integrated window/depth/marker prototype

Opened 2026-10-16. Status: **completed and independently reviewed on 2026-10-17**.
The native workflow succeeds; the whole candidate's conservative recovery is
below preserved dev3. [Review](review.json) owns acceptance, limitations, costs
and the one proposed next control. [Launch](native-observed.json) remains the
historical running observation, not current state.
[D015](../../docs/decisions/D015-coherent-prototype-upgrade.md) owns the rationale.

## Prospective design, fixed before implementation/results

Implement dev4 as a separate candidate CLI path, preserving dev3 algorithms,
defaults, wheel and all E009 evidence. PR #2 merged benchmark-planning head
`bd902f4721aa780338fe961feba4ed15e4d96141` into main at
`5bd59d774306f586c22b23a2f6ee36d64947d052`, whose parents are the unchanged dev3
main `5e54538d1799e8d2538621729400f33fbaf017b9` and that research head. New branch:
`codex/coherent-prototype`, subsequently renamed to `dev4-coherent-prototype`
without rewriting commits at the owner's request. The latter is the pushed/VM
branch. Product Linux CI passed; local E009 contracts passed
91 tests (one Linux /proc test explicitly unavailable on Mac). Local technical
review found no actionable issues; no independent approval/bot reply is claimed.

1. **Views.** Retain full ordered DNA, all length strata, depth columns, zero masks
   and exclusion reasons. For contigs >=2,000 bp, generate two independently
   seeded pairs of disjoint real windows, one from each parent half, each
   1,000–10,000 bp. Retain zero-based half-open coordinates and exact sequence
   hashes. Train on parents with usable window pairs; 500–1,999-bp contigs enter
   inference/grouping, not artificial split-positive training. Below the default
   500-bp cutoff/no usable composition stays explicitly excluded and exported;
   that configurable default is not a product performance claim. No new coverage:
   each window is conditioned on its **parent's measured mean depth**.
2. **Model.** Square-root TNF, fitted composition statistics and unit-normalized
   composition input; fitted log1p sample depth scaled by sqrt(sample count),
   preserving original zero masks. Composition MLP 136→256→128, depth MLP
   S→64→64 (absent/all-zero depth branch explicitly zero), fused MLP→128→64,
   LayerNorm/ReLU and L2 output. Symmetric NT-Xent on paired real windows plus a
   half-weight composition-only auxiliary NT-Xent to discourage an exclusively
   parent-depth shortcut. Twenty epochs, seed 11, batch 512, temperature .2,
   AdamW learning rate .001/weight decay .00001; no marker or taxonomy training,
   truth inputs, checkpoint selection or parameter grid. Other parents can be
   co-genomic negatives; chimeric parents can violate positive assumptions.
3. **Geometry/grouping.** Use the learned unit vectors directly: cosine ordering
   equals Euclidean ordering on the unit sphere. No population z-score after
   learning. Build one sparse 30-neighbor graph with PyNNDescent, exact candidate
   reranking, symmetric positive locally scaled weights; small <=2,048-row
   contracts use bounded exact neighbors. Fixed SHA-selected exact audit queries
   must achieve mean tie-aware recall >=.90 across the fixed query panel; retain
   its minimum query recall too. Otherwise fail without a new search/retry.
   Leiden RB configuration partition, resolution 1, seed 11, two iterations;
   no truth K, candidate grid or marker-selected score. Groups below two contigs
   or 10 kb stay accounted unassigned. Preserve native neighbors and sparse graph.
4. **Markers/refinement.** Own native Pyrodigal meta gene calls and PyHMMER trusted
   cutoff searches with >=.5 HMM coverage, supplied hash/version/license-bound
   SCG profile asset. Cache genes, domains, chosen evidence and skipped/ambiguous
   calls by complete FASTA/asset/policy/runtime identity. No external binner.
   Deduplicate overlapping hits and ambiguous same-protein family assignments;
   same-contig duplicated markers are explicitly unreliable for constraints.
   In a pre-bin, split only on at least two independent clean repeated marker
   families whose distinct-contig conflicts support separation. Use the most
   repeated clean family as deterministic seeds for constrained spherical
   refinement; at most 10 iterations. Ambiguous/no-confident-affinity assignments
   may remain unassigned. Keep unsplittable/unreliable evidence explicit, never
   claim marker absence is genome absence or discard marker-negative DNA.
   Preserve both pre/post partitions and exports, including every DNA record.

These defaults are engineering priors informed by the completed source/literature
review and E009, not independently established optimal settings. Alternatives
(marker training, taxonomy, GLM, context attention, assembly graphs and ensembles)
remain deferred. Candidate-vs-dev3 will establish a bundle result. Pre/post
refinement is the cheap paired diagnostic; another fit ablation requires a
decision-changing uncertainty. No factorial campaign is required.

## Contracts and execution boundary

Local checks: independent owned CPU environment; native tiny DNA-window, training,
reload, approximate/exact-neighbor, marker cache/refinement and complete export
contracts; built wheel tested outside checkout; wheel/sdist/rebuild inspection.
Retain failed attempts and distinguish actual native paths from substituted tests.
Cheap engineering fixtures do not establish biological accuracy/full-scale cost.
Keep truth outside the training/feature CLI and use admitted v2 and independent
sequence truth only during later authorized evaluation.

The first community comparison will reuse E009's full sample-0 assembly and
ordered samples 0,2,3,4,6,9,10,11,14,17; reuse accepted dev3 outputs without a refit.
Before changed scores, freeze additional confirmation inputs/protocol and preserve
their development/source overlap limitations. No data acquisition in this task.
Resource/cost bounds and the exact future approval prompt will be added after
local engineering checks. Prior $20/$2 authorizations do not carry over.
Existing cloud storage retention review remains **2026-10-21**; no extension.

## Local engineering outcome and limits

The prospective design was committed as `e0ff20f` before implementation. Dev4 is
the new `candidate` CLI; original scientific dev3 files/defaults remain byte
identical. [The candidate lock](candidate-lock.json) binds all 18 package/default
members, the tested 54,811-byte wheel, full accepted E009 DNA/depth and ordered ten
sample columns, the 111-profile/107-canonical-family marker asset, runtime recipes
and prospective confirmation protocol. The final rebuilt wheel has identical
logical contents to the actual tested wheel; source-only metadata/tests updates
are separately inspected in the final sdist. No accepted stage was replayed.

Final installed suite: **21 tests pass**, native Mac x86_64/Python3.10, owned
independent CPU closure, two numerical threads/loader zero, 8-GB test safeguard.
Outer measured suite clock **167.983 s**, sampled peak **646,209,536 bytes**;
the unittest-internal clock is 147.179 s. Setup/import/build/review are separate,
not an exact end-to-end task or provider cost. A further focused eight-test pass
retains inspectable tiny artifacts after adding retention/snapshot contracts:
**77.576 s /516,485,120-byte sampled peak**. These are software fixtures, not
assembly-scale forecasts. Complete owned numerical inventories/import origins
and separate tensor/graph/marker runtime probes pass; no borrowed dependencies.

Independent retained-artifact review verifies **15 contigs /37,312 bp**, six length
strata, actual DNA-window coordinates/hashes, ordered depth/zero masks, seven serial
stage receipts, exact pre-save/reloaded arrays and both complete DNA exports.
Both reduced 2-epoch/8-D and **packaged default 20-epoch/64-D** paths pass; default
training uses six real-window parents, leaving short DNA in inference/export.
One/no-depth fusion has native finite-loss/gradient and zero-branch contracts.
The native 512-row approximate-index fixture passes fixed 24-query tie-aware
recall 1.0; full-community recall/throughput remain unmeasured. Hand-counted
refinement fixtures cover two-family splits, marker-negative assignments,
ambiguous noise, insufficient evidence, multicopy/alias/ambiguous protein calls.

The real production-profile adapter reads all 111 trusted-cutoff models, detects
the generated PGK-consensus software positive and re-derives its cache from raw
gene/domain records. This is not an empirical marker-availability result. The
earlier retained 59-kB fixture produced no qualifying hits and its positive-hit
assertion failed; that failure is preserved, not reclassified as success or used
to relax cutoffs. The generated positive is an explicit replacement *fixture*,
with unchanged production trusted cutoffs and >=.5 model coverage. Full E009 marker
availability/multicopy behavior must be reported in the next run before claiming
that refinement helped. `scripts/e010_marker_contract.py` prepares the same real
native production-profile gate for the future Linux runtime.

The initial failed wheel/str-translation contracts, sandbox-denied PR tests,
crash-interrupted log, obsolete build-tree leakage and mixed-OpenMP inventory
warning are retained. Repairs use the native string API, fresh build snapshots
and process isolation, not placeholder dependencies or suppressed library errors.
No executed prefix was upgraded: three independent version-qualified candidate
prefixes and a separate builder remain local. The protected source/tool caches,
dev3 environments, E009 inputs/truth/results and failed journals stay unchanged.

**Six launcher/phase tests pass** with real inert native children, serial failure
handling and archive/member readback checks. Only Cloud Storage transport, guest
status publishing and the local disk-capacity sensor are substituted in the phase
fixture; no cloud verification or scientific execution is claimed. At that local-only cutoff, the E010 Linux/Python3.12 environment, mount/RAM,
live held-process/watchdog/STOP and credit/headroom gates were unexecuted
prerequisites; the later native phase below owns new observations. The
ordinary product suite has no ignored research assets/helpers or mocked workers.

[Operations](OPERATIONS.md) owns the new **$2** proposal (estimated 1–2.5 hours,
existing VM/disks, 4-hour cumulative clock, 4.25-hour STOP, 25-GiB reserve and
20-GiB extra cap), selective bundle/pre-post diagnostics and exact approval prompt.
No new cloud spending was initiated; existing provisioned-disk billing continues.
See [local-observed.json](local-observed.json) for byte/resource evidence and the local archive locator;
that local archive is not a remote backup. Native Linux and community quality are
not inferred from these local checks.

Implementation source is frozen at `d15c95a30c219b64a32a280e248bf167423629e2`.
The local evidence archive is **6,189,207 bytes**, SHA256
`938fade66110686fb39b808d921652aeb53ce506b905d8687bdf0c9cf0b51176`;
all **1,405 regular members /13,947,258 logical bytes**, including its inventory,
verify. It excludes numerical/build prefixes (about **3.4 GiB** rounded local
allocated disk). Existing accepted E009 evidence is not repackaged or modified.

## First native phase, 2026-10-16

The owner subsequently authorized one frozen candidate under a **new $2 gross**
ceiling. [The native receipt](native-observed.json) and [operations](OPERATIONS.md)
own the actual conditional credit admission, exact source/branch sync, full input
verification, fresh independent Python 3.12 runtime, native gates, boot/process-bound
watchdog and provider STOP. Existing VM/disks only; no resize/provisioning, external
binner, refit of dev3, acquisition/mapping/truth replay or retention extension.
The healthy launcher may outlast this task; its launch observation is not accepted
community output or a new E009 score. Final cost needs independent provider stop.
The original local evidence above remains a dated engineering result.

## Completed native result and independent review, 2026-10-17

All seven stages completed at source 6917c3f, seed 11/20 epochs, on the unchanged
8-vCPU/32-GiB VM. GCP stop **October 16 21:47:33.061 UTC /23:47 Copenhagen** is
independent of matching guest/private SUCCESS receipts. Private science archive
**335,636,093 bytes**, SHA256 `3ec883477ce6c9e070632200508be8b707e84a11938f51e6221089eb94d165a3`;
all **692 members /763,504,773 logical bytes** verify against the bound inventory
and archive, including the inventory itself. Closure
archive 99,386 bytes /32 members is checksum-bound and independently inventoried.
No VM wake, original-data replay, new fit or external binner ran in this review.

The compact independent review is also privately archived and readback-verified:
`gs://dl-binner-archive-167650584170/e010/candidate-6917c3f-20261016T212549Z/review-20261017/review-evidence-v1.tar.gz`,
2,275,305 bytes, SHA256 `bf04bb1a3bb945b8ed28493d85f5dad06f2d6d8f73eab0d5ada3aa48e7e79c63`.
All 140 members /11,348,764 logical bytes verify, including failed review journals,
executed source versions, raw diagnostics, closed logs and a pre-archive snapshot
of [the review receipt](review.json). The final receipt binds its archive locator
without a self-referential checksum. Numerical environments/auth caches/native
bulk and the collector's open terminal log are excluded.

The reader verifies full 145,702 IDs /231,678,157 bp, all 1,457,020 ordered ten-depth
cells, 13 zero rows, baseline-identical parent TNF/eligibility and every **54,216
actual window** hash/coordinate from 13,554 training parents. Parent mean depth
remains conditioning, not window coverage. All 18 native installed source/default
members, pinned runtime, 20-epoch histories and seven serial receipt chains pass.
Native pre-save and independently reloaded arrays are bitwise equal. All 1,821,900
sparse weights independently match unit-cosine/local-scale arithmetic (max absolute
error 4.84e-14); the native 64-query audit and independent 128-query audit have mean
recall 1.0, with no unqueried-recall guarantee. There is no post-learning z-score.

The strict Mac inference check **did fail** unchanged rtol1e-5/atol2e-6 at four of
9,324,928 coordinates (maximum 3.135e-6, evidence masks identical). Disabling MKLDNN
did not explain it. Preserve that portability limitation and failed v1 reader;
we did not widen tolerance, refit or substitute vectors. Subsequent diagnostics
explicitly consume original Linux artifacts, with independently passing native
input/output/reload/geometry contracts. A separate reader-v2 failure assumed
ascending numeric edge indices; the writer actually sorts opaque IDs then maps
to FASTA rows. The adapter was corrected and tested on unsorted IDs/refusals;
no native output changed. Failed source snapshots match their pre-run hashes.

Five new reader/diagnostic contracts, reused diagnostic/truth-evaluator contracts
and the actual pinned AMBER API pass. The main local retained review took 59.137 s,
sampled peak 1.526 GB under 4 threads/8 GB/15 min; AMBER 47.906 s /0.554 GB in its separate
unchanged environment. No workers were mocked in the retained review or evaluation.

The primary endpoint below uses >=200 kb bins at >=95% confirmed source support,
all-bin DNA purity and full provided bacterial references (156 targets /
554,661,890 bp), with duplicate-safe loci. It is conservative provided-reference
recovery, not formal MIMAG quality. Available confirmed source union is 18.5321%;
3.3034% N-quarantined DNA and all unknown/non-target/zero-origin competitors remain.
Accepted dev3 values are reused, without refitting/rescoring its outputs.

| Frozen output | Weighted R95 | Macro R95 | Targets >=50% | Targets >=90% |
| --- | ---: | ---: | ---: | ---: |
| dev3 raw TNF+ten depth | 4.5765% | 4.9838% | 6 | 1 |
| dev3 learned TNF+ten depth | **5.3911%** | **6.0264%** | **13** | 1 |
| dev3 raw TNF only | 3.9312% | 4.5794% | 5 | 1 |
| dev3 learned TNF only | 4.5597% | 5.5352% | 11 | 1 |
| dev4 pre-refinement | 1.8763% | 2.1214% | 3 | 1 |
| dev4 post-refinement | 4.2909% | 4.2787% | 6 | **2** |

**The integrated candidate does not establish a stronger whole binner.**
Refinement improves its fixed representation by 2.4146 percentage points, but the
bundle remains 1.1002 points below learned dev3. Post versus pre improves recovered
bp for 6 targets and worsens 1; versus dev3 improves 10 and worsens 13. Do not select
only the two >=90% targets or better geometry to claim a win.

Bacterial 5-NN agreement on the identical 25,543-query population rises 67.05→72.59%,
but bp-weighted agreement falls 79.62→78.73%. The >=10 kb stratum falls 81.79→79.40%,
while 500–767 bp rises 63.27→71.65%. Overall 88.18% neighbor agreement is not a primary
cellular target result. Bacterial restricted B3 precision/recall are 41.41/70.92%
pre, 63.50/49.52% post, versus dev3's 62.29/37.61%; restricted attribution excludes
unknown bin DNA, whereas R95 purity includes it. Native AMBER assigned restricted
bp-purity 69.55→86.89% also must not replace the full-bin denominator.

Before refinement, 35 bins assign 89,041 contigs /209,642,703 bp. Afterward, 73 bins
assign 80,186 /189,143,689 bp, with 8,855 /20,499,014 bp newly unassigned and the same
56,661 /22,035,454 bp below 500 excluded. Every DNA record survives both exports.
The dropped DNA includes 8,485,927 confirmed bacterial bp and 169 >=10kb contigs /
7,190,680 bp. Marker-negative dropped contigs 8,615 are retained, not discarded.

Native cache: 298,955 genes /3,462 domains; 111 profiles /107 canonical families;
1,631 clean-marker contigs, including 86 below 500. Separately, 38 same-contig
multicopy-family cases are unreliable; no multi-family proteins were reported.
All retained gene coordinates, coverage >=.5 and trusted domain score thresholds
verify without redetection.
Marker-bearing eligible contigs are only 1,545/89,041. Eighteen of 22 recorded split
attempts are adopted; four bins retain single-family unresolved conflicts.
A previously 95%-pure source grouping can still lose recovery: ASV399.6 drops
1,288,186 recovered bp after refinement. Markers are evidence with failure modes.

A 35.103 Mb bacterial-dominant pre-bin contains 107 supported genomes and 17.18%
dominant support. Even after refinement, 45/57 large bacterial-dominant bins are
below 95% confirmed purity. This supports **one cheap cached grouping-objective
control**, not proof that grouping is the only problem. Prepare a fixed
CPM-versus-current-RB objective on the same graph/weights, with encoder and marker
refinement unchanged. CPM's density parameter has a different meaning from RB's
resolution; freeze one label-free rule using [the primary API/formula](https://leidenalg.readthedocs.io/en/stable/reference.html#cpmvertexpartition),
not a truth-score grid. Long-contig representation and refinement losses remain
serious alternatives. No changed partition or new execution occurs here. A later
useful fixed mechanism must be confirmed on the prospectively frozen oral GSA,
after separate source/truth/overlap and cost admission. No feature-family/SOTA claim.

Actual VM uptime 1,303.115 s costs ~$0.09884 compute/IP; disk interval ~$0.01547;
335.7 MB compact export upper~$0.03752; prior asset readbacks~$0.00250 plus small
storage/operations. Total~$0.1543 before small charges,<$0.19 with reserve, within
$2; delayed net 0 is not an invoice. Candidate 777.832 s, largest sampled phase
RSS 2.694 GB. Markers 575.741 s dominate; training itself 18.265 s. Allocated uptime
prices are separate from sampled CPU. Sampled candidate/collection filesystem
peak 162.69 GiB /minimum free 132.28 GiB, charged growth 3.41 GiB including early 1 GiB
padding; later outer readback adds 335.6 MB outside persisted sample scope. No new
capacity is needed. Existing disks cost $31.20/month while stopped; **October 21**
review and original retention approval remain, without extension.
