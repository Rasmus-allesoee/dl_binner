# D014: Google Cloud as the connected Linux research workspace

Date: 2026-10-13. Status: **accepted provider/durable workflow choice; initial layout/recurring storage approved by owner; provisioning not started**.

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
not verified balance. Check displayed scope/remaining/expiry, existing billing
and resources before any provisioning. Use only verified trial-credit-covered
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
  10/20-sample scope; provision based on the next actual peak/work budget.
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

First verify billing/credits and access, establish exact pushed commit/SSH/app
Linux command/private archive readback and stop the VM with costs recorded.
Then independently review v14 and choose 10/20 depth sources for one assembly,
with representativeness, actual quotas, storage and monetary budget together.
Revisit size/provider after measured workflow needs or credit constraints, not as
an architecture gate. No accepted science is repeated to migrate infrastructure.

Owner-approved storage/cost exposure on 2026-10-13 includes an expiry review by
2027-01-10; no extra scientific/GPU/cloud service spend is authorized by it.
