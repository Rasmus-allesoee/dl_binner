# First binner prototype

This experimental package implements our own composition-based contrastive
encoder, checkpoint inference, fixed clustering and complete FASTA/assignment
export. It is development software, not validated whole-MAG recovery or a
published release. [D011](decisions/D011-first-binner-prototype.md) owns the design;
[E004](../experiments/E004-first-binner/README.md) owns integration evidence;
[E005](../experiments/E005-linux-pilot/README.md#accepted-v5-native-gi-pilot-and-independent-review-2026-10-06)
accepts native Linux and a capped GI assembly/explicit-depth development pilot.

Install into a separate Python 3.10–3.12 environment with the pinned requirements,
then `python -m pip install --no-deps --no-build-isolation .`. The executable is
`dl-binner`; `python -m dl_binner` provides the same CLI. Keep numerical stages
serial within four CPU threads. A Linux recipe must select CPU PyTorch wheels
explicitly and pass native checks before owner execution; local installation
does not validate that recipe. [E005](../experiments/E005-linux-pilot/OPERATIONS.md)
has accepted the checksum-bound native CPU/Linux smoke and bounded
GI pilot. Its protocol preserves shorter
contigs and requires depth from that exact reference, never fabricated missing rows.

The first actual local integration is accepted in E004: a frozen installed wheel
trained and exported bins, checkpoint reload matched exactly, and the raw control
matched E003. Grouping improved while short-neighbor purity/precision declined.
This is working experimental software, not an established improvement in MAG
recovery. The measured demo used sequence only; optional depth has native contract
tests and a development TNF+measured-depth recovery result in E005. The two arms
share depth, so coverage's separate biological benefit is not isolated.

The installed **`dl-binner run`** command now groups the complete learned path and
matched raw control. [E006](../experiments/E006-cli-usability/README.md) accepts its
built-wheel native Mac checks, recovery, resource enforcement and truthful
accounting. The [prepared E006 owner smoke](../experiments/E006-cli-usability/OPERATIONS.md) tests this generic command on CPU/Linux; native Linux return review remains pending. This is an evolving prototype, not a compatibility promise. The
individual commands `prepare`, `train`, `embed`, `cluster`, and `export` remain,
with `--help` on each. `prepare` reads assembly FASTA and optional mean-depth TSV. Its header is
`contig_id` followed by unique ordered sample names. Every FASTA ID needs one
nonnegative finite depth row; row order may vary, but extra/missing IDs fail.
Absent depth is explicit sequence-only mode. Zero depth remains an observation,
with original masks retained. Sample-column order must match the checkpoint at
inference. Full IUPAC DNA is accepted; ambiguous fourmers do not supply TNF counts.
Matching table IDs verifies the input axis, not read-mapping provenance: depth
must originate from this assembly, with reference/alignment hashes recorded in
the pilot. Coverage's biological value has not been established here.

The default length cutoff is configurable 500 bp. Every original ID remains in
the outputs, including excluded short/zero-evidence contigs and cluster noise.
Training uses only eligible data, without labels. It fits and saves transforms;
inference reuses them without refitting. Different contigs are in-batch negatives
and may be co-genomic: this false-negative assumption is explicit and unproven.

Export writes `assignments.tsv`, bin FASTAs, `unassigned.fna`, `excluded.fna` and
a byte-bound manifest. Each input contig appears in exactly one exported FASTA.
Output paths must be fresh; no command silently overwrites an accepted artifact.
Feature/cache/embedding manifests bind ordered IDs, DNA, arrays and parents.
Checkpoints contain tensor state and fitted transforms and use restricted
`weights_only=True` loading. They must still come from a trusted provenance.

Fixed clustering uses exact cosine neighbors, positive mutual five-neighbor
edges, NetworkX greedy weighted modularity at resolution one, and minimum
community size three. It never receives a genome count or truth. Exact neighbor
queries are blocked to bound matrix memory, but greedy modularity is not yet
benchmarked on a full community. E005 checks 5,309 contigs / 12.92 Mb; neither that
cap nor its timing establishes bulk scaling. Retain the raw-feature control;
declining training loss alone does not establish useful bins.

## Prepared next milestone: one end-to-end command

Prepared 2026-10-06; **completed in E006**. The following prospective contract is
preserved as the acceptance basis, not a request to repeat implementation or
accepted demonstrations. The current usage guide is below. E005 accepts scientific outputs and
observed time/RAM limits and improves confirmed assembled recovery, with 51 learned bins from
four genomes and no ≥90% recovered genome. Preserve that limitation; the next
milestone makes the current experimental binner easier to use without tuning it
to this pilot or requiring another benchmark. No public release/upload is authorized.

The E005 review also found that the declared serial schedule overlapped four-
thread jobs. A local launcher/DAG correction is now tested on data-free native
scheduling fixtures; incorporate those options/barriers and check actual scheduling
events rather than a `serial` label. The scientific pilot is accepted without
rerunning it. Corrected generic-launcher Linux execution is still future work.

Implement `dl-binner run` for assembly FASTA, optional explicit mean-depth and a
fresh output directory. Package the unchanged default training JSON and a small
generic Snakemake DAG; the wheel must contain them and work outside this checkout.
Use the separate existing workflow Python supplied by `--workflow-python`, with
the binner process's own absolute Python for native CLI rules. Keep Snakemake out
of the binner environment; no downloads, environment repair, AMBER, E005 locators
or genome labels in the generic run. `--threads` remains 1–4, interop one, loader
zero and serial native stages. Run prepare→train→saved-checkpoint embed→fixed
cluster→complete export, plus the matched raw branch by default. Preserve the
individual stage commands. No new encoder, loss, augmentation, clusterer or tuning.

Add a byte-bound label-free `run-summary.json`/TSV with both arms' bin count and
size distribution, assigned/noise/excluded contigs and bp, exclusion/noise reasons,
original depth zeros/masks and six existing length strata. Report stage time,
sampled CPU/RSS, declared resource budget and what the clocks exclude; local
thread-wall hours are not provider charges. Do not report R95, completeness,
contamination, genome counts or marker quality without a separately supplied
evaluator. Retained E005 outputs can test summary accounting **without** rerunning
their features or model. Summary input hashes must make modifications detectable.

Define fresh/recovery contracts in Git before measured integration: fresh runs
refuse populated outputs; `--resume` explicitly uses the same workdir only after
matching FASTA/depth/config/source manifests. Finished stages must not reschedule;
reject changed inputs or tampered outputs, preserve partial failures and make no
silent overwrite/repair. Capture parent/child output, timestamped progress,
periodic heartbeats and exit codes **inside** the log. Use explicit `-I -B` for
every Python child: isolated mode ignores `PYTHONDONTWRITEBYTECODE`. Preserve
coherent native thread flags, rule benchmarks and fail-fast process supervision.
Prefer reuse of tested E005 supervisors to a new environment/runner framework.

Test the built wheel from an unrelated directory in a **new versioned local
package environment**, leaving accepted E004/E005 prefixes and artifacts intact.
Use tiny new real-DNA software fixtures for sequence-only and two-sample depth,
below-cutoff/no-fourmer masks, observed zeros, empty valid partitions, exact reload,
complete DNA exports, fresh/partial/completed resume, malformed input, changed
sample order/input hashes, corrupt output and fatal-worker/timeout behavior.
Native readers/writers must run; mocks cannot replace the changed path. Reuse the
healthy workflow environment read-only. At most four threads, 8-GB sampled working
RSS, a two-hour timed integration ceiling; initial fixtures ≤32 contigs / 0.6 Mb.
No accepted E002–E005 demonstration or full pilot is repeated. A local Mac pass
does not pre-accept the newly packaged launcher on Linux.

Acceptance is installability, native contracts, truthful summaries, no rescheduled
accepted stages and bounded failures/resources, **not superiority**. Stop expansion
on a concrete contract failure and fix it within this scope. Retain source/input/
wheel/config hashes, logs and a small receipt; update STATE/D011 and commit. Only
then decide whether a tiny owner-run Linux launcher check is needed. No larger
data, extra seeds, three-way study, architecture gate, push or publication by default.

## Run the binner

Use the installed package in its own CPU environment, plus a **separate existing
Snakemake 9.16.3** Python. The command installs nothing and needs no repository
checkout, internet connection, marker database or truth labels. Defaults and DAG
are inside the wheel. Keep interpreter paths lexical: resolving a venv's `python`
symlink can bypass that environment.

```sh
dl-binner run --fasta assembly.fna --output result \
  --workflow-python /absolute/workflow/bin/python --threads 4
```

Add `--depth mean-depth.tsv` for explicitly supplied mean depth on this exact
assembly. Its `contig_id` header and ordered sample columns follow the contract
above. Depth zeros remain observations; absent depth stays sequence-only. An
alternative to the flag is `DL_BINNER_WORKFLOW_PYTHON=/absolute/workflow/bin/python`.
`dl-binner run --help` shows examples, limits, output paths and recovery options.

The initial defaults remain seed 11, 20 epochs, hidden 128/output 64, mask 0.1,
NT-Xent temperature 0.2, AdamW 0.001/weight decay 0.01 and batch/inference 64.
`--training-config` explicitly selects a JSON matching the existing contract.
`--min-length` defaults to 500; all excluded DNA is preserved. This bounded
version supports 1–4 numerical threads, interop one and loader zero. `--memory-gb`
defaults to 8 GB sampled aggregate working RSS, and `--timeout` to 7,200 seconds
per invocation, including hashing, probes and final accounting. Limits can be
lowered. Tiny/serial stages may not saturate the requested threads.

Outputs are predictable:

```text
result/
  run-manifest.json       input, source, config, environment and budget bindings
  run-summary.json       both arms, masks/reasons/strata and resource receipts
  run-summary.tsv        concise status counts and bp in every length stratum
  completion.json        summary/stage-receipt hashes
  learned/bins/          assignments.tsv, bin_*.fna, unassigned.fna, excluded.fna
  raw/bins/              matched raw control with the same complete exports
  features/              original TNF/depth, ordered axes and masks
  training/              checkpoint, transforms, epochs and pre-save embeddings
  receipts/              successful stage output/evidence hashes
  logs/invocation-*/     terminal.log, status.json, native logs/samples/benchmarks
  staging/               uniquely named retained stage attempts
```

Status/progress lines name each of eight stages; long steps print ten-second
heartbeats. The terminal log captures final exit codes (0 success/intentional
partial stop, 1 failure, 130 cancellation). Errors name the native cause and log
when available. Verbose traces stay in the invocation log. Resources are sampled
process-tree estimates, not exact peaks or provider invoices; the JSON explains
its clocks and preserves each completed stage's original resource receipt.

Fresh execution refuses a populated output directory. To continue the same run,
repeat its input/options and add `--resume`:

```sh
dl-binner run --fasta assembly.fna --output result \
  --workflow-python /absolute/workflow/bin/python --threads 4 --resume
```

FASTA/depth/config/source/runtime/budget and every completed artifact must match.
Finished stages are reused; completed runs schedule no scientific work. Changed,
missing or extra published artifacts fail with evidence retained. Failed work
uses a new staging folder on retry; unreceipted published final artifacts are
refused, never silently repaired. `--stop-after train` makes a deliberate partial
run; omit that flag when continuing. Wall time is per invocation. A stale
`.run-lock` names its PID/host; verify that process has stopped before removing it.

Summary assignment/bin size is **not** genome recovery, completeness,
contamination or MAG quality. AMBER/R95 remain separate evaluation with explicit
truth. E006's synthetic-depth/tiny-DNA fixtures establish software behavior, not
coverage benefit or biological generalization. Accepted E005 accounting was read
from retained outputs; no inference/clustering/evaluation was repeated.

**Next bounded step:** prepare and locally test one tiny checksum-bound owner-run
CPU/Linux generic-launcher smoke. Reuse intact UCloud workflow/assets read-only,
keep the new package in a version-qualified prefix, capture logs/returns and stop
for review. Do not copy the linked Mac test environment to Linux. No new dataset,
seed, architecture gate, three-way study or publication is authorized.
