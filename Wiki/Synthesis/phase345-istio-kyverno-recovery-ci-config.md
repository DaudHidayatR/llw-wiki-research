---
schema_version: 2
id: "synthesis-phase345-istio-kyverno-recovery-ci-config"
type: "synthesis"
title: "Phases 3–5 Synthesis — Istio, Kyverno, OpenBao Recovery, CI, config, Pinning"
topics:
  - "homelab-devsecops"
  - "istio"
  - "kyverno"
  - "openbao"
  - "ci"
aliases: []
status: "active"
confidence: "high"
sources:
  - "Raw/Sources/deep-research-openbao-raft-recovery.md"
  - "Raw/Sources/deep-research-policy-kyverno-istio.md"
  - "Raw/Sources/deep-research-ci-validation.md"
  - "Raw/Sources/deep-research-config-pinning.md"
source_count: 4
related:
  - "project-homelab-devsecops"
  - "concept-kyverno-enforcement"
  - "concept-istio-assessment"
  - "concept-openbao-raft-recovery"
relationships:
  - "synthesizes|concept-kyverno-enforcement"
  - "synthesizes|concept-istio-assessment"
  - "synthesizes|concept-openbao-raft-recovery"
supersedes: []
superseded_by: []
last_verified: "2026-08-24"
review_after: "2026-11-24"
created: 2026-08-24
updated: 2026-08-24
---

# Phases 3–5 Synthesis — Istio, Kyverno, OpenBao Recovery, CI, config, Pinning

## Synthesis Question

What are the remaining simplification decisions for the homelab: Istio, policy
enforcement, OpenBao recovery, CI pipeline, configuration ownership, and tool pinning?

## Executive Understanding

**Istio** is not load-bearing for Headlamp/OpenBao/Tailscale and 1.24.3 is unsupported;
remove it unless service-mesh learning is an explicit objective (then upgrade to 1.30.x
in a dedicated mesh-demo namespace, keeping tailscale/headlamp/openbao out of injection,
because a non-injected Tailscale proxy to an injected STRICT backend fails). [C-001]

**Policy enforcement**: PSA owns Pod Security Standards; Kyverno owns non-PSS admission
rules (engine in `platform`, policies in `policies`); Conftest only unique repo/aggregate
checks; no broad Flux exclusion; audit-to-enforce progressive promotion. [C-001]

**OpenBao recovery**: Raft snapshot save/restore is the backup path; a documented runbook
(daily + pre/post-change snapshots, off-cluster storage, quarterly drill, port-forward to
break the Tailnet Lock cycle) preserves a single-node lab; Shamir preferred. [C-002]

**CI**: delete the Deploy job; validation-only pipeline (render-and-schema, secret/
ignore checks, SARIF with unique categories); branch-main; least-privilege; full-SHA
pinning. [C-003]

**config.env**: one-value-one-owner; keep only bootstrap/secrets; chart/image/scanner
versions belong to their manifests/workflow; no universal versions.yaml. [C-004]

## Relationships

[[Wiki/Projects/homelab-devsecops]] owns this work; the synthesis draws together
[[Wiki/Concepts/istio-assessment]], [[Wiki/Concepts/kyverno-enforcement]],
[[Wiki/Concepts/openbao-raft-recovery]], [[Wiki/Concepts/flux-gitops-graph]], and the
Phase-2 [[Wiki/Synthesis/phase2-openbao-scanner-cli]].

## Contradictions

None observed.

## Unknowns

Multiple Phase-3/4/5 jobs could not retrieve the target repo (search rate limits);
repo-specific state (Kyverno current install/version, OpenBao Raft path/mount/node_id/
seal, exact config.env occurrences, workflow line-level steps, kind CNI NetworkPolicy
support, concrete scanner/action pins) must be verified before implementation. [C-001]
[C-002][C-004]

## Evidence Ledger

- C-001 | confidence=high | PSA + Kyverno own policy enforcement; Istio is not load-bearing and 1.24.3 is unsupported (remove, or upgrade to 1.30.x in a dedicated mesh-demo keeping tailscale/headlamp/openbao out of injection).
  - source: [[Raw/Sources/deep-research-policy-kyverno-istio.md#Normalized Content]]
- C-002 | confidence=high | OpenBao Raft snapshot recovery runbook preserves a single-node lab; Shamir preferred; port-forward breaks the Tailnet Lock cycle.
  - source: [[Raw/Sources/deep-research-openbao-raft-recovery.md#Normalized Content]]
- C-003 | confidence=high | CI should delete the Deploy job and be validation-only with branch-main, least-privilege, and full-SHA pinning.
  - source: [[Raw/Sources/deep-research-ci-validation.md#Normalized Content]]
- C-004 | confidence=high | config.env holds only bootstrap/secrets; chart/image/scanner versions belong to their owning manifests/workflow; one-value-one-owner with no universal versions file.
  - source: [[Raw/Sources/deep-research-config-pinning.md#Normalized Content]]
