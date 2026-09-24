# D009: Parallel Preprocessing Within One Terminal Allocation

Status: accepted for the initial two-lane attempt and amended 2026-09-24 for the
next owner run. The new resource choice supersedes the 8-vCPU/two-lane launch
setting for this preprocessing retry, not the scientific mapping/thinning
contract or the option to revisit parallel execution after measured results.

## Evidence and Correction

The owner confirmed that Terminal offers **Slurm cluster: Yes**, as used for
the thesis. The [Terminal guide](https://docs.cloud.sdu.dk/Apps/terminal.html#create-a-slurm-cluster)
confirms an in-app Slurm cluster, also on one node, with node0 serving as both
controller and compute node. Thus SDU/K8s does not imply Slurm is unavailable;
no separate Snakemake app or provider switch is required. The guide's full-node
warning concerns multi-node configurations, not a requirement to rent a full
physical node for this single-node local-executor workflow.

The [UCloud Slurm integration guide](https://platform.cloud.sdu.dk/slurm/slurm.html)
describes provider-side Slurm integration, account mapping and billing. It is
not the same mechanism as the Terminal application's in-allocation cluster.
The [Snakemake Slurm executor](https://snakemake.github.io/snakemake-plugin-catalog/plugins/executor/slurm.html)
submits rule jobs via Slurm; threads and memory requests belong to individual
rules, while submission concurrency and the overall UCloud allocation are
separate constraints. None of these gives access to CPUs beyond those rented.
All three sources consulted 2026-09-23.

The requested thesis files were inspected read-only at repository commit
`4029b810045ff9196be0035e48e7fb32ca4be792`, under
`/Users/rasmusallesoeenielsen/Documents/Speciale/hadal-binning-benchmark/real_benchmark`:

| File | SHA256 |
| --- | --- |
| `workflow/Snakefile` | `03c075542d9db38989220de90456994c321c9b10c0e5c52dc230a925d01a7ef2` |
| `profiles/slurm/config.yaml` | `b03ab704efc07039cf4b7de733f571f90f9e04f053c9878ae007c19262217ca2` |
| `config/config.yaml` | `6f7a0a630f17160d2056144d810900a619e2bd5617f88baf35f285c052e9a901` |

The profile uses `executor: slurm`, partition `CLOUD`, account `escience`, up to
100 submitted jobs, per-rule threads/memory/runtime and extended benchmarks.
The Snakefile expands sample-wise mapping and joins the resulting BAMs for
coverage extraction; the config separates input paths and external tool
environments. These are useful patterns, not current E001 resource settings.
The thesis mapping pipe gives both Bowtie2 and samtools sort the rule's full
thread count concurrently; E001 intentionally budgets the entire pipeline
instead. No thesis file was changed, and this inspection is not a thesis rerun.

## Initial Decision, 2026-09-23 (superseded for the current retry)

Hardware correction, 2026-09-23: the available Terminal choices are discrete;
the owner's screenshot confirms 8 vCPU / 24 GB and 16 vCPU above it, with no
12-vCPU option. The remaining-nine task has not run. Choose **one 8-vCPU / 24-GB
allocation**, **two sample lanes**, and **4 CPUs per mapping pipeline** (2
strobealign + 1 filter + 1 sort). Download only one archive at a time. Each lane
finishes its sample before starting another, so nine libraries make four full
two-sample waves and a final single-sample wave. The native commands, read
groups, ordered thinning seeds and accepted sample-0 reuse do not change.

Reserve 10 GB per mapping/thinning rule, 1 GB per streaming extraction and
0.512 GB per download. For the chosen 24-GB machine, cap global rule memory at
23 GB, leaving at least 1 GB for coordinator/OS overhead; two simultaneous
mappings request 20 GB.
These are scheduling budgets, not hard OS memory limits or measured peaks.
The accepted full sample ran within 12 GB; prefix subprocess peak was about
4.11 GiB. This supports the two-worker budget but does not measure concurrent RAM.
New per-rule benchmarks provide the next observation. All threads are explicitly
bounded; coordinator overhead shares the allocation.

**Use Snakemake's local executor for this run.** It already schedules parallel
jobs on one node and enforces aggregate thread/memory reservations. Installing
a second executor and testing Slurm account/partition/child-job cancellation
would add no compute capacity or necessary scheduling capability here. Select
Slurm cluster **No** for the simplest launch; an already-enabled **Yes** setting
is compatible, but this command does not submit Slurm jobs. Do not concurrently
run unrelated local or Slurm workloads against the same 8-CPU allocation.

Serial 4-vCPU execution remains a supported fallback (`--max-concurrent-samples 1`),
not the preferred owner command. Based on sample 0's 42-minute full preprocessing
time, two lanes need about five waves (roughly 3.5 hours of mapping/preprocessing)
before downloads and I/O effects. Plan roughly **4-5 hours / 32-40 allocated
core-hours**; this is a projection, not measured parallel throughput. A 16-vCPU
allocation could support four 4-CPU workers if the workflow concurrency cap were
raised, but may reduce elapsed time without reducing charged core-hours: UCloud
charges the full allocation while a partial final wave finishes, and nine samples
do not divide evenly into four. That higher-concurrency configuration is not
prepared for this run. We have no measured 16-vCPU run, so 8 vCPU is the more
resource-conscious next step.
The unchanged 80-core-hour group ceiling becomes **10 hours at 8 vCPU**, including
in-driver waiting. Storage remains roughly 230.4 GB retained, with 275 GB initially
free and extra transient sort space within that headroom. No additional data or
model-training scope is introduced.

## Owner-run utilization review, 2026-09-24

The first corrected grouped run used an 8-vCPU allocation and did start two
mapping rules at once. Its log reports `Provided cores: 8`, `Execute 2 jobs`,
four reserved threads for each mapping rule, and Strobealign processing each
sample with **two threads**. The owner observed about **398% CPU utilization**
on UCloud, or roughly four busy CPUs. The cause is explicit in the wrapper:
`scripts/e001_preprocess.py` set mapper threads to `sample_vcpus - 2`, reserving
one CPU apiece for the concurrently streamed Samtools view and sort stages. It
was not a failure to launch the second sample. The local Strobealign source
README documents `-t N` as the mapping/indexing thread count, and its mapping
loop starts N workers; no new environment or tool installation is needed.

For the next attempt, choose **4 vCPU / 12 GB, one sample at a time, with
Strobealign explicitly set to four threads**. This uses a smaller paid
allocation while giving Strobealign four worker threads. The two single-thread
Samtools helpers remain concurrent in the streaming pipeline and can contend
for CPU time; UCloud still caps total use at the four rented CPUs. The
per-sample benchmark will measure end-to-end wall and CPU time. Do not assume
linear scaling from two to four mapper threads. This is a reversible execution
setting, not a change to samples, inputs, read filters, seeds, or scientific
scope. Reuse only the two publisher-verified archives from the interrupted
attempt after its failure status is recorded; never reuse its partial BAMs.

This 4-vCPU configuration has a **20-hour maximum** under the existing
80-allocated-core-hour group ceiling. The prior 4-5-hour/32-40-core-hour
two-lane projection does not apply to this changed thread/concurrency setup.
Update cost and throughput estimates from the new run's actual allocation and
per-rule benchmarks.

## Future Slurm Use

Use the Terminal Slurm option when multi-node placement, scheduler-managed jobs
or mixed workloads justify it. First capture `sinfo -N -l`, `scontrol show partition`
and the available account information; verify the in-app scheduler advertises
only usable rented resources and all workers see the same mounted paths and
isolated environments. `CLOUD` / `escience` are thesis observations, not universal
constants. UCloud's provider-account mapping must not be confused with them.

Then use a pinned plugin in a new versioned workflow environment, an explicit
Slurm profile, bounded `--jobs`, per-rule `threads`, `mem_mb`, `runtime`, and
aggregate resource limits. `jobs` alone does not cap total CPU consumption.
Test tiny submissions, logging, accounting and cancellation before research
execution. A killed local coordinator is not proof that `sbatch` jobs stopped.
Retain UCloud allocation-walltime accounting even when Slurm reports rule CPU
time; unused parts of an in-app allocation still cost resources.

Revisit if measured I/O contention makes three lanes inefficient, RAM is
insufficient, or the next workflow requires multiple nodes. Reduce concurrency
explicitly or amend resources, never alter read populations or mapping filters.
