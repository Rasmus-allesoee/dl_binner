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
accounting. [E006's Linux return](../experiments/E006-cli-usability/README.md#accepted-native-linux-return-and-independent-review-2026-10-06)
now accepts that generic command, native serial placement, strict resume and
failure/resource handling on the reviewed CPU/Linux runtime. This is an evolving
prototype, not a compatibility promise or whole-MAG validation. The
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
rerunning it. E006 now accepts corrected generic-launcher native Linux execution;
the E005 scientific DAG was not rerun merely to validate its launcher correction.

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

The E006 owner smoke is accepted; do not repeat it or transfer a linked test
environment. Its immutable wheel remains the reference for the next milestone.

## Prepared private-PR readiness milestone

Prepared 2026-10-06 after E006 Linux acceptance; **not implemented or a published
release**. One bounded packaging/testing/documentation task should make this
branch reviewable as the first usable prototype. Acceptance concerns independent
installation and regression reproducibility, not superiority or another scientific
gate. Then request separate authorization to push/open a private PR and, after
review, merge. Do not silently publish or merge as part of local preparation.

The concrete remaining gap is that accepted execution borrows reviewed numerical
dependencies and several current tests require ignored E003/E005 outputs or local
setup paths. The package runs, but a clean clone cannot reproduce its ordinary
software checks or follow a verified independent install recipe. There is no
checked-in CI workflow or selected project license. Those are distinct from the
already validated input/model/export behavior.

Freeze the implementation contract before any new measured software integration:

1. Provide a concise product-first README and installation guide for separate
   binner/workflow CPU environments. Commit version-pinned dependency constraints
   and CPU-PyTorch selection using the accepted versions. Keep platform support
   honest: Python 3.10 Mac and 3.12 CPU/Linux have native evidence; the declared
   3.10–3.12 range is not a complete tested matrix. Install from cached dependencies
   where healthy; use a fresh versioned prefix for a standalone recipe test, no
   links to accepted environments. Do not upgrade/delete/rebuild old prefixes.
2. Build wheel **and sdist** from a clean source snapshot; inspect their contents,
   hashes and metadata/defaults/DAG. Test installation and `dl-binner run --help`
   outside the checkout, with neither checkout imports nor ignored caches. Keep
   accepted dev1 wheel/source hashes as immutable provenance; version a changed
   packaging snapshot separately. Preserve model, transforms, objective, training
   defaults and clustering exactly. Do not rewrite old resume manifests to make
   a new version appear compatible.
3. Separate self-contained product regressions from opt-in retained research
   reviews. Commit tiny deterministic synthetic DNA/depth fixtures or generators
   for ordinary reader/mask/transform/export/failure tests; they establish software
   behavior only. Reuse E006's accepted real-DNA native return as evidence without
   rerunning it. Ordinary targeted checks must pass from the clean snapshot with
   no `agent_context/`, `artifacts/` or experiment-specific setup path. Keep the
   retained E003/E005/E006 accounting/evidence checks available and explicitly
   separate, not silently skipped and called a full scientific validation.
4. Prepare a small CPU/Linux CI workflow that installs the built wheel and runs
   those targeted product contracts and documentation checks. No heavy datasets,
   model downloads, scientific demonstrations or inference benchmark. Capture
   logs, installed origins/inventories and bounded failures; reconcile test CPU
   limits with runner allocation. A checked-in workflow is preparation; only an
   actual authorized remote run validates that Linux installation/CI path.
5. Write an honest validation/limitations section and concrete private-PR review
   description linking D011/E004–E006: what works, what was tested, what is not
   established, failure/resume semantics and resources. Inspect current-tree and
   historical third-party/source packaging; report any public-publication issues
   without deleting files or rewriting history. Do not invent an owner license
   choice. Licensing/public redistribution needs a later explicit owner decision;
   it need not delay a private implementation PR.

Use **at most four numerical threads, interop one, loader zero, 8 GB working RSS**
and a **two-hour measured software integration ceiling**; tiny software fixtures
remain **≤32 contigs / 0.6 Mb**. Freeze whether setup falls inside the clock and
account it separately when excluded; capture entry/setup/test logs and exit codes.
No training schedule change, E002–E006 scientific replay, extra seed/dataset,
UCloud execution, three-way study, architecture gate or remote publication.
Native tiny product regression tests are allowed; do not relabel them biological
evidence. Stop on a concrete packaging/contract failure and fix that cause within
scope. Native independent Linux installation remains pending until actually run;
do not require another owner smoke by default when existing evidence/authorized
CI can establish the relevant path.

Keep this milestone if the package/tests are reproducible without local research
artifacts. Repair a specific install or contract defect if they are not. Abandon
optional packaging polish when it delays the private PR without fixing a real
usability/reproducibility issue. No notebook, Docker/Conda matrix, plugin framework,
public release automation or broad refactor is required.

Alternatives considered: opening the PR immediately would already expose a usable
tool, but leave clean-checkout tests/install instructions dependent on this workspace.
A broad release framework or additional quality benchmark would add unrelated
work before stabilizing the baseline. The narrow packaging/regression task addresses
the observed gap directly and should finish before proposing the PR.

After a separately authorized review/merge, use a **new branch from updated main**
for benchmark work and deliberate matched architecture investigation. Preserve
the accepted baseline/settings and source commits. That later stage should freeze
scope, development/test separation, short strata, raw controls, bin-quality/resource
metrics and overlap before executing; refresh relevant new papers/code then. The
already requested TNF / frozen-GLM-head / hybrid study remains a serious planned
option, not today's implementation or a reason to delay the first prototype.
