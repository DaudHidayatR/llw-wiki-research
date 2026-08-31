---
schema_version: 2
id: "decision-single-k8s-tag-model"
type: "decision"
title: "Single tag:k8s Tailscale Tag Model"
status: "active"
scope: "homelab-devsecops"
supersedes: []
superseded_by: []
related_wiki:
  - "concept-tailscale-l7-ingress"
  - "synthesis-flux-tailscale-redesign"
related_research: []
created: "2026-08-31"
updated: "2026-08-31"
---

# Single tag:k8s Tailscale Tag Model

## Decision

Operator-owned Tailscale resources use a single `tag:k8s`, owned by `tag:k8s-operator`,
with tailnet access granted via one group grant to `tcp:443`. No custom admin tags.

## Context

The v2 audit originally proposed two custom admin tags (`homelab-k8s-admin`,
`homelab-secrets-admin`). Phase-1 deep research found the single-tag model is the
upstream-default pattern, needs no per-tag tagOwners/grants bookkeeping, and covers the
homelab's actual access shape (HTTPS-only reachability). [[Wiki/Concepts/tailscale-l7-ingress]].

## Why

Simplest correct model; access separation can be introduced later without rework since
tags are additive.

## Alternatives Considered

Custom admin tags (real ACL separation, but each tag needs explicit tagOwners + grants —
rejected for now).

## Trade-offs

No ACL-level separation between dashboard and secrets traffic; mitigated by OpenBao's own
auth policies behind the single HTTPS entry point.

## Consequences

ACL grants stay minimal; any future service that needs a distinct trust boundary gets a
new tag + grant at that time.

## Revisit Condition

If a second trust boundary is actually needed (e.g. separating secrets admin from
dashboard users), split tags then.

## Evidence Ledger

- Source: [[Wiki/Concepts/tailscale-l7-ingress]] (Phase-1 research, grants syntax + tag ownership)
- Kanban: t_d0ad0e1e consolidated findings + t_716c4c70 decision comment (2026-08-31, user review)
