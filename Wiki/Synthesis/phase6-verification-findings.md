---
schema_version: 2
id: "synthesis-phase6-verification-findings"
type: "synthesis"
title: "Phase 6 Verification — Gap-Closing Findings"
topics:
  - "homelab-devsecops"
  - "kubernetes"
  - "gitops"
aliases: []
status: "active"
confidence: "high"
sources:
  - "Raw/Sources/deep-research-phase6-verification.md"
source_count: 1
related:
  - "project-homelab-devsecops"
  - "concept-istio-assessment"
  - "concept-kyverno-enforcement"
  - "concept-openbao-raft-recovery"
  - "concept-flux-gitops-graph"
relationships:
  - "extends|concept-istio-assessment"
  - "extends|concept-kyverno-enforcement"
  - "extends|concept-openbao-raft-recovery"
  - "extends|concept-flux-gitops-graph"
supersedes: []
superseded_by: []
last_verified: "2026-08-24"
review_after: "2026-11-24"
created: 2026-08-24
updated: 2026-08-24
---

# Phase 6 Verification — Gap-Closing Findings

## Synthesis Question

Do the documented simplification decisions hold against a live inspection of the repo
and primary upstream sources?

## Executive Understanding

All documented simplification decisions were checked against a live clone of the repo and
primary upstream sources (2026-08-24).

**Tailscale chart verified**: latest stable `1.102.3` (digest `c2440014..`), audit pin
1.96.4 stale, deep-research v1.102.3 confirmed. Tailscale repo state: no Flux operator
HelmRelease — imperative install; Headlamp/OpenBao still on legacy
`tailscale.com/expose`+`serve` annotations, not L7 Ingress. [C-001]

**kind NetworkPolicy**: kind config has no CNI override → default kindnetd → NetworkPolicies
RENDER but are NOT runtime-enforced. Confirmed security-relevant gap (false assurance).
Recommendation (b): document them as declarative-only in this lab. [C-001]

**Kyverno**: ClusterPolicies exist with `Enforce` but the engine is NOT deployed in Flux →
dead manifests, zero runtime enforcement; CI only runs a CLI check (`kyverno-cli:v1.13.0`,
outdated vs v1.19.0). [C-001]

**Istio**: 1.24.3 on all releases; only `demo` (sample-app) is injected; STRICT scoped to
istio-system; removing it does not affect headlamp/openbao/sample-app. RECOMMEND REMOVE.
[C-001]

**OpenBao**: Raft path already aligned `/openbao/data`; tlsDisable: true; backup is
file-based metadata, NOT `bao operator raft snapshot save`; no retention/drill. [C-001]

**CI**: secrets + misconfig jobs already implement report-vs-fail independence + SARIF +
artifact upload; BUT the `deploy` job still exists (tag-triggered, `flux install`,
GitRepository delete/recreate with `--tag-semver`, kubeconfig, Tailscale) — the second
cluster-manager behavior to remove. Actions pinned to major refs, not SHAs. [C-001]

**config.env**: HEADLAMP_VERSION + SAMPLE_APP_IMAGE duplicate manifest digest pins; FLUX_GIT_TAG
enables semver mode — drift confirmed. [C-001]

## Relationships

Owned by [[Wiki/Projects/homelab-devsecops]]. Extends the Phase-3/4/5 synthesis
[[Wiki/Synthesis/phase345-istio-kyverno-recovery-ci-config]] with repo-verified evidence.

## Contradictions

None. The earlier findings (Istio not load-bearing, Kyverno engine needed, deploy job to
remove, Raft snapshot API needed) are all confirmed by live inspection rather than
contradicted.

## Unknowns

Require a live cluster to verify: OpenBao real seal state / Raft node_id / restore
behavior; L7 Ingress runtime behavior; Tailnet Lock external signer placement. Tracked as
Research/Open items.

## Evidence Ledger

- C-001 | confidence=high | Phase-6 profile: Tailscale 1.102.3 verified and legacy exposure; kind no NetworkPolicy; Kyverno engine absent; Istio 1.24.3 removable; OpenBao file backup not snapshot API; CI deploy job present; config.env version drift.
  - source: [[Raw/Sources/deep-research-phase6-verification.md#Normalized Content]]