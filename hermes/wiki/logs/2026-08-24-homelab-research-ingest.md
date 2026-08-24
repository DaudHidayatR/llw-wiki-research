---
schema_version: 2
id: "log-2026-08-24-homelab-research-ingest"
type: "log"
title: "2026-08-24 — Homelab Flux × Tailscale research ingested"
topics:
  - "homelab-devsecops"
aliases: []
status: "active"
confidence: "high"
sources:
  - "https://pkgs.tailscale.com/helmcharts/index.yaml"
  - "https://fluxcd.io/flux/components/kustomize/kustomizations/"
source_count: 21
related:
  - "project-homelab-devsecops-research"
  - "synthesis-flux-tailscale-redesign"
relationships: []
supersedes: []
superseded_by: []
last_verified: "2026-08-24"
review_after: "2026-11-24"
created: 2026-08-24
updated: 2026-08-24
---

# 2026-08-24 — Homelab Flux × Tailscale research ingested

## Action

Ingested the deep-research findings (job `f5139ca8a1534ac2b1f92fb1ce6c323d`) for the
`DaudHidayatR/homelab-devsecops` Flux × Tailscale architecture redesign into this wiki.

## Files Created

- `hermes/wiki/index.md` — project index + consolidated findings + evidence ledger
- `hermes/wiki/concepts/tailscale-operator-helm.md`
- `hermes/wiki/concepts/tailscale-l7-ingress.md`
- `hermes/wiki/concepts/tailnet-lock-rebuilds.md`
- `hermes/wiki/concepts/flux-gitops-graph.md`
- `hermes/wiki/concepts/openbao-http-behind-tls.md`
- `hermes/wiki/synthesis/flux-tailscale-redesign.md`

## Method

Wiki-first (local wiki had no pages on these topics), then async Open Deep Research
(Firecrawl-backed, ~11 min, 21 cited sources). Key corrections to the v2 audit:
re-pin the Tailscale chart to v1.102.3, reconsider the tag model and SOPS decision, and
set the OpenBao external API address to the HTTPS MagicDNS URL.