# D007: Retain COMEBin With an Explicit Resource Amendment

Status: amended, 2026-09-21 and 2026-09-28. The temporary 200-core-hour override is withdrawn;
the effective COMEBin per-fit ceiling is again 80, with total 800 unchanged.

## Allocation correction

The owner clarified that COMEBin ran on **2 vCPU / 6 GB**, not the driver's
assumed 8 vCPU. Preserve raw measurements and the original reasoning below as
history. [Allocation corrections](../../experiments/E001-coverage-thinning/allocation-corrections.json)
recalculate charged cost, not speed: **23.946 core-hours per fit**, **47.891 with
margin**, and **143.674 / 287.348 for six fits** at that measured allocation.
There is no longer a projected total-budget violation from these fits alone.
Keep COMEBin, restore the original 80 limit, and proceed with mapper/preprocessing
feasibility. Actual pilot overhead still determines execution authorization;
no extra optimizer preflight or assumption of linear speedup is needed.

## Pilot resource clarification, 2026-09-27

The two-vCPU allocation is a historical measurement, not a preferred full-pilot
configuration. Source inspection confirms COMEBin starts **four fixed native
DataLoader workers** in addition to its requested PyTorch threads. The prepared
2-thread/2-vCPU plan therefore undercounted processes. Use **8 vCPU / 24 GB** for
the first native pair: four compute threads plus four loader workers, serial C0
then CT, with native BLAS/inter-op pools capped at one. Clustering can run eight
independent native Leiden candidates while retaining the same seeded 120-grid;
seeded HNSW construction remains serial for reproducibility.

This is a resource correction after MetaBAT2/VAMB outcomes were visible, before
any COMEBin result; it changes no scientific settings or selection criteria.
More CPUs preserve cost only with proportional speedup. Eight-vCPU scaling is
unmeasured; neither the old 23.946-hour estimate nor a linear extrapolation is
claimed as current performance. Starting after epoch three, project all 200
epochs from observed elapsed time (including startup); stop if the projection
exceeds 80 allocated core-hours. Keep the 80 per-fit, 15 per-condition clustering
and 200 group ceilings. Native early stopping is allowed but not assumed in the
projection. Four vCPU would not budget native workers plus compute; sixteen
would increase unmeasured scaling risk. Inspect this pair before further seeds.

## Failed first COMEBin launch and revised CPU split, 2026-09-28

The first 8-vCPU return `paired-pilot-comebin-p3983hy8` is preserved in
[observed failure evidence](../../experiments/E001-coverage-thinning/comebin-pilot-failure-observed.json).
COMEBin itself did not fail. The driver killed C0 during its projection check after
mistaking about 5 minutes of one-time setup for per-epoch work: total elapsed at
the epoch-three marker multiplied by all 200 epochs projected 44,443.85 seconds,
above the 36,000-second (80 core-hour) fit cap. The first two persisted epochs each
took about 120 seconds. Count startup once, use native per-epoch elapsed values,
and apply a 25% margin to the remaining schedule; do not assume early stopping.

The same return and the owner's dashboard show about 350% peak CPU on eight vCPU.
The source requested PyTorch intra-op 4 and its fixed loader count 4. Since the
training input is a precomputed `TensorDataset` and shuffled indices are generated
in the seeded parent, loader count is an operational queue setting, not a change to
coverage, views, or training examples. Keep the pinned checkout unchanged; at
runtime reduce its loader constant to one and request seven PyTorch threads, so the
budget is exactly **7 + 1 = 8**. Before C0, exercise the same pinned TensorDataset
DataLoader with one worker under short private `/tmp` and drain every batch. Log the
effective thread/worker values. This makes use of the allocation without the
8-thread + 4-worker oversubscription; measured throughput must still confirm it.

This remains a resource-only retry of seed 11. Keep 200 maximum epochs, early
stopping, six views, batch 1,024, seed, all 120 clustering candidates and every
scientific threshold. The 80 per-fit, 15 per-condition clustering and 200 group
core-hour ceilings remain. A new unique attempt preserves the terminated one.

