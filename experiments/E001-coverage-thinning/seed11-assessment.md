# E001 seed-11 review and bounded closure

Reviewed 2026-09-29. Native execution and primary evaluation accepted; binary
selection/representation diagnostics pending a read-only collection. This is one
paired seed on a fixed GI development derivative, not the completed three-seed design.

## Accepted results

| Tool | C0 R95 | CT R95 | CT minus C0 | Assigned contigs C0 / CT |
| --- | ---: | ---: | ---: | ---: |
| MetaBAT2 | 0.442944 | 0.195018 | -0.247926 | 19,193 / 1,827 |
| VAMB | 0.461772 | 0.487635 | +0.025863 | 22,594 / 22,594 |
| COMEBin | 0.838989 | 0.802555 | -0.036435 | 22,594 / 22,594 |

Sources: [MetaBAT2/VAMB](paired-pilot-observed.json), [COMEBin](comebin-paired-observed.json).
R95 averages each frozen genome's best assembled-sequence recovery in a qualifying
>=95%-pure bin; unassigned genomes count as zero. It is not whole-genome completeness.
COMEBin's inclusive >=50% / >=90% recovery counts change from 194 / 176 to 186 / 168.
All 817,438,232 input bases are assigned in both COMEBin conditions. Native MetaBAT2
emitted support falls from 22,432 to 1,949 rows; emitted support includes cluster-zero
rows and is not synonymous with assigned contigs. Missing rows remain in denominators.

COMEBin preserves the 200-epoch maximum, batch 1,024, six fixed views, mean plus
square-root variance, seed 11, automatic temperature 0.07 (assembly N50 2,870,581 bp), and native early stopping. C0 stops at epoch 111,
CT at 107: the first three consecutive eligible epochs with top-1 accuracy >99%,
matching pinned `simclr.py`. `checkpoint_0200` is named after the configured
maximum, not evidence of 200 completed epochs. C0 and CT share 22,594 ordered IDs,
128-dimensional embedding manifests, package inventories and CheckM payload hashes.
Their native reader checked binary bundles before clustering. Fixed feature provenance
binds augmentation seed 101 and accepted sample/contig axes without repeating extraction.

The independent [review script](../../scripts/e001_review_comebin.py) rehashes all
returned retained members, recomputes R95 from predictions and frozen population,
checks AMBER per-bin and per-genome tables, complete selected assignments, all
120 expected candidate hash receipts per condition, marker-score arithmetic and
lexicographic tie-breaking. Both conditions select
`Leiden_bandwidth_0.2_res_maxedges100respara_30_partgraph_ratio_50.labels.npy`.
The guarded resume DAG excludes C0; its 5,227-artifact receipt matches the reused
hash validation. Historical failures under `recovery/` are not new active failures.

**Evidence limit:** the compact archive contains no candidate `.npy` arrays or
embedding matrices. It supports native execution/receipt acceptance, not independent
content inspection of all 240 partitions, matrix finiteness or recomputation of
marker statistics from those labels. The [collection manifest](diagnostic-collection.json)
requests those exact bytes plus existing normalized features, marker tables and
VAMB embeddings: 297 files, 434,557,937 bytes before compression. No BAMs, raw reads,
model checkpoints or new scientific computation are needed.

## Costs and what the CPU observations mean

[Accounting](seed11-cost-assessment.json) distinguishes measured components:

- Successful C0 rule: 10,581.24 seconds, 23.51387 allocated core-hours.
- Successful CT rule: 7,259.55 seconds, 16.13233 allocated core-hours.
- Successful CT resume driver: 7,268.33 seconds, 16.15183 core-hours, including
  startup. Do not add this to the CT rule cost; it contains that rule.
- Successful condition total: 39.6462 core-hours. The known recovery sequence is
  **at least 58.1075 core-hours**, including 100 interrupted CT epochs, the first
  false-projection failure and stale-lock retry. Missing initial-driver/accounting
  receipts and outside-driver rented time prevent an exact billed total.
- Retained successful condition receipts sum to **11,312,653,376 bytes**. This
  excludes recovery copies, environments, BAMs/features and archives; not total storage.

The rules report 4.39 and 4.30 average sampled CPUs despite eight allocated CPUs;
peak process-tree PSS is 7,624 MiB (about 7.45 GiB; the legacy receipt key says MB).
Native logs confirm seven compute threads plus one loader worker. This resolves
configuration mismatch, not perfect utilization: native serial phases and workload
scaling still limit useful parallelism. No evidence establishes faster/cheaper
16-vCPU execution. The resumed CT epochs averaged ~48 seconds versus ~75 for C0;
these ran in different job contexts, so that difference cannot be attributed solely
to thinning. Future training needs measured throughput decisions, not assumed
linear scaling. No extra resource benchmark is needed for collection.

Two extra COMEBin pairs project 79.29 core-hours if observed early stops repeat;
about 167 core-hours is a more conservative four-fit/cluster planning scenario using
the slower C0 full-schedule projection with margin. New thinning/features, MetaBAT2,
VAMB, setup and failures are additional. These are forecasts, not authorization or
an exact remaining-budget calculation. The successful MetaBAT2/VAMB pair cost 0.76946
core-hours; previously accepted preprocessing/features stay accepted and are not repeated.

## Recovery sequence assessment

Review scope: the entire `6ba21ce` through `07ff631` sequence, including code diffs,
commit explanations, current adapter/native paths and returned evidence.

| Commits | Effect and current disposition |
| --- | --- |
| `6ba21ce`, `90150cf` | Original paired launcher and transfer pin; startup-multiplied cost guard and four-thread/four-loader split required repair. |
| `8a03ca2`, `b06ff17` | Count startup once, seven compute threads plus one loader; successful C0 and later CT validate that native path. |
| `f1eed69`, `fd7d79e` | Package-only evidence recovery and missing-receipt salvage; no scientific rerun or new model. |
| `889d76a`, `17abccb` | Preserve completed C0, monitor open logs, archive old CT, guarded resume. Original path loss remains consistent with mount/job teardown, not a confirmed provider cause. |
| `9ceeb08`, `4f66418`, `07ff631` | Explicit stale-lock recovery, restore partial CT layout, real Snakemake unlock test and handoff. Latest return now validates CT-only execution and successful completion. |

The series is one implementation/recovery effort, not independent experimental
replication. Repeated wrapper/environment failures do not constitute biological
negative results. The compact-return omission is an evidence-transfer gap; resolve
it by collecting retained bytes, not another training or clustering run.

## Decision and final diagnostic boundary

[D010](../../docs/decisions/D010-bounded-e001-and-prototype.md) defers seeds 23/47
and makes this an explicit outcome-informed pilot-scope amendment. The five-point
COMEBin criterion is not met in seed 11 and cannot be assessed across three seeds.
This does not refute H001; VAMB's small gain also prevents a general claim that
thinning damages learned representations. Strong MetaBAT2 support loss motivates
stage accounting, not immediate invention of a reliability model.

Next: one hash-verified collection, then local analysis of all existing candidate
R95 values and marker selection, exact protocol neighborhood probes with fixed
queries/axes and length/lost-recovery overlap. Use existing diagnostic helpers;
truth may score an oracle gap but cannot select the deployed binning method.
Report retained-signal versus information-loss ambiguity. If the evidence cannot
resolve a mechanism, close E001 as inconclusive at this scope. Then select a small
first usable binner with the owner; no additional experiment campaign by default.
