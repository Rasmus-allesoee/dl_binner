# E024: accepted depth data, failed retrieval, and the next recovery decision

Reviewed October 28, 2026. [Inspection](../../experiments/E024-oral-measured-coverage/inspection-observed.json),
[data audit](../../experiments/E024-oral-measured-coverage/data-review.json) and
[priced allocation](../../experiments/E024-oral-measured-coverage/cost-review.json)
are direct project evidence. No new partition, truth score, training, external
binner, VM wake or confirmation run occurred in this inspection.

## What actually passed

The VM is TERMINATED. The matching current-boot/PID watcher requested shutdown at
10:42:08 UTC; the provider records stop at **10:44:39.525 UTC / 11:44 Copenhagen**.
The private completion is **FAILED**, with successful collection/readback. The
guest attribute remains `RUNNING / upload-completion`: the final upload helper
publishes progress after the driver publishes failure. Also, the parent returns
a result dictionary without passing failure to `sys.exit`. Neither its ordinary
exit nor Snakemake's `incomplete: false` metadata establishes science success.
The actual grouping subprocess and workflow exited **1**.

All ten acquisitions, the reusable index, sample-6 pilot, ten mappings, combined
matrix and explicit depth-only rebind passed. Publisher receipt checks cover all
50 segments and ten new full-file MD5/SHA256 identities, totaling 51,731,811,351
compressed bytes. Raw FASTQs were released only after accepted summary and native
full BAM hash/readback/decode proofs. They were not reacquired or reread here.

The independent local reader verified every **12,865,470** matrix cell against
its sample's integer aligned-base numerator, full contig denominator and rebound
float32 value. All **1,286,547 contigs / 1,669,981,123 bp** remain, in original order;
the two original zero-bp records remain separate prior input accounting. Non-depth
arrays are exactly equal to the retained original feature file. Column order is
**6, 7, 8, 13, 14, 15, 16, 17, 18, 19**. No truth was opened.

There are **576,144 measured all-zero rows / 341,271,658 bp**. Among 508,763 eligible
contigs, 317,196 have positive retained depth and 191,567 are measured all-zero.
This is sparse MAPQ-20 read-base evidence, not missing observations, measured
window depth or variance. The strict mapping policy remains unchanged. These
counts do not establish which genomes are distinguishable or how depth affects
recovery; sequence similarity, competitive mappings and sample distributions
remain relevant. Full unfiltered BAMs retain lower-MAPQ records for a separately
declared future measurement without repeating mapping.

## Why the comparison failed

Both indexes built; the retrieval union processed all 508,763 eligible rows.
The stage then refused **final composite recall below the frozen 0.90 gate** on
32 source-blind queries. The sequence-index and depth-index audits returned before
that refusal. Their individual numeric recalls, the final numeric recall and
the generated neighbor arrays were not written before the exception. Report only
the observed inequality. No hierarchy, density/marker partitions, export or final
input-rehash audit exists. The biological KEEP/MODIFY/ABANDON rule is **not
evaluated**; this failure is neither a negative depth result nor a passed MODIFY.

The source matches its declared design. It retrieves up to 60 candidates using
learned-vector/composition coordinates, up to 60 using depth coordinates, and
unions the retained 30 native neighbors. Exact reranking cannot recover a good
joint neighbor that none of those pools supplied. A simple illustration: a pair
with channel distances (1, 1) can beat candidates (0.01, 100) and (100, 0.01) under
a joint score, yet be absent from both channel-specific shortlists. That is a
mathematical limitation of the candidate scheme, not a measured diagnosis of
particular Oral contigs.

The actual final squared distance is

`(native_distance + r * composition_distance + m * depth_distance) / (1 + r + m)`,

followed by square root and the fixed floor. Channel distances use the retained
label-free scales; `r` depends on both contig lengths and `m` on both endpoints'
positive-depth availability. Thus one fixed Euclidean concatenation does not
exactly reproduce this pair-dependent score. More accurate retrieval in either
individual space alone does not guarantee accurate retrieval in this geometry.
No corrupt bytes, OOM, deadline failure, changed learning, depth fabrication or
critical departure from this declared rule was demonstrated. The exact amount
and distribution of the retrieval deficit remain unknown. No community search
was repeated merely to recover the lost audit numbers.

## Strongest next block

**Implement one scalable retrieval path that uses the actual combined distance,
then finish a prospectively amended cached-only information comparison.** Keep
the accepted DNA, means, native E019 vectors, transforms, seed, E023 hierarchy,
marker policy, full-reference recovery rule and 0.90 recall gate fixed. Preserve
this failed union as a distinct treatment. Do not call changed candidate discovery
an unchanged rerun, silently widen it or lower the gate.

A concrete first choice is a Numba-compiled joint-distance NNDescent index, with
the retained native neighbors available as initialization/candidate support,
followed by the existing exact float64 reranking and sampled exhaustive audit.
Freeze one bounded index policy before community outcomes; do not search a grid.
Persist numeric audit values, IDs, scales and reusable bounded neighbor arrays
**before** enforcing refusal. Test pair-dependent weights, all-zero/missing-depth
semantics, opaque-ID mapping, self/tie handling and actual native index/query
execution against exhaustive tiny answers. Passing those tests does not guarantee
the full-scale recall, runtime or biological result.

