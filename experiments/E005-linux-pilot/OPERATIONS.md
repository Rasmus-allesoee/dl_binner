# E005 owner operations

The native Linux smoke **and v5 GI pilot are accepted**:
[pilot inspection](README.md#accepted-v5-native-gi-pilot-and-independent-review-2026-10-06),
[pilot receipt](pilot-observed.json), [smoke receipt](linux-observed.json).
**Do not upload or rerun the command below.** It is the executed recipe retained
for provenance. Preserve `/work/Home/dl_binner/e005/gi-pilot-b9k3j2r3/`, its heavy
files and the original transfers/logs/returns. No additional UCloud job is needed.
The exact next step is local implementation of the
[prepared generic-command milestone](../../docs/PROTOTYPE.md#prepared-next-milestone-one-end-to-end-command).
No larger data, extra seed, three-way study, architecture gate or public release.

## Executed v5 upload files and organization

Create `/work/Home/dl_binner/e005/transfer/` in UCloud Files if needed. Upload
`e005-gi-pilot-v5.tar.gz` and `e005-gi-pilot-v5.tar.gz.sha256` **there**, keeping
filenames. Launch copies, captured terminal logs and returned archive/checksum
also stay there. Persistent unique attempts stay under the E005 root and accepted
runtimes under `envs/`; earlier smoke files are preserved in place.

The small packet contains frozen code/contracts, the exact prepared **13.13-MB**
short-inclusive reference, its full contig metadata and tiny real mapper-contract
DNA. It contains no whole source assembly, large FASTQs/BAMs, runtime copies or
GLM payloads. Reads already retained on shared UCloud storage are sampled in place.
No download, solver, compiler or environment installation runs on the node.

## Historical job and exact executed command

Start a **single-node Terminal job, 4 vCPUs / 12 GB RAM, no GPU**, with Home and
`/work/RasmusAllesøeNielsen#2936/` mounted as before. Local executor, no Slurm cluster
needed. Provision **at least 10 GB free** for this attempt; estimates do not shrink
the frozen data. Do not run other unaccounted workloads. Existing E005 binner and
workflow prefixes plus E001 mapping/AMBER prefixes must remain intact. Nothing
needs activation or sudo. System Bash, Python >=3.10, tar, sha256sum, tee, mktemp
and env are prerequisites; errors are logged and stop dependent work.

The owner executed this recipe after both uploads; retain it without repetition:

```bash
bash <<'BASH'
set -euo pipefail
transfer=/work/Home/dl_binner/e005/transfer
mkdir -p "$transfer/launches"
cd "$transfer"
log=$(mktemp "$transfer/e005-gi-pilot.XXXXXX.log")
trap 'rc=$?; printf "\nTERMINAL_LOG=%s\nEXIT_CODE=%s\n" "$log" "$rc"; exit "$rc"' EXIT
(
  for tool in python3 tar sha256sum tee env; do command -v "$tool" >/dev/null || { echo "Missing prerequisite: $tool"; exit 2; }; done
  python3 -I -c 'import sys; assert sys.version_info >= (3,10), "Python >=3.10 required"'
  sha256sum -c e005-gi-pilot-v5.tar.gz.sha256
  sha256sum e005-gi-pilot-v5.tar.gz
  launch=$(mktemp -d "$transfer/launches/gi-pilot.XXXXXX")
  tar -xzf "$transfer/e005-gi-pilot-v5.tar.gz" -C "$launch"
  env -u PYTHONPATH -u PYTHONHOME -u PYTHONUSERBASE \
    PYTHONNOUSERSITE=1 PYTHONDONTWRITEBYTECODE=1 \
    python3 -I -B -u "$launch/e005-gi-pilot/scripts/e005_pilot_owner.py" \
    --root /work/Home/dl_binner/e005 \
    --allocated-vcpus 4 --allocated-ram-gb 12
) 2>&1 | tee "$log"
BASH
```

## Work, resources and stop conditions

Entry probes verify exact accepted E005 inventories/package code and isolation.
E001 binaries/AMBER source and the original dependency lock are reused read-only.
The AMBER check compares the exact retained lock hash and isolated package inventory;
it excludes only the four EasyBuild packages historically observed outside the
prefix, and resolves the lock's two direct URLs to versions in the earlier clean
prefix inventory. Every discovered distribution must still originate inside AMBER.
Missing or changed runtimes stop without installing or repairing them. Tiny **new adapter** tests check mapping of real DNA, native
flag/CIGAR/zero-depth semantics and AMBER/R95 boundaries; no model smoke is repeated.

The recipe declared a serial Snakemake DAG which validates/hashes each complete anonymous FASTQ twice,
selects exactly **one million pairs per sample** with the frozen label-blind hash
rule and maps samples 1/4 to the exact E005 reference. Mapper requests all four
threads. Sort/index main plus three extra threads fit four; they follow mapping
serially. Native depth main plus two extra BGZF workers plus one Python aggregator
fit four. Sampling/reference parsing are I/O/serial work; thread requests cannot
make every algorithm saturate the allocation. Numeric CLI/BLAS/OpenMP budgets
are four, Torch interop one, loader zero and only one numerical rule runs at once.
Native reports, rule benchmarks and descendant samples retain actual use.

Features are freshly extracted only for this new pilot. Learned TNF+depth and
raw TNF+the same depth use frozen seed-11 transforms/settings/clustering. Reload,
finite axes/masks and both complete exports must pass before truth is consumed by
native AMBER and conservative R95. All **5,309 contigs / 12,924,259 bp** remain in
accounting, including **1,097 below-500 exclusions**, observed zero-depth rows and
noise. No oracle K, truth tuning, forced assignment or requirement for superiority.
This is recovery of available sequence from four GI GSA genomes with development
overlap, not whole-MAG quality, real-assembler performance or independent validation.

Prospective ceilings: setup **30 minutes**, scientific DAG **two hours**, fresh
features **30 minutes**, each cluster **15 minutes**, working sampled subtree RSS
**8 GB**, overall execution **three hours / 12 allocated vCPU-hours at four**.
Parent deadline covers verification/hashing/setup; rule and DAG guards cover
children. Evidence-only collection follows the execution deadline and its time
is charged separately. Initial rough planning range **15–60 minutes**, dominated
by two passes over each ~10.6-GB source and mapping; shared-storage behavior is
unmeasured here and this is not a measured Linux throughput promise. Stop on
mismatched/partial source, missing axes/receipts, native failure or time/RSS cap.
No automatic retry, extra input, seed or architecture is launched.

The terminal shows stage starts and 20-second heartbeats. Detailed timestamped
rule starts/ends/heartbeats live in `pilot/logs/`; worker output, commands and
sampled CPU/RSS live in `rules/`, with extended Snakemake `pilot/benchmarks/`.
Unique attempts preserve previous ones. A completed-directory dry-run must schedule
nothing. Do not rerun this command to obtain accepted outputs or modify old attempts;
return failure evidence before preparing targeted recovery.

## Return and retention

Last lines print absolute **return archive**, **checksum** and **TERMINAL_LOG**,
all below `transfer/`. Download and upload those three files here even on failure.
The return includes verified packet/runtime/commands, selection IDs, native BAM
headers, depth tables/axes, feature masks, checkpoint/reloaded embeddings, raw and
learned partitions, every export, AMBER/R95/strata, benchmarks, resource receipts,
and a file inventory with hashes/bytes and which files were omitted from the copy.
Sampled FASTQs, native SAM and BAM remain in the persistent attempt and are
excluded from the return; never delete them to rerun this accepted pilot.

CPU/RSS samples are not exact peaks or the provider invoice. Allocation times
complete driver wall includes probes/setup and is printed through collection;
outer checksum/extraction, upload and owner idle remain outside that clock. The
inventory records retained attempt bytes; prefix disk/provenance is separate.
If SIGKILL/job termination prevents collection, return the captured terminal log
for evidence-only recovery. Successful software execution is accepted only after
returned-output inspection; any quality degradation is a valid retained result.

## Packet history and final acceptance

The executed **v5** source commit, archive size and checksum are recorded in the
[pilot implementation record](README.md#owner-v4-preflight-failure-and-v5-repair-2026-10-06).
The prior v4 packet passed its local fixture ([receipt](pilot-local-observed.json))
but its owner-run preflight stopped before adapter checks or pilot work because its
AMBER lock comparison mishandled known user-site entries and direct references.
V5 passed the unchanged pilot with the corrected isolated inventory check.
Independent review rehashes 477 returned files and confirms every accepted output
contract. Neither v5 nor any earlier packet should be rerun. Historical future-
tense resource/return instructions above describe that executed recipe, not pending
work. Heavy native hashes remain receipt-bound because those files stay on UCloud.

Actual 4/12 execution through collection: 495.12096 s / 0.5501344 allocated
vCPU-hours, sampled peak worker RSS 1.785 GB; retained attempt inventory 3.297 GB
and return copy 32.09 MB. Prefixes/original reads/old attempts and owner idle are
separate. The original shell EXIT trap printed outside `tee`; success is supported
by all native exit codes and matching driver/return events. The next generic
launcher must capture its exit status inside the log and use explicit `-I -B`
for reused-prefix Python children. No environment rebuild or cleanup is requested.

Returned scheduler events show overlapping four-thread jobs despite the serial
label. Accepted scientific outputs and actual costs remain valid, but that
resource-plan claim is rejected. Current future-launcher options/DAG barriers
are locally corrected and tested; see the
[correction](README.md#scheduling-nonconformance-and-local-correction). No corrected
owner packet is built and no E005 rerun is requested.
