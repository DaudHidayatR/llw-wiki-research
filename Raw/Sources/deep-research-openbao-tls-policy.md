---
schema_version: 2
id: "source-deep-research-openbao-tls-policy"
type: "source"
title: "Deep Research — OpenBao HTTP Behind TLS, Policy-as-Code, Root-Token Minimization"
Author: "Hermes Deep Research"
Reference: "deep-research-jobs-f5139ca8-54802739"
SourceType: "web"
ContentType:
  - "markdown"
Published: "2026-08-24"
Captured: "2026-08-24"
Created: "2026-08-24"
Processed: true
tags:
  - "source"
ContentHash: "sha256:e789ed236b22a1f53a1c7b6308417c66b12cfdfa2876082d8dca82880dcf24b2"
---

# Deep Research — OpenBao HTTP Behind TLS, Policy-as-Code, Root-Token Minimization

## Normalized Content

OpenBao can run with TLS disabled inside Kubernetes (`tlsDisable: true`, listener
`tls_disable = 1`, port 8200) while Tailscale Ingress provides external HTTPS
termination. Traffic flow: client → `https://openbao.<tailnet>.ts.net:443` → Tailscale
proxy TLS-terminates → `http://openbao.openbao.svc:8200`. Ingress backends reference
Services (not Pods, not URLs); the backend targets service `openbao`, port 8200 (by
number or name, matching the pinned chart's actual Service port).

This design provides TLS client→proxy, WireGuard across the tailnet, private MagicDNS,
Tailscale identity and grant enforcement before network access, and plain HTTP only for
the final in-cluster hop. It does NOT provide end-to-end application TLS, encryption
between the proxy Pod and OpenBao Pod, protection from a compromised Pod observing that
path, or cryptographic server identity at the OpenBao process. Reasonable for a small
single-cluster homelab only if OpenBao is reachable only through the private Tailscale
Ingress, no public ingress exposes the same Service, NetworkPolicies restrict :8200, and
the cluster/CNI network is trusted.

The externally relevant API address must be the HTTPS MagicDNS URL
(`https://openbao.<tailnet>.ts.net`), NOT the internal HTTP address. With `tlsDisable:
true`, probes must use HTTP (`/v1/sys/health` :8200); OpenBao/Vault health returns
different status codes for initialized/sealed/standby/active, so readiness must match
desired state or Flux may wait forever on a running-but-sealed server.

OpenBao natively documents ACL policies in HCL or JSON, not YAML. Policies should stay
as native HCL files (`bao policy write` accepts them directly). YAML should not be
converted into a home-grown ACL language. A thin YAML mapping inventory
(`openbao/mappings.yaml`) can bind Kubernetes roles (serviceAccounts/namespaces/audience/
policies/tokenTTL) and be translated by a reconciler into `bao policy write` +
`bao write auth/kubernetes/role/<name>`. Validate the inventory against JSON Schema and
reject unknown keys, empty names, wildcard bindings unless approved, missing policy
files, duplicate roles, and out-of-range TTLs.

Host-driven reconciliation is preferred over an in-cluster controller: a controller that
repairs authentication may depend on the same authentication it repairs, and Git write
access becomes indirect OpenBao administrative access. The OpenBao Secrets Operator is
archived (February 2026) and recommends External Secrets Operator instead; ESO supports
OpenBao through its Vault provider for secret synchronization, not for ACL/auth
configuration. Flux should manage Kubernetes resources but not OpenBao's internal
control plane.

Root policy is not the same as `sudo`. Root-protected API paths require the capability
corresponding to the HTTP operation plus `sudo` on specific prefixes, so a non-root
token can be delegated the necessary capability plus narrowly scoped `sudo`. OpenBao
recommends revoking root tokens before production use. Bootstrap sequence: install →
initialize/unseal (or auto-unseal) → distribute unseal/recovery material outside Git →
use the initial root token to enable auth + create scoped policies/roles → test →
revoke the initial root token; regenerate only via the documented recovery ceremony.
Root tokens, unseal shares, recovery keys, AppRole SecretIDs, and bootstrap tokens must
never be committed to Git.

Auth matrix: in-cluster workloads → Kubernetes auth (ServiceAccount JWT via TokenReview;
Flux v2.9 supports direct OpenBao ServiceAccount-token auth for SOPS decryption);
human administrators → OIDC (individual identity, groups, revocation, MFA); off-cluster
automation → AppRole (RoleID + controlled SecretID, pull-mode, short TTL); userpass only
as a temporary bootstrap or break-glass method. Suggested policy roles: flux-decrypt,
external-secrets-read, policy-reconciler, platform-auditor, platform-admin (selected
sudo), break-glass-admin.

## References

- https://openbao.org/docs/
- https://openbao.org/docs/concepts/policies
- https://openbao.org/docs/auth/kubernetes
- https://openbao.org/docs/auth/approle
- https://openbao.org/docs/commands
- https://openbao.org/api-docs/auth/kubernetes
- https://external-secrets.io/latest/provider/openbao
- https://fluxcd.io/blog/2026/07/flux-openbao-secrets-signatures

## Capture Notes

Consolidated from deep-research jobs f5139ca8a1534ac2b1f92fb1ce6c323d (Phase 1, card 5/5)
and 5480273985814cbd9f2af190a71d7949 (Phase 2, card 1/3). Repo-specific OpenBao
namespace, release name, Raft path, and TLS configuration must be verified against the
deployed manifests.
