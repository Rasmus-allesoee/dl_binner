# E033 stopped-run inspection, November 5

[Inspection receipt](inspection-observed.json) verifies phase
`multiscale-20261104T152005Z-a940769-r2`, operations source `5911e25`, prepared
science `c812eb8`. **The workflow failed; the three-mode comparison is NOT_ASSESSED.**
No new recovery score, negative biological result or architecture conclusion is
admitted. Accepted E009–E032 results and the original E033 journals remain intact.

## What completed and what failed

Independent GCP state is TERMINATED. The main boot ran November 4 from
15:25:50.109 to 20:13:28.697 UTC, or 16:25:50 to **21:13:28 Copenhagen**.
The process-bound watcher observed the expected boot/PID/start/command disappear,
waited 62 seconds and requested shutdown at 20:10:46 UTC. That proves process
exit and subsequent shutdown, not science success. The guest attribute is stale:
RUNNING at the E009 no-GLM checksum readback. Top-level completion.json is absent.

All eight native setup/runtime/tiny/restore gates, the two pilot plus eighteen
remaining BAM commands, two bank seals and three full-shape probes have actual
zero exits and no supervisor stop reason. The pilot and full-schedule admissions
pass; the latter forecast 86,944.6 seconds, including a three-hour closure allowance.
Probe updates were temporary and not consumed by science. The main workflow then
exits **1**, after its first E009 no-GLM teacher fails. Its returned work contains
only started.json and initial-state.json: no completed epoch, checkpoint, student,
new graph, bin partition, inputs-after proof or recovery diagnostic is available.
The scheduler says the barrier finished, but its seal is not in the returned slice.
Do not elevate that statement to independently admitted full-work completion.

The real teacher stderr is `task/work/logs/E009_noGLM_teacher.log`. It was omitted
because collection enumerated each mode directory and the phase logs, leaving
out the global workflow log directory. The scheduler trailer cannot identify its
cause. Passed tiny training and a three-update throughput probe do not establish
that this full teacher passed. In particular, the throughput probe omits training's
random depth dropout and repeats one batch; it is not an entire-epoch contract.
Do not assume a numeric failure, a coverage defect or a safe retry before reading
that actual error.

A separate source defect is reproduced locally through the unchanged production
publisher: 8,300 plausible disk samples exceed its 1 MiB JSON bound. The final
phase embeds its growing disk history before entering the final-upload exception
handler. A roughly 4.7-hour run can therefore exit before publishing completion.
**This is a demonstrated failure mechanism and a plausible explanation of the
missing completion, not the observed native terminal exception.** The original
root terminal/systemd journal is needed to confirm it. The cap must remain;
move the closed time series outside the compact control record in a repair.

## Verified payloads and useful technical evidence

| Slice | Generation | Compressed bytes | Physical members | Outcome |
| --- | --- | ---: | ---: | --- |
| measurements | 1793822884082361 | 636,939,104 | 2,323 | Complete byte-verified measurements slice |
| E009-noGLM | 1793822943225038 | 142,799,961 | 2,279 | Complete byte-verified **partial failed work** slice |

Both complete generation streams pass SHA256, server MD5, every physical member,
manifest closure and no-omission checks; there are no aliases. SHA256 values are
in the [inspection receipt](inspection-observed.json). All six JSON/checksum
sidecars also match current private generation/size/MD5 metadata. A second measured
slice stream restores required bank receipts and features that the initial
forensic selection did not stage. Its extra export is priced explicitly. No
complete compressed Mac duplicate or community BAM is retained. Neither archive
contains later root terminal/delivery logs. Two further mode archives and the
separate final delivery are missing, not successful or zero-valued results.

[The independent measurement audit](measurements-review.json) closes every read
filter ledger and verifies all original source/sort/summary bindings. All ten Oral
streams and samtools sort exits are zero, the raw source SHA256 values match the
frozen generations, the sorted bytes match measured BAM receipts, and only new
regenerable sorts were released. Measurement uses owned pysam 0.23.3 / bundled
HTSlib 1.21; the separately pinned sorter is samtools/HTSlib 1.24. Those are distinct
roles. No mapping or measurement was replayed during inspection.

Both full ordered ten-sample axes match; all DNA, eligibility, composition and
sequence hashes are identical to retained originals. E009 has 145,702 rows /
231,678,157 bp; Oral has 1,286,547 rows / 1,669,981,123 bp. The shared rule retains
primary alignments, excludes 0xF04, rejects MAPQ 255, accepts MAPQ/BQ 0, requires
97% CIGAR/NM identity, counts overlapping mates twice and uses full intervals,
including zeros. The bank retains parent plus four exact DNA intervals, their
squared depth, breadth and MAPQ 20 aligned mass. Full moment bytes are archived
and verified; their numeric/coordinate checks passed in native bank seals and
all three full-shape readers. This inspection does not claim an independent
second traversal of community BAMs or local remeasurement of every moment.

| Population | Old all-zero parents | New measured all-zero parents | Old zero → positive | Old positive → zero |
| --- | ---: | ---: | ---: | ---: |
| E009, all | 13 | 24 | 0 | 11 |
| E009, eligible | 0 | 0 | 0 | 0 |
| Oral, all | 576,144 | 209,841 | 420,474 | 54,171 |
| Oral, eligible | 191,567 | 402 | 191,388 | 223 |

