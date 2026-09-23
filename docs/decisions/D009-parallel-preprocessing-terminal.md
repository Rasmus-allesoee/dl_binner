# D009: Parallel Preprocessing Within One Terminal Allocation

Status: accepted, 2026-09-23. Supersedes the serial scheduling recommendation
from D008's follow-through, not its scientific mapping/thinning contract.

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

## Decision

Use **one 12-vCPU / 36-GB Terminal allocation**, **three sample lanes**, with
**4 CPUs per mapping pipeline** (2 strobealign + 1 filter + 1 sort). Download
only one archive at a time, overlapped with compute, to avoid multiplying load
on the publisher or assuming threefold network throughput. Each lane must
finish its sample before starting another; at most three samples are in flight.
The native commands, read groups, ordered thinning seeds and accepted sample-0
reuse do not otherwise change.

Reserve 10 GB per mapping/thinning rule, 1 GB per streaming extraction and
0.512 GB per download. Snakemake gets a global 35-GB rule budget, leaving at
least 1 GB for coordinator/OS overhead; three mappings request only 30 GB.
These are scheduling budgets, not hard OS memory limits or measured peaks.
The accepted full sample ran within 12 GB; prefix subprocess peak was about
4.11 GiB. This supports the proposed headroom but does not constitute a measured
three-way RAM bound. New per-rule benchmarks provide the next observation.
All threads are explicitly bounded; coordinator overhead shares the allocation.

**Use Snakemake's local executor for this run.** It already schedules parallel
jobs on one node and enforces aggregate thread/memory reservations. Installing
a second executor and testing Slurm account/partition/child-job cancellation
would add no compute capacity or necessary scheduling capability here. Select
Slurm cluster **No** for the simplest launch; an already-enabled **Yes** setting
is compatible, but this command does not submit Slurm jobs. Do not concurrently
run unrelated local or Slurm workloads against the same 12-CPU allocation.

Serial 4-vCPU execution remains a supported fallback (`--max-concurrent-samples 1`),
not the preferred owner command. Parallelism reduces waiting for nine independent
libraries; it is not guaranteed to reduce allocated-core-hour cost. Estimated
processing floor is 6.26/3 = **2.09 hours**, before fill/drain, shared-I/O contention
and downloads. Plan roughly **3-4 hours / 36-48 allocated core-hours**, not a
guaranteed 3x speedup. The unchanged 80-core-hour group ceiling becomes
**6 h 40 min at 12 vCPU**, including in-driver waiting. Storage remains roughly
230.4 GB retained, with 275 GB initially free and extra transient sort space
within that headroom. No additional data or model-training scope is introduced.

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
