# Newer graph evidence for the E034 representation block

Reviewed November 5, 2026, before native paired-link counts or community outcomes.
Purpose: choose a scalable, uncertainty-aware genome-graph treatment after E033's
rejected learning bundle. This is source inspection, not reproduced tool performance.

## UnitigBIN (ICLR 2024)

Primary [repository](https://github.com/xuehansheng/UnitigBIN), inspected commit
`1301766eb02982e04da8fe6f59af8b363aa281e8`; exact README/main/loader/model/modules/
utils/run bytes are in [E034's source audit](../../experiments/E034-genome-graph/source-audit.json).
The primary [paper record](https://openreview.net/forum?id=vBw8JGBJWj) identifies
*Encoding Unitig-level Assembly Graphs with Heterophilous Constraints for
Metagenomic Contigs Binning*. The publisher PDF returned HTTP 403/challenge, so
this note does not claim a full-paper methods/equations read.

Direct code observations: UnitigBIN learns on a unitig GFA and contig-path join,
then matches marker-bearing contigs, propagates to others and refines. Its graph
disentanglement can clone a shared unitig between marker-conflicting contigs.
`loader.batchGraph`'s `readsPair` links duplicated unitigs across graph batches;
it is **not paired-end read evidence**. `model.PPRDiffusionConv_Torch` constructs
dense square matrices and a matrix inverse; its VGAE also reconstructs dense
adjacency. We must not transpose that implementation onto approximately half a
million Oral contigs. Gaussian embedding uncertainty is not measured within-
contig coverage variance. The defined `filter_margers(markers, groundtruth)` is
not called by the inspected default `load_data` / `load_data_flye` paths; its
presence alone does not establish default label leakage.

Transferable lesson: preserve graph resolution and distinguish connection from
unconditional same-genome identity. Our retained Oral GSA has no admitted unitig
assembly graph. Source-genome coordinates cannot supply one without truth leakage.
The E034 scope therefore uses actual mate templates from retained BAMs. Hard SCG
cannot-links are inappropriate without resolving the repeated-locus/call issues
already established by E011/E012. No UnitigBIN executable or database is run.

## More recent screens and scalable graph encoding

[MBGCCA, 2025](https://pubmed.ncbi.nlm.nih.gov/41008047/) describes two-stage
composition/abundance learning followed by assembly-graph contrastive/InfoMax
representation learning. This is an abstract-level screen, without a complete
source/runtime review or reproduced recovery claim. It supports separating the
information graph and its representation from the final constructor; it does not
select our thresholds or prove a gain.

[PlasMAAG, 2026](https://www.nature.com/articles/s41587-026-03005-7) combines
per-sample assembly graphs with between-sample contig-alignment graphs, learned
representation and graph communities, with plasmid/cellular classification.
The available primary abstract/methods snippets are a screen; direct page retrieval
failed. Its alignment graphs are not mate links, and the required assembly graphs,
new aligners and classifiers are outside this task. It is relevant future evidence
for preserving graph type and plasmid ambiguity, not an authorized new pipeline.

[SIGN, 2020](https://arxiv.org/abs/2004.11198) precomputes sparse graph-filter
messages and learns separate branches. This general architecture motivates our
cached one/two-hop physical messages and separate similarity context. It avoids
dense adjacency reconstruction and repeated full neighbor expansion. E034 is a
small residual graph encoder inspired by this scaling pattern, not a claim to
reproduce SIGN, GraphMB, METAMVGL or UnitigBIN.

Reuse the [accepted genome-graph audit](2026-11-05-e033-genome-graph-priority.md)
and [standalone candidate-selection review](2026-11-03-depth-and-standalone-candidate-audit.md)
for GraphMB/METAMVGL, COMEBin, SemiBin2, CompleteBin, SCGBinner, DCVBin and TaxVAMB.
Q006 remains open: E032 selection is provisional, not established optimal.

## Prospective decision

Implement one coherent fixed-bootstrap, confidence-gated physical representation
with measured parent/window context, retaining E032 construction. Stop before fits
if the two frozen pilots cannot establish useful template support. An insufficient
pilot describes these assemblies, libraries and mapping outputs. It does not
reject paired-read information for future users, nor justify inventing links or
lowering the utility gate. Keep actual recovery, disconnected behavior and
unlinked exact fallback visible. The detailed [design](../../experiments/E034-genome-graph/design.md)
freezes practical keep/modify/abandon criteria before native outcomes. No gain or
SOTA-level competitiveness is guaranteed by a source review.
