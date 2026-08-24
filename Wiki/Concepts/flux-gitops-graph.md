---
schema_version: 2
id: "concept-flux-gitops-graph"
type: "concept"
title: "Flux GitOps — 4-Layer Graph, Bootstrap Ownership, Branch vs Semver"
topics:
  - "homelab-devsecops"
  - "flux"
aliases: []
status: "active"
confidence: "high"
sources:
  - "Raw/Sources/deep-research-flux-gitops.md"
source_count: 1
related:
  - "project-homelab-devsecops"
  - "concept-kyverno-enforcement"
relationships:
  - "related-to|project-homelab-devsecops"
supersedes: []
superseded_by: []
last_verified: "2026-08-24"
review_after: "2026-11-24"
created: 2026-08-24
updated: 2026-08-24
---

# Flux GitOps — 4-Layer Graph, Bootstrap Ownership, Branch vs Semver

## Definition

Represent the homelab's desired state as a small Flux Kustomization dependency graph
(`bootstrap → platform → policies → apps`) with deterministic ordering, and let shell wait
on a single terminal readiness signal instead of hard-coding the graph. [C-001]

## Four-Layer Graph

Contents: **bootstrap** (Flux controllers + source, namespaces, secret-decryption
bootstrap, essential CRD prerequisites — keep small), **platform** (reusable infra:
Tailscale operator, ingress controllers, OpenBao, storage, cert/DNS controllers, their
CRDs and prerequisite Secrets), **policies** (NetworkPolicies, admission, RBAC overlays,
pod-security labels — do not apply before their CRDs exist), **apps** (user workloads +
Tailscale Ingress). Use `dependsOn` + `wait: true` + `timeout`; explicit `healthChecks`
for important/out-of-inventory objects. [C-001]

## Waiting on apps Ready

With `wait: true`, the apps Kustomization stays non-Ready until reconciled workloads pass
Flux's health assessment — waiting on `apps` Ready is a sound Kubernetes completion
signal (shell need not know the layer list). Caveat: this is Kubernetes controller health,
not full tailnet DNS/certificate/access-policy/login success. [C-001]

## Branch-Based GitOps vs Semver Source Switching

Keep `GitRepository.spec.ref.branch: main` for a homelab; promotion is a merge/commit to
main. Switching the whole GitRepository to semver is appropriate only for intentionally
published immutable semantic-release config; for a homelab it causes commits not deploying
until tagged, auto-activation of the highest tag, emergency fixes requiring new tags, and
coupled release semantics. [C-001]

## CI Validation Boundary

Flux's documented bootstrap model: bootstrap once → controllers pull → future changes
from Git. CI performing `flux install` / GitRepository delete-recreate / `kubectl apply
-k` / per-layer reconcile violates that model. The target repo's shell also hard-codes
`flux reconcile kustomization infrastructure`, but no such Kustomization exists; shell
should not own the Flux dependency graph. [C-001]

## Evidence Ledger

- C-001 | confidence=high | Flux 4-layer graph with dependsOn/wait/healthChecks; branch-main over semver for a homelab; CI should validate, not deploy; shell must not own the Flux dependency graph; waiting on apps Ready is a Kubernetes-level completion signal.
  - source: [[Raw/Sources/deep-research-flux-gitops.md#Normalized Content]]
