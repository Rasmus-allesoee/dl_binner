# D007: Retain COMEBin With an Explicit Resource Amendment

Status: accepted, 2026-09-20. Amends D004's per-fit ceiling for COMEBin only.

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