This is a large input-availability change on Oral. It does **not** establish a
recovery gain or isolate MAPQ: identity/flags/other measurement semantics changed
in the same prospective bundle. Of Oral's 333,250,002 alignment records,
158,965,398 fail the 97% identity rule; 174,274,488 are accepted. Only 31.78% of
accepted aligned mass has MAPQ at least 20, versus E009's 97.75%. Measured low-MAPQ
support is not unique-origin proof or equivalent information to confident depth.
Its reliability weighting remains part of the uncompleted learning test. Preserve
these observations instead of assuming that fewer zero rows solves the binner.

## Cost, storage and local checks

[Current cost model](inspection-cost.json) prices **17,383.698 seconds** total
VM allocation, including the closed first IAP-failed attempt: **$1.31848** for
CPU/RAM/IP. This is allocated time, not sampled CPU. Setup/measurement/probe/
failed-workflow receipts peak at **21.206 GB** sampled tree RSS (Oral full-shape
probe), below 26 GB; the failed workflow itself peaks at 7.918 GB. The
whole-run disk sample history/final filesystem peak is unavailable; do not invent
it from command guards or the tiny fixture.

Three full archive streams exported 1,416,678,169 bytes; modeled WAN upper is
about $0.159 including small sidecars. The still-preserved 100 GiB task disk costs
about $0.33/day, with **$2.10185** upper through November 11. Complete failed-phase
attribution, including that future disk lifetime, new-object active/tail storage
and $0.25 operation reserve, is **$3.84**, not an invoice. Original 30/300 GiB
storage remains separately authorized at about $7.61/seven days; do not double
count it. Current GCS inventory is 301 versions / 78,513,824,266 bytes, zero
soft-deleted versions. No VM start, resource change, upload or retention renewal
occurred in this inspection. The task disk must remain until its missing tail
and worker logs are preserved.

Fresh signed-in billing shows DKK 1,671.10 Available / 85%, expiry January 12,
2027, Certain usage / Free Trial terms / net pricing, Paid account. November
1–5 gross/savings/net are DKK 26.63 / 26.63 / 0.00, with the more-than-24-hour
delay warning. Keep $35 pending-usage reserve. Fresh official Catalog and credit/
storage terms, paid/open project and full ordinary product coverage pass before
export. Credit delta is not an invoice. Active retention ends November 11 at
00:00 Copenhagen; approved automatic tail ends November 18.

The initial technical feature audit takes 67.1 seconds at 3.452 GB sampled RSS.
The finalized, source-snapshotted reader passes in 35.0 seconds at 3.451 GB with
identical observations after adding strict counter-type checks. Both use four
numerical threads and total 102.1 seconds, with no fit/score. Its first sandbox-blocked ps-monitor attempt
is preserved; the same reader then passes with permitted process monitoring.
Four new tests exercise twenty actual tiny BAM summaries, ten-column bank/feature
reads, reordered axes and bad-counter refusal, incomplete-quality-admission
refusal, and the actual oversized-control writer. Existing science/operations
locks still pass unchanged. Original Mac portability and JGI failures stay.

[Cleanup](inspection-cleanup.json) removes **10,352,432,997 logical bytes** from
eleven obsolete E006/E007/E010/E019 engineering environment roots, after no-live-user and
whole-artifacts dependency-link checks. Retained compact copies include installed
project source and distribution metadata; complete member SHA manifests, package
pins/recipes, wheels, all results and failure journals remain. Required E005
workflow/mapping interpreters, E010 dev4-v3 (201 incoming dependency references),
and E021/E033 numerical bases remain. Logical and
allocated removed bytes do not imply an exact APFS physical-free increase.

## Strongest next decision

Complete the already justified common-information comparison after a **bounded
forensic collection and actual-cause repair**, rather than start a different
architecture or selector campaign. The main biological question has not been
answered, while the expensive new measurements are reusable and reveal a major
Oral support/confidence change. A new Transformer, GLM extraction, read-pair
representation or bin-selection policy cannot fix a missing traceback or establish
this bundle's value. Nor should another loss grid substitute for its completion.

[Recovery assessment](recovery-assessment.json) prices a 30-minute collection-only
wake with a 45-minute STOP at **$0.25 all-in upper**, within the original $20.
It is assessed, **not executed**. First preserve the original worker/root/post-
collector evidence with a fresh boot/process-bound held watcher, without running
science, altering old journals or deleting the task disk. Confirm the two causes,
repair/test the actual production path and freeze new source before outcomes.
Reuse all twenty verified summaries, banks, original states and any independently
verified completed seals; never remeasure/replay them. An unsealed failed teacher
is not a reusable trained model.

The original deadline remains November 6 at 04:20:30 Copenhagen. Reassess the
complete remaining forecast before a release; do not silently reset that clock.
A proposed explicit replacement recovery clock of 30 hours / STOP 30.25 hours,
under the remaining original $20 and unchanged November 11 boundary, has a
conservative complete attribution of about **$15.65**. It requires the following
prompt's execution scope, fresh checks, actual failure diagnosis and prospective
source/runtime gates; it is not released by this inspection.

Keep Q006's source-informed standalone candidate-generation/selection comparison
visible: E032 remains provisional, not optimality evidence. Efficient full Oral
GLM remains complementary, with the pinned 128-view native qualification, complete
bank/state-extension and teacher/proposal/student admission still required; no
new throughput or extraction is invented here. Keep the skin community unscored
pending source/genome/replicon/taxonomy/overlap/ambiguity/unique-versus-origin/depth/
protocol/cost admission. The next recovery result, not this failure, should inform
whether to retain multiscale fusion or choose one stronger coherent successor.
