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
