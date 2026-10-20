# E017: information-aware long cores and conservative recruitment

Status: **implemented and locally tested; community comparison not executed**.
Date: 2026-10-20. Branch: `e017-information-aware-grouping`.
[D015](../../docs/decisions/D015-coherent-prototype-upgrade.md) owns why this coherent
fixed-learning grouping block is next. [Design](design.md), [protocol](protocol.json),
[config](config.json), [source review](source-review.json), [reuse lock](reuse-lock.json)
and [operations](OPERATIONS.md) own the prospective rule and execution boundary.
Dev3/dev4/dev5/E016 and every accepted input/result/failure remain immutable.

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
claim. Quality and generalization remain unassessed.

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

## Local engineering and preparation

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
The new same-clock native gates must still pass before any community consumer.
The original Mac portability tolerance and all failed journals are preserved.

[Resource plan](resource-plan.json): propose **new $2**, existing 8-vCPU/32-GiB VM
and 300-GiB disk, three-hour cumulative clock/3.25-hour STOP, four numerical
threads, 26 GB sampled tree RSS, 25 GiB free reserve, 20 GiB extra work and
3 GiB compressed return. Gross maximum forecast is about **$1.64** including
compute/IP, run disks, maximum export and reserve. Expect 75–150 minutes;
Linux timing/profile competition/headroom and actual member sizes remain gates.
No execution is authorized by the local task. Older budgets do not carry over.

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
DST. Forecast is $7.61 including reserve. No start/resize/service/deletion or
extra retention follows. Current VM remains TERMINATED. Disk cost continues at
$31.20/month; review backup omissions before proposing any later cleanup.

The original [skin confirmation plan](../E016-positive-only-multiview/confirmation-plan.json)
remains frozen and unacquired. Both currently inspected communities are development.
Additional source/genome/replicon/molecule/taxonomy joins, overlap/pretraining,
competitive/ambiguous DNA, duplicate-safe full denominators and unique-versus-
provided-origin truth, unchanged comparator/protocol and separate acquisition/
compute/cost/retention admission remain. A new body site is not unseen genomes.
