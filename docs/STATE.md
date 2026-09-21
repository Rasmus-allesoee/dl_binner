# Current Research State

Updated: 2026-09-21

This is the single current handoff. Detailed evidence belongs in the linked records; this page stays short.

## Where we are

- The intent is defined in [PROJECT_INTENT.md](../PROJECT_INTENT.md).
- The targeted [paper/code audit](evidence/2026-09-17-targeted-audit.md) and [public-data audit](evidence/2026-09-17-benchmark-data.md) are complete for designing the first diagnostic, building on the [initial assessment](research/2026-09-16-initial-assessment.md).
- [E001](../experiments/E001-coverage-thinning/README.md) has its Gate 0 harness, native adapters and tests. Owner-run mapping/AMBER checks passed, including clean-environment reruns. EasyBuild exposure was traced to UCloud's user site and excluded without changing the installed environments. This clears the GI inventory prerequisite, not all Gate 0 checks or scientific launch. See the [validation record](../experiments/E001-coverage-thinning/validation.md).
- [D004](decisions/D004-human-cpu-preflight.md) supersedes D003's dataset/mapper/resource assumptions after owner feedback and a [targeted reassessment](evidence/2026-09-18-human-cpu-audit.md). D002's diagnose-before-architecture direction and D001's research record remain valid. No methodological gap, new model or scientific benchmark score exists yet.

## Immediate direction

Investigate **where reduced coverage evidence loses recoverable sequence**, using CAMI II HMP's **gastrointestinal** short-read GSA and native MetaBAT2, VAMB and COMEBin, contingent on CPU feasibility. Compare pair-preserving read thinning with full evidence and a preprocessing-only scale control. Use strobealign 0.17.0 full SAM provisionally, pending native smoke and a fixed read-prefix comparison with Bowtie2. Human-associated microbiomes are the core focus, not environmental data.

The audit found live total-abundance input in current VAMB and coverage in the inspected DCVBin path, native marker/selection effects, and relevant reliability prior art in GenomeFace, UncertainGen, McDevol and QuickBin. Lower scores after removing reads alone will not support H001: we need evidence that usable signal survives but is lost downstream. AMBER is the chosen standard evaluator; portable supplementary metrics and isolated native evaluator fixtures passed. Integration with scientific outputs remains pending.

E001 is development/diagnosis, not SOTA evaluation, real-assembly validation or a demonstration of unseen-genome generalization. [H001](research/questions.md#h001) remains untested; architecture and the final target regime remain open.

## Next session

1. The 20 FASTA-only intervals have foreign-simulation provenance: seven publisher BAM headers name airskinurogenital sources absent from the gastrooral setup. Both truth tables omit all 20. [Evidence and code review](evidence/2026-09-19-gi-provenance.md) and [D005](decisions/D005-gi-input-derivative.md) authorize a hash-bound quarantine, totaling 28,917,470 bp, plus two empty artifacts. This creates a declared E001 development derivative. Original downloads remain intact; local and owner preparation status is distinguished below.
2. Taxonomy-aware owner return `inventory-resume-6z45cola` matches every pinned population output and is accepted. [Frozen inputs](../experiments/E001-coverage-thinning/frozen-inputs.json) fix the UCloud locator, provenance and hashes: 22,594 contigs, 224 evaluation genomes, 7,964 short queries. No more conversion/taxonomy checks are needed absent changed inputs. See [validation](../experiments/E001-coverage-thinning/validation.md).
3. All three tools' native synthetic smoke and bounded CPU checks are accepted separately: [VAMB](../experiments/E001-coverage-thinning/native-vamb-observed.json), [COMEBin](../experiments/E001-coverage-thinning/native-comebin-observed.json), [MetaBAT2](../experiments/E001-coverage-thinning/native-metabat-observed.json). COMEBin's successful earlier attempt is not invalidated by its companion MetaBAT2 setup failure. The later MetaBAT2-only return passes. Preserve fixes f4cf0c0, 41d0f9d and f9c983a; do not repeat these checks.
4. [D007](decisions/D007-comebin-resource-envelope.md) raises only COMEBin's prospective per-fit limit to 200 core-hours (95.8 projected, 191.6 with margin). The total remains 800; the full six-fit schedule is not yet authorized. The resource-only [compute policy](../experiments/E001-coverage-thinning/compute-policy.json) overrides the old per-fit ceiling without changing frozen input identity.
5. Next run grouped native VAMB/COMEBin clustering, COMEBin marker/selection and AMBER handoff in the [operations guide](../experiments/E001-coverage-thinning/OPERATIONS.md), using 8 vCPU / 24 GB and existing environments. It uses a bounded sequence fixture and random embeddings, with no training, installs or downloads. Then resolve read-prefix acquisition for mapper/storage feasibility: direct CAMI reads returned HTTP 401, whereas the accessible publisher archive begins with BAMs. No bulk reads or scientific training authorized.

## Open dependencies

- **HMP GI** assembly/truth/taxonomy and evaluation population are accepted and frozen. Continue with this declared development derivative, not an unchanged benchmark. Mapping/AMBER and all three tool smoke/CPU checks passed; native clustering/marker integration and read-prefix gates still precede science. See [frozen inputs](../experiments/E001-coverage-thinning/frozen-inputs.json).
- HPC is owner-operated and **CPU only**: 2,100 allocated core-hours, up to 128 vCPU/384 GB RAM. Terminal / Ubuntu / Aug2026 on DeIC Interactive HPC (SDU/K8s), persistent root `/work/Home/dl_binner/e001/e001-gate0`, with per-tool environments under `envs/`. The [E001 configuration](../experiments/E001-coverage-thinning/config.json) caps this diagnostic at 800 core-hours with nested smaller preflight/preprocessing limits; affordability is not established. The owner can expand storage: 200 GB is now a provisioning review threshold, not a scientific ceiling. Do not shrink E001 to fit it.
- Selected source commits are recorded in [tool snapshots](evidence/2026-09-17-tool-snapshots.json); core E001 environments passed scoped native checks, not full scientific workflows. GenomeFace is unversioned, McDevol has an abnormal index state, and DCVBin lacks a model payload. These optional comparisons do not block the core E001 preflight.
- [D006](decisions/D006-environment-ownership.md) retains separate experiment-owned environments, with mapping/AMBER/VAMB reused at their accepted `e001-gate0/envs/<tool>` paths across later gates. No migration or common Python base. COMEBin and MetaBAT2 use their own prefixes there. The grouped driver uses persistent micromamba, no GNU time or root package installs. Job duration is owner-managed; host resources are not allocation measurements.
- Original thesis artifacts remain owner-confirmed on UCloud and optional. Final evaluation/success claims remain open in the [question register](research/questions.md); E001 has only scoped diagnostic criteria.

## Git and continuity

- Local implementation branch: `e001-gate0`; based on `main` at `bc1a3c5`. Baseline commit `2b87cd9` preserves supplied context. Use Git history for subsequent commits; no research run depends on an uncommitted configuration.
- No remote is configured; the owner clarified it has not been created. Nothing has been published or pushed.
- Owner clarification, 2026-09-19: all `agent_context/` is an ignored local inbox. Existing files are removed from current Git tracking while retained on disk and in historical commits. Durable reviewed findings stay in research documentation. This does not sanitize historical material for future publication; [D001](decisions/D001-research-record.md) still requires a separate history/publication review.
- Original planning remains in [history](history/README.md), explicitly nonbinding. New superseded decisions and experiments retain their own identities and links.

Update this page whenever the immediate direction, significant evidence, or execution dependencies change. Do not turn it into a chronological session log.
