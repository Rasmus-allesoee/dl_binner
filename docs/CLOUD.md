# Google Cloud workspace operations

Updated: 2026-10-13. [D014](decisions/D014-google-cloud-workspace.md) owns the
provider choice. [STATE](STATE.md) owns the next action; this guide owns setup,
access, cost and retention. **Preparation only: no GCP resources or authenticated remote session exist yet.**
Google CLI login and read-only project/billing checks pass. Owner confirmed the
current display: **kr1,973 remaining, kr0 used, expiry 2027-01-12**. This is an
owner-read display, not agent browser inspection. The owner approved the concrete layout and expiry review on 2026-10-13;
provisioning has not started yet. Do not treat the proposed names or costs as
allocated resources.

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

## Proposed initial layout and costs

Choose `us-central1` (Iowa), provisionally `us-central1-a`, subject to live quota
and capacity. CPU work on public simulated DNA does not presently need an EU-only
location. Iowa offers low E2 pricing and small US Free Tier storage allowances;
EU locations reduce interactive latency but raise costs/lose these allowances.
Co-locate VM and bucket to avoid cross-region transfers. This is not a data-residency
choice for future private clinical data.

Initial proposal: regular **e2-standard-4, 4 vCPU /16 GiB**, Ubuntu 24.04 LTS
(non-Pro, x86-64), **30-GiB pd-standard boot**, **50-GiB pd-balanced working disk**
mounted at `/srv/dl_binner`. This fits code/setup/small checks now, not bulk E009.
Balanced working storage provides better small-file/random-I/O behavior than a
tiny standard disk; the large UCloud copy problem is not a reason to recreate
snapshots here. Resolve/pin the actual Ubuntu image before creating the VM.
Record actual image/disk/machine descriptions afterward. Enable Shielded VM
features and preserve both disks on VM deletion. No GPU, local SSD or Spot
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

Thus VM+IP is about **$0.139/hour**. A proposed four-hour setup auto-stop bounds
compute/IP to **$0.557**, with about **$0.034** gross provisioned-disk cost over
those four hours. Stopped disks are **$6.20/month gross**, or about $5 if the
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
storage. Prices exclude tax/currency conversion and any unrelated account usage;
recheck the actual console estimate/billing currency before provisioning.

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
open billing account, billed My First Project and owner IAM role. Compute/IAP
APIs are not enabled; no mutation has occurred. Browser access remains unavailable
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

