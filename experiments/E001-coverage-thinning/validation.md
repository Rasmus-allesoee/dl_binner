# E001 Gate 0 Validation

Date: 2026-09-18. These are software checks, not E001 scientific attempts or biological results.

## Runtime version-probe stall repair, 2026-09-23

The owner reported the grouped preprocessing driver became silent immediately
after `PASS: mapping-environment`. No `workflow-lock`, DAG or workflow stage was
observed, and CPU/network activity was idle. The previous direct
`subprocess.check_output()` calls for strobealign, samtools and Snakemake had no
timeout or command records. This is a driver-observability failure, not evidence
of a mapper or workflow failure; no bulk read acquisition or DAG execution was
reported as started.

The three version checks now run sequentially through the shared isolated command
runner, each with a 30-second timeout and its own `START`/`PASS`/`FAIL` message,
stdout, stderr and command JSON. The JSON records argv, elapsed time, timeout
status and final return code; timeout handling kills the probe's process group.
Nonzero exits, launch errors, absent output and unexpected versions stop before
the next probe with an explicit failure message. Regression coverage exercises
probe order, nonzero exit, version mismatch and a real short-lived hanging child.

Version pins and the scientific workload are unchanged. The fix changes only
bounded diagnostics and fail-fast behavior. The owner must use the replacement
committed bundle for the grouped run; no new native execution is accepted yet.

The replacement package was built from clean source commit
`fe2ae8350db46576f2232992269c3e4a7c588322` as
`artifacts/e001-transfer/e001-code-fe2ae8350db4.tar.gz` with SHA256
`e134b25cb88692d995c114a31cc5add2dc0bdaa18a10b9ed71f9eb247906a510`.
Its embedded `SOURCE_COMMIT` matches, `sha256sum --check` passes, and the
extracted archive passes all 12 targeted synthetic probe/command-runner tests.
This is local package verification only; UCloud upload and execution are pending.
The archive predates this package-record and owner-side bundle-pin documentation
commit; its executable snapshot is the stated source commit.

## Parallel scheduling reassessment, 2026-09-23

The owner has not run the remaining-nine command. [D009](../../docs/decisions/D009-parallel-preprocessing-terminal.md)
corrects the earlier Slurm availability inference: Terminal can initialize an
in-app Slurm cluster, including one node. Thesis profile/workflow/config and
all three requested documentation sources were inspected. No separate app or
provider switch is required. For the present single-node workload, use the
already installed local executor to avoid unnecessary plugin/setup work.

The owner corrected the machine menu using a screenshot: available choices
include **8 vCPU / 24 GB** and **16 vCPU**, not 12. The earlier three-lane
recommendation was prepared but has not run. Current choice is **8 vCPU / 24 GB**,
two 4-vCPU sample lanes, 10-GB sample memory budgets, and a 23-GB global Snakemake
rule-memory cap. Two map workers request 20 GB, leaving 3 GB for overlapping
work. These are scheduler budgets, not hard OS limits. Each lane waits for its
prior sample's CT summary; download concurrency stays at one. Scientific
commands, seeds and data scope remain fixed.

At sample 0's observed 42-minute full preprocessing rate, nine samples on two
lanes imply about 3.5 hours of sample processing before acquisition/I/O effects.
Plan **4-5 elapsed hours / 32-40 allocated core-hours**, not measured runtime.
The 80-core-hour group ceiling permits 10 hours at 8 vCPU. A 16-vCPU allocation
could run more lanes, but may reduce elapsed time without reducing charged
core-hours because the final sample can leave most of that allocation idle. We
prefer 8 vCPU to limit charged resources; no parallel native run has established
actual speedup or cost.

The earlier portable tests passed for the three-lane scheduler implementation.
The actual Snakemake fixture verified that concurrency mode; the updated
8-vCPU/two-lane owner configuration has not been run on UCloud. No result here
establishes native concurrent throughput or peak RAM.

## Full sample-0 preprocessing accepted, 2026-09-21

Return `sample0-preprocess-6_gyxp5d-return.tar.gz` matches SHA256
`4e0e4e64131d11ac42450cae6460a3c7ad06a5add29a4049b3fa540a42c33a8e`.
All 38 archive members are unique safe regular files. Terminal and detailed logs,
all command records, runtime configuration and QC were reviewed. Source is
`4235aa4426e252ab8f3c8a52817a6e2dd3eeae14`; reference and sample archive match
the accepted identities. [Observed record](sample0-preprocess-observed.json)
preserves original JSON and every member hash, plus the terminal-log hash.

Workflow environment creation/install, dry-run, full extraction, streamed
mapping/filter/sort, both indexes, thinning and complete BAM QC all passed.
Only routine package-install warnings occurred; no failed commands. Snakemake
9.13.7 and its returned package inventory are now native-executed, not just a recipe.

| Measurement | Observed |
| --- | --- |
| Actual allocation | 4 vCPU / 12 GB RAM |
| Driver wall time / allocated cost | 2,534.53 s (42.24 min) / 2.81615 core-hours |
| Full read pairs | 16,666,043; exactly the independently counted sample-0 truth total |
| Extraction including archive verification | 141.09 s; FASTQ 10,610,713,214 bytes |
| Map/sort/index/QC rule | 2,316.83 s; mapper itself reports 2,013.15 s mapping |
| C0 primary mapped records / BAM bytes | 33,158,847 / 4,319,070,969 |
| CT records / BAM bytes | 3,314,822 / 478,139,342 |
| CT fraction and seed | 0.0999679512 observed; 0.1 requested; seed 1000 |
| CT thinning/index/QC rule | 42.39 s |
| New attempt storage | 15,411,548,225 bytes (15.412 decimal GB) |

Cost excludes owner idle time outside the driver. Storage excludes the original
9.739 GB archive, existing environments and earlier attempts. No peak RAM was
measured; successful execution within the reported allocation is the evidence.
**Accepted: preserve and reuse sample 0; do not remap, rethin or reinstall it.**
This is operational preprocessing, not a biological result or H001 test.

### Next grouped acquisition/preprocessing

[Plan](multisample-plan.json) and [workflow](../../workflows/e001-preprocess/multisample.smk)
cover samples 1,2,3,4,5,9,10,11,12, in frozen order. HTTP HEAD plus 64 KiB
range probes confirmed each archive's size, ETag and dated sample directory;
the nine archives total **91,698,809,375 bytes**. Full payloads were not downloaded
locally. Publisher MD5s remain in acquisition.json and will be verified during
owner download before extraction. Select the dated directory's plain
`reads/anonymous_reads.fq`, never a subsample or simulator BAM. The complete
member suffix is established on sample 0 and enforced at runtime on the others;
the prefix probes alone do not prove every member's presence. Small public
read-origin metadata prefixes confirm `S{sample}R` anonymous IDs in each library.
Extraction validates every pair to EOF; other libraries are not forced to have
sample 0's exact count. The 20-million-pair bound is a stop-for-review resource
guard, never truncation or sample selection.

