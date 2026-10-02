# E002: bounded frozen DNABERT-S CPU feasibility

Prepared: 2026-10-03. Status: planned; operational inference check, **not** a genome
recovery experiment. [D011](../../docs/decisions/D011-first-binner-prototype.md)
owns the design decision and stop/revisit rules. No E001 result is reopened.

## Prospective contract

Use one public author checkpoint and one separate Python environment. Unmodified
checkpoint/tokenizer/custom-code files are bound in [model-pin](model-pin.json).
Dependencies are frozen in [requirements](requirements-local.txt); this is a local
Intel macOS runtime, not a validated Linux recipe. Retain downloads and installation
logs in ignored `artifacts/d011-dnabert-s-spike/`. Model metadata declares Apache-2.0;
custom source retains Apache-2.0/SPDX headers. The author repository has no `LICENSE`
at the probed root path. This local probe does not redistribute model/source assets
or resolve final product licensing.

[Configuration](config.json) is the executable source of truth. Four numerical
threads, interop scheduling limit one, no data-loader workers; OpenMP/BLAS caps four,
tokenizer parallelism off. One numerical stage at a time. Supervisor samples worker
and descendant RSS/CPU, stops at 8,000,000,000 bytes or 3,600 seconds and terminates
the worker group on fatal exit. Timing starts at worker launch, stricter than an
hour after setup. After the input-only failure below, the remaining ceiling is
3,560 seconds, preserving a total budget below one hour. No checkpoint search,
automatic retry, quantization, distillation
or full-model training.

Hash-select forty distinct parents at least 10 kb from the accepted canonical
FASTA, and center eight real-DNA windows at each of 500/768/1,000/2,500/10,000 bp.
Selection uses IDs only, no labels or measured features. Long-parent short windows
test speed and contracts; they do not establish native short-contig accuracy.
Bind the source SHA256 and window coordinates/bytes. Preserve the full assembly
length distribution only for a timing projection.

Extract float32 features with the author's PyTorch CPU attention fallback, frozen
weights and evaluation mode. Mean pooling includes attended special tokens to
match the author's unpadded example, but excludes padding. Canonicalize whole-DNA
orientation, divide into nonoverlapping chunks of at most 4,000 bp / 1,024 tokens,
split recursively in base coordinates if either strand exceeds the limit. Average
both strand features per chunk, then weight chunks by base length. These strand/
chunk adaptations are ours; full-contig author output is **not** claimed equivalent.
The token cap bounds quadratic attention; config position size 512 is not silently
treated as a hard native limit. No token truncation is enabled.

## Acceptance and measurements

The [probe](../../scripts/dnabert_s_cpu_spike.py) must check actual native author
single-sequence parity, unequal-length batch versus singles, padding contamination
under a naive mean, ordered IDs, exact chunk coverage/tails, reverse-complement
invariance, token handling beyond 512, finite nonzero embeddings, model freeze,
bound cache save/load and stale-ID rejection, checkpoint reload equivalence and
import origins. Local portable guard/cache/chunk tests are separate and do not
replace native model contracts.

Measure imports/load, first/cold extraction and length-specific warm timing on all
eight independent windows after one excluded warmup. Log compression, chunk counts,
process CPU/RAM, hardware and library limits. Project at this measured four-thread
budget for an explicit 10,000-contig equal-count length panel (29.536 Mb) and the
accepted 22,594-contig / 817.438 Mb FASTA, using nearest tested log-length per-base
rates. Label these rough projections, excluding setup/I/O/learning/clustering and
unmodelled compression/long-tail costs; no scaling to other machines/CPU counts.

Checkpoint loading alone is insufficient. If contracts fail or the resource ceiling
is reached, retain evidence and defer GLM in favor of the inexpensive contrastive
prototype. If contracts pass and a small development comparison is affordable,
prepare **one** short-inclusive representation comparison with frozen data, scoring,
cluster settings and cost before execution. No utility/biological claim follows
from feasibility. Full-assembly projections also inform eventual product choice;
a small comparison being feasible does not establish a cheap production binner.

## Local command and retained attempt

Commit protocol/code/configuration before timing. Run once from the repository root:

```sh
env -u PYTHONPATH -u PYTHONHOME -u PYTHONUSERBASE PYTHONNOUSERSITE=1 \
  artifacts/d011-dnabert-s-spike/env/bin/python scripts/dnabert_s_cpu_spike.py \
  --config experiments/E002-dnabert-s-feasibility/config.json \
  --output artifacts/d011-dnabert-s-spike/run-002
```

Output directory must be absent. Worker output goes to `terminal.log`; stage
timestamps and incremental `result.json` are retained alongside resource samples,
panel FASTA/provenance and hash-bound feature cache. Live progress can be read with
`tail -f artifacts/d011-dnabert-s-spike/run-002/terminal.log`. Supervisor receipt
records process resource observations and a four-thread wall budget; these are
local costs, **not UCloud billing**. No owner-run UCloud command is prepared.

Actual observations/conclusions will be appended after the one native attempt.

## Input-preparation correction before native inference, 2026-10-03

`run-001`, source `5267241`, stopped after 32.9099 seconds with a strict A/C/G/T/N
validator rejecting the accepted FASTA. A whole-file audit found 162 valid IUPAC
ambiguity symbols across seven contigs (K22/Y33/S18/R44/W29/M16), with no invalid
DNA symbols. This is a probe input-contract defect, not a model/environment or
CPU-feasibility failure. No checkpoint was loaded or inference performed.
The unmodified source checksum remains accepted. Correct the reader/complement
to preserve all IUPAC symbols, retain the failure/audit and continue the same single
checkpoint/environment investigation as `run-002`. This narrow amendment neither
changes window selection nor increases the total time ceiling. Unknown-token
counts/ambiguity must remain explicit; no biological accuracy claim follows.
