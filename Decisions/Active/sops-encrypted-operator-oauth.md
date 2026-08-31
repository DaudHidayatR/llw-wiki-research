---
schema_version: 2
id: "decision-sops-encrypted-operator-oauth"
type: "decision"
title: "SOPS-Encrypted operator-oauth Secret in Git"
status: "active"
scope: "homelab-devsecops"
supersedes: []
superseded_by: []
related_wiki:
  - "concept-tailscale-operator-helm"
  - "synthesis-flux-tailscale-redesign"
related_research: []
created: "2026-08-31"
updated: "2026-08-31"
---

# SOPS-Encrypted operator-oauth Secret in Git

## Decision

The Tailscale `operator-oauth` Secret (`client_id`/`client_secret`) is stored
SOPS-encrypted in Git and decrypted at bootstrap. No plaintext Secret anywhere in the
repository.

## Context

Phase-1 research flagged that Tailscale OAuth credentials are durable API credentials
and that a plaintext committed Secret triggers GitHub secret-scanning (real leak risk).
The original audit stance ("bootstrap-only Secret, no SOPS") is superseded by this
decision — recorded on kanban cards t_3d1e6633 and t_d0ad0e1e (2026-08-31 user review).
[[Wiki/Concepts/tailscale-operator-helm]].

## Why

Removes the plaintext-credential exposure while keeping the bootstrap-only lifecycle:
one-time creation, encrypted at rest in Git, decrypted during cluster bootstrap.

## Alternatives Considered

Plaintext bootstrap Secret (rejected — leak risk); external secret store (rejected —
overkill for the homelab per research).

## Trade-offs

Adds SOPS (age key) to the bootstrap toolchain and a key-custody responsibility on the
host. Accepted as the cost of not committing live credentials in cleartext.

## Consequences

Bootstrap gains a `sops` decrypt step; `.sops.yaml` creation rules scope the encrypted
file; the age private key lives off-cluster with the other recovery material and is
needed for rebuilds (add to the recovery/teardown inventory).

## Revisit Condition

If SOPS custody becomes a recurring operational burden, re-evaluate an external secret
store — but never revert to plaintext.

## Evidence Ledger

- Source: [[Wiki/Concepts/tailscale-operator-helm]] (Secret contract, durable-credential risk)
- Kanban: t_d0ad0e1e consolidated findings (correction #4) + t_3d1e6633 decision comment (2026-08-31)
