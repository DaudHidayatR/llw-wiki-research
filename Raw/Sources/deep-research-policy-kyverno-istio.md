---
schema_version: 2
id: "source-deep-research-policy-kyverno-istio"
type: "source"
title: "Deep Research — Kyverno Policy Enforcement and Istio Assessment"
Author: "Hermes Deep Research"
Reference: "deep-research-jobs-a481a680-c3f6c0e7"
SourceType: "web"
ContentType:
  - "markdown"
Published: "2026-08-24"
Captured: "2026-08-24"
Created: "2026-08-24"
Processed: true
tags:
  - "source"
ContentHash: "sha256:a901bde6a58554848caae6f69596dcb5fb98fb0124b756b43b01c7344c857b8c"
---

# Deep Research — Kyverno Policy Enforcement and Istio Assessment

## Normalized Content

### Policy enforcement (Kyverno + Conftest + PSA)

Kubernetes Pod Security Admission (PSA) applies the Baseline and Restricted Pod Security
Standards using namespace labels; it is built into Kubernetes and version-aware. Kyverno
validation policies can report violations in audit mode or reject admission requests in
enforce mode; background scanning evaluates existing resources but is not admission-time
rejection.

Recommended model: use PSA for PSS (applications: `enforce=baseline`, `audit=restricted`,
`warn=restricted`, profile pinned to the Kubernetes minor version); use Kyverno as the
in-cluster admission controller for Kubernetes-specific rules not covered by PSA; run the
same Kyverno policies in CI with the Kyverno CLI so pull requests fail before Flux
reconciles; retain Conftest only for checks Kyverno should not own (repository structure,
non-Kubernetes files, cross-file GitOps conventions). Do not maintain equivalent security
rules in both Rego and Kyverno — one rule, one authoritative implementation.

Enforcement: `Enforce` immediately for deterministic low-risk rules (disallow mutable
`:latest`, require explicit image tags/digests, reject privileged Pods in app namespaces
if PSA does not already, reject host namespaces/prohibited hostPath, require a minimal
label set). `Audit` first for disruptive rules (runAsNonRoot, read-only rootfs, drop-all-
caps, resource requests/limits, probes, default-deny NetworkPolicy, approved registries,
signed images). Promote individually after reports are clean. Avoid a permanent
audit-everything posture and avoid one global audit-to-enforce switch. Audit-to-enforce
does not evict existing non-compliant Pods; only new/updated resources are rejected.

Kyverno and Flux: Flux-applied resources are API requests subject to admission. Do not
broadly exclude the `flux-system` namespace or Flux controller service accounts; exclude
specific namespaces, kinds, or service accounts only where a policy is incompatible with
a required controller operation. Kyverno mutation can fight Flux (drift and reapply) —
prefer explicit desired values in Git.

Placement: the Kyverno engine belongs in the `platform` Flux layer; ClusterPolicy/Policy
objects and PSA namespace labels belong in `policies`; `policies dependsOn platform`
(ClusterPolicy CRDs must exist first); `apps dependsOn policies` to guarantee
first-admission policy checking. Kyverno should not be bundled into bootstrap.

NetworkPolicy enforcement depends on the cluster's network implementation; creating
NetworkPolicy objects without a supporting CNI has no effect. Verify the kind CNI
implements NetworkPolicy before enforcing default-deny. For a small homelab, prefer
explicit NetworkPolicy manifests beside each application plus one CI aggregate check.

### Istio assessment

Istio istiod alone does not mesh workloads; sidecar injection requires namespace labels
(`istio-injection: enabled`) plus Pod recreation, and Istio CNI only redirects traffic for
already-injected Pods (it does not inject or encrypt). Installing base + CNI + istiod with
no injected workloads is mesh infrastructure without mesh consumers.

A non-injected Tailscale ingress proxy sending plain HTTP to a sidecar-injected backend
with `PeerAuthentication` in `STRICT` mode fails: the destination Envoy rejects the
plaintext connection. OpenBao `tlsDisable` and Headlamp port 80 are not inherently
incompatible with Istio — the destination Envoy terminates mTLS and forwards ordinary
HTTP to the application; the incompatible combination is specifically an uninjected source
proxy plus an injected STRICT destination. Keep the Tailscale proxy and ingress-facing
backends outside the sidecar mesh unless mesh behavior is itself being tested.

Istio is not required for the described Headlamp/OpenBao/Tailscale functionality; those
work via plain Services + Tailscale operator + NetworkPolicies + Kyverno. NetworkPolicy is
not a complete replacement for Istio identity and L7 authorization, but the lab may not
need those properties. Istio 1.24.3 is far outside upstream support as of August 2026
(current trains: 1.30 supported through ~Nov 2026, 1.29 at EOL boundary, 1.28 EOL'd July
2026); running it is unsupported and misses security patches. Decision is binary: upgrade
to a supported 1.30.x patch OR remove. Recommended default for this lab: remove unless
service-mesh learning is an explicit repository objective (then isolate to a dedicated
mesh-demo namespace with one client+server workload, STRICT + one AuthorizationPolicy,
one smoke check, no gateway, and keep tailscale/headlamp/openbao out of injection).

## References

- https://kyverno.io/docs/policy-types/cluster-policy/validate/
- https://kyverno.io/docs/policy-reports/background/
- https://kubernetes.io/docs/concepts/security/pod-security-admission/
- https://kubernetes.io/docs/concepts/security/pod-security-standards/
- https://kubernetes.io/docs/reference/access-authn-authz/admission-controllers/
- https://www.conftest.dev
- https://istio.io/latest/docs/releases/supported-releases
- https://istio.io/latest/docs/ops/deployment/security-model
- https://istio.io/latest/docs/setup/additional-setup/sidecar-injection
- https://tailscale.com/docs/kubernetes-operator/ingress

## Capture Notes

Consolidated from deep-research jobs c3f6c0e74dc14a0ea310166088663ccc (Phase 3, Kyverno)
and a481a680862a4f8781f618711f4678d9 (Phase 3, Istio). Both jobs could NOT retrieve the
repo; repo-specific state (Kyverno install/version, existing Rego/PSA, kind CNI
NetworkPolicy support, Istio injection labels) must be verified before implementation.
