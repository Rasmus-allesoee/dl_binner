# Source Context

These materials explain the project's background. Current authority is [PROJECT_INTENT](../PROJECT_INTENT.md), [AGENTS](../AGENTS.md), and the linked [current state](../docs/STATE.md).

| Material | Role and provenance |
| --- | --- |
| [Thesis](thesis/MSc_RasmusAN_SDU_v5.md) and [supplement](thesis/MSc_RasmusAN_SDU_sup_final_v1.md) | Prior study, preserved with its original figures. Both Markdown files match the inspected thesis repository at commit `4029b810045ff9196be0035e48e7fb32ca4be792`. Source work: Rasmus A. Nielsen, MSc thesis, SDU, June 2026; source repository documents CC BY 4.0 for data/figures/docs. |
| [Beginning-of-project prompt](prompt_beginning_of_project.md) | The owner brief that initiated foundation setup |
| [First research-step prompt](prompt2_first_step.md) | Owner brief and feedback initiating the targeted audit, including public-benchmark and source-cache clarifications |
| [Planning conversation](chatgpt_project_planning.md) | Historical motivation and alternatives; subsequent owner instructions and PROJECT_INTENT take precedence |
| `papers/` | Local paper copies and transcriptions, excluded from Git; neither an exhaustive bibliography nor proof of review |
| `tools_repo/` | Mixture of clones and ZIP/source copies, excluded from Git; selected commits and qualifications are recorded in the tool snapshot manifest |

Use the [evidence index](../docs/evidence/README.md) for interpretations and [asset record](../docs/evidence/assets.md) for reuse. [Context fingerprints](../docs/evidence/context-sources.sha256) identify the current inventoried files; older versions remain in Git. [Tool snapshots](../docs/evidence/2026-09-17-tool-snapshots.json) records selected repository commits separately. A fingerprint does not recover a missing file or identify an upstream commit.

The complete thesis snapshot is already in local Git history. Treat it as a source paper, not project implementation; [the source-packaging decision](../docs/decisions/D001-research-record.md#source-packaging-clarification-2026-09-17) explains the separate review before eventual publication.

On a fresh checkout, optional paper/tool caches will be absent. Consult the upstream links in the landscape note; obtain and pin the needed versions before execution. Do not assume a newly downloaded default branch reproduces a recorded local copy. Original paper copies remain untouched when a newer publication is discovered; record the new version in the research note.
