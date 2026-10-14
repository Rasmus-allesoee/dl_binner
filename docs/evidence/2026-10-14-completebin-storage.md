# CompleteBin storage audit for E009

Date: 2026-10-14. Scope: source interpretation and retained thesis configuration,
not a CompleteBin fit or measured GCP peak. The owner's report of hundreds of GB
is useful operational evidence; no matching historical disk inventory was supplied.
[E009 operations](../../experiments/E009-competitive-benchmark/OPERATIONS.md) owns
the later launch/storage plan.

## Source and thesis boundaries

Audit the actual E009 pin,
[be0b9311](https://github.com/zoubohao/CompleteBin/tree/be0b9311f0fe4278c231010f78d995dca02b66d6),
archive SHA256 `d9a9d408f64650f07d07ed866ec7afc39d9d18e8987eae3e07ccbf2e2be35f0c`.
Local reference-cache Binning_steps/seq_info anchors match the immutable archive;
the audited data_utils_fixed, seq_utils and trainer files also match its members.
Only the already accepted E009 max-50 schedule patch changes the scientific recipe.
Loader/pool limits are operational. V10's CompleteBin BAM/checkpoint/forward
contract stays accepted; it did not exercise full preprocessing/training/clustering.

The thesis repository's `real_benchmark/workflow/Snakefile` rules
`completebin_step1/2/3` create per-assembly temporary directories for the 20 MAM
assemblies and pass each assembly's `get_bam_dir_for_assembly(...)/*.bam` collection.
Thus **20 assemblies/runs and the number of BAM coverage inputs per run are
different multipliers**. The supplementary thesis reports earlier augmented-view
duplication in exported bins; do not infer either the exact old storage peak or
that current E009 exports need that same repair. Native output DNA/ID checks must
still reject duplicates. The old executed CompleteBin source/version is not proven
identical to this pin.

## What this pin writes

| Path/function | Direct code observation | Consequence |
| --- | --- | --- |
| `Seqs/seq_utils.py:base_pair_coverage_calculate` | Dense int64 coverage, one value per eligible base, per BAM; writes per-BAM pickles | Approximately `8*S*L` bytes, even for zero coverage |
| `Seqs/seq_info.py:prepare_sequences_coverage` | Reads those pickles, builds float32 `[S,length]` arrays, writes `contigname2bpcover_nparray_list.pkl`; deletes per-BAM pickles only afterward | Raw and merged arrays coexist: approximately `12*S*L` disk bytes; RAM also holds both collections |
| `DataProcess/data_utils_fixed.py` | Spawn workers, write `_temp_chunks/chunk_*.pkl`, compressed feature `.npz`, then uncompressed object `training_data.npy` containing sequence **and full coverage again**; remove chunks only after success | The memory fix trades IPC for temporary disk; it does not remove persistent coverage duplication |
| `Trainer/trainer.py:ContrastTrainer.train` | Save a state dictionary each resolved epoch | Up to `E*C` checkpoint bytes while training; this is not only the selected late checkpoint |
| `Binning_steps.py` after inference | Copy chosen checkpoint, then unconditionally remove `model_save/` | The epoch checkpoint peak occurs before clustering; do not sum every historical checkpoint into the later clustering peak |
| `Cluster/first_cluster.py` and `sec_cluster.py` | First grid: `7*5*3=105` partitions; second grid: `6*3*2=36`; refinement writes candidate bin FASTAs per partition before selection | Potentially many assembly-DNA copies, independent of epochs and BAM count |
| E009 `command_plan(...completebin...)` | `remove_temp_files=False`; clustering-temp cleanup is conditional on that flag | Retained candidate directories can dominate later disk use; do not silently change this evidence-retention configuration |

The fixed data module's introductory 420–500-GB **RSS** estimate is an upstream
comment, not a disk measurement or our reproduced runtime result. It still
accumulates a final object array/list and pickle buffer; “memory-safe” is not an
admission for our 32-GiB data-stage VM.

## Estimating the peak

Use actual CompleteBin-resolved eligibility: `L` is its retained DNA length, `N`
its retained contig count, `S` the ordered BAM count, `E<=50` resolved epochs and
`C` the measured first checkpoint size. Do not substitute the GSA size or the
whole-source catalog for the real assembly.

Coverage merge peaks near `12*S*L`. Fixed preprocessing can have merged coverage,
chunks and final training data together: approximately `12*S*L + 3*L + 2*F`,
where raw feature-array estimate
`F = 4*N*(6*136 + 12*S + 136*S)` bytes follows the actual six-view features.
Actual CompleteBin eligibility can differ from the >=500-bp admission count.
Object/pickle headers, name strings, filesystem blocks and buffers add overhead;
compression is not a guaranteed saving.

After chunks disappear, retained sequence/coverage/training is roughly
`8*S*L + 2*L + F`. Training adds at most approximately `(E+1)*C` before the
checkpoint directory is removed. Clustering can add up to roughly `105*L + 36*L2`
candidate FASTA DNA, where `L2<=L` is the second-round selected DNA, plus headers,
gene calls, graph/partition tables, polishing candidates and final exports.
That is a conservative planning model assuming each candidate covers DNA at most
once, **not a validated upper bound** if native candidates duplicate records.

Illustratively, at `L=600,000,000`, `N=100,000`, ten BAMs give about **67 GiB**
for coverage coexistence, around **71 GiB** fixed preprocessing before overhead,
and about **47 GiB** retained training/coverage. The 141 candidate-copy allowance
adds **79 GiB** if `L2=L`. The 152,032,963-byte pretrained payload is only a
checkpoint-size proxy: 51 copies are about **7.2 GiB**, with the actual learned
model size still to be measured. The clustering peak could exceed **130 GiB of
CompleteBin-owned output**, plus common reads/BAMs/source/runtime storage.
Twenty BAMs double coverage terms, not all candidate/model terms.

One assembly avoids retaining twenty separate full CompleteBin runs. It **does
not** mean one BAM: the selected E009 design has ten coverage inputs. The 50 cap
reduces training time and checkpoint accumulation; it leaves coverage generation,
training-data size and the native clustering grids unchanged. The native scheduler
can resolve 35/39/lower-capped epochs and change automatic pretraining; retain that
decision. No reduction in views, grid size, contigs or coverage samples is authorized
as a storage workaround.

## Later admission and monitoring

The proposed **300-GiB data-stage disk is not CompleteBin admission**. Once actual
assembly/BAM sizes exist, recalculate the complete overlapping peak. A **400–500-GiB
balanced disk** is a plausible later envelope; at $0.10/GiB-month it costs
$40–50/month for work storage and needs a higher `SSD_TOTAL_GB` quota than today's
250. Do not provision it now. At worst-case coverage merge, raw arrays alone need
about 45 GiB RAM, plus 22 GiB merged arrays and worker/object overhead; a 32-GiB VM
cannot be assumed feasible. A later 128-GiB E2 CPU option may require total-CPU
quota >=16. Published CPU support does not establish fit affordability.

For a later authorized fit, retain free/used filesystem bytes every 10 seconds
and per-directory logical/allocated sizes every 60 seconds, including coverage,
`_temp_chunks`, training data, model checkpoints and both clustering directories.
Record peak **coexisting** usage and phase transitions; frequent disk sampling is
distinct from sampled process RSS and charged VM uptime. Bound the tree/phase with
the approved clock, CPU/RAM and at least 25-GiB disk reserve; raise the reserve if
measured write growth during the stop/flush interval requires it. A free-space
reserve is a prospective stop, not a hard write quota.

The expanded prepared CPU plan also splits the coverage budget: this pin launches
two BAM processes for S>2. Giving each the old N-2 BGZF setting oversubscribes
the node. At 8 CPUs the new plan uses two BGZF slots per coverage process, with
their main processes/coordinator headroom, and loader zero. It remains prospective,
with actual native reports/benchmarks required at fit admission.

Review storage after native preparation and the first checkpoint, before treating
CPU training as affordable; retain productive completed work and failure causes.
Prune only reviewed regenerable files after recording sizes/hashes and preserving
required compact evidence. Any change to `remove_temp_files=False` needs an explicit
operational/evidence amendment; it does not authorize shortening the scientific
schedule. All old UCloud files and accepted evidence remain protected.
