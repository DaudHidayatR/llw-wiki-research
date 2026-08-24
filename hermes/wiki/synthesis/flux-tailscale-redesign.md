---
schema_version: 2
id: "synthesis-flux-tailscale-redesign"
type: "synthesis"
title: "Consolidated Synthesis — Flux × Tailscale Redesign for homelab-devsecops"
topics:
  - "homelab-devsecops"
  - "tailscale"
  - "flux"
aliases: []
status: "active"
confidence: "high"
sources:
  - "https://pkgs.tailscale.com/helmcharts/index.yaml"
  - "https://fluxcd.io/flux/components/kustomize/kustomizations/"
  - "https://tailscale.com/kb/1226/tailnet-lock"
source_count: 21
related:
  - "concept-tailscale-operator-helm"
  - "concept-tailscale-l7-ingress"
  - "concept-tailnet-lock-rebuilds"
  - "concept-flux-gitops-graph"
  - "concept-openbao-http-behind-tls"
relationships:
  - "part-of|project-homelab-devsecops-research"
supersedes: []
superseded_by: []
last_verified: "2026-08-24"
review_after: "2026-11-24"
created: 2026-08-24
updated: 2026-08-24
---

# Consolidated Synthesis — Flux × Tailscale Redesign

## Target Architecture

```text
Git ──► Flux ──► { Tailscale Operator HelmRelease, App manifests }
                        │                           │
                        ▼                           ▼
                  Tailscale Operator        Tailscale Ingress (Headlamp, OpenBao)
                        └──────────┬──────────────┘
                                   ▼
                        generated proxy state
                                   │
                                   ▼
                             private tailnet
```

**Ownership rule:** Flux declares Kubernetes resources; Tailscale reconciles what it
generates from them; Shell bootstraps (kind, OAuth Secret injection, first Flux
bootstrap, Tailnet Lock signing, diagnostics); CI validates (never deploys). [C-001]

## Recommended Operating Matrix

| Area | Recommendation | Source |
|---|---|---|
| Chart repo | `https://pkgs.tailscale.com/helmcharts` (index authoritative) | high |
| Chart version | `v1.102.3`, verify from index (audit's 1.96.4 **stale**) | high |
| OAuth Secret | pre-created `operator-oauth`, keys `client_id`/`client_secret` | high |
| Secret storage | encrypted Git (SOPS) / external store; never plaintext | high |
| Historical | never deploy 1.92.3 with pre-created Secret | high |
| Proxy mode | standalone first; ProxyGroup only for real HA | high |
| Tags | `tag:k8s-operator` owns `tag:k8s`; custom tags need tagOwners | high |
| Access | grant admin group `tcp:443` → `tag:k8s` (grants syntax) | high |
| Tailnet Lock | explicit signing for occasional rebuilds | high |
| Flux source | branch `main`; pin chart + image versions in artifacts | high |
| Graph | `bootstrap → platform → policies → apps`; wait on apps Ready | high |
| OpenBao | HTTP :8200 internally, HTTPS by Tailscale; external addr = MagicDNS URL | high |

## Corrections to Audit v2

1. **Chart version stale** — re-pin to v1.102.3 (verify from official index, leading-`v`
   matters for the Flux constraint).
2. **Tag model** — audit's two custom admin tags vs research default single `tag:k8s` +
   group grant. Custom tags valid but need explicit `tagOwners` + per-tag grants.
3. **OpenBao advertised address** — must be the HTTPS MagicDNS URL, not internal HTTP.
4. **Secret storage** — research defaults to SOPS/external store; audit's "no SOPS now"
   is a scoping choice flagged for review.

## Open Decisions for the Human

- Tag model: single `tag:k8s` (simple) vs two custom admin tags (Headlamp/OpenBao
  separation).
- Secret storage: SOPS/external-secret now vs no-SOPS scoping.
- Tailnet Lock: confirm ≥1 signer + disablement secret outside the kind cluster.
- Verify exact chart version string from official index.

## Migration Order (validated)

P0: fix stale Flux reconcile path → CI validation-only → branch-main GitOps.
P0: Tailscale operator → Flux HelmRelease; bootstrap-only `operator-oauth` Secret;
Headlamp then OpenBao → L7 Ingress; delete custom Serve watcher last (after equivalence).
P1: collapse Flux 7→4 layers; Tailscale CLI → check/sign/credentials; simplify identity
restore. P2: wider OpenBao/scanner/script simplification.

## Evidence Ledger

See per-concept Evidence Ledgers. Consolidated high-confidence claims: C-001 (ownership
model), C-002 (chart + Secret), C-006 (standalone-first), C-008 (tags), C-011 (Flux
graph), C-014 (OpenBao HTTP behind TLS). Lower-confidence items depend on operational
preferences and Tailnet Lock workflow, not vendor API behavior.