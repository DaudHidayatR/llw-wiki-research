---
schema_version: 2
id: "decision-live-cluster-verification-after-p0p1"
type: "decision"
title: "Live-Cluster Verification Runs After P0/P1 Implementation"
status: "active"
scope: "homelab-devsecops"
supersedes: []
superseded_by: []
related_wiki:
  - "synthesis-phase6-verification-findings"
  - "synthesis-phase6c-supply-chain-pins-and-gap-triage"
related_research:
  - "research-open-live-cluster-verification"
created: "2026-08-31"
updated: "2026-08-31"
---

# Live-Cluster Verification Runs After P0/P1 Implementation

## Decision

The live-cluster verification suite (OpenBao real restore, Tailscale L7 Ingress runtime,
Tailnet Lock rebuild, NetworkPolicy data-plane negative control) is executed ONCE, on the
real host, AFTER the P0/P1 implementation cards land — verifying the new architecture
instead of the legacy one.

## Context

All runtime-verification procedures are already written
([[Research/Open/live-cluster-verification]], phase6b synthesis); they cannot run from
the sandbox and need `make up` on the user's host. Sequencing decided in the
2026-08-31 review (kanban t_d0ad0e1e).

## Why

Verifying before the refactor would test a stack scheduled for replacement (Istio,
semver mode, legacy annotations) and double the drill work.

## Alternatives Considered

Run now on the current host (rejected — redundant with the coming refactor); skip
indefinitely (rejected — leaves live-cluster items permanently open).

## Trade-offs

Live-cluster verification items stay `open` longer; accepted because they are
procedures-to-run, not open questions.

## Consequences

`Research/Open/live-cluster-verification` stays open, annotated as sequenced-after-P0/P1;
the implementation phase must not close it, and the verification pass covers the
negative NetworkPolicy control per the kindnetd decision.

## Revisit Condition

If P0/P1 implementation is blocked longer than a quarter, run the verification on the
legacy stack anyway so the drill evidence does not go stale.

## Evidence Ledger

- Source: [[Research/Open/live-cluster-verification]] (procedures, defined 2026-08-26)
- Kanban: t_d0ad0e1e decision comment (2026-08-31, user review)
