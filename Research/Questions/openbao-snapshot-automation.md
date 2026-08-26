---
schema_version: 2
id: "research-question-openbao-snapshot-automation"
type: "research-question"
title: "OpenBao Snapshot Automation Contract"
status: "closed"
priority: "high"
related_wiki:
  - "concept-openbao-raft-recovery"
  - "synthesis-phase6b-snapshot-and-cni-research"
created: 2026-08-24
updated: 2026-08-26
---

# OpenBao Snapshot Automation Contract

## Question

What is the exact automation contract for OpenBao Raft snapshots: destination, retention,
scheduling owner, integrity validation, restore authorization, and quarterly drill
evidence?

## Resolution (2026-08-26)

Resolved with researched recommendations (see
[[Wiki/Synthesis/phase6b-snapshot-and-cni-research]] and
[[Raw/Sources/deep-research-openbao-snapshot-automation]]):

- **Scheduling owner**: systemd timer on an independent backup host (not a Kubernetes
  CronJob — correlated failure domain).
- **Destination**: versioned/immutable object storage, or a tailnet NAS with read-only
  snapshots; never a sole cluster-local path.
- **Retention**: 14 daily / 8 weekly / 12 monthly / pre-change (≥90d) / drill-qualified;
  owner roles assigned (backup operator / OpenBao admin / storage admin / break-glass).
- **Integrity**: SHA-256 manifest + `bao status` + `bao operator raft list-peers` after
  restore; an isolated restore is the real recoverability test.
- **Restore authorization**: export/restore identity split; break-glass restore with human
  approval; `-force` deliberate (bypasses seal-key checks); `-stage` semantics unverified —
  test the installed binary.
- **Quarterly drill**: isolated env, full semantic checklist, redacted evidence bundle
  measuring RTO.

## Why It Matters

The repo currently backs up only file-based metadata (`.runtime-backups/openbao`), not
`bao operator raft snapshot save`. A single-node Raft cluster tolerates zero failures, so
the snapshot contract is the only real protection against data loss. The recommendations
above give a concrete, primary-source-backed contract to implement. [C-001]

## What Remains

Implementation (applying the contract to the repo), plus live-cluster testing of `-stage`
semantics and real restore behavior — tracked in
[[Research/Open/live-cluster-verification]]. Single-node Raft remains DR, not
availability; an odd-numbered multi-node cluster is the availability upgrade.

## Evidence Ledger

- C-001 | confidence=high | The current repo backup is file-metadata only (not snapshot API); the researched contract (systemd timer on independent host, export-only token, versioned off-cluster destination, 14d/8w/12m+pre-change retention, export/restore split, break-glass force, quarterly drill) is now documented and ready to implement.
  - source: [[Raw/Sources/deep-research-openbao-snapshot-automation.md#Normalized Content]]