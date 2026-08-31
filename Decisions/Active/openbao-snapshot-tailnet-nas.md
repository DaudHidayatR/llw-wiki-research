---
schema_version: 2
id: "decision-openbao-snapshot-tailnet-nas"
type: "decision"
title: "OpenBao Raft Snapshot Destination — Tailnet NAS"
status: "active"
scope: "homelab-devsecops"
supersedes: []
superseded_by: []
related_wiki:
  - "concept-openbao-raft-recovery"
  - "synthesis-phase6b-snapshot-and-cni-research"
related_research:
  - "research-question-openbao-snapshot-automation"
created: "2026-08-31"
updated: "2026-08-31"
---

# OpenBao Raft Snapshot Destination — Tailnet NAS

## Decision

OpenBao Raft snapshots are written off-cluster to the Tailnet NAS, using its
read-only/snapshot-protected storage tier as the immutable destination.

## Context

The snapshot automation contract (research question
`research-question-openbao-snapshot-automation`, closed 2026-08-26) fixed the class —
off-cluster + immutable — and left the concrete destination as an implementation choice.
The class was decided; only the provider remained open. [[Wiki/Concepts/openbao-raft-recovery]].

## Why

A tailnet NAS is already present infrastructure, reachable over the tailnet without
public exposure, and its read-only snapshot tier gives the immutability property the
contract requires (ransomware/accidental-deletion resistant) without a new cloud bill.

## Alternatives Considered

Immutable object storage (S3/B2/R2 with versioning) — fully compatible with the
contract, chosen against only because the NAS already exists; decide-later placeholder —
rejected, the contract is ready to implement.

## Trade-offs

NAS availability depends on the homelab host being up — acceptable because the contract
already treats snapshots as DR, not availability, and an isolated restore drill is the
real recoverability test.

## Consequences

Implementation configures: independent-host systemd timer → `bao operator raft snapshot
save` → stage → SHA-256 → atomic rename → NAS upload (read-only tier) → verify size/digest;
retention 14d/8w/12m + pre-change ≥90d + drill-qualified; export/restore identity split.
Live restore drill sequenced after P0/P1 implementation.

## Revisit Condition

If the NAS tier cannot guarantee immutability (snapshots can be deleted by the same
credential), move to object storage with object-lock.

## Evidence Ledger

- Source: [[Raw/Sources/deep-research-openbao-snapshot-automation.md#Normalized Content]]
- Kanban: t_5317ffaa decision comment (2026-08-31, user review)
