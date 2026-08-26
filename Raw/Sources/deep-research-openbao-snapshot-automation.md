---
schema_version: 2
id: "source-deep-research-openbao-snapshot-automation"
type: "source"
title: "Deep Research — OpenBao Single-Node Raft Snapshot Automation"
Author: "Hermes Deep Research"
Reference: "deep-research-job-05f376ba"
SourceType: "web"
ContentType:
  - "markdown"
Published: "2026-08-26"
Captured: "2026-08-26"
Created: "2026-08-26"
Processed: true
tags:
  - "source"
ContentHash: "sha256:cb79224b3d859f351860af835b9b5b7474e230b6222deb963292d804a6b7946f"
---

# Deep Research — OpenBao Single-Node Raft Snapshot Automation

## Normalized Content

### Executive recommendation

For a single-node OpenBao deployment in Kubernetes: (1) run snapshot automation outside
Kubernetes, preferably a systemd timer on an independent management/backup host;
(2) authenticate with a dedicated, narrowly scoped snapshot token, not a root token;
(3) write each snapshot and SHA-256 manifest to temporary local storage, then copy to an
off-cluster destination; (4) prefer versioned/immutable object storage, with a
tailnet-accessible NAS as a reasonable homelab alternative; (5) retention 14 daily /
8 weekly / 12 monthly plus pre-change and drill-qualified snapshots; (6) separate the
identity that can create snapshots from the identity that can restore; (7) treat
`snapshot restore -force` as break-glass; (8) quarterly isolated restore drill with
preserved evidence. OpenBao strongly discourages single-server Raft (tolerates zero
failures); snapshots are DR, not availability — an odd-numbered multi-node Raft cluster
is the real availability improvement.

### Host systemd timer vs Kubernetes CronJob

Use a host-side systemd timer on a SEPARATE management/NAS/backup host. It survives loss
of the Kubernetes API server, scheduler, CNI, PVC, or OpenBao namespace; preserves
snapshots, scheduler config, job history, failure evidence, destination credentials, and
a recovery control point. A CronJob cannot start when the Kubernetes system that creates
it is unavailable and shares the OpenBao failure domain (API, scheduler, DNS, CNI, nodes,
storage, Secret, logs) — correlated failure. CronJob is acceptable only if the cluster is
itself resilient, snapshot data uploads directly off-cluster, no snapshot is retained in
cluster-local storage, credentials are separately recoverable, failures alert outside
Kubernetes, and cluster loss is an accepted automation outage. For a homelab, that
convenience rarely outweighs the shared failure domain. Prefer systemd timers over cron
(persistent catch-up, timeouts, exit status, journal, failure hooks). Schedule once daily
during a low-write period; avoid concurrent upgrades/sys mutations; set a suitable
BAO_CLIENT_TIMEOUT for snapshot size.

### Authentication

Separate identities: (1) snapshot exporter — can read/export raft snapshot, cannot
restore, cannot change policies/auth/mounts/Raft membership/seal; (2) restore operator —
held offline, issued only during recovery, human approval + audit. API: GET
/sys/storage/raft/snapshot (export), POST /sys/storage/raft/snapshot (normal restore),
POST /sys/storage/raft/snapshot-force (force restore, bypasses seal-key-match checks).
Never store a root token in automation (compromise of backup host = full compromise).
Prefer a dedicated export-only policy, periodic/renewable service token, short lifetime
with automated reauth, host credential file readable only by the service account, no
token in argv/history/unit-file/logs. Mount tokens from a Secret in Kubernetes but plan
recovery of policy/auth role/Secret. Validate the exact policy against the installed
release (Vault ACL examples must not be assumed to hold for OpenBao).

### Destination patterns

A successful command is not a durable backup until it leaves the OpenBao/Kubernetes
failure domain (3-2-1: multiple copies, two storage systems, one off-cluster).
Pattern A local dir — staging only; write temp name, digest, atomic rename. Pattern B
tailnet NAS — push protocol with write access only to a dedicated incoming area, enable
filesystem snapshots, read-only history, separate dataset, deny uploader delete, replicate
offsite; tailnet protects transport, not access control. Pattern C object storage
(preferred primary) — versioning, immutable retention/object lock, separate upload vs
retention-admin identities, server-side encryption, TLS, lifecycle matching retention,
second credential path for recovery, periodic inventory, MFA. Hybrid:
OpenBao → authenticated export → independent backup host → temp file + SHA-256 → tailnet
NAS → versioned object storage.

### Retention and ownership

Baseline: daily 14 copies; weekly 8; monthly 12; pre-change (upgrades/major sys ops)
until validated, at least 90 days; drill-qualified until replaced. ~1 year of history.
Define RPO (daily ≈ 24h lost writes) and RTO (measured by drill). Never promote a
snapshot until: command exited 0, file non-empty, SHA-256 manifest exists, remote upload
completed, remote size matches, digest verified, metadata records source + timestamp.
Ownership: snapshot schedule/job health = backup operator; export policy = OpenBao
admin; storage lifecycle = storage admin; restore approval = OpenBao owner/break-glass;
seal/recovery material = separate custodian; drill record = conductor. Credentials must
remain separate even in a one-person homelab.

### Integrity verification

SHA-256 verifies transfer integrity, not recoverability. Create digest after full write;
verify after transfer; store manifest beside snapshot and in an independent inventory.
Minimum metadata sidecar: filename, sha256, byte_size, UTC started/completed, source
cluster, source OpenBao version, source address, scheduler host, exit status, remote
destination, remote object version. No tokens/unseal/sensitive values in metadata.
The real integrity test is an isolated restore + semantic checks: `bao status` (active,
unsealed) and `bao operator raft list-peers` (expected single voter/leader, no stale
peers, indexes progress after a test write).

