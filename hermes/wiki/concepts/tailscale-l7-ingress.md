---
schema_version: 2
id: "concept-tailscale-l7-ingress"
type: "concept"
title: "Tailscale L7 Ingress — Mechanics, Standalone vs ProxyGroup, Tags, Grants"
topics:
  - "tailscale"
  - "homelab-devsecops"
aliases:
  - "tailscale ingress"
status: "active"
confidence: "high"
sources:
  - "https://tailscale.com/kb/1439/kubernetes-operator-cluster-ingress"
  - "https://tailscale.com/kb/1445/kubernetes-operator-customization"
  - "https://tailscale.com/kb/1324/grants"
source_count: 6
related:
  - "concept-tailscale-operator-helm"
  - "project-homelab-devsecops-research"
relationships:
  - "part-of|project-homelab-devsecops-research"
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
operator owns Serve configuration internally (tailscaled local API / SetServeConfig) —
no custom `tailscale serve` CLI / watcher is needed.

## Ingress Shape

Prerequisites: tailnet **MagicDNS enabled** and **HTTPS enabled**. HTTPS is exposed on
port 443; the hostname in `tls.hosts` becomes the service's MagicDNS name under
`<name>.<tailnet>.ts.net`. [C-001]

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: app
  namespace: apps
  annotations:
    tailscale.com/tags: tag:k8s   # optional custom proxy tag
spec:
  ingressClassName: tailscale
  tls:
    - hosts: [app]
  rules:
    - host: app
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: app
                port: { number: 8080 }
```

Keep `rules[].host` aligned with `tls.hosts` (avoids routing ambiguity). HTTPS certs are
provisioned lazily (Let's Encrypt) — the first request can occasionally time out.
Traffic path: client → WireGuard/Tailscale → HTTPS 443 → proxy TLS-terminates →
Service backend over HTTP/HTTPS. [C-001][C-002]

**NetworkPolicy requirement:** the proxy Pod runs in the `tailscale` namespace but must
reach app-namespace Services — NetworkPolicies must allow tailscale-ns → selected app
Pods on the backend target port. [C-002]

## Standalone vs ProxyGroup

**Standalone** (default operator path): one dedicated single-replica proxy per exposed
resource. Pros: least config, lower CPU/memory, easiest troubleshooting, no ProxyGroup
CRD, no advertisement setup. Cons: ingress down during proxy restart / node failure /
full kind rebuild; N ingresses = N proxies. [C-003]

**ProxyGroup** (documented HA): reusable pool of proxy replicas shared by ingresses,
egresses, and API-server proxies. When: proxy restart must not interrupt access, rolling
maintenance, several services share a pool, multi-cluster backends, or intentionally
learning/validating production HA. Costs: more Pods/CRDs/policy/permissions, more complex
diagnosis. **No end-to-end HA if backends/storage/control-plane remain single-instance.**
Regional routing is Premium/Enterprise (not needed for single-cluster HA). [C-003][C-004]

**Homelab recommendation: start standalone.** Move to a two-replica ingress ProxyGroup
only after a real availability problem or intentional HA testing. Do not add ProxyGroup
merely because it exists.

## Tag Model

Defaults: `tag:k8s-operator` (operator identity), `tag:k8s` (proxy). The operator tag
must own every tag it assigns to managed proxies: [C-005]

```json
{
  "tagOwners": {
    "tag:k8s-operator": [],
    "tag:k8s": ["tag:k8s-operator"],
    "tag:k8s-private": ["tag:k8s-operator"],
    "tag:k8s-admin": ["tag:k8s-operator"]
  }
}
```

Do not make individual users owners of generated proxy tags unless they assign them
outside the operator. Custom tags give separate access boundaries but require explicit
`tagOwners` entries and per-tag grants.

## Grants / Access Policy

Tailscale recommends **grants** for new policy (coexist with legacy ACLs; grants are
additive — a broader matching rule is not overridden by a narrower one). [C-006]

Starting policy for administrative HTTPS apps:

```json
{
  "tagOwners": { "tag:k8s-operator": [], "tag:k8s": ["tag:k8s-operator"] },
  "groups": { "group:homelab-admins": ["alice@example.com"] },
  "grants": [
    { "src": ["group:homelab-admins"], "dst": ["tag:k8s"], "ip": ["tcp:443"] }
  ]
}
```

Legacy equivalent: `{"acls": [{"action":"accept","src":["autogroup:admin"],"dst":["tag:k8s:443"],"proto":"tcp"}]}`.
Add policy tests (admin can reach, normal member cannot). Granting `ip: ["*"]` is
unnecessary for L7 Ingress alone.

## Funnel

Do **not** use Funnel (`tailscale.com/funnel: "true"`) for admin interfaces — Funnel is
public internet exposure; these are private tailnet-only workloads.

## Evidence Ledger

- C-001 | confidence=high | ingressClassName tailscale; MagicDNS + HTTPS required; tls.hosts → <name>.<tailnet>.ts.net; HTTPS 443; lazy cert provisioning.
  - source: https://tailscale.com/kb/1439/kubernetes-operator-cluster-ingress
- C-002 | confidence=high | Proxy in tailscale ns; NetworkPolicy must allow tailscale-ns → app backends; troubleshooting via proxy Pod + generated Serve config.
  - source: https://tailscale.com/kb/1446/kubernetes-operator-troubleshooting
- C-003 | confidence=high | Standalone single-replica proxy per resource; ProxyGroup = HA pool; costs and when-to-use.
  - source: https://tailscale.com/kb/1445/kubernetes-operator-customization
- C-004 | confidence=high | Multi-cluster HA uses ≥2 ProxyGroup replicas per cluster; regional routing is Premium/Enterprise.
  - source: https://tailscale.com/kb/1541/kubernetes-operator-multi-cluster-ingress
- C-005 | confidence=high | Default tags and tagOwners contract.
  - source: https://tailscale.com/kb/1446/kubernetes-operator-troubleshooting , https://tailscale.com/docs/kubernetes-operator/reference/tags
- C-006 | confidence=high | Grants preferred; coexist with ACLs; additive semantics.
  - source: https://tailscale.com/kb/1324/grants , https://tailscale.com/kb/1538/grants-syntax , https://tailscale.com/kb/1542/grants-migration