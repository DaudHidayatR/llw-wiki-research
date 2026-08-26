---
schema_version: 2
id: "concept-kind-networkpolicy-enforcement"
type: "concept"
title: "NetworkPolicy Enforcement in kind — kindnetd Does Not Enforce"
topics:
  - "homelab-devsecops"
  - "kubernetes-network"
aliases: []
status: "active"
confidence: "high"
sources:
  - "Raw/Sources/deep-research-phase6-verification.md"
source_count: 1
related:
  - "concept-kyverno-enforcement"
  - "project-homelab-devsecops"
relationships:
  - "related-to|concept-kyverno-enforcement"
supersedes: []
superseded_by: []
last_verified: "2026-08-24"
review_after: "2026-11-24"
created: 2026-08-24
updated: 2026-08-24
---

# NetworkPolicy Enforcement in kind — kindnetd Does Not Enforce

## Definition

kind's default CNI (kindnetd) implements basic pod networking but does NOT enforce
NetworkPolicy. A NetworkPolicy object renders and is accepted by the API server, but
without a policy-enforcing CNI (Calico, Cilium, Antrea) no rule is applied at runtime.
Manifest rendering success is not runtime enforcement. [C-001]

## Repo Evidence

The repo's `bootstrap/controllers/kind-cluster.yaml` sets only `apiServerAddress` in
`networking` — no `disableDefaultCNI: true`, no `cni` override. Therefore the lab runs
kindnetd, and the repo's NetworkPolicies (`openbao/network-policy.yaml`,
`headlamp/network-policy.yaml`) render in CI but have zero runtime enforcement. This is a
confirmed security-relevant gap: the policies give false assurance. [C-001]

## Options

(a) Install a policy-enforcing CNI in kind (Cilium or Calico with `disableDefaultCNI:
true`) — real enforcement, more runtime weight; (b) document explicitly that
NetworkPolicies are declarative-only in this lab (CI-validated shape, not runtime-enforced)
— honest, zero cost; (c) skip NetworkPolicies and rely on Kyverno/PSA for admission
controls. Recommended: (b) now, revisit (a) if the lab's threat model demands real
network segmentation.

## Evidence Ledger

- C-001 | confidence=high | kind default CNI kindnetd does not enforce NetworkPolicy; the repo's kind config has no CNI override; repo NetworkPolicies render without runtime enforcement; options are Cilium/Calico, documented caveat, or admission-only.
  - source: [[Raw/Sources/deep-research-phase6-verification.md#Normalized Content]]