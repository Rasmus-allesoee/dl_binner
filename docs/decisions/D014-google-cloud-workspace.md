# D014: Google Cloud as the connected Linux research workspace

Date: 2026-10-13; preparation amendment: 2026-10-14; acceptance: 2026-10-14 Copenhagen. Status: **accepted; phase-1 infrastructure, private backup and actual Codex desktop SSH project verified**.

## Problem and decision

The owner no longer has a functioning SDU login. UCloud data are reported intact
but inaccessible; its remaining core-hour/storage allowance is not available to
this project. Repeated owner-transfer debugging also hid the actual Linux runtime
from agents. Select GCP as the main cloud provider and a private GitHub-synced,
SSH-connected persistent CPU Linux workspace that Codex can operate within each
explicitly authorized phase. Keep macOS for cheap local work.

[Cloud operations](../CLOUD.md) owns the concrete staged setup/cost/retention guide.
Phase 1 excludes E009 v14 return review, acquisition, all binner installs/fits and
scores. Paid billing and expected USD300/2027-01-12 credit expiry are owner reports,
distinct from the later owner-read kr1,973 remaining/kr0 used display. API billing
status/currency, quota and resources were independently checked before provisioning;
this session could not read the browser display because of a stale plugin loader.
Use only verified trial-credit-covered
products; stop and ask about ambiguous/uncovered/beyond-credit costs.

Owner-approved initial layout: Iowa e2-standard-4 /16 GiB with small separate boot/balanced working disks,
private same-region Standard bucket, IAP-only SSH and an outbound ephemeral IP.
Increase CPU/storage only after the next workload/sample-count decision. No GPU,
public app-server, broad default service account, new orchestration framework,
whole-environment snapshot or automatic paid-cloud spending is implied.

## Alternatives and reasons

- Continue UCloud: currently impossible; preserve evidence/locators without deletion.
- Browser-only Cloud Shell: its small home disk/ephemeral compute is unsuitable as
  the persistent scientific workspace; CLI/browser login can still aid setup.
- Large VM/GPU/terabyte disk now: not justified by setup or the unsettled E009
  then-unsettled 10/20-sample scope; provision based on the next actual peak/work budget.
- No external IP plus NAT: secure but adds a paid gateway and complexity just for
  package/public-read downloads. IAP-restricted inbound plus ephemeral outbound IP
  is simpler; no public SSH firewall is created.
- EU region: lower interactive latency, but higher prices/no small US storage
  allowance. Public simulated DNA currently has no EU residency constraint; revisit
  if latency materially harms usability or future data terms require it.
- Colab/Kaggle: possible future options after credit exhaustion, not configured now.

## Evidence, retention and consequences

Official credit rules, CPU/disk/IP/storage/IAP prices, runtime-limit and SSH docs
were consulted 2026-10-13 and linked in CLOUD. Actual account/VM/app evidence must
be recorded separately. Source history is preserved by normal commit/push of
`benchmark-planning`; no force push, main merge or visibility/publication change.
UCloud instructions are [archived](../history/UCLOUD_OPERATIONS.md); original
experiment records/receipts remain canonical and cannot become GCP run receipts.

Retain irreplaceable inputs and accepted final evidence; checksum/readback compact
private backups. Capture useful failure evidence, then prune obsolete regenerable
bulk after recording what is removed. Whole failed outputs and disk/environment
snapshots are not default backups. Credentials never enter Git or archives.
Stopping a VM stops compute/IP charges but leaves provisioned storage costs.
Expiry/credit exhaustion is an explicit financial review, not a reason to silently
charge the card or automatically delete important data.

## Revisit and next action

Billing/approved layout, strict SSH, exact pushed source-freeze clone, complete
pinned Linux Codex PATH/help and private archive readback pass. ChatGPT
authentication and the actual desktop remote-project Linux command test pass.
Owner-returned output agrees with independently inspected native session metadata
and the four allowlisted command outputs at clean commit
`bde9fbf49c035286cae713799d48d7d55a3d87a5`. An initial AppArmor/Bubblewrap failure is
retained; the official Ubuntu prerequisite repaired the normal CLI sandbox while
leaving global kernel protections enabled. CLOUD/receipt distinguish desktop
retry proof from the subsequent native CLI check. Final records are normally
pushed/synced; unused compute is stopped, preserving both disks and login state.

The 2026-10-14 preparation independently accepts v14 without replay and chooses
ten first-listed subject samples 0,2,3,4,6,9,10,11,14,17 for one sample-0 assembly.
[E009 operations](../../experiments/E009-competitive-benchmark/OPERATIONS.md) owns
the locally tested data stage and proposed 8 CPU/32 GiB, 300-GiB work disk,
24-hour driver/25-hour provider STOP, $20 run plus seven-day storage envelope.
Current quotas (12 total CPU, 24 E2 regional, 250-GiB balanced/SSD) permit the CPU change but require disk quota >=300 GiB; no
VM/start/provisioning/service mutation or bulk data/scientific work ran now.
Displayed credit scope/balance/pending usage and owner resource/retention approval
remain mandatory before execution. Existing read-only GitHub access suffices;
CLOUD records a separate expiring Contents-write credential as the later direct-
push preference, with permanent write deploy key/App alternatives. No permission
changed. Old UCloud command/budget details now live only in history; durable
storage/startup lessons stay available without requiring GCP snapshots.
Revisit size/provider after measured workflow needs or credit constraints, not as
an architecture gate. No accepted science is repeated to migrate infrastructure.

Owner-approved storage/cost exposure on 2026-10-13 includes an expiry review by
2027-01-10; no extra scientific/GPU/cloud service spend is authorized by it.
