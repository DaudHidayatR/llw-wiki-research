---
schema_version: 2
id: "concept-tailnet-lock-rebuilds"
type: "concept"
title: "Tailnet Lock — Signing for Ephemeral kind Rebuilds"
topics:
  - "homelab-devsecops"
  - "tailscale"
aliases: []
status: "active"
confidence: "high"
sources:
  - "Raw/Sources/deep-research-tailnet-lock.md"
source_count: 1
related:
  - "concept-tailscale-operator-helm"
  - "project-homelab-devsecops"
relationships:
  - "related-to|project-homelab-devsecops"
supersedes: []
superseded_by: []
last_verified: "2026-08-24"
review_after: "2026-11-24"
created: 2026-08-24
updated: 2026-08-24
---

# Tailnet Lock — Signing for Ephemeral kind Rebuilds

## Definition

Tailnet Lock requires every new Tailscale node key to be signed by a trusted Tailnet Lock
signing key, protecting against unauthorized node insertion via a compromised
coordination plane. [C-001]

## What a kind Rebuild Changes

A destroyed kind cluster recreates the operator Pod (and potentially its state), ingress
proxy Pods and their state Secrets, and — if persistent state is not restored — the
Tailscale node identities. New identities have new node keys; under Tailnet Lock they must
be signed before becoming trusted. [C-001]

## Explicit Signing vs Pre-signed Auth Keys

Explicit signing (a trusted signing node approves each replacement) provides human
approval, no reusable enrollment credential stored in the cluster, limited blast radius,
and best fits occasional homelab rebuilds; it cannot complete unattended and every
recreated identity may need intervention.

Pre-signed auth keys allow automated enrollment but are high-value credentials: anyone
with a key can enroll nodes within its tag/validity, revocation does not remove
already-enrolled devices, and long-lived keys undermine per-node signing control. If used:
narrowest tag + ephemeral + shortest expiration + non-plaintext Secret + rotation.

Critical distinction: the operator's Helm auth is the OAuth Secret
(`client_id`/`client_secret`); a pre-signed auth key is NOT a drop-in replacement for the
operator OAuth Secret. [C-001]

## Recovery Safety

Tailnet Lock initialization generates disablement secrets; at least one must be stored
OUTSIDE the protected cluster. If the only trusted signing node and recovery material
live inside an ephemeral kind cluster, cluster loss becomes a tailnet-recovery problem.
Safe arrangement: ≥2 trusted signing nodes, ≥1 signer outside Kubernetes, disablement
secrets offline or in a separate vault, no sole dependency on a frequently-reinstalled
laptop or cluster. [C-001]

## Evidence Ledger

- C-001 | confidence=high | Tailnet Lock requires signed node keys; disablement secrets must live outside the protected cluster; explicit signing is preferred for occasional rebuilds; pre-signed auth keys are high-value credentials and not a substitute for the operator OAuth Secret.
  - source: [[Raw/Sources/deep-research-tailnet-lock.md#Normalized Content]]
