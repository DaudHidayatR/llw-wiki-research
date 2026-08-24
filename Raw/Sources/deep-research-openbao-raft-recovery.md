---
schema_version: 2
id: "source-deep-research-openbao-raft-recovery"
type: "source"
title: "Deep Research — OpenBao Raft Snapshot Backup and Recovery"
Author: "Hermes Deep Research"
Reference: "deep-research-job-5831a940"
SourceType: "web"
ContentType:
  - "markdown"
Published: "2026-08-24"
Captured: "2026-08-24"
Created: "2026-08-24"
Processed: true
tags:
  - "source"
ContentHash: "sha256:00800d6936226bb91ace00f6cab91cadb2eca6cc66238021728edbe2e3d6e351"
---

# Deep Research — OpenBao Raft Snapshot Backup and Recovery

## Normalized Content

For single-node OpenBao with Integrated Storage (Raft), `bao operator raft snapshot
save <file>` is the standard logical backup command and `bao operator raft snapshot
restore <file>` restores it. Snapshot operations are not available when Raft is
configured only as `ha_storage`. Add `sha256sum` checksums (OS-level integrity, not an
OpenBao guarantee). The exact semantics of `restore -force` and `restore -stage` are not
established by the retrieved documentation — check `bao operator raft snapshot restore
-help` and `bao version` for the installed version before relying on them.

A Raft snapshot is the OpenBao data stored in Integrated Storage at the snapshot point:
a logical, encrypted storage backup still subject to the seal/barrier model. It is
expected to restore policies, enabled auth methods, auth roles, KV secrets and metadata,
Transit keys/keyrings (as encrypted data), secret-engine mounts, and persistent token
records. It does NOT include server configuration, Kubernetes PVC/Flux state, an external
KMS/HSM key, or a Tailnet Lock external signer key unless deliberately stored in OpenBao
(which creates a recovery dependency). A snapshot is NOT a substitute for unseal or
recovery material.

Sealed/unsealed status is runtime process state, not portable snapshot property; after a
rebuild or restart, expect the process to begin sealed unless auto-unseal succeeds. A
snapshot is encrypted under the source cluster's barrier/seal hierarchy, so preserve the
original Shamir material or external seal dependency; do not assume initializing a new
cluster with unrelated keys makes an old snapshot recoverable.

Single-node Raft: 1 voter = quorum 1, tolerates 0 failures → external snapshots are the
only protection. Use the snapshot API rather than copying live Raft/BoltDB files.
Backups are ideally taken offline; a restore is destructive rollback (writes after the
snapshot are lost).

Storage path alignment: the Raft backend requires a storage `path`, a unique `node_id`,
and a `cluster_addr`; the Kubernetes volume must be mounted at the configured path. A
path/mount mismatch means OpenBao may use an empty container-local directory while the
PVC is unused. After a restore, verify peer state with `bao operator raft list-peers`;
`remove-peer` is hazardous on a one-node cluster (can destroy quorum) — snapshot first.
Differentiate path mismatch, node-ID mismatch, cluster-address mismatch, seal mismatch,
and version mismatch; diagnose before reinitializing (reinit over the wrong path can
create a second empty cluster).

Shamir unseal shares: initialization splits the unseal key into shares; the threshold
reconstructs it; each node must be unsealed after restart. Auto-unseal depends on an
external KMS/HSM and supplies recovery-key shares that CANNOT decrypt the root key and
cannot compensate for permanent loss of the external seal mechanism. For a homelab,
Shamir is usually the simpler disaster-recovery model; auto-unseal is justified only with
a genuinely independent and durable external seal service.

Proposed cadence: daily snapshot + pre-change (upgrades, seal changes, storage changes,
kind recreation) + post-change; retention 7 daily / 4 weekly / 3 monthly; snapshots
copied off-cluster to at least two failure domains; quarterly destructive restore drill.
OpenBao suggests external automation (cron, systemd, Kubernetes CronJobs) because
automated snapshots are not built in.

Rebuild order: kind → Flux prerequisites only (namespaces, storage, OpenBao CRDs/TLS/
PVC/workload — not secret-consuming apps) → validate PVC == Raft path → restore via
snapshot API (never file-copy into the Raft directory; never initialize a second cluster
over old data) → unseal → verify (recovery canary KV/policy/auth/Transit + pod-deletion
persistence) → external-secret controllers → tailnet-dependent workloads → apps. Use
Flux suspension or dependency ordering; add no new orchestration layer.

Tailnet Lock coordination: at least one recovery path must not depend on both OpenBao and
Tailnet Lock simultaneously. Keep an external signer and its key offline, reach OpenBao
over local Kubernetes networking / `kubectl port-forward` during recovery, and do not
store the sole Tailnet Lock signer private key only inside OpenBao.

## References

- https://openbao.org/docs/commands/operator/raft
- https://openbao.org/docs/internals/integrated-storage
- https://openbao.org/docs/configuration/storage/raft
- https://openbao.org/docs/platform/k8s/helm/examples/ha-with-raft
- https://openbao.org/docs/next/concepts/storage
- https://openbao.org/docs/concepts/seal

## Capture Notes

Consolidated from deep-research job 5831a940b05942fdaf378846bff3d6d9 (Phase 4, card 1/2).
Proposed runbook is not yet executed against the repo; a clean-room destructive drill is
required before treating the backup system as reliable. Repo-specific Raft path,
mountPath, node_id, seal config, and existing backup CronJobs must be inspected.
