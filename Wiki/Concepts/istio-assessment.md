---
schema_version: 2
id: "concept-istio-assessment"
type: "concept"
title: "Istio Assessment for the Homelab"
topics:
  - "homelab-devsecops"
  - "istio"
aliases: []
status: "active"
confidence: "high"
sources:
  - "Raw/Sources/deep-research-policy-kyverno-istio.md"
source_count: 1
related:
  - "concept-tailscale-l7-ingress"
  - "project-homelab-devsecops"
relationships:
  - "contrasts-with|concept-tailscale-l7-ingress"
supersedes: []
superseded_by: []
last_verified: "2026-08-24"
review_after: "2026-11-24"
created: 2026-08-24
updated: 2026-08-24
---

# Istio Assessment for the Homelab

## Definition

Istio istiod alone does not mesh workloads; sidecar injection requires namespace labels
(`istio-injection: enabled`) plus Pod recreation, and Istio CNI only redirects traffic
for already-injected Pods (it does not inject or encrypt). Installing base + CNI + istiod
with no injected workloads is mesh infrastructure without mesh consumers. [C-001]

## mTLS × Tailscale Interaction

A non-injected Tailscale ingress proxy sending plain HTTP to a sidecar-injected backend
with `PeerAuthentication` in `STRICT` mode fails: the destination Envoy rejects the
plaintext connection. OpenBao `tlsDisable` and Headlamp port 80 are not inherently
incompatible with Istio — the destination Envoy terminates mTLS and forwards ordinary HTTP
to the application; the incompatible combination is specifically an uninjected source
proxy plus an injected STRICT destination. Keep the Tailscale proxy and ingress-facing
backends outside the sidecar mesh unless mesh behavior is itself being tested. [C-001]

## Version and Recommendation

Istio is not required for the described Headlamp/OpenBao/Tailscale functionality; those
work via plain Services + Tailscale operator + NetworkPolicies + Kyverno. Istio 1.24.3 is
far outside upstream support as of August 2026 (current: 1.30 supported through ~Nov
2026, 1.29 at EOL boundary, 1.28 EOL'd July 2026). Decision is binary: upgrade to a
supported 1.30.x patch OR remove. Recommended default for this lab: remove unless
service-mesh learning is an explicit repository objective (then isolate to a dedicated
mesh-demo namespace with one client+server workload, STRICT + one AuthorizationPolicy,
one smoke check, no gateway, and keep tailscale/headlamp/openbao out of injection).
[C-001]

## Evidence Ledger

- C-001 | confidence=high | Istio does not mesh workloads without injection labels + Pod recreation; an uninjected Tailscale proxy to an injected STRICT backend fails; Istio is not load-bearing for Headlamp/OpenBao/Tailscale; 1.24.3 is unsupported (upgrade to 1.30.x or remove); keep tailscale/headlamp/openbao out of injection.
  - source: [[Raw/Sources/deep-research-policy-kyverno-istio.md#Normalized Content]]