Nine times the measured 2,503.92-second workflow gives **6.26 hours / 25.04
allocated core-hours** at the same allocation, before acquisition. Allow roughly
7-9 hours total at comparable network/I/O throughput; this is a projection,
not a guarantee. The driver has an **80 allocated-core-hour group ceiling**
(20 hours at 4 vCPU), including download/wait/setup probes, within the 200-hour
preprocessing envelope. No linear speedup assumption for other allocations.

Projected new retained storage is **230.40 GB** including all nine archives,
FASTQs and C0/CT outputs; future features/replicates add space. With existing
data/environments this does not safely fit the initial 250 GB Home quota.
The explicit owner command therefore uses the offered shared project directory
for new heavy data, checks 275 GB free initially and 35 GB before each sample,
and leaves environments/sample 0 in Home. No files are deleted or moved.
Filesystem free space is not a project-quota measurement; the owner must mount
the shared directory with sufficient quota. Sequential sample dependencies keep
download/extraction/sort workspaces from overlapping. A failure stops the group,
preserves completed outputs and packages logs for targeted continuation.

### Observability and scheduler choice

New rules have one-shot `benchmark:` TSVs with `--benchmark-extended`, recording
wall time, sampled process-tree RSS/CPU/I/O and requested rule resources. No
benchmark repeats and no sample-0 rerun. These complement, not replace, driver
wall-time times allocated-vCPU accounting. Sampled RSS can miss short peaks and
does not include the entire UCloud container. Detailed per-tool stderr/commands
are retained, with live timestamped mirroring and a 60-second progress heartbeat.