## Follow-up after the first paired launch, 2026-09-27

The 8-vCPU return `paired-pilot-comebin-p3983hy8` is preserved in
[observed failure evidence](../../experiments/E001-coverage-thinning/comebin-pilot-failure-observed.json).
COMEBin itself did not fail. The driver killed C0 during its projection check after
multiplying about five minutes of one-time setup/feature loading by the 200-epoch
schedule; the resulting 44,443.85-second estimate exceeded the 36,000-second
(80 core-hour) fit ceiling. The two persisted completed native epochs took 120.119
and 121.543 seconds. Project the fit's elapsed wall time once plus remaining epochs
at the mean of the latest three native epoch timings, with a 25% margin. Do not
assume early-stop savings.

The owner dashboard showed about 350% peak CPU on eight rented vCPU. The captured
COMEBin resource report confirms PyTorch intra-op 4 and four fixed loader workers.
The pinned source builds a TensorDataset from precomputed six-view tensors; the
seeded parent process owns sample shuffling and workers only fetch tensor slices.
Keep the tool checkout pinned, but reduce its loader constant to one at runtime
and set `--num_threads 7`, making the explicit CPU budget **7 + 1 = 8**. Before
training, drain a small synthetic TensorDataset through that exact one-worker CPU
queue under short private `/tmp`; report effective thread and worker settings.

This resource retry retains seed 11, the 200-epoch maximum, early stopping, six
views, batch 1,024, marker selector and 120 candidates. The 80 per-fit, 15 per-
condition clustering and 200 group core-hour ceilings are unchanged. The retry
uses a fresh attempt and preserves the terminated run. Its changed throughput must
be measured; the earlier 4+4 split was not an efficient use of the allocation.

## Original decision (superseded accounting)

The accepted [COMEBin measurement](../../experiments/E001-coverage-thinning/native-comebin-observed.json)
used the native 1,024-contig, six-view batch, 17,928,576 parameters and full native
InfoNCE logits (30,720 x 6,139). Measured batches took 9.796 and 9.399 seconds at
8 vCPU. The 22-batch, 200-epoch ceiling projects 95.783 allocated core-hours, or
191.565 with the previously declared twofold margin. It excludes extraction,
DataLoader, marker search and clustering. Early stopping savings are not assumed.

The owner considers this cost acceptable. Retain COMEBin and prospectively raise
its per-fit review/stop ceiling from 80 to **200 allocated core-hours**. Other
tools retain 80; the experiment remains capped at **800**, not 2,100. The
[compute policy](../../experiments/E001-coverage-thinning/compute-policy.json)
owns this resource-only override; the frozen `config.json` remains the input
snapshot and is not rewritten to change already accepted output identities.
Future execution must apply this override, not read the historical 80 as the
effective COMEBin limit. No training is authorized by this decision alone.

Six COMEBin fits project 574.696 core-hours centrally, or 1,149.391 with the
twofold margin; six VAMB fits add about 4.883 centrally. Thus the full schedule
is plausible centrally but **not approved under the conservative total**.
Finish bounded integration/read-prefix feasibility, then measure the first paired
pilot's real throughput and overhead before committing to the remaining two paired
replicates. Resource decisions precede interpretation of biological scores. Keep
the pilot regardless of quality; do not shorten native training, silently drop
replicates or remove COMEBin to fit a desired conclusion. If measured costs do not
fit 800, explicitly amend scope or seek a total-budget decision before more fits.

Alternatives: reject COMEBin at the old arbitrary ceiling (premature given actual
memory/throughput and owner acceptance); expand the whole budget now (unnecessary
before measuring overhead); assume early stopping or linear speedup from more
cores (unsupported); reduce batch/epochs (changes the native baseline). None is
selected. A 200-hour per-fit envelope is not a promise to spend 1,200 hours.
