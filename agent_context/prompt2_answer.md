**Completed**
I finished the targeted audit and designed [E001, our first diagnostic experiment](/Users/rasmusallesoeenielsen/Documents/dl_binner/experiments/E001-coverage-thinning/README.md).

The main findings:
- Simply rescaling coverage is different from losing read evidence: normalization can remove scaling, but cannot restore missing observations.
- Current VAMB retains total abundance; the inspected DCVBin pipeline also uses coverage.
- Uncertainty, adaptive weighting and coverage augmentation already have substantial prior art. We have not yet demonstrated a novel opportunity.

E001 will hold a **CAMI II Marine assembly fixed**, compare full versus thinned read evidence using MetaBAT2, VAMB and COMEBin, and examine preprocessing, embeddings and final bins. AMBER remains the standard evaluator.

CAMI III is active, but its challenge assemblies are scheduled for October 15. We need not wait for them. [CAMI schedule](https://cami-challenge.org/schedule/)

No models were trained or datasets downloaded. Documentation checks passed; changes are committed locally and `main` is clean. Nothing was published.

**Exact Next Step**
Implement E001’s small validation harness and native-tool adapters, test them on tiny fixtures, and prepare fresh-download and preflight instructions for UCloud. This comes before scientific runs.

**From You**
Nothing immediately. Later, you’ll provide the UCloud working location and run the prepared commands.

The thesis need not accompany the eventual public code; I documented that recommendation without deleting sources or rewriting existing history.

**Next Prompt**
```text
Read AGENTS.md, PROJECT_INTENT.md and docs/STATE.md. Implement E001 Gate 0: the minimal validation harness, native-tool adapters, evaluator tests and smoke checks. Prepare fresh CAMI II Marine download and inventory instructions for owner-operated UCloud. Run portable checks locally and clearly identify native checks requiring UCloud. Do not begin scientific training or bulk downloads yet. Maintain the research documentation and commit the completed local work.
```