After account/cost verification, use a dedicated custom VPC/subnet with only
IAP's `35.235.240.0/20` allowed to port22 on the designated VM tag, private Google
access, and no public SSH/HTTP rule. The ephemeral external IP permits outbound
apt/Git/CAMI access without NAT; it does not open inbound SSH. Use OS Login with
owner-specific access and a local private key outside Git. Enable guest attributes
before first boot and retrieve the actual host public keys over the authenticated
Compute API to seed/verify a dedicated known-hosts file;
[Google's host-key guidance](https://docs.cloud.google.com/solutions/connecting-securely)
explains the trusted back channel. Verify host keys
through a trusted cloud/serial identity, not `StrictHostKeyChecking=no`. Prefer
an unprivileged working user; use sudo only for OS/disk setup. No default broad
Editor service account: if backup access needs an attached service account, grant
only bucket-specific object access and no key file. Do not grant project-wide
Storage Admin merely to copy archives.

Use `gcloud compute ssh --tunnel-through-iap` first; test OpenSSH from the Mac.
A concrete alias in `~/.ssh/config` can use a `gcloud compute start-iap-tunnel
... --listen-on-stdin` ProxyCommand (absolute CLI path and isolated config),
so the Codex app uses ordinary SSH without a public app-server port. Verify the
actual alias, user, key and host fingerprint rather than publishing placeholders
as a tested command. Disable agent forwarding/password/root SSH. Do not start an
unauthenticated WebSocket app-server on the VM's public interface.

## Git and Codex app acceptance

The initial clean branch is `benchmark-planning` at
`2109998a230a0757be424e6f55c3a1bf17971ebe`. Live GitHub inspection verified
`Rasmus-allesoee/dl_binner` remains private; `origin/main` is
`5e54538d1799e8d2538621729400f33fbaf017b9`, and the benchmark branch was not remote
at entry. The owner authorizes a normal push of this working branch, preserving
all accepted commits; no force push, merge, visibility change or release.
After documented checks/commit, push with upstream and verify the remote SHA.

On the VM, prefer a repo-specific **read-only deploy key** for cloning/fetching,
not a copy of the Mac's general GitHub token. Clone `benchmark-planning` under
`/srv/dl_binner/repo`; verify clean Git state and the exact pushed SHA. Later push
rights require a separate scoped choice. Keep environments under
`/srv/dl_binner/experiments/e009/envs/`, data/tmp/runs separately from the checkout,
and compact archives under `/srv/dl_binner/archive/`. Do not forge UCloud paths
or copy linked Mac environments to Linux.

Install a pinned official Codex CLI on Linux, make it available in the user's
**login shell PATH**, and authenticate with the existing ChatGPT account/plan.
Use documented device login or an SSH-forwarded localhost login callback; do not
silently switch to metered OpenAI API billing or copy a general auth cache to
Git/backup. App-server must remain SSH-managed/private.

In the ChatGPT desktop app: **Settings → Connections → SSH → add/enable the
concrete host alias**, then choose `/srv/dl_binner/repo`. Owner interaction may
be required because native app control is unavailable in this session.
[Official SSH workflow](https://learn.chatgpt.com/docs/remote-connections#connect-to-an-ssh-host),
[login](https://learn.chatgpt.com/docs/auth#login-on-headless-devices).

Acceptance needs two separate observations: (1) SSH reads exact HEAD and runs a
harmless shell command on Linux, and (2) a chat on the saved remote project runs
`pwd`, `git rev-parse HEAD`, `git status --short --branch`, and `uname -s` there.
A locally executed `ssh ...` or remote CLI `--version` alone is not verified app
workflow. Record raw small outputs/commit/runtime identity; no scientific test.
The next phase starts only after this actual connection and billing gate pass.

## Private archive and retention

Use a single regional **Standard** bucket in `us-central1`, uniform bucket-level
access and **public access prevention enforced**. No public ACL/link, versioning,
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

For accepted science retain final partitions/required checkpoints/evaluation,
axes/masks/exclusions, compact logs/metrics/provenance and exact regeneration input
identities. For obsolete failures retain exit causes/useful native diagnostic
snippets/config/hashes, then record and remove bulky regenerable outputs after
review. Do not delete accepted/irreplaceable evidence or old inaccessible UCloud
files. Do not retain all scratch/temp/failed BAMs by default. No files are being
deleted in this setup phase.

## Stop and next phase

Stop the VM when setup/app checks are finished and independently verify its stopped
state. Record actual running elapsed time and projected compute/IP/disk/bucket cost;
reported billing can lag and must be checked separately. Confirm what remains
billable while stopped. Set a credit-expiry review before the displayed deadline;
no automatic billing-disable/data-destruction mechanism is assumed safe.

After phase 1 passes: inspect E009 v14 archive/checksum/terminal evidence, accept
success without replay, then decide **10 versus 20 read samples** using coverage
representativeness for the one-assembly design, peak working storage and USD cost.
Published multi-assembly/multi-sample gains do not determine the optimum here.
Freeze axes/protocol/cost before bulk acquisition/assembly/depth/truth, which will
run directly on the connected GCP VM under a separately authorized phase.
No full fits/scores or architecture comparison follows automatically.

If credits run out, assess **Google Colab** and **Kaggle Kernels** as possible future
compute options; neither is configured, enabled or used now.
