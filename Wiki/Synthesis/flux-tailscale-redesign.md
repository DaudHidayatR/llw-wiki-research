---
schema_version: 2
id: "synthesis-flux-tailscale-redesign"
type: "synthesis"
title: "Flux × Tailscale Redesign Synthesis"
topics:
  - "homelab-devsecops"
  - "tailscale"
  - "flux"
aliases: []
status: "active"
confidence: "high"
sources:
  - "Raw/Sources/deep-research-tailscale-operator.md"
  - "Raw/Sources/deep-research-tailnet-lock.md"
  - "Raw/Sources/deep-research-flux-gitops.md"
  - "Raw/Sources/deep-research-openbao-tls-policy.md"
source_count: 4
related:
  - "project-homelab-devsecops"
  - "concept-tailscale-operator-helm"
  - "concept-tailscale-l7-ingress"
  - "concept-tailnet-lock-rebuilds"
  - "concept-flux-gitops-graph"
  - "concept-openbao-http-behind-tls"
relationships:
  - "synthesizes|concept-tailscale-operator-helm"
  - "synthesizes|concept-tailscale-l7-ingress"
  - "synthesizes|concept-tailnet-lock-rebuilds"
  - "synthesizes|concept-flux-gitops-graph"
supersedes: []
superseded_by: []
last_verified: "2026-08-24"
review_after: "2026-11-24"
created: 2026-08-24
updated: 2026-08-24
---

# Flux × Tailscale Redesign Synthesis

## Synthesis Question

How should Flux and the Tailscale Kubernetes Operator divide ownership for a small
homelab so neither shell nor CI becomes a second control plane?

## Executive Understanding

The redesign gives each component its documented role: **Flux declares** persistent
Kubernetes resources (Tailscale Operator HelmRelease, Headlamp/OpenBao Tailscale
Ingresses, Services, Kustomizations); **Tailscale reconciles** what it generates from
those declarations (proxy Pods, state Secrets, Serve configuration); **Shell bootstraps**
(kind create/delete, `operator-oauth` Secret injection, first Flux bootstrap, Tailnet
Lock signing, diagnostics); **CI validates** (scans, renders, schema-checks, uploads
SARIF) and never deploys. [C-001][C-002][C-003]

Key mechanics: the operator installs via the official Helm chart with a pre-created
`operator-oauth` Secret (`client_id`/`client_secret`); L7 exposure uses
`ingressClassName: tailscale` with standalone proxies first; Tailnet Lock signing stays
explicit for occasional rebuilds; the Flux graph collapses to four layers with
branch-main GitOps; OpenBao runs plain HTTP behind Tailscale TLS termination. [C-001]
[C-002][C-003][C-004]

## Relationships

[[Wiki/Projects/homelab-devsecops]] is the owning project. The redesign synthesizes
[[Wiki/Concepts/tailscale-operator-helm]], [[Wiki/Concepts/tailscale-l7-ingress]],
[[Wiki/Concepts/tailnet-lock-rebuilds]], [[Wiki/Concepts/flux-gitops-graph]], and
[[Wiki/Concepts/openbao-http-behind-tls]].

## Contradictions

None observed. The audit's earlier pinned Tailscale chart version (1.96.4) is stale;
current stable was reported as v1.102.3 and must be verified against the official index
before commit. [C-001]

## Unknowns

Repo-specific values (chart pin, namespace/Secret names, Kustomization layout) must be
verified against the deployed manifests before implementation. Tailnet Lock external
signer placement must be confirmed. [C-002]

## Evidence Ledger

- C-001 | confidence=high | Flux declares (operator HelmRelease + Ingresses), Tailscale reconciles generated proxy state, shell bootstraps, CI validates; chart repo and operator-oauth Secret contract; standalone-first L7 Ingress; OpenBao HTTP behind Tailscale TLS.
  - source: [[Raw/Sources/deep-research-tailscale-operator.md#Normalized Content]]
- C-002 | confidence=high | Tailnet Lock signing stays explicit for occasional rebuilds with an external signer.
  - source: [[Raw/Sources/deep-research-tailnet-lock.md#Normalized Content]]
- C-003 | confidence=high | Flux 4-layer graph, branch-main GitOps, CI validation-only, shell must not own the Flux dependency graph.
  - source: [[Raw/Sources/deep-research-flux-gitops.md#Normalized Content]]
- C-004 | confidence=high | OpenBao tlsDisable behind Tailscale L7 TLS termination is compatible with the correct Ingress backend and external API address.
  - source: [[Raw/Sources/deep-research-openbao-tls-policy.md#Normalized Content]]
