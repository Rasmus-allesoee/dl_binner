# Google Cloud workspace operations

Updated: 2026-10-16 (Copenhagen; provisioning receipts are dated 2026-10-13 UTC).
[D014](decisions/D014-google-cloud-workspace.md) owns the provider choice;
[STATE](STATE.md) owns the next action; this guide owns access, costs and retention.
**E009's four unchanged controls completed; GCP is TERMINATED.**
[The reviewed result](../experiments/E009-competitive-benchmark/controls-review.json)
binds actual stage exits, archive/member checks, local diagnostics and costs.
Provider stop was **2026-10-15 22:55:19.426 UTC /October 16 00:55 Copenhagen**,
after 1.7542275 h; gross compute/IP~$0.479, export~$0.0542, under the separate $2.
No VM wake/resource change/retry/external tool ran in the local review. The current
policy remains 4.25 h/STOP/automaticRestart=false, but no next start is authorized.
Current Welcome credit **DKK1,936.57 Available through 2027-01-12**; reported
cost/savings 31.92/net0 still lag actual usage. Disks remain 30/300 GiB and cost
**$31.20/month while stopped**; retention review **October 21**, no extension.
Prepare one fixed-encoder marker-conflict splitting test, with separate cost and
execution approval if needed. Read-only GitHub access stays unchanged. Earlier
launch/one-hour/25-hour observations below are dated history, not active work.
**Phase 1 accepted: strict IAP SSH, exact private repository clone, pinned Linux
Codex CLI, ChatGPT authentication, actual desktop remote-project commands and
private archive upload/readback pass. The Ubuntu sandbox prerequisite was repaired
and the normal installed CLI sandbox passes.** See the
[structured receipt](evidence/gcp-workspace.json) for observations and hashes.

## Phase boundary and account verification

The completed phase 1 established a CPU Linux workspace, private backup and actual
Codex SSH access; it excluded v14 review and science. The first 2026-10-14 follow-up
accepted v14 and prepared the data stage locally. The **later owner message
authorizes the data-only phase at `5fec4e1`**, conditional on live credit/price/quota
admission: one full sample-0 assembly and ten ordered coverage sources. No binner
fit, score or architecture change is authorized. [D013](decisions/D013-first-comparative-benchmark.md)
replaces the mandatory shortlist with decisions that improve our own binner and
defers CompleteBin. [The phase receipt](../experiments/E009-competitive-benchmark/gcp-data-observed.json)
owns actual resource/execution outcomes. The owner's SDU login is deactivated;
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

### Live data-phase credit gate, 2026-10-14

The supported Chrome connection now reads the console; the earlier loader failure
is historical. Billing Overview shows **Paid account**. Credits shows the upgraded
Free Trial credit **Available**, **DKK1,972.04 remaining of DKK1,973.43**, starting
2026-10-13, ending **2027-01-12**, scope “Certain usage; see the terms for free trial”,
net-pricing application. The pre-upgrade row expired on 2026-10-13 and is not extra
credit. Overview reports DKK1.15 usage/DKK1.15 savings/DKK0 net for October 1–14;
credit consumption is DKK1.39. The UI explicitly warns costs may lag more than
24 hours: pending usage is not zero or precisely observable. Only this project is
linked to this billing account; the API found no running CPU allocation before
the phase, the existing 30/50-GiB disks and compact regional bucket. The known
small setup/storage exposure plus the bounded phase leaves ample credit margin.

Fresh official terms retain remaining Welcome credit after paid upgrade for the
original 90 days. Ordinary E2/non-premium Ubuntu/Persistent Disk/Standard Storage
and VPC/IP are eligible; no GPU, Marketplace, partner model, NAT or premium image
is needed. The existing Billing Catalog API was queried read-only with the existing
login, without creating an API key or enabling a service. Current DKK SKUs price
E2 core at **0.143478820/hour**, RAM **0.019231272/GiB-hour**, balanced disk
**0.657809999/GiB-month** and standard disk **0.263123999/GiB-month** beyond its
allowance. Account Pricing displays list prices in DKK, updated 2026-10-14.
Its quoted conversion is 6.5781 DKK/USD. IPv4's non-free rate is DKK0.032890499/hour;
current allowance tiers are not assumed available in the gross envelope.

