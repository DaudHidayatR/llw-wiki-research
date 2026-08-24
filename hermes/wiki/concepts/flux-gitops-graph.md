---
schema_version: 2
id: "concept-flux-gitops-graph"
type: "concept"
title: "Flux GitOps — 4-Layer Graph, Bootstrap Ownership, Branch vs Semver"
topics:
  - "flux"
  - "homelab-devsecops"
aliases:
  - "flux kustomization graph"
status: "active"
confidence: "high"
sources:
  - "https://fluxcd.io/flux/components/kustomize/kustomizations/"
  - "https://fluxcd.io/flux/installation/bootstrap/github/"
  - "https://fluxcd.io/flux/guides/repository-structure/"
source_count: 3
related:
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

# Flux GitOps — 4-Layer Graph, Bootstrap Ownership, Branch vs Semver

## Definition

Represent the homelab's desired state as a small Flux Kustomization dependency graph
(`bootstrap → platform → policies → apps`) with deterministic ordering, and let shell wait
on a single terminal readiness signal instead of hard-coding the graph.

## Four-Layer Graph

```text
bootstrap
   ↓
platform
   ↓
policies
   ↓
apps
```

- **bootstrap**: Flux controllers + source, namespaces, secret-decryption bootstrap (SOPS
  age key / external secret), essential CRD prerequisites that cannot be introduced
  later. Keep small — everything depends on it. [C-001]
- **platform**: reusable infra — Tailscale operator, ingress controllers, OpenBao,
  storage provisioners, cert/DNS controllers; their CRDs and prerequisite Secrets.
- **policies**: controls depending on platform APIs — NetworkPolicies, admission
  policies, RBAC overlays, pod-security labels. Do NOT apply before their CRDs/controllers
  exist; don't introduce default-deny before required connectivity is described.
- **apps**: user workloads + their Tailscale Ingress.

Represented with Kustomizations using `dependsOn` + `wait: true` + `timeout`; add explicit
`healthChecks` for especially important or out-of-inventory objects (e.g. Deployment +
Ingress openbao). [C-001]

```yaml
apiVersion: kustomize.toolkit.fluxcd.io/v1
kind: Kustomization
metadata: { name: platform, namespace: flux-system }
spec:
  interval: 10m
  path: ./clusters/homelab/platform
  prune: true
  sourceRef: { kind: GitRepository, name: flux-system }
  dependsOn: [{ name: bootstrap }]
  wait: true
  timeout: 15m
```

## Waiting on apps Ready

Set `wait: true` on the apps Kustomization so it stays non-Ready until workloads pass
Flux's health assessment — **waiting on `apps` Ready is a sound K8s completion signal**
(shell doesn't need the layer list). Caveat: Flux readiness = K8s controller health, NOT
full tailnet DNS, cert issuance, access-policy correctness, or app-login success; final
tailnet reachability still needs Ingress-status/tailnet checks. [C-001]

## Don't Over-Serialize

Unrelated platform components (Tailscale vs storage vs OpenBao) can reconcile
independently — refine into per-component platform Kustomizations
(`platform-tailscale`, `platform-openbao`) only where independent failure domains add
real value. A small homelab does not need dozens of micro-Kustomizations.

## Branch-Based GitOps vs Semver Source Switching

Keep `GitRepository.ref.branch: main` for a homelab; promotion = merge/commit to main.
Switching the whole GitRepository to semver is appropriate only for intentionally
published immutable semantic-release configs. For a homelab, semver source causes:
commits to main don't deploy until tagged; the highest matching tag can auto-activate;
emergency fixes require a new tag; source-level release semantics become coupled to all
apps. [C-002]

Prefer: `main` for desired state; pinned Helm chart versions in `HelmRelease`; pinned
container image tags/digests; automated PRs for updates; git history + revert for
rollback.

## CI Validation Boundary

Flux's documented bootstrap model: bootstrap once → controllers pull desired state →
future changes come from Git. CI performing `flux install` / GitRepository
delete-recreate / `kubectl apply -k` / per-layer reconcile violates that model and makes
CI a second controller. CI should validate/scan/render/test/report and upload SARIF;
Flux deploys/reconciles/repairs drift. [C-003]

## Evidence Ledger

- C-001 | confidence=high | Kustomization supports dependsOn, wait, healthChecks, timeout; ordering + readiness semantics.
  - source: https://fluxcd.io/flux/components/kustomize/kustomizations/
- C-002 | confidence=high | Branch-main GitOps for homelab; semver source for published release configs; branch-protection promotion gate.
  - source: https://fluxcd.io/flux/guides/repository-structure/ , https://fluxcd.io/flux/installation/bootstrap/github/
- C-003 | confidence=high | Bootstrap transition model; CI acting as controller violates it.
  - source: https://fluxcd.io/flux/installation/bootstrap/github/