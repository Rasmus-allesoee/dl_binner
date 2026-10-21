# E017: information-aware long cores and conservative recruitment

Status: **completed, checksum-verified and independently reviewed; MODIFY**.
Updated: 2026-10-21. Branch: `e017-information-aware-grouping`.
[Comparison](comparison-review.json), [all 955 target rows](comparison-targets.tsv),
[inspection](inspection-observed.json) and [operations](OPERATIONS.md) own results,
limits, actual costs and the next proposed control. Native source `e78d766` is a
launcher-only descendant of prepared `067ceb2`; both freezes, dev3/dev4/dev5/E016,
all accepted inputs/truth/results and failed journals remain intact. The local
[reader repair](review-repair-lock.json) adapts actual compact writer schemas; it
does not change native science, vectors, thresholds or the failed Mac tolerance.

## Reviewed development result

| Partition | E009 conservative-v2 weighted R95 | Oral provided-origin weighted R95 |
| --- | ---: | ---: |
| Retained E016 post | 5.8219% | 6.7719% |
| E017 long cores | 5.9718% | 1.9045% |
| E017 recruited parent | 7.0741% | 1.9449% |
| E017 old refinement | 7.5284% | 3.5481% |
| E017 E013 post | **7.5284%** | **4.9664%** |

The original **MODIFY** rule applies: E009 gains **9,465,205 recovered bp**
(14 target gains / 9 losses; >=90% targets 4 → 8), while oral loses
**37,609,955 bp** (23 gains / 45 losses; >=90% targets 34 → 21). No global default
is promoted and no per-dataset/per-bin oracle chooses between E016 and E017.
E009 remains below the retained native MetaBAT2 8.5493% reference, with different
native length eligibility. All full 156 / 799 reference denominators stay fixed;
3.3034% E009 N-quarantine and oral known-shared sensitivity remain visible.

All DNA is accounted. Post unassigned DNA rises **2.376 → 59.748 Mb** in E009 and
**11.584 → 410.547 Mb** in oral; excluded DNA is unchanged at 22,035,454 and
226,153,459 bp. Core/recruited/old/E013 tables retain every short, marker-negative,
unknown/non-target and excluded/unassigned row. Fixed learned-neighbor metrics
exactly match E016; the new joint-core retrieval is a different population.
Oral core mixing is substantial (183 / 207 large core bins below 95% supported
origin purity). E013 adds 62,940,105 recovered bp over its oral parent but does not
restore E016. More conservative assignment has not made all remaining bins pure.

The saved gates expose a concrete inconsistency worth one selective control.
Existing distance-first ranking plus margin rejects rows even when a cached core
candidate meets **all existing** profile <=1, >=2 supporters and >=2/3 weighted-vote
conditions: **13,635 E009 contigs / 14,456,937 bp**, **99,067 oral contigs /
95,981,333 bp**. This is a label-free census, not a replacement partition or a
recovery prediction. Most ambiguous-margin rows also fail other checks; dropping
that margin alone would expose only 39,239,154 oral bp. Core mixing also remains.

