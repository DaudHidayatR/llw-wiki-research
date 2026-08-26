---
schema_version: 2
id: "research-open-live-cluster-verification"
type: "research-open"
title: "Live-Cluster Verification of OpenBao, Tailscale Ingress, and Tailnet Lock"
status: "open"
created: 2026-08-24
updated: 2026-08-24
---

# Live-Cluster Verification of OpenBao, Tailscale Ingress, and Tailnet Lock

Several Phase-6 conclusions require a live kind cluster to verify and remain open:

1. OpenBao real seal state (sealed vs unsealed after rebuild), Raft `node_id`, and a
   real `bao operator raft snapshot save` / `restore` cycle (including whether
   `restore -force` / `-stage` behave as expected on the installed version).
2. Tailscale L7 Ingress runtime behavior for Headlamp and OpenBao (cert issuance,
   MagicDNS hostname, HTTPS first-request latency).
3. Tailnet Lock external signer placement and whether a destructive kind rebuild
   reproduces the documented identity-recovery path.

Related: [[Wiki/Concepts/openbao-raft-recovery]], [[Wiki/Concepts/tailscale-l7-ingress]],
[[Wiki/Synthesis/phase6-verification-findings]].

## Procedures now defined (2026-08-26)

The runtime tests below no longer need research — the exact procedures are documented and
just need a live `make up`:

1. **OpenBao restore drill** — full checklist in
   [[Wiki/Synthesis/phase6b-snapshot-and-cni-research]] and
   [[Raw/Sources/deep-research-openbao-snapshot-automation]]: KV canary, policy
   allow/deny, auth roles, Transit round-trip, Raft `list-peers`, pod-deletion
   persistence, `bao status`; redacted evidence bundle + `-stage` semantics tested against
   the installed `bao` binary.
2. **Tailscale L7 Ingress runtime** — deploy ingress for a test Service, confirm
   `spec.tls.hosts` MagicDNS name resolves, HTTPS (443) terminates, first-request
   Let's Encrypt latency tolerable; verify standalone proxy Pod created.
3. **Tailnet Lock signer + destructive rebuild** — confirm ≥1 signing node and a
   disablement secret OUTSIDE the cluster; destroy a disposable kind cluster and verify the
   operator/proxy identities are signed or fail closed as documented.