At 8 CPU/32 GiB with 300-GiB work/30-GiB boot, the conservative 25-hour compute/IP
plus seven-day disk subtotal is about **USD14.01 /DKK92.13**, leaving the rest of
the **USD20 /DKK131.56** envelope for compact archive/operations/rounding. List
estimates are not invoices; current credits and allowances can reduce them.
The ongoing disks cost **USD31.20 /DKK205.24 per 730-hour month gross while stopped**.
That cost continues after day seven: review retention then; stopping alone does
not shrink capacity. Copy/restore to a smaller disk and deletion of accepted
evidence are separate decisions. Keep the 2027-01-10 expiry review.

The **300-GiB quota request is granted in the Compute API** (`SSD_TOTAL_GB=300`,
50 used before growth), case `a11cf91a-b76b-4c95-9f79-7dc7538f3611`. No extra service
or CPU quota was needed. The 300-GiB estimate excludes CompleteBin: the data-only
upper planning components are 232.29 GiB plus 25-GiB free reserve and filesystem
overhead. Reducing to 250 would save about USD1.15 over seven days while weakening
the reserve. Retain 300 and the complete data; no cost-driven DNA filtering.

[Official credit coverage](https://docs.cloud.google.com/free/docs/free-cloud-features?gclsrc=aw.ds),
[VPC prices/credit coverage](https://cloud.google.com/vpc/network-pricing?hl=en),
[localized public SKU method](https://docs.cloud.google.com/billing/v1/how-tos/catalog-api).

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
IAM and OS Login were subsequently enabled for the approved layout. At that
initial setup browser access remained unavailable despite the owner enabling it,
so credit fields were supplied by the owner. The old Browser tool identified a
concrete loader mismatch: it imported absent plugin
`26.930.61225/scripts/browser-service.mjs`, whereas installed plugin is
`26.1007.30912`. A supported Node reset/retry produced the same error. Vendor diagnostics confirm
Chrome running, extension installed/enabled and native-host manifest correct;
That loader failure was distinct from Google login; current supported Chrome
access succeeds in the data phase. Do not modify vendor/native-host files or use
raw cookies/CDP to recover a future browser failure. No API key/JSON service-account key is
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
GitHub token was copied. Repo-local commit identity matches the existing Mac project.
`/srv/dl_binner/repo` was cloned at the source-freeze SHA and subsequently synced
cleanly to `bde9fbf49c035286cae713799d48d7d55a3d87a5` for desktop acceptance.
Repo-local `core.sshCommand` pins GitHub host keys
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
app controls are unavailable in this session, so the owner performed this app action.
[Official SSH workflow](https://learn.chatgpt.com/docs/remote-connections#connect-to-an-ssh-host),
[login](https://learn.chatgpt.com/docs/auth#login-on-headless-devices).

Acceptance needs two separate observations: (1) SSH reads exact HEAD and runs a
harmless shell command on Linux, and (2) a chat on the saved remote project runs
`pwd`, `git rev-parse HEAD`, `git status --short --branch`, and `uname -s` there.
A locally executed `ssh ...` or remote CLI `--version` alone is not verified app
workflow. Record raw small outputs/commit/runtime identity; no scientific test.
The next phase starts only after this actual connection and billing gate pass.

**Observed acceptance, 2026-10-14 Copenhagen:** the owner returned
`/srv/dl_binner/repo`, exact HEAD `bde9fbf49c035286cae713799d48d7d55a3d87a5`, clean
`benchmark-planning...origin/benchmark-planning` and `Linux`. Independently inspected
native session metadata identifies `Codex Desktop`, CLI 0.160.1 and that remote
directory; the allowlisted four-command outputs agree. No chat messages or auth
cache were collected. The first sandboxed calls failed with
`bwrap: loopback: Failed RTM_NEWADDR: Operation not permitted`; the desktop retry
succeeded with escalation. Keep both observations: desktop access passed, while
ordinary sandbox operation needed a host prerequisite repair.

### Ubuntu sandbox prerequisite

The native kernel log attributes the failure to Ubuntu 24.04's AppArmor user-namespace
restriction. The official Codex documentation prescribes a system Bubblewrap and
the distro's scoped `bwrap-userns-restrict` profile. This host now has
`bubblewrap 0.9.0-1ubuntu0.3` and AppArmor tools/profiles
`4.0.1really4.0.1-0ubuntu0.24.04.8`. The following OS setup ran once; reuse the healthy
installation, and inspect any existing custom profile before changing it:

```bash
sudo apt-get update
sudo env DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
  bubblewrap apparmor-profiles apparmor-utils
sudo install -m 0644 /usr/share/apparmor/extra-profiles/bwrap-userns-restrict \
  /etc/apparmor.d/bwrap-userns-restrict
sudo apparmor_parser -r /etc/apparmor.d/bwrap-userns-restrict
```

The installed CLI's actual 0.160.1 contract is `codex sandbox -- COMMAND`, with no
`linux` subcommand. Its normal sandbox ran the same harmless four commands with
exit zero after this repair. `kernel.apparmor_restrict_unprivileged_userns` remains
**1**; no global sandbox/kernel restriction was disabled. This is native CLI proof
after repair, separate from the earlier actual desktop retry. The final sync
restarts the host, clearing the previous app-server's helper selection.
[Official Ubuntu prerequisite](https://learn.chatgpt.com/docs/sandboxing) and
[installed-version sandbox implementation](https://github.com/openai/codex/blob/rust-v0.160.1/codex-rs/linux-sandbox/README.md)
explain the system-helper selection and scoped profile.

## GitHub write-access recommendation

The VM's existing **read-only deploy key is sufficient for the next data phase**:
fetch the normally pushed source commit, run data work and retain outputs/logs on
the VM. No repository permission is changed in this preparation. ChatGPT/Codex
login and GCP OS Login do not confer GitHub push rights. Keep credentials outside
Git, research archives and terminal output.

If the owner wants direct VM pushes later, prefer a **separate fine-grained PAT**
limited to `Rasmus-allesoee/dl_binner`, Contents read/write +required Metadata read,
with an explicit short expiry (e.g. 30 days). Keep the current SSH key for fetch;
configure a separate HTTPS push transport and an owner-only memory/secure credential
helper. The owner creates/enters the token in a protected interactive session;
never paste it into chat, a Git remote URL or a logged shell command. Workflow
permission is a separate grant only if changing workflow files is actually needed.
Token presence is capability, not authorization to push/merge/publish on every task.

A **separate write-enabled deploy key** is a reasonable simple single-repository
alternative, and safer to revoke independently than converting the current read
key. It has no automatic expiry and grants repository write. Neither this key nor a
Contents-write PAT is branch-specific by itself; branch protections/rulesets
govern allowed pushes. A compromised VM/private key can exercise those rights.
GitHub explicitly recommends Apps for finer control; a private App's one-hour
installation tokens suit ongoing automation but require app/key/token-refresh
setup that this single-owner workspace does not presently need. SSH agent forwarding
would expose the owner's existing authority to the remote session and remains
disabled. A broad classic PAT or copied Mac authentication cache is unnecessary.

Recommendation now: **retain read-only**. Optional later direct-push choice:
**short-lived single-repo Contents-write PAT**, or a separate write deploy key if
its simplicity is preferred after accepting non-expiring write scope. Owner action
is choosing/creating that credential and approving its exact scope/revocation;
no action is required for read-only data execution itself. Do not create/register
keys, tokens, an App or an extra cloud secret service without that later direction.
[GitHub deploy-key comparison](https://docs.github.com/en/authentication/connecting-to-github-with-ssh/managing-deploy-keys),
[fine-grained PAT permissions/expiry](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens).

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

The separate acceptance checkpoint at `workspace/20261013T223943Z-acceptance/`
is **5,858 bytes** compressed /19,836 logical archived bytes, eight allowlisted
members, SHA256 `d6fc40d656b855e018091452faf433e4774ee2088a76c5760c2e06c9d9c9d0ca`.
Mac upload and byte/SHA256 readback pass while the VM is stopped. It retains the
actual desktop command metadata/outputs, repaired sandbox output, scoped OS
prerequisite and the first provider stop/cost checkpoint. The full live Codex
session, auth state and inbox are excluded. The initial archive is preserved.

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
explicit task and verify its approved allocation/runtime policy first. The initial
setup used four hours; the authorized data phase uses **25-hour automatic STOP**.
Each start recomputes the current policy; do not assume that 25 hours is the
approved duration of a future small task.
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
accept SSH; start it before the desktop remote project. Changing the policy or
CPU/storage allocation is a separate workload/cost decision.

Record actual running elapsed time and projected compute/IP/disk/bucket cost;
reported billing can lag and must be checked separately. Confirm what remains
billable while stopped. The approved credit-expiry review is **by 2027-01-10**;
no automatic billing-disable/data-destruction mechanism is assumed safe.

**Recorded setup checkpoint:** the first provider-confirmed stop is
2026-10-13 22:39:43.273 UTC (2026-10-14 Copenhagen); status `TERMINATED`, no external
IP. Start-to-stop elapsed is **2,643.825 seconds /44.064 minutes**, or **2.93758
allocated vCPU-hours**. At the consulted rates this is **$0.10210 VM/IP** plus
about **$0.00624 gross disks over the same elapsed period**, excluding tax/FX,
requests and any allowance discount. This is measured allocation priced at list
rates, not an invoice or a newly displayed remaining-credit balance. Disk billing
also continues during stopped time. A brief additional start synchronizes the
final records and verifies persistence; its provider timestamps and aggregate
allocation estimate are retained separately in the checksum-bound private
`workspace/20261013T223943Z-acceptance/final-sync-stop.json` receipt, reported after
the final stop. This avoids a committed record claiming its own Git hash.

The installed sandbox prerequisite and UUID mount configuration are persistent
OS settings. The source-sync restart checks the mount, exact clean Git HEAD,
ChatGPT login status and normal CLI sandbox; it does not repeat a scientific
runtime test. New GCP binner environments/native-scale execution remain unverified
and belong to the authorized scientific phase.

## Data-phase resources and later scope

V14 remains accepted without replay. The later owner message authorizes exact
prepared commit **5fec4e1d1700c64c4bdd9945bad4e116ade73c57**, normally pushed from
the Mac and cleanly fetched/fast-forwarded by the VM's read-only GitHub key.
[The phase receipt](../experiments/E009-competitive-benchmark/gcp-data-observed.json)
owns actual native/data status, provider timestamps, disk changes and costs;
[operations](../experiments/E009-competitive-benchmark/OPERATIONS.md) owns commands
and review boundaries. The older [preparation API snapshot](../experiments/E009-competitive-benchmark/gcp-preparation.json)
remains dated evidence of the initial 4 CPU/16 GiB, 30/50-GiB disks and 250-GiB quota.

Live credit/price admission and effective **SSD_TOTAL_GB=300** passed. The existing
Iowa VM was changed to **e2-standard-8/32 GiB**, existing work disk grown **50→300
GiB**, and existing ext4 filesystem expanded with `resize2fs`, **without formatting**.
Provider STOP was set to **25 hours before start**. SSH verifies eight CPUs,
33,646,948,352 memory bytes, glibc/architecture, the same UUID-backed mount and
clean exact source. No additional VM, GPU, service or GitHub write credential was
created. Full samples **0,2,3,4,6,9,10,11,14,17** use one full sample-0 assembly.
The complete independently owned pinned Linux data runtime and real tiny changed-
driver fixture pass. Runtime/fixture time is counted in the cumulative 24-hour
production allowance; 25-GiB free reserve and existing activity/RAM guards remain.
No new capacity, automatic retry, clock extension or data filtering is permitted.

Stopping compute preserves **USD31.20 /DKK205.24 per 730-hour month** of provisioned
boot/work disks, less any available allowances, plus actual bucket storage.
Review grown retention **by 2026-10-21**, then before **2027-01-10** credit expiry
review. Disk capacity cannot simply be shrunk. An approved smaller replacement
requires verified copy/restore and an explicit decision about accepted evidence.
No unapproved payment-card billing or automatic important-data deletion follows.

## Verified data exit and bounded review, 2026-10-15

The original E009 data driver failed only in final PAF parsing after all assembly/
ten BAM/depth stages completed. Its watchdog snapshot requested shutdown at
**09:29:52 UTC**; the control plane confirms **TERMINATED at 09:32:21.624 UTC /
11:32 Copenhagen**. First provider uptime was **13.179723 h**. A stop is not success;
[the reviewed experiment](../experiments/E009-competitive-benchmark/OPERATIONS.md#earlier-data-review-and-failed-dag-evidence-2026-10-15)
and its original receipts distinguish accepted feature data from then-unadmitted
truth. The separate [v2 admission](../experiments/E009-competitive-benchmark/truth-v2-admission.json)
now resolves that boundary locally without a new wake.

The owner's review request needed evidence on that stopped disk. Before wake,
current console/API checks verified **DKK1,952.79 available**, expiry **2027-01-12**,
paid billing, billing enabled, ordinary eligible resources and unchanged DKK SKU
rates. Reported October cost/savings were **DKK5.16/DKK5.16, net DKK0**; issued-credit
use was DKK20.64. These displays lag and are not a reconciled invoice or zero
pending usage. No extra service, IAM grant, quota, VM or disk was created.

The same 8-CPU/32-GiB VM was set to **one-hour STOP before wake**. The bounded
review ran **12:51:17.410–13:19:53.611 UTC /14:51–15:19 Copenhagen**, **0.4767225 h**,
without resizing, reinstalling or replaying the data DAG. Current API state is
**TERMINATED**, external IP absent, both **30/300-GiB** disks preserved with
`autoDelete=false`; its current provider maximum remains **3,600 seconds /STOP**.
The old boot-bound watchdog is not active on a new boot. Re-arm a suitable end-of-
phase stop only for an authorized future phase; never reuse the old PID binding.

Measured priced uptime gives **$3.5987 original +$0.1302 review = $3.7288 gross
compute/IP** before allowances/credits. Both running intervals total **13.656446 h /
109.251564 allocated vCPU-hours**; sampled native CPU is a different quantity.
Seven-day provisioned boot/work planning cost remains **$7.1803** at the conservative
730-hour conversion. The run/review plus seven-day disk subtotal is **$10.9091**,
before small archive/operations/export and well inside the **$20 data-only** cap.
Seven days is planned retention exposure, not all already-spent cash. The actual
phase invoice remains unavailable while billing catches up.

The exact private 246,936,673-byte archive has verified native upload/readback and
all member hashes independently verified on the Mac. Its ~0.230-GiB regional
Standard storage is **~$0.0046/month gross**. Raw reads, BAMs and environments stay
on working storage. The original production filesystem peak was **170.66 GiB**,
minimum sampled free **124.52 GiB**; the 25-GiB guard was not approached. A future
225–250-GiB data disk may suffice, but shrinking requires a new approved copy/
verification/capacity plan; no resource change or bulk-data deletion ran here.

Stopped provisioned disks still cost **$31.20/month gross**. Review retention by
**2026-10-21** and credit expiry by 2027-01-10. No retention extension or post-credit
card spending is authorized. A later proposed **$2 diagnostic-fit ceiling** is
separate from the data-only $20 and remains unapproved; no external fit is the
immediate next step. CLOUD does not authorize any scientific action from a low
monetary estimate alone.

No binner fits/scores are authorized. [D013's later recommendations](decisions/D013-first-comparative-benchmark.md)
prioritize our unchanged diagnostic controls and at most one resource-admitted
SemiBin2 reference; MetaCAT core is conditional on a useful grouping question.
SCGBinner/COMEBin full runs and **CompleteBin are deferred**, with architecture
ideas and accepted contracts preserved. A future CompleteBin run could require
400–500-GiB work/64–128-GiB RAM, but that is an unapproved source-derived possibility,
not the next provisioning step. Reassess measured input/peak costs and live prices
only when its incremental evidence justifies a run. Native CPU availability and
50 epochs do not imply affordability. Healthy GCP prefixes persist while stopped.

If credits run out, assess Colab/Kaggle as future alternatives; neither is
configured or used. Do not silently charge the card or delete accepted evidence.

## Unchanged-control launch observation, 2026-10-15 (completed October 16)

The existing eight-CPU VM started at **21:10:04.207 UTC**, with 30/300-GiB disks
and no resize/provisioning/service/IAM changes. Fresh paid-account credit check
shows **DKK1,942.67 Available through 2027-01-12**; reported usage/savings27.89, net0,
with pending usage not assumed zero. Fresh SKUs price gross compute/IP at
**$0.273045676/h**, max4.25h **$1.160444124**, within the separate approved **$2**.
Existing storage remains within its October 21 retention review, ~$31.20/month gross.
The truth evidence archive now has a private upload and verified SHA256 readback.

The VM is clean at **cf7bf2a17eab0c5a2f70999d04e766af1e14f98a**; its GitHub key
remains read-only. Initial IAP connection preceded SSH readiness; serial boot
completion was checked before connecting, and no scientific command was retried.
Native mount/8 CPU/basePython3.12 and148.2-GB free-space checks pass. Fresh control
env owns its numeric dependencies; actual source/default/inventory/import/CLI gates
pass. Latest snapshot is live ten-depth feature preparation with ~1 CPU native
work and no failure. It is not a completed fit or a quality result.

The root systemd watcher pins boot63cf3041-14ae-4ce2-82f8-5a1df18e8abc /PID1975,
start tick27468 and exact command hash, every30s with60s exit grace. Live/normal0/
crash7 native detection tests pass without host shutdown. Its timer is active only
for this boot. The service also has a boot-relative four-hour cgroup runtime bound;
provider4.25h STOP/automaticRestart=false remains independent. Hard phase/provider
ends are **October 16 01:10/01:25 UTC =03:10/03:25 Copenhagen**. The held parent was
released only after actual watcher verification. It archives/readbacks completed
results and compact status, then exits to trigger shutdown. Do not stop active
science merely because this chat ends. Do not wait/poll until completion; owner
will request inspection later. Guest attribute `e009-controls/status` and private
completion URI are pointers, not substitutes for actual stage/artifact review.
