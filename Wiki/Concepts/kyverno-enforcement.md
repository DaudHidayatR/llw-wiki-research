---
schema_version: 2
id: "concept-kyverno-enforcement"
type: "concept"
title: "Kyverno Enforcement, PSA, and Conftest Ownership Split"
topics:
  - "homelab-devsecops"
  - "kubernetes-policy"
aliases: []
status: "active"
confidence: "high"
sources:
  - "Raw/Sources/deep-research-policy-kyverno-istio.md"
source_count: 1
related:
  - "concept-flux-gitops-graph"
  - "project-homelab-devsecops"
relationships:
  - "related-to|concept-flux-gitops-graph"
supersedes: []
superseded_by: []
last_verified: "2026-08-24"
review_after: "2026-11-24"
created: 2026-08-24
updated: 2026-08-24
---

# Kyverno Enforcement, PSA, and Conftest Ownership Split

## Definition

Use Kubernetes Pod Security Admission (PSA) for Pod Security Standards, Kyverno as the
in-cluster admission controller for Kubernetes-specific rules beyond PSS, and Conftest
only for unique repository/aggregate/non-Kubernetes checks. Maintain one authoritative
implementation per rule — do not duplicate equivalent rules in Rego and Kyverno. [C-001]

## Audit vs Enforce

`Enforce` immediately for deterministic low-risk rules (disallow mutable `:latest`,
require explicit image tags/digests, reject privileged Pods in application namespaces if
PSA does not already, require a minimal label set). `Audit` first for disruptive rules
(runAsNonRoot, read-only rootfs, drop-all-caps, resource requests/limits, probes,
default-deny NetworkPolicy, approved registries, signed images). Promote individually
after reports are clean. Avoid a permanent audit-everything posture and avoid one global
audit-to-enforce switch. Audit-to-enforce does not evict existing non-compliant Pods;
only new/updated resources are rejected. [C-001]

## Kyverno and Flux

Flux-applied resources are API requests subject to admission. Do not broadly exclude the
`flux-system` namespace or Flux controller service accounts; exclude specific
namespaces, kinds, or service accounts only where a policy is incompatible with a
required controller operation. Kyverno mutation can fight Flux (drift and reapply) —
prefer explicit desired values in Git. [C-001]

## Placement in the Flux Graph

The Kyverno engine belongs in the `platform` Flux layer; ClusterPolicy/Policy objects and
PSA namespace labels belong in `policies`; `policies dependsOn platform`; `apps dependsOn
policies`. Kyverno should not be bundled into bootstrap. NetworkPolicy enforcement depends
on the cluster's network implementation; verify the kind CNI implements NetworkPolicy
before enforcing default-deny. [C-001]

## Evidence Ledger

- C-001 | confidence=high | PSA owns PSS; Kyverno owns non-PSS admission rules; Conftest only unique repo/aggregate/non-Kubernetes checks; enforce low-risk rules immediately and audit disruptive ones; no broad Flux exclusion; Kyverno engine in platform, policies resources in policies; verify kind CNI NetworkPolicy support.
  - source: [[Raw/Sources/deep-research-policy-kyverno-istio.md#Normalized Content]]