This is supported as an engineering option by the author's
[PyNNDescent API](https://pynndescent.readthedocs.io/en/latest/api.html) and the exact
[0.5.13 source](https://raw.githubusercontent.com/lmcinnes/pynndescent/release-0.5.13/pynndescent/pynndescent_.py).
Tag `release-0.5.13` resolves to `ab65f93d108406444932474bf981de7cee322cde`.
Its 83,456-byte main source has SHA256
`6e9e29ef1e7b05efb6c197cc44754a9b6acdeb6abce8020bb1a0bc1e97ddd521`,
identical to our retained package. The inspected constructor accepts a compiled
distance callable and initial graph; native search stores approximate float32
distances. Exact reranking and the unchanged gate remain essential. This source
audit is not execution of that custom metric or proof it will pass on Oral.

Why this before the serious alternatives:

- **A matched depth-enabled learner is a valuable broader upgrade**, but the new
  within-Oral information question has no valid output yet. Resolving its small
  cached consumer avoids another acquisition or training fit and can distinguish
  inadequate information from representation/bin selection. It is not a default
  series of tiny loss tests. Do not perfect every grouping detail first.
- **Full Oral GLM or a larger Transformer is premature.** The E024 workload audit
  projects about 61 GPU hours for the original exposure; even higher cutoffs leave
  roughly 33–43 hours. E021's prior gave mixed gains. Reuse the DCVBin efficiency
  audit for a later explicit cheaper-exposure/batching treatment, rather than
  silently changing crop semantics or discarding short DNA. Capacity is not shown
  to cause the present failure.
- **Calibrated marker-anchored bin construction** remains a stronger alternative
  if joint neighborhoods become biologically coherent but density selection still
  mixes/fragments them. E011–E013's same-genome marker-copy exceptions still rule
  out naive universal cannot-links. Do not change the marker factor here.
- **One SemiBin2 reference** could quantify attainable recovery, but cannot repair
  or identify this failed retrieval component. E009's ten sorted BAMs already have
  passed integrity evidence and make it the cheaper first reference. Oral now has
  ten reusable 50.05 GiB unsorted BAMs; it needs restore/verification and supported
  sorting/feature preparation, with a measured disk plan. The
  [author's co-assembly instructions](https://semibin.readthedocs.io/en/latest/usage/#co-assembly-binning)
  use one FASTA and several sorted BAMs with `single_easy_bin`; E024 means cannot
  replace those inputs. Defer both fits until a named decision warrants them.
- **Dataset expansion is still needed for generalization**, but cannot explain an
  uncompleted engineering contract. E009 and Oral remain development communities;
  their E022 depth/GLM and E019 sequence-only learners remain unmatched. Skin stays
  unscored: 610 targets, 313 exact Oral overlaps, with source/replicon/molecule/
  taxonomy/near/pretraining/ambiguity/unique-versus-origin/depth/protocol/cost
  admission outstanding. A new genuinely depth-enabled independent community is
  still needed before claims about that active feature regime.

The next treatment should retain E024's practical recovery criteria and the full
799-reference / 2,083,072,211 bp provided-origin oracle, known-shared sensitivity
and all length/origin/eligibility/marker/unknown/non-target/unassigned populations.
E009's 156-reference / 3.3034% N-quarantine summaries remain context, without
rescoring. If retrieval passes but recovery does not, that is decision-changing
evidence for the broader learner or calibrated bin-construction alternative.

## Cost and authorization boundary

Five measured allocations total **13.554832 hours**: about **$3.70109 compute/IP**,
plus **$0.57933** run-PD attribution, separate from 84,668.43 sampled workflow CPU
seconds. The existing disks also cost **$31.20 per month while stopped** and are
already under the separate storage approval. All new BAMs cost about **$0.22230**
from creation through November 4; compact storage/export are separately priced.
The combined run-PD/export/projected new-storage subtotal is **$4.61112**, or
**$5.36112** with operations/unreconciled reserves, inside the amended $16 ceiling.
This is a priced estimate, not an invoice or credit-delta attribution. Fresh
Welcome credit is DKK 1,760.04 Available, 89%, through January 12; delayed usage
can exceed 24 hours and the $35 reserve remains.

The old absolute deadline remains **October 29, 08:55:32 UTC**, with independent
STOP at 09:10:02 UTC. This inspection authorizes no new wake or scientific retry;
collection-only recovery is unnecessary. A revised retrieval treatment needs
explicit scope admission, not an automatic reuse of that remaining clock. The
proposed next prompt can authorize a **separate new $2 / three-hour cached-only
block**, with native gates and 3.25-hour STOP, after local preparation/forecast.
That is a new authorization, not a clock reset in this failed journal. Return
only new outputs, referencing this verified data archive rather than copying it
again; about 1.130 GiB remains under E024's cumulative 2 GiB compact export cap.
Current data use only about 9.85 GiB retained work growth / 13.35 GiB sampled peak;
no new disk is justified for this proposal. Exact future peak/return sizes still
need a prelaunch inventory.

Review all storage by **November 4, 00:00 Copenhagen**. No renewal or deletion is
automatic. The BAMs would add about $1.00 per month if retained longer; a later
deletion can still incur about $0.23 during the seven-day soft-delete tail. No
temporary disk exists to delete, no accepted file was removed, and no extra
resource was provisioned in inspection.
