# Prospective design, October 28, 2026

The immediate unresolved decision is whether genuine Oral parent depth improves
recovery with E019 learning fixed. E024 cannot answer it: exact reranking of a
union of separate shortlists missed too many jointly close pairs. More accurate
retrieval in either individual space does not establish combined-score recall.

Use one Numba-compiled PyNNDescent 0.5.13 callable implementing the original
pair-dependent composite expression. Retain raw float32 channel values, require
integer lengths to survive float32 packing exactly, and retain the positive-depth
availability flag. The callable accumulates in float64; the native index's stored
distances remain approximate float32. Its compiled reductions permit
reassociation/FMA for vectorization; real tiny comparisons retain a 1e-12
distance-agreement check. This is not the original failed Mac portability check,
whose tolerance remains unchanged. Final reranking/exhaustive sampled answers
use the unchanged E024 float64 code and distance floor. Missing/uninformative
depth never becomes a fabricated zero contrast. The score is symmetric, but is
not claimed to satisfy the triangle inequality.

Freeze 61 construction neighbors including self, up to 60 native candidate
updates, ten iterations, delta 0.001, seed 11 and four threads. Initialize the graph
with self and retained native neighbors; the pinned implementation fills unknown
slots randomly. No old neighbor index is rebuilt. Consume the training-neighbor
graph directly, then union retained native neighbors and exact-rerank to 30.
Querying the same parents through another approximate search is unnecessary.
Tiny tests still execute the actual compiled external query and pickle/reload;
the community object is not serialized or claimed portable.

PyNNDescent's author's [API](https://pynndescent.readthedocs.io/en/latest/api.html)
and [pinned source](https://raw.githubusercontent.com/lmcinnes/pynndescent/release-0.5.13/pynndescent/pynndescent_.py)
were checked again October 28. The source accepts a compiled callable and an
initial graph with unknown entries; supplying that graph disables tree
initialization. This is source support, not full-scale runtime/recall proof.
The source hash and tag binding remain in the E024 assessment.

Keep E019 vectors/geometry, all measured means and axes, original label-free
transforms/calibration pairs/scales, length weights, final distance, eligibility,
E023 hierarchy and marker selection unchanged. Preserve both density and selected
partitions and all DNA/status populations. Keep E024's practical recovery rule,
full 799 provided-reference denominator and known-shared sensitivity unchanged.
The 0.90 final-composite audit gate uses the same 32 ID-hash queries and 1e-10
tie tolerance. Numeric values, opaque IDs, exact/returned top-k and full sparse
discovery/final arrays are written before refusal. No automatic widening follows.

This bounded cached block is preferable to immediately paying for full Oral GLM
or a larger Transformer: it uses the newly accepted measurement without repeating
acquisition, learning or marker science. It does not make perfect grouping a gate
to a coherent learning upgrade. After valid outputs, jointly interpret matched
neighbor homogeneity, target/length/zero-depth losses and density-versus-marker
selection. Favor depth-enabled learning if representation remains limiting, or
calibrated bin construction if coherent neighborhoods are lost in grouping.
Neither an expected mature-tool win nor a small scalar gain alone chooses the
next block. GLM-efficiency and one targeted SemiBin2 reference remain alternatives,
not automatic work. Independent depth-enabled confirmation remains unadmitted.
