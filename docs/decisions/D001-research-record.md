# D001: One Current Handoff, Linked Research Records

Date: 2026-09-16
Status: accepted

## Problem

The starting folder contained stable intent, earlier plans, a thesis snapshot, paper transcriptions, and downloaded tool sources. There was no Git repository or active research record. Several historical files contained their own authority and roadmap language.

## Decision

Use [STATE](../STATE.md) as the current handoff and the ownership rules in [WORKING](../WORKING.md). Keep evidence, questions, decisions, and experiments linked with stable identities. Keep source reports separate from observations and hypotheses. Preserve failed attempts and abandoned ideas within their own records.

Initialize local Git and preserve the starting material before changing guidance. Track the existing thesis snapshot and figures, original planning, and project records. Keep third-party paper/tool caches external to Git, with local fingerprints and upstream locators for consulted sources. No architecture scaffold or model implementation is needed now.

## Alternatives considered

- A single growing research log is easy to begin but makes the active state and record ownership hard to recover.
- A wiki or experiment-tracking service can become useful later, but adds hosting and synchronization before there are runs to track.
- Many parallel status, failure, roadmap, and learning documents create competing summaries. Keep these details with their originating questions and experiments instead.
- Vendoring all tool folders would add roughly 324 MB of downloaded source without verified upstream revisions. Pin runnable dependencies when selected for an experiment.

## Consequences and review

Agents update the current handoff when direction changes, while past evidence and outcomes remain identifiable. Git records ordinary editing history; important scientific reversals also receive explicit explanations. New record files are created on demand rather than preallocating a roadmap.

Revisit if the question register becomes difficult to navigate, multiple people need concurrent experiment tracking, or run volume makes ordinary manifests inadequate. Any later service must preserve exportable protocols, provenance, and conclusions in the repository.

## Source-packaging clarification, 2026-09-17

The owner correctly distinguishes the thesis from this new project's software: it is a prior source paper, and its full text/figures need not be vendored into the eventual public working tree. Retain citations, provenance and our interpretations regardless of source packaging. Clones and ZIP caches are both acceptable research context; only sources selected for execution require a verified runnable dependency chain.

The thesis snapshot already exists in the foundation commits. Removing it from the current index or adding an ignore rule would **not** remove it from history or prevent its transfer in a first push. During this audit we therefore leave local source files/history intact and record the pre-publication choice explicitly. When publication is requested, recommend a lean current tree with source locators; decide with the owner whether retaining the existing source-containing history is acceptable or whether a separately approved history migration is needed. No remote creation, push, deletion or history rewrite is authorized by this clarification.

## Local inbox clarification, 2026-09-19

The owner now requests that all `agent_context/` remain a local inbox, including
inventory uploads, prompts, logs, screenshots, papers and thesis material. Ignore
the entire directory and remove existing entries from the current Git index,
preserving files on disk and earlier commits. Maintained research records own
reviewed findings and reproducibility-critical summaries/hashes. Local-context
links are optional in a clean checkout. Historical uploads remain recoverable
from Git; their presence in old commits still requires review before publication.
This supersedes the earlier choice to retain context files in current tracking,
but does not authorize deletion or history rewriting.
