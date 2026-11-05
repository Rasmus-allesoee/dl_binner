# Parallel Oral GLM preparation — no extraction or community execution

The separate 128-view batching qualification remains the frozen E029/E032 route;
no T4 start, full bank or additional DNA is included in E034's $15 scope.

`scripts/e034_glm_extension.py` is a local engineering adapter. It constructs a
new hybrid topology around an admitted no-GLM bootstrap, restores all existing
online/EMA/predictor tensors and exact old Adam moments/steps by parameter name,
and appends only zero-output GLM residual modules. The new parameters have absent
Adam state until exercised. New target parameters initially copy the online
extension; the target and bootstrap anchor remain stopped. Caller RNG and all
old bytes are preserved. A real tiny test verifies exact zero-residual inference,
state reload, old slots and stopped target; generated frozen vectors are a fixture,
not an admitted DNABERT-S bank or native GPU result.

A future extension must bind a complete source-blind parent/crop bank to the exact
model/tokenizer/custom source and DNA views, including filtering/availability.
It must regenerate and admit its **GLM-aware own teacher and pair proposals** as a
new treatment. Relabelling the no-GLM checkpoint, adding GLM only to the student,
or substituting a parent vector for crop DNA is refused conceptually and is not
what these tests establish. The complete teacher/proposal training schedule,
optimizer serialization and future adapter admission still need native validation.

After the unchanged 128-view batching probe, use measured throughput/token-length
and memory to price full Oral extraction, transfer, peak coexistence and two-mode
learning. No performance-quality reduction, cutoff sweep or source-selected genome
subset is silently introduced. Any prospectively chosen smaller question needs
explicit population/denominator/short-contig limits. The November 11 active and
November 18 automatic-tail boundaries are unchanged; a new execution must fit or
receive a separate retention decision.
