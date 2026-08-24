---
schema_version: 2
id: "synthesis-phase2-openbao-scanner-cli"
type: "synthesis"
title: "Phase-2 Synthesis — OpenBao, Scanner Consolidation, CLI Architecture"
topics:
  - "homelab-devsecops"
  - "openbao"
  - "security"
  - "cli"
aliases: []
status: "active"
confidence: "high"
sources:
  - "Raw/Sources/deep-research-openbao-tls-policy.md"
  - "Raw/Sources/deep-research-ci-validation.md"
  - "Raw/Sources/deep-research-config-pinning.md"
source_count: 3
related:
  - "project-homelab-devsecops"
  - "concept-openbao-policy-reconcile"
relationships:
  - "synthesizes|concept-openbao-policy-reconcile"
supersedes: []
superseded_by: []
last_verified: "2026-08-24"
review_after: "2026-11-24"
created: 2026-08-24
updated: 2026-08-24
---

# Phase-2 Synthesis — OpenBao, Scanner Consolidation, CLI Architecture

## Synthesis Question

How should OpenBao policy management, security scanning, and the operational CLI be
simplified after the Flux × Tailscale redesign?

## Executive Understanding

**OpenBao**: policies stay as native HCL files; a thin YAML mapping inventory binds
Kubernetes roles; a host-driven `openbao reconcile` applies them (not an in-cluster
operator — the OpenBao Secrets Operator is archived); bootstrap OIDC + Kubernetes auth,
then revoke the initial root token (delegated sudo model). [C-001]

**Scanners**: the mandatory pull-request gate is **Trivy + gitleaks**; scheduled deep
scans add **Grype** (independent comparison) and **Checkov OR KICS** (not both); SARIF
carries source-linked alerts into GitHub code scanning, JSON preserves full evidence.
CI orchestrates and uploads; it never deploys. [C-002][C-003]

**CLI**: retain Bash for phase 2; typed configuration via JSON Schema + `yq`/`jq` (not
Go); Go only for a specific subcommand that outgrows shell (direct Kubernetes API
integration or persistent recovery state machines). ADR-006 holds — no full migration.
[C-001][C-003]

## Relationships

[[Wiki/Projects/homelab-devsecops]] owns this work; it synthesizes
[[Wiki/Concepts/openbao-policy-reconcile]] and builds on the
[[Wiki/Synthesis/flux-tailscale-redesign]].

## Contradictions

None observed.

## Unknowns

Concrete scanner/action versions and digests were not verified (research rate limits);
they must be pinned manually against official release pages before merge. [C-003]

## Evidence Ledger

- C-001 | confidence=high | OpenBao policies are HCL with a thin YAML mapping inventory, host-driven reconcile, delegated sudo root-token minimization; Bash retained for phase 2 with schema-validated config.
  - source: [[Raw/Sources/deep-research-openbao-tls-policy.md#Normalized Content]]
- C-002 | confidence=high | Mandatory gate is Trivy + gitleaks; Grype and Checkov-OR-KICS are scheduled; SARIF for source-linked alerts, JSON for evidence; CI validates and never deploys.
  - source: [[Raw/Sources/deep-research-ci-validation.md#Normalized Content]]
- C-003 | confidence=high | Full-SHA/digest pinning is the policy; concrete pins remain unresolved and must be verified manually; Conftest/TFLint gate by exit status.
  - source: [[Raw/Sources/deep-research-config-pinning.md#Normalized Content]]