### Restore semantics

Normal restore (POST /sys/storage/raft/snapshot) performs consistency checks incl.
seal-key compatibility — use for rebuilding the same logical cluster. Forced restore
(POST /sys/storage/raft/snapshot-force; CLI `restore -force`) bypasses the seal-key-match
check — deliberate break-glass only when: normal fails on an understood mismatch,
snapshot + origin verified, original seal/recovery material available, destination seal
reviewed, rollback documented, drill demonstrated. Never the script default. `-stage`
semantics are NOT established in current OpenBao docs — do not copy Vault `-stage`
guidance; check the exact installed `bao operator raft snapshot restore -help` + `bao
version`; test the full staged workflow in isolation or use only normal/forced paths.
Restore with the same OpenBao version that created the snapshot; preserve source version,
image digest, config, plugins, seal config, TLS material. Restore is destructive rollback
— everything written after the snapshot is lost (KV versions, policies, tokens, auth
roles, identity, transit keys, mounts, audit, PKI, dynamic-secret config).

### Restore authorization and unseal

Break-glass model: routine automation exports only; app identities and workload service
accounts cannot restore; storage admins cannot restore just by reading files; restore
authority held by an OpenBao admin via a separate credential issued for the incident;
forced restore needs a second explicit decision. Preserve audit evidence outside the
restored Raft state (restore can roll back in-cluster audit config). Restoring storage
does not eliminate the seal model: Shamir needs the threshold of unseal shares; Auto
Unseal needs KMS/HSM/Transit config, credentials, network/DNS, TLS trust, recovery keys —
a snapshot without seal dependencies may be cryptographically intact but useless. Recovery
mode (separate facility, needs generated recovery token, reduces to one node) is for
start-failure, not ordinary restore. Production restore guardrails: declare incident +
freeze writes, capture final snapshot of damaged state if possible, preserve logs
off-cluster, record version + peer state, identify exact snapshot, verify checksum after
download, quantify rollback window, confirm seal material, decide normal vs forced, obtain
explicit approval for forced, restore in isolation first if possible, run semantic
validation before reopening, rotate credentials that rollback may have resurrected.

### Quarterly restore drill

Disposable isolated environment (no prod LB/DNS/email/certs/cloud mutations), same OpenBao
version, copied config with network addresses changed, real seal-recovery process. Pre-drill
record: drill ID/date, operator, snapshot timestamp + reason, storage location/version,
expected SHA-256, size, source + restore versions, expected RPO, seal type, recovery
dependency location, isolation controls, success criteria. Verify sha256sum after download.
Restore checklist: provision disposable instance, confirm version/config + no prod
traffic, normal restore (forced only if tested), unseal, `bao status` + `list-peers`,
confirm active leader/voter no stray peers, capture service logs, logical validation,
restart + verify unseal, delete pod + recreate against restored storage, confirm data
persists. Logical validation: KV canary (non-sensitive, predictable value/version;
write new disposable value; verify persists across pod deletion); policies (named policies
exist, representative contents match, allow test + deny test); auth roles (mounts enabled,
role config, safe test login, attached policies, denied out-of-scope); Transit keys
(exists, type/config, expected version, encrypt+decrypt new plaintext, decrypt safe
pre-snapshot ciphertext, min decryption version); Raft + pod-deletion persistence
(pre-snapshot canary + post-restore marker survive pod deletion; `list-peers` again);
optional mounts/audit/identity/PKI/db roles/plugins/seal/TLS/metrics. Evidence bundle:
restore-drill-<id>/ README, snapshot.sha256, checksum-verification.txt, openbao-version.txt,
restore-command-redacted.txt, service-startup.log, bao-status.txt, raft-list-peers.txt,
verification-results.md (table with Check/Expected/Result/Evidence), timing.csv, 
issues-and-actions.md. Redact tokens/unseal/recovery keys/secret values/plaintext/cloud
creds. Record timings for RTO measurement. PASS only if: retrievable, checksum matches,
documented restore works, seal works, active, peer state correct, canary readable,
policies/auth correct, transit works, survives pod deletion, no sensitive exposure, within
RTO. Any failure → owner + due date + retest before next quarter.

### Operational runbook

Daily: timer → snapshot temp name → check exit + size → sha256 → upload → verify remote
size/digest → record metadata → alert on failure → clean staging after remote verify.
Weekly: confirm newest backup within RPO, promote/tag weekly, inspect failures, check
destination capacity. Monthly: promote monthly, test retrieval of one object, verify
lifecycle/immutability, confirm config/plugins/seal instructions also backed up. Pre-upgrade:
on-demand snapshot, verify digest + upload, label with pre-change version, retain ≥90d.
Quarterly: isolated restore + full validation + measure RTO + retain redacted evidence +
remediate.

## References

- https://openbao.org/docs/internals/integrated-storage
- https://openbao.org/docs/commands/operator/raft
- https://openbao.org/docs/api/system/storage/raft
- https://openbao.org/docs/concepts/storage
- https://github.com/openbao/openbao-snapshot-agent
- https://openbao.org/docs/concepts/recovery-mode
- https://openbao.org/docs/configuration/storage/raft

## Capture Notes

Deep-research job 05f376bab30e4695bb86804bd8d7d75e (2026-08-26, model gpt-5.6-sol).
Primary OpenBao docs cited; `-stage` semantics explicitly unverified in current docs —
test against installed binary. Single-node Raft tolerates zero failures.