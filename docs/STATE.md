# Current Research State

Updated: 2026-09-18

This is the single current handoff. Detailed evidence belongs in the linked records; this page stays short.

## Where we are

- The intent is defined in [PROJECT_INTENT.md](../PROJECT_INTENT.md).
- The targeted [paper/code audit](evidence/2026-09-17-targeted-audit.md) and [public-data audit](evidence/2026-09-17-benchmark-data.md) are complete for designing the first diagnostic, building on the [initial assessment](research/2026-09-16-initial-assessment.md).
- [E001](../experiments/E001-coverage-thinning/README.md) now has its Gate 0 harness, native adapters, tests and CPU-only smoke scripts. Portable checks passed; exact native Linux checks and scientific execution have not run. See the [validation record](../experiments/E001-coverage-thinning/validation.md).
- [D004](decisions/D004-human-cpu-preflight.md) supersedes D003's dataset/mapper/resource assumptions after owner feedback and a [targeted reassessment](evidence/2026-09-18-human-cpu-audit.md). D002's diagnose-before-architecture direction and D001's research record remain valid. No methodological gap, new model or scientific benchmark score exists yet.

## Immediate direction

Investigate **where reduced coverage evidence loses recoverable sequence**, using CAMI II HMP's **gastrointestinal** short-read GSA and native MetaBAT2, VAMB and COMEBin, contingent on CPU feasibility. Compare pair-preserving read thinning with full evidence and a preprocessing-only scale control. Use strobealign 0.17.0 full SAM provisionally, pending native smoke and a fixed read-prefix comparison with Bowtie2. Human-associated microbiomes are the core focus, not environmental data.

The audit found live total-abundance input in current VAMB and coverage in the inspected DCVBin path, native marker/selection effects, and relevant reliability prior art in GenomeFace, UncertainGen, McDevol and QuickBin. Lower scores after removing reads alone will not support H001: we need evidence that usable signal survives but is lost downstream. AMBER is the chosen standard evaluator; portable supplementary metric fixtures are implemented and tested, while native parity and integration with scientific outputs remain pending.

E001 is development/diagnosis, not SOTA evaluation, real-assembly validation or a demonstration of unseen-genome generalization. [H001](research/questions.md#h001) remains untested; architecture and the final target regime remain open.

## Next session

1. Guide the owner through the [operations guide's transfer/prerequisite checkpoint](../experiments/E001-coverage-thinning/OPERATIONS.md#first-checkpoint-transfer-and-prerequisites). A committed-code bundle builder is ready. The owner has run nothing on UCloud; wait for upload checksum and Terminal probe output before extraction/bootstrap, then guide mapping setup, mapping smoke, AMBER setup and AMBER smoke as separate inspected steps. Initial job: 8 vCPU, at least 24 GB RAM, two hours, no GPU. No research training or bulk reads.
2. Inspect returned locks/logs, then acquire GI GSA, corrected truth and setup only. Check coordinate-to-anonymous-ID joins and resolve historical taxonomy. The supplied commands intentionally block scientific population approval without domain resolution.
3. Complete the remaining native smoke, measured CPU/full-batch and read-prefix/storage feasibility, then freeze inputs and runtimes. Only afterward implement/authorize the scientific launcher and paired pilot. If COMEBin exceeds budget, amend the scientific scope/triage prospectively rather than silently dropping it.

## Open dependencies

- Fresh **HMP GI** acquisition replaces the earlier Marine plan. Publisher checksum metadata and tiny file prefixes are inspected, not complete payloads. GI sample numbers are nonconsecutive; the source-coordinate FASTA and anonymous truth require an explicit join. See [acquisition manifest](../experiments/E001-coverage-thinning/acquisition.json).
- HPC is owner-operated and **CPU only**: 2,100 allocated core-hours, up to 128 vCPU/384 GB RAM. Terminal / Ubuntu / Aug2026 on DeIC Interactive HPC (SDU/K8s), persistent root `/work/Home/dl_binner/e001/e001-gate0`, with per-tool environments under `envs/`. The [E001 configuration](../experiments/E001-coverage-thinning/config.json) caps this diagnostic at 800 core-hours with nested smaller preflight/preprocessing limits; affordability is not established. The owner can expand storage: 200 GB is now a provisioning review threshold, not a scientific ceiling. Do not shrink E001 to fit it.
- Selected source commits are recorded in [tool snapshots](evidence/2026-09-17-tool-snapshots.json); runnable environments are not yet validated. GenomeFace is unversioned, McDevol has an abnormal index state, and DCVBin lacks a model payload. These optional comparisons do not block the core E001 preflight.
- Linux environment recipes are prepared but unresolved/unexecuted, with no verified container digest. Exact native AMBER/normalization parity, CPU throughput, marker payloads and complete data joins remain gates. Application/path are owner-confirmed; installed prerequisites and mounted path remain unverified. Access expiry is unknown, not a blocker for this synthetic check.
- Original thesis artifacts remain owner-confirmed on UCloud and optional. Final evaluation/success claims remain open in the [question register](research/questions.md); E001 has only scoped diagnostic criteria.

## Git and continuity

- Local implementation branch: `e001-gate0`; based on `main` at `bc1a3c5`. Baseline commit `2b87cd9` preserves supplied context. Use Git history for subsequent commits; no research run depends on an uncommitted configuration.
- No remote is configured; the owner clarified it has not been created. Nothing has been published or pushed.
- Thesis source and figures need not be part of the eventual public project's working tree. They are already in local Git history; leave them intact until the separate pre-publication packaging decision in [D001](decisions/D001-research-record.md#source-packaging-clarification-2026-09-17). Do not rewrite history silently.
- Original planning remains in [history](history/README.md), explicitly nonbinding. New superseded decisions and experiments retain their own identities and links.

Update this page whenever the immediate direction, significant evidence, or execution dependencies change. Do not turn it into a chronological session log.
