---
schema_version: 2
id: "concept-openbao-http-behind-tls"
type: "concept"
title: "OpenBao Plain-HTTP Behind Tailscale L7 TLS Termination"
topics:
  - "homelab-devsecops"
  - "openbao"
  - "tailscale"
aliases: []
status: "active"
confidence: "high"
sources:
  - "Raw/Sources/deep-research-openbao-tls-policy.md"
source_count: 1
related:
  - "concept-tailscale-l7-ingress"
  - "concept-openbao-policy-reconcile"
relationships:
  - "requires|concept-tailscale-l7-ingress"
supersedes: []
superseded_by: []
last_verified: "2026-08-24"
review_after: "2026-11-24"
created: 2026-08-24
updated: 2026-08-24
---

# OpenBao Plain-HTTP Behind Tailscale L7 TLS Termination

## Definition

Run OpenBao with TLS disabled inside the cluster (`tlsDisable: true`, listener
`tls_disable = 1`, port 8200) and let the Tailscale L7 ingress proxy terminate HTTPS at
the tailnet boundary. [C-001]

## Compatibility and Traffic Flow

Traffic flow: client → `https://openbao.<tailnet>.ts.net:443` → Tailscale proxy
TLS-terminates → `http://openbao.openbao.svc:8200`. Ingress backends reference Services;
the backend targets service `openbao`, port 8200 (by number or name, matching the pinned
chart's actual Service port). Keep `tls.hosts` aligned with `rules[].host`. [C-001]

## Security Boundary

Provides TLS client→proxy, WireGuard across the tailnet, private MagicDNS, Tailscale
identity + grant enforcement, and plain HTTP only for the final in-cluster hop. Does NOT
provide end-to-end application TLS, encryption between proxy Pod and OpenBao Pod,
protection from a compromised Pod observing that path, or crypto server identity at the
OpenBao process. Reasonable for a small single-cluster homelab only if OpenBao is
reachable only via the private Tailscale Ingress, no public ingress exposes the same
Service, NetworkPolicies restrict :8200, and the cluster/CNI network is trusted. [C-001]

## Gotchas

The externally relevant API address must be the HTTPS MagicDNS URL, not the internal HTTP
address. With `tlsDisable: true`, probes must use HTTP (`/v1/sys/health` :8200); OpenBao
health returns different status codes for initialized/sealed/standby/active, so readiness
must match desired state or Flux may wait forever on a running-but-sealed server. [C-001]

## Evidence Ledger

- C-001 | confidence=high | OpenBao tlsDisable with HTTP on 8200 is compatible with Tailscale L7 TLS termination; the backend targets Service openbao:8200; the external API address must be the HTTPS MagicDNS URL; HTTP probes must match desired seal state; a restrictive NetworkPolicy is required.
  - source: [[Raw/Sources/deep-research-openbao-tls-policy.md#Normalized Content]]
