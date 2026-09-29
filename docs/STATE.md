# Current Research State

Updated: 2026-09-29. This is the single current handoff.

## Direction

Build and publish a usable deep-learning metagenomic binner while learning through
its development. A paper, novelty and SOTA performance are optional future bonuses,
not prerequisites for the first implementation. [PROJECT_INTENT](../PROJECT_INTENT.md)
and [D010](decisions/D010-bounded-e001-and-prototype.md) record the owner's clarification.
Finish E001's bounded retained-output analysis, then rethink the first prototype;
E001 closes at the explicitly amended seed-11 pilot scope. After closure, conduct
the comprehensive literature/code review described in [PROJECT_INTENT](../PROJECT_INTENT.md)
before fixing the first model architecture. Do not expand the experiment campaign
automatically.

## Accepted evidence

- E001 uses the frozen CAMI II HMP GI development derivative: 22,594 contigs and
  224 evaluation genomes. [D005](decisions/D005-gi-input-derivative.md) and
  [frozen inputs](../experiments/E001-coverage-thinning/frozen-inputs.json) retain
  provenance/exclusions. It is not an unchanged benchmark or real assembly.
- Mapping, all ten samples' C0/CT preprocessing and native features are accepted.
  Reuse the [BAM manifest](../experiments/E001-coverage-thinning/multisample-bam-manifest.json)
  and [features](../experiments/E001-coverage-thinning/features-observed.json).
  No download, remapping, rethinning or feature extraction is needed.
- Seed-11 [MetaBAT2/VAMB](../experiments/E001-coverage-thinning/paired-pilot-observed.json)
  remain accepted: R95 C0→CT is 0.44294→0.19502 and 0.46177→0.48764 respectively.
- The latest checksum-bound COMEBin resume completed; its preserved C0 was reused.
  Native early stopping at epochs 111/107, complete selected partitions and
  independent AMBER/R95 recomputation pass. R95 is **0.83899→0.80255**.
  [Review](../experiments/E001-coverage-thinning/comebin-paired-observed.json) accepts
  native execution and primary evaluation, with explicit binary-evidence limits.
- All 120 candidate receipts per condition and marker-score selection pass compact
  checks. Candidate/embedding arrays were omitted from that return. Direct binary
  inspection, oracle-selection gap and representation diagnostics still need the
  retained bytes; they do not require rerunning scientific work.

## Exact next step

Run the [read-only diagnostic collection](../experiments/E001-coverage-thinning/OPERATIONS.md#current-action-2026-09-29-collect-retained-diagnostics)
once on UCloud, using the prepared two-file transfer and printed logging command.
It packages 297 checksum-bound files (~435 MB uncompressed), using standard-library
Python, one CPU worker and a 20-minute stop limit. Owner returns archive, checksum,
collection-status JSON and terminal log. No new seeds, training or clustering.

Then locally verify all candidate labels and embeddings, complete the existing
selection/neighborhood/length diagnostics, and close E001 at amended seed-11 scope.
**Seeds 23/47 are deferred**, not silently completed. No three-seed reproducibility
claim or rejection of H001 is permitted. [Combined assessment](../experiments/E001-coverage-thinning/seed11-assessment.md)
and [costs](../experiments/E001-coverage-thinning/seed11-cost-assessment.json) explain
why further replication is not the next useful expense. Then complete the
comprehensive current literature/benchmark review and targeted source-code review
of leading candidates before choosing the first architecture. This is not a novelty
gate; low-risk scaffolding may proceed alongside it.

## Resources and continuity

COMEBin's successful conditions used 39.6462 allocated core-hours on 8 vCPU / 24 GB;
the successful resume driver used 16.1518, already containing CT's rule cost.
Known COMEBin recovery-sequence spend is at least 58.1075 core-hours, not exact
billing or total E001 spend. Retained successful condition files sum to 11.313 GB,
excluding recovery copies and other assets. Preserve every old attempt.

UCloud remains owner-operated and CPU-only. The dated allocation was 2,100
core-hours with an E001 ceiling of 800; exact remaining balance is not known.
Do not infer remaining budget from this partial accounting. Persistent tool prefixes
remain under `e001-gate0/envs/` per [D006](decisions/D006-environment-ownership.md).
Scientific source/config hashes stay frozen; D010 changes prospective scope only.

Local branch: `e001-gate0`. No remote is configured and nothing has been pushed or
published. `agent_context/` remains an ignored inbox. Before publication, review
licensing and historical source packaging per [D001](decisions/D001-research-record.md).

Update this handoff when immediate direction, significant evidence, or execution
dependencies change; keep it concise and put session chronology in the owning records.