[Snakemake documentation](https://snakemake.readthedocs.io/en/stable/snakefiles/rules.html#benchmark-rules)
was checked alongside the locally installed **9.13.7** implementation; the live
documentation currently describes a newer release, so the pinned engine itself
is tested. The [Slurm executor](https://snakemake.github.io/snakemake-plugin-catalog/plugins/executor/slurm.html)
submits to a Slurm scheduler. The original assessment inferred that the SDU/K8s
Terminal setup required another provider for Slurm. **Corrected by D009:** Terminal
can itself create the scheduler, including on one node. The local executor is
retained for this workload's simplicity, not because Terminal lacks Slurm.

Local implementation validation finalized 2026-09-23: **143 portable tests pass**.
New coverage includes bounded/checksummed acquisition failures, partial-file
preservation, complete read/sample validation, accepted-sample reuse, explicit
allocation/acquisition guards, grouped driver order and repeat preservation,
packaging failure, live progress, sample-9 read group/seed, and ordered manifests.
The actual pinned Snakemake engine executed a two-sample fixture DAG, produced
eight extended benchmark TSVs, and reported nothing to do on a second invocation.
This validates orchestration with a fixture worker, not a new native mapper run.
Documentation/link checks and whitespace checks pass. Native execution of the
remaining-nine-sample workflow is prepared, not completed; no model was trained.

## All three mapper attempts reviewed, 2026-09-21

The [observed record](mapper-observed.json) preserves all three checksum-verified
archives, exact source/driver identities, command records, allocation, prefix
hashes and successful summary. All terminal logs and captured stdout/stderr were
reviewed. Bowtie2's resolved package list has the same SHA256 in every attempt.
Both corrective commits remain intact.

| Attempt | Source | Outcome | Allocated core-hours |
| --- | --- | --- | --- |
| `13l53afq` | `601cae3` | Bowtie2 setup and sample-0 acquisition passed; wrong `.fq.gz` member stopped extraction before mapping | 0.793842 |
| `3nyb_km0` | `dbee019` | Reused identical archive; the guessed replacement member also failed before mapping | 0.054069 |
| `89gpt00u` | `216c896` | Verified plain anonymous FASTQ, 100,000 pairs, both mappings/filter/sort/index and summaries passed | 0.827075 |

The publisher archive SHA256 is unchanged across attempts:
`6f349a6f3299b4595f8c5acfb9ad7d8e2fc56fe657c1a451cde90e92c364f113`.
The third attempt used the existing archive, not another download. All used
4 vCPU / 12 GB. Combined driver accounting is 1.674986 core-hours, excluding
job time outside the drivers. The accepted attempt took 744.37 seconds, dominated
by Bowtie2 index construction, not read mapping.

| Measurement | strobealign 0.17.0 | Bowtie2 2.5.4 |
| --- | --- | --- |
| Command mapping time | 17.390 s, including reference indexing | 27.300 s, excluding index build |
| Reference indexing | 10.96 s, native log (inside mapping command) | 676.320 s, separate build command |
| Native mapping-only time | 5.83 s, native log | Not separately reported from command |
| Primary mapped reads / 200,000 | 199,036 (99.518%) | 198,731 (99.3655%) |
| MAPQ-zero mapped reads | 111,641 | 42 |
| Sorted BAM bytes | 30,684,630 | 34,158,421 |
| BAM bytes per input pair | 306.8463 | 341.58421 |

Completed-child peak RSS was 4,312,244 KiB (~4.11 GiB), a maximum across sequential
subprocesses, not per-mapper or aggregate whole-job RAM. Successful attempt disk
use was 1,526,832,160 bytes, excluding the retained 9.74 GB archive in the first
attempt. For **planning only**, 16.67 million pairs/sample (5 Gbp at 2x150 bp)
would imply ~5.11 GB strobealign BAM/sample, ~51.1 GB for ten samples. This is a
linear prefix-based estimate, not a measured full-sample size; indexes, raw
archives/reads, other tool features and intermediate files add storage. No need
to move existing small artifacts to shared storage now.

**Accept operational mapper/storage feasibility. Do not rerun this task.** This
does not establish mapping accuracy or finalize the provisional mapper. Only
98,232/200,000 reads (49.116%) have the same mapped reference/start/strand, with
964 unmapped by both. Bowtie2 itself reports 61,799 pairs with multiple concordant
alignments, despite only 42 MAPQ-zero records. Thus MAPQ-zero alone is not a
cross-mapper ambiguity comparison, and mapped percentage cannot choose a winner.
Ambiguity/tie handling is a plausible explanation, not a demonstrated one.

### Local follow-through completed

[e001_mapper_diagnostics.py](../../scripts/e001_mapper_diagnostics.py) analyzes
the existing BAMs against frozen destination-contig origins. It separates exact
placement, same-contig differences, shared-origin different contigs, disjoint-origin
contigs and one-mapper-only assignments; records complete MAPQ/NM/AS-XS histograms,
per-category MAPQ and per-contig read counts. Score scales are not treated as
interchangeable, and destination-origin agreement is not read-origin truth.

The owner supplied both BAMs during this session under `agent_context/mapping/`.
Both match their accepted hashes; local analysis reproduced all earlier counts.
91,339 reads move between disjoint destination-genome sets, 8,954 differ within
one contig, 206 move between contigs sharing a genome origin, and 305 map only
with strobealign. The summed absolute per-contig read-count difference is 32,349;
this is not a base-coverage or accuracy measure. Most cross-genome disagreements
are low-confidence under both tools: 90,046 strobealign MAPQ 0, 90,894 Bowtie2
MAPQ 1. Bowtie2 reports equal AS/XS for 114,509 mapped reads; different confidence
conventions explain why MAPQ-zero counts alone were misleading.

Because cross-genome disagreements were substantial, local analysis continued
directly to read-origin truth, without another owner task. Unlike the FASTQ,
the public `reads/reads_mapping.tsv.gz` object is readable. The 293,229,761-byte
download matches its object MD5 `15cbaa7866defbf486043533e293faf3` and SHA256
`691dc251b267fe301d8f5ef0cf3cf34333648a146539843da0b2a735106fe296`.
All 33,332,086 metadata rows were scanned with gzip CRC validation; all 199,036
mates mapped by either tool joined uniquely. No read sequences were downloaded.
[Diagnostic record](mapper-diagnostics.json) owns URL, identities and results.

True-source-genome compatibility is 105,795 reads for strobealign versus 105,697
for Bowtie2 on the same 200,000-read denominator. Both are compatible for 93,735;
only strobealign for 12,060; only Bowtie2 for 11,962. This is not a significant
accuracy advantage, nor does it establish that ambiguous reads are uniquely
identifiable. [D008](../../docs/decisions/D008-mapper-and-first-preprocessing-slice.md)
retains strobealign and no added MAPQ cutoff, with native downstream filters.
The population is not changed and no mapping rerun is needed.

The next implemented task is the [Snakemake preprocessing slice](../../workflows/e001-preprocess/Snakefile):
full existing sample 0 only, validated interleaved FASTQ, streamed C0 mapping,
seed-1000 10% CT and compact QC/resource reporting. Source truth establishes the
expected 16,666,043 pairs. Snakemake 9.13.7 was installed in an isolated local
test environment and its actual DAG dry-run passed. Portable tests exercise
full extraction/count mismatch, overwrite protection, actual allocation, grouped
driver order, failed prerequisites and repeated-attempt preservation.
All **130 portable tests pass**, including the real pinned-engine DAG dry-run.
At that checkpoint native preprocessing was **prepared, not run**. The subsequent
accepted sample-0 return and bounded next scope are recorded above; scientific
model fits remain unlaunched.

## Integration accepted and accounting corrected, 2026-09-21

`native-integration-p1upv3gg-return.tar.gz` matches its supplied SHA256; source
0855646, driver hash and frozen input identity match. [Observed record](native-integration-observed.json)
records 128 contigs / 2,841,187 bp, both complete AMBER handoffs, 128 VAMB clusters,
52 COMEBin marker hits / 2 seeds, and all 120 native candidates with 128 rows each.
Native CheckM profiling and winner selection completed. Stderr contains the
known pkg_resources deprecation and the marker HMM fallback to E=1e-5 because
the source HMM lacks model-wide TC cutoffs; no failed commands. No biological
quality claim is made from random embeddings.

Total 105.522 seconds at owner-reported **4 vCPU / 12 GB** = **0.117 core-hours**.
The returned driver incorrectly assumed 8; raw evidence is preserved.
COMEBin's earlier optimizer check actually used **2 vCPU / 6 GB**, so its charged
projection is **23.946 / 47.891 core-hours per fit** (central / twofold), and
**143.674 / 287.348 for six fits**. These recalculate measured wall time, not a
speedup extrapolation. [Corrections](allocation-corrections.json) and amended
[D007](../../docs/decisions/D007-comebin-resource-envelope.md) supersede earlier
cost conclusions; no repeat of accepted native checks is necessary. No change
is inferred to the separate MetaBAT2/VAMB allocations.

### Next mapper task and acquisition boundary

On 2026-09-21 the direct Swift object's HEAD returns HTTP 200, size 5,166,013,564
and `x-object-manifest` pointing to a segmented object. A 64 KiB Range GET still
returns HTTP 401. This establishes that a listing/HEAD is not proof of readable
contents; it suggests a segmented-object access issue, not a confirmed diagnosis.
The public publisher archive remains the explicit fallback, not an authentication
workaround. It is one 9.74 GB sample archive, with size/ETag pinned from the earlier
probe. No such archive was downloaded locally.

The new [mapper driver](../../scripts/e001_mapper_feasibility.py) requires either
an existing sample archive or explicit `--allow-sample-archive` authorization.
It installs Bowtie2 2.5.4 separately, extracts only the first 100,000 complete
150-bp pairs, maps identical reads to the frozen assembly with both mappers,
and records index cost, mapping/filter/sort time, primary alignment agreement,
MAPQ-zero counts, BAM bytes per input pair and attempt disk size. Agreement is
not accuracy; an input-order prefix is not a representative community sample.
Expected runtime and network transfer speed remain unmeasured. Timeouts are stop
limits, not expected runtimes. Actual allocation is mandatory CLI input.
Portable tests cover extraction, mate mismatch, short/missing input, changed
remote metadata, opt-in, grouped stage order, allocation accounting and retries.
Native Bowtie2 solve and real-read execution remain owner-run and unvalidated.
All 119 portable tests pass. Publisher HEAD was rechecked on 2026-09-21 and
matches the pinned 9,738,621,091-byte size and ETag; no payload was fetched.

### Mapper owner attempt failed at archive-member lookup, 2026-09-21

The owner ran the mapper feasibility bundle at 4 vCPU / 12 GB. The Bowtie2
environment setup and package lock passed. The single 9,738,621,091-byte
publisher archive was downloaded and its recorded SHA-256 is
`6f349a6f3299b4595f8c5acfb9ad7d8e2fc56fe657c1a451cde90e92c364f113`.
Extraction then stopped before any index build or mapper execution because the
driver searched for
`2017.12.04_18.45.54_sample_0/reads/anonymous_reads.fq.gz`; the archive
member had not yet been inventoried. The earlier suggestion that the member
was below `short_read/` came from a separate publisher object listing and was
not an inner-archive observation. The attempt used 0.794 allocated core-hours
and preserved the archive for reuse.

The owner subsequently listed the retained archive and found exactly these
read-like members:

```text
2017.12.04_18.45.54_sample_0/reads/anonymous_reads.fq
2017.12.04_18.45.54_sample_0/reads/subsample_0.fq
```

CAMISIM documents `anonymous_reads.fq` as the complete anonymized read file;
the mapper therefore pins that plain FASTQ and does not silently use
`subsample_0.fq`. The driver now supports both plain and gzip FASTQ members,
and must be rerun with the retained archive through `--archive`.

## COMEBin and MetaBAT2 accepted separately, 2026-09-21

Both archives match their supplied SHA256 checksums. Recorded driver hashes match
the executed Git snapshots and frozen-input identity. Intentional fixes f4cf0c0
(isolated imports), 41d0f9d (zlib pin), and f9c983a (expected empty MetaBAT2 scale
control) remain intact, without duplicate fixes.

- **COMEBin:** `native-remaining-2sf0rot9` passes imports, pip check, native smoke
  and full-batch CPU measurement at source f4cf0c0. Group exit 1 reflects the
  separate MetaBAT2 failure. [Observed record](native-comebin-observed.json):
  six views, batch 1024, 17,928,576 parameters, logits 30,720 x 6,139. Measured
  steps 9.796/9.399 seconds project 95.783 allocated core-hours per 200-epoch fit,
  191.565 with margin, excluding downstream work. Parent peak RSS 4,688,072 KiB.
  All six views changed 22 mean/variance entries; CS maximum difference 2.1333e-5.
  Setup stdout confirms CheckM database postlink download/extraction into the
  persistent COMEBin environment. Do not download it again for integration.
- **MetaBAT2:** `native-remaining-uvkhdn0o`, source f9c983a, passes its separate
  rerun. [Observed record](native-metabat-observed.json) preserves the legitimate
  expected-empty tiny CS result. At frozen population size, synthetic binning
  assigned 21,405 of 22,594 contigs in 152.450 seconds / 0.339 allocated core-hours;
  completed-child peak RSS 4,759,524 KiB. This excludes BAM extraction and is not
  a real-data runtime guarantee. Whole attempt: 0.421 core-hours.

[D007](../../docs/decisions/D007-comebin-resource-envelope.md) records a prospective
COMEBin-only limit of 200 core-hours, following owner acceptance, while retaining
the 800 total. Six conservative fits exceed that total: actual pilot cost must
inform remaining replicate authorization, independently of biological scores.

The [integration driver](../../scripts/e001_integration.py) groups VAMB/COMEBin
clustering and AMBER handoff, including COMEBin's full grid and marker selection.
Local portable suite: **110 tests passed**, covering repeated unique attempts,
isolated entrypoint, independent failure handling, packaging failure and changed
frozen inputs. Fixture preparation passed on the actual local frozen input too:
128 contigs, 2,841,187 bp, FASTA SHA256
`532315bd216c16daca50af6867a5dba26ea26a73286ffa5ab0196b9fcb1f5355`.
Native Linux clustering/marker/evaluator execution is prepared, **not yet run**.

### Read-prefix access observation, 2026-09-20

A 65,536-byte Range request to
`https://frl.publisso.de/data/frl%3A6425518/gastrooral/sample_0.tar.gz`
returned HTTP 206, total 9,738,621,091 bytes, ETag
`"2447790a3-5d68d6c44295d"`. Its tar prefix begins with
`2017.12.04_18.45.54_sample_0/bam/`, not FASTQ. The container listing at
`https://openstack.cebitec.uni-bielefeld.de:8080/swift/v1/CAMI_Gastrointestinal_tract`
lists `short_read/2017.12.04_18.45.54_sample_0/reads/anonymous_reads.fq.gz`,
but a Range request to that object returned HTTP 401. No read prefix was acquired
and no bulk archive downloaded. Resolve access or explicitly choose a bounded
alternative before mapper throughput work; this is not a reason to reopen the
settled assembly inventory or silently authorize a 9.74 GB download.

## VAMB accepted and remaining tools grouped, 2026-09-20

Owner return `agent_context/native-vamb-rdow5991-return.tar.gz` matches checksum
`01cd6239ccae05551b7882c42ac5ba2737880a24be69c837e2d5e4a0bae1f77e`.
Its driver and frozen-input hashes match the executed snapshot. Source commit
`e129cefe6f5d0eeac9c17be43b885b8b1d225129`; run began 2026-09-20 18:09:39 UTC
on `j-12397090-job-0`. All setup/import/pip/native-smoke/CPU stages passed.
Setup stderr has ordinary clone/package-script notices, no reported error;
smoke and CPU stderr are empty. Python 3.12.10, NumPy 1.26.4 and CPU PyTorch
2.6.0+cpu are isolated at the expected VAMB prefix. Resolved locks were inspected.

[Observed data](native-vamb-observed.json) preserve per-batch timings and provenance.
Total driver 170.91 seconds / 0.190 allocated core-hours (4 vCPU); optimizer
process peak RSS 826,980 KiB. Native normalized C0/CS composition, total abundance
and weights match exactly; largest coverage difference is 5.96e-8.
The 300-epoch schedule projects **0.814 core-hours per fit**, **1.628 with a twofold
margin**. Accept VAMB native synthetic compatibility and optimizer feasibility,
not full-pipeline cost or biological performance. Do not rerun it in the group.

[D006](../../docs/decisions/D006-environment-ownership.md) retains separate
experiment-owned environments for all five E001 tools, reused across gates.
The grouped driver attempts MetaBAT2 and COMEBin independently, preserves partial
failures and packages both outcomes. It leaves accepted runtimes and inputs alone.

Two previously unexecuted setup recipes were hardened after source inspection:
- COMEBin's hnswlib pip dependency may compile; add the pinned C++ compiler to
  the environment-file solve and explicitly select its executable. The tool's
  scientific dependency pins/source remain unchanged. Micromamba's official
  [setup documentation](https://github.com/mamba-org/setup-micromamba) describes
  extra create specs with environment files (not explicit lockfiles).
- MetaBAT source `src/CMakeLists.txt` forces static Boost. Build with the pinned
  Conda shared Boost libraries via the one-line [build patch](metabat-shared-boost.patch)
  in a separate `build/metabat-source` copy. The original execution checkout
  remains pristine; preserve patch/hash and binary hashes in locks. This changes
  linkage, not binning logic, and native smoke remains required. The patch passes
  `git apply --check` against the exact cached commit. Anaconda package metadata
  confirms the pinned libboost/libboost-devel 1.85.0 packages; no native build is
  claimed from metadata or patch inspection alone.

All **102 portable tests passed**, including two isolated tool prefixes, repeat
invocation without reinstall, continuing the second tool after first-tool setup
or smoke failure, preserving partial environments, packaging failure and small
synthetic MetaBAT generation/membership parsing, and selecting only a failed tool
for reviewed recovery without rerunning its accepted peer. Shell syntax and documentation
checks passed. Native grouped Linux execution remains pending. COMEBin timing
uses its source model/InfoNCE at the full six-view batch, without changing loss,
batch or native scientific schedule to improve the projection. MetaBAT CPU timing
uses synthetic uniform lengths/groups and is not a real-data runtime guarantee.

## Owner population frozen and VAMB step prepared, 2026-09-20

Return `agent_context/inventory-resume-6z45cola-return.tar.gz` verified SHA-256
`1bf9a1b442a31cd069b9d9dffcf587e9365a9627a9ad4b9107a74552fd4a8cb2`.
Executed source `64664ac6860b75d5a92c430c222e59f3418b5909`, code hashes and
taxonomy policy match the reviewed snapshot. All five prepared output hashes,
population counts/gates and all taxonomy member hashes match the local validation.
All 196 tax IDs / 259 genomes resolve as expected. All stage stderr files are
empty; exit 0. Run began 2026-09-20 10:48:22 UTC on `j-12396906-job-0`, took
40.06 seconds and reported child peak RSS 620,856 KiB. These are process statistics,
not full allocated job spend. Accepted UCloud input path and immutable output
identities are recorded in [frozen-inputs.json](frozen-inputs.json).

This closes the taxonomy/population prerequisite. No new biological score exists.
Native VAMB is selected next because its pinned CPU dependencies and simpler model
provide a bounded first learned-baseline check. COMEBin-first could expose the
largest compute risk sooner, but its more complex unresolved environment would
combine additional failure sources; it remains the next learned-runtime check,
not an optional baseline. MetaBAT2-first would not answer learned CPU feasibility.

The [new driver](../../scripts/e001_vamb_cpu.py) groups installation, import/pip
checks, existing native synthetic smoke and synthetic full-dimension CPU timing.
Local source inspection confirms the CLI schedule is 300 epochs with doubling at
25/75/150/225, not the different `trainmodel` Python API defaults. Use native
`make_dataloader`, `VAE.trainepoch` and DAdaptAdam without copying model/loss code.
No true sequences/coverage/labels enter timing and no model is saved.
PyPI metadata checked on 2026-09-20 confirms Linux x86_64 CPython 3.12 wheels for
vambcore 0.1.2, pycoverm 0.6.2, pyhmmer 0.10.15 and pyrodigal 3.6.3; this is not
an installed-runtime claim. Source/dependency pins remain unchanged.

All **95 portable tests passed**, including mocked complete VAMB-driver sequencing,
repeat invocation without reinstallation, setup/partial-environment/missing-fixture
failure returns, packaging failure and a real subprocess timeout. Projection
arithmetic/schedule are checked. Mocked orchestration does not establish native
Linux smoke or throughput: those are explicitly awaiting the owner run. Treat
smoke failure as a runtime blocker; interpret measured training projection with
the recorded per-fit and total budget limits before proceeding to science.

## Historical taxonomy and local population, 2026-09-20

The owner's local taxonomy archive was independently verified against the live
CAMI page and object metadata, then every member hashed. All 196 GI tax IDs resolve
directly to Bacteria for all 259 source genomes. The actual local full-data
`prepare-hmp --nodes` run passes all five population gates without any threshold
change: 224 evaluation genomes and 7,964 short queries spanning 66 genomes.
Canonical FASTA/truth hashes are unchanged from the accepted owner conversion.
See the [evidence and requirements](../../docs/evidence/2026-09-20-gi-taxonomy.md)
and [pinned policy](taxonomy-policy.json) for source/output identities.
Ignored local outputs: `artifacts/e001-taxonomy-reviewed/` and
`artifacts/e001-population-reviewed/`; no raw data or taxonomy is tracked.

All **88 portable tests passed**. New tests exercise complete taxonomy-aware
owner-driver invocation twice, invariant output checks, corrupted archive,
wrong member hash, missing/duplicate members, wrong mapping and domain coverage,
and missing-root/cyclic/duplicate taxonomy nodes. Failed attempts retain logs;
return archives contain coverage reports but not the 145 MB nodes table.
The full-data preparation used the existing macOS environment; owner Linux
taxonomy-aware execution remains pending. No read download or model training ran.

Transfer `artifacts/e001-transfer/e001-code-64664ac6860b.tar.gz` and its checksum
were built from committed code. The archive checksum passed and all 88 tests
also passed from its extracted copy outside the repository (18.14 seconds).

## Owner conversion accepted, 2026-09-20

Reviewed local inbox archive `agent_context/inventory-resume-ef6z97y9-return.tar.gz`;
SHA-256 `55705be2a9a01c7b4b43340bd61ed4e5fe4350275badc34b7439073282c73086`
matches the supplied checksum. The archive remains untracked. Its originating
attempt is `/work/Home/dl_binner/e001/e001-gate0/inventory-resume-ef6z97y9`.
Source commit: `9e1f939d4585bdf191dd562787932431235ff281`; returned code hashes
match local committed code, and the returned policy matches byte for byte.

- Execution started 2026-09-19 at 21:50:41 UTC on `j-12396660-job-0`.
  Environment, audit and conversion passed with empty stderr and exit code 0.
  Persistent mapping Python 3.12.10 / Biopython 1.85 passed isolation checks.
- Full setup archive/original mapping verification passed; all three setup
  metadata member hashes match the reviewed policy. Source FASTA and corrected
  mapping hashes match D005. The raw join audit still reports false, as expected:
  it describes the unmodified input before the explicit quarantine policy.
- Exactly 20 foreign-provenance intervals (28,917,470 bp), two empty artifacts
  and six coordinate-alias groups were accounted for. No additional invalid DNA,
  length mismatch, duplicate FASTA key or mapping-only key was reported.
- Conversion retained **22,594 contigs / 817,438,232 bp** at the 2,500 bp cutoff
  from 210,612 truth-joined physical contigs. Canonical FASTA SHA-256:
  `14870c27bc9467b5897bd1b65b347d7d5e2733d8bbe48c0085cb708194966fe1`;
  truth TSV: `f6e1b948f2fbbc6ed404ea27e73fb238bd2f34765b585e8e3fbe77f59b25c301`.
  These are returned output hashes, not independently rehashed local outputs.
- Elapsed 31.37 seconds; child peak RSS 614,272 KiB (about 600 MiB).
  These process measurements do not measure total allocated job cost.
- Population status `blocked` is expected: `nodes` is null, domains unresolved,
  and eligible genomes/short queries are zero pending taxonomy. The reported
  817,438,232 excluded retained bp are currently outside the scored population,
  not removed from the canonical FASTA. Population sufficiency is not yet known.

Conclusion: accept the D005 conversion and continue with the declared GI
development derivative; no dataset switch is warranted by this return. This
does not certify the entire publisher dataset or establish biological results.
Next verify the historical taxonomy and resolve the scored population. The
owner-supplied `setup-members.json` contains no taxonomy/nodes payload. No further
UCloud files are required to start that investigation; the owner can supply
specific files up to 10 GB if local inspection becomes useful.

## Prior implementation review, 2026-09-19

[Publisher provenance investigation](../../docs/evidence/2026-09-19-gi-provenance.md)
resolves all 20 FASTA-only intervals through seven conflicting BAM headers.
[D005](../../docs/decisions/D005-gi-input-derivative.md) records the derivative
decision. The new driver validates the source-bound policy, rechecks the persistent
environment on every job, and creates distinct attempts without moving old data.
Legacy inventory/retry drivers are retired to avoid executing the hardcoded first
snapshot or failing on output-name collisions.

All **82 portable tests passed** locally, including full synthetic owner-driver
execution twice with an empty system PATH, injected Python paths, alias
canonicalization, known empty artifacts, explicit
foreign-record quarantine, completed return/checksum verification, and prior-output
preservation. Corrupted setup metadata and a missing persistent environment stop
before conversion and return logs. A packaging failure returns nonzero and marks
the retained status as failed rather than claiming success.
Additional regressions cover policy source changes, missing/overlapping exceptions,
wrong orphan counts, duplicate truth rows and malformed-header DNA validation.
This does not establish a successful conversion of the real GI data or fresh-job
Linux execution. No scientific conversion was rerun locally.

The owner's newly supplied local inventory allowed a full read-only audit with
the corrected validator. FASTA/mapping hashes matched the policy, all 20 unmatched
keys matched its exact interval set, and the mapping contract passed (210,612
keys, six aliases). The setup archive is absent from the supplied local folder;
full setup/member checks will run on its existing UCloud copy.

Corrections to prior interpretations: raw audit JSON establishes only the underscore
orphan ID, not Biopython normalization of asterisks. The earlier return's absence
of an inventory file did not prove absence of a partial output directory. The
previous chat's claim that Gate 0 was complete was incorrect: other native baseline
checks remain open. Older paragraphs below are dated execution history.

## Executed locally

- macOS Intel, Python 3.13.2; isolated `.venv` with NumPy 2.2.6, Biopython 1.85 and pysam 0.23.3. This is the harness environment, not any native binner environment.
- `.venv/bin/python -m unittest discover -s tests -v`: 56 portable tests passed, including CLI smoke. Fixtures cover perfect/merged/split/missing/empty assignments, ambiguity, exact thresholds, fixed-denominator length strata, malformed joins/coordinates, duplicate predictions, anonymous IDs, reverse-complement duplicate detection, missing taxonomy, zero/filtered feature rows, unsafe archives, mocked download checksums/limits, dry-run acquisition, all-view scaling, stale coverage tensors, and failed-attempt provenance.
- `bash -n scripts/e001_linux_setup.sh scripts/e001_linux_smoke.sh`: passed. Syntax validation does not establish environment solvability or runtime success.
- Public directory/README/checksum metadata and bounded file prefixes were inspected as documented in the [audit](../../docs/evidence/2026-09-18-human-cpu-audit.md). No complete GSA, truth, read archive or scientific feature set was downloaded.

- `verify-source` passed for the four selected native repositories: independent roots, expected commits, no tracked changes, and only allowed Finder metadata untracked. None of the reference caches was modified.
- `python3 scripts/check_docs.py --check-context` passed, including all 83 present source fingerprints. Ten optional missing ZIP-cache paths belong to the explicitly historical September 16 notes, not current baseline provenance.
- Python AST parsing and `git diff --check` passed for the implementation. The separately committed owner brief retains its original trailing space; source briefs were preserved verbatim, not reformatted.

### Transfer preparation, 2026-09-18

At transfer preparation, no UCloud execution had occurred. The updated portable suite passes **59 tests**, including committed-file allowlisting, source-commit/checksum preservation, refusal to overwrite transfers, dirty-checkout rejection and symlink rejection. Shell syntax and documentation/context checks pass. Source validation now reports a contract error even outside a Git checkout, as expected for transferred code. Setup logging and persistent package-cache paths are prepared but not Linux-validated. The bundle contains no environments, source-paper/thesis caches or research data. The later owner-returned probe below updates transfer status; native outcomes remain pending.

The actual transfer archive was built from committed source `9c2b0ec6feb3b7884bbf7d519c63176d4fb10aea` and inspected locally. All **59 tests also passed from its extracted copy outside Git**, using the existing macOS portable environment; this does not validate Linux dependency resolution. `shasum -a 256 -c` passed. Local ignored locator: `artifacts/e001-transfer/e001-code-9c2b0ec6feb3.tar.gz`, with adjacent `.tar.gz.sha256`; approximately 47 KiB. SHA-256: `be85a52dd47eaab8aa9b68f3f9aaa38541d43ed9b68695c26169f95e111a3c85`. Intended owner-side upload locator: `/work/Home/dl_binner/e001/e001-gate0/transfer/`. Upload has not been confirmed. The package intentionally predates this results-only record; its embedded `SOURCE_COMMIT` identifies the executable snapshot. The builder can regenerate equivalent code from that commit, but gzip timestamps mean a rebuilt archive must receive its own checksum.

## Owner-returned initial probe, 2026-09-18

Source: output supplied by the owner in chat, inspected here; not direct HPC access. Job identifier `j-12396047-job-0`, start 15:29 on 2026-09-18 (owner-reported local time; timezone not independently verified). Owner reports **4 vCPU / 12 GB RAM**. Actual submitted duration/end time has not been supplied. The original 8-vCPU/24-GB recommendation was conservative, not a scientific requirement; retain the smaller allocation for extraction and prerequisite bootstrap. Native smoke feasibility remains unmeasured.

- Working directory `/work/Home/dl_binner/e001/e001-gate0/transfer`; mounted filesystem `/work/Home`.
- Ubuntu 24.04.4 LTS, Linux x86_64. Bash, Git, Python 3, tar, sha256sum, timeout, curl and bzip2 are present at `/usr/bin/` paths. **micromamba and `/usr/bin/time` are missing**. Presence alone does not validate program versions.
- Owner's `sha256sum --check` reports `e001-code-9c2b0ec6feb3.tar.gz: OK`. This supersedes the pending upload status at package preparation. Code extraction and all installations remain unconfirmed.
- Startup banner reports AMD EPYC 9535, 256 visible CPUs, roughly 755 GiB host RAM and 13-day uptime. These are not the owner's 4-vCPU/12-GB allocation or elapsed job time. `df` reports shared filesystem capacity (7.2P total, 2.1P available), not personal quota. The ASPEED graphics listing does not establish an allocated ML accelerator; the job remains CPU-only.
- SSH/ttyd startup messages contain no reported failure and do not require SSH configuration for this browser-terminal workflow.

The next checkpoint at that time was extraction. The owner has subsequently returned a successful checksum, `Code extraction verified` at the expected path, and full source commit `9c2b0ec6feb3b7884bbf7d519c63176d4fb10aea`. Extraction is now confirmed. No software installation, native smoke or research-data acquisition has been reported.

## Grouped driver preparation, 2026-09-18

The owner explicitly authorizes grouping steps that do not require intermediate interpretation and takes responsibility for requesting job extensions. This supersedes per-command chat pauses and repeated remaining-time questions. The supplemental [driver](../../scripts/e001_ucloud_preflight.sh) groups verified micromamba bootstrap, GNU time installation and unchanged mapping/AMBER setup/smoke, with fail-fast stages and return packaging. Its micromamba pin/checksum comes from the official release API as documented in [operations](OPERATIONS.md#current-grouped-execution). It does not acquire GI data or run scientific training.

Local validation: **60 portable tests passed**, including a mocked failed download that packages logs, never reaches system/tool installation and refuses a second attempt over the same outputs. Shell syntax passed. This tests orchestration failure handling, not actual Linux installs or native parity. The actual driver and all native stages remain owner-run and unexecuted at this handoff. The old execution snapshot remains unchanged; the separate driver's hash and exact executed copy are recorded by the driver itself.

## First native return reviewed, 2026-09-18

Owner-supplied [terminal output](../../agent_context/e001_ucloud_preflight_output.txt), [return archive](../../agent_context/preflight-return.tar.gz) and [checksum](../../agent_context/preflight-return.tar.gz.sha256) are preserved as a compact synthetic-check record (approximately 97 KiB archive; no research data). SHA-256 `45b5887fdbc80a43eb25a55a960000c5da57399d6cff33c0f47e323d793ad820` verified. All 108 archive members were inspected for path/type/duplicate safety without extraction. The returned driver matches our local driver hash, and returned setup/smoke hashes identify the transferred scripts.

All setup, pip-check, pipeline and smoke exit codes are zero. micromamba 2.9.0 and Ubuntu GNU time package `1.9-0.2build1` installed successfully; GNU time's display string `UNKNOWN` is not an installation failure. Native mapping reports strobealign 0.17.0 and samtools 1.24. AMBER reports the intended `f8b3a601043d13fc4227d5691c13561eb4490e50` source commit. Package-script security warnings are advisory; no reported solver/import/command failure occurred.

- Mapping: 1,870 records; correct-reference fraction 1.0 on the tiny unique-reference fixture. Both thinning checks preserve mates: 107/935 and 111/1,045 retained templates. Random 10% sampling need not retain exactly 10% in small fixtures. No inference about metagenomic mapping accuracy or throughput follows.
- AMBER: perfect, merged, split, missing, unassigned, strict threshold boundary and multi-origin assertions pass. The conservative E001 R95 agrees with AMBER-derived purity-filtered recovery on unique-origin cases. Unconstrained AMBER recall intentionally differs for merged bins (1.0 versus R95 0.0), and multi-origin behavior intentionally differs (1.0 versus 0.5). Neither difference is an evaluator bug.
- Driver timestamps: 14:25:02-14:26:02 UTC, 60 seconds total. Mapping smoke: 0.40 seconds, maximum RSS 53,528 KiB; AMBER: 1.58 seconds, 164,744 KiB. Setup: mapping 17 seconds, AMBER 37 seconds. The batch interval corresponds to approximately 0.067 allocated core-hours at 4 vCPU, not total job cost; idle/earlier allocation remains additional.

**Reproducibility caveat:** both pip inventories expose `easybuild`, `easybuild-easyblocks`, `easybuild-easyconfigs` and `easybuild-framework` 5.3.1, absent from our install recipes and conda inventories. External Python paths or user-site exposure are a hypothesis, not a confirmed cause. Core fixture assertions passed, but do not call these fully isolated/reconstructable environments yet. The micromamba `list --explicit` outputs also lack an `@EXPLICIT` header/checksums and include blank entries; pip freeze contains conda build-time `file://` paths. Preserve them as observed inventories, not directly replayable locks.

Next: [environment review](../../scripts/e001_environment_review.py), no downloads or reinstallations. It records package/import origins with inherited paths, removes PYTHONPATH/PYTHONHOME/PYTHONUSERBASE and disables user-site for child processes, asserts distribution/import containment, records structured conda package provenance, and reruns both native checks into a new directory. Existing installs and first outputs stay intact. Return the resulting archive for inspection before GI acquisition. Python's [environment documentation](https://docs.python.org/3/using/cmdline.html#envvar-PYTHONNOUSERSITE) grounds the process-local isolation controls; these do not edit shell startup files.

Review-driver preparation: 63 portable tests passed, including external-distribution injection/detection, successful clean-process exclusion and failure-status recording. No native clean-environment rerun has yet occurred. Documentation links and whitespace checks pass for maintained edits; original owner terminal output is preserved verbatim.

## Native check status

### GI download succeeded; coordinate collision found

The alias-aware conversion retry [return](../../agent_context/conversion-alias-return.tar.gz) verifies against [checksum](../../agent_context/conversion-alias-return.tar.gz.sha256) (`39658135488174f911bcbac7a010270c4bb7904bcc63a86fa6172877fefa0c00`) but exits 1 after two seconds. No `input-preflight-v2` was created. Stderr reports `Invalid DNA: _from__to_-42_total_0` (the complete scan reports the literal Biopython ID `*from__to*-42_total_0`). The owner's complete local scan found exactly two such records, both length zero and SHA-256 `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`; no other malformed records were found. They have no accession or valid coordinates and cannot match the corrected truth table.

Correction: `prepare_hmp` now records and excludes only the two exact empty orphan spellings observed in the scan/error evidence (`*from__to*-42_total_0` and `_from__to_-42_total_0`), writing `excluded-fasta.json` and `excluded_fasta_records` in `inventory.json`. A nonempty record with either ID still fails. All other malformed headers, invalid DNA, duplicate IDs and join failures remain strict errors. This is explicit handling of a source-file artifact, not arbitrary filtering or a biological result.

The correction is covered by portable tests for both exact empty-orphan spellings, nonempty orphan rejection, alias preservation, conflicting metadata and preservation of repeated failed conversions. With `TMPDIR=/var/tmp`, all **73 portable tests pass**; the first local test invocation failed before test execution because the default macOS temporary directory was unusable. Documentation and shell checks pass. The next bundle contains this correction and the guarded conversion-only retry script.

The first guarded retry was stopped because `input-preflight-v2/` already existed. This was a partial output directory left by the failed parser, not a completed inventory; the return packager intentionally omitted it. The next retry moved it with the prior stage/return under a numbered `failed-conversion-malformed-fasta*` directory, but still failed because the runtime identifier spelling was not in the exception set. Recovery now selects the next unused numbered preservation directory and the parser accepts only the two exact observed empty spellings before creating fresh output. Completed or ambiguous directories remain fatal.

The following retry, from source commit `c8ec39581bfa12d903f89111f274379494738c38`, passed those orphan/recovery checks and reached the next strict input contract. It stopped on `Missing/duplicate coordinate join: CP002609.1_from_3_to_1894400_total_1894398` after four seconds. That message conflates a missing mapping key with a duplicate FASTA coordinate, so it is not yet evidence for either interpretation. The new [read-only HMP join audit](../../scripts/e001_hmp_audit.sh) reports both categories across the complete files before another conversion attempt. The owner's return archive and terminal output are preserved as the latest failure evidence.

The owner-run audit from source commit `6901be8153c2e25f075716b6c72712025a6b096a` completed in ten seconds and returned `join_contract_passes: false`. It inspected 210,634 FASTA records, including the two known empty orphan records. There are 210,632 non-orphan coordinate keys in the FASTA and 210,612 unique keys in the corrected mapping: 20 FASTA keys are absent from the mapping, while no mapping keys are absent from the FASTA. FASTA duplicate-coordinate, duplicate-ID, malformed-header, invalid-DNA and length-mismatch counts are all zero. The mapping contains six duplicate coordinate groups, all with identical non-ID metadata and therefore consistent with the six documented anonymous-ID aliases. Source SHA-256 values are `67aeeeb70e5ba0e1506bf95c79bb25b06869c0486e6c0ea111763c3b060c0baf` (FASTA) and `4353f05be6a94c0c05be083088148eac01bcf34dc05c6a061709ff5fbd61d720` (corrected mapping). This is a data-contract checkpoint, not a scientific result. The 20 FASTA-only records must be compared with the original mapping and setup metadata before conversion is changed.

Owner's targeted FASTA scan subsequently confirmed exactly one sequence for each truth alias pair, with matching declared/actual lengths. Pairs and lengths: PC21351/PC21352 (2,466 bp), PC24985/PC24986 (1,259), PC52686/PC52687 (1,360), PC97787/PC97788 (136,176), PC100714/PC100715 (4,140,334), PC210631/PC210632 (202,292). The three longer sequences total 4,478,802 bp and must not be dropped or counted twice. The three shorter sequences remain below the unchanged 2,500-bp input cutoff.

Correction: coordinates still define the FASTA join. Distinct source IDs at one coordinate are aliases only if every other truth field agrees exactly, including genome, taxonomy and number_reads. Choose the numerically smallest PC ID (stable lexical tie-break), retain all source IDs in `contigs.jsonl` and `inventory.json`, and count the physical sequence once. Duplicate same-ID/same-genome rows, conflicting aliases and multiple FASTA occurrences still fail; same-ID multi-origin truth remains ambiguous, not merged into a unique origin. Source files are never modified. Regression tests cover row-order independence, numeric ID selection, count preservation, below-cutoff reporting, conflicting fields and preserved multi-origin behavior. Corrected real-data conversion remains pending; retry only conversion into new output using a new committed code bundle.

The new owner [terminal output](../../agent_context/e001_gi_inventory_terminal_output.txt) and checksum-verified return replace the earlier same-named local return; the earlier failure remains preserved in Git and UCloud's `failed-inventory-missing-time/`. Recovery installed GNU time, prerequisites passed, and all six manifest-listed files downloaded: GSA 972,133,785 bytes; corrected mapping 12,597,447; original mapping 25,194,106; setup archive 1,906,532,721; README 741; checksum manifest 709,793. The setup member list includes `metadata.tsv`, `genome_to_id.tsv`, per-sample taxonomic profiles and `config.ini`; no extraction is authorized yet.

Conversion failed with `Duplicate truth row` while reading mapping rows, before output-directory creation. Independent read-only inspection of the publisher's corrected mapping (MD5 verified as `954106872f9af342c0b7fd4422d8db9f`) finds 210,618 rows and six duplicated (contig_id,start_position,end_position,genome_id) groups; all six contain differing rows, including differing anonymous IDs. Example: PC21351 and PC21352 both describe HG917869.1:696659-699124 in OTU_97.20215.0. This violates our assumed one-coordinate/one-anonymous-ID join, rather than showing corrupt downloads. Do not drop truth rows blindly. A targeted scan of the already downloaded FASTA is required to count corresponding records and compare sequence hashes before choosing a correction. No biological result or scientific approval follows.

### GI inventory attempt failed before acquisition

Owner return verified: [archive](../../agent_context/gi-inventory-return.tar.gz), [checksum](../../agent_context/gi-inventory-return.tar.gz.sha256), SHA-256 `05287ad75941a1120034c78c9834b264fb4e158cf8d8136b7bf6946ffc8af80e`. Safe archive members and the executed driver match the prepared inventory wrapper. At 2026-09-18 19:37:08 UTC the prerequisites command failed with exit 127 because `/usr/bin/time` was absent. The timing wrapper could not launch Python; acquisition and conversion never ran. This is an infrastructure failure, not a dataset or scientific result. A container restart/replacement would explain loss of the system package, but that event is not confirmed by the return.

Root cause in our wrapper: it assumed the earlier container's system utility persisted, although only experiment files/environments under `/work` are intended to persist. The corrected inventory wrapper checks/install GNU time before timed commands and records package/version/hash and bootstrap logs. Its explicit `--retry-missing-time` mode checks the known failure signature and absence of inventory/conversion data, verifies the old return checksum, and moves the failed stage and return files intact into `failed-inventory-missing-time/`. It refuses existing recovery destinations or partial data; no automatic deletion/retry loop. Only then does the normal grouped inventory resume. The already executed source snapshot and installed tool environments are unchanged.

Local verification: 65 portable tests pass, including failed-attempt preservation and refusal to recover over existing inventory data. Shell syntax and documentation checks pass. Actual recovery and GI acquisition remain owner-run and unexecuted at this handoff.

### Environment review resolved, 2026-09-18

The owner-returned [review archive](../../agent_context/environment-review-return.tar.gz) verifies against its [checksum](../../agent_context/environment-review-return.tar.gz.sha256): `b00b14cc6665b6ff7a6c12fb8a0a284596ff75bebc5a4f923864fec64e7a6819`. All 71 members passed path/type/duplicate checks; the executed review script matches the locally prepared source. All ten recorded commands, pip checks, both native smoke reports and final status pass.

Confirmed cause: the four EasyBuild distributions came from `/home/ucloud/.local/lib/python3.12/site-packages` with `site.ENABLE_USER_SITE=true`; PYTHONPATH and PYTHONHOME were unset even in the observed processes. With clean-process controls, user-site is disabled, all discovered distributions are inside the intended environment prefix, and NumPy/Biopython/pysam (plus pandas for AMBER) resolve inside that prefix. Required module origins were already correct in the first run. No installation changes were needed.

The isolated mapping report preserves 1,870 records, correct-reference fraction 1.0, and exactly the same retained-template counts/pair-consistency results. AMBER's checks match the first return. The mapping BAM byte hash differs between output locations; no byte-identical-output claim is made. Command timings for the clean smoke reruns were approximately 0.52 and 1.67 seconds, not research-scale benchmarks.

Structured conda metadata now contains 52 mapping and 27 AMBER package records, all with URLs and at least one package checksum. This repairs provenance missing from the first text exports, but does not establish tested environment reconstruction or hashed pip wheel locks. Those remain runtime-freeze work before science, not blockers for bounded GI inventory.

**Disposition:** the isolation concern is resolved for these checked imports/distributions. Proceed to GI assembly/truth/setup acquisition and initial coordinate inventory, with process-local Python isolation retained. Other binner smoke, taxonomy resolution, CPU feasibility and scientific launch remain gated. The new inventory driver wraps the unchanged transferred snapshot and returns summaries only; no GI acquisition has run yet.

Local preparation checks: 64 portable tests passed, including refusal to overwrite an existing inventory before starting work; shell syntax and documentation checks passed. Maintained setup/smoke scripts now apply the observed isolation fix for future transfers. Existing UCloud code stays untouched, and the new inventory wrapper supplies the same controls around the old snapshot. The inventory download/conversion itself remains unexecuted here.

| Native check | Current status and what it must establish |
| --- | --- |
| strobealign 0.17.0 / samtools 1.24 | Synthetic native checks and isolation rerun passed. Real-read mapping remains untested. |
| Pinned AMBER | Native fixtures and isolation rerun passed, including intended unique/multi-origin and threshold semantics. No scientific dataset evaluated. |
| Pinned VAMB | Unexecuted. Actual BAM/TNF extraction, native scale invariance including total abundance, zero-row/zero-column behavior and CPU forward pass under its specified dependencies. |
| Pinned COMEBin | Unexecuted. Fixed augmentation identity, full native six-view coverage recomputation, measured variance, pseudocount-aware scaling and CPU forward pass. |
| Pinned MetaBAT2 | Unexecuted. Source-built executable, native mean/variance extraction and assignment format, including genuine empty output versus command failure. |
| Linux environment recipes | Mapping/AMBER installed and process isolation verified; structured provenance captured. Reconstructable locks and other tool recipes remain pending. |

Full native training/clustering, marker payload verification, CPU throughput projection, real-read prefix mapping comparison, full data/truth/taxonomy joins and research launch remain later gates. The smoke job is deliberately not a surrogate benchmark. A failure is retained and investigated; no older PyTorch/tool substitution is allowed under the original pin.
