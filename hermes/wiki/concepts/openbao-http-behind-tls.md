---
schema_version: 2
id: "concept-openbao-http-behind-tls"
type: "concept"
title: "OpenBao Plain-HTTP Behind Tailscale L7 TLS Termination"
topics:
  - "openbao"
  - "tailscale"
  - "homelab-devsecops"
aliases:
  - "openbao ingress"
status: "active"
confidence: "high"
sources:
  - "https://openbao.org/docs/"
  - "https://tailscale.com/kb/1439/kubernetes-operator-cluster-ingress"
source_count: 2
related:
  - "concept-tailscale-l7-ingress"
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

# OpenBao Plain-HTTP Behind Tailscale L7 TLS Termination

## Definition

Run OpenBao with TLS disabled inside the cluster (`tlsDisable: true`, listener
`tls_disable = 1`, port 8200) and let the Tailscale L7 ingress proxy terminate HTTPS at
the tailnet boundary. The current homelab already runs OpenBao this way
(`global.tlsDisable: true`).

## Compatibility — Yes

Traffic flow: client → `https://openbao.<tailnet>.ts.net:443` → Tailscale proxy TLS
termination → `http://openbao.openbao.svc:8200`. Ingress backends reference **Services**
(not Pods, not URLs). [C-001][C-002]

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: openbao
  namespace: openbao
  annotations:
    tailscale.com/tags: tag:k8s
spec:
  ingressClassName: tailscale
  tls:
    - hosts: [openbao]
  rules:
    - host: openbao
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: openbao
                port: { number: 8200 }
```

The Service must expose port 8200; match the pinned chart's actual Service name/selectors.
Use the actual Service name and exposed port (number or name). [C-001]

## Security Boundary — What It Does / Doesn't Provide

Provides: TLS client→proxy, WireGuard across the tailnet, private MagicDNS discovery,
Tailscale identity + grant enforcement before network access, plain HTTP only for the
final in-cluster hop.

Does NOT provide: end-to-end app TLS client→OpenBao, encryption between the proxy Pod and
the OpenBao Pod, protection from a compromised Pod observing that path, or crypto server
identity at the OpenBao process itself.

Reasonable simplification for a small single-cluster homelab **only if**: OpenBao is
reachable only through the private Tailscale Ingress; no public ingress exposes the same
Service; NetworkPolicies restrict :8200; cluster nodes + CNI network are trusted; OpenBao
does not emit insecure redirects or advertise an internal HTTP address. [C-001]

## ⚠️ Advertised-Address Gotcha

OpenBao may generate redirects or advertise API/cluster addresses. The **externally
relevant API address must be the HTTPS MagicDNS URL** (`https://openbao.<tailnet>.ts.net`),
NOT `http://openbao.openbao.svc:8200`. The exact value location depends on the chart and
deployment mode. Internal server-to-server cluster addressing is a separate concern
(per OpenBao storage/clustering docs), not routed through Tailscale Ingress. [C-001]

## NetworkPolicy

Restrict OpenBao ingress to the tailscale namespace on :8200 (verify operator-generated
proxy Pod labels before narrowing the selector):

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: openbao-ingress
  namespace: openbao
spec:
  podSelector:
    matchLabels: { app.kubernetes.io/name: openbao }
  policyTypes: [Ingress]
  ingress:
    - from:
        - namespaceSelector:
            matchLabels: { kubernetes.io/metadata.name: tailscale }
      ports:
        - { protocol: TCP, port: 8200 }
```

## Health Probes

With `tlsDisable: true`, probes must use HTTP (`/v1/sys/health` :8200). OpenBao/Vault
health returns different status codes for initialized / sealed / standby / active —
ensure the chart's readiness matches the desired state, else Flux may wait forever on a
running-but-sealed server. [C-001]

## When to Add OpenBao-Native TLS Later

Untrusted in-cluster clients; multi-node/multi-cluster backend traffic; compliance or
end-to-end encryption requirement; proxy separated by an untrusted network; or a second
ingress path exposing OpenBao. Otherwise HTTP:8200 behind Tailscale HTTPS is the
homelab-default simplification.

## Evidence Ledger

- C-001 | confidence=high | OpenBao listener config (tls_disable, port 8200), health endpoint semantics, advertised address behavior.
  - source: https://openbao.org/docs/
- C-002 | confidence=high | Tailscale L7 Ingress backend references Service; TLS termination at proxy; MagicDNS + HTTPS.
  - source: https://tailscale.com/kb/1439/kubernetes-operator-cluster-ingress