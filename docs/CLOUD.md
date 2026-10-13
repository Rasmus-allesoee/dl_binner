# Google Cloud workspace operations

Updated: 2026-10-14 (Copenhagen; provisioning receipts are dated 2026-10-13 UTC).
[D014](decisions/D014-google-cloud-workspace.md) owns the provider choice;
[STATE](STATE.md) owns the next action; this guide owns access, costs and retention.
**Infrastructure established: strict IAP SSH, exact private repository clone,
pinned Linux Codex CLI and private archive upload/readback pass. ChatGPT
authentication now passes;
an actual desktop remote-project chat is still pending.** See the
[structured receipt](evidence/gcp-workspace.json) for observations and hashes.

## Phase boundary and account verification

Phase 1 establishes a CPU Linux workspace, private backup and actual Codex SSH
access. **Do not inspect the E009 v14 return, acquire data, install all binners,
fit tools or score E009 in this phase.** The owner's SDU login is deactivated;
UCloud files are reported intact but inaccessible. Do not delete them or rerun its
old transfer command. [The archived UCloud guide](history/UCLOUD_OPERATIONS.md)
and [E009 command](history/E009_UCLOUD_OPERATIONS.md) preserve that provenance.

Owner reports paid billing, expected USD300 remaining, expiry 2027-01-12 and a
budget alert. The owner subsequently read the current display as **kr1,973 remaining, none used,
expiring 2027-01-12**. APIs independently confirm account open/project billing
enabled and DKK currency; paid upgrade is owner-reported. The browser could not
read scope/status labels because of the loader mismatch below. Keep those evidence
sources distinct; USD300 is the original expected value, not a new displayed
USD balance.
Before any service activation/resource creation:

1. Inspect Billing → Overview for active paid billing and the selected account.
2. Inspect Billing → Credits for the Welcome credit's displayed remaining and
   original values, currency, available status, scope and exact start/end dates.
   Also inspect current costs/pending usage and the existing budget alert.
3. Inspect existing projects, billing linkage, enabled services, VM/disks/buckets,
   regional CPU/disk/IP quotas and current IAM access. Reuse a suitable project;
   do not create a second billable footprint by assumption.
4. Verify each proposed product/SKU is covered by that credit. Compute Engine CPU,
   ordinary Persistent Disk, non-premium Ubuntu, private Standard Cloud Storage
   and basic GCP IAP are the proposed path. Google documents VPC network charges
   as payable from trial credits; IAP for GCP itself has no service fee. No GPU,
   Marketplace image, Ubuntu Pro, partner model, Cloud NAT, load balancer or paid
   support is required. Paid access does not establish trial-credit eligibility.
5. Reconcile the complete estimate with remaining credit, expiry and existing
   account usage. **Stop and ask before unclear/uncovered costs or possible
   spending beyond credits.** Alerts and API quotas are not a credit hard stop.
   Persistent storage must be addressed before expiry; do not silently accept
   post-expiry payment-card billing or destroy evidence to avoid it.

