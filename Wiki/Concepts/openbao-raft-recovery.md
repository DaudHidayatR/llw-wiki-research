---
schema_version: 2
id: "concept-openbao-raft-recovery"
type: "concept"
title: "OpenBao Raft Snapshot Backup and Recovery"
topics:
  - "homelab-devsecops"
  - "openbao"
aliases: []
status: "active"
confidence: "high"
sources:
  - "Raw/Sources/deep-research-openbao-raft-recovery.md"
source_count: 1
related:
  - "concept-openbao-policy-reconcile"
  - "project-homelab-devsecops"
relationships:
  - "related-to|concept-openbao-policy-reconcile"
supersedes: []
superseded_by: []
last_verified: "2026-08-24"
review_after: "2026-11-24"
created: 2026-08-24
updated: 2026-08-24
---

# OpenBao Raft Snapshot Backup and Recovery

## Definition

For single-node OpenBao with Integrated Storage (Raft), `bao operator raft snapshot
save <file>` / `restore <file>` are the standard commands; add `sha256sum` checksums. The
exact semantics of `restore -force` and `restore -stage` are not established by the
retrieved documentation — check `-help` for the installed version before relying on them.
[C-001]

## Snapshot Contents and Seal Model

A Raft snapshot is the encrypted OpenBao storage state (policies, auth methods/roles, KV
secrets, Transit keys as encrypted data, secret-engine mounts, persistent token records);
it does NOT include server configuration, PVC/Flux state, an external KMS key, or a
Tailnet Lock signer key. A snapshot is NOT a substitute for unseal/recovery material.
Sealed/unsealed is runtime state, not restored; preserve the original Shamir shares or
external seal dependency. Single-node Raft tolerates zero failures, so external snapshots
are the only protection; use the snapshot API, never file copies of live Raft/BoltDB
files. [C-001]

## Recovery Runbook

Cadence: daily + pre-change + post-change snapshots; retention 7d/4w/3m; off-cluster
storage in ≥2 failure domains; quarterly destructive drill. Rebuild order: kind → Flux
prerequisites only (not secret-consuming apps) → validate PVC == Raft path → restore via
snapshot API (never file-copy; never reinitialize over old data) → unseal → verify
(recovery canary KV/policy/auth/Transit + pod-deletion persistence) → external-secret
controllers → tailnet-dependent workloads → apps. Diagnose (path vs node-ID vs
cluster-addr vs seal vs version mismatch) before reinitializing. [C-001]

## Tailnet Lock Coordination

At least one recovery path must not depend on both OpenBao and Tailnet Lock
simultaneously: keep an external signer and its key offline, reach OpenBao over local
Kubernetes networking / `kubectl port-forward` during recovery, and do not store the sole
Tailnet Lock signer private key only inside OpenBao. [C-001]

## Evidence Ledger

- C-001 | confidence=high | Raft snapshot save/restore is the standard backup path (restore -force/-stage semantics unverified); snapshots are encrypted storage state, not unseal material; single-node Raft needs external snapshots; the runbook uses snapshot API restore, PVC/Raft-path alignment, recovery canary verification, and a Tailnet Lock signer outside OpenBao.
  - source: [[Raw/Sources/deep-research-openbao-raft-recovery.md#Normalized Content]]
