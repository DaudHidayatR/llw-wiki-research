---
schema_version: 2
id: "decision-kindnetd-declarative-only-netpol"
type: "decision"
title: "Keep kindnetd — NetworkPolicies Are Declarative-Only"
status: "active"
scope: "homelab-devsecops"
supersedes: []
superseded_by: []
related_wiki:
  - "concept-kind-networkpolicy-enforcement"
  - "synthesis-phase6b-snapshot-and-cni-research"
related_research: []
created: "2026-08-31"
updated: "2026-08-31"
---

# Keep kindnetd — NetworkPolicies Are Declarative-Only

## Decision

Keep the default kindnetd CNI. The repo's NetworkPolicy manifests remain in Git as
CI-validated declarative intent, explicitly documented as NOT runtime-enforced
(`network-policy-mode: declarative-only` labeling/caveat), with the negative control
(same deny-all under kindnetd does not block) kept as evidence of the limit.

## Context

Phase-6 verification proved `kind-cluster.yaml` has no CNI override, so kindnetd runs
and NetworkPolicies render but have zero runtime enforcement — false assurance if left
undocumented. [[Wiki/Concepts/kind-networkpolicy-enforcement]].

## Why

A visibly-documented absent control beats a false one; the homelab threat model does not
currently demand real segmentation, and minimal Cilium adds operational weight the lab
does not need yet.

## Alternatives Considered

Minimal Cilium (`disableDefaultCNI: true`, chart v1.20.1, values already researched) for
real enforcement; Calico for conventional-networking learning. Both fully researched and
reusable if the threat model changes.

## Trade-offs

No runtime network segmentation; smaller cluster footprint and simpler bootstrap.

## Consequences

Document the caveat wherever NetworkPolicies are referenced; keep the data-plane
negative control in the verification procedures. PSA/Kyverno admission controls remain
complementary and never substitute for the policy data plane.

## Revisit Condition

If the lab starts running untrusted workloads or the threat model demands segmentation,
switch to the researched minimal-Cilium contract.

## Evidence Ledger

- Source: [[Wiki/Concepts/kind-networkpolicy-enforcement]] (repo-verified kindnetd non-enforcement)
- Kanban: t_f4b33583 decision comment (2026-08-31, user review)