Official rules: [credit/upgrade terms](https://docs.cloud.google.com/free/docs/free-cloud-features),
[displayed credit fields](https://docs.cloud.google.com/billing/docs/how-to/resolve-issues#viewing_promotional_credits),
[budget behavior](https://docs.cloud.google.com/billing/docs/how-to/budgets).
No credit amount is inferred from account upgrade or absence of known jobs.

## Established initial layout and costs

The workspace uses `us-central1` (Iowa), zone `us-central1-a`. Live quota and
capacity checks passed: 12 global CPUs and 24 regional E2 CPUs available at entry.
CPU work on public simulated DNA does not presently need an EU-only
location. Iowa offers low E2 pricing and small US Free Tier storage allowances;
EU locations reduce interactive latency but raise costs/lose these allowances.
Co-locate VM and bucket to avoid cross-region transfers. This is not a data-residency
choice for future private clinical data.

Created **`dl-binner-cpu`, regular e2-standard-4, 4 vCPU /16 GiB**, with pinned
non-Pro x86-64 image `ubuntu-2404-noble-amd64-v20261009`, **30-GiB pd-standard boot**
(`dl-binner-cpu`) and **50-GiB pd-balanced working disk** (`dl-binner-work`), mounted
at `/srv/dl_binner`. Native Linux reports four CPUs; the UUID-based persistent
mount configuration passed verification after systemd reload. This fits code/setup
and small checks now, not bulk E009.
Balanced working storage provides better small-file/random-I/O behavior than a
tiny standard disk; the large UCloud copy problem is not a reason to recreate
snapshots here. Exact image/VM/disk descriptions are recorded in the receipt.
Secure Boot, vTPM
and integrity monitoring are enabled; both disks have `autoDelete=false`.
No GPU, local SSD or Spot
interruption risk. Grow working storage only after sample-count/peak-space review;
resize the stopped CPU VM for the next phase when its measured needs justify it.

Official USD list prices fetched 2026-10-13 (730-hour month for comparisons):

| Item | Running/ongoing rate | Behavior while VM stopped |
| --- | --- | --- |
| e2-standard-4 /16 GiB | $0.13402284/hour | Compute $0 |
| Alternative e2-standard-8 /32 GiB for later work | $0.26804568/hour | Compute $0 |
| One ephemeral external IPv4 | $0.005/hour while running | Released; $0 |
| 30-GiB standard boot | $1.20/month gross; potentially $0 under unused 30-GiB-month US allowance | Still provisioned/billable |
| 50-GiB balanced working disk | $5/month | Still $5/month |
| Same-region Standard bucket | $0.020/GiB-month gross; small US allowance up to 5 GB-month subject to aggregate limits | Stored/soft-deleted bytes continue accruing |
| Basic IAP to GCP | No IAP service fee | No IAP service fee |

Thus VM+IP is about **$0.139/hour**. The verified four-hour setup STOP policy
targets about **$0.56** compute/IP per start, plus about **$0.034** gross disk cost
over four hours. Provider termination can begin up to 30 seconds after the target
and stopping takes time; this is not a billing or remaining-credit hard cap.
Stopped disks are **$6.20/month gross**, or about $5 if the
boot-disk allowance is available; 5 GiB compact archive is $0.10/month gross.
Do not assume allowances are unused until the account inventory is checked.
Leaving this VM running for a 730-hour month is about **$101.49** compute/IP,
plus disks/archive/transfer/operations. No automatic deletion is proposed.
Owner approved this layout/recurring-storage exposure with a review **by 2027-01-10**.
This is not authorization for further compute, beyond-credit services, GPU or
scientific execution. The four-hour setup safety stop is a spending safeguard for this phase, not a
scientific-stage timeout. Set a deliberate future duration for real jobs.

[CPU rates](https://cloud.google.com/products/compute/pricing/general-purpose),
[disk rates](https://cloud.google.com/compute/disks-image-pricing),
[network/IP rates](https://cloud.google.com/vpc/network-pricing),
[storage/operation/transfer rates](https://cloud.google.com/storage/pricing),
[IAP pricing](https://cloud.google.com/iap/pricing),
[provider-side auto-stop](https://docs.cloud.google.com/compute/docs/instances/limit-vm-runtime).
Disk is charged by provisioned capacity, bucket by actual live/noncurrent/soft-deleted
storage. Prices exclude tax/currency conversion and any unrelated account usage.
The API verifies DKK billing currency; the USD list-price estimates are not a
DKK invoice or a fresh console estimate.

Inbound public downloads have no GCP ingress charge. Same-region bucket↔VM data
transfer has no transfer fee, while requests still have operation charges.
Select Standard network tier for the VM's internet egress: first 200 GiB/month
per account is free; then $0.085/GiB through 10 TiB at the consulted rate. Cloud
Storage has its own allowance/rates (100 GB US→eligible destinations; thereafter
about $0.12/GiB for ordinary internet transfer to Europe at the first tier).
These are distinct allowances, not unlimited downloads or a guarantee of $0.
Only compact setup data transfer is authorized now. Record large future transfers
before use; keep working data and archived outputs in the same region.

## Login and secure remote access

No connected browser or prior `gcloud` login was available at initial inspection.
Official Google CLI **589.0.0** is installed under ignored
`artifacts/gcp-workspace/tools/google-cloud-sdk/`. Its downloaded Mac x86-64
archive is 54,268,176 bytes, SHA256
`b49e8cb9d348267d46fade7b9c916a1aed7ce0ec07e142ce41cc0d24a95a9651`,
matching the official install page. `gcloud version`, no-account auth listing and
actual `compute instances create --help` ran locally. No cloud API was enabled at this initial inspection.
Credentials use an ignored owner-only configuration directory; never commit it
or include it in an archive. Local validation is not Linux installation proof.

Owner action, from Mac Terminal (normal Google login; no credentials in chat):

```bash
cd /Users/rasmusallesoeenielsen/Documents/dl_binner
CLOUDSDK_CONFIG="$PWD/artifacts/gcp-workspace/private-gcloud-config" \
  "$PWD/artifacts/gcp-workspace/tools/google-cloud-sdk/bin/gcloud" auth login
```

The owner completed this login and CLI auth now passes. Read-only APIs verify an
open billing account, billed My First Project and owner IAM role. Compute, IAP,
IAM and OS Login were subsequently enabled for the approved layout. Browser access
remains unavailable
to the tool even after owner enabled it/reset, so actual credit fields were supplied by the owner. The dedicated Browser tool
identified a concrete loader mismatch: it imports absent plugin
`26.930.61225/scripts/browser-service.mjs`, whereas installed plugin is
`26.1007.30912`. A supported Node reset/retry produced the same error. Vendor diagnostics confirm
Chrome running, extension installed/enabled and native-host manifest correct;
the failing chat-specific loader remains the concrete issue. Do not
modify vendor/native-host files or use raw cookies/CDP as a workaround; restart
ChatGPT/start a fresh chat with Chrome, or reinstall Browser through the app UI
if a fresh session still has the mismatch. This is distinct from Google login. No API key/JSON service-account key is
needed on the Mac. Do not replace credentials merely because a sandboxed GitHub
network probe failed: the authorized network probe verified the existing private
GitHub login successfully.

The dedicated `dl-binner` VPC / `dl-binner-us-central1` subnet (`10.50.0.0/24`)
allows only IAP's `35.235.240.0/20` to tcp22 on the `dl-binner-iap` VM tag. Private
Google access is enabled; there is no public SSH/HTTP rule. The project's default
network is unchanged. The ephemeral external IP permits outbound
apt/Git/CAMI access without NAT; it does not open inbound SSH. OS Login uses the
owner's dedicated Mac key outside Git. Guest attributes were
enabled before first boot, and authenticated Compute API host keys seed a dedicated
known-hosts file;
[Google's host-key guidance](https://docs.cloud.google.com/solutions/connecting-securely)
explains the trusted back channel. Verify host keys
through a trusted cloud/serial identity, not `StrictHostKeyChecking=no`. Prefer
an unprivileged working user; use sudo only for OS/disk setup. No default broad
Editor service account: if backup access needs an attached service account, grant
only bucket-specific object access and no key file. Do not grant project-wide
Storage Admin merely to copy archives.

The concrete **`dl-binner-gcp`** alias in the Mac's `~/.ssh/config` uses an absolute
`gcloud compute start-iap-tunnel ... --listen-on-stdin` ProxyCommand and the ignored
Google login configuration. `ssh dl-binner-gcp` passed with strict pinned host keys,
OS Login user `rasmus_allesoee_gmail_com` and a dedicated key. The host's Ed25519
fingerprint is `SHA256:EnphGEWw80eNITGEQcbIFyhdXS2dvuz1NhtW85x7h/4`. Disable agent
forwarding/password/root SSH. Do not start an
unauthenticated WebSocket app-server on the VM's public interface.

## Git and Codex app acceptance

The initial clean branch is `benchmark-planning` at
`2109998a230a0757be424e6f55c3a1bf17971ebe`. Live GitHub inspection verified
`Rasmus-allesoee/dl_binner` remains private; `origin/main` is
`5e54538d1799e8d2538621729400f33fbaf017b9`, and the benchmark branch was not remote
at entry. The owner authorizes a normal push of this working branch, preserving
all accepted commits; no force push, merge, visibility change or release.
Source-freeze commit **`440911904e8342c2f3a27254f95caa51871cf706`** was normally
pushed with upstream and cloned byte-identically onto the VM. Main remains
unchanged. Subsequent setup receipts must be normally pushed and synced before
handoff; the final verified Git state is reported in chat without a self-referential
commit hash inside its own committed receipt.

The VM uses a repo-specific **read-only deploy key** for cloning/fetching; no Mac
GitHub token was copied. Repo-local commit identity matches the existing Mac project. `/srv/dl_binner/repo` is a clean `benchmark-planning` clone
at the exact source-freeze SHA. Repo-local `core.sshCommand` pins GitHub host keys
and this key. Linux push rights are not configured; later authorization can use
a separately scoped choice. Keep environments under
`/srv/dl_binner/experiments/e009/envs/`, data/tmp/runs separately from the checkout,
and compact archives under `/srv/dl_binner/archive/`. Do not forge UCloud paths
or copy linked Mac environments to Linux.

Official **Codex 0.160.1** complete Linux package is installed at
`/srv/dl_binner/tools/codex-0.160.1`; `~/.local/bin/codex` is a wrapper preserving
that package's resource paths. Actual login-shell PATH, version and app-server help
pass. The 160,785,122-byte release archive passed SHA256
`340801565906a7028f6baaa9ab6853addaef221f0016a1417a7c1ffdd96c21f0`; its regenerable
download was removed after installation. Native image-supplied Google CLI is
588.0.0. Authenticate with the existing ChatGPT plan through device login or an
SSH-forwarded localhost callback; do not
silently switch to metered OpenAI API billing or copy a general auth cache to
Git/backup. App-server must remain SSH-managed/private.

**Authentication command** (owner completed it; status independently reports
`Logged in using ChatGPT`; no tokens/login codes in chat):

```bash
ssh -t dl-binner-gcp 'bash -lc "codex login --device-auth"'
```

For a future fresh login, complete the browser flow with the existing ChatGPT account. If device login is
blocked by an account setting, return the non-secret error; do not switch to a
metered API key. In the desktop app: **Settings → Connections → SSH → enable/add
`dl-binner-gcp`**, then choose `/srv/dl_binner/repo`. Start a chat there and run only
`pwd`, `git rev-parse HEAD`, `git status --short --branch`, and `uname -s`. Native
app controls are unavailable in this session, so this final acceptance observation
needs owner interaction.
[Official SSH workflow](https://learn.chatgpt.com/docs/remote-connections#connect-to-an-ssh-host),
[login](https://learn.chatgpt.com/docs/auth#login-on-headless-devices).

Acceptance needs two separate observations: (1) SSH reads exact HEAD and runs a
harmless shell command on Linux, and (2) a chat on the saved remote project runs
`pwd`, `git rev-parse HEAD`, `git status --short --branch`, and `uname -s` there.
A locally executed `ssh ...` or remote CLI `--version` alone is not verified app
workflow. Record raw small outputs/commit/runtime identity; no scientific test.
The next phase starts only after this actual connection and billing gate pass.

## Private archive and retention

The created bucket is **`gs://dl-binner-archive-167650584170/`**, regional Standard
in `us-central1`, uniform bucket-level access and **public access prevention enforced**. No public ACL/link, versioning,
Autoclass, Archive/Nearline minimum-duration fee, bucket lock or paid intelligence
feature. Keep default short soft-delete protection visible in stored-byte costs.
Use append-only uniquely named compact checksum-bound archives of accepted outputs
and diagnostic summaries; no whole-disk/environment snapshots or automatic copy
of raw reads/BAMs. An accepted input that cannot be reacquired needs explicit backup.

Phase-1 backup contains only harmless setup receipts/source commit/config summaries,
never `.ssh`, `.codex/auth.json`, `gcloud` databases, private keys, signed URLs,
GitHub tokens, machine credentials, inbox/history caches or numerical environments.
Upload it, read it back and compare SHA256/byte count; verify bucket IAM and public
access prevention. A future archive is not a backup until its readback succeeds.

The VM's own `dl-binner-archive` service account uploaded and read back the seven-member
setup archive at `workspace/20261013T220405Z/`: **6,126 bytes** compressed /15,748
logical archived bytes, SHA256 `2d88d5c0f1c2cf648f359b487135589e98d77556b1b918f8f3ea03b603a5295b`.
`cmp` and SHA256 pass; the checksum is the second object. The account has only
bucket-scoped Object Creator/Viewer, no project-wide role or JSON key.
Default soft delete is seven days; no public principals, versioning or Autoclass.
This backs up phase-1 setup evidence, not scientific outputs or authenticated app
state. Source history is on private GitHub; existing scientific assets were not migrated.

For accepted science retain final partitions/required checkpoints/evaluation,
axes/masks/exclusions, compact logs/metrics/provenance and exact regeneration input
identities. For obsolete failures retain exit causes/useful native diagnostic
snippets/config/hashes, then record and remove bulky regenerable outputs after
review. Do not delete accepted/irreplaceable evidence or old inaccessible UCloud
files. Do not retain all scratch/temp/failed BAMs by default. Only the newly
downloaded Codex installer was removed; no original research files were deleted.
Installed tools are about 447 MB logical, checkout 34.5 MB and the work disk has
about 461 MiB used, leaving its rest available; bulk E009 will need a new space review.

## VM start, stop and cost control

From the Mac checkout, use the isolated authenticated CLI. Start only for an
explicit task; each start recomputes the verified four-hour automatic STOP.
Both disks, source and login state persist. IAP uses the instance identity, so
an external IP change does not require replacing the SSH alias or host keys.

```bash
cd /Users/rasmusallesoeenielsen/Documents/dl_binner
CLOUDSDK_CONFIG="$PWD/artifacts/gcp-workspace/private-gcloud-config" \
  "$PWD/artifacts/gcp-workspace/tools/google-cloud-sdk/bin/gcloud" \
  compute instances start dl-binner-cpu \
  --project=project-d17bd588-df31-488f-b16 --zone=us-central1-a
```

After the job, use the same command with `stop` instead of `start`; inspect with
`compute instances describe dl-binner-cpu --project=... --zone=us-central1-a
--format='value(status)'` (the exact project is above). `TERMINATED` means stopped
in Compute Engine; the VM and disks have not been deleted. A stopped VM cannot
accept SSH; start it before the desktop remote project. Changing the four-hour
policy or CPU/storage allocation is a separate workload/cost decision.

Record actual running elapsed time and projected compute/IP/disk/bucket cost;
reported billing can lag and must be checked separately. Confirm what remains
billable while stopped. The approved credit-expiry review is **by 2027-01-10**;
no automatic billing-disable/data-destruction mechanism is assumed safe.

## Next phase

After phase 1 passes: inspect E009 v14 archive/checksum/terminal evidence, accept
success without replay, then decide **10 versus 20 read samples** using coverage
representativeness for the one-assembly design, peak working storage and USD cost.
Published multi-assembly/multi-sample gains do not determine the optimum here.
Freeze axes/protocol/cost before bulk acquisition/assembly/depth/truth, which will
run directly on the connected GCP VM under a separately authorized phase.
No full fits/scores or architecture comparison follows automatically.

If credits run out, assess **Google Colab** and **Kaggle Kernels** as possible future
compute options; neither is configured, enabled or used now.
