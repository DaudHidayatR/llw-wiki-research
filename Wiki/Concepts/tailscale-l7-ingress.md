---
schema_version: 2
id: "concept-tailscale-l7-ingress"
type: "concept"
title: "Tailscale L7 Ingress — Mechanics, Standalone vs ProxyGroup, Tags, Grants"
topics:
  - "homelab-devsecops"
  - "tailscale"
aliases: []
status: "active"
confidence: "high"
sources:
  - "Raw/Sources/deep-research-tailscale-operator.md"
source_count: 1
related:
  - "concept-tailscale-operator-helm"
  - "concept-openbao-http-behind-tls"
relationships:
  - "requires|concept-tailscale-operator-helm"
supersedes: []
superseded_by: []
last_verified: "2026-08-24"
review_after: "2026-11-24"
created: 2026-08-24
updated: 2026-08-24
---

# Tailscale L7 Ingress — Mechanics, Standalone vs ProxyGroup, Tags, Grants

## Definition

Expose Kubernetes workloads to the private tailnet via the operator-managed L7 Ingress
(`ingressClassName: tailscale`), with HTTPS terminated by the operator's proxy. The
operator owns Serve configuration internally; no custom `tailscale serve` CLI/watcher is
needed. [C-001]

## Ingress Shape

Prerequisites: tailnet MagicDNS and HTTPS enabled. HTTPS on port 443; the hostname in
`spec.tls.hosts` becomes the service's MagicDNS name under `<name>.<tailnet>.ts.net`.
Keep `rules[].host` aligned with `tls.hosts`. Certificate provisioning is lazy (Let's
Encrypt) — the first request can occasionally time out. [C-001]

## Standalone vs ProxyGroup

Standalone creates one dedicated single-replica proxy per exposed resource: least
configuration, lower resource use, easiest troubleshooting. ProxyGroup is the documented
HA mechanism (reusable replica pool, shared advertisement, multi-cluster backends) but
adds Pods, CRDs, policy, and diagnosis complexity, with no end-to-end HA if backends,
storage, or the control plane remain single-instance. For a homelab, start standalone;
add ProxyGroup only after a real availability problem or intentional HA testing. [C-001]

## Tags and Grants

Default tags: `tag:k8s-operator` (operator identity) and `tag:k8s` (proxy). The operator
tag must own every tag it assigns to managed proxies via `tagOwners`; individual users
should not own generated proxy tags. Tailscale recommends grants for new access-control
policy (coexist with legacy ACLs; additive semantics). Starting policy for administrative
HTTPS: grant the admin group `tcp:443` to `tag:k8s`; legacy equivalent `tag:k8s:443`. Do
not use Funnel for private admin interfaces. [C-001]

## Evidence Ledger

- C-001 | confidence=high | Tailscale L7 Ingress requires ingressClassName tailscale plus MagicDNS and HTTPS; standalone proxies are the homelab default, ProxyGroup adds HA complexity; operator tag must own proxy tags; grants are the recommended ACL syntax; Funnel is public exposure and should not be used for private admin UIs.
  - source: [[Raw/Sources/deep-research-tailscale-operator.md#Normalized Content]]
