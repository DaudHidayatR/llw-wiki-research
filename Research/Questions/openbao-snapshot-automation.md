---
schema_version: 2
id: "research-question-openbao-snapshot-automation"
type: "research-question"
title: "OpenBao Snapshot Automation Contract"
status: "open"
priority: "high"
related_wiki:
  - "concept-openbao-raft-recovery"
created: 2026-08-24
updated: 2026-08-24
---

# OpenBao Snapshot Automation Contract

## Question

What is the exact automation contract for OpenBao Raft snapshots: destination, retention,
scheduling owner, integrity validation, restore authorization, and quarterly drill
evidence?

## Why It Matters

The repo currently backs up only file-based metadata (`.runtime-backups/openbao` —
root-token.txt + metadata), not `bao operator raft snapshot save`. A single-node Raft
cluster tolerates zero failures, so the snapshot contract is the only real protection
against data loss. [C-001]

## Existing Knowledge

[[Wiki/Concepts/openbao-raft-recovery]] documents the runbook (daily + pre/post-change,
retention 7d/4w/3m, off-cluster storage, quarterly drill) but the contract decisions
(destination, retention, scheduling owner, integrity, restore auth, drill evidence) are
not yet made or implemented. [C-001]

## Unknowns

Whether snapshots should be scheduled by a Kubernetes CronJob (needs OpenBao token +
kubectl access inside cluster) or host cron; where off-cluster storage lives; who may
authorize a restore; how drill evidence is recorded.

## Evidence Ledger

- C-001 | confidence=high | The repo has no snapshot-API backup today (file metadata only); the recovery runbook contract decisions remain open.
  - source: [[Raw/Sources/deep-research-phase6-verification.md#Normalized Content]]