---
schema_version: 2
id: "concept-tailnet-lock-rebuilds"
type: "concept"
title: "Tailnet Lock — Signing for Ephemeral kind Rebuilds"
topics:
  - "tailscale"
  - "homelab-devsecops"
aliases:
  - "tailnet lock"
status: "active"
confidence: "high"
sources:
  - "https://tailscale.com/kb/1226/tailnet-lock"
  - "https://tailscale.com/kb/1085/auth-keys"
source_count: 3
related:
  - "concept-tailscale-operator-helm"
  - "project-homelab-devsecops-research"
relationships:
  - "part-of|project-homelab-devsecops-research"
supersedes: []
superseded_by: []
last_verified: "2026-08-24"
review_after: "2026-11-24"
created: 2026-08-24
updated: 2026-08-24
---

# Tailnet Lock — Signing for Ephemeral kind Rebuilds

## Definition

Tailnet Lock requires every new Tailscale node key to be signed by a trusted Tailnet
Lock signing key, protecting against unauthorized node insertion via a compromised
coordination plane. Private signing keys stay on trusted customer-controlled nodes.
[C-001]

## What a kind Rebuild Changes

A destroyed kind cluster recreates the operator Pod (+ potentially its state), ingress
proxy Pods and their state Secrets, and — if persistent state is not restored — the
Tailscale node identities themselves. New identities have new node keys; under Tailnet
Lock they must be signed before becoming trusted participants.

## Option 1: Explicit Signing (recommended for occasional rebuilds)

A trusted signing node approves each replacement via a signing link or
`tailscale lock sign`.

- **Pros:** human approval for every replacement node; no reusable enrollment
  credential stored in the cluster; limits blast radius of a compromised Kubernetes
  Secret; best fit for occasional homelab rebuilds. [C-001]
- **Cons:** every recreated operator/proxy identity may need intervention; rebuild
  cannot complete unattended; multiple exposed workloads = multiple new proxy
  identities.

## Option 2: Pre-signed Auth Keys (only for unattended rebuilds)

Auth keys can be one-off/reusable, ephemeral, tagged, pre-approved, and pre-signed for
Tailnet Lock. A pre-signed key allows automated enrollment without separately signing
each resulting node. [C-002]

- **Pros:** unattended cluster recreation; no repetitive manual signing; can assign a
  restricted tagged identity; ephemeral nodes auto-remove after going offline.
- **Risks:** a reusable pre-signed key is a high-value credential; anyone with it can
  enroll nodes within its tag/validity; revoking the key does not remove already-enrolled
  devices; long-lived keys undermine per-node signing control.
- **If used:** narrowest tag + ephemeral where compatible + shortest practical
  expiration + non-plaintext Secret + rotation after rebuilds + separate credentials per
  workload.

## ⚠️ Operator Distinction (critical)

The operator's Helm auth is the **OAuth Secret** (`client_id`/`client_secret`) used to
call the Tailscale API and manage auth material for its nodes/proxies. A pre-signed auth
key is **NOT a drop-in replacement** for the operator OAuth Secret. Before designing
unattended Tailnet Lock enrollment, verify which operator-managed identities can consume
pre-signed keys in the pinned operator release. [C-001][C-002]

## State Retention vs Recreation

Retaining the operator's Kubernetes state Secrets across ordinary Pod restarts is
preferable to recreating identities unnecessarily. A full destructive kind rebuild is
different: if state is destroyed, expect new identities.

## Recovery Safety

Tailnet Lock initialization generates **disablement secrets** — at least one must be
stored **outside** the protected cluster. If the only trusted signing node and recovery
material live inside an ephemeral kind cluster, cluster loss becomes a tailnet-recovery
problem. Safe arrangement: ≥2 trusted signing nodes, ≥1 signer outside Kubernetes,
disablement secrets offline or in a separate secure vault, no sole dependency on a
frequently-reinstalled laptop or cluster. [C-001]

## Homelab Recommendation

Keep explicit `homelab tailscale sign` for occasional rebuilds. Confirm ≥1 signer +
disablement secret exists OUTSIDE the kind cluster before relying on a
destroy-recreate workflow. Normal-path generated-identity restore can be de-emphasized
(operator state retainable across restarts), but full destructive rebuilds need either
explicit re-signing (recommended) or a carefully scoped pre-signed key.

## Evidence Ledger

- C-001 | confidence=high | Tailnet Lock requires signed node keys; disablement secrets; signing options; pre-signed key caveats.
  - source: https://tailscale.com/kb/1226/tailnet-lock , https://tailscale.com/kb/1230/tailnet-lock-whitepaper
- C-002 | confidence=high | Auth key types incl. pre-signed; ephemeral; revocation semantics; not a substitute for operator OAuth.
  - source: https://tailscale.com/kb/1085/auth-keys