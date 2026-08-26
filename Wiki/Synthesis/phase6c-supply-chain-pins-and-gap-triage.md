---
schema_version: 2
id: "synthesis-phase6c-supply-chain-pins-and-gap-triage"
type: "synthesis"
title: "Phase 6c — Supply-Chain Pins + Remaining-Gap Triage"
topics:
  - "homelab-devsecops"
  - "supply-chain"
  - "ci"
aliases: []
status: "active"
confidence: "high"
sources:
  - "Raw/Sources/source-supply-chain-pin-matrix-2026-08-26.md"
source_count: 1
related:
  - "project-homelab-devsecops"
  - "synthesis-phase6-verification-findings"
  - "synthesis-phase6b-snapshot-and-cni-research"
relationships:
  - "extends|synthesis-phase6-verification-findings"
  - "extends|synthesis-phase6b-snapshot-and-cni-research"
supersedes: []
superseded_by: []
last_verified: "2026-08-26"
review_after: "2026-11-26"
created: 2026-08-26
updated: 2026-08-26
---

# Phase 6c — Supply-Chain Pins + Remaining-Gap Triage

## Synthesis Question

Which supply-chain pins can be recorded now, and what research gaps genuinely remain
after Phases 1–6b?

## Executive Understanding

**Supply-chain pins resolved (primary sources, 2026-08-26).** Action SHAs: checkout
`11d5960a…`, setup-python `a26af69b…`, upload-artifact `ea165f8d…`, codeql upload-sarif
`cdf488f5…`, tailscale/github-action `6cae46e2…`; fluxcd/flux2/action@main is a floating
branch (`da2d22d3…`) — pin to a release SHA or drop with the Deploy job. Tool versions:
Cilium chart v1.20.1, Trivy v0.74.0, Grype v0.117.0, gitleaks v8.30.1, Checkov 3.3.13,
KICS v2.1.21; Kyverno v1.19.0 and Conftest v0.69.0 while the repo pins (v1.13.0/v0.56.0)
are stale. Image digests deferred to implementation-time registry pull (never
fabricated). [C-001]

**Remaining-gap triage.** Closed this phase: Cilium chart pin (v1.20.1) and the
supply-chain matrix. Still genuinely open — live-cluster verification (OpenBao real
restore, Tailscale L7 runtime, Tailnet Lock rebuild, NetworkPolicy data-plane proof) with
procedures written but execution requiring a real `make up`; Cilium resource cost
(measure on host); OpenBao backup destination concrete provider (class decided);
Calico design (only if chosen); Knowledge OS corroboration thresholds and retrieval
benchmark (low priority). [C-001]

## Relationships

Owned by [[Wiki/Projects/homelab-devsecops]]. Extends the Phase-6 verification and
Phase-6b snapshot/CNI syntheses. The live-cluster items remain tracked in
[[Research/Open/live-cluster-verification]].

## Contradictions

None.

## Unknowns

Implementation-time values: container image digests; final CI action set after the
Deploy-job removal; Cilium resource measurement; concrete OpenBao backup destination.

## Evidence Ledger

- C-001 | confidence=high | The supply-chain pin matrix (action SHAs + current tool versions) is resolved from primary sources; remaining gaps are live-cluster verification, Cilium resource measurement, concrete backup destination, optional Calico design, and Knowledge OS threshold/benchmark items.
  - source: [[Raw/Sources/source-supply-chain-pin-matrix-2026-08-26.md#Normalized Content]]