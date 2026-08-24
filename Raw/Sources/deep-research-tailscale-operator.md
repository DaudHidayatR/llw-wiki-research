---
schema_version: 2
id: "source-deep-research-tailscale-operator"
type: "source"
title: "Deep Research — Tailscale Operator Helm, L7 Ingress, Tags, Grants"
Author: "Hermes Deep Research"
Reference: "deep-research-jobs-f5139ca8-a481a680"
SourceType: "web"
ContentType:
  - "markdown"
Published: "2026-08-24"
Captured: "2026-08-24"
Created: "2026-08-24"
Processed: true
tags:
  - "source"
ContentHash: "sha256:7dac7d561a6c4479755a7111cd868d21304f09f06df61432ea08e2913cb97c42"
---

# Deep Research — Tailscale Operator Helm, L7 Ingress, Tags, Grants

## Normalized Content

Official Tailscale Helm repository: `https://pkgs.tailscale.com/helmcharts`. The
authoritative version source is the repository index
(`https://pkgs.tailscale.com/helmcharts/index.yaml`), not the GitHub Chart.yaml, which
carries release-time placeholders (`version: 0.1.0`, `appVersion: stable`).

Current stable chart version reported as v1.102.3 (published 2026-08-20) via Artifact
Hub; verify the exact version string (including leading `v`) against the official index
before committing, because Flux treats the chart-version constraint literally.

The default static-credential path expects a Secret named `operator-oauth` in the
operator's namespace with exactly the keys `client_id` and `client_secret`. The
underscore-separated names are significant; they are not `clientId`/`clientSecret`
(Tailscale issue #16776). Do not place OAuth credentials in the HelmRelease. Tailscale
OAuth secrets are durable API credentials and GitHub secret-scanning flags them.

Chart `1.92.3` regressed the pre-created-Secret path: the rendered Deployment omitted
`CLIENT_ID_FILE`, `CLIENT_SECRET_FILE`, the `/oauth` volumeMount, and the
`operator-oauth` Secret volume, causing a crash loop with "CLIENT_ID_FILE and
CLIENT_SECRET_FILE must be set" (issues #18236, #18237, #18244). "Fixed in 1.92.4" is the
reported boundary; pin a current release and inspect the rendered Deployment.

OAuth client needs `devices:core` (write), `auth_keys` (write), and permission to use
`tag:k8s-operator` plus any configured proxy tags.

Layer 7 exposure is selected with `spec.ingressClassName: tailscale`. The tailnet must
have MagicDNS and HTTPS enabled. HTTPS is exposed on port 443; the hostname in
`spec.tls.hosts` becomes the service's MagicDNS name under `<name>.<tailnet>.ts.net`.
Keep `rules[].host` aligned with `tls.hosts`. Certificate provisioning is lazy
(Let's Encrypt); the first request can occasionally time out.

Standalone ingress creates one dedicated single-replica proxy per exposed resource:
least configuration, lower resource use, easiest troubleshooting. ProxyGroup is the
documented HA mechanism (reusable replica pool, shared advertisement, multi-cluster
backends) but adds Pods, CRDs, policy, and diagnosis complexity; there is no end-to-end
HA if backends, storage, or the control plane remain single-instance. Multi-cluster
regional routing is a Premium/Enterprise feature. For a homelab, start standalone; add
ProxyGroup only after a real availability problem or intentional HA testing.

Default tags: `tag:k8s-operator` (operator identity) and `tag:k8s` (proxy). The operator
tag must own every tag it assigns to managed proxies via `tagOwners`. Do not make
individual users owners of generated proxy tags.

Tailscale recommends grants for new access-control policy (they coexist with legacy
ACLs; grants are additive — a broader matching rule is not overridden by a narrower
one). Starting policy for administrative HTTPS: `grants: [{src: [group:homelab-admins],
dst: [tag:k8s], ip: [tcp:443]}]`; legacy equivalent `tag:k8s:443`. Add policy tests
(admin can reach, normal member cannot). Do not use Funnel for private admin interfaces
(Funnel is public internet exposure).

## References

- https://pkgs.tailscale.com/helmcharts/index.yaml
- https://github.com/tailscale/tailscale/issues/16776
- https://github.com/tailscale/tailscale/issues/18236
- https://github.com/tailscale/tailscale/issues/18237
- https://github.com/tailscale/tailscale/issues/18244
- https://tailscale.com/kb/1446/kubernetes-operator-troubleshooting
- https://tailscale.com/kb/1439/kubernetes-operator-cluster-ingress
- https://tailscale.com/kb/1445/kubernetes-operator-customization
- https://tailscale.com/kb/1324/grants
- https://tailscale.com/kb/1538/grants-syntax

## Capture Notes

Consolidated from deep-research jobs f5139ca8a1534ac2b1f92fb1ce6c323d (Phase 1) and
a481a680862a4f8781f618711f4678d9 (Phase 3, Istio interaction). Repo-specific values
(chart pin, Secret names) must be verified against the deployed manifests.
