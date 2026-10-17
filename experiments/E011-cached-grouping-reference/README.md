# E011: cached grouping objective and one external feasibility reference

Opened 2026-10-17. Status: **native provenance gate failed; VM stopped; no community
consumer executed**. The owner authorized the attempted phase after gates; the
stop-on-failure instruction closed it without a retry. The local repair is tested,
with a new native Linux gate still required. Branch `codex/e011-cached-grouping-reference` starts at reviewed E010 commit
`8950e7e`. Dev3, frozen dev4 and all accepted E009/E010 artifacts/journals stay intact.

## Decision and prospective control

E010's short bacterial neighborhoods improved, but conservative weighted R95 was
1.8763% pre-refinement /4.2909% post versus dev3 learned ten-depth 5.3911%.
The largest bacterial-dominant pre-bin mixed support from 107 genomes. Test one
cached objective change rather than assume that either the encoder or grouping
alone explains this result. The owner also requests an implementation audit.

Use the exact retained full-axis embeddings, 30-neighbor graph and edge weights.
Map its opaque-ID-sorted graph back to FASTA indices explicitly. Leiden CPM uses
unit node sizes, seed 11, two iterations and **gamma = median(positive retained
edge weights) / 30**. This single rule is frozen before any changed community
partition or score. It expresses a graph-local minimum weighted density relative
to one median edge per neighborhood-sized set of possible connections; it is an
engineering prior, not an optimal biological resolution or expected genome count.
No truth, marker count, source label, score grid or new neighbor index selects it.
[The primary CPM/RB formulas](https://leidenalg.readthedocs.io/en/stable/reference.html#cpmvertexpartition)
justify the objective distinction, not this untested density choice.

Reuse the accepted RB pre/post outputs without recomputation. Apply the unchanged
installed dev4 marker refinement to the new CPM partition, preserving every DNA
row and all short/noise/unknown/non-target populations in pre/post exports.
Keep the encoder, vectors, graph weights, seed and refinement code/config fixed.
The audit must distinguish code defects, a design/documentation mismatch and a
correctly implemented but potentially poor scientific choice. Do not silently
repair a frozen policy within the control or erase the Mac portability failure.

One **MetaBAT2 2.18** native reference is worthwhile here: a substantially better
result would demonstrate recovery support under this assembly/truth/metric;
a similarly low result would indicate difficulty/restriction, not a defective
simulation. Use the same full assembly and exact ten measured mean-depth columns
through native **`--cvExt`**, seed 11, 8 threads and native default thresholds
(2,500-bp seed contigs, 200-kb minimum bins; native small-contig recruitment stays
enabled). Source code in this mode assumes variance equals mean internally; no
variance is measured, invented in our input, or claimed comparable to BAM-derived
MetaBAT variance. Retain native exclusions/unassigned DNA and report its different
eligibility. No read/BAM scan, marker detection, training or broader external campaign.

## Prospective interpretation

Primary endpoint: unchanged admitted sequence truth v2, bins >=200 kb and >=95%
confirmed source support divided by **all bin DNA**, full provided bacterial
reference denominators, duplicate-safe loci and 3.3034% N-quarantine. Keep all
lineage/length populations, per-target losses, availability and assignment totals.
Geometry is unchanged by CPM and is reused, not rescored as a new encoder gain.

Keep the CPM mechanism as useful development evidence if post-refinement weighted
R95 improves by >=0.5 percentage points over frozen dev4 post, targets recovered
>=50% do not decrease, and assigned confirmed bacterial bp falls by <=10%.
This alone does not promote the bundle over dev3 or establish generalization.
Modify the hypothesis if pre-refinement improves but refinement erases the gain,
or purity improves with excessive fragmentation/unassignment. Abandon this setting
if there is no useful full-denominator recovery gain; do not search E009 resolutions.
MetaBAT2 is a feasibility reference, not a matched causal ablation. Report it even
if it loses. A >=1-point weighted-R95 advantage over the best preserved own output
is prospectively a material recovery gap; all other outcomes still constrain
interpretation without proving a ceiling or optimality.

The frozen [oral-GSA confirmation](../E010-coherent-prototype/confirmation-plan.json)
remains unacquired. A later useful frozen mechanism requires source/genome/replicon,
taxonomy, overlap and independent truth admission plus separate cost approval.

## Bounded execution and evidence

Use only the existing Iowa e2-standard-8 /32 GiB, 300-GiB work and 30-GiB boot disk.
New phase ceiling **$1 gross**, **30 cumulative minutes from VM start**, provider
STOP **45 minutes**, 25-GiB free reserve, 20-GiB extra-space cap, <=2-GiB compressed
export. The owner permits a justified larger envelope, but none is proposed now.
No provisioning, resize, retry, extension or storage-retention change. Keep the
**October 21** review; disks cost ~$31.20/month while stopped.

Expected work: 5–15 minutes including verification, one cached grouping/refinement,
one MetaBAT2 run and collection; roughly 2–8 GiB RAM /2–5 GiB extra live disk.
45-minute fallback compute/IP ~$0.205, disk interval ~$0.032, worst 2-GiB export
$0.24 plus ~$0.07 setup/storage/operations reserve gives **~$0.55**, below $1.
Refresh live credit scope/balance/expiry, delayed usage, rates, retained storage
approval and actual headroom before release. The estimate is not an invoice.

Restore only verified archive members into a fresh directory; missing/corrupt
evidence refuses execution rather than recreating data. Reuse the accepted E010
runtime read-only after full distribution/source/origin checks; install MetaBAT2
in a distinct pinned prefix. Local real tiny graph/cache/refinement/export and
MetaBAT contracts precede the native gates, all native setup sharing the boot clock.
Arm/test a fresh boot/process-bound held-parent exit watchdog and verify provider
STOP before release. Capture stages/resources/closed terminal snapshots, verify
every archive member and private readback, then stop. No success inference from
shutdown. If still healthy after verified progress and a few minutes, report and
leave supervision intact without polling to completion.

## Native outcome and local repair, 2026-10-17

[The native receipt](native-observed.json) verifies FAILED phase
`cached-20261017T005141Z-ab80312` at executed source ab80312 and independently
TERMINATED VM. Start 00:51:41.313 UTC /stop 00:58:26.197 UTC; 404.884 s allocation.
Restore, full 28-distribution/source/origin check and 35-package independent MetaBAT
installation pass. Actual 2.18 CLI/help passed before the probe rejected normal
libz.so.1: our strict scientific-artifact binding helper was inappropriate for
loader aliases. Neither community CPM nor MetaBAT ran; later native gates were
skipped. This is an execution/verification failure, not a negative biological result.

Private failure archive 19,320 bytes, SHA256
`1fa72f3c51d9c942ac125e2d722e34e3a8e903a02223aa97175e9a94723a622f`;
all 28 members /65,324 logical bytes independently verify. Guest/private completion
agree. The exit watcher uploaded its pinned process-exit/shutdown-request snapshot;
provider stop was also issued and TERMINATED confirmed. No VM wake for serial
console or missing evidence. Full execution-phase disk samples and restore manifest
were omitted by the failed archive collector; collection-only minimum free131.09
GiB is not claimed as full-phase peak. The local repair now retains failed-phase
samples and the restore receipt. Original failed bytes/journals are unchanged.

The corrected dependency probe records the reported alias, direct link and resolved
regular target/hash, without resolving invocation paths or relaxing scientific
artifact refusal. Ten local tests and actual Mac CLI/cache consumers pass; repaired
native Linux remains unexecuted. [Reuse lock](reuse-lock.json) binds passed native
installation and a deterministic expected cache receipt, requiring strict member
checks rather than recopy/reinstall. A missing/corrupt receipt fails, without fallback.

Gross measured-uptime compute/IP $0.03071 + disk interval $0.00481 + asset readback $0.00745
and tiny native export totals ~$0.043 before small charges; <$0.063 with reserve,
inside $1. Sampled CPU is not the charged allocation. Existing disks remain
$31.20/month while stopped, October 21 review unchanged. No model/refinement/seed/
scientific rule/score changed, and no automatic retry or broader tool run followed.
[Operations](OPERATIONS.md#exact-next-prompt) gives the next explicitly authorized
attempt, with fresh financial/native/supervision gates and the same frozen science.