**Next recommendation:** prepare one cached, vote-led/profile-admissibility
control, keeping E017 cores/graph/profiles/learning fixed. A unique candidate with
>=2/3 existing core vote, >=2 distinct supporters and existing profile score <=1
may recruit; no cross-bin profile-distance ranking or runner margin veto. Reject
when none is admissible. No threshold grid or truth-selected routing. This changes
one coherent ranking/acceptance mechanism and can decide whether competing rankers
are needlessly losing supported DNA. It may instead reveal that abstention protects
purity. This specific saved-gate evidence justifies the cheap control before a
larger encoder/context/GLM block; it does not prove such information is unnecessary.
[Operations](OPERATIONS.md#exact-following-prompt) proposes a fresh **$1** native
control, not enacted during this inspection. Skin confirmation stays unacquired.

## Verified execution and resources

VM start **01:26:31.522**, provider stop **01:57:35.627 Copenhagen, October 21**:
**1,864.105 seconds / 31.07 minutes** at 8 vCPU / 32 GiB. All nine Linux gates,
eight serial scientific rules plus final target, reuse-after, collection and all
three upload/readback pairs pass. Private/guest completion hashes agree; matching
boot/PID/start/command watchdog requested shutdown at 01:55. STOP is independently
verified; no new VM job, resource change or retention extension occurs in review.

Archive **1,055,048,062 bytes / 245 members / 1,835,035,318 logical bytes**, SHA256
`7b45916a0b7bd2dc938595c40a501af97ae8d1585a67b23b34103f985a6ca5fc`.
All member, sparse-cache, candidate/profile/vote/reason, full-axis and complete
assignment contracts pass. Native before/after reuse verifies 72 files /
6,041,240,299 bytes. Native science takes 1,238.96 seconds, sampled CPU 1,389.23
seconds, sampled tree RSS 9.347 GB; the charged allocation is 4.1425 vCPU-hours.
Sampled maximum filesystem growth is 5.567 GiB, minimum free 84.671 GiB.

Measured-uptime/current-SKU gross quotes: compute/IP **$0.141385**, run disks
**$0.021714**, archive export **$0.117911**, compact evidence/operations small:
about **$0.282**, **below $0.54 with reserve**, within original $2. These are not a
reconciled invoice or credit-delta attribution. Idle disk cost is separate within
the approved $8 interval, not charged twice. Fresh Welcome credit is DKK 1,893.83
Available through January 12, 2027; delayed usage remains unknown/reserved.
Stopped disks still cost $31.20/month; October 28 at 00:00 Copenhagen is the next
retention boundary. No original budget becomes a future execution entitlement.

The one-hour local review uses four numerical threads, 8 GB sampled RSS and
<=6 GiB extra work. Thirteen frozen evaluator tests, three adapter refusal tests,
two actual retained tiny formats and the actual E009 membership reader pass.
Two failed pre-score adapter journals remain: legacy full-list guard, then an
incorrect expectation of metadata omitted by the unchanged old/E013 writers.
Exact emitted schemas/source/receipt bindings resolve them without editing data
or weakening membership/coordinate/purity contracts. Local peaks/elapsed and the
compact local review seal are bound by the inspection receipt. The optional new
private backup was blocked by automatic approval review because payload upload was
not explicit in this inspection scope; owner approval is pending. No upload
workaround or new scientific execution occurred. Existing native archives remain
privately retained and fully verified.

## Frozen design and historical local preparation

Use >=2,500 bp cores with retained learned vectors, raw Hellinger composition and
available measured parent means. One joint learned/composition index supplies
candidates; depth reranks available evidence. Explicit background agreement and
finite-length reliability weight the core graph, followed by the sole CPM rule.
Freeze core profiles, recruit shorter/unsupported eligible contigs once using
spread, margin and positive support, then apply unchanged E013 refinement. Keep
all core/recruited/old/E013 alternatives and all DNA. No truth K, label-selected
threshold, marker cannot-link, window coverage variance or new learning is added.

This is an unvalidated grouping bundle. The empirical profile envelopes and
length factors are heuristics; a mixed core can recruit incorrectly, a long-core
requirement can miss fragmented genomes, and mean-only depth does not establish
coverage uncertainty. Candidate recall is sampled, not a universal exact-neighbor
claim. The mixed development quality result is above; generalization remains unassessed.

## Length eligibility and retained reference

The [native eligibility audit](eligibility-audit.json) confirms MetaBAT2 2.18's
main default of 2,500 bp (allowed >=1,500), separate default recruitment from
1,000 bp (allowed >=500), plus depth filters. Its actual accepted E011 log has
9,812 large and 27,307 small candidate contigs; 113,891,385 large-contig bp and
102,650 short-contig bp were binned. Our E016 learner admitted >=500 bp, 89,041
E009 contigs. Thus this is a **native whole-tool reference**, not equal eligibility
or a cutoff/encoder ablation. The full provided-reference denominator stays fixed;
we do not retroactively filter or rescore either method.

| Retained label-free axes | E009 ten-depth | Oral sequence-only |
| --- | ---: | ---: |
| All input contigs | 145,702 | 1,286,547 |
| Eligible native E016 vectors | 89,041 | 508,763 |
| >=2,500 bp core candidates | 9,812 | 60,211 |
| Core candidate bp | 133,052,224 | 1,008,845,967 |
| Short eligible recruitment bp | 76,590,479 | 434,981,697 |

All below-cutoff/featureless DNA remains explicitly excluded; ambiguous or
unsupported eligible DNA may remain unassigned. A grouping cutoff is not a new
training cutoff or a permanent product restriction. Keep all six existing length
strata plus native eligibility, origin, marker, assignment and quarantine cells.

## Local engineering and preparation (October 20 snapshot)

[Local evidence](local-evidence.json) records actual versus pending paths, resource
samples and failures. Real feature/opaque-ID/depth, native NNDescent/Leiden,
sparse cache/reload, missing-depth, ambiguity, positive-support and malformed-input
contracts pass. Installed tiny generated DNA/HMM exercises native marker cache
creation/readback, unchanged E013 reliability/refinement and all-DNA exports in
both modes. No community marker scan, encoder fit/inference or quality score ran.
The actual serial nine-job DAG, complete distribution/source/import/library probe,
collection/member/cap/refusal paths and source/sdist/wheel checks are exercised.

The synthetic 4,096-core/8,192-query array kernel takes 83.88 seconds internally
(group 76.32, audit 6.92), sampled process-tree RSS 0.645 GB; no biological recovery
is implied. It is a single-size Mac estimate, not full Linux affordability.
The later native gates pass as recorded above; the local snapshot is preserved.
The original Mac portability tolerance and all failed journals are preserved.

[Resource plan](resource-plan.json): propose **new $2**, existing 8-vCPU/32-GiB VM
and 300-GiB disk, three-hour cumulative clock/3.25-hour STOP, four numerical
threads, 26 GB sampled tree RSS, 25 GiB free reserve, 20 GiB extra work and
3 GiB compressed return. Gross maximum forecast is about **$1.64** including
compute/IP, run disks, maximum export and reserve. Expect 75–150 minutes;
The later full execution/return and review contracts pass above; these were
pre-launch estimates, not actual measured costs.
The later owner message authorizes this execution under a new $2; older budgets
do not carry over.

Complete numeric neighbor axes are retained once. Compact partitions explicitly
name those caches; E013 only copies their empty legacy display field. New local
population diagnostics can attach the separately verified E016 learned-neighbor
lists in memory, keeping fixed learning distinct from new joint-core retrieval.
Full final FASTAs remain on disk; core/pre/old assignment tables and every cache/
alternative are retained. Hashes of omitted DNA are not backups.

Compact preparation is privately backed up and read back: **583,326 bytes,
179 verified members**, including source locks and the tested wheel/sdist.
[Backup receipt](preparation-backup.json) records exact hashes and exclusions;
this is not a bulk-data/environment backup. The readback export quote is below
$0.0001, inside the approved storage operations reserve. Its final receipt is
appended after sealing rather than included in its own hash.

## Storage and confirmation

[Storage admission](storage-admission.json) passes fresh credit/price/resource and
all-version/soft-delete checks. The owner approves **$8 storage-only** from
October 21 at 00:00 through **October 28 at 00:00 Copenhagen**, 169 hours across
DST. The original admission forecasts $7.61; refreshed inventory plus the maximum
new return forecasts $7.63 with reserve. Storage authorization adds no compute,
resize, service, deletion or further retention. The separately authorized E017 VM
is now TERMINATED. Disk cost continues at
$31.20/month; review backup omissions before proposing any later cleanup.

The original [skin confirmation plan](../E016-positive-only-multiview/confirmation-plan.json)
remains frozen and unacquired. Both currently inspected communities are development.
Additional source/genome/replicon/molecule/taxonomy joins, overlap/pretraining,
competitive/ambiguous DNA, duplicate-safe full denominators and unique-versus-
provided-origin truth, unchanged comparator/protocol and separate acquisition/
compute/cost/retention admission remain. A new body site is not unseen genomes.
