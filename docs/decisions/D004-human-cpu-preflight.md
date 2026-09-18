# D004: Center E001 on Human Gut Data and CPU Feasibility

Date: 2026-09-18
Status: accepted, with mapper and full-schedule feasibility gates
Supersedes: [D003](D003-coverage-diagnostic.md)'s dataset and execution assumptions; retains its scientific diagnostic question
Evidence: [human/CPU audit](../evidence/2026-09-18-human-cpu-audit.md); owner brief [prompt3](../../agent_context/prompt3_second_step.md)

## Decision and reasoning

1. Replace Marine with the **CAMI II HMP gastrointestinal subset**, using the body-site-specific short-read GSA and corrected truth. The project prioritizes human-associated microbiomes; this is not an environmental project merely because the thesis was environmental. Keep all ten GI sample columns, with the archive's actual sample IDs, and label this old public simulation as development data.
2. Replace BWA-MEM2 with **strobealign 0.17.0 full SAM alignment**, provisionally. Speed/memory reports make it worth a CPU preflight, not a guaranteed performance claim. Bowtie2 is the preferred fixed-prefix comparison and fallback. Do not use abundance-only mapping or choose a mapper using binner scores.
3. Plan **CPU only**. Retain native MetaBAT2, VAMB and COMEBin as the intended diagnostic panel, but require environment, storage and full-batch CPU cost checks before approving its complete schedule. No default assumption of future GPU access. Allocate only a bounded part of the 2,100-core-hour project budget; use the numerical limits in [E001 config](../../experiments/E001-coverage-thinning/config.json).
4. Implement portable validation and native adapters now; prepare, but do not execute, research-data acquisition/training. UCloud execution remains owner-controlled. Source pins are known, but unresolved native environments are not called reproducible runtimes.

The sequence-selection rule, read-thinning contrast, conservative endpoint, seeds and scientific triage criteria remain unchanged. GI source-coordinate headers require an explicit mapping to anonymous IDs, unlike the earlier assumed already-anonymous FASTA. No scientific outcome has been observed during this amendment.

## Alternatives considered

- Retain Marine: scientifically serviceable but misaligned with the clarified project focus; no diagnostic control depends on that environment.
- CAMI III toy human gut: human-associated and current, but larger and not needed to answer this first contrast. Preserve it as a candidate for a later independent or mechanistic study; do not call it permanently held out before an overlap audit.
- Bowtie2 first: mature, memory-conscious and familiar; a good fallback. We choose to test strobealign's potential efficiency before paying for all mappings.
- minibwa first: credible released alternative; the author's relative speed claims do not establish its behavior on this GI assembly. A full mapper benchmark would expand the task unnecessarily.
- Drop COMEBin immediately or assume it will be affordable: neither follows from lack of a GPU. Check actual native CPU throughput first. A smaller neural method alone cannot answer the current COMEBin-specific selection question.
- Request much more storage immediately: unnecessary for the small initial inventory. A larger quota may be warranted after measured archive/read/BAM expansion; it does not add CPU budget.

## Revisit and stopping conditions

Operational clarification, 2026-09-18: the owner can expand storage and explicitly rejects shrinking E001 to fit the initial conservative estimate. The former 200-GB working ceiling is now a provisioning review threshold (`working_storage_review_gb`); CPU and population ceilings remain unchanged. Preserve measured storage estimates and provision adequate space before execution. No dataset, replicate, training or endpoint change follows from this clarification.

Unresolved truth/coordinate joins, unknown taxonomy, insufficient short-contig/genome support, native parity failures or projected budget overruns block scientific launch. Amend prospectively rather than choosing successful genomes, silently changing native defaults, or converting crashes to zero recovery. A narrower CPU-feasible diagnostic is acceptable, but requires explicitly revised claims and triage rules if COMEBin is removed.

The next step is **owner-run mapping/AMBER synthetic smoke**, followed by returned-output inspection before GI assembly/truth inventory. No new model design is warranted yet. [E001](../../experiments/E001-coverage-thinning/README.md) and its [operations guide](../../experiments/E001-coverage-thinning/OPERATIONS.md) own execution details.
