---
schema_version: 2
id: "project-homelab-devsecops"
type: "project"
title: "Homelab DevSecOps — Architecture Audit and Simplification"
topics:
  - "homelab-devsecops"
  - "kubernetes"
  - "gitops"
aliases:
  - "homelab"
status: "active"
confidence: "high"
sources:
  - "Raw/Sources/deep-research-tailscale-operator.md"
  - "Raw/Sources/deep-research-tailnet-lock.md"
  - "Raw/Sources/deep-research-flux-gitops.md"
  - "Raw/Sources/deep-research-openbao-tls-policy.md"
  - "Raw/Sources/deep-research-openbao-raft-recovery.md"
  - "Raw/Sources/deep-research-policy-kyverno-istio.md"
  - "Raw/Sources/deep-research-ci-validation.md"
  - "Raw/Sources/deep-research-config-pinning.md"
source_count: 8
related:
  - "concept-tailscale-operator-helm"
  - "concept-tailscale-l7-ingress"
  - "concept-tailnet-lock-rebuilds"
  - "concept-flux-gitops-graph"
  - "concept-openbao-http-behind-tls"
  - "concept-openbao-policy-reconcile"
  - "concept-openbao-raft-recovery"
  - "concept-kyverno-enforcement"
  - "concept-istio-assessment"
  - "synthesis-flux-tailscale-redesign"
  - "synthesis-phase2-openbao-scanner-cli"
  - "synthesis-phase345-istio-kyverno-recovery-ci-config"
  - "synthesis-phase6-verification-findings"
  - "synthesis-phase6b-snapshot-and-cni-research"
  - "synthesis-phase6c-supply-chain-pins-and-gap-triage"
  - "concept-kind-networkpolicy-enforcement"
  - "research-question-openbao-snapshot-automation"
relationships:
  - "has-concept|concept-tailscale-operator-helm"
  - "has-concept|concept-tailscale-l7-ingress"
  - "has-concept|concept-tailnet-lock-rebuilds"
  - "has-concept|concept-flux-gitops-graph"
  - "has-concept|concept-openbao-http-behind-tls"
  - "has-concept|concept-openbao-policy-reconcile"
  - "has-concept|concept-openbao-raft-recovery"
  - "has-concept|concept-kyverno-enforcement"
  - "has-concept|concept-istio-assessment"
supersedes: []
superseded_by: []
last_verified: "2026-08-24"
review_after: "2026-11-24"
created: 2026-08-24
updated: 2026-08-24
---

# Homelab DevSecOps — Architecture Audit and Simplification

## Overview

`DaudHidayatR/homelab-devsecops` is a minimal rootless Kubernetes (kind) and Istio lab
managed by Flux, with OpenBao for secrets, Tailscale for private exposure, security
scanning, and CI/CD gates. The deep-research program validated a simplification
direction: make Flux the single owner of persistent Kubernetes desired state, make
Tailscale exposure Kubernetes-native, keep shell to bootstrap/recovery/diagnostics, and
make CI validation-only. [C-001]

## Core Design Principle

> **Flux declares. Tailscale reconciles. Shell bootstraps. CI validates.**

## Key Decisions

- Tailscale Operator installed via Flux HelmRelease with a pre-created `operator-oauth`
  Secret; exposure via Tailscale L7 Ingress (standalone-first). [C-001]
- Tailnet Lock signing stays explicit for occasional kind rebuilds. [C-002]
- Flux 4-layer graph `bootstrap → platform → policies → apps`, branch-main GitOps, CI
  validation-only. [C-003]
- OpenBao: HCL policies + YAML mappings, host-driven reconcile, root-token revocation,
  Raft snapshot recovery runbook. [C-004][C-005]
- PSA + Kyverno enforcement; Istio removed unless service-mesh learning is explicit.
  [C-006]
- config.env one-value-one-owner; full-SHA/digest pinning. [C-007][C-008]

## Evidence Ledger

- C-001 | confidence=high | The Tailscale operator installs via Flux HelmRelease with a pre-created operator-oauth Secret and L7 Ingress exposure; the lab is a kind + Flux + OpenBao + Tailscale DevSecOps environment.
  - source: [[Raw/Sources/deep-research-tailscale-operator.md#Normalized Content]]
- C-002 | confidence=high | Tailnet Lock requires signed node keys and explicit signing is the recommended rebuild workflow.
  - source: [[Raw/Sources/deep-research-tailnet-lock.md#Normalized Content]]
- C-003 | confidence=high | The Flux 4-layer graph with branch-main GitOps and validation-only CI is the recommended operating model.
  - source: [[Raw/Sources/deep-research-flux-gitops.md#Normalized Content]]
- C-004 | confidence=high | OpenBao policies are HCL with a thin YAML mapping inventory and host-driven reconciliation; root tokens are revoked after delegated admin bootstrap.
  - source: [[Raw/Sources/deep-research-openbao-tls-policy.md#Normalized Content]]
- C-005 | confidence=high | OpenBao Raft snapshot save/restore with the documented runbook is the recovery path for a single-node lab.
  - source: [[Raw/Sources/deep-research-openbao-raft-recovery.md#Normalized Content]]
- C-006 | confidence=high | PSA + Kyverno own policy enforcement; Istio is not load-bearing and should be removed unless mesh learning is explicit.
  - source: [[Raw/Sources/deep-research-policy-kyverno-istio.md#Normalized Content]]
- C-007 | confidence=high | config.env should hold only bootstrap/secrets; chart and image versions belong to their manifests.
  - source: [[Raw/Sources/deep-research-config-pinning.md#Normalized Content]]
- C-008 | confidence=high | Actions should be pinned to full SHAs and scanner images by digest; concrete pins require manual upstream verification.
  - source: [[Raw/Sources/deep-research-config-pinning.md#Normalized Content]]
