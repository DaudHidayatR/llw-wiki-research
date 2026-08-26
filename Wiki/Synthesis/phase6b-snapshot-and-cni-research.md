---
schema_version: 2
id: "synthesis-phase6b-snapshot-and-cni-research"
type: "synthesis"
title: "Phase 6b Research — OpenBao Snapshot Automation + kind CNI Choice"
topics:
  - "homelab-devsecops"
  - "openbao"
  - "kubernetes-network"
aliases: []
status: "active"
confidence: "high"
sources:
  - "Raw/Sources/deep-research-openbao-snapshot-automation.md"
  - "Raw/Sources/deep-research-kind-cni.md"
source_count: 2
related:
  - "project-homelab-devsecops"
  - "concept-openbao-raft-recovery"
  - "concept-kind-networkpolicy-enforcement"
  - "research-question-openbao-snapshot-automation"
relationships:
  - "extends|concept-openbao-raft-recovery"
  - "extends|concept-kind-networkpolicy-enforcement"
  - "answers|research-question-openbao-snapshot-automation"
supersedes: []
superseded_by: []
last_verified: "2026-08-26"
review_after: "2026-11-26"
created: 2026-08-26
updated: 2026-08-26
---

# Phase 6b Research — OpenBao Snapshot Automation + kind CNI Choice

## Synthesis Question

What is the concrete automation contract for OpenBao Raft snapshots, and which
NetworkPolicy-enforcing CNI (if any) should the kind lab adopt?

## Executive Understanding

**OpenBao snapshots**: run automation on an independent host via systemd timer (NOT a
Kubernetes CronJob — correlated failure domain); export-only token, never root; stage →
SHA-256 → atomic rename → versioned/immutable off-cluster destination; retention 14d/8w/12m
+ pre-change (≥90d) + drill-qualified; export/restore identity split with break-glass
restore; `-force` is deliberate break-glass (bypasses seal-key checks), `-stage` semantics
unverified in current docs — test the installed binary; quarterly isolated restore drill
with a full semantic checklist (KV canary, policies allow+deny, auth roles, Transit round
trip, pod-deletion persistence, Raft peer state) and a redacted evidence bundle measuring
RTO. Single-node Raft is DR, not availability. [C-001]

**kind CNI**: kindnetd does not enforce NetworkPolicy (Phase-6 confirmed). For real
enforcement, default is **minimal Cilium** (`disableDefaultCNI: true`, bootstrap CNI
directly then hand to Flux, operator 1 replica, kube-proxy retained, Hubble/encryption
off, pinned chart); Calico suits conventional networking/learning goals but its branch
timed out (verify docs.tigera.io). Verification is a data-plane test (two Pods, TCP
positive control → deny-all → fail both directions → recover), never ping/schema.
Alternatives: keep kindnetd + declarative-only label + negative control, or remove the
policies. PSA/Kyverno never implement the NetworkPolicy data plane. [C-002]

## Relationships

Owned by [[Wiki/Projects/homelab-devsecops]]. Extends
[[Wiki/Concepts/openbao-raft-recovery]] and [[Wiki/Concepts/kind-networkpolicy-enforcement]];
answers the open [[Research/Questions/openbao-snapshot-automation]].
The [[Research/Open/live-cluster-verification]] record still holds the runtime-only
items (real restore behavior, L7 runtime, Tailnet Lock signer).

## Contradictions

None. Both reports confirm rather than contradict earlier findings.

## Unknowns

- `bao operator raft snapshot restore -stage` exact semantics (unverified in current
  docs; test the installed binary).
- Calico chart/Installation enum specifics (branch timed out; verify docs.tigera.io).
- Real Cilium-vs-Calico memory footprint on the lab host (no controlled benchmark;
  measure).
- Live-cluster behavior (seal state, real restore, L7 runtime, Tailnet Lock signer) —
  tracked in Research/Open/live-cluster-verification.

## Evidence Ledger

- C-001 | confidence=high | OpenBao snapshot automation contract: independent-host systemd timer, export-only token, staged SHA-256 upload to versioned off-cluster storage, 14d/8w/12m+pre-change retention, export/restore identity split, break-glass force restore, quarterly isolated drill with semantic checklist and redacted evidence.
  - source: [[Raw/Sources/deep-research-openbao-snapshot-automation.md#Normalized Content]]
- C-002 | confidence=high | kind CNI choice: kindnetd does not enforce NetworkPolicy; minimal Cilium is the recommended default for real enforcement (direct bootstrap then Flux, small values, pinned chart); Calico for conventional networking; verification is a two-Pod TCP deny-all data-plane test; declarative-only labeling or removal are the kindnetd alternatives; PSA/Kyverno do not implement the policy data plane.
  - source: [[Raw/Sources/deep-research-kind-cni.md#Normalized Content]]