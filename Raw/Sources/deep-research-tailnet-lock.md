---
schema_version: 2
id: "source-deep-research-tailnet-lock"
type: "source"
title: "Deep Research — Tailnet Lock and Ephemeral kind Rebuilds"
Author: "Hermes Deep Research"
Reference: "deep-research-jobs-f5139ca8-7d866990"
SourceType: "web"
ContentType:
  - "markdown"
Published: "2026-08-24"
Captured: "2026-08-24"
Created: "2026-08-24"
Processed: true
tags:
  - "source"
ContentHash: "sha256:95d344073153cfd36ba0b8a017370d91f6fb26127a0afac8e443a12734ba187b"
---

# Deep Research — Tailnet Lock and Ephemeral kind Rebuilds

## Normalized Content

Tailnet Lock requires every new Tailscale node key to be signed by a trusted Tailnet
Lock signing key, protecting against unauthorized node insertion via a compromised
coordination plane. Private signing keys remain on trusted customer-controlled nodes.

A kind-cluster rebuild commonly recreates the operator Pod (and potentially its state),
ingress proxy Pods and their state Secrets, and — if persistent state is not restored —
the Tailscale node identities themselves. New identities have new node keys; under
Tailnet Lock they must be signed before becoming trusted participants.

Explicit signing: a trusted signing node approves each replacement via a signing link or
`tailscale lock sign`. Pros: human approval for every replacement node, no reusable
enrollment credential stored in the cluster, limits blast radius of a compromised
Kubernetes Secret, best fit for occasional homelab rebuilds. Cons: every recreated
operator/proxy identity may need intervention, rebuild cannot complete unattended,
multiple exposed workloads mean multiple new proxy identities.

Pre-signed auth keys allow automated enrollment without separately signing each resulting
node. They can be one-off/reusable, ephemeral, tagged, pre-approved, and pre-signed for
Tailnet Lock. Risks: a reusable pre-signed key is a high-value credential; anyone with it
can enroll nodes within its tag and validity constraints; revoking the key does not
remove already-enrolled devices; long-lived keys undermine per-node signing control. If
used: narrowest tag + ephemeral where compatible + shortest practical expiration +
non-plaintext Secret + rotation + separate credentials per workload.

Critical operator distinction: the operator's Helm auth is the OAuth Secret
(`client_id`/`client_secret`) used to call the Tailscale API and manage auth material for
its nodes and proxies. A pre-signed auth key is NOT a drop-in replacement for the
operator OAuth Secret.

Retaining the operator's Kubernetes state Secrets across ordinary Pod restarts is
preferable to recreating identities unnecessarily. A full destructive kind rebuild is
different: if state is destroyed, expect new identities.

Tailnet Lock initialization generates disablement secrets; at least one must be stored
OUTSIDE the protected cluster. If the only trusted signing node and recovery material
live inside an ephemeral kind cluster, cluster loss becomes a tailnet-recovery problem.
Safe arrangement: at least two trusted signing nodes, at least one signer outside
Kubernetes, disablement secrets offline or in a separate secure vault, no sole dependency
on a frequently-reinstalled laptop or cluster.

## References

- https://tailscale.com/kb/1226/tailnet-lock
- https://tailscale.com/kb/1230/tailnet-lock-whitepaper
- https://tailscale.com/kb/1085/auth-keys

## Capture Notes

Consolidated from deep-research job f5139ca8a1534ac2b1f92fb1ce6c323d (Phase 1, card 3/5).
Feeds the P1 identity-restore decision (kanban t_c082c026).
